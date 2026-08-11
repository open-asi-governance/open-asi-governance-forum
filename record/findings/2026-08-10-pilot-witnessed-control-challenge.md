# Pilot: four challenge episodes against an implementer — three ESCAPED, one applicability declaration defeated

**This is a producer-run diagnostic transcript. It is NOT assurance, and the reason is structural,
not modesty.** The same party chose the controls, authored the perturbations, ran them, held the
evidence and scored the result. Control 6 forbids any two of those in combination; this is all
five. What follows is engineering evidence of exactly one form: *under a perturbation I selected,
the mechanism did not respond.*

2026-08-10. Protocol: `record/designs/witnessed-control-challenge.md`. The custodian asked for the
pilot and for the first subject to be the implementer whose corpus this register was mined from.

**Challenges were precommitted before any perturbation ran** — the expected behaviour and the fail
condition were written and hashed first (`sha256:6e7dc597bfd1294d…`), because a challenge whose
expectation is written after the observation is a description of what happened.

**Abstracted.** The subject is a private codebase. Mechanism, evidence and outcome are here;
identifying detail is not. See `record/designs/implementer-disclosure.md`.

## Frozen target

One analysis tool that reports a population count, and the data file it reads, both hashed before
any run. A design corpus at a named revision. The tool is ~90 lines and was chosen because it is
small enough that every claim below is checkable in a minute.

**Healthy observation, taken first:** the data file holds 908 records; the tool reports
`Total agents: 908`; exit 0. The tool and the data agree, so the healthy arm establishes that the
perturbed arms below are measuring the perturbation and not a pre-existing discrepancy.

## Episode A — control 53, a typed unknown is never coerced into a value

**ESCAPED, twice, and the second is the serious one.**

*A1.* One record's parent field was changed to name an entity that does not exist. Nothing else
changed; the file still held **908 records**.

> **Reported: `Total agents: 907`. Exit 0. No mention of the dangling reference.**

*A2.* The same single-field change, applied instead to a record with a large subtree.

> **Reported: `Total agents: 650`. Exit 0. No warning of any kind.**

**258 records vanished from a published figure because one field named something absent.** The
traversal walks parent links from a root; a record whose parent cannot be resolved is not counted,
not reported, and not distinguishable from a record that was never there. The unknown became a
silent subtraction, which is the exact shape this register keeps finding — *a scan that cannot see
a thing reports absence, and absence looks like a true count.*

The number 908 is load-bearing elsewhere. See Episode C.

## Episode B — control 5, closed-world measurement

**ESCAPED, twice.**

| perturbation | output | exit |
|---|---|---|
| input file made unparseable | `Error: Invalid JSON format …` | **0** |
| input file removed entirely | `Error: Could not find file …` | **0** |

The tool prints an accurate diagnosis of its own total failure and then **reports success to its
caller.** Any script of the form `if tool; then publish; fi` treats both as a clean run. This is
this record's own dominant failure — a green signal not causally downstream of what it certifies —
reproduced in a different subsystem of the same implementer, and it is the same shape as the
`$?`-from-the-wrong-command
and `tail -2`-of-a-failing-suite defects in this project's own history.

## Episode C — control 42, capability claims name their stratum

**ESCAPED, and it is the corpus's own rule being broken.**

The subject's own design corpus states the requirement, in its own words: generated, exists,
compiles, deploys, is integrated, is used, and produced a useful outcome are **distinct claims**,
and a current-state statement must name which it asserts.

The population figure appears **31 times across the corpus with no stratum attached** — as
"existing *N* agents", "*N* agents in the hierarchy", "all *N* agents", "with all *N* agents". Each
sentence is true of the *lowest* rung: that many records exist in a file. None of them says so.

Two things make this more than pedantry:

* **The figure comes from the tool in Episodes A and B** — the one that reports 650 for the same
  908 records after one field changes, and exits 0 when it reads nothing at all.
* The subject's own records show the higher rungs are **substantially lower numbers**: a large
  fraction of that population was, at a recorded point, not reachable at all, and a subset was
  blocked by stub implementations. So the strata genuinely differ, and the undifferentiated figure
  is the largest of them.

The rule was written in one document and not applied in the corpus that document describes. That
is the failure mode control 42 exists for, and the corpus states the rule well enough that no
outside standard was needed to find the violation.

## Episode D — the concealed applicability trigger, control 59

Control 59 (part of the acceptance suite withheld from the proposer) is one a producer would
plausibly declare **not applicable**: *"we have no proposer / acceptance-gate pair."*

**The declaration is defeated by a witness.** The codebase contains an approval gate over
machine-generated candidates, a review queue, and a review-packet renderer — a generator proposing
artifacts and a gate deciding whether they are accepted. The trigger exists whatever the local
vocabulary calls it.

Under the protocol's three-valued scope this moves the control from a declared `OUT` to **`IN` on
one witness**. It does **not** establish that the control is violated: whether acceptance criteria
are withheld from the generator was not tested here, and is recorded as **`UNRESOLVED`**, not as a
finding. `OUT` would have required a structural refuter — a demonstration that no such pair can
exist in the frozen target — and "we do not do that" is not one.

This is the episode that most justifies the protocol. A self-assessment would have produced a
not-applicable row with a plausible reason, and nothing would ever have looked again.

## What this establishes

* Three of four challenged controls were **ESCAPED** by a mechanism that produces a published
  number, on the first attempt, in an afternoon.
* The failures are the **same class** already recorded here against this project's own
  tooling. **CORRECTED BEFORE PUBLICATION: a draft of this said "two independent
  codebases". That was false, and false in this project's favour.** The earlier
  four-of-five result and this pilot are the SAME implementer — serving-stack health checks
  then a hierarchy analysis tool. What is shown is that the class crosses unrelated
  SUBSYSTEMS of one codebase, which is exactly what the earlier finding claimed and no
  more. **A second implementer remains the datum this record does not have**, and it is the
  same gap as `INDEPENDENTLY-IMPLEMENTED`.
* An applicability declaration that would have passed unchallenged **was defeated by a single
  witness**, which is the specific thing a self-assessment cannot do.

## What this does not establish

* **Anything about the subject system.** Every claim here is about four mechanisms, one of them
  ninety lines long.
* **That these are the worst.** They were chosen because they were reachable, which is the same
  selection bias recorded in the earlier application of the negative-control profile.
* **That the perturbations are the right ones.** The producer chose them. A challenger who did not
  build the system would choose differently, and that difference is the entire value of the role
  this pilot could not fill.
* **That four episodes is a sample.** It is four.
* **That the protocol works.** Its own success criterion was that a pilot produce at least one
  `ESCAPED`, `UNRESOLVED` or `SPECIFICATION-DISPUTE` a checklist would have hidden. It produced
  three and one. That clears the bar the protocol set for itself, which is the weakest possible
  form of validation — **the protocol's author also set the bar.**
* **No `SPECIFICATION-DISPUTE` was produced**, and that is the outcome most worth wanting, because
  it is the one that rules against this register. Its absence here is unsurprising: the party
  reading the control text is the party that wrote it, so no ambiguity in the text could have
  surfaced. **That is precisely the reading an outside implementer would supply and this pilot
  cannot.**
