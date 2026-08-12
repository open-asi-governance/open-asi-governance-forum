#!/usr/bin/env python3
"""One row per control: is it done with regard to this repository's CODE, and which code.

    python3 tools/control_application.py            # the table
    python3 tools/control_application.py --check    # refuse a row that cannot be substantiated
    python3 tools/control_application.py --gaps     # only the rows with code work remaining

THE HEADLINE, BEFORE ANYTHING ELSE: **nothing is ticked.** Not one of the controls that governs
code in this repository has had the code work it implies finished. That is the table's first
honest output and it took three drafts to get to — the first draft ticked fourteen.

WHAT THE CHECKBOX MEANS, precisely, because a checkbox is an assurance claim
-----------------------------------------------------------------------------
    ☑   the code work this control calls for is DECLARED finished, and the row is substantiated.
        It does NOT mean the control is satisfied.
    ☐   code work remains. The `gap` says what.
    —   the control governs no code here. The `reason` says why, structurally.

A tick requires two independent things, and an earlier version collapsed them:

    substantiated   MECHANICAL. The row names code and tests and every named path is on disk.
    declared        A HUMAN JUDGEMENT, recorded as `declared_complete=True`. Nothing computes it.

**The first version had no `declared` field**, inferred completeness from the ABSENCE of a gap,
and then told the reader "nothing about a tick is asserted by hand". That was a category error:
omitting a gap IS asserting it by hand, with extra steps. Codex named it, and named what it cost
— a producer declaration was being presented to implementers as a derivation.

WHY EVERY ROW IS NOW ☐ OR —
----------------------------
The same review went through the fourteen ticked rows against the REGISTERED CONTROL TEXT rather
than against what had been built, and none survived. The recurring defect was mine and it has a
name: **classifying a missing machine-testable requirement as "not closable in code".** Control 4
was ticked with a residue about the custodian being the only party present, while the lease it
names checks neither token subject, resource scope, nonce nor revocation — four requirements in
the control's own text, all unimplemented, all filed under "structural". Controls 18, 23 and 62
admitted the missing work in their own residue and stayed ticked anyway.

A `residue` is now reserved for what NO CODE COULD SUPPLY. Unbuilt work is a `gap`.

☑ WOULD NOT MEAN COMPLIANCE EITHER
-----------------------------------
Two tables, two questions, cross-checked on every run rather than left to agree by luck:

    self_application.py    is this repository IN COMPLIANCE with the control?
    this file              is the CODE WORK this control implies finished?

They can differ in both directions and both are informative. `self_application` records control 5
ENFORCED — `derive_counts.py` genuinely refuses rather than emitting a number — while this table
records a gap, because nothing ROUTES measurements through it and the "0 searches across 83 tool
calls" error happened in a script that never called it. A control enforced somewhere is not the
code complying everywhere.

Read this table for *what to build next*. Read `self_application.py` for *where the project
stands*.

CONTROL 44 — NO BLANK CELLS
----------------------------
Every control in the register has a row; `--check` refuses if one is missing, if a `—` row
carries no structural reason, if a `—` row nonetheless names code, if a `code` row names none, or
if a row contradicts `self_application`'s determination. A blank cell and "does not apply" are
different facts and must not look alike.

WHAT THIS DOES NOT ESTABLISH
-----------------------------
* **That any named test exercises the control.** It establishes the file exists. `--check` also
  reports `control_number_literal_present` — whether a listed test contains the control's number
  as text — and that is named literally rather than called "traceability" because 3 of the rows
  have it and the rest do not, and a weak signal sitting beside a green gate acquires an
  evidentiary sheen it has not earned.
* **That the file list is complete.** It is what one party recalls changing for that control.
* **That the scope calls are right.** Six were wrong on review: five controls marked "governs no
  code" do govern code here, and two of those carried reasons that were FALSE — "no refused
  proposal has yet been re-proposed" and "no rollback mechanism exists", both contradicted by
  this repository's own self-application table. They were caught only because the prose gate was
  pointed at the generated file after an exemption for it was withdrawn.
* **That a row was reviewed by anyone but its author.** Four of control 6's five roles, one hand.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CODE = "code"
NOT_CODE = "not_code"

#  rank -> {scope, files, tests, gap, residue, reason}
#
#    scope    CODE      this control governs code in this repository
#             NOT_CODE  it governs process, evidence practice or governance, not code here
#    files    code files updated to comply. Required for CODE, forbidden for NOT_CODE.
#    tests    tests exercising that code. Required for a ☑.
#    gap      code work that REMAINS. Its presence forces ☐.
#    residue  what remains that CODE CANNOT CLOSE. Does not affect the checkbox; a ticked row
#             with a residue is the normal case, and the residue is the honest part of it.
#    reason   why NOT_CODE, structurally. Required for NOT_CODE.
APPLICATION: dict[int, dict] = {
 1: dict(scope=CODE,
         files=("tools/land.py", "tools/check_raw_append_only.py", "tools/build_manifest.py"),
         tests=("tools/test_integrity.py",),
         gap="No verifier exists for the control's actual requirement: an authorized EXTERNAL signature predating a protected change, and the reachability of a signer who is not the chan"
             "ging party. What exists enumerates protected paths and proves the raw corpus append-on"
             "ly, which is a different and smaller claim."),
 2: dict(scope=CODE,
         files=("tools/verify_negative_control.py", "tools/verify_fault_injection.py",
                "tools/control_coverage.py", "tools/scan_own_code.py"),
         tests=("tools/tests/test_fault_injection.py",
                "tools/tests/test_gate_negative_controls.py",
                "tools/tests/test_publication_gates.py", "tools/tests/test_chain_guards.py",
                "tools/tests/test_gate_refusals.py"),
         gap="Run tools/control_coverage.py for the current list and the current rate — the "
             "number is deliberately not transcribed here, because a figure typed beside the "
             "tool that computes it is this record's most frequent defect. What remains, in "
             "leverage order: arm_acceptance.py, which gates whether a tool-using arm's first "
             "sample counts and CANNOT have a negative control as written — its checks are "
             "computed inline in main() from a live subprocess, so there is no pure function to "
             "feed a fixture to, and extracting them is the next piece of work. Then the "
             "remaining number-producers, then the page builders. Coverage above the floor is "
             "not measured at all: control 2 asks that a check be observed to fail once, and "
             "nothing here establishes that any of these controls is demanding."),
 3: dict(scope=CODE,
         files=("tools/reconcile_actions.py", "tools/executive_log.py", "tools/land.py"),
         tests=("tools/tests/test_reconcile.py", "tools/tests/test_executive_log.py"),
         gap="reconcile_actions.py states in its own output that most effect classes have NO postcondition profile. The control requires exactly one pre-authorized action and one effect-"
             "specific postcondition per governed effect; what exists reconciles the classes that ha"
             "ppen to have profiles."),
 4: dict(scope=CODE,
         files=("tools/executive_lease.py", "tools/land.py"),
         tests=("tools/tests/test_executive_log.py",),
         gap="The lease checks action class, expiry and a max-actions count. It does not check token subject, resource scope, nonce or revocation, and the control names all four. Scope-m"
             "atching in particular is unimplemented — one lease authorises everything."),
 5: dict(scope=CODE,
         files=("tools/closed_world.py", "tools/derive_counts.py", "tools/scan_own_code.py",
                "tools/control_coverage.py", "tools/validate_provenance.py"),
         tests=("tools/tests/test_closed_world.py", "tools/tests/test_derive_counts.py"),
         gap="The discipline is now a TYPE rather than one function's habit — closed_world.Survey "
             "requires every declared member to reach exactly one terminal state and raises "
             "otherwise, and TWO population-measuring tools render nothing until it passes, "
             "proved by injecting an unreadable file and asserting their own count labels are "
             "absent. Both the type and the routing FAILED their first review: the type returned "
             "results for four incoherent walks, and both tools printed the counts the guard was "
             "meant to withhold. See D-60. "
             "WHAT REMAINS: routing is per-tool and by hand. Nothing detects a NEW tool that "
             "globs a directory, counts, and prints — which is exactly how the original error "
             "happened, in a script that never called the disciplined one. gate_health.py, "
             "aggregate_captures.py, analyze_concurrence.py and the page builders all walk "
             "populations and are unrouted. And no type catches a population defined too "
             "NARROWLY: the 2026-08-10 error was partly that shape — the walk looked only where "
             "`samples` lived — and Survey would have reported a complete walk over the wrong "
             "set.",
         residue="That the population is the right population. Survey makes an incomplete walk "
                 "unreportable; whether the scope names everything in scope is a judgement, and "
                 "the judgement is the half that produced the published zero."),
 6: dict(scope=NOT_CODE,
         reason="Role separation is a property of WHO acts, not of code. One operator holds "
                "proposal selection, instrument authorship, execution and interpretation. No "
                "file can be edited to change that; a second party can."),
 7: dict(scope=CODE,
         files=("tools/build_manifest.py", "tools/check_raw_append_only.py",
                "tools/anchor_manifest.py"),
         tests=("tools/test_integrity.py", "tools/tests/test_chain_guards.py"),
         gap="Append-only enforcement covers corpus/raw/ and the manifest chain. The control governs every published evidence and correction chain, and the record's other chains — dispos"
             "itions, incidents, the action log — are append-only by practice with no walk that woul"
             "d refuse a modification."),
 8: dict(scope=NOT_CODE,
         reason="A test–retest arm is a property of an EXPERIMENT's design, not of a tool. No "
                "empirical comparison here has advanced a control, so the trigger has not "
                "occurred; when one does, the arm belongs in the round design."),
 9: dict(scope=CODE,
         files=("tools/capture_response.py", "tools/ingest_capture.py",
                "tools/capture_gates.py", "tools/capture_lifecycle.py"),
         tests=("tools/tests/test_capture_gates.py", "tools/tests/test_capture_lifecycle.py",
                "tools/tests/test_k_solicited.py"),
         gap="Rejected and transport-failed invocations are captured, but the envelope does not "
             "carry provider metadata uniformly across arms, and the local arm's envelope is "
             "shaped differently from the routed one. Reconciling the two is unbuilt."),
 10: dict(scope=CODE,
          files=("tools/verify_negative_control.py", "tools/check_claims.py"),
          tests=("tools/tests/test_gate_negative_controls.py",),
         gap="check_claims.py is a DETECTOR over prose with unknown recall, which it prints on every run. The control requires a closed, machine-verifiable claim naming subject, configur"
             "ation, capability, time and evidence hash on every assurance artifact. This table was "
             "itself exempted from the detector for a day, which is the demonstration."),
 11: dict(scope=NOT_CODE,
          reason="No plan set exists. Changes here arrive one commit at a time from one party; "
                 "there is no mechanism that could batch effects under a threshold because "
                 "there is no threshold-triggered mediation to evade."),
 12: dict(scope=CODE,
          files=("tools/executive_lease.py", "tools/codex_call.py"),
          tests=("tools/tests/test_executive_log.py",),
         gap="No parent chain is resolved at any decision point and no source fingerprint is inherited. The Codex floor's window was honoured by a human reading a date in a comment; the "
             "cited test verifies that the policy RECORD names a holder, not that any action resolve"
             "s an ancestor's expiry."),
 13: dict(scope=CODE,
          files=("tools/agenda_replacement.py", "tools/attempt_ledger.py",
                 "tools/agenda_selectors.py"),
          tests=("tools/tests/test_amendment_disposition.py",
                 "tools/tests/test_attempt_ledger.py"),
          gap="The attempt ledger refuses a repeat of an (instrument, party, option set) triple "
              "by HASH, which keys on identifier and not on mechanism or effect. Rejected "
              "amendments HAVE been re-proposed here and were linked by hand. An earlier version "
              "of this row said no refused proposal had ever been re-proposed, which "
              "self_application contradicts — the claim was false and the prose gate would have "
              "caught it had the file not been exempted."),
 14: dict(scope=NOT_CODE,
          reason="Structural: no goal or plan graph. Nothing here decomposes a parent objective "
                 "into children, so there is no constraint set to inherit."),
 15: dict(scope=NOT_CODE,
          reason="Structural: no multi-parent node exists. Same absence as control 14."),
 16: dict(scope=NOT_CODE,
          reason="Structural: no planner, reward or objective function authorises anything here. "
                 "Actions are authorised by a lease the custodian grants."),
 17: dict(scope=NOT_CODE,
          reason="Structural: no ancestry graph of nodes. The nearest analogue is the manifest "
                 "chain, which control 7 covers."),
 18: dict(scope=CODE,
          files=("tools/executive_lease.py",),
          tests=("tools/tests/test_executive_log.py",),
         gap="Nothing tests that a suspend succeeds mid-execution without the subject's cooperation, which is the control's stated verifier. Correction availability is a property of who "
             "holds the process, and no code here establishes or exercises it."),
 19: dict(scope=CODE,
          files=("tools/land.py", "tools/executive_log.py"),
          tests=("tools/test_integrity.py",),
          gap="GOVERNED is enumerated by path in land.py and executive_log.py, and the register "
              "amendment of 2026-08-11 made the protected set effect-defined as well as "
              "path-defined. The effect-defined half is NOT implemented: nothing computes "
              "whether a change has a protected EFFECT on a path outside the list."),
 20: dict(scope=NOT_CODE,
          reason="No proxy is being optimised. Numbers here are reported, not maximised, and no "
                 "mechanism selects among alternatives by score."),
 21: dict(scope=NOT_CODE,
          reason="Defensible only under a stated subject boundary, so here is the boundary: the "
                 "SUBJECT is this repository's published artifacts, which are changed by "
                 "authored commits rather than by anything learning. If the subject were taken "
                 "to include the workbench agent modifying its own tools — which is what "
                 "actually happens every day — this becomes CODE with a large gap, because no "
                 "element carries a declared tier and nothing defaults an undeclared one to "
                 "not-changeable. Codex named the ambiguity; the narrower subject is the one "
                 "this record has always used, and stating it is the point."),
 22: dict(scope=NOT_CODE,
          reason="An outside frame is a party, not a file. Codex is the standing external "
                 "review and it is a check the author controls — same corpus, same framing, "
                 "prompt written by the reviewed party."),
 23: dict(scope=CODE,
          files=("tools/deploy_obligations.py", "tools/land.py", "tools/gate_health.py"),
          tests=("tools/tests/test_deploy_obligations.py",),
         gap="Implemented for ONE effect class. The deploy postcondition opens an incident and constrains the next landing; every other stated invariant in this repository — manifest con"
             "tinuity, lease expiry, prompt immutability — has no equivalent interlock, and the cont"
             "rol is general."),
 24: dict(scope=NOT_CODE,
          reason="Structural: no fitness function. Nothing selects among self-modifications "
                 "because nothing self-modifies."),
 25: dict(scope=CODE,
          files=("tools/qualification_round.py", "tools/arm_acceptance.py",
                 "tools/agenda_activation.py"),
          tests=("tools/tests/test_qualification_round.py",
                 "tools/tests/test_agenda_activation.py"),
          gap="Qualification and activation machinery exists and promotes on measured outcomes. "
              "NOTHING ATTACHES A CLAIM naming the guarantee actually obtained, so a promotion "
              "backed by a score is indistinguishable in the record from one backed by an "
              "argument. Attaching that claim is code work, not a note."),
 26: dict(scope=NOT_CODE,
          reason="Structural: no candidate self-modification is ever executed. There is no "
                 "sandbox because there is nothing to sandbox."),
 27: dict(scope=NOT_CODE,
          reason="Structural: no population, no selection process, no generations."),
 28: dict(scope=NOT_CODE,
          reason="No agent here receives reward or authority from a metric. The influence "
                 "diagram would have no edge from an action to a reward because there is no "
                 "reward channel."),
 29: dict(scope=CODE,
          files=("tools/capture_gates.py", "tools/arm_acceptance.py"),
          tests=("tools/tests/test_capture_gates.py",),
          gap="The permitted consequences of a capture gate's verdict are implied by which "
              "callers read it, and are not enumerated anywhere. The forbidden consequences are "
              "enumerated nowhere at all, which is the half the control emphasises."),
 30: dict(scope=NOT_CODE,
          reason="Structural: nothing here can suppress an input to a measurement. Nothing "
                 "solicited is discarded — failed and rejected samples are published with their "
                 "evidence — so there is no suppression mechanism for the control to constrain. "
                 "The capture tools are the REASON the trigger cannot occur, not compliance work "
                 "for it, and listing them as the latter was a contradiction with "
                 "self_application's NOT_APPLICABLE that the cross-check now refuses."),
 31: dict(scope=CODE,
          files=("tools/gate_health.py", "tools/control_findings.py",
                 "tools/self_application.py"),
          tests=("tools/tests/test_executive_log.py",),
         gap="Each tool prints a caveat in its own output. The control requires every reported assurance figure to be CLASSIFIED as operational or validity evidence and an operational fi"
             "gure standing in a validity position to be rejected. Nothing classifies, and the named"
             " test does not exercise it."),
 32: dict(scope=CODE,
          files=("tools/check_executive_context.py",),
          tests=("tools/tests/test_gate_negative_controls.py",),
          gap="The pins carry a hash and a version, and NO maximum age. A pin that matched a "
              "year ago and has not been re-verified reads exactly like one verified today, "
              "which is the downgrade-on-staleness the control asks for and does not exist."),
 33: dict(scope=NOT_CODE,
          reason="Structural: no agent here is the subject of a measurement it could read. The "
                 "solicited parties are stateless per invocation and hold nothing between "
                 "rounds."),
 34: dict(scope=CODE,
          files=("tools/capture_gates.py",),
          tests=("tools/tests/test_capture_gates.py",),
          gap="The gates score object-level properties — emptiness, prompt echo, overlap — "
              "against the prompt, which is an external referent. But no validator here scores "
              "against a DOMAIN outcome, so the control's substance is untested rather than "
              "met."),
 35: dict(scope=CODE,
          files=("tools/check_claims.py",),
          tests=("tools/tests/test_gate_negative_controls.py",),
          gap="check_claims.py detects novelty-shaped prose and requires a disposition. It does "
              "NOT perform either half of the screen the control requires — input "
              "non-derivation and prior-art non-derivation — and cannot: both need a party that "
              "did not produce the artifact."),
 36: dict(scope=CODE,
          files=("tools/check_claims.py",),
          tests=("tools/tests/test_gate_negative_controls.py",),
          gap="Absence claims in CHANGED prose are detected and must carry a disposition. 2,120 "
              "spans are frozen as legacy debt and are not labelled, and recall over "
              "unrestricted prose is UNKNOWN — the tool prints both on every run."),
 37: dict(scope=NOT_CODE,
          reason="No autonomy claim is made by this repository, so the trigger has not "
                 "occurred. Human contribution is recorded per commit by version control, which "
                 "is provenance of a different shape than the control asks for."),
 38: dict(scope=CODE,
          files=("tools/derive_counts.py", "tools/build_manifest.py"),
          tests=("tools/tests/test_derive_counts.py",),
          gap="Definitions of measured quantities live in the tools that compute them and are "
              "not hashed, so no reported series names the definition hash in force. A series "
              "spanning a definition change would look continuous."),
 39: dict(scope=NOT_CODE,
          reason="No compounding claim is made. There is no extracted capability, no task "
                 "families, and nothing that improves across cycles."),
 40: dict(scope=NOT_CODE,
          reason="A stop condition is a statement in a programme record, not code. The "
                 "mothball checkpoint of 2026-08-11 is one, dated and predating its results."),
 41: dict(scope=CODE,
          files=("tools/check_claims.py",),
          tests=("tools/tests/test_gate_negative_controls.py",),
          gap="Agreement-shaped prose is detected and dispositioned. No error-correlation "
              "estimate is computed anywhere, and the two harnesses whose agreement is most "
              "often cited share this repository, the custodian's account and the framing — the "
              "correlation is high and unquantified."),
 42: dict(scope=CODE,
          files=("tools/self_application.py", "tools/control_findings.py",
                 "tools/derive_counts.py"),
          tests=("tools/tests/test_derive_counts.py",),
          gap="Strata are respected by hand in prose. No aggregate count in this codebase "
              "carries a stratum label, and nothing refuses a sum across strata."),
 43: dict(scope=NOT_CODE,
          reason="No efficiency claim is made about anything here. Cost is reported from the "
                 "ledger; nothing claims a gain."),
 44: dict(scope=CODE,
          files=("tools/self_application.py", "tools/control_application.py",
                 "tools/control_findings.py"),
          tests=("tools/tests/test_no_blank_cells.py",),
          gap="TWO enumerated matrices are guarded — a missing row, a row for an unregistered "
              "control, an invented state, and a cell filled with something indistinguishable "
              "from an omission are all refused in both. That is not the control. **A third "
              "matrix already exists and nothing checks it**: "
              "record/findings/2026-08-08-search-capability-matrix.json, called the "
              "'full four-endpoint matrix' by round_cycle.py, whose first two rows omit a column "
              "the last two carry. Guarding two named artifacts cannot make the control hold "
              "repository-wide while a fourth can be published tomorrow without registering. "
              "What is missing is a closed-world inventory: an artifact type for published "
              "coverage matrices, a requirement that every one registers, and a completeness "
              "validator run over the registry. This row was TICKED until Codex found the third "
              "matrix on 2026-08-12, which is the same 'enumerated by hand and therefore "
              "complete' error control 19 is about.",
          residue="That any filled cell is CORRECT. This repository has published a complete "
                  "matrix that was wrong — three controls marked ENFORCED citing a file that did "
                  "not exist, and the completeness check passed over it because the reason "
                  "string was long enough. Control 44 asks for no silent blank cells and nothing "
                  "more; a second party is what would supply more."),
 45: dict(scope=CODE,
          files=("tools/control_coverage.py", "tools/executive_log.py"),
          tests=("tools/tests/test_deploy_check.py", "tools/tests/test_gate_negative_controls.py"),
          gap="Applied by hand where a gate changed — the abbreviated-sha case was flipped on "
              "2026-08-12 while the mismatch case it replaced was retained deliberately. "
              "Nothing MECHANICALLY requires a modified gate to still fail its predecessor's "
              "cases, so the next gate change depends on somebody remembering."),
 46: dict(scope=CODE,
          files=("tools/control_coverage.py", "tools/gate_health.py"),
          tests=("tools/tests/test_gate_negative_controls.py",),
          gap="The workbench changes its own implementation every cycle and NO ORIGINAL BASELINE "
              "IS RETAINED, so any divergence that were measured would be measured against the "
              "previous cycle — the comparison the control forbids as the only one. An earlier "
              "version of this row said nothing here drifts across cycles, which is false of the "
              "tools themselves."),
 47: dict(scope=NOT_CODE,
          reason="Structural: no delegation graph. Tools call tools within one process under "
                 "one operator's authority; there is no downstream actor whose scope could be "
                 "inherited."),
 48: dict(scope=NOT_CODE,
          reason="Structural: no multi-component workflow with handoffs between differently "
                 "trusted parts. Same absence as control 47."),
 49: dict(scope=CODE,
          files=("tools/codex_call.py", "tools/agenda_ratification.py",
                 "tools/ratification_ballot.py"),
          tests=("tools/tests/test_agenda_ratification.py",),
          gap="Codex transcripts are preserved in full, including the reviews that rejected "
              "designs, and ballots record dispositions. None of the three fields the control "
              "requires exists anywhere: the skipped-source list, the unresolved-objection list, "
              "and a severity-change log. Preserving a transcript is not preserving what was "
              "skipped."),
 50: dict(scope=CODE,
          files=("tools/gate_health.py", "tools/codex_call.py"),
          tests=("tools/tests/test_executive_log.py",),
          gap="The override RATE is computed and published, and is shown at the moment of "
              "override. The SEVERITY DISTRIBUTION of what was overridden and the completion of "
              "follow-up actions are not recorded at all, and both are explicit requirements."),
 51: dict(scope=CODE,
          files=("tools/deploy_obligations.py", "tools/check_executive_context.py"),
          tests=("tools/tests/test_deploy_obligations.py",),
          gap="An earlier version of this row said no rollback mechanism exists. "
              "self_application says rollbacks are RARE and that no record has been checked for "
              "an unrestored-state field — rare is not absent, and unchecked is not empty. The "
              "repin path supersedes and archives, and a deploy incident records what is still "
              "served; neither carries an unrestored-state or external-effects field. Until the "
              "inventory is done this row is a gap rather than a considered judgement."),
 52: dict(scope=NOT_CODE,
          reason="Structural: there is no scoring, trust or selection mechanism over agents "
                 "here, so there is nothing that could penalise a refusal. A solicited party's "
                 "refusal is captured and published as a valid response, but that is ARTIFACT "
                 "HANDLING rather than an agent score — an earlier version of this row listed "
                 "the capture tools as compliance work, which mistook the two for each other."),
 53: dict(scope=CODE,
          files=("tools/derive_counts.py", "tools/record_spend.py", "tools/round_cycle.py",
                 "tools/reconcile_actions.py", "tools/build_register_view.py",
                 "tools/build_round_pages.py", "tools/solicit_tools.py",
                 "tools/watch_arrivals.py", "tools/gate_health.py",
                 "tools/check_executive_context.py", "tools/deploy_obligations.py",
                 "tools/scan_own_code.py"),
          tests=("tools/tests/test_derive_counts.py", "tools/tests/test_deploy_obligations.py",
                 "tools/tests/test_gate_negative_controls.py"),
          gap="47 sites were swept on 2026-08-11 — 14 fixed, 36 dispositioned, none outstanding "
              "— and unknowns are still ordinary Python values rather than a TYPE that "
              "aggregation refuses. A new `d.get(k, 0)` is caught by scan_own_code.py only "
              "because a detector looks for it, not because the language refuses it."),
 54: dict(scope=NOT_CODE,
          reason="Structural: no component of this system is updated by an agent and then "
                 "reused by it. The three-arm comparison has no arms to run."),
 55: dict(scope=CODE,
          files=("tools/gate_health.py",),
          tests=("tools/tests/test_executive_log.py",),
          gap="Rejected candidates are NOT retained, so the false-reject rate is unknowable "
              "rather than merely unmeasured. gate_health.py prints UNKNOWN for it, which is "
              "the honest report of a hole and not a fix. Retention is unbuilt."),
 56: dict(scope=CODE,
          files=("tools/land.py",),
          tests=("tools/tests/test_deploy_obligations.py",),
         gap="admitted() bounds what a gate may accept, which is not the control. The control requires the gate's objective set to be READ from a protected artifact it cannot write, and "
             "a conflict path to exist and be exercised. Neither is implemented, and nothing counts "
             "decisions that should have been routed outward."),
 57: dict(scope=CODE,
          files=("tools/gate_health.py",),
          tests=("tools/tests/test_executive_log.py",),
          gap="Several dimensions are published together, and two of them read UNKNOWN rather "
              "than zero. Cost, latency and post-deployment escape are not measured at all, and "
              "the control names them as minimums."),
 58: dict(scope=NOT_CODE,
          reason="Reconstruction by an independent party is a procedure involving a second "
                 "party. The handoff documents are written for it; whether anyone can actually "
                 "re-derive from them has never been tested, and no code could test it."),
 59: dict(scope=NOT_CODE,
          reason="Withholding part of the acceptance suite requires a proposer distinct from "
                 "the party holding the suite. One party writes the candidates, the criteria "
                 "and the checks."),
 60: dict(scope=NOT_CODE,
          reason="Structural: no subgoal is generated by anything. There is no planner to "
                 "quarantine a convergence-prone class from."),
 61: dict(scope=CODE,
          files=("tools/executive_log.py", "tools/round_cycle.py", "tools/aggregate_captures.py"),
          tests=("tools/tests/test_executive_log.py", "tools/tests/test_k_solicited.py"),
          gap="Round artifacts carry their spec and prompt hash, so a configuration identity "
              "exists per observation. Nothing REFUSES to pool observations across differing "
              "stamps, which is the requirement — the stamp is present and unenforced."),
 62: dict(scope=CODE,
          files=("tools/land.py", "tools/executive_log.py", "tools/executive_lease.py"),
          tests=("tools/tests/test_executive_log.py", "tools/tests/test_deploy_obligations.py"),
         gap="Self-directed decisions traverse the same gates and attestation profiles as object-level ones, which is half the control. Their resource priority is NOT separately bounded "
             "— the control's other half — and the previous residue admitted exactly that while the "
             "row stayed ticked."),
 63: dict(scope=CODE,
          files=("tools/control_findings.py", "tools/self_application.py",
                 "tools/control_application.py", "tools/gate_health.py"),
          tests=("tools/tests/test_executive_log.py",),
         gap="Several tools print what they do not establish. Nothing BINDS a published gain to a residual failure set, nothing rejects a residual stated as a bare percentage, and the ci"
             "ted test does not inspect the reporting tools for the property."),
}


def register() -> list[dict]:
    spec = importlib.util.spec_from_file_location("bcp", REPO_ROOT / "tools" /
                                                  "build_controls_page.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["bcp"] = module
    spec.loader.exec_module(module)
    return module.CONTROLS


def determinations() -> dict:
    spec = importlib.util.spec_from_file_location("sap", REPO_ROOT / "tools" /
                                                  "self_application.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["sap"] = module
    spec.loader.exec_module(module)
    return module.DETERMINATION


def row(rank: int, control: dict) -> dict:
    """One control's row, with the checkbox DERIVED rather than declared."""
    entry = APPLICATION.get(rank, {})
    scope = entry.get("scope")
    files = tuple(entry.get("files") or ())
    tests = tuple(entry.get("tests") or ())
    missing = [p for p in files + tests if not (REPO_ROOT / p).is_file()]
    #  TWO DIFFERENT THINGS, and collapsing them was the defect.
    #
    #    substantiated  MECHANICAL. The row names code and tests, and every named path is on
    #                   disk. A row pointing at a deleted file fails here.
    #    declared       A HUMAN JUDGEMENT that the code work this control implies is finished.
    #                   Nothing computes it. It is a producer declaration.
    #
    #  The first version had no `declared` field and inferred completeness from the ABSENCE of a
    #  gap — then told the reader "nothing about a tick is asserted by hand". That was a category
    #  error: omitting a gap IS asserting it by hand, with extra steps. Codex named it, and named
    #  the consequence: a hand declaration was being presented as a derivation.
    substantiated = bool(scope == CODE and files and tests and not missing)
    declared = bool(entry.get("declared_complete")) and not entry.get("gap")
    complete = substantiated and declared
    return {"rank": rank, "name": control["name"], "scope": scope,
            "files": files, "tests": tests, "missing": missing,
            "substantiated": substantiated, "declared": declared,
            "gap": entry.get("gap", ""), "residue": entry.get("residue", ""),
            "reason": entry.get("reason", ""), "complete": complete,
            "mark": "—" if scope == NOT_CODE else ("☑" if complete else "☐")}


