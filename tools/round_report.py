#!/usr/bin/env python3
"""A report on one round, written by a party that is not the moderator.

    python3 tools/round_report.py --round round-000
    python3 tools/round_report.py --round round-000 --dry-run

WHY QWEN AND NOT THE MODERATOR.

Gemini made *"the conflicted moderator retains the power to unilaterally synthesize
findings"* a condition of **declining to participate**, and external review
independently proposed the same remedy: a non-target party drafts the synthesis.
The moderator writing what a round established is the objection; a different party
writing it is the fix.

`qwen3.6-35b-a3b` is the party for it. Its provenance can be complete -- exact
weights, quantisation, sampling parameters, requested seed -- which is true of no
other party here, and k >= 5 costs about ninety seconds.

WHY PER ROUND AND NOT PER DAY.

A daily report produces filler on days nothing was deliberated, which is the same
failure as an hourly round: output guaranteed whether or not there is anything to
say. A round is the unit that either happened or did not.

WHY THE INPUT IS A WHOLE ROUND'S SUMMARIES AND NEVER AN EXCERPT.

Measured against qwen3.6's 24,576-token context:

    all raw material            ~537,000 tokens     21x the budget
    one round's raw samples     ~118,000 tokens    4.8x
    the founding transcript      ~31,800 tokens    1.3x
    ONE ROUND'S SUMMARIES         ~4,000 tokens    fits

So a report on "the deliberations" is impossible: the author cannot hold them, and
chunk-and-summarise is forbidden by QCP §2 -- *a summary of the record produced by a
model that cannot hold the record* is the interpretive-artifact-promoted-to-fact
defect at D-16. This tool therefore reports on ONE round, from that round's
summaries ENTIRE, and **refuses if they do not fit**. It never selects an excerpt,
because QCP §6 measured this model deferring to emphatic assertion in text it
judges -- whoever chooses what it sees writes the report.

WHAT THE OUTPUT IS AND IS NOT.

One party's reading of one round, at k >= 5 with computed variance. Not the
record's account of itself, not a consensus, not a finding. The moderator does not
edit it; it is published as returned, and where its categorical fields disagree
with its own prose that disagreement is published too -- D-24 has produced exactly
that twice, both times from this model.

Exit status is 0 when a report was produced, non-zero on refusal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_ENDPOINT = "http://127.0.0.1:5001/v1/chat/completions"

#  THE REPORTER IS NO LONGER THE LOCAL PARTY, for two reasons that arrived together.
#
#  1. It has to see the ANSWERS, not just their distribution, or the report is a commentary on
#     entropy. Round 011's answers are ~30,000 tokens; qwen3.6 holds 24,576, so the tool
#     correctly refused. Excerpting is forbidden -- whoever chooses what the reporter sees
#     writes the report.
#  2. Qwen PARTICIPATED in round 011. Reporting on a round it answered in is the conflict at
#     D-09 and D-11 operating on the synthesis, which is the objection a consulted party made a
#     condition of declining to participate. The reporter must not be a party to the round.
#
#  Kimi K3 (Moonshot AI) is the strongest model on the router from a lineage that appears
#  nowhere else in this record -- not Anthropic, OpenAI, Google, xAI, or Alibaba, all of which
#  are parties. Its 1,048,576-token context holds a round's answers with room to spare, so
#  nothing has to be selected for it.
#
#  What it costs: the reporter's provenance is now WEAKER than qwen's, not stronger. A routed
#  invocation cannot have its weights, quantisation or seed recorded, and every hop between the
#  question and the answer is an intermediary this record cannot describe. That is a real loss
#  and it is the price of the reporter being able to read what it reports on.
#  GLM-5.2 rather than Kimi K3, on price at k >= 5: $0.47/$1.49 per M against $3.00/$15.00, so
#  a five-sample report costs roughly a tenth as much for the same 1M context. Kimi's first
#  attempt failed 5/5 on `finish_reason='length'` -- every sample truncated at exactly 4,000
#  completion tokens -- which was a MAX_TOKENS defect and not a verdict on the model. Swapping
#  models without raising the limit would have reproduced it exactly.
REPORTER_MODEL = "z-ai/glm-5.2"
REPORTER_IDENTITY = ("GLM-5.2 (Z.ai / Zhipu), reached as a routed API invocation "
                     "(z-ai/glm-5.2 via OpenRouter). NOT a party to any round it reports on, "
                     "and from a lineage that appears nowhere else in this record.")

#  A six-field structured report on a whole round's answers is not a 1,800-token reply. The
#  first live attempt gave it 4,000 and every sample was cut off mid-string.
REPORT_MAX_TOKENS = 12_000
BUDGET_TOKENS = 1_048_576
INPUT_CEILING = int(BUDGET_TOKENS * 0.55)          # room for the instruction and the answer

SCHEMA = {
    "type": "object",
    "properties": {
        "what_was_asked": {"type": "string"},
        "where_the_parties_differed": {"type": "string"},
        "did_any_party_refuse_or_reject_the_premise": {"type": "string"},
        "what_this_round_did_not_settle": {"type": "string"},
        "what_a_reader_should_not_conclude": {"type": "string"},
        "confidence_in_this_reading": {"type": "string",
                                       "enum": ["high", "moderate", "low",
                                                "cannot_report_from_what_was_shown"]},
    },
    "required": ["what_was_asked", "where_the_parties_differed",
                 "did_any_party_refuse_or_reject_the_premise",
                 "what_this_round_did_not_settle", "what_a_reader_should_not_conclude",
                 "confidence_in_this_reading"],
    "additionalProperties": False,
}


def _payload(item: dict) -> dict:
    """One sample's answer fields, whichever tool wrote the file."""
    for key in ("parsed", "response", "content"):
        value = item.get(key)
        if isinstance(value, dict) and value:
            return value
        if isinstance(value, str) and value.strip():
            try:
                out = json.loads(value)
                if isinstance(out, dict):
                    return out
            except Exception:                                             # noqa: BLE001
                return {"answer": value}
    return {}


