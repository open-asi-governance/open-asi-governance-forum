#!/usr/bin/env python3
"""Publish the prediction registry as a page, with its own weakness on the page.

    python3 tools/build_predictions_view.py

Writes docs/predictions.html and docs/predictions.md from
predictions/predictions.json. Deterministic; no network; no model calls.

WHAT A PREDICTION REGISTRY IS FOR, and why publishing one is risky.

The registry exists so this project's claims about itself can be scored against
what happened, on dates fixed in advance. That is a real discipline and it has
already caught things: P-CLAUDE-F5-0001's first score was found procedurally
invalid, and the correction is published beside it.

It is also the single easiest artifact in this repository to read as a boast.
"4 correct, 5 incorrect" looks like calibration evidence. **It is not**, and the
reasons are measurable rather than rhetorical, so this page computes them and puts
them at the top rather than in a footnote:

  * **21 of 24 predictions are forecast by the annotator** -- Claude Code, an
    Anthropic invocation surface that is a party to this record. Three come from
    anyone else.
  * **No entry NAMES the party that scored it.** Every scored entry now carries a
    `scored_by` block, and every one of them records `identity: null` with a stated
    reason: the field did not exist when those outcomes were applied, so the
    judging party was never captured. The block records what IS known -- the commit
    the outcome first appears in, and its date -- separately from what is merely
    inferred, and it says nobody verified any of it independently. A backfill that
    had written "Claude Code" into `identity` would have been a value that looks
    like provenance and is a guess. That is D-18's shape -- attribution resting on
    the interested party's own testimony -- applied to calibration.
  * **One binary outcome establishes nothing about calibration** at all, and
    thirteen barely more when they are not independent and share a forecaster.

Every count on the page is DERIVED from the JSON. Track A's status report quoted
"8 open" while the file held 11, because three had been added since -- a hardcoded
count in a document about miscounted claims. Nothing here is typed by hand.

WHAT THIS PAGE DOES NOT DO. It does not compute a calibration curve, a Brier
score, or any aggregate that would imply the sample supports one. Offering a
number that looks like calibration from a self-forecast, self-scored, n=13 set
would be exactly the overstatement the register keeps filing against this project.

Exit status is 0 on success.
"""

from __future__ import annotations

import html
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "predictions" / "predictions.json"
DOCS = REPO_ROOT / "docs"

OUTCOME_LABEL = {
    "correct": "correct",
    "incorrect": "incorrect",
    "unresolvable": "unresolvable",
    "condition_satisfied_early_pending_scheduled_score": "condition met early, not yet scored",
}
OUTCOME_CLASS = {
    "correct": "g", "incorrect": "d", "unresolvable": "w",
    "condition_satisfied_early_pending_scheduled_score": "w",
}
ANNOTATOR_MARKERS = ("Claude Code",)


def forecaster_of(entry: dict) -> str:
    who = entry.get("forecaster")
    if isinstance(who, dict):
        return who.get("identity") or "unrecorded"
    return str(who or "unrecorded")


def is_annotator(name: str) -> bool:
    return any(marker in name for marker in ANNOTATOR_MARKERS)


def load() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def stats(doc: dict) -> dict:
    openp, scored = doc["predictions"], doc["scored"]
    every = openp + scored
    by_forecaster = Counter(forecaster_of(e) for e in every)
    return {
        "open": openp,
        "scored": scored,
        "total": len(every),
        "outcomes": Counter(s.get("outcome", "unrecorded") for s in scored),
        "by_forecaster": by_forecaster,
        "annotator_count": sum(n for who, n in by_forecaster.items() if is_annotator(who)),
        "external": {who: n for who, n in by_forecaster.items() if not is_annotator(who)},
        # A scored_by whose identity is null is a RECORD of an unrecorded scorer,
        # not a recorded scorer. Counting the field's presence would report 13 of 13
        # and mean nothing -- the number that matters is how many name a party.
        "scorer_field_present": sum(1 for s in scored if s.get("scored_by")),
        "scorer_recorded": sum(
            1 for s in scored if (s.get("scored_by") or {}).get("identity")),
        "independently_verified": sum(
            1 for s in scored if (s.get("scored_by") or {}).get("independently_verified")),
    }


