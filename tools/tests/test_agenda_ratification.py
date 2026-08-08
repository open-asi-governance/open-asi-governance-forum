#!/usr/bin/env python3
"""Conformance tests for the singleton-ratification instrument.

    python3 tools/tests/test_agenda_ratification.py

The rule was adopted because two predecessors let near-variants split a ballot. Its whole
mechanism is that only ONE proposition is on the ballot, chosen by a selector nobody can steer.
These tests hold the selector, the ballot shape, and the disclosures that the adopting decision
and D-55 require.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import agenda_ratification as ar                                          # noqa: E402
import agenda_selectors as AS                                             # noqa: E402

PASSED = FAILED = 0
def check(label, cond):
    global PASSED, FAILED
    if cond: PASSED += 1; print(f"  \033[32m✓\033[0m {label}")
    else: FAILED += 1; print(f"  \033[31m✗ {label}\033[0m")

class P:
    def __init__(self, pid): self.pid, self.question, self.party = pid, f"q for {pid}", "x"

print("\nthe selector is a durable cursor, not a modulo over a changing list")
elig = [P("P011"), P("P012"), P("P013")]
check("with an empty cursor it offers the lowest id",
      ar.select_for("gpt", elig, {"offered": {}}).pid == "P011")
check("once offered, it moves to the next unoffered id",
      ar.select_for("gpt", elig, {"offered": {"gpt": ["P011"]}}).pid == "P012")
check("a party's cursor does not affect another party's",
      ar.select_for("grok", elig, {"offered": {"gpt": ["P011", "P012"]}}).pid == "P011")
check("when all have been offered it wraps to the lowest",
      ar.select_for("gpt", elig, {"offered": {"gpt": ["P011","P012","P013"]}}).pid == "P011")
#  The failure a modulo would have: the list shrinks, and an id is skipped forever.
shrunk = [P("P012"), P("P013")]
check("an id already offered is not re-offered when the set SHRINKS",
      ar.select_for("gpt", shrunk, {"offered": {"gpt": ["P011"]}}).pid == "P012")
check("an id NOT yet offered survives the set growing",
      ar.select_for("gpt", [P("P010")] + elig,
                    {"offered": {"gpt": ["P011"]}}).pid == "P010")
check("an empty eligible set offers nothing", ar.select_for("gpt", [], {"offered": {}}) is None)

print("\nthe ballot has exactly two options and no reason field")
disp = AS.disposition_from_records(REPO_ROOT / "record" / "cycles")
queue = AS.load_queue(disposition=disp)
asked = {p.pid for p in queue if p.asked}
standing = AS.active_proposals(asked=asked)
standing["_spent"] = {k: v for k, v in AS.active_proposals().items() if v in asked}
import agenda_activation as aa                                            # noqa: E402
elig_gpt, _ = aa.eligible_for("gpt", queue)
pick = ar.select_for("gpt", elig_gpt, {"offered": {}})
spec = ar.build_spec("gpt", "agenda-test", 5, pick, standing)
check("exactly two options on the ballot", len(spec["eligible_proposal_ids"]) == 2)
check("the options are the offered id and the abstention",
      spec["eligible_proposal_ids"] == [pick.pid, ar.NO_ACTIVE])
props = spec["schema"]["properties"]
check("the schema has ONE field", list(props) == ["active_proposal_id"])
check("no reason field invites the party to reason itself into variance",
      "reason" not in props)
check("the schema forbids extra fields", spec["schema"]["additionalProperties"] is False)
check("no other party's proposal id can validate",
      not any(p.pid in spec["eligible_proposal_ids"]
              for p in aa.eligible_for("grok", queue)[0]))

print("\nthe prompt discloses what the decisions require")
#  WHITESPACE-NORMALISED. The prompt is hard-wrapped, so a phrase that spans a line break is
#  absent from a raw substring search while being plainly present to a reader -- which failed
#  one assertion here and would have silently passed any phrase short enough not to wrap.
prompt = " ".join(spec["prompt"].split())
check("it shows the proposal's exact text, not only its id",
      " ".join(pick.question.split()) in prompt)
check("it states the unanimity threshold", "only if every" in prompt)
check("it states that disagreement authorizes nothing", "nothing is authorized" in prompt)
check("it distinguishes unanimous abstention from failure",
      "recorded as your answer rather" in prompt)
check("it states there is no second attempt", "no second attempt" in prompt)
check("it says the selection is not a judgement about which is best",
      "not a judgement by anyone about which of them is best" in prompt)
check("it says nothing is deleted", "Nothing is deleted" in prompt)
check("D-55: it states the effect on a standing authorization",
      "active proposal" in prompt and ("takes one away" in prompt or "consumed" in prompt
                                       or "remains your active proposal" in prompt))
check("every disclosure survives whitespace normalisation",
      all(" ".join(t.split()) in prompt for t in
          ["only if every", "no second attempt", "Nothing is deleted",
           "not a judgement by anyone about which of them is best"]))

print("\nthe D-55 clause is party-specific, not boilerplate")
c_spent = ar.standing_clause("claude", {"claude": None, "_spent": {"claude": "P004"}})
c_none = ar.standing_clause("gpt", {"gpt": None, "_spent": {}})
c_held = ar.standing_clause("qwen", {"qwen": "P022", "_spent": {}})
check("a party whose authorization was consumed is told which one and where",
      "P004" in c_spent and "consumed" in c_spent)
check("a party that never held one is told nothing is taken away",
      "no** active proposal" in c_none and "takes one away" in c_none)
check("a party still holding one is told this ballot does not revoke it",
      "P022" in c_held and "does not revoke" in c_held)
check("the three clauses are genuinely different text",
      len({c_spent, c_none, c_held}) == 3)

print("\nthe instrument records what it cannot claim")
check("the spec names the adopting decision",
      spec["rule_decision"].endswith("adopt-singleton-ratification.json"))
check("the spec names the CORRECTION to that decision",
      spec["rule_correction"].endswith("singleton-ratification-correction.json"))
check("the correction exists on disk",
      (REPO_ROOT / spec["rule_correction"]).is_file())
corr = json.loads((REPO_ROOT / spec["rule_correction"]).read_text())
check("the correction names the false mitigation claim",
      "bounded rather than permanent" in corr["the_error"])
check("the correction refuses to repair it by retrying",
      "No retry" in corr["what_is_NOT_done_about_it"])
check("the cursor does not advance on failure",
      "does not advance" in spec["authorization_rule"]["cursor_on_failure"])
check("the instrument states the legacy-material confound",
      "blind" in ar.__doc__ and "23 of 25" in ar.__doc__)

print("\nspent authorizations are discharged")
check("an authorization whose proposal has been asked is no longer active",
      AS.active_proposals(asked={"P004", "P019"}).get("claude") is None)
check("...and the party stays PRESENT in the mapping, holding nothing",
      "claude" in AS.active_proposals(asked={"P004", "P019"}))
check("without the asked set the raw authorization still reads active",
      AS.active_proposals().get("claude") == "P004")

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
