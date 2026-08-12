#!/usr/bin/env python3
"""Conformance tests for the redraw guard.

    python3 tools/tests/test_attempt_ledger.py

The guard's whole job is to make one thing impossible: asking a party the same authorization
question twice and keeping whichever answer came out unanimous. These tests are the ways a
caller might get a second draw past it.
"""
from __future__ import annotations
import shutil, sys, tempfile
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import attempt_ledger as al                                              # noqa: E402

#  COVERS — what this suite REQUIRES TO REFUSE, declared rather than inferred. The
#  proximity heuristic that used to guess this counted a shutil.copy list and a comment
#  as coverage; see D-68. A declaration is a claim someone made after reading the file,
#  and it cannot rot silently: a declared tool that does not exist fails the scan, and a
#  suite with no refusal assertion is refused the credit anyway.
COVERS = ("attempt_ledger.py",)

PASSED = FAILED = 0
def check(label, cond):
    global PASSED, FAILED
    if cond: PASSED += 1; print(f"  \033[32m✓\033[0m {label}")
    else: FAILED += 1; print(f"  \033[31m✗ {label}\033[0m")

def fresh():
    return al.Ledger(Path(tempfile.mkdtemp()) / "ledger.jsonl")

def refuses(label, fn):
    try: fn()
    except al.RedrawRefused: check(label, True); return
    except Exception as e: check(f"{label} — raised {type(e).__name__}", False); return
    check(f"{label} — did NOT refuse", False)

OPTS = ["P011", "P012", "P013", "P014", "NO_ACTIVE_PROPOSAL"]

print("\na second draw on the same question is refused")
L = fresh()
L.record("activation", "gpt", OPTS, "a"*64, 5, "unanimous", "activation-01")
check("the first attempt is recorded", len(L.entries()) == 1)
refuses("the identical question to the same party is refused",
        lambda: L.record("activation", "gpt", OPTS, "a"*64, 5, "unanimous", "agenda-03"))
refuses("a different prompt text over the SAME option set is still a redraw",
        lambda: L.record("activation", "gpt", OPTS, "b"*64, 5, "unanimous", "agenda-03"))
refuses("a different k over the same option set is still a redraw",
        lambda: L.record("activation", "gpt", OPTS, "a"*64, 9, "unanimous", "agenda-03"))
refuses("SHUFFLING the enum does not present it as a new question",
        lambda: L.record("activation", "gpt", list(reversed(OPTS)), "a"*64, 5, "u", "agenda-03"))

print("\na genuinely different question is allowed")
L2 = fresh()
L2.record("activation", "gpt", OPTS, "a"*64, 5, "unanimous", "activation-01")
e = L2.record("activation", "gpt", OPTS + ["C001", "C002"], "c"*64, 5, "unanimous", "agenda-03")
check("adding candidates to the option set is a new question", e["attempt_index"] == 2)
check("a narrowed option set is also a new question",
      L2.record("activation", "gpt", ["P011", "NO_ACTIVE_PROPOSAL"], "d"*64, 5, "u",
                "agenda-04")["attempt_index"] == 3)
check("another PARTY over the same options is unaffected",
      L2.record("activation", "grok", OPTS, "a"*64, 5, "unanimous", "activation-01")["party"]
      == "grok")
check("a different INSTRUMENT over the same options is unaffected",
      L2.record("proposal", "gpt", OPTS, "a"*64, 5, "unanimous", "agenda-03")["instrument"]
      == "proposal")

print("\nthe check is not separable from the write")
L3 = fresh()
L3.record("activation", "qwen", OPTS, "a"*64, 5, "unanimous", "activation-01")
before = len(L3.entries())
try: L3.record("activation", "qwen", OPTS, "a"*64, 5, "unanimous", "agenda-03")
except al.RedrawRefused: pass
check("a refused attempt writes NOTHING to the ledger", len(L3.entries()) == before)
raised = False
try:
    L3.check("activation", "qwen", OPTS)
except al.RedrawRefused:
    raised = True
check("check() alone raises on a redraw", raised)
check("check() alone appends nothing", len(L3.entries()) == before)
L3.check("activation", "qwen", ["P011", "NO_ACTIVE_PROPOSAL"])
check("check() alone permits a genuinely different option set", len(L3.entries()) == before)

print("\nthe record supports auditing an asymmetry")
L4 = fresh()
for p in ("gemini", "gpt", "qwen"):
    L4.record("activation", p, OPTS, "a"*64, 5, "unanimous", "agenda-03")
parties = {e["party"] for e in L4.entries()}
check("every party asked is recoverable from the ledger",
      parties == {"gemini", "gpt", "qwen"})
check("the full option set is stored, not only its hash",
      all(e["eligible_ids"] for e in L4.entries()))
check("entries are hash-chained to the one before",
      L4.entries()[0]["prev_sha256"] == "0"*64 and
      L4.entries()[1]["prev_sha256"] != "0"*64)
check("the guard does NOT claim to prove uniformity",
      "cannot" in al.__doc__ and "uniform" in al.__doc__.lower())

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
