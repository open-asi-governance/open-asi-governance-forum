#!/usr/bin/env python3
"""Render a segment annotation file to a navigable Markdown index.

Structured data lives in JSON; narrative lives in Markdown. This program is the
one-way bridge between them. It never edits JSON and never writes anything a
reader could mistake for testimony -- every rendered page states that it is
generated, that it is annotation, and that the raw file is canonical.

Usage:
    python3 tools/render_markdown.py corpus/artifacts/segments.json corpus/index.md

Deterministic: same input, same bytes out.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STATUS_MARK = {
    "repudiated": " **[REPUDIATED]**",
    "invocation integrity disputed": " **[INTEGRITY DISPUTED]**",
    "superseded": " **[SUPERSEDED]**",
    "withdrawn": " **[WITHDRAWN]**",
}


def escape_cell(text: str) -> str:
    """Make a string safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def render_header(document: dict) -> list[str]:
    source = document.get("source", {})
    annotator = document.get("annotator", {})
    defaults = document.get("provenance_defaults", {})

    return [
        "# Corpus Index — Founding Record",
        "",
        "> **Generated file.** Produced by `tools/render_markdown.py` from",
        f"> `corpus/artifacts/segments.json`. Do not edit by hand; edit the JSON and re-render.",
        "",
        "> **This is annotation, not testimony.** The canonical record is the raw file below,",
        "> committed byte-identical and never edited. Everything on this page is one annotator's",
        "> reading of it, and carries the conflict of interest stated below.",
        "",
        "| | |",
        "|---|---|",
        f"| Source | `{source.get('path', '?')}` |",
        f"| SHA-256 | `{source.get('sha256', '?')}` |",
        f"| Lines | {source.get('lines', '?')} |",
        f"| Segments | {document.get('segment_count', len(document.get('segments', [])))} |",
        f"| Annotator | {escape_cell(annotator.get('identity', '?'))} ({escape_cell(annotator.get('provider', '?'))}) |",
        f"| Annotated | {annotator.get('date_utc', '?')} |",
        f"| Status | **{document.get('status', '?')}** |",
        "",
        "**Annotator conflict of interest:** "
        + annotator.get("conflict_of_interest", "*not declared*"),
        "",
        "**Provenance baseline for every contribution in this record:** "
        f"k = {defaults.get('k', '?')}, "
        f"variance reported: {str(defaults.get('variance_reported', '?')).lower()}, "
        f"model version: {defaults.get('version_identifier') or 'unrecorded'}, "
        f"sampling parameters: {defaults.get('sampling_parameters') or 'unrecorded'}. "
        "See [`deficiencies.md`](deficiencies.md) before citing anything here.",
        "",
        "---",
        "",
    ]


def render_contents(segments: list[dict]) -> list[str]:
    lines = ["## Contents", "", "| # | Lines | Identity | Role | Summary |", "|---|---|---|---|---|"]
    for segment in segments:
        start, end = segment.get("lines", ["?", "?"])
        identity = segment.get("identity") or "*unattributed*"
        status = segment.get("attribution_status", "")
        mark = STATUS_MARK.get(status, "")
        role = segment.get("role") or "—"
        summary = escape_cell(segment.get("summary", ""))
        if len(summary) > 110:
            summary = summary[:107].rstrip() + "…"
        anchor = segment.get("id", "").lower()
        lines.append(
            f"| [{segment.get('id')}](#{anchor}) | {start}–{end} | "
            f"{escape_cell(identity)}{mark} | {escape_cell(role)} | {summary} |"
        )
    lines.extend(["", "---", ""])
    return lines


