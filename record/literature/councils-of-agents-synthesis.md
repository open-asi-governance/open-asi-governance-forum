# Councils of agents — prior art, failure modes, and whether OAGF's structure is defensible

> **Provenance.** This synthesis was written in the Consullo working repository on 2026-08-06 and
> copied here. Paths of the form `third-party/…` and references to `_paper-processing-checklist.md`
> or `*-insights.md` belong to that repository's per-paper workflow and have no counterpart here;
> in this repo the PDFs sit alongside this file, indexed by `README.md`. Two of the thirteen papers
> are **not** redistributable and are link-only — see `README.md` for which and why.


Research pass opened 2026-08-06 for Task #4. **Adverse findings first**, by prior commitment: the
risk this task exists to address is that OAGF's deliberation structure is assumed sound rather than
shown sound, and the fastest way to find that out is to look for the literature that would refute it.

> **Evidence discipline / reading status.** This is a *first pass*. Read in full: nothing yet.
> Read abstract + introduction: `nine-judges`, `talk-isnt-always-cheap`, `not-all-flips`.
> Title + search-summary only: the remaining ten. Every quantitative claim below is attributed to a
> paper I have at least read the abstract of; claims sourced only from search summaries are marked
> **[unverified]** and must not be cited onward until the PDF is read. The 13 PDFs are in this
> directory and each still owes a `*-insights.md` per `_paper-processing-checklist.md`.

---

## 1. The finding that most directly threatens OAGF

**Kohli (Apple), "Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation
Panels", arXiv:2605.29800, 28 May 2026.** Read: abstract + introduction.

A panel of **9 frontier LLMs from 7 model families**, on three NLI datasets with 100 human
annotations per item, supplies about **2 independent votes' worth of information**. Roughly
three-quarters of nominal independence is lost to shared mistakes on shared items. Consequences as
stated by the authors:

- panel accuracy falls **8–22 percentage points short** of the independent-voting ideal;
- **the best single judge matches or outperforms the full panel across all conditions**
  (MNLI 71.8 vs 72.0 — within noise; SNLI 84.2 vs 77.7; AlphaNLI 91.2 vs 88.7);
- **neither more judges nor better aggregation helps** — established methods close at most 11% of
  the gap *even when given the correct answers*;
- robust across prompt variants, temperature, chain-of-thought, and a pairwise-preference task.

Measured with Kish effective sample size against a Condorcet null.

**Why this matters here.** OAGF's founding record was built by running review rounds across Grok,
ChatGPT, Gemini, and Claude — four models from four families — and treating convergence among them
as corroboration. This paper's result says that convergence among frontier LLMs is *mostly shared
error*, not independent confirmation.

> **Correction, 2026-08-06 — I had this wrong on first writing.** An earlier version of this section
> said "the corpus does not currently quantify this anywhere." **False.** `corpus/deficiencies.md`
> lines 231–236, under D-11, already carries the formula `n_eff ≈ n / (1 + (n−1)ρ)` with the worked
> case ρ = 0.7 → n_eff ≈ 1.3 for four models — contributed by **Claude Fable 5** in review round 01,
> answering Q-02 — alongside **ChatGPT's** independent requirement to construct an *error-correlation
> matrix rather than an answer-agreement matrix* and report an "effective independent-source count."
> Two of the four reviewers anticipated the Nine Judges framing, and the corpus adopted it.
>
> What the paper adds is therefore **not the framing but the measurement**. The corpus says "until ρ
> is measured, n_eff is unknown." The paper measures it, on a real 9-judge panel, and the answer is
> brutal. That is a *better* relationship between the two than the one I first claimed: the corpus
> posed the question correctly and left it open; the literature closed it.

The ICP separately states, in §4.4 and normatively, that operator-designed model-executed
evaluations are **not** independent — a *procedural* argument about who designed the eval. The
correlated-judges result is a second, *statistical* independence failure that survives even when the
procedural objection is fully addressed. Both are now named in the corpus; only the procedural one
is in the ICP.

**Measured on our own data, 2026-08-06.** `record/methods/reviewer-concurrence-round-01.md` in the
OAGF repo codes all four round-01 responses into 20 distinct findings and reports the overlap.
**The Nine Judges result does not transfer to this round.** No finding was raised by all four
reviewers; pairwise Jaccard averaged ≈ 0.19; 45% of findings came from exactly one reviewer; and 9
of 20 drew an explicit split — including one item on which four reviewers took four different
positions. These reviewers were not redundant.

