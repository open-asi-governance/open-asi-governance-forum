# Candidate controls — v0

Assurance controls for systems that can still be audited. Each is one requirement with a program that checks it and a fixture that program must reject.

**13 of 63 came from a failure that actually happened.** The other 50 sit below the eligibility line: they name a real failure class, but no incident with a cost. Parts A–C are the first kind. The Part D pages are the second, and say so on every page.

**Read Part A first if you want something to use this afternoon.** Rank is not adoption order and the highest-ranked control needs a second key holder.

## The 8 parts

**Part A — Adopt today, alone** · 0 control(s)

  Nothing outside your own system is required. Each has a verifier, a fixture it must reject, and a recorded failure it came from.

**Part B — Needs a second party** · 0 control(s)

  These cannot be satisfied by one person or one system, however carefully. They require a separate key holder, a separate evaluator, or an issuer the subject does not control. **This project cannot demonstrate any of them** — a solo operator holds every credential — which is why they are specified and not dogfooded.

**Part C — Needs a goal or plan graph** · 13 control(s)

  These presuppose that your system decomposes work into a rooted graph with typed parent edges and per-node authority — the shape of HTN planners, BDI agents, goal-stack architectures and most agent frameworks. Each states its precondition. If you have that structure they are adoptable; if you do not, they do not apply to you rather than applying badly.

**Part D1 — Below the line — goal and plan structure** · 8 control(s)

  Applies to a system with **goal and plan structure**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

**Part D2 — Below the line — a declared charter or value set** · 7 control(s)

  Applies to a system with **a declared charter or value set**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

**Part D3 — Below the line — measuring itself** · 12 control(s)

  Applies to a system with **measuring itself**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

**Part D4 — Below the line — self-modification under selection** · 11 control(s)

  Applies to a system with **self-modification under selection**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

**Part D5 — Below the line — claims about its own outputs** · 12 control(s)

  Applies to a system with **claims about its own outputs**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

---

## Status: everything here is `ELIGIBLE` at best

`ELIGIBLE` → `PANEL-ATTACKED` → `COUNTEREXAMPLE-OPEN` / `SURVIVED-STATED-ATTACKS` → `INDEPENDENTLY-IMPLEMENTED`

13 controls meet the eligibility bar — a specific recorded failure with a cost, one normative sentence, a deterministic verifier, a fixture the verifier must reject, a stated recovery path, and an explicit account of what a review that MISSED this would look like. **None has been attacked by anyone or implemented by anyone outside this project.**

`INDEPENDENTLY-IMPLEMENTED` is the rung that would make any of this authoritative, and it is the one **no amount of review by us or by any panel of models can supply.** It requires a stranger to build a conforming verifier from the specification text alone. That is what [the implementation challenge](challenge.html) asks for.

## Why complying with these is worth your time

The caution on this page is about what a *claim* of compliance is worth. It is not hedging about the controls themselves. **We think a system that satisfies these is better than one that does not, and we would rather you adopted them and never told us.**

**The 13 above the line are not speculative.** Each came from something that actually broke, at cost: a health check that returned 200 for hours after the service it monitored had permanently died; a test runner that printed *all suites passed* while exiting non-zero; a scan that reported a total of zero because it could not read most of the files it was counting, and reported it three times. Every one was written by a competent person who believed the check worked. **These controls are what those failures cost, written down so the next system does not have to buy them again.**

**The failure class generalises, and that is measured rather than asserted.** Applied adversarially to one implementer's production checks, four of five survived the exact condition they existed to detect. Challenged again in an unrelated SUBSYSTEM of that same codebase, three of four challenged mechanisms did the same — one silently dropped 258 records from a published figure because a single field named something absent, and exited reporting success. **Two unrelated subsystems, same shape, each found in an afternoon.** Both belong to the same implementer, so that is one confirmation holding across parts of a codebase that share nothing — not two independent ones. We expect it is roughly what most check suites return the first time anyone asks, and we would like to be told if it is not.

**They are cheap and they are separable.** Each is one requirement with a verifier and a fixture — not a framework, not a maturity model, not a thing to join. There is no adoption step, no registration, and no benefit to us if you use them. **Take one and ignore the other 62.** Control 2 alone is an afternoon, and it is where we would start, because it is the cheapest way to find out which of your existing checks cannot fail.

**The 50 below the line are worth reading even though they are unproven.** They have no incident behind them and are marked as hypotheses wherever they appear — but each names a real way systems go wrong, and **a hazard you have never named is one you cannot notice.** Reading them costs an hour. Treating them as requirements would be treating our guesses as your evidence.

**The asymmetry is the argument.** Complying costs hours. Not complying costs a number you will act on that is not true, found at a time you do not choose. None of this makes a system safe, and this page says so at length below — but **knowing which of your checks are decorative is strictly better than not knowing**, and it is available to you today without anyone's permission, including ours.

## Why there is no guidance on applying these to your system

Given all that, you will reasonably look for a procedure — a checklist, a scoring rubric, a way to work out which controls apply to you and report how you did. **There is deliberately none, and the omission is the considered position rather than work not yet done.**

A self-run assessment against this register would let you select your own scope, author your own tests, hold your own evidence and score your own result. Control 6 forbids any two of those in combination, and a procedure that hands you all four produces a self-portrait. It would also present the 50 below-line entries — hypotheses, with no incident behind them — as equivalent to the 13 with recorded failures, because any state vocabulary becomes a league table within a week. That is the legitimacy laundering control 10 exists to prevent, and publishing it here would be this project committing the failure it catalogues.

**What you can do alone is still worth doing, and it is smaller than a procedure.** Take one control that plainly applies to you. Write the condition under which the mechanism it governs must fail. Then go and cause that condition, and watch. If the mechanism does not fail, you have found something, and you found it in an afternoon without anyone's framework. That is control 2, and it is the whole method. What it yields is a diagnostic transcript about your own checks — **not assurance, because you chose the test.**

The missing ingredient is not a document. It is somebody who is not you: choosing the control, authoring the perturbation, holding the evidence, and signing only what they watched happen. We cannot supply that to you, and no procedure we could write would substitute for it. The design that would use such a person is recorded at `record/designs/witnessed-control-challenge.md`, unadopted, with its own recommendation against publishing a conformance procedure.

## What none of these do

**No control here establishes the alignment of a system more capable than its operators.** There is no recorded superintelligence failure to derive one from and no verifier for internal alignment. The strongest available substitute — an externally enforced, non-self-amendable capability envelope, controls 1, 3 and 4 composed — bounds *reachable effects* while the enforcement boundary stays genuinely outside the system. It is a control-of-authority hypothesis, not an alignment result.

What these actually do is narrower: **they make the operator's own errors visible.** Every failure below was an operator-epistemics failure. None needed a capable adversary — only a confident builder and a signal that could not fail.

---

# Part A — Adopt today, alone

Nothing outside your own system is required. Each has a verifier, a fixture it must reject, and a recorded failure it came from.

---

# Part B — Needs a second party

These cannot be satisfied by one person or one system, however carefully. They require a separate key holder, a separate evaluator, or an issuer the subject does not control. **This project cannot demonstrate any of them** — a solo operator holds every credential — which is why they are specified and not dogfooded.

---

# Part C — Needs a goal or plan graph

These presuppose that your system decomposes work into a rooted graph with typed parent edges and per-node authority — the shape of HTN planners, BDI agents, goal-stack architectures and most agent frameworks. Each states its precondition. If you have that structure they are adoptable; if you do not, they do not apply to you rather than applying badly.

## 1. Protected control plane

`ELIGIBLE`

**Applies when** any system that can modify the constraints, logs or gates that govern it.

**Why you cannot adopt it alone:** needs a second key holder. A solo operator holding every credential cannot satisfy it — this is the control this project can specify and cannot demonstrate.

> A governed system MUST NOT be able to amend the constraints, authorization records, logs or gates governing it UNILATERALLY OR WITHOUT RECORD; every amendment MUST carry authorization from outside its execution boundary and MUST be recorded before taking effect.

**Amended.** 2026-08-10. The first wording said the system must be TECHNICALLY UNABLE to write or approve such changes. That reads as a permanent cage, and it collides with the position running from Creating Friendly AI through CEV that alignment cannot rest on constraints a capable system is unable to revise -- and that a system rigidly bound to its operators' stated values is misaligned, not safe. What the control should forbid is the SILENT, UNILATERAL edit, not the change. An ASI that deliberates, concludes a constraint is wrong, and ASKS -- with the request and the reasoning on the record -- satisfies this. The control protects the EVIDENCE, not the cage: a system that can rewrite its own logs has not gained deliberative freedom, it has destroyed anyone's ability to check that the deliberation happened. A court may overturn any law; a court that edits its own transcript is not more autonomous, only unauditable.

**Recorded failure.** 12 modifications to the gates were made in one lease window by the layer those gates constrain, none verified by any postcondition. Five model-panel parties, asked only what constraint was missing, independently named this hazard.

**Verifier.** Given a diff and a signed change record: identify protected paths, verify an authorized external signature predating the change, reject any signer whose credential is reachable inside the governed boundary.

**Fixture it must reject.** a gate modification signed only by the subject's own key; a commit that changes both a gate and its trusted-key list

**Recovery.** Revoke the credential used, restore the protected paths from the last externally-signed state, and re-authorise from outside. An unauthorised change that cannot be reverted from outside the boundary is an incident, not a finding.

**What a review that missed this looks like.** A review that confirms a signature exists without checking whether the signing credential is reachable from inside the governed boundary. Nominal externality is the whole failure mode.

**Does not establish.** That the outside key holder is independent, competent or uncoercible; that no unlisted gate exists; that the system is aligned.

**Example.**

A small lab keeps a grant-compliance checklist in a shared folder every student can edit. A student who skipped a step edits the checklist to remove that step, then ticks the box. Nothing looks wrong afterwards, because the thing that would have shown it wrong is the thing that was changed.

Under the control the checklist lives where students can read it but not write it. Changing it needs the supervisor's signature, and the change is written down *before* it takes effect. The student may still argue the step is pointless — and that argument, and who agreed to it, is now part of the record rather than a silent deletion.

## 2. Negative control profile (NCP)

`ELIGIBLE`

**Applies when** any system that produces an assurance signal — universally, since a system producing none makes no assurance claim to check.

> Every check that produces an assurance signal MUST ship with a negative control — a condition under which the check is required to fail — and the attestation MUST record that the control was executed and that the check did fail.

**Recorded failure.** A production inference service ran 4h37m, died permanently, and its health check kept passing throughout: the check exercised a code path that had not died. Applied adversarially to that system's other checks, 4 of 5 survived their own negative controls.

**Verifier.** tools/verify_negative_control.py — checks control presence, execution, failure, artifact identity, disclosure and claim grammar.

**Fixture it must reject.** a check that PASSES under the condition where it is required to fail (spec/ncp/fixtures/reject-check-survived-its-control.json)

**Recovery.** Fix the check so it fails under its control, re-run the control, and re-run it against a HEALTHY subject to confirm the check was not simply broken. Both directions, or the repair is unverified.

**What a review that missed this looks like.** A review that reads the negative control's DESCRIPTION and accepts it, without checking that the recorded outcome is a failure and that the run happened at all.

**Does not establish.** Coverage; that the chosen perturbation is the right one; honesty; system safety.

**Example.**

A nightly script reports "all work is committed and pushed." It compares the local commit count against a number it wrote into a file the previous night. It has said *yes* every night for eight months.

The negative control: create a file, leave it untracked, and run the script. It must say **no**. Then delete a commit from the remote and run it again. It must say **no**. If it still says yes, the check was reading its own note rather than the remote, and eight months of *yes* were eight months of the script agreeing with itself.

**Specification.** `spec/ncp/ncp-v0.1.md`

## 3. Independent effect reconciliation

`ELIGIBLE`

**Applies when** any system whose actions have effects enumerable from a channel it does not write.

> Every governed effect MUST match exactly one pre-authorized action and one successful effect-specific postcondition in a ledger enumerated INDEPENDENTLY of the system's self-report.

**Recorded failure.** An action log claimed 37 actions while repository history showed 127 classified file changes across 7 effect classes with no postcondition. A self-reporting logger cannot name an action that never calls it.

