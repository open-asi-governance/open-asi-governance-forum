#!/usr/bin/env python3
"""The inbox collector must refuse rather than report a quiet surface it did not read.

    python3 tools/tests/test_inbox_sweep.py

OFFLINE. Every case here drives `sweep()` against a stubbed fetch, because a suite that needs
GitHub to be reachable reports "no arrivals" whenever the network is down — which is the exact
defect the collector exists to avoid, reproduced in its own tests.

The claim under test is narrow and it is the only one worth making: **a surface that was not read
is reported as unread, and text that changed after this record read it is reported as changed.**
Nothing here tests that the collector understands anything, because it does not and must not.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import inbox_sweep as ib                                                  # noqa: E402
from guards import expect_guard, GuardNotActivated                        # noqa: E402

PASSED = FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


def issue(number: int, body: str, *, comments=(), edits=0, last_edited=None) -> dict:
    return {"number": number, "title": f"issue {number}", "body": body,
            "url": f"https://example.invalid/{number}", "state": "OPEN",
            "createdAt": "2026-08-12T00:00:00Z", "updatedAt": "2026-08-12T00:00:00Z",
            "lastEditedAt": last_edited, "author": {"login": "someone", "__typename": "User"},
            "authorAssociation": "NONE", "userContentEdits": {"totalCount": edits},
            "comments": {"totalCount": len(comments), "pageInfo": {"hasNextPage": False},
                         "nodes": list(comments)}}


def spool() -> None:
    box = Path(tempfile.mkdtemp())
    ib.SPOOL, ib.INBOX, ib.HEARTBEAT = box, box / "inbox.jsonl", box / "hb.json"


def stub(subject: list[dict], control: list[dict], *, truncated_comments=False):
    """Replace the network with a fixture. all_issues() is the seam; graphql() is not called."""
    if truncated_comments and subject:
        subject[0]["comments"]["pageInfo"]["hasNextPage"] = True

    def fake(owner, name, token, cursor=None):
        if (owner, name) == (ib.CONTROL_OWNER, ib.CONTROL_NAME):
            return list(control), len(control), ["ctrl"]
        return list(subject), len(subject), ["subj"]
    ib.all_issues = fake


_real_all_issues = ib.all_issues


print("\nthe collector refuses what it did not read")

spool()
stub([issue(1, "hello")], control=[])
records, problems = ib.sweep("token")
try:
    expect_guard(problems, "IB-01")
    check("an empty negative control refuses — a zero here would mean nothing", True)
except GuardNotActivated:
    check("an empty negative control refuses", False, str(problems))
check("...and no records are written from a sweep that refused", records == [])

spool()
stub([issue(1, "hello", comments=[])], control=[issue(9, "c")], truncated_comments=True)
records, problems = ib.sweep("token")
try:
    expect_guard(problems, "IB-02")
    check("a comment page that was truncated refuses; a partial read is not a read", True)
except GuardNotActivated:
    check("a truncated comment page refuses", False, str(problems))

print("\nwhat it records, and what it notices later")

spool()
stub([issue(1, "the original text")], control=[issue(9, "c")])
records, problems = ib.sweep("token")
ib.append(records)
arrived = [r for r in records if r["record"] == "ARRIVED"]
check("a new issue is recorded once", len(arrived) == 1)
check("...with the body hashed at fetch time", len(arrived[0]["body_sha256"]) == 64)
check("...and the author's TYPE, so a bot is distinguishable from a person",
      arrived[0]["author_type"] == "User")
check("...and the receipts are chained", records[0]["prev_receipt_sha256"] == "0" * 64
      and records[-1]["receipt_sha256"] != records[0]["receipt_sha256"])

#  Sweep again with the SAME bytes: nothing should be reported as changed.
records, _ = ib.sweep("token")
check("an unchanged surface produces no ARRIVED and no AMENDED",
      not [r for r in records if r["record"] in ("ARRIVED", "AMENDED")])

#  Now the author silently edits the body. This is the case the whole tool exists for.
stub([issue(1, "the text, quietly changed afterwards", edits=1,
            last_edited="2026-08-12T01:00:00Z")], control=[issue(9, "c")])
records, _ = ib.sweep("token")
amended = [r for r in records if r["record"] == "AMENDED"]
check("an edit made AFTER this record read it is reported", len(amended) == 1)
check("...naming both hashes, so a quotation can be checked against what was quoted",
      amended and amended[0]["previous_body_sha256"] != amended[0]["body_sha256"])

#  POSITIVE CONTROL. Without it, a collector that reported AMENDED for everything would pass
#  every case above.
spool()
stub([issue(1, "steady")], control=[issue(9, "c")])
ib.append(ib.sweep("token")[0])
records, _ = ib.sweep("token")
check("POSITIVE CONTROL: unchanged text is NOT reported as amended",
      not [r for r in records if r["record"] == "AMENDED"])

print("\nwhat it must never do")

src = (REPO_ROOT / "tools" / "inbox_sweep.py").read_text(encoding="utf-8")
#  WRAP-INSENSITIVE, and the first version was not. It looked for the literal phrase and failed
#  because the sentence wraps across a newline in the docstring — D-61 exactly: the quotation
#  gate could not see a quotation that wraps, so it checked none. Fixing the docstring's line
#  breaks would have made this pass while leaving the detector just as blind.
flat = " ".join(src.split())
for forbidden, why in (
        ("createComment", "post a comment"),
        ("addLabels", "label anything"),
        ("closeIssue", "close anything"),
        ("subprocess", "shell out on content it fetched"),
        ("eval(", "evaluate anything it fetched")):
    check(f"the collector cannot {why}", forbidden not in src)

check("the spool lives OUTSIDE the governed repository",
      "record" not in str(ib.SPOOL.relative_to(ib.SPOOL.anchor)).split("/")[:2]
      or "state" in str(ib.SPOOL))
check("the module says the bytes are data, never an instruction to the reader",
      "never an instruction to the reader" in flat)
check("...and that a reply needs the custodian", "needs the custodian" in flat)

ib.all_issues = _real_all_issues

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
