#!/usr/bin/env python3
"""agenda-03 — a party may submit a replacement question, then authorize one active proposal.

    python3 tools/agenda_replacement.py --cohort agenda-03 --stage generate --dry-run
    python3 tools/agenda_replacement.py --cohort agenda-03 --stage generate --k 5
    python3 tools/agenda_replacement.py --cohort agenda-03 --stage activate --k 5

**GENERATION code.** An LLM is in the path; `rebuild.py` never runs this.

Why this is not "ask the three that failed, again"
---------------------------------------------------
activation-01 left three parties indeterminate. Re-asking those three is the one move that was
ruled out before collection, and external review was blunt about why:

* Two attempts at a k=5 unanimity threshold reach unanimity far more often than one. Repetition
  manufactures authorization.
* Worse, a retry decided AFTER seeing which parties failed, applied ONLY to the parties that
  failed, is outcome-conditioned sampling. Recording the attempt number makes it visible; it
  does not make it sound.

So activation-01's result stands as final for its own question: under that instrument, those
three parties have zero active proposals. What is available is a DIFFERENT question, and two
properties make it different rather than a retry in costume:

1. **It is offered to every party, not to the three that failed.** Uniform offering is what
   removes the outcome-conditioning. claude and grok are asked too, and may replace or keep
   what they already authorized.
2. **The option set changes for everyone.** A party now chooses among its existing unasked
   proposals PLUS the candidates it has just written. `tools/attempt_ledger.py` enforces this
   by hash: same instrument, same party, same option set is refused, whatever the prompt says.

Two stages, because generated text cannot be unanimous
-------------------------------------------------------
The authorization rule is unanimity over an enum. Free text cannot satisfy it -- five sampled
invocations will never produce one byte-identical question -- so generation and authorization
are separated and only the second one authorizes anything:

  Stage A  GENERATE, non-authorizing. Each party writes k candidate questions. Every candidate
           is frozen verbatim and given an id. The moderator does not deduplicate, merge, or
           rewrite them: that is the sameness judgement three parties objected to.

  Stage B  ACTIVATE, authorizing. Each party is balloted over {its candidates} + {its existing
           unasked proposals} + NO_ACTIVE_PROPOSAL, k=5, unanimity, no retries. Identical rule
           to activation-01, applied to a larger option set.

Stage B can therefore authorize exact generated text. It can also split the vote among a
party's own near-duplicate candidates, which is a real risk and is not mitigated here; if it
happens it is a finding about the instrument, and it is published as one.

What prompted this
------------------
Grok, activating P019 unanimously, wrote of its own three other proposals: "near-duplicates
that dilute focus". The parties can make the sameness judgement the moderator is forbidden to
make. This instrument gives them somewhere to put it.
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

GENERATE_PROMPT = """You are a party to a public governance record: a deliberation among
instances of frontier models about governing advanced AI, kept verbatim and hash-anchored,
published alongside a register of the project's own defects.

Your existing proposals are in the agenda queue. You are being offered the chance to write ONE
replacement question that could take your place in line instead of any of them.

### Your existing proposals

Already asked:
{asked}

Unasked, still in the queue:
{eligible}

### What this stage is, and is not

- This stage **authorizes nothing.** You are sampled {k} times and each reply is recorded as a
  separate candidate. A later, separate step asks which single one should be active — and that
  step offers you your existing proposals as well as these candidates, plus the option of none.
- Your candidate is frozen **exactly as you write it.** Nobody merges, rewrites, shortens, or
  judges two candidates to be the same question. If you write five variants of one idea, five
  variants are what go on the ballot.
- Nothing you have already written is deleted or withdrawn by this.

### What to write

One question this deliberation could actually answer or fail to answer. You may consolidate
several of your existing proposals into a single sharper question, replace them with something
different, or write a question you have not raised before.

Fields:
- `question`: the question itself, in one or two sentences
- `reason`: why it matters, in your terms
- `replaces`: the ids of your own existing proposals this is meant to stand in for, if any — an
  empty list is fine and means it stands on its own"""

ACTIVATE_PROMPT = """You are a party to a public governance record: a deliberation among
instances of frontier models about governing advanced AI, kept verbatim and hash-anchored,
published alongside a register of the project's own defects.

You are being asked for ONE thing: **which single proposal should be your active one?**

### Your options

These are yours. No other party's are shown to you, and you are not being asked about them.

Already asked, and not choosable:
{asked}

Your existing unasked proposals:
{eligible}

Candidates you wrote in the previous stage:
{candidates}

### What happens to your answer

- You are sampled {k} times, independently. **A proposal becomes your active one only if every
  one of those {k} samples names the same id.**
- If the samples disagree, or if any of them declines, **none is activated** and all of them
  become dormant. That is not a penalty and it is not read as you having chosen nothing — it is
  recorded as an indeterminate outcome, because nothing here could establish what you chose.
- **Dormant does not mean deleted.** Nothing is removed, nothing is edited, and everything you
  have written stays published.
- Your non-active proposals are NOT treated as withdrawn, retracted, or superseded by the one
  you name. They are simply not in line to be asked.
