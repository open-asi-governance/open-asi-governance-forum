#!/usr/bin/env python3
"""Build the threaded deliberation viewer as a single self-contained HTML page.

Output: docs/index.html, served by GitHub Pages at
https://open-asi-governance.github.io/open-asi-governance-forum/

Design constraints, each of them a consequence of something this project learned:

  * **Self-contained.** All data, CSS and JS are inlined. The page fetches
    nothing. Gemini's round-01 environment could reach neither
    raw.githubusercontent.com nor the github.com blob UI, and a viewer that
    silently fails to load is worse than no viewer.
  * **Raw text embedded.** Search runs over what the parties actually wrote, not
    over the annotator's summaries of what they wrote. A viewer that only
    searches annotation would make the interpretation layer the record.
  * **Corrections shown adjacent, never replacing.** The same rule the corpus
    follows. A reader must be able to see the claim and its correction together.
  * **Deterministic.** No timestamps, no randomness. Same repository state, same
    bytes out, so the page can be regenerated and diffed.

Usage:
    python3 tools/build_viewer.py
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "docs" / "index.html"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deficiency_count() -> int:
    """Count entries in the register rather than hardcoding the number.

    This page published "21 open" while the register held 28 entries and the
    register's own status line said 24 -- three artifacts of one repository
    stating three different counts of its own defects. A number a human retypes
    is a number that drifts, and this one drifts in the flattering direction.
    `tools/check_register.py` enforces the register's internal consistency; this
    derives from it so the page cannot disagree with it at all.
    """
    register = REPO_ROOT / "corpus" / "deficiencies.md"
    return len(re.findall(r"^### D-\d+ — ", register.read_text(encoding="utf-8"), re.MULTILINE))


def head_commit() -> str:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%H"], cwd=REPO_ROOT,
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except Exception:
        return "unavailable"


def raw_lines(path: Path, start: int, end: int) -> str:
    """Extract an inclusive 1-indexed line range, verbatim."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[start - 1:end])


def facet_identity(identity: str) -> str:
    """Group the same party under one filter without rewriting either record.

    segments.json bakes the provider into the identity string ("Grok (xAI)");
    the contribution records keep identity and provider as separate fields
    ("Grok" + "xAI"). That is an inconsistency between the two artifact families,
    not two different parties. Facets normalise for filtering; every node still
    displays and stores the identity exactly as its own record states it.
    """
    return identity.split(" (")[0].strip()


def build_founding_nodes() -> list[dict]:
    seg_doc = json.loads((REPO_ROOT / "corpus/artifacts/segments.json").read_text(encoding="utf-8"))
    transcript = REPO_ROOT / "corpus/raw/initial-transcript.txt"
    defaults = seg_doc.get("provenance_defaults", {})

    nodes = []
    current_prompt = None
    for seg in seg_doc["segments"]:
        start, end = seg["lines"]
        is_prompt = seg.get("role") == "prompt"
        node = {
            "id": seg["id"],
            "round": "founding",
            "identity": seg.get("identity") or "unattributed",
            "label_in_raw": seg.get("author_label_in_raw"),
            "label_absent": bool(seg.get("author_label_absent")),
            "role": seg.get("role") or "",
            "summary": seg.get("summary", ""),
            "text": raw_lines(transcript, start, end),
            "lines": [start, end],
            "note": seg.get("annotator_note", ""),
            "correction": seg.get("correction_round_01", ""),
            "ballot": seg.get("ballot", ""),
            "status": seg.get("attribution_status", defaults.get("attribution_status", "active")),
            "durable": seg.get("durable_outputs", []),
            "claims": seg.get("key_claims", []),
            "evidence": seg.get("identity_evidence", ""),
            "conflict": seg.get("conflict_flag", ""),
            "superseded": seg.get("superseded_by", []),
            "k": defaults.get("k", 1),
            "phase": defaults.get("phase", "unclassified"),
            "citability": defaults.get("citability", ""),
            "parent": None if is_prompt else current_prompt,
            "is_prompt": is_prompt,
        }
        if is_prompt:
            current_prompt = seg["id"]
        nodes.append(node)
    return nodes


