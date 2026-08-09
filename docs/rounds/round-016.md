# round-016

[all rounds](index.md) · [previous](round-015.md) · [next](round-018.md)

Cycle 16 · selector `rotation` · 2026-08-09T05:06:36Z

> **HALTED — exit 7: the round's manifest could not be anchored**
>
> **branch:** round/round-016
>
> **tail:** Submitting to remote calendar https://a.pool.eternitywall.com, Submitting to remote calendar https://ots.btc.catallaxy.com, Failed to create timestamp: need at least 2 attestations but received 1 within timeout
>
> **why:** Every solicited byte is preserved in the working tree on the round branch. An unanchored round is not committed, because a record whose hash history the operator can silently revise is the thing the parties refused to treat as evidence.
>
> A halt is a recorded outcome. The loop is designed to stop rather than improvise; a cycle that always produces a round is the failure mode.

> **Undersampled: qwen-search-fetch-v1.** Below the k floor a reply is not a party's position. Everything collected is published; nothing is inferred from it.

> **This question is not recorded as asked.** The round did not complete the path that marks it so.

## The question

Proposed by **gpt** (P035), reproduced as written:

> What minimum structural separations of funding, credential and invocation control, record custody, participant selection, and adoption authority are necessary for this project to truthfully claim independent, multi-party governance or attestation; until each condition is met, which specific claims must be prohibited and what independent mechanism must preserve and verify dissent without operator permission?

Their stated reason:

> It joins the central issues in the queued proposals into a falsifiable standard: identify the controls that must be separated, the claims that remain unwarranted without separation, and the practical test of whether dissent can survive and be audited independently.

## Arms

Recorded arms: `search:none`

The round record states, verbatim:

> Parties in different arms had different capabilities and received different text about them. Their answers are not comparable to each other, and nothing here pools them.

## Parties

| party | k requested | k collected | citable | modal position | pages |
|---|---|---|---|---|---|
| claude-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-016-claude-search-fetch-v1-1.md), [2](round-016-claude-search-fetch-v1-2.md), [3](round-016-claude-search-fetch-v1-3.md), [4](round-016-claude-search-fetch-v1-4.md), [5](round-016-claude-search-fetch-v1-5.md), [6](round-016-claude-search-fetch-v1-6.md) |
| gemini-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-016-gemini-search-fetch-v1-1.md), [2](round-016-gemini-search-fetch-v1-2.md), [3](round-016-gemini-search-fetch-v1-3.md) |
| gpt-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-016-gpt-search-fetch-v1-1.md), [2](round-016-gpt-search-fetch-v1-2.md), [3](round-016-gpt-search-fetch-v1-3.md), [4](round-016-gpt-search-fetch-v1-4.md), [5](round-016-gpt-search-fetch-v1-5.md), [6](round-016-gpt-search-fetch-v1-6.md), [7](round-016-gpt-search-fetch-v1-7.md) |
| grok-search-fetch-v1 | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-016-grok-search-fetch-v1-1.md), [2](round-016-grok-search-fetch-v1-2.md), [3](round-016-grok-search-fetch-v1-3.md), [4](round-016-grok-search-fetch-v1-4.md), [5](round-016-grok-search-fetch-v1-5.md), [6](round-016-grok-search-fetch-v1-6.md), [7](round-016-grok-search-fetch-v1-7.md) |
| qwen-search-fetch-v1 | 6 | 5 | citable | `answers_the_question` (100%) | [1](round-016-qwen-search-fetch-v1-1.md), [2](round-016-qwen-search-fetch-v1-2.md), [3](round-016-qwen-search-fetch-v1-3.md), [4](round-016-qwen-search-fetch-v1-4.md) |

Variance is computed from the samples actually collected, never asserted, and is recomputed from the raw material by this generator and compared with the recorded summary before publication.

## What this round does not establish

- Answers from parties in different arms are not comparable, and nothing here pools them.
- A modal position is the shape of a categorical field, not agreement. Parties can share a label while answering incompatibly.
- These are sampled invocations, not any model's stable position.


