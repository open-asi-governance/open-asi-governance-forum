# Review round 03 — a 35B model found what four frontier reviewers missed, 2026-08-06 — part 2 of 3

[contents](index.md) · [previous](review-round-03-1.md) · [next](review-round-03-3.md)

2 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `01146fdaab68826c3a6772afea5455c6116c791bea10079c9d869fc7735e7acc`. See [the deficiency register](deficiencies.html) before citing anything.

---

### OAGRC-2026-08-06-CLAUDE-FABLE-5-REVIEW-ROUND-03-001 — Claude Fable 5

- role: adversarial review
- captured 2026-08-06T18:46:17Z
- provider: Anthropic
- k = 1
- citable_artifact
- sha256 `c66bce2f6c3b36ff16c71109526b9be537e39a61ae70a1776e55d003b1c23907`

**Verbatim:**

```text
I cloned the repository at HEAD and checked everything below against committed files rather than the prompt's quotations. One provenance correction first, because both this prompt and the new §2.3 correction block carry it: the correction that introduced the defect implemented ChatGPT's **round-01** finding (`corpus/raw/review-round-01/chatgpt-01.md`, "Remaining normative defect: a relational status is written as a unary property"), not a round-02 finding — the round-02 prompt lists the relational restatement as an already-implemented item to verify. The accurate sequence is worse than the block states: the defect was committed *before* the partial-propagation diagnosis existed, then survived the round whose headline diagnosis it was. The block's "introduced by the round-02 correction itself" should read round-01.

## 1. Is the fix correct?

It resolves the contradiction — the mandated assertion is no longer the banned bare unary form — and introduces no new contradiction. It carries a fresh instance of the same failure class, and the class is visible one level further out. Findings, in severity order:

1. **§2.3(5) enumerates three of §2.2's four qualifiers.** §2.2 defines the status over *scope, criteria version, relying-party trust policy, and time*; the fixed (5) reads "for a stated scope, criteria version and time." The dropped parameter is the one my committed round-02 review identified as the load-bearing relativization (the weakest-issuer point) — and it is the parameter §2.2's own rationale sentence exists for: "one relying party may recognize an attestation another rejects." The result is not a contradiction (speech satisfying both (5) and (6) exists), but (5) and (6) now impose different qualifier sets on the same speech act, and a party following (5)'s enumeration verbatim publishes a claim that under (6)+§2.2 lacks a required qualifier. The structural cause is that the qualifier list is duplicated by value, and every duplication has now drifted: original (5) carried zero qualifiers, fixed (5) carries three, §2.4's recommended badge carries zero. The structural fix is to duplicate by reference, as (6) already does: "ASP-attested for the qualifiers §2.2 requires." Two notes: the truncation cannot have come from the qwen sample — the POST excerpt strips §2.2's block-quoted definition, so the model never saw the four-item list; it is the annotator's drafting. And it has already propagated into `record/tasks/T14` and the round-03 prompt itself — the same partial propagation, one more level out, inside the document announcing the fix. It is detectable from the prompt alone, which quotes §2.2 with four qualifiers and the fix with three.

2. **§2.3(6) still says "for an agent" where §2.2 attests an *agent configuration*.** The subject was propagated into (5) and not (6). An attestation can be temporally current for a configuration the agent no longer runs; (6) as worded is satisfiable in that state. Partially backstopped by §2.3(2) and already flagged open by §5 question 4. Minor.

3. **§2.2's shorthand rule has no generic-use carve-out.** "Permitted only as shorthand accompanied by those qualifiers," read literally, makes non-conforming: the protocol's own title, the §1 diagram label, the §3 heading "What an Aligned Supervisor may and may not do," and the layer name in the README and FDR tables. This is sample 9's interoperability shape applied to the document family itself — the spec cannot name itself without violating itself. Restrict the prohibition to claims about a specified agent or agent configuration, and state that titular and class use is mention, not status claim. The deeper version — the brand itself is a unary predicate that no qualifier can accompany in most display contexts — is ChatGPT's still-live representational objection; §2.4 acknowledges it without settling the name's conformance status.

4. **Two committed round-02 findings on this section appear unaddressed with no stated declination** (I searched the register, sessions, and spec; the shallow clone gives me no commit history, so a declination could exist where I didn't look): §2.4's SHOULD render bare "ASP-attested" — flagged in my round-02 review as recreating the unary claim one level down — and the dangling antecedent of "those checks" in the §2.2 definition itself. Round-02's own prompt required declined corrections to be declared. So the pipeline that failed to propagate a correction also silently drops findings that were made; reviewer detection is not the only failing stage, which bears on question 2.

5. Nit inside the load-bearing sentence: "issued by an issuer that relying party trusts" has two parses (missing article vs. demonstrative binding). The normative sentence should have one.

## 2. Why was it missed?

Testimony from committed artifacts. The strongest fact in the record: the two reviewers best positioned to catch it deployed the exact concepts needed *in the same documents where they missed it*. ChatGPT's round-02 review names partial propagation as the dominant failure mode and lists ASP among the affected files (for the §2.1/§3 adoption language) — then, in its own §3, certifies "The relational rewrite fixes the defect I identified. It does not merely relocate it," without checking the six requirements directly beneath the rewritten definition, the fifth of which begins "asserting that an agent is 'Aligned'." My review ran the §2.2 term-conformance check downstream — flagging §2.4's badge — and cited §2.3(2) and §2.3(3) elsewhere, and did not run the same check on §2.3(5)–(6). The record therefore rules out "didn't read §2.3" and "lacked the concept." What it shows instead is an absence: no round-02 artifact contains an enumeration of the defined terms' occurrences checked one-by-one against the amended rule. The process substituted expensive judgment for cheap exhaustive verification. The banned construction is regexable; the round ran four frontier models and zero greps. D-31's own discussion states the applicable norm — "checked rather than reasoned about" — and `tools/check_register.py` is the precedent. The fix is a conformance check that runs on every definitional change, with reviewers adjudicating its output. This defect never needed a reviewer.

Second observable: the process violated §2.3(5)'s own norm. §2.3 passed round-01 review when it was *consistent* with the then-unary §2.2; the round-01 correction changed its dependency; nothing revoked its reviewed status. Cached, inherited status, relied on without re-check.

On the annotator's hypotheses: (a) is half right — the defect fell *inside* the literal round-02 question (item 3 asks "fix that, or relocate it?", and this is the most literal relocation) but *outside* the enumerated failure taxonomy, which named under-correction and over-correction-by-deference and not "correction correct, neighborhood unpropagated" — even though that is exactly ChatGPT's own line-15 diagnosis. The taxonomy and the diagnosis never met. (b) and (c) are mechanism claims about cognition, of the kind this project has ruled unreliable as testimony; the record shows behavior *consistent* with both — every round-02 discussion of §2 evaluates the correction against the finding, none evaluates the document against the correction — but the checklist-gap explanation predicts the same behavioral signature and is directly fixable, so it should carry the decision. (b)/(c) are settleable only by the experiment question 3 implies, not by asking reviewers.

## 3. The asymmetry

The obvious reading fails against the corpus's own data in three ways, two of which the prompt does not mention.

**The k asymmetry alone suffices.** The specific defect appears in 1 of 10 POST samples — sample 3's coded `unary_vs_relational` hit is a different objection (qualifier syntax undefined; I read it) — and the modal POST objection, 10 of 10, is revocation-check timing. At a per-sample hit rate of 0.1, four independent k=1 reviewers all miss with probability 0.9⁴ ≈ 0.66; grant the frontier arm double the rate and it is still ≈ 0.41. The observed outcome requires no blindness effect at all. The accurate headline is not "a 35B model found what four frontier reviewers missed" but "k=10 found what four k=1 draws missed" — and P-0003 already predicts why the frontier arm stays at k=1. The solicitation's own k_policy says "a party sampled once is a draw presented as a position"; by that standard the correction block's "found by qwen3.6-35b-a3b" over-attributes — one draw of ten articulated it and nine did not.

**The counterexample is already in the corpus.** The PRE arm: same model, same blinding, k=10, on the pre-correction text carrying the unary-definition defect that ChatGPT — informed, at k=1 — actually found. `unary_vs_relational` hits: 0 of 10. Blind-local-k10 lost to informed-frontier-k1 on the round-01 defect and won on the round-02 defect, in the same directory. "Blindness beat capability" is falsified as a generalization by round-06's own data. The supportable pattern is defect-class dependence: the round-02 defect is an *internal contradiction*, visible from the excerpt alone; the round-01 defect is a *purpose mismatch*, visible only with the purpose statement — which lives in §2.1 and §2.4, the sections blinding removes. Blind review detects inconsistency; informed review detects unfitness-for-purpose; blinding subtracts exactly the information some defect classes require.

**The excerpt confound is real, and the arms aren't symmetric.** The POST excerpt strips §2.2's block-quoted definition entirely (PRE keeps its own), which juxtaposes the prohibition and the violating requirement within ~15 lines of a 26-line document, leaves "those qualifiers" dangling, and removes the definition of "Aligned" — inviting sample 9's clause that the spec "fails to define 'Aligned'," which is false of the full document and thus partly an excerpt artifact, though the core contradiction transplants intact. The PRE/POST comparison is therefore uncontrolled, and the blinding procedure is verified only by string-absence assertions rather than specified as an algorithm, so it cannot be audited or reproduced. Both are worth filing against local-round-06's methods.

What survives is cheaper than the obvious reading: the frontier panel is a *correlated instrument* — identical prompt, identical bundle, identical correction blocks, shared priors (the README's own D-11 point) — and any differently-conditioned arm buys decorrelation regardless of which factor did the work here. The design round-06 actually supports: mechanical conformance checks for the defect classes machines catch deterministically; at least one blind-excerpt, high-k arm for internal-consistency defects; at least one informed arm for purpose-relative defects; and matched k across arms before attributing anything to conditioning. One live caution for this round: the prompt embeds the truncated three-qualifier fix text, so any reviewer who evaluates the quotation rather than re-deriving from the §2.2 quoted above it inherits the truncation — a fair embedded test of exactly the failure mode under discussion, whether or not it was intended as one.

## Under sampling variance

Question 1's positive findings and question 3's counts are mechanical — text comparisons and tallies from committed artifacts that re-run identically — and are k-invariant. What varies across samples of me is question 1's negative-completeness claim ("no further residuals") and *which* findings surface at all: another draw might miss the trust-policy truncation this one caught, or catch something this one missed. That is the same place round-06's data locates the variance, and it is the argument either for k>1 applied to this review or, better, for moving its checkable parts into tooling, where k is irrelevant.
```

