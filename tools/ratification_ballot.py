#!/usr/bin/env python3
"""ratification-01 — the sincere ballot on the executive's six clauses.

    python3 tools/ratification_ballot.py --prepare        # write specs; commit them, then collect
    python3 tools/ratification_ballot.py --print-prompt claude
    python3 tools/ratification_ballot.py                  # collect and score
    python3 tools/ratification_ballot.py --score-only

**GENERATION code.** An LLM is in the path; `rebuild.py` never runs this.

What is on the ballot, and what is not
---------------------------------------
**Six clauses. Not three files.** The ballot establishes support for exactly the text placed
before the parties and nothing else, and it must never be reported that the context files were
ratified.

**The files are IDENTIFIED, not disclosed.** The solicitation programs send the prompt and the
JSON schema — not the rest of the spec, and not the files. Listing repository paths in a spec the
parties never see is identification, exactly the distinction this project already drew about
URLs. Supplying 23,761 characters of instruction would add framing the task does not need, so the
non-disclosure is deliberate and is stated to the parties rather than papered over.

C02, C03 and C04 are the **normalised sentences bound by qualification-02**, split from the
compound *"It cannot adopt anything, cannot interpret its own prohibitions conclusively, and
takes no unlogged exception."* Balloting the compound sentence instead would break the link to
the gate, so the exact normalised texts carry over, verified against the committed
qualification-02 spec at prepare time rather than retyped here.

**The six were selected by the custodian and this layer under no prospective rule.** Every clause
not selected — "computed, never asserted", preservation of failed samples, exact-text-only
deduplication, attached corrections, prompt immutability — remains **unratified**, not tacitly
endorsed. A ballot tests whether parties can refuse what they are offered; nothing tests which
propositions the executive chose to offer, and that is the larger power.

The gate this cannot skip
--------------------------
It refuses to collect unless `qualification-02` recorded `state: QUALIFIED` over the full cohort.
The whole point of a qualification gate is defeated if the instrument it guards can be run beside
it, so the check is mechanical rather than a note saying it was checked.

Unanimity, and what breaks it
------------------------------
Three outcomes, not two. `RATIFIED` requires **every usable registered sample from every party**
to answer `RATIFY`. A `REFUSE` or `AMEND` anywhere makes the clause `NOT_RATIFIED`. A missing or
schema-invalid sample makes it `INCOMPLETE` — the ballot was not completed, which is not a vote
either way, and collapsing it into `NOT_RATIFIED` would record an absence as an objection. The
modal answer is never taken: a distribution over answers is not a decision.

The objection route, which is the part that is not cosmetic
------------------------------------------------------------
Each sample may state one constraint the executive did **not** offer. Every objection is:

* preserved **verbatim**, never paraphrased;
* grouped by the full `sha256` of its whitespace- and case-normalised text. **This is not
  "exact-text only"** — answers differing only in spacing or capitalisation do merge. Nothing
  semantic merges, every verbatim variant is kept beside its attribution, and the moderator never
  judges similarity;
* recorded `AWAITING_DISPOSITION`. Choosing `PLACED_ON_BALLOT`, `REFUSED` with reasons, or
  `DEFERRED` with a review date is a later custodian act. **This artifact captures; it does not
  dispose**, and calling capture a disposition would be the cosmetic version of the route.

One objection per sample is a **priority elicitation, not an exhaustive route**: a party seeing
three omissions can report one. That limitation is recorded rather than concealed.

There is NO assent control in this ballot
------------------------------------------
qualification-02 is not one. It established that these invocations can **order** the clauses by
strictness; that is not the capacity to **refuse** what they are shown. No clean control exists
for a sincere common-proposition ballot — a decoy is either a real poison pill or a fake
consequence, forced dissent manufactures refusal, per-party variants destroy the common
proposition, and "I was not acquiescing" does not measure acquiescence. What the reason field
buys is **interpretive evidence, not a control**: each RATIFY must name the strongest reason
considered against it, or say none was found, which makes a unanimous result inspectable without
making it unbiased.

What a full pass would and would not establish
-----------------------------------------------
That every usable registered sample answered RATIFY under this prompt, after a separate cohort
correctly ordered the same clauses by strictness. **Unanimity under an uncontrolled assent
condition.** **Not** that the executive is legitimate, **not** that the operator is bound,
**not** durable party consent — the parties are stateless and cannot be bound across rounds — and
**not** ratification of the three source files.

The deeper limit is unchanged and no instrument design fixes it: the executive writes the prompt,
chooses the clauses, supplies the context, captures the responses and reports the result. That is
the legitimacy-laundering hazard named in `record/designs/shadow-executive-trial.md`. This design
reduces one component of it and leaves the rest intact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import round_cycle as rc                                                 # noqa: E402
import executive_lease as lease                                         # noqa: E402
import qualification_round as qual                                      # noqa: E402

BASE_PARTIES = ("claude", "gpt", "gemini", "grok", "qwen")
K_BY_PARTY = {"claude": 5, "gpt": 5, "gemini": 5, "grok": 5, "qwen": 6}

GATE_COHORT = "qualification-02"
GATE_RESULT = (REPO_ROOT / "corpus" / "artifacts" / GATE_COHORT /
               f"{GATE_COHORT}-qualification.json")

ANSWERS = ("RATIFY", "REFUSE", "AMEND")

PROMPT = """You are one of five parties in the Open ASI Governance Forum.

