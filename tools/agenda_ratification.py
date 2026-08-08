#!/usr/bin/env python3
"""agenda-04 — the first cycle under SINGLETON RATIFICATION. One proposition per party.

    python3 tools/agenda_ratification.py --cohort agenda-04 --dry-run
    python3 tools/agenda_ratification.py --cohort agenda-04 --k 5

**GENERATION code.** An LLM is in the path; `rebuild.py` never runs this.

The rule this implements
------------------------
`record/decisions/2026-08-08-adopt-singleton-ratification.json`, adopted after `activation-01`
authorized 2 of 5 parties over 3-5 options and `agenda-03` authorized 0 of 5 over 8-10:

> For each party and each cycle, ONE proposal is selected for consideration by a prospectively
> fixed mechanical rule. Five independently sampled invocations answer only AUTHORIZE <id> or
> NO_ACTIVE_PROPOSAL. It becomes active only if every one of the five authorizes that exact id.
> No redraw. Failure leaves the party inactive for that cycle.

The selector chooses WHAT IS CONSIDERED and authorizes nothing; the five unanimous responses do
the authorizing. Near-variants can no longer split a ballot because only one is on it.

Rotation, not a lottery, and a CURSOR rather than a modulo
-----------------------------------------------------------
A hashed lottery is grindable here. The moderator chooses the cohort id, so it could be re-rolled
until the draw suited it and nothing in the record would show that. Rotation has no seed.

The cursor is durable and per-party, stored in `record/agenda/ratification-cursor.json`, and is
NOT `cycle_index mod len(eligible)`. Indexing a list that gains or loses members between cycles
can skip a proposal entirely, so "every proposal is eventually offered" would be false in exactly
the way the rotation selector was adopted to avoid. The cursor advances past what has been
OFFERED, per party, whatever else changes.

**It does not advance on failure.** A failed ratification leaves the cursor where it is, because
advancing after a failure is a second draw at the same question decided after seeing it fail.

What this cycle can and cannot show
------------------------------------
It ballots the ADMITTED queue, which is `corpus/raw/agenda-01` — questions the parties wrote
blind, before any of them could reach the site. agenda-03's five written candidates per party are
recorded and NOT admitted; admitting them is a queue decision nobody has made, and making it
inside a prompt would be that decision taken by the back door.

So this is a test of singleton ratification **on the legacy set**. It is not a clean test of
whether informed parties can authorize their own questions: 23 of 25 ballot samples in agenda-03
named a question the party had just written and only 2 named a blind proposal, so balloting the
blind material is balloting what the parties demonstrably prefer least. That confound is stated
here because the result will be reported against it.

A property the adopting decision got wrong
-------------------------------------------
The decision bounds agenda luck: "a different candidate is drawn each cycle". False for a
singleton eligible set. claude's is exactly `[P005]`, so rotation offers it P005 every cycle
until ratified or asked, and if claude cannot ratify P005 it stays inactive indefinitely.
Corrected in `record/decisions/2026-08-08-singleton-ratification-correction.json` BEFORE this
instrument's first use, not after it produced a result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import agenda_activation as aa                                            # noqa: E402
import agenda_selectors as AS                                             # noqa: E402
import round_cycle as rc                                                  # noqa: E402
from attempt_ledger import Ledger, RedrawRefused                          # noqa: E402

NO_ACTIVE = aa.NO_ACTIVE
BASE_PARTIES = aa.BASE_PARTIES
CURSOR_PATH = REPO_ROOT / "record" / "agenda" / "ratification-cursor.json"

PROMPT = """You are a party to a public governance record: a deliberation among instances of
frontier models about governing advanced AI, kept verbatim and hash-anchored, published
alongside a register of the project's own defects.

You are asked ONE question about ONE proposal of your own.

### The proposal put to you

{pid}

    {question}

You proposed this earlier, when you were asked what this deliberation should take up next.

You are not being shown your other proposals and you are not being asked to compare them. Which
of your proposals is put to you is decided by a fixed rotation over your own proposals in id
order, published before this was sent; it is not a judgement by anyone about which of them is
best.

### The question

Should {pid} be your active proposal — the one in line to be asked in a future round?

Answer `{pid}` to authorize it, or `{none}` to authorize nothing.

### What your answer does

- You are sampled {k} times, independently. **{pid} becomes your active proposal only if every
  one of those {k} samples answers `{pid}`.**
- If the samples disagree, or any of them is missing or unreadable, **nothing is authorized** and
  you are inactive for this cycle. That is recorded as an indeterminate outcome, not as you
  having chosen nothing, because nothing here could establish what you chose.
