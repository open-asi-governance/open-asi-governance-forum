#!/usr/bin/env python3
"""The ratchet must refuse a lost negative control and new debt — and nothing else.

    python3 tools/tests/test_coverage_ratchet.py

A gate whose green means less than a reader assumes is this repository's dominant failure class,
so the claims this makes are deliberately small and every one of them ships with a case that must
fail. What it asserts: a tool that HAD a declared negative control and lost it is refused; a NEW
tool arriving with none is refused; a tool that GAINED one is allowed; and a detector-contract
change refuses rather than silently reinterpreting the numbers.

What it does NOT assert, and the module says so on every success: that the coverage is adequate,
that any case is demanding, or that the tools reading NONE are unprotected.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import control_coverage as cc                                             # noqa: E402

COVERS = ("control_coverage.py",)

PASSED = FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


def with_baseline(determinations: dict, *, version=None, excused=None):
    """Point the module at a baseline this test owns. Never the live one — a fixture that
    rewrote the committed baseline to prove the ratchet works would be the D-62 shape again."""
    box = Path(tempfile.mkdtemp()) / "coverage-baseline.json"
    box.write_text(json.dumps({
        "detector_contract_version": cc.DETECTOR_CONTRACT_VERSION if version is None else version,
        "determinations": determinations,
        "authorised_regressions": excused or {}}), encoding="utf-8")
    cc.BASELINE = box


_saved_baseline = cc.BASELINE
HAS, NONE = "HAS_NEGATIVE_CONTROL", "NONE"


def run(determinations: dict, current: list[tuple[str, str, str]], **kw) -> list[str]:
    with_baseline(determinations, **kw)
    try:
        return cc.ratchet(current)
    finally:
        cc.BASELINE = _saved_baseline


print("\nwhat the ratchet must refuse")

problems = run({"a.py": HAS}, [("a.py", NONE, "no suite declares it")])
check("a tool that LOST its negative control is refused",
      any("HAD a negative control" in p for p in problems), str(problems))

problems = run({"a.py": HAS}, [("a.py", HAS, ""), ("b.py", NONE, "")])
check("a NEW tool arriving with none is refused",
      any("is NEW and arrives with no negative control" in p for p in problems), str(problems))

problems = run({"a.py": HAS}, [("b.py", HAS, "")])
check("a baselined tool that VANISHED is refused",
      any("is GONE" in p for p in problems), str(problems))

problems = run({"a.py": HAS}, [("a.py", HAS, "")], version=1)
check("a detector-contract change refuses rather than reinterpreting the numbers",
      any("detector contract" in p for p in problems), str(problems))
check("...and it says why the two events must not be confused",
      any("corrected MEASUREMENT" in p for p in problems), str(problems))

print("\nwhat it must ALLOW, without which it would refuse everything and score full marks")

problems = run({"a.py": NONE}, [("a.py", HAS, "")])
check("POSITIVE CONTROL: a tool that GAINED a negative control passes", problems == [],
      str(problems))

problems = run({"a.py": HAS, "b.py": NONE}, [("a.py", HAS, ""), ("b.py", NONE, "")])
check("POSITIVE CONTROL: unchanged legacy debt passes — it is a ratchet, not a target",
      problems == [], str(problems))

problems = run({"a.py": "NOT_APPLICABLE"}, [("a.py", "NOT_APPLICABLE", "no signal")])
check("POSITIVE CONTROL: a stable NOT_APPLICABLE passes", problems == [], str(problems))

print("\nthe escape hatch is narrow on purpose")

ground = ("the tool was withdrawn entirely on 2026-08-12 at the custodian's direction; it emits "
          "no assurance signal because it no longer exists")
problems = run({"a.py": HAS}, [("b.py", HAS, "")], excused={"a.py": ground})
check("a withdrawal recorded with a ground is allowed", problems == [], str(problems))

problems = run({"a.py": HAS}, [("b.py", HAS, "")], excused={"a.py": "because"})
check("a one-word ground is not a ground",
      any("is GONE" in p for p in problems), str(problems))

problems = run({"a.py": HAS}, [("a.py", NONE, "")], excused={"a.py": "meh"})
check("a HAS -> NONE with a too-short ground is still refused",
      any("HAD a negative control" in p for p in problems), str(problems))

print("\nand it refuses to run at all without a baseline")

problems = run({}, [("a.py", HAS, "")])
check("no baseline means no ratchet, rather than a vacuous pass",
      any("no baseline has been stamped" in p for p in problems), str(problems))

print("\nthe success line must not overclaim")

src = (REPO_ROOT / "tools" / "control_coverage.py").read_text(encoding="utf-8")
flat = " ".join(src.split())
check("the green says NON-REGRESSION ONLY", "NON-REGRESSION ONLY" in flat)
check("...and prints how much legacy debt remains beside it",
      "legacy tool(s) still have none" in flat)
check("...and denies that it means the coverage is adequate",
      "does not say the coverage is adequate" in flat)
check("the debt list is not truncated", "none[:20]" not in flat)

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