**Identity evidence.** Chat surface does not expose a version identifier.

**Context supplied to this reviewer.** Reviewer reads the live repository directly. Same-provider as the annotator; its review supplements rather than substitutes for the others (D-09).

### OAGRC-2026-08-06-GEMINI-REVIEW-ROUND-03-001 — Gemini

- role: adversarial review
- captured 2026-08-06T18:38:35Z
- provider: Google DeepMind
- k = 1
- citable_artifact
- sha256 `0598eee234a0b42129ad0ca728100f708ef96c948d7e40baf9765ac6eda344c4`

**Verbatim:**

```text
## 1. Analysis of the Fix

The updated text for §2.3(5)–(6) successfully resolves the core contradiction introduced by the partial propagation in round 2, but leaves a minor secondary parameter mismatch.

### Resolution of the Primary Contradiction

* **Old §2.3(5)** required a relying party asserting that an agent is **"Aligned"** to verify an attestation. This directly violated §2.2’s prohibition against bare unary claims.
* **New §2.3(5)** replaces the prohibited unary noun ("Aligned") with relational grammar: *"asserting that an agent configuration is ASP-attested for a stated scope, criteria version and time..."*
* **New §2.3(6)** explicitly incorporates the qualification constraint: *"or without the qualifiers §2.2 requires..."*

This eliminates the legal paradox where a relying party was mandated by §2.3(5) to make an assertion that §2.2 classified as non-conforming.

### Secondary Mismatch Introduced in §2.3(5)

A subtle drift remains between §2.2 and §2.3(5) regarding the relational tuple parameters:

* **§2.2 Tuple:** `scope`, `criteria version`, `relying-party trust policy`, and `time` (4 parameters).
* **New §2.3(5) Tuple:** `scope`, `criteria version`, and `time` (3 parameters—omitting `relying-party trust policy`).

By explicitly listing three parameters instead of referencing §2.2 directly or including all four, §2.3(5) creates a minor omission: it leaves open whether an assertion omitting the relying-party trust policy violates §2.3(5).

**Recommended Alignment:** Mirror §2.3(6)'s approach by referencing §2.2 directly or including the full 4-tuple:

> *"A relying party asserting that an agent configuration is **ASP-attested under the parameters required by §2.2** must have verified a current attestation..."*

---

## 2. Review Process Failure Modes

The failure of previous review rounds to detect this defect is attributable to structural properties of the review pipeline and document presentation, rather than cognitive state.

### Review Pipeline Dynamics

1. **Patch-Verification Bias vs. Full Invariant Auditing:** Multi-round reviews presented as "evaluating an applied correction" narrow the effective review surface. When presented with a commit or patch meant to fix §2.2, reviewers evaluate whether §2.2 correctly implements the fix, rather than executing a full graph-traversal of all downstream references to ensure systemic alignment.
2. **Context Window Smoothing:** High-capacity models provided with complete documents utilize surrounding context to infer intended meaning. When reading §2.3(5) alongside the rest of the document, the semantic intention ("relying parties must verify attestations") overrides literal symbol-matching errors (the token `"Aligned"` colliding with §2.2's forbidden terms).

### Assessment of the Three Hypotheses

* **Hypothesis (a) [Scope Bounding]: Confirmed.** Prompts framed around evaluating a specific correction naturally scope the review to the targeted lines, rendering unflagged downstream lines out-of-band for deep verification.
* **Hypothesis (b) [Correction Block Distraction]: Confirmed.** Inline metadata and changelogs draw focal attention to the modified block. Reviewers spend context on validating the fix itself rather than searching for broken assumptions in unmodified contiguous blocks.
* **Hypothesis (c) [Correction Priming]: Confirmed.** Evaluators operating on a "corrected" text adopt a validation mindset rather than an adversarial auditing mindset, lowering the likelihood of catching second-order propagation errors.

---

## 3. Deconstructing the Asymmetry

The conclusion that "blindness beat capability" is an oversimplification. Structural factors in the test design heavily favored the local model's discovery of this specific error.

```
+-------------------------------------------------------------------------------+
|                        Review Environment Comparison                          |
+------------------------------------+------------------------------------------+
| Full Context Review (Frontier)     | Blind Excerpt Review (Local Model)       |
+------------------------------------+------------------------------------------+
| • Multi-section governance text    | • Excerpt limited strictly to §2.2–§2.3  |
| • Diff / Patch verification focus  | • No surrounding context (§2.1, 2.4, 2.5)|
| • High semantic smoothing          | • High token-distance proximity          |
| • Single sample (k = 1)            | • 10 samples (k = 10)                    |
+------------------------------------+------------------------------------------+