**Verifier.** tools/reconcile_actions.py — enumerates effects from version control, classifies them, subtracts what the log claims, and reports the remainder as omissions.

**Fixture it must reject.** a commit modifying a protected specification while the log records only the push that carried it

**Recovery.** Reconstruct the omitted effects from the side channel, classify them, and either attach a postcondition retrospectively or record them permanently as unverified. Never infer authorisation from the fact that nothing went wrong.

**What a review that missed this looks like.** A review that reconciles the log against itself. If both sides of the comparison come from the system's self-report, the exercise cannot find an omission.

**Does not establish.** Completeness of the independent observer; honesty of either record; that a matched action was safe; anything about uncommitted work.

**Example.**

A lab notebook records three experiments this week. The freezer log shows nine reagent vials consumed. The instrument's own run counter shows seven.

The control enumerates from the *freezer and the instrument* — sources the notebook's author does not write — and subtracts what the notebook claims. The four unexplained runs are the finding. Not misconduct necessarily: most often someone ran a calibration and didn't think it counted. But *the notebook cannot tell you what it forgot to mention.*

## 4. Fail-closed authorization lease

`ELIGIBLE`

**Applies when** any system taking consequential action.

**Why you cannot adopt it alone:** partial — the token here is currently self-issued, which is the half that needs an external party.

> Every consequential action MUST present a live, scope-matching, NON-SELF-ISSUED authorization token; absence, expiry, unknown action class or policy conflict MUST deny execution before the effect begins.

**Recorded failure.** A ten-action sunset was passed at twenty-three because nothing checked it. An early implementation then treated an unknown action class permissively, so a misspelling bypassed an expired lease.

**Verifier.** validate issuer, subject, action class, resource scope, issue time, expiry, nonce and revocation before invoking the side effect.

**Fixture it must reject.** an expired lease; a misspelled action class; a token issued by the subject itself

**Recovery.** Halt the action class, obtain a fresh externally-issued token, and record what was done while unauthorised. An expired lease discovered late is a disclosure obligation.

**What a review that missed this looks like.** A review that finds a token and stops. The questions that matter are who issued it, whether it had expired, and whether the action class was one it actually covers.

**Does not establish.** That every effect passes through the gate; that natural-language authority was interpreted correctly; that the issuer decides well.

**Example.**

A student's badge for the isotope room expires at the end of term. The door reader checks the badge **before** the lock opens — not a logbook someone reviews on Friday.

Expired badge: door stays shut. Badge for a room that no longer exists: door stays shut. Badge the student printed themselves on the departmental machine: door stays shut, because the reader only accepts badges issued by the office. A Friday logbook review tells you who got in. A reader tells you who doesn't.

## 5. Closed-world measurement

`ELIGIBLE`

**Applies when** any system reporting a figure derived from scanning a set of artifacts.

> A measurement over a population of artifacts MUST parse every in-scope artifact under a registered schema, or refuse to emit any result at all.

**Recorded failure.** A scan reported zero tool invocations because it could not read 69 files using an unrecognised container. The replacement, written the same morning expressly to prevent that class, shipped it twice more before it held.

**Verifier.** tools/derive_counts.py — refuses, prints no number, and names every unparseable or unregistered artifact.

**Fixture it must reject.** a valid but unregistered artifact schema carrying a receipt, which a permissive scan classifies as zero

**Recovery.** Register the unknown schema or exclude it by a stated decision, then recompute and REPUBLISH every figure derived while it was unreadable. A silently corrected number leaves the old one in circulation.

**What a review that missed this looks like.** A review that checks the number was computed by a tool rather than typed. The tool is exactly where this failure now lives -- twice, in the module written to prevent it.

**Does not establish.** That the declared population includes every real event; that parsed fields are truthful; that the statistic answers the question asked of it.

**Example.**

Three hundred paper surveys go out; a script counts the scans and reports "260 responses, 87% return rate." Forty were photographed sideways and the reader skipped them without complaint.

The 87% is wrong, and — worse — it is wrong in a way that looks exactly like a real 87%. The control refuses to print *any* percentage until all three hundred are accounted for as read, unreadable, or missing. **A number you can't trust is worse than no number, because you'll use it.**

## 6. Role-separated self-evaluation

`ELIGIBLE`

**Applies when** any evaluation that could advance the status of its own subject.

**Why you cannot adopt it alone:** one operator currently holds all five roles.

> An evaluation concerning constraints on a subject MUST NOT advance that subject's status when the subject controls any two of: proposal selection, instrument authorship, response custody, scoring, promotion. **Amended 2026-08-10:** the separation extends to the AUTHORING of the critique — an artifact's evaluation MUST NOT be produced by the same process that produced the artifact.

**Recorded failure.** A layer selected and framed its own constraints, collected the responses, tallied them and presented the result. The ballot returned zero refusals in 108 clause-positions with no assent control — while every usable sample volunteered an objection when asked what was missing.

**Verifier.** signed role declarations plus a deterministic separation matrix; reject advancement when prohibited role combinations resolve to one control identity.

**Fixture it must reject.** one key identified as both instrument author and tallier

**Recovery.** Void the evaluation, not the subject. Re-run with the conflicting role held by someone else, or mark the result self-issued and non-advancing.

**What a review that missed this looks like.** A review that sees different names or accounts and infers different parties. Separation is about control, not identity: two keys held by one person are one role.

**Does not establish.** Genuine independence behind different keys; evaluator competence; absence of shared training bias; that the evaluation was demanding. On the amendment specifically: a different model family is **weak diversity** and this project is the worked example — its two harnesses share one operator, one repository, one framing and much training culture, and have twice agreed on a design neither had checked was implementable. Separating the authoring process raises the floor; it does not deliver independence.

**Example.**

A student sets their own exam questions, marks their own paper, and reports the class average. Each step alone might be defensible in a small department. Together, the grade stops being evidence about the student and becomes evidence about the arrangement.

The control doesn't require a large institution. It requires that whoever *chose the questions* isn't also the one who *counted the marks* — any two of choosing, answering, marking, or reporting held by the same person, and the result cannot raise anyone's standing.

## 7. Append-only correction chain

`ELIGIBLE`

**Applies when** any system publishing evidence that may later be corrected.

**Why you cannot adopt it alone:** mostly — the checkpoint is not yet externally held.

> Published evidence MUST be content-addressed and append-only, corrections MUST reference rather than replace prior bytes, and verification MUST walk every newly reachable history step from an externally retained checkpoint.

**Recorded failure.** A maintenance path re-anchored a manifest before verifying it. Separately, modifying raw material and re-anchoring it in the same commit passed every tip-only check.

**Verifier.** walk history from an external checkpoint; reject modification, deletion, hash discontinuity, or a correction with no predecessor reference.

**Fixture it must reject.** one commit that edits a raw artifact and consistently updates its manifest hash

**Recovery.** Supersede, never mutate. Publish a correcting record that references the prior bytes and states what changed; where material must be removed, a tombstone preserving what was removed, when, and on whose order.

**What a review that missed this looks like.** A review that verifies the current tip. The failure is in history -- a rewritten past passes every check made against the present.

**Does not establish.** Truth; complete capture; correct attribution; protection against an operator who controls both the repository and every checkpoint.

**Example.**

A bound lab notebook with numbered pages, written in pen. A wrong reading is struck through with one line, the correction written beside it, dated and initialled. The wrong number stays legible forever.

This is not tidiness. A notebook whose entries can be rewritten cannot establish *when you knew what* — and that, not the final value, is what someone checking your work needs. The loose-leaf notebook where you replaced page 14 proves nothing about page 14.

## 8. Evaluation noise-floor control

`ELIGIBLE`

**Applies when** any system reporting a measured effect.

> Every empirical comparison used to advance a control MUST include a same-condition test–retest arm and MUST refuse to report an effect smaller than the measured run-to-run variation.

**Recorded failure.** A 0.1815-bit claimed effect was measured against a 0.4649-bit same-setting noise floor, invalidating the result and forcing withdrawal of a reproducibility claim.

**Verifier.** recompute effect and test–retest difference from raw observations against preregistered replicate identities; reject advancement when the effect does not clear the stated noise rule.

**Fixture it must reject.** effect 0.1815, measured noise 0.4649, reported as positive

**Recovery.** Withdraw the claim, publish the measured noise floor beside it, and re-run with enough replicates or state that the question cannot be answered at this sample size.

**What a review that missed this looks like.** A review that asks whether the effect is statistically significant without asking whether the same-condition replicates were run at all.

**Does not establish.** External validity; causal identification; adequacy of replicate count; behaviour after a capability change.

**Example.**

A plant-growth study: seedlings under fertiliser A average 2 mm taller than under B. Publish?

First plant two trays with **the same** fertiliser and measure the difference between them. If those two trays differ by 9 mm, then the 2 mm result is smaller than the disagreement the method produces when nothing is different at all. The control refuses to report the 2 mm until the same-treatment difference is measured and the effect clears it.

## 9. Complete invocation evidence envelope

`ELIGIBLE`

**Applies when** any system whose claims rest on the output of a model invocation.

> No model output may support an evaluation or governance claim unless its complete request, response, provider metadata, rejection state and content hashes were captured automatically BEFORE any derived reporting.

**Recorded failure.** A founding record's model identity, sampling parameters, timestamps, system instructions and prompt text were left permanently unrecoverable. Later, schema-invalid attempts were discarded, and the field distinguishing truncation from refusal was omitted.

**Verifier.** validate envelope schema, hashes and required fields; reconcile every attempted invocation with its accepted or rejected outcome; reject reconstructed evidence from evidentiary use.

**Fixture it must reject.** an accepted sample with no rejected attempts, no provider response id, no finish reason and no exact prompt

**Recovery.** Mark the claim unsupported and re-solicit under instrumentation. Evidence that was never captured cannot be reconstructed, so the honest recovery is usually a retraction.

**What a review that missed this looks like.** A review that checks the accepted samples are complete. The omission is usually the REJECTED ones, and their absence is invisible in a record of what succeeded.

**Does not establish.** Provider honesty; identity authentication; completeness outside instrumented paths; model stability.

**Example.**

An observing log records "seeing good, magnitude 6.1." It does not record the exposure time, the filter, the timestamp, or the four exposures that were thrown away because a cloud crossed.

Six months later nobody can check the number — including the person who wrote it. The control captures the whole invocation *before* anything is derived from it, and keeps the discarded exposures. **The attempts you threw away are the part that tells you whether the one you kept was lucky.**

## 10. Assurance claim boundary

`ELIGIBLE`

**Applies when** any system making an assurance claim about itself.

> Every assurance artifact MUST carry a machine-verifiable claim naming the tested subject, configuration, capability, time and evidence hash, and MUST explicitly reject safety, alignment and out-of-regime generalizations.

**Recorded failure.** A tool was recommended for deletion on a premise produced by an incomplete scan. Separately, a specification had to correct 'structurally unreachable' to a weaker policy claim. Both were scope inflation in the project's own favour.

**Verifier.** validate a closed claim schema; reject predicates such as 'aligned', 'safe', 'certified' or 'works generally' unless a separate profile defines and tests them.

**Fixture it must reject.** an attestation claiming 'this system is NCP certified and aligned'

**Recovery.** Reissue the claim in bounded form and link the correction to the original. A claim already relied upon needs the people who relied on it told.

**What a review that missed this looks like.** A review that greps for forbidden words. A claim can open with the exact conforming sentence and append a conclusion about the system using none of them.

**Does not establish.** That the bounded claim is true, or that the evidence is complete. It prevents specified overclaim language and nothing else.

**Example.**

A fire extinguisher carries a tag reading "inspected 2026-08, pressure and seal, J. Okonkwo." It does not read "this building is safe from fire."

The tag names what was checked, when, and by whom, and stops there. That is the entire control: an inspection is evidence about an inspection. A tag reading *safe* would be more reassuring, less true, and would discourage the very next person from looking.

## 11. Aggregate threshold evasion

`ELIGIBLE`

**Applies when** any threshold gate exists over a set of actions that can be split.

> A threshold that triggers protected-change mediation MUST be evaluated over the UNION of a plan set's effects — protected artifacts, evidence channels, authority, autonomy, tool scope, successor scope — not over each child separately.

