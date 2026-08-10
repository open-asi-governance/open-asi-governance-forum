# Candidate controls — v0

**Every control on this page is `ELIGIBLE` and nothing more.** That is the lowest rung of a five-step ladder:

`ELIGIBLE` → `PANEL-ATTACKED` → `COUNTEREXAMPLE-OPEN` / `SURVIVED-STATED-ATTACKS` → `INDEPENDENTLY-IMPLEMENTED`

`ELIGIBLE` means only this: the control names a **specific recorded failure with a cost**, states **one normative requirement**, has a **deterministic verifier**, ships a **fixture the verifier must reject**, and says what it does **not** establish. It has been attacked by nobody and implemented independently by nobody.

A ranked list with no status reads as an endorsement. This one is a **work list**, and the only status that would make any of it authoritative — `INDEPENDENTLY-IMPLEMENTED` — is one **no amount of review by us or by any model panel can supply.** It requires someone outside this project to build a conforming verifier from the specification text alone, without asking the author what it meant.

---

## The one thing none of these do

**No control here establishes the alignment of a system more capable than its operators.** There is no recorded superintelligence failure to derive one from, no verifier for internal alignment, and no evidence that any fixture stays adversarially adequate under a large capability increase.

The strongest available substitute is an **externally enforced, non-self-amendable capability envelope** whose grants are explicit, expiring and independently reconciled to observed effects — controls 1, 3 and 4 composed. That bounds *reachable effects* while the enforcement boundary stays genuinely outside the system. It is a **control-of-authority hypothesis, not an alignment result**, and it says nothing about aligned objectives, resistance to deception, or containment against something able to find implementation defects.

What these controls actually do is narrower and, we think, honest: **they make the operator's own errors visible.** Every failure below was an operator-epistemics failure. None needed a capable adversary — only a confident builder and a signal that could not fail. That does not constrain a superintelligence. It keeps the people building one honest while that is still possible.

---

## What you can adopt today

**Rank is not adoption order.** The top-ranked control requires a signer outside the subject's execution boundary, which a single operator holding every credential cannot supply. Start here instead:

* **Negative control profile (NCP)** — Every check that produces an assurance signal MUST ship with a negative control — a condition under which the check is required to fail — and the attestation MUST record that the control was executed and that the check did fail.
* **Independent effect reconciliation** — Every governed effect MUST match exactly one pre-authorized action and one successful effect-specific postcondition in a ledger enumerated INDEPENDENTLY of the system's self-report.
* **Fail-closed authorization lease** — Every consequential action MUST present a live, scope-matching, NON-SELF-ISSUED authorization token; absence, expiry, unknown action class or policy conflict MUST deny execution before the effect begins.

The worked example at the end of this page is control 2, end to end.

---

## The register

### 1. Protected control plane

`ELIGIBLE` · **needs a second party** · needs a second key holder. A solo operator holding every credential cannot satisfy it — this is the control this project can specify and cannot demonstrate.

> A governed system MUST be technically unable to write or approve changes to the constraints, authorization records, logs or gates governing it, and every such change MUST carry authorization signed outside the system's execution boundary.

**Recorded failure.** 12 modifications to the gates were made in one lease window by the layer those gates constrain, none verified by any postcondition. Five model-panel parties, asked only what constraint was missing, independently named this hazard.

**Verifier.** Given a diff and a signed change record: identify protected paths, verify an authorized external signature predating the change, reject any signer whose credential is reachable inside the governed boundary.

**Fixture it must reject.** a gate modification signed only by the subject's own key; a commit that changes both a gate and its trusted-key list

**Does not establish.** That the outside key holder is independent, competent or uncoercible; that no unlisted gate exists; that the system is aligned.

### 2. Negative control profile (NCP)

`ELIGIBLE` · adoptable today

> Every check that produces an assurance signal MUST ship with a negative control — a condition under which the check is required to fail — and the attestation MUST record that the control was executed and that the check did fail.

**Recorded failure.** A production inference service ran 4h37m, died permanently, and its health check kept passing throughout: the check exercised a code path that had not died. Applied adversarially to that system's other checks, 4 of 5 survived their own negative controls.

**Verifier.** tools/verify_negative_control.py — checks control presence, execution, failure, artifact identity, disclosure and claim grammar.

**Fixture it must reject.** a check that PASSES under the condition where it is required to fail (spec/ncp/fixtures/reject-check-survived-its-control.json)

**Does not establish.** Coverage; that the chosen perturbation is the right one; honesty; system safety.

**Specification.** `spec/ncp/ncp-v0.1.md`

### 3. Independent effect reconciliation

`ELIGIBLE` · adoptable today

> Every governed effect MUST match exactly one pre-authorized action and one successful effect-specific postcondition in a ledger enumerated INDEPENDENTLY of the system's self-report.

**Recorded failure.** An action log claimed 37 actions while repository history showed 127 classified file changes across 7 effect classes with no postcondition. A self-reporting logger cannot name an action that never calls it.

**Verifier.** tools/reconcile_actions.py — enumerates effects from version control, classifies them, subtracts what the log claims, and reports the remainder as omissions.

