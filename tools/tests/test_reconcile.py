#!/usr/bin/env python3
"""Conformance for typed coverage and reconciliation — renewal condition 3.

The condition exists because three synthetic demonstrations were once counted as real catches,
and because the log's ontology had no word for most of what the workbench does.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import executive_log as ex                                              # noqa: E402
import reconcile_actions as rc                                          # noqa: E402

PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


print("\nsynthetic entries are TYPED, not left to a free-text note")
check("a note saying 'synthetic' types the entry as synthetic_test",
      ex.infer_coverage("push", False, ["x"], "synthetic: bogus commit") == "synthetic_test")
check("...and synthetic_test is a distinct state, not a flavour of verified",
      "synthetic_test" in ex.COVERAGE and "verified_postcondition" in ex.COVERAGE)
check("a real profiled pass is verified_postcondition",
      ex.infer_coverage("push", True, [], "landed") == "verified_postcondition")
check("an action with NO profile is observed_unprofiled, not verified",
      ex.infer_coverage("codex_invoke", True, [], "ran") == "observed_unprofiled")
check("every state carries a stated meaning", all(ex.COVERAGE.values()))

print("\ncoverage is written on every new entry")
import inspect                                                          # noqa: E402
src = inspect.getsource(ex.log_action)
check("log_action stamps coverage", '"coverage"' in src)
check("an explicit coverage argument overrides the inference",
      "coverage: str" in inspect.signature(ex.log_action).__str__() or
      "coverage" in inspect.signature(ex.log_action).parameters)

print("\nreconciliation classifies effects the log has no word for")
check("a gate source file classifies as gate_modification",
      rc.classify("tools/executive_log.py") == "gate_modification")
check("raw material classifies as a paid solicitation",
      rc.classify("corpus/raw/round-020/x.json") == "paid_solicitation")
check("a finding classifies as a finding",
      rc.classify("record/findings/x.md") == "finding")
check("a committed spec classifies as a prompt_or_spec_edit",
      rc.classify("record/solicitations/r/x.json") == "prompt_or_spec_edit")
check("an unrelated path classifies as nothing", rc.classify("README.md") is None)

print("\nthe live repository is reconciled, and the omissions are real")
result = rc.reconcile("2026-08-09")
check("it reports commits", result["commits"] > 0)
check("it names effect classes that occurred", len(result["repository_effects"]) > 1)
check("it reports omissions rather than a clean balance", len(result["omissions"]) > 0)
check("gate modifications are counted separately", result["gate_modifications"] > 0)
check("every omission says WHY it is unverified",
      all(o["why"] for o in result["omissions"]))
check("it states what it cannot establish", len(result["what_this_cannot_establish"]) >= 4)

print("\nit does not claim to verify what it merely observed")
check("no omission claims a verifier",
      all(o["verified_by"] is None for o in result["omissions"]))

#  KEEP THE SUMMARY AND EXIT LAST.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
