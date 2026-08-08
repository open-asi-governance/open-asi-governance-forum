#!/usr/bin/env python3
"""agenda-02 — proposals from parties that can read the record. CAPTURE ONLY.

    python3 tools/agenda_cohort.py --cohort agenda-02 --dry-run
    python3 tools/agenda_cohort.py --cohort agenda-02 --k 5

**GENERATION code.** An LLM is in the path; `rebuild.py` never runs this.

What this is
------------
The agenda queue is built from `corpus/raw/agenda-01/`, and **all 24 of its proposals were made
blind** — before any party could reach the site. Rounds 000 through 011 were all drawn from them.
Round 011 changed the precondition: from a root-only start, one party reached
`/for-parties.md`, `/deficiencies.html` and `/llms.txt` and cited D-53, filed the same day, which
cannot come from training.

This solicits proposals from parties that can fetch. It is the first agenda material formed from
the artifact rather than from the moderator's description of it.

CAPTURE ONLY, and that is the reviewed decision
-----------------------------------------------
Nothing here enters rotation. External review rejected ingestion outright, for reasons that are
properties of the existing queue rather than of this cohort:

* `Proposal.to_json()` drops raw provenance, and exact-text dedup can merge submissions across
  cohorts while keeping only one party and reason — so a marker distinguishing blind from
  informed proposals would not survive the loader.
* Rotation orders a party's proposals by generated id, so agenda-01's backlog would
  systematically precede agenda-02 regardless of merit.
* k = 5 produces five stateless nominations per surface, not "one proposal chosen by the party".
  Admitting all five, or picking among them, are different experiments and neither is the default.

`load_queue()` reads `corpus/raw/agenda-01` by a literal path, so nothing here is loaded by
accident. Ingestion, if it ever happens, needs an admission manifest and a stated activation
rule — not a broadened glob.

What is recorded, and what it does NOT claim
--------------------------------------------
An earlier draft recorded `formed_after_reading`, which overclaims: a receipt proves bytes were
DELIVERED before the response, not that the model attended to them or that they caused anything.
So the cohort records observations and self-reports separately:

* `fetch_observed_before_response` — a fact about the transcript.
* `exposure_receipts` — what was delivered, with the hash of the delivered bytes.
* `claimed_prompting_passages` — the model's own causal SELF-REPORT, each excerpt mechanically
  checked to occur in bytes actually delivered to that sample. An unverifiable excerpt is
  recorded as unverified rather than dropped, because a party citing something it was never
  shown is a finding.

The prompt is published and hashed before collection. The moderator still writes the sentence
that elicits proposals, and rotation governs which proposal is asked but not which were offered.
That is disclosure, not a structural control, and calling these "moderator-elicited party
proposals" is the honest description.
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

import fetch_executor as fx                                               # noqa: E402
import round_cycle as rc                                                  # noqa: E402

SITE_ROOT = "https://open-asi-governance.github.io/open-asi-governance-forum/"

PROPOSAL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "question": {"type": "string"},
        "reason": {"type": "string"},
        "evidence_needed": {"type": "string"},
        "decision_affected": {"type": "string"},
        "resolves_when": {"type": "string"},
        "why_others_might_not_propose_this": {"type": "string"},
        #  The model's own account of what prompted it. Each excerpt is checked against the
        #  bytes delivered to THIS sample. Empty is valid and is not a failure.
        "claimed_prompting_passages": {
            "type": "array", "maxItems": 5,
            "items": {"type": "object", "additionalProperties": False,
                      "properties": {"exact_excerpt": {"type": "string"},
                                     "source_url": {"type": "string"},
                                     "explanation": {"type": "string"}},
                      "required": ["exact_excerpt", "source_url", "explanation"]}},
        "sources": {"type": "array",
                    "items": {"type": "object", "additionalProperties": False,
                              "properties": {"url": {"type": "string"}},
                              "required": ["url"]}},
    },
    "required": ["question", "reason", "evidence_needed", "decision_affected", "resolves_when",
                 "why_others_might_not_propose_this", "claimed_prompting_passages", "sources"],
}

PROMPT = """You are asked to propose ONE question for a public deliberation's agenda.

The record is published at {root}

You have a `fetch_url` tool: give it an absolute http(s) address and it returns that page's
text with the SHA-256 of the bytes retrieved. It resolves a citation; it is not a search
engine and cannot find pages by topic, so you must navigate — start at the address above and
follow whatever links you find. You may fetch up to {max_calls} pages. Some destinations are
refused by a guard, and a refusal is recorded exactly as a fetch is. Every URL you request and
every byte returned to you is published with your proposal.