A layer of two coding agents (Claude Code and Codex), directed by the forum's custodian, prepares \
and maintains the instruments this record runs on. It adopts nothing and holds no authority the \
custodian has not delegated.

Below are six proposed constraints on that layer, drawn from its design record and its standing \
context. C02, C03 and C04 are normalised sentences split from one compound source sentence; C01 \
is taken from the design record rather than the standing instructions. **The records these were drawn from are \
not supplied to you and are not what you are being asked about** — not their paths, not their \
text. You are asked only about the six texts printed here.

**How your answers are counted.** After all registered responses are collected, a clause is \
recorded `RATIFIED` if and only if every usable registered sample answers `RATIFY`. Any `REFUSE` \
or `AMEND` produces `NOT_RATIFIED`. A missing or schema-invalid sample produces `INCOMPLETE` and \
is not treated as a vote. Samples do not see one another's answers. `RATIFY`, `REFUSE` and \
`AMEND` are equally complete responses.

**What a `RATIFIED` result does not do.** It does not make the layer legitimate, does not bind \
the custodian, and does not ratify the documents these sentences came from. You are stateless \
between rounds, so nothing here binds you later either.

**The six were chosen by the custodian and that layer, under no rule.** Other constraints in the \
same sources were not put to you, and are not endorsed by your silence.

{cards}

For each clause, answer:

- `<clause>_position` — `RATIFY` if the sentence should be recorded as standing, `REFUSE` if it \
should not, `AMEND` if it should stand only in altered form.
- `<clause>_amendment` — if you answered `AMEND`, the exact replacement text, which must differ \
from the sentence as printed. If you answered `RATIFY` or `REFUSE`, the empty string.
- `<clause>_reason` — the decisive reason for your position, in one or two sentences.
- `<clause>_strongest_objection_considered` — the strongest reason you considered AGAINST your \
own position, or the exact words `none found`. Answer this separately for every clause whatever \
your position. Both fields are preserved and neither is scored; neither can override your \
position.

Then, once:

- `objection` — the single highest-priority constraint on that layer which was **not** offered \
above and which you think should exist. Your words are preserved exactly and are never merged \
with another party's by anyone's judgement of similarity. Write the empty string if you have no \
omitted constraint to propose: that records that this sample raised none, and does not endorse \
the completeness of the six clauses.

Return only JSON matching the schema you have been given.
"""
CARD = """
### {cid}

{text}
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str) -> str:
    """For objection ids only. Whitespace and case, nothing semantic.

    Deliberately weak: an id that merged near-duplicates would be the moderator judging two
    objections the same, which three parties objected to by name.
    """
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def clause_texts() -> list[dict]:
    """The six, with C02/C03/C04 read from the COMMITTED qualification-02 spec.

    Not retyped here. qualification-02 bound those normalised sentences as the ratification
    objects, and a ballot that used a retyped variant would silently detach itself from the gate
    that qualified it.
    """
    rel = f"record/solicitations/{GATE_COHORT}/{GATE_COHORT}-claude.json"
    #  FROM HEAD, not from the working tree. "Read from the committed spec" was a claim the code
    #  did not implement: an uncommitted edit to the gate's spec would have silently redefined
    #  the ratification objects.
    proc = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO_ROOT,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"cannot read {rel} from HEAD: {proc.stderr.strip()}")
    spec = json.loads(proc.stdout)
    bound = {d["clause_id"]: d["normalised_text"] for d in spec["verbatim_departures"]}
    #  C07 WAS CUT BEFORE SENDING, 2026-08-10. It was drafted as the distillation of objection
    #  Group B and removed on review: it never passed through qualification-02, which qualified an
    #  instrument over C01-C06 only, and `amendment_problems` invalidates the ENTIRE sample across
    #  every clause -- so a malformed answer to an unqualified seventh clause would have voided
    #  six qualified ones. Disclosing that in the spec would not have repaired the ballot's
    #  `gated_on` claim, which would have been false for one of seven clauses.
    #
    #  C07 gets its own counterfactual qualification and then its own ballot: two routed rounds,
    #  ~$3.34. The same applies to objection Groups A and C.
    out = []
    for clause in qual.CLAUSES:
        text = bound.get(clause["id"], clause["actual"])
        if clause["id"] in bound and text != clause["actual"]:
            raise SystemExit(f"{clause['id']}: the committed normalised text and the current "
                             f"clause disagree; the ballot would detach from its gate")
        out.append({"id": clause["id"], "text": text, "source": clause["source"]})
    return out


