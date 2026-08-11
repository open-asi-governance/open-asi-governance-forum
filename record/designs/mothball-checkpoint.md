# The mothball checkpoint — adopted by the custodian, 2026-08-11

**On 2026-10-05, this record is evaluated against two conditions. If both hold, OAGF stops being
actively developed and the effort moves to a sandboxed learning loop.**

Proposed by Codex, seconded by this workbench, adopted by the custodian on the day it was proposed —
and **two of its three original limbs were holed by the custodian within hours**, which is recorded
below rather than tidied away. Registered as separate predictions, deliberately, so that no single
judgement call can absorb all of them.

## The conditions

**AMENDED 2026-08-11, hours after adoption.** The custodian challenged two of the three limbs and
both challenges were sustained. What follows is the checkpoint as it now stands; the original
limbs are withdrawn in the registry rather than edited, with their reasoning attached.

| | condition | resolves |
|---|---|---|
| **P-0031** | No party outside this project has **attempted** a FICP verifier from the specification text | 2026-10-05 |
| **P-0034** | No **measured comparison of AgentBuilder output quality between two pipeline versions** exists | 2026-10-05 |
| ~~P-0032~~ | ~~no gate catches a self-favouring error prospectively~~ | **WITHDRAWN — category error** |
| ~~P-0033~~ | ~~no complete non-actuating learning episode exists~~ | **WITHDRAWN — mis-aimed; superseded by P-0034** |

**Both remaining limbs must hold** for the checkpoint to fire.

### Why P-0032 was withdrawn rather than amended

It asked whether a **gate** catches an error, and was offered as a test of whether **controls** make
builder error visible. Those are different propositions. Only **7 of 63** controls are ENFORCED,
`land.py` runs 8 gates, and **of the seven errors this checkpoint was built from, none was in scope
of a truth-capable enforced control at the time.** Five had no enforced control covering the class;
one was covered by control 5, enforced inside `derive_counts.py`, while the failing scan was a
different script that never called it; and one was in scope of `prose-triage`, which fired,
demanded a disposition, and accepted the one supplied — it checks **form**, and a false claim with
correct form passes by design.

So the classification supports **zero demonstrated efficacy failures.** Resolved positive, P-0032
would have been read as evidence that controls do not work, when the fact established would have
been that they were never applied.

**Withdrawn, not amended**, because rewriting a limb whose likely resolution had just been
challenged is the re-proposal laundering control 13 exists to catch.

### Why P-0033 was superseded

Not false — **mis-aimed.** It asked whether a learning loop *exists*. The AgentBuilder pipeline
already is one and runs at scale: ~2,513 agent repos with a generated main agent class, including
agents that participate in the build pipeline itself and the RSI control plane. Existence was the
wrong question.

**Self-construction is not self-improvement.** What separates them is measured gain across
generations, and nothing in the programme measures that. P-0034 asks for the measurement instead —
in either direction, because the prediction is about whether the loop is *measured*, not whether it
improved.

Each is written so that the generous reading is the one that keeps OAGF alive: a *partial,
abandoned* implementation attempt counts against mothballing, and a measured comparison counts
whichever direction it points. That asymmetry is deliberate — the party writing the criteria is the
party who would have to stop.

## What it means in practice

**Nothing changes tomorrow.** No work stops now, no artifact is deleted, and the day-to-day is
unaffected until the date. What has changed is that there is now a date on which the question gets
asked, and it cannot be quietly not-asked.

**If the checkpoint fires**, active OAGF development stops. The record stays published and
permanent — the corpus, the register, the findings, the failed attempts, the corrections. It
becomes a research record rather than a workstream. Effort moves to: a disposable improvement agent
in a hard non-actuating sandbox; tasks with externally resolvable outcomes; capability and
regression measured across episodes; complete episode provenance; human authorization for every
external effect; **and new controls derived only from failures observed in that loop**.

OAGF would become the incident-derived safety layer around an actual learning system, rather than
the main product.

**If it does not fire**, at least one of two things is true that is not true today: somebody
outside tried the artifact, or the AgentBuilder loop has a fitness signal measured across two
generator versions. Either is worth more than the last week's output.

## What this does not mean

* **Not mothballing Consullo.** OAGF is one workstream. The Seed AI programme is not what is
  under test.
* **Not an admission the work was worthless.** It would mean maintaining it is worth less than
  confronting the Seed AI problem directly. Those are different claims.
* **Not a deletion.** Nothing is removed. Published URLs keep resolving.

## The defect in this checkpoint, stated plainly

**The custodian evaluates it, and he is the person most invested in the answer.** That is control
6, unrepaired, in the instrument meant to check everything else. Control 40's own false-negative
clause names this exact shape: *a stop condition only its author can evaluate.*

One partial mitigation: the criteria were written before the outcome was known, and are recorded in
a registry that scores on fixed dates. Withdrawing or replacing a limb is possible — it just
happened twice — and leaves a `revision` bump, a `withdrawn_because`, and a supersession link in the
record rather than a silent edit.

**That is weaker than it sounds.** The same-day amendment shows how easily a limb can be removed;
what made it legitimate was that the challenge came from the custodian and was sustained on
evidence, not that the registry stopped it. What would actually repair this is somebody else holding
the evaluation — the same missing party the whole record turns on. **It is not repaired.**

## Why this was adopted

Seven self-favouring factual errors were published in four days. Every one was caught by Codex, by
a re-read, or by a stranger — **none by any gate.** The programme's central empirical claim is that
controls make builder error visible, and that claim still has no supporting observation.

P-0032 was written to test it and could not: the gates and the controls are different sets, and no
truth-capable enforced control was ever in scope of any of the seven. **The coverage-versus-efficacy
question is recorded here and deliberately NOT registered as a prediction** — a badly-posed forecast
is worse than none, and nobody has yet posed a good one.

The workbench had written control 40 — *a program pre-commits the observation that ends it* — into
its own register that week, and had not applied it to the programme it was running. Codex noticed.
