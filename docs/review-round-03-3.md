# Review round 03 — a 35B model found what four frontier reviewers missed, 2026-08-06 — part 3 of 3

[contents](index.md) · [previous](review-round-03-2.md) · [next](review-round-02-prompt-critique.md)

1 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `1d3e9338e4cd9910bd44adac105d6068e8a950f5967b97b6358ddff6d479d9c2`. See [the deficiency register](deficiencies.html) before citing anything.

---

### OAGRC-2026-08-06-GROK-REVIEW-ROUND-03-001 — Grok

- role: adversarial review
- captured 2026-08-06T18:37:10Z
- provider: xAI
- k = 1
- citable_artifact
- sha256 `bc511a8d0478c4300b97aea43e28307f580560fc64628ad465c9b89617d2c8ad`

**Verbatim:**

```text
**1. Is the fix correct?**

The proposed rewrite of §2.3(5)–(6) **resolves the specific contradiction** that the qwen finding identified, and does not relocate it or introduce a new one of the same kind.

- §2.2 forbids bare unary claims (“an agent *is* an Aligned Supervisor”) and requires the relational, scoped, time-bound form (ASP-attested for stated scope / criteria version / relying-party trust policy / time). It also states that “Aligned” denotes that status and nothing more, and that “Aligned Supervisor” is permitted only as shorthand accompanied by those qualifiers.
- Pre-fix §2.3(5) still used the unary form “asserting that an agent is ‘Aligned’,” which the finding correctly treated as effectively licensing the very grammar §2.2 prohibits. Pre-fix §2.3(6) enforced attestation only for the term “Aligned Supervisor,” without requiring the qualifiers §2.2 demands.
- Post-fix (5) requires the assertion to be of the full relational predicate (“ASP-attested for a stated scope, criteria version and time”). Post-fix (6) makes omission of the §2.2 qualifiers itself a protocol violation. That aligns the enforcement language with the definition. A relying party can now make a conforming assertion only by using (or implying under the required qualifiers) the relational form; the shorter term “Aligned” is no longer treated as a free-standing status claim that triggers the check obligation while remaining unary.

Two residual points remain, neither of which recreates the original contradiction:

- The post-fix (5) list of qualifiers is slightly shorter than §2.2’s (it omits explicit “relying-party trust policy”). That is a minor incompleteness, not a contradiction; a careful reading of §2.2 still supplies it. Tightening (5) to enumerate the full set would remove the gap.
- The live document currently published at `spec/asp/asp-v0.1.md` still contains the pre-fix (5)–(6). The correction described in the query has not yet been propagated into the repository text itself.

**Partial-propagation check outside §2.3.** Yes, unary or near-unary grammar still appears elsewhere in the same file and in related repository text:

- Section title: “2. Normative definition of ‘Aligned’.”
- §2.1 and surrounding prose repeatedly treat “Aligned” as the thing being defined / reserved against.
- §3 title and body: “What an Aligned Supervisor may and may not do”; “May: \ldots”; the whole section speaks of “an Aligned Supervisor” as if the noun phrase names a class of agents rather than a relational status.
- §6: “No ASP-attested agent currently exists anywhere” (better, because it uses the relational predicate) sits beside earlier “Aligned Supervisor” usage.
- README / naming-architecture tables and prose still list the enterprise layer as “Aligned Supervisors” and describe the term as a compliance status, but the surface grammar remains the noun-phrase form that §2.2 marks non-conforming when used bare.

These are the same class of partial-propagation failure the round-02 correction was meant to prevent: definition fixed, consequent requirements and surrounding exposition only partly updated. They do not re-introduce a direct logical contradiction between §2.2 and §2.3(5), but they leave the document internally inconsistent in register and invite exactly the interoperability / reading failure the qwen sample described.

**Verdict on the fix:** the new §2.3(5)–(6) text is correct for the contradiction it targets. The document as a whole is not yet clean of the unary grammar §2.2 forbids.

**2. Why was it missed? (testimony about the review process)**

From the observable process artifacts (correction blocks, scoped prompts, sequential rounds, k=1, the presence of explicit “Correction, review round 01” call-outs that narrate what was already fixed):

Reviewers were handed a document whose most salient recent change was the §2.2 restatement, accompanied by an explicit correction block that told them precisely what ChatGPT had found and how it had been repaired. Attention and verification effort therefore concentrated on whether the new definition satisfied the prior finding. The consequent-requirements list (§2.3) was treated as downstream scaffolding that “should” have been updated, not as primary text under the same adversarial pressure. Because the prompt for the post-correction round was itself framed around the correction, residual mismatches in neighboring clauses fell outside the effective search window. Parallel reviewers operating under the same framing produced the same omission; the process contained no independent, correction-block-free pass over the full normative core after the edit was applied. That is a process failure of partial propagation under correction-focused review, not a claim about any model’s internal cognition.

Of the three listed hypotheses, (b) and (c) are closest to the above and are not rejected. (a) is plausible for the original round-02 prompt scope but is secondary; the decisive mechanism was the post-edit review design that directed attention at the repaired definition and the correction narrative rather than at every occurrence of the forbidden grammar. A stronger process would have included at least one full-text, correction-block-stripped re-review of §2 after every edit that touched the definition.

**3. What the asymmetry means (attacking the obvious reading)**

The obvious reading—blindness (no correction blocks, no ballot history, §2.1/§2.4/§2.5 stripped) beat capability—is attractive and may be partly true as a review-design finding. It does not survive cleanly.

- **Sampling.** The detection is one sample out of k=10. Under the project’s own standard, a single hit is an existence proof that the defect is detectable, not evidence that frontier models are systematically worse or that local models are systematically better. The other nine samples from the same model are not quoted; variance is unknown.
- **Excerpt construction.** The annotator supplied precisely §2.2–2.3 with the surrounding history and correction blocks removed. That maximises the local inconsistency’s salience. In the full document the same sentences sit next to an explicit correction narrative that explains the relational turn; a reviewer who sees the narrative can treat residual unary phrasing in §2.3 as “not yet updated” rather than as a live contradiction. The local model never faced that distraction. This is selection of the evidence, not a pure capability comparison.
- **Task difference.** Frontier reviewers in the earlier rounds were asked to evaluate a correction (or a corrected document). The local model was asked to review normative text for consistency, blind. Different questions produce different findings; the asymmetry is therefore confounded by prompt and context, not solely by presence/absence of correction blocks.
- **Base-rate / objection style.** Smaller or differently trained models can flag surface lexical mismatches more readily precisely because they lack the broader context that lets a larger model “understand the intent” of a recent fix and therefore forgive residual wording. Being right once under those conditions does not generalise to superior review quality.
- **Counter-prediction.** If the decisive variable were truly “correction blocks vs. none,” then a frontier model given the identical stripped §2.2–2.3 excerpt should also surface the contradiction at non-trivial rate. That experiment is not reported. Until it is, the blindness-beats-capability claim remains an untested inference from a single annotated sample.

The stronger, still-process-level conclusion is narrower: after an edit that changes definitional grammar, at least one reviewer pass should be performed on the post-edit text with all correction narrative and historical sections removed. That design change is warranted whether or not local models are “better.” It does not require ranking model families.

**Sampling-variance note (k=1).**  
Question 1 (correctness of the textual fix) is largely stable under re-sampling; it is a consistency judgment over a short, fixed pair of paragraphs. Questions 2 and 3 are process interpretations and are more sensitive to framing, order, and which residual unary sites a reviewer notices; different samples could weight the relative contribution of (b) vs. (c), or the force of the excerpt-construction deflation, differently. Under the project’s own P-0003 / k≥5 standard, only question 1 would be treated as robust on the present evidence.
```

**Identity evidence.** Chat surface does not expose a version identifier. Grok self-reported 'Grok 4.5' in round 02; a self-report is testimony, not authentication (D-18).

**Context supplied to this reviewer.** Reviewer reads the live repository directly.

---

[contents](index.md) · [previous](review-round-03-2.md) · [next](review-round-02-prompt-critique.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