def caveats(s: dict) -> list[str]:
    """The reasons the numbers below are weak. Computed, not asserted."""
    pct = round(100 * s["annotator_count"] / s["total"]) if s["total"] else 0
    return [
        f"<strong>{s['annotator_count']} of {s['total']} predictions are forecast by the "
        f"annotator</strong> ({pct}%) — Claude Code, an Anthropic invocation surface that is a "
        f"party to this record. External forecasters: "
        f"{', '.join(f'{k} ({v})' for k, v in sorted(s['external'].items())) or 'none'}.",

        f"<strong>{s['scorer_recorded']} of {len(s['scored'])} scored entries name the party that "
        f"scored them</strong>, and <strong>{s['independently_verified']} were independently "
        f"verified.</strong> All {s['scorer_field_present']} now carry a <code>scored_by</code> "
        f"block, but every one records <code>identity: null</code> with a stated reason: the field "
        f"did not exist when they were scored, so the judging party was never captured and is "
        f"inferred from git history rather than recorded. The party that wrote each claim, wrote "
        f"its resolution criterion, and applied the outcome is the same party. See D-18.",

        f"<strong>Every scored entry now cites the hash-anchored artifacts its evidence rests "
        f"on.</strong> Two external parties scoring this registry blind judged that 10 of 13 "
        f"could not be verified from what was published, because the evidence restated derived "
        f"numbers instead of pointing at samples that were in the corpus the whole time (D-40). "
        f"The citations are a CANDIDATE SET derived mechanically from each outcome's own commit; "
        f"nobody has verified per claim that those samples establish that criterion.",

        f"<strong>{len(s['scored'])} scored outcomes cannot establish calibration.</strong> They "
        f"are not independent, they share a forecaster, and several concern this project's own "
        f"behaviour, which the forecaster also controls. No aggregate score is computed here, "
        f"deliberately.",
    ]


def entry_rows(entries: list[dict], scored: bool) -> str:
    e_ = html.escape
    rows = []
    for entry in entries:
        who = forecaster_of(entry)
        mark = ' <span class="tag w">annotator</span>' if is_annotator(who) else ""
        if scored:
            outcome = entry.get("outcome", "unrecorded")
            state = (f'<span class="tag {OUTCOME_CLASS.get(outcome, "w")}">'
                     f'{e_(OUTCOME_LABEL.get(outcome, outcome))}</span>')
        else:
            status = entry.get("status", "open")
            state = f'<span class="tag">{e_(status.replace("_", " "))}</span>'
        extra = []
        sa = entry.get("supporting_artifacts") or {}
        if sa.get("paths"):
            links = "".join(
                f'<li><code class="h">{e_(r["path"])}</code><br>'
                f'sha256 <code class="h">{e_(str(r["sha256"]))}</code></li>'
                for r in sa["paths"])
            extra.append(
                f'<div class="box"><b>the material this rests on '
                f'({len(sa["paths"])} artifact(s))</b>'
                f'<ul>{links}</ul>{e_(sa.get("how_derived",""))} '
                f'{e_(sa.get("limit",""))}</div>')
        by = entry.get("scored_by") or {}
        if by and by.get("identity") is None:
            extra.append(
                f'<div class="box corr"><b>who scored this is not recorded</b>'
                f'{e_(by.get("identity_unrecorded_reason", ""))} '
                f'Inferred: {e_(str(by.get("inferred_identity", "unknown")))}. '
                f'{e_(str(by.get("inference_basis", "")))} '
                f'Independently verified: {"yes" if by.get("independently_verified") else "no"}.'
                f'</div>')
        for key, label in (("why_this_score_is_worth_little", "why this score is worth little"),
                           ("scoring_correction_round_02", "scoring corrected after review"),
                           ("criterion_defect", "criterion defect recorded"),
                           ("scoring_note", "not scored yet, and why")):
            if entry.get(key):
                extra.append(f'<div class="box corr"><b>{label}</b>{e_(str(entry[key]))}</div>')
        rows.append(
            f'<article class="node" id="p-{e_(entry["id"])}">'
            f'<div class="nh"><span class="who">{e_(entry["id"])}</span>{state}'
            f'<span class="tag">{e_(who)}</span>{mark}</div>'
            f'<details><summary><p class="sum">{e_(entry["claim"][:240])}'
            f'{"…" if len(entry["claim"]) > 240 else ""}</p></summary>'
            f'<div class="body">'
            f'<div class="meta">resolves {e_(str(entry.get("resolution_date", "—")))}'
            f' · confidence {e_(str(entry.get("confidence", "—")))}</div>'
            f'<p><strong>Claim.</strong> {e_(entry["claim"])}</p>'
            f'<p><strong>Resolution criterion.</strong> '
            f'{e_(str(entry.get("resolution_criterion", "not stated")))}</p>'
            + (f'<p><strong>Resolution limit.</strong> {e_(str(entry["resolution_limit"]))}</p>'
               if entry.get("resolution_limit") else "")
            + (f'<p><strong>Rationale.</strong> {e_(str(entry["rationale"]))}</p>'
               if entry.get("rationale") else "")
            + (f'<p><strong>Evidence.</strong> {e_(str(entry["evidence"]))}</p>'
               if entry.get("evidence") else "")
            + "".join(extra)
            + '</div></details></article>')
    return "".join(rows)