The real weakness found was different and is not in the literature above: **effort asymmetry.**
ChatGPT alone raised 80% of all findings, and two of the four reviewers originated nothing at all.
Their value was almost entirely *oppositional* — the dissents that made six findings contested
rather than nodded through.

## 2. Deliberation can actively make things worse

**"Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate", arXiv:2509.05396.**
Read: abstract.

Debate "can sometimes be harmful rather than helpful": accuracy **decreases over time**, *even when
stronger models outnumber weaker ones*. Models "frequently shift from correct to incorrect answers in
response to peer reasoning, favoring agreement over challenging flawed reasoning." Contributing
factors examined include sycophancy and social conformity.

This is the sharpest available answer to "is more deliberation always better?" — no, and the
direction of the error is toward consensus, which is precisely the signal a deliberation record is
tempted to read as convergence on truth.

Related, **[unverified]**: a "tyranny of the majority" / echo-chamber effect, strict conformity
measured around 29% and predominantly harmful (57–77% correct-to-wrong); and unanimity being
compatible with being unanimously wrong.

## 3. A methodological hit on OAGF's own paired-phase probe

**"Not All Flips Are Conformity: Decomposing Stance Convergence in Multi-Agent LLM Debate",
arXiv:2606.00820.** Read: abstract + introduction.

The paper names **spontaneous instability**: models revise answers on mere re-examination, with no
new information. It decomposes observed answer changes into (1) spontaneous change that would have
happened anyway, (2) conformity triggered by peer *positions* alone, and (3) additional change from
peer *reasoning* — via three counterfactual arms per agent-question pair: self-reflection,
stance-only exposure, full reasoning exposure. Their stated finding is that spontaneous instability
is a **large** baseline source of change.

Their framing is blunt and applies directly to us: *"If we cannot separate this baseline drift from
genuine social influence, then every measurement of conformity in multi-agent debate carries an
unknown margin of error."*

**This is a defect in the corpus's `local-round-01` contribution, and it is mine.** That probe
compared Phase-1 (blind) entropy 0.9928 bits against Phase-2 (informed) 0.8113 bits over 40 samples
and attributed the narrowing to informedness. It has **no self-reflection control arm**. Under this
paper's decomposition, an unknown share of that 0.18-bit narrowing is spontaneous drift that would
have occurred on re-examination with no Phase-1 information at all. The measurement is not wrong,
but its *causal interpretation* is unsupported as recorded, and the corpus states it more confidently
than the design licenses.

**This should become a deficiency entry (D-22) and a correction to the round-01 method note**, not a
quiet edit — the corpus's whole claim to seriousness is that corrections are recorded alongside the
originals rather than replacing them.

## 4. Debate has a known adversarial failure mode with a formal fix

**Brown-Cohen, Irving, Piliouras, "Avoiding Obfuscation with Prover-Estimator Debate",
arXiv:2506.13609.** Read: title page only.

The **obfuscated arguments problem**: a dishonest debater decomposes an easy claim into
intractable subproblems, so an honest opponent cannot locate the flaw. **[unverified]** reports
describe obfuscation as emerging naturally in prior empirical work and as a likely attractor state,
with prover-estimator debate the most rigorous published countermeasure.

