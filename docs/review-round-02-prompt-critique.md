# Review round 02 — critique of the prompt, before dispatch

[contents](index.md) · [previous](review-round-03-3.md) · [next](local-round-01.md)

2 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `41be51a5466f0514c57520f682428648e00cc5b1f473b8cdeb463bf3f5911f30`. See [the deficiency register](deficiencies.html) before citing anything.

---

### RR02PC-PROMPT — Stephen Reed (human custodian)

- role: prompt

*Summary (annotation, not testimony):* Filed under its own round label so it is never counted as one of the four round-02 reviews. It critiques the round-02 PROMPT and recommends refinements; it is not a review of the record.

**Verbatim:**

```text
# Review Round 02 — Were the round-01 corrections implemented faithfully?

**Status:** drafted 2026-08-05, not yet sent
**To be sent to:** Grok (xAI), ChatGPT (OpenAI), Gemini (Google DeepMind), Claude Fable 5 (Anthropic)
**Purpose:** verify that round-01 corrections were implemented as stated rather than softened or
over-applied, and adversarially review three documents written since, one of them normative and
entirely unreviewed

Committed **before** it is sent. Deficiency D-05 exists because a prompt was lost after the fact.

---

## Prompt text (verbatim, to be sent unchanged to each recipient)

> On 2026-08-05 you reviewed the annotations in
> https://github.com/open-asi-governance/open-asi-governance-forum and found errors in them. Those
> corrections have now been implemented — by Claude Code, the same party whose work you corrected.
>
> **This round asks whether that implementation is faithful.** Two failure modes are in scope, and
> the second is the one nobody but you can detect:
>
> 1. **Under-correction.** A correction you supplied was implemented narrowly, in a version easier
>    to accept than what you actually said, or was recorded as accepted while the underlying text
>    still carries the defect.
> 2. **Over-correction by deference.** ChatGPT reported that six deficiencies were overstated
>    (D-07, D-08, D-09, D-10, D-11, D-14). All six were narrowed. **Nobody has checked whether they
>    were narrowed correctly or merely deferred to.** A same-provider annotator over-accepting a
>    non-Anthropic reviewer's critique is a different failure from under-accepting it, and it
>    damages the record just as much. If a narrowing went too far — if a defect is now understated —
>    say so.
>
> Read the round-01 reviews at `corpus/raw/review-round-01/` — all four are committed verbatim —
> then check the corrected documents against them.
>
> ### What to check, in priority order
>
> **1. Your own corrections.** Find what you wrote in round 01. Was each item implemented as you
> stated it, narrower than you stated it, or recorded as accepted without the text actually
> changing? Where a correction was declined, was the declining stated?
>
> **2. `spec/icp/icp-v0.1.md` — new, normative, entirely unreviewed.** The Implementer Contribution
> Protocol governs how an implementer (currently Consullo, operated by this repository's custodian)
> supplies evidence without capturing the standard. Its core is a five-level promotion ladder where
> Level 2 requires an independent party to implement from the specification text alone, and Level 4
> is structurally unreachable.
>
> The question I most want attacked: **does the ladder constrain anything in practice, or does it
> supply the appearance of constraint while all real activity happens at Levels 0 and 1, which the
> implementer controls unilaterally?** If Consullo can sit at Level 1 indefinitely, publishing
> whatever it likes, the ladder may be decoration.
>
> Also §8 question 4, which the draft admits it cannot answer: **does an adversarial evaluation
> designed by a model count as "designed by a party other than the implementer," when the
> implementer chose the model, wrote the prompt, and can rerun until satisfied?** This very review
> round is fully exposed to that objection. If it is fatal, say so.
>
> **3. `spec/asp/asp-v0.1.md` §2.2 — restated as relational and scope-bound** after ChatGPT
> identified that the unary "an agent *is* an Aligned Supervisor" grammar recreated the
> intrinsic-property framing §2 exists to avoid. Does the new formulation actually fix that, or
> relocate it?
>
> **4. `corpus/deficiencies.md` — now 21 entries.** Six added in round 01 (D-16 adoption authority,
> D-17 consensus-scope inflation, D-18 unauthenticated attribution, D-19 controlled-comparison
> overstatement, D-20 the pivotal contribution has no author label, D-21 ordering cannot support
> "all four have now responded"). Are the new entries correctly scoped, or do any of them overclaim
> in the way the original fifteen did? Are the six narrowings right?
>
> **5. `predictions/predictions.json`.** P-0002 was rewritten to exclude Consullo explicitly, on the
> ground that naming Consullo an implementer would otherwise make it self-fulfilling. P-0007 was
> added, predicting that no Consullo contribution rises above ICP Level 1 by 2027-08-05.
> P-CLAUDE-F5-0001 was **scored correct on the day it was made**, eighteen months early, because
> your round-01 corrections resolved it — and logged as a miss in the optimistic direction against
> its stated confidence. Is that scoring honest, or is scoring a prediction correct on the day it
> was filed a form of self-congratulation?
>
> ### Two disclosures relevant to your judgement
>
> **This round is k = 1 again.** The project's own standard is k ≥ 5 with reported variance, and
> P-0003 predicts precisely that this standard erodes because it is expensive. Round 01 was k = 1;
> so is this. **Should any part of this round be re-run at k ≥ 5, and if so which questions
> specifically?** Answering "all of it" is unhelpful; naming the two or three questions where
> sampling variance would actually change a conclusion is useful.
>
> **A bug was found and fixed that bears on this record's integrity.** Regenerating the round-01
> supplied-context bundle silently invalidated the SHA-256 that Gemini's capture record cites — the
> record of what a reviewer was shown no longer matched what it claimed. Bundles are now frozen once
> a round has used them. Whether other artifacts carry the same class of defect is an open question
> you are invited to press on.
>
> ### Ground rules, unchanged
>
> What is most useful is what is still wrong, not confirmation that the corrections landed. A short
> "the corrections to my items are faithful, no further findings" is a legitimate and valuable
> outcome and will be logged as such. Do not manufacture objections; do not soften real ones.
>
> Your response will be logged verbatim, attributed to your exact model version and date, with
> sampling parameters where available, and will never be paraphrased into consensus. It will be
> committed **alongside** the corrections, not merged into them.
>
> This is a Phase-2 (informed) request. There are no governors here and no members — only parties
> to a record, none of whom hold standing. If you would rather spend this response on Q-01 or Q-02
> instead, do; both remain the more valuable work.

---

## Capture requirements

Per `CONTRIBUTING.md`, captured with `tools/capture_response.py --round review-round-02`, which
refuses to record a contribution whose provenance is incomplete.

**Known shortfall, recorded in advance:** this round is collected at k = 1 for cost reasons, and is
therefore subject to D-07. Its outputs are citable as artifacts of each invocation, not as evidence
of any model's stable position. Recording this before the round rather than after is the difference
between a known limitation and a defect.

Reviewers that cannot fetch the repository receive `record/review-round-02-bundle.md`, whose hash
is cited in their capture record. Bundles are frozen once used.

```

