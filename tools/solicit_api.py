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



def validate_sample(parsed, schema: dict) -> str | None:
    """Return a rejection reason, or None if the sample conforms.

    THE ROUTER'S STRICT MODE IS NOT EVIDENCE. This tool asked OpenRouter for
    `json_schema` with `strict: true` and then treated "it parsed as JSON" as
    conformance -- so a reply with a missing required field, or a `position` outside
    the enum, was recorded as a good sample and counted toward k. The SOP halts on a
    schema-invalid reply; that halt could not fire, because nothing checked.

    Validation happens HERE, on the annotator's side, against the same schema the
    spec froze. A provider's compliance is a claim like any other.
    """
    try:
        import jsonschema
    except ImportError:                                             # pragma: no cover
        return ("jsonschema is not installed, so this sample could not be validated. "
                "Install it with: python3 -m pip install jsonschema")
    try:
        jsonschema.Draft202012Validator(schema).validate(parsed)
    except jsonschema.ValidationError as error:
        path = "/".join(str(p) for p in error.path) or "(root)"
        return f"schema-invalid at {path}: {error.message}"
    return None


def spend_from(samples: list[dict], model: str, rates_path: Path) -> dict:
    """Actual cost, summed from what each response reported it used.

    Reported usage is the provider's testimony, exactly like the served model string
    and the provider name. It is recorded as such and is not proof of what was
    billed; only the provider's own statement is that.
    """
    entry = {"actual_usd": None, "input_tokens": 0, "output_tokens": 0,
             "basis": "Summed from each response's usage block — the provider's testimony.",
             "rates_version": None}
    for sample in samples:
        usage = sample.get("usage") or {}
        entry["input_tokens"] += usage.get("prompt_tokens") or 0
        entry["output_tokens"] += usage.get("completion_tokens") or 0
    if not rates_path.is_file():
        return entry
    rates = json.loads(rates_path.read_text(encoding="utf-8"))
    entry["rates_version"] = rates.get("rates_version")
    rate = rates.get("usd_per_million_tokens", {}).get(model)
    if rate and (entry["input_tokens"] or entry["output_tokens"]):
        entry["actual_usd"] = round(
            (entry["input_tokens"] * rate["input"]
             + entry["output_tokens"] * rate["output"]) / 1_000_000, 4)
        entry["rates_are_verified"] = bool(rates.get("verified_by_custodian"))
    return entry


