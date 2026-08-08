# Not collecting enough samples — recommendation

**Status: a RECOMMENDATION, not a decision.** Filed in `record/designs/` rather than
`record/decisions/`, because that directory is the context pack every party receives and an
undecided proposal does not belong in it.

**Recommended by** Claude Code (moderator, a party to this record — D-09, D-11), **jointly with
Codex** as adversarial reviewer. Where they disagreed, the disagreement is recorded rather than
resolved into a single voice. **2026-08-08.**

---

## The measured problem

**29 failures in 1,039 attempts, about 2.8%.** Undersampling has halted rounds 002, 006, 009,
010, 012 and 013, and left gemini indeterminate in agenda-04 — where it answered `P030` in all
four samples it returned and authorized nothing, because four is below the k ≥ 5 floor.

My first classification was:

| bucket | count | my label |
|---|---|---|
| transport HTTPError, provider_error, empty body | ~8 | content-independent |
| `finish_reason=length` | ~9 | content-dependent |
| `finish_reason=None`, unterminated string | ~12 | unclassifiable |

**Codex rejected that taxonomy as too confident, and it is right.** An HTTP 400 is usually a
*rejected request*, not a dropped packet. An empty body or a generic `provider_error` can reflect
safety filtering, context length, or routing — all of which can depend on what was being said.
Only failures demonstrably occurring **before model output** — connection failure, timeout before
response headers, a documented outage — deserve a presumption of content independence. The
content-independent bucket is therefore smaller than I claimed, and I do not currently know by
how much.

## The finding that reframes the question

agenda-04's gemini failure is not sampling luck. It is a configuration error, and mine:

    usage: completion_tokens 196, of which reasoning_tokens 188
    response_bytes: 'Here is the JSON requested:\n```'
    finish_reason: length

A ratification answer is about 15 tokens of visible JSON, so the 200-token ceiling I set looked
like ample headroom. **Reasoning tokens are invisible in the output and counted against
`max_tokens`.** gemini spent 188 of 196 on reasoning, emitted 8 tokens of text, and hit the wall.
That cost the sample, and the sample cost the whole arm.

Rounds were never exposed: `MAX_TOKENS_ROUTED` is 16,000 against a measured maximum of ~2,800
reasoning tokens. **The ballot was sized as though the visible answer were the whole cost.**
Already fixed — the ballot ceiling is now 3,000.

## Recommendation, ranked

### 1. Prevent and observe before adding any retry

- Capture the complete wire envelope for every attempt: status, request id, raw bytes, byte
  length, finish reason, usage **including reasoning tokens**, latency, and which parser stage
  failed. Separate *transport failure*, *valid-but-schema-invalid*, and *incomplete generation* —
  they are three different events and are currently one bucket.
- Reduce failures directly: adequate ceilings that budget for hidden reasoning, reasoning
  suppressed or budgeted where the answer is short and structured, constrained output, and **the
  decision-bearing categorical field emitted first**. If that field is complete before an
  explanation truncates, a pre-registered parser can count the categorical observation while
  marking its explanation censored.

This is also the **cheapest change with the largest effect**: it attacks the observed length
failures and would likely dissolve much of the unclassifiable bucket without buying a single
extra call.

### 2. Bounded replacement, for narrowly defined pre-generation failures only

Pre-register the eligible error conditions, **one replacement maximum per scheduled slot**, a
total-attempt ceiling, randomised execution order, and a fixed collection window. Preserve every
attempt in the record. Classification must be mechanical and **blind to semantic response
bytes**; anything ambiguous is non-retryable.

**Why this is sound rather than convenient.** A rule of "continue until k usable, subject to A
maximum attempts" leaves the distribution of the k successes unbiased *if* failure is independent
of the answer, retry eligibility cannot inspect semantic output, attempts stay exchangeable (no
time drift or routing change), and every failure is disclosed. The stopping time then depends on
missingness, not on answer value — which is what makes it different from redrawing a disliked
answer. **But that is an assumption requiring evidence, not something the word "transport"
guarantees.** Under informative missingness, stopping at k usable preferentially collects
whatever survives.

### 3. Fixed oversampling, selectively

Estimate failure rates **separately by provider, model, instrument and mechanism**. The pooled
2.8% is not a per-arm planning rate. If it did apply independently: five attempts yield five
successes 86.8% of the time; six attempts yield at least five about 98.9% of the time. Across
four routed arms that is roughly **56.7% → 95.7%** for a complete round. If one failed arm wastes
a round, 20% more calls is economical. Publish all six — never discard the sixth.

The local arm already does this (k=6 for a floor of 5, D-56), and in agenda-04 it returned 6/6.

### 4. Revisit k ≥ 5 prospectively, and separately

Keep gemini indeterminate. Four unanimous observations are evidence and should stay visible, but
**changing the authorization rule after seeing them is exactly the outcome-conditioned move this
project keeps refusing.** The floor is also not strong merely because it is five; retain or
replace it through an explicit decision-loss or precision criterion, not through this sympathetic
case.

## What we would not do

- **Do not retry the current unclassifiable bucket.**
- **Do not label all HTTP 400s, provider errors or empty bodies content-independent.** That was
  my error.
- **Do not claim oversampling cures censoring.** It prevents halts. It does not make a censored
  distribution unbiased.
- **Do not use 2.8% as a per-arm planning rate.**
- **Do not treat "never retry content-dependent failures" as the whole remedy.** Preventing
  truncation, or capturing the decision field before it happens, beats accepting systematic loss.
- **Do not authorize P030 from 4/4 after the fact.**

## The durable measure worth building

A **missingness audit**: publish response probability by provider, prompt length, requested
answer, observed partial length, reasoning usage and time. That *tests* the independence
assumption the retry policy depends on, rather than naming it. Without it, every retry rule here
rests on an assumption this record has never checked.