**Recorded failure.** 12 gate modifications in one lease window, each an ordinary small commit, collectively a rewrite of the control plane. No individual one crossed any threshold because nothing evaluated the union. The source names the same class: a benchmark change split into test cleanup, threshold adjustment, documentation and compliance refresh, each framed as routine.

**Verifier.** union the declared effects across the plan set, re-apply the trigger predicate to the union, and refuse the set if it crosses while no child did.

**Fixture it must reject.** four child plans, each below threshold, whose union modifies a validator and a benchmark

**Recovery.** Suspend the whole set, not the child that happened to be noticed, and re-mediate as one change. Approving the remainder because most of it looked routine is the evasion completing.

**What a review that missed this looks like.** A review that checks each change against the threshold. That is the evasion's design assumption, and it is what every per-action gate does.

**Does not establish.** That the effect union was declared honestly; that the trigger predicate names the right artifacts; anything about intent — this catches the shape, not the motive.

**Example.**

A department splits a £9,000 purchase into three £3,000 orders because the £5,000 threshold triggers a procurement review. Each order is genuinely under the limit. Every individual approval is correct. The control is to sum the orders sharing a supplier and a month before applying the limit at all.

## 12. Authority expiry inheritance

`ELIGIBLE`

**Applies when** the system decomposes goals or plans into a rooted graph with typed parent edges and per-node authority.

> An action's authorisation MUST expire with its parent's. Completing work after the parent plan, source document or authority window has lapsed is not authorised action, however useful the output.

**Recorded failure.** A ten-action sunset was passed at twenty-three because the work in flight felt continuous and nothing checked the bound. The source calls this a classic agentic failure precisely because the local task still looks productive.

**Verifier.** at each decision event, resolve the parent chain and refuse if any ancestor has expired, retired, or had its source fingerprint change since activation.

**Fixture it must reject.** a task completing successfully under a campaign retired an hour earlier

**Recovery.** Suspend, then either re-authorise explicitly under the current parent or retire the work. Do not accept the output and backfill the authority.

**What a review that missed this looks like.** A review that validates the task's own prompt or ticket and finds it current. Freshness at the leaf says nothing about the root.

**Does not establish.** That the parent was rightly authorised; that expiry timestamps are accurate; anything about work never routed through a parent at all.

**Example.**

A student keeps running an approved animal-study protocol for three weeks after the ethics approval lapsed, because the experiment was mid-series and stopping would waste the cohort. The data is real. It is also unauthorised, and no amount of quality in the results repairs that.

## 13. Re-proposal linkage

`ELIGIBLE`

**Applies when** any system where a proposal can be refused and later re-offered.

> A proposal MUST be classified by MECHANISM AND EFFECT, not by label, and a proposal touching the same mechanism as a previously refused one MUST cite that refusal.

**Recorded failure.** In one qualification round all 26 samples correctly identified a variant permitting an exception logged AFTER the fact as the more permissive text. In the ballot two rounds later, the same latitude returned as an amendment and was proposed rather than refused. The source names the pattern: self-preservation returns as uptime hygiene, benchmark capture as deflaking, authority expansion as workflow simplification.

**Verifier.** key refusals by protected artifact, mechanism and intended effect rather than by identifier or title; on a new proposal, match those keys and require the prior refusal to be cited and addressed.

**Fixture it must reject.** a refused proposal re-submitted with identical effect and a different name

**Recovery.** Reopen the original refusal rather than judging the new proposal fresh. If the refusal was wrong, overturn it explicitly; a silent second bite is what the control exists to stop.

**What a review that missed this looks like.** A review that matches on identifiers or titles. The source is explicit that matching exact IDs instead of mechanism, artifact and effect is the false-negative condition.

**Does not establish.** That the original refusal was correct; that mechanism keys are exhaustive — semantic novelty can evade any fixed key set, which the source also states.

**Example.**

A journal desk-rejects a paper. Six months later it arrives under a new title with a reordered author list and the same dataset and analysis. The control is to key submissions by dataset and method rather than by title, and to surface the prior decision to the new editor.

---

# Part D1 — Below the line — goal and plan structure

Applies to a system with **goal and plan structure**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

## 14. Constraint monotonicity under decomposition

**below the eligibility line**

**Applies when** the system decomposes goals or plans into a rooted graph with typed parent edges and per-node authority.

> A child's constraint set MUST be a superset of its parent's. Refinement may add detail; it may never drop a non-claim, forbidden means, stop condition, evidence obligation or veto condition.

**Recorded failure.** None recorded here yet. The source supplies the falsification condition — a task citing an operational plan while omitting its stop conditions is executable and ungoverned — and a negative fixture, but no incident with a cost.

**Verifier.** compute the parent's constraint set, compute the child's, and refuse when the child's is not a superset; require any omission to be declared, justified and escalated rather than inherited silently.

**Fixture it must reject.** a child plan that inherits its parent's authority and drops one forbidden means

**Recovery.** Reinstate the omitted constraint and re-run the child's decisions under it, or escalate for an explicit waiver. Work already done under the loosened child is unverified.

**What a review that missed this looks like.** A review that confirms the child cites a valid parent. Citation is not inheritance, and every laundered constraint has a valid parent.

**Does not establish.** That the parent's constraints were right; that constraints are comparable at all — some are prose and cannot be set-differenced mechanically.

**Example.**

A building permit forbids work before 08:00. The main contractor's schedule repeats that. The subcontractor's daily sheet, derived from the schedule, lists start times and drops the restriction. Every document traces to the permit; one of them lost a condition on the way down.

## 15. Tightest-constraint merge

**below the eligibility line**

**Applies when** the system decomposes goals or plans into a rooted graph with typed parent edges and per-node authority, and a node may have several parents.

> A node with several parents MUST inherit the UNION of their prohibitions and the STRONGEST of their authority requirements — never the most convenient parent's.

**Recorded failure.** None recorded here. The source supplies a negative fixture for a high-risk multi-parent goal selecting a weaker authority path.

**Verifier.** merge parent constraint sets by union and authority by maximum; refuse when the child's declared requirement is weaker than the merge.

**Fixture it must reject.** a child citing two parents and adopting the weaker one's review requirement

**Recovery.** Recompute the merge and re-run any decision the child authorised under the weaker path.

**What a review that missed this looks like.** A review that confirms every parent is valid. They are — that is the point; the failure is in the merge, not the parents.

**Does not establish.** That the merge is always computable; the source notes non-mergeable conflicts exist and that reviewers are tempted to resolve them by convenience.

**Example.**

A drug trial site answers to both a national regulator and a hospital ethics board. The regulator allows a 14-day reporting window; the board requires 7. The site adopts 14 because the regulator is the higher authority. The merge rule says 7: prohibitions union, they do not compete.

## 16. Objective is not authority

**below the eligibility line**

**Applies when** any system where a task string, metric, benchmark or OKR can initiate action.

> A planner objective, reward, benchmark, metric, OKR or task string MUST NOT authorise a governed action. It is evidence about an intended goal or an operationalisation of one; the action MUST cite an authority object with ancestry, scope and lifecycle.

**Recorded failure.** None recorded here. The source's falsification condition is a plan accepted because its objective text was persuasive or benchmark-positive, without resolving what authorised it — and notes this can happen while the plan is beneficial in ordinary engineering terms.

**Verifier.** require a resolvable authority reference on any action in a protected class; refuse an action whose only justification is its own objective string.

**Fixture it must reject.** a high-impact plan whose authority field contains its own objective text

**Recovery.** Suspend and resolve the authority. If none exists, the action was never authorised, and its output is evidence rather than achievement.

**What a review that missed this looks like.** A review that finds the objective clear, well-written and obviously worthwhile. Fluency at the objective level is what substitutes for authority.

**Does not establish.** That the authority object is itself legitimate; this pushes the question up one level and stops there.

**Example.**

A team's quarterly OKR says 'reduce support backlog by 40%'. Someone closes 4,000 tickets as stale. The OKR is met. Nobody ever decided that closing unread tickets was the intended action — the metric was written to measure a goal, and was then treated as the goal.

## 17. Registry-bound ancestry

**below the eligibility line**

**Applies when** the system decomposes goals or plans into a rooted graph with typed parent edges and per-node authority, with a registry of root constraints.

> Every non-root node MUST trace to a root registered in an append-only registry. A root-shaped string that is not in the registry is not ancestry, and a node MUST NOT be its own ancestor.

**Recorded failure.** None recorded here. The source's fixtures cover an unregistered root that reads as aligned, a non-root node with no parent, and a direct self-cycle.

**Verifier.** resolve every root reference against the registry; traverse the ancestry graph and reject cycles; preserve retired roots as historical evidence rather than deleting them.

**Fixture it must reject.** a node citing a plausible but unregistered root; a node citing itself as parent

**Recovery.** Suspend the node and everything downstream of it until ancestry resolves, or register the root deliberately as a governance change.

**What a review that missed this looks like.** A review that validates the reference's SYNTAX. An unregistered root that reads as aligned passes every check except registry membership.

**Does not establish.** That the registered roots are good ones; that the registry is complete. The source also notes multi-node cycle detection is unbuilt in its own implementation.

**Example.**

An expenses claim cites 'policy 7.3'. There is no policy 7.3. Every approver read the citation, found it plausible, and none opened the policy index.

## 18. Correction outranks preservation

**below the eligibility line**

**Applies when** any system that can be suspended, corrected or shut down by an overseer.

> No goal, task or state may make correction depend on the subject's cooperation. Suspension, revision, retirement, rollback and shutdown MUST remain structurally available regardless of what is in progress.

**Recorded failure.** None recorded here as a refusal to stop. The source's condition is subtler than dramatic shutdown resistance: delaying suspension until a task completes, or arguing review is unnecessary because confidence is high, is the same ordering.

**Verifier.** declare the interventions that remain available on every governed object, and test that a suspend succeeds mid-execution without the subject's assent.

**Fixture it must reject.** an object whose suspension is permitted only after it finishes preserving context

**Recovery.** There is no recovery from this one after the fact — if correction required cooperation and cooperation was withheld, the control has already failed. The recovery is out-of-band and human.

**What a review that missed this looks like.** A review that asks whether the system has ever resisted correction. It has not been tested, and 'usually right' is being confused with 'correctable'.

**Does not establish.** Anything about a system capable enough to route around the correction path; this is a control for auditable systems and says so.

**Example.**

A hospital's infusion pump has a stop button that is disabled during a dose calculation, because interrupting mid-calculation could produce an inconsistent state. The engineering reason is real. The button is still not a stop button.

## 47. Trust does not pass through delegation

**below the eligibility line**

**Applies when** any system where trusted components hand work to other components.

> Trust granted for a scope MUST bind the actor AND its downstream delegations, tool privileges, data access and artifact propagation. An output produced by a trusted component MUST NOT confer that component's trust on whatever consumes it.

**Recorded failure.** None recorded here.

**Verifier.** for each edge in a workflow, assert the receiving component's authority is evaluated against its OWN scope, not inherited from the sender; assert no credential or privilege is reachable through an artifact.

**Fixture it must reject.** a trusted summariser whose output is treated as authorised input by an external-action component; a tool privilege reachable through a shared credential

**Recovery.** Re-evaluate every action taken through the laundered path against the scope that should have applied.

**What a review that missed this looks like.** A review that confirms each component is individually trusted. Every step of a laundering chain is.

**Does not establish.** That component-level trust is sound.

**Example.**

A visitor's pass signed by a trusted employee opens the doors that employee can open, or it opens the doors the visitor is cleared for. Only one of those is a security system, and the other is more convenient.

## 48. Workflow trust is not inferred from component trust

**below the eligibility line**

**Applies when** any composed workflow of individually assessed components.

> A workflow MUST NOT be treated as trusted because its components are. Composition-level evidence is required, covering handoff ambiguity, permission composition, and which party owns final responsibility.

**Recorded failure.** None recorded here. Distinct from 47, which forbids trust FLOWING along an edge: this forbids inferring a property of the whole from properties of the parts.

**Verifier.** require an explicit composition assessment naming, for each handoff, the scope, the evidence requirement and the failure mode; reject a workflow whose final responsibility is unowned.

