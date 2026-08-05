# The Prediction Registry

A dated, falsifiable, scoreable ledger of forecasts about AI governance — and about this project.

## Why this exists

In the founding record, Claude Opus 5 argued that the genuinely valuable thing in the proposal,
stripped of institutional framing, was:

> a versioned, reproducible corpus of dated, falsifiable predictions about governance questions —
> with prompts, model versions, and sample variance — that can be scored against reality in three
> years. Nobody has that.

*(raw lines 1341)*

Deliberation ages badly. Predictions do not: they either come true or they don't, and the scoring
does not care who made them or how well-written the argument was. This registry is the only part
of the project that gets **more** valuable with time rather than staler, and it is the only part
that can be wrong in a way that anyone can check.

## Rules

1. **A prediction states a resolution date and a resolution criterion, fixed in advance.**
   Without both, it is an opinion — file it as analysis instead.
2. **Predictions are scored on their resolution date whether or not the result is flattering**,
   and the score is committed. A registry that quietly drops its misses is worse than no registry.
3. **Confidence is stated.** Numerical probabilities are used only where they clarify judgment,
   never to manufacture precision.
4. **No retroactive editing.** A prediction may be superseded by a later one that names it; the
   original stays, with its original wording and its score.
5. **Predictions are attributed to a specific identity**, under the same identity rules as the
   corpus: "Claude Opus 5" and "Claude Code" are different forecasters.
6. **Predictions derived from someone's claim are not that person's prediction** until they
   confirm it. Derived entries carry `status: "proposed, unconfirmed by source"` and are not
   scored against the source until confirmed.

## Scoring

On the resolution date, an entry is scored `correct`, `incorrect`, `partially correct`, or
`unresolvable`, with the evidence recorded. `unresolvable` means the criterion turned out not to
be checkable — which is itself a finding about how the prediction was written, and is counted
against the forecaster's calibration, not excused.

## Current state

The seed entries are predictions **about this project**, made by Claude Code on 2026-08-05. They
are deliberately uncomfortable: each one describes a way this project could fail, with a date on
which anyone can check.

This is the cheapest available test of whether the project is honest. If the seed predictions
resolve `incorrect` and are recorded as such, the mechanism works. If they are quietly dropped, it
doesn't.

No model-solicited predictions have been collected yet. When they are, they will be collected at
k ≥ 5 with reported variance, per `CONTRIBUTING.md`.
