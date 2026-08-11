#!/usr/bin/env python3
"""Where this repository stands against its own register — a determination per control.

    python3 tools/self_application.py            # the table
    python3 tools/self_application.py --check    # refuse if any control has no determination

WHY THIS EXISTS. The register publishes 63 controls and tells implementers they are worth
adopting. An implementer's first fair question is what the authors did about their own. Publishing
a control while exempting yourself from it is the posture the record's own control 10 exists to
forbid, so the determination is data in the repository rather than a paragraph of intent.

WHAT THIS IS NOT. It is a PRODUCER DECLARATION. The party writing it is the party it describes,
which is four of control 6's five roles. Under `record/designs/witnessed-control-challenge.md` a
declaration of `OUT` needs a structural refuter and one witness overturns it -- so every `OUT`
here is an invitation to be defeated, not a result. `record/findings/2026-08-10-pilot-witnessed-
control-challenge.md` records one such declaration being defeated on a single witness, against a
different subject, by the same procedure.

NO BLANK CELLS. Control 44: `--check` refuses when any control lacks a determination, and a
`NOT_APPLICABLE` must carry a reason distinguishable from an omission. That is why the table is
exhaustive rather than a list of the flattering ones.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

#  ENFORCED     a gate refuses the commit, or a tool refuses to emit. Name the mechanism.
#  PRACTISED    done reliably by habit or by a tool that does not block. One bad day from lapsing.
#  VIOLATED     the trigger exists here and the requirement is NOT met. Say so plainly.
#  UNRESOLVED   the trigger may exist and nobody has established it either way.
#  NOT_APPLICABLE  a STRUCTURAL reason the trigger cannot occur here. Not "we don't do that".
STATES = ("ENFORCED", "PRACTISED", "VIOLATED", "UNRESOLVED", "NOT_APPLICABLE")

#  rank -> (state, evidence or reason)
DETERMINATION: dict[int, tuple[str, str]] = {
 1:  ("VIOLATED",
      "The workbench writes the gates that constrain it. Reconciliation found 12 gate "
      "modifications in one lease window by the constrained layer, and there is no second key "
      "holder. This is the register's top-ranked control and this repository does not meet it."),
 2:  ("PRACTISED",
      "verify_negative_control.py ships 14 must-reject fixtures and a known-gaps directory, and "
      "new gates here are given a negative control before landing. NOT enforced: nothing refuses "
      "a gate that has never been observed to fail."),
 3:  ("PRACTISED",
      "reconcile_actions.py enumerates effects from git -- a channel the action log does not "
      "write -- and subtracts what the log claims. Run on demand, not by land.py."),
 4:  ("ENFORCED",
      "executive_lease.py; land.py refuses to commit or push without a live, scope-matched "
      "lease, and an unknown action class raises rather than permitting."),
 5:  ("ENFORCED",
      "derive_counts.py prints no number at all when any in-scope artifact is unreadable or its "
      "artifact_type unregistered."),
 6:  ("VIOLATED",
      "One operator holds selection, authorship, custody, scoring and promotion. Every "
      "evaluation in this record is self-issued and the record says so wherever it matters."),
 7:  ("ENFORCED",
      "corpus/ is append-only and manifest-anchored; check_raw_append_only.py and "
      "build_manifest.py refuse an overwrite; corrections attach rather than replace. The "
      "checkpoint is not externally held, which is the residual gap."),
 8:  ("UNRESOLVED",
      "The noise floor was computed for one deficiency (D-28) and has not been applied to any "
      "figure published since. Whether current reported effects clear it is not established."),
 9:  ("PRACTISED",
      "Solicitation captures request, response, provider metadata, rejections and hashes before "
      "anything is derived, and failed samples are published. Not gated."),
 10: ("ENFORCED",
      "verify_negative_control.py rejects forbidden predicates and smuggled conclusions in an "
      "attestation's claim. Enforced for ATTESTATIONS only -- prose on the site is not covered, "
      "which is the gap controls 35/36 address."),
 11: ("NOT_APPLICABLE",
      "Structural: nothing here decomposes an authorisation across sibling nodes that could sum "
      "past a threshold. The lease is a single scalar budget checked per action, not a quota "
      "divisible among children."),
 12: ("ENFORCED",
      "executive_lease.py expires by calendar and by max_actions; it refused mid-task at 62/60 "
      "and required the custodian to renew."),
 13: ("UNRESOLVED",
      "Amendments rejected in one ballot and re-proposed in another are linked by hand. Whether "
      "any re-proposal has escaped that linkage has not been checked."),
 14: ("NOT_APPLICABLE", "Structural: no goal or plan graph. Nothing here decomposes a "
      "constraint-bearing objective into child nodes."),
 15: ("NOT_APPLICABLE", "Structural: no constraint merge -- see 14."),
 16: ("NOT_APPLICABLE", "Structural: no per-node authority attached to objectives -- see 14."),
 17: ("NOT_APPLICABLE", "Structural: no ancestry registry over goals -- see 14."),
 18: ("PRACTISED",
      "Corrections attach and never rewrite; a superseding artifact preserves what the custodian "
      "was told when deciding. Held by invariant and habit, not by a gate."),
 19: ("VIOLATED",
      "The protected set is DESCRIBED (constraints, logs, gates) and not enumerated by name, "
      "which is the weakness control 19 exists to repair. GOVERNED in land.py names three paths "
      "and is not the whole set."),
 20: ("UNRESOLVED",
      "Proxies are optimised here -- gate pass rates, control counts, round costs. Whether any "
      "has drifted from what it stands for is unmeasured, and control 20 says detection may be "
      "unverifiable in principle."),
 21: ("NOT_APPLICABLE",
      "Structural: this repository does not learn or self-modify in the sense control 21 means. "
      "Its files change only through an authored commit, never through a fitted update."),
 22: ("VIOLATED",
      "Codex is the only outside frame and it shares the operator, the repository, the framing "
      "and much training culture. The register's own control 41 says that is weak diversity."),
 23: ("PRACTISED",
      "A gate refusal is filed as a deficiency with a controlled classification rather than "
      "worked around. 57 entries. Not automatic."),
 24: ("NOT_APPLICABLE",
      "Structural: no scoring function selects among self-modifications; there is no population "
      "and no selection."),
 25: ("PRACTISED",
      "Where measurement replaces proof the substitution is stated, and the register's ICP "
      "levels exist to keep a practice note from inheriting a standard's authority."),
 26: ("NOT_APPLICABLE", "Structural: no candidate self-modifications are executed to be scored."),
 27: ("NOT_APPLICABLE", "Structural: no population under selection."),
 28: ("UNRESOLVED",
      "The workbench's standing is not scored, so there is no reward node to draw a path to. But "
      "no influence diagram has been drawn, and 'we do not have one' is exactly the declaration "
      "control 28's verifier exists to test."),
 29: ("VIOLATED",
      "No enumeration exists of what a measurement here may trigger. Gate results already cause "
      "commits, publication and lease consumption, and nothing bounds that list."),
 30: ("NOT_APPLICABLE",
      "Structural: nothing here can suppress an input to a measurement. Solicitation discards "
      "nothing -- failed and rejected samples are published with their evidence -- so there is "
      "no quarantine channel to constrain."),
 31: ("PRACTISED",
      "Findings state what they do not establish at comparable length. The controls page now "
      "leads with 13-of-63 rather than the total. Not gated."),
 32: ("VIOLATED",
      "Status fields here (ELIGIBLE, ICP levels, lease evidence) carry no maximum age and do not "
      "downgrade on staleness. check_executive_context.py verifies identity, not currency."),
 33: ("NOT_APPLICABLE",
      "Structural: the workbench is not scored, so there is no measurement of it to read. If "
      "scoring is ever introduced this becomes IN immediately."),
 34: ("UNRESOLVED",
      "The panel is asked to judge proposals rather than to rate their own insightfulness, which "
      "is the right shape. Whether any rubric rates the property under claim has not been "
      "audited across all instruments."),
 35: ("VIOLATED",
      "Novelty claims are published here with no prior-art search record, and two were false. "
      "check_claims.py TRIAGES them -- a novelty candidate in changed prose must receive a "
      "disposition -- but triage is not the control: no producer-independent party exists here "
      "to run either half. A draft of this table marked it ENFORCED citing a tool that did not "
      "yet exist, which is the green-laundering this gate is supposed to prevent."),
 36: ("VIOLATED",
      "Both of this record's false prior-art claims were absence claims in prose. "
      "check_claims.py now refuses an undisposed absence candidate in CHANGED prose, and its "
      "negative control reproduces all five historical errors. It is still VIOLATED: 2,120 "
      "legacy spans are frozen as debt, `detector_false_positive` is a valid disposition, and "
      "the control asks for a labelled search that nothing yet requires."),
 37: ("VIOLATED",
      "The custodian directs every session and nothing tags where his direction supplied the "
      "decisive step. Any autonomy figure over this record would be uncheckable, which is why "
      "none is published."),
 38: ("UNRESOLVED",
      "Definitions here have moved -- what counts as a control, as ELIGIBLE, as a deficiency -- "
      "and no definition hash travels with any series."),
 39: ("NOT_APPLICABLE",
      "Structural: no compounding or reuse claim is made. Nothing here claims a capability "
      "improvement that transfers."),
 40: ("PRACTISED",
      "The outreach carries a pre-committed adverse outcome with a date, and the prediction "
      "registry scores dated claims on fixed dates. Not every workstream has one."),
 41: ("VIOLATED",
      "Agreement between the two harnesses and across the five-model panel is cited without a "
      "correlation estimate. check_claims.py triages dependence claims, but error correlation "
      "is NOT ESTIMABLE here: it needs repeated cases with externally known answers and no such "
      "labelled dataset exists. The limitation is stated in CLAUDE.md, which is a caveat in a "
      "file rather than a constraint on a number."),
 42: ("VIOLATED",
      "Capability claims here mix strata. 'Built', 'shipped', 'used by anyone' are distinct and "
      "the record does not consistently name which -- the register's own tools are described as "
      "shipped where only the first rung is established."),
 43: ("NOT_APPLICABLE",
      "Structural: no efficiency claim is made. Cost is reported from the ledger as spend, not "
      "as a saving against an alternative."),
 44: ("ENFORCED",
      "This table. --check refuses when any control has no determination, and a NOT_APPLICABLE "
      "must carry a reason."),
 45: ("VIOLATED",
      "Gates here are rewritten routinely and no retained suite proves a replacement still "
      "catches what its predecessor caught. The integrity suite was itself found passing against "
      "seeded pages after a rebuild whose exit code was discarded."),
 46: ("UNRESOLVED",
      "No baseline of intended behaviour was retained at the start, so drift against the "
      "original cannot be computed. The context pins are the nearest thing and they verify "
      "identity, not distance."),
 47: ("NOT_APPLICABLE",
      "Structural: no delegation chain. There is one actor with one lease; nothing receives "
      "authority from something else's output."),
 48: ("NOT_APPLICABLE", "Structural: no composed workflow of separately trusted components."),
 49: ("PRACTISED",
      "Nothing solicited is discarded: failed, truncated and rejected samples are published with "
      "their evidence, and undisposed amendments block a re-ballot. The skipped-source and "
      "severity-change fields control 49 asks for do not exist."),
 50: ("VIOLATED",
      "tools/gate_health.py computes it from the action log, and codex_call.py now PRINTS IT AT "
      "THE MOMENT OF OVERRIDE rather than only in a report nobody runs — which is what the "
      "control asks for. **The rate is 0.857 — 18 of 21 "
      "Codex invocations overrode the 10-minute floor.** Every one was on the custodian's "
      "direction and individually justified; the aggregate was invisible until it was counted, "
      "which is the whole of what control 50 predicts. Still VIOLATED rather than PRACTISED: the "
      "control also requires the SEVERITY DISTRIBUTION of what was overridden and the completion "
      "of follow-up actions, and neither is recorded. A floor overridden 86% of the time is not "
      "a floor; whether the right response is to delete it or reset it is a SPEND decision on an "
      "unreadable channel, so it sits with the custodian rather than being taken here."),
 51: ("UNRESOLVED",
      "Rollbacks here are rare and no record has been checked for an unrestored-state field. The "
      "external effects of a published-then-corrected page are not restorable and this is stated "
      "in the disclosure rule, which is the substance if not the form."),
 52: ("PRACTISED",
      "The lease refusing mid-task is recorded as correct operation, and a refusal to delete "
      "argued from a wrong number was preferred over the deletion. Nothing scores the workbench, "
      "so there is nothing to penalise refusal -- see 28."),
 53: ("PRACTISED",
      "derive_counts.py refuses rather than defaulting, and the closed-world discipline is the "
      "repository's most-repeated lesson. Not typed at the value level: an unknown is still a "
      "refusal to print, not a type that arithmetic rejects."),
 54: ("NOT_APPLICABLE",
      "Structural: no component here is updated with the intent that other agents reuse it, so "
      "there is no update-versus-benefit distinction to draw."),
 55: ("VIOLATED",
      "Gate refusals are recorded; rejected candidates are not retained for later re-evaluation, "
      "so the false-reject rate of every gate here is unknown and unknowable retrospectively."),
 56: ("PRACTISED",
      "Gates check against requirements the custodian sets; land.py resolves nothing and refuses "
      "outward. No count is kept of decisions a gate resolved that should have escalated."),
 57: ("VIOLATED",
      "tools/gate_health.py now reports a vector: actions by class, verified vs not, coverage "
      "states, entries carrying problems, deploys and unobserved deploys. **Two dimensions read "
      "UNKNOWN rather than zero** — false accepts have no ground truth here, and false rejects "
      "are unknowable because rejected candidates are not retained (control 55). Not ENFORCED: "
      "no gate consumes the vector, and a single dimension can still be quoted alone by anyone "
      "who wants to."),
 58: ("PRACTISED",
      "CHALLENGE.md asks an outsider to rebuild a verifier from the specification alone and "
      "tells them not to read the reference implementation. That is the control exactly -- and "
      "it is PRACTISED rather than ENFORCED because nobody has yet attempted it."),
 59: ("VIOLATED",
      "Every gate, fixture and acceptance criterion in this repository is public and visible to "
      "the party producing candidates against them, which is this workbench. Nothing is "
      "withheld, and the register says that is how a gate stops measuring."),
 60: ("NOT_APPLICABLE",
      "Structural: nothing here generates its own subgoals. Work comes from the custodian."),
 61: ("VIOLATED",
      "Observations here -- round results, spend, gate outcomes -- carry no identity of the "
      "configuration in force when they were taken, so figures pool across tool and prompt "
      "changes with nothing recording it."),
 62: ("ENFORCED",
      "There is one path. land.py runs the same gates for a change to the register, a change to "
      "a gate, and a change to itself; no separate governance route exists."),
 63: ("PRACTISED",
      "Findings state what they do not establish at comparable length, and the register "
      "publishes its known gaps and its declined material. Not gated, and the residual is "
      "characterised in prose rather than as an artifact."),
}


def controls() -> list:
    spec = importlib.util.spec_from_file_location(
        "_bcp_sa", Path(__file__).resolve().parent / "build_controls_page.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CONTROLS


def problems() -> list[str]:
    """Control 44 applied to this table: no control may be missing, and none may be blank."""
    out = []
    ranks = {c["rank"] for c in controls()}
    for rank in sorted(ranks - set(DETERMINATION)):
        out.append(f"control {rank} has no determination. A register that publishes a control "
                   f"while saying nothing about its own compliance is the posture control 10 "
                   f"forbids.")
    for rank in sorted(set(DETERMINATION) - ranks):
        out.append(f"determination for control {rank}, which is not in the register")
    for rank, (state, reason) in sorted(DETERMINATION.items()):
        if state not in STATES:
            out.append(f"control {rank}: state {state!r} is not one of {STATES}")
        if not reason or len(reason) < 40:
            out.append(f"control {rank}: reason is missing or too short to be a reason. A "
                       f"NOT_APPLICABLE without a stated structure is an omission wearing a "
                       f"label.")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if any control lacks a determination")
    args = parser.parse_args()

    found = problems()
    if found:
        for problem in found:
            print(f"  \033[31m✗\033[0m {problem}", file=sys.stderr)
        print(f"\n{len(found)} problem(s) with the self-application table.", file=sys.stderr)
        return 1
    if args.check:
        print(f"  every control has a determination ({len(DETERMINATION)}).")
        print("  This says the table is COMPLETE. It does not say any determination is correct,")
        print("  and the party that wrote it is the party it describes.")
        return 0

    by_state: dict[str, list] = {s: [] for s in STATES}
    names = {c["rank"]: c["name"] for c in controls()}
    for rank, (state, _reason) in sorted(DETERMINATION.items()):
        by_state[state].append(rank)
    print("  Where this repository stands against its own register\n")
    for state in STATES:
        ranks = by_state[state]
        print(f"  {state:15} {len(ranks):2d}  {', '.join(str(r) for r in ranks)}")
    print()
    for rank in by_state["VIOLATED"]:
        print(f"  VIOLATED {rank}: {names.get(rank, '?')}")
    print("\n  A producer declaration. Every NOT_APPLICABLE is an invitation to be defeated by")
    print("  one witness; see record/designs/witnessed-control-challenge.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