def render_segment(segment: dict) -> list[str]:
    start, end = segment.get("lines", ["?", "?"])
    identity = segment.get("identity") or "*unattributed*"
    status = segment.get("attribution_status")

    lines = [
        f"### {segment.get('id')}",
        "",
        f"**Identity:** {identity}  ",
        f"**Label in raw file:** `{segment.get('author_label_in_raw', '?')}`  ",
        f"**Raw lines:** {start}–{end}  ",
    ]

    if segment.get("role"):
        lines.append(f"**Role:** {segment['role']}  ")
    if segment.get("ballot"):
        lines.append(f"**Ballot:** **{segment['ballot']}**  ")
    if status and status != "active":
        lines.append(f"**Attribution status:** **{status.upper()}**  ")
    if segment.get("identity_evidence"):
        lines.append(f"**Identity evidence:** {segment['identity_evidence']}  ")

    lines.extend(["", segment.get("summary", ""), ""])

    if segment.get("key_claims"):
        lines.append("**Key claims:**")
        lines.append("")
        lines.extend(f"- {claim}" for claim in segment["key_claims"])
        lines.append("")

    if segment.get("durable_outputs"):
        lines.append("**Durable outputs adopted by the project:**")
        lines.append("")
        lines.extend(f"- {output}" for output in segment["durable_outputs"])
        lines.append("")

    if segment.get("superseded_by"):
        lines.append("**Superseded:**")
        lines.append("")
        lines.extend(f"- {item}" for item in segment["superseded_by"])
        lines.append("")

    if segment.get("disposition"):
        lines.append("**Disposition:**")
        lines.append("")
        lines.extend(f"- `{key}` — {value}" for key, value in segment["disposition"].items())
        lines.append("")

    if segment.get("conflict_flag"):
        lines.extend([f"> ⚠ **Conflict:** {segment['conflict_flag']}", ""])

    if segment.get("claim_typing_flag"):
        lines.extend([f"> **Claim typing:** {segment['claim_typing_flag']}", ""])

    if segment.get("annotator_note"):
        lines.extend([f"> **Annotator note:** {segment['annotator_note']}", ""])

    return lines


def render_questions(document: dict) -> list[str]:
    questions = document.get("unresolved_questions", [])
    if not questions:
        return []

    lines = [
        "---",
        "",
        "## Unresolved questions",
        "",
        "Carried forward from the founding record. These are the record's outstanding work,",
        "and they are listed here so that no synthesis can quietly close them.",
        "",
    ]
    for question in questions:
        lines.extend(
            [
                f"### {question.get('id')} — raised by {question.get('raised_by')}"
                + (f" (raw line {question['raw_line']})" if question.get("raw_line") else ""),
                "",
                f"> {question.get('question', '')}",
                "",
                f"**Status:** {question.get('status', '?')}",
                "",
            ]
        )
        if question.get("note"):
            lines.extend([question["note"], ""])
    return lines


def render_ballots(document: dict) -> list[str]:
    ballots = document.get("ballots", {})
    if not ballots:
        return []

    lines = ["---", "", "## Ballots", ""]
    for name, detail in ballots.items():
        lines.append(f"### {name.replace('_', ' ').title()}")
        lines.append("")
        results = detail.get("results", {})
        if results:
            lines.extend(["| Participant | Ballot |", "|---|---|"])
            lines.extend(f"| {who} | {what} |" for who, what in results.items())
            lines.append("")
        if detail.get("shared_reservation"):
            lines.extend([f"**Shared reservation:** {detail['shared_reservation']}", ""])
        if detail.get("reservation_status"):
            lines.extend([f"**Status:** {detail['reservation_status']}", ""])
        if detail.get("epistemic_caveat"):
            lines.extend([f"> ⚠ {detail['epistemic_caveat']}", ""])
    return lines


def render(document: dict) -> str:
    segments = document.get("segments", [])
    lines: list[str] = []
    lines.extend(render_header(document))
    lines.extend(render_contents(segments))
    lines.append("## Segments")
    lines.append("")
    for segment in segments:
        lines.extend(render_segment(segment))
    lines.extend(render_ballots(document))
    lines.extend(render_questions(document))
    lines.extend(
        [
            "---",
            "",
            "*Generated by `tools/render_markdown.py`. The raw record is canonical; this page is not.*",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2

    source = Path(argv[1])
    target = Path(argv[2])
    if not source.is_absolute():
        source = REPO_ROOT / source
    if not target.is_absolute():
        target = REPO_ROOT / target

    if not source.exists():
        print(f"not found: {argv[1]}")
        return 1

    document = json.loads(source.read_text(encoding="utf-8"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(document), encoding="utf-8")

    relative = target.relative_to(REPO_ROOT) if target.is_relative_to(REPO_ROOT) else target
    print(f"wrote {relative} — {len(document.get('segments', []))} segment(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
