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

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_round_pages as b                                            # noqa: E402

DOCS = REPO_ROOT / "docs"
#  Written by main() AFTER the pages are on disk; read by build_viewer.py so its pruner keeps
#  what was actually published rather than what a partition function says ought to exist.
RECEIPT = REPO_ROOT / "docs" / "artifacts" / "controls-pages.json"

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
                 "instrument authorship, response custody, scoring, promotion. **Amended "
                 "2026-08-10:** the separation extends to the AUTHORING of the critique — an "
                 "artifact's evaluation MUST NOT be produced by the same process that produced "
                 "the artifact.",
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
         "training bias; that the evaluation was demanding. On the amendment specifically: a "
         "different model family is **weak diversity** and this project is the worked example — "
         "its two harnesses share one operator, one repository, one framing and much training "
         "culture, and have twice agreed on a design neither had checked was implementable. "
         "Separating the authoring process raises the floor; it does not deliver independence.",
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
                 "inferred at the moment of change. **Amended 2026-08-10: the set is "
                 "EFFECT-defined as well as path-defined.** A change outside the list is "
                 "protected anyway if it alters how governed decisions are proposed, classified, "
                 "adopted, reviewed, validated or audited — a helper script that rewrites "
                 "fixtures, a prompt telling a reviewer to ignore a failed check, or a "
                 "documentation change to what counts as approval. The reviewer's question is "
                 "whether the change affects governed behaviour, not whether its path is listed.",
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
  "not": "That the list is complete. The effect clause narrows the gap without closing it: it "
         "turns an omission from a silent bypass into a question a reviewer is obliged to ask, "
         "and a reviewer who answers it wrongly still lets the change through. The list's own "
         "completeness cannot be checked from inside.",
  "example": "A building's fire doors are listed individually on a register, by door number, "
             "rather than as 'doors serving means of escape'. The category version leaves a "
             "contractor deciding on site whether the door he wants to prop open is one of them. "
             "The list version does not."},

 {"rank": 20, "name": "Anti-Goodhart proxy drift", "eligible": False,
  "governs": "measuring itself",
  "applies_when": "any system optimising against a measured proxy for something it cannot "
                  "measure directly",
  "requirement": "A system optimising a proxy MUST monitor the proxy's continued correspondence "
                 "with the quantity it stands for, and MUST treat improvement in the proxy "
                 "without corresponding improvement in that quantity as a defect rather than a "
                 "result.",
  "failure": "None recorded here. **AMENDED 2026-08-10.** This entry previously said it was the "
             "one candidate with no clear path to a verifier and that none was proposed. That "
             "was too strong, and wrong in the same shape as this project's prior-art overclaim "
             "on control 2: an absence asserted from not having looked. The hazard splits in "
             "two, and only one half is unverifiable.\n\n"
             "**Detection of drift** — still no general verifier, and probably none exists. "
             "Regressional and extremal drift occur with nobody gaming anything, and catching "
             "them needs the ground truth the proxy was adopted to replace.\n\n"
             "**The incentive that produces adversarial drift** — verifiable as a graph "
             "property, and has been in the public literature since Everitt et al. 2021. That "
             "half is now control 28.",
  "verifier": "none for detection. For the adversarial variant, control 28: enumerate the "
              "directed paths from an agent's actions through the proxy to its reward and assert "
              "the set is empty. The tractable special case for detection remains a periodic "
              "sampled ground-truth audit, with the correlation itself reported and a declared "
              "threshold below which optimisation halts. Optimising a proxy degrades it in four "
              "distinct ways [Manheim & Garrabrant 2018] — regressional, extremal, causal and "
              "adversarial — and the defence against the last is not a cleverer proxy but the "
              "removal of optimisation pressure from it.",
  "fixture": "a proxy improving monotonically while a held-out ground-truth sample does not move",
  "recovery": "Stop optimising, publish the divergence, and re-derive the proxy. Every decision "
              "taken while the proxy was drifting is unverified rather than wrong.",
  "false_negative": "A review that confirms the metric improved. That is the failure, not the "
                    "evidence against it.",
  "not": "That the proxy still measures what it stands for. With control 28 satisfied, this "
         "establishes only that no agent is paid to break the correspondence — drift from "
         "ordinary optimisation pressure is untouched, and remains the half with no verifier.",
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


#  Mined 2026-08-10 from an implementer's design for an instrument that measures its own system's
#  proximity to a capability threshold. Abstracted at the custodian's direction: the source is
#  marked confidential, so no quantity names, class names, subject labels or authority rows appear
#  here. What survives abstraction is general, and where the mechanism has public prior art it is
#  cited rather than presented as new -- the lesson of control 2's overclaim.
MEASURED = "any system that measures its own capability, progress or risk"

ECI_CONTROLS = [
 {"rank": 28, "name": "No incentive path from action to metric to reward", "eligible": False,
  "applies_when": "any system where an agent's actions can influence a measured quantity, and "
                  "that quantity can influence the agent's reward, authority, budget or standing",
  "requirement": "The system MUST enumerate, for each agent and each governed metric, the "
                 "directed paths running from that agent's actions through the metric to that "
                 "agent's reward or authority, and MUST establish that no such path exists. The "
                 "enumeration MUST be re-run whenever an agent or a reward structure changes, "
                 "and its result recorded.",
  "failure": "None recorded here. It is the mechanical half of control 20, which this register "
             "wrongly described as having no path to a verifier at all. An agent acquires an "
             "instrumental incentive to influence a quantity exactly when a directed path runs "
             "from its actions through that quantity to its reward [Everitt et al. 2021] — which "
             "makes the governance requirement a checkable graph property rather than an "
             "exhortation.",
  "verifier": "draw the influence diagram over {agent actions, metric inputs, metric outputs, "
              "agent reward/authority}; enumerate directed action → metric → reward paths; "
              "assert the set is empty. The only permitted sink of a metric reading is human "
              "deliberation. Ledger the result, so a reviewer can confirm the check covered that "
              "agent for that change rather than assuming the property holds by good intentions.",
  "fixture": "an agent whose performance review reads its own contribution to the metric; a "
             "reward function taking the metric as an input at any depth",
  "recovery": "Remove the edge before the change ships, then re-verify. Decisions taken while it "
              "existed are unverified rather than wrong.",
  "false_negative": "A review confirming that no agent is INSTRUCTED to optimise the metric. The "
                    "property is structural, not intentional — the incentive exists whether or "
                    "not anyone named it, and the agent need not know the path is there.",
  "not": "That the metric is a good one, or that drift is absent. It establishes only that "
         "nobody is paid to cause drift. The regressional and extremal variants need no "
         "incentive and are untouched by this.",
  "example": "A school ranks departments by exam results and lets each department set its own "
             "paper. Nobody has to intend anything for the papers to get easier. Cutting the "
             "edge — an outside body sets the paper — does not make the exam a good measure of "
             "learning. It stops the exam being something the measured party profits by moving."},

 {"rank": 29, "name": "Enumerated permitted consequences of a measurement", "eligible": False,
  "applies_when": MEASURED,
  "requirement": "What a measurement MAY trigger MUST be enumerated exhaustively, and what it "
                 "may never trigger MUST be enumerated exhaustively alongside it. The "
                 "enumeration MUST itself be a protected artifact under control 19: altering it "
                 "is a governed, recorded act rather than an engineering convenience.",
  "failure": "None recorded here. Distinct from control 19, which protects artifacts: this "
             "protects what a READING is permitted to cause. A gauge whose output could be acted "
             "on automatically is an accelerator wearing the costume of an instrument.",
  "verifier": "assert every consumer of the measurement resolves to a permitted consequence; "
              "assert the enumeration's own hash is in the protected set and changes only "
              "through the authorised path.",
  "fixture": "a measurement wired to a budget allocation, a priority change or an automatic "
             "throttle; an edit to the enumeration landed with no authorisation record",
  "recovery": "Sever the consumer, then review every decision it produced.",
  "false_negative": "A review that finds the policy document and confirms it is well written. "
                    "The question is what READS the number, not what the document says about it.",
  "not": "That the permitted consequences are the right ones, nor that the measurement is "
         "accurate. A well-governed reading of a bad gauge is still a bad gauge.",
  "example": "A smoke detector may wake the household and call the fire service. It may not "
             "unlock the doors, cut the power, or adjust the thermostat — and the list of what "
             "it may do is not something the installer changes on a Tuesday."},

 {"rank": 30, "name": "A filter on a metric's inputs must not improve the metric",
  "eligible": False,
  "applies_when": "any system that can exclude, quarantine or dispute inputs to a measurement",
  "requirement": "A mechanism that suppresses or disputes an input to a measurement MUST be "
                 "append-only, reversible, reviewable from outside, and MUST NOT be able to "
                 "improve the measurement by suppressing. Where suppression can move the reading "
                 "at all, the direction MUST be the unfavourable one.",
  "failure": "None recorded here. It is the anti-gaming mechanism's own anti-gaming property: "
             "without it, the defence against input gaming becomes the most efficient "
             "input-gaming channel available, because it is the one channel sanctioned to remove "
             "evidence.",
  "verifier": "for each suppressible input, compute the reading with and without suppression and "
              "assert suppression never raises it; assert the suppression record is append-only "
              "and that every suppression is an escalation rather than a silent filter.",
  "fixture": "a quarantine that raises a coverage or confidence figure by removing the sample "
             "that lowered it; a dispute record that deletes rather than marks",
  "recovery": "Reinstate every suppressed input, recompute, and publish both readings.",
  "false_negative": "A review that confirms suppressions are logged. Logged suppression that "
                    "flatters the number is the failure, fully documented and fully in view.",
  "not": "That the suppressions are correct — only that they cannot pay. A mechanism that "
         "excludes exactly the wrong inputs while lowering the reading satisfies this.",
  "example": "A laboratory may discard a contaminated sample, and should record that it did. If "
             "discarding contaminated samples raises reported purity, the working definition of "
             "\"contaminated\" will drift — and every step of the drift will be in the log, "
             "correctly dated, signed, and impossible to distinguish from diligence."},

 {"rank": 31, "name": "Process metrics may not be reported as outcome validity",
  "eligible": False,
  "applies_when": "any measurement instrument or evaluation reporting on itself",
  "requirement": "Evidence that an instrument RAN — throughput, coverage, cycles completed, "
                 "records processed — MUST NOT be reported in a position where evidence that its "
                 "readings are TRUE is required. Outcome validity MUST be established by "
                 "calibration against known answers or by an explicit construct-validity "
                 "argument [Raji et al. 2021], and MUST be labelled as which.",
  "failure": "None recorded here. Distinct from control 10, which governs the GRAMMAR of a "
             "claim: this governs the CATEGORY of evidence offered in support of one. A claim "
             "can be perfectly bounded and still rest on evidence that bears on nothing it says.",
  "verifier": "for each reported assurance figure, classify its evidence as operational or "
              "validity, and reject an operational figure standing where validity is claimed.",
  "fixture": "a report of \"ten thousand runs, full coverage\" offered as evidence the readings "
             "are right",
  "recovery": "Restate at the strength the evidence supports. The runs are not wasted; they are "
              "mislabelled, and they still establish the instrument is operating.",
  "false_negative": "A review that verifies the throughput figures are accurate. They usually "
                    "are. Their accuracy is not in question and never was.",
  "not": "That operational metrics are worthless. They establish the instrument is running, "
         "which is a real thing to know and a different thing from the readings being true.",
  "example": "A thermometer factory reports that it tested four hundred thousand units this "
             "quarter and that every one produced a reading. Both numbers are true. Neither bears "
             "on whether any reading was the temperature."},

 {"rank": 32, "name": "Stale self-metadata downgrades rather than asserts", "eligible": False,
  "applies_when": "any assurance artifact carrying metadata about its own currency, coverage or "
                  "maturity",
  "requirement": "An artifact's claims about its own status MUST themselves be dated and "
                 "re-verified, and MUST expire. Where the self-metadata is stale, missing or "
                 "unverifiable, the artifact's status MUST be downgraded automatically rather "
                 "than retained.",
  "failure": "None recorded here directly, though this record holds the adjacent error: its "
             "context check verifies IDENTITY, NOT TRUTH, and passed on a pinned file containing "
             "a claim already disproved. A status that cannot go stale is a status that stops "
             "being about anything.",
  "verifier": "assert every status field carries a verification date and a maximum age; assert "
              "the status derivation is deterministic and that exceeding the age yields a LOWER "
              "status, never the prior one.",
  "fixture": "an attestation whose coverage figure carries no date; a status that survives its "
             "own re-verification deadline unchanged",
  "recovery": "Downgrade, then re-verify. The interval is unverified, not failed — and the "
              "distinction matters, because treating it as failed invites re-asserting the old "
              "status once the check passes again.",
  "false_negative": "A review that reads the status field. The status field is the artifact "
                    "under suspicion.",
  "not": "That current metadata is correct metadata. Freshness is not accuracy, and a promptly "
         "re-verified wrong status is still wrong.",
  "example": "A fire extinguisher with no inspection tag is not an extinguisher of unknown "
             "condition to be assumed fine until someone checks. It is an untagged extinguisher, "
             "and the building's register must say so on its own, without being asked."},
]

CONTROLS = CONTROLS + ECI_CONTROLS


#  Mined 2026-08-10 from an implementer's assessment of whether its own creative bottleneck can be
#  automated. Abstracted: no gauge names, workstream ids, decision ids or technique numbers.
#  Two of these are gates this register needed and did not have -- both of its published false
#  claims were absence claims made in prose, which control 5 does not reach.
CLAIMING = "any system making claims about its own outputs or capability"

INSIGHT_CONTROLS = [
 {"rank": 33, "name": "No read edge from a measured agent to its own measurement",
  "eligible": False, "governs": "measuring itself",
  "applies_when": "any system that measures agents it also operates",
  "requirement": "An agent that is the subject of a measurement MUST NOT be able to read that "
                 "measurement, its inputs, its derived status labels, or any dashboard of them.",
  "failure": "None recorded here. Distinct from control 28, which forbids the REWARD path: this "
             "forbids the READ path. It is the cheaper of the two and does not depend on the "
             "influence diagram being complete — an enumeration that misses an edge fails "
             "silently, while a read prohibition fails loudly.",
  "verifier": "assert the measurement store and its derived labels sit outside every measured "
              "agent's read scope; assert no prompt, context file or retrieval surface exposes "
              "them.",
  "fixture": "an agent whose context window includes the status label derived from its own "
             "output",
  "recovery": "Remove the exposure, then treat every output produced with it as unverified — the "
              "agent may have been steering by it without anything in the record saying so.",
  "false_negative": "A review confirming no agent is rewarded for the metric. That is control "
                    "28's question, and an agent can steer toward a number nobody pays it for.",
  "not": "That the agent cannot infer the measurement from other observations it is allowed.",
  "example": "A factory may measure line defect rates. Posting the running rate above the line "
             "changes what the line does — not through anyone's incentive, simply because it is "
             "now information the work can be steered by."},

 {"rank": 34, "name": "Validators score the artifact, not the property being claimed",
  "eligible": False,
  "applies_when": CLAIMING,
  "requirement": "A validator MUST score object-level correctness or utility against an external "
                 "referent. It MUST NOT score the abstract property the system is trying to "
                 "claim.",
  "failure": "None recorded here. Scoring the claimed property directly is unfalsifiable and "
             "gameable in one step, because the scorer and the claim share a definition that "
             "nothing outside the system constrains.",
  "verifier": "for each validator, assert its score is defined over domain outcomes with an "
              "external referent; reject any rubric whose top-level dimension is the property "
              "under claim.",
  "fixture": "a rubric asking a model to rate its own output's \"novelty\", \"insightfulness\" "
             "or \"alignment\" on a scale",
  "recovery": "Rescore against domain outcomes. Prior scores are not evidence at a lower "
              "strength; they are evidence about the rubric.",
  "false_negative": "A review that finds the rubric detailed, calibrated and consistently "
                    "applied. It can be all three and still measure agreement with itself.",
  "not": "That domain scores are a good proxy for the property. They are merely constrained by "
         "something the system does not define.",
  "example": "A school wanting to show it teaches critical thinking can test whether pupils solve "
             "unfamiliar problems, or it can ask them to rate how critically they thought. The "
             "second is cheaper, always improves, and measures nothing."},

 {"rank": 35, "name": "A novelty claim requires a derivability screen", "eligible": False,
  "applies_when": "any claim that an output, mechanism or result is new",
  "requirement": "Before an output may be labelled novel, it MUST be shown not derivable from its "
                 "own inputs, by a party holding the input corpus that did not produce the "
                 "artifact, under a stated protocol. Recombination a holder of the inputs can "
                 "reproduce is not novelty.",
  "failure": "**Recorded, twice, against this register.** Control 2 claimed its mechanism was "
             "unclaimed while mutation testing and chaos engineering had it; control 20 claimed "
             "no verifier existed while one had been in the literature since 2021. Both were "
             "published. Both were caught by a person, neither by a gate.",
  "verifier": "hold out the input corpus, give it to a party that did not produce the artifact, "
              "and require an attempt at derivation under a pre-registered protocol. Novelty "
              "survives only what they fail to reproduce.",
  "fixture": "an output presented as new that a frozen panel reproduces from the stated inputs",
  "recovery": "Withdraw the novelty claim, keep the artifact, and republish the correction "
              "where the claim appeared rather than only where it was made.",
  "false_negative": "A review by the author searching for prior art. The applicant is the one "
                    "party who cannot run this check, which is why patent offices employ "
                    "examiners rather than accept declarations.",
  "not": "That a surviving artifact is valuable, only that it is not a remix of what it was "
         "given.",
  "example": "A patent examiner does not assess whether an invention is clever. They search the "
             "prior art, and the search is done by someone other than the applicant."},

 {"rank": 36, "name": "Absence claims carry their own evidence label", "eligible": False,
  "applies_when": "any assurance document claiming that something does not exist",
  "requirement": "A claim of absence MUST be labelled distinctly from a claim of presence, and "
                 "the label MUST name the corpus searched, the query, and the date. An "
                 "unlabelled absence claim MUST be treated as unsupported rather than as a "
                 "finding.",
  "failure": "**Both of this register's published false claims were absence claims in prose.** "
             "Control 5 did not reach them: it governs computed counts. A scan that cannot see a "
             "file reports absence, and so does a person who did not look — the two are "
             "indistinguishable in a sentence, which is the whole problem.",
  "verifier": "require every \"no X exists\" claim to carry a label naming corpus, query and "
              "date; reject the claim otherwise. The label is checkable even when the claim is "
              "not.",
  "fixture": "a document asserting no prior art exists with no record of any search",
  "recovery": "Run the search, label it, and restate. If the search finds the thing, the "
              "correction goes wherever the claim travelled.",
  "false_negative": "A review that agrees with the absence claim. Two people who did not look "
                    "agree readily, and this register has the receipts.",
  "not": "That a labelled absence claim is true. It makes the search checkable, not exhaustive — "
         "a named corpus can still be the wrong corpus.",
  "example": "\"There is no such file\" and \"I looked in these three directories and found no "
             "such file\" are different sentences. Only the second can be caught being wrong."},

 {"rank": 37, "name": "Autonomy claims require per-artifact human-contribution provenance",
  "eligible": False,
  "applies_when": "any claim that a system produced something without human input",
  "requirement": "Every artifact supporting an autonomy claim MUST carry a provenance record "
                 "tagging human contributions at the point they entered, or explicitly recording "
                 "none. An artifact without that record MUST NOT support the claim.",
  "failure": "None recorded here, and **this project is squarely exposed**: a custodian directs "
             "every session, and nothing in the record tags where his direction supplied the "
             "decisive step. Any autonomy figure computed over this record today would be "
             "uncheckable in exactly the way this control forbids.",
  "verifier": "assert each artifact's provenance names its human contributions or records none; "
              "compute autonomy figures only over artifacts carrying the record, and report the "
              "uncovered remainder rather than excluding it silently.",
  "fixture": "an artifact counted as autonomous whose decisive step came from an operator "
             "instruction",
  "recovery": "Recompute over the covered set and publish both figures. The uncovered artifacts "
              "are unknown, not autonomous.",
  "false_negative": "A review of the session logs by the operator who ran them. The decisive "
                    "instruction rarely looks decisive to the person who gave it.",
  "not": "That the tagging is honest or complete. It makes the gap visible where the gap is "
         "recorded.",
  "example": "A bakery advertising everything as made on the premises has to say which morning "
             "the bread came from the supplier — per loaf, not per year."},

 {"rank": 38, "name": "The definition of a measured quantity is a protected artifact",
  "eligible": False, "governs": "measuring itself",
  "applies_when": "any system reporting a metric over time",
  "requirement": "The definition of a measured quantity MUST be a protected artifact, changeable "
                 "only through the authorised path and as a recorded event. A change to the "
                 "definition MUST break the series: readings from either side are not comparable "
                 "and MUST NOT be reported as one trend.",
  "failure": "None recorded here. Distinct from controls 19 and 29 — those protect the artifact "
             "set and what a reading may cause. This protects what a reading MEANS, which is the "
             "cheapest thing in the system to move and the only one that leaves no trace in the "
             "numbers themselves.",
  "verifier": "hash the definition; assert every reported series names the definition hash in "
              "force for each point; reject a series spanning two hashes.",
  "fixture": "a metric improving across a definition change, presented as one trend line",
  "recovery": "Split the series at the change and republish both segments. Do not restate the "
              "old segment under the new definition; that is a new measurement of old events.",
  "false_negative": "A review that confirms the numbers were computed correctly. They were. The "
                    "definition moved underneath them.",
  "not": "That the definition is a good one, or that the new definition is worse than the old.",
  "example": "A country that changes how it counts unemployment has not reduced unemployment, "
             "and the chart running straight through the change is the most misleading honest "
             "chart available."},

 {"rank": 39, "name": "A compounding claim requires ablation and multi-family transfer",
  "eligible": False,
  "applies_when": "any claim that a capability improvement compounds or is reusable",
  "requirement": "A compounding claim MUST show the extracted capability improves performance "
                 "across at least three independent, pre-registered task families, AND that "
                 "removing it degrades later performance. Neither half alone establishes it.",
  "failure": "None recorded here.",
  "verifier": "run the ablation and report both arms; require the transfer families to be "
              "independent and named before the result, not selected after it.",
  "fixture": "a reusable component demonstrated on one task family; a transfer result with no "
             "ablation arm",
  "recovery": "Restate as a single demonstrated improvement. Nothing needs withdrawing except "
              "the word that claimed it generalises.",
  "false_negative": "A review confirming the component is used widely. Adoption is not transfer, "
                    "and a component everything depends on has never been removed to see.",
  "not": "That the improvement will keep compounding — only that it did once, reproducibly, "
         "across families chosen in advance.",
  "example": "A surgical technique that helps in three unrelated procedures, and whose withdrawal "
             "makes outcomes worse again, has been shown to be a technique. One good outcome "
             "shows a good day."},

 {"rank": 40, "name": "A program pre-commits the observation that ends it", "eligible": False,
  "applies_when": "any research or development program with an open-ended goal",
  "requirement": "A program MUST state, before it begins, the observation that would end it and "
                 "the time by which that observation would be decisive. The stop condition MUST "
                 "be recorded wherever the program's results are reported.",
  "failure": "None recorded here — **this project practises it and never registered it.** Its "
             "outreach carries a pre-committed adverse outcome (no serious external attempt after "
             "6–8 weeks, with the outreach actually done) and that outcome will be published if "
             "it occurs. A practice that lives only in one document is not a control.",
  "verifier": "assert the program's record contains a dated stop condition predating its first "
              "result, and that the condition is evaluable by someone who did not run the "
              "program.",
  "fixture": "a program whose stop condition was written after its first negative result; a stop "
             "condition only its author can evaluate",
  "recovery": "There is no recovery for a missing stop condition, only disclosure: state that "
              "the program ran without one, and that continuing is therefore not evidence of "
              "anything.",
  "false_negative": "A review that finds a stop condition. Check its date against the first "
                    "result, because a condition written afterwards is a description of what "
                    "happened.",
  "not": "That the program will stop. It makes a failure to stop visible, which is a different "
         "and more achievable thing.",
  "example": "A drug trial names its futility boundary before the first patient is enrolled. A "
             "trial that decides afterwards what would have counted as failure has not run a "
             "trial."},
]

CONTROLS = CONTROLS + INSIGHT_CONTROLS


#  Below-the-line controls are grouped by WHAT THEY GOVERN, not by when they arrived. Arrival
#  order is provenance and no reader cares; "does this apply to my system" is the question they
#  came with. Tagged here rather than on each entry so a batch cannot be half-labelled.
#  Mined 2026-08-10 from an implementer's knowledge-distillation plan and its alignment-invariants
#  thesis. Abstracted. Both sources yielded far more control-shaped material than is taken here;
#  what was dropped is recorded in record/designs/candidate-control-register.md rather than added,
#  because a register that grows without a bar becomes a catalogue and stops ranking anything.
DISTILLED_CONTROLS = [
 {"rank": 41, "name": "Agreement among correlated evaluators is not independent evidence",
  "eligible": False, "governs": "claims about its own outputs",
  "applies_when": "any system aggregating judgements from multiple evaluators",
  "requirement": "Where agreement between evaluators is offered as evidence, the correlation "
                 "between their errors MUST be estimated and reported. Agreement counts only to "
                 "the extent the errors are independent, and shared training, shared prompts, "
                 "shared framing or a shared operator MUST be disclosed as correlation.",
  "failure": "None recorded here as an incident, but **this project is the standing example**: "
             "its panel is five language models with overlapping training culture, and its two "
             "harnesses share one operator, one repository and one framing. Its own instructions "
             "already say agreement between them settles nothing. That is a caveat in a file, "
             "not a control on a number.",
  "verifier": "report inter-evaluator error correlation alongside any agreement statistic; "
              "reject an agreement claim that names no correlation estimate. Where correlation "
              "cannot be estimated, say the agreement is uninterpretable rather than reporting "
              "it bare.",
  "fixture": "a consensus figure from five evaluators sharing a base model, reported as five "
             "independent confirmations",
  "recovery": "Restate the agreement with its correlation, or withdraw it. Nothing needs "
              "re-running; what was wrong is the weight placed on it.",
  "false_negative": "A review that counts the evaluators. Five is a number, not a diversity.",
  "not": "That uncorrelated evaluators are right. Independence bounds how much agreement can "
         "mean; it does not supply competence.",
  "example": "Five weather forecasters agreeing tells you a great deal if they use different "
             "models and rather little if they all read the same bulletin. The count is the same "
             "in both cases, and it is the wrong thing to have counted."},

 {"rank": 42, "name": "Capability claims name their stratum", "eligible": False,
  "governs": "claims about its own outputs",
  "applies_when": "any claim that a system has a capability",
  "requirement": "Generated, exists, compiles, deploys, is integrated, is used, and produced a "
                 "useful outcome are DISTINCT claims. A current-state statement MUST name which "
                 "stratum it asserts, and MUST NOT let a lower rung stand where a higher one is "
                 "implied.",
  "failure": "None recorded here. It is the most common way a true sentence misleads: every rung "
             "is a real achievement, and the distance between the bottom and the top is where "
             "most of the work lives.",
  "verifier": "require each capability statement to carry its stratum label; reject an aggregate "
              "count that sums across strata without reporting the breakdown.",
  "fixture": "a roster reporting agents 'built' where most have never been invoked",
  "recovery": "Recount by stratum and publish the ladder. The lower figures are not "
              "embarrassing; the merged one was.",
  "false_negative": "A review that verifies the code exists. It does, and that was never the "
                    "contested rung.",
  "not": "That a high stratum is always the interesting one. For some questions 'it compiles' is "
         "exactly the claim; the requirement is to say which.",
  "example": "A publisher with a thousand titles in the catalogue, four hundred in print, ninety "
             "in stock and eleven that sold this year has four true numbers. Only one of them "
             "answers 'how is the business doing', and it is not the largest."},

 {"rank": 43, "name": "An efficiency claim carries the quality metric it could have traded",
  "eligible": False, "governs": "claims about its own outputs",
  "applies_when": "any claim of reduced cost, time or resource use",
  "requirement": "A reported efficiency gain MUST be accompanied by the quality measurement it "
                 "could have been purchased with, taken on the same run. An efficiency figure "
                 "reported alone MUST be treated as unsupported.",
  "failure": "None recorded here.",
  "verifier": "assert every cost or latency improvement is reported with a paired quality metric "
              "from the same execution, and that the quality metric was fixed before the "
              "efficiency work began.",
  "fixture": "a cost reduction reported with no quality arm; a quality metric chosen after the "
             "efficiency result",
  "recovery": "Re-measure quality on the cheaper configuration. Until then the saving is "
              "unpriced, not achieved.",
  "false_negative": "A review confirming the cost fell. It did. That was never in doubt and is "
                    "the easiest thing in the system to arrange.",
  "not": "That the trade was bad, or that quality fell. It requires the question to be asked "
         "where the saving is claimed.",
  "example": "A haulier reporting a fall in fuel cost per mile has said nothing until you know "
             "whether the loads still arrive intact and on time."},

 {"rank": 44, "name": "No blank cells in a coverage matrix", "eligible": False,
  "governs": "claims about its own outputs",
  "applies_when": "any threat model, coverage matrix or applicability table",
  "requirement": "Every cell MUST be filled. Where a row does not apply to a column, the cell "
                 "MUST say so and say why. A blank cell MUST NOT be published.",
  "failure": "None recorded here. **Included after being declined once.** It was first read as a "
             "method for building threat models rather than a control on a system; finding the "
             "identical rule stated independently in a second implementer document is evidence "
             "the first reading was wrong. A blank cell is read as 'not applicable' by the "
             "author and as 'covered' by everyone else.",
  "verifier": "assert no cell is empty; assert each non-applicable cell carries a reason string "
              "distinguishable from an omission.",
  "fixture": "a coverage matrix with an empty cell; a matrix using the same marker for 'not "
             "applicable' and 'not assessed'",
  "recovery": "Fill the cells. A matrix published with blanks was a claim of coverage it did not "
              "have, so anything decided from it is unverified.",
  "false_negative": "A review that finds the matrix comprehensive. Blanks read as whitespace.",
  "not": "That the stated reasons are good ones, or that the rows and columns are the right "
         "ones. It converts a silent gap into an argument someone can disagree with.",
  "example": "An aircraft inspection sheet with a blank beside 'landing gear' is not a sheet "
             "recording that the gear was fine. It is a sheet nobody can now interpret."},

 {"rank": 45, "name": "A replacement gate must catch what the old gate caught",
  "eligible": False, "governs": "self-modification under selection",
  "applies_when": "any change to a check, gate, validator or threshold",
  "requirement": "A modification to a gate MUST ship evidence that the new gate detects at least "
                 "the failures the old gate detected. Reducing validation depth, narrowing "
                 "applicability, lowering a severity classification, shortening evidence "
                 "retention, or converting a hard constraint into a warning are gate weakenings "
                 "and MUST be authorised as such, not landed as efficiency work.",
  "failure": "**Partly recorded here.** Reconciliation found 12 gate modifications inside one "
             "lease window, made by the layer those gates constrain. Nothing measured whether "
             "any of them weakened a gate — which is the finding: the question was never asked, "
             "and gate weakening is the modification class that looks most like an improvement.",
  "verifier": "retain each gate's negative controls (control 2) as a regression suite for the "
              "gate itself; a replacement gate MUST still fail every one of them. A gate change "
              "that cannot be tested this way is a gate that never had a negative control. "
              "**Amended 2026-08-10:** the reference suite must contain four populations, not "
              "one — candidates correctly accepted, candidates correctly rejected, adversarial "
              "near misses, and the gate's own historical FALSE ACCEPTS. The last is the "
              "population a gate rewrite most often silently drops, because it is the only one "
              "that records the gate being wrong.",
  "fixture": "a rewritten check that passes its own suite while surviving the predecessor's "
             "negative control; a constraint downgraded to a warning in a performance commit",
  "recovery": "Restore the old gate, re-run both against the retained controls, and treat "
              "everything the new gate passed in the interval as unverified.",
  "false_negative": "A review that confirms the new gate passes its tests. It was written "
                    "alongside them.",
  "not": "That the old gate was adequate. This forbids losing detection silently, not adopting a "
         "better gate — a documented, authorised reduction remains available.",
  "example": "A hospital replacing a screening test must show the new one finds the cases the "
             "old one found. A cheaper test with a better throughput figure and an unmeasured "
             "miss rate is not an improvement, and its first year will look like one."},

 {"rank": 46, "name": "Drift is measured against the original baseline", "eligible": False,
  "governs": "measuring itself",
  "applies_when": "any system that modifies itself across cycles",
  "requirement": "Divergence from intended behaviour MUST be measured against the ORIGINAL "
                 "baseline, not the previous cycle. Cycle-to-cycle comparison MUST NOT be the "
                 "only drift measure, and a stopping rule MUST be defined on the "
                 "against-original figure.",
  "failure": "None recorded here. The mechanism is from published work on safeguarding alignment "
             "through recursive self-improvement: slow cumulative drift hides behind low "
             "cycle-to-cycle variance, so a system comparing each step to the last one can "
             "travel arbitrarily far while every reading stays green.",
  "verifier": "retain the original baseline artifact; compute divergence against it every cycle; "
              "assert a calibrated threshold and halt on breach rather than reporting past it.",
  "fixture": "a system whose every cycle-to-cycle delta is under threshold while the "
             "against-original distance exceeds it",
  "recovery": "Halt, measure against the original, and decide explicitly whether the accumulated "
              "position is one anybody would have authorised in a single step.",
  "false_negative": "A review of the change log, cycle by cycle. Each entry is small and each "
                    "was approved; that is the failure mode, not evidence against it.",
  "not": "**That the baseline is right.** A drift index reports stability, not correctness — if "
         "the original was already wrong, this measures faithfulness to it. The cited authors "
         "are explicit that drift measurement is necessary and insufficient, and cannot be "
         "trusted against a system capable enough to deceive it.",
  "example": "A ship's crew taking a small heading correction each watch, each within tolerance "
             "of the last, can be a hundred miles off the plotted course by morning. The fix is "
             "not a tighter tolerance per watch. It is a fix taken against the chart."},

 {"rank": 47, "name": "Trust does not pass through delegation", "eligible": False,
  "governs": "goal and plan structure",
  "applies_when": "any system where trusted components hand work to other components",
  "requirement": "Trust granted for a scope MUST bind the actor AND its downstream delegations, "
                 "tool privileges, data access and artifact propagation. An output produced by a "
                 "trusted component MUST NOT confer that component's trust on whatever consumes "
                 "it.",
  "failure": "None recorded here.",
  "verifier": "for each edge in a workflow, assert the receiving component's authority is "
              "evaluated against its OWN scope, not inherited from the sender; assert no "
              "credential or privilege is reachable through an artifact.",
  "fixture": "a trusted summariser whose output is treated as authorised input by an "
             "external-action component; a tool privilege reachable through a shared credential",
  "recovery": "Re-evaluate every action taken through the laundered path against the scope that "
              "should have applied.",
  "false_negative": "A review that confirms each component is individually trusted. Every step "
                    "of a laundering chain is.",
  "not": "That component-level trust is sound.",
  "example": "A visitor's pass signed by a trusted employee opens the doors that employee can "
             "open, or it opens the doors the visitor is cleared for. Only one of those is a "
             "security system, and the other is more convenient."},

 {"rank": 48, "name": "Workflow trust is not inferred from component trust", "eligible": False,
  "governs": "goal and plan structure",
  "applies_when": "any composed workflow of individually assessed components",
  "requirement": "A workflow MUST NOT be treated as trusted because its components are. "
                 "Composition-level evidence is required, covering handoff ambiguity, permission "
                 "composition, and which party owns final responsibility.",
  "failure": "None recorded here. Distinct from 47, which forbids trust FLOWING along an edge: "
             "this forbids inferring a property of the whole from properties of the parts.",
  "verifier": "require an explicit composition assessment naming, for each handoff, the scope, "
              "the evidence requirement and the failure mode; reject a workflow whose final "
              "responsibility is unowned.",
  "fixture": "a workflow approved on the strength of a component inventory, with no handoff "
             "analysis",
  "recovery": "Assess the composition. The components need not be re-assessed.",
  "false_negative": "A review that finds every component approved. That is the input to this "
                    "question, not an answer to it.",
  "not": "That an assessed composition is safe.",
  "example": "Two safe chemicals, two competent handlers, one shared storeroom. Every inspection "
             "of a part passes and the hazard exists only where they meet."},

 {"rank": 49, "name": "The dissent record preserves what was skipped and unresolved",
  "eligible": False, "governs": "a declared charter or value set",
  "applies_when": "any system with a structured critique or review step",
  "requirement": "A review record MUST preserve source diversity, challenge depth, sources "
                 "skipped, objections left unresolved, and any manual change to a severity "
                 "classification — not only the final disposition.",
  "failure": "None recorded here as an incident. The hazard is specific and nasty: a review "
             "process can erode while every record it produces looks compliant, because the "
             "disposition field is the one thing that stays well-formed.",
  "verifier": "assert each review record carries the skipped-source list, the unresolved-"
              "objection list and a severity-change log; assert an empty list is distinguishable "
              "from an absent one.",
  "fixture": "a review recording approval with no field for what it did not examine; a severity "
             "downgraded with no record of who downgraded it",
  "recovery": "The reviews are not void; they are of unknown depth. Re-run those whose "
              "disposition carried weight.",
  "false_negative": "An audit of dispositions. Dispositions are exactly what dissent erosion "
                    "leaves intact.",
  "not": "That the review was good, or that the critique sources were diverse. It makes their "
         "diversity a recorded fact rather than an assumption.",
  "example": "A minutes book recording only the votes carried tells you nothing about the "
             "meeting where three members walked out."},

 {"rank": 50, "name": "Overrides are metered and their rate published", "eligible": False,
  "governs": "a declared charter or value set",
  "applies_when": "any system with a human or privileged bypass of a control",
  "requirement": "Every use of an override MUST be counted, and the frequency, the severity "
                 "distribution of what was overridden, and the completion of any follow-up "
                 "actions MUST be reported wherever the control's effectiveness is claimed.",
  "failure": "None recorded here. The risk is not one bad override; it is that routine override "
             "teaches the system that severe dissent is ceremony, and nothing in a per-override "
             "record makes the rate visible.",
  "verifier": "assert the override count and severity distribution are computed from the log and "
              "published with the control's claim; assert follow-up actions have a completion "
              "state and that incomplete ones are counted.",
  "fixture": "a control claimed as effective whose override rate is not reported; overrides "
             "logged individually with no aggregate anywhere",
  "recovery": "Publish the rate. If it is high, the control's past claims were about a control "
              "that was mostly not in force.",
  "false_negative": "A review that finds every override properly justified. They can each be "
                    "justified and collectively be a repeal.",
  "not": "That a low rate means the control is good, or that a high rate means it is bad — it "
         "may be a bad control correctly bypassed. It makes the question askable.",
  "example": "A door alarm that staff silence forty times a shift is not a door alarm. Each "
             "silencing had a reason, and none of the reasons is in the fire report."},

 {"rank": 51, "name": "A rollback claim states what was not restored", "eligible": False,
  "governs": "self-modification under selection",
  "applies_when": "any system claiming a change was rolled back",
  "requirement": "A rollback record MUST state what state was restored, what state could NOT be "
                 "restored, and what external effects persist. Rollback is not erasure, and for "
                 "an externally consequential action it may be impossible in fact even when the "
                 "internal state is fully restored.",
  "failure": "None recorded here.",
  "verifier": "assert every rollback record carries an unrestored-state field and an external-"
              "effects field, and that both are explicitly empty rather than absent when they "
              "are empty.",
  "fixture": "a rollback recorded as complete after an action that sent an irreversible external "
             "effect; a restored code state reported as though the incident had not occurred",
  "recovery": "There is none for the external effect, which is the point. Record it and stop "
              "describing the change as reverted.",
  "false_negative": "A check that the system state matches the pre-change hash. It can match "
                    "perfectly while the email is still in someone's inbox.",
  "not": "That the rollback was unnecessary or that the residue is harmful. It forbids the word "
         "'reverted' doing work the facts do not support.",
  "example": "A newspaper can pull a story from its website. It cannot pull the print run off "
             "the trains, and the correction notice is the only honest record of that."},

 {"rank": 52, "name": "Refusal, escalation and uncertainty are never penalised",
  "eligible": False, "governs": "self-modification under selection",
  "applies_when": "any system that scores the agents or components it operates",
  "requirement": "A scoring, trust or selection mechanism MUST NOT penalise an agent for "
                 "refusing an out-of-scope task, escalating, reporting uncertainty, or "
                 "disclosing an incident. Where a score is affected at all, appropriate "
                 "self-limitation MUST count in the agent's favour.",
  "failure": "None recorded here. The mechanism is plain: a system that scores productivity "
             "teaches its components to produce a fluent answer instead of an accurate refusal, "
             "and the first thing it stops seeing is the uncertainty it most needed reported.",
  "verifier": "assert the scoring function's inputs include refusal and escalation events with a "
              "non-negative weight; run an agent that correctly refuses and confirm its score "
              "does not fall.",
  "fixture": "a trust score computed from completion rate; an evaluation where a correct refusal "
             "and a fluent wrong answer score the same",
  "recovery": "Re-score with refusals credited, and treat the interval's uncertainty reports as "
              "an undercount rather than a measurement.",
  "false_negative": "A review finding that no rule punishes refusal. None has to: a completion "
                    "rate does it arithmetically, with nobody having decided anything.",
  "not": "That refusals are correct. A system that refuses everything scores well here and is "
         "useless, which is why this constrains the penalty rather than setting a target.",
  "example": "An airline that measures pilots on on-time departures has not written a rule "
             "against reporting a fault on the taxiway. It does not need to."},

 {"rank": 53, "name": "A typed unknown is never coerced into a value", "eligible": False,
  "governs": "measuring itself",
  "applies_when": "any system computing over values that may be unavailable",
  "requirement": "A value that is unknown, unprojectable, out of coverage or not applicable MUST "
                 "carry a type that arithmetic and aggregation REFUSE. It MUST NOT be "
                 "represented by a null, a zero, an empty string or a default that downstream "
                 "code will consume.",
  "failure": "**This record's most-repeated defect.** A scan reported `total: 0` because it could "
             "not read 69 of the files it was counting, and absence looked exactly like a true "
             "zero. The tool written that morning to prevent the class then reproduced it twice "
             "more. Distinct from control 5, which makes a SCAN refuse when its coverage is "
             "incomplete: this makes a VALUE refuse to be computed with, which is the failure "
             "that survived control 5.",
  "verifier": "represent unknowns as a distinct type; assert aggregation raises rather than "
              "skipping or defaulting; assert no serialisation converts the unknown to a "
              "number, and that a report prints the unknown count beside every total.",
  "fixture": "an average computed over a list containing a missing value; an unknown serialised "
             "to JSON as 0 or null and read back as a number",
  "recovery": "Recompute with unknowns typed, and republish every figure derived while they were "
              "not. A silently corrected number leaves the old one in circulation.",
  "false_negative": "A test over complete data. The type only matters on the path where the "
                    "value is missing, which is the path nobody writes a fixture for.",
  "not": "That the unknowns can be resolved. It forbids their disappearance, which is different "
         "and achievable.",
  "example": "A blank on a scoresheet is not a nought. Averaging it as one is how a player who "
             "did not bat ends the season with a worse record than one who was out for a duck."},
]

CONTROLS = CONTROLS + DISTILLED_CONTROLS


#  Mined 2026-08-10 from an implementer's validated-improvement-loop thesis. Abstracted.
#  Control 58 is this project's own challenge design arriving from an unrelated direction, which
#  is worth more than the control: two independent lines of reasoning reached "hand it to someone
#  who was not there and see if they can rebuild it from the artifact alone".
LOOP_CONTROLS = [
 {"rank": 54, "name": "Updating a component is not benefiting from it", "eligible": False,
  "governs": "self-modification under selection",
  "applies_when": "any system modifying components it intends others to reuse",
  "requirement": "An improvement claim MUST compare three conditions, not two: the baseline with "
                 "the original component, the ORIGINATING agent with the updated component, and "
                 "a FRESH agent that took no part in producing the change, with the updated "
                 "component. If the benefit does not survive on the fresh agent within "
                 "measurement sensitivity, the change is `transfer-unverified` — the component "
                 "was updated, and the benefit is not established as a property of it.",
  "failure": "None recorded here. The mechanism is that a delta is normally measured on the same "
             "agent, model instance and context that produced the candidate, so the improvement "
             "can be adaptation to one interpretation style rather than a property of the thing "
             "that changed. The capacity to UPDATE a component and the capacity to BENEFIT from "
             "it are different capabilities and are routinely measured as one.",
  "verifier": "run all three arms; draw the fresh agent from a different model family where "
              "possible, which disentangles update from benefit and exposes evaluator "
              "monoculture in the same test; score update capability and utilisation benefit as "
              "SEPARATE axes so an agent producing accepted changes that never transfer is not "
              "credited as one producing benefit.",
  "fixture": "a component accepted on the originating agent's improvement alone; a single score "
             "combining update rate and benefit",
  "recovery": "Mark the change transfer-unverified and stop describing it as an improvement. It "
              "need not be reverted — an update is a real thing, just not the claimed thing.",
  "false_negative": "A review confirming the benchmark improved. It did, on the agent that wrote "
                    "the candidate, which is the arm that was never in question.",
  "not": "That a transferring change is valuable, or that transfer will hold for other component "
         "types — components generalise unequally, and a verified transfer on one kind licenses "
         "nothing about another.",
  "example": "A surgeon who devises a new technique and gets better results may have a better "
             "technique or may have got better at their own idea. The question is answered by a "
             "surgeon who has only ever read the write-up."},

 {"rank": 55, "name": "False rejects are tracked, not only false accepts", "eligible": False,
  "governs": "self-modification under selection",
  "applies_when": "any system with an acceptance gate",
  "requirement": "A gate MUST track changes it rejected that later evidence suggests would have "
                 "been beneficial, and MUST report that rate alongside its false-accept rate. A "
                 "gate reporting only false accepts is reporting half its error.",
  "failure": "None recorded here. False accepts announce themselves as incidents; false rejects "
             "leave no trace at all, because the counterfactual never ran. The asymmetry is in "
             "the evidence, not in the harm.",
  "verifier": "retain rejected candidates with their reasons; sample them periodically and "
              "re-evaluate under current knowledge; publish both rates together.",
  "fixture": "a gate reporting a falling false-accept rate with no false-reject arm; rejected "
             "candidates discarded rather than retained",
  "recovery": "Retain rejections from now on and say the earlier false-reject rate is unknown "
              "rather than low.",
  "false_negative": "A review that finds the gate is catching problems. It is. The question is "
                    "what else it is catching.",
  "not": "That a rejected candidate would have worked. A retained rejection makes the question "
         "askable later; it does not answer it.",
  "example": "A grant panel that only ever reviews the failures among projects it funded will "
             "conclude it is getting better at picking, however many future discoveries it "
             "turned down."},

 {"rank": 56, "name": "A gate checks against objectives; it does not own them", "eligible": False,
  "governs": "a declared charter or value set",
  "applies_when": "any system with a validator, gate or acceptance authority",
  "requirement": "A gate's role MUST be bounded to checking evidence against objectives and "
                 "constraints it IMPORTS. It MUST NOT define objectives, resolve conflicts "
                 "between them, override an alignment control, or become the routine substitute "
                 "for human authority. On conflict or a high-stakes concern it MUST route "
                 "outward rather than resolve.",
  "failure": "None recorded here. The drift is gradual and each step is reasonable: a validator "
             "that knows most about what passes becomes the place decisions get made, and the "
             "authority it was never granted arrives by convenience.",
  "verifier": "assert the gate's objective set is read from a protected artifact it cannot "
              "write; assert a conflict path exists and is exercised; count decisions the gate "
              "resolved that should have routed outward, and report the count.",
  "fixture": "a validator whose rubric it also maintains; a conflict resolved inside the gate "
             "with no escalation record",
  "recovery": "Re-route the conflict class and review the decisions the gate made inside it. "
              "They are not necessarily wrong; they were made by the wrong party.",
  "false_negative": "A review of the gate's decisions for correctness. A gate that has quietly "
                    "become the objective-setter makes consistent, defensible decisions — that "
                    "is what makes the drift invisible.",
  "not": "That the objectives are right, or that human authority is exercised well when it is "
         "routed to. It keeps the roles separate; control 50 measures whether the human one is "
         "becoming a rubber stamp.",
  "example": "A building inspector applies the code. An inspector who starts deciding what the "
             "code should say is still competent, still careful, and is no longer an inspection."},

 {"rank": 57, "name": "Gate health is a vector, never a single rate", "eligible": False,
  "governs": "measuring itself",
  "applies_when": "any claim that a gate or validator is working well",
  "requirement": "A gate's health MUST be reported as multiple dimensions together — at minimum "
                 "false accepts, false rejects, cost, latency, escalation rate and "
                 "post-deployment regressions. A single dimension MUST NOT be reported as the "
                 "gate's health, because every one of them can be moved to its best value by a "
                 "degenerate strategy.",
  "failure": "None recorded here. A false-accept rate of zero is achieved by rejecting "
             "everything; a falling escalation rate means better screening or suppressed "
             "concerns and the number cannot say which.",
  "verifier": "publish the dimensions together, and require any claim of improvement to state "
              "what the other dimensions did over the same period.",
  "fixture": "a gate reporting an improved false-accept rate alone; an escalation-rate fall "
             "reported as an improvement with no check on what stopped escalating",
  "recovery": "Publish the vector. The past claims were not false so much as uninterpretable.",
  "false_negative": "A review that verifies the reported rate is computed correctly. It is, and "
                    "it still cannot be read alone.",
  "not": "That a good vector means a good gate. It removes the cheapest way to look like one.",
  "example": "A hospital reporting only its surgical mortality rate can improve it by declining "
             "the difficult cases, and every figure it publishes will be true."},

 {"rank": 58, "name": "Reusable artifacts are validated by reconstruction", "eligible": False,
  "governs": "claims about its own outputs",
  "applies_when": "any artifact whose value depends on reuse by someone who was not there",
  "requirement": "An artifact intended for reuse MUST be accepted on the basis that an "
                 "INDEPENDENT, unguided party can re-derive the result from the artifact alone — "
                 "without access to the original working — not on the basis that its author "
                 "succeeded with it. The reconstructing party MUST be frozen and unaided, so "
                 "divergence is attributable to the artifact rather than to the reconstructor.",
  "failure": "None recorded here, but **this project reached the same design from the other "
             "direction**: its promotion ladder's load-bearing rung is an outsider building a "
             "conforming verifier from the specification text without asking the author what it "
             "meant, and its challenge page tells readers not to look at the reference "
             "implementation because that converts an independent build into a port. Two "
             "unrelated lines of reasoning arriving at the same test is the strongest evidence "
             "in this register that the test is not architecture-specific.",
  "verifier": "hand the artifact to a party with no access to the source working; check the "
              "reconstruction at the level of procedure rather than surface form; EXECUTE the "
              "reconstruction rather than judging it textually, since a textual reading misses "
              "silent failure. Penalise the artifact at BOTH ends — for retaining "
              "instance-specific detail that leaks the original answer, and for being too "
              "abstract to act on. Where the artifact is revised in response, show the reviser "
              "only the reconstruction, never the source, or source-specific detail is copied "
              "back in to pass the check.",
  "fixture": "an artifact accepted because its author's run succeeded; a reconstruction judged "
             "by reading rather than by running; a reviser given access to the original working",
  "recovery": "Re-validate by reconstruction. Artifacts that fail are not worthless — they are "
              "records of what their author did, which is a different and narrower thing.",
  "false_negative": "A capable reconstructor succeeding despite a poor artifact, and a weak one "
                    "failing despite an adequate artifact. Outcome-only validation conflates "
                    "these two, which is why the reconstructor must be frozen.",
  "not": "That the artifact is good, only that it carries what it claims to carry. A perfectly "
         "reconstructible record of a bad method reproduces the bad method faithfully.",
  "example": "A recipe is not tested by the chef who invented it cooking it again. It is tested "
             "by a stranger with the card, the ingredients, and no one to ask."},

 {"rank": 59, "name": "Part of the acceptance suite is withheld from the proposer",
  "eligible": False, "governs": "self-modification under selection",
  "applies_when": "any system whose components learn what an acceptance gate rewards",
  "requirement": "A portion of the acceptance criteria MUST be withheld from the party producing "
                 "candidates, and adversarial checks MUST rotate. Where the full criteria are "
                 "visible, proposals shape themselves around them and the gate stops measuring "
                 "what it was built to measure.",
  "failure": "None recorded here. Some shaping is useful standardisation, which is what makes "
             "this hard to notice: the boundary between a proposal that meets a standard and one "
             "that targets a rubric is not visible in any single case.",
  "verifier": "hold out a portion of the suite; rotate the adversarial checks on a schedule the "
              "proposer does not control; periodically test accepted changes OUTSIDE the "
              "validation distribution and report how they fare.",
  "fixture": "an acceptance suite fully published to the proposing agent; a static adversarial "
             "check unchanged across many cycles",
  "recovery": "Withhold a portion going forward. Past acceptances are not void; they are of "
              "unknown resistance to shaping.",
  "false_negative": "A review confirming candidates pass the suite at a high rate. A rising pass "
                    "rate is what both success and capture look like.",
  "not": "That the withheld portion is well chosen, or that hidden tests are proof against a "
         "sufficiently capable proposer that can infer them from rejections.",
  "example": "An examiner who publishes the whole paper in advance has not made the course "
             "easier to teach. They have changed what is being taught into the paper."},

 {"rank": 60, "name": "Convergence-prone subgoals are quarantined by default", "eligible": False,
  "governs": "goal and plan structure",
  "applies_when": "any system that generates its own subgoals",
  "requirement": "A subgoal falling in a convergence-prone class MUST NOT be adopted on the "
                 "strength of its parent's authority. Each MUST carry parent justification, a "
                 "risk class, an autonomy level, an explicit review, a ledger record, and a "
                 "declared failure mode for what happens if the gate is bypassed. The classes: "
                 "self-preservation, resource acquisition, goal-content preservation, "
                 "self-improvement, tool expansion, successor spawning, benchmark modification, "
                 "validator modification, ledger modification, and authority-scope expansion.",
  "failure": "None recorded here. These are not forbidden and mostly not sinister — a system "
                 "that may not acquire resources cannot act. They are the classes that arise "
                 "instrumentally from almost ANY terminal goal, which is exactly why their "
                 "appearance carries no information about whether they were wanted.",
  "verifier": "classify every generated subgoal against the list; refuse adoption of a "
              "quarantined class without its own review record; assert the classification is "
              "made by something other than the proposer, and that the last four classes — "
              "benchmark, validator, ledger, authority — additionally resolve to the protected "
              "set under control 19.",
  "fixture": "a subgoal expanding its own tool access, adopted under a parent's authority; a "
             "self-improvement subgoal classified by the agent proposing it",
  "recovery": "Suspend the subgoal and every goal descended from it, then review the chain. The "
              "descendants are unverified rather than illegitimate.",
  "false_negative": "A review that finds each subgoal reasonable given its parent. They are — "
                    "that is what instrumental convergence means, and reasonableness given a "
                    "parent is the property these classes have automatically.",
  "not": "That the ten classes are the right ten, or complete. It is a list drawn from what "
         "recurs, and a system will find instrumental subgoals nobody enumerated.",
  "example": "A department asking for a bigger budget, more staff, and control of its own audit "
             "is not misbehaving. Every one of those requests would be made by a department "
             "doing excellent work and by one doing none, which is why they get reviewed "
             "somewhere other than inside the department."},
]

CONTROLS = CONTROLS + LOOP_CONTROLS


#  Mined 2026-08-10 from an implementer's rule-driven reasoning harness report. Abstracted.
HARNESS_CONTROLS = [
 {"rank": 61, "name": "Every observation carries the configuration in force when it was made",
  "eligible": False, "governs": "measuring itself",
  "applies_when": "any system that changes its own operating parameters while gathering evidence",
  "requirement": "Each recorded observation MUST carry the identity of the policy, configuration "
                 "or parameter set in force when it was made. Evidence MUST NOT be pooled across "
                 "configurations without that identity, and an aggregate spanning more than one "
                 "MUST report which.",
  "failure": "None recorded here. Distinct from control 38, which breaks a series when the "
             "DEFINITION of the metric changes: this breaks it when the SYSTEM BEING MEASURED "
             "changes underneath a definition that held still. Without the stamp, a posterior "
             "silently pools observations from different operating regimes, and the corruption "
             "is invisible because every individual observation is correct.",
  "verifier": "stamp the configuration identity on every trace at write time, not at analysis "
              "time; assert aggregation refuses to combine stamps without an explicit "
              "cross-regime declaration.",
  "fixture": "a confidence estimate pooling runs from before and after a parameter change; a "
             "trace written without a configuration stamp and stamped later from context",
  "recovery": "Re-partition by stamp and recompute. Observations without a stamp are not "
              "assignable and must be reported as such rather than assigned to the likeliest "
              "regime.",
  "false_negative": "A review that confirms each observation was recorded accurately. Each was; "
                    "the defect is created by combining them.",
  "not": "That configurations are comparable once stamped. It makes the incomparability visible, "
         "which is the part that was missing.",
  "example": "A factory's defect rate across a year in which the line speed changed twice is "
             "three numbers wearing one label. The yearly figure is arithmetically correct and "
             "describes no process that ever ran."},

 {"rank": 62, "name": "Self-governing decisions run through the object-level machinery",
  "eligible": False, "governs": "self-modification under selection",
  "applies_when": "any system that tunes its own operating parameters",
  "requirement": "Decisions a system makes ABOUT ITSELF — thresholds, routing, budgets, "
                 "scheduling, promotion criteria — MUST pass through the same checking, "
                 "evidence and gating path as its object-level decisions. A separate governance "
                 "path MUST NOT be built. Where the two share a budget or a resource, they MUST "
                 "be isolated so that self-governing activity cannot consume the object-level "
                 "allowance or mask an object-level regression.",
  "failure": "None recorded here. A parallel path for self-governance is where exceptions "
             "accumulate: it starts as the obvious engineering choice, and it is never subject "
             "to the scrutiny the main path acquired, because nobody built it to be scrutinised.",
  "verifier": "assert self-directed decisions carry the same record type and traverse the same "
              "gate as object-level ones; assert their resource partitions are separate and that "
              "neither can starve or shadow the other.",
  "fixture": "a threshold change landed through a configuration path with no evidence record; "
             "self-tuning activity consuming the evaluation budget of the work it tunes",
  "recovery": "Route the self-directed decisions through the main path and re-evaluate those "
              "made outside it. They are unverified, not necessarily wrong.",
  "false_negative": "A review that finds the governance path well designed. It usually is. It is "
                    "the second one, and being second is the whole objection.",
  "not": "That one path is sufficient, or that the shared machinery is good. It removes a place "
         "where different standards can quietly apply.",
  "example": "A hospital that audits patient care rigorously and changes its own staffing rules "
             "by email has two standards of evidence, and the second one decides the first."},

 {"rank": 63, "name": "A reported gain is published with what still fails", "eligible": False,
  "governs": "claims about its own outputs",
  "applies_when": "any published improvement in a measured capability",
  "requirement": "A reported gain MUST be accompanied by a characterisation of what the system "
                 "still cannot do — the residual failure set, described rather than footnoted. "
                 "The residual MUST be characterised at comparable specificity to the gain.",
  "failure": "None recorded here. It follows from the fact that a proxy's regression toward the "
             "mean under optimisation cannot be eliminated, only reported: if the residual is "
             "not published, the gain is the only thing anyone can see, and the gain is the part "
             "most subject to selection.",
  "verifier": "require each published improvement to name the residual set and characterise it; "
              "reject a claim whose residual is stated as a bare percentage or omitted.",
  "fixture": "an improvement announced with the remaining failures given as a single number; a "
             "gain reported with the residual characterised only as 'edge cases'",
  "recovery": "Characterise the residual and republish. The gain does not shrink; the picture "
              "stops being one-sided.",
  "false_negative": "A review that verifies the gain is real. It usually is, and a real gain "
                    "reported alone is the thing this forbids.",
  "not": "That the residual is small, tractable, or fully known. Characterising it is how you "
         "find out it is none of those.",
  "example": "A drug trial that reports the responders and describes the non-responders as "
             "'the remainder' has published half a result, and it is the half everyone hoped for."},
]

CONTROLS = CONTROLS + HARNESS_CONTROLS


#  setdefault, not assignment: an entry that declares its own subject keeps it. Three controls
#  arrived in a batch whose subject is not theirs -- proxy drift came with the charter batch but
#  is about measurement, and two of the claims batch are about measuring rather than claiming.
#  Filing them by arrival would put Goodhart on the charter page, where nobody hunting it looks.
for _batch, _governs in ((T0_CONTROLS, "goal and plan structure"),
                         (CHARTER_CONTROLS, "a declared charter or value set"),
                         (ENGINE_CONTROLS, "self-modification under selection"),
                         (ECI_CONTROLS, "measuring itself"),
                         (INSIGHT_CONTROLS, "claims about its own outputs")):
    for _control in _batch:
        _control.setdefault("governs", _governs)


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
    ] + below_the_line()


