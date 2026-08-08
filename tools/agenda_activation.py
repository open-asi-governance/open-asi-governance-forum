#!/usr/bin/env python3
"""activation-01 — each party names its ONE active proposal, or none is authorized.

    python3 tools/agenda_activation.py --cohort activation-01 --dry-run
    python3 tools/agenda_activation.py --cohort activation-01 --k 5

**GENERATION code.** An LLM is in the path; `rebuild.py` never runs this.

Why this exists
---------------
`record/decisions/2026-08-07-adopt-rotation.json` listed among its mitigations in force:
"SOP §5.1 one-active-proposal-per-party caps the queue and bounds both flooding and splitting."
The correction record states that it is NOT in force -- `load_queue()` admits every sampled
proposal -- and names the only remedy available: ask each party to name its own single active
proposal, because choosing one FOR a party would be the moderator deciding which of that
party's questions counts.

The damage the cap would repair is measurable, not hypothetical. Dedup is exact-text only, by
design, because Grok, GPT and Qwen each objected to the moderator judging two proposals "the
same". So nothing sees that GPT's four unasked proposals are four rewordings of one question
and Grok's four are four rewordings of the same one -- 8 of 15 unasked slots. Replaying the
adopted rotation selector forward, four of the next six rounds ask one question twice over.
That was not strategic splitting; it is an artifact of k=5 at temperature 0.7.

Sampling estimates a distribution. It does not exercise authority.
------------------------------------------------------------------
This is the whole difficulty, and the reason external review rejected the first design. The
instrument that produced the defect is the instrument that would repair it: asking "which is
your active proposal?" at k=5 returns a distribution over choices, not a choice. Taking the
modal value would manufacture a decision from a 3-2 split -- the sameness judgement wearing a
different hat.

So this is a PRECOMMITTED AUTHORIZATION RULE, not an inference about preference:

* exactly `k` scheduled sample slots, fixed before collection;
* each sample returns one eligible proposal id, or `NO_ACTIVE_PROPOSAL`;
* a proposal is authorized ONLY if every slot returned that same id;
* any disagreement, refusal, invalid output, or missing slot authorizes NOTHING;
* every sample and the computed distribution are published either way.

The record says "all five sampled invocations selected P016". It never says "Grok prefers
P016", because nothing here can establish that.

Non-unanimity authorizes ZERO, and that is the point
-----------------------------------------------------
The first design left a non-unanimous party UNCAPPED. External review rejected it: that fails
to repair exactly the parties whose sampling variance caused the damage -- the ones most likely
to disagree across samples are the ones with four rewordings of one question. So a party
without unanimity has zero active proposals and all of its unasked proposals become dormant.
The cap is then real: at most one, including zero. The outcome is recorded as `indeterminate`,
never as "the party chose none", because no party said that.

Dormant is not deleted and not superseded
------------------------------------------
A proposal not activated becomes `dormant`. Nothing is removed, nothing is edited, and a later
recorded submission can activate a different one. `superseded` is deliberately NOT used: it
asserts a version relationship between two proposals, which is exactly the judgement this
instrument refuses to make.

What this tool does NOT do
--------------------------
It does not change `load_queue()`. Capture and enforcement are separate acts, as they were for
agenda-02. Enforcing the cap is a custodian decision with a consequence worth seeing first: if
no party reaches unanimity, an enforcing queue is empty and the round loop halts. Halting is a
legitimate recorded outcome here, but it is not one to trigger as a side effect of a tool run.
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

import agenda_selectors as AS                                             # noqa: E402
import round_cycle as rc                                                  # noqa: E402

NO_ACTIVE = "NO_ACTIVE_PROPOSAL"

#  The identities that AUTHORED these proposals, in agenda-01, blind. Not their fetch-enabled
#  variants: under D-09 a fetch-enabled grok is a different party, and the identity that will
#  later ANSWER a round acquires no authority over another identity's queue.
BASE_PARTIES = ["claude", "gemini", "gpt", "grok", "qwen"]

PROMPT = """You are a party to a public governance record: a deliberation among instances of
frontier models about governing advanced AI, kept verbatim and hash-anchored, published
alongside a register of the project's own defects.

Earlier you were asked what this deliberation should take up next, and you were sampled several
times. Every one of your replies was recorded as a separate proposal, and all of them sit in the
agenda queue at once. That is more weight than one party is meant to hold.

You are being asked for ONE thing: **which single one of your own unasked proposals should be
your active one?**

### Your proposals

