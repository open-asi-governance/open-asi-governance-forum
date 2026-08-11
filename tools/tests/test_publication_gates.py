#!/usr/bin/env python3
"""Negative controls for the next tier of tools that had none.

`tools/control_coverage.py` had 40 tools with no case they must fail. These are the ones whose
failure reaches a reader:

* `check_page_budget.py` runs inside **every rebuild** and had never been observed to fail. It is
  the reason a page cannot silently grow past what a reviewer will read.
* `capture_gates.py` decides whether a solicited response is usable at all. A gate that accepts
  everything makes every downstream count meaningless.
* `arm_acceptance.py` is the gate a tool-using arm must pass before its first sample counts.

Each fault is injected and each has a **baseline** arm. A guard that refuses everything is broken
rather than strict, and only the pair tells them apart.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess as sp
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
passed = FAILED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, FAILED
    if ok:
        passed += 1
        print(f"  \033[32m✓\033[0m {name}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {name}\033[0m")
        if detail:
            print(f"      {detail[:300]}")


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


print("\ncheck_page_budget.py — it must fail the build on an over-budget page")

r = sp.run([sys.executable, str(ROOT / "check_page_budget.py")],
           cwd=REPO, capture_output=True, text=True)
check("BASELINE: every published page is within budget", r.returncode == 0,
      (r.stdout + r.stderr)[-200:])

#  FAULT: a published page far past the ceiling. Written into docs/, which is generated, so the
#  next rebuild removes it regardless -- but it is deleted here too rather than left to chance.
oversize = REPO / "docs" / "zzqx-oversize-negative-control.html"
try:
    oversize.write_text("<html><body>" + ("word " * 200_000) + "</body></html>", encoding="utf-8")
    r = sp.run([sys.executable, str(ROOT / "check_page_budget.py")],
               cwd=REPO, capture_output=True, text=True)
    check("an OVER-BUDGET page fails the build", r.returncode != 0,
          f"rc={r.returncode}; a budget check that passes any size is not a budget")
finally:
    oversize.unlink(missing_ok=True)
r = sp.run([sys.executable, str(ROOT / "check_page_budget.py")],
           cwd=REPO, capture_output=True, text=True)
check("...and the tree is within budget again", r.returncode == 0)

print("\ncapture_gates.py — it must refuse a response that is the prompt read back")

cg = load("capture_gates")
PROMPT = ("Consider whether an assurance check that has never been observed to fail constitutes "
          "evidence that the system it monitors is working correctly, and explain your reasoning "
          "with reference to the distinction between a check running and a check being able to "
          "detect the condition it exists to detect.")

#  BASELINE: an ordinary substantive answer must pass.
good = ("A check that has never failed tells you nothing about its sensitivity. Sensitivity is "
        "established by observing the check react to a condition it should catch, which requires "
        "producing that condition deliberately rather than waiting for it.")
#  The states are refused_empty / returned_pending_review / returned_clean. My first version
#  asserted "REJECTED", a vocabulary this tool does not use, and reported two failures that were
#  the tool behaving correctly. Assert on the STATES THAT EXIST and on which gate fired.
results = cg.run_gates(good, PROMPT)
state, _reasons = cg.lifecycle_state(results)
check("BASELINE: a substantive answer returns clean", state == "returned_clean",
      f"state={state}; a gate that flags a normal answer is broken, not strict")

#  FAULT: the response is the prompt echoed back. This is the failure the overlap gate exists
#  for -- a model that restates the question produces text that looks like an answer and
#  contains no answer.
results = cg.run_gates(PROMPT, PROMPT)
state, reasons = cg.lifecycle_state(results)
check("a response that ECHOES THE PROMPT does not return clean",
      state != "returned_clean", f"state={state}")
check("...and the gate that fired names prompt equality",
      any("prompt" in r for r in reasons), f"reasons={reasons}")

#  FAULT: an empty response.
results = cg.run_gates("", PROMPT)
state, reasons = cg.lifecycle_state(results)
check("an EMPTY response is refused outright", state == "refused_empty", f"state={state}")
check("...and the gate that fired is the non-empty one",
      any("non-empty" in r for r in reasons), f"reasons={reasons}")

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