def render_html(doc: dict, part: dict | None = None, pager: str = "") -> str:
    s = stats(doc)
    css_source = REPO_ROOT / "tools" / "build_viewer.py"
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    from build_viewer import CSS                                   # noqa: E402

    outcome_bits = " · ".join(
        f"{n} {OUTCOME_LABEL.get(k, k)}" for k, n in sorted(s["outcomes"].items()))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prediction registry — Open ASI Governance Forum</title>
<meta name="description" content="Dated, pre-registered predictions about this project, scored on their resolution dates — published together with the reasons the scores are weak evidence.">
<link rel="alternate" type="text/markdown" href="predictions.md">
<style>{CSS}</style>
</head>
<body>
<header><div class="hrow">
<h1>Prediction registry<small>claims about this project, dated in advance</small></h1>
<nav class="nav"><a href="index.html">home</a><a href="record.html">the record</a>
<a href="deficiencies.html">deficiency register</a>
<a href="predictions.md">this page as plain text</a></nav>
</div></header>
<main>
<p><strong>{len(s['open'])} open · {len(s['scored'])} scored</strong> — {outcome_bits}.</p>

<div class="box corr">
<b>Read these before reading the numbers.</b>
<ul>{"".join(f"<li>{c}</li>" for c in caveats(s))}</ul>
</div>

{pager}
<h2 class="round">Open — showing {len(part['open']) if part else len(s['open'])} of {len(s['open'])}</h2>
{entry_rows(part['open'] if part else s['open'], scored=False)}

