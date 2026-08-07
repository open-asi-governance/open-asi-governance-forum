#!/usr/bin/env python3
"""Publish PROPOSAL COHORTS to docs/cohorts/. A cohort is not a round.

    python3 tools/build_cohort_pages.py
    python3 tools/build_cohort_pages.py --check

**DETERMINISTIC.** No LLM is in the path; this reads committed artifacts and writes pages.

Why this is a separate tool
---------------------------
`build_round_pages.py` publishes rounds. A round asks every party ONE question, drawn by
rotation from the agenda queue, and records how they answered it. A cohort asks every party to
PROPOSE a question, and nothing it produces enters the agenda.

The first design taught `load_round()` to treat a MISSING `record/cycles/<id>.json` as "this
must be a cohort". External review rejected that outright, and rightly: absence is ambiguous.
A cycle file that failed to be written, was deleted, or was never committed would then be
silently published as a cohort -- a fail-closed loader turned fail-open by inference. So a
cohort is identified by an EXPLICIT `record/cohorts/<id>.json` carrying
`artifact_type: proposal_cohort`, discovered by its own glob, and loaded by `load_cohort()`
with its own invariants.

Low-level rendering (samples, packing, variance recomputation, markdown-to-HTML) is imported
from the round publisher, because a reader should see one house style and because that code has
been beaten into shape by real material. The DOMAIN loaders stay distinct.

Separate subtree, separate pruner
---------------------------------
Pages go to `docs/cohorts/`. The round publisher's `prune()` owns `docs/rounds/` and deletes
anything there it does not expect -- so writing cohort pages into that subtree would have them
deleted on the next round build, quietly and with a green exit. This tool prunes only its own
subtree, on the same rule.

What every cohort page must say
-------------------------------
A published cohort must not be mistakable for a round that happened. Every page carries, above
the material: that no rotation cycle occurred, that no question was selected or asked, and that
nothing on the page entered the agenda. Round vocabulary -- cycle, selector, arms, spend,
previous/next round -- is not rendered here, because there is none to render.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_round_pages as b                                             # noqa: E402

COHORTS = REPO_ROOT / "record" / "cohorts"
OUT = REPO_ROOT / "docs" / "cohorts"

#  Solicitations that live beside a cohort's party specs without being a party.
NON_PARTY_SPECS = {"report"}

BANNER = (
    "> **CAPTURE-ONLY PROPOSAL COHORT — NOT A DELIBERATION ROUND.** No rotation cycle "
    "occurred. No question was selected and none was asked. Nothing on this page — no party "
    "proposal, no reporter suggestion — entered the agenda or records a decision."
)


class BuildRefusal(Exception):
    """An inconsistency that must not be published. Never a warning."""


# ---------------------------------------------------------------------------------------------
# Loading, with the cohort's own invariants
# ---------------------------------------------------------------------------------------------


def load_cohort(cohort_id: str) -> dict:
    """Load one cohort, refusing on any set inequality.

    The invariant a cohort must satisfy, which is NOT the round invariant:

        spec parties            = successful ∪ failed
        successful              = summary parties
        failed                  = rejected-record parties
        successful ∩ failed     = ∅

    A round refuses outright when a party has a spec and no summary. A cohort must not: a party
    whose every attempt failed in transport is a RECORDED TERMINAL FAILURE, and suppressing the
    other four parties over it would publish less than was collected. It is published visibly,
    with its rejection evidence, and it is not called a refusal -- the party never declined
    anything, the provider returned HTTP 400.
    """
    descriptor_path = COHORTS / f"{cohort_id}.json"
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    if descriptor.get("artifact_type") != "proposal_cohort":
        raise BuildRefusal(
            f"{cohort_id}: artifact_type is {descriptor.get('artifact_type')!r}, not "
            "'proposal_cohort'. This tool publishes cohorts and will not guess.")

    spec_dir = REPO_ROOT / "record" / "solicitations" / cohort_id
    raw_dir = REPO_ROOT / "corpus" / "raw" / cohort_id
    art_dir = REPO_ROOT / "corpus" / "artifacts" / cohort_id

    specs = {}
    for path in sorted(spec_dir.glob(f"{cohort_id}-*.json")):
        party = path.stem[len(cohort_id) + 1:]
        if party in NON_PARTY_SPECS:
            continue
        specs[party] = json.loads(path.read_text(encoding="utf-8"))
    if not specs:
        raise BuildRefusal(f"{cohort_id}: no solicitation specs; nothing to publish")

    #  Globbed independently, not looked up per spec: looking them up by spec makes an orphan
    #  unreachable by construction, so the set equality below would hold vacuously.
    summaries, samples, rejected = {}, {}, {}
    for path in sorted(art_dir.glob(f"{cohort_id}-*-summary.json")) if art_dir.exists() else []:
        key = path.stem[len(cohort_id) + 1:-len("-summary")]
        if key in NON_PARTY_SPECS:
            continue
        summaries[key] = json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(raw_dir.glob(f"{cohort_id}-*-samples.json")) if raw_dir.exists() else []:
        key = path.stem[len(cohort_id) + 1:-len("-samples")]
        if key in NON_PARTY_SPECS:
            continue
        samples[key] = json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(raw_dir.glob(f"{cohort_id}-*-rejected.json")) if raw_dir.exists() else []:
        key = path.stem[len(cohort_id) + 1:-len("-rejected")]
        rejected[key] = json.loads(path.read_text(encoding="utf-8"))

    successful, failed = set(summaries), set(rejected)
    spec_parties = set(specs)

    both = successful & failed
    if both:
        raise BuildRefusal(
            f"{cohort_id}: {sorted(both)} appear as BOTH successful and failed. A party cannot "
            "have produced a summary and have every attempt rejected.")
    unaccounted = spec_parties - successful - failed
    if unaccounted:
        raise BuildRefusal(
            f"{cohort_id}: {sorted(unaccounted)} were solicited but have neither a summary nor a "
            "rejection record. A solicited party must be accounted for either way.")
    orphan_summaries = successful - spec_parties
    if orphan_summaries:
        raise BuildRefusal(
            f"{cohort_id}: {sorted(orphan_summaries)} have summaries but no solicitation spec.")
    orphan_rejections = failed - spec_parties
    if orphan_rejections:
        raise BuildRefusal(
            f"{cohort_id}: {sorted(orphan_rejections)} have rejection records but no spec.")
    missing_raw = successful - set(samples)
    if missing_raw:
        raise BuildRefusal(
            f"{cohort_id}: {sorted(missing_raw)} have summaries with no raw samples behind them.")

    #  A rejection record must account for every attempt that was paid for. A file saying
    #  "5 requested" and listing two is a record with three attempts missing from it.
    for party, record in rejected.items():
        listed = len(record.get("rejected") or [])
        requested = record.get("k_requested")
        if requested is not None and listed != requested:
            raise BuildRefusal(
                f"{cohort_id}: {party}'s rejection record lists {listed} attempts but "
                f"{requested} were requested. Every attempt must be accounted for.")

    return {"cohort": cohort_id, "descriptor": descriptor, "specs": specs,
            "summaries": summaries, "samples": samples, "rejected": rejected,
            "successful": sorted(successful), "failed": sorted(failed)}


# ---------------------------------------------------------------------------------------------
# The pages
# ---------------------------------------------------------------------------------------------


def write_pair(slug: str, title: str, markdown: str) -> None:
    """Write into THIS tool's subtree. Deliberately not the round publisher's write_pair."""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.md").write_text(markdown, encoding="utf-8")
    (OUT / f"{slug}.html").write_text(
        b.md_to_html(markdown, title, alternate=f"{slug}.md"), encoding="utf-8")


def party_pages(data: dict, party: str) -> list[str]:
    """One party's proposals, verbatim, packed under the ceiling. Returns the slugs written."""
    cohort_id = data["cohort"]
    spec = data["specs"][party]
    summary = data["summaries"].get(party, {})
    raw = data["samples"].get(party, {})
    contributor = summary.get("contributor") or {}

    items = b.accepted_samples(raw)
    blocks = [b.render_sample(item, artifact_stem=f"{cohort_id}-{party}") for item in items]
    blocks += b.divergence_section(items, summary.get("variance") or {})

    header = "\n".join([
        f"# {cohort_id} — {party}", "",
        b.nav(("all rounds", "../rounds/index.md"), ("this cohort", f"{cohort_id}.md"),
              ("prompts", f"{cohort_id}-prompts.md")), "",
        BANNER, "",
        f"**Identity.** {contributor.get('identity') or spec.get('identity','(not recorded)')}",
        "",
        f"**Reached via.** {spec.get('reached_via') or contributor.get('provider') or '(not recorded)'}",
        "",
        f"**Sampling.** {json.dumps(contributor.get('sampling_parameters') or {}, ensure_ascii=False)}",
        "",
        f"**k requested {summary.get('k_requested','?')}, collected "
        f"{summary.get('k_collected','?')}** — {summary.get('citability','(not recorded)')}",
        "",
        f"**Exact prompt this party received:** "
        f"[{cohort_id}-{party}.txt](../artifacts/prompts/{cohort_id}-{party}.txt) "
        f"(sha256 `{spec.get('prompt_sha256','?')}`)",
        "",
        "These are questions this party PROPOSED, from sampled invocations. They are not that "
        "model's stable position, they are not answers to anything, and no rotation selected "
        "them.", "",
    ])
    footer = "\n" + b.nav(("all rounds", "../rounds/index.md"),
                          ("this cohort", f"{cohort_id}.md"))

    pages = b.pack(blocks, header, footer)
    slugs = []
    for i, body in enumerate(pages, 1):
        slug = f"{cohort_id}-{party}" + (f"-{i}" if len(pages) > 1 else "")
        part = f"  (part {i} of {len(pages)})" if len(pages) > 1 else ""
        more = ""
        if len(pages) > 1:
            links = [(f"part {j}", f"{cohort_id}-{party}-{j}.md")
                     for j in range(1, len(pages) + 1)]
            more = "\n" + b.nav(*links) + "\n"
        write_pair(slug, f"{cohort_id} — {party}{part}",
                   header.replace(f"# {cohort_id} — {party}",
                                  f"# {cohort_id} — {party}{part}") + more + body + footer)
        slugs.append(slug)
    return slugs


