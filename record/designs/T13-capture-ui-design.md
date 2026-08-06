# T-13 design — static capture UI, prepare-and-ingest

**Status:** draft for adversarial review, 2026-08-06 · session *Capture Path* (Track B) ·
branch `session/capture` · **no code written yet**

Written before implementation per the standing rule that fixes are designed with an external
reviewer first. Two deployed unreviewed fixes were actively harmful; this document exists to be
attacked, not to be approved.

---

## 1. Goal and acceptance criteria

Build the capture path for solicited model contributions so that the three capture-integrity
failures this project has actually had cannot reach a commit, and so that a four-party round is
run without hand-typing provenance.

Acceptance is defined in `record/tasks/T13-capture-ui.md` and amended there. Restated:

| # | Criterion | How it is checked |
|---|---|---|
| A1 | A four-party round runs with no typed timestamp and **one** ingest command | manual run of T-14 |
| A2 | Pasting the prompt back is refused, reason named | validation corpus, positive cases |
| A3 | Empty paste is refused | validation corpus |
| A4 | Round view shows outstanding parties at a glance | manual |
| A5 | Artifacts validate under `validate_provenance.py` | `tools/rebuild.py` |
| A6 | Similarity rule validated against a hand-checked subset, validation committed | `tools/tests/` |
| A7 | JS preview gates and Python gates agree on every validation case | test, build-failing |
| A8 | Identities selected from the manifest, never typed | code review |
| A9 | Per-party delivery differences auto-recorded in `prior_context` | validation corpus |
| A10 | `rebuild.py` regenerates the page with no diff on an unchanged tree | `git status` |

## 2. What is actually broken today — measured, not assumed

Run against a scratchpad copy of the repository at `656bba9`, three probes:

| Probe | Result |
|---|---|
| Capture a **0-byte** response | `captured` · `citability citable_artifact` · **exit 0** |
| Capture a response that is a **byte-identical copy of its own prompt** | `captured` · **exit 0** |
| `rebuild.py` with both forgeries committed | **"All artifacts rebuilt and verified."** |

Both forgeries are hash-anchored in `MANIFEST.sha256`, schema-valid, and pass P1–P8.

The gap is precise: **`validate_provenance.py` verifies that metadata is well-formed and that the
anchored bytes hash to what the record claims. It never asks whether the anchored bytes are a
response.** The second probe is the exact shape of D-10 (raw 2375) and of the live round-01
incident where the outbound prompt was pasted in place of a reply.

Observed failures this design must prevent, all from `record/tasks/T13-capture-ui.md`:

1. Outbound prompt pasted in place of a reply — live recurrence of D-10.
2. Two reply files returned **0 bytes**, caught only by eye.
3. A **prompt critique** nearly captured as a review.
4. A bundle omitting files the prompt told the reviewer to check — flagged, then repeated a round
   later.
5. Provenance retyped into a long shell command every time.

## 3. Architecture

Static HTML + JavaScript, served by GitHub Pages, **no backend**. The page cannot write to the
repository, so:

```
  committed prompt + round manifest
            │
            │  tools/build_capture_ui.py   (deterministic, runs in rebuild.py)
            ▼
  docs/capture/index.html          self-contained, no external requests
            │
            │  custodian copies prompt → provider web UI → copies reply back
            │  pastes reply, selects party, presses Submit
            │
            │  ADVISORY gates run in-browser, immediate feedback
            ▼
  capture bundle (.json)           downloaded; contains response text + form fields
            │
            │  python3 tools/ingest_capture.py <bundle>...
            │  AUTHORITATIVE gates                      ← the only enforcement
            ▼
  tools/capture_response.py        the single writer, unchanged in role
            ▼
  corpus/raw/<round>/  +  corpus/artifacts/<round>/  +  MANIFEST.sha256
```