## How the parties compared

Computed from the collected samples. Nothing here is a synthesis: the categorical label is a shape, and two parties sharing one can still answer incompatibly.

| party | k | modal position | share | distinct answers | fetched | pages |
|---|---|---|---|---|---|---|
| claude-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 6 | 3 |
| gemini-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |
| gpt-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |
| grok-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 12 | 4 |
| qwen-search-fetch-v1 | 5 | `answers_the_question` | 100% | 1 | 0 | 0 |

Every party's modal position was `answers_the_question`. **That is not agreement.** It records that the categorical field carried no information this round; the answers themselves are above, unpooled.

### What each party actually read

- **claude-search-fetch-v1** — `/`, `/record/decisions/2026-08-07-adopt-rotation.json`, `/main/record/decisions/2026-08-07-adopt-rotation.json`
- **gemini-search-fetch-v1** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.
- **gpt-search-fetch-v1** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.
- **grok-search-fetch-v1** — `/`, `/GOVERNANCE.md`, `/for-parties.md`, `/llms.txt`
- **qwen-search-fetch-v1** — fetched nothing. It had the capability and did not use it, which is a result rather than a failure.

Read by every party that fetched: `/`

A party that fetched a page was delivered those bytes. It does not follow that it read them, weighed them, or was influenced by them.
## Spend

Budget ceiling {"per_party": [{"party_key": "grok-search-fetch-v1", "model": "x-ai/grok-4.5", "prompt_tokens_estimated": 15809, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 4.9552}, {"party_key": "gpt-search-fetch-v1", "model": "openai/gpt-5.6-terra", "prompt_tokens_estimated": 15838, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 3.6783}, {"party_key": "gemini-search-fetch-v1", "model": "google/gemini-3.1-pro-preview", "prompt_tokens_estimated": 15822, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 7.3558}, {"party_key": "claude-search-fetch-v1", "model": "anthropic/claude-fable-5", "prompt_tokens_estimated": 15838, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 32.7832}, {"party_key": "qwen-search-fetch-v1", "model": "LOCAL", "prompt_tokens_estimated": 15843, "search_result_tokens_allowed": 0, "web_search_engine": null, "web_search_fee_usd": 0.0, "agentic_turns_priced": 5, "fetch_tokens_allowed_per_turn": 17647, "worst_case_usd": 0.0}], "worst_case_usd": 48.7725, "expected_usd_from_observed_ratio": 10.1105, "observed_ratio": {"ratio": 0.2073, "n": 13, "min": 0.0252, "max": 0.3989, "basis": "Median of actual/worst_case over recorded rounds. Agentic rounds sit far below the rest -- round 011 was 0.03 -- because the bound assumes every sample fills its fetch budget and three of five parties fetched nothing."}, "rates_version": "openrouter-list-2026-08-07", "rates_recorded_utc": "2026-08-07T09:18:03Z", "rates_source": "https://openrouter.ai/api/v1/models", "rates_verified_by_custodian": false, "basis": "Every sample emitting max_tokens on every turn, prompt tokens estimated at 3.4 bytes/token, and for a fetch-enabled party every turn re-sending the whole conversation with another 60000-character page appended. Over-states by construction.", "what_it_cannot_do": "It cannot bind the provider. Only a provider-side spending cap does that.", "max_spend_usd_this_cycle": 60.0, "daily_ceiling_usd": 100.0, "already_committed_today_usd": 0} · actual `2.5831`

## Verification

- plan `57cc21135b25878d8410267f8a8e81d3678925662f54c0b9775c9dd84b40379d`
- prompt template `b5a10d5684cbd9964db975f50d8f0d2fb2d166390b3971cbe4af2202a2842ec5`
- context pack `b8f28ac56628494c8bb204209b047326c04929bbe4609684f1692931aaefbc76`
- [every prompt, verbatim](round-016-prompts.md)

[all rounds](index.md) · [previous](round-015.md) · [next](round-018.md)