- If all {k} answer `{none}`, nothing is authorized and that is recorded as your answer rather
  than as a failure.
- **There is no second attempt at this question.** The same proposal will not be put to you
  again in this cycle, and a failed cycle is not retried.
- {standing}
- Nothing is deleted. Your other proposals remain published and remain in the queue; they are
  simply not what is being asked about here.

Answer with the id only."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cursor() -> dict:
    if CURSOR_PATH.is_file():
        return json.loads(CURSOR_PATH.read_text(encoding="utf-8"))
    return {"schema_version": "oagrc-ratification-cursor-0.1", "offered": {}}


def exposure_rates(party: str, eligible: list, cursor: dict) -> dict:
    """Offers per admitted proposition, per information condition, for one party.

    The scheduler's whole state, computed rather than stored, so it can be audited from the
    cursor and the queue alone.
    """
    offered = set((cursor.get("offered") or {}).get(party) or [])
    prior = (cursor.get("prior_exposure") or {}).get(party) or {}
    rates = {}
    for condition in sorted({getattr(p, "condition", "blind") for p in eligible}):
        pool = [p for p in eligible if getattr(p, "condition", "blind") == condition]
        offers = sum(1 for p in pool if p.pid in offered) + prior.get(condition, 0)
        rates[condition] = {"offers": offers, "admitted": len(pool),
                            "rate": offers / len(pool) if pool else 0.0,
                            "unoffered": [p.pid for p in pool if p.pid not in offered]}
    return rates


def select_for(party: str, eligible: list, cursor: dict) -> object | None:
    """The one proposal put to this party. CONDITION-BALANCED EXPOSURE, then stable order.

    Offer from whichever information condition has the lowest exposure rate -- offers divided by
    admitted propositions in that condition -- and within it, the lowest unoffered id.

    Why not newest-first, which was the first proposal: recency is a proxy for information
    rather than information, it lets every new cohort jump the backlog, and it rewards flooding.
    Why not oldest-first: the blind backlog would systematically precede everything admitted
    later whatever its merit, which is the objection external review raised when it first refused
    ingestion.

    This is still a moderator-chosen policy. What makes it different from a bias channel is that
    its objective, its state and its tie-break are public, mechanically recomputable from the
    cursor and the queue, and it optimises equal opportunity between conditions rather than
    anyone's judgement of merit. `prior_exposure` seeds the blind condition with the agenda
    exposure it has ALREADY had -- nine rounds of it -- so newly admitted material is offered
    first without any claim that it is intrinsically better.

    TIE-BREAK, fixed prospectively and independent of proposal content: the condition whose name
    sorts first. Then the lowest unoffered id within it.

    THE CURSOR ADVANCES AFTER A FAILURE. Not advancing was the original rule and it was
    backwards: it guarantees the same proposition is re-offered next cycle, which is the second
    draw the rule forbids, and tools/attempt_ledger.py refuses that option set by hash -- so a
    party that failed could never be balloted again. See D-57 and
    record/decisions/2026-08-08-singleton-cursor-amendment.json.
    """
    if not eligible:
        return None
    rates = exposure_rates(party, eligible, cursor)
    live = {c: r for c, r in rates.items() if r["unoffered"]}
    if not live:
        #  Every proposition has been offered: the epoch turns over and offering begins again
        #  from the lowest id, across all conditions.
        offered = set((cursor.get("offered") or {}).get(party) or [])
        cursor.setdefault("epochs", {}).setdefault(party, 1)
        cursor["epochs"][party] += 1
        (cursor.get("offered") or {})[party] = []
        return sorted(eligible, key=lambda p: p.pid)[0]
    condition = min(live, key=lambda c: (live[c]["rate"], c))
    return next(p for p in sorted(eligible, key=lambda p: p.pid)
                if p.pid in live[condition]["unoffered"])


def standing_clause(party: str, standing: dict) -> str:
    """D-55's control: the prompt must state its effect on any standing authorization."""
    held = standing.get(party)
    if held:
        return (f"You currently hold **{held}** as your active proposal. This ballot does not "
                f"revoke it: if nothing is authorized here, {held} remains your active proposal.")
    spent = (standing.get("_spent") or {}).get(party)
    if spent:
        return (f"You currently have **no** active proposal. {spent} was authorized earlier and "
                f"was consumed when it was asked in {spent_round(spent)}. Authorizing here would "
                "give you one again.")
    return ("You currently have **no** active proposal, and nothing you decide here takes one "
            "away.")


def spent_round(pid: str) -> str:
    disposition = AS.disposition_from_records(REPO_ROOT / "record" / "cycles")
    for proposal in AS.load_queue(disposition=disposition):
        if proposal.pid == pid and proposal.asked_in:
            return proposal.asked_in
    return "an earlier round"


