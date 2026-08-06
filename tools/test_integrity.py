#!/usr/bin/env python3
"""Regression tests for the corpus integrity mechanisms.

    python3 tools/test_integrity.py

Every case here is a defect that was live in this repository on 2026-08-06 and
was found by running the attack rather than by reading the code. They are tests
because a repair reported in a commit message is a claim, and a repair that a
build re-runs is a control. D-29's forward requirement is precisely this: **a
check that is available is not a check that runs**, and the way to establish a
claim about an integrity property is to violate the property and confirm the
documented path fails.

Runs against a **temporary clone**, never the working tree, so the tests can
tamper freely and a failure cannot leave the real corpus modified.

Exit status is 0 when every case passes and 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RAW_LOCAL = "corpus/raw/local-round-02/level-4-guarantee-crosslineage-probe-samples.json"
RAW_CONTRIB = "corpus/raw/review-round-02/chatgpt-01.md"

PASSED: list[str] = []
FAILED: list[str] = []


def run(clone: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=clone,
                          capture_output=True, text=True)


def case(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        PASSED.append(name)
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name}{'  — ' + detail if detail else ''}")


TRACKED_ROOTS = ("tools", "corpus", "docs", "record", "predictions", "spec")


def build_reference(tmp: Path) -> Path:
    """One reference repository holding the CURRENT working tree, committed.

    Not `git clone`: this file usually runs inside a git worktree, whose `.git`
    is a file rather than a directory, and `--local` cannot clone that. And a
    clone of HEAD would test the last commit rather than the code in front of
    you, which is exactly backwards for a pre-commit gate.

    So: a fresh repository seeded with the working tree as it stands, committed,
    so that HEAD is the state under test. The lineage check reads
    `HEAD:corpus/MANIFEST.sha256`, so HEAD has to be real and has to match.
    """
    reference = tmp / "reference"
    reference.mkdir()
    for name in TRACKED_ROOTS:
        source = REPO_ROOT / name
        if source.is_dir():
            shutil.copytree(source, reference / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    git = ["git", "-C", str(reference)]
    subprocess.run([*git, "init", "--quiet"], check=True, capture_output=True)
    subprocess.run([*git, "add", "-A"], check=True, capture_output=True)
    subprocess.run([*git, "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "--quiet", "-m", "state under test"],
                   check=True, capture_output=True)
    return reference


def fresh(tmp: Path, n: int, reference: Path) -> Path:
    """A clean copy per case, so cases cannot contaminate each other."""
    clone = tmp / f"c{n}"
    shutil.copytree(reference, clone)
    return clone


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        reference = build_reference(tmp)
        n = 0

        def nxt() -> Path:
            nonlocal n
            n += 1
            return fresh(tmp, n, reference)

        print("baseline")
        c = nxt()
        case("clean clone: rebuild succeeds",
             run(c, "tools/rebuild.py").returncode == 0)

        print("\nD-29 — tampered raw material must stop the build")
        c = nxt()
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        r = run(c, "tools/rebuild.py")
        case("solicitation-family tamper rejected", r.returncode == 1)
        case("names the modified file", "MODIFIED" in r.stdout and "local-round-02" in r.stdout)

        c = nxt()
        (c / RAW_CONTRIB).write_bytes((c / RAW_CONTRIB).read_bytes() + b"\n")
        case("contribution-family tamper rejected",
             run(c, "tools/rebuild.py").returncode == 1)

        print("\nthe manifest must not re-anchor silently")
        c = nxt()
        (c / "corpus/raw/local-round-02/NEW.md").write_text("new material\n")
        r = run(c, "tools/rebuild.py")
        case("unanchored new file rejected by the default path", r.returncode == 1)
        case("reports UNANCHORED", "UNANCHORED" in r.stdout)
        r = run(c, "tools/build_manifest.py", "corpus/raw/", "--add")
        case("--add anchors the new file", r.returncode == 0)
        case("--add anchors exactly one", "anchored 1 new artifact" in r.stdout)

        c = nxt()
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        case("--add refuses when a recorded artifact was modified",
             run(c, "tools/build_manifest.py", "corpus/raw/", "--add").returncode == 1)

        print("\nlaundering — the manifest cannot vouch for itself")
        c = nxt()
        man = c / "corpus/MANIFEST.sha256"
        man.write_text("".join(l for l in man.read_text().splitlines(keepends=True)
                               if "level-4-guarantee" not in l))
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        r = run(c, "tools/build_manifest.py", "corpus/raw/", "--add")
        case("dropping a manifest line does not make a modified file look new",
             r.returncode == 1)
        case("reports DROPPED against HEAD", "DROPPED" in r.stdout)

        c = nxt()
        (c / "corpus/MANIFEST.sha256").unlink()
        case("deleting the whole manifest does not let --add re-anchor the tree",
             run(c, "tools/build_manifest.py", "corpus/raw/", "--add").returncode == 1)

        c = nxt()
        man = c / "corpus/MANIFEST.sha256"
        man.write_text("".join(l for l in man.read_text().splitlines(keepends=True)
                               if "level-4-guarantee" not in l))
        (c / RAW_LOCAL).unlink()
        case("dropping a line AND its file does not verify clean",
             run(c, "tools/build_manifest.py", "corpus/raw/").returncode == 1)

        print("\nmode selection must never be guessed at")
        c = nxt()
        for combo in (("--verify", "--add"), ("--verify", "--force-rewrite"),
                      ("--add", "--force-rewrite")):
            case(f"rejects {' '.join(combo)}",
                 run(c, "tools/build_manifest.py", "corpus/raw/", *combo).returncode == 2)
        case("rejects an unknown flag",
             run(c, "tools/build_manifest.py", "corpus/raw/", "--nope").returncode == 2)

        print("\ndeterminism — the signal the whole commit gate depends on")
        c = nxt()
        run(c, "tools/rebuild.py")
        first = (c / "docs/index.html").read_bytes()
        run(c, "tools/rebuild.py")
        case("rebuild is byte-identical on an unchanged repository",
             (c / "docs/index.html").read_bytes() == first)
        case("rebuild leaves no diff on an unchanged repository",
             subprocess.run(["git", "diff", "--quiet"], cwd=c).returncode == 0)

        print("\ncapture must still work, and must not leave partial artifacts")
        c = nxt()
        reply = c / "reply.md"
        reply.write_text("A response, for regression purposes.\n")
        r = run(c, "tools/capture_response.py", "--round", "regression-test",
                "--response", str(reply), "--prompt", "record/review-round-01-prompt.md",
                "--identity", "RegressionProbe", "--provider", "none",
                "--version-unknown", "test", "--sampling-unknown", "test",
                "--effort-unknown", "test", "--system-instructions-unknown", "test",
                "--captured-utc", "2026-08-06T00:00:00Z", "--phase", "informed",
                "--captured-by", "regression test")
        case("capture succeeds", r.returncode == 0, r.stderr.strip()[:200])
        case("capture anchored its own new file",
             run(c, "tools/build_manifest.py", "corpus/raw/").returncode == 0)

        print("\nthe register must count itself correctly")
        c = nxt()
        case("register self-description consistent",
             run(c, "tools/check_register.py").returncode == 0)
        reg = c / "corpus/deficiencies.md"
        # Derive the declared count instead of hardcoding it. This case previously
        # searched for the literal "**30 entries**"; filing D-31 and D-32 made that
        # string absent, so the tamper silently became a no-op and the case tested
        # nothing. It would have failed loudly here -- but only because the assertion
        # is "the build must fail". A fixture that goes stale in the passing direction
        # is the shape this suite exists to catch.
        declared = re.search(r"\*\*Status:\*\*\s*open\s*—\s*\*\*(\d+) entries\*\*", reg.read_text())
        case("count-tamper fixture still matches the register", declared is not None)
        if declared:
            wrong = f"**{int(declared.group(1)) - 1} entries**"
            reg.write_text(reg.read_text().replace(declared.group(0),
                           declared.group(0).replace(f"**{declared.group(1)} entries**", wrong)))
            case("a wrong declared count fails the build",
                 run(c, "tools/rebuild.py").returncode == 1)

        print("\nD-33 — every generator that writes under docs/ must be in the build")
        c = nxt()
        cap = c / "docs/capture/index.html"
        cap.write_text(cap.read_text() + "<!-- hand edit -->")
        # COMMIT the edit. That is the scenario CI actually faces: it checks out a
        # commit and asks whether the committed page equals a regeneration. An
        # uncommitted hand edit is not the threat -- rebuild.py simply overwrites it
        # and the diff comes back clean, which is why this case first asserted the
        # wrong thing and passed for the wrong reason until it was run.
        subprocess.run(["git","-c","user.name=t","-c","user.email=t@t",
                        "commit","-qam","hand edit"], cwd=c, capture_output=True)
        run(c, "tools/rebuild.py")
        case("a committed hand-edited capture page is caught by the CI diff gate",
             subprocess.run(["git","diff","--quiet","--","docs/"], cwd=c).returncode == 1)

        c = nxt()
        # The real 2026-08-06 failure: edit a prompt the capture page embeds, and the
        # page's committed prompt_sha256 silently stops matching the file it names.
        # Before build_capture_ui.py was in rebuild.py, this left NO diff at all --
        # rebuild exited 0, git status was clean, and CI's byte-equality gate passed.
        prompt = c / "record/review-round-03-prompt.md"
        prompt.write_text(prompt.read_text() + "\nAn edit that changes the digest.\n")
        run(c, "tools/rebuild.py")
        case("editing an embedded prompt leaves a diff in the capture page",
             subprocess.run(["git","diff","--quiet","--","docs/capture/"],
                            cwd=c).returncode == 1)
        digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
        case("the regenerated page carries the prompt's real digest",
             digest in (c / "docs/capture/index.html").read_text())

        print("\nD-32 — colliding identifiers must fail the build")
        c = nxt()
        reg = c / "corpus/deficiencies.md"
        # Reproduce the actual 2026-08-06 collision: Track B's entry filed as D-29,
        # the number Track A had concurrently used.
        reg.write_text(reg.read_text().replace(
            "### D-31 — External reviewers", "### D-29 — External reviewers", 1))
        r = run(c, "tools/rebuild.py")
        case("duplicate D-NN fails the build", r.returncode == 1)
        case("names the colliding id, not just a bad count", "duplicate entry id: D-29" in r.stdout)

        c = nxt()
        pred = c / "predictions" / "predictions.json"
        data = json.loads(pred.read_text())
        entries = data["predictions"] if isinstance(data, dict) else data
        entries.append(dict(entries[0]))
        pred.write_text(json.dumps(data, indent=2))
        r = run(c, "tools/rebuild.py")
        case("duplicate P-NNNN fails the build", r.returncode == 1)
        case("names the colliding prediction id",
             "duplicate prediction id" in r.stdout)

        c = nxt()
        # A prediction with no id at all: the loop that collects ids would otherwise
        # raise KeyError, and a checker that crashes is not a checker that failed.
        pred = c / "predictions" / "predictions.json"
        data = json.loads(pred.read_text())
        entries = data["predictions"] if isinstance(data, dict) else data
        entries[0].pop("id", None)
        pred.write_text(json.dumps(data, indent=2))
        r = run(c, "tools/rebuild.py")
        case("a prediction with no id fails cleanly", r.returncode == 1)
        case("reports the missing id rather than a traceback",
             "have no id" in r.stdout and "Traceback" not in r.stdout + r.stderr)

    print()
    total = len(PASSED) + len(FAILED)
    if FAILED:
        print(f"FAILED — {len(FAILED)} of {total}:")
        for name in FAILED:
            print(f"  {name}")
        return 1
    print(f"All {total} integrity cases pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
