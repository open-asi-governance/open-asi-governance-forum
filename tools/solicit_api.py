#!/usr/bin/env python3
"""Solicit a contribution from a routed API party at k samples, with computed variance.

    python3 tools/solicit_api.py --spec <spec.json> --k 5 --model openai/gpt-5.6-terra \\
        --out-round <round>

**GENERATION code, not maintenance code**, exactly like `solicit_local.py`. Nothing
in `tools/` that the build runs calls a model.

WHY THIS IS A DIFFERENT PARTY FROM THE CHAT SURFACE, and why that matters here.

This corpus already contains contributions from **ChatGPT (OpenAI chat surface)**,
pasted by the custodian. A model reached over an API through a router is **NOT that
party** and must never be merged with it, under the same never-merge rule that keeps
Claude Opus 5, Claude Fable 5 and Claude Code separate (D-09). It is a different
model version, a different invocation surface, and it arrives through
intermediaries the chat surface does not have.

The delivery chain is recorded on every sample because each hop is a party that
could alter what was sent or returned, and none of them is the annotator's to
vouch for:

    annotator  ->  OpenRouter  ->  serving provider (e.g. Azure)  ->  the model

`provider` and the generation id come back from the router and are recorded as the
router reported them. That is the router's testimony, not proof -- D-18 applies to
it exactly as it applies to a model self-reporting its version.

WHAT THIS BUYS THAT THE LOCAL MODEL DOES NOT. The local party is divergent in
lineage but is served by the annotator's own operator on the annotator's own
hardware. This party is not. For the specific question of "did anyone other than
the party that wrote these claims ever check them", a routed frontier model is a
materially stronger answer than a locally-served one -- and still not an
independent evaluation in ICP section 4.4's sense, because the annotator chose the
question, the schema and the excerpt.

Sampling parameters, the requested model, the served model, the router's generation
id, and a machine-captured timestamp are recorded per sample. What CANNOT be
recorded is the provider's system prompt or any router-side transformation, and
those absences are written into the artifact rather than left to be assumed.

Exit status is 0 when at least one sample was collected and recorded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from math import log2
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    return -sum((n / total) * log2(n / total) for n in counts.values() if n)


def call_once(key: str, body: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))



def write_summary(spec: dict, args, samples: list[dict], raw_path: Path) -> None:
    """Conform to tools/schemas/solicitation.schema.json, exactly as the local arm does.

    The first version of this invented its own summary shape and the build refused
    it -- correctly. Two solicitation families writing two different summary shapes
    is how a corpus ends up unable to compare its own arms, and the schema exists to
    prevent that.
    """
    art_dir = REPO_ROOT / "corpus" / "artifacts" / args.out_round
    art_dir.mkdir(parents=True, exist_ok=True)
    served = {s["delivery_chain"]["served_model"] for s in samples}
    providers = sorted({str(s["delivery_chain"]["serving_provider_as_reported_by_router"])
                        for s in samples})
    variance = {}
    for field in spec["variance_fields"]:
        counts = Counter(s["parsed"].get(field) for s in samples)
        top, n = counts.most_common(1)[0]
        variance[field] = {
            "distribution": dict(counts), "n": len(samples),
            "distinct_values": len(counts), "modal_value": top,
            "modal_fraction": round(n / len(samples), 4),
            "shannon_entropy_bits": round(entropy(counts), 4),
            "unanimous": len(counts) == 1,
        }
        print(f"  {field}: modal={top!r} ({n/len(samples):.0%}), "
              f"{len(counts)} distinct, H={variance[field]['shannon_entropy_bits']} bits")

    summary = {
        "schema_version": "oagrc-local-solicitation-0.1",
        "artifact_type": "solicitation_summary",
        "round": args.out_round,
        "slug": spec["slug"],
        "question": spec["question"],
        "phase": spec["phase"],
        "k_requested": args.k,
        "k_collected": len(samples),
        "failures": [],
        "variance": variance,
        "citability": "citable" if len(samples) >= 5 else "non-citable (k<5)",
        "contributor": {
            "identity": spec["identity"],
            # The router's report of what it served. Testimony, not authentication.
            "version_identifier": ", ".join(sorted(served)) or args.model,
            "sampling_parameters": {"temperature": args.temperature,
                                    "max_tokens": args.max_tokens,
                                    "seed": None,
                                    "seed_unsupported_reason":
                                        "The router does not expose a seed parameter."},
        },
        "serve_configuration": {
            "captured": True,
            "router": "openrouter.ai",
            "serving_provider_as_reported_by_router": providers,
            "delivery_chain": "annotator -> OpenRouter -> serving provider -> model",
            "not_captured": ["provider system prompt", "router-side transformation",
                             "weights or build identifier"],
        },
        "prompt_sha256": hashlib.sha256(spec["prompt"].encode("utf-8")).hexdigest(),
        "spec_sha256": hashlib.sha256(Path(args.spec).read_bytes()).hexdigest(),
        "raw_samples": str(raw_path.relative_to(REPO_ROOT)),
    }
    (art_dir / f"{spec['slug']}-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--spec", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--model", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--out-round", required=True)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    args = parser.parse_args()

    import os
    key = os.environ.get(args.api_key_env)
    if not key:
        print(f"REFUSED: {args.api_key_env} is not set.")
        return 1

    if args.temperature <= 0:
        # Same rule solicit_local.py enforces: k identical samples make variance
        # meaningless, and reporting a distribution over them would be a number
        # that looks like variance and is not.
        print("REFUSED: temperature must be > 0, or the k samples measure nothing.")
        return 1

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec_sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    print(f"soliciting k={args.k} from {args.model} at temperature {args.temperature}")
    print(f"  spec      {spec_path}  sha256 {spec_sha[:16]}…")

    samples = []
    for index in range(1, args.k + 1):
        body = {
            "model": args.model,
            "messages": [{"role": "user", "content": spec["prompt"]}],
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": spec["schema_name"], "strict": True,
                                "schema": spec["schema"]},
            },
        }
        try:
            raw = call_once(key, body, args.timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
            print(f"  [{index:2}/{args.k}] FAILED: {error}")
            continue
        if "error" in raw:
            print(f"  [{index:2}/{args.k}] FAILED: {str(raw['error'])[:120]}")
            continue
        text = raw["choices"][0]["message"].get("content")
        if not text:
            # A provider can return an empty completion -- a filter, a refusal, or a
            # response that spent its budget before emitting content. This used to
            # raise out of the loop and lose every sample already collected in the
            # batch, which is D-39's shape: one bad item destroying the rest.
            print(f"  [{index:2}/{args.k}] FAILED: empty completion "
                  f"(finish_reason={raw['choices'][0].get('finish_reason')!r})")
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            print(f"  [{index:2}/{args.k}] FAILED: response was not JSON")
            continue
        samples.append({
            "sample_index": index,
            "captured_utc": utc_now(),
            "parsed": parsed,
            "raw_text": text,
            "delivery_chain": {
                "requested_model": args.model,
                "served_model": raw.get("model"),
                "router": "openrouter.ai",
                "serving_provider_as_reported_by_router": raw.get("provider"),
                "router_generation_id": raw.get("id"),
                "note": ("Each hop could alter what was sent or returned and none is the "
                         "annotator's to vouch for. provider and id are the ROUTER'S "
                         "testimony, not proof -- D-18."),
            },
            "sampling": {"temperature": args.temperature, "max_tokens": args.max_tokens},
            "finish_reason": raw["choices"][0].get("finish_reason"),
            "usage": raw.get("usage"),
        })
        print(f"  [{index:2}/{args.k}] {raw['choices'][0].get('finish_reason')} "
              f"{raw.get('usage',{}).get('completion_tokens','?')}tok")

    if not samples:
        print("REFUSED: no samples collected; nothing recorded.")
        return 1

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{spec['slug']}-samples.json"
    raw_path.write_text(json.dumps({
        "artifact_type": "raw_samples",
        "slug": spec["slug"],
        "identity": spec["identity"],
        "spec_path": str(spec_path),
        "spec_sha256": spec_sha,
        "k_requested": args.k,
        "k_collected": len(samples),
        "unrecorded": {
            "system_prompt": "Not disclosed by the provider or the router.",
            "router_side_transformation": "Cannot be observed from the client.",
            "version_identifier": ("The served model string is what the router reported; "
                                   "no build or weights identifier is exposed."),
        },
        "samples": samples,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_summary(spec, args, samples, raw_path)
    print(f"\ncollected {len(samples)}/{args.k}  →  {raw_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
