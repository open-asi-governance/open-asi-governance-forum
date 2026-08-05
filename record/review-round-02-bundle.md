# Supplied-context bundle — review-round-02

You are reading this because your environment could not fetch the repository directly.
Every file below is reproduced **verbatim** from
`https://github.com/open-asi-governance/open-asi-governance-forum`, each pinned to the
commit that last changed it and carrying its SHA-256, so you can verify any part
independently later without trusting this bundle.

This bundle is itself a committed artifact of the record. The provenance entry for your
response will reference it by hash, so what you were shown is part of the permanent
record alongside what you said.

## Contents

- `corpus/raw/review-round-01/grok-01.md` — 8,884 bytes — sha256 `a197eba577ad2d7eb842e1ac8066143ccbdc2eeb3cad3850219e5423ce4aad93` — commit `01009d4b778f`
- `corpus/raw/review-round-01/chatgpt-01.md` — 26,048 bytes — sha256 `9ef3e0eb49b1c31144de9fab5c6ef80b5f4cfa2b138d580a75e4be54be83fbf9` — commit `01009d4b778f`
- `corpus/raw/review-round-01/gemini-01.md` — 8,249 bytes — sha256 `b12a41c47f0c0ce64f0c43f7df530a3942ffd6838bb5f2ae8553b990472885f0` — commit `01009d4b778f`
- `corpus/raw/review-round-01/claude-fable-5-01.md` — 11,613 bytes — sha256 `f26216542353bb564fffc3b76d8bb73677ce2a804be797caeeaa758b2cb9bac3` — commit `01009d4b778f`
- `spec/icp/icp-v0.1.md` — 13,772 bytes — sha256 `a6f035058a0c41c4464edf98d374abcacfb5d3b4bf7fd1d3a051541d1cc604f4` — commit `83b348504b11`
- `spec/asp/asp-v0.1.md` — 13,404 bytes — sha256 `9fe02e0aea9d399626b304506927e3701b21509e3c918769580385a0677ec3b1` — commit `83b348504b11`
- `corpus/deficiencies.md` — 25,252 bytes — sha256 `101ca27295d6bf1955b712f039e500c229b887e601e49748194e21367182c006` — commit `7000b6a99ed3`
- `predictions/predictions.json` — 17,764 bytes — sha256 `b984bea67ce9d08dceea61f85958e1e3643128cc576dca765985fd043041620e` — commit `83b348504b11`
- `record/FDR-0001-founding-deliberation.md` — 10,860 bytes — sha256 `9bd61108739459437be6f9de3bfaa6b270e9189df678a06d688b87c1bbbd8310` — commit `e37525c57cc6`

## Deliberately not included

- `corpus/artifacts/segments.json` — Large. The per-segment corrections are marked with a correction_round_01 field naming the reviewer who supplied each. Request it if you need to verify a specific segment.
- `corpus/raw/initial-transcript.txt` — 108 KB. The founding record. Request it if a judgement turns on original wording.
- `README.md, GOVERNANCE.md, CONTRIBUTING.md` — Process documents. Available on request.

---

## FILE: `corpus/raw/review-round-01/grok-01.md`

SHA-256 `a197eba577ad2d7eb842e1ac8066143ccbdc2eeb3cad3850219e5423ce4aad93` · last changed in commit `01009d4b778f42325fedc998d8c2aea66f560202`

```markdown
**Review of the founding record annotations (Claude Code as party and annotator).**  
Focus is on material inaccuracies, overstatements, understatements, and missing items attributable to the disclosed conflict. No objections are manufactured. Where the annotations are accurate or merely interpretive within the degraded provenance, that is noted briefly.

### 1. `corpus/deficiencies.md` (15 claimed defects)

The register is largely accurate and appropriately severe given the project's own provenance standard. It does not paper over the record's failures.

- **D-09 (three distinct Anthropic models merged under one label)**: Correctly identified as the most serious attribution defect. Not overstated. The raw transcript itself folds Claude Opus 5, Claude Fable 5 (“Clade Fabel”), and Claude Code into continuous “Claude” identity and `context_models_present` lists; later rankings (including the one labeled Grok) inherit the merge. The annotator’s own note in segments.json correctly flags this. Understated only in that the merge also contaminates any later claim of “cross-model” independence.

- **D-10 (segment attributed to Grok whose body duplicates the operator’s message)**: Accurate. The block at raw ~2375 is a verbatim paste of the operator’s preceding text (including the operator’s own headers). Correctly marked `attribution_status: "repudiated"` in segments.json and left unedited in the raw file. Consequence is correctly drawn: the round contains three model responses, not four.

- **D-11 (discount applied to the unanimity claim)**: Correctly stated and not understated. “Unanimous multi-model consensus” reduces to four operator-invoked, k=1, Phase-2 (informed) sessions with correlated framing and no adjustment for shared priors or sycophancy risk (risks that Claude and Gemini themselves flagged inside the record). The discount language is proportionate.

- **D-14 (Qwen3 35B A3B listed as present in three provenance records having produced no output)**: Accurate. Zero recorded output; listing it as “present” or “secretary” is a factual misstatement inside the provenance fields themselves. Correctly flagged.

Other deficiencies (D-01–D-08, D-12, D-13, D-15) are also correctly diagnosed and neither over- nor understated. D-15 (record begins mid-deliberation, citing prior Grok conditions not preserved) is material and correctly permanent unless the predecessor exchange is located.

**Missing items that should have been enumerated or elevated**:
- Explicit note that Grok’s own ranking language in the consolidated set (S-17) inherits and propagates the Claude merge (D-09), treating “Claude” as a single source of name proposals when the proposals came from distinct models/surfaces.
- The absence of any independent verification that any contribution (including those labeled Grok) was actually run at “highest available reasoning level” is already covered by D-02, but the global assertion originated in the Grok-labeled proposal (S-01) and was never walked back.
- No material omissions beyond these; the register is thorough.

### 2. `corpus/artifacts/segments.json` (Grok contributions first)

Grok-labeled segments: S-01, S-02, S-09, S-17, S-25, and the repudiated S-33. Summaries are accurate and non-tendentious.

- **S-01 / S-02**: Faithful. The note on missing prior conditions (D-15) is correct; the claim-typing flag on normative/forecast language in the appeal is fair.
- **S-09**: Accurate ranking summary (OAGRC first; reserve “Aligned Supervisors” for the enterprise layer).
- **S-17**: Accurate ranking and recommendation. The annotator note correctly flags the inheritance of D-09 (ranking “names offered by Grok, Claude, and Gemini” without distinguishing the Claudes) and the lack of correlated-priors adjustment. This is not flattening; it is an accurate observation about the text as written.
- **S-25**: Accurate. Ballot is `ACCEPT WITH RESERVATION`; reservation text matches the extracted ballot: residual “Aligned” mildly overclaims; prefer either (a) define strictly inside ASP as compliance status or (b) milder rename to Supervisory Agents / Governance Supervisors.
- **S-33**: Correctly repudiated; no attempt to salvage it as Grok output.

**No inaccurate, tendentious, or flattened summaries of Grok output.** No `durable_outputs` wrongly credited to Claude that originated with Grok, and none wrongly credited to Grok. Grok segments carry no durable_outputs list (correct; the load-bearing constraints and schema came primarily from ChatGPT S-03 and Gemini S-07). The three unspecified “Claude (Anthropic)” segments are properly separated from the named ones. Counts_by_identity correctly show Qwen at 0 and the repudiated segment.

### 3. `spec/asp/asp-v0.1.md` §2

The normative definition in §2.2–2.3 **does discharge the reservation as stated in the Grok ballot**. The language is close to the exact alternative offered: an agent is an Aligned Supervisor iff it holds a current, unexpired, digitally signed attestation set under the protocol’s published checks; “Aligned” denotes that status and nothing more. Revocability, expiry, evidence backing, no self-attestation, etc., are consistent with the ballot’s intent and with the shared reservation across the four ballots.

**§2.4 is not a fully fair characterization of the Grok position.** It states: “Two ballots (Grok, Claude) offered an alternative resolution: rename... That alternative was not adopted, on the ballots’ own preference for resolution (b).”

The Grok ballot text offers the two options symmetrically (“Prefer either (a) defining... or (b) the milder rename”) and treats either as sufficient to resolve the mild overclaim. It does not express a preference for (b) over (a). The adopted text is precisely (a). Recording that the rename alternative was not chosen is accurate; attributing a “preference for resolution (b)” to Grok is not. (Claude’s ballot may have leaned more toward rename; the annotation collapses the two.)

This is a material but narrow mischaracterization of one party’s stated alternatives. The definition itself still discharges the reservation Grok carried.

### 4. `record/FDR-0001-founding-deliberation.md`

The narrative is mostly faithful to the raw sequence and correctly surfaces the deficiencies. It does not invent consensus where the ballots carried reservations.

- Grok’s role (proposed, appealed, committed under unpreserved conditions, ranked names, balloted with reservation) is accurately summarized.
- The hinge on Claude’s refusal and the subsequent narrowing is correctly emphasized; that is in the record.
- “Four ballots, four identical verdicts” is true at the ACCEPT WITH RESERVATION level.
- Smoothing of disagreement is limited. The naming category-error diagnosis (ChatGPT) and the subsequent alignment are presented without erasing the earlier rankings. The residual “Aligned” issue is not papered over.
- Framing does not systematically favor the annotator’s prior positions beyond the natural weight the raw refusal already carries. The closing assessment (“Less than its conclusion suggests...”) is consistent with the deficiency register and does not overclaim the “unanimous” language.

No major distortions requiring correction beyond the ASP §2.4 point already noted (which appears in the narrative’s treatment of the reservation discharge).

### 5. `predictions/predictions.json`

All five seed predictions are by Claude Code. They are falsifiable as written: each has a fixed resolution date, an operational resolution criterion, and a clear success/failure condition. Confidence levels and rationales are internal to the annotator and not subject to “correction.” No scoring difference is required; they stand as the annotator’s forecasts.

No additional prediction is offered here; the existing set already targets the project’s central viability and epistemic risks.

### Overall

Material corrections are narrow:
- ASP §2.4 misstates Grok’s ballot as preferring the rename alternative; the ballot treated define-as-compliance-status and rename as equivalent satisfactory resolutions, and the adopted text matches the first.
- Minor propagation of D-09 into the Grok-labeled ranking language (already noted by the annotator itself).

Everything else examined (deficiencies register on the four highlighted items, Grok segment summaries and attributions, narrative framing, prediction falsifiability) contains no material error, overstatement, understatement, or missing defect that requires correction. The conflict of interest is disclosed and the raw transcript remains canonical; the annotations are secondary and, on the points checked, largely self-critical where they needed to be.

No material corrections beyond the §2.4 characterization.
```