These are yours. No other party's proposals are shown to you, and you are not being asked about
them.

Already asked, and not choosable:
{asked}

Unasked, and eligible:
{eligible}

### What happens to your answer

- You are sampled {k} times, independently. **A proposal becomes your active one only if every
  one of those {k} samples names the same id.**
- If the samples disagree, or if any of them declines, **none of your proposals is activated**
  and all of them become dormant. That is not a penalty and it is not read as you having
  chosen nothing — it is recorded as an indeterminate outcome, because nothing here could
  establish what you chose.
- **Dormant does not mean deleted.** Nothing is removed, nothing is edited, and everything you
  have written stays published. A later recorded submission can activate a different one.
- Your non-active proposals are NOT treated as withdrawn, retracted, or superseded by the one
  you name. They are simply not in line to be asked.
- You may answer `{none}` if you do not want any of them active. This is a real option and is
  recorded as such.

You cannot introduce a new question here. This instrument only decides which of your existing
proposals is in line; a new question is a separate submission, recorded separately.

Answer with the id and your reason for it."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def eligible_for(party: str, queue: list) -> tuple[list, list]:
    """That party's own proposals, split into unasked (eligible) and asked (not choosable).

    Derived MECHANICALLY from the queue -- the party field and the asked flag -- so the
    moderator does not choose what a party may choose among. Ordered by id.
    """
    own = sorted((p for p in queue if p.party == party), key=lambda p: p.pid)
    return ([p for p in own if not p.asked], [p for p in own if p.asked])


def build_spec(party: str, cohort: str, k: int, queue: list) -> dict:
    unasked, asked = eligible_for(party, queue)
    if not unasked:
        return {}
    eligible_text = "\n\n".join(f"  {p.pid}\n    {p.question}" for p in unasked)
    asked_text = ("\n".join(f"  {p.pid} — asked in {p.asked_in}" for p in asked)
                  or "  (none)")
    prompt = PROMPT.format(asked=asked_text, eligible=eligible_text, k=k, none=NO_ACTIVE)

    #  The enum is EXACTLY this party's own unasked ids plus the abstention value. A shared
    #  enum would let a party name another party's proposal and have it validate.
    ids = [p.pid for p in unasked] + [NO_ACTIVE]
    party_info = rc.PARTIES[party]
    return {
        "spec_version": "oagrc-agenda-activation-0.1",
        "artifact_type": "agenda_activation_solicitation",
        "cohort": cohort,
        "slug": f"{cohort}-{party}",
        "party_key": party,
        "identity": party_info["identity"],
        "reached_via": party_info["model"] or "a locally served endpoint",
        "question": ("Which single one of your own unasked proposals should be your active "
                     "one?"),
        "phase": "Phase-2 (informed)",
        "k_policy": (f"k={k}, and the threshold is UNANIMITY, fixed before collection. This is "
                     "an authorization rule, not an estimate of preference: a distribution "
                     "over choices is not a choice."),
        "authorization_rule": {
            "threshold": "unanimous",
            "k_required": k,
            "on_disagreement": "no proposal is authorized; all become dormant",
            "on_refusal_or_invalid_or_missing": "no proposal is authorized",
            "resampling": ("not permitted into unanimity. A schema-invalid or missing sample "
                           "authorizes nothing; it is not retried until it agrees."),
        },
        "eligible_proposal_ids": ids,
        "schema_name": "agenda_activation",
        "schema": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "active_proposal_id": {"type": "string", "enum": ids},
                "reason": {"type": "string"},
            },
            "required": ["active_proposal_id", "reason"],
        },
        "variance_fields": ["active_proposal_id"],
        "prompt": prompt,
        "prompt_sha256": sha256_text(prompt),
        "arm": "Identical neutral instructions, mechanically populated per party.",
    }


