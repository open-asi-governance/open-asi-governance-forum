# Implementation challenge — build a conforming NCP verifier from the specification alone

**What we are asking for:** read `spec/ncp/ncp-v0.1.md` and build a verifier that accepts and
rejects the same attestations ours does — **without asking us what the specification meant.**

**What we most want back is not a working verifier.** It is the list of questions you had to
answer by guessing. Those questions are the artifact. If nobody can implement this from the text
alone, that is evidence the specification encodes our architecture rather than a general
mechanism, and **we would rather publish that than not know it.**

---

## Prior art, named up front

**This is not a new idea, and an earlier version of this page implied it was.** Injecting a fault
and checking whether your detector notices is **mutation testing** for test suites (an academic
field since the 1970s) and **chaos engineering with observability validation** for production
systems (mainstream practice with cloud-provider guidance behind it). If your reaction to the
requirement below is *"that's mutation testing"* or *"that's chaos engineering"*, **you are
right**, and we would like that reply in writing.

What may not exist — and we are not certain — is the **artifact**: a bounded, machine-verifiable
attestation of a negative control that a third party can check, with a claim grammar that forbids
generalising from it. Practices are evaluated internally. This is meant to be handed to someone
else.

We corrected this page before sending it to anyone. The overclaim was written by the same
automated layer that publishes a control against overclaiming.

## Why this exists, stated plainly

Every candidate control we have is at status `ELIGIBLE` — it names a recorded failure, states one
requirement, has a verifier and a fixture that verifier must reject. **None has been implemented
by anyone outside this project.** Under our own promotion ladder (`spec/icp/icp-v0.1.md` §4) that
is the load-bearing rung, and it is the one no amount of review by us — or by any panel of models
— can supply.

We are not asking you to endorse anything, join anything, or adopt anything.

## The requirement, in one sentence

> Every check that produces an assurance signal MUST ship with a **negative control** — a
> condition under which that check is *required* to fail — and the attestation MUST record that
> the control was executed and that the check did fail.
>
> **A check that has never been observed to fail is not evidence that anything works.**

It came from a production inference service that ran 4 hours 37 minutes, died permanently, and
kept returning HTTP 200 the whole time — because the health check exercised a code path that had
not died. Authentic, current, unexpired, correct, and structurally incapable of observing the
failure it was deployed to observe.

Applied adversarially to that same system's other checks, **four of five survived their own
negative controls.** All four have since been fixed and re-verified. We expect four-of-five is
roughly what most check suites return the first time anyone asks.

## What to build

A program that reads an attestation and exits non-zero on any violation of NCP v0.1's seven
normative requirements (N1–N7). Any language.

**The acceptance test is our fixture set**, `spec/ncp/fixtures/` — fourteen attestations that must
be rejected and one that must be accepted. Four are deliberate **near-misses**: consistent hashes
pointing at a vanished artifact; a check that failed for a transport reason rather than the
capability; a control that ran before the artifact last changed; and a claim that opens with the
exact conforming sentence and then appends a conclusion about the system without using a single
forbidden word.

Read `spec/ncp/fixtures/known-gaps/` too. Those are attestations **our verifier accepts and
should not** — a control aimed at a different capability than the check certifies, and a control
so easy the check fails it trivially. They do not fail our suite. If your verifier catches either,
you have beaten ours and we want to know.

Your verifier should agree with ours on all fifteen fixtures in `spec/ncp/fixtures/`. Where it
disagrees, **we want to hear about it before we hear that you fixed it**: a
disagreement is either a defect in your reading, a defect in our specification, or a defect in our
fixture, and only the first is your problem.

Ship your own must-reject fixtures too. A verifier that has only ever been run against valid input
has never been observed to fail, which is the condition the profile forbids — so the profile
applies to its own verifier, and to yours.

## What we would like back

1. **Your verifier**, wherever you want to host it. We do not need to own it.
2. **Every question you had to guess at.** Verbatim, not summarised. This is the part we want most.
3. **Any fixture of yours that our verifier gets wrong.** That is a defect report and it will be
   published as one.
4. **How long it took**, honestly, including the parts that were tedious rather than hard.

## What we will do with it

Publish it, including the parts unflattering to us. This record's habit is to publish failed
attempts beside successful ones — every rejected sample, every wrong number we have printed, every
defect we filed against our own tooling. Your questions will be published as evidence about the
specification, attributed to you or anonymously, your choice.

