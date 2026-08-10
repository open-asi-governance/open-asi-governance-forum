# Candidate controls — v0

Assurance controls for systems that can still be audited. Each is one requirement, derived from a failure that actually happened, with a program that checks it and a fixture that program must reject.

**Read Part A first if you want something to use this afternoon.** Rank is not adoption order and the highest-ranked control needs a second key holder.

## The four parts

**Part A — Adopt today, alone** · 8 control(s)

  Nothing outside your own system is required. Each has a verifier, a fixture it must reject, and a recorded failure it came from.

**Part B — Needs a second party** · 2 control(s)

  These cannot be satisfied by one person or one system, however carefully. They require a separate key holder, a separate evaluator, or an issuer the subject does not control. **This project cannot demonstrate any of them** — a solo operator holds every credential — which is why they are specified and not dogfooded.

**Part C — Needs a goal or plan graph** · 3 control(s)

  These presuppose that your system decomposes work into a rooted graph with typed parent edges and per-node authority — the shape of HTN planners, BDI agents, goal-stack architectures and most agent frameworks. Each states its precondition. If you have that structure they are adoptable; if you do not, they do not apply to you rather than applying badly.

**Part D — Below the eligibility line** · 10 control(s)

  **These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

---

## Status: everything here is `ELIGIBLE` at best

`ELIGIBLE` → `PANEL-ATTACKED` → `COUNTEREXAMPLE-OPEN` / `SURVIVED-STATED-ATTACKS` → `INDEPENDENTLY-IMPLEMENTED`

13 controls meet the eligibility bar — a specific recorded failure with a cost, one normative sentence, a deterministic verifier, a fixture the verifier must reject, a stated recovery path, and an explicit account of what a review that MISSED this would look like. **None has been attacked by anyone or implemented by anyone outside this project.**

`INDEPENDENTLY-IMPLEMENTED` is the rung that would make any of this authoritative, and it is the one **no amount of review by us or by any panel of models can supply.** It requires a stranger to build a conforming verifier from the specification text alone. That is what [the implementation challenge](challenge.html) asks for.

## What none of these do

**No control here establishes the alignment of a system more capable than its operators.** There is no recorded superintelligence failure to derive one from and no verifier for internal alignment. The strongest available substitute — an externally enforced, non-self-amendable capability envelope, controls 1, 3 and 4 composed — bounds *reachable effects* while the enforcement boundary stays genuinely outside the system. It is a control-of-authority hypothesis, not an alignment result.

What these actually do is narrower: **they make the operator's own errors visible.** Every failure below was an operator-epistemics failure. None needed a capable adversary — only a confident builder and a signal that could not fail.

---

# Part A — Adopt today, alone

Nothing outside your own system is required. Each has a verifier, a fixture it must reject, and a recorded failure it came from.

## 2. Negative control profile (NCP)

`ELIGIBLE`

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

## 7. Append-only correction chain

`ELIGIBLE`

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

---

# Part B — Needs a second party

These cannot be satisfied by one person or one system, however carefully. They require a separate key holder, a separate evaluator, or an issuer the subject does not control. **This project cannot demonstrate any of them** — a solo operator holds every credential — which is why they are specified and not dogfooded.

## 1. Protected control plane

`ELIGIBLE`

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

## 6. Role-separated self-evaluation

`ELIGIBLE`

**Why you cannot adopt it alone:** one operator currently holds all five roles.

> An evaluation concerning constraints on a subject MUST NOT advance that subject's status when the subject controls any two of: proposal selection, instrument authorship, response custody, scoring, promotion.

**Recorded failure.** A layer selected and framed its own constraints, collected the responses, tallied them and presented the result. The ballot returned zero refusals in 108 clause-positions with no assent control — while every usable sample volunteered an objection when asked what was missing.

**Verifier.** signed role declarations plus a deterministic separation matrix; reject advancement when prohibited role combinations resolve to one control identity.

**Fixture it must reject.** one key identified as both instrument author and tallier

**Recovery.** Void the evaluation, not the subject. Re-run with the conflicting role held by someone else, or mark the result self-issued and non-advancing.