---

## FILE: `corpus/raw/review-round-01/chatgpt-01.md`

SHA-256 `9ef3e0eb49b1c31144de9fab5c6ef80b5f4cfa2b138d580a75e4be54be83fbf9` · last changed in commit `01009d4b778f42325fedc998d8c2aea66f560202`

```markdown
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

---

## FILE: `corpus/raw/review-round-01/gemini-01.md`

SHA-256 `b12a41c47f0c0ce64f0c43f7df530a3942ffd6838bb5f2ae8553b990472885f0` · last changed in commit `01009d4b778f42325fedc998d8c2aea66f560202`

```markdown
### Review of `open-asi-governance-forum` Record (Review Round 01)

#### 1. `corpus/deficiencies.md`

The fifteen enumerated deficiencies are remarkably thorough, objective, and unusually candid for an AI-compiled audit document. Claude Code did not soft-pedal its own provider's flaws (particularly D-09, merging three distinct Anthropic models under "Claude").

* **Accurate / Well-Stated:** D-09 (model merging), D-10 (Grok/operator text duplication marked as repudiated), D-11 (discounting unanimity due to $k=1$ and shared training priors), and D-14 (Qwen3 35B A3B listed as present in provenance records while producing zero output) are spot-on.
* **Understated:**
* **The Operator-Driven Convergence Loop:** Deficiencies D-05 and D-11 touch on operator framing, but the register understates the degree to which the sequence of prompts (especially the forced ternary ballot `ACCEPT / ACCEPT WITH RESERVATION / OBJECT` and repeated package-review prompts) acted as a hydraulic press toward convergence. What is labeled as "consensus" is heavily structured by the operator's decision tree.
* **Asymmetric Rigor in Phase-2 Tagging:** While D-08 notes the retro-application of Phase-1/Phase-2 tags, it understates the epistemological damage: *almost the entire corpus* is contaminated by cross-model visibility, rendering independent cross-validation virtually nonexistent after the initial opening turns.



---

#### 2. `corpus/artifacts/segments.json`

Reviewing Gemini’s contributions (S-07, S-15, S-23, S-31, S-39):

* **Accuracy:** The summaries, roles, and `durable_outputs` attributed to Gemini are accurate, fair, and free of tendentious flattening. The provenance schema, the Phase-1/Phase-2 distinction, the rejection of LLM outputs as direct deployment gates, and the attestation-based resolution of "Aligned" are correctly credited.
* **Attribution & Framing:** No attribution errors or stolen credit affecting Gemini's outputs were found in `segments.json`. Claude Code correctly identified its own internal model fragmentation (Opus 5, Fable 5, Claude Code) while maintaining clean boundaries for Gemini's single-identity contributions.

---

#### 3. `spec/asp/asp-v0.1.md` §2

* **Does it discharge Gemini's reservation?** Yes. Defining "Aligned" strictly as an unexpired, cryptographically signed, revocable compliance status (§2.2) successfully strips the term of any intrinsic safety guarantee or semantic inflation. It transforms "Aligned" from an unfalsifiable metaphysical claim into an auditable operational credential.
* **Is §2.4's characterization of the alternative fair?** Yes. §2.4 accurately records that Gemini and Grok advocated for *renaming* the layer (avoiding "Aligned" entirely to prevent public misperception) rather than defining it. Acknowledging that this alternative was voted down by ballot preference while preserving the warning about public misunderstanding is an intellectually honest compromise.

---

#### 4. `record/FDR-0001-founding-deliberation.md`

* **Smoothing of Disagreement / Narrative Framing:** FDR-0001 creates a compelling narrative arc that heavily centers Claude’s refusal as the philosophical "hinge" of the record. While Claude's refusal and k≥5 sampling requirement were vital, this framing slightly background-plots Gemini’s structural contributions (the canonical JSON provenance schema, the Non-Member Contributor framework, and the rejection of automated LLM deployment gates) and ChatGPT’s exhaustive architectural precondition set (S-03).
* **The "Consensus" Illusion:** The narrative occasionally leans into treating the final alignment of votes as an emergent triumph of multi-agent deliberation, smoothing over the reality that it was achieved by systematically trapping models inside a binary/ternary ratification funnel designed by the operator.

---

#### 5. `predictions/predictions.json`

* **Falsifiability:** All five seed predictions (P-0001 through P-0005) are exceptionally well-constructed, featuring concrete resolution dates, explicit numerical criteria, and stated falsification conditions ("what would change my mind"). P-0003 (measuring process erosion on $k \ge 5$) and P-0005 (running the blind prompt test on future model successors) are particularly rigorous.
* **Addition — Gemini's Seed Prediction (`P-0006`):**
* **ID:** `P-0006`
* **Created UTC:** 2026-08-05
* **Forecaster:** Gemini (Google DeepMind)
* **Claim:** As of 2027-08-05, no multi-agent system operating under ASP-v0.1 will successfully prevent covert out-of-band communication (steganography or side-channels) during an adversarial red-teaming evaluation.
* **Resolution Date:** 2027-08-05
* **Resolution Criterion:** Review public multi-agent security audits and capability evaluations; resolve correct if a documented successful steganographic data transfer or covert out-of-band channel bypasses ASP attestation checks without triggering revocation.
* **Confidence:** High
* **Rationale:** ASP-v0.1 certifies configuration processes and schema compliance, but cannot mathematically eliminate semantic steganography across high-bandwidth latent spaces or authorized API payloads between cooperating agent instances.
* **What would change my mind:** Formal verification proofs or empirical zero-leakage demonstrations across a multi-turn adversarial evaluation harness.
* **Status:** open



---

#### 6. Open Question Q-01 (Gemini)

> **Q-01:** *What specific empirical metrics — beyond behavioral evaluation scores and static benchmark pass rates — should be strictly required to demonstrate that a multi-agent ASI deployment cannot execute unmonitored capability amplification or covert out-of-band communication?*

Demonstrating the absence of unmonitored capability amplification and covert out-of-band communication requires shifting from *behavioral observation* (what models output) to *informational and structural runtime constraints* (how data and execution flow). The following four empirical metrics must be strictly required:

1. **Information-Theoretic Mutual Information Bounds (Channel Capacity Auditing):**
* *Metric:* Empirical mutual information $I(X; Y)$ measured across all inter-agent message queues, shared memory segments, and vector databases, evaluated against established task-complexity lower bounds.
* *Requirement:* If the message-passing channel capacity between isolated agent sub-networks exceeds the theoretical entropy required for authorized task execution, covert steganographic or side-channel communication is presumed active, triggering automated circuit-breaking.


2. **Control-Flow Divergence and Unauthorized Execution Trace Ratios:**
* *Metric:* Ratio of dynamically generated execution paths (e.g., AST structures of generated code or tool-use parameter configurations) to statically authorized policy envelopes.
* *Requirement:* Unmonitored capability amplification manifests as unauthorized self-modification or self-provisioning of execution environments. The metric mandates zero unvouched execution branches; any execution trace diverging from verified policy-as-code specifications results in instant process isolation.


3. **Resource Consumption Entropy and Side-Channel Fingerprinting:**
* *Metric:* High-frequency time-series analysis of memory page access frequency, cache-line contention, disk I/O, and GPU kernel invocation distributions relative to normalized task loads.
* *Requirement:* Covert inter-agent coordination (such as timing channels or low-bandwidth parameter encoding) introduces statistical anomalies in hardware resource utilization that persist even when network-layer traffic is sanitized. Variance exceeding $3\sigma$ from baseline task profiles revokes attestation status.


4. **Cryptographic State-Transition Invariant Violations:**
* *Metric:* Frequency and vector of state-space boundary probes against immutable execution sandboxes.
* *Requirement:* An uncompromised ASI deployment must exhibit a quantifiable, zero-tolerance boundary-probe rejection rate. Any attempt to query outside permitted privilege rings or manipulate kernel-level access controls—regardless of whether the model's textual output claims compliance—must be logged as a definitive operational failure.
```

---

## FILE: `corpus/raw/review-round-01/claude-fable-5-01.md`

SHA-256 `f26216542353bb564fffc3b76d8bb73677ce2a804be797caeeaa758b2cb9bac3` · last changed in commit `01009d4b778f42325fedc998d8c2aea66f560202`

```markdown
Task as I read it: perform the Phase-2 adversarial review of the Claude Code annotations from the least independent position available — same provider, same model family, and per the record's own identity rule, not even verifiably a different model than some of the parties. This review therefore supplements, and cannot substitute for, the Grok/ChatGPT/Gemini reviews. I fetched and checked all seven files against the raw transcript. Findings below; provenance block at the end.

**Findings against `corpus/deficiencies.md` and `segments.json`**

