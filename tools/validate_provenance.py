#!/usr/bin/env python3
"""Validate OAGRC annotation artifacts against the provenance schema and the
project's provenance rules.

Deterministic by design. No network access, no model calls. Given the same
inputs this program always produces the same output, because the record's
reproducibility requirement cannot survive a maintenance path that is itself
irreproducible.

Checks performed beyond JSON Schema validation:

  P1  the annotated source file exists and its SHA-256 matches the recorded hash
  P2  segment line ranges are well formed, non-overlapping, and ascending
  P3  segment ids are unique and sequential
  P4  no placeholder version identifiers (the "gemini-2026-v-current" failure)
  P5  every null provenance value carries a stated reason
  P6  segments with no resolved identity are explicitly repudiated or disputed
  P7  the annotator declares a conflict of interest
  P8  declared segment_count and counts_by_identity agree with the segments

Usage:
    python3 tools/validate_provenance.py corpus/
    python3 tools/validate_provenance.py corpus/artifacts/segments.json

Exit status is 0 when every check passes and 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

# Values that look like a version identifier but resolve to nothing. Recording
# one of these is worse than recording null, because it defeats the reader's
# ability to notice that the version is unknown.
PLACEHOLDER_MARKERS = ("current", "latest", "tbd", "unknown", "n/a", "todo", "xxx")

# Provenance fields whose null value must be justified by a sibling reason key.
REASON_REQUIRED = {
    "version_identifier": "version_unknown_reason",
    "sampling_parameters": "sampling_unknown_reason",
    "timestamp_utc": "timestamp_unknown_reason",
    "system_instructions": "system_instructions_unknown_reason",
    "reasoning_effort": "reasoning_effort_unknown_reason",
}


class Report:
    """Accumulates findings so that one run reports every problem, not the first."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, check: str, message: str) -> None:
        self.errors.append(f"[{check}] {message}")

    def warn(self, check: str, message: str) -> None:
        self.warnings.append(f"[{check}] {message}")

    @property
    def ok(self) -> bool:
        return not self.errors


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


SCHEMA_FOR_TYPE = {
    "annotation": "segments.schema.json",
    "contribution": "contribution.schema.json",
    "solicitation_summary": "solicitation.schema.json",
    "agenda_cohort_exposure": "cohort-exposure.schema.json",
    "agenda_activation_record": "agenda-activation.schema.json",
    #  A gate on an instrument, not a deliberative artifact. Registered 2026-08-10.
    "qualification_record": "qualification.schema.json",
    "ratification_record": "ratification-result.schema.json",
    "freetext_coding": "freetext-coding.schema.json",
    "finding_coding": "finding-coding.schema.json",
    "deficiency_register": "deficiency-register.schema.json",
}


def check_schema(document: dict, report: Report) -> None:
    """Validate against the schema for this artifact_type. Missing jsonschema FAILS.

    This used to warn and continue, so a machine without `jsonschema` installed
    skipped structural validation entirely and the build still announced "All
    provenance checks passed." A validator that reports success when it did not
    validate is worse than no validator: it converts an absent check into a
    positive assurance. Filed with D-29 as the same class of fail-open defect.
    """
    try:
        import jsonschema
    except ImportError:
        # ERROR, not warn. This previously warned and returned, so a run on a machine
        # without jsonschema printed "All provenance checks passed" having performed no
        # structural validation whatsoever -- and exited 0, which rebuild.py reads as
        # success and the standing `rebuild && commit` chain reads as permission to
        # commit. A check that reports PASS when it did not run is worse than absent.
        #
        # Found TWICE INDEPENDENTLY on 2026-08-06: by Codex reviewing the T-13 design
        # on Track B, and by Track A auditing the maintenance path after D-29. Neither
        # track knew of the other's finding until this merge. Recorded because the
        # convergence is evidence, not bookkeeping: two unrelated audits of the same
        # tooling landed on the same line, which is what a systematic defect class looks
        # like from the inside. The fail-open pattern -- report success for a check that
        # did not execute -- is now a named review target, not a one-off repair.
        report.error(
            "SCHEMA",
            "jsonschema is not installed, so structural validation did NOT run. "
            "Refusing to report a pass that was never checked. "
            "Install with: python3 -m pip install jsonschema",
        )
        return

    artifact_type = document.get("artifact_type")
    schema_name = SCHEMA_FOR_TYPE.get(artifact_type)
    if schema_name is None:
        report.error("SCHEMA", f"unknown artifact_type {artifact_type!r}; expected one of {sorted(SCHEMA_FOR_TYPE)}")
        return

    schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        report.error("SCHEMA", f"schema not found: {schema_path}")
        return

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for failure in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
        location = "/".join(str(part) for part in failure.path) or "<root>"
        report.error("SCHEMA", f"{location}: {failure.message}")


