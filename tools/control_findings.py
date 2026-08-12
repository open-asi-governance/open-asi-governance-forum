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

**A detector fired for 9 of 27 — the largest single category, and every one of them control 53,
whose defect shape is mechanically recognisable.** The other 18 came from reading, from running the
fault, or from an outsider. So the controls both caught things directly AND directed attention to
the right code, and the split matters more than either number alone.

Those two numbers are CHECKED against the table below by `--check`, which refuses if they have
drifted apart. A count transcribed into prose beside the data it describes is this record's most
frequent defect: three published figures were wrong on 2026-08-10 in exactly this way, and a
docstring is not exempt for being a comment.

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
    print(f"\n  A DETECTOR FIRED FOR {detector_n} OF {total} — the largest single category, and")
    print("  all of them control 53, whose defect shape is mechanically recognisable. The other")
    print(f"  {total - detector_n} came from reading, from running the fault, or from someone outside.")
    print("\n  An earlier version of this line said 'most were found by reading or by an")
    print("  outsider'. That was true only by summing three categories against one, and it read")
    print("  as a claim the numbers do not support. Corrected here rather than quietly.")
    print("\n  This is process evidence about one small codebase audited by its own authors.")
    print("  It is NOT evidence that the controls work in general (control 31), that these")
    print("  defects would have caused harm, or that the count is complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