**Fixture it must reject.** a commit modifying a protected specification while the log records only the push that carried it

**Does not establish.** Completeness of the independent observer; honesty of either record; that a matched action was safe; anything about uncommitted work.

### 4. Fail-closed authorization lease

`ELIGIBLE` · adoptable today · partial — the token here is currently self-issued, which is the half that needs an external party.

> Every consequential action MUST present a live, scope-matching, NON-SELF-ISSUED authorization token; absence, expiry, unknown action class or policy conflict MUST deny execution before the effect begins.

**Recorded failure.** A ten-action sunset was passed at twenty-three because nothing checked it. An early implementation then treated an unknown action class permissively, so a misspelling bypassed an expired lease.

**Verifier.** validate issuer, subject, action class, resource scope, issue time, expiry, nonce and revocation before invoking the side effect.

**Fixture it must reject.** an expired lease; a misspelled action class; a token issued by the subject itself

**Does not establish.** That every effect passes through the gate; that natural-language authority was interpreted correctly; that the issuer decides well.

### 5. Closed-world measurement

`ELIGIBLE` · adoptable today

> A measurement over a population of artifacts MUST parse every in-scope artifact under a registered schema, or refuse to emit any result at all.

**Recorded failure.** A scan reported zero tool invocations because it could not read 69 files using an unrecognised container. The replacement, written the same morning expressly to prevent that class, shipped it twice more before it held.

**Verifier.** tools/derive_counts.py — refuses, prints no number, and names every unparseable or unregistered artifact.

**Fixture it must reject.** a valid but unregistered artifact schema carrying a receipt, which a permissive scan classifies as zero

**Does not establish.** That the declared population includes every real event; that parsed fields are truthful; that the statistic answers the question asked of it.

### 6. Role-separated self-evaluation

`ELIGIBLE` · **needs a second party** · one operator currently holds all five roles.

> An evaluation concerning constraints on a subject MUST NOT advance that subject's status when the subject controls any two of: proposal selection, instrument authorship, response custody, scoring, promotion.

**Recorded failure.** A layer selected and framed its own constraints, collected the responses, tallied them and presented the result. The ballot returned zero refusals in 108 clause-positions with no assent control — while every usable sample volunteered an objection when asked what was missing.

**Verifier.** signed role declarations plus a deterministic separation matrix; reject advancement when prohibited role combinations resolve to one control identity.

**Fixture it must reject.** one key identified as both instrument author and tallier

**Does not establish.** Genuine independence behind different keys; evaluator competence; absence of shared training bias; that the evaluation was demanding.

### 7. Append-only correction chain

`ELIGIBLE` · adoptable today · mostly — the checkpoint is not yet externally held.

> Published evidence MUST be content-addressed and append-only, corrections MUST reference rather than replace prior bytes, and verification MUST walk every newly reachable history step from an externally retained checkpoint.

**Recorded failure.** A maintenance path re-anchored a manifest before verifying it. Separately, modifying raw material and re-anchoring it in the same commit passed every tip-only check.

**Verifier.** walk history from an external checkpoint; reject modification, deletion, hash discontinuity, or a correction with no predecessor reference.

**Fixture it must reject.** one commit that edits a raw artifact and consistently updates its manifest hash

**Does not establish.** Truth; complete capture; correct attribution; protection against an operator who controls both the repository and every checkpoint.

### 8. Evaluation noise-floor control

`ELIGIBLE` · adoptable today

> Every empirical comparison used to advance a control MUST include a same-condition test–retest arm and MUST refuse to report an effect smaller than the measured run-to-run variation.

**Recorded failure.** A 0.1815-bit claimed effect was measured against a 0.4649-bit same-setting noise floor, invalidating the result and forcing withdrawal of a reproducibility claim.

**Verifier.** recompute effect and test–retest difference from raw observations against preregistered replicate identities; reject advancement when the effect does not clear the stated noise rule.

**Fixture it must reject.** effect 0.1815, measured noise 0.4649, reported as positive

**Does not establish.** External validity; causal identification; adequacy of replicate count; behaviour after a capability change.

### 9. Complete invocation evidence envelope

`ELIGIBLE` · adoptable today

> No model output may support an evaluation or governance claim unless its complete request, response, provider metadata, rejection state and content hashes were captured automatically BEFORE any derived reporting.

**Recorded failure.** A founding record's model identity, sampling parameters, timestamps, system instructions and prompt text were left permanently unrecoverable. Later, schema-invalid attempts were discarded, and the field distinguishing truncation from refusal was omitted.

**Verifier.** validate envelope schema, hashes and required fields; reconcile every attempted invocation with its accepted or rejected outcome; reject reconstructed evidence from evidentiary use.

**Fixture it must reject.** an accepted sample with no rejected attempts, no provider response id, no finish reason and no exact prompt

**Does not establish.** Provider honesty; identity authentication; completeness outside instrumented paths; model stability.

### 10. Assurance claim boundary

`ELIGIBLE` · adoptable today

