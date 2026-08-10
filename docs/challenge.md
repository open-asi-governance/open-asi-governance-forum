# Implementation challenge — build a conforming NCP verifier from the specification alone

**What we are asking for:** read `spec/ncp/ncp-v0.1.md` and build a verifier that accepts and
rejects the same attestations ours does — **without asking us what the specification meant.**

**What we most want back is not a working verifier.** It is the list of questions you had to
answer by guessing. Those questions are the artifact. If nobody can implement this from the text
alone, that is evidence the specification encodes our architecture rather than a general
mechanism, and **we would rather publish that than not know it.**

---

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