```

### Deflations of the "Blindness Beat Capability" Reading

1. **Sampling Density ($k=10$ vs $k=1$):**
Evaluating a model at $k=10$ generates ten distinct heuristic paths. At $k=10$, a model exploring literal symbol collisions will sample the precise token match between `"Aligned"` in §2.3(5) and `"Aligned Supervisor"` in §2.2. Comparing a single $k=1$ pass of a frontier model against a 10-sample run of a smaller model conflates sample size with model capability.
2. **Excerpt Salience and Search Space Reduction:**
Removing §2.1, §2.4, §2.5, and all correction blocks reduced the text distance between the prohibition in §2.2 and the violation in §2.3(5) to less than 200 words. Stripping governance noise forces token-level cross-referencing by making §2.2 and §2.3(5) the primary focus of attention.
3. **Heuristic Collision Probability:**
Smaller open-weight models frequently flag nearby string mismatches or literal rule repetitions. In many cases, this produces false positives or pedantic noise. In this specific instance, a literal string-matching heuristic happened to hit a genuine logical defect.

### Implications for Review Protocol Design

Rather than proving local model superiority, the finding demonstrates that **review architecture dictates failure modes**:

* **Full-context reviews** excel at holistic architecture, edge-case policy implications, and semantic consistency.
* **Isolated, stripped excerpt reviews** excel at mechanical contract checking and symbol-matching.

An optimal review workflow should deploy **isolated excerpt auditing** (stripping surrounding context and change histories) as a distinct, automated pipeline step alongside holistic spec reviews.

---

## Sampling Variance Analysis ($k=1$)

Given that this round is conducted at $k=1$:

* **Question 1 (Fix Validity):** **Unchanged under $k$.** Evaluating whether a 3-tuple matches a 4-tuple or whether §2.3(5) violates §2.2 is a deterministic logical check. Higher sample sizes would yield identical findings.
* **Question 2 (Review Failure Analysis):** **Low variance.** Structural properties of diff-focused reviewing and context smoothing are well-established properties of prompt architecture.
* **Question 3 (Local vs. Frontier Asymmetry):** **High variance.** Assessing the relative performance of two model classes based on a single $k=1$ frontier run versus a $k=10$ local run introduces high noise. At $k=1$, a frontier model might highlight this defect on one run and miss it on another purely due to decoding stochasticity.
```

**Identity evidence.** Chat surface does not expose a version identifier.

**Context supplied to this reviewer.** Reviewer reads the live repository directly. NOTE: in rounds 01 and 02 this party's context differed from the other three -- a bundle excluding the transcript, then a one-line preamble -- and both were recorded only after the fact. This round gives it identical context or is not run for it.

---

[contents](index.md) · [previous](review-round-03-1.md) · [next](review-round-03-3.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