def failure_page(data: dict, party: str) -> str:
    """A party whose every attempt was rejected. Published, with the evidence, not summarised."""
    cohort_id = data["cohort"]
    record = data["rejected"][party]
    spec = data["specs"][party]
    attempts = record.get("rejected") or []

    lines = [f"# {cohort_id} — {party} — 0 of {record.get('k_requested','?')} collected", "",
             b.nav(("all rounds", "../rounds/index.md"), ("this cohort", f"{cohort_id}.md")), "",
             BANNER, "",
             f"**Identity.** {spec.get('identity','(not recorded)')}", "",
             "**Every attempt was rejected.** This is a recorded terminal solicitation failure, "
             "not a refusal: the party never declined anything. Where a fetch receipt is present "
             "below, the tool call SUCCEEDED and the provider rejected the follow-up request "
             "that carried the tool result.", "",
             f"**Exact prompt this party received:** "
             f"[{cohort_id}-{party}.txt](../artifacts/prompts/{cohort_id}-{party}.txt) "
             f"(sha256 `{spec.get('prompt_sha256','?')}`)", "",
             f"## The {len(attempts)} attempts", ""]
    for attempt in attempts:
        lines += [f"### Attempt {attempt.get('sample_index','?')} — "
                  f"`{attempt.get('category','?')}`", "",
                  f"- captured `{attempt.get('captured_utc','?')}`",
                  f"- reason: `{attempt.get('reason','?')}`",
                  f"- fetches made before the failure: "
                  f"{len(attempt.get('fetch_receipts') or [])}", ""]
    lines += ["", b.nav(("all rounds", "../rounds/index.md"),
                        ("this cohort", f"{cohort_id}.md"))]
    slug = f"{cohort_id}-{party}"
    write_pair(slug, f"{cohort_id} — {party} — every attempt rejected", "\n".join(lines))
    return slug


