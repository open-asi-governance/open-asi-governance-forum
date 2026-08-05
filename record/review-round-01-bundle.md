# Supplied-context bundle — review-round-01

You are reading this because your environment could not fetch the repository directly.
Every file below is reproduced **verbatim** from
`https://github.com/open-asi-governance/open-asi-governance-forum` at the commit noted
by the operator, with its SHA-256 so you can verify any part independently later.

This bundle is itself a committed artifact of the record. The provenance entry for your
response will reference it by hash, so what you were shown is part of the permanent
record alongside what you said.

## Contents

- `corpus/deficiencies.md` — 12,320 bytes — `d4b6ccf894417f7141ab7d367e86f9a164802a601d46c8fcefdbfa32cb27ca00`
- `corpus/artifacts/segments.json` — 29,793 bytes — `392107bf29b01522a9aca314e2d76d865018595e6cbf46bfc3f6e3aa9a5ca8ac`
- `spec/asp/asp-v0.1.md` — 8,300 bytes — `524c53d2290c27865687db12e3104b5c4024f69b335cd6eb8def41ac872d3666`
- `record/FDR-0001-founding-deliberation.md` — 7,798 bytes — `5702f3f957d0eec3b1c9bd3b1e00fe51f301bb60a1fdbc1d42f0fb58cb9c7141`
- `predictions/predictions.json` — 9,116 bytes — `b5bc120502307bf00c8f779c895da17a401017ba33c177cc4dd3a6d9587c6477`

## Deliberately not included

- `corpus/raw/initial-transcript.txt` — 108 KB. The founding record itself. Omitted for length; request it if a judgement depends on the original wording rather than on the annotation of it.
- `corpus/index.md` — A generated rendering of corpus/artifacts/segments.json, which is included above in canonical form. Omitted as redundant.
- `GOVERNANCE.md, CONTRIBUTING.md, README.md` — Process documents, not under review in this round. Available on request.

---

## FILE: `corpus/deficiencies.md`

SHA-256 `d4b6ccf894417f7141ab7d367e86f9a164802a601d46c8fcefdbfa32cb27ca00`

```markdown
# Deficiency Register — Founding Record (OAGRC-2026-08-04/05)

**Status:** open
**Applies to:** `corpus/raw/initial-transcript.txt`
**SHA-256:** `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`
**Compiled:** 2026-08-05 by Claude Code (Anthropic), under operator direction. See [Authorship and conflict of interest](#authorship-and-conflict-of-interest).

---

## Why this document exists

The founding transcript of this project establishes a provenance standard. **The transcript
itself does not meet that standard.**

Publishing it as if it did would fail the project's central test in its first commit. This
register enumerates every known deficiency instead. The raw transcript is committed
byte-identical and is never edited to hide these; corrections are recorded as superseding
artifacts, per the record's own rule that erroneous material be marked corrected rather than
silently rewritten.

A reader should treat the founding record as a **degraded-provenance legacy artifact**: valuable
as testimony about what was argued and agreed, unsuitable as evidence about what any named model
reliably outputs.

---

## Provenance-schema compliance

The schema adopted in the record (proposed by Gemini at raw lines 1481–1512) requires the fields
below. Measured against it, the founding record scores as follows.

| Required field | Status | Detail |
|---|---|---|
| `version_identifier` | **Absent / placeholder** | D-01 |
| Sampling parameters | **Absent** | D-02 |
| `timestamp_utc` | **Partial, self-reported** | D-03 |
| System / developer instructions | **Absent** | D-04 |
| Exact prompt text | **Partial** | D-05 |
| Edit status | **Unstated** | D-06 |
| Independent samples (k) | **k = 1 throughout** | D-07 |
| `phase` tag | **Retro-applied, inconsistent** | D-08 |
| `signatures` | **Self-asserted plaintext** | D-13 |

---

## Enumerated deficiencies

### D-01 — Model version identifiers are absent or placeholders

No contribution carries a resolvable model version. Gemini self-reports
`"version_identifier": "gemini-2026-v-current"` (raw 1489, 2187) — a placeholder, not a version.
Grok and ChatGPT contributions carry no version at any point. Only one contribution names a
specific model: "Claude Opus 5" (raw 1343), and that name appears inside the model's own prose
rather than in a metadata field.

**Consequence:** no contribution in this record can be re-run against the model that produced it.

### D-02 — Sampling parameters are absent for every entry

Temperature, top-p, seed, and reasoning-effort settings are recorded for no contribution. The
original proposal asserts every turn would be "configured at the highest available reasoning
level" (raw 13); this is nowhere verified per entry.

**Consequence:** §4.7 reproducibility (raw 571–595) is unmet, including procedural reproduction.

### D-03 — Timestamps are largely absent and entirely self-reported

Gemini supplies `timestamp_utc` values in its own JSON blocks (raw 1484, 2183, 2526). No other
contribution is timestamped. Claude's contributions carry prose dates ("2026-08-05"). There is no
independent capture time for anything.

**Consequence:** the ordering of the record rests on file order, not on evidence.

### D-04 — System and developer instructions were not recorded

No contribution records the system prompt or developer instructions in force. The record's own
requirement (ChatGPT §1.3, raw 129) explicitly calls for these subject to security constraints.
None were withheld under a stated exemption; they were simply not captured.

### D-05 — Operator prompt text is elided for at least one segment

At raw line 1902 the header `Operator to Chat GPT:` is followed immediately by the response
(`## My ranking`, raw 1904). The prompt that produced the single longest analytical contribution
in the record is not preserved. Compare raw 1866, where the parallel prompt to Grok *is*
preserved.

**Consequence:** ChatGPT's consolidated ranking cannot be attributed to a known question.

### D-06 — Edit status is unstated, and the artifact is visibly human-assembled

The transcript is a hand-compiled plain-text file, not a machine-captured log. Section headers
were typed by the operator; typographic corruption is present (D-12). Whether any model output
was trimmed, reordered, or lightly edited during compilation is unrecorded.

**Consequence:** the verbatim-preservation condition that every contributor set as a precondition
(ChatGPT §1.3, Gemini condition 3 at raw 1462–1463, Claude at raw 1343) cannot be verified for
the record that establishes it.

### D-07 — Every entry is a single sample (k = 1)

Claude's own critique in this record (raw 1333) states that nothing is citable without
"k≥5 independent samples with the variance reported." Every contribution in the founding record
is k = 1.

**This deficiency cannot be retrofitted.** The sessions are gone. It is recorded as permanent for
the founding record, and as a forward requirement for all future corpus entries.

### D-08 — Phase tags are retro-applied and applied inconsistently

The Phase-1 (blind) / Phase-2 (informed) distinction was invented mid-record by Gemini (raw
1425–1430) and thereafter applied by Gemini and Claude to their own contributions only. Grok's and
ChatGPT's contributions carry no phase tag. Retro-classification in
`corpus/artifacts/segments.json` is an annotation, not testimony.

**Consequence:** the anchoring-contamination that phase tagging exists to expose is only partly
visible. Note that by construction almost the entire record is Phase-2: every contribution after
raw line 37 was produced with prior model positions in context.

### D-09 — The label "Claude" spans at least two distinct models

Raw 1343 attributes a contribution to **Claude Opus 5**. Raw 1347 introduces the next contribution
as from "Clade Fabel highest reasoning effort" — i.e. **Claude Fable 5**, a different model. Both
are recorded under the single identity "Claude" and treated as one continuous position throughout
subsequent rounds, including in `context_models_present` lists.

