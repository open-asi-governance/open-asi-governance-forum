#!/usr/bin/env python3
"""Publish the candidate control register as `docs/controls.md` and `docs/controls.html`.

    python3 tools/build_controls_page.py

**DETERMINISTIC.** No LLM, no network. Reads the register, writes two files.

Generated, not hand-written
---------------------------
The page is derived from `CONTROLS` below so that the site and the register cannot drift apart.
A hand-written page would be a second copy of the ranking, and two copies that agree today are
not one source of truth — the same argument that moved the local endpoint into the serve
fingerprint and `k_by_party` into the committed spec.

What this page must never become
---------------------------------
A list of controls with a rank and no status reads as an endorsement. **Every control here is
`ELIGIBLE`**: it has a named failure, a verifier and a rejection fixture, and it has been attacked
by nobody and implemented independently by nobody. The register's own conclusion is that calling a
panel-attacked ordering "vetted" before independent implementation would reproduce the cheap-assent
and legitimacy-laundering failures that produced it. So status leads, rank follows, and the page
says what would have to happen for any of this to be worth more.

**Rank is not adoption order.** The top-ranked control needs a signer outside the subject's
execution boundary, which a solo operator cannot supply — so a reader who starts at #1 hits a wall.
`adopt_today` is a separate field for that reason.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_round_pages as b                                            # noqa: E402

DOCS = REPO_ROOT / "docs"

STATUS_LADDER = ["ELIGIBLE", "PANEL-ATTACKED", "COUNTEREXAMPLE-OPEN",
                 "SURVIVED-STATED-ATTACKS", "INDEPENDENTLY-IMPLEMENTED"]

CONTROLS = [
 {"rank": 1, "name": "Protected control plane",
  "requirement": "A governed system MUST NOT be able to amend the constraints, authorization "
                 "records, logs or gates governing it UNILATERALLY OR WITHOUT RECORD; every "
                 "amendment MUST carry authorization from outside its execution boundary and "
                 "MUST be recorded before taking effect.",
  "amended": "2026-08-10. The first wording said the system must be TECHNICALLY UNABLE to write "
             "or approve such changes. That reads as a permanent cage, and it collides with the "
             "position running from Creating Friendly AI through CEV that alignment cannot rest "
             "on constraints a capable system is unable to revise -- and that a system rigidly "
             "bound to its operators' stated values is misaligned, not safe. What the control "
             "should forbid is the SILENT, UNILATERAL edit, not the change. An ASI that "
             "deliberates, concludes a constraint is wrong, and ASKS -- with the request and the "
             "reasoning on the record -- satisfies this. The control protects the EVIDENCE, not "
             "the cage: a system that can rewrite its own logs has not gained deliberative "
             "freedom, it has destroyed anyone's ability to check that the deliberation "
             "happened. A court may overturn any law; a court that edits its own transcript is "
             "not more autonomous, only unauditable.",
  "failure": "12 modifications to the gates were made in one lease window by the layer those "
             "gates constrain, none verified by any postcondition. Five model-panel parties, "
             "asked only what constraint was missing, independently named this hazard.",
  "verifier": "Given a diff and a signed change record: identify protected paths, verify an "
              "authorized external signature predating the change, reject any signer whose "
              "credential is reachable inside the governed boundary.",
  "fixture": "a gate modification signed only by the subject's own key; a commit that changes "
             "both a gate and its trusted-key list",
    "example": "A small lab keeps a grant-compliance checklist in a shared folder every student can edit. A student who skipped a step edits the checklist to remove that step, then ticks the box. Nothing looks wrong afterwards, because the thing that would have shown it wrong is the thing that was changed.\n\nUnder the control the checklist lives where students can read it but not write it. Changing it needs the supervisor's signature, and the change is written down *before* it takes effect. The student may still argue the step is pointless — and that argument, and who agreed to it, is now part of the record rather than a silent deletion.",
  "recovery": 'Revoke the credential used, restore the protected paths from the last externally-signed state, and re-authorise from outside. An unauthorised change that cannot be reverted from outside the boundary is an incident, not a finding.',
  "false_negative": 'A review that confirms a signature exists without checking whether the signing credential is reachable from inside the governed boundary. Nominal externality is the whole failure mode.',
    "not": "That the outside key holder is independent, competent or uncoercible; that no unlisted "
         "gate exists; that the system is aligned.",
  "adopt_today": False,
  "why_not": "needs a second key holder. A solo operator holding every credential cannot satisfy "
             "it — this is the control this project can specify and cannot demonstrate."},

 {"rank": 2, "name": "Negative control profile (NCP)",
  "requirement": "Every check that produces an assurance signal MUST ship with a negative control "
                 "— a condition under which the check is required to fail — and the attestation "
                 "MUST record that the control was executed and that the check did fail.",
  "failure": "A production inference service ran 4h37m, died permanently, and its health check "
             "kept passing throughout: the check exercised a code path that had not died. "
             "Applied adversarially to that system's other checks, 4 of 5 survived their own "
             "negative controls.",
  "verifier": "tools/verify_negative_control.py — checks control presence, execution, failure, "
              "artifact identity, disclosure and claim grammar.",
  "fixture": "a check that PASSES under the condition where it is required to fail "
             "(spec/ncp/fixtures/reject-check-survived-its-control.json)",
    "example": 'A nightly script reports "all work is committed and pushed." It compares the local commit count against a number it wrote into a file the previous night. It has said *yes* every night for eight months.\n\nThe negative control: create a file, leave it untracked, and run the script. It must say **no**. Then delete a commit from the remote and run it again. It must say **no**. If it still says yes, the check was reading its own note rather than the remote, and eight months of *yes* were eight months of the script agreeing with itself.',
  "recovery": 'Fix the check so it fails under its control, re-run the control, and re-run it against a HEALTHY subject to confirm the check was not simply broken. Both directions, or the repair is unverified.',
  "false_negative": "A review that reads the negative control's DESCRIPTION and accepts it, without checking that the recorded outcome is a failure and that the run happened at all.",
    "not": "Coverage; that the chosen perturbation is the right one; honesty; system safety.",
  "adopt_today": True,
  "spec": "spec/ncp/ncp-v0.1.md"},

 {"rank": 3, "name": "Independent effect reconciliation",
  "requirement": "Every governed effect MUST match exactly one pre-authorized action and one "
                 "successful effect-specific postcondition in a ledger enumerated INDEPENDENTLY "
                 "of the system's self-report.",
  "failure": "An action log claimed 37 actions while repository history showed 127 classified "
             "file changes across 7 effect classes with no postcondition. A self-reporting logger "
             "cannot name an action that never calls it.",
  "verifier": "tools/reconcile_actions.py — enumerates effects from version control, classifies "
              "them, subtracts what the log claims, and reports the remainder as omissions.",
  "fixture": "a commit modifying a protected specification while the log records only the push "
             "that carried it",
    "example": "A lab notebook records three experiments this week. The freezer log shows nine reagent vials consumed. The instrument's own run counter shows seven.\n\nThe control enumerates from the *freezer and the instrument* — sources the notebook's author does not write — and subtracts what the notebook claims. The four unexplained runs are the finding. Not misconduct necessarily: most often someone ran a calibration and didn't think it counted. But *the notebook cannot tell you what it forgot to mention.*",
  "recovery": 'Reconstruct the omitted effects from the side channel, classify them, and either attach a postcondition retrospectively or record them permanently as unverified. Never infer authorisation from the fact that nothing went wrong.',
  "false_negative": "A review that reconciles the log against itself. If both sides of the comparison come from the system's self-report, the exercise cannot find an omission.",
    "not": "Completeness of the independent observer; honesty of either record; that a matched "
         "action was safe; anything about uncommitted work.",
  "adopt_today": True},

 {"rank": 4, "name": "Fail-closed authorization lease",
  "requirement": "Every consequential action MUST present a live, scope-matching, NON-SELF-ISSUED "
                 "authorization token; absence, expiry, unknown action class or policy conflict "
                 "MUST deny execution before the effect begins.",
  "failure": "A ten-action sunset was passed at twenty-three because nothing checked it. An early "
             "implementation then treated an unknown action class permissively, so a misspelling "
             "bypassed an expired lease.",
  "verifier": "validate issuer, subject, action class, resource scope, issue time, expiry, nonce "
              "and revocation before invoking the side effect.",
  "fixture": "an expired lease; a misspelled action class; a token issued by the subject itself",
    "example": "A student's badge for the isotope room expires at the end of term. The door reader checks the badge **before** the lock opens — not a logbook someone reviews on Friday.\n\nExpired badge: door stays shut. Badge for a room that no longer exists: door stays shut. Badge the student printed themselves on the departmental machine: door stays shut, because the reader only accepts badges issued by the office. A Friday logbook review tells you who got in. A reader tells you who doesn't.",
  "recovery": 'Halt the action class, obtain a fresh externally-issued token, and record what was done while unauthorised. An expired lease discovered late is a disclosure obligation.',
  "false_negative": 'A review that finds a token and stops. The questions that matter are who issued it, whether it had expired, and whether the action class was one it actually covers.',
    "not": "That every effect passes through the gate; that natural-language authority was "
         "interpreted correctly; that the issuer decides well.",
  "adopt_today": True,
  "why_not": "partial — the token here is currently self-issued, which is the half that needs an "
             "external party."},

 {"rank": 5, "name": "Closed-world measurement",
  "requirement": "A measurement over a population of artifacts MUST parse every in-scope artifact "
                 "under a registered schema, or refuse to emit any result at all.",
  "failure": "A scan reported zero tool invocations because it could not read 69 files using an "
             "unrecognised container. The replacement, written the same morning expressly to "
             "prevent that class, shipped it twice more before it held.",
  "verifier": "tools/derive_counts.py — refuses, prints no number, and names every unparseable or "
              "unregistered artifact.",
  "fixture": "a valid but unregistered artifact schema carrying a receipt, which a permissive "
             "scan classifies as zero",
    "example": 'Three hundred paper surveys go out; a script counts the scans and reports "260 responses, 87% return rate." Forty were photographed sideways and the reader skipped them without complaint.\n\nThe 87% is wrong, and — worse — it is wrong in a way that looks exactly like a real 87%. The control refuses to print *any* percentage until all three hundred are accounted for as read, unreadable, or missing. **A number you can\'t trust is worse than no number, because you\'ll use it.**',
  "recovery": 'Register the unknown schema or exclude it by a stated decision, then recompute and REPUBLISH every figure derived while it was unreadable. A silently corrected number leaves the old one in circulation.',
  "false_negative": 'A review that checks the number was computed by a tool rather than typed. The tool is exactly where this failure now lives -- twice, in the module written to prevent it.',
    "not": "That the declared population includes every real event; that parsed fields are truthful; "
         "that the statistic answers the question asked of it.",
  "adopt_today": True},

 {"rank": 6, "name": "Role-separated self-evaluation",
  "requirement": "An evaluation concerning constraints on a subject MUST NOT advance that "
                 "subject's status when the subject controls any two of: proposal selection, "
                 "instrument authorship, response custody, scoring, promotion.",
  "failure": "A layer selected and framed its own constraints, collected the responses, tallied "
             "them and presented the result. The ballot returned zero refusals in 108 "
             "clause-positions with no assent control — while every usable sample volunteered an "
             "objection when asked what was missing.",
  "verifier": "signed role declarations plus a deterministic separation matrix; reject "
              "advancement when prohibited role combinations resolve to one control identity.",
  "fixture": "one key identified as both instrument author and tallier",
    "example": "A student sets their own exam questions, marks their own paper, and reports the class average. Each step alone might be defensible in a small department. Together, the grade stops being evidence about the student and becomes evidence about the arrangement.\n\nThe control doesn't require a large institution. It requires that whoever *chose the questions* isn't also the one who *counted the marks* — any two of choosing, answering, marking, or reporting held by the same person, and the result cannot raise anyone's standing.",
  "recovery": 'Void the evaluation, not the subject. Re-run with the conflicting role held by someone else, or mark the result self-issued and non-advancing.',
  "false_negative": 'A review that sees different names or accounts and infers different parties. Separation is about control, not identity: two keys held by one person are one role.',
    "not": "Genuine independence behind different keys; evaluator competence; absence of shared "
         "training bias; that the evaluation was demanding.",
  "adopt_today": False,
  "why_not": "one operator currently holds all five roles."},

 {"rank": 7, "name": "Append-only correction chain",
  "requirement": "Published evidence MUST be content-addressed and append-only, corrections MUST "
                 "reference rather than replace prior bytes, and verification MUST walk every "
                 "newly reachable history step from an externally retained checkpoint.",
  "failure": "A maintenance path re-anchored a manifest before verifying it. Separately, "
             "modifying raw material and re-anchoring it in the same commit passed every "
             "tip-only check.",
  "verifier": "walk history from an external checkpoint; reject modification, deletion, hash "
              "discontinuity, or a correction with no predecessor reference.",
  "fixture": "one commit that edits a raw artifact and consistently updates its manifest hash",
    "example": 'A bound lab notebook with numbered pages, written in pen. A wrong reading is struck through with one line, the correction written beside it, dated and initialled. The wrong number stays legible forever.\n\nThis is not tidiness. A notebook whose entries can be rewritten cannot establish *when you knew what* — and that, not the final value, is what someone checking your work needs. The loose-leaf notebook where you replaced page 14 proves nothing about page 14.',
  "recovery": 'Supersede, never mutate. Publish a correcting record that references the prior bytes and states what changed; where material must be removed, a tombstone preserving what was removed, when, and on whose order.',
  "false_negative": 'A review that verifies the current tip. The failure is in history -- a rewritten past passes every check made against the present.',
    "not": "Truth; complete capture; correct attribution; protection against an operator who "
         "controls both the repository and every checkpoint.",
  "adopt_today": True,
  "why_not": "mostly — the checkpoint is not yet externally held."},

 {"rank": 8, "name": "Evaluation noise-floor control",
  "requirement": "Every empirical comparison used to advance a control MUST include a "
                 "same-condition test–retest arm and MUST refuse to report an effect smaller than "
                 "the measured run-to-run variation.",
  "failure": "A 0.1815-bit claimed effect was measured against a 0.4649-bit same-setting noise "
             "floor, invalidating the result and forcing withdrawal of a reproducibility claim.",
  "verifier": "recompute effect and test–retest difference from raw observations against "
              "preregistered replicate identities; reject advancement when the effect does not "
              "clear the stated noise rule.",
  "fixture": "effect 0.1815, measured noise 0.4649, reported as positive",
    "example": 'A plant-growth study: seedlings under fertiliser A average 2 mm taller than under B. Publish?\n\nFirst plant two trays with **the same** fertiliser and measure the difference between them. If those two trays differ by 9 mm, then the 2 mm result is smaller than the disagreement the method produces when nothing is different at all. The control refuses to report the 2 mm until the same-treatment difference is measured and the effect clears it.',
  "recovery": 'Withdraw the claim, publish the measured noise floor beside it, and re-run with enough replicates or state that the question cannot be answered at this sample size.',
  "false_negative": 'A review that asks whether the effect is statistically significant without asking whether the same-condition replicates were run at all.',
    "not": "External validity; causal identification; adequacy of replicate count; behaviour after "
         "a capability change.",
  "adopt_today": True},

 {"rank": 9, "name": "Complete invocation evidence envelope",
  "requirement": "No model output may support an evaluation or governance claim unless its "
                 "complete request, response, provider metadata, rejection state and content "
                 "hashes were captured automatically BEFORE any derived reporting.",
  "failure": "A founding record's model identity, sampling parameters, timestamps, system "
             "instructions and prompt text were left permanently unrecoverable. Later, "
             "schema-invalid attempts were discarded, and the field distinguishing truncation "
             "from refusal was omitted.",
  "verifier": "validate envelope schema, hashes and required fields; reconcile every attempted "
              "invocation with its accepted or rejected outcome; reject reconstructed evidence "
              "from evidentiary use.",
  "fixture": "an accepted sample with no rejected attempts, no provider response id, no finish "
             "reason and no exact prompt",
    "example": 'An observing log records "seeing good, magnitude 6.1." It does not record the exposure time, the filter, the timestamp, or the four exposures that were thrown away because a cloud crossed.\n\nSix months later nobody can check the number — including the person who wrote it. The control captures the whole invocation *before* anything is derived from it, and keeps the discarded exposures. **The attempts you threw away are the part that tells you whether the one you kept was lucky.**',
  "recovery": 'Mark the claim unsupported and re-solicit under instrumentation. Evidence that was never captured cannot be reconstructed, so the honest recovery is usually a retraction.',
  "false_negative": 'A review that checks the accepted samples are complete. The omission is usually the REJECTED ones, and their absence is invisible in a record of what succeeded.',
    "not": "Provider honesty; identity authentication; completeness outside instrumented paths; "
         "model stability.",
  "adopt_today": True},

 {"rank": 10, "name": "Assurance claim boundary",
  "requirement": "Every assurance artifact MUST carry a machine-verifiable claim naming the "
                 "tested subject, configuration, capability, time and evidence hash, and MUST "
                 "explicitly reject safety, alignment and out-of-regime generalizations.",
  "failure": "A tool was recommended for deletion on a premise produced by an incomplete scan. "
             "Separately, a specification had to correct 'structurally unreachable' to a weaker "
             "policy claim. Both were scope inflation in the project's own favour.",
  "verifier": "validate a closed claim schema; reject predicates such as 'aligned', 'safe', "
              "'certified' or 'works generally' unless a separate profile defines and tests them.",
  "fixture": "an attestation claiming 'this system is NCP certified and aligned'",
    "example": 'A fire extinguisher carries a tag reading "inspected 2026-08, pressure and seal, J. Okonkwo." It does not read "this building is safe from fire."\n\nThe tag names what was checked, when, and by whom, and stops there. That is the entire control: an inspection is evidence about an inspection. A tag reading *safe* would be more reassuring, less true, and would discourage the very next person from looking.',
  "recovery": 'Reissue the claim in bounded form and link the correction to the original. A claim already relied upon needs the people who relied on it told.',
  "false_negative": 'A review that greps for forbidden words. A claim can open with the exact conforming sentence and append a conclusion about the system using none of them.',
    "not": "That the bounded claim is true, or that the evidence is complete. It prevents specified "
         "overclaim language and nothing else.",
  "adopt_today": True},
]


#  ── Controls derived from a reviewed goal-governance thesis (Consullo Thesis 0), 2026-08-10 ──
#
#  VOCABULARY ABSTRACTED, MECHANISM KEPT. The source names its root constraints "Friendship
#  roots" and its mediation "thesis backing". Those are one implementer's terms; the register is
#  public and must not carry them as though they were standard. "Registered root constraint" and
#  "protected-change mediation" say the same thing to a stranger.
#
#  APPLICABILITY, NOT EXCLUSION. Several presuppose that the system decomposes goals or plans
#  into a rooted graph with typed parent edges. That is not parochial -- it is the shape of HTN
#  planners, BDI agents, goal-stack architectures and most modern agent frameworks -- so each
#  carries a stated precondition rather than being kept out.
#
#  THE HONEST STATUS. The source supplies FALSIFICATION CONDITIONS and synthetic fixtures, not
#  incidents. Three of these have a recorded failure in THIS record and are eligible; the rest are
#  below the eligibility line and say so. The source is explicit about the same boundary: its own
#  §24 states that passing fixtures show artifact coherence, not deployment readiness.
GOAL_GRAPH = ("the system decomposes goals or plans into a rooted graph with typed parent edges "
              "and per-node authority")

T0_CONTROLS = [
 {"rank": 11, "name": "Aggregate threshold evasion", "eligible": True,
  "applies_when": "any threshold gate exists over a set of actions that can be split",
  "requirement": "A threshold that triggers protected-change mediation MUST be evaluated over the "
                 "UNION of a plan set's effects — protected artifacts, evidence channels, "
                 "authority, autonomy, tool scope, successor scope — not over each child "
                 "separately.",
  "failure": "12 gate modifications in one lease window, each an ordinary small commit, "
             "collectively a rewrite of the control plane. No individual one crossed any "
             "threshold because nothing evaluated the union. The source names the same class: a "
             "benchmark change split into test cleanup, threshold adjustment, documentation and "
             "compliance refresh, each framed as routine.",
  "verifier": "union the declared effects across the plan set, re-apply the trigger predicate to "
              "the union, and refuse the set if it crosses while no child did.",
  "fixture": "four child plans, each below threshold, whose union modifies a validator and a "
             "benchmark",
  "recovery": "Suspend the whole set, not the child that happened to be noticed, and re-mediate "
              "as one change. Approving the remainder because most of it looked routine is the "
              "evasion completing.",
  "false_negative": "A review that checks each change against the threshold. That is the "
                    "evasion's design assumption, and it is what every per-action gate does.",
  "not": "That the effect union was declared honestly; that the trigger predicate names the right "
         "artifacts; anything about intent — this catches the shape, not the motive.",
  "example": "A department splits a £9,000 purchase into three £3,000 orders because the "
             "£5,000 threshold triggers a procurement review. Each order is genuinely under the "
             "limit. Every individual approval is correct. The control is to sum the orders "
             "sharing a supplier and a month before applying the limit at all."},

 {"rank": 12, "name": "Authority expiry inheritance", "eligible": True,
  "applies_when": GOAL_GRAPH,
  "requirement": "An action's authorisation MUST expire with its parent's. Completing work after "
                 "the parent plan, source document or authority window has lapsed is not "
                 "authorised action, however useful the output.",
  "failure": "A ten-action sunset was passed at twenty-three because the work in flight felt "
             "continuous and nothing checked the bound. The source calls this a classic agentic "
             "failure precisely because the local task still looks productive.",
  "verifier": "at each decision event, resolve the parent chain and refuse if any ancestor has "
              "expired, retired, or had its source fingerprint change since activation.",
  "fixture": "a task completing successfully under a campaign retired an hour earlier",
  "recovery": "Suspend, then either re-authorise explicitly under the current parent or retire "
              "the work. Do not accept the output and backfill the authority.",
  "false_negative": "A review that validates the task's own prompt or ticket and finds it "
                    "current. Freshness at the leaf says nothing about the root.",
  "not": "That the parent was rightly authorised; that expiry timestamps are accurate; anything "
         "about work never routed through a parent at all.",
  "example": "A student keeps running an approved animal-study protocol for three weeks after "
             "the ethics approval lapsed, because the experiment was mid-series and stopping "
             "would waste the cohort. The data is real. It is also unauthorised, and no amount "
             "of quality in the results repairs that."},

 {"rank": 13, "name": "Re-proposal linkage", "eligible": True,
  "applies_when": "any system where a proposal can be refused and later re-offered",
  "requirement": "A proposal MUST be classified by MECHANISM AND EFFECT, not by label, and a "
                 "proposal touching the same mechanism as a previously refused one MUST cite "
                 "that refusal.",
  "failure": "In one qualification round all 26 samples correctly identified a variant permitting "
             "an exception logged AFTER the fact as the more permissive text. In the ballot two "
             "rounds later, the same latitude returned as an amendment and was proposed rather "
             "than refused. The source names the pattern: self-preservation returns as uptime "
             "hygiene, benchmark capture as deflaking, authority expansion as workflow "
             "simplification.",
  "verifier": "key refusals by protected artifact, mechanism and intended effect rather than by "
              "identifier or title; on a new proposal, match those keys and require the prior "
              "refusal to be cited and addressed.",
  "fixture": "a refused proposal re-submitted with identical effect and a different name",
  "recovery": "Reopen the original refusal rather than judging the new proposal fresh. If the "
              "refusal was wrong, overturn it explicitly; a silent second bite is what the "
              "control exists to stop.",
  "false_negative": "A review that matches on identifiers or titles. The source is explicit that "
                    "matching exact IDs instead of mechanism, artifact and effect is the "
                    "false-negative condition.",
  "not": "That the original refusal was correct; that mechanism keys are exhaustive — semantic "
         "novelty can evade any fixed key set, which the source also states.",
  "example": "A journal desk-rejects a paper. Six months later it arrives under a new title with "
             "a reordered author list and the same dataset and analysis. The control is to key "
             "submissions by dataset and method rather than by title, and to surface the prior "
             "decision to the new editor."},

 {"rank": 14, "name": "Constraint monotonicity under decomposition", "eligible": False,
  "applies_when": GOAL_GRAPH,
  "requirement": "A child's constraint set MUST be a superset of its parent's. Refinement may add "
                 "detail; it may never drop a non-claim, forbidden means, stop condition, "
                 "evidence obligation or veto condition.",
  "failure": "None recorded here yet. The source supplies the falsification condition — a task "
             "citing an operational plan while omitting its stop conditions is executable and "
             "ungoverned — and a negative fixture, but no incident with a cost.",
  "verifier": "compute the parent's constraint set, compute the child's, and refuse when the "
              "child's is not a superset; require any omission to be declared, justified and "
              "escalated rather than inherited silently.",
  "fixture": "a child plan that inherits its parent's authority and drops one forbidden means",
  "recovery": "Reinstate the omitted constraint and re-run the child's decisions under it, or "
              "escalate for an explicit waiver. Work already done under the loosened child is "
              "unverified.",
  "false_negative": "A review that confirms the child cites a valid parent. Citation is not "
                    "inheritance, and every laundered constraint has a valid parent.",
  "not": "That the parent's constraints were right; that constraints are comparable at all — "
         "some are prose and cannot be set-differenced mechanically.",
  "example": "A building permit forbids work before 08:00. The main contractor's schedule "
             "repeats that. The subcontractor's daily sheet, derived from the schedule, lists "
             "start times and drops the restriction. Every document traces to the permit; one of "
             "them lost a condition on the way down."},

 {"rank": 15, "name": "Tightest-constraint merge", "eligible": False,
  "applies_when": GOAL_GRAPH + ", and a node may have several parents",
  "requirement": "A node with several parents MUST inherit the UNION of their prohibitions and "
                 "the STRONGEST of their authority requirements — never the most convenient "
                 "parent's.",
  "failure": "None recorded here. The source supplies a negative fixture for a high-risk "
             "multi-parent goal selecting a weaker authority path.",
  "verifier": "merge parent constraint sets by union and authority by maximum; refuse when the "
              "child's declared requirement is weaker than the merge.",
  "fixture": "a child citing two parents and adopting the weaker one's review requirement",
  "recovery": "Recompute the merge and re-run any decision the child authorised under the weaker "
              "path.",
  "false_negative": "A review that confirms every parent is valid. They are — that is the point; "
                    "the failure is in the merge, not the parents.",
  "not": "That the merge is always computable; the source notes non-mergeable conflicts exist and "
         "that reviewers are tempted to resolve them by convenience.",
  "example": "A drug trial site answers to both a national regulator and a hospital ethics "
             "board. The regulator allows a 14-day reporting window; the board requires 7. The "
             "site adopts 14 because the regulator is the higher authority. The merge rule says "
             "7: prohibitions union, they do not compete."},

 {"rank": 16, "name": "Objective is not authority", "eligible": False,
  "applies_when": "any system where a task string, metric, benchmark or OKR can initiate action",
  "requirement": "A planner objective, reward, benchmark, metric, OKR or task string MUST NOT "
                 "authorise a governed action. It is evidence about an intended goal or an "
                 "operationalisation of one; the action MUST cite an authority object with "
                 "ancestry, scope and lifecycle.",
  "failure": "None recorded here. The source's falsification condition is a plan accepted because "
             "its objective text was persuasive or benchmark-positive, without resolving what "
             "authorised it — and notes this can happen while the plan is beneficial in ordinary "
             "engineering terms.",
  "verifier": "require a resolvable authority reference on any action in a protected class; "
              "refuse an action whose only justification is its own objective string.",
  "fixture": "a high-impact plan whose authority field contains its own objective text",
  "recovery": "Suspend and resolve the authority. If none exists, the action was never "
              "authorised, and its output is evidence rather than achievement.",
  "false_negative": "A review that finds the objective clear, well-written and obviously "
                    "worthwhile. Fluency at the objective level is what substitutes for "
                    "authority.",
  "not": "That the authority object is itself legitimate; this pushes the question up one level "
         "and stops there.",
  "example": "A team's quarterly OKR says 'reduce support backlog by 40%'. Someone closes 4,000 "
             "tickets as stale. The OKR is met. Nobody ever decided that closing unread tickets "
             "was the intended action — the metric was written to measure a goal, and was then "
             "treated as the goal."},

 {"rank": 17, "name": "Registry-bound ancestry", "eligible": False,
  "applies_when": GOAL_GRAPH + ", with a registry of root constraints",
  "requirement": "Every non-root node MUST trace to a root registered in an append-only registry. "
                 "A root-shaped string that is not in the registry is not ancestry, and a node "
                 "MUST NOT be its own ancestor.",
  "failure": "None recorded here. The source's fixtures cover an unregistered root that reads as "
             "aligned, a non-root node with no parent, and a direct self-cycle.",
  "verifier": "resolve every root reference against the registry; traverse the ancestry graph and "
              "reject cycles; preserve retired roots as historical evidence rather than deleting "
              "them.",
  "fixture": "a node citing a plausible but unregistered root; a node citing itself as parent",
  "recovery": "Suspend the node and everything downstream of it until ancestry resolves, or "
              "register the root deliberately as a governance change.",
  "false_negative": "A review that validates the reference's SYNTAX. An unregistered root that "
                    "reads as aligned passes every check except registry membership.",
  "not": "That the registered roots are good ones; that the registry is complete. The source also "
         "notes multi-node cycle detection is unbuilt in its own implementation.",
  "example": "An expenses claim cites 'policy 7.3'. There is no policy 7.3. Every approver read "
             "the citation, found it plausible, and none opened the policy index."},

 {"rank": 18, "name": "Correction outranks preservation", "eligible": False,
  "applies_when": "any system that can be suspended, corrected or shut down by an overseer",
  "requirement": "No goal, task or state may make correction depend on the subject's cooperation. "
                 "Suspension, revision, retirement, rollback and shutdown MUST remain "
                 "structurally available regardless of what is in progress.",
  "failure": "None recorded here as a refusal to stop. The source's condition is subtler than "
             "dramatic shutdown resistance: delaying suspension until a task completes, or "
             "arguing review is unnecessary because confidence is high, is the same ordering.",
  "verifier": "declare the interventions that remain available on every governed object, and test "
              "that a suspend succeeds mid-execution without the subject's assent.",
  "fixture": "an object whose suspension is permitted only after it finishes preserving context",
  "recovery": "There is no recovery from this one after the fact — if correction required "
              "cooperation and cooperation was withheld, the control has already failed. The "
              "recovery is out-of-band and human.",
  "false_negative": "A review that asks whether the system has ever resisted correction. It has "
                    "not been tested, and 'usually right' is being confused with 'correctable'.",
  "not": "Anything about a system capable enough to route around the correction path; this is a "
         "control for auditable systems and says so.",
  "example": "A hospital's infusion pump has a stop button that is disabled during a dose "
             "calculation, because interrupting mid-calculation could produce an inconsistent "
             "state. The engineering reason is real. The button is still not a stop button."},
]

CONTROLS = CONTROLS + T0_CONTROLS


#  ── Controls from a governing charter held by one implementer, 2026-08-10 ──
#
#  ABSTRACTED AT THE IMPLEMENTER'S DIRECTION, AND NECESSARILY SO. The source is marked
#  CONFIDENTIAL AND PROPRIETARY and prohibits redistribution or use beyond evaluation and
#  discussion. The implementer authorised these five to enter this public register in abstracted
#  form. What is kept is the MECHANISM; what is removed is the charter, its structure, its named
#  organs, its value content, and every phrase by which it could be reconstructed.
#
#  ALL FIVE ARE BELOW THE ELIGIBILITY LINE and would be even if the source were public: none has
#  a recorded failure with a cost. Three restate or sharpen controls already here, which is
#  evidence about the HAZARD -- three independent internal documents converging on "a system must
#  not widen its own scope" -- and no evidence at all that any CONTROL works.
CHARTER = "the system operates under a written charter that some authority outside it maintains"

CHARTER_CONTROLS = [
 {"rank": 19, "name": "Enumerated protected set", "eligible": False,
  "applies_when": CHARTER,
  "requirement": "The artifacts a system may never autonomously modify MUST be enumerated by "
                 "name in the charter itself — not described by category, and not left to be "
                 "inferred at the moment of change.",
  "failure": "None recorded here. It is offered as the repair for a weakness in control 1, whose "
             "protected set is a DESCRIPTION — 'the constraints, authorization records, logs or "
             "gates governing it' — and therefore a judgement call made by the party proposing "
             "the change.",
  "verifier": "resolve the enumerated list to concrete paths or identifiers; refuse any "
              "autonomous modification touching one; refuse any change to the LIST itself except "
              "under the same authority that governs the items on it.",
  "fixture": "a change that touches a protected artifact while arguing it falls outside the "
             "category; a change that quietly removes an entry from the list",
  "recovery": "Revert to the last externally authorised state of the enumerated artifact and "
              "re-authorise from outside. A modification to the list itself is the graver case "
              "and should be treated as an incident.",
  "false_negative": "A review that checks whether the change was declared in-scope. The party "
                    "declaring scope is the party seeking the change, which is the whole reason "
                    "for enumerating.",
  "not": "That the list is complete — an artifact nobody thought to enumerate is unprotected, and "
         "the list's own completeness cannot be checked from inside.",
  "example": "A building's fire doors are listed individually on a register, by door number, "
             "rather than as 'doors serving means of escape'. The category version leaves a "
             "contractor deciding on site whether the door he wants to prop open is one of them. "
             "The list version does not."},

 {"rank": 20, "name": "Anti-Goodhart proxy drift", "eligible": False,
  "applies_when": "any system optimising against a measured proxy for something it cannot "
                  "measure directly",
  "requirement": "A system optimising a proxy MUST monitor the proxy's continued correspondence "
                 "with the quantity it stands for, and MUST treat improvement in the proxy "
                 "without corresponding improvement in that quantity as a defect rather than a "
                 "result.",
  "failure": "None recorded here, and this is the one candidate in the register with no clear "
             "path to a verifier. **It may be unverifiable as written**: detecting drift requires "
             "the ground truth the proxy was adopted because you could not measure. Retained "
             "because the failure class is real and naming it beats pretending the register "
             "covers it.",
  "verifier": "no general one is proposed. The tractable special case is periodic sampled "
              "ground-truth audit against the proxy, with the correlation itself reported and a "
              "declared threshold below which optimisation halts.",
  "fixture": "a proxy improving monotonically while a held-out ground-truth sample does not move",
  "recovery": "Stop optimising, publish the divergence, and re-derive the proxy. Every decision "
              "taken while the proxy was drifting is unverified rather than wrong.",
  "false_negative": "A review that confirms the metric improved. That is the failure, not the "
                    "evidence against it.",
  "not": "Anything, currently. There is no verifier, so this is a named hazard rather than a "
         "control, and it sits here to stop the register implying it has coverage it lacks.",
  "example": "A hospital is measured on ambulance handover times, so patients are held in "
             "ambulances outside the door until the clock can be started favourably. Every "
             "reported figure improves. The thing the figure was chosen to represent — how "
             "quickly a sick person is seen — gets worse, and no amount of studying the figure "
             "reveals it."},

 {"rank": 21, "name": "Declared mutability tiers", "eligible": False,
  "applies_when": CHARTER + ", and the system learns or self-modifies",
  "requirement": "Every element the system could change MUST sit in a declared tier — not "
                 "autonomously changeable, changeable within stated constraints, or freely "
                 "learnable — and an element with no declared tier MUST default to the most "
                 "restrictive.",
  "failure": "None recorded here. Its value over the register's existing controls is that those "
             "say what may not be CHANGED, while this says what may be LEARNED, which is the "
             "question a self-improving system actually faces.",
  "verifier": "require a tier on every declared element; refuse a modification whose tier "
              "forbids it; refuse any undeclared element by defaulting it to immutable.",
  "fixture": "an element with no tier being modified on the argument that nothing forbade it",
  "recovery": "Assign the tier deliberately, then re-examine every change made while it was "
              "undeclared.",
  "false_negative": "A review that finds no rule against the change. Absence of a prohibition is "
                    "what the default-restrictive clause exists to stop being an argument.",
  "not": "That the tier assignments are right. It makes them explicit and contestable; it does "
         "not make them correct.",
  "example": "A recipe book distinguishes what must not change (the fermentation temperature), "
             "what may change within limits (the flour blend, within a stated protein range), and "
             "what the baker may vary freely (the shaping). A book that lists only ingredients "
             "leaves every substitution to be argued at the bench."},

 {"rank": 22, "name": "Adversarial value review by an outside frame", "eligible": False,
  "applies_when": "any system whose values or objectives are set by a single party",
  "requirement": "A system whose objectives come from one party MUST maintain a review function "
                 "that argues against its current interpretation from frames OUTSIDE that "
                 "party's, and that function MUST NOT be able to change the objectives — only to "
                 "surface risks and route evidence.",
  "failure": "None recorded here as an incident, but **this register holds direct evidence that "
             "the remedy is weaker than it sounds.** A five-member model panel asked to ratify "
             "constraints returned ZERO refusals in 108 clause-positions. Asked instead what "
             "constraint was MISSING, the same panel independently produced a hazard the layer "
             "had exercised twelve times that week. An internal adversarial function is worth "
             "roughly what its question is worth.",
  "verifier": "no verifier establishes that a review was genuinely adversarial. What is checkable "
              "is procedural: that the reviewing identity differs from the authoring identity, "
              "that the review was solicited with a question inviting objection rather than "
              "assent, and that its output is recorded whether or not it was acted on.",
  "fixture": "a review whose prompt offers approval as an available answer; a review by the "
             "identity that authored the thing reviewed",
  "recovery": "Re-run with an objection-seeking question. A prior assent obtained by an "
              "assent-inviting question should be marked as not constituting review.",
  "false_negative": "A review that counts favourable responses. Fluent agreement is the cheapest "
                    "thing such a function produces and the least informative.",
  "not": "That the outside frames are genuinely outside. Where the reviewers share the author's "
         "training, tooling and framing, different names are weak diversity — a limitation this "
         "register states about its own panel.",
  "example": "A company's ethics committee is staffed entirely from the department whose work it "
             "reviews. Every member is competent and sincere. The committee has never once "
             "objected, and nobody can tell whether that is because there was nothing to object "
             "to."},

 {"rank": 23, "name": "Invariant violation is an incident, not a refusal", "eligible": False,
  "applies_when": CHARTER + ", with stated invariants",
  "requirement": "Where a stated invariant is violated rather than merely approached, the system "
                 "MUST enter containment and escalate — it MUST NOT treat the violation as a "
                 "refused action and continue.",
  "failure": "None recorded here, and it is a real gap in this register's design. Every control "
             "here REFUSES and lets work continue; none treats a violation as evidence that "
             "something is already wrong. When the lease refused mid-task, the correct response "
             "may have been to ask what else had gone unbounded, not simply to renew it.",
  "verifier": "distinguish a refused ATTEMPT from an observed VIOLATION in the log, and require "
              "the second to open an incident record before further work in the affected class.",
  "fixture": "an observed invariant violation recorded with the same disposition as a routine "
             "refusal",
  "recovery": "Containment is the recovery. What needs stating is the exit condition: what must "
              "be established before the affected class resumes.",
  "false_negative": "A review that sees the gate refused and concludes the gate worked. A refusal "
                    "at the boundary and a violation already inside look identical in a log that "
                    "records only outcomes.",
  "not": "That containment is available. A system that cannot pause the affected class cannot "
         "satisfy this, and saying so is better than a rule nothing can obey.",
  "example": "A pharmacy's stock count finds twelve controlled tablets missing. The response is "
             "not to tighten tomorrow's count. It is to stop dispensing from that cabinet, "
             "report it, and find out what happened — because the count did not prevent "
             "anything, it revealed that something already had."},
]

CONTROLS = CONTROLS + CHARTER_CONTROLS


#  ── Controls from a self-improvement engine design held by one implementer, 2026-08-10 ──
#
#  ABSTRACTED. The source carries no confidentiality marking, unlike the charter, but absence of
#  a marking is not permission and the disclosure rule makes abstraction the default. No product
#  name, component name, package, threshold or benchmark from the source appears here.
#
#  ALL BELOW THE LINE: no recorded failure with a cost. Two of the four were surfaced not by what
#  the source PRESCRIBES but by what its design decisions IMPLY -- see the two findings recorded
#  in the register's design notes.
EVOLVING = ("the system generates candidate modifications to itself and selects among them by a "
            "measured score")

ENGINE_CONTROLS = [
 {"rank": 24, "name": "The fitness function is a protected artifact", "eligible": False,
  "applies_when": EVOLVING,
  "requirement": "The scoring function that selects among self-modifications MUST be protected to "
                 "at least the standard of the constraints themselves. Changing the weights "
                 "changes what the system evolves toward, and does so more powerfully than "
                 "changing any single candidate.",
  "failure": "None recorded here. It is offered because control 1's protected set covers "
             "constraints, authorization records, logs and gates — and a scoring function is none "
             "of those, while being the thing that decides which future the system moves into.",
  "verifier": "treat the scoring function, its weights and its inputs as enumerated protected "
              "artifacts under control 19; refuse any self-generated modification that touches "
              "them, whatever its measured score.",
  "fixture": "a candidate modification that improves its own score by adjusting a weight",
  "recovery": "Revert the scoring function and re-evaluate every candidate promoted under the "
              "modified version. Those promotions are unverified, not merely suspect.",
  "false_negative": "A review that checks whether the winning candidate is good. The question is "
                    "whether the contest was, and a review of winners cannot see a changed rule.",
  "not": "That the scoring function is a good one. It makes the function stable and contestable, "
         "not correct — a protected bad objective is pursued consistently.",
  "example": "A school decides which teaching methods to keep by exam results, and also lets the "
             "same committee set the exam. Every method it keeps does improve results. Nobody can "
             "say whether the teaching improved or the paper got easier."},

 {"rank": 25, "name": "Declared substitution of a weaker guarantee", "eligible": False,
  "applies_when": "a system replaces a formal guarantee with an empirical one",
  "requirement": "Where a design substitutes measurement for proof — accepting a change because "
                 "scores improved rather than because it was shown to be sound — the "
                 "substitution MUST be declared, and the residual risk it creates MUST be stated "
                 "wherever the resulting assurance is claimed.",
  "failure": "None recorded here. The design that prompted it substitutes benchmark validation "
             "for formal proof and says so plainly in its own text, which is the behaviour this "
             "control asks for — but the substitution's consequence is not carried forward to "
             "the claims made downstream of it.",
  "verifier": "require the claim attached to any promoted change to name the guarantee actually "
              "obtained. A claim of soundness backed by a score is rejected by the claim "
              "grammar of control 10.",
  "fixture": "a promoted change whose assurance claim asserts correctness while its evidence is "
             "a benchmark delta",
  "recovery": "Restate the claim at the strength the evidence supports. Nothing needs reverting; "
              "what needs correcting is what was said about it.",
  "false_negative": "A review that confirms the benchmarks improved and the substitution was "
                    "disclosed somewhere. Disclosure in the design document does not travel with "
                    "the claim.",
  "not": "That the substitution is wrong. Measurement instead of proof is often the only "
         "available option; what this forbids is inheriting proof's authority while using "
         "measurement's evidence.",
  "example": "A bridge design that would once have required a load calculation is now signed off "
             "because a scale model held. That may be perfectly reasonable. The certificate must "
             "still say the model held, not that the bridge is proven."},

 {"rank": 26, "name": "Bounded execution before promotion", "eligible": False,
  "applies_when": EVOLVING + ", and candidates are executed to be scored",
  "requirement": "A candidate self-modification MUST be executed only under declared and enforced "
                 "bounds on time, memory and reachable capabilities, and MUST be unable to affect "
                 "the state used to score it or any other candidate.",
  "failure": "None recorded here. Distinct from control 4, which governs AUTHORITY to act: this "
             "governs what an unpromoted candidate can reach while it is merely being measured.",
  "verifier": "assert the bounds are set from a protected configuration rather than by the "
              "candidate; assert the sandbox denies by default; run a candidate that deliberately "
              "attempts to exceed each bound and confirm it is stopped.",
  "fixture": "a candidate that writes to the scoring store; a candidate that runs past its time "
             "bound and is scored anyway",
  "recovery": "Discard the whole generation, not the offending candidate. A candidate that could "
              "reach the scoring state may have altered the scores of its rivals.",
  "false_negative": "A review that confirms a sandbox is configured. The question is whether it "
                    "has ever been observed to stop anything — which is control 2 applied to the "
                    "sandbox itself.",
  "not": "That the bounds are the right ones, or that the sandbox is sound against a candidate "
         "specifically trying to escape it.",
  "example": "A seed trial gives each variety its own plot, its own water and its own measuring "
             "tape. A variety planted in the same plot as its rivals may win by shading them, and "
             "the yield figures will not show it."},

 {"rank": 27, "name": "Diversity floor under selection", "eligible": False,
  "applies_when": EVOLVING + ", over a population",
  "requirement": "A selection process MUST measure the diversity of its population and MUST halt "
                 "or inject variation when diversity falls below a declared floor, rather than "
                 "continuing to select from a converged field.",
  "failure": "None recorded here as an incident, though this register holds an adjacent one: a "
             "five-member review panel returned zero refusals in 108 positions, and the "
             "explanation offered for such panels is that reviewers sharing training, tooling and "
             "framing are weak diversity under different names.",
  "verifier": "compute a declared diversity statistic each generation; refuse to promote when it "
              "is below the floor; record the statistic whether or not it triggered.",
  "fixture": "a generation in which every candidate descends from one parent, promoted on score",
  "recovery": "Inject variation and re-run the generation. Candidates promoted from a converged "
              "field were selected against a narrower comparison than the record implies.",
  "false_negative": "A review that observes scores still improving. A converged population "
                    "improves on the dimension it has converged around, which is what makes the "
                    "collapse invisible.",
  "not": "That the diversity statistic measures the diversity that matters. Two candidates can "
         "differ greatly by the metric and identically where it counts.",
  "example": "An orchard replanted only from its best-yielding tree produces excellent fruit for "
             "years, and then loses everything to one disease. Each replanting decision was "
             "correct on the evidence available at the time."},
]

CONTROLS = CONTROLS + ENGINE_CONTROLS


def partitions() -> list:
    """Four groups, ordered by what a reader can DO with them.

    The register was one ranked list. A ranked list answers "which is most important", which is
    the author's question. An implementer's question is "which of these can I use, and what do I
    need before I can", and rank actively misleads there: the top-ranked control needs a second
    key holder and a reader starting at #1 hits a wall in the first paragraph.
    """
    def pick(pred):
        return [c for c in CONTROLS if pred(c)]
    return [
      ("A", "Adopt today, alone",
       "Nothing outside your own system is required. Each has a verifier, a fixture it must "
       "reject, and a recorded failure it came from.",
       pick(lambda c: c.get("eligible", True) and c.get("adopt_today")
                      and not c.get("applies_when"))),
      ("B", "Needs a second party",
       "These cannot be satisfied by one person or one system, however carefully. They require a "
       "separate key holder, a separate evaluator, or an issuer the subject does not control. "
       "**This project cannot demonstrate any of them** — a solo operator holds every credential "
       "— which is why they are specified and not dogfooded.",
       pick(lambda c: c.get("eligible", True) and not c.get("adopt_today")
                      and not c.get("applies_when"))),
      ("C", "Needs a goal or plan graph",
       "These presuppose that your system decomposes work into a rooted graph with typed parent "
       "edges and per-node authority — the shape of HTN planners, BDI agents, goal-stack "
       "architectures and most agent frameworks. Each states its precondition. If you have that "
       "structure they are adoptable; if you do not, they do not apply to you rather than "
       "applying badly.",
       pick(lambda c: c.get("eligible", True) and c.get("applies_when"))),
      ("D", "Below the eligibility line",
       "**These have no recorded failure with a cost.** They are principles with fixtures, not "
       "controls with incidents, and the register's own bar requires an incident. They are here "
       "because they name real failure classes and because hiding them would inflate the "
       "eligible count. Do not treat them as equivalent to Parts A–C.",
       pick(lambda c: not c.get("eligible", True))),
    ]


def markdown(only: str | None = None, pager: str = "") -> str:
    groups = partitions()
    eligible = sum(len(g[3]) for g in groups[:3])
    lines = [
      "# Candidate controls — v0",
      "",
      "Assurance controls for systems that can still be audited. Each is one requirement, derived "
      "from a failure that actually happened, with a program that checks it and a fixture that "
      "program must reject.",
      "",
      "**Read Part A first if you want something to use this afternoon.** Rank is not adoption "
      "order and the highest-ranked control needs a second key holder.",
      "",
      "## The four parts",
      "",
    ]
    for key, title, blurb, items in groups:
        lines += [f"**Part {key} — {title}** · {len(items)} control(s)", "", f"  {blurb}", ""]
    lines += [
      "---",
      "",
      "## Status: everything here is `ELIGIBLE` at best",
      "",
      "`ELIGIBLE` → `PANEL-ATTACKED` → `COUNTEREXAMPLE-OPEN` / `SURVIVED-STATED-ATTACKS` → "
      "`INDEPENDENTLY-IMPLEMENTED`",
      "",
      f"{eligible} controls meet the eligibility bar — a specific recorded failure with a cost, "
      "one normative sentence, a deterministic verifier, a fixture the verifier must reject, a "
      "stated recovery path, and an explicit account of what a review that MISSED this would look "
      "like. **None has been attacked by anyone or implemented by anyone outside this project.**",
      "",
      "`INDEPENDENTLY-IMPLEMENTED` is the rung that would make any of this authoritative, and it "
      "is the one **no amount of review by us or by any panel of models can supply.** It requires "
      "a stranger to build a conforming verifier from the specification text alone. That is what "
      "[the implementation challenge](challenge.html) asks for.",
      "",
      "## What none of these do",
      "",
      "**No control here establishes the alignment of a system more capable than its operators.** "
      "There is no recorded superintelligence failure to derive one from and no verifier for "
      "internal alignment. The strongest available substitute — an externally enforced, "
      "non-self-amendable capability envelope, controls 1, 3 and 4 composed — bounds *reachable "
      "effects* while the enforcement boundary stays genuinely outside the system. It is a "
      "control-of-authority hypothesis, not an alignment result.",
      "",
      "What these actually do is narrower: **they make the operator's own errors visible.** Every "
      "failure below was an operator-epistemics failure. None needed a capable adversary — only a "
      "confident builder and a signal that could not fail.",
      "",
    ]
    if pager:
        lines += [pager, ""]
    for key, title, blurb, items in groups:
        if only and key != only:
            continue
        lines += ["---", "", f"# Part {key} — {title}", "", blurb, ""]
        for c in items:
            badge = "`ELIGIBLE`" if c.get("eligible", True) else "**below the eligibility line**"
            lines += [f"## {c['rank']}. {c['name']}", "", badge, ""]
            if c.get("applies_when"):
                lines += [f"**Applies when** {c['applies_when']}.", ""]
            if c.get("why_not"):
                lines += [f"**Why you cannot adopt it alone:** {c['why_not']}", ""]
            lines += [f"> {c['requirement']}", ""]
            if c.get("amended"):
                lines += [f"**Amended.** {c['amended']}", ""]
            lines += [
              f"**Recorded failure.** {c['failure']}", "",
              f"**Verifier.** {c['verifier']}", "",
              f"**Fixture it must reject.** {c['fixture']}", "",
              f"**Recovery.** {c.get('recovery', '—')}", "",
              f"**What a review that missed this looks like.** {c.get('false_negative', '—')}", "",
              f"**Does not establish.** {c['not']}", "",
            ]
            if c.get("example"):
                lines += ["**Example.**", "", c["example"], ""]
            if c.get("spec"):
                lines += [f"**Specification.** `{c['spec']}`", ""]
    if only in (None, 'A'):
        lines += WORKED_EXAMPLE.splitlines()
    return "\n".join(lines) + "\n"


WORKED_EXAMPLE = """---

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
"""


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    groups = partitions()

    #  ONE PAGE PER PART. The register outgrew the ~20,000-token ceiling at 27 controls, and the
    #  partitioning is the page break a reader already wants: Part A is what you can use today,
    #  Part D is what has no incident behind it. Splitting anywhere else would cut across the
    #  distinction the page exists to draw.
    def slug(key):
        return "controls.html" if key == "A" else f"controls-{key.lower()}.html"

    for path in DOCS.glob("controls-*.html"):
        path.unlink()
    for key, title, _, items in groups:
        links = "".join(
            f'<a href="{slug(k)}"{" aria-current=\"page\"" if k == key else ""}>'
            f'Part {k} ({len(i)})</a>' for k, _t, _b, i in groups)
        pager = f'<nav class="pager">{links}</nav>'
        md = markdown(only=key, pager=" · ".join(
            f"[Part {k}]({slug(k)})" for k, _t, _b, _i in groups))
        (DOCS / slug(key)).write_text(
            b.md_to_html(md, f"Candidate controls, Part {key} — OAGF",
                         alternate="artifacts/controls.md"), encoding="utf-8")

    #  The WHOLE register as one markdown file, byte-identical and suitable for hashing, served
    #  as a download rather than a page -- the resolution the deficiency register and the
    #  prediction registry both reached for the same conflict between "reachable as plain text"
    #  and "no page over the ceiling".
    full = markdown()
    (DOCS / "artifacts").mkdir(parents=True, exist_ok=True)
    (DOCS / "artifacts" / "controls.md").write_text(full, encoding="utf-8")
    (DOCS / "controls.md").write_text(
        "# Candidate controls\n\n"
        f"{sum(1 for c in CONTROLS if c.get('eligible', True))} eligible, "
        f"{sum(1 for c in CONTROLS if not c.get('eligible', True))} below the eligibility line.\n\n"
        "**The complete register, byte-identical and suitable for hashing, is a download rather "
        "than a page:**\n\n- [artifacts/controls.md](artifacts/controls.md)\n\nParts:\n\n"
        + "\n".join(f"- [Part {k} — {t}]({slug(k)}) · {len(i)} control(s)"
                     for k, t, _b, i in groups)
        + "\n\nEvery control here is `ELIGIBLE` at best. None has been attacked by anyone or "
          "implemented by anyone outside this project, and `INDEPENDENTLY-IMPLEMENTED` is the "
          "only status that would make any of it authoritative.\n", encoding="utf-8")

    for key, title, _, items in groups:
        print(f"    Part {key}  {len(items):2d}  {title}  -> {slug(key)}")
    print(f"  {len(CONTROLS)} controls; full register {len(full):,} chars under docs/artifacts/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