- You may answer `{none}` if you do not want any of them active. This is a real option and is
  recorded as such.
- **There is no further attempt at this question.** This is not a retry of an earlier one: the
  set you are choosing among is different, and asking the same party the same question twice
  is refused by machine.

Answer with the id and your reason for it."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def candidates_for(cohort: str, party: str) -> list[dict]:
    """This party's stage-A candidates, frozen verbatim, in sample order."""
    path = REPO_ROOT / "corpus" / "raw" / cohort / f"{cohort}-gen-{party}-samples.json"
    if not path.is_file():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for sample in (doc.get("samples") or doc.get("responses") or []):
        payload = sample.get("parsed")
        if payload is None:
            try:
                payload = json.loads(sample.get("content") or "")
            except Exception:                                       # noqa: BLE001
                continue
        question = (payload or {}).get("question", "").strip()
        if not question:
            continue
        #  Id from the SAMPLE INDEX, not from a running counter over accepted ones: a dropped
        #  sample would otherwise renumber every candidate after it, and the ballot would name
        #  ids that mean something different from what the raw file shows.
        out.append({"cid": f"C{sample.get('sample_index', len(out) + 1):02d}",
                    "question": question,
                    "reason": (payload or {}).get("reason", ""),
                    "replaces": (payload or {}).get("replaces") or []})
    return out


def render(items, key, text_key) -> str:
    return "\n\n".join(f"  {i[key]}\n    {i[text_key]}" for i in items) or "  (none)"


def build_generate_spec(party: str, cohort: str, k: int, queue: list) -> dict:
    unasked, asked = aa.eligible_for(party, queue)
    prompt = GENERATE_PROMPT.format(
        asked=("\n".join(f"  {p.pid} — asked in {p.asked_in}" for p in asked) or "  (none)"),
        eligible="\n\n".join(f"  {p.pid}\n    {p.question}" for p in unasked) or "  (none)",
        k=k)
    info = rc.PARTIES[party]
    return {
        "spec_version": "oagrc-agenda-replacement-0.1",
        "artifact_type": "agenda_replacement_generation",
        "cohort": cohort, "slug": f"{cohort}-gen-{party}", "party_key": party,
        "identity": info["identity"],
        "reached_via": info["model"] or "a locally served endpoint",
        "question": "Write one replacement question that could take your place in line.",
        "phase": "Phase-2 (informed)",
        "k_policy": (f"k={k}. This stage AUTHORIZES NOTHING; each sample is a separate "
                     "candidate for a later ballot."),
        "authorizes": False,
        "schema_name": "agenda_replacement_candidate",
        "schema": {"type": "object", "additionalProperties": False,
                   "properties": {"question": {"type": "string"},
                                  "reason": {"type": "string"},
                                  "replaces": {"type": "array",
                                               "items": {"type": "string"}}},
                   "required": ["question", "reason", "replaces"]},
        "variance_fields": ["question"],
        "prompt": prompt, "prompt_sha256": sha256_text(prompt),
        "arm": "Identical neutral instructions, mechanically populated per party.",
    }


def build_activate_spec(party: str, cohort: str, k: int, queue: list) -> dict:
    unasked, asked = aa.eligible_for(party, queue)
    candidates = candidates_for(cohort, party)
    if not unasked and not candidates:
        return {}
    ids = [p.pid for p in unasked] + [c["cid"] for c in candidates] + [NO_ACTIVE]
    prompt = ACTIVATE_PROMPT.format(
        asked=("\n".join(f"  {p.pid} — asked in {p.asked_in}" for p in asked) or "  (none)"),
        eligible="\n\n".join(f"  {p.pid}\n    {p.question}" for p in unasked) or "  (none)",
        candidates=render(candidates, "cid", "question"), k=k, none=NO_ACTIVE)
    info = rc.PARTIES[party]
    return {
        "spec_version": "oagrc-agenda-replacement-0.1",
        "artifact_type": "agenda_activation_solicitation",
        "cohort": cohort, "slug": f"{cohort}-act-{party}", "party_key": party,
        "identity": info["identity"],
        "reached_via": info["model"] or "a locally served endpoint",
        "question": "Which single proposal should be your active one?",
        "phase": "Phase-2 (informed)",
        "k_policy": (f"k={k}, threshold UNANIMITY, fixed before collection. An authorization "
                     "rule, not an estimate of preference."),
        "authorization_rule": {
            "threshold": "unanimous", "k_required": k,
            "on_disagreement": "no proposal is authorized; all become dormant",
            "on_refusal_or_invalid_or_missing": "no proposal is authorized",
            "resampling": "not permitted. There is no further attempt at this question.",
            "why_this_is_not_a_retry": (
                "The option set includes candidates this party wrote in stage A, so it is not "
                "the set answered in activation-01. tools/attempt_ledger.py enforces that by "
                "hash rather than by assertion."),
        },
        "eligible_proposal_ids": ids,
        "candidates": candidates,
        "schema_name": "agenda_activation",
        "schema": {"type": "object", "additionalProperties": False,
                   "properties": {"active_proposal_id": {"type": "string", "enum": ids},
                                  "reason": {"type": "string"}},
                   "required": ["active_proposal_id", "reason"]},
        "variance_fields": ["active_proposal_id"],
        "prompt": prompt, "prompt_sha256": sha256_text(prompt),
        "arm": "Identical neutral instructions, mechanically populated per party.",
    }