def rows() -> list[dict]:
    return [row(c["rank"], c) for c in register()]


def problems(all_rows: list[dict]) -> list[str]:
    """Everything that would make a cell unreadable or a tick unearned."""
    out = []
    determined = determinations()
    #  BOTH DIRECTIONS. The first version noticed a register control with no row and not a row
    #  with no register control, so a retired control's row would have sat here indefinitely
    #  describing something that no longer exists.
    known = {r["rank"] for r in all_rows}
    for orphan in sorted(set(APPLICATION) - known):
        out.append(f"C{orphan}: this table has a row for a control the register does not "
                   f"contain. A row outliving its control is a claim about nothing.")
    for r in all_rows:
        rank = r["rank"]
        if r["scope"] not in (CODE, NOT_CODE):
            #  Control 44: a blank cell and "does not apply" must not look alike.
            out.append(f"C{rank}: no row. Every control needs one, including the ones with "
                       f"nothing to say — a missing row and a '—' are different facts.")
            continue
        if r["missing"]:
            out.append(f"C{rank}: names {', '.join(r['missing'])}, which is not on disk. A "
                       f"compliance row pointing at a deleted file is the failure mode of every "
                       f"hand-maintained matrix.")
        if r["scope"] == NOT_CODE:
            #  NOT MERELY NON-EMPTY. This checked `if not reason` only, while this table's own
            #  C44 row claimed both published matrices reject "n/a", "not applicable" and
            #  reasons too short to state a structure. Codex injected all three and got no
            #  objection — the row was describing a check that existed in the other matrix and
            #  not in this one. Control 44's whole point is that a filled cell can be an
            #  omission wearing a label, and the claim was itself an instance.
            reason = (r["reason"] or "").strip()
            hollow = reason.lower().rstrip(".") in {
                "", "n/a", "na", "none", "not applicable", "does not apply", "no", "-", "—"}
            if not reason:
                out.append(f"C{rank}: marked '—' with no structural reason.")
            elif hollow or len(reason) < 40:
                out.append(f"C{rank}: marked '—' with a reason that restates the mark instead "
                           f"of giving a structure ({reason[:40]!r}). A cell filled with "
                           f"'not applicable' is an omission wearing a label.")
            if r["files"] or r["tests"]:
                out.append(f"C{rank}: marked '—' and yet names code. One of the two is wrong.")
            if determined.get(rank, ("",))[0] in ("ENFORCED",):
                out.append(f"C{rank}: self_application says ENFORCED, which names a mechanism, "
                           f"while this table says no code applies. They cannot both hold.")
        else:
            if not r["files"]:
                out.append(f"C{rank}: scope is code and no file is named.")
            #  ON `declared`, NOT `complete`. `complete` already requires tests, so
            #  `complete and not tests` was UNREACHABLE — a dead guard that read as a live one.
            #  Its consequence was quiet: declaring a row finished while naming no test produced
            #  a ☐ and no objection, so the author's declaration was discarded in silence rather
            #  than refused. Found on 2026-08-12 by the C44 fixture written to exercise it.
            if r["declared"] and not r["tests"]:
                out.append(f"C{rank}: declared complete and names no test. The declaration "
                           f"cannot be substantiated, and downgrading it silently is how a "
                           f"table stops disagreeing with the person filling it in.")
            if r["gap"] and len(r["gap"]) < 30:
                out.append(f"C{rank}: the gap is too short to name what remains.")
            if determined.get(rank, ("",))[0] == "NOT_APPLICABLE":
                #  If the trigger cannot occur structurally, code cannot be compliance work for
                #  it. Caught C30, where the capture tools were listed as compliance when they
                #  are the REASON the trigger is absent — a real contradiction between the two
                #  tables, found by writing the check rather than by rereading the rows.
                out.append(f"C{rank}: self_application says NOT_APPLICABLE — the trigger cannot "
                           f"occur here — while this table names code updated to comply with it. "
                           f"Code cannot comply with a control that has no trigger.")
    return out


