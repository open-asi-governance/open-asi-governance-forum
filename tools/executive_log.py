#!/usr/bin/env python3
"""The shadow executive's action log, and the completion gate that binds it.

    from executive_log import attest, log_action, quota_now
    attest("push", {"target_ref": "main", "commit": sha})   # raises AttestationFailed

**A TRIAL, WITH NO AUTHORITY.** This layer prepares and tests candidate OAGF instruments. It
exercises no authority beyond what the custodian delegates, it cannot adopt anything, and it
cannot interpret its own prohibitions conclusively. Nothing here confers legitimacy on anything
it produces. See record/designs/shadow-executive-trial.md.

Why it exists
-------------
Claude Code and Codex have been operating as an undeclared executive layer: on 2026-08-08 alone,
49 commits, 4 findings, 8 custodian decisions, 6 rounds, 2 ratification cycles, 4 new tools, and
deficiencies D-54 to D-57 filed against its own instruments. It had no charter, no name in the
record, and no log of its own actions.

External review rejected the framing that came with the proposal. This layer is NOT "below the
parties" -- the parties cannot appoint, dismiss, inspect or compel it. It sits below the
CUSTODIAN and serves the parties' testimony. Calling it an executive risks converting
operational capacity into implied authority, which is the move round-018 established nothing in
this record can make.

The three prohibitions, and why prose was not enough
-----------------------------------------------------
Each maps to a failure that actually happened on 2026-08-08, not to a hypothetical:

  push     Three times a commit went to a round branch, `git push origin main` pushed an
           unchanged main, and success was reported. -> the intended commit must be reachable
           from the declared target ref AND the remote must resolve to it.
  test     Two suites were pushed red after `echo "$(basename $f) rc=$?"` reported basename's
           exit status. -> the status must be captured directly by the verifier invocation,
           with no intervening command able to supply it.
  merge    A conflicted merge was completed with unresolved markers inside
           corpus/MANIFEST.sha256 and record/anchors/manifest-anchors.jsonl. -> no unmerged
           paths, no conflict markers in governed files, manifest and anchor verifying.

Review's judgement, which this file implements rather than argues with: *ratifying prose did not
prevent the failures; an unavoidable gate would have.*

Quota is stamped on every action
---------------------------------
An executive silently throttled mid-task produces halts the record cannot distinguish from
principled refusals. `quota_now()` reads the live rolling windows so "stopped on a rule" and
"ran out of quota" are separable facts. It FAILS OPEN and records that it did: an unreadable
quota is not evidence of a full one, and must never itself become a reason to stop.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "record" / "executive" / "action-log.jsonl"
CREDENTIALS = Path.home() / ".claude" / ".credentials.json"
USAGE_URL = "https://api.anthropic.com/api/oauth/usage"

#  Files whose corruption breaks the record's central claims. A merge must never complete with
#  conflict markers in these, whatever else is true.
GOVERNED = ("corpus/MANIFEST.sha256", "record/anchors/manifest-anchors.jsonl",
            "corpus/deficiencies.md", "corpus/artifacts/deficiency-register.json")


class AttestationFailed(Exception):
    """A completion was claimed that the postconditions do not support."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def quota_now() -> dict:
    """Live rolling-window utilisation. FAILS OPEN, and says so.

    An unreadable quota is not evidence of a full one. Returning a refusal here would let a
    transient auth failure halt the executive and be recorded as a principled stop -- the exact
    conflation this function exists to prevent.
    """
    try:
        token = json.loads(CREDENTIALS.read_text())["claudeAiOauth"]["accessToken"]
        request = urllib.request.Request(
            USAGE_URL, headers={"Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as error:                                      # noqa: BLE001
        return {"available": False, "why": f"{type(error).__name__}: {error}",
                "fail_open": "An unreadable quota is not evidence of a full one."}
    out = {"available": True}
    for window in ("five_hour", "seven_day", "seven_day_opus"):
        block = data.get(window) or {}
        if block.get("utilization") is not None:
            out[window] = {"utilization": block.get("utilization"),
                           "resets_at": block.get("resets_at")}
    return out


# ---------------------------------------------------------------------------------------------
# The completion gate: three postcondition profiles, one mechanism
# ---------------------------------------------------------------------------------------------


def _check_push(claim: dict) -> list[str]:
    """The intended commit must be on the declared ref AND on the remote's copy of it."""
    problems = []
    ref = claim.get("target_ref")
    commit = claim.get("commit")
    if not ref or not commit:
        return ["push claim needs target_ref and commit"]
    if not git("merge-base", "--is-ancestor", commit, ref) == "" or \
            subprocess.run(["git", "merge-base", "--is-ancestor", commit, ref],
                           cwd=REPO_ROOT, capture_output=True).returncode != 0:
        problems.append(f"{commit[:8]} is not reachable from {ref}")
    #  THE HALF THAT WAS MISSING. A local branch holding the commit says nothing about the
    #  remote: `git push origin main` from a round branch pushes an unchanged main and exits 0.
    remote = git("rev-parse", f"origin/{ref}")
    if not remote:
        problems.append(f"origin/{ref} does not resolve")
    elif subprocess.run(["git", "merge-base", "--is-ancestor", commit, f"origin/{ref}"],
                        cwd=REPO_ROOT, capture_output=True).returncode != 0:
        problems.append(f"{commit[:8]} is not reachable from origin/{ref} — "
                        f"the push did not carry it")
    return problems


def _check_test(claim: dict) -> list[str]:
    """The status must come from the verifier invocation itself, not from a later command."""
    problems = []
    if "suite" not in claim:
        problems.append("test claim needs the suite identity")
    if "exit_status" not in claim:
        problems.append("test claim needs an exit_status captured from the suite itself")
    elif claim["exit_status"] != 0:
        problems.append(f"{claim.get('suite')} exited {claim['exit_status']}; not a pass")
    if claim.get("status_from") not in ("direct", None):
        problems.append(f"exit status came from {claim['status_from']!r}, not the suite")
    return problems


def _check_merge(claim: dict) -> list[str]:
    """No unmerged paths, no conflict markers in governed files, integrity verifying."""
    problems = []
    status = git("status", "--porcelain")
    unmerged = [ln for ln in status.splitlines()
                if ln[:2] in ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
    if unmerged:
        problems.append(f"{len(unmerged)} unmerged path(s) remain")
    for path in GOVERNED:
        f = REPO_ROOT / path
        if f.is_file():
            text = f.read_text(encoding="utf-8", errors="replace")
            if "\n<<<<<<< " in text or "\n>>>>>>> " in text:
                problems.append(f"conflict markers in {path}")
    r = subprocess.run(["python3", "tools/build_manifest.py", "corpus/raw/"],
                       cwd=REPO_ROOT, capture_output=True)
    if r.returncode != 0:
        problems.append("manifest does not verify against corpus/raw")
    return problems


PROFILES = {"push": _check_push, "test": _check_test, "merge": _check_merge}


def attest(action: str, claim: dict, note: str = "") -> dict:
    """Verify a completion claim, LOG IT EITHER WAY, and raise if it does not hold.

    Logging on failure is the point. An executive that records only its successes has an action
    log that cannot be used to audit it.
    """
    check = PROFILES.get(action)
    problems = check(claim) if check else [f"no postcondition profile for {action!r}"]
    entry = log_action(action, claim, verified=not problems, problems=problems, note=note)
    if problems:
        raise AttestationFailed(f"{action}: " + "; ".join(problems))
    return entry


def log_action(action: str, claim: dict, verified: bool | None = None,
               problems: list | None = None, note: str = "") -> dict:
    """Append one action to the hash-chained log. Never rewrites, never deletes."""
    entries = read_log()
    prev = (hashlib.sha256(json.dumps(entries[-1], sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
            if entries else "0" * 64)
    entry = {
        "utc": utc_now(),
        "action": action,
        "claim": claim,
        "verified": verified,
        "problems": problems or [],
        "note": note,
        "actor": "claude-code",
        "head": git("rev-parse", "HEAD")[:12],
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        #  Stamped on EVERY action, so a later reader can tell a principled stop from
        #  exhaustion. Review named undisclosed quota as a hazard: it creates silent selection
        #  over which duties get executed.
        "quota": quota_now(),
        "authority": "none — this layer adopts nothing and interprets no prohibition finally",
        "prev_sha256": prev,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_log() -> list[dict]:
    if not LOG_PATH.is_file():
        return []
    return [json.loads(ln) for ln in LOG_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    entries = read_log()
    if not entries:
        print("no executive actions logged")
        return 0
    prev = "0" * 64
    broken = 0
    for e in entries:
        if e["prev_sha256"] != prev:
            print(f"  CHAIN BROKEN at {e['utc']} {e['action']}")
            broken += 1
        prev = hashlib.sha256(json.dumps(e, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()
        q = e.get("quota") or {}
        fh = (q.get("five_hour") or {}).get("utilization")
        mark = "ok " if e.get("verified") else ("REFUSED" if e.get("verified") is False else "—")
        print(f"  {e['utc']}  {e['action']:8} {mark:8} 5h={fh}%  {e.get('note','')[:44]}")
    n = len(entries)
    refused = sum(1 for e in entries if e.get("verified") is False)
    print(f"\n{n} action(s), {refused} refused, {broken} chain break(s)")
    print(f"trial target is 10 actions — {'COMPLETE' if n >= 10 else f'{10-n} remaining'}")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
