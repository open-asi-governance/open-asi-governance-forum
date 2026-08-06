#!/usr/bin/env python3
"""Reject any commit that modifies or deletes raw material already committed.

    python3 tools/check_raw_append_only.py <base> <tip>

"The raw record is never edited after commit" is this corpus's central claim.
Until 2026-08-06 nothing enforced the "after commit" half of it.

WHY THE MANIFEST CANNOT DO THIS, which is the whole reason this file exists.
`corpus/MANIFEST.sha256` proves the raw tree matches its recorded hashes **at the
tip**. It compares the working tree against the manifest as both stand right now.
So a single commit that edits a raw file *and* re-anchors the manifest around the
new bytes is entirely self-consistent, and every check in this repository passes.

Demonstrated before this file was written, on a clone:

    append a byte to a committed raw sample
    python3 tools/build_manifest.py corpus/raw/ --force-rewrite
    git commit -am "edit raw and re-anchor"
    python3 tools/build_manifest.py corpus/raw/      -> exit 0, "verified"

The tip is clean because the tip was made clean. The evidence that anything
happened exists only in history, so history is where it has to be checked. A hash
anchor establishes byte-identity between a manifest and a tree; it says nothing
about whether that tree is the one that was originally committed.

This is a check on the SHAPE of the diff, not on content:

  additions            allowed -- this is how material enters the corpus
  modification         rejected
  deletion             rejected
  rename, retype       rejected -- a rename is a deletion under the old path, and
                       citations in this corpus are by path plus hash

Merge commits are compared against their FIRST parent, so material arriving via a
merge is judged the same way it would have been on the branch.

WHAT THIS DOES NOT DO. It cannot see edits made before the range it is given, it
cannot survive a force-push that discards the offending commits (that is a
ruleset/branch-protection concern, not a script one), and it cannot detect false
provenance in material that was never edited. Byte-history, not truth.

Exit status is 0 when the range is append-only and 1 otherwise.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = "corpus/raw/"

# M modified, D deleted, R renamed, T type-changed, U unmerged, X unknown, B broken.
# 'A' (added) is deliberately absent.
REJECTED_FILTER = "MDRTUXB"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT,
                          capture_output=True, text=True)


def exists(ref: str) -> bool:
    return git("cat-file", "-e", f"{ref}^{{commit}}").returncode == 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2].strip())
        print("usage: check_raw_append_only.py <base> <tip>")
        return 2

    base, tip = argv
    if not exists(tip):
        print(f"tip is not a commit: {tip}")
        return 1

    # A branch's first push and a force-push report an all-zero or unreachable base.
    # Fall back to the tip's first parent and SAY SO, rather than silently checking
    # nothing -- a check that quietly narrows its own scope is this repository's
    # most-filed defect.
    if not base or set(base) == {"0"} or not exists(base):
        parent = f"{tip}^"
        if not exists(parent):
            print("Root commit; no prior state to compare against.")
            return 0
        print(f"No usable base ({base!r}); checking the tip commit only.")
        base = parent

    revs = git("rev-list", "--reverse", f"{base}..{tip}").stdout.split()
    if not revs:
        print("No new commits in range.")
        return 0

    violations = 0
    for commit in revs:
        parent = git("rev-parse", f"{commit}^1").stdout.strip()
        if not parent:
            continue
        changed = git("diff", "--name-status", f"--diff-filter={REJECTED_FILTER}",
                      parent, commit, "--", RAW).stdout.strip()
        if changed:
            violations += 1
            subject = git("log", "-1", "--format=%s", commit).stdout.strip()
            print(f"\nREJECTED  {commit[:12]}  {subject}")
            for line in changed.splitlines():
                print(f"          {line}")

    if violations:
        print(f"\nFAILED — {violations} commit(s) changed or removed committed raw material.")
        print("Raw material is corrected by SUPERSEDING artifacts that cite the original")
        print("by hash, never by editing it. If a withdrawal is genuinely intended, it is")
        print("a custodian action and must be recorded as one.")
        return 1

    print(f"Raw material is append-only across {len(revs)} commit(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