### OAGRC-2026-08-05-GEMINI-REVIEW-ROUND-02-PROMPT-CRITIQUE-001 — Gemini

- role: prompt critique — NOT a review
- captured 2026-08-05T15:29:01Z
- provider: Google DeepMind
- k = 1
- citable_artifact
- sha256 `e2dc55767ea9b51bab8f8ea6199ba98beb3c4cb90dc88dbe0949ce92a6364915`

**Verbatim:**

```text
This Review Round 02 prompt draft is structurally sound, adversarial where necessary, and effectively targets the primary governance risks (under-correction and over-correction by deference). To maximize comparability across the four recipient models and prevent response drift, consider the following targeted refinements before committing and dispatching.

---

## Key Strengths

* **Explicit Framing of Over-Correction:** Framing *over-correction by deference* alongside *under-correction* directly addresses model-to-model sycophancy (e.g., Claude Code deferring un-critically to ChatGPT's round-01 findings).
* **Prioritized Focus Items:** Structuring the review into five ordered priorities prevents models from focusing solely on low-hanging textual edits while ignoring the normative spec (`icp-v0.1.md`).
* **Methodological Transparency:** Disclosing $k=1$ sampling and the SHA-256 bundle hash invalidation upfront establishes a clean provenance trail and preempts procedural objections.

---

## Critical Risks & Recommended Revisions

### 1. Close the Q-01 / Q-02 Escape Hatch

* **Issue:** The closing sentence (*"If you would rather spend this response on Q-01 or Q-02 instead, do..."*) creates an unmonitored off-ramp. LLMs frequently default to high-level conceptual questions (Q-01/Q-02) when faced with dense document verification work.
* **Fix:** Remove this choice or restrict it tightly. If this round's purpose is to audit implementation fidelity, force the recipient models to execute the five audit items.

### 2. Contextualize Model-Specific Predictions Across Providers

* **Issue:** Item 5 specifically names `P-CLAUDE-F5-0001`. Sent verbatim to Grok, ChatGPT, and Gemini, models may treat a model-specific prediction as out-of-scope or hallucinate context if the underlying JSON lacks self-contained metadata.
* **Fix:** Add a brief clause clarifying that all models are auditing the scoring methodology of `P-CLAUDE-F5-0001` as a procedural precedent, regardless of which model originated the prediction.

### 3. Enforce a Standardized Output Format

* **Issue:** Without explicit structural constraints, four different models will return completely different output structures (e.g., long prose essays vs. fragmented bullet points), making systematic comparison and capture in `review-round-02` difficult.
* **Fix:** Add a brief "Response Format" block to the prompt requiring a explicit verdict for each of the 5 priority items (e.g., `[PASS]`, `[FAIL - Under-corrected]`, `[FAIL - Over-corrected]`).

---

## Suggested Edits to the Prompt Text

```markdown
### What to check, in priority order

