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
