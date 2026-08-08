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
#  AGAINST A SYNTHETIC TREE. These used to assert that claude's live authorization is P004,
#  which agenda-04 then replaced with P025 -- a test failing because the project advanced
#  exactly as designed. Assert the transition, not whose turn it happens to be.
import shutil as _sh, tempfile as _tf                                     # noqa: E402
_root = Path(_tf.mkdtemp()); _d = _root / "c01"; _d.mkdir(parents=True)
(_d / "c01-authorization.json").write_text(json.dumps(
    {"artifact_type": "agenda_activation_record",
     "by_party": [{"party": "alpha", "selection_outcome": "authorized",
                   "active_proposal_id": "P900"}]}))
check("an authorization whose proposal has been asked is no longer active",
      AS.active_proposals(_root, asked={"P900"}).get("alpha") is None)
check("...and the party stays PRESENT in the mapping, holding nothing",
      "alpha" in AS.active_proposals(_root, asked={"P900"}))
check("with the proposal unasked it still reads active",
      AS.active_proposals(_root).get("alpha") == "P900")
check("a party never balloted is absent, not None",
      "beta" not in AS.active_proposals(_root, asked={"P900"}))
_sh.rmtree(_root, ignore_errors=True)


print("\ncondition-balanced exposure, and the cursor amendment")
class Q:
    def __init__(self, pid, cond): self.pid, self.condition = pid, cond
    question, party = "q", "x"
pool = [Q("P001","blind"), Q("P002","blind"), Q("P025","saw_own_queue"), Q("P026","saw_own_queue")]

empty = {"offered": {}, "prior_exposure": {}}
check("with equal exposure the tie-break is the condition sorting first",
      ar.select_for("x", pool, empty).pid == "P001")

seeded = {"offered": {}, "prior_exposure": {"x": {"blind": 4}}}
check("a condition with prior agenda exposure yields to one with none",
      ar.select_for("x", pool, seeded).pid == "P025")

r = ar.exposure_rates("x", pool, seeded)
check("the rate is offers divided by admitted, per condition",
      r["blind"]["rate"] == 2.0 and r["saw_own_queue"]["rate"] == 0.0)
check("the scheduler's whole state is recomputable from cursor and queue",
      set(r["blind"]) == {"offers", "admitted", "rate", "unoffered"})

after = {"offered": {"x": ["P025"]}, "prior_exposure": {"x": {"blind": 4}}}
check("THE CURSOR ADVANCES: an offered proposition is not offered again",
      ar.select_for("x", pool, after).pid == "P026")
check("...which is what stops the redraw the ledger refuses by hash",
      ar.select_for("x", pool, after).pid != "P025")

allof = {"offered": {"x": ["P001","P002","P025","P026"]}, "prior_exposure": {}}
pick = ar.select_for("x", pool, allof)
check("when every proposition has been offered the epoch turns over",
      pick.pid == "P001" and allof["offered"]["x"] == [])
check("...and the epoch count advances", allof["epochs"]["x"] == 2)

print("\nadmission is explicit and ids are stable")
import agenda_selectors as _AS                                            # noqa: E402
mans = _AS.admitted_manifests()
check("at least one admission manifest is published", len(mans) >= 1)
check("the manifest declares its information condition",
      all(m.get("information_condition") for m in mans))
check("the manifest declares an admission budget",
      all(m.get("admission_budget_per_party") for m in mans))
check("the manifest anchors its sources by hash",
      all(m.get("sources") and all(x.get("sha256") for x in m["sources"]) for m in mans))
reg = json.loads((REPO_ROOT / "record" / "agenda" / "proposition-ids.json").read_text())
check("every admitted proposition has a registered id",
      all(a["question_sha256"] in reg["by_question_sha256"]
          for m in mans for a in m["admitted"]))
live = _AS.load_queue()
check("the original 24 ids are unchanged by the admission",
      [p.pid for p in live if p.condition == "blind"][:3] == ["P001", "P002", "P003"])
check("ids are unique across cohorts",
      len({p.pid for p in live}) == len(live))
check("a proposition carries the condition it was written under",
      {p.condition for p in live} == {"blind", "saw_own_queue"})
check("to_json publishes cohort and condition",
      "cohort" in live[0].to_json() and "condition" in live[0].to_json())

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