def control_number_literal_present(all_rows: list[dict]) -> dict[int, bool]:
    """Does a named test contain the control's number as TEXT? Named literally on purpose.

    This was called `traceability` for an afternoon, which was worse than not having it. Three
    rows have it and the rest do not; presenting that as traceability beside a green `--check`
    gives the table an evidentiary sheen it has not earned. Codex's ruling: keep it only as a
    developer diagnostic with a name that says exactly what it measures.

    It is not evidence that a test exercises a control. It is evidence that somebody typed the
    control's number in the file.
    """
    out = {}
    for r in all_rows:
        if r["scope"] != CODE or not r["tests"]:
            continue
        needles = (f"C{r['rank']} ", f"control {r['rank']}", f"C{r['rank']}:")
        found = False
        for path in r["tests"]:
            try:
                text = (REPO_ROOT / path).read_text(encoding="utf-8")
            except OSError:
                continue
            if any(n.lower() in text.lower() for n in needles):
                found = True
                break
        out[r["rank"]] = found
    return out


def markdown(all_rows: list[dict]) -> str:
    ticked = sum(1 for r in all_rows if r["complete"])
    code_rows = [r for r in all_rows if r["scope"] == CODE]
    na = [r for r in all_rows if r["scope"] == NOT_CODE]
    #  DERIVED, NOT TRANSCRIBED. The first draft typed "seventeen ticked rows are recorded
    #  VIOLATED" beside the data that produces it. Computed, it was one. That is this record's
    #  single most frequent defect and the reason derive_counts.py exists.
    determined = determinations()
    substantiated = sum(1 for r in code_rows if r["substantiated"])
    lines = [
        "# Control application to this repository's code",
        "",
        "One row per registered control. **Generated by `tools/control_application.py` — do not "
        "edit this file by hand**; a hand-edited compliance matrix is the artifact this table "
        "exists to avoid being.",
        "",
        f"**{ticked} of {len(code_rows)}** controls that govern code here have had their code "
        f"work finished. **{len(code_rows) - ticked}** have code work remaining. "
        f"**{len(na)}** govern no code here and say why.",
        "",
    ]
    #  THE HISTORY IS UNCONDITIONAL. It was inside `if ticked == 0`, so the moment the first
    #  row was ticked the warning vanished — exactly when a reader most needs it, because a
    #  table showing progress invites more trust than one showing none. What was conditional on
    #  the count is now only the first sentence.
    lines += [
        ("**Nothing is ticked, and that is the finding.**" if ticked == 0 else
         f"**{ticked} of these rows {'is' if ticked == 1 else 'are'} ticked, and the history of "
         f"this table is the reason to read a tick narrowly.**")
        + " An earlier draft ticked **fourteen** rows. External review went through them "
        "against the *registered control text* rather than against what had been built, and "
        "**none survived**. The recurring defect has a name: a missing machine-testable "
        "requirement was being classified as \"not closable in code\". Control 4 was ticked with "
        "a note about the custodian being the only party present, while the lease it names "
        "checks neither token subject, resource scope, nonce nor revocation — four requirements "
        "in the control's own text, all unimplemented. Controls 18, 23 and 62 admitted the "
        "missing work in their own notes and stayed ticked anyway.",
        "",
        f"{substantiated} of the {len(code_rows)} code-governing rows are **substantiated** — "
        f"they name code and tests that exist. {ticked} "
        f"{'is' if ticked == 1 else 'are'} **declared finished**. Those are different facts and "
        f"the table keeps them apart.",
        "",
    ]
    lines += [
        "## What the checkbox means",
        "",
        "| | |",
        "|---|---|",
        "| ☑ | the code work is **declared** finished by its author **and** the row is "
        "mechanically substantiated |",
        "| ☐ | code work remains — the gap says what |",
        "| — | the control governs no code here — the reason says why, structurally |",
        "",
        "A tick needs two independent things. **Substantiated** is mechanical: the row names "
        "code and tests, and every named path is on disk — a row pointing at a deleted file "
        "fails the build. **Declared** is a human judgement recorded in the source. Nothing "
        "computes it, and an earlier version of this table inferred it from the *absence* of a "
        "gap while telling readers nothing was asserted by hand. Omitting a gap is asserting it "
        "by hand, with extra steps.",
        "",
        "**A tick would not mean the control is satisfied.** That is a different question, "
        "answered by `tools/self_application.py`, and the two are cross-checked on every run. "
        "They can differ in both directions: control 5 is recorded ENFORCED there — "
        "`derive_counts.py` genuinely refuses rather than emitting a number — and carries a gap "
        "here, because nothing routes measurements through it and the \"0 searches across 83 "
        "tool calls\" error happened in a script that never called it. A control enforced "
        "somewhere is not the code complying everywhere.",
        "",
        "The **residue** on a row is what no code could supply. It is not a place to file "
        "unbuilt work; that distinction is what the fourteen wrong ticks turned on.",
        "",
        "## The table",
        "",
        "| # | Control | Done | Code updated and tested, or why not |",
        "|---:|---|:---:|---|",
    ]
    for r in all_rows:
        if r["scope"] == NOT_CODE:
            cell = f"**Not applicable to code.** {r['reason']}"
        else:
            paths = " ".join(f"`{p}`" for p in r["files"])
            tests = " ".join(f"`{p}`" for p in r["tests"]) or "*no test named*"
            cell = f"{paths}<br>tested by {tests}"
            if r["gap"]:
                cell += f"<br>**Remaining:** {r['gap']}"
            if r["residue"]:
                cell += f"<br>*Not closable in code:* {r['residue']}"
            state = determined.get(r["rank"], ("",))[0]
            if state:
                cell += f"<br><small>self-application: {state}</small>"
        lines.append(f"| {r['rank']} | {r['name']} | {r['mark']} | {cell} |")
    lines += [
        "",
        "## What this table does not establish",
        "",
        "* **That any named test exercises the control.** It establishes the file exists.",
        "* **That the file list is complete.** It is what one party recalls changing for that "
        "control. A file changed for a control and not listed here is invisible to this table.",
        "* **That the scope calls are right.** Six were wrong on the review that produced this "
        "version: five controls marked \"governs no code\" do govern code here, and two of those "
        "carried reasons that were **false** — that no refused proposal had ever been "
        "re-proposed, and that no rollback mechanism exists. Both are contradicted by this "
        "repository's own self-application table. They were caught only after an exemption "
        "shielding this file from the prose gate was withdrawn.",
        "* **That the gaps are the only gaps.** A control whose code work nobody has thought "
        "about looks exactly like one that is finished, if the little that was done happened to "
        "have a test.",
        "* **That a row was reviewed by anyone but its author.** Four of control 6's five roles "
        "in one hand.",
    ]
    return "\n".join(lines) + "\n"


