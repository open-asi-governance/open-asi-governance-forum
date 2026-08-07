#!/usr/bin/env python3
"""Publish the deliberation rounds. Deterministic, no model in the path.

    python3 tools/build_round_pages.py            # build
    python3 tools/build_round_pages.py --check    # verify only, write nothing

WHY THIS EXISTS, and why its absence mattered
---------------------------------------------
Nine deliberation rounds were merged and **none was published**. `docs/` carried the founding
deliberation, three review rounds and the local rounds; not one page mentioned a round id.

That is a recurrence. `tools/build_local_rounds.py` was written because all eight local rounds —
the entire measurement programme, and the source of D-23 through D-28 — were committed to the
corpus and absent from the site. Same failure, one artifact class over, after the fix had been
written for the first one.

It also compounds **D-52**. That entry records that parties given this record's address never
reached it. But a party that fetched *perfectly* would still have found no rounds here, including
the round it was being asked to participate in.

Who this is for
---------------
External readers **and the parties**. A party's only available form of verification is checking
that it was quoted correctly and asked what the page says it was asked, so this publishes the
exact prompt each party received — not a representative one — and every attempt, accepted and
rejected.

The prompt decision, which was reviewed and changed
--------------------------------------------------
The first design published one party's prompt verbatim and the other parties' SHA-256 only.
External review rejected it: *"A hash proves possession; it does not disclose content. A stateless
party cannot be expected to retain its own copy."* That is right, and it is the party audience the
shortcut failed. Every prompt is now published in full as an exact `.txt` artifact, and a build
assertion recomputes which template slots vary rather than trusting the template's claim.

The page budget is the shaping constraint
-----------------------------------------
`check_page_budget.py` gates every page at ~20,000 tokens because `qwen3.6-35b-a3b` serves this
corpus with a 24,576-token context and once could not read the project's own website. A round is
~40,000 tokens, so it must split. Sample pages are packed **after rendering**, never by assuming
sizes, and a sample is never split across pages. Exact prompts live under `docs/artifacts/`, which
is the budget's named exception for verification downloads rather than pages meant to be read in
one request.

Fail-closed, because a green build over an incomplete set is the failure this project keeps having
--------------------------------------------------------------------------------------------------
Parties are discovered from the **solicitation specs**, never from the summaries. Discovering them
from summaries would silently omit exactly the party whose solicitation failed — the one a reader
most needs to see. The build then requires set equality between specs, raw samples, summaries and
the cycle record's own party list, and refuses on any mismatch.

Variance is **recomputed from the raw accepted samples** and compared with the summary. Publishing
the summary's numbers unchecked would make "computed, never asserted" a claim this page could not
support.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
OUT = DOCS / "rounds"
PROMPTS = DOCS / "artifacts" / "prompts"
CYCLES = REPO_ROOT / "record" / "cycles"

#  Same estimator as the gate, so packing and gating cannot disagree.
BYTES_PER_TOKEN = 3.4
#  Packing is measured on the MARKDOWN, but the HTML rendered from it is what the gate sizes,
#  and escaping plus tags expanded it by up to 2.22x in practice -- pushing pages to ~16,400 of
#  20,000 on the first build. The budget here is the gate divided by that measured ratio, with
#  headroom, so the two cannot disagree.
HTML_EXPANSION = 2.4
PAGE_CEILING_TOKENS = int(20_000 / HTML_EXPANSION)     # ~8,300 markdown tokens
ROUND_ID = re.compile(r"^round-[0-9]{3}")


class BuildRefusal(Exception):
    """An inconsistency that must not be published. Never a warning."""


# ---------------------------------------------------------------------------------------------
# Loading, with the set-equality checks that make a green build mean something
# ---------------------------------------------------------------------------------------------


def load_round(round_id: str) -> dict:
    cycle = json.loads((CYCLES / f"{round_id}.json").read_text(encoding="utf-8"))
    spec_dir = REPO_ROOT / "record" / "solicitations" / round_id
    raw_dir = REPO_ROOT / "corpus" / "raw" / round_id
    art_dir = REPO_ROOT / "corpus" / "artifacts" / round_id

    #  Parties come from the SPECS. A party whose solicitation failed has a spec and no summary,
    #  and is precisely the one a reader needs to see.
    specs = {}
    for path in sorted(spec_dir.glob(f"{round_id}-*.json")):
        party = path.stem[len(round_id) + 1:]
        specs[party] = json.loads(path.read_text(encoding="utf-8"))
    if not specs:
        raise BuildRefusal(f"{round_id}: no solicitation specs; nothing to publish")

    #  Discovered INDEPENDENTLY by globbing, not looked up per known spec. Looking them up by
    #  spec made `orphans` unreachable by construction, so the "set equality" this docstring
    #  claimed did not exist -- a summary with no spec, or a summary with no raw file, passed.
    summaries, samples = {}, {}
    for path in sorted(art_dir.glob(f"{round_id}-*-summary.json")) if art_dir.exists() else []:
        summaries[path.stem[len(round_id) + 1:-len("-summary")]] = json.loads(
            path.read_text(encoding="utf-8"))
    for path in sorted(raw_dir.glob(f"{round_id}-*-samples.json")) if raw_dir.exists() else []:
        samples[path.stem[len(round_id) + 1:-len("-samples")]] = json.loads(
            path.read_text(encoding="utf-8"))

    failed = {f.get("party") if isinstance(f, dict) else f
              for f in (cycle.get("solicitation_failures") or [])}
    #  specs == succeeded ∪ failed. Anything else means an artifact is missing, orphaned, or
    #  the cycle record disagrees with the corpus -- all publishable-looking and all wrong.
    unexplained = set(specs) - set(summaries) - failed
    if unexplained:
        raise BuildRefusal(
            f"{round_id}: {sorted(unexplained)} have a solicitation spec but no summary and are "
            f"not recorded as a solicitation failure. Either the round is mid-flight or an "
            f"artifact is missing; publishing would show a round with a party silently absent.")
    orphans = set(summaries) - set(specs)
    if orphans:
        raise BuildRefusal(f"{round_id}: {sorted(orphans)} have a summary with no solicitation "
                           f"spec — an answer with no recorded question.")
    #  `parties` is a list of per-party result objects, not names. Reading it as names once
    #  raised TypeError; taking party_key is the shape the round loop actually writes.
    #  A summary asserting collected samples with no raw file is an answer with no evidence.
    missing_raw = {p for p, sm in summaries.items()
                   if (sm.get("k_collected") or 0) > 0 and p not in samples}
    if missing_raw:
        raise BuildRefusal(f"{round_id}: {sorted(missing_raw)} have a summary claiming collected "
                           f"samples with no raw samples file. The party page would be empty "
                           f"while the round table called it citable.")
    raw_orphans = set(samples) - set(specs)
    if raw_orphans:
        raise BuildRefusal(f"{round_id}: raw samples for {sorted(raw_orphans)} with no "
                           f"solicitation spec.")
    recorded = {p.get("party_key") for p in (cycle.get("parties") or [])
                if isinstance(p, dict) and p.get("party_key")}
    if recorded and recorded != set(specs):
        raise BuildRefusal(f"{round_id}: cycle record lists {sorted(recorded)} but the "
                           f"solicitations are {sorted(specs)}.")
    #  A halted round must not render as an ordinary completed one. The halt is a recorded
    #  OUTCOME, not an error, and hiding it would make a round that stopped look like a round
    #  that finished.
    halts = []
    for path in sorted(CYCLES.glob("halt-*.json")):
        h = json.loads(path.read_text(encoding="utf-8"))
        if h.get("round") == round_id:
            halts.append(h)
    undersampled = sorted(p for p, sm in summaries.items()
                          if (sm.get("k_collected") or 0) < (sm.get("k_requested") or 0))
    return {"round": round_id, "cycle": cycle, "specs": specs, "summaries": summaries,
            "samples": samples, "failed": failed, "halts": halts,
            "undersampled": undersampled}


def accepted_samples(raw: dict) -> list[dict]:
    """Every accepted sample, whichever arm's tool wrote the file.

    solicit_api and solicit_local disagree on the key (`samples` vs `responses`), and the
    tool-using arm adds a third shape. Guessing one would silently publish an empty round.
    """
    for key in ("samples", "responses"):
        if isinstance(raw.get(key), list) and raw[key]:
            items = raw[key]
            break
    else:
        return []
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("ok") is False:
            continue
        out.append(item)
    return out


#  Keys that carry the party's ANSWER. Everything else in a sample record is metadata and is
#  rendered too -- nothing is dropped, because "every attempt, verbatim" was claimed while the
#  first recognised field won and the rest vanished, taking raw_text, usage and web_citations
#  with it.
ANSWER_KEYS = ("parsed", "response", "content")


def sample_payload(item: dict) -> dict:
    """The party's answer fields. Metadata is NOT discarded; see render_sample."""
    for key in ANSWER_KEYS:
        value = item.get(key)
        if isinstance(value, dict) and value:
            return value
        if isinstance(value, str) and value.strip():
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:                                             # noqa: BLE001
                pass
            return {"answer": value}
    return {}


