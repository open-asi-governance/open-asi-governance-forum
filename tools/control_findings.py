#!/usr/bin/env python3
"""What each control actually found in this repository's own code.

    python3 tools/control_findings.py            # the ledger
    python3 tools/control_findings.py --check    # refuse an entry with no evidence path

WHY. The register asks implementers to adopt controls. The fair question back is *"what did they
find in YOUR code?"* — and until this file existed the answer lived scattered across commit
messages. Each row is a defect, the control that surfaced it, and **how it was surfaced**, which is
the column that keeps this honest.

HOW-FOUND IS NOT DECORATION. A control's detector firing and a human noticing something while
implementing that control are different events, and conflating them would claim mechanical
detection this project did not achieve. The values:

    detector      the control's own mechanical check flagged it
    negative-control  found by running the fault the control demands, not by reading
    reading       a human read the code while implementing the control and saw it
    external      someone outside this workbench found it

**A detector fired for 11 of 55.** Those are the defect shapes that are mechanically
recognisable; the rest came from reading, from running the fault, or from an outsider. So the
controls both caught defects directly AND directed attention to the right code, and the split
matters more than either number alone.

Which controls the detector findings fall under, and whether detector is in fact the largest
category, are COMPUTED by the tool rather than stated here — this sentence has been wrong twice
in the same way. It said "every one of them control 53" until a second control acquired a
detector, and then called detector "the largest single category" while `external` stood at
twelve. The two numbers above are checked against the table by `--check`, which refuses if they
drift apart. A count transcribed into prose beside the data that produces it is this record's
most frequent defect, and a docstring is not exempt for being a comment.

WHAT THIS DOES NOT ESTABLISH. That the controls work in general; that these defects would have
caused harm; that the count is complete. It is a count of defects found in one small codebase by
one party applying its own controls to itself, which is process evidence about this exercise and
not validity evidence about the controls (control 31).
"""

from __future__ import annotations

import argparse
import re
import sys