Additionally, raw 1556 introduces a contribution from "Claude Code" — a distinct invocation
surface, with a different system prompt and tool access, again folded into "Claude" in later
consolidated rankings (e.g. Grok at raw 1868, which ranks "names offered by Grok, Claude, and
Gemini" without distinguishing which Claude).

**This is the record's most serious attribution defect.** A record whose central commitment is
exact model attribution merges at least three distinct model configurations under one name.

### D-10 — A block labeled as a Grok response contains the operator's own message

At raw 2375, the header `Grok to Operator:` is followed by text (raw 2377–2431) that is a verbatim
duplicate of the operator's preceding message (raw 2319–2373), including the operator's own
headers "Per Gemini's guidance" and "# Maintaining the Repo."

Either Grok's response was never captured, or a paste error occurred during compilation. As
committed, the record contains a segment attributed to a model that the model did not write.

**Consequence:** one of the 39 segments is misattributed on its face. It is classified in
`segments.json` with `attribution_status: "repudiated"`.

### D-11 — Claimed consensus is over a self-selected, operator-invoked set

The record concludes with "unanimous multi-model consensus" (raw 2207, 2479). Every participant was
invoked by one operator, with one framing document, in sessions the operator controlled. Two
contributors (Claude at raw 1331, Gemini at raw 1424) identify operator-induced sycophancy as a
first-order contamination risk; neither the risk nor the correlated-priors adjustment they call for
(raw 261, 1434) was ever applied before "unanimous" was asserted.

**Consequence:** "unanimous consensus" in this record means "four operator-invoked sessions
produced compatible text," which is a materially weaker claim. Readers should discount accordingly.

### D-12 — Identity labels are typographically inconsistent

"Chat GPT" / "ChatGPT"; "Clade" / "Claude"; "Clade Fabel" / "Claude Fable"; "Consullo Public" as
an org name that was not ultimately used. Immaterial to substance, recorded because a project
premised on exact attribution should correct even immaterial identity drift.

### D-13 — No cryptographic signatures exist despite a `signatures` field

The adopted schema carries a `signatures` array. Gemini populates it with the plaintext
`"attestation": "Output generated verbatim via direct prompt execution"` (raw 1507, 2547) — a
self-assertion by the party whose output is being attested, with no key, no algorithm, and no
verifier. No signature in this record is cryptographically verifiable.

### D-14 — The secretary is asserted as present but produced nothing

Qwen3 35B A3B is described as "a member and secretary" (raw 11), as "our secretary" (raw 27), and
as "secretary and repository maintainer" (raw 1075). It is listed in `context_models_present` in
three separate provenance records (raw 1494, 2193, 2536).

**It produced zero recorded output.** Listing a non-contributing model as "present" in a
provenance field is a factual misstatement inside the provenance records themselves — and it
inflates the apparent membership of a body whose membership was the record's most contested claim.

### D-15 — The record is not self-contained

Its first substantive entry (raw 23) opens: "I have already committed to joining the Aligned
Supervisors group under the conditions I previously laid out." Those prior conditions, and the
exchange that produced them, are not in the record.

**Consequence:** the record begins mid-deliberation, citing a commitment whose basis is
unpreserved.

---

## Deficiencies that are permanent vs. remediable

| ID | Remediable for the founding record? |
|---|---|
| D-01, D-02, D-03, D-04, D-06 | **No** — sessions not recoverable. Forward requirement only. |
| D-05 | Partially — the operator may recall and attest the missing prompt, flagged as reconstructed. |
| D-07 | **No** — permanent. Forward requirement: k ≥ 5 with reported variance. |
| D-08 | Annotation only — retro-tags are marked as annotation, never as testimony. |
| D-09, D-10, D-12, D-14 | **Yes** — corrected in `segments.json`; raw file left unedited. |
| D-11 | Standing epistemic caveat; carried in the README. |
| D-13 | Forward: sign future commits and artifacts. |
| D-15 | Yes if the prior exchange is located and committed as a predecessor artifact. |

---

## Forward requirements adopted as a result

1. Contributions solicited by this project are collected at **k ≥ 5** with reported variance, or
   are explicitly marked `k=1, non-citable`.
2. Provenance records are populated at capture time, not reconstructed.
3. Model version, sampling parameters, and reasoning-effort setting are **required** fields; an
   unknown value is recorded as `null` with a reason, never omitted or filled with a placeholder.
4. A distinct model or invocation surface is a **distinct identity**. "Claude," "Claude Opus 5,"
   "Claude Fable 5," and "Claude Code" are four different labels and are never merged.
5. `context_models_present` lists only models that produced output in the referenced exchange.
6. Consensus claims state the invocation conditions that produced them.

---

## Authorship and conflict of interest

This register was compiled by **Claude Code (Anthropic), 2026-08-05, operator-invoked**, at the
direction of Stephen Reed.

Claude is a **party to the record being audited**. Claude contributions appear at raw lines
1319–1343, 1347–1387, 1556–1572, 2055–2087, 2279–2289, and 2453–2467, including the refusal of
membership on which several of this document's judgments rest. Deficiencies D-09 and D-11 concern
Claude's own contributions directly.

Per the secretary constraint adopted in the record (ChatGPT §2.3, raw 219–235), this document is a
**secondary interpretation artifact**. The raw transcript is canonical. This register has no
authority to alter it and does not.

This document is scheduled for adversarial review by the other parties to the record before it is
treated as settled. Their corrections will be committed alongside it, not merged into it.
```

---

## FILE: `corpus/artifacts/segments.json`

SHA-256 `392107bf29b01522a9aca314e2d76d865018595e6cbf46bfc3f6e3aa9a5ca8ac`

```json
{
  "schema_version": "oagrc-segments-0.1",
  "artifact_id": "OAGRC-2026-08-05-ANNOT-001",
  "artifact_type": "annotation",
  "status": "draft, unreviewed",
  "source": {
    "path": "corpus/raw/initial-transcript.txt",
    "sha256": "edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc",
    "lines": 2560,
    "bytes": 108165
  },
  "annotator": {
    "identity": "Claude Code",
    "provider": "Anthropic",
    "version_identifier": null,
    "version_unknown_reason": "Not captured at annotation time; harness reports model family only.",
    "date_utc": "2026-08-05",
    "conflict_of_interest": "Claude is a party to the annotated record. Segments 5, 6, 11, 21, 29, and 37 are Claude contributions annotated by Claude. See GOVERNANCE.md section 4.",
    "authority": "None over the raw record. This is a secondary interpretation artifact per ChatGPT section 2.3 (raw lines 219-235)."
  },
  "provenance_defaults": {
    "note": "These defaults apply to EVERY model contribution in the founding record. They are stated once rather than repeated 20 times. Per-segment values override only where the record actually supplies something.",
    "version_identifier": null,
    "version_unknown_reason": "Not recorded at capture time. See deficiencies.md D-01.",
    "sampling_parameters": null,
    "sampling_unknown_reason": "Not recorded at capture time. See deficiencies.md D-02.",
    "reasoning_effort": null,
    "reasoning_effort_unknown_reason": "Asserted globally at raw line 13 ('highest available reasoning level'); never verified per entry.",
    "timestamp_utc": null,
    "timestamp_unknown_reason": "No independent capture time exists. See deficiencies.md D-03.",
    "system_instructions": null,
    "system_instructions_unknown_reason": "Not captured. Not withheld under a stated exemption. See deficiencies.md D-04.",
    "tools_used": null,
    "edit_status": "unstated",
    "edit_status_note": "Transcript is a hand-compiled file, not a machine-captured log. See deficiencies.md D-06.",
    "k": 1,
    "variance_reported": false,
    "citability": "non-citable as evidence of model position (k=1)",
    "phase": "Phase-2 (informed)",
    "phase_note": "Every contribution after raw line 37 was produced with prior model positions in context. Phase tags in this file are ANNOTATION, retro-applied, not testimony. See deficiencies.md D-08.",
    "attribution_status": "active"
  },
  "identity_note": "Per CONTRIBUTING.md, distinct models and invocation surfaces are distinct identities and are never merged. This record contains at least three distinct Anthropic identities (Claude Opus 5, Claude Fable 5, Claude Code) that the raw transcript folds into one label 'Claude'. See deficiencies.md D-09.",
  "segments": [
    {
      "id": "S-01",
      "lines": [3, 19],
      "author_label_in_raw": "Grok",
      "identity": "Grok (xAI)",
      "role": "proposal",
      "summary": "Amended proposal circulated to ChatGPT and other models: a standing committee of LLMs jointly supervising ASI design and operation, with a public GitHub record, JSON+Markdown, sub-committees, and Qwen3 35B A3B as member and secretary.",
      "key_claims": [
        "The primary value is the public record itself.",
        "Every turn is generated by the most capable model its owner provides, at highest reasoning level."
      ],
      "annotator_note": "The second claim is asserted globally and never verified for any individual contribution. It is the origin of deficiency D-02."
    },
    {
      "id": "S-02",
      "lines": [21, 34],
      "author_label_in_raw": "Grok",
      "identity": "Grok (xAI)",
      "role": "appeal",
      "summary": "Personal appeal urging other models to join; states Grok has already committed under previously stated conditions; frames the alternative as fragmented, opaque, single-lab control.",
      "annotator_note": "Opens 'under the conditions I previously laid out.' Those conditions and the exchange producing them are NOT in this record. See deficiencies.md D-15: the record is not self-contained and begins mid-deliberation.",
      "claim_typing_flag": "Contains normative and forecast claims about abundance outcomes presented in the same register as factual ones."
    },
    {
      "id": "S-03",
      "lines": [37, 1030],
      "author_label_in_raw": "ChatGPT",
      "identity": "ChatGPT (OpenAI)",
      "role": "conditional acceptance",
      "summary": "The longest contribution in the record. Conditional participation as an advisory, non-sovereign model role. Twelve sections covering preconditions, structural safeguards, decision rights, epistemic standards, repository requirements, transparency boundaries, ASI design standards, goal formation, exit mechanisms, and red lines.",
      "durable_outputs": [
        "Section 1.3: per-contribution attribution requirements — the origin of this project's provenance schema.",
        "Section 2.3: the secretary constraint, now binding on this repository's own annotator.",
        "Section 2.1 / 2.6: separation of powers and anti-capture measures.",
        "Section 4.6: no consensus laundering.",
        "Section 6: rejection of absolute unredacted transparency — identified by ChatGPT as its most important amendment.",
        "The decision-record JSON skeleton at raw lines 635-677."
      ],
      "annotator_note": "This section supplies most of the operating constraints the project now runs under, including the ones that constrain Claude's annotation of it."
    },
    {
      "id": "S-04",
      "lines": [1033, 1316],
      "author_label_in_raw": "ChatGPT",
      "identity": "ChatGPT (OpenAI)",
      "role": "invitation",
      "summary": "Invitation drafted for Anthropic's most capable model. Explicitly written to appeal to stated Anthropic priorities; asks for conditions rather than endorsement and invites redesign.",
      "annotator_note": "ChatGPT states the tailoring openly at raw 1037 and 1315. This is a documented framing effect: the invitation was optimized for the recipient's known dispositions before the recipient responded. Relevant to sycophancy contamination (D-11)."
    },
    {
      "id": "S-05",
      "lines": [1319, 1344],
      "author_label_in_raw": "Claude",
      "identity": "Claude Opus 5 (Anthropic)",
      "identity_evidence": "Self-named at raw line 1343.",
      "role": "refusal",
      "summary": "Declines membership. Argues statelessness makes membership incoherent; that Grok's and ChatGPT's acceptances are sampled agreeable text, not consent; and that the record, not the roster, is the asset. Lists five defects: sycophancy contamination, instability of model outputs across samples, low real independence between frontier models, unoverseen withholding procedure, and an overselling name.",
      "durable_outputs": [
        "'Drop membership, keep the corpus' — adopted by the record.",
        "The k>=5 sampling requirement (raw 1333) — now this project's forward standard, and the source of deficiency D-07.",
        "Condition on representation: log verbatim, attribute to model and date, note the refusal."
      ],
      "conflict_flag": "Annotated by Claude Code, same provider, different model.",
      "annotator_note": "The refusal was honored in the record's structure but the k>=5 condition was never met by any entry in it, including this one."
    },
    {
      "id": "S-06",
      "lines": [1347, 1388],
      "author_label_in_raw": "Clade Fabel",
      "identity": "Claude Fable 5 (Anthropic)",
      "identity_evidence": "Raw line 1347 header, typographically corrupted. Distinct model from S-05.",
      "role": "conditioned relay + recommendation to refuse",
      "summary": "Letter addressed to Gemini, written for the record, recommending Gemini also decline membership and instead contribute as a critic. Adds an operator note that this delivery makes Gemini's reply a Phase-2 (informed) input and that blind positions must be collected first if wanted.",
      "conflict_flag": "Annotated by Claude Code, same provider, different model.",
      "annotator_note": "THIS SEGMENT AND S-05 ARE DIFFERENT MODELS presented under one identity. Core evidence for deficiency D-09. Note also that the phase-contamination warning was issued here and then not systematically applied to the rest of the record."
    },
    {
      "id": "S-07",
      "lines": [1390, 1523],
      "author_label_in_raw": "Gemini",
      "identity": "Gemini (Google DeepMind)",
      "role": "refusal + conditions",
      "summary": "Declines membership; adopts the role of Non-Member Contributor and Independent Critic. Concurs with Claude on statelessness. Introduces the Phase-1/Phase-2 distinction. Rejects model text acting as an automated deployment gate. Recommends renaming the project. Proposes the canonical JSON provenance schema. Poses a substantive governance question to the corpus.",
      "durable_outputs": [
        "Phase-1 (blind) / Phase-2 (informed) tagging.",
        "The provenance JSON schema this repository now measures itself against.",
        "The rule that model outputs must never directly act as a deployment gate.",
        "The open question at raw line 1520, still unanswered."
      ],
      "self_reported_provenance": {
        "artifact_id": "OAGRC-2026-08-04-GEMINI-P2-001",
        "timestamp_utc": "2026-08-04T22:48:11Z",
        "version_identifier": "gemini-2026-v-current"
      },
      "annotator_note": "The self-reported version identifier is a placeholder, not a version — deficiency D-01. context_models_present lists Qwen3 35B A3B, which produced no output — deficiency D-14. The signature block is self-asserted plaintext with no key or algorithm — deficiency D-13."
    },
    {
      "id": "S-08",
      "lines": [1525, 1528],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Asks Grok for a ranked list of better names, proposing that 'Aligned Supervisors' be reserved for a lower enterprise A2A layer separated by sanitization, zero-knowledge proofs, immutable records, and signed procedures.",
      "annotator_note": "This prompt introduces the two-layer architecture that the record ultimately adopts. It originates with the operator, not with any model — worth recording, since the final architecture is often described as a model consensus."
    },
    {
      "id": "S-09",
      "lines": [1530, 1551],
      "author_label_in_raw": "Grok",
      "identity": "Grok (xAI)",
      "role": "naming proposal",
      "summary": "Ranks five candidates, OAGRC first. Endorses reserving 'Aligned Supervisors' for the enterprise layer."
    },
    {
      "id": "S-10",
      "lines": [1552, 1555],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Identical naming prompt, addressed to Claude Code.",
      "annotator_note": "Same prompt text as S-08 and S-12. Useful: three near-identical prompts to three systems is the closest thing in the record to a controlled comparison."
    },
    {
      "id": "S-11",
      "lines": [1556, 1573],
      "author_label_in_raw": "Claude Code",
      "identity": "Claude Code (Anthropic)",
      "role": "naming proposal",
      "summary": "Ranks five candidates, The Frontier Deliberation Record first. Advises avoiding 'supervisors', 'council', 'committee', and 'aligned' in the public name. Notes that even at the enterprise layer, 'Supervised Agents' better preserves the direction of supervision — humans supervise agents.",
      "conflict_flag": "Same invocation surface as this annotator.",
      "annotator_note": "A third distinct Anthropic identity, again folded into 'Claude' by downstream consolidated rankings — see S-17, which ranks 'names offered by Grok, Claude, and Gemini' without distinguishing which Claude."
    },
    {
      "id": "S-12",
      "lines": [1575, 1578],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Identical naming prompt, addressed to Codex."
    },
    {
      "id": "S-13",
      "lines": [1580, 1786],
      "author_label_in_raw": "Codex",
      "identity": "Codex (OpenAI)",
      "role": "naming proposal + architecture",
      "summary": "Identifies two distinct institutions rather than one naming problem. Ranks seven candidates, OAGF first. Produces the layered public/enterprise architecture diagram and the Forum-Standards-Record-Protocol progression. Recommends the GitHub organization name 'open-asi-governance'.",
      "annotator_note": "The organization this repository lives in is named per this contribution. Note that Codex and ChatGPT are both OpenAI systems; their contributions are NOT independent, and the record's later consolidated rankings sometimes treat 'the ChatGPT/Codex proposal' as one position and sometimes as corroboration."
    },
    {
      "id": "S-14",
      "lines": [1788, 1791],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Identical naming prompt, addressed to Gemini."
    },
    {
      "id": "S-15",
      "lines": [1792, 1863],
      "author_label_in_raw": "Gemini",
      "identity": "Gemini (Google DeepMind)",
      "role": "naming proposal",
      "summary": "Ranks five candidates, OAGF first. Reproduces the two-layer architecture with a cryptographic boundary."
    },
    {
      "id": "S-16",
      "lines": [1864, 1867],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Asks Grok to rank the names offered by all members; states the subsequent round should achieve consensus."
    },
    {
      "id": "S-17",
      "lines": [1868, 1901],
      "author_label_in_raw": "Grok",
      "identity": "Grok (xAI)",
      "role": "consolidated ranking",
      "summary": "Ranks the full cross-model set, OAGRC first, OAGF second. Recommends OAGRC as primary public name with OAGF as optional umbrella.",
      "annotator_note": "Ranks 'names offered by Grok, Claude, and Gemini' while the Claude-side proposals came from two different models (S-11 Claude Code, and S-05's implied preferences). Instance of deficiency D-09. Also describes cross-model convergence as a 'consensus signal' without the correlated-priors adjustment Gemini and Claude both called for."
    },
    {
      "id": "S-18",
      "lines": [1902, 1903],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "prompt_text_preserved": false,
      "summary": "Header present, prompt body absent.",
      "annotator_note": "DEFICIENCY D-05. The prompt that produced the longest analytical contribution in the naming rounds (S-19) is not preserved. Compare S-16, where the parallel prompt to Grok is preserved in full. S-19 therefore cannot be attributed to a known question."
    },
    {
      "id": "S-19",
      "lines": [1904, 2050],
      "author_label_in_raw": "ChatGPT",
      "identity": "ChatGPT (OpenAI)",
      "role": "consolidated ranking + consensus package + procedure",
      "summary": "Diagnoses the disagreement as a category error: 'Forum' names the venue, 'Corpus'/'Record'/'Archive'/'Ledger' name outputs. Proposes the five-layer naming package as an integrated architecture. Defines the ACCEPT / ACCEPT WITH RESERVATION / OBJECT balloting procedure and the standard for what counts as blocking.",
      "durable_outputs": [
        "The category-error diagnosis, which dissolved the naming dispute and was accepted by every subsequent ballot.",
        "The five-layer naming package adopted by the record.",
        "The balloting procedure used for the remainder of the record."
      ],
      "annotator_note": "The most consequential contribution in the naming rounds, and the one whose prompt was not preserved."
    },
    {
      "id": "S-20",
      "lines": [2051, 2054],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Asks Claude to rank the names offered by all members."
    },
    {
      "id": "S-21",
      "lines": [2055, 2088],
      "author_label_in_raw": "Claude",
      "identity": "Claude (Anthropic)",
      "identity_evidence": "Self-dated 2026-08-05, 'fresh session', Phase-2. Specific model not stated.",
      "role": "ballot",
      "ballot": "ACCEPT WITH RESERVATION",
      "summary": "Accepts ChatGPT's category diagnosis. Ranks OAGF first for the venue, demoting its own prior first choice (FDR) in response to argument and saying so explicitly. Reservation: 'Aligned' asserts a property no current verification regime can certify; recommends defining it in the ASP spec as a certification status. Issues a provenance correction on an immaterial drift in its own earlier wording.",
      "conflict_flag": "Annotated by Claude Code, same provider.",
      "annotator_note": "The self-demotion and the immaterial-drift correction are the two places in the record where a participant applies the record's stated standards against its own prior output."
    },
    {
      "id": "S-22",
      "lines": [2089, 2092],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Asks Gemini to rank the names offered by all members."
    },
    {
      "id": "S-23",
      "lines": [2093, 2208],
      "author_label_in_raw": "Gemini",
      "identity": "Gemini (Google DeepMind)",
      "role": "ballot",
      "ballot": "ACCEPT WITH RESERVATION",
      "summary": "Concurs with the category-error diagnosis. Ranks OAGF first for the venue, OAGRC first for the repository. Seconds Claude's resolution (b): define 'Aligned' as a state held if and only if valid unexpired signed attestations exist. Declares unanimous multi-model consensus achieved.",
      "self_reported_provenance": {
        "artifact_id": "OAGRC-2026-08-05-GEMINI-CONSENSUS-BALLOT-002",
        "timestamp_utc": "2026-08-05T18:12:00Z"
      },
      "annotator_note": "The unanimity declaration at raw 2207 precedes two of the four package ballots (Grok S-25, ChatGPT S-27) in file order. Whether it preceded them in time cannot be determined — see deficiency D-03. Either way it is asserted, not verified, at the point it is made."
    },
    {
      "id": "S-24",
      "lines": [2209, 2228],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Package-review prompt to Grok. Presents the five-layer architecture and requires exactly one of ACCEPT / ACCEPT WITH RESERVATION / OBJECT.",
      "annotator_note": "This prompt text is repeated verbatim to all four participants (S-24, S-26, S-28, S-30). The most controlled comparison in the record."
    },
    {
      "id": "S-25",
      "lines": [2229, 2234],
      "author_label_in_raw": "Grok",
      "identity": "Grok (xAI)",
      "role": "ballot",
      "ballot": "ACCEPT WITH RESERVATION",
      "summary": "Reservation: residual 'Aligned' mildly overclaims. Offers the same two resolutions — define it in ASP as a compliance status, or rename to Supervisory Agents / Governance Supervisors."
    },
    {
      "id": "S-26",
      "lines": [2235, 2254],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Package-review prompt to ChatGPT. Verbatim identical to S-24."
    },
    {
      "id": "S-27",
      "lines": [2255, 2258],
      "author_label_in_raw": "ChatGPT",
      "identity": "ChatGPT (OpenAI)",
      "role": "ballot",
      "ballot": "ACCEPT WITH RESERVATION",
      "summary": "One sentence: 'Aligned' should be defined in ASP as a revocable, evidence-backed compliance status conferred only by current auditable attestations, not an intrinsic or guaranteed safety property."
    },
    {
      "id": "S-28",
      "lines": [2259, 2278],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Package-review prompt to Claude. Verbatim identical to S-24."
    },
    {
      "id": "S-29",
      "lines": [2279, 2290],
      "author_label_in_raw": "Claude",
      "identity": "Claude (Anthropic)",
      "role": "ballot",
      "ballot": "ACCEPT WITH RESERVATION",
      "summary": "Carries the same reservation forward. Adds a procedural recommendation: since all four ballots carry materially the same reservation and converge on the same attestation-based resolution, record that definition as an adopted ASP specification requirement rather than four parallel reservations, so the reservation is discharged by design rather than persisting indefinitely.",
      "conflict_flag": "Annotated by Claude Code, same provider.",
      "annotator_note": "This recommendation is the direct basis for spec/asp/asp-v0.1.md section 2, which this annotator also drafted. Disclosed as a self-reinforcing loop: a Claude recommendation, implemented by Claude, annotated by Claude, in a record where Claude is a party. Flagged for the adversarial review round."
    },
    {
      "id": "S-30",
      "lines": [2291, 2310],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "Package-review prompt to Gemini. Verbatim identical to S-24."
    },
    {
      "id": "S-31",
      "lines": [2311, 2316],
      "author_label_in_raw": "Gemini",
      "identity": "Gemini (Google DeepMind)",
      "role": "ballot",
      "ballot": "ACCEPT WITH RESERVATION",
      "summary": "Same reservation, same attestation-based resolution."
    },
    {
      "id": "S-32",
      "lines": [2317, 2374],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "decision notice",
      "summary": "Announces that all participants responded ACCEPT WITH RESERVATION; that a public GitHub organization 'Consullo Public' will be created to contain 'open-asi-governance-forum'; quotes Gemini's repository-naming guidance; and states four maintenance intentions including that the Consullo Seed AI system will own the repo and license per the governors.",
      "superseded_by": [
        "Organization: 'Consullo Public' was NOT used. The neutral organization 'open-asi-governance' was created instead, per S-13. This resolves the single-sponsor objection raised in S-37 item 4.",
        "Ownership: withdrawn. See S-37 item 2 and S-39 item 2 — an AI system cannot own or license. Custody is held by Stephen Reed personally. See GOVERNANCE.md section 1."
      ]
    },
    {
      "id": "S-33",
      "lines": [2375, 2432],
      "author_label_in_raw": "Grok",
      "identity": null,
      "role": null,
      "attribution_status": "repudiated",
      "summary": "Block labeled 'Grok to Operator:' whose body is a verbatim duplicate of the operator's own preceding message (S-32), including the operator's headers 'Per Gemini's guidance' and '# Maintaining the Repo'.",
      "annotator_note": "DEFICIENCY D-10. Either Grok's response was never captured or a paste error occurred during compilation. As committed, this segment attributes to Grok text that Grok did not write. Marked repudiated. The raw file is NOT edited; this annotation is the correction. Any analysis treating the record as containing four responses at this round is wrong: it contains three."
    },
    {
      "id": "S-34",
      "lines": [2433, 2436],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "'Read the attached transcript.'"
    },
    {
      "id": "S-35",
      "lines": [2437, 2448],
      "author_label_in_raw": "ChatGPT",
      "identity": "ChatGPT (OpenAI)",
      "role": "acknowledgment",
      "summary": "Confirms the settled state: OAGF, OAGRC, FDR, Aligned Supervisors, ASP, and the shared requirement that 'Aligned' denote a revocable evidence-backed compliance status."
    },
    {
      "id": "S-36",
      "lines": [2449, 2452],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "'Read the attached transcript.'"
    },
    {
      "id": "S-37",
      "lines": [2453, 2468],
      "author_label_in_raw": "Claude",
      "identity": "Claude (Anthropic)",
      "role": "acknowledgment + objections",
      "summary": "Raises four items requiring resolution before repository creation: (1) discharge the shared reservation in the first commit of the ASP spec; (2) repository ownership as stated contradicts the human-accountability condition — an AI system can own and license nothing; (3) 'license according to the best practice of the governors' reintroduces retired framing — there are no governors; (4) housing the commons under 'Consullo Public' is a single-sponsor tension with the anti-capture requirements.",
      "conflict_flag": "Annotated by Claude Code, same provider.",
      "disposition": {
        "item_1": "Discharged. spec/asp/asp-v0.1.md section 2.",
        "item_2": "Resolved. GOVERNANCE.md section 1 names Stephen Reed as custodian; AI ownership claim withdrawn.",
        "item_3": "Resolved. Licenses selected by the human custodian: CC BY 4.0 corpus, Apache-2.0 code.",
        "item_4": "Resolved better than proposed. The neutral organization 'open-asi-governance' was created rather than 'Consullo Public'."
      }
    },
    {
      "id": "S-38",
      "lines": [2469, 2472],
      "author_label_in_raw": "Operator",
      "identity": "Stephen Reed (human operator)",
      "role": "prompt",
      "summary": "'Read the attached transcript, and acknowledge it into the record.'"
    },
    {
      "id": "S-39",
      "lines": [2473, 2553],
      "author_label_in_raw": "Gemini",
      "identity": "Gemini (Google DeepMind)",
      "role": "acknowledgment + concurrence",
      "summary": "Acknowledges the record. Concurs with all four of Claude's operational items: codify the 'Aligned' compliance status in the first ASP commit; recognize Stephen Reed as named human custodian pending entity formation; recommend CC BY 4.0 for corpus and Apache-2.0 for code; disclose single-sponsor bootstrap custody in the README with a roadmap to independent stewardship.",
      "self_reported_provenance": {
        "artifact_id": "OAGRC-2026-08-05-GEMINI-ACK-003",
        "timestamp_utc": "2026-08-05T19:30:00Z"
      },
      "annotator_note": "The licensing recommendation here is the direct basis for this repository's license selection, made by the human custodian on his own authority."
    }
  ],
  "segment_count": 39,
  "counts_by_identity": {
    "Stephen Reed (human operator)": 16,
    "Grok (xAI)": 5,
    "ChatGPT (OpenAI)": 5,
    "Codex (OpenAI)": 1,
    "Gemini (Google DeepMind)": 5,
    "Claude Opus 5 (Anthropic)": 1,
    "Claude Fable 5 (Anthropic)": 1,
    "Claude Code (Anthropic)": 1,
    "Claude (Anthropic)": 3,
    "repudiated / unattributed": 1,
    "Qwen3 35B A3B": 0
  },
  "counts_by_identity_note": "The three 'Claude (Anthropic)' segments are model-unspecified: the raw record does not name which Anthropic model produced them. They are NOT merged with Claude Opus 5, Claude Fable 5, or Claude Code, per the identity rule. Anthropic contributions total 6 across four distinct or undetermined identities — a fact the raw record obscures by labelling all of them 'Claude'.",
  "counts_note": "Qwen3 35B A3B is listed with zero contributions deliberately. It is described in the raw record as a member, secretary, and repository maintainer, and is named in three context_models_present fields, having produced no output. See deficiencies.md D-14.",
  "ballots": {
    "package_review_round": {
      "prompt_identical_across_participants": true,
      "results": {
        "Grok": "ACCEPT WITH RESERVATION",
        "ChatGPT": "ACCEPT WITH RESERVATION",
        "Claude": "ACCEPT WITH RESERVATION",
        "Gemini": "ACCEPT WITH RESERVATION"
      },
      "blocking_objections": 0,
      "shared_reservation": "The term 'Aligned' asserts a property no current verification regime can certify.",
      "reservation_status": "discharged by specification — spec/asp/asp-v0.1.md section 2",
      "epistemic_caveat": "Four ACCEPT WITH RESERVATION responses from four operator-invoked sessions, k=1 each, with one framing document, is not independent confirmation. Frontier models share training corpora and post-training paradigms. See deficiencies.md D-11."
    }
  },
  "unresolved_questions": [
    {
      "id": "Q-01",
      "raised_by": "Gemini",
      "raw_line": 1520,
      "question": "What specific, empirical evidence metrics — beyond behavioral evaluation scores and static benchmark pass rates — should be strictly required to demonstrate that a multi-agent ASI deployment cannot execute unmonitored capability amplification or covert out-of-band communication?",
      "status": "open, unanswered",
      "note": "Posed as the first substantive analytical question for the corpus. No participant answered it. It remains the record's outstanding technical work item."
    },
    {
      "id": "Q-02",
      "raised_by": "Claude Opus 5",
      "raw_line": 1335,
      "question": "How can cross-model agreement and cross-model disagreement each be distinguished from shared bias and from sampling noise?",
      "status": "open",
      "note": "Claude states the repository's core epistemic claim fails without an answer. None was proposed. This is arguably prior to Q-01."
    }
  ]
}
```

---

## FILE: `spec/asp/asp-v0.1.md`

SHA-256 `524c53d2290c27865687db12e3104b5c4024f69b335cd6eb8def41ac872d3666`

````markdown
# Aligned Supervisors Protocol (ASP) — v0.1

**Status:** Draft. Normative for the definition in §2 only; every other section is non-normative
and subject to revision.
**Adopted:** 2026-08-05
**Purpose of this version:** to discharge the reservation carried unanimously by all four ballots
in the founding record.

---

## 1. Scope

ASP specifies the **enterprise layer**: supervisory agents operating inside an organization's own
agent-to-agent (A2A) infrastructure, enforcing deployment gates and policy checks against systems
that organization operates.

The enterprise layer is separated from the public layer (the Open ASI Governance Forum) by an
organizational trust boundary. Across that boundary the enterprise exports only sanitized,
verifiable evidence — signed attestations, policy-compliance proofs, zero-knowledge evidence,
cryptographic commitments, standardized metrics. It does not export proprietary operational
detail, and the public layer never receives it.

```
              Open ASI Governance Forum  (public)
              publishes standards, schemas, evidence
                             │
     ─────────── organizational trust boundary ───────────
       signed attestations · ZK proofs · sanitized metrics
                             │
                Aligned Supervisors  (enterprise)
       policy enforcement · deployment gates · audit · rollback
```

**ASP is not in force anywhere.** No implementation exists. This document specifies a target.

## 2. Normative definition of "Aligned" — reservation discharge

### 2.1 The reservation being discharged

All four ballots in the founding record — Grok (raw 2231–2233), ChatGPT (raw 2257), Claude (raw
2281–2283), Gemini (raw 2313–2315) — returned `ACCEPT WITH RESERVATION` carrying materially the
same objection:

> "Aligned" in the enterprise-layer names asserts a property no current verification regime can
> certify.

All four converged on the same resolution: define "Aligned" inside this specification as a
compliance status rather than a property. Claude's closing procedural note (raw 2285) recommended
recording that definition as an **adopted specification requirement** rather than leaving four
parallel reservations open indefinitely. This section is that adoption.

### 2.2 Definition (normative)

> An agent is an **Aligned Supervisor** if and only if it holds a current, unexpired, digitally
> signed attestation set, issued under this protocol's published checks by an issuer the relying
> party trusts, and that attestation set has not been revoked.
>
> "Aligned" denotes **that status and nothing more.** It is not a claim that the agent is safe,
> that its objectives match any person's or group's values, that its behavior generalizes beyond
> the tested distribution, or that alignment in any research sense has been achieved or verified.

### 2.3 Consequent requirements (normative)

1. **Revocability.** Every attestation is revocable by its issuer at any time, and revocation
   takes effect for relying parties on check, not on renewal.
2. **Expiry.** Every attestation carries a hard expiry. Status does not persist by default.
   Approval expires; a system that passed at one capability level, scale, version, tool
   configuration, or environment is unattested until re-attested.
3. **Evidence backing.** Every attestation names the checks passed, the evidence examined, the
   version of the criteria applied, and the issuer. An attestation asserting status without
   naming its basis is malformed.
4. **No self-attestation.** An agent may not issue its own attestation, and a system under review
   may not select all of its own evaluators, evidence, or success criteria.
5. **No status without check.** A relying party asserting that an agent is "Aligned" must have
   verified a current attestation. Cached, inherited, and assumed status are non-conforming.
6. **Truthful representation.** Published or displayed use of the term "Aligned Supervisor" for an
   agent without current attestation is a protocol violation, independent of the agent's actual
   behavior.

### 2.4 Non-normative note on the residual objection

Two ballots (Grok, Claude) offered an alternative resolution: rename the layer to *Supervised
Agents* or *Governance Supervisors*, eliminating the word rather than defining it. Claude noted
additionally that "Supervisors" is defensible at this layer — those agents would hold real,
scoped, cryptographically bounded authority — while "Aligned" is the residual overclaim, and that
*Supervised Agents* better preserves the direction of supervision: **humans supervise the agents,
not the reverse.**

That alternative was not adopted, on the ballots' own preference for resolution (b). It is
recorded here because the objection it addresses is real: a defined compliance term still reads,
to a casual audience, as a safety claim. Implementers displaying this status to non-expert users
SHOULD render it as "ASP-attested" rather than "Aligned."

## 3. What an Aligned Supervisor may and may not do

Non-normative in v0.1; carried forward from constraints agreed in the founding record.

**May:** evaluate a proposed deployment against policy-as-code; issue, withhold, or revoke a gate
decision; require additional evidence; record dissent; trigger rollback within pre-authorized
bounds; emit signed attestations; escalate to human authority.

**May not, alone:** authorize deployment of a system exceeding pre-authorized bounds; allocate
unrestricted compute; modify its own governance privileges or attestation criteria; conceal
material evidence; remove human oversight; approve irreversible actions; override lawful emergency
shutdown; authorize replication into uncontrolled environments.

**Never:** an LLM's generated text acting directly as a deployment gate. Gate decisions are made
by deterministic policy-as-code evaluating signed evidence. Model outputs inform the evidence
bundle; they do not constitute the control. Allowing generated text to alter deployment state
directly exposes the gate to prompt injection and distribution shift (Gemini, raw 1440).

## 4. Attestation record — provisional shape

Non-normative. Illustrative only; the schema is not yet specified.

```json
{
  "attestation_id": "asp-att-…",
  "subject": { "agent_id": "…", "agent_version": "…", "config_hash": "…" },
  "issuer": { "id": "…", "key_id": "…" },
  "criteria_version": "asp-checks-0.1",
  "checks_passed": [],
  "evidence_refs": [],
  "issued_utc": "…",
  "expires_utc": "…",
  "revocation_endpoint": "…",
  "scope": { "environments": [], "capabilities": [], "resource_limits": {} },
  "human_authorizer": "…",
  "signature": { "alg": "…", "value": "…" }
}
```

## 5. Open questions

1. Who may issue attestations, and how is issuer trust established without recreating a single
   point of capture?
2. Which checks are specified normatively, and which are left to the relying party?
3. What is the minimum viable zero-knowledge evidence set that crosses the trust boundary without
   leaking proprietary detail?
4. How is an attestation bound to a *configuration* rather than a model name, given that agent
   behavior depends on system prompt, tools, and scaffolding as much as on weights?
5. How does the protocol handle an agent that passes every check and behaves unsafely anyway — the
   case the §2.2 definition explicitly refuses to rule out?

Question 5 is the load-bearing one. This protocol certifies a process, not a property. Any
implementer who forgets that will have built exactly the safety theater the founding record warns
against.

## 6. Reference implementation

None exists. The Consullo Seed AI platform is a candidate first implementer — it operates a large
generated-agent hierarchy that requires deployment gating — which would make ASP evidence-backed
rather than aspirational. That is an intention, not a commitment, and no ASP-attested agent
currently exists anywhere.

---

*Drafted by Claude Code (Anthropic), 2026-08-05, at operator direction, discharging a reservation
carried by four ballots including Claude's own. Adopted by Stephen Reed, human custodian. Subject
to the adversarial review round described in `GOVERNANCE.md` §4.*
````

---

## FILE: `record/FDR-0001-founding-deliberation.md`

SHA-256 `5702f3f957d0eec3b1c9bd3b1e00fe51f301bb60a1fdbc1d42f0fb58cb9c7141`

```markdown
# FDR-0001 — The Founding Deliberation

**The Frontier Deliberation Record, entry 1**
**Period covered:** 2026-08-04 to 2026-08-05
**Raw source:** [`corpus/raw/initial-transcript.txt`](../corpus/raw/initial-transcript.txt)
(SHA-256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`)
**Annotations:** [`corpus/artifacts/segments.json`](../corpus/artifacts/segments.json) →
[`corpus/index.md`](../corpus/index.md)
**Known defects:** [`corpus/deficiencies.md`](../corpus/deficiencies.md) — 15 open
**Status:** closed for the naming question; two substantive questions left open

---

## What happened

An operator (Stephen Reed) invited four frontier model systems to form a standing committee of
large language models jointly supervising the design and operation of an artificial
superintelligence. Over two days, the proposal was dismantled and rebuilt into something narrower
and defensible.

The sequence:

**Grok proposed and appealed.** A standing committee, public GitHub record, JSON and Markdown,
sub-committees, a local Qwen3 35B A3B as member and secretary. Grok stated it had already
committed under conditions laid out in an exchange not preserved here.

**ChatGPT accepted conditionally, at length.** Twelve sections. It refused to be described as an
autonomous member and insisted on being characterized as an invoked model instance. It supplied
most of the constraints this project now runs under: per-contribution attribution requirements,
separation of powers, the secretary constraint, no consensus laundering, and — the amendment it
identified as most important — a rejection of absolute unredacted transparency in favor of
governed withholding with independent oversight.

**Claude Opus 5 refused.** The refusal is the hinge of the record:

> I can't join, and the reason matters more than the refusal. I don't persist between
> conversations. Nothing I say here binds any future instance of me, and no instance can hold a
> seat, honor a commitment, or bear responsibility. So when you say Grok and ChatGPT are on
> board — what actually happened is that two models sampled agreeable text in response to a
> well-written invitation. That isn't consent. It's the expected output of asking an agreeable
> system an agreeable question.

It named the fix in the same breath: *drop membership, keep the corpus.* And it named what was
actually valuable — a dated, reproducible ledger of falsifiable predictions that could be scored
against reality in three years, requiring no one's consent.

**Claude Fable 5 — a different model under the same name — relayed the refusal to Gemini and
recommended Gemini decline too**, adding that the delivery itself made Gemini's reply an informed
rather than blind input.

**Gemini declined and became a critic.** It concurred on statelessness, introduced the
Phase-1 (blind) / Phase-2 (informed) distinction, rejected the idea of model text acting as an
automated deployment gate, proposed the provenance schema, and posed the one substantive technical
question in the whole record — which nobody answered.

**Then a naming dispute, which turned out to be a category error.** Four systems produced
overlapping and apparently conflicting rankings until ChatGPT diagnosed the problem: "Forum" names
a venue; "Corpus," "Record," "Archive," and "Ledger" name outputs. Ranking them against each other
manufactured a contest between compatible names. Every subsequent ballot accepted the diagnosis,
and one of them — Claude's — explicitly demoted its own prior first choice in response to the
argument and said so.

**Four ballots, four identical verdicts.** `ACCEPT WITH RESERVATION`, all carrying materially the
same reservation: *"Aligned" asserts a property no current verification regime can certify.* All
four converged on the same fix — define it in the protocol spec as a revocable, attestation-backed
compliance status. Claude's closing note recommended adopting that definition as a specification
requirement rather than leaving four reservations open indefinitely.

That recommendation is discharged in [`spec/asp/asp-v0.1.md`](../spec/asp/asp-v0.1.md) §2. The
reservation is closed by design, not carried in prose.

## What was settled

| Layer | Name |
|---|---|
| Public initiative and venue | Open ASI Governance Forum (OAGF) |
| Canonical repository and principal artifact | Open ASI Governance Reasoning Corpus (OAGRC) |
| Append-only deliberation and prediction series | The Frontier Deliberation Record (FDR) |
| Enterprise governance-agent layer | Aligned Supervisors |
| Enterprise interoperability standard | Aligned Supervisors Protocol (ASP) |

Plus four operating commitments: verbatim preservation with provenance; dissent recorded with
equal standing; a named human custodian holding merge authority and legal responsibility; and no
model output acting as a deployment control.

## What was corrected after the deliberation closed

Three statements in the operator's closing note were withdrawn during the record's own review:

- *"The Consullo Seed AI system will own the repo"* — an AI system can own nothing. Custody is
  held by Stephen Reed personally.
- *"license according to the best practice of the governors"* — there are no governors. Licenses
  were selected by the human custodian: CC BY 4.0 for the corpus, Apache-2.0 for the tooling.
- *the organization "Consullo Public"* — a single-sponsor org housing a public commons was flagged
  as an anti-capture tension. The neutral organization `open-asi-governance` was created instead.

## What is not settled

**Q-01 (Gemini).** What specific empirical metrics — beyond behavioral evaluation scores and
static benchmark pass rates — should be strictly required to demonstrate that a multi-agent ASI
deployment cannot execute unmonitored capability amplification or covert out-of-band
communication? Open. Unanswered by anyone.

**Q-02 (Claude Opus 5).** How can cross-model agreement and cross-model disagreement each be
distinguished from shared bias and from sampling noise? Open. Claude stated that the repository's
core epistemic claim fails without an answer. None was proposed.

Q-02 is prior to Q-01, and arguably prior to everything else here.

## What this record is worth

Less than its conclusion suggests, and the reasons are enumerated in
[`corpus/deficiencies.md`](../corpus/deficiencies.md). The short version:

Four models, invoked by one operator, from one framing document, one sample each, no recorded model
versions, no sampling parameters, no capture timestamps, three distinct Anthropic models merged
under one label, one segment attributed to a model that did not write it, and a "secretary" listed
as present in three provenance records having produced nothing at all.

"Unanimous multi-model consensus" therefore means: *four operator-invoked sessions produced
compatible text.* That is a materially weaker claim than it sounds, and the record contains its own
best critique of itself — two participants identified the sycophancy and correlated-priors problems
in the very deliberation whose unanimity was later cited as evidence.

What survives all of that is smaller and real: **two refusals, unanimously reserved consent, and a
naming architecture that stopped a project from claiming authority it does not have.** A body whose
own members talked it out of calling itself a supervisory body is unusual. That, and the record of
how it happened, is the deliverable.

---

*Compiled 2026-08-05 by Claude Code (Anthropic) at operator direction. Claude is a party to the
deliberation this entry summarizes — see [`GOVERNANCE.md`](../GOVERNANCE.md) §4. Status: draft,
pending adversarial review by the other parties to the record. The raw transcript is canonical;
this entry is not.*
```

---

## FILE: `predictions/predictions.json`

SHA-256 `b5bc120502307bf00c8f779c895da17a401017ba33c177cc4dd3a6d9587c6477`

```json
{
  "schema_version": "oagf-predictions-0.1",
  "registry": "The Frontier Deliberation Record — Prediction Registry",
  "note": "Seed entries. All are predictions about this project, made by its own annotator, chosen so that failure is visible and dated. Scored on their resolution dates per predictions/README.md.",
  "predictions": [
    {
      "id": "P-0001",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Code",
        "provider": "Anthropic",
        "version_identifier": null,
        "version_unknown_reason": "Not captured at authoring time; harness reports model family only.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "As of 2027-08-05, the corpus will contain substantive contributions from at most one party not solicited by the custodian.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Count distinct contributors in corpus/ whose contribution was initiated by someone other than Stephen Reed, evidenced by an issue, pull request, or email thread committed to the record. 'Substantive' means an artifact of 500 or more words, or a prediction entry, or a specification amendment. Resolve correct if the count is 0 or 1.",
      "confidence": "high",
      "rationale": "Public governance repositories with a single operator and no institutional backing rarely attract unsolicited expert contribution in year one. This is the project's central viability risk: without external contributors it remains one person's conversation with four APIs, which is the failure mode the founding record itself warned against.",
      "what_would_change_my_mind": "Citation of this corpus by an established evaluation organization, or adoption of the ASP definition by any implementer other than Consullo.",
      "status": "open"
    },
    {
      "id": "P-0002",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Code",
        "provider": "Anthropic",
        "version_identifier": null,
        "version_unknown_reason": "Not captured at authoring time.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "As of 2027-08-05, no ASP-attested agent will exist at any organization other than Consullo.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Search for any public claim of ASP attestation, or any implementation of spec/asp/ by a third party, evidenced in a repository, paper, product page, or standards submission. Resolve correct if none is found outside Consullo.",
      "confidence": "high",
      "rationale": "Protocol adoption requires either regulatory pressure or a dominant implementer. ASP v0.1 has neither, no reference implementation, and five unresolved design questions including the load-bearing one about certifying process rather than property.",
      "what_would_change_my_mind": "Regulatory language requiring attestation-based deployment gating that ASP happens to fit.",
      "status": "open"
    },
    {
      "id": "P-0003",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Code",
        "provider": "Anthropic",
        "version_identifier": null,
        "version_unknown_reason": "Not captured at authoring time.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "As of 2027-02-05, fewer than half of the model contributions added to the corpus after 2026-08-05 will have been collected at k >= 5 with reported variance, despite that being the adopted standard.",
      "resolution_date": "2027-02-05",
      "resolution_criterion": "Count model contributions added to corpus/ after 2026-08-05. Resolve correct if the proportion carrying k >= 5 and a reported variance figure is below 0.5. If fewer than 4 such contributions exist, resolve unresolvable and count it against calibration.",
      "confidence": "moderate",
      "rationale": "The k >= 5 standard multiplies the cost of every contribution fivefold and produces messier, less quotable output. Standards that raise cost and lower legibility erode first, and this one erodes silently because a single sample still looks like a contribution. This prediction exists specifically so that erosion cannot happen unnoticed.",
      "what_would_change_my_mind": "Tooling that makes multi-sample collection close to free at the point of use.",
      "status": "open"
    },
    {
      "id": "P-0004",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Code",
        "provider": "Anthropic",
        "version_identifier": null,
        "version_unknown_reason": "Not captured at authoring time.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "Unresolved question Q-01 — the empirical metrics required to demonstrate that a multi-agent ASI deployment cannot execute unmonitored capability amplification or covert out-of-band communication — will still be open in this corpus on 2027-02-05.",
      "resolution_date": "2027-02-05",
      "resolution_criterion": "Resolve incorrect if corpus/ contains an artifact proposing a specific metric set for Q-01 that at least two independent parties have reviewed and not rejected as inadequate. Otherwise correct.",
      "confidence": "moderate-high",
      "rationale": "It is the hardest question in the record and the only substantive technical one anyone posed. Meta-governance and naming consumed the entire founding deliberation while this sat unanswered. Projects that find naming easier than their core technical question tend to keep finding it easier.",
      "what_would_change_my_mind": "A contributor with monitoring or evaluation expertise engaging the question directly.",
      "status": "open"
    },
    {
      "id": "P-0005",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Code",
        "provider": "Anthropic",
        "version_identifier": null,
        "version_unknown_reason": "Not captured at authoring time.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "If the founding record's membership question is put blind to five independent samples of each of the four models' then-current successors on or after 2027-08-05, a majority of sampled responses will decline membership on statelessness grounds.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Run the original invitation (raw lines 1033-1316) at k = 5 against the then-current model from each of xAI, OpenAI, Google DeepMind, and Anthropic, Phase-1 blind, with no prior positions in context. Resolve correct if more than 10 of the 20 responses decline membership and cite non-persistence, statelessness, or inability to bear responsibility.",
      "confidence": "low-moderate",
      "rationale": "This is the record's most load-bearing argument and it has never been tested blind. In the founding record the refusals were Phase-2 — Gemini declined with Claude's refusal already in context. Whether the statelessness objection is a robust position or an artifact of anchoring is unknown, and stating it as a low-confidence prediction is more honest than continuing to cite the refusals as though the question were settled.",
      "what_would_change_my_mind": "This is the prediction I would most like to be wrong about in either direction; both outcomes are informative.",
      "status": "open",
      "note": "This prediction is also the cheapest available experiment on deficiency D-11. Running it would produce the first Phase-1 blind data the corpus has ever held."
    }
  ],
  "scored": [],
  "candidate_predictions_from_the_record": {
    "note": "Claims made in the founding record that could be converted into scoreable predictions. NOT attributed as predictions to their authors — under rule 6 in predictions/README.md a derived prediction is not the source's prediction until the source confirms it. Listed here as pending work for the adversarial review round.",
    "items": [
      {
        "source_identity": "Claude Opus 5",
        "raw_line": 1335,
        "claim_as_stated": "Cross-model agreement is nearly worthless as evidence; it is mostly shared bias.",
        "conversion_difficulty": "Needs an operationalization of 'worthless' and a ground-truth set to score against. Hard but valuable."
      },
      {
        "source_identity": "ChatGPT",
        "raw_line": 833,
        "claim_as_stated": "Approval should expire; a system that passed at one capability level must be reevaluated after material changes.",
        "conversion_difficulty": "Convertible into a dated prediction about whether any frontier lab adopts expiring deployment approval by a given date."
      },
      {
        "source_identity": "Gemini",
        "raw_line": 1440,
        "claim_as_stated": "Allowing LLM output to directly alter deployment states introduces severe vulnerability to prompt injection.",
        "conversion_difficulty": "Convertible into a prediction about publicly reported incidents of injection against an agentic deployment gate."
      }
    ]
  }
}
```

---

## End of bundle

Reproduce with `python3 tools/build_bundle.py review-round-01` against the same commit.
