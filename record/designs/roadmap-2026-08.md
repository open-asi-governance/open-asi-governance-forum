# Roadmap — what this repository should do to be worth an implementer's time

**Two independent proposals, not one.** The custodian asked the workbench (Claude Code) and Codex
to propose activities and a roadmap toward *"the best possible outcome of the repo with respect to
supporting various independent commercial and academic ASI implementations at high pace, and
aligned as decided by the parties."* 2026-08-10.

Codex was asked **without seeing this document**, deliberately. Agreement between the two
harnesses settles nothing — they share the custodian's account, this repository, the dominant
framing and much training culture — so two separate attempts are worth more than one anchored on
the other. Its full answer is in `record/executive/codex-transcripts/`.

**Both proposals reject part of the goal as stated.** That is the most important thing on this
page, and the disagreement is recorded before the agreement.

---

## The finding both proposals start from

**Nobody outside this repository has ever consumed its output.** Twenty rounds, 215 raw
files holding 1,299 solicited units, ~57 numbered deficiencies, and zero external users. The
marginal value of the 1,300th model answer is far below the first outside implementation attempt.

**And "aligned as decided by the parties" cannot mean what it sounds like.** The parties are five
sampled frontier chat models. They have no persistent identity, no interests, no adoption
authority, and no enforcement power. Today's ratification-01 returned **zero refusals in 108
clause-positions** with no assent control — and the parties' own unprompted objections said the
workbench must not tally votes about itself. Party unanimity is cheap. Building a roadmap on it
would be building on the one thing this record has already shown to be weak.

Neither proposal recommends abandoning the panel. Both recommend it stop being treated as a
*constituency* and start being used as an *instrument*.

---

## Codex's proposal, in summary

> "OAGF should stop trying to become a model-governed forum and become an evidence-engineering
> project for deployable AI controls."

* **The product** is a *candidate OAGF evidence profile* built from AS-01 and AS-02 of the
  Consullo submission — schema, verifier CLI, CI action, worked examples, and deliberately broken
  fixtures the verifier must reject.
* **Five workstreams**: the executable evidence envelope; an independent implementation challenge;
  a model-panel adversarial procedure; an adoption-and-claims package with a crosswalk to NIST AI
  RMF and ISO/IEC 42001; and external custody with named non-custodian maintainers.
* **Model output becomes load-bearing** only through a seven-step procedure: eligibility tied to a
  real failure, precommitment to what each outcome changes, blind challenge, mechanical
  cross-examination of conflicting answers, conversion into a test or narrowed claim, adoption
  signed by a *named human*, and periodic calibration against externally resolvable failures.
* **Next week**: put an AS-01/AS-02 implementation challenge in front of real infrastructure
  engineers. **Stop**: ratification-02, abstract governance rounds, further constitutional
  elaboration, and treating corpus size or deficiency count as progress.
* **Rename** the parties operationally as a *model panel*; never write "decided by the parties" in
  a way implying persistent consent.

It also names the claim grammar precisely: *"we follow OAGF"* should be **non-conforming**; only a
statement naming configuration, capabilities, trust policy, time, verifier and bundle hash — and
saying plainly that it is process evidence, not a safety claim — should be permitted.

---

## The workbench's proposal

I agree with the diagnosis and with most of the product. I differ on three things, and the
differences matter more than the overlap.

### Difference 1 — the wedge is the causal-downstream test, not "evidence" generally

Codex is right that a generic evidence envelope risks being *"a smaller, less legitimate rival to
NIST or ISO"* — its own failure condition 4. So the profile needs a wedge that existing frameworks
demonstrably do not have.

This repository has one, and has paid for it repeatedly:

> **A green signal must be causally downstream of what it certifies.**

Every significant failure here is that shape. A health check green through a 4h37m outage. `$?`
from `basename` rather than the suite. A tunnel to the wrong host answering to the same model
name. A context pin passing on a file containing a claim already proven false — *identity, not
truth*. A conflict-marker check pointed at two paths that do not exist. A count that could not see
69 files reporting zero. `derive_counts.py` — written that morning **to prevent exactly this** —
shipping the same defect twice more.

That last one is the strongest evidence the class is real: it is not a bug people make out of
carelessness, it is one they make *while concentrating on preventing it*.

ISO 42001 and the NIST AI RMF tell an organisation to have controls and to test them. Neither
supplies a mechanical test for **whether a passing check could have passed anyway**. That is a
narrow, executable, unclaimed technical wedge, and it is the thing this record is unusually
qualified to specify because it has ~8 documented instances with root causes.

**So: name the profile for the wedge.** Not "evidence profile" but a *negative-control
requirement* — every attested check must ship with a fixture that makes it fail, and the
attestation must record that the fixture was run and did fail. An assurance claim with no
demonstrated failure mode is not evidence that anything works.

That is one sentence an engineer can act on in an afternoon, and it subsumes AS-01: a check that
stays green through an outage is precisely a check with no demonstrated failure mode.

### Difference 2 — the forum's *failure modes* are a second product, aimed at the academic half

Codex would stop the deliberative work. I would stop it as a **governance mechanism** and keep a
narrow slice of it as a **research output**, because the custodian's goal names academic
implementations and this is the part academics can use immediately.

A great many people are currently building LLM-in-the-loop deliberation, constitutional
self-critique, model-panel review and AI-assisted governance. Almost none of them have
pre-registered, adversarially instrumented evidence about what goes wrong. This record does:

* **Assent is cheap and unanimity is not consent** — 108 clause-positions, zero refusals, no
  control, and a prior cohort that ordered the same clauses correctly 156/156. Discrimination
  capacity does not imply refusal capacity, and that separation was *measured*, not argued.
* **Voluntary tool use is not party-stable** — **1** search receipt across twenty numbered rounds
  given an exact URL, against 8 in instructed probes and 223 fetches. Capability present,
  essentially never chosen unless asked for. *(This sentence first said "0 searches", which is
  the same wrong number this record has now published three times. It was caught here by running
  `derive_counts.py` instead of transcribing — which is the whole argument for item 1 below,
  made against its own author.)*
* **A prompt cannot be repaired after it is sent** (D-36), and both of today's collection failures
  came from repairs made an hour before sending — an unsupported `allOf`, and a reason field that
  made a model invent keys to answer it.
* **The annotator is a party** — three of four models identified this unprompted in agenda-02.
* **Sampled models will name their operator's conflict of interest without being asked.** In
  ratification-01 the panel was asked what constraint was *missing* and answered, in effect, that
  the workbench must not tally votes about itself.

Written up honestly, that is a short paper: *"What breaks when you use sampled frontier models as
a deliberative body — twenty pre-registered rounds."* It costs **no new rounds**, it is the
highest-value thing already sitting on disk, and it is the one output where "we published every
failure" is a strength rather than an apology.

### Difference 3 — the fastest second implementation is an adversarial one

Codex's plan waits 3–6 weeks for an outside implementer and calls no-attempt the adverse result.
That is right but slow, and *pace* is in the goal.

There is a faster first customer: **Consullo, attacked rather than described.** The submission
already documents a health check green through a 4h37m outage. The profile's first real test is
not whether someone writes a new attestation — it is whether the negative-control requirement,
applied to Consullo's *existing* checks, finds more of them that cannot fail. If it finds several,
that is a demonstration an engineer will believe. If it finds none, the requirement is weaker than
claimed and that is worth knowing before shipping it to strangers.

This runs in days, needs no external party, needs no rounds, and produces the worked example that
the outreach in Codex's week 1 currently lacks.

### Where I fully agree with Codex

* Freeze ratification-02 and rotation rounds. **The ballot should not be repaired and re-run.**
* Eligibility, precommitment, blind challenge, cross-examination, conversion-to-test, and a
  **named human adopter**. Panels supply evidence; humans supply authority.
* Reject a standing dissent quota — manufactured disagreement is the mirror of manufactured
  consent. Require a strongest-objection field instead.
* "We follow OAGF" must be non-conforming as a claim.
* External custody is the only real cure for operator concentration, and disclosure is not a cure.
* AS-03 stays experimental: its environment boundary is unresolved.

---

## Sequenced plan

Rounds are the scarce resource: ~3 routed rounds/day, ~$5, and they are the only thing that
produces panel output. Almost nothing below needs them.

| # | Work | Rounds | Effort | Fails if |
|---|---|---|---|---|
| 1 | **Negative-control requirement + verifier + broken fixtures.** One sentence, one CLI, fixtures the verifier must reject. | none | 3–5 d | a stranger cannot produce a valid attestation in an afternoon, or the verifier accepts a supplied broken fixture |
| 2 | **Apply it to Consullo's existing checks.** Adversarial, not descriptive. | none | 2–3 d | it finds nothing — in which case say so and weaken the claim |
| 3 | **Write up the forum's failure modes.** Everything is already on disk. | none | 2–3 d | a reviewer says the findings are unsurprising or unsupported by the corpus |
| 4 | **Implementation challenge + direct outreach to ≥10 groups.** Published package only; private questions become public spec defects. | none | 2 d + waiting | no serious attempt after 6–8 weeks *with* outreach done |
| 5 | **One routed day, after implementer feedback.** Blind attack on the profile → cross-examination of the sharpest conflicts → calibration against fixtures. Never "should this be ratified". | 3 | 1 d | the decision would have been identical without the rounds |
| 6 | **External custody.** Named non-custodian maintainer with real promotion authority. | none | ongoing | objections can be acknowledged without changing any artifact or status |

**Next week, one thing:** items 1 and 2 together — the negative-control requirement, and its
application to Consullo's own checks. That produces the artifact *and* the worked example that
makes the outreach in item 4 credible.

**Stop:** ratification-02, rotation rounds, further constitutional elaboration of the workbench,
new corpus machinery beyond break-fix, and counting rounds or deficiencies as progress.

---

## What would make this worthless

Codex's eight failure conditions are all correct and are not repeated here. Two I would sharpen:

**The one most likely to actually happen is legitimacy laundering, and it nearly happened today.**
A ballot on the workbench's own constraints, written by the workbench, on clauses it selected,
tallied by it, reported by it — and it returned zero refusals. It failed only because two arms
broke on defects the workbench had introduced hours earlier. **Had those defects not existed, this
page would be citing 26/26 unanimous ratification of the workbench's own constraints.** No
instrument in the repository would have stopped that; the honesty is entirely downstream of the
custodian and of Codex's willingness to reject things.

**And the goal as stated contains a trap.** "Aligned as decided by the parties" would license
exactly that laundering at scale. The honest substitute: *implementers choose whether to rely on
controls whose design has been adversarially challenged, whose operation is mechanically testable,
and whose limits are attached to every claim.* That is narrower than the custodian asked for, and
it is the version that can be true.