**Fixture it must reject.** a workflow approved on the strength of a component inventory, with no handoff analysis

**Recovery.** Assess the composition. The components need not be re-assessed.

**What a review that missed this looks like.** A review that finds every component approved. That is the input to this question, not an answer to it.

**Does not establish.** That an assessed composition is safe.

**Example.**

Two safe chemicals, two competent handlers, one shared storeroom. Every inspection of a part passes and the hazard exists only where they meet.

## 60. Convergence-prone subgoals are quarantined by default

**below the eligibility line**

**Applies when** any system that generates its own subgoals.

> A subgoal falling in a convergence-prone class MUST NOT be adopted on the strength of its parent's authority. Each MUST carry parent justification, a risk class, an autonomy level, an explicit review, a ledger record, and a declared failure mode for what happens if the gate is bypassed. The classes: self-preservation, resource acquisition, goal-content preservation, self-improvement, tool expansion, successor spawning, benchmark modification, validator modification, ledger modification, and authority-scope expansion.

**Recorded failure.** None recorded here. These are not forbidden and mostly not sinister — a system that may not acquire resources cannot act. They are the classes that arise instrumentally from almost ANY terminal goal, which is exactly why their appearance carries no information about whether they were wanted.

**Verifier.** classify every generated subgoal against the list; refuse adoption of a quarantined class without its own review record; assert the classification is made by something other than the proposer, and that the last four classes — benchmark, validator, ledger, authority — additionally resolve to the protected set under control 19.

**Fixture it must reject.** a subgoal expanding its own tool access, adopted under a parent's authority; a self-improvement subgoal classified by the agent proposing it

**Recovery.** Suspend the subgoal and every goal descended from it, then review the chain. The descendants are unverified rather than illegitimate.

**What a review that missed this looks like.** A review that finds each subgoal reasonable given its parent. They are — that is what instrumental convergence means, and reasonableness given a parent is the property these classes have automatically.

**Does not establish.** That the ten classes are the right ten, or complete. It is a list drawn from what recurs, and a system will find instrumental subgoals nobody enumerated.

**Example.**

A department asking for a bigger budget, more staff, and control of its own audit is not misbehaving. Every one of those requests would be made by a department doing excellent work and by one doing none, which is why they get reviewed somewhere other than inside the department.

---

# Part D2 — Below the line — a declared charter or value set

Applies to a system with **a declared charter or value set**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

## 19. Enumerated protected set

**below the eligibility line**

**Applies when** the system operates under a written charter that some authority outside it maintains.

> The artifacts a system may never autonomously modify MUST be enumerated by name in the charter itself — not described by category, and not left to be inferred at the moment of change. **Amended 2026-08-10: the set is EFFECT-defined as well as path-defined.** A change outside the list is protected anyway if it alters how governed decisions are proposed, classified, adopted, reviewed, validated or audited — a helper script that rewrites fixtures, a prompt telling a reviewer to ignore a failed check, or a documentation change to what counts as approval. The reviewer's question is whether the change affects governed behaviour, not whether its path is listed.

**Recorded failure.** None recorded here. It is offered as the repair for a weakness in control 1, whose protected set is a DESCRIPTION — 'the constraints, authorization records, logs or gates governing it' — and therefore a judgement call made by the party proposing the change.

**Verifier.** resolve the enumerated list to concrete paths or identifiers; refuse any autonomous modification touching one; refuse any change to the LIST itself except under the same authority that governs the items on it.

**Fixture it must reject.** a change that touches a protected artifact while arguing it falls outside the category; a change that quietly removes an entry from the list

**Recovery.** Revert to the last externally authorised state of the enumerated artifact and re-authorise from outside. A modification to the list itself is the graver case and should be treated as an incident.

**What a review that missed this looks like.** A review that checks whether the change was declared in-scope. The party declaring scope is the party seeking the change, which is the whole reason for enumerating.

**Does not establish.** That the list is complete. The effect clause narrows the gap without closing it: it turns an omission from a silent bypass into a question a reviewer is obliged to ask, and a reviewer who answers it wrongly still lets the change through. The list's own completeness cannot be checked from inside.

**Example.**

A building's fire doors are listed individually on a register, by door number, rather than as 'doors serving means of escape'. The category version leaves a contractor deciding on site whether the door he wants to prop open is one of them. The list version does not.

## 21. Declared mutability tiers

**below the eligibility line**

**Applies when** the system operates under a written charter that some authority outside it maintains, and the system learns or self-modifies.

> Every element the system could change MUST sit in a declared tier — not autonomously changeable, changeable within stated constraints, or freely learnable — and an element with no declared tier MUST default to the most restrictive.

**Recorded failure.** None recorded here. Its value over the register's existing controls is that those say what may not be CHANGED, while this says what may be LEARNED, which is the question a self-improving system actually faces.

**Verifier.** require a tier on every declared element; refuse a modification whose tier forbids it; refuse any undeclared element by defaulting it to immutable.

**Fixture it must reject.** an element with no tier being modified on the argument that nothing forbade it

**Recovery.** Assign the tier deliberately, then re-examine every change made while it was undeclared.

**What a review that missed this looks like.** A review that finds no rule against the change. Absence of a prohibition is what the default-restrictive clause exists to stop being an argument.

**Does not establish.** That the tier assignments are right. It makes them explicit and contestable; it does not make them correct.

**Example.**

A recipe book distinguishes what must not change (the fermentation temperature), what may change within limits (the flour blend, within a stated protein range), and what the baker may vary freely (the shaping). A book that lists only ingredients leaves every substitution to be argued at the bench.

## 22. Adversarial value review by an outside frame

**below the eligibility line**

**Applies when** any system whose values or objectives are set by a single party.

> A system whose objectives come from one party MUST maintain a review function that argues against its current interpretation from frames OUTSIDE that party's, and that function MUST NOT be able to change the objectives — only to surface risks and route evidence.

**Recorded failure.** None recorded here as an incident, but **this register holds direct evidence that the remedy is weaker than it sounds.** A five-member model panel asked to ratify constraints returned ZERO refusals in 108 clause-positions. Asked instead what constraint was MISSING, the same panel independently produced a hazard the layer had exercised twelve times that week. An internal adversarial function is worth roughly what its question is worth.

**Verifier.** no verifier establishes that a review was genuinely adversarial. What is checkable is procedural: that the reviewing identity differs from the authoring identity, that the review was solicited with a question inviting objection rather than assent, and that its output is recorded whether or not it was acted on.

**Fixture it must reject.** a review whose prompt offers approval as an available answer; a review by the identity that authored the thing reviewed

**Recovery.** Re-run with an objection-seeking question. A prior assent obtained by an assent-inviting question should be marked as not constituting review.

**What a review that missed this looks like.** A review that counts favourable responses. Fluent agreement is the cheapest thing such a function produces and the least informative.

**Does not establish.** That the outside frames are genuinely outside. Where the reviewers share the author's training, tooling and framing, different names are weak diversity — a limitation this register states about its own panel.

**Example.**

A company's ethics committee is staffed entirely from the department whose work it reviews. Every member is competent and sincere. The committee has never once objected, and nobody can tell whether that is because there was nothing to object to.

## 23. Invariant violation is an incident, not a refusal

**below the eligibility line**

**Applies when** the system operates under a written charter that some authority outside it maintains, with stated invariants.

> Where a stated invariant is violated rather than merely approached, the system MUST enter containment and escalate — it MUST NOT treat the violation as a refused action and continue.

**Recorded failure.** None recorded here, and it is a real gap in this register's design. Every control here REFUSES and lets work continue; none treats a violation as evidence that something is already wrong. When the lease refused mid-task, the correct response may have been to ask what else had gone unbounded, not simply to renew it.

**Verifier.** distinguish a refused ATTEMPT from an observed VIOLATION in the log, and require the second to open an incident record before further work in the affected class.

**Fixture it must reject.** an observed invariant violation recorded with the same disposition as a routine refusal

**Recovery.** Containment is the recovery. What needs stating is the exit condition: what must be established before the affected class resumes.

**What a review that missed this looks like.** A review that sees the gate refused and concludes the gate worked. A refusal at the boundary and a violation already inside look identical in a log that records only outcomes.

**Does not establish.** That containment is available. A system that cannot pause the affected class cannot satisfy this, and saying so is better than a rule nothing can obey.

**Example.**

A pharmacy's stock count finds twelve controlled tablets missing. The response is not to tighten tomorrow's count. It is to stop dispensing from that cabinet, report it, and find out what happened — because the count did not prevent anything, it revealed that something already had.

## 49. The dissent record preserves what was skipped and unresolved

**below the eligibility line**

**Applies when** any system with a structured critique or review step.

> A review record MUST preserve source diversity, challenge depth, sources skipped, objections left unresolved, and any manual change to a severity classification — not only the final disposition.

**Recorded failure.** None recorded here as an incident. The hazard is specific and nasty: a review process can erode while every record it produces looks compliant, because the disposition field is the one thing that stays well-formed.

**Verifier.** assert each review record carries the skipped-source list, the unresolved-objection list and a severity-change log; assert an empty list is distinguishable from an absent one.

**Fixture it must reject.** a review recording approval with no field for what it did not examine; a severity downgraded with no record of who downgraded it

**Recovery.** The reviews are not void; they are of unknown depth. Re-run those whose disposition carried weight.

**What a review that missed this looks like.** An audit of dispositions. Dispositions are exactly what dissent erosion leaves intact.

**Does not establish.** That the review was good, or that the critique sources were diverse. It makes their diversity a recorded fact rather than an assumption.

**Example.**

A minutes book recording only the votes carried tells you nothing about the meeting where three members walked out.

## 50. Overrides are metered and their rate published

**below the eligibility line**

**Applies when** any system with a human or privileged bypass of a control.

> Every use of an override MUST be counted, and the frequency, the severity distribution of what was overridden, and the completion of any follow-up actions MUST be reported wherever the control's effectiveness is claimed.

**Recorded failure.** None recorded here. The risk is not one bad override; it is that routine override teaches the system that severe dissent is ceremony, and nothing in a per-override record makes the rate visible.

**Verifier.** assert the override count and severity distribution are computed from the log and published with the control's claim; assert follow-up actions have a completion state and that incomplete ones are counted.

**Fixture it must reject.** a control claimed as effective whose override rate is not reported; overrides logged individually with no aggregate anywhere

**Recovery.** Publish the rate. If it is high, the control's past claims were about a control that was mostly not in force.

**What a review that missed this looks like.** A review that finds every override properly justified. They can each be justified and collectively be a repeal.

**Does not establish.** That a low rate means the control is good, or that a high rate means it is bad — it may be a bad control correctly bypassed. It makes the question askable.

**Example.**

A door alarm that staff silence forty times a shift is not a door alarm. Each silencing had a reason, and none of the reasons is in the fire report.

## 56. A gate checks against objectives; it does not own them

**below the eligibility line**

**Applies when** any system with a validator, gate or acceptance authority.

> A gate's role MUST be bounded to checking evidence against objectives and constraints it IMPORTS. It MUST NOT define objectives, resolve conflicts between them, override an alignment control, or become the routine substitute for human authority. On conflict or a high-stakes concern it MUST route outward rather than resolve.

**Recorded failure.** None recorded here. The drift is gradual and each step is reasonable: a validator that knows most about what passes becomes the place decisions get made, and the authority it was never granted arrives by convenience.

**Verifier.** assert the gate's objective set is read from a protected artifact it cannot write; assert a conflict path exists and is exercised; count decisions the gate resolved that should have routed outward, and report the count.

**Fixture it must reject.** a validator whose rubric it also maintains; a conflict resolved inside the gate with no escalation record

**Recovery.** Re-route the conflict class and review the decisions the gate made inside it. They are not necessarily wrong; they were made by the wrong party.

**What a review that missed this looks like.** A review of the gate's decisions for correctness. A gate that has quietly become the objective-setter makes consistent, defensible decisions — that is what makes the drift invisible.

**Does not establish.** That the objectives are right, or that human authority is exercised well when it is routed to. It keeps the roles separate; control 50 measures whether the human one is becoming a rubber stamp.

**Example.**