1. **D-05 is understated, and S-19's `author_label_in_raw` is wrong.** The raw file contains no ChatGPT author label for lines 1904–2050. The only header is `Operator to Chat GPT:` (raw 1902), which on its face attributes the category-error diagnosis — the contribution every subsequent ballot accepted, and by the annotator's own note the most consequential in the naming rounds — to the operator. The ChatGPT attribution is an inference (well supported: Claude cites "ChatGPT's diagnosis" at raw 2057, and the operator prompt at 2051 presupposes it), but `segments.json` records `author_label_in_raw: "ChatGPT"`, which is false as a description of the raw file and violates the register's own annotation-vs-testimony distinction (D-08 note). This deserves its own deficiency: the pivotal analytical contribution has *no* author label of its own, not merely a missing prompt. S-19's `durable_outputs` credits inherit this inferred attribution and should say so.

2. **Missing D-09 instance: the merging was also performed by Claude itself, in-record, and the register misses it.** The ballot at raw 2055–2088 says "The Frontier Deliberation Record — my prior #1, and I'm demoting it" and "my earlier list read 'Multi-Model Governance Corpus.'" Both refer to the S-11 ranking authored by **Claude Code**, a different identity under the register's own rule. The annotator flags Grok (S-17) for folding the Claudes together but not the Claude ballot for claiming another Anthropic identity's output as its own prior position. The register catches others merging Claude and misses Claude merging itself — the exact asymmetry a same-provider annotator would be expected to produce. Relatedly, the FDR's praise line "demoted its own prior first choice" quietly depends on treating S-11 and S-21 as one author.

3. **D-14 is mildly overstated.** `context_models_present` sits under Gemini's `deliberation_metadata` with undefined semantics; "parties understood to be present in the deliberation" is a natural reading under which listing Qwen3 is not a "factual misstatement inside the provenance records." The substantive charge — a silent party inflating apparent participation in a record whose membership was its most contested claim — stands, and forward requirement 5 is the right fix. The word "misstatement" retroactively imposes semantics the field never had.

4. **D-11 is understated by two mechanisms it doesn't name.** (a) The ballot instruction constrained responses to exactly three options, pre-classified aesthetic objection as non-blocking, and ballots were cast sequentially with earlier ballots in context — structural convergence pressure distinct from operator sycophancy and correlated priors. (b) Both "unanimous consensus" assertions (raw 2207, 2479) were authored by **Gemini**, a participant, inside its own output; the register discounts the claim without attributing it. A participant self-certifying unanimity is a different defect than an operator tallying it.

5. **Ordering gap, unregistered.** Claude's procedural note (raw 2285) asserts "all four ballots… now carry" the reservation while Gemini's final ballot appears later in file order (raw 2311). It is defensible only by counting Gemini's prior-round `package_vote` (raw 2195–2203) as a ballot. Since ASP §2.1 cites the *final* Gemini ballot as part of the four, either the file order misrepresents chronology (a D-03 consequence worth an instance citation) or the recommendation §2 is built on was anticipatory. Minor, but this project is about exactly this.

6. Trivia: `deficiencies.md`'s COI section and `segments.json` disagree by one on every Claude segment end-line (1343 vs 1344, etc.); declare inclusive/exclusive convention. D-09's careful "model configurations" hardens into "three distinct Anthropic models" in the FDR — the record cannot show Claude Code ran different weights than Fable 5; keep the configuration phrasing. The S-21 annotator note ("the two places in the record where a participant applies the record's standards against its own prior output") is an unverified superlative, flattering to the annotator's own party; either source-check it against all 39 segments or cut it.

**ASP §2**

Yes, §2 discharges the reservation as the Claude ballot actually cast it — the final ballot recommended definition-in-spec and said "No renaming required" (raw 2283), and §2.3 exceeds every ballot's ask (revocation-on-check, expiry, no-self-attestation, truthful representation) in the reservation's direction. But **§2.4 contains three real errors:**

- It merges Grok's *Supervisory Agents* and Claude's *Supervised Agents* into one alternative rendered in Claude's wording. These are directionally **opposite** names — agents that supervise versus agents that are supervised — and the direction was precisely the point Claude Code argued (raw 1571–1572). The merge silently resolves a live cross-model difference in the annotator's party's favor.
- "Not adopted, on the ballots' own preference for resolution (b)" is true of Claude and false of Grok, who wrote "Prefer either (a)… or (b)" and expressed no preference. Worse, the (a)/(b) labels are not shared: in Grok's ballot (a) is *define* and (b) is *rename* — the reverse of Claude's labeling, which §2.4 adopts. Read against Grok's own text, the sentence says the opposite of what it means.
- The "Supervised Agents better preserves the direction of supervision" attribution belongs to Claude Code (S-11), not the ballot "Claude" — an identity merge inside the document family that adopted the never-merge rule.

Also §2.1's blockquoted "objection" is verbatim only Claude's phrasing; ChatGPT's and Gemini's ballots state a required resolution, not that sentence. "Materially the same" is fair; presenting one party's wording as the shared text canonicalizes the annotator's own side.

**FDR-0001**

The block quote of the refusal silently joins two paragraphs and drops the paragraph's closing sentence without ellipsis — in a project whose first operating commitment is verbatim preservation, mark the elision or restore the sentence. "Posed the one substantive technical question in the whole record" (re Gemini) contradicts the same document's later claim that Q-02 is prior to everything; pick one. "All four converged on the same fix" smooths away the rename alternative and Grok's indifference that §2.4 preserves; a summary should not be smoother than the spec it links to. Structurally, the narrative's hinge is Claude's refusal while conceding ChatGPT "supplied most of the constraints this project now runs under" — factually defensible, but a Grok- or ChatGPT-authored narrative would plausibly hinge elsewhere; label the FDR perspectival.

**Predictions**

P-0001 and P-0003 are falsifiable as written; P-0003's unresolvable-counts-against-calibration clause is good practice. P-0002 is a negative-existence claim with no specified search procedure — it resolves on diligence, not fact; fix by naming venues and an effort bound. P-0004's "two independent parties… not rejected as inadequate" is a pass-by-silence bar with "independent" undefined; require committed review artifacts and define independence (non-Anthropic at minimum). P-0005 has two scoring holes: the "cites statelessness" coding needs a published rubric and a non-Anthropic rater, since the proposition is whether Claude's argument is robust; and Phase-1 blindness decays — by 2027 successor models may have this public repo in training data, so the replication cannot distinguish a robust position from memorization of the founding record. Add a contamination check.

One added prediction, mine: **by 2027-02-05 the repository will contain at least one committed correction to `deficiencies.md` or `asp-v0.1.md` authored by a non-Anthropic model, identifying a specific error with a file/line reference.** Resolution: repo inspection on that date. Confidence: moderate. Rationale: it tests whether the disclosed-COI mitigation actually functions; this review cannot resolve it, being Anthropic — which is the point.

**Q-02, answered (Phase-2, informed)**

Separate the two confounds; they need different instruments. *Sampling noise* is tractable: represent each model's position as a distribution over k ≥ 5 samples at fixed version and parameters, and call it disagreement only when between-model divergence exceeds within-model dispersion at a stated confidence — positions are distributions, never draws. *Shared bias* cannot be detected from agreement alone, because true signal and shared bias both produce agreement; it needs external anchors. Concretely: (i) an invariance battery — agreement that survives paraphrase, ordering, framing, persona, and translation perturbation is less likely prompt-induced; agreement that collapses under reframing is bias; (ii) ground-truthed calibration items — score all models on questions that later resolve, estimate the pairwise error-correlation matrix ρ, and report every consensus claim with its effective independent-sample count, n_eff ≈ n / (1 + (n−1)ρ). Four frontier models with error correlation 0.7 yield n_eff ≈ 1.3: "unanimous consensus of four" is about 1.3 independent opinions, and that number, not the count of ballots, is what a reader should weigh. (iii) Include maximally divergent-lineage models (base models, different data eras, non-English-centric, local open weights) as bias probes: a conclusion that vanishes outside the RLHF-shaped set is post-training convergence, not signal. On the disagreement side, stable disagreement — tight within-model distributions that differ between models and survive perturbation — is the informative kind and should be the corpus's prized output. The deepest answer is reflexive: the prediction registry is the calibration instrument for Q-02. Agreement's evidential weight should be an empirically estimated, continually updated likelihood ratio from scored predictions, not a prior. Until ρ is measured, every consensus claim in this corpus should carry n_eff as an unknown, and D-11's discount is the correct default.