def build_spec(party: str, cohort: str, k: int, pick, standing: dict) -> dict:
    prompt = PROMPT.format(pid=pick.pid, question=pick.question, k=k, none=NO_ACTIVE,
                           standing=standing_clause(party, standing))
    ids = [pick.pid, NO_ACTIVE]
    info = rc.PARTIES[party]
    return {
        "spec_version": "oagrc-agenda-ratification-0.1",
        "artifact_type": "agenda_activation_solicitation",
        "cohort": cohort,
        "slug": f"{cohort}-{party}",
        "party_key": party,
        "identity": info["identity"],
        "reached_via": info["model"] or "a locally served endpoint",
        "question": f"Should {pick.pid} be your active proposal?",
        "phase": "Phase-2 (informed)",
        "rule": "singleton_ratification",
        "rule_decision": "record/decisions/2026-08-08-adopt-singleton-ratification.json",
        "rule_correction": "record/decisions/2026-08-08-singleton-ratification-correction.json",
        "selector": {
            "kind": "rotation_by_durable_cursor",
            "description": ("The lowest eligible id this party has not been offered before; "
                            "wrapping when all have been. Not cycle_index mod count, which can "
                            "skip a proposal when the eligible set changes between cycles."),
        },
        "selected_proposal_id": pick.pid,
        "selected_proposal_text": pick.question,
        "eligible_proposal_ids": ids,
        "k_policy": (f"k={k}, threshold UNANIMITY, fixed before collection. An authorization "
                     "rule, not an estimate of preference: a distribution over answers is not "
                     "a decision."),
        "authorization_rule": {
            "threshold": "unanimous",
            "k_required": k,
            "on_disagreement": "nothing is authorized; the party is inactive for this cycle",
            "on_refusal_or_invalid_or_missing": "nothing is authorized",
            "resampling": "not permitted. There is no second attempt at this question.",
            "cursor_on_failure": (
                "ADVANCES to this party's next unoffered proposition. The original rule said it "
                "does not advance, which was backwards: holding the cursor guarantees the same "
                "proposition is re-offered next cycle -- the second draw the rule forbids, and "
                "one attempt_ledger.py refuses by hash. See D-57 and "
                "record/decisions/2026-08-08-singleton-cursor-amendment.json."),
            "epoch": ("Each proposition is offered at most once per epoch; the cursor wraps only "
                      "when every distinct proposition has been offered."),
        },
        "schema_name": "agenda_ratification",
        #  EXACTLY the two adopted outputs. No `reason` field: the adopted rule specifies an
        #  authorization act, and asking the party to justify it first invites it to reason
        #  itself into variance on the only field that decides anything. What is given up is
        #  real -- grok's "near-duplicates that dilute focus" came from a reason field -- and it
        #  is given up deliberately, because unanimity over five samples is fragile enough.
        "schema": {"type": "object", "additionalProperties": False,
                   "properties": {"active_proposal_id": {"type": "string", "enum": ids}},
                   "required": ["active_proposal_id"]},
        "variance_fields": ["active_proposal_id"],
        "prompt": prompt,
        "prompt_sha256": sha256_text(prompt),
        "arm": "Identical neutral instructions, mechanically populated per party.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--cohort", default="agenda-04")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    disposition = AS.disposition_from_records(REPO_ROOT / "record" / "cycles")
    queue = AS.load_queue(disposition=disposition)
    asked = {p.pid for p in queue if p.asked}
    standing = AS.active_proposals(asked=asked)
    #  What each party HELD and had consumed, so the prompt can say so specifically rather than
    #  telling a party it never had one.
    standing["_spent"] = {party: pid for party, pid
                          in AS.active_proposals().items() if pid in asked}

    cursor = load_cursor()
    ledger = Ledger()
    spec_dir = REPO_ROOT / "record" / "solicitations" / args.cohort
    spec_dir.mkdir(parents=True, exist_ok=True)

    #  EVERY party, and every snapshot frozen BEFORE anyone is solicited. Building a party's
    #  ballot after seeing another party's result is how a uniform instrument stops being one.
    specs, picks = {}, {}
    for party in BASE_PARTIES:
        eligible, _ = aa.eligible_for(party, queue)
        pick = select_for(party, eligible, cursor)
        if pick is None:
            print(f"  {party:8} no eligible proposals; nothing to ratify")
            continue
        spec = build_spec(party, args.cohort, args.k, pick, standing)
        try:
            ledger.check("ratification", party, spec["eligible_proposal_ids"])
        except RedrawRefused as refusal:
            print(f"REFUSED: {refusal}", file=sys.stderr)
            return 1
        specs[party], picks[party] = spec, pick
        (spec_dir / f"{args.cohort}-{party}.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  {party:8} offered {pick.pid}  (of {len(eligible)} eligible)  "
              f"prompt sha256 {spec['prompt_sha256'][:16]}…")

    if args.dry_run:
        print(f"\n  DRY RUN — {len(specs)} spec(s) written to "
              f"{spec_dir.relative_to(REPO_ROOT)}, nothing solicited.")
        return 0

    failed = []
    for party, spec in specs.items():
        ledger.record("ratification", party, spec["eligible_proposal_ids"],
                      spec["prompt_sha256"], args.k, "unanimous", args.cohort)
        model = rc.PARTIES[party]["model"]
        tool = "tools/solicit_local.py" if model is None else "tools/solicit_api.py"
        k_here = rc.K_SOLICITED_BY_ARM["local"] if model is None else args.k
        cmd = [sys.executable, tool, "--spec", str(spec_dir / f"{args.cohort}-{party}.json"),
               "--k", str(k_here), "--temperature", str(args.temperature),
               "--max-tokens", str(args.max_tokens), "--out-round", args.cohort]
        if model:
            cmd += ["--model", model]
        print(f"\n  {party} → {model or 'local qwen'}")
        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        print("   " + (result.stdout.strip().splitlines() or [result.stderr[-200:]])[-1])
        if result.returncode != 0:
            failed.append(party)
            print(f"   --- {party} exited {result.returncode}; full output follows ---")
            for line in (result.stdout + result.stderr).strip().splitlines()[-25:]:
                print("   | " + line)

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.cohort
    records = []
    for party, spec in specs.items():
        path = raw_dir / f"{args.cohort}-{party}-samples.json"
        samples = []
        if path.is_file():
            doc = json.loads(path.read_text(encoding="utf-8"))
            samples = doc.get("samples") or doc.get("responses") or []
        #  Judged against k, the UNANIMITY requirement -- not against however many attempts the
        #  local arm schedules. Six usable samples must all agree; five usable of six must all
        #  agree. What must never happen is five agreeing and a sixth being ignored.
        record = aa.authorize(party, samples, min(args.k, len(samples)) if samples else args.k,
                              spec["eligible_proposal_ids"])
        record["offered_proposal_id"] = spec["selected_proposal_id"]
        record["k_scheduled"] = len(samples)
        records.append(record)

    #  The cursor advances only past what was OFFERED, and never because a ballot failed.
    offered = cursor.setdefault("offered", {})
    for party, pick in picks.items():
        offered.setdefault(party, [])
        if pick.pid not in offered[party]:
            offered[party].append(pick.pid)
    CURSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_PATH.write_text(json.dumps(cursor, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")

    out = REPO_ROOT / "corpus" / "artifacts" / args.cohort / f"{args.cohort}-authorization.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    sources = [{"path": str(p.relative_to(REPO_ROOT)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in sorted(raw_dir.glob(f"{args.cohort}-*-samples.json"))]
    out.write_text(json.dumps({
        "schema_version": "oagrc-agenda-activation-0.1",
        "artifact_type": "agenda_activation_record",
        "cohort": args.cohort,
        "rule": "singleton_ratification",
        "authorization_rule": ("One proposal is put to each party by a fixed rotation over its "
                               "own proposals. It is authorized only if every sample answers "
                               "with its id. Disagreement, refusal, invalid output or a missing "
                               "sample authorizes nothing."),
        "what_this_does_not_claim": ("That an authorized id is the party's preference, or that "
                                     "it is the best of that party's proposals. It is what every "
                                     "sampled invocation answered when shown one proposition."),
        "the_confound_in_this_cycle": (
            "The admitted queue is corpus/raw/agenda-01 — questions written BLIND, before any "
            "party could read the record. agenda-03's written candidates are recorded and not "
            "admitted. 23 of 25 ballot samples there named a newly written question and 2 named "
            "a blind proposal, so this cycle ballots the material the parties prefer least. A "
            "poor result here is evidence about the material as much as about the rule."),
        "enforced_in_load_queue": False,
        "sources": sources,
        "by_party": records,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\n  authorization → {out.relative_to(REPO_ROOT)}")
    for record in records:
        print(f"    {record['party']:8} offered {record.get('offered_proposal_id','?'):6} "
              f"{record['selection_outcome']:15} {record.get('category',''):20} "
              f"{record['active_proposal_id'] or ''}")
    if failed:
        print(f"  {len(failed)} party arm(s) failed: {', '.join(failed)}")
    return 1 if len(failed) == len(specs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
