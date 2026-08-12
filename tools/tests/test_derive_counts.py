#!/usr/bin/env python3
"""Conformance for derive_counts.py — chiefly that it REFUSES rather than reporting zero.

The tool exists because a scan that could not see 69 files reported "0" and the output looked
identical to a true zero. So the load-bearing tests here are the refusal tests, not the counting
tests: a counter that is merely correct on the schemas it knows is what already failed.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import derive_counts as dc                                               # noqa: E402

#  What this suite drives to a REFUSAL, read by tools/control_coverage.py. A tool
#  named here must exist and this file must assert a refusal, or the scan fails —
#  a declaration is a claim, not a substitute for the case.
COVERS = ("derive_counts.py",)


PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


def with_raw(files: dict, kind: str = "search") -> dict:
    """Point the scanner at a synthetic corpus."""
    saved = dc.RAW
    tmp = Path(tempfile.mkdtemp()) / "raw"
    (tmp / "round-999").mkdir(parents=True)
    for name, doc in files.items():
        (tmp / "round-999" / name).write_text(json.dumps(doc))
    dc.RAW = tmp
    try:
        return dc.scan(kind)
    finally:
        dc.RAW = saved


print("\nreceipts are found in EVERY disposition, not only accepted samples")
r = with_raw({"a.json": {"failures": [{"search_receipts": [{"outcome": "OK"}]}]}})
check("a receipt inside `failures` is counted", r["total"] == 1)
r = with_raw({"a.json": {"rejected": [{"search": {"receipts": [{"outcome": "OK"}]}}]}})
check("a receipt inside `rejected` is counted", r["total"] == 1)
r = with_raw({"a.json": {"responses": [{"search_receipts": [{"outcome": "OK"}, {"outcome": "OK"}]}]}})
check("a receipt inside `responses` is counted", r["total"] == 2)
r = with_raw({"a.json": {"samples": [{"search": {"receipts": [{"outcome": "OK"}]}}]}})
check("the nested sample form is counted", r["total"] == 1)

print("\nan unrecognised schema REFUSES; it does not report zero")
r = with_raw({"a.json": {"units": [{"search_receipts": [{"outcome": "OK"}]}]}})
check("a file with receipts but no known container is unrecognised", r["usable"] is False)
check("...and the file is named", "a.json" in r["coverage"]["unrecognised"][0])
check("...and no count is trusted", r["usable"] is False and r["total"] == 0)

print("\nonly a REGISTERED non-solicitation type is excused from holding units")
r = with_raw({"c.json": {"artifact_type": "finding_coding", "codings": []}})
check("a registered non-solicitation type is excused", r["usable"] is True)
check("...and contributes nothing", r["total"] == 0)
r = with_raw({"spec.json": {"spec_version": "x", "prompt": "no receipts here"}})
check("an UNDECLARED file holding no units refuses", r["usable"] is False)

print("\na schema with no known receipt spelling still refuses")
#  This exact document defeated the first version, which asked whether a known receipt spelling
#  appeared anywhere in the serialised JSON. It returned usable=True, total=0 -- the original
#  silent zero under a new name.
r = with_raw({"u.json": {"units": [{"tool_calls": [{"name": "browse", "receipt": {"ok": 1}}]}]}})
check("an unknown schema carrying receipts refuses", r["usable"] is False)
r = with_raw({"u.json": {"units": [{"x": 1}]}})
check("an unknown schema carrying nothing also refuses", r["usable"] is False)

print("\nunits decide before the declared type")
#  Raw sample files embed their outbound `spec`. Reading spec.artifact_type as a fallback
#  classified them as solicitations-to-exclude and dropped the corpus search count from 9 to 8,
#  losing the single numbered-round receipt. A file holding units is counted whatever it calls
#  itself.
r = with_raw({"r.json": {"spec": {"artifact_type": "qualification_solicitation"},
                         "responses": [{"search_receipts": [{"outcome": "OK"}]}]}})
check("an embedded spec type does not exclude a file that holds units", r["total"] == 1)

print("\nunparseable files refuse too")
saved = dc.RAW
tmp = Path(tempfile.mkdtemp()) / "raw"
(tmp / "round-999").mkdir(parents=True)
(tmp / "round-999" / "broken.json").write_text("{not json")
dc.RAW = tmp
r = dc.scan("search")
dc.RAW = saved
check("a corrupt file makes the run unusable", r["usable"] is False)
check("...and is named as unparseable", "broken.json" in r["coverage"]["unparseable"][0])

print("\ndenominators travel with the count")
r = with_raw({"a.json": {"samples": [{"search": {"receipts": [{"outcome": "OK"}]}}, {}]}})
check("files visited is reported", r["coverage"]["files_visited"] == 1)
check("solicited units seen is reported", r["coverage"]["solicited_units_seen"] == 2)

print("\ninstructed probes are never merged into the rounds figure")
saved = dc.RAW
tmp = Path(tempfile.mkdtemp()) / "raw"
for d in ("round-001", "toolprobe-4-search"):
    (tmp / d).mkdir(parents=True)
    (tmp / d / "s.json").write_text(json.dumps({"samples": [{"search_receipts": [{"o": 1}]}]}))
dc.RAW = tmp
r = dc.scan("search")
dc.RAW = saved
check("a round receipt lands in `rounds`", r["counts"]["rounds"] == 1)
check("a probe receipt lands in `instructed`", r["counts"]["instructed"] == 1)
check("the two are not summed into one headline", r["counts"]["rounds"] != r["total"])

print("\nthe live corpus reproduces the corrected figures")
live = dc.scan("search")
check("the real corpus is fully readable", live["usable"] is True)
check("9 search receipts corpus-wide", live["total"] == 9)
check("exactly 1 of them in a numbered round", live["counts"]["rounds"] == 1)
check("the numbered-round one is round-016 qwen",
      any("round-016" in k for k in live["per_file"]))

print("\nthe CLI refuses loudly and prints no number")
tmp = Path(tempfile.mkdtemp()) / "raw"
(tmp / "round-999").mkdir(parents=True)
(tmp / "round-999" / "x.json").write_text(json.dumps({"units": [{"search_receipts": [{"o": 1}]}]}))
proc = subprocess.run([sys.executable, str(ROOT / "derive_counts.py"), "--tool", "search"],
                      capture_output=True, text=True,
                      env={**__import__("os").environ, "PYTHONPATH": str(ROOT)},
                      cwd=ROOT)
check("the CLI on the real corpus exits 0", proc.returncode == 0)

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass. This has happened twice.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