def prompts_page(data: dict) -> str:
    cohort_id, specs = data["cohort"], data["specs"]
    varying = b.varying_slots(specs)
    lines = [f"# {cohort_id} — the prompts", "",
             b.nav(("all rounds", "../rounds/index.md"), ("this cohort", f"{cohort_id}.md")), "",
             BANNER, "",
             "Every party's exact prompt, in full, as a plain-text artifact.", "",
             "| party | bytes | sha256 | exact prompt |", "|---|---|---|---|"]
    for party, spec in sorted(specs.items()):
        lines.append(f"| {party} | {len(spec['prompt'])} | `{spec.get('prompt_sha256','?')[:16]}…` "
                     f"| [.txt](../artifacts/prompts/{cohort_id}-{party}.txt) |")
    lines += ["", "## Which sections actually differ", "",
              "Computed by comparing the prompts, not taken from the template's claim about "
              "itself.", ""]
    if varying:
        for name in varying:
            lines.append(f"- `{name}`")
        lines += ["", "Every other section is byte-identical across the parties."]
    else:
        lines.append("No section differs: every party received byte-identical text.")
    lines += ["", b.nav(("all rounds", "../rounds/index.md"),
                        ("this cohort", f"{cohort_id}.md"))]
    write_pair(f"{cohort_id}-prompts", f"{cohort_id} — the prompts", "\n".join(lines))

    b.PROMPTS.mkdir(parents=True, exist_ok=True)
    for party, spec in specs.items():
        (b.PROMPTS / f"{cohort_id}-{party}.txt").write_text(spec["prompt"], encoding="utf-8")
    return f"{cohort_id}-prompts"