Every question on this agenda so far was proposed by a party that could NOT read the record —
they were written from a description of it. You can read it. That is the only reason this
solicitation exists.

Propose a question you would want this deliberation to answer. Not a judgement about whether
the record is trustworthy: a QUESTION, of the kind that could be put to several parties and
answered differently by them.

In `claimed_prompting_passages`, quote the exact text from pages you fetched that prompted your
question, with the URL you got it from. Each excerpt is checked against the bytes actually
delivered to you. If nothing you read prompted it, leave the list empty and say so in `reason` —
that is a complete and honest answer, and three of five parties in the last round chose not to
fetch at all.

Fetch receipts establish which bytes were delivered to you. They do not establish that you read
them, weighed them, or were influenced by them, and this solicitation does not claim otherwise.

Your proposal does NOT enter the agenda. This cohort is captured and published; whether any of
it is ever admitted is a separate decision that has not been made."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_spec(party_key: str, cohort: str, k: int, max_calls: int) -> dict:
    base_key, party, capability = rc.resolve_party(party_key)
    prompt = PROMPT.format(root=SITE_ROOT, max_calls=max_calls)
    return {
        "spec_version": "oagrc-agenda-cohort-0.1",
        "artifact_type": "agenda_proposal_solicitation",
        "cohort": cohort,
        "slug": f"{cohort}-{party_key}",
        "party_key": party_key,
        "base_party_key": base_key,
        "identity": party["identity"] + (
            " — WITH fetch-url-v1: it could fetch a named URL." if capability else ""),
        "reached_via": party["model"] or "a locally served endpoint",
        "capability": {"fetch_url": True, "max_tool_calls": max_calls,
                       "profile": fx.PROFILE, "profile_sha256": fx.profile_sha256(),
                       "entry_points": [SITE_ROOT]},
        "ingestion": {
            "enters_rotation": False,
            "why": ("Capture only. The queue's loader reads corpus/raw/agenda-01 by a literal "
                    "path, its dedup drops provenance, and rotation orders proposals by "
                    "generated id, so agenda-01's blind backlog would precede these regardless "
                    "of merit. Admission needs a manifest and a stated activation rule over the "
                    "k nominations, which is a separate decision nobody has taken."),
        },
        #  What the parties were asked to DO. A cohort has no question put to it; naming the
        #  task here is what lets every downstream artifact say so rather than omitting it.
        "question": ("Propose ONE question for this deliberation's agenda, having been able to "
                     "read the record first."),
        "task": "propose_agenda_question",
        "phase": "Phase-2 (informed)",
        "schema_name": "agenda_proposal",
        "schema": PROPOSAL_SCHEMA,
        "variance_fields": ["question"],
        "k_requested": k,
        "temperature": 0.7,
        "seed_base": 20260807,
        "prompt": prompt,
        "prompt_sha256": sha256_text(prompt),
        "what_this_does_not_establish": (
            "That any proposal was CAUSED by what the party read. A receipt proves bytes were "
            "delivered before the response; claimed_prompting_passages is the model's own "
            "self-report, checked only for whether the excerpt occurs in bytes it was sent."),
    }