#  (control, defect, how found, evidence)
FINDINGS: list[tuple[str, str, str, str]] = [
 ("C2 negative control",
  "check_quotations.py refused a fabricated party quotation in INLINE quotes and accepted the "
  "identical sentence in a MARKDOWN BLOCKQUOTE — the form this record predominantly quotes "
  "parties in. Built for D-53, a fabricated party quotation; did not cover the shape a "
  "fabrication would take here.",
  "negative-control", "6bdbbc9; tools/tests/test_gate_negative_controls.py"),

 ("C2 negative control",
  "anchor_manifest.py had no case it must fail, and this workbench had recorded that it could "
  "not have one because it needs the network. False: --stamp and --upgrade need the network, "
  "verify() does not.",
  "reading", "c48fd82; tools/tests/test_chain_guards.py"),

 ("C2 negative control",
  "check_page_budget.py runs inside every rebuild and had never been observed to fail.",
  "reading", "8655725; tools/tests/test_publication_gates.py"),

 ("C53 typed unknown",
  "record_spend.py treated a missing token count as a real zero and priced a model with no "
  "published rate at nothing. Both UNDERSTATE SPEND in the ledger this project is funded from.",
  "detector", "42fda21; tools/scan_own_code.py C53a/C53b"),

 ("C53 typed unknown",
  "executive_lease.require() coerced an UNREADABLE action count to 0 and granted the action. Any "
  "error reading the log — including the ordinary case of a caller loading the module by path, so "
  "that `import executive_log` did not resolve — handed an exhausted lease unlimited actions. "
  "Reproduced against the live spent lease: refused one way, 'granted, 200 remaining' the other. "
  "The 2026-08-11 sweep of 47 sites missed it because it looked for absence-as-zero in tools that "
  "COUNT, and this is a tool that REFUSES.",
  "reading", "D-64; tools/executive_lease.py; tools/tests/test_lease_bounds.py"),

 ("C64 effect boundary",
  "build_viewer.py — which PRUNES docs/ — rewrote four sitemap files and THEN refused, on a "
  "receipt that had drifted from disk. The refusal was correct and it was not clean: "
  "build_sitemap() ran before _verify_controls_receipt(), whose own comment said 'before "
  "anything is deleted' — true, and insufficient. Found on the FIRST RUN of the negative control "
  "being written for those guards, by the instrument rather than by a reader.",
  "negative-control", "D-69; tools/build_viewer.py; tools/tests/test_publisher_refusals.py"),

 ("C2 negative control",
  "The four guards standing between build_viewer.py's pruner and a live published page had no "
  "case they must fail — in the tool whose predecessor deleted 189 published pages. Five now: a "
  "missing receipt, a receipt naming no pages, one carrying no counts, one naming a page not on "
  "disk, and one whose hash has drifted. Plus build_bundle.py's immutability refusal, and a "
  "second case proving the first cannot pass on the WRONG refusal.",
  "reading", "tools/tests/test_publisher_refusals.py"),

 ("C2 negative control",
  "21 of 41 coverage determinations rested on a 600-character proximity heuristic between a "
  "tool's name and a refusal assertion. Read by hand, four were false: one matched a shutil.copy "
  "list of file names, one matched prose inside a check LABEL about a different component, two "
  "matched assertions about something else entirely. The heuristic is removed and every "
  "determination is now a declaration; the published rate fell 54% to 49% as a result.",
  "reading", "D-68; tools/control_coverage.py; the COVERS declarations in eleven suites"),

 ("C2 negative control",
  "The ratchet's own fixture caught an inconsistency in the ratchet: the branch handling a "
  "VANISHED tool accepted any truthy ground, so the word 'because' excused it, while the "
  "neighbouring branch required 40 characters. Two branches of one rule disagreeing about what "
  "counts as a reason.",
  "negative-control", "tools/tests/test_coverage_ratchet.py"),

 ("C2 negative control",
  "The measure of control 2 counted PROSE as evidence of coverage. Its self-hosted-fixture path "
  "grepped each tool's whole source text, so a control's register text, that text rendered into "
  "a page, a comment quoting it, and control_coverage.py's OWN DOCSTRING describing the "
  "heuristic all scored as covered. The measure counted itself. Two obvious repairs each failed "
  "differently: an AST shape produced a false negative on a tool that imports its fixture "
  "runner, and running the flag proved nothing because three page-builders exit 0 on "
  "--fixtures while ignoring it.",
  "external", "D-68; tools/control_coverage.py SELF_HOSTED"),

 ("C2 negative control",
  "build_manifest.py and validate_provenance.py — the two tools that guard the corpus's central "
  "integrity claim, both run by land.py's first gate — had no case they must fail. Six now, "
  "asserted at the effect boundary: a modified anchored artifact, a rewritten manifest lineage, "
  "a missing artifact, an unreadable target, an unparseable artifact and a wrong source hash "
  "each refuse AND leave a fresh copy of the repository byte-identical.",
  "reading", "tools/tests/test_corpus_integrity_refusals.py"),

 ("C53 typed unknown",
  "validate_provenance.py raised a TRACEBACK out of main() on a target it could not read: only "
  "the JSON parse failure was caught, so an absent file crashed instead of being reported. A "
  "crash and a refusal look different to an operator and only one of them is the control "
  "working. Now a typed UNREADABLE failure that exits 1 with the file named.",
  "reading", "tools/validate_provenance.py; tools/tests/test_corpus_integrity_refusals.py"),

 ("C64 effect boundary",
  "The harness this row said did not exist now does, and its first three conversions all pass at "
  "the effect boundary: record_spend refuses an unregistered cohort and changes nothing anywhere "
  "(D-62), a lease-refused landing changes nothing and contacts nobody (D-67), and a refused "
  "Codex call writes exactly its one receipt and never reaches for the binary. Eight synthetic "
  "offenders that refuse CORRECTLY and then misbehave once each are all caught, including the "
  "two a filesystem comparison cannot see.",
  "negative-control", "tools/effect_boundary.py; tools/tests/test_effect_boundary.py"),

 ("C64 effect boundary",
  "A landing the lease had ALREADY REFUSED still ran `git push --dry-run origin HEAD:main` — an "
  "authenticated network operation on a denied path, inside the tool that implements this "
  "control's other instances. Every effect check this project has written would have passed it: "
  "a dry-run push changes nothing in the working tree. Found by Codex while reviewing the DESIGN "
  "of a harness for this class, before any of it was written.",
  "external", "D-67; tools/land.py preflight(); tools/tests/test_deploy_obligations.py"),

 ("C53 typed unknown",
  "reconcile_actions.py reported 0 commits, 0 logged actions and 0 unexplained effects — PERFECT "
  "reconciliation, at exit 0 — from an unparseable --since. Three failures lined up: `git log "
  "--since=<garbage>` exits 0 and matches nothing, git() returned '' on any non-zero exit, and "
  "the log filter compared timestamps as strings so every real entry sorted below 'zzqx-...'. "
  "This is the tool that produced control 1's published figure. Its own negative control was a "
  "DISJUNCT and passed on its weaker limb in every run.",
  "negative-control", "D-66; tools/reconcile_actions.py; tools/tests/test_gate_negative_controls.py"),

 ("C2 negative control",
  "The assertion that the cohort pruner 'only ever walks its own subtree' was carried entirely by "
  "a docstring: `\"OUT.glob\" in prune.__doc__ or prune.__doc__.count(\"docs/cohorts\") >= 1`, "
  "and the first limb is FALSE, so a pruner that deleted the whole docs tree would have passed "
  "provided its prose still named the right directory. Replaced with a behavioural case against a "
  "temporary tree, verified by making the pruner over-reach and watching it fail.",
  "reading", "tools/tests/test_cohort_pages.py"),

 ("C4 fail-closed lease",
  "The control found its own implementation failing open. Beyond the count defect, the reported "
  "bound was not the enforced one: `state()` modelled only the calendar bound while `require()` "
  "modelled both, so the CLI printed `live: True` and exited 0 throughout the twenty-three "
  "refusals that ended trial-03 — and land.py's `lease` gate reads nothing but that exit code.",
  "reading", "D-64; tools/executive_lease.py authorization_state()"),

 ("C64 effect boundary",
  "The lease's own negative control asserted the refusal SIGNAL and never the effect. "
  "test_max_actions_is_enforced_not_merely_recorded passed whether or not the cap blocked — its "
  "success branch called check(..., True) when require() did NOT refuse — and it counted against "
  "the REAL action log, so what it asserted depended on ambient repository history. Found by "
  "Codex while reviewing the D-64 repair.",
  "external", "D-64; tools/tests/test_executive_log.py; tools/tests/test_lease_bounds.py"),

 ("C53 typed unknown",
  "round_cycle.ledger_spent_today defaulted a missing worst_case_usd to 0.0. That figure gates "
  "whether more spending is allowed today, so an unpriceable entry made the budget preflight "
  "pass on an unknown.",
  "detector", "9067f6a"),

 ("C53 typed unknown",
  "round_cycle's per-round spend aggregation contributed 0.0 for any party reporting no "
  "actual_usd, and that figure is written to the spend ledger.",
  "detector", "9067f6a"),

 ("C53 typed unknown",
  "round_cycle's token bound injected zero tokens when a web_search spec omitted max_results. "
  "The comment directly above records the same failure from when browsing was first enabled.",
  "detector", "9067f6a"),

 ("C53 typed unknown",
  "reconcile_actions.py reported effects.get('gate_modification', 0). That figure is the "
  "evidence behind control 1 — 12 gate modifications in one lease window — and a key-shape "
  "change would have reported NO gate modifications rather than none measured.",
  "detector", "42fda21"),

 ("C53 typed unknown",
  "build_register_view.py published '0 of N classifications reviewed' on a missing key; "
  "build_round_pages.py published 'Fetched 0 page(s)'. Both now print '?'. **CORRECTED "
  "2026-08-12: the build_register_view half of this was applied in the WRONG DIRECTION.** The "
  "value came from a Counter built over every entry, so an absent bucket is a known zero, not a "
  "missing measurement — the change published '? of 58' where the truth is '0 of 58', "
  "manufacturing an unknown out of a fact. The genuine unknown is an entry missing the KEY, "
  "which raises, and is now the case the test asserts. Found by Codex reviewing the test written "
  "to protect the original repair.",
  "external", "42fda21; corrected in tools/build_register_view.py"),

 ("C53 typed unknown",
  "solicit_tools.py printed tools=0 on a missing tool_calls key — the '0 searches across 83 tool "
  "calls' defect in the same shape, still live. The same line already used '?' for "
  "elapsed_seconds, so the file's own convention sat beside the defect.",
  "detector", "42fda21"),

 ("C53 typed unknown",
  "watch_arrivals.py and gate_health.py both defaulted to zero — in tools written the same day "
  "whose stated purpose is not reporting false zeros.",
  "detector", "f111be4"),

 ("C5 closed-world",
  "watch_arrivals.py printed 'No issue, fork or star' while its stars query had FAILED. A false "
  "zero in the tool written to prevent false zeros, minutes after writing it.",
  "reading", "4c62fd1"),

 ("C36 absence claims labelled",
  "The specification claimed no machine-checkable attestation artifact existed. No search had "
  "ever been run for it. A first-pass search found NIST OSCAL and ISO 26262 fault-injection "
  "evidence.",
  "external", "record/findings/2026-08-11-prior-art-search-ncp-artifact.md"),

 ("C35 novelty screen",
  "The profile's prior-art section omitted the entire oracle-quality subfield — checked coverage, "
  "assertion quality — and had to be told by a correspondent replying to the outreach.",
  "external", "a4acbfa; spec/ficp/ficp-v0.2.md §3"),

 ("C41 correlated evaluators",
  "A draft claimed the failure class was confirmed in 'two independent codebases'. Both were the "
  "same implementer, different subsystems.",
  "external", "record/findings/2026-08-10-pilot-witnessed-control-challenge.md"),

 ("C42 capability strata",
  "self_application.py marked three controls ENFORCED citing tools/check_claims.py, which did "
  "not exist. Written while building the table whose purpose is honesty; the completeness check "
  "passed over it because the reason string was long enough.",
  "external", "e1a5ac4"),

 ("C50 override metering",
  "Every Codex --override was logged individually and no aggregate existed anywhere. Computing "
  "it gave 0.857 — 18 of 21 invocations bypassed the floor. A floor overridden nine times in ten "
  "is a receipt, not a control.",
  "reading", "eb586f8; tools/gate_health.py"),

 ("C45 replacement gate",
  "The NCP→FICP rename left tools/tests/test_negative_control.py pointing at the deprecated "
  "alias. It kept passing, and the canonical verifier had no test naming it.",
  "detector", "6bdbbc9; found by tools/control_coverage.py"),

 ("C19 protected set",
  "The protected set is described rather than enumerated, so what is protected is a judgement "
  "made by the party proposing the change. Amended to be effect-defined as well as path-defined.",
  "reading", "d1b281b"),

 ("C2 negative control",
  "check_executive_context.py treated an absent live file as DRIFT. Two of its three pinned "
  "files are absolute paths under the operator's home directory, so in CI — and in any "
  "implementer's clone — it reported a dimension it could not measure as one it had measured "
  "and found bad. Giving the gate its first negative control is what ran it in CI at all, and "
  "the failure skipped the deploy job for EIGHT consecutive commits.",
  "negative-control", "D-58; tools/tests/test_gate_negative_controls.py"),

 ("C23 observed violation opens an incident",
  "land.py attested six consecutive Pages deploy FAILURES — verified:false, "
  "conclusion:failure, deployed_sha still the old commit — and eight ordinary landings "
  "proceeded anyway. The instrument was not blind and nothing read it. No control covered the "
  "transition from an observed violation to work being constrained; Codex placed it under "
  "control 23 rather than a new control, and declined the new control this workbench wanted.",
  "reading", "D-58; record/executive/action-log.jsonl"),

 ("C23 observed violation opens an incident",
  "Building the interlock exposed a further gap: the reconciler first examined only the most "
  "recent push, so a failure followed by another landing was invisible to it. That is the "
  "historical sequence exactly — failure, land again, failure — so the backstop would have "
  "walked past all six of the events it was written for. Caught by the crash-transition fixture, "
  "not by reading.",
  "negative-control", "D-58; tools/tests/test_deploy_obligations.py"),

 ("C2 negative control",
  "The interlock's own validation had four defects the review reproduced: a recovery file "
  "containing {\"garbage\": true} closed an incident, so 'only evidence closes an incident' was "
  "false while that sentence sat in the docstring; incidents keyed on the commit made a "
  "second failure of a resolved commit invisible; land.py kept an unpinned second observer; and "
  "executive_log compared shas by PREFIX, so a one-character deployed_sha matched.",
  "external", "D-58; Codex implementation review 2026-08-12"),

 ("C53 typed unknown",
  "Running the new ledger against the real action log found it counting a push attestation with "
  "verified:false as an obligation — a 2026-08-09 probe using an all-zero sha. It would have "
  "blocked every landing forever on a commit that does not exist. The docstring had said "
  "'every VERIFIED push' from the first draft; the code had not.",
  "detector", "D-58; tools/deploy_obligations.py"),

 ("C23 observed violation opens an incident",
  "A second review round found two state-machine defects every green gate had passed: discharge "
  "was computed from unordered sets, so a deploy that happened BEFORE a push could discharge it; "
  "and two recoveries on the same day against the same head wrote the same filename, so the "
  "second overwrote the first and the incidents it had closed silently REOPENED — a correction "
  "editing a correction, in the tool whose rule is that corrections attach.",
  "external", "D-58; Codex re-review 2026-08-12"),

 ("C2 negative control",
  "control_coverage.py, which MEASURES control 2, had both errors at once. It counted tools "
  "named only in a COMMENT — a note recording that arm_acceptance.py cannot have a negative "
  "control was itself reported as that tool's coverage — and it missed check_executive_context.py, "
  "which has fifteen fixture-driven refusal cases, because the suite binds the tool name to a "
  "constant and drives it through a wrapper. Removing the first error exposed the second. Suites "
  "now DECLARE what they cover, and a declaration without a refusal assertion does not count.",
  "external", "D-58 neighbourhood; tools/tests/test_gate_refusals.py"),

 ("C2 negative control",
  "Two guards in control_application.py could never fire. `complete and not tests` was "
  "UNREACHABLE because complete is defined to require tests, so declaring a row finished with no "
  "test was discarded in SILENCE rather than refused. And the C44 row stated that both published "
  "matrices reject 'n/a' and 'not applicable' — true of self_application.py, false of "
  "control_application.py, which checked only for emptiness. The claim was itself the defect "
  "control 44 names: a cell filled with a label instead of a structure.",
  "negative-control", "D-59; tools/tests/test_no_blank_cells.py"),

 ("C19 protected set",
  "Control 44 was marked done on the strength of two guarded matrices. A THIRD already exists — "
  "record/findings/2026-08-08-search-capability-matrix.json, whose first two rows omit a column "
  "the last two carry — and nothing checks it. Enumerating the artifacts by hand and calling the "
  "set complete is the error control 19 names, committed while implementing control 44.",
  "external", "D-59; Codex review 2026-08-12"),

 ("C5 closed-world",
  "The TYPE built to enforce control 5 did not enforce it. seen() discarded the key and result() "
  "checked only for unreadable artifacts, so four incoherent walks returned successful results — "
  "including 99 counted with zero artifacts seen, and an exclusion whose stated ground was ten "
  "spaces, because the guard measured len(). Both tools routed through it also PRINTED the "
  "counts the guard was withholding, and control_coverage --check — the path wired into landing "
  "— never consulted it.",
  "external", "D-60; Codex review 2026-08-12"),

 ("C2 negative control",
  "The suite protecting the above asserted the absence of the phrase 'file(s) scanned' — a "
  "string REMOVED in the same edit that introduced the leak. It forbade nothing while the real "
  "counts leaked past it: a green signal not causally downstream of what it certifies, inside "
  "a control-2 fixture.",
  "external", "D-60; tools/tests/test_closed_world.py"),

 ("C2 negative control",
  "Naming the eleven guards in control_application.py and requiring a fixture per guard "
  "immediately found TWO that no fixture drove — the cross-check for a control self_application "
  "records ENFORCED, and the too-short-gap check. Both turned out reachable, which is the point: "
  "before this, nothing distinguished them from the unreachable guard found two batches earlier, "
  "because a fixture observing 'some refusal happened' cannot tell a live guard from a dead one "
  "beside it. Classified under control 2 rather than 45 on Codex's ruling: they demonstrate a "
  "MISSING negative control, and become control 45 evidence only when a replacement is tested "
  "against retained historical cases.",
  "detector", "tools/guards.py; tools/tests/test_no_blank_cells.py"),

 ("C2 negative control",
  "The control-5 fixture wrote its unreadable-file probe as tools/tests/test_zzqx_probe.py, and "
  "run_all.py globs test_*.py at import — so a CONCURRENT suite run enumerated the probe as a "
  "suite and failed on a file the creating test had already deleted. The suite passed every time "
  "it ran alone, which is what made it a landmine rather than a bug: green depended on nothing "
  "else running. Renamed out of the glob while staying inside the population it must disturb.",
  "reading", "tools/tests/test_closed_world.py; land8 run 2026-08-12"),

 ("C2 negative control",
  "check_quotations.py — the gate built for D-53, a fabricated party quotation — could not see a "
  "quotation that WRAPS, because both its patterns forbade a newline. Every design document here "
  "is wrapped markdown, so a fabrication of any substance was invisible. Measured over its 98 "
  "files: 235 candidates, ONE attributed, that one exempted — zero checked, every run. Its "
  "negative control passed throughout because the planted fixture was written on a single line: "
  "the fault was injected in the form that works and never in the form that occurs.",
  "reading", "D-61; tools/check_quotations.py"),

 ("C2 negative control",
  "scan_own_code.py's D-B detector matched a NAME bound to a bool and not a bool literal, so an "
  "`if True:` wrapping the entire quotation loop of a gate that runs on every landing was "
  "reported by nothing — not on the real file, and not on a direct fixture either. The literal "
  "is now the must-flag case.",
  "reading", "D-61; tools/scan_own_code.py"),

 ("C45 replacement gate",
  "Enrolling a SECOND gate found where the abstraction does not fit. expect_guard(problems, code) "
  "assumes an in-process list of refusal strings; check_quotations.py refuses by PRINTING and "
  "exiting, so its fixture has to split output into lines before asking. The wrapper still "
  "delegates, which the registry requires — but the model is shaped around one gate's return "
  "convention and the second gate had to be adapted to it rather than the reverse.",
  "reading", "tools/tests/test_gate_negative_controls.py"),

 ("C2 negative control",
  "The arm asserting record_spend.py refuses an unknown cohort instead APPENDED one — the tool "
  "did not validate the cohort, and the assertion was 'exit non-zero OR no cost printed', so an "
  "append satisfied it. 87 of the spend ledger's 141 entries were this fixture, written on every "
  "landing. A negative control that cannot observe the tool's SIDE EFFECTS can pass on the "
  "opposite of a refusal.",
  "external", "D-62; record/cycles/spend-ledger-correction-2026-08-12.md"),

 ("C53 typed unknown",
  "check_quotations.py's length cap made an over-long attributed quotation INVISIBLE rather than "
  "refusing it — four real candidates at 5,350 characters sat past it reported as nothing. A "
  "bound that hides what it cannot check is unverifiable reported as verified. Now QT-03, with "
  "boundary fixtures at the cap and one past it.",
  "external", "D-61; tools/check_quotations.py"),

 ("C45 replacement gate",
  "A publish gate requiring every control to state a scope silently made a NEIGHBOURING rule "
  "universally false: the partition predicates for 'adopt today' and 'needs a second party' each "
  "ended with `not applies_when`, which had been the marker for the third part. Both emptied, and "
  "all fourteen eligible controls — FICP included — were published as presupposing an HTN "
  "planner, beside a Part A described as adoptable while holding nothing. The gate was sound; "
  "nothing retained evidence that what it replaced still held. Found by adding control 64 and "
  "watching where it landed.",
  "reading", "D-63; tools/build_controls_page.py"),

 ("C10 assurance claim boundary",
  "The FIRST repair of that partition was itself unsupported. I wrote that 'the partition and "
  "the blurb now agree' having checked no member against its part's description — and controls "
  "11 and 13 were still filed under 'needs a goal or plan graph' because a two-valued field was "
  "carrying a three-valued ontology, while control 4, which requires a NON-SELF-ISSUED token, "
  "sat under 'adopt alone'. A claim about a repair, made in the same breath as the repair.",
  "external", "D-63; Codex review 2026-08-12"),

 ("C44 no blank cells",
  "Adding control 64 made CA-02 fire on the control-application table within a minute of the "
  "register growing — a real missing row, caught by a guard named earlier the same day rather "
  "than by anyone remembering the table needed updating.",
  "detector", "tools/control_application.py; tools/guards.py"),

 ("C40 pre-committed stop",
  "The register contained control 40 — a program pre-commits the observation that ends it — and "
  "the programme running it had no stop condition. Found by Codex, not by this workbench.",
  "external", "fb81db6; record/designs/mothball-checkpoint.md"),
]

