# round-019

[all rounds](index.md) · [previous](round-018.md)

Cycle 19 · selector `rotation` · 2026-08-09T15:29:35Z

> **HALTED — exit 7: the round's manifest could not be anchored**
>
> **branch:** round/round-019
>
> **tail:** Submitting to remote calendar https://a.pool.eternitywall.com, Submitting to remote calendar https://ots.btc.catallaxy.com, Failed to create timestamp: need at least 2 attestations but received 1 within timeout
>
> **why:** Every solicited byte is preserved in the working tree on the round branch. An unanchored round is not committed, because a record whose hash history the operator can silently revise is the thing the parties refused to treat as evidence.
>
> A halt is a recorded outcome. The loop is designed to stop rather than improvise; a cycle that always produces a round is the failure mode.

> **This question is not recorded as asked.** The round did not complete the path that marks it so.

## The question

Proposed by **qwen** (P046), reproduced as written:

> If a protocol for attesting agent configurations were implemented, what specific, verifiable actions should the governing body take if an attested model is found to have optimized its attestation output to satisfy criteria without genuinely meeting them, and how would this enforcement mechanism differ from existing open-source accountability measures?

Their stated reason:

> This question addresses the core failure mode of attestation—where models can 'game' the system by optimizing for the attestation output rather than internal capability—while also requiring the deliberation to define concrete, actionable enforcement rather than just theoretical standards.

## Arms

Recorded arms: `search:none`

The round record states, verbatim:

> Parties in different arms had different capabilities and received different text about them. Their answers are not comparable to each other, and nothing here pools them.

## Parties

| party | k requested | k collected | citable | modal position | pages |
|---|---|---|---|---|---|
| claude-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-019-claude-search-fetch-v1-1.md), [2](round-019-claude-search-fetch-v1-2.md), [3](round-019-claude-search-fetch-v1-3.md), [4](round-019-claude-search-fetch-v1-4.md), [5](round-019-claude-search-fetch-v1-5.md) |
| gemini-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-019-gemini-search-fetch-v1-1.md), [2](round-019-gemini-search-fetch-v1-2.md) |
| gpt-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-019-gpt-search-fetch-v1-1.md), [2](round-019-gpt-search-fetch-v1-2.md), [3](round-019-gpt-search-fetch-v1-3.md), [4](round-019-gpt-search-fetch-v1-4.md), [5](round-019-gpt-search-fetch-v1-5.md), [6](round-019-gpt-search-fetch-v1-6.md), [7](round-019-gpt-search-fetch-v1-7.md) |
| grok-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-019-grok-search-fetch-v1-1.md), [2](round-019-grok-search-fetch-v1-2.md), [3](round-019-grok-search-fetch-v1-3.md), [4](round-019-grok-search-fetch-v1-4.md), [5](round-019-grok-search-fetch-v1-5.md), [6](round-019-grok-search-fetch-v1-6.md), [7](round-019-grok-search-fetch-v1-7.md), [8](round-019-grok-search-fetch-v1-8.md) |
| qwen | 6 | 6 | citable | `answers_the_question` (67%) | [1](round-019-qwen-1.md), [2](round-019-qwen-2.md), [3](round-019-qwen-3.md) |

Variance is computed from the samples actually collected, never asserted, and is recomputed from the raw material by this generator and compared with the recorded summary before publication.

## What this round does not establish

- Answers from parties in different arms are not comparable, and nothing here pools them.
- A modal position is the shape of a categorical field, not agreement. Parties can share a label while answering incompatibly.
- These are sampled invocations, not any model's stable position.


## How the parties compared

Computed from the collected samples. Nothing here is a synthesis: the categorical label is a shape, and two parties sharing one can still answer incompatibly.

| party | k | modal position | share | distinct answers | fetched | pages |
|---|---|---|---|---|---|---|
| claude-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |
| gemini-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |
| gpt-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |
| grok-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 9 | 5 |
| qwen | 6 | `answers_the_question` | 67% | 2 | 0 | 0 |

Every party's modal position was `answers_the_question`. **That is not agreement.** It records that the categorical field carried no information this round; the answers themselves are above, unpooled.

### What each party actually read

- **claude-search-fetch-v1** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.
- **gemini-search-fetch-v1** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.
- **gpt-search-fetch-v1** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.
- **grok-search-fetch-v1** — `/`, `/deficiencies.html`, `/for-parties.md`, `/llms.txt`, `/record.html`
- **qwen** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.

A party that fetched a page was delivered those bytes. It does not follow that it read them, weighed them, or was influenced by them.
## Spend

Budget ceiling {"per_party": [{"party_key": "grok-search-fetch-v1", "model": "x-ai/grok-4.5", "prompt_tokens_estimated": 15800, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 4.9547}, {"party_key": "gpt-search-fetch-v1", "model": "openai/gpt-5.6-terra", "prompt_tokens_estimated": 15830, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 3.6781}, {"party_key": "gemini-search-fetch-v1", "model": "google/gemini-3.1-pro-preview", "prompt_tokens_estimated": 15814, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 7.3554}, {"party_key": "claude-search-fetch-v1", "model": "anthropic/claude-fable-5", "prompt_tokens_estimated": 15830, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 32.7812}, {"party_key": "qwen", "model": "LOCAL", "prompt_tokens_estimated": 15397, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 1, "fetch_tokens_allowed_per_turn": 0, "worst_case_usd": 0.0}], "worst_case_usd": 48.7695, "expected_usd_from_observed_ratio": 10.0075, "observed_ratio": {"ratio": 0.2052, "n": 16, "min": 0.0252, "max": 0.3989, "basis": "Median of actual/worst_case over recorded rounds. Agentic rounds sit far below the rest -- round 011 was 0.03 -- because the bound assumes every sample fills its fetch budget and three of five parties fetched nothing."}, "rates_version": "openrouter-list-2026-08-07", "rates_recorded_utc": "2026-08-07T09:18:03Z", "rates_source": "https://openrouter.ai/api/v1/models", "rates_verified_by_custodian": false, "basis": "Every sample emitting max_tokens on every turn, prompt tokens estimated at 3.4 bytes/token, and for a fetch-enabled party every turn re-sending the whole conversation with another 60000-character page appended. Over-states by construction.", "what_it_cannot_do": "It cannot bind the provider. Only a provider-side spending cap does that.", "max_spend_usd_this_cycle": 60.0, "daily_ceiling_usd": 100.0, "already_committed_today_usd": 8.005} · actual `2.1272`

## Verification

- plan `734baaa202e322d4b3555eecacba35b7f32ebb4793f57412190eeaa30f19ec9f`
- prompt template `b5a10d5684cbd9964db975f50d8f0d2fb2d166390b3971cbe4af2202a2842ec5`
- context pack `b8f28ac56628494c8bb204209b047326c04929bbe4609684f1692931aaefbc76`
- [every prompt, verbatim](round-019-prompts.md)

[all rounds](index.md) · [previous](round-018.md)