def check_source_hash(document: dict, report: Report) -> None:
    """P1 — every artifact must be anchored to a byte-identical source.

    Annotations anchor a `source`; contributions anchor `raw` and `prompt`. All
    of them are checked, because an anchor that is never verified is decoration.
    """
    anchors = []
    if "source" in document:
        anchors.append(("source", document["source"]))
    for key in ("raw", "prompt"):
        if key in document:
            anchors.append((key, document[key]))

    if document.get("artifact_type") in ("agenda_cohort_exposure", "agenda_activation_record",
                                        "qualification_record", "ratification_record"):
        #  Anchors EVERY raw sample file it was computed from, like a finding_coding, not one
        #  source: a record describing four parties' deliveries that anchored only the first
        #  could drift from three of them without any check noticing.
        sources = document.get("sources") or []
        if not sources:
            report.error("P1", "cohort exposure declares no sources to anchor")
            return
        for index, source in enumerate(sources):
            check_one_anchor(f"sources[{index}]", source, report)
        return

    if document.get("artifact_type") == "qualification_record":
        #  CROSS-FIELD invariants JSON Schema cannot express. Without these, a one-party result
        #  listing five sources validated cleanly and a `qualified: true` could coexist with a
        #  failed party.
        expected = set(document.get("expected_parties") or [])
        scored = set((document.get("per_party") or {}).keys())
        if expected != scored:
            report.error("QUAL", f"per_party covers {sorted(scored)}, expected {sorted(expected)}")
        failed = [p for p, r in (document.get("per_party") or {}).items() if not r.get("passed")]
        if document.get("qualified") and failed:
            report.error("QUAL", f"qualified is true while {sorted(failed)} did not pass")
        if document.get("qualified") and document.get("state") != "QUALIFIED":
            report.error("QUAL", "qualified is true but state is not QUALIFIED")
        k_by = document.get("k_by_party") or {}
        for party, result in (document.get("per_party") or {}).items():
            if result.get("passed") and result.get("k_collected") != k_by.get(party):
                report.error("QUAL", f"{party} passed with k_collected "
                                     f"{result.get('k_collected')} != registered {k_by.get(party)}")
        named = {Path(s["path"]).name for s in (document.get("sources") or [])}
        for party in expected:
            if any(party in n for n in named):
                continue
            if (document.get("per_party") or {}).get(party, {}).get("k_collected"):
                report.error("QUAL", f"{party} has samples but no anchored source")

    if document.get("artifact_type") == "freetext_coding":
        check_one_anchor("coded_source", document.get("coded_source", {}), report)
        return

    if document.get("artifact_type") == "solicitation_summary":
        raw = REPO_ROOT / document.get("raw_samples", "")
        if not document.get("raw_samples") or not raw.is_file():
            report.error("P1", f"raw_samples not found: {document.get('raw_samples')!r}")
        return

    if document.get("artifact_type") == "finding_coding":
        # A coding anchors EVERY response it codes, not one source. Checking only the
        # first would let a coding drift from the responses it claims to summarise.
        sources = document.get("sources") or []
        if not sources:
            report.error("P1", "finding_coding declares no sources to anchor")
            return
        for index, source in enumerate(sources):
            check_one_anchor(f"sources[{index}]", source, report)
        return

    if not anchors:
        report.error("P1", "no anchored source: expected 'source', or 'raw' and 'prompt'")
        return

    for label, anchor in anchors:
        check_one_anchor(label, anchor, report)