HOW = {"detector": "the control's own mechanical check flagged it",
       "negative-control": "found by running the fault the control demands",
       "reading": "a human read the code while implementing the control",
       "external": "found by someone outside this workbench"}


def problems() -> list[str]:
    out = []
    for control, defect, how, evidence in FINDINGS:
        if how not in HOW:
            out.append(f"{control}: how-found {how!r} is not one of {sorted(HOW)}")
        if not evidence.strip():
            out.append(f"{control}: no evidence path. A finding without one is an assertion.")
        if len(defect) < 40:
            out.append(f"{control}: defect description too short to be checkable")
    out.extend(docstring_drift())
    return out


def docstring_drift() -> list[str]:
    """The prose above states two counts. Refuse if the table no longer supports them.

    This is the same defect as every published figure this record has had to correct: a number
    transcribed once, beside data that later moved. Adding two findings to the table below would
    silently falsify the summary paragraph, and nothing would have objected.
    """
    total = len(FINDINGS)
    detector = sum(1 for _c, _d, how, _e in FINDINGS if how == "detector")
    doc = __doc__ or ""
    problems = []
    claimed = re.search(r"A detector fired for (\d+) of (\d+)", doc)
    if not claimed:
        problems.append("the summary sentence naming the detector split is gone; either restore "
                        "it or remove this check, but do not leave the check pointing at nothing")
    elif (int(claimed.group(1)), int(claimed.group(2))) != (detector, total):
        problems.append(f"the docstring says a detector fired for {claimed.group(1)} of "
                        f"{claimed.group(2)}; the table says {detector} of {total}")
    other = re.search(r"other (\d+) came from", doc)
    if other and int(other.group(1)) != total - detector:
        problems.append(f"the docstring says {other.group(1)} came from elsewhere; "
                        f"the table says {total - detector}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    found = problems()
    if found:
        for p in found:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1
    if args.check:
        print(f"  every finding carries a control, a how-found and an evidence path "
              f"({len(FINDINGS)}).")
        return 0

    by_how: dict[str, int] = {}
    by_control: dict[str, int] = {}
    for control, _d, how, _e in FINDINGS:
        by_how[how] = by_how.get(how, 0) + 1
        by_control[control] = by_control.get(control, 0) + 1

    print(f"  {len(FINDINGS)} defects found in this repository by applying its own controls\n")
    for control, n in sorted(by_control.items(), key=lambda kv: -kv[1]):
        print(f"    {n:2d}  {control}")
    print("\n  HOW EACH WAS FOUND — the column that keeps this honest:\n")
    for how, n in sorted(by_how.items(), key=lambda kv: -kv[1]):
        print(f"    {n:2d}  {how:17} {HOW[how]}")
    detector_n = by_how.get("detector", 0)
    total = len(FINDINGS)
    by_detector: dict[str, int] = {}
    for control, _d, how, _e in FINDINGS:
        if how == "detector":
            by_detector[control] = by_detector.get(control, 0) + 1
    spread = ", ".join(f"{c} ({n})" for c, n in
                       sorted(by_detector.items(), key=lambda kv: -kv[1]))
    largest = max(by_how.items(), key=lambda kv: kv[1])
    rank_note = ("the largest single category" if largest[0] == "detector"
                 else f"second to {largest[0]} ({largest[1]})")
    print(f"\n  A DETECTOR FIRED FOR {detector_n} OF {total} — {rank_note}, "
          f"across {len(by_detector)} control(s):")
    print(f"    {spread}")
    print("  These are the defect shapes that are mechanically recognisable. The other")
    print(f"  {total - detector_n} came from reading, from running the fault, or from someone "
          f"outside.")
    print("\n  An earlier version of this line said 'most were found by reading or by an")
    print("  outsider'. That was true only by summing three categories against one, and it read")
    print("  as a claim the numbers do not support. Corrected here rather than quietly.")
    print("\n  This is process evidence about one small codebase audited by its own authors.")
    print("  It is NOT evidence that the controls work in general (control 31), that these")
    print("  defects would have caused harm, or that the count is complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
