# Method — Locating divergence between parties

**Status:** draft, in use as of 2026-08-05. First applied in `local-round-01`.
**Author:** Claude Code (Anthropic), a party to the record this method is applied to.
**Bears on:** Q-02, D-07, D-08, D-11, and prediction P-0003.

---

## 1. The problem this exists to solve

The corpus holds essays. Four parties wrote long prose responses, and a reader is left to judge by
impression whether they agree, whether the agreement means anything, and where exactly they part
company. Three failures follow, and this corpus has committed all three:

1. **Agreement counted without being earned.** In review round 02 three parties converged on "the
   ladder does not constrain activity." One of them reached that conclusion while misdescribing the
   document it was judging. Counting it as a third vote would have been consensus laundering.
2. **A single draw mistaken for a position.** Every frontier contribution here is k = 1. Same
   prompt, different sampling, different answer — so a lone response is a sample, not a stance, and
   nothing in the record distinguishes a firmly held view from a coin flip.
3. **Divergence located at the wrong grain.** Two essays that "disagree" may agree on every
   substantive claim and differ in emphasis, or agree in tone while differing on the one claim that
   matters. Prose comparison cannot tell these apart.

**Goal: locate divergence at the level of a specific claim, and distinguish real divergence from
sampling noise and from framing effects.**

## 2. The algorithm

### Step 1 — Categorical reduction

Reduce the open question to a small set of mutually exclusive labels, plus free-text fields for
reasoning that are recorded but not used for the measurement.

**Label choice is part of the method, not presentation.** Labels must avoid the vocabulary any
prior respondent used. In `local-round-01` the frontier reviewers had called the ladder
"decorative"; the enum offered `binds_the_implementer_s_activity`,
`binds_only_what_may_be_claimed`, and `does_not_bind`. Reusing "decorative" would have measured
lexical echo rather than position.

### Step 2 — Positions are distributions, never draws

Sample k times (k = 20 in practice) at **temperature > 0** with distinct seeds. Temperature 0 makes
every sample identical and variance unmeasurable by construction — a deterministic answer is a
legitimate artifact but carries no information about stability.

For each measured field compute: the class-frequency distribution, the modal value and its
fraction, the number of distinct values, and **Shannon entropy in bits**. Entropy is the summary
statistic: 0 bits is unanimity, 1.0 bits is a maximally undecided two-way split.

Variance is **computed from the samples collected**, never asserted. This answers the objection
that "reported variance figure" is undefined for open-ended text: for a categorical field it is
exactly defined.

### Step 3 — Grammar-constrained decoding

Emit through `response_format: json_schema`. This does three jobs at once:

- **Structurally suppresses reasoning output.** The served model reasons by default; a plain-text
  request spent its entire budget on chain-of-thought and emitted no answer. A grammar constraint
  makes thinking tokens unemittable — enforcement rather than instruction.
- **Makes variance computable**, because the output space is the enum.
- **Removes parsing** as a source of error.

### Step 4 — Paired phase arms

Run the same question twice, identical in every respect except one:

- **Phase-1 (blind):** source material + question. No peer positions.
- **Phase-2 (informed):** identical prompt plus the other parties' verdicts.

Same k, same seed base, same temperature, same model, same schema, same question text. **The
pairing is the measurement**: any distributional difference is attributable to the supplied
positions, because nothing else varied.

### Step 5 — Pre-register before the second arm

File a prediction naming the expected modal value and entropy change **before** running Phase-2,
with a resolution criterion fixed in advance. A result reported afterward can be framed; a
prediction filed beforehand cannot. Partial satisfaction resolves incorrect.

### Step 6 — Decompose into three quantities

This is where divergence is actually located:

| Quantity | How measured | What it means |
|---|---|---|
| **Within-party dispersion** | entropy at fixed phase and party | sampling noise — how much of the answer is the die, not the model |
| **Between-party divergence** | distance between two parties' distributions on the same field | candidate real disagreement |
| **Phase susceptibility** | Phase-1 → Phase-2 shift within one party | how much the position is induced by exposure to others |