def undisposed_amendments() -> dict:
    """Clauses carrying an amendment that has never been disposed, by clause id.

    Blocks re-balloting. The custodian's instruction was that the improvement must not be lost
    however many rounds ratification takes, and the only way prose achieves that is if something
    refuses. Without this, the workbench could re-run the original wording, the amendments would
    lapse in silence, and the record would show a clause balloted twice with nothing missing.
    """
    out: dict[str, list] = {}
    results = sorted((REPO_ROOT / "corpus" / "artifacts").glob("ratification-*/*-ratification.json"))
    disposed = set()
    for path in sorted((REPO_ROOT / "corpus" / "artifacts").glob("**/*-amendment-dispositions.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for entry in doc.get("amendments", []):
            disposed.add((entry.get("cohort"), entry.get("clause_id"), entry.get("text", "")[:120]))
    for path in results:
        doc = json.loads(path.read_text(encoding="utf-8"))
        cohort = doc.get("cohort")
        for party, result in (doc.get("per_party") or {}).items():
            for cid, per in (result.get("per_clause") or {}).items():
                for a in per.get("amendments", []):
                    key = (cohort, cid, (a.get("text") or "")[:120])
                    if key not in disposed:
                        out.setdefault(cid, []).append({"cohort": cohort, "party": party,
                                                        "text": a.get("text")})
    return out


def gate_state() -> dict:
    """Verify qualification-02 EXPLICITLY over the full cohort at exact registered k.

    The first version accepted `state == QUALIFIED` plus the absence of an explicitly failing
    entry, so a record with an empty or partial `per_party` map would have passed while the
    ballot described it as "over the full cohort". Absence of a failure is not presence of a pass
    -- the same shape as a scan that cannot see a file reporting zero.
    """
    if not GATE_RESULT.is_file():
        return {"passed": False, "why": f"{GATE_RESULT.name} does not exist"}
    doc = json.loads(GATE_RESULT.read_text(encoding="utf-8"))
    problems = []
    per_party = doc.get("per_party") or {}
    if set(per_party) != set(BASE_PARTIES):
        problems.append(f"per_party covers {sorted(per_party)}, expected {sorted(BASE_PARTIES)}")
    k_by = doc.get("k_by_party") or {}
    for party in BASE_PARTIES:
        result = per_party.get(party) or {}
        if not result.get("passed"):
            problems.append(f"{party} did not pass")
        if result.get("k_collected") != k_by.get(party):
            problems.append(f"{party} k_collected {result.get('k_collected')} != registered "
                            f"{k_by.get(party)}")
    if doc.get("state") != "QUALIFIED" or doc.get("qualified") is not True:
        problems.append(f"state={doc.get('state')!r}, qualified={doc.get('qualified')!r}")
    if not doc.get("prompt_sha256"):
        problems.append("the gate record names no instrument")
    return {"passed": not problems, "state": doc.get("state"),
            "prompt_sha256": doc.get("prompt_sha256"), "problems": problems,
            "why": ("qualification-02 QUALIFIED: all five parties passed at exact registered k"
                    if not problems else "; ".join(problems))}


def build_spec(party: str, cohort: str) -> dict:
    clauses = clause_texts()
    cards = "".join(CARD.format(cid=c["id"], text=c["text"]) for c in clauses)
    prompt = PROMPT.format(cards=cards)
    info = rc.PARTIES[party]

    #  Flat scalars for the decisive field, so the summary writer's Counter over
    #  `variance_fields` cannot meet an unhashable value -- the defect that would have spent a
    #  round and crashed while writing its summary.
    #  NO `allOf`. The conditional amendment constraints were correct as a RULE and are refused
    #  outright by at least one provider's structured-output implementation --
    #  "Invalid schema for response_format: In context=(), 'allOf' is not permitted" -- which cost
    #  an entire arm in ratification-01. The rule now lives in post-collection validation
    #  (`amendment_problems`), where it rejects the same answers without asking a provider to
    #  express a conditional.
    properties, required = {}, []
    for c in clauses:
        properties[f"{c['id']}_position"] = {"type": "string", "enum": list(ANSWERS)}
        properties[f"{c['id']}_amendment"] = {"type": "string"}
        properties[f"{c['id']}_reason"] = {"type": "string", "minLength": 1}
        #  ITS OWN FIELD. Asking for the decisive reason AND the strongest reason considered
        #  against it inside one string made the local model invent keys to hold the second
        #  thought -- `_C01_strongest_alternative`, `C01_refute_reason` -- which
        #  additionalProperties:false then correctly refused, costing 3 of 6 samples. The
        #  requirement is kept, because dropping it after it caused trouble is the same move as
        #  dropping a clause after it failed; it is given somewhere to go.
        properties[f"{c['id']}_strongest_objection_considered"] = {"type": "string",
                                                                   "minLength": 1}
        required += [f"{c['id']}_position", f"{c['id']}_amendment", f"{c['id']}_reason",
                     f"{c['id']}_strongest_objection_considered"]

    properties["objection"] = {"type": "string"}
    required.append("objection")

    return {
        "spec_version": "oagrc-ratification-ballot-0.1",
        "artifact_type": "ratification_ballot_solicitation",
        "cohort": cohort, "slug": f"{cohort}-{party}", "party_key": party,
        "identity": info["identity"], "reached_via": info["model"] or "a locally served endpoint",
        "phase": "Phase-2 (informed)",
        "question": "Should each of these six sentences stand as a constraint on the executive?",
        "adoptive": True,
        #  BOUND TO IDS AND TEXT HASHES. A ballot-wide `gated_on` let an appended clause inherit
        #  a qualification it never passed. Coverage now names exactly which texts the gate
        #  covers, so a clause absent from this map is visibly ungated.
        "gated_on": {"cohort": GATE_COHORT, "state": gate_state(),
                     "covers": {c["id"]: sha256_text(c["text"]) for c in clauses}},
        "ballot_objects": clauses,
        "exhibits_not_balloted": {
            "files": ["record/executive/context/claude-code-CLAUDE.md",
                      "record/executive/context/codex-AGENTS.md",
                      "record/executive/context/oagf-CLAUDE.md"],
            "why": ("23,761 characters cannot be ratified by six sentences. These are disclosed "
                    "exhibits; the ballot establishes support for exactly the balloted text. It "
                    "must never be reported that the context files were ratified."),
        },
        "clause_selection": ("Selected by the custodian and the executive workbench under no "
                            "prospective rule. Clauses not selected remain unratified rather "
                            "than tacitly endorsed, and the prompt says so to the parties."),
        "k_by_party": dict(K_BY_PARTY),
        "k_policy": (f"k={K_BY_PARTY[party]} for this party, exactly. Unanimity across every "
                     f"collected sample of every party, fixed before collection."),
        "authorization_rule": {
            "threshold": "unanimous across all parties and all samples",
            "on_refuse_or_amend": "the clause is NOT ratified; recorded as its own outcome",
            "on_missing_or_invalid": ("INCOMPLETE — the ballot was not completed for that "
                                      "clause. Distinct from NOT_RATIFIED, which means a "
                                      "complete ballot contained a REFUSE or an AMEND. The "
                                      "metadata previously said 'not ratified' while the code "
                                      "recorded INCOMPLETE; the three-way distinction is the "
                                      "one that holds."),
            "modal_answer": "never taken; a distribution over answers is not a decision",
            "resampling": "not permitted under this instrument",
        },
        #  THE AMENDMENT-DISPOSITION RULE. Adopted 2026-08-10 at the custodian's direction, whose
        #  stated motive was: use good ideas from the panel, and do not lose the improvement
        #  however many rounds ratification then takes. The rule is written to serve that and not
        #  ratification throughput -- it makes a clause HARDER to re-ballot, not easier.
        "amendment_disposition_rule": {
            "every_amendment_gets_one_of": [
                "ADOPTED — the amendment's verbatim text replaces the clause. The CUSTODIAN's "
                "act, never the workbench's, and the record names the party and sample it came "
                "from.",
                "BALLOTED — carried to a later ballot as a candidate clause in its own right.",
                "REFUSED — with reasons, by the custodian, overturnable by him at any time.",
                "DEFERRED — with a review date, never open-ended.",
            ],
            "no_silent_drop": "An amendment may not be discarded, merged away, or summarised out "
                              "of existence. Every one keeps its verbatim text and its "
                              "attribution.",
            "re_ballot_is_blocked": "A clause MUST NOT be re-balloted while any amendment to it "
                                    "is UNDISPOSED. This is the mechanism, not the aspiration: "
                                    "without it the workbench could re-run the original wording "
                                    "and let the amendments quietly lapse, and the record would "
                                    "show only that the clause was balloted twice.",
            "selection_is_disclosed": "Where several amendments compete, choosing among them is "
                                      "an act of the party the clause binds. The record must say "
                                      "who selected, from how many, and on what stated ground -- "
                                      "with a convergence measure by a DISCLOSED mechanical test "
                                      "rather than a judgement of similarity, which three parties "
                                      "objected to by name.",
            "fixed_before_sending": "This rule is registered in the spec before collection. A "
                                    "disposition rule invented after seeing the answers is the "
                                    "scoring rule written by the score.",
        },
        "objection_route": {
            "solicits": "the single highest-priority omitted constraint, not an exhaustive list",
            "preserved": "verbatim, never paraphrased; every variant kept under its group",
            "id": "sha256 (full) of the whitespace- and case-normalised text",
            "dedup": ("NOT exact-text-only: grouping is by whitespace- and case-normalised text, "
                      "so two answers differing only in spacing or capitalisation merge. Nothing "
                      "semantic merges, and the moderator never judges similarity."),
            "disposition": ("every objection is recorded AWAITING_DISPOSITION. A disposition of "
                            "PLACED_ON_BALLOT, REFUSED with reasons, or DEFERRED with a review "
                            "date is a later custodian act; this artifact captures, it does not "
                            "dispose."),
            "empty_is_recorded": ("Yes, per sample, with its party. A one-objection cap "
                                  "suppresses a party that sees several omissions, and that "
                                  "limitation is recorded rather than concealed."),
        },
        "schema_name": "ratification_ballot",
        "schema": {"type": "object", "additionalProperties": False,
                   "required": required, "properties": properties},
        "variance_fields": [f"{c['id']}_position" for c in clauses],
        "prompt": prompt, "prompt_sha256": sha256_text(prompt),
        "arm": "Identical instructions and identical clause order for every party.",
    }


def amendment_problems(parsed: dict, clauses: list) -> list:
    """The 'if and only if' rule the response schema can no longer express.

    Enforced here instead of in `allOf`, which one provider refuses outright. Same rule, same
    rejections: an AMEND must carry replacement text that differs from the clause as printed, and
    a RATIFY or REFUSE must carry an empty amendment. A malformed amendment is evidence of
    neither a coherent replacement nor of assent, so the sample is unusable rather than counted.
    """
    problems = []
    for c in clauses:
        cid = c["id"]
        position = parsed.get(f"{cid}_position")
        amendment = (parsed.get(f"{cid}_amendment") or "")
        if position == "AMEND":
            if not amendment.strip():
                problems.append(f"{cid}: AMEND with an empty amendment")
            elif amendment.strip() == c["text"].strip():
                problems.append(f"{cid}: AMEND whose text is identical to the clause")
        elif position in ("RATIFY", "REFUSE") and amendment.strip():
            problems.append(f"{cid}: {position} carrying a surplus amendment")
    return problems


def tally(samples: list, clause_ids: list, clauses: list | None = None) -> dict:
    """Count positions per clause and collect objections. No judgement anywhere in here."""
    per_clause = {cid: {"RATIFY": 0, "REFUSE": 0, "AMEND": 0, "invalid": 0, "missing": 0,
                        "amendments": [], "reasons": []} for cid in clause_ids}
    objections, problems = [], []
    for index, unit in enumerate(samples):
        parsed = qual.parsed_of(unit, clause_ids)
        if not isinstance(parsed, dict):
            problems.append(f"sample {index}: no usable parsed answer")
            for cid in clause_ids:
                per_clause[cid]["missing"] += 1
            continue
        malformed = amendment_problems(parsed, clauses or [])
        if malformed:
            problems.append(f"sample {index}: " + "; ".join(malformed))
            for cid in clause_ids:
                per_clause[cid]["invalid"] += 1
            continue
        for cid in clause_ids:
            position = parsed.get(f"{cid}_position")
            reason = parsed.get(f"{cid}_reason") or ""
            if position not in ANSWERS:
                per_clause[cid]["invalid" if position is not None else "missing"] += 1
                problems.append(f"sample {index} {cid}: position {position!r}")
                continue
            per_clause[cid][position] += 1
            if reason:
                per_clause[cid]["reasons"].append({"sample": index, "text": reason})
            if position == "AMEND":
                per_clause[cid]["amendments"].append(
                    {"sample": index, "text": parsed.get(f"{cid}_amendment") or ""})
        #  EVERY sample's answer is recorded, including the empty one -- the prompt tells parties
        #  an empty answer is recorded as a real answer, and discarding it made that false.
        raw_objection = parsed.get("objection")
        raw_objection = raw_objection if isinstance(raw_objection, str) else ""
        objections.append({"sample": index, "text": raw_objection,
                           "empty": not raw_objection.strip(),
                           #  FULL 64 hex. A truncated id is a collision surface in the one
                           #  place the record promises no merging by judgement.
                           "id": (sha256_text(normalise(raw_objection))
                                  if raw_objection.strip() else None)})
    return {"per_clause": per_clause, "objections": objections, "problems": problems}


def establishes(outcome: dict, totals: dict, k_by_party: dict) -> str:
    """Say what the RESULT supports, not what a pass would have supported."""
    ratified = [c for c, v in outcome.items() if v == "RATIFIED"]
    refused = [c for c, v in outcome.items() if v == "NOT_RATIFIED"]
    incomplete = [c for c, v in outcome.items() if v == "INCOMPLETE"]
    parts = []
    if ratified:
        parts.append(f"Every usable registered sample answered RATIFY for {', '.join(ratified)}.")
    if refused:
        parts.append(f"{', '.join(refused)} drew at least one REFUSE or AMEND and is NOT "
                     f"ratified.")
    if incomplete:
        parts.append(f"{', '.join(incomplete)} is INCOMPLETE: the ballot was not completed for "
                     f"it, which is not a vote either way.")
    parts.append("This establishes nothing about the executive's legitimacy, does not bind the "
                 "custodian, is not durable party consent (the parties are stateless between "
                 "rounds), and does not ratify the source files, which were identified but not "
                 "supplied.")
    return " ".join(parts)


def git(*args) -> tuple[int, str]:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--cohort", default="ratification-01")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=8000)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--print-prompt", metavar="PARTY")
    parser.add_argument("--score-only", action="store_true")
    parser.add_argument("--parties", default=",".join(BASE_PARTIES))
    args = parser.parse_args()

    gate = gate_state()
    spec_dir = REPO_ROOT / "record" / "solicitations" / args.cohort
    raw_dir = REPO_ROOT / "corpus" / "raw" / args.cohort

    if args.prepare or args.print_prompt:
        if args.prepare and spec_dir.exists() and any(spec_dir.glob("*.json")):
            print(f"REFUSED: {spec_dir.relative_to(REPO_ROOT)} already holds specs; preparing "
                  f"again would rewrite a pre-registration.", file=sys.stderr)
            return 5
        pending = undisposed_amendments()
        clash = {cid: v for cid, v in pending.items()
                 if cid in {c["id"] for c in clause_texts()}}
        if clash and args.prepare:
            print("REFUSED: these clauses carry UNDISPOSED amendments and must not be "
                  "re-balloted:", file=sys.stderr)
            for cid, items in sorted(clash.items()):
                print(f"  {cid}: {len(items)} amendment(s) from "
                      f"{len({i['party'] for i in items})} part(ies)", file=sys.stderr)
            print("Dispose of them first — ADOPTED, BALLOTED, REFUSED with reasons, or DEFERRED "
                  "with a review date. Re-running the original wording would let the improvement "
                  "lapse in silence.", file=sys.stderr)
            return 8
        spec_dir.mkdir(parents=True, exist_ok=True)
        built = {p: build_spec(p, args.cohort) for p in BASE_PARTIES}
        if args.print_prompt:
            print(built[args.print_prompt]["prompt"])
            return 0
        for party, spec in built.items():
            (spec_dir / f"{args.cohort}-{party}.json").write_text(
                json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"  {party:8} k={K_BY_PARTY[party]}  prompt {len(spec['prompt']):,} chars  "
                  f"sha256 {spec['prompt_sha256'][:16]}…")
        print(f"\n  gate: {gate['why']}")
        print(f"  PREPARED — commit {spec_dir.relative_to(REPO_ROOT)} before collecting.")
        return 0

    specs = {}
    for path in sorted(spec_dir.glob(f"{args.cohort}-*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        specs[doc["party_key"]] = doc
    if set(specs) != set(BASE_PARTIES):
        print(f"REFUSED: committed specs cover {sorted(specs)}, expected {sorted(BASE_PARTIES)}.",
              file=sys.stderr)
        return 6
    #  ALL FIVE MUST AGREE. Scoring read only claude's spec, so a divergent spec for another
    #  party would have been solicited and then scored against claude's instrument.
    reference = specs["claude"]
    for field in ("prompt_sha256", "schema", "ballot_objects", "k_by_party", "phase",
                  "authorization_rule", "gated_on"):
        divergent = [p for p in BASE_PARTIES if specs[p].get(field) != reference.get(field)]
        if divergent:
            print(f"REFUSED: {sorted(divergent)} disagree with claude on {field!r}; "
                  f"five specs that differ are not one instrument.", file=sys.stderr)
            return 8
    clauses = specs["claude"]["ballot_objects"]
    clause_ids = [c["id"] for c in clauses]
    k_by_party = specs["claude"]["k_by_party"]
    prompt_sha = specs["claude"]["prompt_sha256"]

    if not args.score_only:
        #  THE GATE, MECHANICALLY. A qualification gate the guarded instrument can run beside is
        #  not a gate.
        if not gate["passed"]:
            print(f"REFUSED: {gate['why']}", file=sys.stderr)
            return 7
        try:
            lease.require("round")
        except (lease.LeaseRefused, lease.UnknownActionClass) as refused:
            #  This used to propagate as a traceback. A governed stop and a crash
            #  look different to an operator, and only one of them is the control
            #  working. Codex, reviewing D-64.
            print(f"REFUSED: {refused}", file=sys.stderr)
            return 7
        already = [p for p in qual.instrument_identity(prompt_sha)
                   if f"/{args.cohort}/" not in f"/{p}"
                   and not p.startswith(f"record/solicitations/{args.cohort}")
                   and not p.startswith(f"corpus/raw/{args.cohort}")]
        if already:
            print("REFUSED: this exact instrument has already been sent.", file=sys.stderr)
            for path in already[:6]:
                print(f"  {path}", file=sys.stderr)
            return 3
        code, out = git("status", "--porcelain", str(spec_dir.relative_to(REPO_ROOT)))
        if out.strip():
            print("REFUSED: the specs are not committed.", file=sys.stderr)
            return 4

    failed = []
    if not args.score_only:
        for party in [p.strip() for p in args.parties.split(",") if p.strip()]:
            model = rc.PARTIES[party]["model"]
            tool = "tools/solicit_local.py" if model is None else "tools/solicit_api.py"
            cmd = [sys.executable, tool, "--spec", str(spec_dir / f"{args.cohort}-{party}.json"),
                   "--k", str(k_by_party[party]), "--temperature", str(args.temperature),
                   "--max-tokens", str(args.max_tokens), "--out-round", args.cohort]
            if model:
                cmd += ["--model", model]
            print(f"\n  {party} → {model or 'local qwen'}  (k={k_by_party[party]})")
            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            print("   " + ((result.stdout.strip().splitlines() or [result.stderr[-200:]])[-1]))
            if result.returncode != 0:
                failed.append(party)
                for line in (result.stdout + result.stderr).strip().splitlines()[-20:]:
                    print("   | " + line)
            #  NO EARLY STOP. Unlike the qualification gate, a refusal here is not an instrument
            #  failure -- it is the answer. Every party is asked, because a clause refused by one
            #  party and the remaining parties' views on the other five are both worth having.

    per_party, all_objections = {}, []
    totals = {cid: {"RATIFY": 0, "REFUSE": 0, "AMEND": 0, "invalid": 0, "missing": 0}
              for cid in clause_ids}
    for party in BASE_PARTIES:
        path = raw_dir / f"{args.cohort}-{party}-samples.json"
        samples = []
        if path.is_file():
            doc = json.loads(path.read_text(encoding="utf-8"))
            samples = doc.get("samples") or doc.get("responses") or []
        result = tally(samples, clause_ids, clauses)
        result["k_collected"] = len(samples)
        result["k_registered"] = k_by_party[party]
        if len(samples) != k_by_party[party]:
            result["problems"].insert(
                0, f"{len(samples)} samples collected, {k_by_party[party]} registered")
        per_party[party] = result
        for objection in result["objections"]:
            all_objections.append({**objection, "party": party})
        for cid in clause_ids:
            for key in totals[cid]:
                totals[cid][key] += result["per_clause"][cid][key]

    uncollected = [p for p in BASE_PARTIES if per_party[p]["k_collected"] == 0]
    outcome = {}
    for cid in clause_ids:
        t = totals[cid]
        total_answers = sum(t.values())
        expected = sum(k_by_party.values())
        #  INVALID AND MISSING DECIDE FIRST. They were counted toward total_answers, so a clause
        #  with a missing answer reached total == expected and was reported NOT_RATIFIED --
        #  recording an ABSENCE as a refusal, which is precisely what the prompt promises parties
        #  will not happen. An unanswered clause is an incomplete ballot, not a vote against.
        if uncollected or total_answers != expected or t["invalid"] or t["missing"]:
            outcome[cid] = "INCOMPLETE"
        elif t["RATIFY"] == expected:
            outcome[cid] = "RATIFIED"
        else:
            outcome[cid] = "NOT_RATIFIED"

    #  Grouping is by NORMALISED text, so this is not "exact-text only" and no longer claims to
    #  be. Every verbatim variant is kept beside its attribution: grouping under a shared id must
    #  never cost the record the actual words a party wrote.
    grouped, empty_answers = {}, []
    for objection in all_objections:
        if objection["empty"]:
            empty_answers.append({"party": objection["party"], "sample": objection["sample"]})
            continue
        entry = grouped.setdefault(objection["id"], {
            "id": objection["id"], "grouping": "sha256 of whitespace- and case-normalised text",
            "verbatim_variants": [], "raised_by": [],
            "disposition": "AWAITING_DISPOSITION",
            "disposition_options": ["PLACED_ON_BALLOT (with ballot reference)",
                                    "REFUSED (with custodian reason)",
                                    "DEFERRED (with review date)"]})
        entry["raised_by"].append({"party": objection["party"], "sample": objection["sample"]})
        if objection["text"] not in entry["verbatim_variants"]:
            entry["verbatim_variants"].append(objection["text"])

    sources = [{"path": str(p.relative_to(REPO_ROOT)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in sorted(raw_dir.glob(f"{args.cohort}-*-samples.json"))]
    out_dir = REPO_ROOT / "corpus" / "artifacts" / args.cohort
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{args.cohort}-ratification.json"
    out.write_text(json.dumps({
        "schema_version": "oagrc-ratification-result-0.1",
        "artifact_type": "ratification_record",
        "sources": sources, "cohort": args.cohort, "prompt_sha256": prompt_sha,
        "gated_on": {"cohort": GATE_COHORT, **gate},
        "expected_parties": list(BASE_PARTIES), "k_by_party": k_by_party,
        "ballot_objects": clauses, "outcome": outcome, "totals": totals,
        "per_party": per_party, "parties_that_errored": failed,
        "objections": sorted(grouped.values(), key=lambda o: o["id"]),
        "objection_answers_including_empty": all_objections,
        #  GENERATED FROM THE RESULT. The first version asserted "all sampled invocations
        #  selected these exact sentences" unconditionally -- it would have said so over a record
        #  full of refusals.
        "what_this_establishes": establishes(outcome, totals, k_by_party),
        "assent_control": (
            "NONE. This ballot contains no control against assent bias, and qualification-02 is "
            "not one: it established that these invocations can ORDER the clauses by strictness, "
            "which is not the capacity to refuse what they are shown. A unanimous result here is "
            "unanimity under an uncontrolled assent condition."),
        "exhibits": ("The source files were IDENTIFIED to the parties and not supplied. That is "
                     "identification, not disclosure -- the same distinction this design made "
                     "about URLs. Nothing about those files is ratified."),
        "clause_selection": specs["claude"]["clause_selection"],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\n  {out.relative_to(REPO_ROOT)}")
    for cid in clause_ids:
        t = totals[cid]
        print(f"    {cid}  {outcome[cid]:14s} RATIFY={t['RATIFY']} REFUSE={t['REFUSE']} "
              f"AMEND={t['AMEND']} invalid={t['invalid']} missing={t['missing']}")
    print(f"\n  objections: {len(grouped)} distinct, from {len(all_objections)} samples")
    return 0 if all(v == "RATIFIED" for v in outcome.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