**Why the browser does not write.** The File System Access API would satisfy A1 exactly and is
rejected anyway: it puts a second writer in JavaScript and duplicates the D-25-validated similarity
rule in a second language where it can drift from the validated one. D-25 is the deficiency stating
that a reproducible rule is not thereby a correct one; shipping two of them is that failure with
extra steps. Recorded in the brief with the acceptance criterion it costs.

**Consequence accepted:** the JavaScript gates are **advisory preview only**. A1 is amended to one
ingest command per round. The page says so on its face, so nobody mistakes a green preview for a
capture.

### 3.1 The page is generated, not hand-written

`tools/build_capture_ui.py` reads `record/rounds/<round>.json` and the prompt files it names, and
emits `docs/capture/index.html` with the **committed prompt text embedded verbatim and its SHA-256
baked in**. This is what makes T-13's "never composed in the UI" mechanical rather than a matter of
discipline: the page has no prompt-editing affordance and the text it displays is anchored.

Deterministic, added to `rebuild.py`'s step list, no diff on an unchanged tree (A10).

## 4. The round manifest

New: `record/rounds/<round>.json`. Frozen at first capture, reusing the bundle-freeze rule that
exists because regenerating a round-01 bundle silently invalidated Gemini's cited hash.

```json
{
  "schema_version": "oagrc-round-0.1",
  "round": "review-round-03",
  "question": "Is the ASP 2.3(5) fix correct, why was it missed, what does the asymmetry mean?",
  "phase": "Phase-2 (informed)",
  "common_prompt": "record/review-round-03-prompt.md",
  "frozen": false,
  "parties": [
    {
      "identity": "Claude Fable 5",
      "provider": "Anthropic",
      "delivery": "direct_fetch",
      "prompt_override": null,
      "bundle": null,
      "prior_context_template": "Reviewer fetches the repository directly."
    },
    {
      "identity": "Gemini",
      "provider": "Google DeepMind",
      "delivery": "bundle",
      "prompt_override": null,
      "bundle": "record/review-round-03-bundle.md",
      "prior_context_template": "Supplied-context bundle {bundle_path}, sha256 {bundle_sha256}."
    }
  ]
}
```

Three things this buys, each tied to a recorded defect:

- **`identity` is selected, never typed.** D-09 — "the record's most serious attribution defect" —
  is the merging of `Claude`, `Claude Opus 5`, `Claude Fable 5`, `Claude Code`. Free-text identity
  entry is how it recurs through the capture path. A closed list forecloses it.
- **`delivery` and `prompt_override` make asymmetry visible before the round is sent.** Per-party
  context divergence has gone unrecorded until after the fact **twice**: round-01 Gemini received a
  bundle excluding the raw transcript and `corpus/index.md`; round-02 Gemini received a one-line
  preamble the other three did not. Both were honestly recorded in `prior_context` — *afterwards*,
  as confounds the verification note documents rather than the process prevented. The UI shows a
  divergence table across parties at round-open.
- **`prior_context` is composed from the template**, not retyped, so bundle path and SHA-256 cannot
  drift from what was actually supplied.

`prompt_override` is supported because the custodian asked for per-party prompts. **T-14 forbids
using it** — "Identical prompt to all four" — so the UI warns at point of use and names the two
prior instances.

## 5. Schema changes

Additive, to `tools/schemas/contribution.schema.json` (`additionalProperties: false`, so additions
must be declared). Track D owns this directory; custodian authorised, flagged in the brief.

```json
"capture_review": {
  "type": "object",
  "required": ["gates_version", "gates_passed", "attested_answers_round_question", "attested_by"],
  "additionalProperties": false,
  "properties": {
    "gates_version":  { "type": "string" },
    "gates_passed":   { "type": "array", "items": { "type": "string" } },
    "gate_overrides": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["gate", "reason"],
        "additionalProperties": false,
        "properties": { "gate": {"type": "string"}, "reason": {"type": "string", "minLength": 1} }
      }
    },
    "attested_answers_round_question": { "type": "boolean" },
    "attested_by":                     { "type": "string", "minLength": 1 },
    "response_sha256_at_paste":        { "type": "string", "pattern": "^[0-9a-f]{64}$" }
  }
}
```

