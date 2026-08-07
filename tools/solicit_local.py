#!/usr/bin/env python3
"""Solicit a contribution from a locally-served model at k samples, with computed variance.

**This is GENERATION code, not maintenance code.** The rest of `tools/` is deterministic and
contains no LLM in the path, because a maintenance path that calls a model cannot be reproduced.
This program instead *solicits* a contribution, exactly as a human pasting into a chat surface
does — the difference is that everything a chat surface hides is recorded here.

Why this exists
---------------
Every contribution in this corpus so far is k = 1, because each frontier contribution costs a
manual paste. P-0003 predicts that the project's own k >= 5 standard erodes for precisely that
reason. A locally-served model is the one participant for which the standard is nearly free, and
the one participant whose provenance can be complete: exact model path, quantisation, sampling
parameters, seed, and a machine-captured timestamp. Deficiencies D-01 through D-04 are
unremediable for chat-surface models and fully satisfiable here.

Two design choices that are not incidental
------------------------------------------
1. **Structured output via `response_format: json_schema`.** Verified on 2026-08-05: the served
   model reasons by default, and a plain-text request spent its entire budget on chain-of-thought
   without emitting an answer. Grammar-constrained decoding prevents thinking tokens *structurally*
   rather than by instruction, so the answer is the whole output.
2. **Variance is computed, never asserted.** ChatGPT's round-02 review noted that "reported
   variance figure" is undefined for open-ended text and that the capture tool accepts a variance
   string without verifying the samples exist. So solicitations are shaped as categorical
   judgements: variance is the class-frequency distribution and its Shannon entropy over the k
   samples, computed from the samples actually collected.

Usage
-----
    python3 tools/solicit_local.py --spec solicitations/q02-blind.json --k 20

The spec file declares the prompt, the JSON schema, the categorical fields to measure variance
over, and the phase. Prompts live in files so the exact text is committed before it is sent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import urllib.request
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENDPOINT = "http://localhost:8000/v1/chat/completions"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def capture_serve_config() -> dict:
    """Record how the model is actually being served, from the running process.

    A chat surface cannot supply this. Recording it is the entire reason a locally-served
    contribution can carry provenance that a frontier contribution structurally cannot.
    """
    try:
        out = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True, check=True).stdout
    except Exception as error:
        return {"captured": False, "reason": f"ps failed: {error}"}

    for line in out.splitlines():
        if "trtllm-serve" in line and "grep" not in line:
            tokens = line.split()
            flags = {}
            for i, tok in enumerate(tokens):
                if tok.startswith("--") and i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                    flags[tok.lstrip("-")] = tokens[i + 1]
            model_path = next((t for t in tokens if "/models/" in t), None)
            return {"captured": True, "backend": "tensorrt_llm", "model_path": model_path,
                    "serve_flags": flags, "command_line": line.strip()}
    return {"captured": False, "reason": "no trtllm-serve process found"}


def call_once(endpoint: str, body: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        endpoint, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def validate_sample(parsed, schema: dict) -> str | None:
    """Return a rejection reason, or None if the sample conforms. See solicit_api.py."""
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


def shannon_entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in counts.values() if n)


def compute_variance(samples: list[dict], fields: list[str]) -> dict:
    """Variance over the samples actually collected. Never asserted, always derived."""
    report = {}
    for field in fields:
        values = [json.dumps(s.get(field), sort_keys=True) if isinstance(s.get(field), (dict, list))
                  else s.get(field) for s in samples]
        counts = Counter(values)
        total = len(values)
        modal, modal_n = counts.most_common(1)[0] if counts else (None, 0)
        report[field] = {
            "distribution": {str(k): v for k, v in counts.most_common()},
            "n": total,
            "distinct_values": len(counts),
            "modal_value": modal,
            "modal_fraction": round(modal_n / total, 4) if total else 0.0,
            "shannon_entropy_bits": round(shannon_entropy(counts), 4),
            "unanimous": len(counts) == 1,
        }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", required=True, help="solicitation spec JSON, committed before sending")
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="must be > 0 to measure sampling variance at all")
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default="qwen3.6-35b-a3b")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--out-round", required=True, help="round label under corpus/raw/")
    args = parser.parse_args()

    spec_path = REPO_ROOT / args.spec if not Path(args.spec).is_absolute() else Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    prompt = spec["prompt"]

    if args.temperature <= 0:
        print("REFUSED: temperature must be > 0, or every sample is identical and variance is "
              "meaningless. Use --k 1 for a deterministic single answer instead.", file=sys.stderr)
        return 1

    serve = capture_serve_config()
    print(f"soliciting k={args.k} from {args.model} at temperature {args.temperature}")
    print(f"  spec      {spec_path.relative_to(REPO_ROOT)}  sha256 {sha256_text(spec_path.read_text())[:16]}…")
    print(f"  serve cfg {'captured' if serve.get('captured') else serve.get('reason')}")

    samples, raw_responses, failures = [], [], []
    for i in range(args.k):
        body = {
            "model": args.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "seed": spec.get("seed_base", 1000) + i,
            "stream": False,
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": spec.get("schema_name", "response"),
                                                "schema": spec["schema"]}},
        }
        try:
            result = call_once(args.endpoint, body, args.timeout)
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except Exception as error:
            failures.append({"sample_index": i + 1, "category": "transport_or_malformed",
                             "error": f"{type(error).__name__}: {error}"})
            print(f"  [{i+1:>2}/{args.k}] REJECTED (transport_or_malformed): {error}")
            continue
        #  A grammar-constrained endpoint is not a validator. `response_format` above
        #  is a request; whether the bytes conform is a separate question, and this
        #  arm used to answer it by assuming. The routed arm validates identically,
        #  so the two arms' k_collected mean the same thing.
        invalid = validate_sample(parsed, spec["schema"])
        if invalid:
            failures.append({"sample_index": i + 1, "category": "schema_invalid",
                             "error": invalid, "response_bytes": content[:4000]})
            print(f"  [{i+1:>2}/{args.k}] REJECTED (schema_invalid): {invalid[:140]}")
            continue
        samples.append(parsed)
        raw_responses.append({"sample_index": i + 1, "content": content,
                              "finish_reason": result["choices"][0].get("finish_reason"),
                              "usage": result.get("usage"), "seed": body["seed"]})
        print(f"  [{i+1:>2}/{args.k}] {result['choices'][0].get('finish_reason')} "
              f"{result.get('usage', {}).get('completion_tokens')}tok")

    if not samples:
        print("REFUSED: no samples collected; nothing recorded.", file=sys.stderr)
        return 1

    variance = compute_variance(samples, spec["variance_fields"])

    out_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = spec["slug"]

    raw_path = out_dir / f"{slug}-samples.json"
    if raw_path.exists():
        print(f"REFUSED: {raw_path.relative_to(REPO_ROOT)} exists. Raw material is immutable.", file=sys.stderr)
        return 1
    raw_path.write_text(json.dumps({"spec": spec, "responses": raw_responses, "failures": failures},
                                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        "schema_version": "oagrc-local-solicitation-0.1",
        "artifact_type": "solicitation_summary",
        "round": args.out_round,
        "slug": slug,
        "question": spec.get("question"),
        "phase": spec["phase"],
        "k_requested": args.k,
        "k_collected": len(samples),
        "failures": failures,
        "attempts": args.k,
        "rejected": failures,
        "spend": {"actual_usd": 0.0, "input_tokens": None, "output_tokens": None,
                  "basis": ("Served on the custodian's own hardware. Zero marginal API "
                            "cost; electricity and wear are real and are not modelled.")},
        "variance": variance,
        "citability": ("citable" if len(samples) >= 5 else "non-citable (k<5)"),
        "citability_note": ("Variance is computed from the samples actually collected, not asserted. "
                            "k>=5 with computed variance is the project's stated bar; this is the first "
                            "contribution type able to meet it, because a locally-served model makes "
                            "repeated sampling nearly free."),
        "contributor": {
            "identity": spec.get("identity", "qwen3.6-35b-a3b (API surface)"),
            "provider": "locally served, operator-hosted",
            "version_identifier": args.model,
            "sampling_parameters": {"temperature": args.temperature, "max_tokens": args.max_tokens,
                                    "seed_base": spec.get("seed_base", 1000),
                                    "response_format": "json_schema (grammar-constrained)"},
            "reasoning_effort": "thinking disabled structurally by grammar constraint",
            "system_instructions": "none supplied; the prompt is the entire input",
            "tools_used": [],
        },
        "serve_configuration": serve,
        "prompt_sha256": sha256_text(prompt),
        "spec_sha256": sha256_text(spec_path.read_text(encoding="utf-8")),
        "raw_samples": str(raw_path.relative_to(REPO_ROOT)),
    }

    summary_dir = REPO_ROOT / "corpus" / "artifacts" / args.out_round
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / f"{slug}-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\ncollected {len(samples)}/{args.k}  →  {raw_path.relative_to(REPO_ROOT)}")
    print(f"summary   →  {summary_path.relative_to(REPO_ROOT)}")
    for field, stats in variance.items():
        print(f"  {field}: modal={stats['modal_value']!r} "
              f"({stats['modal_fraction']:.0%}), {stats['distinct_values']} distinct, "
              f"H={stats['shannon_entropy_bits']} bits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