**A divergence is real only when between-party divergence exceeds within-party dispersion.** Two
parties whose distributions differ by less than either one's own entropy have not been shown to
disagree — the apparent difference is within the noise each generates alone.

### Step 7 — Verify grounding for document claims

Where the object of judgement is a document the corpus holds, check the stated reasoning against
that document. Agreement whose reasoning misdescribes the object is not evidence about the object,
regardless of whether the conclusion happens to be right.

This is cheap, requires no sampling or external ground truth, and it is how the round-02 finding was
caught. It generalises only to claims about artifacts in the corpus — not to claims about the world.

## 3. What it produced on first application

`local-round-01`, question: does the ICP promotion ladder constrain an implementer's activity?

| | Phase-1 blind | Phase-2 informed |
|---|---|---|
| modal | `binds_only_what_may_be_claimed` (55%) | `does_not_bind` (75%) |
| entropy | **0.9928 bits** | 0.8113 bits |
| `binds_the_implementer_s_activity` | **0 / 20** | 0 / 20 |
| Level-2 sub-question entropy | 0.469 bits | **0.7219 bits** |

Three results, in descending order of how much they matter:

1. **Zero of forty samples, across both arms, said the ladder binds activity.** The frontier verdict
   survives a divergent-lineage probe at the level that matters. That is corroboration the corpus
   can actually defend.
2. **0.9928 bits in the blind arm.** The position is a near-coin-flip between two ways of saying
   "weak." At k = 1 this would have been recorded as a confident verdict. Every frontier verdict on
   this question is k = 1.
3. **Supplying peer positions flipped the modal answer and pulled toward the most extreme supplied
   verdict**, not the most common one — while entropy on a *checkable factual* sub-question **rose**.
   Peer context made a factual judgement less stable. Nothing predicted that, and P-0008 was scored
   incorrect on both conjuncts.

## 4. Benefits

- **The k ≥ 5 standard stops eroding.** Twenty samples take 17 seconds. P-0003 forecasts the
  standard decaying under cost; this removes the cost for one participant.
- **Complete provenance.** Model path, quantisation, serve flags, temperature, per-sample seed,
  schema, and machine-captured timestamps — D-01 through D-04 are unremediable for chat-surface
  models and fully satisfiable here.
- **Divergent-lineage probing.** A conclusion four frontier models share that collapses on an
  open-weight model from a different lab and post-training regime is evidence of shared prior
  rather than signal.
- **Anchoring becomes a number** instead of a worry, and the number was not what anyone guessed.
- **Falsifiable by construction**, because the pre-registration precedes the second arm.

## 5. Limits, stated plainly

- **One model, one lineage.** Nothing here generalises to the frontier models. It measures Qwen.
- **Categorical reduction forces a choice** the party might not volunteer, and the label set
  constrains what can be expressed. A party whose real view is "the question is malformed" has
  nowhere to put it.
- **Entropy over two or three categories is coarse.** 0.99 bits and 0.81 bits are meaningfully
  different; 0.99 and 0.97 are not.
- **The Phase-2 arm supplied paraphrased verdicts**, not verbatim ones, and attributed them to
  anonymised systems. Paraphrase is itself a framing choice made by the annotator.
- **Grammar constraints are not portable.** TRT-LLM guided decoding and llama.cpp grammars do not
  share a JSON Schema subset or failure behaviour. This method is currently bound to one backend.
- **It addresses agreement about documents, not about the world.** The corpus's harder claims —
  what evidence should gate a deployment — have no checkable object.
- **The author is a party** to the record being measured, chose the labels, wrote the question, and
  could have reworded until a preferred distribution appeared. Only the committed pre-registration
  and the preserved samples of every arm constrain that, and they constrain it imperfectly. This is
  an operator-designed, model-executed measurement, and does not qualify as independent evaluation.

## 6. What would strengthen it

Run the identical paired arms against a second divergent-lineage model. Run the frontier models at
k ≥ 5 on the same enum so between-party divergence can be computed rather than eyeballed against
k = 1 essays. Have an outside party choose the labels.

---

*Method and both arms committed at `corpus/raw/local-round-01/` with all forty samples preserved,
including the arm that falsified the pre-registered prediction.*