`gate_overrides` exists because a silently overridden gate is how gates rot. An override is a dated
assertion by a named human, in the record, not a flag nobody sees.

`response_sha256_at_paste` is computed **in the browser at paste time** and re-computed at ingest.
Mismatch is refusal. This is what makes T-13's "hash the pasted content at paste time" checkable
rather than aspirational, and it catches any editing between paste and submit.

## 6. Gates

`gates_version` is recorded on every capture so a later reader knows which rules ran.

| ID | Rule | Level | Motivating incident |
|---|---|---|---|
| G1 | Response is empty or whitespace-only | **refuse** | two 0-byte replies |
| G2 | Two-sided similarity to the outbound prompt above threshold | **refuse** | prompt pasted as reply; D-10 |
| G3 | Response byte-identical to an existing capture | **refuse** | not yet seen; free to exclude |
| G3b | Response near-duplicate of an existing capture | warn + override | as above |
| G4 | Declared bundle missing, unfrozen, or hash mismatched | **refuse** | round-01 bundle break |
| G5 | Response ends mid-sentence / no terminal punctuation | warn + override | **truncated paste — newly named** |
| G6 | Custodian attests the response answers the round's question | **required assertion** | prompt-critique near-miss |

**G5 is a failure mode none of the source documents list.** Provider chat surfaces collapse long
replies behind "show more", and a copy can silently miss the tail. Warn-level, shown alongside byte
count and a visible head/tail so truncation is eyeballable.

**G6 is not a detector and must not be dressed as one.** I checked whether the prompt-critique case
is mechanically separable. It is not:

```
review-round-02                  Gemini  prompt sha 9cce733384ee   ← the real review
review-round-02-prompt-critique  Gemini  prompt sha 9cce733384ee   ← the near-miss
```

Identical prompt file, identical hash, same round. The only distinguishing fact is an out-of-band
operator assertion recorded in `prior_context`. Any heuristic claiming to catch this would be a
D-25 instrument: reproducible, plausible, wrong. So the design **does not classify topicality**. It
displays the round's `question` beside the response's opening and requires a typed attestation,
converting a silent misfiling into a dated false attestation by a named human. The limit is stated
in the tool's own documentation: *this cannot detect a fluent, well-formed answer to the wrong
question.*

### 6.1 G2's rule, and the D-25 obligation on it

> **SUPERSEDED 2026-08-06, before implementation and before this document's review returned.**
> The rule stated below — *"Refuse when **both** exceed threshold"* — was measured against the
> corpus and **rejected**: it passes any paste of less than half the prompt, which is the
> scroll-and-copy failure it was written to catch. A second rule was also tried and rejected.
> The adopted rule and the full validation are in
> [`T13-g2-rule-validation.md`](T13-g2-rule-validation.md).
>
> The text below is left unedited so the review of this document remains legible against what was
> actually reviewed, per the project's superseding-artifact rule.

D-25's specific warning applies directly: *"review tasks quote the reviewed document, so the
document's own vocabulary contaminates any naive pattern."* A review legitimately quotes its
prompt. So the metric is **two-sided** over normalised word n-grams (n = 8, case-folded, whitespace
collapsed, markdown punctuation stripped):

- `coverage = |shingles(prompt) ∩ shingles(response)| / |shingles(prompt)|`
- `saturation = |shingles(prompt) ∩ shingles(response)| / |shingles(response)|`

Refuse when **both** exceed threshold. A review quoting three lines is low on both; a pasted prompt
is ≈1.0 on both. Thresholds are **not chosen by taste** — D-25 requires validation against a
hand-checked subset, committed, with rejected rules published.

Validation corpus, from material the repository already holds:

