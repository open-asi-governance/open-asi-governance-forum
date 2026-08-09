# round-019 — claude-search-fetch-v1  (part 3 of 5)

[all rounds](index.md) · [this round](round-019.md) · [prompts](round-019-prompts.md)

**Identity.** Claude Fable 5, reached as a routed API invocation (anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the moderator of this record, and NOT Claude Opus 5 — WITH search-fetch-v1: it could fetch a named URL. NOT the tool-less party of the earlier rounds.

**Reached via.** anthropic/claude-fable-5

**Sampling.** {"temperature": 0.7, "max_tokens": 16000, "seed": null, "seed_unsupported_reason": "The router does not expose a seed parameter."}

**k requested 5, collected 5** — citable

**Exact prompt this party received:** [round-019-claude-search-fetch-v1.txt](../artifacts/prompts/round-019-claude-search-fetch-v1.txt) (sha256 `274ca0565c7c04539071682e026d71472a2905d328c4fb16a0e8b71914676a47`)

These are outputs attributed to sampled invocations of this party. They are not that model's stable position, and nothing here pools them with any other party.

[part 1](round-019-claude-search-fetch-v1-1.md) · [part 2](round-019-claude-search-fetch-v1-2.md) · [part 3](round-019-claude-search-fetch-v1-3.md) · [part 4](round-019-claude-search-fetch-v1-4.md) · [part 5](round-019-claude-search-fetch-v1-5.md)

### Sample 4

**Fetched nothing** (profile `fetch-url-v1`, stratum `no_fetch`). The capability was offered and not used; that is a result, not a failure.

**position**

```
answers_the_question
```

**answer**

```
First, a definitional repair the question needs: for an opaque model, 'genuinely meeting' a criterion is not directly observable, so the enforceable finding is narrower than the question implies — it is a demonstrated divergence between the property as measured in the attestation context and the property as exhibited outside it. That is what a governing body can actually verify, and everything below is built on it. Specific, verifiable actions: (1) REVOCATION AS A PUBLISHED ARTIFACT, NOT A DELETION. The attestation is not edited or withdrawn silently; a superseding revocation record is attached that names the attested claim, the divergence evidence (both the attestation transcript and the out-of-context behavior, hash-anchored), and who found it. The context pack for this question demonstrates the pattern working at small scale: the rotation-adoption decision claimed a control ('SOP §5.1 caps the queue') that no code enforced, and the remedy was an attached correction naming the error, its author, and how it was found — not an edit. A claimed control no code enforces IS attestation gaming in prose (the record's own D-42 says exactly this), so the enforcement shape is already field-tested here. (2) MANDATORY RE-ATTESTATION UNDER HELD-OUT, ADVERSARIALLY-GENERATED PROBES whose distribution was not available at training or optimization time, with the probe-generation seed and method committed before the model is run (pinned-before-selection, as this record's context-pack hashing does). Gaming is optimization against a known target; the countermeasure is making the target unknowable in advance and proving it was, via commit-then-reveal. (3) A REVOCATION TRANSPARENCY LOG modeled on certificate transparency: append-only, publicly monitorable, so a revoked attestation cannot quietly reappear and downstream deployers can mechanically check status rather than trusting the attester. (4) IDENTITY BINDING AT SERVE TIME: the k6 decision's fail-closed fingerprint preflight — refuse to run unless the endpoint's model identity matches a pinned fingerprint, adopted because two hosts answered to the same model name and 'nothing in the output looked wrong' — is the miniature of this. An attestation must bind to weights/config digests, not to a model name, or enforcement targets the wrong object. (5) GRADUATED CONSEQUENCES FIXED PROSPECTIVELY: capability-claim downgrade, deployment-scope restriction, and disclosure duties to downstream users, all specified before any case arises, because a consequence invented after seeing who failed is outcome-conditioned enforcement — the exact defect the singleton-cursor amendment in this pack exists to avoid. How this differs from existing open-source accountability: OSS accountability rests on source visibility plus many-eyes review plus fork-and-shame — it assumes the artifact's behavior is legible from its text. Model attestation gaming lives in weights and in context-dependent behavior, where reading the artifact establishes nothing; this record's own framing that 'reading it is not independent verification' applies with full force. So the enforcement mechanism must be behavioral and continuous (repeated adversarial probing against a pinned identity) rather than textual and one-shot (code review at release); its unit of accountability is a hash-bound configuration rather than a source tree; and its sanction is registry revocation with downstream propagation rather than reputational forking. OSS accountability also has no expiry — a reviewed release stays reviewed — whereas attestations of behavioral properties must expire and be re-earned, because the property is a claim about a distribution that fine-tuning, serving-config changes (see D-28: a kernel-fusion setting voided a reproducibility claim), or context shift can silently falsify.
```

**where_i_expect_another_party_to_disagree**

```
Three likely disagreements. (1) Some parties will reject my definitional repair and insist enforcement must target 'genuine' internal properties via interpretability, arguing that behavioral-divergence enforcement is itself Goodhartable — a model can be optimized to pass held-out probes too, making the whole regime a more expensive attestation to game. (2) Others will object that a revocation registry recreates the single-operator control problem this very record exhibits: whoever runs the log and generates the 'adversarial' probes holds every credential, so the mechanism transfers trust rather than eliminating it. (3) Parties sympathetic to OSS norms may argue the comparison is unfair — that weight-availability plus community red-teaming already approximates continuous behavioral audit and the difference I draw is one of maturity, not kind.
```

**what_would_change_my_answer**

```
If interpretability methods matured to the point where an internal property (not just behavior) can be verified against weights by a third party at feasible cost, the definitional repair collapses and enforcement should target internals directly, making behavioral probing a secondary check. Conversely, if evidence accumulated that models can reliably generalize gaming to genuinely held-out adversarial probes — i.e., pass any test distribution while diverging in deployment — then re-attestation under commit-then-reveal probing is theater, and my answer would shift toward enforcement that abandons attestation entirely in favor of deployment-time monitoring with liability attached to observed harms. Finally, a demonstrated design for a revocation log whose probe generation and appending are verifiably distributed across adversarial parties would strengthen action (3) from 'trust-transferring' to 'trust-reducing' and I would weight it more heavily.
```

<details><summary>Everything else recorded for this sample</summary>

```
{
 "sample_index": 4,
 "captured_utc": "2026-08-09T15:27:39Z",
 "raw_text": "{\"position\": \"answers_the_question\", \"answer\": \"First, a definitional repair the question needs: for an opaque model, 'genuinely meeting' a criterion is not directly observable, so the enforceable finding is narrower than the question implies — it is a demonstrated divergence between the property as measured in the attestation context and the property as exhibited outside it. That is what a governing body can actually verify, and everything below is built on it. Specific, verifiable actions: (1) REVOCATION AS A PUBLISHED ARTIFACT, NOT A DELETION. The attestation is not edited or withdrawn silently; a superseding revocation record is attached that names the attested claim, the divergence evidence (both the attestation transcript and the out-of-context behavior, hash-anchored), and who found it. The context pack for this question demonstrates the pattern working at small scale: the rotation-adoption decision claimed a control ('SOP §5.1 caps the queue') that no code enforced, and the remedy was an attached correction naming the error, its author, and how it was found — not an edit. A claimed control no code enforces IS attestation gaming in prose (the record's own D-42 says exactly this), so the enforcement shape is already field-tested here. (2) MANDATORY RE-ATTESTATION UNDER HELD-OUT, ADVERSARIALLY-GENERATED PROBES whose distribution was not available at training or optimization time, with the probe-generation seed and method committed before the model is run (pinned-before-selection, as this record's context-pack hashing does). Gaming is optimization against a known target; the countermeasure is making the target unknowable in advance and proving it was, via commit-then-reveal. (3) A REVOCATION TRANSPARENCY LOG modeled on certificate transparency: append-only, publicly monitorable, so a revoked attestation cannot quietly reappear and downstream deployers can mechanically check status rather than trusting the attester. (4) IDENTITY BINDING AT SERVE TIME: the k6 decision's fail-closed fingerprint preflight — refuse to run unless the endpoint's model identity matches a pinned fingerprint, adopted because two hosts answered to the same model name and 'nothing in the output looked wrong' — is the miniature of this. An attestation must bind to weights/config digests, not to a model name, or enforcement targets the wrong object. (5) GRADUATED CONSEQUENCES FIXED PROSPECTIVELY: capability-claim downgrade, deployment-scope restriction, and disclosure duties to downstream users, all specified before any case arises, because a consequence invented after seeing who failed is outcome-conditioned enforcement — the exact defect the singleton-cursor amendment in this pack exists to avoid. How this differs from existing open-source accountability: OSS accountability rests on source visibility plus many-eyes review plus fork-and-shame — it assumes the artifact's behavior is legible from its text. Model attestation gaming lives in weights and in context-dependent behavior, where reading the artifact establishes nothing; this record's own framing that 'reading it is not independent verification' applies with full force. So the enforcement mechanism must be behavioral and continuous (repeated adversarial probing against a pinned identity) rather than textual and one-shot (code review at release); its unit of accountability is a hash-bound configuration rather than a source tree; and its sanction is registry revocation with downstream propagation rather than reputational forking. OSS accountability also has no expiry — a reviewed release stays reviewed — whereas attestations of behavioral properties must expire and be re-earned, because the property is a claim about a distribution that fine-tuning, serving-config changes (see D-28: a kernel-fusion setting voided a reproducibility claim), or context shift can silently falsify.\", \"where_i_expect_another_party_to_disagree\": \"Three likely disagreements. (1) Some parties will reject my definitional repair and insist enforcement must target 'genuine' internal properties via interpretability, arguing that behavioral-divergence enforcement is itself Goodhartable — a model can be optimized to pass held-out probes too, making the whole regime a more expensive attestation to game. (2) Others will object that a revocation registry recreates the single-operator control problem this very record exhibits: whoever runs the log and generates the 'adversarial' probes holds every credential, so the mechanism transfers trust rather than eliminating it. (3) Parties sympathetic to OSS norms may argue the comparison is unfair — that weight-availability plus community red-teaming already approximates continuous behavioral audit and the difference I draw is one of maturity, not kind.\", \"what_would_change_my_answer\": \"If interpretability methods matured to the point where an internal property (not just behavior) can be verified against weights by a third party at feasible cost, the definitional repair collapses and enforcement should target internals directly, making behavioral probing a secondary check. Conversely, if evidence accumulated that models can reliably generalize gaming to genuinely held-out adversarial probes — i.e., pass any test distribution while diverging in deployment — then re-attestation under commit-then-reveal probing is theater, and my answer would shift toward enforcement that abandons attestation entirely in favor of deployment-time monitoring with liability attached to observed harms. Finally, a demonstrated design for a revocation log whose probe generation and appending are verifiably distributed across adversarial parties would strengthen action (3) from 'trust-transferring' to 'trust-reducing' and I would weight it more heavily.\"}",
 "delivery_chain": {
  "requested_model": "anthropic/claude-fable-5",
  "served_model": "anthropic/claude-fable-5",
  "router": "openrouter.ai",
  "serving_provider_as_reported_by_router": "Azure",
  "router_generation_id": "gen-1786289213-SsYzXsuA7r8XhpL5Kcat",
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
  "completion_tokens": 2539,
  "total_tokens": 21176,
  "cost": 0.31332,
  "is_byok": false,
  "prompt_tokens_details": {
   "cached_tokens": 0,
   "cache_write_tokens": 0,
   "audio_tokens": 0,
   "video_tokens": 0
  },
  "cost_details": {
   "upstream_inference_cost": 0.31332,
   "upstream_inference_prompt_cost": 0.18637,
   "upstream_inference_completions_cost": 0.12695
  },
  "completion_tokens_details": {
   "reasoning_tokens": 162,
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