Relevance: OAGF's promotion ladder rewards a contributor for surviving adversarial review. If an
adversarial reviewer can win by obfuscation rather than by being right, the ladder measures
resistance-to-scrutiny rather than correctness — and Level 2 ("independent implementation from spec
text alone") is the only rung that structurally resists this, because it requires producing an
artifact rather than winning an exchange.

## 5. What survives — the case *for* councils, kept honest

- **Task-aware routing beats voting.** Already in this directory:
  `task-aware-llm-council-adaptive-decision-pathways-insights.md` (TALC, arXiv:2601.22662) reports
  ablations where task-aware routing beats random, round-robin, **voting**, and collaborative
  baselines. The useful primitive is *routing authority to the most competent member per step*, not
  *averaging the members*.
- **Heterogeneity is the lever, not headcount.** The through-line of §1–§2 is that panel value is
  bounded by effective independence. Anything that buys genuine diversity — a different model family,
  a different prompt frame, a *human*, a deterministic checker, an executable test — is worth more
  than another frontier LLM.
- **A non-LLM verifier is worth more than another judge.** This is the strongest practical
  implication, and it is the same conclusion the TRT-LLM campaign reached independently this week:
  the CPU-only regression test settles a question no amount of model agreement could.

## 6. Provisional verdict on OAGF's structure

**Defensible in shape, over-claimed in strength.** The venue/corpus/record separation, the
verbatim-preservation discipline, the deficiency register, and the prediction registry do not depend
on council independence at all — they are provenance machinery, and they stand.

What does not currently stand is any implicit claim that **agreement among four frontier models
constitutes corroboration**. On the evidence above it constitutes roughly one-to-two votes of
evidence, in a direction biased toward consensus.

Concrete changes this implies, in priority order:

1. **Record the correlation caveat as a first-class limitation of the founding record**, with the
   `nine-judges` numbers, rather than leaving it implicit in ICP §4.4.
2. **File D-22 and correct the round-01 causal claim** (§3). Preserve the original alongside.
3. **Add a self-reflection control arm** to any future paired-phase probe — the cheapest possible
   fix, one extra arm, and it converts an uninterpretable delta into an attributable one.
4. **Weight the ICP ladder toward Level 2** — artifact-producing contributions — because they are the
   rungs that survive both correlated judges and obfuscated arguments.
5. **Treat a deterministic checker as a council member with more weight than any model.**

## 7. Cheapest discriminating tests

| Question | Test | Cost |
|---|---|---|
| How correlated are *our* four reviewers? | Re-score the round-01 and round-02 responses for pairwise error agreement; compute Kish n_eff against the Condorcet null, exactly as `nine-judges` does | one afternoon, data already captured |
| Was the Phase-1→Phase-2 narrowing real influence? | Re-run the probe with a third arm: re-examination with no peer information | one extra arm on an existing harness |
| Does the panel beat its best member here? | Compare each reviewer's solo findings against the merged set on round-01/02 deficiencies | data already captured |

The first and third need **no new model calls at all** — the responses are already in the corpus.
That is the strongest argument for doing this now.

---

## 8. Corpus of 13 papers downloaded 2026-08-06

Each owes a `*-insights.md` under the established per-paper protocol.

**Independence / aggregation**
- `nine-judges-two-effective-votes-correlated-errors-llm-panels-arxiv-2605.29800.pdf`
- `examining-independence-ensemble-condorcet-jury-theorem-llms-arxiv-2409.00094.pdf` (Lefort et al. 2024)

**Debate failure modes**
- `talk-isnt-always-cheap-failure-modes-multi-agent-debate-arxiv-2509.05396.pdf`
- `not-all-flips-are-conformity-stance-convergence-debate-arxiv-2606.00820.pdf`
- `demystifying-multi-agent-debate-confidence-diversity-arxiv-2601.19921.pdf`
- `when-identity-skews-debate-anonymization-bias-reduced-arxiv-2510.07517.pdf`
- `heterogeneous-llm-debate-adversarial-peers-arxiv-2606.19826.pdf`

**Aggregation / social choice**
- `from-debate-to-decision-conformal-social-choice-deliberation-arxiv-2604.07667.pdf`

**Scalable oversight**
- `avoiding-obfuscation-prover-estimator-debate-arxiv-2506.13609.pdf` (Brown-Cohen, Irving, Piliouras)
- `debate-helps-weak-judges-reward-stronger-models-arxiv-2605.27483.pdf`
- `collaborative-disagreement-resolution-scalable-oversight-arxiv-2607.01251.pdf`
- `scalable-oversight-superhuman-ai-recursive-self-critiquing-arxiv-2502.04675.pdf`
- `calibrating-conservatism-scalable-oversight-arxiv-2605.28807.pdf`

Already present and directly relevant:
- `task-aware-llm-council-adaptive-decision-pathways-arxiv-2601.22662.pdf` + insights
- `dynamic-role-assignment-multi-agent-debate-arxiv-2601.17152.pdf` + insights
- `agenticsimlaw-juvenile-courtroom-multi-agent-debate-tabular-arxiv-2601.21936.pdf` + insights

Every PDF's title was verified against its slug via `pdftotext`; `2506.13609` was renamed after that
check showed the search-derived slug ("obfuscated-arguments-recursive-debate") did not match its
actual title.