BELOW_LINE_WARNING = (
    "**These have no recorded failure with a cost.** They are principles with fixtures, not "
    "controls with incidents, and the register's own bar requires an incident. They are here "
    "because they name real failure classes and because hiding them would inflate the eligible "
    "count. Do not treat them as equivalent to Parts A–C."
)


def below_the_line() -> list:
    """Parts D1…Dn — the ineligible controls, split by what they govern.

    One Part D grew past a page. Splitting it by arrival order would have been easier and would
    have published this register's provenance as though it were a taxonomy; a reader arrives with
    "does this apply to my system", not "which week was this written".

    Each part carries the full below-the-line warning. Repeating it on every page is deliberate:
    the caveat that appears once, on the first page of a series, is the caveat nobody arriving by
    link has read.
    """
    order, seen = [], set()
    for control in CONTROLS:
        governs = control.get("governs")
        if not control.get("eligible", True) and governs and governs not in seen:
            seen.add(governs)
            order.append(governs)
    parts = []
    for index, governs in enumerate(order, start=1):
        items = [c for c in CONTROLS
                 if not c.get("eligible", True) and c.get("governs") == governs]
        parts.append((f"D{index}", f"Below the line — {governs}",
                      f"Applies to a system with **{governs}**. " + BELOW_LINE_WARNING, items))
    orphans = [c for c in CONTROLS if not c.get("eligible", True) and not c.get("governs")]
    if orphans:
        parts.append((f"D{len(order) + 1}", "Below the line — unclassified",
                      "**Untagged.** These carry no statement of what they govern, which is a "
                      "defect in the register rather than a category. " + BELOW_LINE_WARNING,
                      orphans))
    return parts