def fence(text: str) -> str:
    """Wrap text in a fence longer than any backtick run inside it.

    A party answer containing its own ``` closes the wrapper, after which its text becomes page
    structure -- headings, tables and links rendered from testimony. Escaping is not enough
    because the markdown alternate is published too.
    """
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    bar = "`" * max(3, longest + 1)
    return f"{bar}\n{text}\n{bar}"


def render_sample(item: dict) -> str:
    """One whole sample as ONE block: answer fields, then every remaining field."""
    payload = sample_payload(item)
    idx = item.get("sample_index", "?")
    out = [f"\n### Sample {idx}\n"]
    for key, value in payload.items():
        out.append(f"**{key}**\n")
        out.append(fence(value if isinstance(value, str)
                         else json.dumps(value, indent=1, ensure_ascii=False)) + "\n")
    rest = {k: v for k, v in item.items() if k not in ANSWER_KEYS}
    if rest:
        out.append("<details><summary>Everything else recorded for this sample</summary>\n")
        out.append(fence(json.dumps(rest, indent=1, ensure_ascii=False)) + "\n")
        out.append("</details>\n")
    return "\n".join(out)


def recompute_variance(payloads: list[dict], fields: list[str]) -> dict:
    from collections import Counter
    report = {}
    for field in fields:
        values = [json.dumps(p.get(field), sort_keys=True) if isinstance(p.get(field), (dict, list))
                  else p.get(field) for p in payloads]
        counts = Counter(values)
        modal, modal_n = counts.most_common(1)[0] if counts else (None, 0)
        report[field] = {"distribution": {str(k): v for k, v in counts.most_common()},
                         "n": len(values), "distinct_values": len(counts), "modal_value": modal,
                         "modal_fraction": round(modal_n / len(values), 4) if values else 0.0}
    return report


