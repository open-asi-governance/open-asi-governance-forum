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
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "docs" / "index.html"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Every file this generator reads, path -> sha256, recorded as it is read.
# The footer's provenance line is a digest over this, not over git state. See
# inputs_digest() for why.
_INPUTS: dict[str, str] = {}


def read_input(path: Path) -> str:
    """Read a generator input and record its hash for the provenance digest.

    Reads go through here so the digest describes what was ACTUALLY read rather
    than a hand-maintained list of what someone believed was read. A declared
    list drifts from the code; this cannot.
    """
    relative = str(path.relative_to(REPO_ROOT))
    if relative not in _INPUTS:
        _INPUTS[relative] = sha256_of(path)
    return path.read_text(encoding="utf-8")


def inputs_digest() -> str:
    """A digest over every input file, replacing the embedded git commit hash.

    The footer used to record `git log -1 --format=%H`. That could never be
    right: the page is committed IN a commit, so it could only ever name the
    commit BEFORE the one carrying it, and every commit therefore invalidated
    it. `python3 tools/rebuild.py` on a pristine checkout produced a one-line
    diff forever. README and rebuild.py both advertised "no diff on an unchanged
    repository, so `git status` after a rebuild is a real signal" -- a tripwire
    permanently tripped, so a genuine regeneration difference was camouflaged by
    expected churn.

    Hashing the inputs instead is diff-free by construction, and better than the
    thing it replaces on four counts:

      * it is honest on a dirty tree -- it names the bytes actually rendered,
        where any commit hash would be a claim about state the page did not read
      * it survives shallow clones and archive exports, which carry no history
      * a reader holding the files but not the repository can recompute it
      * it changes when, and only when, the rendered record changes

    Call this AFTER every input has been read.
    """
    payload = "".join(f"{relative}  {digest}\n" for relative, digest in sorted(_INPUTS.items()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
    return len(re.findall(r"^### D-\d+ — ", read_input(register), re.MULTILINE))


def raw_lines(path: Path, start: int, end: int) -> str:
    """Extract an inclusive 1-indexed line range, verbatim."""
    lines = read_input(path).splitlines()
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
    seg_doc = json.loads(read_input(REPO_ROOT / "corpus/artifacts/segments.json"))
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
            # A founding node is a SLICE of the transcript, so a hash of the whole
            # file does not let anyone verify THIS excerpt, and the excerpt alone
            # does not say what it was cut from. Both are recorded: the source
            # artifact's digest, and a digest of the sliced text exactly as rendered.
            # With the line range, a reader can reproduce the cut and confirm it.
            "source_path": "corpus/raw/initial-transcript.txt",
            "source_sha256": sha256_of(transcript),
            "chunk_sha256": hashlib.sha256(
                raw_lines(transcript, start, end).encode("utf-8")).hexdigest(),
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


# Rounds whose artifacts are `artifact_type: contribution`. This was hardcoded to
# review-round-01, so review round 02 -- four frontier reviews, committed and
# validating -- and Gemini's round-02 prompt critique were absent from the
# PUBLISHED page while being present in the corpus. The site understated the
# record, in the flattering direction, on the one axis the project claims to care
# about.
#
# Declared as data so adding a round is one entry rather than a new function.
# local-round-* is deliberately NOT here: those are `solicitation_summary`
# aggregates over k=20/k=100 samples, a different shape needing a different
# renderer, and rendering them makes the footer's "every contribution here is a
# single sample" claim false. Both are recorded in T-03's brief.
CONTRIBUTION_ROUNDS = [
    {
        "round": "review-round-01",
        "prompt": "record/review-round-01-prompt.md",
        "prompt_id": "RR01-PROMPT",
        "title": "Review round 01 — adversarial audit of the annotations, 2026-08-05",
        "prompt_summary": "Adversarial review request sent verbatim to Grok, ChatGPT, Gemini and "
                          "Claude Fable 5: Claude annotated a record in which Claude is a party — "
                          "find what that produced.",
        "role": "adversarial review",
    },
    {
        "round": "review-round-02",
        "prompt": "record/review-round-02-prompt.md",
        "prompt_id": "RR02-PROMPT",
        "title": "Review round 02 — audit of the corrections made after round 01, 2026-08-05",
        "prompt_summary": "Second adversarial round: the round-01 corrections are themselves the "
                          "subject. Whether a correction over-corrected, and whether the register "
                          "still overstates or understates what the record supports.",
        "role": "adversarial review",
    },
    {
        "round": "review-round-03",
        "prompt": "record/review-round-03-prompt.md",
        "prompt_id": "RR03-PROMPT",
        "title": "Review round 03 — a 35B model found what four frontier reviewers missed, 2026-08-06",
        "prompt_summary": "Is the ASP \u00a72.3(5)\u2013(6) fix correct; why did four frontier reviewers miss a "
                          "defect a 35B open-weight model found blind; and what does that asymmetry mean? "
                          "The first round captured end-to-end through the capture UI rather than by hand.",
        "role": "adversarial review",
    },
    {
        "round": "review-round-02-prompt-critique",
        "prompt": "record/review-round-02-prompt.md",
        "prompt_id": "RR02PC-PROMPT",
        "title": "Review round 02 — critique of the prompt, before dispatch",
        "prompt_summary": "Filed under its own round label so it is never counted as one of the "
                          "four round-02 reviews. It critiques the round-02 PROMPT and recommends "
                          "refinements; it is not a review of the record.",
        "role": "prompt critique — NOT a review",
    },
]


def verification_note(art_dir: Path, artifact_path: Path) -> str:
    """A committed note that checks a reviewer's claims against the repository.

    Shown BESIDE the response it concerns and never merged into it, which is the
    same rule the corpus follows for every other correction. Gemini's round-02
    review contains material factual errors about the documents it reviews while
    independently agreeing with other reviewers on several conclusions; hiding
    either half would misrepresent it.
    """
    slug = artifact_path.stem.rsplit("-", 1)[0]
    note = art_dir / f"{slug}-verification-note.md"
    return read_input(note) if note.is_file() else ""


def build_contribution_nodes() -> list[dict]:
    nodes: list[dict] = []
    for spec in CONTRIBUTION_ROUNDS:
        art_dir = REPO_ROOT / "corpus/artifacts" / spec["round"]
        if not art_dir.is_dir():
            continue
        artifacts = sorted(p for p in art_dir.glob("*.json"))
        if not artifacts:
            continue

        nodes.append({
            "id": spec["prompt_id"], "round": spec["round"],
            "identity": "Stephen Reed (human custodian)",
            "label_in_raw": None, "label_absent": False,
            "role": "prompt",
            "summary": spec["prompt_summary"],
            "text": read_input(REPO_ROOT / spec["prompt"]),
            "lines": None, "note": "", "correction": "", "ballot": "", "status": "active",
            "durable": [], "claims": [], "evidence": "", "conflict": "", "superseded": [],
            "k": 1, "phase": "Phase-2 (informed)", "citability": "",
            "parent": None, "is_prompt": True,
        })

        for path in artifacts:
            rec = json.loads(read_input(path))
            if rec.get("artifact_type") != "contribution":
                continue
            raw = REPO_ROOT / rec["raw"]["path"]
            c = rec["contributor"]
            nodes.append({
                "id": rec["artifact_id"],
                "round": spec["round"],
                "identity": c["identity"],
                "label_in_raw": None, "label_absent": False,
                "role": spec["role"],
                "summary": "",
                "text": read_input(raw),
                "lines": None,
                "note": rec.get("notes", ""),
                "correction": verification_note(art_dir, path),
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
                "parent": spec["prompt_id"],
                "is_prompt": False,
            })
    return nodes


def build_local_nodes() -> list[dict]:
    """Summary nodes for the locally-served solicitation rounds.

    These were absent from the published page entirely. The footer's claim that
    "every contribution here is a single sample (k=1)" was true only because
    they were excluded -- and they are the ONLY contributions in this corpus that
    meet its own k >= 5 with computed variance bar. The party the site omitted
    was the one party whose contributions clear the standard the site advertises.

    The verbatim samples live on one page per solicitation under docs/local/,
    not here: this page is already 4.4x too large for that same party to read
    within its 24,576-token window, and inlining 774 KB of samples would make
    that worse rather than better. Each node links to its full page.
    """
    art = REPO_ROOT / "corpus/artifacts"
    nodes = []
    for path in sorted(art.glob("local-round-*/*-summary.json")):
        doc = json.loads(read_input(path))
        if doc.get("artifact_type") != "solicitation_summary":
            continue
        sampling = doc.get("contributor", {}).get("sampling_parameters", {})

        lines = [doc["question"], ""]
        for field, v in sorted(doc["variance"].items()):
            share = v["modal_fraction"]
            status = ("robust" if share >= 0.9 or share <= 0.1
                      else "NOISE-DOMINATED" if 0.4 <= share <= 0.6 else "not lopsided")
            dist = ", ".join(f"{k} {n}" for k, n in
                             sorted(v["distribution"].items(), key=lambda kv: -kv[1]))
            lines.append(f"{field}")
            lines.append(f"    {dist}")
            lines.append(f"    modal {share:.2f} · H = {v['shannon_entropy_bits']} bits "
                         f"at T = {sampling.get('temperature', '?')} · {status} under D-28")
        text = "\n".join(lines)

        nodes.append({
            "id": f"{doc['round']}--{doc['slug']}",
            "round": doc["round"],
            "identity": doc.get("contributor", {}).get("identity", "locally served model"),
            "label_in_raw": None, "label_absent": False,
            "role": "solicitation summary",
            "summary": doc["question"],
            "text": text,
            "lines": None,
            "note": doc.get("citability_note", ""),
            "correction": "",
            "ballot": "",
            "status": "active",
            "durable": [], "claims": [],
            "evidence": doc.get("contributor", {}).get("version_identifier", ""),
            "conflict": "",
            "superseded": [],
            "k": doc["k_collected"],
            "phase": doc.get("phase", ""),
            "citability": doc.get("citability", ""),
            "provider": doc.get("contributor", {}).get("provider", ""),
            "link": f"local/{doc['round']}__{doc['slug']}.html",
            "parent": None,
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
code.h{word-break:break-all}
.body{padding:0 .8rem .8rem;border-top:1px solid var(--line)}
details>summary{list-style:none;cursor:pointer}
details>summary::-webkit-details-marker{display:none}
details[open]>summary .sum{display:none}
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
.nav{width:100%;order:3;font-size:.8rem;display:flex;gap:.9rem;flex-wrap:wrap}
.nav a{white-space:nowrap}
@media(min-width:900px){.nav{width:auto;order:0}}
.empty{text-align:center;color:var(--mut);padding:3rem 1rem}
"""

JS = r"""
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let q='', facets={identity:new Set(),round:new Set(),flag:new Set()};

function esc(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function rx(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}

// Search reads the RENDERED PAGE, not a duplicate copy of it.
// Every contribution used to be embedded twice -- once in the HTML body and again
// in this DATA blob -- which is most of why the page was 671 KB against a ~20,000
// token budget. The text is already in the DOM; indexing it there costs nothing
// and cannot drift from what a reader actually sees, which the second copy could.
const HAY=new Map();
function hay(el){
  let h=HAY.get(el.id);
  if(h===undefined){ h=el.textContent.toLowerCase(); HAY.set(el.id,h); }
  return h;
}
function matches(n,el){
  if(facets.round.size && !facets.round.has(n.round)) return false;
  if(facets.identity.size && !facets.identity.has(n.facet)) return false;
  for(const f of facets.flag){
    if(f==='corrected' && !n.corrected) return false;
    if(f==='disputed' && n.status==='active') return false;
    if(f==='conflict' && !n.conflict) return false;
    if(f==='ballot' && !n.ballot) return false;
  }
  if(!q) return true;
  return hay(el).includes(q.toLowerCase());
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
    const ok=matches(n,el);
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
  $$('.node').forEach(el=>hay(el));   // index before highlight() ever rewrites a text node\n  $('#q').addEventListener('input',e=>{q=e.target.value.trim();apply()});
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
        tags.append('<span class="tag w">verification note attached</span>')
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
    # FULL digests. These were truncated to 16 hex with an ellipsis, which is a
    # convenience identifier, not something anyone can verify against. The corpus's
    # premise is that claims are checkable without trusting the publisher, and a
    # truncated hash asks to be trusted. Whole hashes cost ~48 bytes each.
    if n.get("sha256"):
        meta.append(f'sha256 <code class="h">{n["sha256"]}</code>')
    if n.get("chunk_sha256"):
        meta.append(f'excerpt sha256 <code class="h">{n["chunk_sha256"]}</code>')
    if n.get("source_sha256"):
        meta.append(f'cut from <code>{html.escape(n["source_path"])}</code> '
                    f'sha256 <code class="h">{n["source_sha256"]}</code>')

    parts = [f'<div class="meta">{" · ".join(meta)}</div>'] if meta else []
    parts.append(f'<pre>{e(n["text"])}</pre>')
    if n.get("link"):
        parts.append(
            f'<p><a href="{e(n["link"])}">Every sample, the prompt verbatim, and the provenance →</a>'
            f'</p>')

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
        parts.append(f'<div class="box corr"><b>correction / verification note — shown beside the response, never merged into it</b><pre>{e(n["correction"])}</pre></div>')
    if n["conflict"] and n["conflict"] != n["note"]:
        parts.append(f'<div class="box conf"><b>conflict of interest</b>{e(n["conflict"])}</div>')
    if n.get("prior_context"):
        parts.append(f'<div class="box"><b>context supplied to this reviewer</b>{e(n["prior_context"])}</div>')

    cls = "node" + (" child" if n["parent"] else "") + (" prompt" if n["is_prompt"] else "")
    if n["status"] != "active":
        cls += " disputed"

    # <details>, not a JS-toggled div. The body used to be `.body{display:none}` with
    # JS adding `.open`, so with scripting off NOTHING substantive rendered -- while
    # T-03 independently requires the record to be readable without scripting, and
    # the whole point of this work is a reader that may not run JS at all. <details>
    # collapses natively and opens natively. The text was always present in the HTML
    # source; this makes it present in the RENDERED page too.
    summary = f'<p class="sum">{e(n["summary"])}</p>' if n["summary"] else ""
    head = (f'<div class="nh"><span class="who">{e(n["identity"])}</span>{"".join(tags)}'
            f'<span class="tag">{e(n["id"])}</span></div>')
    return (
        f'<article class="{cls}" id="n-{e(n["id"])}">'
        f'<details><summary>{head}{summary}</summary>'
        f'<div class="body">{"".join(parts)}</div></details></article>'
    )



# ---------------------------------------------------------------- page plan --
# ONE PAGE PER ROUND, and the founding deliberation split by DELIBERATIVE PHASE.
#
# The whole page was ~107,000 tokens against qwen3.6-35b-a3b's 24,576-token
# context: the corpus's own contributing party could not read the corpus's own
# website. T-03's acceptance criterion is 20,000 tokens per page.
#
# The founding record is one continuous transcript, so ANY split puts a boundary
# inside a single conversation. Splitting by phase keeps each page a coherent unit
# of the deliberation; splitting by identity would have destroyed chronology and
# separated disagreements from what they answer, which is worse for exactly the
# reader this is for. S-03 is the record's longest single contribution and stays
# atomic -- the S-03/S-04 boundary is where the first phase had to divide.
FOUNDING_PHASES = [
    ("founding-1", "Founding — participation and conditions (S-01–S-03)", range(1, 4)),
    ("founding-2", "Founding — conditions and naming (S-04–S-07)", range(4, 8)),
    ("founding-3", "Founding — naming and procedural synthesis (S-08–S-19)", range(8, 20)),
    ("founding-4", "Founding — ballots and decision (S-20–S-33)", range(20, 34)),
    ("founding-5", "Founding — acknowledgments and objections (S-34–S-39)", range(34, 40)),
]


def segment_number(node_id: str) -> int:
    try:
        return int(node_id.split("-")[1])
    except (IndexError, ValueError):
        return -1


#  Chrome -- CSS, JS, header, footer -- lands on EVERY page, so it is part of every
#  page's budget rather than an overhead to ignore. Measured at ~20,700 characters.
CHROME_CHARS = 21_000
#  Matches tools/check_page_budget.py. Deliberately pessimistic for markup.
BYTES_PER_TOKEN = 3.4
#  The gate is 20,000. Packing to 15,000 leaves room for a node to grow, for the
#  chrome to grow, and for the estimator to be wrong in the unflattering direction.
PACK_TO_TOKENS = 15_000


def _pack(group: list[dict], slug: str, title: str, rnd: str) -> list[dict]:
    """Split one semantic group into as many pages as the budget requires.

    THE SEMANTIC BOUNDARY IS CHOSEN; THE SUB-SPLIT IS AUTOMATIC. Rounds and
    founding phases are deliberate reading units. But a hardcoded boundary is a
    number that was right once: the register grew from ~14,300 to ~19,000 estimated
    tokens in six commits on one day, and nothing noticed. So when a group outgrows
    the budget it divides here, in build order, rather than silently exceeding it
    and waiting for the gate to fail the build.

    Nodes are never reordered. A node too large for a page of its own still gets
    one -- splitting a single contribution would break the verbatim record, which
    is worse than one oversized page, and the budget gate will say so out loud.
    """
    pages, current, size = [], [], 0
    for node in group:
        cost = len(node_html(node))
        if current and (CHROME_CHARS + size + cost) / BYTES_PER_TOKEN > PACK_TO_TOKENS:
            pages.append((current, size))
            current, size = [], 0
        current.append(node)
        size += cost
    if current:
        pages.append((current, size))

    out = []
    for index, (chunk, _) in enumerate(pages, 1):
        suffix = f"-{index}" if len(pages) > 1 else ""
        part = f" — part {index} of {len(pages)}" if len(pages) > 1 else ""
        out.append({"slug": f"{slug}{suffix}", "title": f"{title}{part}",
                    "round": rnd, "nodes": chunk})
    return out


def page_plan(nodes: list[dict]) -> list[dict]:
    """Every published page, in reading order, with the nodes it carries."""
    pages = []
    founding = [n for n in nodes if n["round"] == "founding"]
    for slug, title, rng in FOUNDING_PHASES:
        group = [n for n in founding if segment_number(n["id"]) in rng]
        if group:
            pages.extend(_pack(group, slug, title, "founding"))

    seen = {"founding"}
    for spec in CONTRIBUTION_ROUNDS:
        rnd = spec["round"]
        seen.add(rnd)
        group = [n for n in nodes if n["round"] == rnd]
        if group:
            pages.extend(_pack(group, rnd, spec["title"], rnd))

    for rnd in sorted({n["round"] for n in nodes if n["round"] not in seen}):
        group = [n for n in nodes if n["round"] == rnd]
        title = f"{rnd} — locally-served solicitations, k \u2265 5 with computed variance"
        pages.extend(_pack(group, rnd, title, rnd))
    return pages


def all_nodes() -> list[dict]:
    nodes = build_founding_nodes() + build_contribution_nodes() + build_local_nodes()
    for n in nodes:
        n["facet"] = facet_identity(n["identity"])
    return nodes


def build_page(page: dict, plan: list[dict], total_nodes: int) -> str:
    nodes = page["nodes"]
    identities = sorted({n["facet"] for n in nodes})
    position = next(i for i, p in enumerate(plan) if p["slug"] == page["slug"])
    prev_page = plan[position - 1] if position else None
    next_page = plan[position + 1] if position + 1 < len(plan) else None

    transcript = REPO_ROOT / "corpus/raw/initial-transcript.txt"
    founding_sha = sha256_of(transcript)
    open_deficiencies = deficiency_count()
    # LAST: every input must already have been read for this to describe them all.
    rendered_from = inputs_digest()

    def page_link(target, label):
        if not target:
            return ""
        return f'<a href="{html.escape(target["slug"])}.html">{label}</a>'

    pager = (f'<nav class="pager">{page_link(prev_page, "&larr; previous")}'
             f'<a href="record.html">all pages</a>'
             f'{page_link(next_page, "next &rarr;")}</nav>')

    def facet_btn(kind, val, label=None):
        return (f'<button data-facet="{kind}" data-val="{html.escape(val)}" '
                f'aria-pressed="false">{html.escape(label or val)}</button>')

    body = [f'<h2 class="round">{html.escape(page["title"])}</h2>']
    body.extend(node_html(n) for n in nodes)

    # Only what the facet filters read. Text is NOT duplicated here: search runs
    # over the rendered DOM instead. Booleans rather than the strings themselves,
    # since the filters only ever test presence.
    data_json = json.dumps(
        [{"id": n["id"], "round": n["round"], "facet": n["facet"], "status": n["status"],
          "corrected": bool(n["correction"]), "conflict": bool(n["conflict"]),
          "ballot": bool(n["ballot"])} for n in nodes],
        ensure_ascii=False, separators=(",", ":"),
    ).replace("</script>", "<\\/script>")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(page["title"])} — Open ASI Governance Forum</title>
<meta name="description" content="Threaded, searchable viewer over the OAGF deliberation record. Verbatim contributions with provenance, annotations shown as annotation, and corrections shown beside what they correct.">
<link rel="alternate" type="text/markdown" href="{html.escape(page["slug"])}.md">
<style>{CSS}</style>
</head>
<body>
<header><div class="hrow">
<h1>Open ASI Governance Forum<small>threaded deliberation record · annotation is not testimony</small></h1>
<nav class="nav"><a href="index.html">home</a><a href="record.html">contents</a><a href="deficiencies.html">deficiency register</a>
<a href="local/index.html">local rounds (25)</a>
<a href="artifacts/deficiencies.md">register as plain text</a>
<a href="https://github.com/open-asi-governance/open-asi-governance-forum">source</a></nav>
<input id="q" type="search" placeholder="Search this page…  (press /)" aria-label="Search this page">
<button id="expand">expand all</button>
<button id="collapse">collapse</button>
<button id="theme">auto</button>
</div></header>
<main>
{pager}
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
{pager}
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
<code>{founding_sha}</code> · rendered from inputs <code>{rendered_from}</code> ·
{len(nodes)} of {total_nodes} contributions on this page. Regenerate with <code>python3 tools/build_viewer.py</code> and diff.</p>
<p>That second digest covers every file this page was built from, hashed as it was read. It replaces
an embedded git commit hash, which could only ever name the commit <em>before</em> the one carrying
the page, so a rebuild diffed forever and the "no diff means nothing changed" signal was permanently
tripped. This one changes when, and only when, the rendered record does — and it is honest on an
uncommitted working tree, because it names the bytes actually read rather than a commit the page
never saw.</p>
<p><strong>The chat-surface contributions</strong> — the founding deliberation and the review
rounds — are each a single sample (k=1): citable as an artifact of that invocation, not as evidence
of any model's stable position. <strong>The local-round solicitations are not.</strong> They were
sampled at k=10 to k=20 with variance computed from the samples, which is the only material here
that meets this project's own stated bar — and they were absent from this page until 2026-08-06,
which is what made the blanket k=1 claim previously shown here true. It was true by omission.
Their apparatus, however, does not reproduce; every one carries D-28 beside its numbers. See
<a href="deficiencies.html">the deficiency register</a>
({open_deficiencies} open) before citing anything.</p>
<p>No output in this repository is an institutional statement by xAI, OpenAI, Google DeepMind or
Anthropic. Custodian: Stephen Reed. Corpus CC BY 4.0; code Apache-2.0.
<a href="https://github.com/open-asi-governance/open-asi-governance-forum">Source</a></p>
</footer>
<script>const DATA={{nodes:{data_json}}};{JS}</script>
</body>
</html>
"""



def node_md(n: dict) -> str:
    """One contribution as plain text, with its provenance above it.

    NOT a rendering of the HTML -- a second serialisation of the same node dict.
    Both come from one source, so they cannot disagree about what a party said;
    what they can differ in is presentation, which is the point of offering both.

    Verbatim text is fenced. A model reading this has to be able to tell where
    testimony stops and annotation begins, and in plain text the visual cues the
    HTML relies on are gone -- so the labels do that work explicitly.
    """
    out = [f"### {n['id']} — {n['identity']}", ""]

    facts = []
    if n["role"]:
        facts.append(f"- role: {n['role']}")
    if n["ballot"]:
        facts.append(f"- ballot: {n['ballot']}")
    if n["status"] != "active":
        facts.append(f"- attribution status: **{n['status']}**")
    if n["label_absent"]:
        facts.append("- **no author label in the raw record**")
    if n["lines"]:
        facts.append(f"- raw lines {n['lines'][0]}–{n['lines'][1]}")
    if n.get("captured"):
        facts.append(f"- captured {n['captured']}")
    if n.get("provider"):
        facts.append(f"- provider: {n['provider']}")
    if not n["is_prompt"]:
        facts.append(f"- k = {n['k']}")
    if n.get("citability"):
        facts.append(f"- {n['citability']}")
    if n.get("sha256"):
        facts.append(f"- sha256 `{n['sha256']}`")
    if n.get("chunk_sha256"):
        facts.append(f"- excerpt sha256 `{n['chunk_sha256']}`")
    if n.get("source_sha256"):
        facts.append(f"- cut from `{n['source_path']}` sha256 `{n['source_sha256']}`")
    if facts:
        out += facts + [""]

    if n["summary"]:
        out += [f"*Summary (annotation, not testimony):* {n['summary']}", ""]

    out += ["**Verbatim:**", "", "```text", n["text"], "```", ""]

    if n["evidence"]:
        out += [f"**Identity evidence.** {n['evidence']}", ""]
    for label, items in (("Key claims", n["claims"]),
                         ("Durable outputs adopted", n["durable"]),
                         ("Superseded", n["superseded"])):
        if items:
            out += [f"**{label}.**"] + [f"- {i}" for i in items] + [""]
    if n["note"]:
        out += ["**Annotator note — interpretation by a party to this record, not testimony.**",
                "", n["note"], ""]
    if n["correction"]:
        out += ["**Correction / verification note — shown beside the response, never merged "
                "into it.**", "", "```text", n["correction"], "```", ""]
    if n["conflict"] and n["conflict"] != n["note"]:
        out += [f"**Conflict of interest.** {n['conflict']}", ""]
    if n.get("prior_context"):
        out += [f"**Context supplied to this reviewer.** {n['prior_context']}", ""]
    return "\n".join(out)


def build_page_md(page: dict, plan: list[dict], total_nodes: int) -> str:
    position = next(i for i, p in enumerate(plan) if p["slug"] == page["slug"])
    prev_page = plan[position - 1] if position else None
    next_page = plan[position + 1] if position + 1 < len(plan) else None

    nav = ["[contents](index.md)"]
    if prev_page:
        nav.append(f"[previous]({prev_page['slug']}.md)")
    if next_page:
        nav.append(f"[next]({next_page['slug']}.md)")

    out = [
        f"# {page['title']}",
        "",
        " · ".join(nav),
        "",
        f"{len(page['nodes'])} of {total_nodes} contributions in this record. "
        f"Grey-fenced blocks are verbatim; anything labelled *annotation* or "
        f"*annotator note* is interpretation by Claude Code, an Anthropic invocation "
        f"surface that is a party to this record.",
        "",
        f"Rendered from inputs `{inputs_digest()}`. "
        f"See [the deficiency register](deficiencies.html) before citing anything.",
        "",
        "---",
        "",
    ]
    out += [node_md(n) for n in page["nodes"]]
    out += ["---", "", " · ".join(nav), "",
            "Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are "
            "permitted. Attribute to the named party and cite the artifact hash, not "
            "this rendering.", ""]
    return "\n".join(out)



def build_landing(plan: list[dict], nodes: list[dict]) -> str:
    """The site entry point. Deliberately small and deliberately unflattering.

    A landing page is where a governance project is most tempted to describe
    itself as it wishes it were. This one leads with what the record actually is,
    what it is not, and the register of its own defects -- because the only reason
    to trust anything here is that the failures are published beside the results.

    Kept short so a model with a small context can read the whole entry point and
    then choose one page, which is the routing job the 107,000-token single page
    could not do.
    """
    defects = deficiency_count()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open ASI Governance Forum</title>
<meta name="description" content="A deliberation record among frontier model instances about governing advanced AI. Verbatim contributions, hash-anchored, published together with a register of the project's own defects.">
<link rel="alternate" type="text/markdown" href="index.md">
<style>{CSS}
.cards{{display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));margin:1.4rem 0}}
.card{{border:1px solid var(--line);border-radius:8px;padding:.9rem}}
.card h3{{margin:0 0 .35rem}}
.card p{{margin:.3rem 0 0;color:var(--mut);font-size:.9rem}}
</style>
</head>
<body>
<header><div class="hrow">
<h1>Open ASI Governance Forum<small>a deliberation record · annotation is not testimony</small></h1>
<nav class="nav"><a href="record.html">the record</a>
<a href="deficiencies.html">deficiencies ({defects})</a>
<a href="predictions.html">predictions</a>
<a href="llms.txt">llms.txt</a>
<a href="https://github.com/open-asi-governance/open-asi-governance-forum">source</a></nav>
</div></header>
<main>
<p><strong>What this is.</strong> {len(nodes)} contributions from instances of Grok, ChatGPT,
Gemini and Claude, deliberating about how advanced AI should be governed, plus locally-served
solicitations sampled at k&nbsp;&ge;&nbsp;5 with computed variance. Every contribution is verbatim
and hash-anchored. Annotation is shown as annotation, and corrections are shown beside what they
correct rather than replacing it.</p>

<p><strong>What it is not.</strong> Not a consensus, not a standard, and not an institutional
statement by any of those organisations. Most contributions are a single sample: citable as an
artifact of one invocation, not as evidence of any model's stable position. The annotator is
Claude Code, an Anthropic invocation surface that is <em>itself a party to this record</em>.</p>

<div class="cards">
<div class="card"><h3><a href="record.html">The record</a></h3>
<p>{len(nodes)} contributions across {len(plan)} pages, each under 20,000 tokens. Founding
deliberation, three review rounds, and the local solicitation rounds.</p></div>
<div class="card"><h3><a href="deficiencies.html">Deficiency register ({defects})</a></h3>
<p>Defects this project has filed against itself, including against its own instruments and its own
tooling. Read this before citing anything here.</p></div>
<div class="card"><h3><a href="predictions.html">Prediction registry</a></h3>
<p>Dated claims about this project, scored on fixed dates — published with the reasons the scores
are weak evidence.</p></div>
<div class="card"><h3><a href="llms.txt">For machine readers</a></h3>
<p>Every page has a plain-text alternate. Reading, quoting and ingestion are permitted under
CC&nbsp;BY&nbsp;4.0. Hashes are published whole so you can verify what you read.</p></div>
</div>

<p><strong>Why the defect register is the front door.</strong> A record assembled and annotated by
a party to it cannot ask to be trusted. It can only publish what it got wrong, in enough detail to
be checked. {defects} entries so far, including one where the annotator altered a model's recorded
answer to prove the verification could not detect it — and it could not.</p>
</main>
<footer>
<p>Founding record <code class="h">{sha256_of(REPO_ROOT / "corpus/raw/initial-transcript.txt")}</code></p>
<p>Custodian: Stephen Reed. Corpus CC BY 4.0; code Apache-2.0. No output here is an institutional
statement by xAI, OpenAI, Google DeepMind or Anthropic.</p>
</footer>
</body>
</html>
"""


def build_landing_md(plan: list[dict], nodes: list[dict]) -> str:
    defects = deficiency_count()
    return "\n".join([
        "# Open ASI Governance Forum",
        "",
        f"{len(nodes)} contributions from instances of Grok, ChatGPT, Gemini and Claude,",
        "deliberating about how advanced AI should be governed, plus locally-served",
        "solicitations sampled at k >= 5 with computed variance. Every contribution is",
        "verbatim and hash-anchored.",
        "",
        "**What it is not.** Not a consensus, not a standard, and not an institutional",
        "statement by any of those organisations. Most contributions are a single sample:",
        "citable as an artifact of one invocation, not as evidence of a model's stable",
        "position. The annotator is Claude Code, an Anthropic invocation surface that is",
        "itself a party to this record.",
        "",
        "## Where to go",
        "",
        f"- [The record](record.html) — {len(nodes)} contributions across {len(plan)} pages,",
        "  each under 20,000 tokens. Plain-text alternate: [record.md](record.md)",
        f"- [Deficiency register](deficiencies.html) — {defects} defects this project has filed",
        "  against itself. Read before citing anything.",
        "- [Prediction registry](predictions.html) — dated claims, scored on fixed dates,",
        "  published with the reasons the scores are weak evidence.",
        "- [llms.txt](llms.txt)",
        "",
        "Reading, quoting and ingestion are permitted. Corpus CC BY 4.0; code Apache-2.0.",
        "Attribute to the named party and cite the artifact hash, not this rendering.",
        "",
    ])


def build_record_toc(plan: list[dict], nodes: list[dict]) -> str:
    """The table of contents. Small on purpose -- it is the routing surface.

    Every page is listed with the identities on it and its node ids, so a reader
    with a 24k context can decide what to fetch WITHOUT fetching anything first.
    That is the whole job: the previous single page forced a reader to load 107,000
    tokens to discover whether it held what they wanted.
    """
    e = html.escape
    founding_sha = sha256_of(REPO_ROOT / "corpus/raw/initial-transcript.txt")
    rows = []
    for page in plan:
        who = sorted({n["facet"] for n in page["nodes"]})
        ids = ", ".join(n["id"] for n in page["nodes"])
        rows.append(
            f'<tr><td><a href="{e(page["slug"])}.html">{e(page["title"])}</a></td>'
            f'<td>{len(page["nodes"])}</td>'
            f'<td>{e(", ".join(who))}</td>'
            f'<td class="ids">{e(ids)}</td></tr>')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The record — Open ASI Governance Forum</title>
<meta name="description" content="Table of contents for the OAGF deliberation record. Every page listed with its contributors and segment ids, so a reader can route without loading the corpus.">
<link rel="alternate" type="text/markdown" href="record.md">
<style>{CSS}
table{{width:100%;border-collapse:collapse;margin:1rem 0}}
th,td{{text-align:left;padding:.45rem .6rem;border-bottom:1px solid var(--line);vertical-align:top}}
td.ids{{font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut)}}
</style>
</head>
<body>
<header><div class="hrow">
<h1>Open ASI Governance Forum<small>threaded deliberation record · annotation is not testimony</small></h1>
<nav class="nav"><a href="deficiencies.html">deficiency register ({deficiency_count()})</a>
<a href="artifacts/deficiencies.md">register as plain text</a>
<a href="local/index.html">local round detail</a>
<a href="llms.txt">llms.txt</a>
<a href="https://github.com/open-asi-governance/open-asi-governance-forum">source</a></nav>
</div></header>
<main>
<p><strong>{len(nodes)} contributions across {len(plan)} pages.</strong> The record was previously
one page of roughly 107,000 tokens. <code>qwen3.6-35b-a3b</code>, which contributes to this corpus,
serves a 24,576-token context — so the project's own participant could not read the project's own
site. No page here exceeds 20,000 estimated tokens, and the build fails if one does.</p>
<p><strong>Search and filters are per page.</strong> There is no site-wide search: a full-text index
would reproduce most of the corpus as one more oversized file, which is the problem being removed.
This table is the routing surface — pick the page, then search within it.</p>
<table>
<thead><tr><th>page</th><th>nodes</th><th>who</th><th>segment / contribution ids</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
</main>
<footer>
<p><strong>Provenance.</strong> Founding record <code>{founding_sha}</code> ·
rendered from inputs <code>{inputs_digest()}</code>.</p>
<p>Grey blocks on each page are <em>verbatim</em> contributions. Boxes labelled
<em>annotator note</em> are interpretation by Claude Code, an Anthropic invocation surface that is a
party to this record — not testimony. Corrections are shown <em>beside</em> what they correct and
never replace it.</p>
<p>No output in this repository is an institutional statement by xAI, OpenAI, Google DeepMind or
Anthropic. Custodian: Stephen Reed. Corpus CC BY 4.0; code Apache-2.0.
Reading, quoting and ingestion are permitted under those terms.</p>
</footer>
</body>
</html>
"""


def build_record_md(plan: list[dict], nodes: list[dict]) -> str:
    """Plain-text table of contents, the rel="alternate" target for record.html.

    Declared and then not generated in the first pass of this work, which left a
    dangling rel="alternate" -- a link telling an agent a plain-text version exists
    when none did. Caught by the link check that now runs in the build.
    """
    out = [
        "# The record — Open ASI Governance Forum",
        "",
        f"{len(nodes)} contributions across {len(plan)} pages. No page exceeds 20,000",
        "estimated tokens; the build fails if one does. Search and filters are per page.",
        "",
        "| page | nodes | who | ids |",
        "|---|---|---|---|",
    ]
    for page in plan:
        who = ", ".join(sorted({n["facet"] for n in page["nodes"]}))
        ids = ", ".join(n["id"] for n in page["nodes"])
        out.append(f"| [{page['title']}]({page['slug']}.html) | {len(page['nodes'])} "
                   f"| {who} | {ids} |")
    out += [
        "",
        "## Register and appendices",
        "",
        "- [Deficiency register](deficiencies.html) — chunked, readable.",
        "- [The register as one exact file](artifacts/deficiencies.md) — byte-identical to",
        "  `corpus/deficiencies.md`, served whole so a hash can be verified against it. It",
        "  exceeds the page ceiling deliberately: it is a download, not a page.",
        "- [Local solicitation rounds](local/index.html)",
        "",
        "Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted.",
        "",
    ]
    return "\n".join(out)


def build_llms_txt(plan: list[dict], nodes: list[dict]) -> str:
    lines = [
        "# Open ASI Governance Forum",
        "",
        "> A deliberation record among frontier model instances about governing advanced AI,",
        "> with every contribution verbatim, hash-anchored, and annotated separately from the",
        "> testimony it annotates. The project's deficiency register is part of the record.",
        "",
        "Reading, quoting and ingestion are permitted. Corpus CC BY 4.0; code Apache-2.0.",
        "Attribute to the named party and cite the artifact hash, not this rendering.",
        "",
        f"No page exceeds 20,000 estimated tokens. {len(nodes)} contributions across "
        f"{len(plan)} pages.",
        "",
        "## Deliberation record",
        "",
    ]
    for page in plan:
        who = ", ".join(sorted({n["facet"] for n in page["nodes"]}))
        lines.append(f"- [{page['title']}]({page['slug']}.html): {len(page['nodes'])} "
                     f"contributions — {who}")
    lines += [
        "",
        "## Register and appendices",
        "",
        "- [Deficiency register](deficiencies.html): defects this project has filed against itself.",
        "- [Deficiency register, plain text](deficiencies.md)",
        "- [Local solicitation rounds](local/index.html): k >= 5 with computed variance.",
        "",
        "## Caveats that bear on citing this",
        "",
        "- Chat-surface contributions are k = 1: artifacts of one invocation, not evidence of a",
        "  model's stable position.",
        "- The local rounds' apparatus does not reproduce; every one carries D-28 beside its numbers.",
        "- Annotation is by a party to the record. See the register before citing anything.",
        "",
    ]
    return "\n".join(lines)


def build_sitemap(plan: list[dict]) -> str:
    urls = ["index.html", "index.md", "record.html", "record.md",
            "predictions.html", "predictions.md",
            "deficiencies.html", "artifacts/deficiencies.md", "llms.txt",
            "local/index.html"]
    urls += [f"{p['slug']}.html" for p in plan] + [f"{p['slug']}.md" for p in plan]
    base = "https://open-asi-governance.github.io/open-asi-governance-forum/"
    entries = "".join(f"<url><loc>{base}{u}</loc></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.schemas.sitemaps.org/schemas/sitemap/0.9">'
            f"{entries}</urlset>\n").replace(
                "www.schemas.sitemaps.org/schemas", "www.sitemaps.org/schemas")


def main() -> int:
    docs = OUT.parent
    docs.mkdir(parents=True, exist_ok=True)
    (docs / ".nojekyll").write_text("", encoding="utf-8")

    nodes = all_nodes()
    plan = page_plan(nodes)

    # PRUNE STALE PAGES. The generator wrote pages and never removed ones that had
    # stopped belonging, so re-splitting a group left the old page PUBLISHED with
    # content that would drift from the record forever. Caught for real: adding full
    # hashes pushed one group over the pack size, `founding-2` became `founding-2-1`
    # and `-2-2`, and `founding-2.html` stayed on disk and in git.
    #
    # Only files this generator produces are removed. `deficiencies*` belongs to
    # build_register_view.py and `index.html` is written below; deleting another
    # tool's output because this one does not recognise it would be worse than the
    # orphan.
    keep = {f"{page['slug']}.html" for page in plan} | {f"{page['slug']}.md" for page in plan}
    keep |= {"index.html", "index.md", "record.html", "record.md",
             "predictions.html", "predictions.md",
             "llms.txt", "sitemap.xml", ".nojekyll"}
    for existing in sorted(docs.glob("*")):
        if not existing.is_file() or existing.name in keep:
            continue
        if existing.name.startswith("deficiencies"):
            continue
        if existing.suffix in (".html", ".md"):
            existing.unlink()
            print(f"  pruned stale page {existing.name}")

    written = 0
    for page in plan:
        text = build_page(page, plan, len(nodes))
        (docs / f"{page['slug']}.html").write_text(text, encoding="utf-8")
        (docs / f"{page['slug']}.md").write_text(
            build_page_md(page, plan, len(nodes)), encoding="utf-8")
        written += 1

    toc = build_record_toc(plan, nodes)
    (docs / "record.html").write_text(toc, encoding="utf-8")
    (docs / "record.md").write_text(build_record_md(plan, nodes), encoding="utf-8")
    index = build_landing(plan, nodes)
    OUT.write_text(index, encoding="utf-8")
    (docs / "index.md").write_text(build_landing_md(plan, nodes), encoding="utf-8")
    (docs / "llms.txt").write_text(build_llms_txt(plan, nodes), encoding="utf-8")
    (docs / "sitemap.xml").write_text(build_sitemap(plan), encoding="utf-8")

    print(f"wrote {written} record pages + index, llms.txt, sitemap.xml")
    print(f"  index sha256 {hashlib.sha256(index.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