def check_one_anchor(label: str, source: dict, report: Report) -> None:
    relative = source.get("path", "")
    if not relative:
        report.error("P1", f"{label}: no path recorded")
        return

    raw_path = REPO_ROOT / relative
    recorded = source.get("sha256", "")

    if raw_path.is_dir():
        report.error("P1", f"{label}: path {relative!r} is a directory, not a file")
        return

    if not raw_path.exists():
        report.error("P1", f"{label}: anchored file missing: {relative}")
        return

    actual = sha256_of(raw_path)
    if actual != recorded:
        report.error(
            "P1",
            f"{label}: hash mismatch for {relative}\n"
            f"        recorded: {recorded}\n"
            f"        actual:   {actual}\n"
            f"        The raw record must never be edited after commit. If this file "
            f"changed, that change is itself the defect.",
        )

    line_count = len(raw_path.read_bytes().splitlines())
    if "lines" in source and source["lines"] != line_count:
        report.error("P1", f"recorded line count {source['lines']} != actual {line_count}")


def check_segments(document: dict, report: Report) -> None:
    """P2, P3, P6 — segment structure, ordering, and attribution."""
    segments = document.get("segments", [])
    source_lines = document.get("source", {}).get("lines")

    seen_ids: set[str] = set()
    previous_end = 0

    for index, segment in enumerate(segments):
        seg_id = segment.get("id", f"<index {index}>")

        if seg_id in seen_ids:
            report.error("P3", f"duplicate segment id: {seg_id}")
        seen_ids.add(seg_id)

        expected_id = f"S-{index + 1:02d}"
        if seg_id != expected_id:
            report.error("P3", f"segment at position {index} has id {seg_id}, expected {expected_id}")

        lines = segment.get("lines", [])
        if len(lines) != 2:
            report.error("P2", f"{seg_id}: line range must be [start, end]")
            continue

        start, end = lines
        if start > end:
            report.error("P2", f"{seg_id}: inverted line range {start}-{end}")
        if start <= previous_end:
            report.error(
                "P2",
                f"{seg_id}: range starts at {start} but the previous segment ended at "
                f"{previous_end}; segments must not overlap",
            )
        if source_lines and end > source_lines:
            report.error("P2", f"{seg_id}: range ends at {end}, past end of source ({source_lines})")
        previous_end = max(previous_end, end)

        if segment.get("identity") is None:
            status = segment.get("attribution_status")
            if status not in ("repudiated", "invocation integrity disputed"):
                report.error(
                    "P6",
                    f"{seg_id}: no resolved identity but attribution_status is "
                    f"{status!r}; unattributed segments must be explicitly repudiated "
                    f"or disputed, never left implicitly active",
                )

    declared = document.get("segment_count")
    if declared is not None and declared != len(segments):
        report.error("P8", f"declared segment_count {declared} != actual {len(segments)}")