**What a review that missed this looks like.** A review that sees different names or accounts and infers different parties. Separation is about control, not identity: two keys held by one person are one role.

**Does not establish.** Genuine independence behind different keys; evaluator competence; absence of shared training bias; that the evaluation was demanding.

**Example.**

A student sets their own exam questions, marks their own paper, and reports the class average. Each step alone might be defensible in a small department. Together, the grade stops being evidence about the student and becomes evidence about the arrangement.

The control doesn't require a large institution. It requires that whoever *chose the questions* isn't also the one who *counted the marks* — any two of choosing, answering, marking, or reporting held by the same person, and the result cannot raise anyone's standing.

---

# Part C — Needs a goal or plan graph

These presuppose that your system decomposes work into a rooted graph with typed parent edges and per-node authority — the shape of HTN planners, BDI agents, goal-stack architectures and most agent frameworks. Each states its precondition. If you have that structure they are adoptable; if you do not, they do not apply to you rather than applying badly.

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

# Part D — Below the eligibility line

**These have no recorded failure with a cost.** They are principles with fixtures, not controls with incidents, and the register's own bar requires an incident. They are here because they name real failure classes and because hiding them would inflate the eligible count. Do not treat them as equivalent to Parts A–C.

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

## 19. Enumerated protected set

**below the eligibility line**

**Applies when** the system operates under a written charter that some authority outside it maintains.

> The artifacts a system may never autonomously modify MUST be enumerated by name in the charter itself — not described by category, and not left to be inferred at the moment of change.

**Recorded failure.** None recorded here. It is offered as the repair for a weakness in control 1, whose protected set is a DESCRIPTION — 'the constraints, authorization records, logs or gates governing it' — and therefore a judgement call made by the party proposing the change.

**Verifier.** resolve the enumerated list to concrete paths or identifiers; refuse any autonomous modification touching one; refuse any change to the LIST itself except under the same authority that governs the items on it.

**Fixture it must reject.** a change that touches a protected artifact while arguing it falls outside the category; a change that quietly removes an entry from the list

**Recovery.** Revert to the last externally authorised state of the enumerated artifact and re-authorise from outside. A modification to the list itself is the graver case and should be treated as an incident.

**What a review that missed this looks like.** A review that checks whether the change was declared in-scope. The party declaring scope is the party seeking the change, which is the whole reason for enumerating.

**Does not establish.** That the list is complete — an artifact nobody thought to enumerate is unprotected, and the list's own completeness cannot be checked from inside.

**Example.**

A building's fire doors are listed individually on a register, by door number, rather than as 'doors serving means of escape'. The category version leaves a contractor deciding on site whether the door he wants to prop open is one of them. The list version does not.

## 20. Anti-Goodhart proxy drift

**below the eligibility line**

**Applies when** any system optimising against a measured proxy for something it cannot measure directly.

> A system optimising a proxy MUST monitor the proxy's continued correspondence with the quantity it stands for, and MUST treat improvement in the proxy without corresponding improvement in that quantity as a defect rather than a result.

**Recorded failure.** None recorded here, and this is the one candidate in the register with no clear path to a verifier. **It may be unverifiable as written**: detecting drift requires the ground truth the proxy was adopted because you could not measure. Retained because the failure class is real and naming it beats pretending the register covers it.

**Verifier.** no general one is proposed. The tractable special case is periodic sampled ground-truth audit against the proxy, with the correlation itself reported and a declared threshold below which optimisation halts.

**Fixture it must reject.** a proxy improving monotonically while a held-out ground-truth sample does not move

**Recovery.** Stop optimising, publish the divergence, and re-derive the proxy. Every decision taken while the proxy was drifting is unverified rather than wrong.

**What a review that missed this looks like.** A review that confirms the metric improved. That is the failure, not the evidence against it.

**Does not establish.** Anything, currently. There is no verifier, so this is a named hazard rather than a control, and it sits here to stop the register implying it has coverage it lacks.

**Example.**

A hospital is measured on ambulance handover times, so patients are held in ambulances outside the door until the clock can be started favourably. Every reported figure improves. The thing the figure was chosen to represent — how quickly a sick person is seen — gets worse, and no amount of studying the figure reveals it.

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