def check_variance(data: dict) -> list[str]:
    """Recompute variance from raw and compare with the summary. Differences are refusals."""
    notes = []
    for party, summary in data["summaries"].items():
        raw = data["samples"].get(party)
        if not raw:
            continue
        fields = list((summary.get("variance") or {}).keys())
        if not fields:
            continue
        payloads = [sample_payload(s) for s in accepted_samples(raw)]
        if not payloads:
            continue
        mine = recompute_variance(payloads, fields)
        for field in fields:
            theirs = summary["variance"][field]
            if mine[field]["modal_value"] != theirs.get("modal_value"):
                raise BuildRefusal(
                    f"{data['round']}/{party}: recomputing variance for {field!r} from the raw "
                    f"samples gives modal {mine[field]['modal_value']!r}, the summary says "
                    f"{theirs.get('modal_value')!r}. One of them is wrong and neither may be "
                    f"published as computed.")
            for key in ("n", "distinct_values"):
                if mine[field][key] != theirs.get(key):
                    raise BuildRefusal(
                        f"{data['round']}/{party}: recomputed {key} for {field!r} is "
                        f"{mine[field][key]}, the summary says {theirs.get(key)}. An `n` "
                        f"mismatch used to be collected into notes the caller discarded, which "
                        f"made 'computed, never asserted' a claim this page could not support.")
            if mine[field]["distribution"] != theirs.get("distribution"):
                raise BuildRefusal(
                    f"{data['round']}/{party}: recomputed distribution for {field!r} differs "
                    f"from the summary's.")
        if len(payloads) != (summary.get("k_collected") or 0):
            raise BuildRefusal(
                f"{data['round']}/{party}: {len(payloads)} accepted samples in the raw file but "
                f"the summary reports k_collected={summary.get('k_collected')}.")
    return notes


def varying_slots(specs: dict) -> list[str]:
    """Which template slots actually differ between parties — computed, not taken on trust.

    The template asserts that prompts are identical modulo two declared slots. This checks it.
    """
    slot = re.compile(r"<!-- SLOT: ([a-z_]+) -->")
    per_party = {}
    for party, spec in specs.items():
        text = spec["prompt"]
        marks = [(m.group(1), m.start()) for m in slot.finditer(text)]
        sections = {}
        for i, (name, start) in enumerate(marks):
            end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
            sections[name] = text[start:end]
        per_party[party] = sections
    names = sorted({n for s in per_party.values() for n in s})
    varying = [n for n in names if len({s.get(n) for s in per_party.values()}) > 1]
    #  Text BEFORE the first marker belongs to no section and was never compared, so a differing
    #  preamble -- or a prompt with no markers at all -- reported "byte-identical".
    preambles = {p: t["prompt"][:t["prompt"].find("<!-- SLOT:")] if "<!-- SLOT:" in t["prompt"]
                 else t["prompt"] for p, t in specs.items()}
    if len(set(preambles.values())) > 1:
        varying.append("(text before the first slot marker)")
    covered = {p: sum(len(v) for v in sections.values()) + len(preambles[p])
               for p, sections in per_party.items()}
    for party, spec in specs.items():
        if covered[party] != len(spec["prompt"]):
            varying.append(f"(unaccounted bytes in {party}'s prompt — comparison incomplete)")
            break
    return varying


