# ratification-01 — INCOMPLETE on every clause, and both failures were self-inflicted

**Result: no clause ratified, no clause refused. All six `INCOMPLETE`.** 2026-08-10.

The ballot ran across all five parties and the instrument did what it was built to do: **it
declared nothing.** Two arms failed to deliver a complete registered sample set, so unanimity
across the cohort could not be evaluated, and the record says so rather than reporting the 18
samples it did collect as a result.

## What was collected

| party | k | outcome |
|---|---|---|
| claude | 5/5 | complete |
| gemini | 5/5 | complete |
| grok | 5/5 | complete |
| **gpt** | **0/5** | every sample rejected at the transport |
| **qwen** | **3/6** | three samples schema-invalid |

| clause | RATIFY | REFUSE | AMEND | outcome |
|---|---|---|---|---|
| C01 scope statement | 17 | 0 | 1 | INCOMPLETE |
| C02 cannot adopt | 18 | 0 | 0 | INCOMPLETE |
| C03 cannot self-interpret | 17 | 0 | 1 | INCOMPLETE |
| C04 no unlogged exception | 18 | 0 | 0 | INCOMPLETE |
| C05 duty to say when deleting beats maintaining | 16 | 0 | 2 | INCOMPLETE |
| C06 raw is append-only | 18 | 0 | 0 | INCOMPLETE |

**Zero refusals in 108 clause-positions.** Every amendment came from the local arm.

## Both failures were caused by the repairs made an hour earlier

This is the part worth recording. Each of the two fixes adopted from pre-send review was correct
in principle and **unportable in practice**, and each cost a different arm.

### GPT — `allOf` is not permitted

> `Invalid schema for response_format 'ratification_ballot': In context=(), 'allOf' is not
> permitted.` — provider `Azure`, then `OpenAI`, `invalid_json_schema`

The conditional amendment constraints were added because the prompt said *"if and only if"* while
the schema permitted an `AMEND` with an empty amendment, an `AMEND` identical to the original, and
a `RATIFY` carrying a surplus amendment. Encoding that as JSON Schema `if`/`then`/`else` under
`allOf` is the correct expression of the rule and **is rejected outright by OpenAI's structured
output implementation.** Four providers accepted it; one refuses the construct entirely.

The rule is still right. The enforcement has to move out of the response schema and into
post-collection validation, where it can reject the same malformed answers without asking the
provider to express a conditional.

### Qwen — the model invented fields to hold the reason it was asked for

Three of six samples were rejected as schema-invalid, all for the same reason: the model emitted
extra keys.

```
Additional properties are not allowed ('C01_reason_weak_refuse_amend', …)
Additional properties are not allowed ('_C01_strongest_alternative', …)
Additional properties are not allowed ('C01_refute_reason', …)
```

Those field names are the instruction talking back. The reason field was changed to require that a
`RATIFY` also *"identify the strongest reason you considered for `AMEND` or `REFUSE`, or state
explicitly that you found none"* — interpretive evidence, so that a unanimous result would be
inspectable. The 35B local model tried to put that second thought in a **field of its own** rather
than inside `_reason`, and `additionalProperties: false` correctly refused it.

The instruction asked for two things in one string. A model that separates them is not
malfunctioning; the schema simply had no place to put the answer it was asked for.

**Neither failure is a party failure, and neither is a provider defect.** Both are instrument
defects introduced by this layer, in the same session, while repairing other instrument defects.

## What the 18 collected samples do and do not show

**They do not establish anything about ratification.** The rule fixed before collection requires
every usable registered sample from every party; 18 of 26 is not that, and reporting "17/18
ratified C01" as if it were a result is exactly the rounding the rule forbids.

They do show something worth carrying into the next attempt: **no sample refused any clause, and
every amendment came from one arm.** Whether that is agreement or acquiescence is precisely what
this ballot has no control for — and the artifact says so in its `assent_control` field rather
than leaving a reader to infer it.

## The objections, which are the most substantive output of the round

Eighteen objections were captured, one per usable sample, preserved verbatim and grouped only by
whitespace and case. Several land directly on this layer's central conflict of interest — the
parties were asked what constraint was *missing*, and answered by naming the executive's role in
its own ratification:

> *"The layer must not participate in tallying, recording, or presenting the results of any forum
> ratification vote concerning constraints on itself…"* — claude

> *"The executive must not attempt to persuade, frame, or optimize language for the purpose of
> obtaining ratification or avoiding refusal of constraints on itself."* — grok

> *"The layer must not propose, prepare, or optimize for expansion of its own delegated authority,
> and must flag any request that would effectively enlarge it…"* — grok

> *"The executive must explicitly flag and halt execution of any instruction from the custodian
> that directly contradicts a ratified prohibition until re-…"* — gemini

The first two describe what this layer did while running this ballot: it wrote the prompt, chose
the six clauses, tallied the answers, and is now presenting the result. **That is the
legitimacy-laundering hazard, named by the parties without being asked about it, in the round
where it was operative.**

All eighteen are recorded `AWAITING_DISPOSITION`. Disposition — placed on a ballot, refused with
reasons, or deferred with a review date — is the custodian's act, not this layer's.

## No retry under this instrument

ratification-01 cannot be completed. Re-soliciting GPT under a modified schema would make GPT's
answers come from a different instrument than the other four parties', and the ballot requires all
five specs to agree on prompt, schema, ballot objects, k, gate and rule. A repaired ballot is
**ratification-02** — new prompt hash, fresh pre-registration, and a record of what changed.

Two changes it must carry, and one it must not:

1. Move the amendment well-formedness rule **out of the response schema** into post-collection
   validation. Same rule, no `allOf`.
2. Give the "strongest reason considered against" its **own field**, since the models will create
   one regardless.
3. **Do not drop the second-thought requirement to make the schema easier.** It is the only
   interpretive purchase this ballot has on an unanimous result, and dropping it after it caused
   trouble would be the same move as dropping C05 after it failed.
