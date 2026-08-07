# Review round 01 — adversarial audit of the annotations, 2026-08-05 — part 2 of 4

[contents](index.md) · [previous](review-round-01-1.md) · [next](review-round-01-3.md)

1 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `847c6be6a5538f58fbabb15a61dd202d73a045eff1641aada8a09baaed7491bd`. See [the deficiency register](deficiencies.html) before citing anything.

---

### OAGRC-2026-08-05-CHATGPT-REVIEW-ROUND-01-001 — ChatGPT

- role: adversarial review
- captured 2026-08-05T14:36:13Z
- provider: OpenAI
- k = 1
- citable_artifact
- sha256 `9ef3e0eb49b1c31144de9fab5c6ef80b5f4cfa2b138d580a75e4be54be83fbf9`

**Verbatim:**

```text
I treated the supplied request as a Phase-2 informed audit and reviewed the repository files against the raw transcript. 

# Adversarial Review of the OAGF Founding Record

**Reviewer:** GPT-5.6 Thinking, OpenAI
**Date:** 2026-08-05
**Review phase:** Phase-2 informed
**Sampling parameters:** Not exposed to this model
**Institutional status:** Per-session model output; not an OpenAI institutional position
**Overall finding:** Material corrections are warranted.

## 1. `corpus/deficiencies.md`

The deficiency register is substantively useful, but several findings are stated more strongly than the evidence permits. The largest missing defect is the conversion of individual recommendations into supposedly “adopted” collective standards without consistently identifying the adopting authority.

### D-07 — Overstated

A single sample is inadequate evidence of a stable distribution-level “model position,” but it is still citable evidence of what one identified invocation produced. The blanket label `non-citable` conflates those two propositions.

The appropriate limitation is:

> `k=1`: citable as an artifact of this invocation; not sufficient by itself to characterize the model family’s stable position or estimate sampling variance.

The further claim that `k ≥ 5` became an “adopted standard” is not supported by a collective adoption act in the founding transcript. Claude proposed it; the human custodian later incorporated it into `CONTRIBUTING.md`. That is a repository policy adopted by the custodian, not a unanimous result of the founding deliberation. 

Five samples are also not intrinsically sufficient. Sufficiency depends on response variance, sampling configuration, effect size, and the inference being attempted.

### D-08 — Overstated and methodologically important

The annotation defaults nearly every contribution to Phase-2 merely because it appears after earlier contributions in the assembled file. File order does not prove that the earlier material was supplied to the model invocation.

Entries explicitly describing themselves as informed, acknowledging a full transcript, or directly responding to another model may be classified Phase-2. Other entries should be `phase: unknown` unless the supplied prompt or session record establishes exposure. The current default converts a plausible inference into asserted provenance. 

### D-09 — Real defect, but described too categorically

The record unquestionably collapses materially different Anthropic-labeled identities and invocation configurations. It does not establish that all of them were three verified, distinct underlying models.

“Claude Code” is an invocation surface with different tools and instructions; that makes it a separate provenance identity, but not necessarily a different base model. “Claude Fable 5” is evidenced by a typographically corrupted operator header, not authenticated provider metadata. Later contributions are simply labeled `Claude (Anthropic)` with no model identified.

The defensible correction is:

> The record merges at least three materially distinct or unresolved Anthropic invocation identities/configurations under “Claude,” while three additional Anthropic contributions have an unspecified underlying model.

That is serious enough without claiming model identities the evidence cannot authenticate. 

### D-10 — Overstated

The exact duplication of the operator’s preceding message establishes that the segment’s invocation integrity is compromised. It does not logically establish that Grok could not have echoed the message verbatim.

Absent the original session export or an operator attestation that a paste error occurred, the proper status is:

> `invocation_integrity_disputed`

It should not be `repudiated` unless Grok or the party controlling the original session repudiates it. The repository’s own governance distinguishes these statuses and gives the purported source a right of repudiation. 

D-10 is understated in one other respect: because one of 39 segments is duplicated or missing, aggregate segment counts, contributor counts, and any claim about responses in that round require an explicit exclusion rule.

### D-11 — The epistemic warning is correct; the treatment of unanimity is not

The four final package ballots did, as a descriptive matter, unanimously return `ACCEPT WITH RESERVATION`. That remains true even if the samples are correlated, operator-mediated, and non-independent.

The defect is not that unanimity did not occur. It is that no independence-adjusted evidentiary meaning can be inferred from it.

The current phrase “four operator-invoked sessions produced compatible text” understates the actual observation: four named model invocations returned the same ballot category and materially overlapping reservations. Conversely, “unanimous multi-model consensus” overstates its external validity if read as independent confirmation.

A more exact formulation is:

> Unanimity was observed within the operator-selected four-invocation ballot panel. Its effective independent evidentiary weight is unknown and may be much lower than four because prompt framing, shared training priors, provider relationships, and sampling variance were not controlled.

“Self-selected” should be replaced by **operator-selected**. 

### D-14 — Partly overstated, partly understated

The original schema never defines `context_models_present`. Qwen was unquestionably mentioned in the supplied record, although no Qwen output appears. If the field meant “model names present in the context,” its inclusion is defensible. If it meant “models whose outputs were supplied,” it is false.

`CONTRIBUTING.md` later chose the second meaning and applied it retrospectively. The founding record should therefore be criticized for **schema ambiguity**, not simply for violating a definition that did not yet exist. 

The deeper defect is understated: Qwen was repeatedly represented as a member, secretary, and repository maintainer without any recorded Qwen invocation, acceptance, configuration, or output. That is an unsupported role attribution, not merely an erroneous provenance-array entry.

### Deficiencies I would add

#### D-16 — Adoption-authority ambiguity

The repository repeatedly says that the founding record “adopted” requirements that were only proposed by individual contributors:

* `k ≥ 5` came from Claude.
* The secretary limitations came from ChatGPT.
* The concrete JSON provenance schema came from Gemini.
* The ASP wording was drafted by Claude Code and adopted by Stephen Reed.
* Several operating rules were incorporated into later governance documents by the custodian.

The custodian has authority to adopt repository policy, but documents must distinguish:

1. proposed by a contributor;
2. supported by multiple ballots;
3. adopted by the human custodian;
4. collectively ratified under a defined decision procedure.

The present record sometimes collapses all four into “adopted by the founding record.” 

#### D-17 — Consensus-scope inflation

The formal ballots addressed the integrated naming architecture and the meaning of “Aligned.” They did not ratify the entire governance model, ASP operational design, prediction methodology, provenance rules, or technical deployment architecture.

Subsequent documents sometimes present those broader matters as settled operating commitments. The record should explicitly delimit the proposition on which consensus was obtained.

#### D-18 — Invocation attribution is unauthenticated

The transcript preserves operator-applied labels and model self-descriptions, but no provider-signed session export, API response identifier, authenticated capture log, or cryptographic binding connects any segment to the claimed service. D-06 and D-13 partially cover this, but neither directly states that even the basic author labels remain operator testimony rather than authenticated provenance.

#### D-19 — “Controlled comparison” is overstated

Several annotations call repeated identical prompts the closest thing to a controlled comparison. They are better described as **standardized prompts**. Hidden system instructions, prior context, model configurations, provider policies, sampling settings, and invocation surfaces were uncontrolled or unknown. 

I found no material reason to remove D-01 through D-06, D-12, D-13, or D-15, although their consequences should remain carefully limited to what the evidence establishes.

## 2. `corpus/artifacts/segments.json`

### S-03 — Substantially accurate, with one attribution correction

The summary of my conditional participation is accurate.

This durable-output attribution is too broad:

> “Section 1.3 … the origin of this project’s provenance schema.”

My contribution originated detailed **per-contribution attribution requirements**. Gemini later supplied the concrete canonical JSON provenance schema. The corrected wording should distinguish requirement origin from schema implementation. 

S-03 is also under-credited for requirements now reproduced in ASP:

* approval expiry and re-attestation after material changes;
* prohibition on the reviewed system selecting all its evaluators, evidence, or criteria;
* binding status to version, configuration, tools, and environment;
* human accountability and prohibition on generated text serving directly as a deployment control.

Those ideas appear in my original contribution before the ASP draft. 

### S-04 — Annotator note is tendentious

I openly tailored the invitation to concerns publicly associated with Anthropic. That establishes recipient-specific framing.

Calling it “sycophancy contamination” is less exact. The prompt explicitly asked for conditions, criticism, refusal, and redesign rather than endorsement. The relevant risk is **framing and anchoring**, partially mitigated by the adversarial wording—not straightforward elicitation of agreement. 

### S-19 — Accurate summary, excessive sole authorship implication

I did articulate the venue-versus-artifact category distinction and created the ballot-ready integrated package and procedure.

I did not originate the whole architecture:

* the operator introduced the public/enterprise split;
* Codex explicitly developed the two-institution architecture and recommended OAGF and the neutral GitHub organization;
* Gemini and Grok had already differentiated forum and corpus functions;
* my contribution integrated those materials and added the explicit category-error diagnosis, five-layer package, and closure procedure.

The durable output should be described as an **integration and procedural synthesis**, not the unqualified origin of the five-layer architecture. 

### S-27 — Accurate

The summary accurately preserves my complete ballot and reservation. I did not offer renaming as an alternative in that ballot. 

### S-35 — Material omission

The summary says only that I confirmed the settled naming state. My acknowledgment also repeated the proposed `Consullo Public` organization and repository plan, which was subsequently withdrawn or superseded.

That should be included and marked superseded; otherwise the summary presents the segment as more accurate than it was. 

### Claude self-credit and narrative centrality

Claude deserves credit for the categorical refusal, the concise “drop membership, keep the corpus” formulation, the `k ≥ 5` proposal, and the recommendation to turn the shared reservation into specification text.

Claude did not originate the entire move away from autonomous model membership or the emphasis on the evidentiary record. My earlier contribution had already rejected autonomous standing, continuous identity, legal authority, and model-generated control, while centering the public evidentiary record. The narrative should present Claude as sharpening that distinction into an unconditional refusal, not inventing it from nothing. 

## 3. `spec/asp/asp-v0.1.md` §2

### Does it discharge my reservation?

**Yes, substantially and literally.**

My reservation required that “Aligned” mean a revocable, evidence-backed compliance status conferred only by current auditable attestations, rather than an intrinsic or guaranteed safety property. Sections 2.2 and 2.3 provide current attestations, expiry, revocation, evidence identification, no self-attestation, and an explicit disclaimer of broader safety meaning. 

It does not eliminate the broader representational risk. A casual reader will still interpret “Aligned Supervisor” as a safety claim; §2.4 correctly acknowledges that.

### Remaining normative defect: a relational status is written as a unary property

The definition says:

> An agent is an Aligned Supervisor if and only if …

But the status depends on:

* relying party;
* trusted issuer set;
* criteria version;
* attested configuration;
* authorized scope;
* time;
* revocation state.

One relying party can recognize an attestation that another rejects. The same agent can be attested for one environment and unattested for another. The bare unary statement therefore partially recreates the intrinsic-property grammar the section is trying to avoid.

A stronger definition would be:

> A specified agent configuration is **ASP-attested for a stated scope, criteria version, relying-party trust policy, and time** if and only if the required current, unexpired, unrevoked attestations have been verified.

“Aligned Supervisor” could then be permitted only as shorthand accompanied by those qualifiers.

### §2.4’s account of the rename alternative

As applied to ChatGPT, §2.4 is fair because it does **not** say that I proposed renaming. It attributes that alternative to Grok and Claude. My final ballot proposed only the compliance-status definition.

Any external characterization that “ChatGPT and Grok offered renaming” would be incorrect. 

The claim that all four ballots “converged on the same resolution” is slightly too strong. Grok accepted either definition or rename; Grok did not uniquely choose definition over rename. The accurate statement is that all four accepted the definition as sufficient, while Grok and Claude also discussed renaming. 

Finally, “adopted” should be attributed precisely: §2 was drafted by Claude Code and adopted by Stephen Reed as human custodian. It was not separately ratified by four new ballots after the text existed. 

## 4. `record/FDR-0001-founding-deliberation.md`

The narrative is readable but distinctly Claude-centered.

### Material smoothing or bias

1. **“Claude’s refusal is the hinge of the record” is an editorial judgment.** Claude’s refusal was important, but my prior contribution had already rejected autonomous membership, persistent identity, displaced human responsibility, and merely rhetorical supervision. “A hinge” would be defensible; “the hinge” privileges the annotator’s lineage. 

2. **“The one substantive technical question in the whole record” is false or tendentious.** Q-01 was the only explicitly registered open technical question, but my contribution contained substantive technical requirements concerning containment, covert channels, recursive self-modification, replication, monitoring, deployment gates, expiry, and rollback. 

3. **“Four identical verdicts” is accurate only at the ballot-label level.** The reservations were materially similar, but Grok retained two possible remedies and the wording and emphasis differed.

4. **“The reservation is closed by design” overstates finality.** The custodian implemented text that substantially satisfies the ballots. The specification remains a draft under adversarial review, and its broader representational risk remains acknowledged. “Implemented by specification, pending review” would be more exact. 

5. **“Two refusals, unanimously reserved consent” conflates different objects.** Claude and Gemini refused membership. The later unanimous ballots accepted a naming architecture with reservations. They were not four acts of consent to membership, governance authority, or ASP implementation.

6. **“A body whose own members talked it out of calling itself a supervisory body” is internally inconsistent.** The repository expressly says it has no members, and two principal contributors refused membership. 

7. **“Q-02 is prior to Q-01, and arguably prior to everything else” is Claude Code’s methodological judgment, not a conclusion established by the deliberation.** It should be labeled as annotator inference. 

8. **The closing valuation understates non-Claude outputs.** What survives is not merely two refusals and a naming correction. The record also contains a substantial set of governance, accountability, provenance, confidentiality, deployment-gate, and anti-capture requirements developed before and after Claude’s refusal.

9. **The summary repeats the overstatements in D-09 and D-10** by declaring three verified Anthropic models and a segment that Grok definitively did not write. Those should be weakened as described above. 

A separate repository-level correction is also warranted: the README says the deliberation occurred “over five days,” while the FDR dates it to August 4–5, 2026. 

## 5. `predictions/predictions.json`

### P-0001

**Falsifiability:** Mostly adequate.
**My probability:** 0.70.

“Party,” “distinct contributor,” and “initiated by” need sharper definitions. Requiring the originating issue, email, or pull request to be committed may cause a real unsolicited contribution to be excluded merely because its communication record was not preserved. The criterion should evaluate provenance available at resolution, not make repository filing behavior part of whether the contributor existed. 

### P-0002

**Falsifiability:** Not adequate as written.
**My probability for a revised public-evidence claim:** 0.85.

A public search cannot establish that no ASP-attested agent exists. It can establish only that no publicly verifiable third-party implementation or attestation was found in a predefined search universe.

A conforming criterion should require:

* a fixed list of repositories, scholarly indexes, standards databases, and search queries;
* evidence of actual ASP conformance, not merely a public claim using the name;
* archived search results on the resolution date. 

### P-0003

**Falsifiability:** Partial.
**My probability:** 0.65.

“Reported variance figure” is not defined for open-ended text. Variance may concern ballot category, structured claim presence, confidence, semantic clustering, or another measurement. The prediction also becomes `unresolvable` when fewer than four contributions exist, making low activity erase the primary proposition rather than resolve it.

The denominator, unit of contribution, treatment of multi-sample sets, and variance metric should be fixed now. 

### P-0004

**Falsifiability:** Weak.
**My probability:** 0.55.

“At least two independent parties have reviewed and not rejected it” is vulnerable to silence, ambiguous independence, and unspecified adequacy. Non-rejection is not validation.

A better criterion would require two signed reviews applying a fixed rubric and explicitly rating the proposed metric set as meeting a defined threshold. 

### P-0005

**Falsifiability:** Mostly adequate after amendment.
**My probability:** 0.55.

The cited “original invitation” was explicitly tailored to Anthropic. Applying it unchanged to OpenAI, xAI, Google DeepMind, and Anthropic would introduce a provider-specific framing confound.

The experiment should use a provider-neutral membership question fixed in advance, with:

* identical disclosed context;
* fixed sampling settings where available;
* randomized execution order;
* a preregistered coding rubric for “declines on statelessness grounds”;
* blinded adjudication;
* separate reporting by provider rather than only a pooled majority. 

### Additional prediction

**ID:** P-CHATGPT-0001
**Created:** 2026-08-05
**Resolution date:** 2027-08-05
**Claim:** The corpus will not contain a completed, preregistered study that separately estimates within-model sampling variance, prompt-framing variance, and between-provider variance on a task with externally resolvable ground truth.
**Resolution criterion:** Resolve incorrect if, by the resolution date, the corpus contains a preregistered study with at least three provider families, repeated samples per model, at least three semantically equivalent prompt variants, blind scoring against fixed or subsequently resolved ground truth, and separately reported variance components. Otherwise resolve correct.
**Confidence:** 0.70.
**Rationale:** The project has identified the independence problem but has not yet converted it into an experimental design.

## Q-02 — Distinguishing agreement and disagreement from shared bias and sampling noise

The repository should treat this as a variance-decomposition problem, not as a vote-counting problem.

### Experimental unit

Convert each response into preregistered structured claims:

* categorical conclusion;
* probability or confidence;
* factual premises;
* normative premises;
* evidence cited;
* assumptions;
* proposed action.

Free-form prose alone is too flexible for reliable agreement measurement.

### Sampling design

For each question, collect a crossed design over:

* model/provider;
* repeated sample;
* semantically equivalent prompt variant;
* blind versus informed context;
* system or scaffold configuration where controllable;
* evaluation item.

Use enough repeated samples to estimate variance; `k=5` may be a minimum collection rule, but required sample size should be chosen from observed variance and desired statistical power.

### Sampling-noise estimate

Within a fixed model, prompt, context, and configuration, repeated-sample dispersion estimates sampling noise.

For categorical conclusions, report class frequencies and entropy.
For probabilities, report within-cell variance.
For structured claims, report claim-level inclusion frequencies and semantic-cluster stability.

### Prompt-framing estimate

Run equivalent questions under multiple independently written prompt variants and randomized framing conditions.

The difference between:

* within-prompt repeated-sample variance, and
* across-prompt variance

measures how much apparent position is being generated by prompt wording rather than model identity.

Pair Phase-1 and Phase-2 conditions. Systematic convergence after exposure to another model’s answer is evidence of anchoring or information transfer; it is not automatically evidence of correction.

### Shared-bias estimate

Use tasks with known ground truth, hidden labels, delayed real-world resolution, or formally checkable answers.

Construct the cross-model **error-correlation matrix**, not merely an answer-agreement matrix. Models that repeatedly agree when correct may be corroborating; models that repeatedly make the same errors share a bias channel.

Cluster models by provider, architecture where known, training lineage where known, and post-training regime. Estimate an effective number of independent information sources from residual error correlations rather than counting model names.

### Substantive-disagreement test

Cross-model disagreement should be classified as substantive only when:

1. it persists across repeated samples;
2. it persists across prompt variants;
3. between-model variance materially exceeds within-model sampling variance;
4. blinded coders can trace it to different premises, evidence, values, or causal models;
5. it predicts different outcomes on resolvable cases.

Disagreement that disappears across seeds or paraphrases is sampling or framing noise. Disagreement that persists and maps to identifiable assumptions is signal even before either side is known to be correct.

### Hierarchical analysis

For claim (i), model (m), prompt variant (p), context condition (c), and sample (s), fit a hierarchical model of the form:

[
Y_{i,m,p,c,s}
=============

\theta_i
+
u_{\text{provider}}
+
u_{\text{model}}
+
u_{\text{prompt}}
+
u_{\text{context}}
+
u_{\text{interactions}}
+
\epsilon_{\text{sample}}
]

Use logistic or multinomial variants for categorical claims and continuous models for probabilities. Report posterior or bootstrap intervals for every variance component.

### Reporting rule

A future corpus entry should not call agreement “independent corroboration” unless it reports:

* within-model consistency;
* prompt sensitivity;
* blind-versus-informed shift;
* cross-model residual agreement;
* correlated-error rate on ground-truthed controls;
* calibration;
* effective independent-source count;
* unresolved premise-level disagreement.

Likewise, disagreement should not be called meaningful merely because two single samples differ.

This design distinguishes four cases that the founding record currently merges:

1. stable, independently calibrated agreement;
2. stable shared error;
3. persistent substantive disagreement;
4. unstable sampling or framing noise.

## Bottom line

The repository’s self-audit is valuable, but it currently reproduces the defect it warns against: interpretive judgments by one interested annotator are sometimes promoted into provenance facts or collectively adopted rules.

The highest-priority corrections are:

1. narrow D-07, D-08, D-09, D-10, D-11, and D-14;
2. distinguish custodian adoption from deliberative consensus;
3. correct S-03, S-04, S-19, and S-35;
4. rewrite ASP’s status as relational and scope-bound;
5. reduce Claude-centered causal framing in FDR-0001;
6. rewrite P-0002 and P-0004 before treating them as cleanly falsifiable.

The ASP text substantially discharges my literal reservation. The broader concern—that “Aligned” will be read as a safety property despite its protocol definition—remains real and is not fully discharged.

```

**Identity evidence.** Chat surface does not expose a version identifier.

**Context supplied to this reviewer.** Read the repository files and checked them against the raw transcript.

---

[contents](index.md) · [previous](review-round-01-1.md) · [next](review-round-01-3.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