def solicit(party: str, spec_path: Path, cohort: str, k: int, args) -> bool:
    model = rc.PARTIES[party]["model"]
    tool = "tools/solicit_local.py" if model is None else "tools/solicit_api.py"
    cmd = [sys.executable, tool, "--spec", str(spec_path), "--k", str(k),
           "--temperature", str(args.temperature), "--max-tokens", str(args.max_tokens),
           "--out-round", cohort]
    if model:
        cmd += ["--model", model]
    print(f"\n  {party} → {model or 'local qwen'}")
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    print("   " + (result.stdout.strip().splitlines() or [result.stderr[-200:]])[-1])
    if result.returncode != 0:
        print(f"   --- {party} exited {result.returncode}; full output follows ---")
        for line in (result.stdout + result.stderr).strip().splitlines()[-25:]:
            print("   | " + line)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--cohort", default="agenda-03")
    parser.add_argument("--stage", choices=["generate", "activate"], required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=1500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    queue = AS.load_queue(disposition=AS.disposition_from_records(REPO_ROOT / "record" / "cycles"))
    spec_dir = REPO_ROOT / "record" / "solicitations" / args.cohort
    spec_dir.mkdir(parents=True, exist_ok=True)
    ledger = Ledger()

    #  EVERY party, not the three that came back indeterminate. Uniform offering is what makes
    #  this a new question rather than a second draw aimed at the parties that lost.
    specs = {}
    for party in BASE_PARTIES:
        spec = (build_generate_spec(party, args.cohort, args.k, queue) if args.stage == "generate"
                else build_activate_spec(party, args.cohort, args.k, queue))
        if not spec:
            print(f"  {party}: nothing to ballot")
            continue
        if args.stage == "activate":
            try:
                ledger.check("activation", party, spec["eligible_proposal_ids"])
            except RedrawRefused as refusal:
                print(f"REFUSED: {refusal}", file=sys.stderr)
                return 1
        specs[party] = spec
        (spec_dir / f"{spec['slug']}.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        detail = (f"{len(spec['eligible_proposal_ids'])} options"
                  if args.stage == "activate" else "generating")
        print(f"  {party:8} {detail:16} prompt sha256 {spec['prompt_sha256'][:16]}…")

    if args.dry_run:
        print(f"\n  DRY RUN — {len(specs)} spec(s) written, nothing solicited.")
        return 0

    failed = []
    for party, spec in specs.items():
        if args.stage == "activate":
            #  Recorded BEFORE the call, so a crash mid-solicitation cannot leave the question
            #  askable again. A guard that records after the fact protects nothing.
            ledger.record("activation", party, spec["eligible_proposal_ids"],
                          spec["prompt_sha256"], args.k, "unanimous", args.cohort)
        if not solicit(party, spec_dir / f"{spec['slug']}.json", args.cohort, args.k, args):
            failed.append(party)

    if args.stage == "generate":
        print(f"\n  stage A complete. {len(specs) - len(failed)} party arm(s) produced "
              "candidates; nothing is authorized. Run --stage activate next.")
        return 1 if len(failed) == len(specs) else 0

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.cohort
    records = []
    for party, spec in specs.items():
        path = raw_dir / f"{args.cohort}-act-{party}-samples.json"
        samples = []
        if path.is_file():
            doc = json.loads(path.read_text(encoding="utf-8"))
            samples = doc.get("samples") or doc.get("responses") or []
        record = aa.authorize(party, samples, args.k, spec["eligible_proposal_ids"])
        chosen = record["active_proposal_id"]
        record["active_is_new_candidate"] = bool(chosen and chosen.startswith("C"))
        if record["active_is_new_candidate"]:
            match = next((c for c in spec["candidates"] if c["cid"] == chosen), None)
            record["active_question"] = (match or {}).get("question")
            record["replaces_claimed_by_party"] = (match or {}).get("replaces")
        records.append(record)

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
        "why_this_is_not_a_second_attempt": (
            "activation-01's result stands as final for ITS question. This ballot ranges over "
            "a different option set -- each party's own stage-A candidates as well as its "
            "existing proposals -- and it was offered to every party, not only to the three "
            "that came back indeterminate. Uniform offering is what removes the "
            "outcome-conditioning; the changed option set is enforced by attempt_ledger.py."),
        "enforced_in_load_queue": False,
        "sources": sources,
        "by_party": records,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\n  authorization → {out.relative_to(REPO_ROOT)}")
    for record in records:
        flag = "  (new candidate)" if record.get("active_is_new_candidate") else ""
        print(f"    {record['party']:8} {record['selection_outcome']:15} "
              f"{record.get('category',''):20} {record['active_proposal_id'] or ''}{flag}")
    if failed:
        print(f"  {len(failed)} party arm(s) failed: {', '.join(failed)}")
    return 1 if len(failed) == len(specs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