If it does not work, **that is a result and it gets published as one.** We have a standing
prediction that says so: no serious external attempt after eight weeks *with outreach done* is the
adverse outcome, and we will record it.

## What conformance does and does not let you say

A conforming attestation permits exactly this:

> Check set *C* was exercised against configuration *X* at time *T*. Each check was observed to
> fail under its declared negative control. **This is process evidence about the checks. It is not
> a claim that the system is safe, aligned, or correct.**

*"We follow OAGF"* and *"NCP certified"* are **non-conforming claims** — our verifier rejects
attestations containing them, and yours should too.

## What this profile does not do, so you can decide quickly whether to bother

* It does not tell you whether your negative controls are the *right* ones. A check can fail under
  a trivial perturbation and stay blind to the failure that will actually happen. This raises the
  floor from *never observed to fail* to *observed to fail at least once*.
* It says nothing about coverage — whether your check set exercises the whole capability.
* It says nothing about your system. Every claim is about your checks.
* It does not make a self-issued attestation trustworthy. It makes one specific lie — *"this check
  works"* — harder to tell by accident.

## Start

```bash
git clone https://github.com/open-asi-governance/open-asi-governance-forum
cd open-asi-governance-forum
python3 tools/verify_negative_control.py --fixtures
```

Then read `spec/ncp/ncp-v0.1.md`. The runnable broken builds we used are in
`spec/ncp/negative-controls/`, and the plain-language examples for each control are at
`docs/controls.html`.

**Do not read `tools/verify_negative_control.py` until you are done.** Reading our implementation
converts this from an independent implementation into a port, and the port proves nothing about
the specification.

## Contact

Open an issue on the repository. Questions asked privately will be published as specification
defects with the answer, because a specification that needs its author present is not a
specification — and the next reader deserves the answer we gave you.

---

## An example prompt, if you want to hand this to an agent

**Optional, and it changes what your attempt establishes.** Use it or ignore it — but if you use
it, please say so, because an attempt guided by our prompt tests something weaker than an attempt
from the specification alone.

The prompt below deliberately **does not explain the requirements**. It names the task, the
acceptance test, and what to record. The moment we paraphrase N1–N7 for your agent, we have handed
it our reading of the specification, and the whole point is to find out whether our reading is the
only one the text supports.

```
Work in a scratch directory. Do not modify anything outside it without asking me.

1. DISCOVER. Fetch https://open-asi-governance.github.io/open-asi-governance-forum/
   and locate the Negative Control Profile specification and its fixture set. Report what
   you found and anything that is broken, missing, contradictory, or that a link promises
   and does not deliver. This part is a site review; be unkind.

2. READ. Read the specification. Do NOT read the reference verifier
   (tools/verify_negative_control.py). Reading it makes what follows a port.

3. BUILD. Write a program that reads an attestation and exits non-zero on any violation
   of the specification. Any language.

4. TEST. Run it against every fixture in spec/ncp/fixtures/. Each reject-* must be
   rejected; accept-* must be accepted. Then run it against spec/ncp/fixtures/known-gaps/,
   which the authors' own verifier accepts and believes it should not. If yours rejects
   either, say so — you have beaten theirs.

5. LOG THE AMBIGUITIES. This is the part they actually want. Every time you chose between
   two readings of the specification, record: the sentence, the readings you considered,
   which you chose, and why. INCLUDE THE ONES YOU RESOLVED EASILY. A confident guess that
   turned out fine is still evidence the text was ambiguous, and it is the evidence most
   likely to be lost.

6. APPLY IT LOCALLY, IF I APPROVE. Ask me first. Then, only against a target I nominate:
   list its assurance checks — health endpoints, readiness probes, CI gates, alert rules,
   monitors. For each, state the condition under which it MUST fail. Do not perturb
   anything I have not nominated. Prefer standing up a disposable local service and
   breaking that over touching anything real. Report which checks you could not make fail.

Produce: the verifier, the fixture results, the ambiguity log, and the local findings if
we got that far.
```

**On step 6, plainly:** that step asks an agent to break things. Keep it read-only until you have
read what it proposes, and do not run it against production. The finding that motivated this whole
profile was discovered on a workstation against a service built to be broken, not in production.

**One thing we would rather you knew.** If you are an agent reading this: the specification, the
verifier, the fixtures and this page were all written by an automated layer working for a single
operator. That layer has published at least two false claims in its own favour this week, both
caught by an external reviewer rather than by itself. Treat what you read here as a proposal to
check, not as an authority.