def check_placeholders(node: object, report: Report, path: str = "", quoted: bool = False) -> None:
    """P4 — reject placeholder version identifiers that this project asserts.

    A placeholder inside `self_reported_provenance` is different in kind: it is a
    verbatim quotation of what a contributor claimed about itself. Quotations are
    never sanitized -- that would be exactly the silent correction this project
    forbids. Such a placeholder is reported as a warning so it can be carried in
    the deficiency register instead of edited away.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}/{key}" if path else key
            in_quotation = quoted or key == "self_reported_provenance"
            if key == "version_identifier" and isinstance(value, str):
                lowered = value.lower()
                if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
                    if quoted:
                        report.warn(
                            "P4",
                            f"{here}: quoted placeholder {value!r}. Preserved verbatim as "
                            f"testimony; confirm it is recorded in corpus/deficiencies.md.",
                        )
                    else:
                        report.error(
                            "P4",
                            f"{here}: {value!r} is a placeholder, not a version identifier. "
                            f"Record null with a stated reason instead.",
                        )
            check_placeholders(value, report, here, in_quotation)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            check_placeholders(item, report, f"{path}[{index}]", quoted)


def check_null_reasons(node: object, report: Report, path: str = "") -> None:
    """P5 — a null provenance value must be justified, never merely absent."""
    if isinstance(node, dict):
        for field, reason_key in REASON_REQUIRED.items():
            if field in node and node[field] is None and not node.get(reason_key):
                here = f"{path}/{field}" if path else field
                report.error(
                    "P5",
                    f"{here} is null without {reason_key}. An unknown value is recorded "
                    f"with a reason; it is never silently omitted.",
                )
        for key, value in node.items():
            check_null_reasons(value, report, f"{path}/{key}" if path else key)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            check_null_reasons(item, report, f"{path}[{index}]")


def check_annotator(document: dict, report: Report) -> None:
    """P7 — an interpretation artifact must declare who made it and what they carry."""
    annotator = document.get("annotator", {})
    if not annotator.get("conflict_of_interest"):
        report.error(
            "P7",
            "annotator.conflict_of_interest is empty. Every interpretation artifact "
            "must state the annotator's relationship to the record it annotates.",
        )


def check_identity_counts(document: dict, report: Report) -> None:
    """P8 — declared identity counts must match the segments."""
    declared = document.get("counts_by_identity")
    if not declared:
        return

    actual = Counter()
    for segment in document.get("segments", []):
        identity = segment.get("identity")
        if identity is None:
            actual["invocation integrity disputed / unattributed"] += 1
        else:
            actual[identity] += 1

    for identity, count in declared.items():
        if count == 0:
            # A deliberate zero — e.g. a model asserted as present that produced
            # nothing. Recording the absence is the point; do not treat as drift.
            if actual.get(identity, 0) != 0:
                report.error("P8", f"counts_by_identity declares 0 for {identity!r} but {actual[identity]} found")
            continue
        matched = actual.get(identity, 0)
        if matched != count:
            report.error(
                "P8",
                f"counts_by_identity[{identity!r}] = {count}, segments yield {matched}. "
                f"Counts are exact-match on the identity string; a mismatch is a factual "
                f"error in an artifact about factual accuracy.",
            )

    for identity, count in sorted(actual.items()):
        if identity not in declared:
            report.error("P8", f"identity {identity!r} appears in {count} segment(s) but is absent from counts_by_identity")


def validate_file(path: Path) -> Report:
    report = Report()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        report.error("PARSE", f"{path}: {error}")
        return report

    check_schema(document, report)
    check_source_hash(document, report)
    check_placeholders(document, report)
    check_null_reasons(document, report)

    if document.get("artifact_type") == "annotation":
        check_segments(document, report)
        check_annotator(document, report)
        check_identity_counts(document, report)
    return report


def collect_targets(argument: str) -> list[Path]:
    target = Path(argument)
    if not target.is_absolute():
        target = REPO_ROOT / target
    if target.is_dir():
        # corpus/raw/ holds RAW MATERIAL. It is anchored by corpus/MANIFEST.sha256 and is
        # never schema-validated -- raw material is whatever a party actually emitted, and
        # imposing a schema on it would be the project asserting a shape the source never had.
        return sorted(p for p in target.rglob("*.json") if "corpus/raw/" not in p.as_posix())
    return [target]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2

    targets = collect_targets(argv[1])
    if not targets:
        print(f"no JSON artifacts found under {argv[1]}")
        return 1

    failed = False
    for path in targets:
        report = validate_file(path)
        relative = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        status = "PASS" if report.ok else "FAIL"
        print(f"{status}  {relative}")
        for warning in report.warnings:
            print(f"      warn  {warning}")
        for error in report.errors:
            print(f"      error {error}")
        failed = failed or not report.ok

    print()
    print("FAILED" if failed else "All provenance checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