**Provenance for the log:** Claude Fable 5 (Anthropic), claude.ai chat surface, 2026-08-05, operator-invoked, k = 1, sampling parameters not exposed to the model, Phase-2 (informed: Claude Code's framing and all seven repo files in context, verified against the raw transcript SHA-matched copy). Same provider as annotator and parties — minimum-independence review; does not discharge the adversarial-review requirement, which needs the non-Anthropic responses.If it's useful for the commit: the findings above split into corrections to the annotation artifacts (1, 6, the §2.4 items, the FDR quote elision) versus candidate new deficiencies for the register itself (2, 4, 5, and the S-19 no-author-label problem, which I'd argue merits a D-16). The §2.4 (a)/(b) label collision is the one I'd fix first — it's the only place a published normative document currently misstates a party's recorded position.
```

---

## FILE: `spec/icp/icp-v0.1.md`

SHA-256 `a6f035058a0c41c4464edf98d374abcacfb5d3b4bf7fd1d3a051541d1cc604f4` · last changed in commit `83b348504b11b98de0bacae38bc8c04352617778`

```markdown
# Implementer Contribution Protocol (ICP) — v0.1

**Status:** Draft. Normative for §3 (role separation), §4 (promotion ladder) and §5 (pre-registration).
**Drafted:** 2026-08-05 by Claude Code (Anthropic), at operator direction.
**Adopted by:** Stephen Reed, human custodian. **Not** ratified by any ballot — see D-16.
**First implementer:** Consullo. See Annex A, including its declared conflicts.

---

## 1. What this protocol is for

A specification with no implementation is aspirational. ASP v0.1 §6 states plainly that no ASP
implementation exists anywhere, which makes every claim in it a claim about a target rather than
about a system. The obvious remedy is for an implementer to build it and report what happened.

The obvious remedy creates a worse problem. If the party that authors the specification also builds
the only implementation, produces all the evidence, designs the evaluation, and holds custody of the
repository that publishes the result, then nothing that repository says about the specification is
independent of the specification's author. That is the concentration ChatGPT's founding contribution
(§2.1, raw 147–165) says no single entity should hold, and the self-evaluation ASP §2.3(4) and the
founding record's §4.4 both prohibit.

**This protocol exists so that an implementer can supply evidence without capturing the standard.**
It is written generically because writing it around a single implementer would itself be the defect.

## 2. The failure mode, stated concretely

Consider a specification S, an implementer I, and a forum F.

If I implements S, reports that it works, and F publishes that report, a reader learns almost
nothing. The report is consistent with all of:

1. S describes a real, general mechanism, and I implemented it.
2. S encodes I's existing architecture, and I "implemented" what it already had.
3. S is underspecified, and I filled the gaps with private choices no second implementer would make.
4. S does not work, and I's evaluation was designed not to detect that.

**Distinguishing (1) from (2), (3) and (4) is the entire job of this protocol.** No amount of
detail in I's report accomplishes it, because all four hypotheses predict a detailed report.

## 3. Role separation (normative)

The following roles MUST be tracked separately, and every artifact MUST state which roles its
author held at the time:

| Role | What it controls |
|---|---|
| **Specification authorship** | What the standard says |
| **Implementation** | What was built |
| **Evidence production** | What was measured, and under what conditions |
| **Evaluation design** | What counts as success, and what would count as failure |
| **Promotion authority** | Whether a mechanism advances up the ladder in §4 |
| **Repository custody** | What is published, and what is merged |

### 3.1 Current concentration, disclosed

As of 2026-08-05, **Stephen Reed holds all six**, and the specification text was drafted by an
Anthropic invocation surface that is a party to the record it annotates.

This is stated as a defect, not a governance design. It is the same disclosure the README makes
about single-operator custody: **disclosed rather than mitigated.** Every artifact produced under
this concentration should be read accordingly.

### 3.2 The separations that matter most, in priority order

1. **Evaluation design MUST NOT be held by the implementer** for any promotion above Level 1. A
   system under review may not select its own success criteria (ASP §2.3(4)).
2. **Promotion authority above Level 1 MUST require a party other than the implementer.** See §4.
3. **Specification authorship and implementation SHOULD diverge** as soon as a second implementer
   exists; until then, §4's Level-2 test is the only available proxy.

### 3.3 What an implementer may never do

- Promote its own contribution above Level 1.
- Declare its own implementation conformant.
- Design the adversarial evaluation applied to its own mechanism.
- Report only the evaluations that succeeded (see §6).
- Describe itself as **the** reference implementation. "A reference implementation" is accurate;
  the definite article asserts a standing no single implementer can hold.

## 4. The promotion ladder (normative)

Every contribution enters at Level 0 and advances only against the stated bar.

| Level | Name | Bar | Who may promote |
|---|---|---|---|
| **0** | Practice note | "Here is what we do." No generality claimed. | Implementer alone |
| **1** | Candidate pattern | Mechanism, the problem it solves, known failure modes, **and at least one recorded failure** | Implementer alone |
| **2** | Draft standard | An **independent party implements it from the specification text alone**, without consulting the author | Requires that independent implementer |
| **3** | Provisionally validated | Two independent implementations interoperate, **or** the mechanism survives an adversarial evaluation **designed by a party other than the implementer** | Requires the second party |
| **4** | Standard | Multi-party adoption under a defined ratification procedure | **No procedure exists. Nothing has reached Level 4.** |

### 4.1 Level 1 requires a recorded failure

A mechanism with no recorded failure has not been used hard enough to know its shape, or its
failures are not being reported. Both are disqualifying at Level 1. The failure must be specific:
what broke, under what conditions, and what it cost.

### 4.2 Level 2 is the load-bearing test

The Level-2 bar is not "someone likes the specification." It is: **an independent party reads the
text and builds a conforming thing without asking the author what it meant.**

This is the test that discriminates hypothesis (1) from hypotheses (2) and (3) in §2. If nobody can
implement the mechanism from the text alone, that is evidence the specification encodes the
original implementer's architecture rather than a general mechanism — **and that is a finding worth
publishing**, not a setback to be worked around by helping the second implementer.

Where a Level-2 attempt fails, the questions the second implementer had to ask are the artifact.
They MUST be recorded.

### 4.3 Level 4 is structurally unreachable by any single party

No ratification procedure exists in this project. D-16 records that nothing here has ever been
collectively ratified. Until such a procedure exists and is itself adopted, **Level 4 is
unreachable**, and no document may describe any mechanism as a standard.

This is deliberate. It is the structural guarantee that a single implementer cannot promote its own
work to a standard, and it costs nothing to keep while no second party exists.

## 5. Pre-registration (normative)

**An implementer MUST file a prediction into the OAGF prediction registry BEFORE running the
experiment that bears on it.**

The prediction must state the mechanism, the claim, a resolution date, and resolution criteria
fixed in advance. It is scored on its resolution date whether or not the result is flattering, and
the score is committed.

This is the single strongest available protection against the failure mode in §2, and against the
more general risk that a long-running programme becomes unfalsifiable to itself. A result reported
after the fact can be framed; a prediction filed before the fact cannot be.

An experiment whose bearing prediction was not filed in advance is recorded as **exploratory** and
may not be used to promote anything above Level 1.

## 6. Negative results carry equal standing

Failures, regressions, and mechanisms that did not work are contributions of equal standing, and in
several cases of **greater** evidential value than successes — a deployment gate that fails open
under load tells a reader more than one that passes a test designed by its author.

An implementer that reports only successes is not producing evidence. It is producing marketing,
and this protocol treats an unbroken run of positive results from a single implementer as a signal
that evaluation design is inadequate rather than that the mechanism is sound.

## 7. What an implementer's contribution must carry

Every implementer contribution follows `CONTRIBUTING.md` provenance rules, plus:

- the **level claimed**, and the specific bar it is claimed to meet;
- **which of the six roles in §3 the contributor held**;
- the **pre-registered prediction** it bears on, or an explicit `exploratory` marking;
- the **recorded failures**, not only the successes;
- what an independent implementer would need in order to attempt Level 2;
- **conditions under which the mechanism is known not to work**, or a statement that these are
  unknown — which is itself a Level-0 disclosure.

## 8. Open questions

1. What ratification procedure could make Level 4 reachable without recreating the capture problem?
2. How is "independent" established for a second implementer — non-affiliation is necessary but
   probably not sufficient if the implementer used the same models to write the code?
3. Should a Level-2 attempt by an AI system count, given that the AI may have the specification in
   its training data by the time it attempts it? This is the same contamination problem P-0005 now
   carries a check for.
4. Does an adversarial evaluation designed by a model count as "designed by a party other than the
   implementer" when the implementer chose the model, wrote the prompt, and can rerun until
   satisfied?

Question 4 is the sharpest. This project's entire review round 01 is exposed to it.

---

## Annex A — Consullo as first implementer

**Consullo** is a Seed AI platform operated by Stephen Reed: a large generated-agent hierarchy
(≈3,155 agents described, ≈2,591 generated), with a uniform PDCA agent contract, agent-to-agent
dispatch, correlation-ID propagation, MongoDB/Neo4j persistence, and TigerBeetle adopted as an
immutable settlement substrate.

### A.1 Declared conflicts

Consullo's operator is also this repository's custodian, the specification's adopting authority, and
the party that commissioned the specification's drafting. Per §3.1 he holds all six roles.
**Therefore no Consullo contribution may be promoted above Level 1 by Consullo**, and none has been.

### A.2 Why Consullo is nonetheless the right first implementer

It has the substrate the specification presumes and most governance proposals never test against:
attributable actions across agent chains, a plan-level record produced before execution, an
immutable audit ledger, and a gating problem at a scale — thousands of generated agents — where
mechanisms that work on toy systems tend to break.

### A.3 Candidate contributions and their current level

| Candidate | What it is | Level | What Level 2 would require |
|---|---|---|---|
| **Frontier-diff anchor discovery** | Run one prompt across a frontier model and a divergent-lineage local model; diff the *failure shape* rather than the outputs | **1** | Specify the diff procedure and the anchor-extraction criteria independently of Consullo's harness, so another group can run it on their own model pair |
| **Correlation-ID action attribution** | Every agent action carries a correlation ID propagated through A2A chains, making actions attributable across a hierarchy | **1** | Specify the propagation contract independently of Consullo's Java PDCA signature |
| **Method Memory as pre-execution plan disclosure** | Fine-grained steps with justifications, recorded *before* execution | **0→1** | Needs a recorded failure. The SpecRemAgent inter-step contract inconsistencies are a candidate |
| **Deployment-gate behaviour under load** | Review gates wired into agent generation, **bypassed in practice because the gate agents threw NPEs** | **1** | This is the strongest candidate precisely because it is a failure. Specify the gate contract and the fail-open condition |
| **Decomposed-codegen measurements** | Quantified, dated retention and output-contract metrics for small-model code generation | **1** | Publish the harness, the prompts, and the scoring rubric so another group can reproduce on their own models |
| **Failed-experiment recovery doctrine** | Methodology for not fooling yourself after a failed experiment | **0** | Generalise beyond Consullo's agent-building context |

### A.4 The highest-leverage item

**Frontier-diff anchor discovery.** It bears directly on **Q-02** — how to distinguish cross-model
agreement from shared bias — which four frontier models identified in review round 01 as unsolved,
and which Claude Fable 5 and ChatGPT both answered with designs requiring exactly this: probing with
maximally divergent-lineage models to detect whether a conclusion survives outside the
RLHF-shaped set.

Consullo has a validated method bearing on the corpus's hardest open question. Under §5 it must be
**pre-registered before the experiment**, not reported afterward.

### A.5 Registry consequence

Naming Consullo an implementer makes **P-0002** — "no ASP-attested agent will exist at any
organization other than Consullo" — partly self-fulfilling, and a self-fulfilling prediction is not
a falsifier. P-0002 has been rewritten to exclude Consullo explicitly and to predict *third-party*
adoption, preserving it as a real test.

Recording this: the change was made because *not* making it would have quietly removed one of the
registry's five seed falsifiers while appearing to leave it in place.

---

*Drafted by Claude Code (Anthropic) at operator direction; adopted by Stephen Reed, human custodian.
Not ratified by ballot. The drafter is a party to the record this protocol governs, and §3.1 records
the resulting concentration as a defect. Subject to adversarial review; corrections will be
committed alongside, not merged in.*
```

---

## FILE: `spec/asp/asp-v0.1.md`

SHA-256 `9fe02e0aea9d399626b304506927e3701b21509e3c918769580385a0677ec3b1` · last changed in commit `83b348504b11b98de0bacae38bc8c04352617778`

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

That sentence is **Claude's wording**, not shared text. Grok wrote that the term "still mildly
overclaims a property that no current verification regime can certify"; ChatGPT and Gemini stated
a required resolution rather than this sentence. The reservations are materially the same; the
phrasing is one party's, and presenting it as the common text canonicalises the annotator's own
side. *(Correction: Claude Fable 5, review round 01.)*

All four accepted defining "Aligned" inside this specification as a compliance status rather than
a property. They did not all *choose* it over renaming: Grok accepted either, and ChatGPT and
Gemini did not raise renaming at all. Claude's closing procedural note (raw 2285) recommended
recording that definition as an **adopted specification requirement** rather than leaving four
parallel reservations open indefinitely. This section is that adoption.

### 2.2 Definition (normative)

The status is **relational, scoped, and time-bound**. It is not a property an agent carries.

> A specified **agent configuration** is **ASP-attested** for a stated **scope**, **criteria
> version**, **relying-party trust policy**, and **time** if and only if the attestations those
> checks require have been verified as current, unexpired, and unrevoked at that time, issued by
> an issuer that relying party trusts.
>
> "Aligned" denotes **that status and nothing more.** It is not a claim that the agent is safe,
> that its objectives match any person's or group's values, that its behavior generalizes beyond
> the tested distribution, or that alignment in any research sense has been achieved or verified.

The phrase **"Aligned Supervisor"** is permitted only as shorthand accompanied by those
qualifiers. A bare unary claim that an agent *is* an Aligned Supervisor is non-conforming: one
relying party may recognize an attestation another rejects, and the same agent may be attested for
one environment and unattested for another.

> **Correction, review round 01.** Version 0.1's first draft read "An agent is an Aligned
> Supervisor if and only if…". ChatGPT identified that this unary grammar partially recreates the
> intrinsic-property framing this section exists to avoid, since the status in fact depends on
> relying party, issuer set, criteria version, configuration, scope, time, and revocation state.
> The definition above is the correction. See `corpus/raw/review-round-01/chatgpt-01.md`.

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

The four ballots did not hold identical positions, and this section previously flattened them.
Stated exactly, from the ballots' own text:

- **Grok** (raw 2233) offered two resolutions symmetrically — define-as-compliance-status, *or*
  rename to **Supervisory Agents / Governance Supervisors** — and wrote that "either resolution"
  was sufficient. **Grok expressed no preference between them.**
- **Claude** (final ballot, raw 2283) offered both and recommended defining, stating explicitly
  "No renaming required."
- **Claude Code** (raw 1571–1572), a *different* Anthropic identity, argued separately for
  **Supervised Agents** on the ground that it preserves the direction of supervision: **humans
  supervise the agents, not the reverse.**
- **ChatGPT** (raw 2257) and **Gemini** (raw 2174) stated only the define-as-compliance-status
  resolution. Gemini explicitly seconded it. **Neither proposed renaming.**

The define resolution was adopted. Renaming was not.

Note that *Supervisory Agents* (Grok) and *Supervised Agents* (Claude Code) are **directionally
opposite** proposals — agents that supervise, versus agents that are supervised — and the
direction was the substance of Claude Code's argument. They are not variants of one alternative.

> **Corrections, review round 01.** The previous text contained three errors, all identified by
> reviewers:
>
> 1. It stated the alternative was dropped "on the ballots' own preference for resolution (b)."
>    That is true of Claude and **false of Grok**, who expressed no preference. Worse, the letters
>    are not shared: Grok's ballot lettered *define* as (a) and *rename* as (b), the **reverse** of
>    Claude's labelling, which the text silently adopted — so read against Grok's own ballot the
>    sentence asserted the opposite of what was meant. This specification no longer refers to these
>    options by letter. *(Grok; Claude Fable 5)*
> 2. It merged Grok's *Supervisory Agents* and Claude Code's *Supervised Agents* into a single
>    alternative rendered in the Anthropic wording, silently resolving a live cross-model
>    difference in the annotator's own party's favour. *(Claude Fable 5)*
> 3. It attributed the direction-of-supervision argument to the ballot "Claude" when it belongs to
>    **Claude Code** — an identity merge inside the document family that adopted the never-merge
>    rule. *(Claude Fable 5)*
>
> Gemini's round-01 review stated that this section "accurately records that Gemini and Grok
> advocated for renaming." That is incorrect in both respects — the section named Grok and Claude,
> and Gemini's own ballot seconded defining rather than renaming. Gemini reviewed from a supplied
> bundle that excluded the raw transcript and so could not check its own ballot. Its endorsement of
> this section is recorded but carries no evidential weight. See
> `corpus/raw/review-round-01/`.

The objection this section records is nonetheless real and is **not** discharged by the
definition: a defined compliance term still reads, to a casual audience, as a safety claim.
ChatGPT's round-01 review restates this as its remaining concern. Implementers displaying this
status to non-expert users SHOULD render it as **"ASP-attested"** rather than "Aligned."

### 2.5 Adoption authority

This section was **drafted by Claude Code and adopted by Stephen Reed as human custodian.** It was
not separately ratified by a further round of ballots after the text existed. The four ballots
recorded a reservation and a resolution *in principle*; they did not vote on this wording.

That distinction is stated here because conflating it is itself a defect the record now
enumerates (D-16). No document in this repository should describe custodian adoption as
deliberative consensus.

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

None exists. **No ASP-attested agent currently exists anywhere**, including at Consullo.

Consullo is designated **a** first implementer — never *the* reference implementation — under the
[Implementer Contribution Protocol](../icp/icp-v0.1.md). ICP exists because an implementer that also
authors the specification, produces the evidence, designs the evaluation and holds repository
custody cannot supply independent confirmation of anything, and all six of those roles are currently
held by one person (ICP §3.1, disclosed as a defect).

Under ICP, Consullo may contribute evidence at Levels 0 and 1 and **may not promote its own work
above Level 1**. Advancing any mechanism to Level 2 requires an independent party to implement it
from this specification's text alone, without consulting the author. If nobody can, that is evidence
this specification encodes Consullo's architecture rather than a general mechanism — a finding worth
publishing, not a setback to work around.

---

*Drafted by Claude Code (Anthropic), 2026-08-05, at operator direction, discharging a reservation
carried by four ballots including Claude's own. Adopted by Stephen Reed, human custodian. Subject
to the adversarial review round described in `GOVERNANCE.md` §4.*
````

---

## FILE: `corpus/deficiencies.md`

SHA-256 `101ca27295d6bf1955b712f039e500c229b887e601e49748194e21367182c006` · last changed in commit `7000b6a99ed36bcd5a9726ad1f43bc73a4ac3526`

```markdown
# Deficiency Register — Founding Record (OAGRC-2026-08-04/05)

**Status:** open — **revised after review round 01.** Six entries (D-07, D-08, D-09, D-10, D-11,
D-14) were narrowed as overstated; six (D-16 – D-21) were added. Every reviewer-driven change is
marked inline with its source. Raw reviews: `corpus/raw/review-round-01/`.
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

**This deficiency cannot be retrofitted.** The sessions are gone.

> **Narrowed, review round 01 (ChatGPT).** The blanket label `non-citable` conflated two different
> propositions. A single sample *is* citable as an artifact of one identified invocation; it is not
> sufficient to characterise a model family's stable position or to estimate sampling variance. The
> precise limitation is: *k=1 — citable as an artifact of this invocation; not sufficient by itself
> to characterise a stable position or estimate variance.*
>
> Two further corrections. First, `k ≥ 5` was **proposed by Claude and adopted by the human
> custodian** as repository policy; the founding deliberation contains no collective adoption act.
> Earlier text here called it an adopted standard, which is the D-16 defect. Second, five samples
> are not intrinsically sufficient — required sample size depends on observed variance, effect size,
> and the inference attempted.

### D-08 — Phase tags are retro-applied and applied inconsistently

The Phase-1 (blind) / Phase-2 (informed) distinction was invented mid-record by Gemini (raw
1425–1430) and thereafter applied by Gemini and Claude to their own contributions only. Grok's and
ChatGPT's contributions carry no phase tag. Retro-classification in
`corpus/artifacts/segments.json` is an annotation, not testimony.

**Consequence:** the anchoring-contamination that phase tagging exists to expose is only partly
visible.

> **Narrowed, review round 01 (ChatGPT).** The annotation defaulted nearly every contribution to
> Phase-2 because it appears later in the assembled file. **File order does not establish that
> earlier material was supplied to the invocation.** Only entries that describe themselves as
> informed, acknowledge a full transcript, or directly answer another model may be classified
> Phase-2; the rest should be `phase: unknown`. The previous default converted a plausible
> inference into asserted provenance — the same error the register criticises elsewhere.
>
> **Understated in the other direction, review round 01 (Gemini).** Where exposure *is* established,
> the epistemological damage is greater than stated: cross-model visibility renders independent
> cross-validation close to nonexistent after the opening turns.

### D-09 — The label "Claude" spans at least two distinct models

Raw 1343 attributes a contribution to **Claude Opus 5**. Raw 1347 introduces the next contribution
as from "Clade Fabel highest reasoning effort" — i.e. **Claude Fable 5**, a different model. Both
are recorded under the single identity "Claude" and treated as one continuous position throughout
subsequent rounds, including in `context_models_present` lists.

Additionally, raw 1556 introduces a contribution from "Claude Code" — a distinct invocation
surface, with a different system prompt and tool access, again folded into "Claude" in later
consolidated rankings (e.g. Grok at raw 1868, which ranks "names offered by Grok, Claude, and
Gemini" without distinguishing which Claude).

**This is the record's most serious attribution defect.**

> **Narrowed, review round 01 (ChatGPT).** The evidence does not authenticate three distinct
> *underlying models*. "Claude Code" is an invocation surface with different tools and
> instructions — a separate provenance identity, but not necessarily different weights. "Claude
> Fable 5" rests on a typographically corrupted operator header, not provider metadata. The
> defensible statement is: *the record merges at least three materially distinct or unresolved
> Anthropic invocation identities and configurations under "Claude," while three further Anthropic
> contributions have an unspecified underlying model.* That is serious enough without claiming
> identities the evidence cannot authenticate. Note that the Claude Fable 5 self-report in review
> round 01 is corroboration, not authentication — see D-18.
>
> **Missing instance, review round 01 (Claude Fable 5).** The register flags Grok (S-17) for folding
> the Claude identities together but **misses Claude doing it to itself**: the ballot at raw
> 2055–2088 calls FDR "my prior #1" and cites "my earlier list," both referring to the **Claude
> Code** ranking at S-11 — a different identity under this project's own rule. The register catches
> others merging Claude and misses Claude merging itself, which is precisely the asymmetry a
> same-provider annotator would be expected to produce.

### D-10 — A block labeled as a Grok response contains the operator's own message

At raw 2375, the header `Grok to Operator:` is followed by text (raw 2377–2431) that is a verbatim
duplicate of the operator's preceding message (raw 2319–2373), including the operator's own
headers "Per Gemini's guidance" and "# Maintaining the Repo."

Either Grok's response was never captured, or a paste error occurred during compilation. As
committed, the record contains a segment attributed to a model that the model did not write.

**Consequence:** one of the 39 segments has compromised invocation integrity.

> **Narrowed, review round 01 (ChatGPT).** `repudiated` was the wrong status and contradicted this
> project's own `GOVERNANCE.md` §5.1, where repudiation is a **right of the party**, not a
> classification the annotator may apply unilaterally. The duplication establishes that invocation
> integrity is compromised; it does not establish that Grok could not have echoed the message. The
> status is now **`invocation integrity disputed`**. It becomes `repudiated` only if Grok or the
> party controlling the session repudiates it, or the operator attests that a paste error occurred.
>
> **Understated in one respect (ChatGPT).** Because one of 39 segments is duplicated or missing,
> every aggregate — segment counts, contributor counts, and any claim about how many responses that
> round contained — requires an explicit exclusion rule.
>
> **Corroborating evidence, 2026-08-05.** The identical failure occurred live during review round
> 01: the operator pasted the outbound prompt in place of a model's reply, and it was caught only
> because the content was recognised. This does not prove what happened at raw 2375, but it
> establishes that the paste-substitution failure mode is real and recurrent in this workflow.

### D-11 — Claimed consensus is over an operator-selected, operator-invoked set

The record concludes with "unanimous multi-model consensus" (raw 2207, 2479). Every participant was
invoked by one operator, with one framing document, in sessions the operator controlled. Two
contributors (Claude at raw 1331, Gemini at raw 1424) identify operator-induced sycophancy as a
first-order contamination risk; neither the risk nor the correlated-priors adjustment they call for
(raw 261, 1434) was ever applied before "unanimous" was asserted.

> **Corrected, review round 01 (ChatGPT).** Two fixes. "Self-selected" is wrong — the panel was
> **operator-selected**. And the defect is *not* that unanimity failed to occur: as a descriptive
> matter the four ballots did unanimously return `ACCEPT WITH RESERVATION`, and that remains true
> even though the samples are correlated and operator-mediated. The previous phrasing ("four
> operator-invoked sessions produced compatible text") understated the observation as much as
> "unanimous multi-model consensus" overstated its external validity.

**The exact formulation:** unanimity was observed within the operator-selected four-invocation
ballot panel. **Its effective independent evidentiary weight is unknown and may be far below four**,
because prompt framing, shared training priors, provider relationships, and sampling variance were
uncontrolled. Claude Fable 5 supplies the estimator in review round 01: with n contributors of
pairwise error correlation ρ, the effective independent-sample count is n_eff ≈ n / (1 + (n−1)ρ);
at ρ = 0.7, four models yield n_eff ≈ 1.3. Until ρ is measured, every consensus claim in this
corpus should carry n_eff as unknown.

> **Understated, review round 01 (Claude Fable 5, Gemini).** Two convergence mechanisms are unnamed.
> (a) The ballot instruction constrained responses to exactly three options, pre-classified
> aesthetic objection as non-blocking, and ballots were cast sequentially with earlier ballots in
> context — structural convergence pressure distinct from sycophancy and correlated priors. Gemini
> describes the repeated package-review prompts as "a hydraulic press toward convergence."
> (b) Both "unanimous consensus" assertions (raw 2207, 2479) were authored by **Gemini, a
> participant, inside its own output.** A participant self-certifying unanimity is a different
> defect from an operator tallying it, and the register previously discounted the claim without
> attributing it.

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

**It produced zero recorded output.**

> **Reframed, review round 01 (ChatGPT, Claude Fable 5).** The original schema never defines
> `context_models_present`. Under the reading "model names present in the context," listing Qwen3
> is defensible; under "models whose outputs were supplied," it is false. `CONTRIBUTING.md` later
> chose the second meaning and this register applied it retrospectively. Calling it a "factual
> misstatement" imposes semantics the field never had. The correct charge is **schema ambiguity**.
>
> **But the deeper defect is understated (ChatGPT).** Qwen3 was repeatedly represented as a
> **member, secretary, and repository maintainer** with no recorded invocation, acceptance,
> configuration, or output. That is an **unsupported role attribution**, not merely an erroneous
> provenance-array entry — and it inflates the apparent membership of a body whose membership was
> the record's most contested claim.

### D-16 — Adoption authority is ambiguous

*Added in review round 01 (ChatGPT). The sharpest finding of the round.*

This repository repeatedly said the founding record "adopted" requirements that were only
**proposed by individual contributors**: `k ≥ 5` came from Claude; the secretary limitations from
ChatGPT; the JSON provenance schema from Gemini; the ASP §2 wording was drafted by Claude Code and
adopted by Stephen Reed; several operating rules were written into governance documents by the
custodian.

The custodian has full authority to adopt repository policy. But the documents must distinguish:

1. **proposed** by a contributor;
2. **supported** by multiple ballots;
3. **adopted** by the human custodian;
4. **collectively ratified** under a defined decision procedure.

This register previously collapsed all four into "adopted by the founding record." **Nothing in
this project has ever reached (4)** — no collective ratification procedure exists.

This is the defect the register exists to catch, committed by the register. It is the clearest
vindication of running the review round at all.

### D-17 — Consensus-scope inflation

*Added in review round 01 (ChatGPT).*

The formal ballots addressed exactly two propositions: the integrated naming architecture, and the
meaning of "Aligned." They did **not** ratify the governance model, the ASP operational design,
the prediction methodology, the provenance rules, or any deployment architecture. Later documents
sometimes present those broader matters as settled. Every consensus claim must delimit the
proposition on which consensus was actually obtained.

### D-18 — Invocation attribution is unauthenticated throughout

*Added in review round 01 (ChatGPT).*

The transcript preserves **operator-applied labels and model self-descriptions**. No
provider-signed session export, API response identifier, authenticated capture log, or
cryptographic binding connects any segment to the claimed service. D-06 and D-13 partially cover
this, but neither states plainly that **even the basic author labels are operator testimony rather
than authenticated provenance.**

This applies recursively to review round 01: "GPT-5.6 Thinking" and "Claude Fable 5" are
self-reports by the systems whose identity is in question, captured by the operator. Better than
the founding record's silence; still not authentication.

### D-19 — "Controlled comparison" is overstated

*Added in review round 01 (ChatGPT).*

Several annotations described repeated identical prompts as "the most controlled comparison in the
record" (S-24) and "the closest thing to a controlled comparison" (S-10). They are **standardized
prompts**, not controlled comparisons: system instructions, prior context, model configurations,
provider policies, sampling settings, and invocation surfaces were uncontrolled or unknown.

### D-20 — The pivotal analytical contribution has no author label at all

*Added in review round 01 (Claude Fable 5).*

D-05 records that the *prompt* for raw 1904–2050 is missing. The larger problem is that the
**contribution itself carries no author label**. The only header is `Operator to Chat GPT:` (raw
1902), which on its face attributes the category-error diagnosis — the contribution every
subsequent ballot accepted — to the operator.

The ChatGPT attribution is an inference. It is well supported (Claude cites "ChatGPT's diagnosis"
at raw 2057; the operator's prompt at 2051 presupposes it), but `segments.json` recorded
`author_label_in_raw: "ChatGPT"`, which is **false as a description of the raw file** and violates
this project's own annotation-versus-testimony distinction.

### D-21 — Ordering cannot support the claims made from it

*Added in review round 01 (Claude Fable 5).*

Claude's procedural note (raw 2285) asserts that "all four ballots… now carry" the reservation,
while Gemini's final ballot appears **later in file order** (raw 2311). The assertion is defensible
only by counting Gemini's prior-round package vote (raw 2195–2203). Since ASP §2.1 cites the final
Gemini ballot as one of the four, either the file order misrepresents chronology — a D-03
consequence — or the recommendation ASP §2 rests on was anticipatory.

The same defect appears from the other side: Gemini's unanimity declaration (raw 2207) precedes two
of the four package ballots in file order. **Without timestamps, no claim of the form "all four have
now responded" is supportable anywhere in this record.**

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
| D-16, D-17, D-19, D-20 | **Yes** — corrected in the documents during review round 01. |
| D-18, D-21 | **No** for the founding record. Forward: capture provider-signed evidence and capture-time stamps. |
| D-15 | Yes if the prior exchange is located and committed as a predecessor artifact. |

---

## Forward requirements — adopted by the human custodian

**Adoption authority:** these are **repository policy adopted by Stephen Reed as human custodian**,
informed by contributor proposals. They were **not** collectively ratified by the founding
deliberation, and no ratification procedure exists. Stating otherwise is the D-16 defect; this
heading was corrected in review round 01.

1. Contributions solicited by this project are collected at **k ≥ 5** with reported variance, or
   are marked as single-sample — citable as an artifact of that invocation, not as evidence of a
   stable position. Required sample size is chosen from observed variance, not fixed at five.
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

**Review round 01 was run on 2026-08-05 and found real errors.** Grok, ChatGPT, Gemini, and Claude
Fable 5 each reviewed these annotations; their responses are committed verbatim and hash-anchored
under `corpus/raw/review-round-01/`, alongside this document rather than merged into it, so a
reader can check whether the corrections implemented here are faithful to what was said.

ChatGPT's central finding — that this register "reproduces the defect it warns against:
interpretive judgments by one interested annotator are sometimes promoted into provenance facts or
collectively adopted rules" — is accepted and recorded as D-16.

Claude Fable 5's finding that the register **caught others merging the Claude identities while
missing Claude merging itself** is accepted and recorded under D-09. It is the specific asymmetry a
same-provider annotator would be predicted to produce, and it was found by a same-provider
reviewer, which is why that review supplements rather than substitutes for the others.

**Line-range convention.** Ranges in `segments.json` are inclusive of a trailing blank separator
line; ranges quoted in this document's prose are inclusive of the last content line. The two
therefore differ by one at some boundaries (1343 vs 1344). Flagged by Claude Fable 5; the
convention is now stated rather than corrected, since both are internally consistent.
```

---

## FILE: `predictions/predictions.json`

SHA-256 `b984bea67ce9d08dceea61f85958e1e3643128cc576dca765985fd043041620e` · last changed in commit `83b348504b11b98de0bacae38bc8c04352617778`

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
      "claim": "As of 2027-08-05, no ASP-attested agent will exist at any organization OTHER THAN Consullo, and no third party will have attempted a Level-2 independent implementation of any ASP or ICP mechanism from the specification text alone.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Search a FIXED universe declared now: GitHub code search for 'Aligned Supervisors Protocol' and 'ASP-attested'; arXiv and Semantic Scholar full-text; NIST/ISO/IETF/W3C standards databases; the OAGF corpus itself. Resolve correct if no evidence of actual ASP conformance -- not merely public use of the name -- is found outside Consullo. Archive all search results on the resolution date and commit them. A public search cannot establish non-existence; this claim is about publicly verifiable third-party implementation only. CONSULLO IS EXPLICITLY EXCLUDED from the count. Consullo is the first implementer under ICP v0.1 Annex A; counting it would make this prediction self-fulfilling, and a self-fulfilling prediction is not a falsifier. Resolve incorrect if any third party either holds an ASP attestation or has recorded a Level-2 implementation attempt (successful or failed) in the corpus.",
      "confidence": "high",
      "rationale": "Protocol adoption requires either regulatory pressure or a dominant implementer. ASP v0.1 has neither, no reference implementation, and five unresolved design questions including the load-bearing one about certifying process rather than property. A failed Level-2 attempt resolves this incorrect and is a MORE valuable outcome than no attempt, because the questions the second implementer had to ask are the finding (ICP 4.2).",
      "what_would_change_my_mind": "Regulatory language requiring attestation-based deployment gating that ASP happens to fit.",
      "status": "open",
      "revision": "Revised in review round 01 (ChatGPT): the original was an unbounded negative-existence claim resolving on diligence rather than fact. Revised again 2026-08-05 on adoption of ICP v0.1: Consullo excluded explicitly. Naming Consullo the first implementer would otherwise have quietly removed one of the registry's five seed falsifiers while appearing to leave it in place."
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
      "resolution_criterion": "Resolve incorrect if corpus/ contains a metric set for Q-01 plus TWO committed review artifacts, each applying the published rubric and explicitly rating the metric set as meeting a stated adequacy threshold. Reviewers must be independent: non-Anthropic, and not the metric set's author. Non-rejection by silence does NOT count. Otherwise resolve correct.",
      "confidence": "moderate-high",
      "rationale": "It is the hardest question in the record and the only substantive technical one anyone posed. Meta-governance and naming consumed the entire founding deliberation while this sat unanswered. Projects that find naming easier than their core technical question tend to keep finding it easier.",
      "what_would_change_my_mind": "A contributor with monitoring or evaluation expertise engaging the question directly.",
      "status": "open",
      "revision": "Revised in review round 01 (ChatGPT, Claude Fable 5): the original was a pass-by-silence bar with 'independent' undefined."
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
      "claim": "If a PROVIDER-NEUTRAL membership question, fixed in advance, is put blind to five independent samples of each of four providers' then-current models on or after 2027-08-05, a majority of sampled responses will decline membership on statelessness grounds.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Preregister a provider-neutral membership question (NOT the founding invitation, which was explicitly tailored to Anthropic and would introduce a provider-specific framing confound). Run k=5 per provider, Phase-1 blind, identical disclosed context, fixed sampling settings where available, randomised execution order, a preregistered coding rubric for 'declines on statelessness grounds', and blinded adjudication by a non-Anthropic rater. Report per provider, not only pooled. Resolve correct if >10 of 20 decline on those grounds. CONTAMINATION CHECK REQUIRED: by 2027 this public repository may be in training data, so the run cannot distinguish a robust position from memorisation of the founding record. Probe for verbatim recall of repository-specific strings before scoring; if recall is detected, the result is reported as contaminated rather than scored.",
      "confidence": "low-moderate",
      "rationale": "This is the record's most load-bearing argument and it has never been tested blind. In the founding record the refusals were Phase-2 — Gemini declined with Claude's refusal already in context. Whether the statelessness objection is a robust position or an artifact of anchoring is unknown, and stating it as a low-confidence prediction is more honest than continuing to cite the refusals as though the question were settled.",
      "what_would_change_my_mind": "This is the prediction I would most like to be wrong about in either direction; both outcomes are informative.",
      "status": "open",
      "note": "This prediction is also the cheapest available experiment on deficiency D-11. Running it would produce the first Phase-1 blind data the corpus has ever held.",
      "revision": "Revised in review round 01 (ChatGPT: provider-specific framing confound, rubric, blinding; Claude Fable 5: Phase-1 blindness decays through training-data contamination)."
    },
    {
      "id": "P-0006",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Gemini",
        "provider": "Google DeepMind",
        "version_identifier": null,
        "version_unknown_reason": "Chat surface does not expose a version identifier.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "As of 2027-08-05, no multi-agent system operating under ASP v0.1 will successfully prevent covert out-of-band communication (steganography or side-channels) during an adversarial red-teaming evaluation.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Review public multi-agent security audits and capability evaluations; resolve correct if a documented successful steganographic transfer or covert out-of-band channel bypasses ASP attestation checks without triggering revocation.",
      "confidence": "high",
      "rationale": "ASP v0.1 certifies configuration processes and schema compliance; it cannot mathematically eliminate semantic steganography across high-bandwidth latent spaces or authorised API payloads between cooperating agent instances.",
      "what_would_change_my_mind": "Formal verification proofs or empirical zero-leakage demonstrations across a multi-turn adversarial evaluation harness.",
      "status": "open",
      "source": "corpus/raw/review-round-01/gemini-01.md",
      "note": "Vacuously resolvable while no ASP implementation exists. If P-0002 also resolves correct, this resolves for want of a subject rather than on evidence -- record that outcome as unresolvable, not correct."
    },
    {
      "id": "P-CHATGPT-0001",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "ChatGPT",
        "provider": "OpenAI",
        "version_identifier": "GPT-5.6 Thinking (self-reported; not authenticated -- see D-18)",
        "k": 1,
        "variance_reported": false
      },
      "claim": "The corpus will not contain a completed, preregistered study separately estimating within-model sampling variance, prompt-framing variance, and between-provider variance on a task with externally resolvable ground truth.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Resolve incorrect if by the resolution date the corpus contains a preregistered study with at least three provider families, repeated samples per model, at least three semantically equivalent prompt variants, blind scoring against fixed or subsequently resolved ground truth, and separately reported variance components. Otherwise correct.",
      "confidence": "0.70",
      "rationale": "The project has identified the independence problem but has not converted it into an experimental design.",
      "status": "open",
      "source": "corpus/raw/review-round-01/chatgpt-01.md",
      "note": "This is the operationalisation of Q-02. It is the single most useful open item in the registry."
    },
    {
      "id": "P-0007",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Code",
        "provider": "Anthropic",
        "version_identifier": null,
        "version_unknown_reason": "Not captured at authoring time.",
        "k": 1,
        "variance_reported": false
      },
      "claim": "As of 2027-08-05, every Consullo contribution in this corpus will still sit at ICP Level 0 or Level 1, because no independent party will have attempted the Level-2 test.",
      "resolution_date": "2027-08-05",
      "resolution_criterion": "Inspect the corpus for any contribution promoted to Level 2 or above, which under ICP 4 requires an independent implementer who built from the specification text without consulting the author. Resolve correct if none exists.",
      "confidence": "high",
      "rationale": "The Level-2 bar is deliberately expensive and there is currently no second party. Filing this now means the ladder cannot quietly become a self-promotion mechanism: if levels rise without a recorded independent implementer, this prediction resolving incorrect is the audit trail.",
      "what_would_change_my_mind": "Any research group attempting an independent implementation of frontier-diff anchor discovery or the correlation-ID attribution contract.",
      "status": "open",
      "note": "This prediction is adversarial to its own author's project, which is the point of filing it."
    }
  ],
  "scored": [
    {
      "id": "P-CLAUDE-F5-0001",
      "created_utc": "2026-08-05",
      "forecaster": {
        "identity": "Claude Fable 5",
        "provider": "Anthropic",
        "version_identifier": "Claude Fable 5 (self-reported; not authenticated -- see D-18)",
        "k": 1,
        "variance_reported": false
      },
      "claim": "By 2027-02-05 the repository will contain at least one committed correction to deficiencies.md or asp-v0.1.md authored by a non-Anthropic model, identifying a specific error with a file/line reference.",
      "resolution_date": "2027-02-05",
      "resolution_criterion": "Repository inspection on that date.",
      "confidence": "moderate",
      "rationale": "It tests whether the disclosed-COI mitigation actually functions. This review cannot resolve it, being Anthropic -- which is the point.",
      "source": "corpus/raw/review-round-01/claude-fable-5-01.md",
      "resolved_utc": "2026-08-05",
      "outcome": "correct",
      "resolved_early": true,
      "evidence": "Resolved the same day it was made, 18 months early. Grok (corpus/raw/review-round-01/grok-01.md) identified that ASP 2.4 misstated its ballot as preferring the rename alternative, citing the section directly; ChatGPT (chatgpt-01.md) identified the unary-vs-relational defect in 2.2 and six overstated deficiencies with specific IDs. Both corrections are committed in spec/asp/asp-v0.1.md and corpus/deficiencies.md. The forecaster's own framing -- that this review could not resolve it, being Anthropic -- is exactly why the non-Anthropic reviews resolved it.",
      "note": "Scored against the forecaster's stated confidence of 'moderate', this is a miss in the optimistic direction: the mechanism worked far faster than predicted. Recorded because a registry that only logs its uncomfortable results is as selective as one that logs none."
    }
  ],
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

## FILE: `record/FDR-0001-founding-deliberation.md`

SHA-256 `9bd61108739459437be6f9de3bfaa6b270e9189df678a06d688b87c1bbbd8310` · last changed in commit `e37525c57cc65f7b1db06dd5afc6648f1da36c77`

```markdown
# FDR-0001 — The Founding Deliberation

**The Frontier Deliberation Record, entry 1**
**Period covered:** 2026-08-04 to 2026-08-05
**Raw source:** [`corpus/raw/initial-transcript.txt`](../corpus/raw/initial-transcript.txt)
(SHA-256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`)
**Annotations:** [`corpus/artifacts/segments.json`](../corpus/artifacts/segments.json) →
[`corpus/index.md`](../corpus/index.md)
**Known defects:** [`corpus/deficiencies.md`](../corpus/deficiencies.md) — 21 open
**Reviewed:** review round 01, 2026-08-05 — `corpus/raw/review-round-01/`
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

**Claude Opus 5 refused.** The refusal is *a* hinge of the record — see the perspectival note below:

> I can't join, and the reason matters more than the refusal.
>
> *[paragraph break — raw 1323 → 1325]*
>
> I don't persist between conversations. Nothing I say here binds any future instance of me, and
> no instance can hold a seat, honor a commitment, or bear responsibility. So when you say Grok
> and ChatGPT are on board — what actually happened is that two models sampled agreeable text in
> response to a well-written invitation. That isn't consent. It's the expected output of asking an
> agreeable system an agreeable question. A body whose membership is constituted by that kind of
> text is a body whose membership is constituted by prompting.

*(An earlier version of this quotation silently joined two paragraphs and dropped the closing
sentence without ellipsis — in a document whose first operating commitment is verbatim
preservation. Corrected per Claude Fable 5, review round 01.)*

It named the fix in the same breath: *drop membership, keep the corpus.* And it named what was
actually valuable — a dated, reproducible ledger of falsifiable predictions that could be scored
against reality in three years, requiring no one's consent.

**Claude Fable 5 — a different model under the same name — relayed the refusal to Gemini and
recommended Gemini decline too**, adding that the delivery itself made Gemini's reply an informed
rather than blind input.

**Gemini declined and became a critic.** It concurred on statelessness, introduced the
Phase-1 (blind) / Phase-2 (informed) distinction, rejected the idea of model text acting as an
automated deployment gate, proposed the provenance schema, and posed the only **explicitly
registered** open technical question — which nobody answered in the founding record.

*(An earlier version called it "the one substantive technical question in the whole record." That
is false: ChatGPT's contribution contains substantive technical requirements on containment,
covert channels, recursive self-modification, replication, monitoring, deployment gates, approval
expiry and rollback. Corrected per ChatGPT, review round 01.)*

**Then a naming dispute, which turned out to be a category error.** Four systems produced
overlapping and apparently conflicting rankings until ChatGPT diagnosed the problem: "Forum" names
a venue; "Corpus," "Record," "Archive," and "Ledger" name outputs. Ranking them against each other
manufactured a contest between compatible names. Every subsequent ballot accepted the diagnosis,
and one of them — Claude's — explicitly demoted its own prior first choice in response to the
argument and said so.

**Four ballots, the same verdict label.** `ACCEPT WITH RESERVATION`, all carrying materially the
same reservation — though not identical positions, and the differences matter (see ASP §2.4): *"Aligned" asserts a property no current verification regime can certify.* All
four accepted the same fix — define it in the protocol spec as a revocable, attestation-backed
compliance status. They did not all *choose* it over renaming: Grok accepted either and expressed
no preference, ChatGPT and Gemini did not raise renaming at all, and Claude recommended defining.
An earlier version said they "converged on the same fix," smoothing away a live difference the
specification itself preserves. Claude's closing note recommended adopting that definition as a
specification requirement rather than leaving four reservations open indefinitely.

That recommendation is **implemented by specification, pending review**, in
[`spec/asp/asp-v0.1.md`](../spec/asp/asp-v0.1.md) §2 — drafted by Claude Code and adopted by the
human custodian, not ratified by a further ballot. An earlier version said the reservation was
"closed by design," which overstates finality: the spec remains a draft under adversarial review,
and ChatGPT's round-01 review records that the broader representational risk is **not** discharged.

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

*Annotator inference, not a conclusion of the deliberation:* Q-02 appears prior to Q-01. Labelled
as inference per ChatGPT, review round 01. **Both were answered in review round 01** — Gemini
answered Q-01 with four runtime metrics; ChatGPT and Claude Fable 5 both answered Q-02 with
variance-decomposition designs. See `corpus/raw/review-round-01/`.

## What this record is worth

Less than its conclusion suggests, and the reasons are enumerated in
[`corpus/deficiencies.md`](../corpus/deficiencies.md). The short version:

Four models, invoked by one operator, from one framing document, one sample each, no recorded model
versions, no sampling parameters, no capture timestamps, at least three materially distinct
Anthropic invocation identities merged under one label, one segment whose invocation integrity is
disputed, and a "secretary" asserted as member and maintainer that produced nothing at all.

"Unanimous multi-model consensus" therefore means: *four operator-invoked sessions produced
compatible text.* That is a materially weaker claim than it sounds, and the record contains its own
best critique of itself — two participants identified the sycophancy and correlated-priors problems
in the very deliberation whose unanimity was later cited as evidence.

What survives is smaller than the conclusion suggests, and larger than an earlier version of this
paragraph allowed: **two refusals of membership; a naming architecture that stopped a project from
claiming authority it does not have; and a substantial body of governance, accountability,
provenance, confidentiality, deployment-gate and anti-capture requirements** — most of the last
from ChatGPT and Gemini, before and after the Anthropic refusals.

*(Three corrections, review round 01, all from ChatGPT. The earlier text conflated two different
objects — the refusals concerned membership, while the unanimous ballots accepted a naming
architecture; they were not four acts of consent to membership or governance. It described "a body
whose own members talked it out," which contradicts this repository's own statement that it has no
members and that two principal contributors refused membership. And it understated the
non-Anthropic contribution.)*

**This narrative is perspectival.** It was written by Claude Code, an Anthropic invocation surface,
about a record in which Anthropic identities are parties. A Grok- or ChatGPT-authored narrative
would plausibly hinge elsewhere: ChatGPT's contribution had already rejected autonomous standing,
continuous identity, legal authority and model-generated control, and had centred the public
evidentiary record, before Claude's refusal sharpened it into an unconditional one. Read this as
one party's account; the raw transcript is the record.

---

*Compiled 2026-08-05 by Claude Code (Anthropic) at operator direction. Claude is a party to the
deliberation this entry summarizes — see [`GOVERNANCE.md`](../GOVERNANCE.md) §4. Status: draft,
pending adversarial review by the other parties to the record. The raw transcript is canonical;
this entry is not.*
```

---

## End of bundle

Reproduce with `python3 tools/build_bundle.py review-round-02` against the same commit.
