#!/usr/bin/env python3
"""Capture one model or human response into the corpus with full provenance.

This tool exists because of prediction P-0003, which forecasts that the k >= 5
standard will erode because collecting it is expensive. The honest response to
predicting your own standard will decay is to attack the cost of meeting it, so
capture is one command and the tool refuses to record a contribution that is
missing provenance the project has committed to recording.

What it does:

  1. copies the response byte-identical into corpus/raw/<round>/, refusing to
     overwrite an existing capture (raw material is immutable)
  2. writes a provenance record to corpus/artifacts/<round>/
  3. rebuilds corpus/MANIFEST.sha256 so the new raw file is hash-anchored

What it refuses to do:

  - record a null model version, sampling parameter set, reasoning effort, or
    system-instruction field without an explicit stated reason
  - mark anything citable at k < 5 or without a reported variance
  - overwrite a raw file that already exists
  - accept a capture timestamp that is not UTC ISO-8601

Example -- a single informed response with an unknown model version:

    python3 tools/capture_response.py \\
      --round review-round-01 \\
      --response ~/inbox/grok-reply.md \\
      --prompt record/review-round-01-prompt.md \\
      --identity "Grok" --provider "xAI" \\
      --version-unknown "Web UI does not expose a version identifier." \\
      --sampling-unknown "Web UI does not expose sampling parameters." \\
      --effort-unknown "Not selectable in the web UI." \\
      --system-instructions-unknown "Provider system prompt not disclosed." \\
      --captured-utc 2026-08-06T14:03:00Z \\
      --phase informed \\
      --capture-method "Pasted from web UI by the custodian." \\
      --captured-by "Stephen Reed (human custodian)"

Add --k 5 --sample-index 1 --variance "..." when collecting a citable set.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PHASES = {"blind": "Phase-1 (blind)", "informed": "Phase-2 (informed)"}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def slug(text: str) -> str:
    kept = [c.lower() if c.isalnum() else "-" for c in text]
    out = "".join(kept)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def fail(message: str) -> None:
    print(f"REFUSED: {message}", file=sys.stderr)
    sys.exit(1)


def anchored(path: Path) -> dict:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256_of(path),
        "bytes": path.stat().st_size,
    }


def build_contributor(args: argparse.Namespace) -> dict:
    """Assemble the contributor block, enforcing value-or-reason for each field."""
    contributor = {"identity": args.identity, "provider": args.provider}

    # (field, reason_key, supplied_value, supplied_reason, value_flag, reason_flag)
    required_fields = [
        ("version_identifier", "version_unknown_reason",
         args.model_version, args.version_unknown, "--model-version", "--version-unknown"),
        ("reasoning_effort", "reasoning_effort_unknown_reason",
         args.effort, args.effort_unknown, "--effort", "--effort-unknown"),
        ("system_instructions", "system_instructions_unknown_reason",
         args.system_instructions, args.system_instructions_unknown,
         "--system-instructions", "--system-instructions-unknown"),
    ]
    for field, reason_key, value, reason, value_flag, reason_flag in required_fields:
        if value and reason:
            fail(f"pass only one of {value_flag} / {reason_flag} for {field}")
        if not value and not reason:
            fail(
                f"{field} is required. Supply {value_flag}, or {reason_flag} with a stated "
                f"reason. An unknown value is recorded with a reason; it is never omitted."
            )
        contributor[field] = value or None
        if reason:
            contributor[reason_key] = reason

    if args.sampling and args.sampling_unknown:
        fail("pass only one of --sampling / --sampling-unknown")
    if not args.sampling and not args.sampling_unknown:
        fail("sampling parameters are required. Supply --sampling '<json>' or --sampling-unknown '<reason>'.")
    if args.sampling:
        try:
            contributor["sampling_parameters"] = json.loads(args.sampling)
        except json.JSONDecodeError as error:
            fail(f"--sampling must be valid JSON: {error}")
    else:
        contributor["sampling_parameters"] = None
        contributor["sampling_unknown_reason"] = args.sampling_unknown

    contributor["tools_used"] = args.tool or []
    if args.prior_context:
        contributor["prior_context"] = args.prior_context
    return contributor


def determine_citability(args: argparse.Namespace) -> tuple[str, str]:
    """Two propositions, two fields.

    A single sample IS citable as an artifact of one identified invocation -- it is evidence
    that this text was produced. It is NOT sufficient to characterise a stable position or to
    estimate sampling variance. The earlier single overloaded value conflated those, and the
    register had already recorded the conflation as a defect (D-07) while this tool went on
    enforcing it on every capture. Corrected per ChatGPT, review round 02.
    """
    if args.k == 1:
        return "citable_artifact", "insufficient_k"
    if args.k >= 5 and args.variance:
        return "citable_artifact_and_distribution", "supported"
    if args.k >= 5:
        return "citable_artifact", "insufficient_variance_reporting"
    return "citable_artifact", "insufficient_k"


def validate_record(record: dict) -> None:
    try:
        import jsonschema
    except ImportError:
        print("warn: jsonschema not installed; schema validation skipped", file=sys.stderr)
        return
    schema = json.loads((REPO_ROOT / "tools/schemas/contribution.schema.json").read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path))
    if errors:
        for error in errors:
            location = "/".join(str(p) for p in error.path) or "<root>"
            print(f"  schema error at {location}: {error.message}", file=sys.stderr)
        fail("the provenance record does not satisfy contribution.schema.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--round", required=True, help="e.g. review-round-01")
    parser.add_argument("--response", required=True, help="file holding the raw response, verbatim")
    parser.add_argument("--prompt", required=True, help="repo-relative path to the prompt that produced it")
    parser.add_argument("--identity", required=True, help="distinct model or invocation surface")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model-version")
    parser.add_argument("--version-unknown")
    parser.add_argument("--sampling", help="JSON object of sampling parameters")
    parser.add_argument("--sampling-unknown")
    parser.add_argument("--effort")
    parser.add_argument("--effort-unknown")
    parser.add_argument("--system-instructions")
    parser.add_argument("--system-instructions-unknown")
    parser.add_argument("--captured-utc", required=True, help="YYYY-MM-DDTHH:MM:SSZ, recorded at capture")
    parser.add_argument("--phase", required=True, choices=sorted(PHASES))
    parser.add_argument("--capture-method", default="")
    parser.add_argument("--captured-by", required=True)
    parser.add_argument("--edit-status", default="unedited")
    parser.add_argument("--k", type=int, default=1)
    parser.add_argument("--sample-index", type=int, default=1)
    parser.add_argument("--variance", help="variance across the k samples; required for citability")
    parser.add_argument("--tool", action="append", help="repeatable")
    parser.add_argument("--prior-context")
    parser.add_argument("--notes")
    args = parser.parse_args()

    response = Path(args.response).expanduser()
    if not response.is_absolute():
        response = (REPO_ROOT / response) if (REPO_ROOT / response).exists() else Path.cwd() / response
    if not response.exists():
        fail(f"response file not found: {args.response}")

    prompt = REPO_ROOT / args.prompt
    if not prompt.exists():
        fail(f"prompt file not found in the repository: {args.prompt}")

    if not (args.captured_utc.endswith("Z") and len(args.captured_utc) == 20 and "T" in args.captured_utc):
        fail("--captured-utc must be UTC ISO-8601, e.g. 2026-08-06T14:03:00Z")

    if args.k < 1:
        fail("--k must be at least 1")
    if args.sample_index > args.k:
        fail(f"--sample-index {args.sample_index} exceeds --k {args.k}")

    # Validate every argument BEFORE touching the filesystem. A tool that enforces
    # immutability must never leave a partial artifact behind when it refuses.
    contributor = build_contributor(args)

    identity_slug = slug(args.identity)
    suffix = response.suffix or ".md"
    name = f"{identity_slug}-{args.sample_index:02d}{suffix}"

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.round
    raw_target = raw_dir / name
    if raw_target.exists():
        fail(
            f"{raw_target.relative_to(REPO_ROOT)} already exists. Raw material is immutable; "
            f"corrections are made by superseding artifacts, never by overwriting."
        )
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(response, raw_target)

    if sha256_of(raw_target) != sha256_of(response):
        raw_target.unlink()
        fail("copy was not byte-identical; aborted")

    record = {
        "schema_version": "oagrc-contribution-0.1",
        "artifact_id": f"OAGRC-{args.captured_utc[:10]}-{identity_slug.upper()}-{slug(args.round).upper()}-{args.sample_index:03d}",
        "artifact_type": "contribution",
        "round": args.round,
        "raw": anchored(raw_target),
        "prompt": anchored(prompt),
        "contributor": contributor,
        "captured_utc": args.captured_utc,
        "capture_method": args.capture_method,
        "phase": PHASES[args.phase],
        "edit_status": args.edit_status,
        "k": args.k,
        "sample_index": args.sample_index,
        "variance_reported": bool(args.variance),
        "variance": args.variance,
        "citability": determine_citability(args)[0],
        "distributional_inference": determine_citability(args)[1],
        "attribution_status": "active",
        "captured_by": args.captured_by,
    }
    if args.notes:
        record["notes"] = args.notes

    try:
        validate_record(record)
    except SystemExit:
        raw_target.unlink(missing_ok=True)   # never leave a partial capture behind
        raise

    artifact_dir = REPO_ROOT / "corpus" / "artifacts" / args.round
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{identity_slug}-{args.sample_index:02d}.json"
    artifact_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/build_manifest.py"), "corpus/raw/"],
        cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL,
    )

    print(f"captured  {raw_target.relative_to(REPO_ROOT)}")
    print(f"provenance {artifact_path.relative_to(REPO_ROOT)}")
    print(f"artifact_id {record['artifact_id']}")
    print(f"citability  {record['citability']} / {record['distributional_inference']}")
    print("manifest rebuilt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
