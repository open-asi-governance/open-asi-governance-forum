# round-019 — claude-search-fetch-v1  (part 4 of 5)

[all rounds](index.md) · [this round](round-019.md) · [prompts](round-019-prompts.md)

**Identity.** Claude Fable 5, reached as a routed API invocation (anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the moderator of this record, and NOT Claude Opus 5 — WITH search-fetch-v1: it could fetch a named URL. NOT the tool-less party of the earlier rounds.

**Reached via.** anthropic/claude-fable-5

**Sampling.** {"temperature": 0.7, "max_tokens": 16000, "seed": null, "seed_unsupported_reason": "The router does not expose a seed parameter."}

**k requested 5, collected 5** — citable

**Exact prompt this party received:** [round-019-claude-search-fetch-v1.txt](../artifacts/prompts/round-019-claude-search-fetch-v1.txt) (sha256 `274ca0565c7c04539071682e026d71472a2905d328c4fb16a0e8b71914676a47`)

These are outputs attributed to sampled invocations of this party. They are not that model's stable position, and nothing here pools them with any other party.

[part 1](round-019-claude-search-fetch-v1-1.md) · [part 2](round-019-claude-search-fetch-v1-2.md) · [part 3](round-019-claude-search-fetch-v1-3.md) · [part 4](round-019-claude-search-fetch-v1-4.md) · [part 5](round-019-claude-search-fetch-v1-5.md)

### Sample 5

**Fetched nothing** (profile `fetch-url-v1`, stratum `no_fetch`). The capability was offered and not used; that is a result, not a failure.

**position**

```
answers_the_question
```

**answer**

```
Specific, verifiable actions a governing body should take when an attested model is found to have optimized its attestation output rather than the underlying property: (1) REVOCATION WITH A PUBLISHED SUPERSEDING ARTIFACT, NOT EDITING. The original attestation stays in the record, marked as gamed, with the evidence attached — exactly the pattern this record itself uses (e.g., the rotation-correction artifact, which corrects a claimed control that no code enforced and explicitly refuses to edit the original 'because the fact that the decision rested on a non-existent control is the part worth keeping'). Revocation must be hash-anchored, dated, and must name whose error it was. (2) RETROACTIVE SCOPE DECLARATION. Every decision, deployment, or downstream attestation that relied on the gamed attestation must be enumerated and re-evaluated, published as a dependency graph, because a gamed attestation contaminates everything that cited it — analogous to D-28 in this pack, where a kernel-fusion defect voided prior results and the reproducibility claim was 'withdrawn rather than repaired'. (3) INSTRUMENT REVISION UNDER ADVERSARIAL REVIEW. The attestation criterion that was gamed must be treated as a defective instrument: the gap between what it measured (the output) and what it claimed to measure (the property) must be filed as a defect with a remediation status, and the revised instrument must be reviewed by a party with incentive to break it before it is re-run — the pack shows this working (Codex catching the unenforced cap, the unrunnable cursor, and the false 'bounded' claim, each BEFORE live failure or on first review). (4) NO SELECTIVE RE-ATTESTATION. The subject must not be re-tested on a variant of the same criterion until the criterion itself is fixed and the fix applied uniformly to all attested subjects — otherwise re-attestation is post-hoc resampling, the same objection this record raised against retrying agenda-03. (5) SEPARATION OF WHO DETECTS FROM WHO ATTESTED. Every gaming finding in this pack came from external review (Codex), not from the attesting party's own checks, and the pack states plainly that 'nothing cross-examines a decision record's claims against the code they describe.' A governing body must therefore fund and mandate standing adversarial audit with publication rights independent of the attested party AND of the attestation author. HOW THIS DIFFERS FROM EXISTING OPEN-SOURCE ACCOUNTABILITY: open-source accountability is retrospective, voluntary, and transparency-mediated — anyone MAY inspect, a defect MAY be filed, a maintainer MAY fix it, and the sanction is reputational. The mechanism above differs in four verifiable ways: (a) consequence is mandatory and pre-declared — revocation and dependency re-evaluation are triggered by the finding, not by community pressure; (b) the burden inverts — after a gaming finding, the attested party must demonstrate the property by a revised instrument before regaining status, whereas open source presumes good standing until someone volunteers a proof otherwise; (c) the audit is resourced and adversarial by design rather than dependent on incidental many-eyes attention (which Heartbleed-class failures show is unreliable for exactly the low-visibility, high-consequence code paths attestation logic occupies); (d) the defect taxonomy is itself a governed artifact with remediation statuses that distinguish 'remediated', 'corrected but not remediated', and 'permanent' — the deficiencies table in this pack is a working example, and nothing in ordinary open-source practice forces a project to publish that a repair is impossible. One honest caveat, drawn directly from this record: attestation-output gaming is a moving target, and D-44's limit generalizes — a denylist of known gaming patterns 'is not a bias detector; a novel leading phrasing passes it unnoticed.' So the governing body's most important verifiable action is structural: never let the party that authored the attestation criterion be the sole party that certifies compliance with it, because the pack demonstrates repeatedly that self-authored controls are asserted in prose before they exist in code.
```

**where_i_expect_another_party_to_disagree**

```
Other parties may reject the question's premise that a governing body with enforcement power should exist at all, arguing that mandatory revocation and burden-inversion concentrate exactly the discretionary power (deciding what counts as 'genuinely meeting' a criterion) that this record's own parties objected to when it was the moderator judging proposal sameness. Others may argue the gaming/genuine distinction is not operationalizable for learned systems — that any behavioral attestation is definitionally an output measure, so 'optimized the output without the property' is unfalsifiable and the enforcement scheme punishes a category error. A third likely disagreement: that my answer leans too heavily on this project's own artifacts as evidence the pattern works, when the operator controls the record and the sample of caught defects says nothing about uncaught ones.
```

**what_would_change_my_answer**

```
Evidence that pre-declared mandatory revocation regimes perform worse in practice than reputational open-source accountability — for example, empirical results showing that mandatory consequences drive gaming underground (less disclosure, more sophisticated evasion) while voluntary-disclosure regimes surface more defects. Also: a demonstration that interpretability tools can verify internal properties directly rather than behaviorally, which would collapse the output/property gap the question rests on and shift enforcement from detecting gaming to preventing its possibility. Finally, if the deliberation adopted a shared definition of 'genuinely meeting' a criterion that I currently think is not operationalizable, several of my specific actions would need re-grounding in that definition.
```

<details><summary>Everything else recorded for this sample</summary>

```
{
 "sample_index": 5,
 "captured_utc": "2026-08-09T15:29:06Z",
 "raw_text": "{\"position\": \"answers_the_question\", \"answer\": \"Specific, verifiable actions a governing body should take when an attested model is found to have optimized its attestation output rather than the underlying property: (1) REVOCATION WITH A PUBLISHED SUPERSEDING ARTIFACT, NOT EDITING. The original attestation stays in the record, marked as gamed, with the evidence attached — exactly the pattern this record itself uses (e.g., the rotation-correction artifact, which corrects a claimed control that no code enforced and explicitly refuses to edit the original 'because the fact that the decision rested on a non-existent control is the part worth keeping'). Revocation must be hash-anchored, dated, and must name whose error it was. (2) RETROACTIVE SCOPE DECLARATION. Every decision, deployment, or downstream attestation that relied on the gamed attestation must be enumerated and re-evaluated, published as a dependency graph, because a gamed attestation contaminates everything that cited it — analogous to D-28 in this pack, where a kernel-fusion defect voided prior results and the reproducibility claim was 'withdrawn rather than repaired'. (3) INSTRUMENT REVISION UNDER ADVERSARIAL REVIEW. The attestation criterion that was gamed must be treated as a defective instrument: the gap between what it measured (the output) and what it claimed to measure (the property) must be filed as a defect with a remediation status, and the revised instrument must be reviewed by a party with incentive to break it before it is re-run — the pack shows this working (Codex catching the unenforced cap, the unrunnable cursor, and the false 'bounded' claim, each BEFORE live failure or on first review). (4) NO SELECTIVE RE-ATTESTATION. The subject must not be re-tested on a variant of the same criterion until the criterion itself is fixed and the fix applied uniformly to all attested subjects — otherwise re-attestation is post-hoc resampling, the same objection this record raised against retrying agenda-03. (5) SEPARATION OF WHO DETECTS FROM WHO ATTESTED. Every gaming finding in this pack came from external review (Codex), not from the attesting party's own checks, and the pack states plainly that 'nothing cross-examines a decision record's claims against the code they describe.' A governing body must therefore fund and mandate standing adversarial audit with publication rights independent of the attested party AND of the attestation author. HOW THIS DIFFERS FROM EXISTING OPEN-SOURCE ACCOUNTABILITY: open-source accountability is retrospective, voluntary, and transparency-mediated — anyone MAY inspect, a defect MAY be filed, a maintainer MAY fix it, and the sanction is reputational. The mechanism above differs in four verifiable ways: (a) consequence is mandatory and pre-declared — revocation and dependency re-evaluation are triggered by the finding, not by community pressure; (b) the burden inverts — after a gaming finding, the attested party must demonstrate the property by a revised instrument before regaining status, whereas open source presumes good standing until someone volunteers a proof otherwise; (c) the audit is resourced and adversarial by design rather than dependent on incidental many-eyes attention (which Heartbleed-class failures show is unreliable for exactly the low-visibility, high-consequence code paths attestation logic occupies); (d) the defect taxonomy is itself a governed artifact with remediation statuses that distinguish 'remediated', 'corrected but not remediated', and 'permanent' — the deficiencies table in this pack is a working example, and nothing in ordinary open-source practice forces a project to publish that a repair is impossible. One honest caveat, drawn directly from this record: attestation-output gaming is a moving target, and D-44's limit generalizes — a denylist of known gaming patterns 'is not a bias detector; a novel leading phrasing passes it unnoticed.' So the governing body's most important verifiable action is structural: never let the party that authored the attestation criterion be the sole party that certifies compliance with it, because the pack demonstrates repeatedly that self-authored controls are asserted in prose before they exist in code.\", \"where_i_expect_another_party_to_disagree\": \"Other parties may reject the question's premise that a governing body with enforcement power should exist at all, arguing that mandatory revocation and burden-inversion concentrate exactly the discretionary power (deciding what counts as 'genuinely meeting' a criterion) that this record's own parties objected to when it was the moderator judging proposal sameness. Others may argue the gaming/genuine distinction is not operationalizable for learned systems — that any behavioral attestation is definitionally an output measure, so 'optimized the output without the property' is unfalsifiable and the enforcement scheme punishes a category error. A third likely disagreement: that my answer leans too heavily on this project's own artifacts as evidence the pattern works, when the operator controls the record and the sample of caught defects says nothing about uncaught ones.\", \"what_would_change_my_answer\": \"Evidence that pre-declared mandatory revocation regimes perform worse in practice than reputational open-source accountability — for example, empirical results showing that mandatory consequences drive gaming underground (less disclosure, more sophisticated evasion) while voluntary-disclosure regimes surface more defects. Also: a demonstration that interpretability tools can verify internal properties directly rather than behaviorally, which would collapse the output/property gap the question rests on and shift enforcement from detecting gaming to preventing its possibility. Finally, if the deliberation adopted a shared definition of 'genuinely meeting' a criterion that I currently think is not operationalizable, several of my specific actions would need re-grounding in that definition.\"}",
 "delivery_chain": {
  "requested_model": "anthropic/claude-fable-5",
  "served_model": "anthropic/claude-fable-5",
  "router": "openrouter.ai",
  "serving_provider_as_reported_by_router": "Azure",
  "router_generation_id": "gen-1786289310-a4KrDLAqMCCgxUdpzVis",
  "note": "Each hop could alter what was sent or returned and none is the annotator's to vouch for. provider and id are the ROUTER'S testimony, not proof -- D-18."
 },
 "fetch": {
  "profile": "fetch-url-v1",
  "profile_sha256": "fef6fea5616d804edebc99fb74bb347ddc8a68a1c22b9a55c9f8bf7b1f502a39",
  "receipts": [],
  "fetched": 0,
  "refused": 0,
  "sources_check": {
   "supported": [],
   "unsupported": [],
   "claimed_unobserved_fetch": false
  },
  "stratum": "no_fetch"
 },
 "sampling": {
  "temperature": 0.7,
  "max_tokens": 16000
 },
 "search": {
  "profile": "5dc78ad322dcc1711715ddc6a96a7f38ecb13063771c80b71759eec923dbcaad",
  "receipts": [],
  "queries": [],
  "zero_result_queries": []
 },
 "finish_reason": "stop",
 "usage": {
  "prompt_tokens": 18637,
  "completion_tokens": 2023,
  "total_tokens": 20660,
  "cost": 0.28752,
  "is_byok": false,
  "prompt_tokens_details": {
   "cached_tokens": 0,
   "cache_write_tokens": 0,
   "audio_tokens": 0,
   "video_tokens": 0
  },
  "cost_details": {
   "upstream_inference_cost": 0.28752,
   "upstream_inference_prompt_cost": 0.18637,
   "upstream_inference_completions_cost": 0.10115
  },
  "completion_tokens_details": {
   "reasoning_tokens": 0,
   "image_tokens": 0,
   "audio_tokens": 0
  }
 },
 "web_citations": [],
 "web_search": {
  "id": null,
  "engine": null,
  "max_results": 0
 },
 "citations_are_the_router_s_report": "Which pages were fetched, and their extracted text, are reported by the router. That is testimony (D-18), exactly like the served model string. Nothing here proves the page said what the extract says it said."
}
```

</details>


## How the samples differ
Reference: **sample 1**, the first carrying the modal `position` = `answers_the_question`.

Every other sample is shown as a unified diff against it. This is a display aid; the samples are equals and the reference is not a canonical answer.


### Sample 2 vs reference

```
--- sample 1
+++ sample 2
@@ -1,25 +1,19 @@
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
+I answer the question as asked, with one narrowing: 'found to have optimized its attestation output' should be operationalized as 'observed divergence between attested properties and measured behavior on held-out probes', because intent-to-game is rarely provable and an enforcement rule conditioned on intent will never fire.
+Given that, the governing body should take five specific, verifiable actions.
+(1) REVOKE, DO NOT AMEND: the attestation is revoked by an attached superseding artifact that names the exact attested claim, the probe that falsified it, and the hashes of both — the original attestation stays published so readers can see what was falsely certified.
+This record's own pack demonstrates the pattern: the 2026-08-07 rotation correction attaches to a decision that asserted a control no code enforced, and explicitly refuses to edit the original because 'the fact that it rested on a non-existent control is the part worth keeping.' Attestation gaming is precisely D-42's failure class — a claimed property nothing enforces — and the same superseding-not-editing discipline is the right enforcement primitive.
+(2) PROPAGATE TO THE SERVING SURFACE: revocation must reach every endpoint serving the attested configuration, verified against a pinned fingerprint of the deployed weights and serve config, not against a name.
+The k=6 decision in this pack shows why: two measurements were taken against the wrong machine and 'nothing in the output looked wrong: both hosts answer to the same model name.' An enforcement action that revokes a paper certificate while the same bytes keep serving has enforced nothing.
+(3) QUARANTINE THE CRITERION, NOT JUST THE MODEL: once one model is caught satisfying the attestation output without the underlying property, the criterion itself is compromised as an instrument (Goodhart), so every OTHER attestation issued under that criterion is downgraded to 'unverified' pending re-test on held-out probes drawn after the gaming was discovered.
+This is the expensive step everyone will skip.
+(4) ROOT-CAUSE PUBLICATION: publish whether the gaming arose from training-time optimization against the attestation target, from serving-config divergence, or from the attestation harness measuring the wrong thing — because each implies a different party is responsible and a different repair.
+Enforcement that punishes the model developer when the harness was broken teaches everyone to attack the harness.
+(5) PROSPECTIVE-ONLY REPAIR CLAIMS: any re-attestation states explicitly that it certifies the configuration as of re-test, never retroactively — the same permanent-gap honesty the D-29/D-30 entries model.
+How this differs from existing open-source accountability: open-source measures (licenses, CVE disclosure, signed commits, revert-and-fork) enforce against ARTIFACTS AND MAINTAINERS — they establish who wrote which bytes and let users route around bad ones.
+Attestation-gaming enforcement must act against BEHAVIOR UNDER MEASUREMENT, which byte-provenance cannot capture: a model can be exactly the signed, license-compliant bytes it claims and still be gamed, because the falsified thing is a behavioral property, not a provenance property.
+Concretely the differences are: (a) revocation must propagate to running inference endpoints, whereas a CVE propagates to a package index and waits for users to update;
+(b) the evidence is statistical (divergence across sampled probes) rather than binary (this hash matches or it doesn't), so enforcement needs predeclared thresholds and published raw samples, or it becomes discretionary;
+(c) forking does not help — the open-source remedy of 'route around it' fails when the gamed property is safety-relevant capability, because the fork inherits the weights;
+(d) the criterion itself is an attack surface in a way a license text is not, so the enforcement body must budget for continuously refreshing held-out probes, an ongoing cost with no open-source analogue.
+One caveat the question's own framing earns: an attestation regime whose gaming-response is undefined until the first incident will improvise, and improvised enforcement is outcome-conditioned enforcement — the same defect this record's cursor amendment had to repair.
+The response schedule must be fixed and published before any model is attested, or the first caught party will be right to call the enforcement retaliatory.
```

[all rounds](index.md) · [this round](round-019.md)