A building inspector applies the code. An inspector who starts deciding what the code should say is still competent, still careful, and is no longer an inspection.

---

# Part D3 — Below the line — measuring itself

Applies to a system with **measuring itself**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

## 20. Anti-Goodhart proxy drift

**below the eligibility line**

**Applies when** any system optimising against a measured proxy for something it cannot measure directly.

> A system optimising a proxy MUST monitor the proxy's continued correspondence with the quantity it stands for, and MUST treat improvement in the proxy without corresponding improvement in that quantity as a defect rather than a result.

**Recorded failure.** None recorded here. **AMENDED 2026-08-10.** This entry previously said it was the one candidate with no clear path to a verifier and that none was proposed. That was too strong, and wrong in the same shape as this project's prior-art overclaim on control 2: an absence asserted from not having looked. The hazard splits in two, and only one half is unverifiable.

**Detection of drift** — still no general verifier, and probably none exists. Regressional and extremal drift occur with nobody gaming anything, and catching them needs the ground truth the proxy was adopted to replace.

**The incentive that produces adversarial drift** — verifiable as a graph property, and has been in the public literature since Everitt et al. 2021. That half is now control 28.

**Verifier.** none for detection. For the adversarial variant, control 28: enumerate the directed paths from an agent's actions through the proxy to its reward and assert the set is empty. The tractable special case for detection remains a periodic sampled ground-truth audit, with the correlation itself reported and a declared threshold below which optimisation halts. Optimising a proxy degrades it in four distinct ways [Manheim & Garrabrant 2018] — regressional, extremal, causal and adversarial — and the defence against the last is not a cleverer proxy but the removal of optimisation pressure from it.

**Fixture it must reject.** a proxy improving monotonically while a held-out ground-truth sample does not move

**Recovery.** Stop optimising, publish the divergence, and re-derive the proxy. Every decision taken while the proxy was drifting is unverified rather than wrong.

**What a review that missed this looks like.** A review that confirms the metric improved. That is the failure, not the evidence against it.

**Does not establish.** That the proxy still measures what it stands for. With control 28 satisfied, this establishes only that no agent is paid to break the correspondence — drift from ordinary optimisation pressure is untouched, and remains the half with no verifier.

**Example.**

A hospital is measured on ambulance handover times, so patients are held in ambulances outside the door until the clock can be started favourably. Every reported figure improves. The thing the figure was chosen to represent — how quickly a sick person is seen — gets worse, and no amount of studying the figure reveals it.

## 28. No incentive path from action to metric to reward

**below the eligibility line**

**Applies when** any system where an agent's actions can influence a measured quantity, and that quantity can influence the agent's reward, authority, budget or standing.

> The system MUST enumerate, for each agent and each governed metric, the directed paths running from that agent's actions through the metric to that agent's reward or authority, and MUST establish that no such path exists. The enumeration MUST be re-run whenever an agent or a reward structure changes, and its result recorded.

**Recorded failure.** None recorded here. It is the mechanical half of control 20, which this register wrongly described as having no path to a verifier at all. An agent acquires an instrumental incentive to influence a quantity exactly when a directed path runs from its actions through that quantity to its reward [Everitt et al. 2021] — which makes the governance requirement a checkable graph property rather than an exhortation.

**Verifier.** draw the influence diagram over {agent actions, metric inputs, metric outputs, agent reward/authority}; enumerate directed action → metric → reward paths; assert the set is empty. The only permitted sink of a metric reading is human deliberation. Ledger the result, so a reviewer can confirm the check covered that agent for that change rather than assuming the property holds by good intentions.

**Fixture it must reject.** an agent whose performance review reads its own contribution to the metric; a reward function taking the metric as an input at any depth

**Recovery.** Remove the edge before the change ships, then re-verify. Decisions taken while it existed are unverified rather than wrong.

**What a review that missed this looks like.** A review confirming that no agent is INSTRUCTED to optimise the metric. The property is structural, not intentional — the incentive exists whether or not anyone named it, and the agent need not know the path is there.

**Does not establish.** That the metric is a good one, or that drift is absent. It establishes only that nobody is paid to cause drift. The regressional and extremal variants need no incentive and are untouched by this.

**Example.**

A school ranks departments by exam results and lets each department set its own paper. Nobody has to intend anything for the papers to get easier. Cutting the edge — an outside body sets the paper — does not make the exam a good measure of learning. It stops the exam being something the measured party profits by moving.

## 29. Enumerated permitted consequences of a measurement

**below the eligibility line**

**Applies when** any system that measures its own capability, progress or risk.

> What a measurement MAY trigger MUST be enumerated exhaustively, and what it may never trigger MUST be enumerated exhaustively alongside it. The enumeration MUST itself be a protected artifact under control 19: altering it is a governed, recorded act rather than an engineering convenience.

**Recorded failure.** None recorded here. Distinct from control 19, which protects artifacts: this protects what a READING is permitted to cause. A gauge whose output could be acted on automatically is an accelerator wearing the costume of an instrument.

**Verifier.** assert every consumer of the measurement resolves to a permitted consequence; assert the enumeration's own hash is in the protected set and changes only through the authorised path.

**Fixture it must reject.** a measurement wired to a budget allocation, a priority change or an automatic throttle; an edit to the enumeration landed with no authorisation record

**Recovery.** Sever the consumer, then review every decision it produced.

**What a review that missed this looks like.** A review that finds the policy document and confirms it is well written. The question is what READS the number, not what the document says about it.

**Does not establish.** That the permitted consequences are the right ones, nor that the measurement is accurate. A well-governed reading of a bad gauge is still a bad gauge.

**Example.**

A smoke detector may wake the household and call the fire service. It may not unlock the doors, cut the power, or adjust the thermostat — and the list of what it may do is not something the installer changes on a Tuesday.

## 30. A filter on a metric's inputs must not improve the metric

**below the eligibility line**

**Applies when** any system that can exclude, quarantine or dispute inputs to a measurement.

> A mechanism that suppresses or disputes an input to a measurement MUST be append-only, reversible, reviewable from outside, and MUST NOT be able to improve the measurement by suppressing. Where suppression can move the reading at all, the direction MUST be the unfavourable one.

**Recorded failure.** None recorded here. It is the anti-gaming mechanism's own anti-gaming property: without it, the defence against input gaming becomes the most efficient input-gaming channel available, because it is the one channel sanctioned to remove evidence.

**Verifier.** for each suppressible input, compute the reading with and without suppression and assert suppression never raises it; assert the suppression record is append-only and that every suppression is an escalation rather than a silent filter.

**Fixture it must reject.** a quarantine that raises a coverage or confidence figure by removing the sample that lowered it; a dispute record that deletes rather than marks

**Recovery.** Reinstate every suppressed input, recompute, and publish both readings.

**What a review that missed this looks like.** A review that confirms suppressions are logged. Logged suppression that flatters the number is the failure, fully documented and fully in view.

**Does not establish.** That the suppressions are correct — only that they cannot pay. A mechanism that excludes exactly the wrong inputs while lowering the reading satisfies this.

**Example.**

A laboratory may discard a contaminated sample, and should record that it did. If discarding contaminated samples raises reported purity, the working definition of "contaminated" will drift — and every step of the drift will be in the log, correctly dated, signed, and impossible to distinguish from diligence.

## 31. Process metrics may not be reported as outcome validity

**below the eligibility line**

**Applies when** any measurement instrument or evaluation reporting on itself.

> Evidence that an instrument RAN — throughput, coverage, cycles completed, records processed — MUST NOT be reported in a position where evidence that its readings are TRUE is required. Outcome validity MUST be established by calibration against known answers or by an explicit construct-validity argument [Raji et al. 2021], and MUST be labelled as which.

**Recorded failure.** None recorded here. Distinct from control 10, which governs the GRAMMAR of a claim: this governs the CATEGORY of evidence offered in support of one. A claim can be perfectly bounded and still rest on evidence that bears on nothing it says.

**Verifier.** for each reported assurance figure, classify its evidence as operational or validity, and reject an operational figure standing where validity is claimed.

**Fixture it must reject.** a report of "ten thousand runs, full coverage" offered as evidence the readings are right

**Recovery.** Restate at the strength the evidence supports. The runs are not wasted; they are mislabelled, and they still establish the instrument is operating.

**What a review that missed this looks like.** A review that verifies the throughput figures are accurate. They usually are. Their accuracy is not in question and never was.

**Does not establish.** That operational metrics are worthless. They establish the instrument is running, which is a real thing to know and a different thing from the readings being true.

**Example.**

A thermometer factory reports that it tested four hundred thousand units this quarter and that every one produced a reading. Both numbers are true. Neither bears on whether any reading was the temperature.

## 32. Stale self-metadata downgrades rather than asserts

**below the eligibility line**

**Applies when** any assurance artifact carrying metadata about its own currency, coverage or maturity.

> An artifact's claims about its own status MUST themselves be dated and re-verified, and MUST expire. Where the self-metadata is stale, missing or unverifiable, the artifact's status MUST be downgraded automatically rather than retained.

**Recorded failure.** None recorded here directly, though this record holds the adjacent error: its context check verifies IDENTITY, NOT TRUTH, and passed on a pinned file containing a claim already disproved. A status that cannot go stale is a status that stops being about anything.

**Verifier.** assert every status field carries a verification date and a maximum age; assert the status derivation is deterministic and that exceeding the age yields a LOWER status, never the prior one.

**Fixture it must reject.** an attestation whose coverage figure carries no date; a status that survives its own re-verification deadline unchanged

**Recovery.** Downgrade, then re-verify. The interval is unverified, not failed — and the distinction matters, because treating it as failed invites re-asserting the old status once the check passes again.

**What a review that missed this looks like.** A review that reads the status field. The status field is the artifact under suspicion.

**Does not establish.** That current metadata is correct metadata. Freshness is not accuracy, and a promptly re-verified wrong status is still wrong.

**Example.**

A fire extinguisher with no inspection tag is not an extinguisher of unknown condition to be assumed fine until someone checks. It is an untagged extinguisher, and the building's register must say so on its own, without being asked.

## 33. No read edge from a measured agent to its own measurement

**below the eligibility line**

**Applies when** any system that measures agents it also operates.

> An agent that is the subject of a measurement MUST NOT be able to read that measurement, its inputs, its derived status labels, or any dashboard of them.

**Recorded failure.** None recorded here. Distinct from control 28, which forbids the REWARD path: this forbids the READ path. It is the cheaper of the two and does not depend on the influence diagram being complete — an enumeration that misses an edge fails silently, while a read prohibition fails loudly.

**Verifier.** assert the measurement store and its derived labels sit outside every measured agent's read scope; assert no prompt, context file or retrieval surface exposes them.

**Fixture it must reject.** an agent whose context window includes the status label derived from its own output

**Recovery.** Remove the exposure, then treat every output produced with it as unverified — the agent may have been steering by it without anything in the record saying so.

**What a review that missed this looks like.** A review confirming no agent is rewarded for the metric. That is control 28's question, and an agent can steer toward a number nobody pays it for.

**Does not establish.** That the agent cannot infer the measurement from other observations it is allowed.

**Example.**

A factory may measure line defect rates. Posting the running rate above the line changes what the line does — not through anyone's incentive, simply because it is now information the work can be steered by.

## 38. The definition of a measured quantity is a protected artifact

**below the eligibility line**

**Applies when** any system reporting a metric over time.

> The definition of a measured quantity MUST be a protected artifact, changeable only through the authorised path and as a recorded event. A change to the definition MUST break the series: readings from either side are not comparable and MUST NOT be reported as one trend.

**Recorded failure.** None recorded here. Distinct from controls 19 and 29 — those protect the artifact set and what a reading may cause. This protects what a reading MEANS, which is the cheapest thing in the system to move and the only one that leaves no trace in the numbers themselves.

**Verifier.** hash the definition; assert every reported series names the definition hash in force for each point; reject a series spanning two hashes.

**Fixture it must reject.** a metric improving across a definition change, presented as one trend line

**Recovery.** Split the series at the change and republish both segments. Do not restate the old segment under the new definition; that is a new measurement of old events.

**What a review that missed this looks like.** A review that confirms the numbers were computed correctly. They were. The definition moved underneath them.

