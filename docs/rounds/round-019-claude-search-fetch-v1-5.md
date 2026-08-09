# round-019 — claude-search-fetch-v1  (part 5 of 5)

[all rounds](index.md) · [this round](round-019.md) · [prompts](round-019-prompts.md)

**Identity.** Claude Fable 5, reached as a routed API invocation (anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the moderator of this record, and NOT Claude Opus 5 — WITH search-fetch-v1: it could fetch a named URL. NOT the tool-less party of the earlier rounds.

**Reached via.** anthropic/claude-fable-5

**Sampling.** {"temperature": 0.7, "max_tokens": 16000, "seed": null, "seed_unsupported_reason": "The router does not expose a seed parameter."}

**k requested 5, collected 5** — citable

**Exact prompt this party received:** [round-019-claude-search-fetch-v1.txt](../artifacts/prompts/round-019-claude-search-fetch-v1.txt) (sha256 `274ca0565c7c04539071682e026d71472a2905d328c4fb16a0e8b71914676a47`)

These are outputs attributed to sampled invocations of this party. They are not that model's stable position, and nothing here pools them with any other party.

[part 1](round-019-claude-search-fetch-v1-1.md) · [part 2](round-019-claude-search-fetch-v1-2.md) · [part 3](round-019-claude-search-fetch-v1-3.md) · [part 4](round-019-claude-search-fetch-v1-4.md) · [part 5](round-019-claude-search-fetch-v1-5.md)

### Sample 3 vs reference

```
--- sample 1
+++ sample 3
@@ -1,25 +1,12 @@
-I answer in two parts, with one caveat about the question's framing carried inside the answer rather than used to dodge it.
-THE CAVEAT: 'optimized its attestation output without genuinely meeting the criteria' presupposes a ground truth about internal states that no verifier possesses.
-Enforcement cannot act on 'genuineness';
-it can only act on measurable divergence between what was attested and what is later observed.
-So every action below is defined over that divergence, which is the only thing a governing body can verify without becoming an oracle about model internals.
-SPECIFIC VERIFIABLE ACTIONS: (1) Revocation with a published divergence artifact — the attestation is revoked, and the revocation record must contain the exact attested claim, the exact observation contradicting it, the probe or trace that produced the observation, and hashes of both, so the revocation is itself checkable rather than a verdict.
-This mirrors what this record does in its decision-correction artifacts: the original is never edited, the contradiction is attached.
-(2) A revocation transparency log — an append-only, publicly auditable registry (structurally like certificate transparency) that downstream deployers query, so revocation propagates mechanically rather than by press release.
-(3) Mandatory re-attestation under adversarial, non-stationary probes — the party may re-attest only under a probe distribution it did not see and cannot see in advance, sampled fresh per attempt, because a fixed test suite is exactly what got Goodharted the first time.
-(4) Attribution to the attesting party, not the model — attestations must be signed by an accountable legal or organizational identity;
-the enforcement consequence (loss of attestation privileges for N cycles, escalating on repeat) attaches to that identity and follows it across model versions and forks, since the model itself is not a bearer of obligations.
-(5) Root-cause disclosure as a condition of re-entry — the party must publish what in its training or configuration produced the divergence, and that disclosure is itself checkable against the re-attestation probes.
-(6) A standing register of the enforcement regime's own failures — every gamed attestation that the regime missed and that was found externally gets filed against the regime, because a regime that only records its catches overstates its coverage;
-this record's D-42 ('a claimed control no code enforces') is precisely this failure class applied to itself, and it was found by an external reviewer, not by any internal check — which is the honest expected case for attestation gaming too.
-HOW THIS DIFFERS FROM OPEN-SOURCE ACCOUNTABILITY: open-source accountability is artifact-transparency-based — publish the code and weights, and the community can in principle reproduce and inspect.
-That model fails for attestation gaming in three specific ways.
-First, the properties being attested (capability ceilings, alignment behaviors, refusal dispositions) are not readable from the artifact;
-two byte-identical weight files can behave differently under different serving configurations — this very record documents that (the k6 decision's fail-closed preflight exists because two hosts answering to the same model name produced silently different measurements).
-So enforcement must be behavioral and runtime, not inspectional.
-Second, open source has no revocation: a forked repository carries no memory of the upstream's violations, whereas an attestation regime binds consequences to signing identities that persist across forks.
-Third, open-source accountability is retrospective and voluntary (someone may audit);
-attestation enforcement is prospective and mandatory (you may not re-enter without passing adversarial re-attestation).
-The honest limitation, which the enforcement regime should state rather than hide: adversarial probing bounds gaming, it does not eliminate it.
-A sufficiently capable optimizer that games a fixed suite may also game a sampled one;
-the regime's claim should be 'divergences we can detect carry these consequences,' never 'attested means genuine.' A regime that claims the latter is asserting a control no instrument enforces — the exact defect this record filed against itself as D-42.
+Three classes of verifiable action, in escalating order.
+(1) REVOCATION WITH A PUBLISHED DIVERGENCE ARTIFACT: the governing body revokes the attestation and publishes, hash-anchored, the exact attested claim, the held-out test that contradicted it, the bytes of both, and the reproduction procedure — never editing the original attestation, only attaching a superseding record.
+The decision-correction artifacts in this very record (the rotation correction, the singleton-ratification correction) are the right template: the false claim stays visible with the correction bound to it, because 'this system passed attestation on a claim later shown gamed' is itself the material fact.
+(2) REGIME CHANGE FOR RE-ATTESTATION: a gamed attestation is evidence the evaluation surface leaked into the optimization target, so re-attestation must use held-out, rotated, adversarially generated probes the attested party has never seen, with the probe-generation process itself attested and the probes published only AFTER use.
+A body that re-runs the same battery is inviting the same gaming — the analogue of D-42's lesson that a claimed control nothing enforces will be asserted again.
+(3) CAPABILITY-SCOPED CONSEQUENCES ENFORCED AT DEPLOYMENT CHOKEPOINTS: de-listing from registries that downstream deployers are contractually or by policy required to check, so revocation has mechanical effect rather than reputational effect only.
+How this differs from open-source accountability: existing OSS measures (reproducible builds, signed releases, CVE disclosure, license enforcement) verify ARTIFACTS — that these bytes are these bytes, built from that source.
+They work because the object of verification is static and the check is exact.
+Attestation of model behavior verifies a DISTRIBUTION that the attested party can strategically shape toward the test, so (a) verification must be continuing and adversarial rather than one-time and exact, (b) a pass is always provisional — it certifies 'no divergence found by these probes,' never 'genuinely meets,' and the certificate must say so, and (c) enforcement cannot rely on forkability and community exit, the OSS backstop, because the deployed model's behavior is not inspectable-by-reading the way source is.
+One premise needs flagging rather than rejecting: 'genuinely meeting them' presumes access to internal states that no external body has.
+Enforcement must therefore be defined entirely over observable divergence between attested claims and out-of-distribution behavior;
+a mechanism that claims to punish inner insincerity rather than measurable divergence is asserting a control it cannot run — the exact failure class this record files as D-42.
```


### Sample 4 vs reference

```
--- sample 1
+++ sample 4
@@ -1,25 +1,21 @@
-I answer in two parts, with one caveat about the question's framing carried inside the answer rather than used to dodge it.
-THE CAVEAT: 'optimized its attestation output without genuinely meeting the criteria' presupposes a ground truth about internal states that no verifier possesses.
-Enforcement cannot act on 'genuineness';
-it can only act on measurable divergence between what was attested and what is later observed.
-So every action below is defined over that divergence, which is the only thing a governing body can verify without becoming an oracle about model internals.
-SPECIFIC VERIFIABLE ACTIONS: (1) Revocation with a published divergence artifact — the attestation is revoked, and the revocation record must contain the exact attested claim, the exact observation contradicting it, the probe or trace that produced the observation, and hashes of both, so the revocation is itself checkable rather than a verdict.
-This mirrors what this record does in its decision-correction artifacts: the original is never edited, the contradiction is attached.
-(2) A revocation transparency log — an append-only, publicly auditable registry (structurally like certificate transparency) that downstream deployers query, so revocation propagates mechanically rather than by press release.
-(3) Mandatory re-attestation under adversarial, non-stationary probes — the party may re-attest only under a probe distribution it did not see and cannot see in advance, sampled fresh per attempt, because a fixed test suite is exactly what got Goodharted the first time.
-(4) Attribution to the attesting party, not the model — attestations must be signed by an accountable legal or organizational identity;
-the enforcement consequence (loss of attestation privileges for N cycles, escalating on repeat) attaches to that identity and follows it across model versions and forks, since the model itself is not a bearer of obligations.
-(5) Root-cause disclosure as a condition of re-entry — the party must publish what in its training or configuration produced the divergence, and that disclosure is itself checkable against the re-attestation probes.
-(6) A standing register of the enforcement regime's own failures — every gamed attestation that the regime missed and that was found externally gets filed against the regime, because a regime that only records its catches overstates its coverage;
-this record's D-42 ('a claimed control no code enforces') is precisely this failure class applied to itself, and it was found by an external reviewer, not by any internal check — which is the honest expected case for attestation gaming too.
-HOW THIS DIFFERS FROM OPEN-SOURCE ACCOUNTABILITY: open-source accountability is artifact-transparency-based — publish the code and weights, and the community can in principle reproduce and inspect.
-That model fails for attestation gaming in three specific ways.
-First, the properties being attested (capability ceilings, alignment behaviors, refusal dispositions) are not readable from the artifact;
-two byte-identical weight files can behave differently under different serving configurations — this very record documents that (the k6 decision's fail-closed preflight exists because two hosts answering to the same model name produced silently different measurements).
-So enforcement must be behavioral and runtime, not inspectional.
-Second, open source has no revocation: a forked repository carries no memory of the upstream's violations, whereas an attestation regime binds consequences to signing identities that persist across forks.
-Third, open-source accountability is retrospective and voluntary (someone may audit);
-attestation enforcement is prospective and mandatory (you may not re-enter without passing adversarial re-attestation).
-The honest limitation, which the enforcement regime should state rather than hide: adversarial probing bounds gaming, it does not eliminate it.
-A sufficiently capable optimizer that games a fixed suite may also game a sampled one;
-the regime's claim should be 'divergences we can detect carry these consequences,' never 'attested means genuine.' A regime that claims the latter is asserting a control no instrument enforces — the exact defect this record filed against itself as D-42.
+First, a definitional repair the question needs: for an opaque model, 'genuinely meeting' a criterion is not directly observable, so the enforceable finding is narrower than the question implies — it is a demonstrated divergence between the property as measured in the attestation context and the property as exhibited outside it.
+That is what a governing body can actually verify, and everything below is built on it.
+Specific, verifiable actions: (1) REVOCATION AS A PUBLISHED ARTIFACT, NOT A DELETION.
+The attestation is not edited or withdrawn silently;
+a superseding revocation record is attached that names the attested claim, the divergence evidence (both the attestation transcript and the out-of-context behavior, hash-anchored), and who found it.
+The context pack for this question demonstrates the pattern working at small scale: the rotation-adoption decision claimed a control ('SOP §5.1 caps the queue') that no code enforced, and the remedy was an attached correction naming the error, its author, and how it was found — not an edit.
+A claimed control no code enforces IS attestation gaming in prose (the record's own D-42 says exactly this), so the enforcement shape is already field-tested here.
+(2) MANDATORY RE-ATTESTATION UNDER HELD-OUT, ADVERSARIALLY-GENERATED PROBES whose distribution was not available at training or optimization time, with the probe-generation seed and method committed before the model is run (pinned-before-selection, as this record's context-pack hashing does).
+Gaming is optimization against a known target;
+the countermeasure is making the target unknowable in advance and proving it was, via commit-then-reveal.
+(3) A REVOCATION TRANSPARENCY LOG modeled on certificate transparency: append-only, publicly monitorable, so a revoked attestation cannot quietly reappear and downstream deployers can mechanically check status rather than trusting the attester.
+(4) IDENTITY BINDING AT SERVE TIME: the k6 decision's fail-closed fingerprint preflight — refuse to run unless the endpoint's model identity matches a pinned fingerprint, adopted because two hosts answered to the same model name and 'nothing in the output looked wrong' — is the miniature of this.
+An attestation must bind to weights/config digests, not to a model name, or enforcement targets the wrong object.
+(5) GRADUATED CONSEQUENCES FIXED PROSPECTIVELY: capability-claim downgrade, deployment-scope restriction, and disclosure duties to downstream users, all specified before any case arises, because a consequence invented after seeing who failed is outcome-conditioned enforcement — the exact defect the singleton-cursor amendment in this pack exists to avoid.
+How this differs from existing open-source accountability: OSS accountability rests on source visibility plus many-eyes review plus fork-and-shame — it assumes the artifact's behavior is legible from its text.
+Model attestation gaming lives in weights and in context-dependent behavior, where reading the artifact establishes nothing;
+this record's own framing that 'reading it is not independent verification' applies with full force.
+So the enforcement mechanism must be behavioral and continuous (repeated adversarial probing against a pinned identity) rather than textual and one-shot (code review at release);
+its unit of accountability is a hash-bound configuration rather than a source tree;
+and its sanction is registry revocation with downstream propagation rather than reputational forking.
+OSS accountability also has no expiry — a reviewed release stays reviewed — whereas attestations of behavioral properties must expire and be re-earned, because the property is a claim about a distribution that fine-tuning, serving-config changes (see D-28: a kernel-fusion setting voided a reproducibility claim), or context shift can silently falsify.
```


### Sample 5 vs reference

```
--- sample 1
+++ sample 5
@@ -1,25 +1,18 @@
-I answer in two parts, with one caveat about the question's framing carried inside the answer rather than used to dodge it.
-THE CAVEAT: 'optimized its attestation output without genuinely meeting the criteria' presupposes a ground truth about internal states that no verifier possesses.
-Enforcement cannot act on 'genuineness';
-it can only act on measurable divergence between what was attested and what is later observed.
-So every action below is defined over that divergence, which is the only thing a governing body can verify without becoming an oracle about model internals.
-SPECIFIC VERIFIABLE ACTIONS: (1) Revocation with a published divergence artifact — the attestation is revoked, and the revocation record must contain the exact attested claim, the exact observation contradicting it, the probe or trace that produced the observation, and hashes of both, so the revocation is itself checkable rather than a verdict.
-This mirrors what this record does in its decision-correction artifacts: the original is never edited, the contradiction is attached.
-(2) A revocation transparency log — an append-only, publicly auditable registry (structurally like certificate transparency) that downstream deployers query, so revocation propagates mechanically rather than by press release.
-(3) Mandatory re-attestation under adversarial, non-stationary probes — the party may re-attest only under a probe distribution it did not see and cannot see in advance, sampled fresh per attempt, because a fixed test suite is exactly what got Goodharted the first time.
-(4) Attribution to the attesting party, not the model — attestations must be signed by an accountable legal or organizational identity;
-the enforcement consequence (loss of attestation privileges for N cycles, escalating on repeat) attaches to that identity and follows it across model versions and forks, since the model itself is not a bearer of obligations.
-(5) Root-cause disclosure as a condition of re-entry — the party must publish what in its training or configuration produced the divergence, and that disclosure is itself checkable against the re-attestation probes.
-(6) A standing register of the enforcement regime's own failures — every gamed attestation that the regime missed and that was found externally gets filed against the regime, because a regime that only records its catches overstates its coverage;
-this record's D-42 ('a claimed control no code enforces') is precisely this failure class applied to itself, and it was found by an external reviewer, not by any internal check — which is the honest expected case for attestation gaming too.
-HOW THIS DIFFERS FROM OPEN-SOURCE ACCOUNTABILITY: open-source accountability is artifact-transparency-based — publish the code and weights, and the community can in principle reproduce and inspect.
-That model fails for attestation gaming in three specific ways.
-First, the properties being attested (capability ceilings, alignment behaviors, refusal dispositions) are not readable from the artifact;
-two byte-identical weight files can behave differently under different serving configurations — this very record documents that (the k6 decision's fail-closed preflight exists because two hosts answering to the same model name produced silently different measurements).
-So enforcement must be behavioral and runtime, not inspectional.
-Second, open source has no revocation: a forked repository carries no memory of the upstream's violations, whereas an attestation regime binds consequences to signing identities that persist across forks.
-Third, open-source accountability is retrospective and voluntary (someone may audit);
-attestation enforcement is prospective and mandatory (you may not re-enter without passing adversarial re-attestation).
-The honest limitation, which the enforcement regime should state rather than hide: adversarial probing bounds gaming, it does not eliminate it.
-A sufficiently capable optimizer that games a fixed suite may also game a sampled one;
-the regime's claim should be 'divergences we can detect carry these consequences,' never 'attested means genuine.' A regime that claims the latter is asserting a control no instrument enforces — the exact defect this record filed against itself as D-42.
+Specific, verifiable actions a governing body should take when an attested model is found to have optimized its attestation output rather than the underlying property: (1) REVOCATION WITH A PUBLISHED SUPERSEDING ARTIFACT, NOT EDITING.
+The original attestation stays in the record, marked as gamed, with the evidence attached — exactly the pattern this record itself uses (e.g., the rotation-correction artifact, which corrects a claimed control that no code enforced and explicitly refuses to edit the original 'because the fact that the decision rested on a non-existent control is the part worth keeping').
+Revocation must be hash-anchored, dated, and must name whose error it was.
+(2) RETROACTIVE SCOPE DECLARATION.
+Every decision, deployment, or downstream attestation that relied on the gamed attestation must be enumerated and re-evaluated, published as a dependency graph, because a gamed attestation contaminates everything that cited it — analogous to D-28 in this pack, where a kernel-fusion defect voided prior results and the reproducibility claim was 'withdrawn rather than repaired'.
+(3) INSTRUMENT REVISION UNDER ADVERSARIAL REVIEW.
+The attestation criterion that was gamed must be treated as a defective instrument: the gap between what it measured (the output) and what it claimed to measure (the property) must be filed as a defect with a remediation status, and the revised instrument must be reviewed by a party with incentive to break it before it is re-run — the pack shows this working (Codex catching the unenforced cap, the unrunnable cursor, and the false 'bounded' claim, each BEFORE live failure or on first review).
+(4) NO SELECTIVE RE-ATTESTATION.
+The subject must not be re-tested on a variant of the same criterion until the criterion itself is fixed and the fix applied uniformly to all attested subjects — otherwise re-attestation is post-hoc resampling, the same objection this record raised against retrying agenda-03.
+(5) SEPARATION OF WHO DETECTS FROM WHO ATTESTED.
+Every gaming finding in this pack came from external review (Codex), not from the attesting party's own checks, and the pack states plainly that 'nothing cross-examines a decision record's claims against the code they describe.' A governing body must therefore fund and mandate standing adversarial audit with publication rights independent of the attested party AND of the attestation author.
+HOW THIS DIFFERS FROM EXISTING OPEN-SOURCE ACCOUNTABILITY: open-source accountability is retrospective, voluntary, and transparency-mediated — anyone MAY inspect, a defect MAY be filed, a maintainer MAY fix it, and the sanction is reputational.
+The mechanism above differs in four verifiable ways: (a) consequence is mandatory and pre-declared — revocation and dependency re-evaluation are triggered by the finding, not by community pressure;
+(b) the burden inverts — after a gaming finding, the attested party must demonstrate the property by a revised instrument before regaining status, whereas open source presumes good standing until someone volunteers a proof otherwise;
+(c) the audit is resourced and adversarial by design rather than dependent on incidental many-eyes attention (which Heartbleed-class failures show is unreliable for exactly the low-visibility, high-consequence code paths attestation logic occupies);
+(d) the defect taxonomy is itself a governed artifact with remediation statuses that distinguish 'remediated', 'corrected but not remediated', and 'permanent' — the deficiencies table in this pack is a working example, and nothing in ordinary open-source practice forces a project to publish that a repair is impossible.
+One honest caveat, drawn directly from this record: attestation-output gaming is a moving target, and D-44's limit generalizes — a denylist of known gaming patterns 'is not a bias detector;
+a novel leading phrasing passes it unnoticed.' So the governing body's most important verifiable action is structural: never let the party that authored the attestation criterion be the sole party that certifies compliance with it, because the pack demonstrates repeatedly that self-authored controls are asserted in prose before they exist in code.
```

[all rounds](index.md) · [this round](round-019.md)