def report_pages(data: dict) -> list[str]:
    """The external reporter's reading. Reuses the round publisher's renderer verbatim."""
    cohort_id = data["cohort"]
    raw_path = REPO_ROOT / "corpus" / "raw" / cohort_id / f"{cohort_id}-report-samples.json"
    if not raw_path.exists():
        return []
    return b.report_pages({"round": cohort_id, "cycle": data["descriptor"]},
                          writer=write_pair, index_href="../rounds/index.md", kind="cohort")


def cohort_page(data: dict, party_slugs: dict[str, list[str]], report_slugs: list[str]) -> None:
    cohort_id, descriptor = data["cohort"], data["descriptor"]
    lines = [f"# {cohort_id} — a proposal cohort", "",
             b.nav(("all rounds", "../rounds/index.md")), "",
             BANNER, "",
             descriptor.get("what_this_is", ""), "",
             "## What this is not", "",
             f"- **No rotation cycle occurred.** {descriptor.get('why_there_is_no_cycle','')}",
             f"- **Nothing here enters the agenda.** "
             f"{descriptor.get('how_a_proposal_could_enter_the_agenda','')}",
             "- **These are sampled invocations, not stable positions.** Each party was sampled "
             f"{descriptor.get('k_requested','?')} times and every sample is published.", "",
             "## The parties", "",
             "| party | outcome | material |", "|---|---|---|"]
    for party in sorted(data["specs"]):
        if party in data["summaries"]:
            summary = data["summaries"][party]
            outcome = (f"{summary.get('k_collected','?')}/"
                       f"{summary.get('k_requested','?')} collected")
            links = " · ".join(f"[{s}]({s}.md)" for s in party_slugs.get(party, []))
        else:
            record = data["rejected"][party]
            outcome = (f"0/{record.get('k_requested','?')} — every attempt rejected "
                       "(transport failure, not a refusal)")
            links = f"[{cohort_id}-{party}]({cohort_id}-{party}.md)"
        lines.append(f"| `{party}` | {outcome} | {links} |")

    lines += ["", f"[The exact prompts]({cohort_id}-prompts.md)", ""]

    if report_slugs:
        report = descriptor.get("report") or {}
        lines += ["## An independent reading", "",
                  f"`{report.get('reporter','?')}` was solicited separately to report on this "
                  "cohort. It is **not a party** to it and did not propose anything. Its reading "
                  "is published unedited, beside the material it was written from.", "",
                  "Its *candidate follow-up questions* are that reporter's own suggestions. They "
                  "are **not party proposals**, no rotation governs them, and they have exactly "
                  "the same standing as everything else on this page: none.", ""]
        lines += [f"- [{s}]({s}.md)" for s in report_slugs]
        lines.append("")

    lines += ["", b.nav(("all rounds", "../rounds/index.md"))]
    write_pair(cohort_id, f"{cohort_id} — a proposal cohort", "\n".join(lines))