def build_review_nodes() -> list[dict]:
    art_dir = REPO_ROOT / "corpus/artifacts/review-round-01"
    if not art_dir.is_dir():
        return []

    prompt_path = REPO_ROOT / "record/review-round-01-prompt.md"
    nodes = [{
        "id": "RR01-PROMPT", "round": "review-round-01",
        "identity": "Stephen Reed (human custodian)",
        "label_in_raw": None, "label_absent": False,
        "role": "prompt",
        "summary": "Adversarial review request sent verbatim to Grok, ChatGPT, Gemini and Claude Fable 5: "
                   "Claude annotated a record in which Claude is a party — find what that produced.",
        "text": prompt_path.read_text(encoding="utf-8"),
        "lines": None, "note": "", "correction": "", "ballot": "", "status": "active",
        "durable": [], "claims": [], "evidence": "", "conflict": "", "superseded": [],
        "k": 1, "phase": "Phase-2 (informed)", "citability": "",
        "parent": None, "is_prompt": True,
    }]

    for path in sorted(art_dir.glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        raw = REPO_ROOT / rec["raw"]["path"]
        c = rec["contributor"]
        nodes.append({
            "id": rec["artifact_id"],
            "round": "review-round-01",
            "identity": c["identity"],
            "label_in_raw": None, "label_absent": False,
            "role": "adversarial review",
            "summary": "",
            "text": raw.read_text(encoding="utf-8"),
            "lines": None,
            "note": rec.get("notes", ""),
            "correction": "",
            "ballot": "",
            "status": rec.get("attribution_status", "active"),
            "durable": [], "claims": [],
            "evidence": c.get("version_identifier") or c.get("version_unknown_reason", ""),
            "conflict": rec.get("notes", ""),
            "superseded": [],
            "k": rec.get("k", 1),
            "phase": rec.get("phase", ""),
            "citability": rec.get("citability", ""),
            "prior_context": c.get("prior_context", ""),
            "captured": rec.get("captured_utc", ""),
            "provider": c.get("provider", ""),
            "sha256": rec["raw"]["sha256"],
            "parent": "RR01-PROMPT",
            "is_prompt": False,
        })
    return nodes


CSS = """
:root{--bg:#fbfaf8;--fg:#1a1a1a;--mut:#6b6b6b;--line:#e2ded8;--card:#fff;--accent:#7a5c3e;
--warn:#8a5a00;--bad:#9b2c2c;--ok:#2f6b4f;--code:#f4f1ec;--hl:#ffe9a8}
@media(prefers-color-scheme:dark){:root{--bg:#161514;--fg:#e8e4de;--mut:#9a948c;--line:#33302c;
--card:#1e1c1a;--accent:#c9a678;--warn:#d9a441;--bad:#e07a7a;--ok:#7ab894;--code:#242220;--hl:#5a4a1e}}
:root[data-theme=dark]{--bg:#161514;--fg:#e8e4de;--mut:#9a948c;--line:#33302c;--card:#1e1c1a;
--accent:#c9a678;--warn:#d9a441;--bad:#e07a7a;--ok:#7ab894;--code:#242220;--hl:#5a4a1e}
:root[data-theme=light]{--bg:#fbfaf8;--fg:#1a1a1a;--mut:#6b6b6b;--line:#e2ded8;--card:#fff;
--accent:#7a5c3e;--warn:#8a5a00;--bad:#9b2c2c;--ok:#2f6b4f;--code:#f4f1ec;--hl:#ffe9a8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line);padding:.7rem 1rem}
.hrow{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;max-width:1100px;margin:0 auto}
h1{font-size:1rem;margin:0;font-weight:650;letter-spacing:-.01em}
h1 small{font-weight:400;color:var(--mut);display:block;font-size:.75rem}
input[type=search]{flex:1;min-width:200px;padding:.45rem .7rem;border:1px solid var(--line);
border-radius:6px;background:var(--card);color:var(--fg);font:inherit;font-size:.9rem}
button{padding:.35rem .6rem;border:1px solid var(--line);border-radius:6px;background:var(--card);
color:var(--fg);font:inherit;font-size:.8rem;cursor:pointer}
button:hover{border-color:var(--accent)}
button[aria-pressed=true]{background:var(--accent);color:var(--bg);border-color:var(--accent)}
main{max-width:1100px;margin:0 auto;padding:1rem}
.bar{display:flex;gap:.4rem;flex-wrap:wrap;margin:.6rem 0 1rem;align-items:center}
.bar span.lbl{color:var(--mut);font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;margin-right:.2rem}
.count{color:var(--mut);font-size:.8rem;margin-left:auto}
.round{margin:2rem 0 1rem;padding-bottom:.3rem;border-bottom:2px solid var(--line);font-size:1.05rem;font-weight:650}
.node{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:.6rem 0;overflow:hidden}
.node.child{margin-left:1.5rem}
@media(max-width:640px){.node.child{margin-left:.6rem}}
.node.prompt{border-left:3px solid var(--mut)}
.node.disputed{border-left:3px solid var(--bad)}
.nh{display:flex;gap:.5rem;align-items:baseline;flex-wrap:wrap;padding:.6rem .8rem;cursor:pointer}
.nh:hover{background:var(--code)}
.who{font-weight:650}
.tag{font-size:.68rem;padding:.1rem .4rem;border-radius:99px;border:1px solid var(--line);color:var(--mut);white-space:nowrap}
.tag.b{border-color:var(--accent);color:var(--accent)}
.tag.w{border-color:var(--warn);color:var(--warn)}
.tag.d{border-color:var(--bad);color:var(--bad)}
.tag.g{border-color:var(--ok);color:var(--ok)}
.sum{color:var(--mut);font-size:.85rem;padding:0 .8rem .6rem;margin:0}
.body{display:none;padding:0 .8rem .8rem;border-top:1px solid var(--line)}
.node.open .body{display:block}
.node.open .sum{display:none}
pre{background:var(--code);padding:.7rem;border-radius:6px;overflow-x:auto;font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;word-wrap:break-word;margin:.6rem 0}
.meta{font-size:.78rem;color:var(--mut);margin:.5rem 0}
.meta code{background:var(--code);padding:.05rem .3rem;border-radius:3px;font-size:.92em;word-break:break-all}
.box{border-left:3px solid var(--line);padding:.4rem .7rem;margin:.6rem 0;font-size:.87rem;background:var(--code);border-radius:0 6px 6px 0}
.box.note{border-left-color:var(--accent)}
.box.corr{border-left-color:var(--warn)}
.box.conf{border-left-color:var(--bad)}
.box b{display:block;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin-bottom:.2rem}
mark{background:var(--hl);color:inherit;padding:0 .1em;border-radius:2px}
.hidden{display:none!important}
footer{max-width:1100px;margin:2rem auto;padding:1rem;border-top:1px solid var(--line);
color:var(--mut);font-size:.78rem}
footer code{word-break:break-all}
a{color:var(--accent)}
.empty{text-align:center;color:var(--mut);padding:3rem 1rem}
"""

JS = r"""
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let q='', facets={identity:new Set(),round:new Set(),flag:new Set()};

function esc(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function rx(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}

function matches(n){
  if(facets.round.size && !facets.round.has(n.round)) return false;
  if(facets.identity.size && !facets.identity.has(n.facet)) return false;
  for(const f of facets.flag){
    if(f==='corrected' && !n.correction) return false;
    if(f==='disputed' && n.status==='active') return false;
    if(f==='conflict' && !n.conflict) return false;
    if(f==='ballot' && !n.ballot) return false;
  }
  if(!q) return true;
  const hay=[n.identity,n.role,n.summary,n.text,n.note,n.correction,n.evidence,
             (n.durable||[]).join(' '),(n.claims||[]).join(' ')].join(' ').toLowerCase();
  return hay.includes(q.toLowerCase());
}

function highlight(el){
  $$('.node mark').forEach(m=>m.replaceWith(document.createTextNode(m.textContent)));
  if(!q) return;
  const re=new RegExp(rx(q),'gi');
  const walk=(node)=>{
    for(const c of [...node.childNodes]){
      if(c.nodeType===3){
        const t=c.textContent;
        if(re.test(t)){
          const span=document.createElement('span');
          span.innerHTML=esc(t).replace(new RegExp(rx(esc(q)),'gi'),m=>`<mark>${m}</mark>`);
          c.replaceWith(span);
        }
        re.lastIndex=0;
      } else if(c.nodeType===1 && c.tagName!=='MARK') walk(c);
    }
  };
  $$('.node:not(.hidden)').forEach(walk);
}

function apply(){
  let shown=0;
  for(const n of DATA.nodes){
    const el=document.getElementById('n-'+n.id);   // literal id: never CSS-escape here
    if(!el) continue;
    const ok=matches(n);
    el.classList.toggle('hidden',!ok);
    if(ok){shown++; if(q) el.classList.add('open');}
  }
  // a round header hides when nothing under it survives
  $$('.round').forEach(h=>{
    let sib=h.nextElementSibling, any=false;
    while(sib && !sib.classList.contains('round')){
      if(sib.classList.contains('node') && !sib.classList.contains('hidden')) any=true;
      sib=sib.nextElementSibling;
    }
    h.classList.toggle('hidden',!any);
  });
  $('#count').textContent=shown+' of '+DATA.nodes.length+' contributions';
  $('#empty').classList.toggle('hidden',shown>0);
  highlight();
}

function facet(kind,val,btn){
  const s=facets[kind];
  s.has(val)?s.delete(val):s.add(val);
  btn.setAttribute('aria-pressed',s.has(val));
  apply();
}

function init(){
  $('#q').addEventListener('input',e=>{q=e.target.value.trim();apply()});
  $('#q').addEventListener('keydown',e=>{if(e.key==='Escape'){e.target.value='';q='';apply()}});
  $$('[data-facet]').forEach(b=>b.addEventListener('click',()=>facet(b.dataset.facet,b.dataset.val,b)));
  $$('.nh').forEach(h=>h.addEventListener('click',()=>{
    const n=h.parentElement; n.classList.toggle('open');
    if(n.classList.contains('open')) history.replaceState(null,'','#'+n.id.slice(2));
  }));
  $('#expand').addEventListener('click',()=>$$('.node:not(.hidden)').forEach(n=>n.classList.add('open')));
  $('#collapse').addEventListener('click',()=>$$('.node').forEach(n=>n.classList.remove('open')));
  $('#theme').addEventListener('click',()=>{
    const cur=document.documentElement.getAttribute('data-theme');
    const next=cur==='dark'?'light':cur==='light'?'':'dark';
    next?document.documentElement.setAttribute('data-theme',next)
        :document.documentElement.removeAttribute('data-theme');
    $('#theme').textContent=next==='dark'?'dark':next==='light'?'light':'auto';
  });
  if(location.hash){
    const el=document.getElementById('n-'+location.hash.slice(1));
    if(el){el.classList.add('open');el.scrollIntoView()}
  }
  document.addEventListener('keydown',e=>{
    if(e.key==='/'&&e.target.tagName!=='INPUT'){e.preventDefault();$('#q').focus()}
  });
  apply();
}
document.addEventListener('DOMContentLoaded',init);
"""


def node_html(n: dict) -> str:
    e = html.escape
    tags = []
    if n["role"]:
        tags.append(f'<span class="tag">{e(n["role"])}</span>')
    if n["ballot"]:
        tags.append(f'<span class="tag b">{e(n["ballot"])}</span>')
    if n["status"] != "active":
        tags.append(f'<span class="tag d">{e(n["status"])}</span>')
    if n["correction"]:
        tags.append('<span class="tag w">corrected in round 01</span>')
    if n.get("phase") and n["phase"] != "unclassified":
        tags.append(f'<span class="tag">{e(n["phase"])}</span>')
    if not n["is_prompt"]:
        tags.append(f'<span class="tag">k={n["k"]}</span>')
    if n["label_absent"]:
        tags.append('<span class="tag d">no author label in raw</span>')

    meta = []
    if n["lines"]:
        meta.append(f'raw lines {n["lines"][0]}–{n["lines"][1]}')
    if n.get("captured"):
        meta.append(f'captured {e(n["captured"])}')
    if n.get("provider"):
        meta.append(e(n["provider"]))
    if n.get("citability"):
        meta.append(e(n["citability"]))
    if n.get("sha256"):
        meta.append(f'sha256 <code>{n["sha256"][:16]}…</code>')

    parts = [f'<div class="meta">{" · ".join(meta)}</div>'] if meta else []
    parts.append(f'<pre>{e(n["text"])}</pre>')

    if n["evidence"]:
        parts.append(f'<div class="box"><b>identity evidence</b>{e(n["evidence"])}</div>')
    if n["claims"]:
        items = "".join(f"<li>{e(c)}</li>" for c in n["claims"])
        parts.append(f'<div class="box"><b>key claims</b><ul>{items}</ul></div>')
    if n["durable"]:
        items = "".join(f"<li>{e(d)}</li>" for d in n["durable"])
        parts.append(f'<div class="box"><b>durable outputs adopted</b><ul>{items}</ul></div>')
    if n["superseded"]:
        items = "".join(f"<li>{e(s)}</li>" for s in n["superseded"])
        parts.append(f'<div class="box corr"><b>superseded</b><ul>{items}</ul></div>')
    if n["note"]:
        parts.append(f'<div class="box note"><b>annotator note — interpretation, not testimony</b>{e(n["note"])}</div>')
    if n["correction"]:
        parts.append(f'<div class="box corr"><b>correction, review round 01</b>{e(n["correction"])}</div>')
    if n["conflict"] and n["conflict"] != n["note"]:
        parts.append(f'<div class="box conf"><b>conflict of interest</b>{e(n["conflict"])}</div>')
    if n.get("prior_context"):
        parts.append(f'<div class="box"><b>context supplied to this reviewer</b>{e(n["prior_context"])}</div>')

    cls = "node" + (" child" if n["parent"] else "") + (" prompt" if n["is_prompt"] else "")
    if n["status"] != "active":
        cls += " disputed"

    summary = f'<p class="sum">{e(n["summary"])}</p>' if n["summary"] else ""
    return (
        f'<article class="{cls}" id="n-{e(n["id"])}">'
        f'<div class="nh"><span class="who">{e(n["identity"])}</span>{"".join(tags)}'
        f'<span class="tag">{e(n["id"])}</span></div>'
        f'{summary}<div class="body">{"".join(parts)}</div></article>'
    )


def build() -> str:
    nodes = build_founding_nodes() + build_review_nodes()
    for n in nodes:
        n["facet"] = facet_identity(n["identity"])
    identities = sorted({n["facet"] for n in nodes})

    transcript = REPO_ROOT / "corpus/raw/initial-transcript.txt"
    commit = head_commit()

    def facet_btn(kind, val, label=None):
        return (f'<button data-facet="{kind}" data-val="{html.escape(val)}" '
                f'aria-pressed="false">{html.escape(label or val)}</button>')

    round_titles = {"founding": "Founding deliberation — 2026-08-04 / 2026-08-05",
                    "review-round-01": "Review round 01 — adversarial audit of the annotations, 2026-08-05"}

    body = []
    for rnd in ("founding", "review-round-01"):
        group = [n for n in nodes if n["round"] == rnd]
        if not group:
            continue
        body.append(f'<h2 class="round">{html.escape(round_titles[rnd])}</h2>')
        body.extend(node_html(n) for n in group)

    data_json = json.dumps(
        [{k: n[k] for k in ("id", "round", "identity", "facet", "role", "summary", "text", "note",
                            "correction", "conflict", "ballot", "status", "durable", "claims",
                            "evidence")} for n in nodes],
        ensure_ascii=False, separators=(",", ":"),
    ).replace("</script>", "<\\/script>")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open ASI Governance Forum — threaded deliberation record</title>
<meta name="description" content="Threaded, searchable viewer over the OAGF deliberation record. Verbatim contributions with provenance, annotations shown as annotation, and corrections shown beside what they correct.">
<style>{CSS}</style>
</head>
<body>
<header><div class="hrow">
<h1>Open ASI Governance Forum<small>threaded deliberation record · annotation is not testimony</small></h1>
<input id="q" type="search" placeholder="Search verbatim text, summaries, notes and corrections…  (press /)" aria-label="Search">
<button id="expand">expand all</button>
<button id="collapse">collapse</button>
<button id="theme">auto</button>
</div></header>
<main>
<div class="bar"><span class="lbl">round</span>
{facet_btn("round", "founding", "founding")}
{facet_btn("round", "review-round-01", "review 01")}
</div>
<div class="bar"><span class="lbl">who</span>
{"".join(facet_btn("identity", i) for i in identities)}
</div>
<div class="bar"><span class="lbl">flags</span>
{facet_btn("flag", "corrected", "corrected in round 01")}
{facet_btn("flag", "disputed", "attribution disputed")}
{facet_btn("flag", "conflict", "declared conflict")}
{facet_btn("flag", "ballot", "carries a ballot")}
<span class="count" id="count"></span>
</div>
{"".join(body)}
<p class="empty hidden" id="empty">Nothing matches those filters.</p>
</main>
<footer>
<p><strong>What you are reading.</strong> Grey blocks are <em>verbatim</em> contributions. Boxes
labelled <em>annotator note</em> are interpretation by Claude Code, an Anthropic invocation surface
that is a party to this record — not testimony. Corrections are shown <em>beside</em> what they
correct and never replace it.</p>
<p><strong>Identity filters are normalised.</strong> <code>segments.json</code> records identity
with the provider inline ("Grok (xAI)") while contribution records keep them as separate fields
("Grok" + "xAI"). That is an inconsistency between two artifact families of this repository, not
two parties. Filtering groups them; each contribution still shows the identity exactly as its own
record states it. Distinct <em>models</em> — Claude Opus 5, Claude Fable 5, Claude Code — are never
merged.</p>
<p><strong>Provenance.</strong> Founding record
<code>{sha256_of(transcript)}</code> · generated from commit <code>{commit}</code> ·
{len(nodes)} contributions. Regenerate with <code>python3 tools/build_viewer.py</code> and diff.</p>
<p>Every contribution here is a single sample (k=1) — citable as an artifact of that invocation,
not as evidence of any model's stable position. See
<a href="https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/deficiencies.md">the deficiency register</a>
({deficiency_count()} open) before citing anything.</p>
<p>No output in this repository is an institutional statement by xAI, OpenAI, Google DeepMind or
Anthropic. Custodian: Stephen Reed. Corpus CC BY 4.0; code Apache-2.0.
<a href="https://github.com/open-asi-governance/open-asi-governance-forum">Source</a></p>
</footer>
<script>const DATA={{nodes:{data_json}}};{JS}</script>
</body>
</html>
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    (OUT.parent / ".nojekyll").write_text("", encoding="utf-8")
    page = build()
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO_ROOT)} — {len(page):,} bytes")
    print(f"  sha256 {hashlib.sha256(page.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