<h2 class="round">Scored — showing {len(part['scored']) if part else len(s['scored'])} of {len(s['scored'])}</h2>
{entry_rows(part['scored'] if part else s['scored'], scored=True)}
{pager}
</main>
<footer>
<p>Generated from <code>predictions/predictions.json</code> by
<code>tools/build_predictions_view.py</code>. Every count on this page is derived from that file;
none is typed. A status report once quoted "8 open" while the file held 11.</p>
<p>No aggregate calibration score is computed. A self-forecast, self-scored set of
{len(s['scored'])} outcomes does not support one, and offering a number that looked like
calibration would be the overstatement this project keeps filing against itself.</p>
<p>Corpus CC BY 4.0; code Apache-2.0. Custodian: Stephen Reed.</p>
</footer>
</body>
</html>
"""


def render_md(doc: dict) -> str:
    s = stats(doc)
    out = [
        "# Prediction registry — Open ASI Governance Forum",
        "",
        f"{len(s['open'])} open · {len(s['scored'])} scored — "
        + " · ".join(f"{n} {OUTCOME_LABEL.get(k, k)}" for k, n in sorted(s["outcomes"].items())),
        "",
        "## Read these before reading the numbers",
        "",
    ]
    import re
    for caveat in caveats(s):
        out.append(f"- {re.sub(r'<[^>]+>', '', caveat)}")
    out += ["", "## Open", ""]
    for entry in s["open"]:
        out += [f"### {entry['id']} — {forecaster_of(entry)}", "",
                f"- resolves {entry.get('resolution_date', '—')}",
                f"- confidence {entry.get('confidence', '—')}",
                f"- status {entry.get('status', 'open')}", "",
                f"**Claim.** {entry['claim']}", "",
                f"**Resolution criterion.** {entry.get('resolution_criterion', 'not stated')}", ""]
        if entry.get("resolution_limit"):
            out += [f"**Resolution limit.** {entry['resolution_limit']}", ""]
        if entry.get("scoring_note"):
            out += [f"**Not scored yet, and why.** {entry['scoring_note']}", ""]
    out += ["## Scored", ""]
    for entry in s["scored"]:
        out += [f"### {entry['id']} — {forecaster_of(entry)}", "",
                f"- outcome **{OUTCOME_LABEL.get(entry.get('outcome',''), entry.get('outcome'))}**",
                f"- resolved {entry.get('resolved_utc', '—')}", "",
                f"**Claim.** {entry['claim']}", ""]
        if entry.get("evidence"):
            out += [f"**Evidence.** {entry['evidence']}", ""]
        by = entry.get("scored_by") or {}
        if by and by.get("identity") is None:
            out += [f"**Who scored this is not recorded.** "
                    f"{by.get('identity_unrecorded_reason','')} "
                    f"Inferred: {by.get('inferred_identity','unknown')}. "
                    f"{by.get('inference_basis','')} "
                    f"Independently verified: "
                    f"{'yes' if by.get('independently_verified') else 'no'}.", ""]
        sa = entry.get("supporting_artifacts") or {}
        if sa.get("paths"):
            out += ["**The material this rests on.**"]
            out += [f"- `{r['path']}` sha256 `{r['sha256']}`" for r in sa["paths"]]
            out += ["", sa.get("how_derived", ""), sa.get("limit", ""), ""]
        if entry.get("why_this_score_is_worth_little"):
            out += [f"**Why this score is worth little.** "
                    f"{entry['why_this_score_is_worth_little']}", ""]
        if entry.get("scoring_correction_round_02"):
            out += [f"**Scoring corrected after review.** "
                    f"{entry['scoring_correction_round_02']}", ""]
    out += ["---", "",
            "No aggregate calibration score is computed. A self-forecast, self-scored set does "
            "not support one.", ""]
    return "\n".join(out)


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing {SOURCE.relative_to(REPO_ROOT)}")
        return 1
    doc = load()
    DOCS.mkdir(parents=True, exist_ok=True)
    # CHUNKED by measured size, like the register. Adding two pre-registrations
    # pushed this page over the 20,000-token ceiling within hours of the gate being
    # built -- the gate caught it, which is the whole point, but a page that splits
    # itself is better than one that fails the build every time a prediction is
    # filed.
    s = stats(doc)
    every = [("open", e) for e in s["open"]] + [("scored", e) for e in s["scored"]]
    CHROME, PER_TOKEN, PACK_TO = 24_000, 3.4, 14_000
    chunks, current, size = [], [], 0
    for kind, entry in every:
        cost = len(json.dumps(entry)) * 2
        if current and (CHROME + size + cost) / PER_TOKEN > PACK_TO:
            chunks.append(current); current, size = [], 0
        current.append((kind, entry)); size += cost
    if current:
        chunks.append(current)

    def slug_for(i):
        return "predictions.html" if i == 0 else f"predictions-{i + 1}.html"

    for path in DOCS.glob("predictions-*.html"):
        path.unlink()
    for index, chunk in enumerate(chunks):
        links = "".join(
            f'<a href="{slug_for(j)}"{" aria-current=\"page\"" if j == index else ""}>'
            f'part {j + 1}</a>' for j in range(len(chunks)))
        pager = f'<nav class="pager">{links}</nav>' if len(chunks) > 1 else ""
        part = {"open": [e for k, e in chunk if k == "open"],
                "scored": [e for k, e in chunk if k == "scored"]}
        (DOCS / slug_for(index)).write_text(
            render_html(doc, part=part, pager=pager), encoding="utf-8")
    (DOCS / "predictions.md").write_text(render_md(doc), encoding="utf-8")
    print(f"wrote docs/predictions.html and docs/predictions.md — "
          f"{len(s['open'])} open, {len(s['scored'])} scored, "
          f"{s['annotator_count']} of {s['total']} forecast by the annotator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