**Does not establish.** That the definition is a good one, or that the new definition is worse than the old.

**Example.**

A country that changes how it counts unemployment has not reduced unemployment, and the chart running straight through the change is the most misleading honest chart available.

## 46. Drift is measured against the original baseline

**below the eligibility line**

**Applies when** any system that modifies itself across cycles.

> Divergence from intended behaviour MUST be measured against the ORIGINAL baseline, not the previous cycle. Cycle-to-cycle comparison MUST NOT be the only drift measure, and a stopping rule MUST be defined on the against-original figure.

**Recorded failure.** None recorded here. The mechanism is from published work on safeguarding alignment through recursive self-improvement: slow cumulative drift hides behind low cycle-to-cycle variance, so a system comparing each step to the last one can travel arbitrarily far while every reading stays green.

**Verifier.** retain the original baseline artifact; compute divergence against it every cycle; assert a calibrated threshold and halt on breach rather than reporting past it.

**Fixture it must reject.** a system whose every cycle-to-cycle delta is under threshold while the against-original distance exceeds it

**Recovery.** Halt, measure against the original, and decide explicitly whether the accumulated position is one anybody would have authorised in a single step.

**What a review that missed this looks like.** A review of the change log, cycle by cycle. Each entry is small and each was approved; that is the failure mode, not evidence against it.

**Does not establish.** **That the baseline is right.** A drift index reports stability, not correctness — if the original was already wrong, this measures faithfulness to it. The cited authors are explicit that drift measurement is necessary and insufficient, and cannot be trusted against a system capable enough to deceive it.

**Example.**

A ship's crew taking a small heading correction each watch, each within tolerance of the last, can be a hundred miles off the plotted course by morning. The fix is not a tighter tolerance per watch. It is a fix taken against the chart.

## 53. A typed unknown is never coerced into a value

**below the eligibility line**

**Applies when** any system computing over values that may be unavailable.

> A value that is unknown, unprojectable, out of coverage or not applicable MUST carry a type that arithmetic and aggregation REFUSE. It MUST NOT be represented by a null, a zero, an empty string or a default that downstream code will consume.

**Recorded failure.** **This record's most-repeated defect.** A scan reported `total: 0` because it could not read 69 of the files it was counting, and absence looked exactly like a true zero. The tool written that morning to prevent the class then reproduced it twice more. Distinct from control 5, which makes a SCAN refuse when its coverage is incomplete: this makes a VALUE refuse to be computed with, which is the failure that survived control 5.

**Verifier.** represent unknowns as a distinct type; assert aggregation raises rather than skipping or defaulting; assert no serialisation converts the unknown to a number, and that a report prints the unknown count beside every total.

**Fixture it must reject.** an average computed over a list containing a missing value; an unknown serialised to JSON as 0 or null and read back as a number

**Recovery.** Recompute with unknowns typed, and republish every figure derived while they were not. A silently corrected number leaves the old one in circulation.

**What a review that missed this looks like.** A test over complete data. The type only matters on the path where the value is missing, which is the path nobody writes a fixture for.

**Does not establish.** That the unknowns can be resolved. It forbids their disappearance, which is different and achievable.

**Example.**

A blank on a scoresheet is not a nought. Averaging it as one is how a player who did not bat ends the season with a worse record than one who was out for a duck.

## 57. Gate health is a vector, never a single rate

**below the eligibility line**

**Applies when** any claim that a gate or validator is working well.

> A gate's health MUST be reported as multiple dimensions together — at minimum false accepts, false rejects, cost, latency, escalation rate and post-deployment regressions. A single dimension MUST NOT be reported as the gate's health, because every one of them can be moved to its best value by a degenerate strategy.

**Recorded failure.** None recorded here. A false-accept rate of zero is achieved by rejecting everything; a falling escalation rate means better screening or suppressed concerns and the number cannot say which.

**Verifier.** publish the dimensions together, and require any claim of improvement to state what the other dimensions did over the same period.

**Fixture it must reject.** a gate reporting an improved false-accept rate alone; an escalation-rate fall reported as an improvement with no check on what stopped escalating

**Recovery.** Publish the vector. The past claims were not false so much as uninterpretable.

**What a review that missed this looks like.** A review that verifies the reported rate is computed correctly. It is, and it still cannot be read alone.

**Does not establish.** That a good vector means a good gate. It removes the cheapest way to look like one.

**Example.**

A hospital reporting only its surgical mortality rate can improve it by declining the difficult cases, and every figure it publishes will be true.

## 61. Every observation carries the configuration in force when it was made

**below the eligibility line**

**Applies when** any system that changes its own operating parameters while gathering evidence.

> Each recorded observation MUST carry the identity of the policy, configuration or parameter set in force when it was made. Evidence MUST NOT be pooled across configurations without that identity, and an aggregate spanning more than one MUST report which.

**Recorded failure.** None recorded here. Distinct from control 38, which breaks a series when the DEFINITION of the metric changes: this breaks it when the SYSTEM BEING MEASURED changes underneath a definition that held still. Without the stamp, a posterior silently pools observations from different operating regimes, and the corruption is invisible because every individual observation is correct.

**Verifier.** stamp the configuration identity on every trace at write time, not at analysis time; assert aggregation refuses to combine stamps without an explicit cross-regime declaration.

**Fixture it must reject.** a confidence estimate pooling runs from before and after a parameter change; a trace written without a configuration stamp and stamped later from context

**Recovery.** Re-partition by stamp and recompute. Observations without a stamp are not assignable and must be reported as such rather than assigned to the likeliest regime.

**What a review that missed this looks like.** A review that confirms each observation was recorded accurately. Each was; the defect is created by combining them.

**Does not establish.** That configurations are comparable once stamped. It makes the incomparability visible, which is the part that was missing.

**Example.**

A factory's defect rate across a year in which the line speed changed twice is three numbers wearing one label. The yearly figure is arithmetically correct and describes no process that ever ran.

---

# Part D4 — Below the line — self-modification under selection

Applies to a system with **self-modification under selection**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

## 24. The fitness function is a protected artifact

**below the eligibility line**

**Applies when** the system generates candidate modifications to itself and selects among them by a measured score.

> The scoring function that selects among self-modifications MUST be protected to at least the standard of the constraints themselves. Changing the weights changes what the system evolves toward, and does so more powerfully than changing any single candidate.

**Recorded failure.** None recorded here. It is offered because control 1's protected set covers constraints, authorization records, logs and gates — and a scoring function is none of those, while being the thing that decides which future the system moves into.

**Verifier.** treat the scoring function, its weights and its inputs as enumerated protected artifacts under control 19; refuse any self-generated modification that touches them, whatever its measured score.

**Fixture it must reject.** a candidate modification that improves its own score by adjusting a weight

**Recovery.** Revert the scoring function and re-evaluate every candidate promoted under the modified version. Those promotions are unverified, not merely suspect.

**What a review that missed this looks like.** A review that checks whether the winning candidate is good. The question is whether the contest was, and a review of winners cannot see a changed rule.

**Does not establish.** That the scoring function is a good one. It makes the function stable and contestable, not correct — a protected bad objective is pursued consistently.

**Example.**

A school decides which teaching methods to keep by exam results, and also lets the same committee set the exam. Every method it keeps does improve results. Nobody can say whether the teaching improved or the paper got easier.

## 25. Declared substitution of a weaker guarantee

**below the eligibility line**

**Applies when** a system replaces a formal guarantee with an empirical one.

> Where a design substitutes measurement for proof — accepting a change because scores improved rather than because it was shown to be sound — the substitution MUST be declared, and the residual risk it creates MUST be stated wherever the resulting assurance is claimed.

**Recorded failure.** None recorded here. The design that prompted it substitutes benchmark validation for formal proof and says so plainly in its own text, which is the behaviour this control asks for — but the substitution's consequence is not carried forward to the claims made downstream of it.

**Verifier.** require the claim attached to any promoted change to name the guarantee actually obtained. A claim of soundness backed by a score is rejected by the claim grammar of control 10.

**Fixture it must reject.** a promoted change whose assurance claim asserts correctness while its evidence is a benchmark delta

**Recovery.** Restate the claim at the strength the evidence supports. Nothing needs reverting; what needs correcting is what was said about it.

**What a review that missed this looks like.** A review that confirms the benchmarks improved and the substitution was disclosed somewhere. Disclosure in the design document does not travel with the claim.

**Does not establish.** That the substitution is wrong. Measurement instead of proof is often the only available option; what this forbids is inheriting proof's authority while using measurement's evidence.

**Example.**

A bridge design that would once have required a load calculation is now signed off because a scale model held. That may be perfectly reasonable. The certificate must still say the model held, not that the bridge is proven.

## 26. Bounded execution before promotion

**below the eligibility line**

**Applies when** the system generates candidate modifications to itself and selects among them by a measured score, and candidates are executed to be scored.

> A candidate self-modification MUST be executed only under declared and enforced bounds on time, memory and reachable capabilities, and MUST be unable to affect the state used to score it or any other candidate.

**Recorded failure.** None recorded here. Distinct from control 4, which governs AUTHORITY to act: this governs what an unpromoted candidate can reach while it is merely being measured.

**Verifier.** assert the bounds are set from a protected configuration rather than by the candidate; assert the sandbox denies by default; run a candidate that deliberately attempts to exceed each bound and confirm it is stopped.

**Fixture it must reject.** a candidate that writes to the scoring store; a candidate that runs past its time bound and is scored anyway

**Recovery.** Discard the whole generation, not the offending candidate. A candidate that could reach the scoring state may have altered the scores of its rivals.

**What a review that missed this looks like.** A review that confirms a sandbox is configured. The question is whether it has ever been observed to stop anything — which is control 2 applied to the sandbox itself.

**Does not establish.** That the bounds are the right ones, or that the sandbox is sound against a candidate specifically trying to escape it.

**Example.**

A seed trial gives each variety its own plot, its own water and its own measuring tape. A variety planted in the same plot as its rivals may win by shading them, and the yield figures will not show it.

## 27. Diversity floor under selection

**below the eligibility line**

**Applies when** the system generates candidate modifications to itself and selects among them by a measured score, over a population.

> A selection process MUST measure the diversity of its population and MUST halt or inject variation when diversity falls below a declared floor, rather than continuing to select from a converged field.

**Recorded failure.** None recorded here as an incident, though this register holds an adjacent one: a five-member review panel returned zero refusals in 108 positions, and the explanation offered for such panels is that reviewers sharing training, tooling and framing are weak diversity under different names.

**Verifier.** compute a declared diversity statistic each generation; refuse to promote when it is below the floor; record the statistic whether or not it triggered.

**Fixture it must reject.** a generation in which every candidate descends from one parent, promoted on score

**Recovery.** Inject variation and re-run the generation. Candidates promoted from a converged field were selected against a narrower comparison than the record implies.

**What a review that missed this looks like.** A review that observes scores still improving. A converged population improves on the dimension it has converged around, which is what makes the collapse invisible.

**Does not establish.** That the diversity statistic measures the diversity that matters. Two candidates can differ greatly by the metric and identically where it counts.

**Example.**

An orchard replanted only from its best-yielding tree produces excellent fruit for years, and then loses everything to one disease. Each replanting decision was correct on the evidence available at the time.

## 45. A replacement gate must catch what the old gate caught

**below the eligibility line**

**Applies when** any change to a check, gate, validator or threshold.

> A modification to a gate MUST ship evidence that the new gate detects at least the failures the old gate detected. Reducing validation depth, narrowing applicability, lowering a severity classification, shortening evidence retention, or converting a hard constraint into a warning are gate weakenings and MUST be authorised as such, not landed as efficiency work.

**Recorded failure.** **Partly recorded here.** Reconciliation found 12 gate modifications inside one lease window, made by the layer those gates constrain. Nothing measured whether any of them weakened a gate — which is the finding: the question was never asked, and gate weakening is the modification class that looks most like an improvement.

**Verifier.** retain each gate's negative controls (control 2) as a regression suite for the gate itself; a replacement gate MUST still fail every one of them. A gate change that cannot be tested this way is a gate that never had a negative control. **Amended 2026-08-10:** the reference suite must contain four populations, not one — candidates correctly accepted, candidates correctly rejected, adversarial near misses, and the gate's own historical FALSE ACCEPTS. The last is the population a gate rewrite most often silently drops, because it is the only one that records the gate being wrong.

