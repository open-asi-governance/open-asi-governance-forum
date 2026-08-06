# Literature — councils of agents, deliberation failure modes, scalable oversight

Assembled 2026-08-06 to answer one question adversarially: **is this corpus's four-reviewer
deliberation structure defensible, or does the literature refute it?**

The synthesis is `councils-of-agents-synthesis.md`. The measured answer for *this* corpus's own
round-01 panel is `../methods/reviewer-concurrence-round-01.md`, and the defect it prompted in the
corpus's own method is **D-22**.

## Redistribution and licensing

**Eleven of the thirteen papers are included here in full.** All eleven are CC-BY 4.0 or CC-BY-SA
4.0, which permits redistribution with attribution; each is attributed by title, authors and arXiv
identifier below.

**Two are deliberately NOT included**, because they carry the arXiv
`nonexclusive-distrib` license: the authors retain copyright and granted redistribution rights to
arXiv, not to third parties. Copying them into this public repository would not be lawful. They are
cited and linked instead, and the synthesis quotes only short passages under fair use, with the
source and page context stated.

That one of the two is the single most important paper in the set is unfortunate but not a reason
to bend the rule. A governance corpus that violates a copyright license while lecturing others
about provenance discipline would deserve everything it got.

## Not included — link only

| Paper | arXiv | License | Why it matters |
|---|---|---|---|
| Guneet Kohli (Apple). *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels* | [2605.29800](https://arxiv.org/abs/2605.29800) | arXiv non-exclusive-distrib | **The load-bearing paper.** 9 frontier LLMs across 7 families ≈ 2 independent votes; panel accuracy 8–22pp short of the independent ideal; best single judge matches or beats the panel; aggregation recovers ≤11% of the gap. |
| Jonah Brown-Cohen, Geoffrey Irving, Georgios Piliouras. *Avoiding Obfuscation with Prover-Estimator Debate* | [2506.13609](https://arxiv.org/abs/2506.13609) | arXiv non-exclusive-distrib | The obfuscated-arguments problem: a dishonest debater can decompose an easy claim into intractable subproblems so an honest opponent cannot find the flaw. Directly relevant to the ICP ladder. |

## Included

### Independence and aggregation

| File | Paper | arXiv | License |
|---|---|---|---|
| `examining-independence-…-2409.00094.pdf` | Lefort, Benhamou, Ohana, Guez, Saltiel, Jacquot. *Examining Independence in Ensemble Sentiment Analysis: A Study on the Limits of Large Language Models Using the Condorcet Jury Theorem* | [2409.00094](https://arxiv.org/abs/2409.00094) | CC-BY 4.0 |

### Debate failure modes

| File | Paper | arXiv | License |
|---|---|---|---|
| `talk-isnt-always-cheap-…-2509.05396.pdf` | *Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate* | [2509.05396](https://arxiv.org/abs/2509.05396) | CC-BY 4.0 |
| `not-all-flips-are-conformity-…-2606.00820.pdf` | *Not All Flips Are Conformity: Decomposing Stance Convergence in Multi-Agent LLM Debate* | [2606.00820](https://arxiv.org/abs/2606.00820) | CC-BY 4.0 |
| `demystifying-multi-agent-debate-…-2601.19921.pdf` | Zhu, Zhang et al. *Demystifying Multi-Agent Debate: The Role of Confidence and Diversity* | [2601.19921](https://arxiv.org/abs/2601.19921) | CC-BY 4.0 |
| `when-identity-skews-debate-…-2510.07517.pdf` | *When Identity Skews Debate: Anonymization for Bias-Reduced Multi-Agent Reasoning* | [2510.07517](https://arxiv.org/abs/2510.07517) | CC-BY 4.0 |
| `heterogeneous-llm-debate-adversarial-peers-…-2606.19826.pdf` | *Heterogeneous LLM Debate Under Adversarial Peers: Honest Gains, Replacement Costs, and Resilience* | [2606.19826](https://arxiv.org/abs/2606.19826) | CC-BY 4.0 |

### Aggregation and social choice

| File | Paper | arXiv | License |
|---|---|---|---|
| `from-debate-to-decision-…-2604.07667.pdf` | *From Debate to Decision: Conformal Social Choice for Safe Multi-Agent Deliberation* | [2604.07667](https://arxiv.org/abs/2604.07667) | CC-BY 4.0 |

### Scalable oversight

| File | Paper | arXiv | License |
|---|---|---|---|
| `debate-helps-weak-judges-…-2605.27483.pdf` | Elasky et al. *Debate Helps Weak Judges Reward Stronger Models* | [2605.27483](https://arxiv.org/abs/2605.27483) | CC-BY 4.0 |
| `collaborative-disagreement-resolution-…-2607.01251.pdf` | Jiang, Chen et al. *Collaborative Disagreement Resolution for Scalable Oversight* | [2607.01251](https://arxiv.org/abs/2607.01251) | CC-BY 4.0 |
| `scalable-oversight-superhuman-ai-…-2502.04675.pdf` | Wen, Lou et al. *Scalable Oversight for Superhuman AI via Recursive Self-Critiquing* | [2502.04675](https://arxiv.org/abs/2502.04675) | **CC-BY-SA 4.0** |
| `calibrating-conservatism-…-2605.28807.pdf` | Overman, Bayati. *Calibrating Conservatism for Scalable Oversight* | [2605.28807](https://arxiv.org/abs/2605.28807) | CC-BY 4.0 |

## Reading status — stated because it changes how much weight these citations carry

Read abstract and introduction: `nine-judges` (2605.29800), `talk-isnt-always-cheap` (2509.05396),
`not-all-flips` (2606.00820). **Read in full: none.** The remaining ten are title-and-abstract only.
Claims in the synthesis sourced from search summaries rather than the papers themselves are marked
`[unverified]` there and must not be cited onward until checked against the PDF.

This is the same discipline the corpus applies to model outputs: a claim's provenance is recorded,
and "I have not actually read this" is a recordable state rather than something to paper over.

## Every title was verified against its file

Each PDF's first page was checked with `pdftotext` against the slug it was saved under. One
mismatch was found and corrected: `2506.13609` had been saved from a search result as
`obfuscated-arguments-recursive-debate`, but its actual title is *Avoiding Obfuscation with
Prover-Estimator Debate*. A citation index built from search snippets rather than from the
documents would have carried that error forward.
