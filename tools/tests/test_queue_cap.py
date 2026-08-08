#!/usr/bin/env python3
"""Conformance tests for the one-active-proposal cap.

    python3 tools/tests/test_queue_cap.py

The cap decides which question the next round asks, so its state machine is the part that must
not be wrong. Three states have to stay distinct, and the first implementation collapsed two of
them -- three parties that HAD been balloted were treated as though they never were, and nine
proposals came through a cap that reported itself as enforced.

    never balloted           -> not capped
    balloted, holds X        -> X only
    balloted, holds nothing  -> nothing

The asymmetry between `indeterminate` and `explicit_none` is a custodian ruling, not a reading
of the ballots: record/decisions/2026-08-08-agenda-03-revocation-invalid.json, D-55.
"""
from __future__ import annotations
import json, shutil, sys, tempfile
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import agenda_selectors as AS                                            # noqa: E402

PASSED = FAILED = 0
def check(label, cond):
    global PASSED, FAILED
    if cond: PASSED += 1; print(f"  \033[32m✓\033[0m {label}")
    else: FAILED += 1; print(f"  \033[31m✗ {label}\033[0m")

def tree(*records):
    """A temporary corpus/artifacts holding the given authorization records, in order."""
    root = Path(tempfile.mkdtemp())
    for i, rec in enumerate(records):
        d = root / f"cohort-{i:02d}"; d.mkdir(parents=True)
        (d / f"cohort-{i:02d}-authorization.json").write_text(json.dumps(
            {"artifact_type": "agenda_activation_record", "by_party": rec}))
    return root

def entry(party, outcome, pid=None):
    return {"party": party, "selection_outcome": outcome, "active_proposal_id": pid}

print("\nthe three states stay distinct")
root = tree([entry("claude", "authorized", "P004"), entry("gpt", "indeterminate")])
active = AS.active_proposals(root)
check("an authorized party maps to its proposal", active.get("claude") == "P004")
check("a balloted-but-indeterminate party is PRESENT in the mapping", "gpt" in active)
check("...and holds nothing", active.get("gpt") is None)
check("a party never balloted is ABSENT, not None", "qwen" not in active)
shutil.rmtree(root, ignore_errors=True)

print("\nindeterminate does not revoke; explicit_none does")
root = tree([entry("claude", "authorized", "P004")],
            [entry("claude", "indeterminate")])
check("a later indeterminate leaves a standing authorization alone",
      AS.active_proposals(root).get("claude") == "P004")
shutil.rmtree(root, ignore_errors=True)

root = tree([entry("claude", "authorized", "P004")],
            [entry("claude", "none_authorized")])
check("a later unanimous NO_ACTIVE_PROPOSAL clears it",
      AS.active_proposals(root).get("claude") is None)
shutil.rmtree(root, ignore_errors=True)

root = tree([entry("claude", "authorized", "P004")],
            [entry("claude", "authorized", "P005")])
check("a later authorization replaces an earlier one",
      AS.active_proposals(root).get("claude") == "P005")
shutil.rmtree(root, ignore_errors=True)

root = tree([entry("claude", "indeterminate")], [entry("claude", "authorized", "P004")])
check("indeterminate then authorized ends authorized",
      AS.active_proposals(root).get("claude") == "P004")
shutil.rmtree(root, ignore_errors=True)

print("\nthe cap is opt-in and never silent")
import inspect                                                           # noqa: E402
sig = inspect.signature(AS.load_queue)
check("enforce_cap defaults to OFF", sig.parameters["enforce_cap"].default is False)

disp = AS.disposition_from_records(REPO_ROOT / "record" / "cycles")
uncapped = [p for p in AS.load_queue(disposition=disp) if not p.asked]
capped = [p for p in AS.load_queue(disposition=disp, enforce_cap=True) if not p.asked]
check("the default call is unaffected by the cap", len(uncapped) > len(capped))

print("\non the live record")
check("exactly the two authorized proposals survive the cap",
      sorted(p.pid for p in capped) == ["P004", "P019"])
check("every surviving proposal is its party's authorized one",
      all(AS.active_proposals().get(p.party) == p.pid for p in capped))
check("no party balloted without an authorization keeps anything",
      not any(p.party in ("gemini", "gpt", "qwen") for p in capped))
check("an ASKED proposal is not removed by the cap — history is not rewritten",
      len([p for p in AS.load_queue(disposition=disp, enforce_cap=True) if p.asked]) ==
      len([p for p in AS.load_queue(disposition=disp) if p.asked]))

print("\nan authorization the queue cannot honour fails closed")
raised = False
try:
    AS.load_queue(round_dir=REPO_ROOT / "corpus" / "raw" / "agenda-02",
                  disposition=disp, enforce_cap=True)
except ValueError:
    raised = True
check("an authorized id absent from the queue raises rather than being ignored", raised)

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