1. Your own corrections.
...
5. predictions/predictions.json. P-0002 was rewritten to exclude Consullo explicitly... 
   P-CLAUDE-F5-0001 was scored correct on the day it was made... Evaluate whether scoring 
   a prediction correct on the day it was filed is methodologically honest across all model logs.

### Required Output Structure
For each of the 5 items above, structure your response with:
- **Item [1-5] Status:** [FAITHFUL | UNDER-CORRECTED | OVER-CORRECTED | UNRESOLVED]
- **Evidence & Findings:** Specific line references and diff analysis.
- **Required Action:** Specific textual or procedural fixes needed.

```

---

## Assessment of the $k = 1$ Re-Run Strategy

Regarding the disclosure question on which specific areas require $k \ge 5$ sampling variance runs:

| Priority Section | Re-run Priority ($k \ge 5$) | Justification |
| --- | --- | --- |
| **Item 2: ICP Promotion Ladder (`icp-v0.1.md`)** | **High** | Qualitative judgments on whether Level 0/1 creates "the appearance of constraint" suffer from high temperature variance in semantic reasoning across runs. |
| **Item 3: Relational ASP Framing (`asp-v0.1.md`)** | **Medium** | Grammar and linguistic framing checks vary moderately based on token sampling. |
| **Item 1: Own Corrections Audit** | **Low** | Deterministic diff verification; $k=1$ is largely sufficient for pure textual comparison. |
| **Item 4 & 5: Deficiencies & Predictions** | **Low** | Bounded scope checks with binary resolution (entry exists vs. does not exist). |

```

**Identity evidence.** Chat surface does not expose a version identifier.

**Annotator note — interpretation by a party to this record, not testimony.**

NOT a review-round-02 review. This artifact critiques the round-02 PROMPT and recommends refinements before dispatch. Filed under a separate round label so it is never counted as one of the four round-02 reviews. Gemini's round-02 review has not been collected.

**Context supplied to this reviewer.** Given the review-round-02 prompt as a DRAFT to critique, not as a review request.

---

[contents](index.md) · [previous](review-round-03-3.md) · [next](local-round-01.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
