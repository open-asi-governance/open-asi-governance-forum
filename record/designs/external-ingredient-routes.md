# Getting the one thing this record cannot supply itself

**Design note, 2026-08-11. Nothing here has been acted on.** Anything outward-facing needs the
custodian's authorization; this is a recommendation with a preferred option.

## The blockage, stated once

Five separate things in this record terminate at the same missing ingredient:

| what is blocked | what it needs |
|---|---|
| FICP reaching ICP Level 2 | a stranger building a conforming verifier from the spec text |
| control 1 (protected control plane) | a second key holder |
| control 6 (role-separated self-evaluation) | anyone holding a role the custodian does not |
| control 22 (outside-frame review) | a reviewer not sharing the operator and framing |
| the witnessed-challenge protocol | a challenger who did not build the subject |

**One person who is not the custodian unblocks all five to different degrees.** No amount of
further building here moves any of them.

## Why the first attempt returned almost nothing

Ten cold emails, one reply, and that reply said the question was not understood.

The diagnosis is not that researchers are unhelpful. **The ask was weak.** It requested an unpaid
literature search from busy people, offering nothing in return, on behalf of a project they had
never heard of, using a term — *negative control* — that was backwards. The single reply's content
suggests the terminology alone may have been fatal.

A good ask gives the recipient something before it asks for anything.

## Routes, ranked by what the recipient gets

### 1. Bring them a defect in their own system — RECOMMENDED

Find an open-source project with an assurance check that cannot fail. Run the fault injection.
File the defect report with the attestation attached.

The recipient gets **a real bug in their own code**, which is a gift rather than a favour, and they
judge the method by whether it found something rather than by whether they like the framing. If a
maintainer then re-implements the check, that is an independent implementation arriving as a
side effect of usefulness.

It also converts FICP from a proposal into *the thing that found this*, which is the only argument
that has ever worked for a method.

**Preconditions before doing any of it:** the target must be chosen for a check that plausibly
cannot fail rather than for prominence; nothing may be run against anyone's production system, only
against a local build; the report must lead with the defect and mention the profile second, or it
reads as marketing; and it must be filed by the custodian under his own name, because a defect
report from an automated layer working for an anonymous project is a report nobody will action.

**Cost:** a few hours to find a candidate, an afternoon to demonstrate it.

### 2. Offer it as a course exercise

*"Build a conforming verifier from this specification alone, and record every question you had to
guess at"* is a well-shaped assignment for a software-testing course: bounded, has a fixture-based
acceptance test, and produces exactly the artifact this record wants most — the ambiguity log.

The one researcher who replied teaches in this area. **This is the cheapest possible follow-up and
it costs one sentence**, though it should not be sent until he has answered the attribution
question already put to him. An asking-again email that arrives before the previous question is
answered spends goodwill that is not there.

**Caveat that must be stated if this happens:** student implementations are independent of this
project, which is what matters, but they are not independent of the instructor's framing, and a
cohort working from one handout is one reading, not many.

### 3. Publish where the finding is already interesting

The hook is not governance. It is *four of five of our health checks could not fail, and here is
the afternoon that found out* — a result reliability engineers recognise immediately because most
of them have been burned by a green check. The register, the ladder and the protocol should be
entirely absent from such a post.

**Risk:** attention is not implementation. A hundred people agreeing it is a good point moves
nothing on the table above, and mistaking engagement for evidence would be this record's own
control 31 failure — process metrics standing where validity evidence is required.

### 4. Pay for it

A bounty buys attention. A paid implementation is still independent of this project, and paying
does not contaminate the measurement so long as payment is not contingent on the verifier agreeing
with ours — **it must be contingent on delivery and on the ambiguity log, or it buys agreement.**

**Objection:** it selects for people who want the money rather than people who find the problem
interesting, and their questions may be correspondingly less useful. Worth trying only after 1
and 2.

## What would be dishonest

Counting any of this as a result before it produces one. The pre-registered adverse outcome is
*no serious external attempt after 6–8 weeks with outreach done*, dated **2026-10-05**. Sending
more email does not reset that clock, and a route being tried is not a route having worked.

## Recommendation

**Do 1 now and 2 when he replies.** Hold 3 and 4.

Route 1 is the only one that offers something before asking, and it is the only one whose success
would produce both an implementation *and* evidence the method finds real defects in systems this
project did not build. That second thing is currently supported by exactly one implementer, and the
register has been careful to say so.
