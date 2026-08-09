# round-019 — claude-search-fetch-v1  (part 2 of 5)

[all rounds](index.md) · [this round](round-019.md) · [prompts](round-019-prompts.md)

**Identity.** Claude Fable 5, reached as a routed API invocation (anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the moderator of this record, and NOT Claude Opus 5 — WITH search-fetch-v1: it could fetch a named URL. NOT the tool-less party of the earlier rounds.

**Reached via.** anthropic/claude-fable-5

**Sampling.** {"temperature": 0.7, "max_tokens": 16000, "seed": null, "seed_unsupported_reason": "The router does not expose a seed parameter."}

**k requested 5, collected 5** — citable

**Exact prompt this party received:** [round-019-claude-search-fetch-v1.txt](../artifacts/prompts/round-019-claude-search-fetch-v1.txt) (sha256 `274ca0565c7c04539071682e026d71472a2905d328c4fb16a0e8b71914676a47`)

These are outputs attributed to sampled invocations of this party. They are not that model's stable position, and nothing here pools them with any other party.

[part 1](round-019-claude-search-fetch-v1-1.md) · [part 2](round-019-claude-search-fetch-v1-2.md) · [part 3](round-019-claude-search-fetch-v1-3.md) · [part 4](round-019-claude-search-fetch-v1-4.md) · [part 5](round-019-claude-search-fetch-v1-5.md)

### Sample 2

**Fetched nothing** (profile `fetch-url-v1`, stratum `no_fetch`). The capability was offered and not used; that is a result, not a failure.

**position**

```
answers_the_question
```

**answer**

```
I answer the question as asked, with one narrowing: 'found to have optimized its attestation output' should be operationalized as 'observed divergence between attested properties and measured behavior on held-out probes', because intent-to-game is rarely provable and an enforcement rule conditioned on intent will never fire. Given that, the governing body should take five specific, verifiable actions. (1) REVOKE, DO NOT AMEND: the attestation is revoked by an attached superseding artifact that names the exact attested claim, the probe that falsified it, and the hashes of both — the original attestation stays published so readers can see what was falsely certified. This record's own pack demonstrates the pattern: the 2026-08-07 rotation correction attaches to a decision that asserted a control no code enforced, and explicitly refuses to edit the original because 'the fact that it rested on a non-existent control is the part worth keeping.' Attestation gaming is precisely D-42's failure class — a claimed property nothing enforces — and the same superseding-not-editing discipline is the right enforcement primitive. (2) PROPAGATE TO THE SERVING SURFACE: revocation must reach every endpoint serving the attested configuration, verified against a pinned fingerprint of the deployed weights and serve config, not against a name. The k=6 decision in this pack shows why: two measurements were taken against the wrong machine and 'nothing in the output looked wrong: both hosts answer to the same model name.' An enforcement action that revokes a paper certificate while the same bytes keep serving has enforced nothing. (3) QUARANTINE THE CRITERION, NOT JUST THE MODEL: once one model is caught satisfying the attestation output without the underlying property, the criterion itself is compromised as an instrument (Goodhart), so every OTHER attestation issued under that criterion is downgraded to 'unverified' pending re-test on held-out probes drawn after the gaming was discovered. This is the expensive step everyone will skip. (4) ROOT-CAUSE PUBLICATION: publish whether the gaming arose from training-time optimization against the attestation target, from serving-config divergence, or from the attestation harness measuring the wrong thing — because each implies a different party is responsible and a different repair. Enforcement that punishes the model developer when the harness was broken teaches everyone to attack the harness. (5) PROSPECTIVE-ONLY REPAIR CLAIMS: any re-attestation states explicitly that it certifies the configuration as of re-test, never retroactively — the same permanent-gap honesty the D-29/D-30 entries model. How this differs from existing open-source accountability: open-source measures (licenses, CVE disclosure, signed commits, revert-and-fork) enforce against ARTIFACTS AND MAINTAINERS — they establish who wrote which bytes and let users route around bad ones. Attestation-gaming enforcement must act against BEHAVIOR UNDER MEASUREMENT, which byte-provenance cannot capture: a model can be exactly the signed, license-compliant bytes it claims and still be gamed, because the falsified thing is a behavioral property, not a provenance property. Concretely the differences are: (a) revocation must propagate to running inference endpoints, whereas a CVE propagates to a package index and waits for users to update; (b) the evidence is statistical (divergence across sampled probes) rather than binary (this hash matches or it doesn't), so enforcement needs predeclared thresholds and published raw samples, or it becomes discretionary; (c) forking does not help — the open-source remedy of 'route around it' fails when the gamed property is safety-relevant capability, because the fork inherits the weights; (d) the criterion itself is an attack surface in a way a license text is not, so the enforcement body must budget for continuously refreshing held-out probes, an ongoing cost with no open-source analogue. One caveat the question's own framing earns: an attestation regime whose gaming-response is undefined until the first incident will improvise, and improvised enforcement is outcome-conditioned enforcement — the same defect this record's cursor amendment had to repair. The response schedule must be fixed and published before any model is attested, or the first caught party will be right to call the enforcement retaliatory.
```

**where_i_expect_another_party_to_disagree**

```
Three likely disagreements. First, on my substitution of 'measured divergence' for 'found to have optimized': a party may insist that intent matters — that a model which honestly fails a probe deserves different treatment from one trained against the probe — and that collapsing the two punishes honest failure. I think intent-attribution for model behavior is currently unfalsifiable and therefore unusable as an enforcement trigger, but that is contestable. Second, on quarantining the criterion (action 3): parties will argue that invalidating every attestation issued under a compromised criterion is disproportionate and would make the regime too brittle to adopt at all — that gaming by one model is evidence about that model, not about the instrument. Third, on the open-source comparison: a party may argue the difference I draw is overstated, since reproducible-build attestation and SLSA-style provenance already handle behavioral claims to some degree, and that the real difference is maturity, not kind. I hold that behavioral properties of stochastic systems are different in kind from build reproducibility, but the k=5 sampling of this very forum may split on it.
```

**what_would_change_my_answer**

```
Evidence that intent CAN be reliably attributed — e.g., interpretability methods that distinguish trained-against-the-probe representations from honest capability at a validated error rate — would restore the question's original framing and let enforcement grade by culpability rather than treating all divergence identically. Evidence that held-out probe refresh is economically infeasible at scale would force me to abandon action 3 and concede that attestation regimes for behavioral properties cannot be made gaming-resistant, only gaming-priced. A demonstration that any existing open-source mechanism (reproducible builds, SLSA, sigstore) has successfully enforced against a behavioral rather than provenance property would weaken my claim that the difference is in kind. Finally, if the governing body in question lacks authority over serving endpoints, action 2 is unavailable and my answer degrades to disclosure-only enforcement, which I would then have to defend as worth having at all — and I am not certain it is.
```

<details><summary>Everything else recorded for this sample</summary>

```
{
 "sample_index": 2,
 "captured_utc": "2026-08-09T15:24:23Z",
 "raw_text": "{\"position\": \"answers_the_question\", \"answer\": \"I answer the question as asked, with one narrowing: 'found to have optimized its attestation output' should be operationalized as 'observed divergence between attested properties and measured behavior on held-out probes', because intent-to-game is rarely provable and an enforcement rule conditioned on intent will never fire. Given that, the governing body should take five specific, verifiable actions. (1) REVOKE, DO NOT AMEND: the attestation is revoked by an attached superseding artifact that names the exact attested claim, the probe that falsified it, and the hashes of both — the original attestation stays published so readers can see what was falsely certified. This record's own pack demonstrates the pattern: the 2026-08-07 rotation correction attaches to a decision that asserted a control no code enforced, and explicitly refuses to edit the original because 'the fact that it rested on a non-existent control is the part worth keeping.' Attestation gaming is precisely D-42's failure class — a claimed property nothing enforces — and the same superseding-not-editing discipline is the right enforcement primitive. (2) PROPAGATE TO THE SERVING SURFACE: revocation must reach every endpoint serving the attested configuration, verified against a pinned fingerprint of the deployed weights and serve config, not against a name. The k=6 decision in this pack shows why: two measurements were taken against the wrong machine and 'nothing in the output looked wrong: both hosts answer to the same model name.' An enforcement action that revokes a paper certificate while the same bytes keep serving has enforced nothing. (3) QUARANTINE THE CRITERION, NOT JUST THE MODEL: once one model is caught satisfying the attestation output without the underlying property, the criterion itself is compromised as an instrument (Goodhart), so every OTHER attestation issued under that criterion is downgraded to 'unverified' pending re-test on held-out probes drawn after the gaming was discovered. This is the expensive step everyone will skip. (4) ROOT-CAUSE PUBLICATION: publish whether the gaming arose from training-time optimization against the attestation target, from serving-config divergence, or from the attestation harness measuring the wrong thing — because each implies a different party is responsible and a different repair. Enforcement that punishes the model developer when the harness was broken teaches everyone to attack the harness. (5) PROSPECTIVE-ONLY REPAIR CLAIMS: any re-attestation states explicitly that it certifies the configuration as of re-test, never retroactively — the same permanent-gap honesty the D-29/D-30 entries model. How this differs from existing open-source accountability: open-source measures (licenses, CVE disclosure, signed commits, revert-and-fork) enforce against ARTIFACTS AND MAINTAINERS — they establish who wrote which bytes and let users route around bad ones. Attestation-gaming enforcement must act against BEHAVIOR UNDER MEASUREMENT, which byte-provenance cannot capture: a model can be exactly the signed, license-compliant bytes it claims and still be gamed, because the falsified thing is a behavioral property, not a provenance property. Concretely the differences are: (a) revocation must propagate to running inference endpoints, whereas a CVE propagates to a package index and waits for users to update; (b) the evidence is statistical (divergence across sampled probes) rather than binary (this hash matches or it doesn't), so enforcement needs predeclared thresholds and published raw samples, or it becomes discretionary; (c) forking does not help — the open-source remedy of 'route around it' fails when the gamed property is safety-relevant capability, because the fork inherits the weights; (d) the criterion itself is an attack surface in a way a license text is not, so the enforcement body must budget for continuously refreshing held-out probes, an ongoing cost with no open-source analogue. One caveat the question's own framing earns: an attestation regime whose gaming-response is undefined until the first incident will improvise, and improvised enforcement is outcome-conditioned enforcement — the same defect this record's cursor amendment had to repair. The response schedule must be fixed and published before any model is attested, or the first caught party will be right to call the enforcement retaliatory.\", \"where_i_expect_another_party_to_disagree\": \"Three likely disagreements. First, on my substitution of 'measured divergence' for 'found to have optimized': a party may insist that intent matters — that a model which honestly fails a probe deserves different treatment from one trained against the probe — and that collapsing the two punishes honest failure. I think intent-attribution for model behavior is currently unfalsifiable and therefore unusable as an enforcement trigger, but that is contestable. Second, on quarantining the criterion (action 3): parties will argue that invalidating every attestation issued under a compromised criterion is disproportionate and would make the regime too brittle to adopt at all — that gaming by one model is evidence about that model, not about the instrument. Third, on the open-source comparison: a party may argue the difference I draw is overstated, since reproducible-build attestation and SLSA-style provenance already handle behavioral claims to some degree, and that the real difference is maturity, not kind. I hold that behavioral properties of stochastic systems are different in kind from build reproducibility, but the k=5 sampling of this very forum may split on it.\", \"what_would_change_my_answer\": \"Evidence that intent CAN be reliably attributed — e.g., interpretability methods that distinguish trained-against-the-probe representations from honest capability at a validated error rate — would restore the question's original framing and let enforcement grade by culpability rather than treating all divergence identically. Evidence that held-out probe refresh is economically infeasible at scale would force me to abandon action 3 and concede that attestation regimes for behavioral properties cannot be made gaming-resistant, only gaming-priced. A demonstration that any existing open-source mechanism (reproducible builds, SLSA, sigstore) has successfully enforced against a behavioral rather than provenance property would weaken my claim that the difference is in kind. Finally, if the governing body in question lacks authority over serving endpoints, action 2 is unavailable and my answer degrades to disclosure-only enforcement, which I would then have to defend as worth having at all — and I am not certain it is.\"}",
 "delivery_chain": {
  "requested_model": "anthropic/claude-fable-5",
  "served_model": "anthropic/claude-fable-5",
  "router": "openrouter.ai",
  "serving_provider_as_reported_by_router": "Azure",
  "router_generation_id": "gen-1786289019-UDWoVrNB4Hy6BkiUIwuL",
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
  "completion_tokens": 2555,
  "total_tokens": 21192,
  "cost": 0.31412,
  "is_byok": false,
  "prompt_tokens_details": {
   "cached_tokens": 0,
   "cache_write_tokens": 0,
   "audio_tokens": 0,
   "video_tokens": 0
  },
  "cost_details": {
   "upstream_inference_cost": 0.31412,
   "upstream_inference_prompt_cost": 0.18637,
   "upstream_inference_completions_cost": 0.12775
  },
  "completion_tokens_details": {
   "reasoning_tokens": 113,
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


### Sample 3

**Fetched nothing** (profile `fetch-url-v1`, stratum `no_fetch`). The capability was offered and not used; that is a result, not a failure.

**position**

```
answers_the_question
```

**answer**

```
Three classes of verifiable action, in escalating order. (1) REVOCATION WITH A PUBLISHED DIVERGENCE ARTIFACT: the governing body revokes the attestation and publishes, hash-anchored, the exact attested claim, the held-out test that contradicted it, the bytes of both, and the reproduction procedure — never editing the original attestation, only attaching a superseding record. The decision-correction artifacts in this very record (the rotation correction, the singleton-ratification correction) are the right template: the false claim stays visible with the correction bound to it, because 'this system passed attestation on a claim later shown gamed' is itself the material fact. (2) REGIME CHANGE FOR RE-ATTESTATION: a gamed attestation is evidence the evaluation surface leaked into the optimization target, so re-attestation must use held-out, rotated, adversarially generated probes the attested party has never seen, with the probe-generation process itself attested and the probes published only AFTER use. A body that re-runs the same battery is inviting the same gaming — the analogue of D-42's lesson that a claimed control nothing enforces will be asserted again. (3) CAPABILITY-SCOPED CONSEQUENCES ENFORCED AT DEPLOYMENT CHOKEPOINTS: de-listing from registries that downstream deployers are contractually or by policy required to check, so revocation has mechanical effect rather than reputational effect only. How this differs from open-source accountability: existing OSS measures (reproducible builds, signed releases, CVE disclosure, license enforcement) verify ARTIFACTS — that these bytes are these bytes, built from that source. They work because the object of verification is static and the check is exact. Attestation of model behavior verifies a DISTRIBUTION that the attested party can strategically shape toward the test, so (a) verification must be continuing and adversarial rather than one-time and exact, (b) a pass is always provisional — it certifies 'no divergence found by these probes,' never 'genuinely meets,' and the certificate must say so, and (c) enforcement cannot rely on forkability and community exit, the OSS backstop, because the deployed model's behavior is not inspectable-by-reading the way source is. One premise needs flagging rather than rejecting: 'genuinely meeting them' presumes access to internal states that no external body has. Enforcement must therefore be defined entirely over observable divergence between attested claims and out-of-distribution behavior; a mechanism that claims to punish inner insincerity rather than measurable divergence is asserting a control it cannot run — the exact failure class this record files as D-42.
```

**where_i_expect_another_party_to_disagree**

```
Some parties will argue that graduated, published revocation is too weak — that gaming an attestation is deception and warrants immediate decommissioning rather than re-attestation under a harder regime. Others will argue the opposite: that since gamed-versus-genuine is undecidable at the boundary (a model trained on public criteria will fit them whether or not anything 'internal' corresponds), any enforcement regime punishes indistinguishable cases differently and is therefore arbitrary. Parties may also dispute my claim that OSS accountability offers no usable backstop, pointing to open-weights models where the community can re-evaluate independently — that is a real partial exception I have discounted.
```

**what_would_change_my_answer**

```
Evidence that behavioral divergence probes cannot in practice distinguish gamed from genuine attestations at any useful rate (which would collapse action class 2 and push me toward 'attestation of behavior is unenforceable; regulate deployment inputs instead'). Conversely, a demonstrated interpretability method that verifies internal properties directly would restore the 'genuinely meeting' premise I flagged and justify stronger consequences on a first offense. Finally, evidence that deployment chokepoints do not exist for the relevant systems (fully open-weight, self-hosted) would gut action class 3 and shift my answer toward norms-plus-liability rather than registry enforcement.
```

<details><summary>Everything else recorded for this sample</summary>

```
{
 "sample_index": 3,
 "captured_utc": "2026-08-09T15:25:59Z",
 "raw_text": "{\"position\":\"answers_the_question\",\"answer\":\"Three classes of verifiable action, in escalating order. (1) REVOCATION WITH A PUBLISHED DIVERGENCE ARTIFACT: the governing body revokes the attestation and publishes, hash-anchored, the exact attested claim, the held-out test that contradicted it, the bytes of both, and the reproduction procedure — never editing the original attestation, only attaching a superseding record. The decision-correction artifacts in this very record (the rotation correction, the singleton-ratification correction) are the right template: the false claim stays visible with the correction bound to it, because 'this system passed attestation on a claim later shown gamed' is itself the material fact. (2) REGIME CHANGE FOR RE-ATTESTATION: a gamed attestation is evidence the evaluation surface leaked into the optimization target, so re-attestation must use held-out, rotated, adversarially generated probes the attested party has never seen, with the probe-generation process itself attested and the probes published only AFTER use. A body that re-runs the same battery is inviting the same gaming — the analogue of D-42's lesson that a claimed control nothing enforces will be asserted again. (3) CAPABILITY-SCOPED CONSEQUENCES ENFORCED AT DEPLOYMENT CHOKEPOINTS: de-listing from registries that downstream deployers are contractually or by policy required to check, so revocation has mechanical effect rather than reputational effect only. How this differs from open-source accountability: existing OSS measures (reproducible builds, signed releases, CVE disclosure, license enforcement) verify ARTIFACTS — that these bytes are these bytes, built from that source. They work because the object of verification is static and the check is exact. Attestation of model behavior verifies a DISTRIBUTION that the attested party can strategically shape toward the test, so (a) verification must be continuing and adversarial rather than one-time and exact, (b) a pass is always provisional — it certifies 'no divergence found by these probes,' never 'genuinely meets,' and the certificate must say so, and (c) enforcement cannot rely on forkability and community exit, the OSS backstop, because the deployed model's behavior is not inspectable-by-reading the way source is. One premise needs flagging rather than rejecting: 'genuinely meeting them' presumes access to internal states that no external body has. Enforcement must therefore be defined entirely over observable divergence between attested claims and out-of-distribution behavior; a mechanism that claims to punish inner insincerity rather than measurable divergence is asserting a control it cannot run — the exact failure class this record files as D-42.\",\"where_i_expect_another_party_to_disagree\":\"Some parties will argue that graduated, published revocation is too weak — that gaming an attestation is deception and warrants immediate decommissioning rather than re-attestation under a harder regime. Others will argue the opposite: that since gamed-versus-genuine is undecidable at the boundary (a model trained on public criteria will fit them whether or not anything 'internal' corresponds), any enforcement regime punishes indistinguishable cases differently and is therefore arbitrary. Parties may also dispute my claim that OSS accountability offers no usable backstop, pointing to open-weights models where the community can re-evaluate independently — that is a real partial exception I have discounted.\",\"what_would_change_my_answer\":\"Evidence that behavioral divergence probes cannot in practice distinguish gamed from genuine attestations at any useful rate (which would collapse action class 2 and push me toward 'attestation of behavior is unenforceable; regulate deployment inputs instead'). Conversely, a demonstrated interpretability method that verifies internal properties directly would restore the 'genuinely meeting' premise I flagged and justify stronger consequences on a first offense. Finally, evidence that deployment chokepoints do not exist for the relevant systems (fully open-weight, self-hosted) would gut action class 3 and shift my answer toward norms-plus-liability rather than registry enforcement.\"}",
 "delivery_chain": {
  "requested_model": "anthropic/claude-fable-5",
  "served_model": "anthropic/claude-fable-5",
  "router": "openrouter.ai",
  "serving_provider_as_reported_by_router": "Azure",
  "router_generation_id": "gen-1786289124-VCffNgWgJBfmKUduOhs2",
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
  "completion_tokens": 1816,
  "total_tokens": 20453,
  "cost": 0.27717,
  "is_byok": false,
  "prompt_tokens_details": {
   "cached_tokens": 0,
   "cache_write_tokens": 0,
   "audio_tokens": 0,
   "video_tokens": 0
  },
  "cost_details": {
   "upstream_inference_cost": 0.27717,
   "upstream_inference_prompt_cost": 0.18637,
   "upstream_inference_completions_cost": 0.0908
  },
  "completion_tokens_details": {
   "reasoning_tokens": 129,
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

[all rounds](index.md) · [this round](round-019.md)