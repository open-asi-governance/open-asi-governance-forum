#!/usr/bin/env python3
"""Generate tools/capture_ui/index.html — the capture UI. Deterministic, self-contained.

    python3 tools/build_capture_ui.py

Reads every round declaration in record/rounds/*.json and emits one static page
that embeds the committed prompt text verbatim with its SHA-256. The page has no
backend, makes no external request, holds no credential, and cannot write to this
repository. It produces a capture bundle the custodian downloads and feeds to
tools/ingest_capture.py.

WHAT MAKES THIS SAFE TO SERVE PUBLICLY
--------------------------------------
GitHub Pages has no access control on a public repository, so the page is public
whether or not that is wanted. It is safe because it is inert: a stranger who loads
it and pastes text produces a JSON file on their own machine and nothing else.
GOVERNANCE.md section 2 already puts every write through the custodian, so the
authorisation boundary is at ingest and merge, not at the door.

A password box would be worse than nothing. It would assert a control that does not
exist -- bypassable by view-source, by saving the file, or by reading the public
repository this page is generated from -- which is D-13 (a signature field with no
key, no algorithm and no verifier) in a new place. ASP section 2.3 says the same
thing normatively: status is verified on check, not cached at issue.

DETERMINISM
-----------
No timestamp, no random id, no build-host detail, sorted iteration everywhere. The
generated file must be byte-identical on an unchanged repository. tools/rebuild.py
stamps build-time HEAD into docs/index.html and thereby dirties the tree after
every commit; that defect is Track A's and is not reproduced here.

OPENED OVER file://, NOT SERVED
------------------------------
The page is generated into tools/capture_ui/ and opened directly from disk. It is
public for examination -- the source is in a public repository, readable and
diffable -- and it is not served, so there is nothing to gate and no access control
to assert falsely.

file:// costs two browser APIs, and both are handled rather than assumed:

  crypto.subtle       requires a secure context. Browsers generally treat file://
                      as trustworthy, but "generally" is not a guarantee, and the
                      paste-time hash is the page's central integrity claim. A
                      pure-JS SHA-256 fallback runs when subtle crypto is absent.
  navigator.clipboard also requires a secure context, and silently rejects rather
                      than throwing in some configurations. Falls back to selecting
                      the prompt text so the custodian can copy it manually.

A page whose hash silently stopped being computed would be exactly the failure this
project keeps filing: a green signal that verified nothing.

TERRITORY
---------
docs/ is Track A's and this no longer writes there at all.
"""

from __future__ import annotations

import hashlib
import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from capture_gates import sent_prompt_text                      # noqa: E402

#  NOT under docs/. docs/ is the published GitHub Pages surface; the custodian
#  directed 2026-08-06 that the page ship as source in the repository and be opened
#  locally over file://, so it is never served. That makes "public for examination,
#  not public for use" true by construction rather than asserted by a control.
OUT = REPO_ROOT / "tools" / "capture_ui" / "index.html"
ROUNDS_DIR = REPO_ROOT / "record" / "rounds"
GATES_JS = REPO_ROOT / "tools" / "capture_ui" / "gates.js"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    print(f"REFUSED: {message}", file=sys.stderr)
    sys.exit(1)