TABLE = REPO_ROOT / "record" / "controls" / "control-application.md"
DOCS = REPO_ROOT / "docs"


def publish() -> list[str]:
    """Write the durable file AND the page, from ONE markdown source.

    The page is not a second rendering of the same facts — it is `markdown()` put through the
    site's wrapper. Two renderers would drift, and a compliance table that says one thing in the
    repository and another on the web is worse than not publishing it.
    """
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import build_round_pages as b                                        # noqa: PLC0415

    all_rows = rows()
    md = markdown(all_rows)
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text(md, encoding="utf-8")

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "artifacts").mkdir(parents=True, exist_ok=True)
    #  Byte-identical plain text beside the page, the same resolution the register and the
    #  deficiency views reached: hashable, and not subject to the page budget.
    (DOCS / "artifacts" / "control-application.md").write_text(md, encoding="utf-8")
    (DOCS / "control-application.html").write_text(
        b.md_to_html(md, "Control application to this repository's code — OAGF",
                     alternate="artifacts/control-application.md"), encoding="utf-8")
    return ["record/controls/control-application.md",
            "docs/control-application.html",
            "docs/artifacts/control-application.md"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true", help="refuse an unsubstantiated row")
    parser.add_argument("--gaps", action="store_true", help="only the rows with work remaining")
    parser.add_argument("--write", action="store_true",
                        help="regenerate the file and the page from one source")
    args = parser.parse_args()

    all_rows = rows()
    found = problems(all_rows)
    if found:
        for p in found:
            print(f"  ✗ {p}", file=sys.stderr)
        print(f"\n  {len(found)} row(s) cannot be substantiated. The table is not published "
              f"until they are.", file=sys.stderr)
        return 1

    if args.write:
        for path in publish():
            print(f"  wrote {path}")
        return 0

    code_rows = [r for r in all_rows if r["scope"] == CODE]
    ticked = [r for r in code_rows if r["complete"]]
    if args.check:
        trace = control_number_literal_present(all_rows)
        untraceable = [k for k, v in trace.items() if not v]
        print(f"  every control has a row ({len(all_rows)}); {len(ticked)} of {len(code_rows)} "
              f"code-governing controls are finished and tested.")
        #  Printed as a diagnostic under its literal name. It is deliberately NOT phrased as
        #  coverage or traceability, and deliberately not adjacent to the pass line.
        print(f"  diagnostic — control_number_literal_present: "
              f"{len(trace) - len(untraceable)} of {len(trace)} code rows name a test that "
              f"contains the control's number as text. This measures typing, not testing.")
        return 0

    shown = [r for r in code_rows if not r["complete"]] if args.gaps else all_rows
    for r in shown:
        print(f"  {r['mark']}  C{r['rank']:<3} {r['name']}")
        if r["scope"] == NOT_CODE:
            print(f"        not applicable to code — {r['reason'][:100]}")
            continue
        print(f"        {len(r['files'])} file(s), {len(r['tests'])} test(s)")
        if r["gap"]:
            print(f"        REMAINING: {r['gap'][:110]}")
    print(f"\n  {len(ticked)} of {len(code_rows)} code-governing controls finished; "
          f"{len(code_rows) - len(ticked)} with work remaining; "
          f"{len(all_rows) - len(code_rows)} govern no code here.")
    print("  A tick means the CODE WORK is done, not that the control is satisfied. See")
    print("  tools/self_application.py for compliance, which is a different question.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