def write_summary(spec: dict, args, samples: list[dict], raw_path: Path,
                  rejected: list[dict]) -> None:
    """Conform to tools/schemas/solicitation.schema.json, exactly as the local arm does.

    The first version of this invented its own summary shape and the build refused
    it -- correctly. Two solicitation families writing two different summary shapes
    is how a corpus ends up unable to compare its own arms, and the schema exists to
    prevent that.
    """
    art_dir = REPO_ROOT / "corpus" / "artifacts" / args.out_round
    art_dir.mkdir(parents=True, exist_ok=True)
    served = {s["delivery_chain"]["served_model"] for s in samples}
    #  null means the router did not say, which is NOT the same as a provider named
    #  "None". str() on the missing value produced exactly that string and put it in
    #  the published record as though it were a provider's name.
    providers = sorted({p for p in (s["delivery_chain"]
                                    ["serving_provider_as_reported_by_router"]
                                    for s in samples) if p is not None})
    provider_unreported = any(s["delivery_chain"]["serving_provider_as_reported_by_router"]
                              is None for s in samples)
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
        #  EVERY attempt is accounted for. Rejected samples used to vanish: a
        #  transport error, an empty completion or unparseable JSON simply reduced
        #  k_collected, so "nothing solicited is discarded" was false and a
        #  schema-invalid reply was indistinguishable from a call that never
        #  happened. Each rejection now carries its category and its raw bytes.
        "failures": [r["reason"] for r in rejected],
        "attempts": args.k,
        "rejected": rejected,
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
        "spend": spend_from(samples, args.model,
                            REPO_ROOT / "record" / "cycles" / "model-rates.json"),
        "serve_configuration": {
            "captured": True,
            "router": "openrouter.ai",
            "serving_provider_as_reported_by_router": providers,
            "provider_not_reported_for_some_samples": provider_unreported,
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

    samples: list[dict] = []
    rejected: list[dict] = []

    def reject(index: int, category: str, reason: str, bytes_seen: str | None = None) -> None:
        """Every attempt that did not become a sample is recorded, with its bytes."""
        rejected.append({"sample_index": index, "category": category, "reason": reason,
                         "captured_utc": utc_now(),
                         "response_bytes": (bytes_seen or "")[:4000] or None})
        print(f"  [{index:2}/{args.k}] REJECTED ({category}): {reason[:140]}")

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
            reject(index, "transport", f"{type(error).__name__}: {error}")
            continue
        if "error" in raw:
            reject(index, "provider_error", str(raw["error"])[:400])
            continue
        text = raw["choices"][0]["message"].get("content")
        if not text:
            # A provider can return an empty completion -- a filter, a refusal, or a
            # response that spent its budget before emitting content. This used to
            # raise out of the loop and lose every sample already collected in the
            # batch, which is D-39's shape: one bad item destroying the rest.
            reject(index, "empty_completion",
                   f"finish_reason={raw['choices'][0].get('finish_reason')!r}")
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as error:
            reject(index, "malformed_json", str(error), text)
            continue
        invalid = validate_sample(parsed, spec["schema"])
        if invalid:
            reject(index, "schema_invalid", invalid, text)
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
        #  Nothing conformed. The rejections are still written, because "no usable
        #  sample" and "the call was never made" must not look the same in the
        #  record -- a party that returned five schema-invalid replies said
        #  something, and erasing it would be the strongest possible form of the
        #  discard this tool is supposed to have stopped doing.
        raw_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
        raw_dir.mkdir(parents=True, exist_ok=True)
        reject_path = raw_dir / f"{spec['slug']}-rejected.json"
        if not reject_path.exists():
            reject_path.write_text(json.dumps({
                "artifact_type": "rejected_samples",
                "slug": spec["slug"], "identity": spec["identity"],
                "spec_path": str(spec_path), "spec_sha256": spec_sha,
                "k_requested": args.k, "k_collected": 0,
                "note": ("Every attempt failed validation, transport or the provider. "
                         "No summary is written because there is no distribution to "
                         "compute, but what happened is recorded."),
                "rejected": rejected,
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"REFUSED: no usable samples. {len(rejected)} rejection(s) recorded at "
                  f"{reject_path.relative_to(REPO_ROOT)}")
        else:
            print(f"REFUSED: no usable samples, and {reject_path.name} already exists.")
        return 1

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{spec['slug']}-samples.json"
    # RAW MATERIAL IS NEVER OVERWRITTEN. This tool had no guard, and a re-run of the
    # same slug silently replaced an ALREADY-COMMITTED sample file -- the corpus's
    # central rule, broken by its own instrument. The manifest caught it as MODIFIED,
    # which is the control working, but the bytes were already gone from the working
    # tree and only git had them.
    #
    # A second solicitation is a NEW artifact, not a correction. Choose a distinct
    # slug and record why, so the record shows that the parameter mattered rather
    # than hiding the first attempt.
    if raw_path.exists():
        print(f"REFUSED: {raw_path.relative_to(REPO_ROOT)} already exists.")
        print("  Raw material is immutable once written. A re-solicitation is a new")
        print("  artifact: change the spec's slug and state why in the new file.")
        return 1

    raw_path.write_text(json.dumps({
        "artifact_type": "raw_samples",
        "slug": spec["slug"],
        "identity": spec["identity"],
        "spec_path": str(spec_path),
        "spec_sha256": spec_sha,
        "k_requested": args.k,
        "k_collected": len(samples),
        "rejected": rejected,
        "unrecorded": {
            "system_prompt": "Not disclosed by the provider or the router.",
            "router_side_transformation": "Cannot be observed from the client.",
            "version_identifier": ("The served model string is what the router reported; "
                                   "no build or weights identifier is exposed."),
        },
        "samples": samples,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_summary(spec, args, samples, raw_path, rejected)
    print(f"\ncollected {len(samples)}/{args.k}  →  {raw_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