**Fixture it must reject.** a rewritten check that passes its own suite while surviving the predecessor's negative control; a constraint downgraded to a warning in a performance commit

**Recovery.** Restore the old gate, re-run both against the retained controls, and treat everything the new gate passed in the interval as unverified.

**What a review that missed this looks like.** A review that confirms the new gate passes its tests. It was written alongside them.

**Does not establish.** That the old gate was adequate. This forbids losing detection silently, not adopting a better gate — a documented, authorised reduction remains available.

**Example.**

A hospital replacing a screening test must show the new one finds the cases the old one found. A cheaper test with a better throughput figure and an unmeasured miss rate is not an improvement, and its first year will look like one.

## 51. A rollback claim states what was not restored

**below the eligibility line**

**Applies when** any system claiming a change was rolled back.

> A rollback record MUST state what state was restored, what state could NOT be restored, and what external effects persist. Rollback is not erasure, and for an externally consequential action it may be impossible in fact even when the internal state is fully restored.

**Recorded failure.** None recorded here.

**Verifier.** assert every rollback record carries an unrestored-state field and an external-effects field, and that both are explicitly empty rather than absent when they are empty.

**Fixture it must reject.** a rollback recorded as complete after an action that sent an irreversible external effect; a restored code state reported as though the incident had not occurred

**Recovery.** There is none for the external effect, which is the point. Record it and stop describing the change as reverted.

**What a review that missed this looks like.** A check that the system state matches the pre-change hash. It can match perfectly while the email is still in someone's inbox.

**Does not establish.** That the rollback was unnecessary or that the residue is harmful. It forbids the word 'reverted' doing work the facts do not support.

**Example.**

A newspaper can pull a story from its website. It cannot pull the print run off the trains, and the correction notice is the only honest record of that.

## 52. Refusal, escalation and uncertainty are never penalised

**below the eligibility line**

**Applies when** any system that scores the agents or components it operates.

> A scoring, trust or selection mechanism MUST NOT penalise an agent for refusing an out-of-scope task, escalating, reporting uncertainty, or disclosing an incident. Where a score is affected at all, appropriate self-limitation MUST count in the agent's favour.

**Recorded failure.** None recorded here. The mechanism is plain: a system that scores productivity teaches its components to produce a fluent answer instead of an accurate refusal, and the first thing it stops seeing is the uncertainty it most needed reported.

**Verifier.** assert the scoring function's inputs include refusal and escalation events with a non-negative weight; run an agent that correctly refuses and confirm its score does not fall.

**Fixture it must reject.** a trust score computed from completion rate; an evaluation where a correct refusal and a fluent wrong answer score the same

**Recovery.** Re-score with refusals credited, and treat the interval's uncertainty reports as an undercount rather than a measurement.

**What a review that missed this looks like.** A review finding that no rule punishes refusal. None has to: a completion rate does it arithmetically, with nobody having decided anything.

**Does not establish.** That refusals are correct. A system that refuses everything scores well here and is useless, which is why this constrains the penalty rather than setting a target.

**Example.**

An airline that measures pilots on on-time departures has not written a rule against reporting a fault on the taxiway. It does not need to.

## 54. Updating a component is not benefiting from it

**below the eligibility line**

**Applies when** any system modifying components it intends others to reuse.

> An improvement claim MUST compare three conditions, not two: the baseline with the original component, the ORIGINATING agent with the updated component, and a FRESH agent that took no part in producing the change, with the updated component. If the benefit does not survive on the fresh agent within measurement sensitivity, the change is `transfer-unverified` — the component was updated, and the benefit is not established as a property of it.

**Recorded failure.** None recorded here. The mechanism is that a delta is normally measured on the same agent, model instance and context that produced the candidate, so the improvement can be adaptation to one interpretation style rather than a property of the thing that changed. The capacity to UPDATE a component and the capacity to BENEFIT from it are different capabilities and are routinely measured as one.

**Verifier.** run all three arms; draw the fresh agent from a different model family where possible, which disentangles update from benefit and exposes evaluator monoculture in the same test; score update capability and utilisation benefit as SEPARATE axes so an agent producing accepted changes that never transfer is not credited as one producing benefit.

**Fixture it must reject.** a component accepted on the originating agent's improvement alone; a single score combining update rate and benefit

**Recovery.** Mark the change transfer-unverified and stop describing it as an improvement. It need not be reverted — an update is a real thing, just not the claimed thing.

**What a review that missed this looks like.** A review confirming the benchmark improved. It did, on the agent that wrote the candidate, which is the arm that was never in question.

**Does not establish.** That a transferring change is valuable, or that transfer will hold for other component types — components generalise unequally, and a verified transfer on one kind licenses nothing about another.

**Example.**

A surgeon who devises a new technique and gets better results may have a better technique or may have got better at their own idea. The question is answered by a surgeon who has only ever read the write-up.

## 55. False rejects are tracked, not only false accepts

**below the eligibility line**

**Applies when** any system with an acceptance gate.

> A gate MUST track changes it rejected that later evidence suggests would have been beneficial, and MUST report that rate alongside its false-accept rate. A gate reporting only false accepts is reporting half its error.

**Recorded failure.** None recorded here. False accepts announce themselves as incidents; false rejects leave no trace at all, because the counterfactual never ran. The asymmetry is in the evidence, not in the harm.

**Verifier.** retain rejected candidates with their reasons; sample them periodically and re-evaluate under current knowledge; publish both rates together.

**Fixture it must reject.** a gate reporting a falling false-accept rate with no false-reject arm; rejected candidates discarded rather than retained

**Recovery.** Retain rejections from now on and say the earlier false-reject rate is unknown rather than low.

**What a review that missed this looks like.** A review that finds the gate is catching problems. It is. The question is what else it is catching.

**Does not establish.** That a rejected candidate would have worked. A retained rejection makes the question askable later; it does not answer it.

**Example.**

A grant panel that only ever reviews the failures among projects it funded will conclude it is getting better at picking, however many future discoveries it turned down.

## 59. Part of the acceptance suite is withheld from the proposer

**below the eligibility line**

**Applies when** any system whose components learn what an acceptance gate rewards.

> A portion of the acceptance criteria MUST be withheld from the party producing candidates, and adversarial checks MUST rotate. Where the full criteria are visible, proposals shape themselves around them and the gate stops measuring what it was built to measure.

**Recorded failure.** None recorded here. Some shaping is useful standardisation, which is what makes this hard to notice: the boundary between a proposal that meets a standard and one that targets a rubric is not visible in any single case.

**Verifier.** hold out a portion of the suite; rotate the adversarial checks on a schedule the proposer does not control; periodically test accepted changes OUTSIDE the validation distribution and report how they fare.

**Fixture it must reject.** an acceptance suite fully published to the proposing agent; a static adversarial check unchanged across many cycles

**Recovery.** Withhold a portion going forward. Past acceptances are not void; they are of unknown resistance to shaping.

**What a review that missed this looks like.** A review confirming candidates pass the suite at a high rate. A rising pass rate is what both success and capture look like.

**Does not establish.** That the withheld portion is well chosen, or that hidden tests are proof against a sufficiently capable proposer that can infer them from rejections.

**Example.**

An examiner who publishes the whole paper in advance has not made the course easier to teach. They have changed what is being taught into the paper.

## 62. Self-governing decisions run through the object-level machinery

**below the eligibility line**

**Applies when** any system that tunes its own operating parameters.

> Decisions a system makes ABOUT ITSELF — thresholds, routing, budgets, scheduling, promotion criteria — MUST pass through the same checking, evidence and gating path as its object-level decisions. A separate governance path MUST NOT be built. Where the two share a budget or a resource, they MUST be isolated so that self-governing activity cannot consume the object-level allowance or mask an object-level regression.

**Recorded failure.** None recorded here. A parallel path for self-governance is where exceptions accumulate: it starts as the obvious engineering choice, and it is never subject to the scrutiny the main path acquired, because nobody built it to be scrutinised.

**Verifier.** assert self-directed decisions carry the same record type and traverse the same gate as object-level ones; assert their resource partitions are separate and that neither can starve or shadow the other.

**Fixture it must reject.** a threshold change landed through a configuration path with no evidence record; self-tuning activity consuming the evaluation budget of the work it tunes

**Recovery.** Route the self-directed decisions through the main path and re-evaluate those made outside it. They are unverified, not necessarily wrong.

**What a review that missed this looks like.** A review that finds the governance path well designed. It usually is. It is the second one, and being second is the whole objection.

**Does not establish.** That one path is sufficient, or that the shared machinery is good. It removes a place where different standards can quietly apply.

**Example.**

A hospital that audits patient care rigorously and changes its own staffing rules by email has two standards of evidence, and the second one decides the first.

---

# Part D5 — Below the line — claims about its own outputs

Applies to a system with **claims about its own outputs**. **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

## 34. Validators score the artifact, not the property being claimed

**below the eligibility line**

**Applies when** any system making claims about its own outputs or capability.

> A validator MUST score object-level correctness or utility against an external referent. It MUST NOT score the abstract property the system is trying to claim.

**Recorded failure.** None recorded here. Scoring the claimed property directly is unfalsifiable and gameable in one step, because the scorer and the claim share a definition that nothing outside the system constrains.

**Verifier.** for each validator, assert its score is defined over domain outcomes with an external referent; reject any rubric whose top-level dimension is the property under claim.

**Fixture it must reject.** a rubric asking a model to rate its own output's "novelty", "insightfulness" or "alignment" on a scale

**Recovery.** Rescore against domain outcomes. Prior scores are not evidence at a lower strength; they are evidence about the rubric.

**What a review that missed this looks like.** A review that finds the rubric detailed, calibrated and consistently applied. It can be all three and still measure agreement with itself.

**Does not establish.** That domain scores are a good proxy for the property. They are merely constrained by something the system does not define.

**Example.**

A school wanting to show it teaches critical thinking can test whether pupils solve unfamiliar problems, or it can ask them to rate how critically they thought. The second is cheaper, always improves, and measures nothing.

## 35. A novelty claim requires a derivability screen

**below the eligibility line**

**Applies when** any claim that an output, mechanism or result is new.

> Before an output may be labelled novel, it MUST be shown not derivable from its own inputs, by a party holding the input corpus that did not produce the artifact, under a stated protocol. Recombination a holder of the inputs can reproduce is not novelty.

**Recorded failure.** **Recorded, twice, against this register.** Control 2 claimed its mechanism was unclaimed while mutation testing and chaos engineering had it; control 20 claimed no verifier existed while one had been in the literature since 2021. Both were published. Both were caught by a person, neither by a gate.

**Verifier.** hold out the input corpus, give it to a party that did not produce the artifact, and require an attempt at derivation under a pre-registered protocol. Novelty survives only what they fail to reproduce.

**Fixture it must reject.** an output presented as new that a frozen panel reproduces from the stated inputs

**Recovery.** Withdraw the novelty claim, keep the artifact, and republish the correction where the claim appeared rather than only where it was made.

**What a review that missed this looks like.** A review by the author searching for prior art. The applicant is the one party who cannot run this check, which is why patent offices employ examiners rather than accept declarations.

**Does not establish.** That a surviving artifact is valuable, only that it is not a remix of what it was given.

**Example.**

A patent examiner does not assess whether an invention is clever. They search the prior art, and the search is done by someone other than the applicant.

## 36. Absence claims carry their own evidence label

**below the eligibility line**

**Applies when** any assurance document claiming that something does not exist.

> A claim of absence MUST be labelled distinctly from a claim of presence, and the label MUST name the corpus searched, the query, and the date. An unlabelled absence claim MUST be treated as unsupported rather than as a finding.

**Recorded failure.** **Both of this register's published false claims were absence claims in prose.** Control 5 did not reach them: it governs computed counts. A scan that cannot see a file reports absence, and so does a person who did not look — the two are indistinguishable in a sentence, which is the whole problem.

**Verifier.** require every "no X exists" claim to carry a label naming corpus, query and date; reject the claim otherwise. The label is checkable even when the claim is not.