def index_page(cohorts: list[dict]) -> None:
    lines = ["# Proposal cohorts", "",
             b.nav(("all rounds", "../rounds/index.md")), "",
             "A **cohort is not a round.** A round asks every party one question, drawn by "
             "rotation from the agenda, and records how they answered. A cohort asks every party "
             "to *propose* a question. Nothing a cohort produces enters the agenda, and no "
             "mechanism to admit it has been written.", ""]
    for data in cohorts:
        descriptor = data["descriptor"]
        n_ok, n_bad = len(data["successful"]), len(data["failed"])
        lines += [f"## [{data['cohort']}]({data['cohort']}.md)", "",
                  f"Captured {descriptor.get('captured_utc','?')} · "
                  f"{len(data['specs'])} parties solicited · {n_ok} produced samples · "
                  f"{n_bad} had every attempt rejected", "",
                  descriptor.get("what_this_is", ""), ""]
    lines += ["", b.nav(("all rounds", "../rounds/index.md"))]
    write_pair("index", "Proposal cohorts", "\n".join(lines))


def prune(expected: set[str]) -> list[str]:
    """Remove files this generator no longer produces. Owns ONLY docs/cohorts/."""
    removed = []
    for path in sorted(OUT.glob("*")) if OUT.exists() else []:
        if path.is_file() and path.stem not in expected:
            path.unlink()
            removed.append(path.name)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = parser.parse_args()

    ids = sorted(p.stem for p in COHORTS.glob("*.json")) if COHORTS.exists() else []
    if not ids:
        print("no cohorts in record/cohorts/; nothing to publish")
        return 0

    loaded = []
    for cohort_id in ids:
        try:
            loaded.append(load_cohort(cohort_id))
        except BuildRefusal as refusal:
            print(f"REFUSED: {refusal}", file=sys.stderr)
            return 1

    for data in loaded:
        #  check_variance RAISES on a mismatch rather than returning one. Recomputes every
        #  distribution from the raw samples and refuses if the summary disagrees -- the reason
        #  "computed, never asserted" is a claim these pages can support.
        try:
            b.check_variance({"round": data["cohort"], "summaries": data["summaries"],
                              "samples": data["samples"]})
        except b.BuildRefusal as refusal:
            print(f"REFUSED: {refusal}", file=sys.stderr)
            return 1

    if args.check:
        print(f"checked {len(loaded)} cohort(s); wrote nothing")
        return 0

    expected = {"index"}
    for data in loaded:
        party_slugs = {}
        for party in sorted(data["specs"]):
            if party in data["summaries"]:
                party_slugs[party] = party_pages(data, party)
                expected.update(party_slugs[party])
            else:
                expected.add(failure_page(data, party))
        expected.add(prompts_page(data))
        report_slugs = report_pages(data)
        expected.update(report_slugs)
        cohort_page(data, party_slugs, report_slugs)
        expected.add(data["cohort"])
    index_page(loaded)

    removed = prune(expected)
    print(f"published {len(loaded)} cohort(s) to docs/cohorts/ "
          f"({len(list(OUT.glob('*.md')))} markdown pages)")
    if removed:
        print(f"  pruned {len(removed)} stale file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