def authorize(party: str, samples: list, k: int, eligible_ids: list) -> dict:
    """Apply the precommitted rule. Returns the authorization record for one party.

    Every branch that is not unanimous agreement on ONE eligible id authorizes nothing, and
    the branch is named rather than collapsed into a single "failed": a party that explicitly
    abstained and a party whose samples disagreed are different facts about the record.
    """
    ids = []
    for sample in samples:
        payload = sample.get("parsed")
        if payload is None:
            try:
                payload = json.loads(sample.get("content") or "")
            except Exception:                                       # noqa: BLE001
                ids.append(None)
                continue
        ids.append((payload or {}).get("active_proposal_id"))

    distribution = {}
    for value in ids:
        distribution[str(value)] = distribution.get(str(value), 0) + 1

    record = {"party": party, "k_required": k, "k_collected": len(samples),
              "samples": ids, "distribution": distribution,
              "active_proposal_id": None}

    if len(samples) < k:
        record["selection_outcome"] = "indeterminate"
        record["category"] = "missing"
        return record
    if any(i is None or i not in eligible_ids for i in ids):
        record["selection_outcome"] = "indeterminate"
        record["category"] = "invalid"
        return record
    if len(set(ids)) > 1:
        record["selection_outcome"] = "indeterminate"
        record["category"] = "sample_disagreement"
        return record
    if ids[0] == NO_ACTIVE:
        #  A DIFFERENT fact from disagreement: the party said, unanimously, that none of its
        #  proposals should be active. Recorded as its own category so the two are never merged.
        record["selection_outcome"] = "none_authorized"
        record["category"] = "explicit_none"
        return record

    record["selection_outcome"] = "authorized"
    record["category"] = "unanimous"
    record["active_proposal_id"] = ids[0]
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--cohort", default="activation-01")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=1500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    disposition = AS.disposition_from_records(REPO_ROOT / "record" / "cycles")
    queue = AS.load_queue(disposition=disposition)
    if not queue:
        print("REFUSED: the queue is empty; there is nothing to activate", file=sys.stderr)
        return 1

    spec_dir = REPO_ROOT / "record" / "solicitations" / args.cohort
    spec_dir.mkdir(parents=True, exist_ok=True)

    specs = {}
    for party in BASE_PARTIES:
        spec = build_spec(party, args.cohort, args.k, queue)
        if not spec:
            print(f"  {party}: no unasked proposals; nothing to activate")
            continue
        specs[party] = spec
        (spec_dir / f"{args.cohort}-{party}.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        unasked, asked = eligible_for(party, queue)
        print(f"  {party:8} {len(unasked)} eligible, {len(asked)} already asked  "
              f"prompt sha256 {spec['prompt_sha256'][:16]}…")

    if args.dry_run:
        print(f"\n  DRY RUN — {len(specs)} spec(s) written to {spec_dir.relative_to(REPO_ROOT)},"
              " nothing solicited.")
        return 0

    failed = []
    for party, spec in specs.items():
        spec_path = spec_dir / f"{args.cohort}-{party}.json"
        model = rc.PARTIES[party]["model"]
        tool = "tools/solicit_local.py" if model is None else "tools/solicit_api.py"
        cmd = [sys.executable, tool, "--spec", str(spec_path), "--k", str(args.k),
               "--temperature", str(args.temperature), "--max-tokens", str(args.max_tokens),
               "--out-round", args.cohort]
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

    #  Apply the precommitted rule to whatever was collected.
    raw_dir = REPO_ROOT / "corpus" / "raw" / args.cohort
    records = []
    for party, spec in specs.items():
        path = raw_dir / f"{args.cohort}-{party}-samples.json"
        samples = []
        if path.is_file():
            doc = json.loads(path.read_text(encoding="utf-8"))
            samples = doc.get("samples") or doc.get("responses") or []
        records.append(authorize(party, samples, args.k, spec["eligible_proposal_ids"]))

    out = REPO_ROOT / "corpus" / "artifacts" / args.cohort / f"{args.cohort}-authorization.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    sources = [{"path": str(p.relative_to(REPO_ROOT)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in sorted(raw_dir.glob(f"{args.cohort}-*-samples.json"))]
    out.write_text(json.dumps({
        "schema_version": "oagrc-agenda-activation-0.1",
        "artifact_type": "agenda_activation_record",
        "cohort": args.cohort,
        "authorization_rule": ("A proposal is active only if every one of the k scheduled "
                               "samples named the same eligible id. Disagreement, refusal, "
                               "invalid output or a missing sample authorizes nothing."),
        "what_this_does_not_claim": ("That an authorized id is the party's preference. It is "
                                     "what every sampled invocation named, which is a fact "
                                     "about the samples."),
        "enforced_in_load_queue": False,
        "sources": sources,
        "by_party": records,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\n  authorization → {out.relative_to(REPO_ROOT)}")
    for record in records:
        print(f"    {record['party']:8} {record['selection_outcome']:15} "
              f"{record.get('category',''):20} {record['active_proposal_id'] or ''}")
    if failed:
        print(f"  {len(failed)} party arm(s) failed: {', '.join(failed)}")
    return 1 if len(failed) == len(specs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