# ---------------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------------

STYLE = """<style>
body{max-width:46rem;margin:2rem auto;padding:0 1rem;font:16px/1.6 system-ui,sans-serif;color:#111}
code,pre{background:#f4f4f4}pre{padding:.75rem;overflow-x:auto;white-space:pre-wrap}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.35rem .5rem;
text-align:left;font-size:.92em}nav{font-size:.9em;margin-bottom:1.5rem}
blockquote{border-left:3px solid #ccc;margin:0;padding-left:1rem;color:#333}
@media(prefers-color-scheme:dark){body{background:#111;color:#eee}code,pre{background:#1e1e1e}
td,th{border-color:#444}blockquote{border-color:#555;color:#ccc}a{color:#7ab7ff}}
</style>"""


def md_to_html(markdown: str, title: str, alternate: str | None = None) -> str:
    """Deliberately small: headings, tables, code fences, blockquotes, links, emphasis.

    Sibling `.md` links are rewritten to `.html`, because the same markdown source produces both
    renderings and an HTML page linking to markdown produced 19 broken links on first build.
    External and artifact links are left alone.
    """
    markdown = re.sub(r"\]\((?!https?:|\.\./artifacts/)([A-Za-z0-9._-]+)\.md\)",
                      r"](\1.html)", markdown)
    out, in_code, in_table = [], False, False
    for line in markdown.splitlines():
        if line.startswith("```"):
            out.append("</pre>" if in_code else "<pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        if line.startswith("|") and set(line.replace("|", "").strip()) <= set("-: "):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            tag = "th" if not in_table else "td"
            if not in_table:
                out.append("<table>")
                in_table = True
            out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            out.append(f"<h{level}>{inline(line.lstrip('# '))}</h{level}>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.startswith("- "):
            out.append(f"<li>{inline(line[2:])}</li>")
        elif not line.strip():
            out.append("")
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_table:
        out.append("</table>")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            + (f'<link rel="alternate" type="text/markdown" href="{alternate}">'
               if alternate else "")
            + f"<title>{html.escape(title)}</title>{STYLE}</head><body>"
            + "\n".join(out) + "</body></html>\n")


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    #  Only http(s) and same-origin relative targets. `javascript:` was permitted, and party
    #  testimony is rendered through this.
    def link(m):
        label, href = m.group(1), m.group(2)
        if re.match(r"(?i)^(https?://|[A-Za-z0-9._~/-]+(\.(html|md|txt|json))?(#|$))", href):
            return f'<a href="{href}">{label}</a>'
        return f"{label} ({html.escape(href)})"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    return text


def nav(*links: tuple[str, str]) -> str:
    return " · ".join(f"[{t}]({h})" for t, h in links)


def write_pair(slug: str, title: str, markdown: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.md").write_text(markdown, encoding="utf-8")
    (OUT / f"{slug}.html").write_text(
        md_to_html(markdown, title, alternate=f"{slug}.md"), encoding="utf-8")


def pack(blocks: list[str], header: str, footer: str) -> list[str]:
    """Pack rendered blocks into pages under the ceiling. Never splits a BLOCK.

    Each block must be one whole sample. An earlier version appended a sample's heading,
    metadata and every field as SEPARATE blocks, so a sample could split mid-answer while this
    docstring claimed it could not.

    Sizes are encoded byte lengths, matching the gate's estimator; `len(str)` undercounts every
    non-ASCII character and the gate exists precisely so a party can load the page.
    """
    ceiling = PAGE_CEILING_TOKENS * BYTES_PER_TOKEN
    size_of = lambda t: len(t.encode("utf-8"))                            # noqa: E731
    pages, current = [], []
    base = size_of(header) + size_of(footer)
    size = base
    for block in blocks:
        if current and size + size_of(block) > ceiling:
            pages.append(current)
            current, size = [], base
        current.append(block)
        size += size_of(block)
    if current:
        pages.append(current)
    return ["\n".join(p) for p in pages] or [""]


# ---------------------------------------------------------------------------------------------
# The pages
# ---------------------------------------------------------------------------------------------


DIFF_MAX_LINES = 120


def answer_text(item: dict) -> str:
    """The longest text field in a sample — what a reader means by "the answer"."""
    payload = sample_payload(item)
    texts = [v for v in payload.values() if isinstance(v, str)]
    return max(texts, key=len) if texts else ""


def diff_lines(text: str) -> list[str]:
    """Split into sentences for diffing. Display only — the recorded text is never altered.

    Answers arrive as single long paragraphs, so a line diff reports one deletion and one
    insertion of the whole thing, which shows that samples differ while hiding WHERE. Splitting
    on sentence boundaries first is what makes the diff show changes rather than replacement.
    """
    out = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        out.extend(s.strip() for s in re.split(r"(?<=[.!?;])\s+", para) if s.strip())
    return out


def divergence_section(items: list[dict], variance: dict) -> list[str]:
    """Show WHERE the samples differ, not merely that a categorical field has entropy.

    The variance table can report `modal=X (100%)` while five answers argue incompatibly — the
    label is a shape, not a position, and this record has already measured a party holding two
    incompatible positions under one label. So one sample is taken as the reference and the rest
    are diffed against it.

    The reference is the FIRST sample carrying the modal value of the first variance field, and
    which one it is, is stated. It is not a canonical answer and no sample is privileged by it:
    a temperature-0 draw was considered for this role and rejected, because mixing a second
    temperature into a k>=5 set is D-26 exactly -- treating temperature as fixed when it
    controls the quantity being measured -- and because the router exposes no seed, so a
    temperature-0 routed draw would not be reproducible either.
    """
    if len(items) < 2:
        return []
    field = next(iter(variance), None)
    modal = (variance.get(field) or {}).get("modal_value") if field else None
    ref = next((i for i in items if field and sample_payload(i).get(field) == modal), items[0])
    ref_text = answer_text(ref)
    if not ref_text:
        return []

    out = ["\n## How the samples differ\n"
           + f"Reference: **sample {ref.get('sample_index','?')}**"
           + (f", the first carrying the modal `{field}` = `{modal}`." if modal is not None
              else ", the first collected.") + "\n\n"
           + "Every other sample is shown as a unified diff against it. This is a display aid; "
             "the samples are equals and the reference is not a canonical answer.\n"]
    for item in items:
        if item is ref:
            continue
        text = answer_text(item)
        diff = list(difflib.unified_diff(
            diff_lines(ref_text), diff_lines(text),
            fromfile=f"sample {ref.get('sample_index','?')}",
            tofile=f"sample {item.get('sample_index','?')}", lineterm="", n=1))
        head = f"\n### Sample {item.get('sample_index','?')} vs reference\n"
        if not diff:
            out.append(head + "\nByte-identical to the reference.\n")
            continue
        shown, truncated = diff[:DIFF_MAX_LINES], len(diff) > DIFF_MAX_LINES
        body = head + "\n" + fence("\n".join(shown)) + "\n"
        if truncated:
            body += (f"\n*Diff truncated at {DIFF_MAX_LINES} of {len(diff)} lines. The full "
                     f"samples are above and in the linked raw artifact; nothing is omitted "
                     f"from those.*\n")
        out.append(body)
    return out


def party_pages(data: dict, party: str) -> list[str]:
    """One party's attempts, verbatim, packed under the ceiling. Returns the slugs written."""
    round_id = data["round"]
    spec, summary = data["specs"][party], data["summaries"].get(party, {})
    raw = data["samples"].get(party, {})
    contributor = summary.get("contributor") or {}

    items = accepted_samples(raw)
    #  ONE block per sample, so packing can never split one. The divergence section returns a
    #  LIST of blocks (intro, then one per diff) rather than one joined string -- joining it made
    #  a single unsplittable block that pushed a page to 16,396 of a 20,000 ceiling.
    blocks = [render_sample(item) for item in items]
    blocks += divergence_section(items, summary.get("variance") or {})

    rejected = summary.get("failures") or summary.get("rejected") or []
    if rejected:
        blocks.append("\n### Rejected attempts\n")
        blocks.append("A round with rejected attempts is a different round from one without, so "
                      "they are published rather than counted.\n")
        for r in rejected:
            #  Tools disagree on this shape: solicit_api writes dicts, older runs wrote strings.
            #  Assuming dict raised AttributeError on real committed material.
            if isinstance(r, dict):
                #  The whole record, not a 300-character excerpt. One round's rejected reply was
                #  46,603 bytes and was being published as 300 of them, dropping the finish
                #  reason and usage that distinguish "the model stopped" from "we cut it off" --
                #  truncation has twice masqueraded as a refusal in this record.
                blocks.append(f"\n#### Rejected sample {r.get('sample_index','?')} — "
                              f"`{r.get('category','?')}`\n")
                blocks.append(fence(json.dumps(r, indent=1, ensure_ascii=False)) + "\n")
            else:
                blocks.append("\n" + fence(str(r)) + "\n")

    header = "\n".join([
        f"# {round_id} — {party}", "",
        nav(("all rounds", "index.md"), ("this round", f"{round_id}.md"),
            ("prompts", f"{round_id}-prompts.md")), "",
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
        f"[{round_id}-{party}.txt](../artifacts/prompts/{round_id}-{party}.txt) "
        f"(sha256 `{spec.get('prompt_sha256','?')}`)",
        "",
        "These are outputs attributed to sampled invocations of this party. They are not that "
        "model's stable position, and nothing here pools them with any other party.", "",
    ])
    footer = "\n" + nav(("all rounds", "index.md"), ("this round", f"{round_id}.md"))

    pages = pack(blocks, header, footer)
    slugs = []
    for i, body in enumerate(pages, 1):
        slug = f"{round_id}-{party}" + (f"-{i}" if len(pages) > 1 else "")
        part = f"  (part {i} of {len(pages)})" if len(pages) > 1 else ""
        more = ""
        if len(pages) > 1:
            links = [(f"part {j}", f"{round_id}-{party}-{j}.md") for j in range(1, len(pages) + 1)]
            more = "\n" + nav(*links) + "\n"
        write_pair(slug, f"{round_id} — {party}{part}",
                   header.replace(f"# {round_id} — {party}",
                                  f"# {round_id} — {party}{part}") + more + body + footer)
        slugs.append(slug)
    return slugs


def prompts_page(data: dict) -> None:
    round_id, specs = data["round"], data["specs"]
    varying = varying_slots(specs)
    lines = [f"# {round_id} — the prompts", "",
             nav(("all rounds", "index.md"), ("this round", f"{round_id}.md")), "",
             "Every party's exact prompt is published in full below as a plain-text artifact. An "
             "earlier design published one prompt and the others' hashes; that was rejected in "
             "review, because a hash proves possession without disclosing content and a stateless "
             "party cannot be expected to hold its own copy.", "",
             "| party | bytes | sha256 | exact prompt |", "|---|---|---|---|"]
    for party, spec in sorted(specs.items()):
        lines.append(f"| {party} | {len(spec['prompt'])} | `{spec.get('prompt_sha256','?')[:16]}…` "
                     f"| [.txt](../artifacts/prompts/{round_id}-{party}.txt) |")
    lines += ["", "## Which sections actually differ", "",
              "Computed by comparing the prompts, not taken from the template's claim about "
              "itself.", ""]
    if varying:
        for name in varying:
            lines.append(f"- `{name}`")
        lines.append("")
        lines.append("Every other section is byte-identical across the parties in this round.")
    else:
        lines.append("No section differs: every party received byte-identical text.")
    lines += ["", nav(("all rounds", "index.md"), ("this round", f"{round_id}.md"))]
    write_pair(f"{round_id}-prompts", f"{round_id} — the prompts", "\n".join(lines))

    PROMPTS.mkdir(parents=True, exist_ok=True)
    for party, spec in specs.items():
        (PROMPTS / f"{round_id}-{party}.txt").write_text(spec["prompt"], encoding="utf-8")


def round_page(data: dict, party_slugs: dict[str, list[str]], neighbours: tuple) -> None:
    round_id, cycle = data["round"], data["cycle"]
    selected = cycle.get("selected") or {}
    prev_id, next_id = neighbours
    links = [("all rounds", "index.md")]
    if prev_id:
        links.append(("previous", f"{prev_id}.md"))
    if next_id:
        links.append(("next", f"{next_id}.md"))

    lines = [f"# {round_id}", "", nav(*links), "",
             f"Cycle {cycle.get('cycle','?')} · selector `{cycle.get('selector','?')}` · "
             f"{cycle.get('utc','?')}", ""]
    #  A halted round is a recorded OUTCOME, not an error -- but rendering it identically to a
    #  completed one made the round look finished while a party was undersampled.
    for halt in data.get("halts") or []:
        lines += [f"> **HALTED — exit {halt.get('exit_code','?')}: "
                  f"{halt.get('reason','(no reason recorded)')}**", ">"]
        detail = halt.get("detail")
        #  `detail` is a structured record, and stringifying it printed a Python dict repr into
        #  a published page. Rendered field by field instead; `why` is prose and carries the
        #  reasoning a reader actually needs.
        if isinstance(detail, dict):
            for key, value in detail.items():
                if not value:
                    continue
                shown = ", ".join(map(str, value)) if isinstance(value, list) else str(value)
                lines += [f"> **{key}:** {shown}", ">"]
        elif detail:
            lines += [f"> {detail}", ">"]
        if halt.get("note"):
            lines += [f"> {halt['note']}", ""]
        else:
            lines += [""]
    if data.get("undersampled"):
        lines += [f"> **Undersampled: {', '.join(data['undersampled'])}.** Below the k floor a "
                  f"reply is not a party's position. Everything collected is published; nothing "
                  f"is inferred from it.", ""]
    if not (cycle.get("selected") or {}).get("asked", True):
        lines += ["> **This question is not recorded as asked.** The round did not complete the "
                  "path that marks it so.", ""]
    lines += ["## The question", "",
             f"Proposed by **{selected.get('party','?')}** ({selected.get('id','?')}), reproduced "
             f"as written:", "", f"> {selected.get('question','(not recorded)')}", ""]
    if selected.get("reason"):
        lines += ["Their stated reason:", "", f"> {selected['reason']}", ""]

    lines += ["## Arms", "",
              f"Recorded arms: {', '.join(f'`{a}`' for a in cycle.get('arms') or []) or '(none)'}",
              ""]
    if cycle.get("arms_note"):
        lines += ["The round record states, verbatim:", "", f"> {cycle['arms_note']}", ""]

    lines += ["## Parties", "",
              "| party | k requested | k collected | citable | modal position | pages |",
              "|---|---|---|---|---|---|"]
    for party in sorted(data["specs"]):
        summary = data["summaries"].get(party)
        if not summary:
            lines.append(f"| {party} | — | — | **solicitation failed** | — | — |")
            continue
        variance = summary.get("variance") or {}
        first = next(iter(variance.values()), {})
        modal = first.get("modal_value")
        frac = first.get("modal_fraction")
        modal_cell = (f"`{modal}` ({frac:.0%})" if modal is not None and frac is not None
                      else "—")
        pages = ", ".join(f"[{i+1}]({s}.md)" for i, s in enumerate(party_slugs.get(party, [])))
        lines.append(f"| {party} | {summary.get('k_requested','?')} | "
                     f"{summary.get('k_collected','?')} | {summary.get('citability','?')} | "
                     f"{modal_cell} | {pages} |")

    lines += ["", "Variance is computed from the samples actually collected, never asserted, and "
              "is recomputed from the raw material by this generator and compared with the "
              "recorded summary before publication.", "",
              "## What this round does not establish", "",
              "- Answers from parties in different arms are not comparable, and nothing here "
              "pools them.",
              "- A modal position is the shape of a categorical field, not agreement. Parties can "
              "share a label while answering incompatibly.",
              "- These are sampled invocations, not any model's stable position.", ""]

    if round_id in ("round-007-p006-with-pointer", "round-008-p006-pinned"):
        lines += ["- **This round's search reached nothing of this record.** Round 007 returned "
                  "100 citations across 20 samples, none of them of this record; round 008, "
                  "pinned to the record's host, returned zero citations of any kind because the "
                  "site is not in the search index. No position may be attributed to anything a "
                  "party read here. Filed as D-52.", ""]

    lines += [f"## Spend", "",
              f"Budget ceiling {json.dumps(cycle.get('budget'))} · actual "
              f"`{cycle.get('actual_usd')}`", "",
              "## Verification", "",
              f"- plan `{cycle.get('plan_sha256','?')}`",
              f"- prompt template `{cycle.get('template_sha256','?')}`",
              f"- context pack `{cycle.get('context_pack_sha256','?')}`",
              f"- [every prompt, verbatim]({round_id}-prompts.md)", "",
              nav(*links)]
    write_pair(round_id, round_id, "\n".join(lines))


def index_page(rounds: list[dict]) -> None:
    lines = ["# Deliberation rounds", "",
             f"{len(rounds)} rounds. Each was one question, asked of several parties at k >= 5 "
             "with computed variance, and stopped there — no synthesis and no adoption.", "",
             "The prompt each party received is published in full beside its answers, because a "
             "party's only available verification is checking that it was asked what the page "
             "says it was asked.", "",
             "| round | cycle | question | parties | outcome |", "|---|---|---|---|---|"]
    for data in rounds:
        cycle, selected = data["cycle"], (data["cycle"].get("selected") or {})
        q = (selected.get("question") or "").strip()
        q = (q[:90] + "…") if len(q) > 90 else q
        flags = []
        if data.get("halts"):
            flags.append(f"**HALTED {data['halts'][-1].get('exit_code','?')}**")
        if data.get("undersampled"):
            flags.append("undersampled: " + ", ".join(data["undersampled"]))
        lines.append(f"| [{data['round']}]({data['round']}.md) | {cycle.get('cycle','?')} | "
                     f"{q} | {len(data['specs'])} | {'; '.join(flags) or 'completed'} |")
    lines += ["", "Variance is computed from collected samples, never asserted. Parties in "
              "different arms are never pooled.", ""]
    write_pair("index", "Deliberation rounds", "\n".join(lines))


def prune(expected_pages: set[str], expected_prompts: set[str]) -> list[str]:
    """Remove files this generator no longer produces. Owns only its own subtree.

    Pages and prompts need SEPARATE sets: page slugs split into `-1`/`-2` as a party's samples
    grow, while a prompt is always `<round>-<party>`. Sharing one set deleted every prompt whose
    page had split.
    """
    removed = []
    for path in sorted(OUT.glob("*")) if OUT.exists() else []:
        if path.is_file() and path.stem not in expected_pages:
            path.unlink()
            removed.append(path.name)
    for path in sorted(PROMPTS.glob("*.txt")) if PROMPTS.exists() else []:
        if path.stem not in expected_prompts:
            path.unlink()
            removed.append(f"artifacts/prompts/{path.name}")
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = parser.parse_args()

    ids = sorted(p.stem for p in CYCLES.glob("*.json") if ROUND_ID.match(p.stem))
    rounds, skipped = [], []
    for round_id in ids:
        try:
            rounds.append(load_round(round_id))
        except BuildRefusal as refusal:
            #  A round still being solicited has specs and no summaries yet. That is not a
            #  defect, and refusing the whole build for it would make the loop unrunnable.
            if "mid-flight" in str(refusal) or "no summary" in str(refusal):
                skipped.append((round_id, str(refusal)))
                continue
            print(f"REFUSED  {refusal}", file=sys.stderr)
            return 1
    for data in rounds:
        try:
            check_variance(data)
        except BuildRefusal as refusal:
            print(f"REFUSED  {refusal}", file=sys.stderr)
            return 1

    if args.check:
        flagged = [d["round"] for d in rounds if d.get("halts") or d.get("undersampled")]
        print(f"{len(rounds)} round(s) internally consistent; {len(skipped)} skipped as "
              f"incomplete.")
        if flagged:
            print(f"  {len(flagged)} halted or undersampled (consistent is not complete): "
                  f"{', '.join(flagged)}")
        for round_id, why in skipped:
            print(f"  skipped {round_id}: {why[:150]}")
        return 0

    expected, expected_prompts = {"index"}, set()
    for i, data in enumerate(rounds):
        neighbours = (rounds[i - 1]["round"] if i else None,
                      rounds[i + 1]["round"] if i + 1 < len(rounds) else None)
        prompts_page(data)
        expected.add(f"{data['round']}-prompts")
        expected_prompts |= {f"{data['round']}-{p}" for p in data["specs"]}
        #  Slugs come from party_pages(), NEVER from a guess at the unsplit name. Whitelisting
        #  `<round>-<party>` unconditionally kept the pre-split page alive after a party's
        #  samples grew and split into -1/-2, leaving a stale 16,396-token page published beside
        #  its own replacements -- the exact failure build_viewer's pruner was written for.
        slugs = {}
        for party in sorted(data["summaries"]):
            slugs[party] = party_pages(data, party)
            expected |= set(slugs[party])
        round_page(data, slugs, neighbours)
        expected.add(data["round"])
    index_page(rounds)

    removed = prune(expected, expected_prompts)
    print(f"published {len(rounds)} round(s) to docs/rounds/ "
          f"({len(list(OUT.glob('*.md')))} markdown pages, "
          f"{len(list(PROMPTS.glob('*.txt')))} exact prompts)")
    for round_id, why in skipped:
        print(f"  skipped {round_id} (incomplete): {why[:110]}")
    if removed:
        print(f"  pruned {len(removed)} stale file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
