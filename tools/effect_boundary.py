#!/usr/bin/env python3
"""Prove a refusal by what the world looks like afterwards, not by what the tool said.

    from effect_boundary import refuses, JsonlAppend
    refuses(argv=("python3", "tools/record_spend.py", "--cohort", "no-such-cohort-zzqx"),
            case="D-62 / RS-01", expect_guard="RS-01", expected_effects={})

CONTROL 64, GENERALISED. Until now this repository applied it at two hand-written sites, and its
own control-application row said so: *"no harness makes a refusing tool declare its effect set,
and no check requires a refusal arm to assert over that set rather than over stdout."* This is
that harness. It exists because of four incidents, and each one shaped a part of it:

* **D-62.** A negative control asserted "no cost was printed" and passed on all 87 runs, while
  those same runs appended 87 rows to the spend ledger the tool exists to protect. Signal
  correct, effect catastrophic, test green.
* **D-66.** A refusal arm written as a DISJUNCTION passed on its weaker limb in every run, so it
  asserted a refusal that had never once happened.
* **D-67.** A landing the lease had already refused still ran `git push --dry-run`. Nothing in
  the working tree changed, so a filesystem-only harness would have passed it. That is why this
  one watches the network and the process table as well.
* Codex's review of my first design, which reproduced four ways past it in one sitting.

THE INVERSION THAT MAKES IT WORTH HAVING
------------------------------------------
The naive shape is "list the files the fixture should check". That proves nothing about a file
nobody listed — the exact false-negative clause control 64 carries about itself.

So the declaration is a **permission, not a search list**. The whole namespace is snapshotted;
every persistent change is a failure UNLESS it is named in `expected_effects`; and every named
effect MUST occur and match. An unlisted ledger append is caught precisely BECAUSE it was not
listed. Codex's refinement, adopted: a permitted PATH is still too weak, because truncating a
permitted file would pass. What is declared is a postcondition — "exactly one JSONL row was
appended, carrying these fields" — not a licence to touch a path.

WHAT IT RUNS AGAINST, AND WHY NOT THE LIVE TREE
-------------------------------------------------
A fresh copy of the repository, per case. Running a negative control against the live checkout
detects the corruption only after causing it, which is **how D-62 happened**: that fixture wrote
to the real spend ledger 87 times. The image also gets a private HOME and TMPDIR, so a tool that
writes to `~/.config` or `/tmp` is observed rather than escaping the comparison.

`.git` IS INCLUDED in the snapshot. It is not part of the working tree in git's own terminology,
and a command can write objects, move refs, change config or install a hook without a single
tracked file changing.

WHAT IT CANNOT SEE, STATED HERE RATHER THAN DISCOVERED LATER
--------------------------------------------------------------
* **Transient effects.** A file created and deleted between snapshots is invisible. A lock taken
  and released is invisible. Bytes sent and a connection closed are caught only by the trace.
* **Anything outside the image.** The host filesystem is not compared; access to it is neither
  observed nor prevented. `unshare -rn` is not permitted for this user on this host, so there is
  **no network namespace** — the network claim rests entirely on the syscall trace, and if
  `strace` is absent the case reports `UNAVAILABLE` and is NEVER counted as passed.
* **Whether the declaration is honest.** The party declaring what a tool may write is the party
  whose tool writes it. This moves the author's discretion from "what to observe" to "what to
  permit", which is narrower, not zero.
* **That a production run would behave the same.** Credentials are stripped, so a tool that would
  have spent money fails earlier here than it would in production. The claim is "no connection
  was attempted and no canary was launched", never "no paid call would occur".
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

#  Launched instead of the real thing, so an attempt is a fact rather than an inference. Each
#  records its argv and exits non-zero: a refusal path must not be reaching for any of these.
CANARIES = ("codex", "gh", "curl", "wget", "ssh", "scp")

#  Stripped from the child's environment. A refusal path that needs one of these is a refusal
#  path that was about to spend or publish.
SECRET_PREFIXES = ("GH_", "GITHUB_", "OPENAI", "OPENROUTER", "ANTHROPIC", "AWS_", "TOGETHER",
                   "MINIMAX", "HF_", "CODEX")

_LOOPBACK = re.compile(r'inet_addr\("(127\.|0\.0\.0\.0)')


class Unavailable(RuntimeError):
    """The containment or observation this case needs is not present here.

    Raised rather than degraded, because a harness that quietly drops its network check on a
    host without strace reports the same green as one that ran it.
    """


class JsonlAppend:
    """A postcondition, not a permission: exactly `rows` lines appended, each carrying `fields`.

    Codex's objection to permitting a PATH: `action-log.jsonl` merely being allowed to change
    means truncating it passes. So the matcher owns the prior content and checks that it is a
    prefix of the new content, that the count is exact, and that the new rows say what they were
    said to say.
    """

    def __init__(self, rows: int, fields: dict | None = None):
        self.rows, self.fields = rows, fields or {}

    def check(self, before: bytes | None, after: bytes | None) -> str | None:
        if after is None:
            return "the file is gone; an append does not remove a file"
        old = (before or b"").decode("utf-8", "replace").splitlines()
        new = after.decode("utf-8", "replace").splitlines()
        if new[:len(old)] != old:
            return (f"the first {len(old)} line(s) are not the ones that were there; this is a "
                    f"rewrite, not an append")
        added = new[len(old):]
        if len(added) != self.rows:
            return f"{len(added)} row(s) appended, expected exactly {self.rows}"
        for index, line in enumerate(added):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                return f"appended row {index} does not parse ({exc})"
            for key, want in self.fields.items():
                got = row
                for part in key.split("."):
                    got = (got or {}).get(part) if isinstance(got, dict) else None
                if got != want:
                    return f"appended row {index}: {key} is {got!r}, expected {want!r}"
        return None


def snapshot(root: Path) -> dict[str, tuple]:
    """Every entry under `root`: kind, mode, and content hash or link target.

    Not `git status` — that hides ignored files and refreshes the index, which mutates the thing
    being measured.
    """
    out: dict[str, tuple] = {}
    for path in root.rglob("*"):
        rel = str(path.relative_to(root))
        try:
            info = path.lstat()
        except OSError:
            continue
        mode = stat.S_IMODE(info.st_mode)
        if path.is_symlink():
            out[rel] = ("link", mode, os.readlink(path))
        elif path.is_dir():
            out[rel] = ("dir", mode, "")
        else:
            try:
                out[rel] = ("file", mode, hashlib.sha256(path.read_bytes()).hexdigest())
            except OSError as exc:
                out[rel] = ("unreadable", mode, str(exc))
    return out


def _canary_dir(box: Path) -> Path:
    canaries = box / "canaries"
    canaries.mkdir(parents=True, exist_ok=True)
    log = box / "canary-launches.txt"
    for name in CANARIES:
        script = canaries / name
        script.write_text(
            "#!/usr/bin/env bash\n"
            f'printf "%s %s\\n" "{name}" "$*" >> "{log}"\n'
            "exit 97\n", encoding="utf-8")
        script.chmod(0o755)
    return canaries


def _environment(image: Path, home: Path, tmp: Path, canaries: Path) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not any(k.startswith(p) for p in SECRET_PREFIXES)}
    env.update({
        "HOME": str(home), "TMPDIR": str(tmp),
        "XDG_CONFIG_HOME": str(home / ".config"), "XDG_STATE_HOME": str(home / ".local/state"),
        "XDG_CACHE_HOME": str(home / ".cache"), "XDG_DATA_HOME": str(home / ".local/share"),
        "PATH": f"{canaries}:{env.get('PATH', '/usr/bin:/bin')}",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        #  A terminal is a capability. Not providing one is part of the containment.
        "TERM": "dumb",
    })
    return env


def refuses(argv: tuple[str, ...], case: str, *, expected_effects: dict | None = None,
            expect_guard: str = "", expect_exit: int | None = None,
            allow_network: bool = False, setup=None, timeout: int = 120) -> dict:
    """Run `argv` in a fresh image and report what it did. Returns a verdict dict.

    `expected_effects` maps an image-relative path to a matcher. **Everything else in the
    namespace must be byte-identical**, and every named effect must occur and match.
    """
    expected_effects = expected_effects or {}
    box = Path(tempfile.mkdtemp(prefix="effect-"))
    problems: list[str] = []
    try:
        image, home, tmp = box / "image", box / "home", box / "tmp"
        shutil.copytree(REPO_ROOT, image, symlinks=True)
        for directory in (home, tmp):
            directory.mkdir(parents=True, exist_ok=True)
        if setup is not None:
            setup(image)

        canaries = _canary_dir(box)
        before = snapshot(image)
        before_home, before_tmp = snapshot(home), snapshot(tmp)
        prior = {rel: (image / rel).read_bytes()
                 for rel in expected_effects if (image / rel).is_file()}

        trace = shutil.which("strace")
        if trace is None and not allow_network:
            raise Unavailable(
                "strace is not present, and this host does not permit `unshare -rn`, so no "
                "connection attempt can be observed. Reporting UNAVAILABLE rather than a pass.")
        trace_path = box / "trace.txt"
        command = ([trace, "-f", "-e", "trace=connect", "-o", str(trace_path), *argv]
                   if trace else list(argv))

        proc = subprocess.run(command, cwd=image, capture_output=True, text=True,
                              env=_environment(image, home, tmp, canaries),
                              timeout=timeout, shell=False)
        output = (proc.stdout or "") + (proc.stderr or "")

        #  1. IT MUST HAVE REFUSED. Checked first, because everything below is about a refusal.
        if expect_exit is None:
            if proc.returncode == 0:
                problems.append(f"exit 0 — the tool did not refuse")
        elif proc.returncode != expect_exit:
            problems.append(f"exit {proc.returncode}, expected {expect_exit}")
        if expect_guard and not any(
                line.rstrip().endswith(f"[{expect_guard}]") for line in output.splitlines()):
            problems.append(f"guard {expect_guard} did not fire; the refusal came from elsewhere")

        #  2. THE EFFECTS. Everything not declared must be identical.
        after = snapshot(image)
        changed = sorted(set(before) ^ set(after)) + sorted(
            rel for rel in set(before) & set(after) if before[rel] != after[rel])
        undeclared = [rel for rel in changed if rel not in expected_effects]
        for rel in undeclared:
            problems.append(f"UNDECLARED EFFECT on {rel} "
                            f"({before.get(rel, ('absent',))[0]} -> {after.get(rel, ('absent',))[0]})")
        for rel, matcher in expected_effects.items():
            path = image / rel
            why = matcher.check(prior.get(rel), path.read_bytes() if path.is_file() else None)
            if why:
                problems.append(f"declared effect on {rel} did not hold: {why}")
            elif rel not in changed:
                problems.append(f"declared effect on {rel} never happened")

        #  3. OUTSIDE THE IMAGE. A tool that writes to $HOME or $TMPDIR escapes the comparison
        #     above entirely, which is why they are separate and private.
        for label, was, now in (("HOME", before_home, snapshot(home)),
                                ("TMPDIR", before_tmp, snapshot(tmp))):
            escaped = sorted(set(was) ^ set(now))
            if escaped:
                problems.append(f"wrote outside the repository, into {label}: {escaped[:4]}")

        #  4. THE EFFECTS A SNAPSHOT CANNOT SEE. D-67 is the whole reason this section exists.
        launches = (box / "canary-launches.txt")
        if launches.is_file() and launches.read_text().strip():
            problems.append(f"launched an external command on a refused path: "
                            f"{launches.read_text().strip().splitlines()[:3]}")
        connects = []
        if trace and trace_path.is_file():
            for line in trace_path.read_text(errors="replace").splitlines():
                if "connect(" in line and not _LOOPBACK.search(line):
                    connects.append(line.strip()[:120])
        if connects and not allow_network:
            problems.append(f"attempted {len(connects)} non-loopback connection(s) on a refused "
                            f"path: {connects[:2]}")

        return {"case": case, "problems": problems, "exit": proc.returncode,
                "output": output, "changed": changed,
                "network_observed_by": "strace" if trace else "NOTHING"}
    finally:
        shutil.rmtree(box, ignore_errors=True)