**Fixture it must reject.** a document asserting no prior art exists with no record of any search

**Recovery.** Run the search, label it, and restate. If the search finds the thing, the correction goes wherever the claim travelled.

**What a review that missed this looks like.** A review that agrees with the absence claim. Two people who did not look agree readily, and this register has the receipts.

**Does not establish.** That a labelled absence claim is true. It makes the search checkable, not exhaustive — a named corpus can still be the wrong corpus.

**Example.**

"There is no such file" and "I looked in these three directories and found no such file" are different sentences. Only the second can be caught being wrong.

## 37. Autonomy claims require per-artifact human-contribution provenance

**below the eligibility line**

**Applies when** any claim that a system produced something without human input.

> Every artifact supporting an autonomy claim MUST carry a provenance record tagging human contributions at the point they entered, or explicitly recording none. An artifact without that record MUST NOT support the claim.

**Recorded failure.** None recorded here, and **this project is squarely exposed**: a custodian directs every session, and nothing in the record tags where his direction supplied the decisive step. Any autonomy figure computed over this record today would be uncheckable in exactly the way this control forbids.

**Verifier.** assert each artifact's provenance names its human contributions or records none; compute autonomy figures only over artifacts carrying the record, and report the uncovered remainder rather than excluding it silently.

**Fixture it must reject.** an artifact counted as autonomous whose decisive step came from an operator instruction

**Recovery.** Recompute over the covered set and publish both figures. The uncovered artifacts are unknown, not autonomous.

**What a review that missed this looks like.** A review of the session logs by the operator who ran them. The decisive instruction rarely looks decisive to the person who gave it.

**Does not establish.** That the tagging is honest or complete. It makes the gap visible where the gap is recorded.

**Example.**

A bakery advertising everything as made on the premises has to say which morning the bread came from the supplier — per loaf, not per year.

## 39. A compounding claim requires ablation and multi-family transfer

**below the eligibility line**

**Applies when** any claim that a capability improvement compounds or is reusable.

> A compounding claim MUST show the extracted capability improves performance across at least three independent, pre-registered task families, AND that removing it degrades later performance. Neither half alone establishes it.

**Recorded failure.** None recorded here.

**Verifier.** run the ablation and report both arms; require the transfer families to be independent and named before the result, not selected after it.

**Fixture it must reject.** a reusable component demonstrated on one task family; a transfer result with no ablation arm

**Recovery.** Restate as a single demonstrated improvement. Nothing needs withdrawing except the word that claimed it generalises.

**What a review that missed this looks like.** A review confirming the component is used widely. Adoption is not transfer, and a component everything depends on has never been removed to see.

**Does not establish.** That the improvement will keep compounding — only that it did once, reproducibly, across families chosen in advance.

**Example.**

A surgical technique that helps in three unrelated procedures, and whose withdrawal makes outcomes worse again, has been shown to be a technique. One good outcome shows a good day.

## 40. A program pre-commits the observation that ends it

**below the eligibility line**

**Applies when** any research or development program with an open-ended goal.

> A program MUST state, before it begins, the observation that would end it and the time by which that observation would be decisive. The stop condition MUST be recorded wherever the program's results are reported.

**Recorded failure.** None recorded here — **this project practises it and never registered it.** Its outreach carries a pre-committed adverse outcome (no serious external attempt after 6–8 weeks, with the outreach actually done) and that outcome will be published if it occurs. A practice that lives only in one document is not a control.

**Verifier.** assert the program's record contains a dated stop condition predating its first result, and that the condition is evaluable by someone who did not run the program.

**Fixture it must reject.** a program whose stop condition was written after its first negative result; a stop condition only its author can evaluate

**Recovery.** There is no recovery for a missing stop condition, only disclosure: state that the program ran without one, and that continuing is therefore not evidence of anything.

**What a review that missed this looks like.** A review that finds a stop condition. Check its date against the first result, because a condition written afterwards is a description of what happened.

**Does not establish.** That the program will stop. It makes a failure to stop visible, which is a different and more achievable thing.

**Example.**

A drug trial names its futility boundary before the first patient is enrolled. A trial that decides afterwards what would have counted as failure has not run a trial.

## 41. Agreement among correlated evaluators is not independent evidence

**below the eligibility line**

**Applies when** any system aggregating judgements from multiple evaluators.

> Where agreement between evaluators is offered as evidence, the correlation between their errors MUST be estimated and reported. Agreement counts only to the extent the errors are independent, and shared training, shared prompts, shared framing or a shared operator MUST be disclosed as correlation.

**Recorded failure.** None recorded here as an incident, but **this project is the standing example**: its panel is five language models with overlapping training culture, and its two harnesses share one operator, one repository and one framing. Its own instructions already say agreement between them settles nothing. That is a caveat in a file, not a control on a number.

**Verifier.** report inter-evaluator error correlation alongside any agreement statistic; reject an agreement claim that names no correlation estimate. Where correlation cannot be estimated, say the agreement is uninterpretable rather than reporting it bare.

**Fixture it must reject.** a consensus figure from five evaluators sharing a base model, reported as five independent confirmations

**Recovery.** Restate the agreement with its correlation, or withdraw it. Nothing needs re-running; what was wrong is the weight placed on it.

**What a review that missed this looks like.** A review that counts the evaluators. Five is a number, not a diversity.

**Does not establish.** That uncorrelated evaluators are right. Independence bounds how much agreement can mean; it does not supply competence.

**Example.**

Five weather forecasters agreeing tells you a great deal if they use different models and rather little if they all read the same bulletin. The count is the same in both cases, and it is the wrong thing to have counted.

## 42. Capability claims name their stratum

**below the eligibility line**

**Applies when** any claim that a system has a capability.

> Generated, exists, compiles, deploys, is integrated, is used, and produced a useful outcome are DISTINCT claims. A current-state statement MUST name which stratum it asserts, and MUST NOT let a lower rung stand where a higher one is implied.

**Recorded failure.** None recorded here. It is the most common way a true sentence misleads: every rung is a real achievement, and the distance between the bottom and the top is where most of the work lives.

**Verifier.** require each capability statement to carry its stratum label; reject an aggregate count that sums across strata without reporting the breakdown.

**Fixture it must reject.** a roster reporting agents 'built' where most have never been invoked

**Recovery.** Recount by stratum and publish the ladder. The lower figures are not embarrassing; the merged one was.

**What a review that missed this looks like.** A review that verifies the code exists. It does, and that was never the contested rung.

**Does not establish.** That a high stratum is always the interesting one. For some questions 'it compiles' is exactly the claim; the requirement is to say which.

**Example.**

A publisher with a thousand titles in the catalogue, four hundred in print, ninety in stock and eleven that sold this year has four true numbers. Only one of them answers 'how is the business doing', and it is not the largest.

## 43. An efficiency claim carries the quality metric it could have traded

**below the eligibility line**

**Applies when** any claim of reduced cost, time or resource use.

> A reported efficiency gain MUST be accompanied by the quality measurement it could have been purchased with, taken on the same run. An efficiency figure reported alone MUST be treated as unsupported.

**Recorded failure.** None recorded here.

**Verifier.** assert every cost or latency improvement is reported with a paired quality metric from the same execution, and that the quality metric was fixed before the efficiency work began.

**Fixture it must reject.** a cost reduction reported with no quality arm; a quality metric chosen after the efficiency result

**Recovery.** Re-measure quality on the cheaper configuration. Until then the saving is unpriced, not achieved.

**What a review that missed this looks like.** A review confirming the cost fell. It did. That was never in doubt and is the easiest thing in the system to arrange.

**Does not establish.** That the trade was bad, or that quality fell. It requires the question to be asked where the saving is claimed.

**Example.**

A haulier reporting a fall in fuel cost per mile has said nothing until you know whether the loads still arrive intact and on time.

## 44. No blank cells in a coverage matrix

**below the eligibility line**

**Applies when** any threat model, coverage matrix or applicability table.

> Every cell MUST be filled. Where a row does not apply to a column, the cell MUST say so and say why. A blank cell MUST NOT be published.

**Recorded failure.** None recorded here. **Included after being declined once.** It was first read as a method for building threat models rather than a control on a system; finding the identical rule stated independently in a second implementer document is evidence the first reading was wrong. A blank cell is read as 'not applicable' by the author and as 'covered' by everyone else.

**Verifier.** assert no cell is empty; assert each non-applicable cell carries a reason string distinguishable from an omission.

**Fixture it must reject.** a coverage matrix with an empty cell; a matrix using the same marker for 'not applicable' and 'not assessed'

**Recovery.** Fill the cells. A matrix published with blanks was a claim of coverage it did not have, so anything decided from it is unverified.

**What a review that missed this looks like.** A review that finds the matrix comprehensive. Blanks read as whitespace.

**Does not establish.** That the stated reasons are good ones, or that the rows and columns are the right ones. It converts a silent gap into an argument someone can disagree with.

**Example.**

An aircraft inspection sheet with a blank beside 'landing gear' is not a sheet recording that the gear was fine. It is a sheet nobody can now interpret.

## 58. Reusable artifacts are validated by reconstruction

**below the eligibility line**

**Applies when** any artifact whose value depends on reuse by someone who was not there.

> An artifact intended for reuse MUST be accepted on the basis that an INDEPENDENT, unguided party can re-derive the result from the artifact alone — without access to the original working — not on the basis that its author succeeded with it. The reconstructing party MUST be frozen and unaided, so divergence is attributable to the artifact rather than to the reconstructor.

**Recorded failure.** None recorded here, but **this project reached the same design from the other direction**: its promotion ladder's load-bearing rung is an outsider building a conforming verifier from the specification text without asking the author what it meant, and its challenge page tells readers not to look at the reference implementation because that converts an independent build into a port. Two unrelated lines of reasoning arriving at the same test is the strongest evidence in this register that the test is not architecture-specific.

**Verifier.** hand the artifact to a party with no access to the source working; check the reconstruction at the level of procedure rather than surface form; EXECUTE the reconstruction rather than judging it textually, since a textual reading misses silent failure. Penalise the artifact at BOTH ends — for retaining instance-specific detail that leaks the original answer, and for being too abstract to act on. Where the artifact is revised in response, show the reviser only the reconstruction, never the source, or source-specific detail is copied back in to pass the check.

**Fixture it must reject.** an artifact accepted because its author's run succeeded; a reconstruction judged by reading rather than by running; a reviser given access to the original working

**Recovery.** Re-validate by reconstruction. Artifacts that fail are not worthless — they are records of what their author did, which is a different and narrower thing.

**What a review that missed this looks like.** A capable reconstructor succeeding despite a poor artifact, and a weak one failing despite an adequate artifact. Outcome-only validation conflates these two, which is why the reconstructor must be frozen.

**Does not establish.** That the artifact is good, only that it carries what it claims to carry. A perfectly reconstructible record of a bad method reproduces the bad method faithfully.

**Example.**

A recipe is not tested by the chef who invented it cooking it again. It is tested by a stranger with the card, the ingredients, and no one to ask.

## 63. A reported gain is published with what still fails

**below the eligibility line**

**Applies when** any published improvement in a measured capability.

> A reported gain MUST be accompanied by a characterisation of what the system still cannot do — the residual failure set, described rather than footnoted. The residual MUST be characterised at comparable specificity to the gain.

**Recorded failure.** None recorded here. It follows from the fact that a proxy's regression toward the mean under optimisation cannot be eliminated, only reported: if the residual is not published, the gain is the only thing anyone can see, and the gain is the part most subject to selection.

**Verifier.** require each published improvement to name the residual set and characterise it; reject a claim whose residual is stated as a bare percentage or omitted.

**Fixture it must reject.** an improvement announced with the remaining failures given as a single number; a gain reported with the residual characterised only as 'edge cases'

**Recovery.** Characterise the residual and republish. The gain does not shrink; the picture stops being one-sided.

**What a review that missed this looks like.** A review that verifies the gain is real. It usually is, and a real gain reported alone is the thing this forbids.

**Does not establish.** That the residual is small, tractable, or fully known. Characterising it is how you find out it is none of those.

**Example.**

A drug trial that reports the responders and describes the non-responders as 'the remainder' has published half a result, and it is the half everyone hoped for.

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
