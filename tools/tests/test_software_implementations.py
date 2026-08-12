#!/usr/bin/env python3
"""The companion view's admission rule must REFUSE — eight guards, eight conditions.

    python3 tools/tests/test_software_implementations.py

Control 2 applied to a rule about control 2's own family: every clause of the admission rule
ships with a member that must be rejected by it. Without these, the rule is a paragraph in a
docstring and the eight guards are decoration — which is the exact shape this project has now
filed four deficiencies about.

The members are constructed by MUTATING A REAL ONE, not by writing a minimal dict. A minimal dict
would trip several guards at once, and a fixture that passes because of the wrong guard is a
fixture that goes on passing after its own guard is deleted. Each case here changes one field and
asserts that one code fires.

THE POSITIVE CONTROL IS THE LIVE SET. If `problems()` over the real members is ever non-empty,
every refusal below could be firing for reasons unrelated to the mutation.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import software_implementations as si                                     # noqa: E402
from guards import expect_guard, GuardNotActivated                        # noqa: E402

PASSED = FAILED = 0


def check(label: str, cond: bool) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


def refuses(label: str, code: str, mutate) -> None:
    """Mutate one field of a real member and require exactly the named guard to fire."""
    saved = si.MEMBERS
    try:
        member = copy.deepcopy(saved[0])
        mutate(member)
        si.MEMBERS = [member]
        found = si.problems()
        try:
            expect_guard(found, code)
            check(f"{label} [{code}]", True)
        except GuardNotActivated:
            check(f"{label} [{code}] — did not fire; saw {found}", False)
    finally:
        si.MEMBERS = saved


print("\nthe live set, which every case below is measured against")
check("POSITIVE CONTROL: the real members pass their own rule", si.problems() == [])
check("...and there are members to pass it", len(si.MEMBERS) > 0)
check("...and refusals recorded by hand, since two clauses are not computable",
      len(si.REFUSED_MEMBERS) > 0)

print("\nthe admission rule, one clause at a time")

refuses("a member referencing a control below the eligibility line", "SI-01",
        lambda m: m.update(control=23))

refuses("a member referencing a control that does not exist", "SI-01",
        lambda m: m.update(control=999))

refuses("a member with an empty required field", "SI-02",
        lambda m: m.update(fixture="   "))

refuses("several predicates bundled under one name", "SI-03",
        lambda m: m.update(requirement=m["requirement"] + " It MUST also be logged."))

refuses("a requirement stating no MUST at all", "SI-03",
        lambda m: m.update(requirement="Landing claims should name the ref."))

refuses("consensus offered as evidence", "SI-04",
        lambda m: m.update(incident=m["incident"] + " This is industry standard."))

refuses("a categorical ASI applicability claim", "SI-05",
        lambda m: m.update(boundary="this always applies"))

refuses("a nonclaim that omits one of the six topics", "SI-06",
        lambda m: m.update(nonclaim="It does not establish that the code is correct, safe, "
                                    "aligned, complete, or bypass-resistant."))

refuses("a nonclaim shorter than the requirement it qualifies", "SI-07",
        lambda m: m.update(nonclaim="Not tested on an ASI; bypass, capability, completeness, "
                                    "safety, alignment unaddressed."))

refuses("a verifier that observes only the subject's own signal", "SI-08",
        lambda m: m.update(observes="the exit status the tool returned"))


print("\nwhat the view may not quietly become")


def test_it_confers_no_status() -> None:
    """A view that promoted its members would be the endorsement the register forbids."""
    md = si.markdown()
    check("every member is stated as an instance of a canonical control",
          md.count("**Canonical identity:** implementation instance of control") == len(si.MEMBERS))
    check("no member is described as a new control",
          "new control" not in md.lower().replace("not a new control", ""))
    check("the page says appearing here confers nothing",
          "confers nothing" in md or "confers no rank" in md)


def test_the_refusals_are_published_before_the_members() -> None:
    """The refused list is the honest half. Burying it under the members would make the view an
    adoptability display, which is Codex's central objection to the whole idea."""
    md = si.markdown()
    check("what was refused appears before the members",
          md.index("## What was refused") < md.index("## Members"))
    for refused in si.REFUSED_MEMBERS:
        check(f"...including {refused['proposed'][:44]}", refused["proposed"] in md)


def test_status_and_prerequisite_are_read_not_stored() -> None:
    """A second handwritten copy of rank, status or prerequisite would drift from the register."""
    src = (REPO_ROOT / "tools" / "software_implementations.py").read_text(encoding="utf-8")
    for member in si.MEMBERS:
        check(f"{member['slug']} stores no rank or status of its own",
              "rank" not in member and "status" not in member
              and "prerequisite" not in member)
    check("the view reads the register at render time",
          "build_controls_page.py" in src and "def register(" in src)


def test_the_uncomputable_clauses_are_labelled() -> None:
    """Two clauses of the rule cannot be checked mechanically. Presenting all of it as enforced
    would be exactly the overclaim the rule exists to prevent."""
    md = si.markdown()
    check("the page names the clauses that are hand judgements",
          "not computable" in md.lower())
    check("...and says which two", "adjacent" in md and "discriminat" in md)


def test_publication_refuses_while_a_member_is_rejected() -> None:
    """Publishing a view whose own rule rejects a member would be a false-absence claim one level
    out — the register has published two of those already."""
    src = (REPO_ROOT / "tools" / "software_implementations.py").read_text(encoding="utf-8")
    check("main() refuses to write when problems() is non-empty",
          "REFUSED: the admission rule rejects a member" in src)


test_it_confers_no_status()
test_the_refusals_are_published_before_the_members()
test_status_and_prerequisite_are_read_not_stored()
test_the_uncomputable_clauses_are_labelled()
test_publication_refuses_while_a_member_is_rejected()

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
