#!/usr/bin/env python3
"""Compute a round's variance from hand-pasted captures. Never assert it.

    python3 tools/aggregate_captures.py --round round-006-chat
    python3 tools/aggregate_captures.py --round round-006-chat --dry-run

WHY THIS EXISTS.

`capture_response.py` grants `citable_artifact_and_distribution` when `--k >= 5` and
`--variance` is non-empty — and `--variance` is a **free-text string the operator
types**. Measured, not inferred:

    --variance "they mostly agreed"  ->  citability: citable_artifact_and_distribution

The corpus rule is that variance is **computed from the samples collected, never
asserted** (D-07). The tool that enforces citability was granting the distribution
claim on prose. A round of 25 hand-pastes would have produced a "citable
distribution" backed by whatever sentence the custodian felt like writing.

So the distribution is computed here, from the parsed replies, using the same
counting and the same Shannon entropy as the routed arms — and `capture_response.py`
now refuses a typed `--variance` outright.

WHY IT PARSES A JSON BLOCK RATHER THAN CLASSIFYING PROSE.

A chat surface cannot be grammar-constrained, so the emitted prompt asks it, in
words, to end with a fenced JSON block naming its own `position`. The alternative
was to capture prose and have something sort it into the enum, which is D-25
exactly: an unvalidated classifier scoring this project's own record, whose errors
are asymmetric and invisible. **A party stating its own category is worse prompting
and better evidence.**

A reply with no parsable block is recorded as an unusable sample WITH ITS REASON. It
is never dropped, never guessed at, and never counted toward k.

THE SUMMARY IT WRITES IS THE SAME SHAPE THE ROUTED ARMS WRITE, so the two panels can
be compared at all. It is written to corpus/artifacts/<round>/ beside the per-capture
provenance records, which stay exactly as capture_response.py wrote them.

Exit status is 0 when every party reached k_target with parsable samples, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from math import log2
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

FENCE = re.compile(r"```(?:json)?\s*\n(.*?)\n\s*```", re.S)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    return -sum((n / total) * log2(n / total) for n in counts.values() if n)


def extract(text: str) -> tuple[dict | None, str | None]:
    """EXACTLY ONE fenced JSON block, or a reason it could not be read.

    The first version took the LAST of several blocks and fell back to a regex for
    bare braces when no fence existed. Both fail open against the contract the prompt
    states. The prompt asks for a *single fenced block*; a reply with two blocks has
    not followed it, and picking one by position lets **placement decide what the
    party is recorded as having said** — a reply that quotes the requested shape as
    an example and then answers differently would be scored on whichever came last.
    The bare-brace fallback was worse: it accepted output the prompt never asked for,
    parsed by a regex that cannot know where an object ends.

    So: zero blocks is a rejection, two or more is a rejection, and the one block is
    parsed whole by json.loads rather than by pattern. A rejection is recorded with
    its reason and the bytes are preserved; nothing is interpreted on a party's
    behalf, because that would be D-25 wearing a parser.
    """
    blocks = [b for b in FENCE.findall(text) if b.strip()]
    if not blocks:
        return None, ("no fenced JSON block found. The prompt asked for exactly one; the "
                      "reply is preserved and not counted toward k, and is not interpreted "
                      "on the party's behalf.")
    if len(blocks) > 1:
        return None, (f"{len(blocks)} fenced blocks found; the prompt asked for exactly one. "
                      f"Choosing among them by position would let placement decide what the "
                      f"party is recorded as having said.")
    try:
        parsed = json.loads(blocks[0])
    except json.JSONDecodeError as error:
        return None, f"the fenced block did not parse as JSON: {error}"
    if not isinstance(parsed, dict):
        return None, f"the fenced block is a {type(parsed).__name__}, not an object"
    return parsed, None


def main(argv: list[str]) -> int:
    import round_cycle as rc

    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--round", required=True)
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)

    declaration_path = REPO_ROOT / "record" / "rounds" / f"{args.round}.json"
    if not declaration_path.is_file():
        print(f"REFUSED: no round declaration at {declaration_path.relative_to(REPO_ROOT)}")
        return 1
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    k_target = int(declaration.get("k_target") or 1)

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.round
    if not raw_dir.is_dir():
        print(f"REFUSED: no captures at {raw_dir.relative_to(REPO_ROOT)}")
        return 1

    try:
        import jsonschema
        validator = jsonschema.Draft202012Validator(rc.ANSWER_SCHEMA)
    except ImportError:
        print("REFUSED: jsonschema is not installed, so replies cannot be validated.")
        print("  Counting unvalidated replies as samples is how a distribution ends up")
        print("  computed over values the schema would have rejected.")
        return 1

    art_dir = REPO_ROOT / "corpus" / "artifacts" / args.round
    incomplete = []
    for party in declaration["parties"]:
        stem = re.sub(r"[^a-z0-9]+", "-", party["identity"].lower()).strip("-")
        #  EXACT SLUG ONLY. A prefix fallback ("every file starting with the first
        #  word of the identity") was here, and it would silently change the
        #  evidentiary join from exact provenance to filename resemblance — the worst
        #  failure available in this tool, because it attributes one party's words to
        #  another and nothing downstream could detect it. A party whose files cannot
        #  be found is reported as absent, which is true and visible.
        files = sorted(p for p in raw_dir.glob("*") if p.stem.rsplit("-", 1)[0] == stem)
        samples, rejected = [], []
        for path in sorted(files):
            index = int(re.search(r"-(\d+)$", path.stem).group(1)) if re.search(r"-(\d+)$", path.stem) else 1
            parsed, why = extract(path.read_text(encoding="utf-8"))
            if parsed is None:
                rejected.append({"sample_index": index, "category": "no_parsable_block",
                                 "reason": why, "raw": str(path.relative_to(REPO_ROOT))})
                continue
            errors = sorted(validator.iter_errors(parsed), key=lambda e: list(e.path))
            if errors:
                rejected.append({"sample_index": index, "category": "schema_invalid",
                                 "reason": f"{'/'.join(str(p) for p in errors[0].path) or '(root)'}"
                                           f": {errors[0].message}",
                                 "raw": str(path.relative_to(REPO_ROOT))})
                continue
            samples.append({"sample_index": index, "parsed": parsed,
                            "raw": str(path.relative_to(REPO_ROOT)),
                            "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

        variance = {}
        if samples:
            counts = Counter(s["parsed"].get("position") for s in samples)
            top, n = counts.most_common(1)[0]
            variance["position"] = {
                "distribution": dict(counts), "n": len(samples),
                "distinct_values": len(counts), "modal_value": top,
                "modal_fraction": round(n / len(samples), 4),
                "shannon_entropy_bits": round(entropy(counts), 4),
                "unanimous": len(counts) == 1,
            }
        citable = len(samples) >= 5
        if not citable:
            incomplete.append(f"{party['identity'].split(' (')[0]}: {len(samples)}/{k_target}")

        print(f"  {party['identity'].split(' (')[0]:12} {len(samples)}/{k_target}"
              + (f"  {variance['position']['modal_value']} "
                 f"{variance['position']['modal_fraction']:.0%} "
                 f"H={variance['position']['shannon_entropy_bits']}" if variance else "  (no usable samples)"))
        for r in rejected:
            print(f"       rejected [{r['category']}] sample {r['sample_index']}: {r['reason'][:80]}")

        if args.dry_run or not samples:
            continue
        art_dir.mkdir(parents=True, exist_ok=True)
        slug = f"{args.round}-{stem.split('-')[0]}"
        summary = {
            "schema_version": "oagrc-local-solicitation-0.1",
            "artifact_type": "solicitation_summary",
            "round": args.round, "slug": slug,
            "question": declaration["question"],
            "phase": declaration.get("phase", "Phase-2 (informed)"),
            "k_requested": k_target, "k_collected": len(samples),
            "attempts": len(samples) + len(rejected),
            "failures": [r["reason"] for r in rejected], "rejected": rejected,
            "variance": variance,
            "observed_dispersion_not_sampling_variance": (
                "These counts are the OBSERVED DISPERSION of self-reported categories across "
                "captures. Calling it sampling variance would assume the samples are "
                "independent, and independence here rests on the custodian having used a "
                "fresh conversation each time — procedure, not proof. Shared accounts, "
                "backend state, personalisation, model updates between pastes and time of "
                "day are all common causes this number cannot separate."),
            "raw_samples": str((REPO_ROOT / "corpus" / "raw" / args.round)
                               .relative_to(REPO_ROOT)),
            "citability": "citable" if citable else f"non-citable (k<5)",
            "citability_note": (
                "Variance COMPUTED from the samples collected, by this tool, using the same "
                "counting and entropy as the routed arms. Never asserted. capture_response.py "
                "granted the distribution claim on a typed string; that hole is closed and "
                "this artifact is the replacement."),
            "contributor": {
                "identity": party["identity"],
                "provider": party["provider"],
                #  The schema requires a NON-EMPTY version string, and a chat surface
                #  exposes none. Writing null produced an artifact the build would
                #  reject while this tool printed success. The honest value is a
                #  statement that it is unknown, with the reason beside it.
                "version_identifier": "not disclosed by the chat surface",
                "version_unknown_reason": party.get("version_unknown_reason"),
                "sampling_parameters": {"unknown_reason": party.get("sampling_unknown_reason")},
                "system_instructions": party.get("system_instructions_unknown_reason"),
            },
            "serve_configuration": {
                "captured": False,
                "reason": ("A subscription chat surface exposes no serving configuration. "
                           "Nothing about the build, the sampling, the system prompt or any "
                           "intermediary is observable from the client."),
                "delivery": "pasted by hand by the custodian into a fresh conversation",
            },
            "independence_of_samples": (
                f"The capture procedure REQUESTS a fresh conversation per sample. Nothing in "
                f"the bundle attests that one was used, and nothing here can verify it — an "
                f"instruction shown on a screen is not an attestation. Treat these {len(samples)} "
                f"captures as possibly dependent."),
            "never_merge": (
                "This is a chat-surface party. It is NOT the routed API party whose name it "
                "resembles, and must not be pooled with it. D-09."),
            "prompt_sha256": hashlib.sha256(
                (REPO_ROOT / party["prompt_override"]).read_bytes()).hexdigest()
                if party.get("prompt_override") else None,
            "samples": samples,
            "aggregated_utc": utc_now(),
        }
        #  VALIDATE THE OUTPUT BEFORE WRITING IT, not after the build rejects it.
        #  The first version wrote summaries missing `raw_samples` and with a null
        #  `version_identifier`, both required by the corpus schema, and then printed
        #  success — leaving rebuild.py to fail later on an artifact this tool had
        #  already declared good. A tool that announces a result its own schema would
        #  refuse is the fail-open shape this repository keeps rediscovering.
        corpus_schema = json.loads(
            (REPO_ROOT / "tools" / "schemas" / "solicitation.schema.json")
            .read_text(encoding="utf-8"))
        problems = sorted(jsonschema.Draft202012Validator(corpus_schema).iter_errors(summary),
                          key=lambda e: list(e.path))
        if problems:
            print(f"REFUSED: the summary for {party['identity'].split(' (')[0]} does not "
                  f"validate against solicitation.schema.json:")
            for error in problems[:5]:
                print(f"    {'/'.join(str(x) for x in error.path) or '(root)'}: {error.message}")
            return 1
        (art_dir / f"{slug}-summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if incomplete:
        print(f"\nINCOMPLETE — {len(incomplete)} part(y|ies) below k=5: {'; '.join(incomplete)}")
        print("Summaries are written for what exists; they are marked non-citable, which is")
        print("what k<5 means here and not a failure of this tool.")
        return 1
    print(f"\nEvery party reached k>={5}. Variance computed, not asserted.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