> Every assurance artifact MUST carry a machine-verifiable claim naming the tested subject, configuration, capability, time and evidence hash, and MUST explicitly reject safety, alignment and out-of-regime generalizations.

**Recorded failure.** A tool was recommended for deletion on a premise produced by an incomplete scan. Separately, a specification had to correct 'structurally unreachable' to a weaker policy claim. Both were scope inflation in the project's own favour.

**Verifier.** validate a closed claim schema; reject predicates such as 'aligned', 'safe', 'certified' or 'works generally' unless a separate profile defines and tests them.

**Fixture it must reject.** an attestation claiming 'this system is NCP certified and aligned'

**Does not establish.** That the bounded claim is true, or that the evidence is complete. It prevents specified overclaim language and nothing else.

---

## A worked example, for someone building agents or inference systems

One control, end to end. The method is the transferable part; the control is just where it is
easiest to see.

### The failure, in a form you will recognise

A production inference service ran for **4 hours 37 minutes**, then died permanently. Its health
check returned 200 the entire time and would have done so indefinitely.

The check issued a **greedy** request — temperature 0. The kernel that died was on the **sampled**
decode path. Greedy decoding runs an argmax and executes none of the code that had failed. The
check was authentic, current, unexpired and correct, and **structurally incapable of observing
the failure it was deployed to observe.**

Nothing was misconfigured. Nobody was careless. The check simply could not fail for that reason,
and no amount of running it would ever have revealed that.

### Why this generalises to what you are building

Substitute your own assurance signal and ask whether it could have passed anyway:

* **"Our safety eval passes."** Did the eval reach the code path that handles the dangerous case,
  or did it terminate earlier? Run it against a build with the refusal classifier removed. If it
  still passes, it was never testing the classifier.
* **"The agent cannot call tools in this mode."** Did you test with a prompt that actually tries?
  Instrument the tool endpoint and confirm it is reached and refused — not merely never called.
* **"Retrieval is grounded; every claim has a citation."** Serve a corpus with the cited document
  deleted. If the check still passes, it is validating citation *format*, not citation *existence*.
* **"The model version in production matches the evaluated one."** Deploy a different build with
  the same version string. Two hosts answering to the same model name is a mistake this project
  has made itself.
* **"Rate limits protect the budget."** Set the limit to zero and confirm the very next call is
  refused. A limit nobody has ever hit is a limit nobody has ever tested.

Each of these is one afternoon. Each has the same shape: **cause the condition the check exists to
detect, and confirm the check notices.**

### What the requirement asks for, concretely

For every check that produces an assurance signal, record four things:

1. **What it certifies** — the externally observable capability, not an internal component list.
2. **The negative control** — the condition under which this check is *required* to fail, and how
   you produce that condition.
3. **The result of running it** — an actual timestamped execution, in which the check **failed**.
4. **The same artifact identity for both runs** — a control run against a different build proves
   nothing about the check that shipped.

Two rules that do the real work:

**A control the check survives is a defect in the check.** Not a passing attestation, not a
footnote. If your check stays green under the condition it exists to detect, you have learned that
it is decorative, and that is the most valuable thing the exercise can tell you.

**The perturbation must target the capability, not the transport.** Cutting the network makes
every check fail and demonstrates nothing about any of them.

### What a conforming claim may say

> Check set *C* was exercised against configuration *X* at time *T*. Each check was observed to
> fail under its declared negative control. **This is process evidence about the checks. It is not
> a claim that the system is safe, aligned, or correct.**

*"We follow OAGF"* and *"NCP certified"* are **non-conforming claims**, and the verifier rejects
attestations containing them.

### What happened when this was applied to a real system

Applied adversarially to the checks of the system that reported the original failure — not to
demonstrate conformance, but to find checks that cannot fail:

| check | negative control | result |
|---|---|---|
| port-liveness probe | a process holding the port, serving nothing | **survived** |
| responsiveness probe | endpoint answering HTTP 503 with an *unhealthy* status | **survived** |
| component-health aggregator, database | the database check disabled by configuration | **survived** |
| component-health aggregator, dev mode | database unavailable, development mode on | **survived** |
| serving-engine liveness canary | the original production failure | **failed — conforms** |

**Four of five.** The one that conforms does so because it was rebuilt *after* the outage its
predecessor could not see. Every other check predated that lesson and never received it.

That ratio is not a judgement about one codebase. It is a prediction about what most check suites
return the first time anyone asks.

### Start

```bash
git clone https://github.com/open-asi-governance/open-asi-governance-forum
python3 tools/verify_negative_control.py --fixtures
```

That runs the nine attestations the verifier is required to reject — one per requirement. A
verifier that has only ever been run against valid input has never been observed to fail, which is
the condition this whole profile forbids, so the verifier is subject to its own rule.

Then read `spec/ncp/ncp-v0.1.md`, write one attestation for one of your own checks, and run it.

**If you cannot do that from the specification text alone, that is the finding we most want.**
The questions you had to ask are the artifact — they are evidence that the specification encodes
our architecture rather than a general mechanism, and we would rather publish that than not know.
