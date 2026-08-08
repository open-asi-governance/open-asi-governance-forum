#!/usr/bin/env python3
"""Conformance tests for the activation authorization rule.

    python3 tools/tests/test_agenda_activation.py

This instrument turns sampled output into a governance act, so the rule that converts samples
into an authorization is the part that must not be wrong. The precommitted rule:

    a proposal is active ONLY if every one of the k scheduled samples named the same
    eligible id; anything else authorizes nothing.

The tests below are the branches that "anything else" covers. The one that matters most is
`sample_disagreement`: the first design left a non-unanimous party UNCAPPED, which would have
failed to repair exactly the parties whose sampling variance created the defect.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import agenda_activation as aa                                            # noqa: E402

PASSED = FAILED = 0
ELIGIBLE = ["P011", "P012", "P013", aa.NO_ACTIVE]


def check(label: str, condition: bool) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


def samples(*ids):
    return [{"parsed": {"active_proposal_id": i, "reason": "r"}} for i in ids]


print("\nunanimity authorizes, and only unanimity")
r = aa.authorize("gpt", samples("P011", "P011", "P011", "P011", "P011"), 5, ELIGIBLE)
check("five identical eligible ids authorize that proposal",
      r["selection_outcome"] == "authorized" and r["active_proposal_id"] == "P011")
check("the authorized case is categorised 'unanimous'", r["category"] == "unanimous")

r = aa.authorize("gpt", samples("P011", "P011", "P011", "P011", "P012"), 5, ELIGIBLE)
check("a 4-1 split authorizes NOTHING", r["active_proposal_id"] is None)
check("a 4-1 split is 'indeterminate', not 'the party chose none'",
      r["selection_outcome"] == "indeterminate")
check("a 4-1 split is categorised as sample_disagreement",
      r["category"] == "sample_disagreement")

r = aa.authorize("gpt", samples("P011", "P011", "P011", "P012", "P012"), 5, ELIGIBLE)
check("a 3-2 split authorizes nothing — the modal value is NOT taken",
      r["active_proposal_id"] is None and r["category"] == "sample_disagreement")

print("\nabstention is a real answer and is not merged with disagreement")
r = aa.authorize("grok", samples(*[aa.NO_ACTIVE] * 5), 5, ELIGIBLE)
check("unanimous abstention authorizes nothing", r["active_proposal_id"] is None)
check("unanimous abstention is 'none_authorized', NOT 'indeterminate'",
      r["selection_outcome"] == "none_authorized")
check("unanimous abstention is categorised explicit_none", r["category"] == "explicit_none")

r = aa.authorize("grok", samples("P011", aa.NO_ACTIVE, "P011", "P011", "P011"), 5, ELIGIBLE)
check("one abstention among four picks authorizes nothing",
      r["active_proposal_id"] is None and r["category"] == "sample_disagreement")

print("\nmissing and invalid samples authorize nothing")
r = aa.authorize("qwen", samples("P011", "P011", "P011"), 5, ELIGIBLE)
check("three of five scheduled slots authorizes nothing",
      r["active_proposal_id"] is None and r["category"] == "missing")
check("a short run is never silently treated as unanimous",
      r["selection_outcome"] == "indeterminate")

r = aa.authorize("qwen", samples("P011", "P011", "P011", "P011", "P999"), 5, ELIGIBLE)
check("an id outside this party's own eligible set authorizes nothing",
      r["active_proposal_id"] is None and r["category"] == "invalid")

r = aa.authorize("qwen", [{"content": "not json"}] * 5, 5, ELIGIBLE)
check("five unparseable samples authorize nothing",
      r["active_proposal_id"] is None and r["category"] == "invalid")

r = aa.authorize("qwen", samples(None, None, None, None, None), 5, ELIGIBLE)
check("five null ids authorize nothing", r["active_proposal_id"] is None)

r = aa.authorize("qwen", [], 5, ELIGIBLE)
check("zero collected samples authorize nothing",
      r["active_proposal_id"] is None and r["category"] == "missing")

print("\nevery sample is published either way")
r = aa.authorize("gpt", samples("P011", "P012", "P011", "P013", "P011"), 5, ELIGIBLE)
check("all five observed ids are recorded on an indeterminate outcome",
      r["samples"] == ["P011", "P012", "P011", "P013", "P011"])
check("the distribution is computed and published",
      r["distribution"] == {"P011": 3, "P012": 1, "P013": 1})
check("k_collected is recorded beside k_required",
      r["k_collected"] == 5 and r["k_required"] == 5)

print("\nthe eligible set is per-party, never shared")
import agenda_selectors as AS                                             # noqa: E402
queue = AS.load_queue(disposition=AS.disposition_from_records(REPO_ROOT / "record" / "cycles"))
if queue:
    gpt_unasked, gpt_asked = aa.eligible_for("gpt", queue)
    grok_unasked, _ = aa.eligible_for("grok", queue)
    check("a party's eligible set contains only its own proposals",
          all(p.party == "gpt" for p in gpt_unasked))
    check("no asked proposal is eligible", all(not p.asked for p in gpt_unasked))
    check("an asked proposal is still shown, separately",
          all(p.asked for p in gpt_asked) and len(gpt_asked) > 0)
    check("two parties' eligible sets are disjoint",
          not ({p.pid for p in gpt_unasked} & {p.pid for p in grok_unasked}))

    spec = aa.build_spec("gpt", "activation-test", 5, queue)
    check("the spec's enum is exactly this party's unasked ids plus the abstention value",
          set(spec["eligible_proposal_ids"]) ==
          {p.pid for p in gpt_unasked} | {aa.NO_ACTIVE})
    check("another party's id would not validate against this spec",
          not any(p.pid in spec["eligible_proposal_ids"] for p in grok_unasked))
    check("the prompt names the unanimity consequence",
          "every\n  one of those" in spec["prompt"] or "every one of those" in spec["prompt"])
    check("the prompt says dormant does not mean deleted",
          "does not mean deleted" in spec["prompt"].lower().replace("**", ""))
    check("the prompt offers abstention explicitly", aa.NO_ACTIVE in spec["prompt"])
    check("the prompt forbids introducing a new question",
          "cannot introduce a new question" in spec["prompt"])
    check("the prompt does not tell a party its proposals are rewordings",
          "reword" not in spec["prompt"].lower()
          and "duplicat" not in spec["prompt"].lower())
    check("no other party's proposal text appears in this party's prompt",
          not any(p.question[:60] in spec["prompt"] for p in grok_unasked))

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
