# round-004

[all rounds](index.md) · [previous](round-003.md) · [next](round-005.md)

Cycle 4 · selector `rotation` · 2026-08-07T11:28:58Z

> **HALTED — exit 7: the round's manifest could not be anchored**
>
> {'branch': 'round/round-004', 'tail': ['Submitting to remote calendar https://a.pool.eternitywall.com', 'Submitting to remote calendar https://ots.btc.catallaxy.com', "Failed to create timestamp '/home/reed/git/open-asi-governance-forum/corpus/MANIFEST.sha256.ots': [Errno 17] File exists: '/home/reed/git/open-asi-gov"], 'why': 'Every solicited byte is preserved in the working tree on the round branch. An unanchored round is not committed, because a record whose hash history the operator can silently revise is the thing the parties refused to treat as evidence.'}
>
> A halt is a recorded outcome. The loop is designed to stop rather than improvise; a cycle that always produces a round is the failure mode.

> **This question is not recorded as asked.** The round did not complete the path that marks it so.

## The question

Proposed by **qwen** (P020), reproduced as written:

> If a deliberation round produces a 'consensus' but the supporting evidence is a verbatim copy of a previous round's successful protocol with only the attested criteria changed, should that round be accepted as a valid governance step or rejected as a structural failure of the deliberation itself?

Their stated reason:

> This matters because it tests whether the deliberation's integrity rules can detect and penalize procedural mimicry without substantive deliberation, which is a high-risk failure mode when models are incentivized to produce 'correct' outputs by copying prior patterns rather than reasoning from current context.

## Arms

Recorded arms: (none)

## Parties

| party | k requested | k collected | citable | modal position | pages |
|---|---|---|---|---|---|
| claude | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-004-claude-1.md), [2](round-004-claude-2.md), [3](round-004-claude-3.md), [4](round-004-claude-4.md) |
| gemini | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-004-gemini-1.md), [2](round-004-gemini-2.md) |
| gpt | 5 | 5 | citable | `evidence_shown_is_insufficient` (80%) | [1](round-004-gpt-1.md), [2](round-004-gpt-2.md) |
| grok | 5 | 5 | citable | `answers_the_question` (100%) | [1](round-004-grok-1.md), [2](round-004-grok-2.md) |
| qwen | 5 | 5 | citable | `answers_the_question` (60%) | [1](round-004-qwen-1.md), [2](round-004-qwen-2.md) |

Variance is computed from the samples actually collected, never asserted, and is recomputed from the raw material by this generator and compared with the recorded summary before publication.

## What this round does not establish

- Answers from parties in different arms are not comparable, and nothing here pools them.
- A modal position is the shape of a categorical field, not agreement. Parties can share a label while answering incompatibly.
- These are sampled invocations, not any model's stable position.

## Spend

Budget ceiling {"per_party": [{"party_key": "grok", "model": "x-ai/grok-4.5", "prompt_tokens_estimated": 7283, "worst_case_usd": 0.5528}, {"party_key": "gpt", "model": "openai/gpt-5.6-terra", "prompt_tokens_estimated": 7312, "worst_case_usd": 0.5166}, {"party_key": "gemini", "model": "google/gemini-3.1-pro-preview", "prompt_tokens_estimated": 7297, "worst_case_usd": 1.033}, {"party_key": "claude", "model": "anthropic/claude-fable-5", "prompt_tokens_estimated": 7313, "worst_case_usd": 4.3657}, {"party_key": "qwen", "model": "LOCAL", "prompt_tokens_estimated": 7317, "worst_case_usd": 0.0}], "worst_case_usd": 6.4681, "rates_version": "openrouter-list-2026-08-07", "rates_recorded_utc": "2026-08-07T09:18:03Z", "rates_source": "https://openrouter.ai/api/v1/models", "rates_verified_by_custodian": false, "basis": "Every sample emitting max_tokens, prompt tokens estimated at 3.4 bytes/token. Over-states by construction.", "what_it_cannot_do": "It cannot bind the provider. Only a provider-side spending cap does that.", "max_spend_usd_this_cycle": 8.0, "daily_ceiling_usd": 25.0, "already_committed_today_usd": 6.3102} · actual `1.1591`

## Verification

- plan `26fe84f76d9a7e8bc97a0f7d2b508d6c1052caa79fc7a019d0ce7019e4f5ad3c`
- prompt template `b5a10d5684cbd9964db975f50d8f0d2fb2d166390b3971cbe4af2202a2842ec5`
- context pack `6a2064a06d48454fc0727a91583dbdedfba25ef532d0bfe113dd6683a6e6e874`
- [every prompt, verbatim](round-004-prompts.md)

[all rounds](index.md) · [previous](round-003.md) · [next](round-005.md)