def gather(round_id: str) -> tuple[str, list[dict]]:
    """Every summary AND every answer for the round, entire. No selection.

    The reporter used to be shown distributions only, so it could describe the SHAPE of a round
    and not what anybody said -- a commentary on entropy rather than on responses. It now
    receives every accepted answer verbatim.

    That is only possible because the reporter has a large context. Selecting a representative
    answer per party would be the moderator choosing what the reporter sees, and whoever chooses
    what it sees writes the report.
    """
    art = REPO_ROOT / "corpus" / "artifacts" / round_id
    raw_dir = REPO_ROOT / "corpus" / "raw" / round_id
    if not art.is_dir():
        raise SystemExit(f"REFUSED: no artifacts for {round_id}")
    anchors, blocks = [], []
    for path in sorted(art.glob("*summary.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        anchors.append({"path": str(path.relative_to(REPO_ROOT)),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        slug = doc["slug"]
        answers = []
        raw_path = raw_dir / f"{slug}-samples.json"
        if raw_path.is_file():
            anchors.append({"path": str(raw_path.relative_to(REPO_ROOT)),
                            "sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest()})
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            for item in (raw.get("samples") or raw.get("responses") or []):
                if item.get("ok") is False:
                    continue
                payload = _payload(item)
                if payload:
                    answers.append({"sample_index": item.get("sample_index"),
                                    **{k: v for k, v in payload.items() if k != "sources"}})
        blocks.append({"party": doc.get("contributor", {}).get("identity", doc["slug"]),
                       "k_collected": doc.get("k_collected"),
                       "question": doc.get("question"),
                       "variance": doc.get("variance"),
                       "every_answer_collected": answers})
    if not blocks:
        raise SystemExit(f"REFUSED: {round_id} has no summaries yet")
    return json.dumps(blocks, indent=2, ensure_ascii=False), anchors


def build_prompt(round_id: str, material: str) -> str:
    return f"""You are asked to report on one round of a public deliberation, for readers of the
record. You are not its moderator and you are not being asked to endorse anything.

Below is the COMPLETE material for {round_id}. Nothing has been selected, excerpted,
or characterised for you: this is every summary the round produced AND every answer
each party gave, verbatim. Each block gives a party, how many samples were collected
from it, the distribution of its categorical answers with entropy, and the full text
of every one of those answers.

A shared categorical label is a shape, not agreement: this corpus has measured a
party holding two incompatible positions under one label. Read the answers.

{material}

Write a report a reader can use. Say what was asked, WHERE THE PARTIES DIFFERED, and
whether any party refused or rejected the premise. Then say what the round did not
settle, and what a reader should not conclude from it.

If the material shown is not enough to report from, say so in
`confidence_in_this_reading` and explain what is missing. That is a complete answer.

You are one party reading one round. Your report is published as that, beside the
summaries it was written from, and it is not the record's account of itself."""


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--round", required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    material, anchors = gather(args.round)
    prompt = build_prompt(args.round, material)
    est = int(len(prompt.encode()) / 3.4)
    #  anchors counts BOTH the summary and the raw samples file per party, since the reporter
    #  now reads the answers as well as the distributions. Calling it "summaries" over-counted
    #  the parties two-to-one in the tool's own report of what it was doing.
    print(f"  {args.round}: {len(anchors)} anchored file(s), prompt ~{est:,} est-tokens "
          f"(ceiling {INPUT_CEILING:,})")

    if est > INPUT_CEILING:
        print("REFUSED: the round's summaries do not fit the author's context.")
        print("  This tool does NOT excerpt. Selecting what the reporter sees would make the")
        print("  selector the author -- QCP §6 measured this model deferring to emphatic")
        print("  assertion in text it judges. A round that does not fit gets no report.")
        return 1

    spec = {
        "slug": f"{args.round}-report", "identity": REPORTER_IDENTITY,
        "contribution_class": "CONTRIBUTION — one party's report on one round",
        "contribution_class_note": ("Written by a party that is NOT the moderator, because a "
                                    "consulted party made unilateral synthesis by the conflicted "
                                    "moderator a condition of declining. Not a consensus, not a "
                                    "finding, not the record's account of itself."),
        "question": f"How should a reader understand {args.round}?",
        "phase": "Phase-2 (informed)",
        "phase_justification": ("Shown the round's complete summaries, unexcerpted. Nothing was "
                                "selected for it."),
        "seed_base": 9800, "schema_name": "round_report", "schema": SCHEMA,
        "variance_fields": ["confidence_in_this_reading"],
        "k_policy": f"k={args.k}; a single report is a draw, not a reading.",
        "source_excerpt": {"path": f"corpus/artifacts/{args.round}/",
                           "sha256": hashlib.sha256(material.encode()).hexdigest()},
        "input_anchors": anchors,
        "reachability_target": "A reading of a round by someone other than its moderator.",
        "prompt": prompt, "arm": "Complete summaries, no excerpt.",
    }
    spec_dir = REPO_ROOT / "record" / "solicitations" / args.round
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{args.round}-report.json"
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.dry_run:
        print(f"  DRY RUN — spec written to {spec_path.relative_to(REPO_ROOT)}, nothing solicited.")
        return 0

    cmd = [sys.executable, "tools/solicit_api.py", "--spec", str(spec_path),
           "--k", str(args.k), "--temperature", "0.7",
           "--max-tokens", str(REPORT_MAX_TOKENS),
           "--model", REPORTER_MODEL, "--out-round", args.round]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    print(result.stdout.strip()[-400:] or result.stderr[-300:])
    if result.returncode != 0:
        print("REFUSED: the report was not collected. Nothing published.")
        return 1
    print(f"\n  report collected for {args.round}. Published as ONE PARTY'S READING,")
    print("  beside the summaries it was written from. The moderator does not edit it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
