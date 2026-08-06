#!/usr/bin/env python3
"""Publish the locally-served solicitation rounds, one page per solicitation.

    python3 tools/build_local_rounds.py

Writes `docs/local/<round>__<slug>.html` for each `solicitation_summary`, plus
`docs/local/index.html` listing them.

WHY THESE WERE MISSING, and why that mattered. The viewer rendered the founding
deliberation and the review rounds only. All eight local rounds -- the entire
measurement programme, and the source of D-23 through D-28 -- were committed to
the corpus and absent from the published site. Two consequences, and the second
is worse than the first:

  * The site's footer said "every contribution here is a single sample (k=1)".
    That was true ONLY because the k=10 and k=20 rounds were excluded. The one
    party whose contributions actually meet this project's own k >= 5 bar was
    the one party the site did not show.
  * The excluded party is the locally-served model, which is also the only
    contributor whose output this project can produce at will. Excluding it
    published a record of what frontier chat surfaces said and omitted the only
    systematically sampled evidence in the corpus.

ONE PAGE PER SOLICITATION, not per round. The agent-readability amendment sets a
~20,000-token budget per page, from the measured fact that the main viewer at
109k tokens was 4.4x too large for this corpus's own contributing party to read.
Per-round pages would breach that for local-round-07 and -03; per-solicitation
pages do not, and the split is uniform rather than special-cased.

D-28 IS ATTACHED TO EVERY RESULT, not linked from a footnote. The apparatus that
produced these does not reproduce: identical prompt, identical seeds, identical
temperature, identical model gave 8/20 identical answers and a run-to-run
entropy gap of 0.4649 bits. The operational rule from that entry is applied per
field, so a reader sees "noise-dominated" beside the number rather than having
to know to go and look it up.

Deterministic: no clock, no randomness, sorted throughout.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = REPO_ROOT / "corpus/artifacts"
OUT_DIR = REPO_ROOT / "docs/local"

# D-28's operational rule, applied to a single field's modal share.
ROBUST = ("robust", "g",
          "Lopsided margin. Numeric noise cannot flip it, so this result survives D-28.")
NOISE = ("noise-dominated", "d",
         "Near a coin flip, which is exactly where a rounding difference decides the answer. "
         "Report the split; claim nothing from it.")
MIDDLE = ("not lopsided", "w",
          "Between the thresholds D-28 makes claims about. Weaker than a lopsided margin and "
          "stronger than a coin flip; treat the exact fraction as soft.")


def classify(modal_fraction: float) -> tuple[str, str, str]:
    if modal_fraction >= 0.9 or modal_fraction <= 0.1:
        return ROBUST
    if 0.4 <= modal_fraction <= 0.6:
        return NOISE
    return MIDDLE


def summaries() -> list[tuple[Path, dict]]:
    found = []
    for path in sorted(ARTIFACTS.glob("local-round-*/*-summary.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("artifact_type") == "solicitation_summary":
            found.append((path, doc))
    return found


def page_name(doc: dict) -> str:
    return f"{doc['round']}__{doc['slug']}.html"


CSS = """
:root{--bg:#fbfaf8;--fg:#1a1a1a;--mut:#6b6b6b;--line:#e2ded8;--card:#fff;--accent:#7a5c3e;
--warn:#8a5a00;--bad:#9b2c2c;--ok:#2f6b4f;--code:#f4f1ec}
@media(prefers-color-scheme:dark){:root{--bg:#161514;--fg:#e8e4de;--mut:#9a948c;--line:#33302c;
--card:#1e1c1a;--accent:#c9a678;--warn:#d9a441;--bad:#e07a7a;--ok:#7ab894;--code:#242220}}
:root[data-theme=dark]{--bg:#161514;--fg:#e8e4de;--mut:#9a948c;--line:#33302c;--card:#1e1c1a;
--accent:#c9a678;--warn:#d9a441;--bad:#e07a7a;--ok:#7ab894;--code:#242220}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
header{border-bottom:1px solid var(--line);padding:.8rem 1rem}
.hrow{max-width:900px;margin:0 auto}
h1{font-size:1rem;margin:0 0 .2rem;font-weight:650}
h1 small{display:block;font-weight:400;color:var(--mut);font-size:.75rem;margin-top:.15rem}
nav a{color:var(--accent);font-size:.82rem;margin-right:.8rem}
main{max-width:900px;margin:0 auto;padding:1rem}
h2{font-size:1rem;margin:1.8rem 0 .5rem;padding-bottom:.25rem;border-bottom:2px solid var(--line)}
h3{font-size:.9rem;margin:1.1rem 0 .3rem}
table{border-collapse:collapse;width:100%;margin:.5rem 0;font-size:.85rem}
th,td{border:1px solid var(--line);padding:.32rem .5rem;text-align:left;vertical-align:top}
th{background:var(--code);font-weight:600}
.wrap{overflow-x:auto}
pre{background:var(--code);padding:.6rem;border-radius:6px;overflow-x:auto;
font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;word-wrap:break-word}
.box{border-left:3px solid var(--line);padding:.5rem .8rem;margin:.7rem 0;font-size:.87rem;
background:var(--code);border-radius:0 6px 6px 0}
.box.bad{border-left-color:var(--bad)}
.box.warn{border-left-color:var(--warn)}
.box b{display:block;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;
color:var(--mut);margin-bottom:.25rem}
.tag{font-size:.68rem;padding:.1rem .45rem;border-radius:99px;border:1px solid var(--line);
color:var(--mut);white-space:nowrap;display:inline-block}
.tag.d{border-color:var(--bad);color:var(--bad)}
.tag.w{border-color:var(--warn);color:var(--warn)}
.tag.g{border-color:var(--ok);color:var(--ok)}
.s{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:.6rem 0;padding:.6rem .8rem}
.meta{font-size:.8rem;color:var(--mut)}
footer{max-width:900px;margin:2rem auto;padding:1rem;border-top:1px solid var(--line);
color:var(--mut);font-size:.78rem}
a{color:var(--accent)}
code{background:var(--code);padding:.05rem .3rem;border-radius:3px;font-size:.92em;word-break:break-all}
"""


def shell(title: str, subtitle: str, nav: str, body: str, alternate: str = "") -> str:
    alt = f'<link rel="alternate" type="text/markdown" href="{alternate}">' if alternate else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
{alt}
<style>{CSS}</style>
</head>
<body>
<header><div class="hrow">
<h1>{html.escape(title)}<small>{html.escape(subtitle)}</small></h1>
<nav>{nav}</nav>
</div></header>
<main>{body}</main>
<footer>
<p>Locally-served solicitation. The model is operator-hosted, so unlike a chat-surface contribution
its sampling parameters are known and it can be sampled repeatedly — which is why these are the only
contributions in this corpus that meet the project's own k&nbsp;&ge;&nbsp;5 bar, and why they are
also the only ones whose apparatus could be caught failing to reproduce.</p>
<p>Generated by <code>tools/build_local_rounds.py</code>. Annotation by Claude Code (Anthropic), a
party to the record. Custodian: Stephen Reed. Corpus CC BY 4.0. Reading, quoting and ingestion are
permitted under those terms.</p>
</footer>
</body>
</html>
"""


D28_BANNER = (
    '<div class="box bad"><b>D-28 — the apparatus that produced this does not reproduce</b>'
    'Replaying a probe at <em>identical</em> prompt, seeds, temperature and model reproduced '
    '<strong>8 of 20</strong> answers, with a run-to-run entropy gap of <strong>0.4649 bits</strong>. '
    'Root-caused to a vendor-documented MoE kernel fusion that is non-deterministic above top-k 2; '
    'this model runs top-k 8. <strong>No effect smaller than ~0.5 bits is measurable here</strong>, '
    'and the recorded <code>seed</code> records what was requested rather than something that '
    'reproduces. Each field below carries its own status under that rule.</div>'
)


def render_variance(doc: dict) -> str:
    rows = []
    for field, v in sorted(doc["variance"].items()):
        label, cls, why = classify(v["modal_fraction"])
        dist = ", ".join(f"{html.escape(str(k))} — {n}"
                         for k, n in sorted(v["distribution"].items(), key=lambda kv: -kv[1]))
        rows.append(
            f'<tr><td><code>{html.escape(field)}</code></td>'
            f'<td>{dist}</td>'
            f'<td>{v["modal_fraction"]:.2f}</td>'
            f'<td>{v["shannon_entropy_bits"]} bits<br><span class="meta">at T = 0.7</span></td>'
            f'<td><span class="tag {cls}">{html.escape(label)}</span><br>'
            f'<span class="meta">{html.escape(why)}</span></td></tr>')
    return ('<div class="wrap"><table><tr><th>Field</th><th>Distribution</th><th>Modal share</th>'
            f'<th>Entropy</th><th>Status under D-28</th></tr>{"".join(rows)}</table></div>')


def render_solicitation(doc: dict) -> str:
    e = html.escape
    raw_path = REPO_ROOT / doc["raw_samples"]
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    spec = raw.get("spec", {})
    responses = raw.get("responses", [])
    contributor = doc.get("contributor", {})
    sampling = contributor.get("sampling_parameters", {})
    flags = doc.get("serve_configuration", {}).get("serve_flags", {})

    parts = [D28_BANNER]

    parts.append(f'<h2>The question</h2><p>{e(doc["question"])}</p>')
    parts.append(
        f'<p class="meta"><span class="tag">{e(doc["phase"])}</span> '
        f'<span class="tag">k requested {doc["k_requested"]}</span> '
        f'<span class="tag">k collected {doc["k_collected"]}</span> '
        f'<span class="tag">T = {sampling.get("temperature", "?")}</span></p>')
    if doc["k_collected"] != doc["k_requested"]:
        parts.append(
            f'<div class="box warn"><b>Shortfall</b>{doc["k_requested"] - doc["k_collected"]} '
            f'of {doc["k_requested"]} samples were not collected. Recorded rather than rounded up; '
            f'the variance below is computed over the {doc["k_collected"]} that were.</div>')
    if spec.get("phase_justification"):
        parts.append(f'<div class="box"><b>Phase justification — what was withheld</b>'
                     f'{e(spec["phase_justification"])}</div>')
        if doc["phase"].startswith("Phase-1"):
            parts.append(
                '<div class="box warn"><b>D-23 — withholding responses is not sufficient to make an '
                'arm blind</b>The task instruction, the schema and the enum labels are all channels '
                'through which a prior party\'s conclusion can reach a supposedly independent probe. '
                'One Phase-1 arm in this corpus was contaminated exactly that way. <strong>No Phase-1 '
                'claim here has been audited for it.</strong></div>')

    parts.append("<h2>Result</h2>")
    parts.append(render_variance(doc))

    parts.append("<h2>Provenance</h2>")
    prov = [
        ("model", contributor.get("version_identifier", "?")),
        ("provider", contributor.get("provider", "?")),
        ("sampling", ", ".join(f"{k} = {v}" for k, v in sorted(sampling.items()))),
        ("reasoning effort", contributor.get("reasoning_effort", "?")),
        ("system instructions", contributor.get("system_instructions", "?")),
        ("serving", ", ".join(f"{k} = {v}" for k, v in sorted(flags.items())
                              if k in ("served_model_name", "backend", "max_seq_len",
                                       "max_batch_size", "max_num_tokens"))),
        ("prompt sha256", doc.get("prompt_sha256", "—")),
        ("spec sha256", doc.get("spec_sha256", "—")),
        ("raw samples", doc["raw_samples"]),
    ]
    parts.append('<div class="wrap"><table>'
                 + "".join(f"<tr><th>{e(k)}</th><td><code>{e(str(v))}</code></td></tr>"
                           for k, v in prov)
                 + "</table></div>")
    parts.append(
        '<div class="box warn"><b>D-30 — the samples are referenced by path, with no hash</b>'
        'A <code>solicitation_summary</code> records <code>raw_samples</code> as a bare path, so '
        'nothing binds the numbers above to the specific bytes they were computed from. '
        'Contributions and free-text codings record <code>{path, sha256, bytes}</code> and are '
        'checked; this family is not. The file is covered by <code>corpus/MANIFEST.sha256</code>, '
        'so a lone edit is caught — the missing thing is the artifact-level binding.</div>')
    parts.append(
        '<div class="box"><b>Not shown here</b>The artifact also records the serving '
        '<code>model_path</code> and full <code>command_line</code>, which are absolute paths on the '
        "operator's machine. They are omitted from this page as infrastructure detail rather than "
        'record. This is <em>presentation</em>, not protection: those fields are committed in '
        f'<code>{e(str(Path("corpus/artifacts") / doc["round"] / (doc["slug"] + "-summary.json")))}</code> '
        'and are already public. Saying so, rather than implying something was withheld, is the '
        'distinction this project draws between sanitisation and selection.</div>')

    if spec.get("prompt"):
        parts.append("<h2>The prompt, verbatim</h2>")
        parts.append(f"<pre>{e(spec['prompt'])}</pre>")

    parts.append(f"<h2>All {len(responses)} responses, verbatim</h2>")
    parts.append('<p class="meta">Every sample collected, including the ones that disagree with the '
                 'modal answer. Nothing is selected for presentation.</p>')
    for r in responses:
        parts.append(
            f'<div class="s"><p class="meta"><b>sample {r.get("sample_index", "?")}</b> · '
            f'seed <code>{r.get("seed", "—")}</code> · finish '
            f'<code>{e(str(r.get("finish_reason", "—")))}</code></p>'
            f'<pre>{e(r.get("content", ""))}</pre></div>')
    if raw.get("failures"):
        parts.append(f'<div class="box bad"><b>Failures</b><pre>{e(json.dumps(raw["failures"], indent=1))}</pre></div>')

    nav = ('<a href="index.html">all local rounds</a>'
           '<a href="../index.html">threaded record</a>'
           '<a href="../deficiencies.html">deficiency register</a>')
    return shell(f"{doc['round']} · {doc['slug']}",
                 f"locally-served solicitation, k={doc['k_collected']} · {doc['phase']}",
                 nav, "".join(parts))


def render_index(docs: list[dict]) -> str:
    e = html.escape
    by_round: dict[str, list[dict]] = {}
    for d in docs:
        by_round.setdefault(d["round"], []).append(d)

    parts = [
        '<div class="box bad"><b>Read this before any number on these pages</b>'
        'These rounds were produced by an apparatus that <strong>does not reproduce</strong>. '
        'Identical prompt, identical seeds, identical temperature and identical model returned '
        '8 of 20 identical answers, with a run-to-run entropy gap of 0.4649 bits (D-28). '
        'Effects smaller than that are not measurable here at all, and one reported effect — '
        "local-round-01's 0.1815-bit phase shift — is <strong>void</strong> as a result, along with "
        "the evidence for prediction P-0008.</div>",
        '<p>Eight rounds of solicitations to a locally-served model. Unlike the chat-surface '
        'contributions in the threaded record, these were sampled repeatedly with known parameters, '
        'so they are the only contributions in this corpus that meet its own '
        '<strong>k&nbsp;&ge;&nbsp;5 with computed variance</strong> bar — and, for the same reason, '
        'the only ones whose apparatus could be caught failing.</p>',
        '<p class="meta">One page per solicitation, because the main viewer is 4.4&times; too large '
        "for this corpus's own contributing party to read within its 24,576-token window. Each page "
        'below carries every sample collected, the prompt verbatim, and the provenance.</p>',
    ]
    for rnd in sorted(by_round):
        parts.append(f'<h2>{e(rnd)}</h2>')
        rows = []
        for d in sorted(by_round[rnd], key=lambda x: x["slug"]):
            worst = min((classify(v["modal_fraction"])[0] for v in d["variance"].values()),
                        key=lambda label: ["noise-dominated", "not lopsided", "robust"].index(label))
            cls = {"robust": "g", "not lopsided": "w", "noise-dominated": "d"}[worst]
            rows.append(
                f'<tr><td><a href="{e(page_name(d))}">{e(d["slug"])}</a><br>'
                f'<span class="meta">{e(d["question"])}</span></td>'
                f'<td>{e(d["phase"])}</td><td>{d["k_collected"]}/{d["k_requested"]}</td>'
                f'<td><span class="tag {cls}">weakest field: {e(worst)}</span></td></tr>')
        parts.append('<div class="wrap"><table><tr><th>Solicitation</th><th>Phase</th>'
                     f'<th>k</th><th>Under D-28</th></tr>{"".join(rows)}</table></div>')

    nav = ('<a href="../index.html">threaded record</a>'
           '<a href="../deficiencies.html">deficiency register</a>'
           '<a href="https://github.com/open-asi-governance/open-asi-governance-forum">source</a>')
    return shell("Local solicitation rounds — Open ASI Governance Forum",
                 f"{len(docs)} solicitations across {len(by_round)} rounds · "
                 "every sample published, including the void ones",
                 nav, "".join(parts))


def main() -> int:
    found = summaries()
    if not found:
        print("no solicitation summaries found")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    docs = [doc for _, doc in found]
    total = 0
    for doc in docs:
        page = render_solicitation(doc)
        (OUT_DIR / page_name(doc)).write_text(page, encoding="utf-8")
        total += len(page)
    index = render_index(docs)
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")

    largest = max(len(render_solicitation(d)) for d in docs)
    print(f"wrote docs/local/ — {len(docs)} solicitation page(s) + index, {total + len(index):,} bytes")
    print(f"  largest page {largest:,} chars (~{largest // 4:,} tokens; budget is ~20,000)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
