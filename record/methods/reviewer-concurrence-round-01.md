# Reviewer concurrence, review round 01 — how much did the panel add?

Run 2026-08-06 against data already in the corpus. No new model calls were made; the four responses
were captured on 2026-08-05 and are hash-anchored under `corpus/raw/review-round-01/`.

Coding: `corpus/artifacts/review-round-01/finding-coding.json`
Tool: `tools/analyze_concurrence.py` (deterministic; re-runnable)

---

## Why this was run

External literature — *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation
Panels* (arXiv:2605.29800) — reports that a 9-judge panel across 7 model families carries about **2
independent votes' worth of information**, that the best single judge matches or beats the panel in
every condition tested, and that better aggregation does not recover the loss. If that result
transferred here, this corpus's four-reviewer rounds would be worth far less than they appear.

The corpus had already anticipated the question. D-11 carries the formula
`n_eff ≈ n / (1 + (n−1)ρ)` with the worked case ρ = 0.7 → n_eff ≈ 1.3 for four models, contributed by
Claude Fable 5, alongside ChatGPT's requirement to build an **error-correlation matrix rather than an
answer-agreement matrix**. Both said the same thing: **until ρ is measured, n_eff is unknown.**

This analysis does not measure ρ. It measures something weaker that the available data can support.

## What this is and is not

**It is** an agreement-on-findings analysis: which of 20 distinct findings each reviewer raised.

**It is not** an error-correlation analysis, and therefore **does not yield n_eff**. Computing ρ
requires knowing which findings were *correct*, and the only adjudication available is by the same
interested annotator whose work was under review. ChatGPT flagged exactly this trap in round 01:
models that agree when correct are corroborating; models that make the same *errors* share a bias
channel — and only the second is measurable as ρ.

**Coder conflict.** The coding was performed by Claude Code, which is both the annotator under review
and same-provider with one reviewer. Deciding whether two reviewers "raised the same finding" is
interpretive. An independent recoding would be a material improvement; that is registered, not
waved away.

## Results

```
Findings: 20 distinct

                  raised   sole-raiser   engaged
  grok                 3             0        10
  chatgpt             16             6        16
  gemini               4             0         9
  claude-fable-5      12             3        12

  raised by 1:  9 findings (45%)
  raised by 2:  7
  raised by 3:  4
  raised by 4:  0        <-- no finding was raised by all four

  Pairwise Jaccard on raised findings: 0.00 – 0.40 (mean ≈ 0.19)

  Explicit splits: 9/20 findings drew an opposing position from at least one reviewer.

  Leave-one-out losses:  grok 0 · chatgpt 6 · gemini 0 · claude-fable-5 3
  Best single reviewer (chatgpt) raised 16/20 = 80%.
```

## Reading

**The Nine Judges result does not transfer to this round, and the reason is instructive.** That
paper's panels were highly redundant: judges made the same mistakes on the same items. These
reviewers were the opposite of redundant. **No finding was raised by all four.** Pairwise overlap
averaged about 0.19, and Grok and Gemini shared *zero* raised findings with each other. Nearly half
of all findings came from exactly one reviewer.

**The disagreement is the strongest evidence of independence.** Nine of twenty findings drew an
explicit split, and the splits are not noise:

- **F-02 (the D-09 identity merge) produced four different positions from four reviewers.** Grok:
  understated. ChatGPT: *overstated* — "described too categorically," because the record cannot
  authenticate three distinct base models. Gemini: accurate as written. Claude Fable 5: a missing
  *instance* — the register caught others merging Claude identities and missed Claude merging its
  own. Four models, one item, four positions. Correlated judges do not do this.
- **F-01 (ASP §2.4)**: three reviewers independently found that §2.4 misstates Grok's ballot;
  Gemini said §2.4 was fair *and* asserted §2.4 recorded Gemini as advocating rename — which,
  per ChatGPT, it does not. Three of four caught it; one misread the document about its own position.
- **F-12 (FDR framing)**: three objected that the narrative privileges the annotator's lineage;
  Grok explicitly held that it does not.

**But the panel was badly unbalanced, and that is the real finding.** ChatGPT alone raised 80% of
everything found. Grok and Gemini were **sole-raiser of nothing** — dropping either would have cost
the round zero findings. On raised-findings alone the effectively contributing panel was about
**two**, which coincidentally matches the Nine Judges headline for an entirely different reason:
not correlated error, but asymmetric depth of engagement.

**That undercounts Grok and Gemini, and the leave-one-out metric is the wrong instrument for them.**
Their contribution was largely *oppositional*: Grok took a position on 10 findings and opposed 6 of
them; Gemini engaged 9 and opposed 4. Those dissents are what made F-03, F-12, F-14, F-18, F-19 and
F-20 **contested rather than nodded through**. A panel in which nobody dissents supplies no evidence
that the majority was checked. Counting only what a reviewer *originates* treats disagreement as
silence, which is exactly the error a deliberation record should not make.

## Consequences for the corpus

1. **D-11's discount remains correct, and its stated reason should be widened.** The warning was
   framed around correlated priors producing spurious agreement. In this round the observed problem
   was not excess agreement — it was **effort asymmetry**. One reviewer did most of the work.
2. **"Four reviewers" overstates the panel in a way "n_eff unknown" does not capture.** Two of the
   four originated nothing. This should be stated where round-01 is cited.
3. **ρ is still unmeasured and this does not measure it.** The route to ρ runs through the
   prediction registry, as Claude Fable 5 argued: score models on questions that later resolve, then
   estimate the pairwise error-correlation matrix from outcomes. That remains the open work.
4. **Solicit dissent explicitly.** The most valuable thing Grok and Gemini did was disagree, and
   nothing in the round-01 prompt asked them to. A future prompt should require each reviewer to
   name at least one finding by another reviewer it believes is *wrong*.

## Reproduction

```bash
python3 tools/analyze_concurrence.py corpus/artifacts/review-round-01/finding-coding.json
```

Round 02 has not been coded. Doing so would show whether the ChatGPT-dominance pattern is stable or
an artifact of one round.