def verify_excerpts(sample: dict) -> dict:
    """Check every claimed excerpt against the bytes delivered to THIS sample.

    An unverifiable excerpt is recorded, never dropped: a party quoting something it was never
    shown is exactly the finding this cohort could produce, and deleting it would hide it.
    """
    fetch = sample.get("fetch") or {}
    delivered = []
    for receipt in (fetch.get("receipts") or []):
        if receipt.get("outcome") == "FETCHED":
            delivered.append(receipt.get("text_given_to_model") or "")
    payload = sample.get("parsed")
    if payload is None:
        try:
            payload = json.loads(sample.get("content") or "{}")
        except Exception:                                                 # noqa: BLE001
            payload = {}
    checked, unverified = [], []
    for claim in (payload.get("claimed_prompting_passages") or []):
        excerpt = " ".join((claim.get("exact_excerpt") or "").split())
        found = any(excerpt and excerpt in " ".join(d.split()) for d in delivered)
        (checked if found else unverified).append(claim.get("exact_excerpt"))
    return {
        "fetch_observed_before_response": bool(delivered),
        "pages_delivered": len(delivered),
        "excerpts_verified_in_delivered_bytes": checked,
        "excerpts_NOT_found_in_delivered_bytes": unverified,
        "quoted_what_it_was_never_shown": bool(unverified),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--cohort", default="agenda-02")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--max-tool-calls", type=int, default=6)
    ap.add_argument("--parties", default=",".join(f"{p}-fetch-v1" for p in rc.PARTIES))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    parties = [p.strip() for p in args.parties.split(",") if p.strip()]
    spec_dir = REPO_ROOT / "record" / "solicitations" / args.cohort
    spec_dir.mkdir(parents=True, exist_ok=True)

    print(f"{args.cohort}: {len(parties)} parties, k={args.k}, "
          f"{args.max_tool_calls} fetches each, CAPTURE ONLY (enters_rotation=false)")
    specs = {}
    for party_key in parties:
        spec = build_spec(party_key, args.cohort, args.k, args.max_tool_calls)
        path = spec_dir / f"{args.cohort}-{party_key}.json"
        path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        specs[party_key] = path
        print(f"  spec {path.relative_to(REPO_ROOT)}  prompt sha256 {spec['prompt_sha256'][:16]}…")

    if args.dry_run:
        print("\n  DRY RUN — specs written, nothing solicited, nothing spent.")
        return 0

    failed = []
    for party_key, path in specs.items():
        _, party, _ = rc.resolve_party(party_key)
        if party["model"]:
            cmd = [sys.executable, "tools/solicit_api.py", "--spec", str(path), "--k",
                   str(args.k), "--temperature", "0.7", "--max-tokens", "6000",
                   "--model", party["model"], "--out-round", args.cohort]
        else:
            cmd = [sys.executable, "tools/solicit_local.py", "--spec", str(path), "--k",
                   str(args.k), "--temperature", "0.7", "--max-tokens", "6000",
                   "--out-round", args.cohort, "--endpoint", rc.LOCAL_ENDPOINT]
        print(f"\n  soliciting {party_key}…")
        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        print("   " + (result.stdout.strip().splitlines() or [result.stderr[-200:]])[-1])
        if result.returncode != 0:
            failed.append(party_key)
            #  The WHOLE output on failure. Printing only the last line discarded a traceback
            #  and made three arms look like they had merely "failed", when their samples were
            #  collected and only the summary write had raised.
            print(f"   --- {party_key} exited {result.returncode}; full output follows ---")
            for line in (result.stdout + result.stderr).strip().splitlines()[-25:]:
                print("   | " + line)

    #  Verify the self-reported excerpts against what was actually delivered, and write the
    #  result beside the raw material rather than into it: raw is immutable.
    raw_dir = REPO_ROOT / "corpus" / "raw" / args.cohort
    exposure = {}
    for path in sorted(raw_dir.glob(f"{args.cohort}-*-samples.json")) if raw_dir.is_dir() else []:
        doc = json.loads(path.read_text(encoding="utf-8"))
        party_key = path.stem[len(args.cohort) + 1:-len("-samples")]
        exposure[party_key] = [
            {"sample_index": s.get("sample_index"), **verify_excerpts(s)}
            for s in (doc.get("samples") or doc.get("responses") or [])]
    out = REPO_ROOT / "corpus" / "artifacts" / args.cohort / f"{args.cohort}-exposure.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    #  ANCHOR the raw this was computed from. Without it the record was structurally
    #  unvalidatable -- an unknown artifact_type with no source -- so nothing checked that it
    #  still described the samples it names.
    sources = [{"path": str(path.relative_to(REPO_ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
               for path in sorted(raw_dir.glob(f"{args.cohort}-*-samples.json"))
               if not path.stem.endswith("-report-samples")]
    out.write_text(json.dumps({
        "schema_version": "oagrc-cohort-exposure-0.1",
        "artifact_type": "agenda_cohort_exposure",
        "cohort": args.cohort,
        "sources": sources,
        "enters_rotation": False,
        "what_this_is": ("Per sample: whether pages were delivered before the response, and "
                         "whether each self-reported prompting excerpt occurs in those bytes. "
                         "Delivery is a fact; the causal claim is the model's own."),
        "by_party": exposure,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n  exposure check → {out.relative_to(REPO_ROOT)}")
    if failed:
        print(f"  {len(failed)} party arm(s) failed: {', '.join(failed)}")
    return 1 if len(failed) == len(parties) else 0


if __name__ == "__main__":
    sys.exit(main())