def load_rounds() -> list[dict]:
    """Load every round declaration, resolving the prompt text each party receives."""
    rounds = []
    for path in sorted(ROUNDS_DIR.glob("*.json")):
        if path.name.endswith("-lifecycle.jsonl"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("artifact_type") != "round_declaration":
            continue

        common = REPO_ROOT / data["common_prompt"]
        if not common.exists():
            fail(f"{path.name}: common_prompt not found: {data['common_prompt']}")

        parties = []
        for party in data["parties"]:
            prompt_rel = party.get("prompt_override") or data["common_prompt"]
            prompt_path = REPO_ROOT / prompt_rel
            if not prompt_path.exists():
                fail(f"{path.name}: prompt not found for {party['identity']}: {prompt_rel}")
            bundle_sha = None
            if party.get("bundle"):
                bundle_path = REPO_ROOT / party["bundle"]
                if not bundle_path.exists():
                    fail(f"{path.name}: bundle not found for {party['identity']}: {party['bundle']}")
                bundle_sha = sha256_of(bundle_path)
            parties.append({
                **party,
                "prompt_path": prompt_rel,
                "prompt_sha256": sha256_of(prompt_path),
                "sent_text": sent_prompt_text(prompt_path.read_text(encoding="utf-8")),
                "bundle_sha256": bundle_sha,
                "is_override": bool(party.get("prompt_override")),
            })
        rounds.append({**data, "parties": parties, "declaration_path": str(path.relative_to(REPO_ROOT))})
    return rounds


STYLE = """
:root{--fg:#111;--bg:#fff;--mut:#5b5b5b;--line:#d8d8d8;--warn:#8a5a00;--warnbg:#fff6e5;
--bad:#8a1c1c;--badbg:#fdeded;--ok:#17502a;--okbg:#edf7f0;--pre:#f6f6f6}
@media(prefers-color-scheme:dark){:root{--fg:#e8e8e8;--bg:#131313;--mut:#a6a6a6;--line:#333;
--warn:#f0c070;--warnbg:#2e2410;--bad:#f09a9a;--badbg:#301616;--ok:#8fd6a8;--okbg:#122419;--pre:#1c1c1c}}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1.25rem 5rem;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",
Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}
main{max-width:60rem;margin:0 auto}
h1{font-size:1.5rem;margin:0 0 .25rem}h2{font-size:1.1rem;margin:2rem 0 .5rem}
.sub{color:var(--mut);margin:0 0 1.5rem}
.banner{border:1px solid var(--line);border-left:3px solid var(--warn);background:var(--warnbg);
padding:.75rem 1rem;margin:0 0 1.5rem;font-size:.9rem}
label{display:block;font-weight:600;margin:.9rem 0 .25rem;font-size:.9rem}
select,input,textarea{width:100%;padding:.5rem;font:inherit;color:var(--fg);background:var(--bg);
border:1px solid var(--line);border-radius:3px}
textarea{min-height:16rem;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.85rem}
pre{background:var(--pre);border:1px solid var(--line);border-radius:3px;padding:.75rem;
overflow-x:auto;font-size:.8rem;max-height:26rem}
button{font:inherit;padding:.5rem 1rem;border:1px solid var(--line);border-radius:3px;
background:var(--pre);color:var(--fg);cursor:pointer}
button:hover{border-color:var(--fg)}
button[disabled]{opacity:.5;cursor:not-allowed}
table{border-collapse:collapse;width:100%;font-size:.85rem;margin:.5rem 0}
th,td{border:1px solid var(--line);padding:.35rem .5rem;text-align:left;vertical-align:top}
th{background:var(--pre)}
.v{border:1px solid var(--line);border-left-width:3px;padding:.6rem .8rem;margin:.5rem 0;font-size:.88rem}
.v.ok{border-left-color:var(--ok);background:var(--okbg)}
.v.warn{border-left-color:var(--warn);background:var(--warnbg)}
.v.bad{border-left-color:var(--bad);background:var(--badbg)}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.78rem;word-break:break-all}
.muted{color:var(--mut);font-size:.85rem}
.row{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;margin:.5rem 0}
fieldset{border:1px solid var(--line);border-radius:3px;padding:.75rem 1rem;margin:1rem 0}
legend{font-weight:600;font-size:.85rem;padding:0 .4rem}
"""

APP_JS = r"""
'use strict';
const $ = s => document.querySelector(s);
const state = { round: null, party: null, pasteSha: null };

function h(s){ return String(s).replace(/[&<>"']/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

/* SHA-256 with a pure-JS fallback. crypto.subtle needs a secure context, and this
 * page is opened over file://. Browsers generally treat file:// as trustworthy but
 * "generally" is not a guarantee, and a page whose hash silently stopped being
 * computed would be a green signal that verified nothing -- the failure this
 * project keeps filing. Which path ran is reported on the page. */
let HASH_IMPL = 'unknown';
async function sha256(text){
  const bytes = new TextEncoder().encode(text);
  if (globalThis.crypto && crypto.subtle && crypto.subtle.digest) {
    try {
      const buf = await crypto.subtle.digest('SHA-256', bytes);
      HASH_IMPL = 'crypto.subtle';
      return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2,'0')).join('');
    } catch (e) { /* fall through */ }
  }
  HASH_IMPL = 'in-page fallback';
  return sha256Fallback(bytes);
}

/* FIPS 180-4. Verified against crypto.subtle over the corpus by
 * tools/tests/test_page_hash_fallback.py -- two implementations of a hash is a
 * drift hazard and the same rule applies as to the gates: check it, do not hope. */
function sha256Fallback(bytes){
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const ml=bytes.length*8, withPad=new Uint8Array((((bytes.length+9)+63)>>6)<<6);
  withPad.set(bytes); withPad[bytes.length]=0x80;
  new DataView(withPad.buffer).setUint32(withPad.length-4, ml>>>0, false);
  new DataView(withPad.buffer).setUint32(withPad.length-8, Math.floor(ml/4294967296), false);
  const rr=(x,n)=>(x>>>n)|(x<<(32-n));
  for(let i=0;i<withPad.length;i+=64){
    const w=new Array(64), dv=new DataView(withPad.buffer,i,64);
    for(let j=0;j<16;j++) w[j]=dv.getUint32(j*4,false);
    for(let j=16;j<64;j++){
      const s0=rr(w[j-15],7)^rr(w[j-15],18)^(w[j-15]>>>3);
      const s1=rr(w[j-2],17)^rr(w[j-2],19)^(w[j-2]>>>10);
      w[j]=(w[j-16]+s0+w[j-7]+s1)>>>0;
    }
    let [a,b,c,d,e,f,g,h]=H;
    for(let j=0;j<64;j++){
      const S1=rr(e,6)^rr(e,11)^rr(e,25), ch=(e&f)^(~e&g);
      const t1=(h+S1+ch+K[j]+w[j])>>>0;
      const S0=rr(a,2)^rr(a,13)^rr(a,22), mj=(a&b)^(a&c)^(b&c);
      const t2=(S0+mj)>>>0;
      h=g; g=f; f=e; e=(d+t1)>>>0; d=c; c=b; b=a; a=(t1+t2)>>>0;
    }
    H=[H[0]+a,H[1]+b,H[2]+c,H[3]+d,H[4]+e,H[5]+f,H[6]+g,H[7]+h].map(x=>x>>>0);
  }
  return H.map(x=>x.toString(16).padStart(8,'0')).join('');
}

function rounds(){ return window.OAGF_ROUNDS; }
function currentRound(){ return rounds().find(r => r.round === state.round); }
function currentParty(){ const r = currentRound(); return r && r.parties.find(p => p.identity === state.party); }

function renderRoundPicker(){
  const sel = $('#round');
  sel.innerHTML = rounds().map(r => `<option value="${h(r.round)}">${h(r.round)}</option>`).join('');
  state.round = rounds().length ? rounds()[0].round : null;
}

function renderParties(){
  const r = currentRound(); if (!r) return;
  $('#party').innerHTML = r.parties.map(p =>
    `<option value="${h(p.identity)}">${h(p.identity)} — ${h(p.provider)}</option>`).join('');
  state.party = r.parties[0].identity;
  $('#question').textContent = r.question;
  $('#divergence').innerHTML =
    '<tr><th>party</th><th>delivery</th><th>prompt</th><th>bundle</th></tr>' +
    r.parties.map(p => `<tr><td>${h(p.identity)}</td><td>${h(p.delivery)}</td>` +
      `<td>${p.is_override ? '<strong>OVERRIDE</strong> ' : 'common '}` +
      `<span class="mono">${h(p.prompt_sha256.slice(0,12))}</span></td>` +
      `<td>${p.bundle ? '<span class="mono">'+h(p.bundle_sha256.slice(0,12))+'</span>' : '—'}</td></tr>`).join('');
  const anyOverride = r.parties.some(p => p.is_override);
  $('#override-warning').hidden = !anyOverride;
}

function renderPrompt(){
  const p = currentParty(); if (!p) return;
  $('#prompt-text').textContent = p.sent_text;
  $('#prompt-meta').innerHTML =
    `<span class="mono">${h(p.prompt_path)}</span> · sha256 <span class="mono">${h(p.prompt_sha256)}</span>` +
    (p.bundle ? ` · bundle <span class="mono">${h(p.bundle)}</span> sha256 <span class="mono">${h(p.bundle_sha256)}</span>` : '');
  renderProvenanceDefaults();
  evaluate();
}

function renderProvenanceDefaults(){
  const p = currentParty(); if (!p) return;
  for (const [id, key] of [['version-reason','version_unknown_reason'],
                           ['sampling-reason','sampling_unknown_reason'],
                           ['effort-reason','effort_unknown_reason'],
                           ['sysinstr-reason','system_instructions_unknown_reason']]) {
    const el = $('#'+id);
    if (!el.dataset.touched) el.value = p[key] || defaultReason(key);
  }
}
function defaultReason(key){
  return {version_unknown_reason:'Chat surface does not expose a version identifier.',
          sampling_unknown_reason:'Chat surface does not expose sampling parameters.',
          effort_unknown_reason:'Not selectable or not reported by the chat surface.',
          system_instructions_unknown_reason:'Provider system prompt not disclosed.'}[key] || '';
}

async function evaluate(){
  const p = currentParty(); if (!p) return;
  const text = $('#response').value;
  state.pasteSha = text ? await sha256(text) : null;

  const results = window.GATES.runGates(text, p.sent_text, {});
  const { state: st, reasons } = window.GATES.lifecycleState(results);

  const cls = st === 'refused_empty' ? 'bad' : st === 'returned_pending_review' ? 'warn' : 'ok';
  const head = st === 'refused_empty'
      ? 'REFUSED — nothing to capture'
      : st === 'returned_pending_review'
        ? 'Would be held for custodian review — the bytes are kept either way'
        : 'Preview clean';
  $('#verdict').className = 'v ' + cls;
  $('#verdict').innerHTML = `<strong>${h(head)}</strong>` +
    (reasons.length ? '<ul>' + reasons.map(x => `<li>${h(x)}</li>`).join('') + '</ul>' : '') +
    '<div class="muted">This is a PREVIEW. Python decides at ingest, every time.</div>';

  $('#diagnostics').innerHTML = results.map(r => {
    const sc = r.scores ? ' — ' + Object.entries(r.scores)
      .map(([k,v]) => `${k} ${typeof v==='number' && !Number.isInteger(v) ? v.toFixed(3) : v}`).join(', ') : '';
    return `<tr><td class="mono">${h(r.gate)}</td><td>${h(r.kind)}</td>` +
           `<td>${r.passed ? '·' : '<strong>fired</strong>'}</td><td>${h(r.detail)}${h(sc)}</td></tr>`;
  }).join('');

  $('#paste-meta').innerHTML = text
    ? `${new TextEncoder().encode(text).length} bytes · ${text.split('\n').length} lines · sha256 `
      + `<span class="mono">${h(state.pasteSha)}</span> <span class="muted">(${h(HASH_IMPL)})</span>`
    : 'nothing pasted';
  $('#download').disabled = (st === 'refused_empty') || !$('#attest').checked || !$('#attested-by').value.trim();
}

async function download(){
  const r = currentRound(), p = currentParty();
  const text = $('#response').value;
  // Recomputed here rather than reading state.pasteSha, which is written by an
  // async handler and can lag the textarea if Download is pressed quickly after a
  // paste. The bundle's own hash must describe the bytes being written INTO it.
  const responseSha = await sha256(text);
  const bundle = {
    bundle_version: 'oagrc-capture-bundle-0.1',
    gates_version: window.GATES.GATES_VERSION,
    round: r.round,
    identity: p.identity,
    provider: p.provider,
    captured_utc: new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'),
    response_text: text,
    response_sha256_at_paste: responseSha,
    prompt_path: p.prompt_path,
    prompt_sha256: p.prompt_sha256,
    bundle_path: p.bundle || null,
    bundle_sha256: p.bundle_sha256 || null,
    delivery: p.delivery,
    model_version: $('#version').value.trim() || null,
    version_unknown_reason: $('#version').value.trim() ? null : $('#version-reason').value,
    sampling_unknown_reason: $('#sampling-reason').value,
    effort_unknown_reason: $('#effort-reason').value,
    system_instructions_unknown_reason: $('#sysinstr-reason').value,
    attested_answers_round_question: $('#attest').checked,
    attested_by: $('#attested-by').value.trim(),
    round_question: r.question,
    notes: $('#notes').value.trim() || null,
  };
  // CONTENT-ADDRESSED. The name used to be round+party only, so every capture for a
  // party in a round produced the SAME filename. Browsers do not overwrite on
  // collision, they suffix -- so a corrected capture landed at "... (1).json" while
  // the page told the custodian to ingest the original. A hash of the response makes
  // different responses different files and identical responses the same file, which
  // is also the identity the ingest side compares on.
  //
  // A timestamp was the alternative and is worse: it says only when Download was
  // pressed, depends on the clock, and gives every re-save of the SAME capture a new
  // name -- manufacturing a second bundle that ingest would then treat as a dispute.
  const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'') || 'capture';
  const filename = `oagf-capture-${slug(r.round)}-${slug(p.identity)}-${responseSha.slice(0,16)}.json`;
  const blob = new Blob([JSON.stringify(bundle, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
  // The exact path, not a glob. A glob makes every historical capture in the folder
  // part of a state-changing operation, and lets shell collation decide which
  // response becomes canonical -- "grok (1).json" sorts BEFORE "grok.json", and
  // "(10)" before "(2)".
  $('#ingest-command').textContent =
    `python3 tools/ingest_capture.py "$HOME/Downloads/${filename}"`;
  $('#next').hidden = false;
}

window.addEventListener('DOMContentLoaded', () => {
  if (!rounds().length) { $('#app').hidden = true; $('#no-rounds').hidden = false; return; }
  renderRoundPicker(); renderParties(); renderPrompt();
  $('#round').addEventListener('change', e => { state.round = e.target.value; renderParties(); renderPrompt(); });
  $('#party').addEventListener('change', e => { state.party = e.target.value; renderPrompt(); });
  $('#response').addEventListener('input', evaluate);
  $('#attest').addEventListener('change', evaluate);
  $('#attested-by').addEventListener('input', evaluate);
  for (const id of ['version-reason','sampling-reason','effort-reason','sysinstr-reason']) {
    $('#'+id).addEventListener('input', e => { e.target.dataset.touched = '1'; });
  }
  /* navigator.clipboard needs a secure context and can reject silently over
   * file://. On failure, select the prompt so the custodian can copy it manually --
   * a copy button that quietly does nothing is worse than no button. */
  $('#copy').addEventListener('click', async () => {
    const text = currentParty().sent_text;
    try {
      if (!navigator.clipboard) throw new Error('no clipboard API');
      await navigator.clipboard.writeText(text);
      $('#copy').textContent = 'copied';
    } catch (e) {
      const pre = $('#prompt-text'), sel = window.getSelection(), range = document.createRange();
      range.selectNodeContents(pre); sel.removeAllRanges(); sel.addRange(range);
      $('#copy').textContent = 'selected — press Ctrl/Cmd+C';
    }
    setTimeout(() => $('#copy').textContent = 'copy prompt', 2400);
  });
  $('#download').addEventListener('click', download);
});
"""


def build() -> str:
    rounds = load_rounds()
    gates_js = GATES_JS.read_text(encoding="utf-8")
    payload = json.dumps(rounds, ensure_ascii=False, sort_keys=True, indent=1)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>OAGF — capture</title>
<style>{STYLE}</style>
</head>
<body>
<main>
<h1>Open ASI Governance Forum — capture</h1>
<p class="sub">Paste a model's reply, check it, and produce a capture bundle for the custodian.</p>

<div class="banner">
<strong>This page writes nothing.</strong> It has no server, no credentials, and no access to the
repository. Pressing <em>Download capture bundle</em> saves a JSON file to your own machine and does
nothing else. Only the custodian, running <span class="mono">tools/ingest_capture.py</span> and
committing the result, can enter anything into the record — <span class="mono">GOVERNANCE.md</span> §2.
Gate verdicts here are a <strong>preview</strong>; the authoritative check runs at ingest.
</div>

<div id="no-rounds" class="v bad" hidden>
<strong>No round declarations found.</strong> Add one under <span class="mono">record/rounds/</span>
and rebuild.
</div>

<div id="app">
<h2>1 · Round and party</h2>
<div class="row">
  <div style="flex:1;min-width:14rem"><label for="round">Round</label><select id="round"></select></div>
  <div style="flex:1;min-width:14rem"><label for="party">Party</label><select id="party"></select></div>
</div>
<p class="muted">Identities come from the round declaration and cannot be typed. D-09 — the record's
most serious attribution defect — is the merging of <span class="mono">Claude</span>,
<span class="mono">Claude Opus 5</span>, <span class="mono">Claude Fable 5</span> and
<span class="mono">Claude Code</span>; free-text entry is how that recurs.</p>

<h2>2 · Delivery across parties</h2>
<p class="muted">Per-party asymmetry has gone unrecorded until after the fact twice. It is shown here
<em>before</em> the round is sent.</p>
<table id="divergence"></table>
<div id="override-warning" class="v warn" hidden>
<strong>A party has a prompt override.</strong> T-14 requires an identical prompt to all four: a
per-party preamble in round 02 created an asymmetry that contaminated the comparison, and a bundle
exclusion did the same in round 01.
</div>

<h2>3 · The prompt, as committed</h2>
<p class="muted" id="prompt-meta"></p>
<div class="row"><button id="copy" type="button">copy prompt</button>
<span class="muted">Read-only. The page has no prompt-editing control — what is sent is what is committed.</span></div>
<pre id="prompt-text"></pre>

<h2>4 · The reply</h2>
<p class="muted">Paste exactly what the provider returned. There is deliberately no reformat, clean-up
or trim control. The hash below is computed on every keystroke, so any edit after pasting is visible.</p>
<textarea id="response" spellcheck="false" autocorrect="off" autocapitalize="off"
  placeholder="Paste the model's reply here"></textarea>
<p class="muted" id="paste-meta">nothing pasted</p>
<div id="verdict" class="v"></div>
<table><tr><th>gate</th><th>kind</th><th></th><th>detail</th></tr><tbody id="diagnostics"></tbody></table>

<h2>5 · Provenance</h2>
<fieldset><legend>Value, or a stated reason. Never a placeholder.</legend>
<label for="version">Model version identifier, if the surface reports one</label>
<input id="version" placeholder="leave blank if not exposed">
<p class="muted">Self-reported is not authenticated — D-18. Recorded as testimony.</p>
<label for="version-reason">…otherwise, why it is unknown</label><input id="version-reason">
<label for="sampling-reason">Sampling parameters unknown because</label><input id="sampling-reason">
<label for="effort-reason">Reasoning effort unknown because</label><input id="effort-reason">
<label for="sysinstr-reason">System instructions unknown because</label><input id="sysinstr-reason">
</fieldset>

<h2>6 · Attestation</h2>
<div class="v warn">
<p style="margin:.2rem 0"><strong>The round asked:</strong> <span id="question"></span></p>
<p class="muted" style="margin:.2rem 0">No tool can tell whether this reply answers that question. A
prompt critique and a review are not mechanically separable — identical prompt file, identical hash,
same round — which is how one was nearly filed as the other. Only you can say.</p>
<label><input type="checkbox" id="attest" style="width:auto"> This reply answers the question above.</label>
<label for="attested-by">Attested by</label><input id="attested-by" placeholder="Stephen Reed (human custodian)">
</div>
<label for="notes">Notes (optional)</label><input id="notes">

<h2>7 · Produce the bundle</h2>
<div class="row"><button id="download" type="button" disabled>Download capture bundle</button></div>
<div id="next" class="v ok" hidden>
Saved. Ingest it with:
<pre id="ingest-command"></pre>
<span class="muted">This is the <strong>suggested</strong> filename. A browser will not overwrite an
existing file &mdash; if one of that name is already in the folder it saves as
<span class="mono">&hellip;&nbsp;(1).json</span> instead, and a page cannot see the name that was
actually used. If the command below fails, check the folder. The name contains a hash of the
response, so a differently-named file with the same hash holds the same response.</span>
Nothing has entered the record yet.
</div>
</div>

<p class="muted" style="margin-top:3rem">Generated by <span class="mono">tools/build_capture_ui.py</span>
from the committed round declarations. Self-contained: no external requests, no fonts, no analytics.</p>
</main>

<script>{gates_js}
window.GATES = {{GATES_VERSION, MIN_SHINGLES_FOR_SATURATION, SATURATION_THRESHOLD,
  sentPromptText, normalise, shingles, overlap, runGates, lifecycleState}};
window.OAGF_ROUNDS = {payload};
</script>
<script>{APP_JS}</script>
</body>
</html>
"""


#  A page that fetches anything is a page that breaks in a restricted environment,
#  and review round 01 proved that is a real constraint rather than a hypothetical:
#  a reviewer could not reach raw.githubusercontent.com at all.
#
#  The check is on SUBRESOURCES, not on the string "https://". Embedded prompt text
#  legitimately contains URLs -- the round-03 prompt cites the repository by URL,
#  because that is what was sent to the reviewers. Rejecting those would be
#  rejecting the content the page exists to display. A first version of this guard
#  did exactly that and failed the build on its own payload.
SUBRESOURCE_PATTERNS = (
    ("<script src", "external script"),
    ("<link ", "stylesheet or preload link"),
    ("<img ", "image element"),
    ("<iframe", "iframe"),
    ("@import", "CSS import"),
    ("url(http", "CSS remote url()"),
    ("fetch('http", "runtime fetch"),
    ('fetch("http', "runtime fetch"),
    ("XMLHttpRequest", "XHR"),
    ("new WebSocket", "websocket"),
    ("navigator.sendBeacon", "beacon"),
)


def check_self_contained(page: str) -> None:
    """Refuse to emit a page that would make any network request."""
    found = [why for marker, why in SUBRESOURCE_PATTERNS if marker in page]
    if found:
        fail(
            "the generated page would make an external request (" + ", ".join(sorted(set(found))) + "). "
            "It must be self-contained: review round 01 proved a blocked CDN is a real constraint, "
            "and a capture UI that degrades in a restricted environment is that failure one layer up."
        )


def main() -> int:
    if not GATES_JS.exists():
        fail(f"gate mirror not found: {GATES_JS.relative_to(REPO_ROOT)}")
    page = build()

    check_self_contained(page)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    unchanged = OUT.exists() and OUT.read_text(encoding="utf-8") == page
    OUT.write_text(page, encoding="utf-8")
    print(f"{'unchanged' if unchanged else 'wrote'}  {OUT.relative_to(REPO_ROOT)}  ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