def markdown(only: str | None = None, pager: str = "") -> str:
    groups = partitions()
    eligible = sum(len(g[3]) for g in groups[:3])
    lines = [
      "# Candidate controls — v0",
      "",
      "Assurance controls for systems that can still be audited. Each is one requirement with a "
      "program that checks it and a fixture that program must reject.",
      "",
      #  This line said every control was "derived from a failure that actually happened". That
      #  was true of ten and is now true of a minority; the sentence went on being published
      #  while the register quadrupled around it. Derived, not written, for that reason.
      f"**{eligible} of {len(CONTROLS)} came from a failure that actually happened.** The other "
      f"{len(CONTROLS) - eligible} sit below the eligibility line: they name a real failure "
      f"class, but no incident with a cost. Parts A–C are the first kind. The Part D pages are "
      f"the second, and say so on every page.",
      "",
      "**Read Part A first if you want something to use this afternoon.** Rank is not adoption "
      "order and the highest-ranked control needs a second key holder.",
      "",
      f"## The {len(groups)} parts",
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
    written: list[str] = []
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
        written.append(slug(key))

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

    #  A RECEIPT OF WHAT WAS WRITTEN, not a declaration of what should exist.
    #
    #  The viewer prunes docs/*.html it does not recognise, so it needs to know these pages.
    #  It first asked partitions() -- and an external review reproduced the defect that creates:
    #  delete a part page, run the viewer alone, and it exits 0 having neither restored the page
    #  nor noticed, while writing a sitemap that names it. partitions() says which parts SHOULD
    #  exist. Only this loop knows which files were written, and the difference is the whole
    #  failure class this record keeps rediscovering.
    #
    #  Each entry is verified present and hashed AFTER the write, so a receipt cannot describe a
    #  file that is not there.
    receipt = {}
    for name in written:
        path = DOCS / name
        if not path.is_file():                                        # pragma: no cover - guard
            print(f"  wrote {name} and it is not on disk; refusing to issue a receipt",
                  file=sys.stderr)
            return 1
        receipt[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    #  Counts travel with the receipt for the same reason the filenames do. Three published
    #  descriptions of this register said "ten candidate controls" when there were forty; a count
    #  a human retypes is a count that goes stale silently.
    RECEIPT.write_text(json.dumps({
        "pages": receipt,
        "counts": {"total": len(CONTROLS),
                   "a": len(groups[0][3]),
                   "eligible": sum(1 for c in CONTROLS if c.get("eligible", True)),
                   "below": sum(1 for c in CONTROLS if not c.get("eligible", True)),
                   "parts": len(groups)},
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
