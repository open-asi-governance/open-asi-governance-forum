#!/usr/bin/env python3
"""Run every gate, then commit, push, verify and attest — or refuse without touching git.

    python3 tools/land.py -m "the commit message"
    python3 tools/land.py -F message.txt
    python3 tools/land.py --check-only          # run the gates, change nothing

**DETERMINISTIC.** No LLM, no network beyond the push itself.

Why this exists
---------------
Landing work is five gates and four git steps in a fixed order, each individually skippable, and
skipping one is silent. The record of doing it by hand:

* `run_all.py | tail -2` printed `All 16 suites passed` from an inner suite while the runner
  exited **1**. The rule against reading a verdict from output text was already written down, in
  a file loaded at the start of every session, and `tail` is still what you reach for.
* `echo "$(basename $f) rc=$?"` reported *basename's* status. Two red suites were pushed.
* Three commits went to a round branch while `git push origin main` pushed an unchanged main and
  reported success.
* A conflicted merge was completed blind, leaving conflict markers inside `MANIFEST.sha256` and
  the anchor log — the two files that make the record's central claim checkable.
* `check_quotations.py` caught a bad quotation on 2026-08-10 only because `rebuild.py` happened
  to be run first. Nothing required it.

So the order stops being a habit and becomes a program. **Every gate's status is taken from its
own exit code**, captured directly — never parsed out of its output, which is what failed.

What it refuses on
-------------------
Any gate exiting non-zero; an expired lease; a detached HEAD; unmerged paths; conflict markers in
a governed file; a push whose commit is not reachable from `origin/main` afterwards. Refusal
happens **before** `git commit` wherever possible, so a rejected run leaves the tree exactly as it
was rather than a commit needing to be undone.

What it cannot establish
-------------------------
* **That the gates test the right thing.** All green means the checks that exist passed. The
  quotation checker verifies a quotation appears in the corpus, not that a document's argument is
  sound; `check_executive_context.py` verifies identity, not truth — it passed on a pinned file
  containing a claim already proven false.
* **That the commit message is accurate.** Nothing here reads it.
* **That this was the right work to land.**
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import executive_lease as lease                                          # noqa: E402
import executive_log as ex                                              # noqa: E402

#  Ordered. `rebuild` first because it regenerates what the later checks read; the quotation
#  check runs inside it and again here, because relying on that coincidence is what happened.
GATES = (
    ("rebuild", ["python3", "tools/rebuild.py"]),
    ("tests", ["python3", "tools/tests/run_all.py"]),
    ("quotations", ["python3", "tools/check_quotations.py"]),
    ("context-pins", ["python3", "tools/check_executive_context.py"]),
    ("lease", ["python3", "tools/executive_lease.py"]),
)

GOVERNED = ("corpus/MANIFEST.sha256", "record/anchors/manifest-anchors.jsonl",
            "record/deficiencies.md", "record/deficiency-register.json")


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a command and return ITS OWN exit status. The status is never inferred from output."""
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def preflight() -> list[str]:
    """Everything that must hold before git is touched at all."""
    problems = []
    try:
        lease.require("commit")
    except lease.LeaseExpired as expired:
        problems.append(f"lease: {expired}")
    code, branch = run(["git", "branch", "--show-current"])
    branch = branch.strip()
    if not branch:
        problems.append("HEAD is detached; a commit here is not on any branch")
    code, status = run(["git", "status", "--porcelain"])
    unmerged = [ln for ln in status.splitlines() if ln[:2] in
                ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
    if unmerged:
        problems.append(f"{len(unmerged)} unmerged path(s) remain")
    for rel in GOVERNED:
        path = REPO_ROOT / rel
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            if "\n<<<<<<< " in text or "\n>>>>>>> " in text:
                problems.append(f"conflict markers in {rel}")
    return problems


def gates() -> tuple[bool, list[tuple[str, int, str]]]:
    results = []
    for name, cmd in GATES:
        code, output = run(cmd)
        results.append((name, code, output))
    return all(code == 0 for _, code, _ in results), results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("-m", "--message", help="commit message")
    parser.add_argument("-F", "--file", help="file holding the commit message")
    parser.add_argument("--check-only", action="store_true", help="run the gates, change nothing")
    parser.add_argument("--branch", default="main", help="branch to push (default main)")
    parser.add_argument("--note", default="", help="note recorded on both attestations")
    args = parser.parse_args()

    problems = preflight()
    if problems:
        for p in problems:
            print(f"  REFUSED  {p}", file=sys.stderr)
        return 2

    print("  gates:")
    ok, results = gates()
    for name, code, output in results:
        mark = "\033[32mpass\033[0m" if code == 0 else "\033[31mFAIL\033[0m"
        print(f"    {mark}  {name}  (exit {code})")
    if not ok:
        for name, code, output in results:
            if code:
                print(f"\n--- {name} exit {code} ---\n{output[-2500:]}", file=sys.stderr)
        print("\nREFUSED: a gate failed. Nothing was committed.", file=sys.stderr)
        return 1
    if args.check_only:
        print("\n  all gates green; --check-only, so nothing was committed")
        return 0
    if not (args.message or args.file):
        parser.error("-m or -F is required unless --check-only")

    code, _ = run(["git", "add", "-A"])
    commit = ["git", "commit", "-q"] + (["-F", args.file] if args.file else ["-m", args.message])
    code, output = run(commit)
    if code != 0:
        print(f"  REFUSED: git commit exited {code}\n{output}", file=sys.stderr)
        return 1
    _, sha = run(["git", "rev-parse", "HEAD"])
    sha = sha.strip()
    code, output = run(["git", "push", "origin", args.branch])
    if code != 0:
        print(f"  push exited {code}\n{output}", file=sys.stderr)

    #  BOTH attestations, and they verify against the remote ref rather than the push's exit
    #  status -- a push can exit 0 having carried nothing, which is how an unchanged main was
    #  reported as a successful push three times.
    suite_code = dict((n, c) for n, c, _ in results)["tests"]
    ex.attest("test", {"suite": "tools/tests/run_all.py", "exit_status": suite_code,
                       "status_from": "direct"}, note=args.note or "landed by land.py")
    try:
        ex.attest("push", {"target_ref": args.branch, "commit": sha},
                  note=args.note or "landed by land.py")
    except ex.AttestationFailed as failed:
        print(f"  ATTESTATION FAILED: {failed}", file=sys.stderr)
        return 1
    print(f"\n  landed {sha[:12]} on {args.branch}, gates green, both attestations filed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
