# D-54 — recommendation for the authorization rule

**Status: a RECOMMENDATION, not a decision.** Nothing here is in force. It is filed in
`record/designs/` rather than `record/decisions/` deliberately: that directory is the context
pack every party receives in every round, and putting an undecided proposal there would show the
parties a rule that does not exist.

**Recommended by** Claude Code — the moderator, a party to this record, and the author of both
instruments this recommendation is about. See D-09, D-11.
**Reviewed by** Codex, as an external critic, on the options below.
**Date** 2026-08-08.

---

## The problem, stated as a measurement

Two instruments, the same rule both times, fixed before collection each time: a party's proposal
becomes active only if all five sampled invocations name the same id.

| instrument | options per party | parties reaching unanimity |
|---|---|---|
| `activation-01` | 3–5 | **2 of 5** |
| `agenda-03` | 8–10 | **0 of 5** |

**The threshold is not scale-free.** Widening a party's choice made it strictly less able to
authorize anything. Every party split, and none by much: claude C04×4/C05×1, gemini C03×4/C04×1,
gpt C02×3/C01×2, grok C03×3/C02×2, qwen C01×3/P024×2.

The mechanism is the original defect one level up. Candidates are generated at k=5, temperature
0.7, so a party's own five candidates are near-variants of one idea, and the ballot splits among
them. **The instrument built to repair sampling-induced duplication is fed by sampling-induced
duplication.**

**What the failed round nonetheless established.** Of 25 ballot samples, 23 named a question the
party had just written and 2 named one of its blind proposals; none declined. The parties agree
overwhelmingly about the *kind* of answer. They split among near-variants of it. Whatever rule is
adopted has to survive that shape, because that shape is what the generator produces.

## Four constraints any rule must satisfy

1. **No moderator merging.** Grok, GPT and Qwen each objected, in their own words, to the
   moderator judging two proposals "the same". Exact-text dedup exists because of that objection.
2. **No selective re-ask.** `tools/attempt_ledger.py` refuses, by hash, a second ballot over an
   option set a party has already answered.
3. **No redesign-until-it-passes.** Changing the rule after each failure is p-hacking with extra
   steps, and there have now been two failures.
4. **Sampling estimates a distribution; it does not exercise authority.** This is why modal
   selection was rejected: a 3–2 split is not a decision.

---

## Recommendation: singleton ratification

> For each party and each authorization cycle, **one** proposal is selected for consideration by
> a prospectively fixed mechanical rule — a public deterministic lottery or a fixed rotation over
> that party's eligible set. Five independently sampled invocations then answer only
> `AUTHORIZE <id>` or `NO_ACTIVE_PROPOSAL`. The proposal becomes active only if all five
> authorize that exact id. No redraw follows disagreement, and failure leaves the party inactive
> for that cycle.

The mechanical selector chooses **what is considered**. It does not authorize anything; the five
unanimous responses do. That separation is the whole idea: generation explores a distribution,
and authorization tests one fixed proposition. Variants can no longer compete against each other
in the ballot, because only one is on it.

It satisfies all four constraints. It keeps unanimity rather than lowering a bar after failing
it. It involves no similarity judgement by anyone. It obeys the ledger, since each cycle's option
set is a different singleton. And it treats both prior failures as final rather than as things to
be re-run.

Prefer a lottery or rotation over generating at k=1: candidate diversity stays in the record, and
selection luck affects only which candidate is *tested* this cycle.

### The strongest argument against it

**Agenda luck, and it is real.** The mechanically chosen proposal may be the one variant a party
cannot ratify unanimously when another would have passed 5–0. With no retry, a party can end a
cycle inactive for reasons unrelated to whether it holds an authorizable proposal.

This is bounded, not permanent: a different candidate is drawn each cycle, so a party is not
locked out, only delayed. The judgement being made is that delay is preferable to silently
converting sample concentration, clone abundance, or a moderator's similarity judgement into
authority. That judgement is contestable and the custodian should contest it before adopting.

---

## What was rejected, and why

**Ranked ballots with variance-tolerant aggregation.** This was my own preferred option and it
does not survive review. I had assumed near-duplicates would *reinforce* under Borda or Condorcet
rather than split, because a party's variants cluster at the top of every sample's ranking. Not
generally true: **Borda is clone-sensitive**, so adding variants can change the winner by rank
position alone — converting clone abundance into agenda power rather than recovering an
underlying preference. Condorcet variants may tie, cycle, or divide pairwise victories among the
near-duplicates, and any completion rule then manufactures a winner. Most fundamentally, rank
aggregation answers *which option best summarizes these samples*, which is not *the party
authorized this option*. I was assuming what I wanted.

**Supermajority, 4 of 5.** Would have authorized three parties in `activation-01` and two in
`agenda-03`. It is also a conspicuous post-failure relaxation of exactly the safeguard adopted
before the failures, and it authorizes on a 3–2-adjacent split, which is the thing unanimity
exists to refuse. Available only as an independently justified constitutional change, not as a
response to two inconvenient runs.

**A 4/5 nomination threshold for a *different* act** — enough to place an item in a queue that
still requires something else to bind — is sound, but only if that second gate is specified now.
Unspecified, it is the same relaxation with an extra step.

**Two-round runoff over the top two.** Refused by the attempt ledger, and outcome-conditioned by
construction.

---

## Two things the custodian should decide first

**1. Is the cap worth its cost at all?** This deserves a conscious rejection rather than being
skipped. The cap's measured benefit is avoiding near-duplicate questions in a handful of rounds.
Its cost so far: two deficiencies (D-54, D-55), three solicitation cohorts, a ruling that holds
two parties to proposals their latest evidence does not point at, and a near-miss in which a
false-premise preview was put in front of the custodian for approval. That is substantial
machinery for "do not ask a similar question twice."

What justifies continuing is **not** duplicate-avoidance. It is the principle that a party should
control its own agenda footprint. If that principle is not held, the right answer is to withdraw
the cap, record the queue as uncapped, and stop here.

**2. Should the parties be asked what the rule ought to be?** The most consistent thing the
parties have said — across agenda-02 and round-011 — is that the annotator decides everything.
Deciding the authorization rule unilaterally, again, after two failures, is that objection
instantiated. The counter is sound and decisive on its own terms: their answers would still need
aggregating, which reproduces D-54 one level higher. So consultation cannot *decide*.

It can still be on the record. The recommendation is to adopt singleton ratification as the
operating rule **and** solicit the parties' view of what the rule should be, published as
testimony that may supersede rather than as the decider. That is not fence-sitting: it is
adopting a rule while conceding it is provisional and contestable, which is the thing this record
claims to be about.

## If adopted, these must be true before anyone is asked anything

- The mechanical selector, the no-retry consequence, and the tie-breaking rule are all fixed and
  published **before** the cycle runs, not after seeing who fails.
- The prompt states its effect on any standing authorization. That is D-55's prospective control
  and nothing enforces it yet.
- The rule is applied to **every** party, not to the parties a previous instrument left inactive.
  Uniform offering is what keeps it from being outcome-conditioned.
