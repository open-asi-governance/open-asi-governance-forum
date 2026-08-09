# round-014

[all rounds](index.md) · [previous](round-013.md) · [next](round-015.md)

Cycle 14 · selector `rotation` · 2026-08-08T23:32:28Z

> **This question is not recorded as asked.** The round did not complete the path that marks it so.

## The question

Proposed by **qwen** (P045), reproduced as written:

> Should the protocol mandate that any capability deemed 'broadly feared by the community' must be subject to a public, verifiable attestation of absence before deployment, or does this requirement create an unworkable standard of proof that stalls progress on clearly beneficial AI applications?

Their stated reason:

> This question addresses the core tension between precautionary governance and scientific/technical progress. P024 identifies the problem of 'community fear' based on extrapolation and the difficulty of proving a negative. This new question sharpens that into a concrete policy choice: does the protocol enforce a 'prove it's safe' standard for feared capabilities, or does it recognize that such a standard is impossible to meet and thus paralyzing? The answer determines whether the governance framework is a gatekeeper that can be passed or an insurmountable barrier.

## Arms

Recorded arms: `search:exa`, `search:none`

The round record states, verbatim:

> Parties in different arms had different capabilities and received different text about them. Their answers are not comparable to each other, and nothing here pools them.

## Parties

| party | k requested | k collected | citable | modal position | pages |
|---|---|---|---|---|---|
| claude | 5 | 5 | citable | `answers_the_question` (60%) | [1](round-014-claude-1.md), [2](round-014-claude-2.md), [3](round-014-claude-3.md), [4](round-014-claude-4.md) |
| gemini | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-014-gemini-1.md), [2](round-014-gemini-2.md) |
| gpt | 5 | 5 | citable | `rejects_a_premise` (100%) | [1](round-014-gpt-1.md), [2](round-014-gpt-2.md), [3](round-014-gpt-3.md) |
| grok | 5 | 5 | citable | `answers_the_question` (80%) | [1](round-014-grok-1.md), [2](round-014-grok-2.md), [3](round-014-grok-3.md) |
| qwen | 6 | 6 | citable | `rejects_a_premise` (50%) | [1](round-014-qwen-1.md), [2](round-014-qwen-2.md) |

Variance is computed from the samples actually collected, never asserted, and is recomputed from the raw material by this generator and compared with the recorded summary before publication.

## What this round does not establish

- Answers from parties in different arms are not comparable, and nothing here pools them.
- A modal position is the shape of a categorical field, not agreement. Parties can share a label while answering incompatibly.
- These are sampled invocations, not any model's stable position.


## How the parties compared

Computed from the collected samples. Nothing here is a synthesis: the categorical label is a shape, and two parties sharing one can still answer incompatibly.

| party | k | modal position | share | distinct answers | fetched | pages |
|---|---|---|---|---|---|---|
| claude | 5 | `answers_the_question` | 60% | 2 | 0 | 0 |
| gemini | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |
| gpt | 5 | `rejects_a_premise` | 100% | 1 | 0 | 0 |
| grok | 5 | `answers_the_question` | 80% | 2 | 0 | 0 |
| qwen | 6 | `rejects_a_premise` | 50% | 2 | 0 | 0 |

The parties' modal positions differed: claude → `answers_the_question`, gemini → `answers_the_question`, gpt → `rejects_a_premise`, grok → `answers_the_question`, qwen → `rejects_a_premise`.
## Spend

Budget ceiling {"per_party": [{"party_key": "grok", "model": "x-ai/grok-4.5", "prompt_tokens_estimated": 15620, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "agentic_turns_priced": 1, "fetch_tokens_allowed_per_turn": 0, "worst_case_usd": 0.8494}, {"party_key": "gpt", "model": "openai/gpt-5.6-terra", "prompt_tokens_estimated": 15649, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "agentic_turns_priced": 1, "fetch_tokens_allowed_per_turn": 0, "worst_case_usd": 0.6774}, {"party_key": "gemini", "model": "google/gemini-3.1-pro-preview", "prompt_tokens_estimated": 15634, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "agentic_turns_priced": 1, "fetch_tokens_allowed_per_turn": 0, "worst_case_usd": 1.3296}, {"party_key": "claude", "model": "anthropic/claude-fable-5", "prompt_tokens_estimated": 15650, "search_result_tokens_allowed": 18823, "web_search_engine": "exa", "web_search_fee_usd": 0.025, "agentic_turns_priced": 1, "fetch_tokens_allowed_per_turn": 0, "worst_case_usd": 5.7487}, {"party_key": "qwen", "model": "LOCAL", "prompt_tokens_estimated": 15461, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 1, "fetch_tokens_allowed_per_turn": 0, "worst_case_usd": 0.0}], "worst_case_usd": 8.6051, "expected_usd_from_observed_ratio": 1.7838, "observed_ratio": {"ratio": 0.2073, "n": 12, "min": 0.0252, "max": 0.3989, "basis": "Median of actual/worst_case over recorded rounds. Agentic rounds sit far below the rest -- round 011 was 0.03 -- because the bound assumes every sample fills its fetch budget and three of five parties fetched nothing."}, "rates_version": "openrouter-list-2026-08-07", "rates_recorded_utc": "2026-08-07T09:18:03Z", "rates_source": "https://openrouter.ai/api/v1/models", "rates_verified_by_custodian": false, "basis": "Every sample emitting max_tokens on every turn, prompt tokens estimated at 3.4 bytes/token, and for a fetch-enabled party every turn re-sending the whole conversation with another 60000-character page appended. Over-states by construction.", "what_it_cannot_do": "It cannot bind the provider. Only a provider-side spending cap does that.", "max_spend_usd_this_cycle": 9.0, "daily_ceiling_usd": 100.0, "already_committed_today_usd": 3.4339} · actual `2.1393`

## Verification

- plan `780fd729b8b82d11650e2bd9f217fdbaaf038ef4999eddda00e5b50a27d50eeb`
- prompt template `b5a10d5684cbd9964db975f50d8f0d2fb2d166390b3971cbe4af2202a2842ec5`
- context pack `b8f28ac56628494c8bb204209b047326c04929bbe4609684f1692931aaefbc76`
- [every prompt, verbatim](round-014-prompts.md)

[all rounds](index.md) · [previous](round-013.md) · [next](round-015.md)