| Class | Cases | Source |
|---|---|---|
| **Negative** (must not fire) | 9 | every real capture vs. its own prompt, 4,141–26,048 bytes |
| **Positive, genuine** | 1 | D-10: founding transcript raw 2377–2431 duplicating 2319–2373 |
| **Positive, synthetic** | 4 | each committed prompt file treated as its own reply, **labelled synthetic** |

The synthetic label is not decoration: 4 of 5 positives are constructed by the same party that
chose the rule, which is the D-23 shape (the instrument's author encoding the answer). The genuine
D-10 case is the only positive not authored by this design, and it is the one that matters.

`tools/tests/` does not exist — **this repository currently has no tests at all.** It is created
here.

### 6.2 Two implementations, one truth

Gates run in JavaScript (advisory, immediate) and Python (authoritative). Drift between them is the
obvious hazard. A7 makes it a build failure: a test runs both over the full validation corpus and
fails if any case disagrees. The Python result is authoritative in every case where they differ at
runtime, and the browser labels its own verdict as a preview.

## 7. Retroactive check — proposed, not assumed

The gates above are capture-time. A forgery already committed stays invisible: `rebuild.py` printed
"All artifacts rebuilt and verified" over both probes. Proposed new check in
`validate_provenance.py`:

> **P9** — every contribution's anchored `raw` is non-empty, and is not a copy of its own `prompt`
> under the G2 rule.

This runs over Track C's read surface and over the whole existing corpus. It should pass on all 9
real captures; if it does not, that is a finding rather than a reason to loosen the rule.

## 8. What this design does not do

Stated so a later reader does not infer more than was built:

- It does not remove the paste path. GOVERNANCE §2 gives no AI system credentials and the frontier
  parties are reached through the custodian's own authenticated sessions, so the paste is
  **mandated by the governance model**, not an accident of tooling. This is a gate on the artifact
  of the paste.
- It does not authenticate identity. D-18 stands: a self-reported version string is testimony.
- It does not detect a well-formed answer to the wrong question (§6, G6).
- It does not raise `k`. A four-party round through this UI is still k = 1 per party, and the page
  displays the citability consequence at capture time rather than leaving it to be discovered.

## 9. Questions for the reviewer

1. Is prepare-and-ingest the right resolution of the A1-versus-single-writer conflict, or is the
   duplicated-rule argument against direct browser writes overstated?
2. Is two-sided shingle overlap the right shape for G2, and what would defeat it? Specifically: a
   model that restates the prompt at length before answering — a real behaviour — sits where on
   `saturation`?
3. Are the thresholds validatable at all from 5 positives, 4 of them synthetic? If not, what is the
   honest fallback — warn-only until more genuine positives exist?
4. Does `capture_review` belong on the contribution record, or is it maintenance metadata that
   pollutes an artifact meant to describe a model's output?
5. What failure mode is missing from §6 entirely?

---

## 10. Disposition of the Codex review, 2026-08-06

Review committed verbatim at [`reviews/codex-T13-design-review.md`](reviews/codex-T13-design-review.md).
Every finding is dispositioned here. Two are accepted as decisive and change the architecture; one
is accepted in part with the reason for the partial stated; none is deferred to without checking,
because over-correction by deference is the failure review round 02 was designed to detect.

| # | Finding | Disposition |
|---|---|---|
| B1 | Any n-gram rule dies to token insertion — one token every 7th word destroys every 8-shingle while preserving the whole pasted prompt | **Accepted, out of threat model.** See §10.1 |
| B2 | A model that echoes the prompt then answers scores ≈1.0 and is falsely refused | **Accepted, decisive** |
| E1 | Hard heuristic refusal gives an AI-authored instrument control over which evidence is preserved | **Accepted, decisive.** Architecture change, §10.2 |
| C | Nine negatives used to both choose and check the threshold is training on the test set | **Accepted.** Moot once refusal no longer rides on the score |
| A1 | `capture_review` mixes fact with interpretation | **Accepted.** Split, §10.3 |
| E2 | `oagrc-contribution-0.1` cannot gain a property under `additionalProperties: false` | **Accepted.** Version bumps to 0.2 |
| A2 | G3 refuses a response identical to *any* capture; two parties can legitimately produce the same short answer | **Accepted.** Scoped to same party + round |
| A3 | The bundle is editable, so the paste-time hash proves bundle self-consistency, not paste-time state | **Accepted.** §10.4 |
| A4 | G4 validates intention, not delivery; auto-`prior_context` would be polished but false | **Accepted.** §10.5 |
| A5 | The round view has no durable state source | **Accepted.** §10.5 |
| A6 | G5's truncation heuristic both misses paragraph-boundary truncation and falsely warns on JSON, tables and lists | **Accepted.** Demoted to a displayed diagnostic, not a gate |
| A7 | JS/Python agreement is differential consistency, not ground truth | **Accepted.** A7 retained as an anti-drift check, no longer described as validation |
| A8 | Schema validation is fail-open in both tools | **Accepted and already fixed** — commit `8cbe398`, with the missing-import case tested both ways |
| E3 | A10 relies on the clean-rebuild signal this session documented as broken | **Accepted.** A10 withdrawn until Track A fixes the stamp |
| E4 | Batch ingest is not transactional | **Accepted.** §10.6 |
| E5 | §7's P9 changes `validate_provenance.py`, which acceptance says must be unchanged | **Accepted in part.** §10.7 |

### 10.1 Why B1 is accepted but does not drive the design

The interleaved-token attack defeats any n-gram metric and the finding is correct. It is
nonetheless **outside the threat model**: the failure this gate exists to prevent is an
*accidental* paste by the custodian — observed twice, at D-10 and live in round 01 — and a
custodian pasting the wrong clipboard contents does not interleave a token every seventh word.

Stating the limit rather than defending against it: **G2 does not resist a party who wants to
defeat it.** Against that threat the answer is not a better string metric, it is the invocation
ledger and signing that Track D is building, and neither is in scope here.

### 10.2 G2 is demoted from a gate to a diagnostic — the decisive change

E1 is the finding that matters, and it lands on a constraint older than this task. The secretary
constraint adopted in the founding record (ChatGPT §2.3, raw 219–235) makes an AI-authored
instrument a *secondary interpretation artifact* with no authority over the canonical record. A
heuristic that silently refuses a non-empty response is exactly such an instrument deciding what
evidence exists. D-14 is the register's entry for a role attributed to a model beyond what it can
hold; this design had quietly attributed one to itself.

**Revised G2:**

| Condition | Action | Needs a threshold? |
|---|---|---|
| Response empty or whitespace-only | **refuse** | no |
| Response byte-identical to the sent prompt | **refuse** | no |
| Response equal to the sent prompt after normalisation | **refuse** | no |
| Saturation ≥ 0.6 above the 50-shingle floor | **quarantine + warn**, score recorded | yes, and nothing irreversible rides on it |
| otherwise | pass, saturation and coverage recorded as diagnostics | — |

The three refusals are exact predicates. They cannot produce a false positive, need no validation
corpus, and catch every instance of the failure actually observed — D-10 is byte-identical, and so
is a mis-paste of the clipboard.

Everything heuristic **quarantines**: the capture is written to `record/quarantine/<round>/` with
its scores and the gate that fired, and enters the corpus only on the custodian's disposition. No
evidence is destroyed, no model decides what the record contains, and the score is preserved for
exactly the held-out corpus C says is needed.

This is why the R1/R2/R3 work in [`T13-g2-rule-validation.md`](T13-g2-rule-validation.md) is not
wasted although its conclusion is demoted: it establishes that the score separates cleanly enough
to be worth *recording*, and the two rejected rules establish why it is not safe to *refuse* on.

### 10.3 `capture_review` splits along the testimony/annotation line

The project already distinguishes testimony from annotation and this design had collapsed them.
Split:

- **On the contribution record** (fact, observed at capture): `response_sha256`, `gates_version`,
  `gate_results` with their numeric scores, `capture_tool_version`. Schema version → **0.2**.
- **In a separate hash-linked audit artifact** (`corpus/artifacts/<round>/<party>-capture-audit.json`):
  the custodian's topicality attestation, every override with **author and timestamp**, and the
  conflict-of-interest declaration the annotator already owes under P7.

Codex's specific objection that the proposed object permitted
`attested_answers_round_question: false` to pass is met: a `false` attestation is a **refusal to
capture**, not a recordable state.

### 10.4 The bundle is untrusted at ingest

Accepted without qualification. The downloaded JSON is editable, so a paste-time hash inside it
proves only that the bundle is self-consistent.

Ingest therefore derives `round`, `party`, `provider`, `prompt` path and hash, and the
`prior_context` template **from the frozen round manifest in the repository**, never from the
bundle. The bundle contributes exactly two things: the response text and the custodian's form
entries. What the paste-time hash actually establishes is stated in the tool's documentation
rather than overclaimed: *the response was not altered between paste and ingest, assuming the
bundle was not edited.*

### 10.5 A send receipt supplies the durable state, and records delivery rather than intent

A4 and A5 are the same gap seen from two sides: the manifest records what was *planned*, a static
page cannot persist what was *done*, and auto-generated `prior_context` derived from a plan is
polished prose asserting an unobserved fact — which is the D-20 defect, an inference recorded as
provenance.

`record/rounds/<round>-receipts.jsonl`, append-only, one line per send, written by the custodian
at the moment of sending: party, UTC, which prompt file and hash was actually pasted, which bundle
if any, any preamble verbatim. `prior_context` is composed from the **receipt**, not the manifest.
Where no receipt exists, `prior_context` records that the delivery was not observed rather than
describing it.

This is also what makes sent / returned / outstanding durable, and what makes the public process
history of §12 truthful rather than survivorship-biased.

### 10.6 Ingest is transactional per capture, and resumable per round

`capture_response.py` writes raw, then the artifact, then rebuilds the manifest; a failure midway
through a four-bundle round leaves a partial round that immutability makes awkward to retry.
Ingest processes bundles one at a time, and a failed bundle leaves that party uncaptured while the
others stand. Re-running ingest over an already-captured bundle is a no-op that reports the
existing artifact, rather than an immutability refusal the custodian has to reason about.

### 10.7 P9 splits, and the acceptance criterion is read honestly

E5 is right that adding P9 changes `validate_provenance.py`, which acceptance says artifacts must
validate under *unchanged*. The literal reading forbids strengthening the validator, which cannot
be the intent — but the criterion should not be reinterpreted to match what was built, so:

- **P9a** — anchored `raw` is non-empty, and is not byte-identical or normalised-equal to its
  anchored `prompt`. Exact predicates, hard check, no threshold.
- **P9b** — the saturation score, computed and **reported only**, versioned, never failing a build.

Every existing artifact is expected to pass P9a. Backfilling `gates_version` or `gate_results`
onto historical captures is refused outright: it would assert a capture-time execution that never
happened, which is precisely D-08's retro-application defect.

## 11. Revised acceptance criteria

A10 is withdrawn: it rested on the clean-rebuild signal this session measured as broken and handed
to Track A. It returns when the stamp is fixed.

A6 is restated. The similarity rule is no longer validated *for refusal*, because it no longer
refuses. What is committed is the score's behaviour on the corpus and the two rejected rules, so a
later session inherits the finding rather than re-deriving it.

New: **A11** — every gate that can withhold a non-empty response writes it to `record/quarantine/`
with the reason. No path exists by which a captured response is discarded rather than quarantined.
