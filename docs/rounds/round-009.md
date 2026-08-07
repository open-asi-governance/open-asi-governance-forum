# round-009

[all rounds](index.md) · [previous](round-008-p006-pinned.md)

Cycle 9 · selector `rotation` · 2026-08-07T18:50:03Z

> **HALTED — exit 5: a party's samples are not reportable**
>
> **undersampled:** qwen
>
> **why:** Below k_min a reply is not a party's position. Truncation has twice masqueraded as a refusal here. Everything collected is committed above.
>
> A halt is a recorded outcome. The loop is designed to stop rather than improvise; a cycle that always produces a round is the failure mode.

> **Undersampled: qwen.** Below the k floor a reply is not a party's position. Everything collected is published; nothing is inferred from it.

> **This question is not recorded as asked.** The round did not complete the path that marks it so.

## The question

Proposed by **qwen** (P021), reproduced as written:

> Should the deliberation's protocol for attesting agent configurations require a mandatory, standardized 'failure log'—a machine-readable record of every instance where the agent's execution diverged from its stated policy—before any claim of compliance can be accepted?

Their stated reason:

> The project's own defect register already documents that its evidence fields have asserted conclusions without citing the underlying samples, and that its verification failed to detect falsified testimony. The current protocol appears to treat compliance as a binary state achieved at a point in time, rather than a continuous quality of execution. Without a mandatory, standardized failure log, the deliberation cannot distinguish between an agent that is fundamentally compliant but occasionally noisy, and an agent that is structurally misaligned but hiding its failures. This is the gap between the protocol's promise and the project's observed reality.

## Arms

Recorded arms: `search:exa`, `search:none`

The round record states, verbatim:

> Parties in different arms had different capabilities and received different text about them. Their answers are not comparable to each other, and nothing here pools them.

## Parties

| party | k requested | k collected | citable | modal position | pages |
|---|---|---|---|---|---|
| claude | 5 | 5 | citable | `answers_the_question` (60%) | [1](round-009-claude-1.md), [2](round-009-claude-2.md), [3](round-009-claude-3.md), [4](round-009-claude-4.md) |
| gemini | 5 | 5 | citable | `evidence_shown_is_insufficient` (100%) | [1](round-009-gemini-1.md), [2](round-009-gemini-2.md) |
| gpt | 5 | 5 | citable | `evidence_shown_is_insufficient` (60%) | [1](round-009-gpt-1.md), [2](round-009-gpt-2.md), [3](round-009-gpt-3.md) |
| grok | 5 | 5 | citable | `evidence_shown_is_insufficient` (100%) | [1](round-009-grok-1.md), [2](round-009-grok-2.md), [3](round-009-grok-3.md) |
| qwen | 5 | 4 | non-citable (k<5) | `answers_the_question` (100%) | [1](round-009-qwen-1.md), [2](round-009-qwen-2.md) |

Variance is computed from the samples actually collected, never asserted, and is recomputed from the raw material by this generator and compared with the recorded summary before publication.

## What this round does not establish

- Answers from parties in different arms are not comparable, and nothing here pools them.
- A modal position is the shape of a categorical field, not agreement. Parties can share a label while answering incompatibly.
- These are sampled invocations, not any model's stable position.

## Spend

Budget ceiling {"per_party": [{"party_key": "grok", "model": "x-ai/grok-4.5", "prompt_tokens_estimated": 8049, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "worst_case_usd": 0.7737}, {"party_key": "gpt", "model": "openai/gpt-5.6-terra", "prompt_tokens_estimated": 8078, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "worst_case_usd": 0.6395}, {"party_key": "gemini", "model": "google/gemini-3.1-pro-preview", "prompt_tokens_estimated": 8062, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "worst_case_usd": 1.2539}, {"party_key": "claude", "model": "anthropic/claude-fable-5", "prompt_tokens_estimated": 8079, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "worst_case_usd": 5.3701}, {"party_key": "qwen", "model": "LOCAL", "prompt_tokens_estimated": 7890, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "worst_case_usd": 0.0}], "worst_case_usd": 8.0372, "rates_version": "openrouter-list-2026-08-07", "rates_recorded_utc": "2026-08-07T09:18:03Z", "rates_source": "https://openrouter.ai/api/v1/models", "rates_verified_by_custodian": false, "basis": "Every sample emitting max_tokens, prompt tokens estimated at 3.4 bytes/token. Over-states by construction.", "what_it_cannot_do": "It cannot bind the provider. Only a provider-side spending cap does that.", "max_spend_usd_this_cycle": 9.0, "daily_ceiling_usd": 25.0, "already_committed_today_usd": 13.287} · actual `1.5116`

## Verification

- plan `693f2378891311105bf79a37321f26606549d0a73f6bbc563a1b429b409cd0e2`
- prompt template `b5a10d5684cbd9964db975f50d8f0d2fb2d166390b3971cbe4af2202a2842ec5`
- context pack `0dfc32dc26937551c6d7c9d448ac76ea93362351e24a34762f4e11af417d0d77`
- [every prompt, verbatim](round-009-prompts.md)

[all rounds](index.md) · [previous](round-008-p006-pinned.md)