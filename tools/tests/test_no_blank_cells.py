#!/usr/bin/env python3
"""Control 44 on the two coverage matrices this repository publishes.

    Every cell MUST be filled. Where a row does not apply to a column, the cell MUST say so
    and say why. A blank cell MUST NOT be published.

Both matrices carry completeness logic and NEITHER had a case it must fail. `land.py` runs both
`--check` gates on every landing, and until now the only evidence they worked was that they had
never objected — which is the exact condition control 2 forbids, in the tool that enforces
control 44.

WHAT THIS ESTABLISHES, AND THE LIMIT IS THE POINT: **no silent blank cells.** That is all control
44 asks for. It does not establish that any filled cell is correct, that a stated reason is a
good reason, or that a determination is accurate. A matrix can be complete and wrong, and this
repository has published one that was — the self-application table marked three controls ENFORCED
citing a file that did not exist, and the completeness check passed over it because the reason
string was long enough.

THE THIRD ARM IS THE INTERESTING ONE. A blank cell is easy to catch. What control 44 actually
warns about is a cell that is filled with something indistinguishable from an omission: "n/a",
"none", an empty reason, a stated exemption with no structure behind it. Each matrix is tested
against that shape, not merely against emptiness.

Faults are injected into the modules' own data structures and restored in a `finally`. Nothing
here writes to the repository.
"""

from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

#  What this suite drives to a REFUSAL, read by tools/control_coverage.py. A tool named here must
#  exist and this file must assert a refusal, or the scan fails — a declaration is a claim, not
#  a substitute for the case.
COVERS = ("self_application.py", "control_application.py")

passed = FAILED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, FAILED
    if ok:
        passed += 1
        print(f"  \033[32m✓\033[0m {name}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {name}\033[0m")
        if detail:
            print(f"      {detail[:300]}")


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


print("\nself_application.py — a determination for every control, and no blank reasons")

sa = load("self_application")
ORIGINAL_DETERMINATION = copy.deepcopy(sa.DETERMINATION)

try:
    check("BASELINE: the table is complete as it stands", sa.problems() == [],
          str(sa.problems()[:2]))

    #  A MISSING ROW. The register publishes a control and the table says nothing about the
    #  authors' own compliance with it — the posture control 10 forbids.
    sa.DETERMINATION = copy.deepcopy(ORIGINAL_DETERMINATION)
    removed = sa.DETERMINATION.pop(53)
    found = sa.problems()
    check("a control with NO determination is refused", len(found) == 1, str(found))
    check("...and the refusal names the control that is missing",
          found and "53" in found[0], str(found))

    #  A ROW FOR A CONTROL THAT DOES NOT EXIST. The mirror image, and the one that lets a
    #  determination outlive the control it describes.
    sa.DETERMINATION = copy.deepcopy(ORIGINAL_DETERMINATION)
    sa.DETERMINATION[999] = ("NOT_APPLICABLE", "A determination for a control nobody registered, "
                                               "which describes nothing at all.")
    found = sa.problems()
    check("a determination for a control NOT in the register is refused", len(found) == 1,
          str(found))

    #  AN INVENTED STATE. The vocabulary is closed on purpose: an invented enum value is how a
    #  table starts saying something nobody can compare across rows.
    sa.DETERMINATION = copy.deepcopy(ORIGINAL_DETERMINATION)
    sa.DETERMINATION[53] = ("MOSTLY_FINE", ORIGINAL_DETERMINATION[53][1])
    found = sa.problems()
    check("a state outside the controlled vocabulary is refused", len(found) == 1, str(found))

    #  THE ONE THAT MATTERS. Not blank — filled with something indistinguishable from blank.
    for label, reason in (("an empty reason", ""),
                          ("'n/a'", "n/a"),
                          ("'not applicable'", "not applicable"),
                          ("a reason too short to state a structure", "Doesn't apply here.")):
        sa.DETERMINATION = copy.deepcopy(ORIGINAL_DETERMINATION)
        sa.DETERMINATION[53] = ("NOT_APPLICABLE", reason)
        found = sa.problems()
        check(f"NOT_APPLICABLE with {label} is refused — an omission wearing a label",
              len(found) == 1, str(found))

    sa.DETERMINATION = copy.deepcopy(ORIGINAL_DETERMINATION)
    check("...and the table is clean again once restored", sa.problems() == [])
finally:
    sa.DETERMINATION = ORIGINAL_DETERMINATION

print("\ncontrol_application.py — a row for every control, and no cell that means nothing")

ca = load("control_application")
ORIGINAL_APPLICATION = copy.deepcopy(ca.APPLICATION)


guards = load("guards")


def failures() -> list[str]:
    return ca.problems(ca.rows())


def fired(code: str) -> bool:
    """Did THAT guard fire? Not 'did something fire' — the distinction all three defects fell
    through. A neighbouring guard firing used to satisfy every assertion here.

    Routed through `expect_guard`, which RAISES, because the registry counts only that form: a
    predicate whose result can be discarded registered as an expectation while asserting nothing.
    """
    try:
        guards.expect_guard(failures(), code)
    except guards.GuardNotActivated:
        return False
    return True


try:
    check("BASELINE: every row substantiates as it stands", failures() == [],
          str(failures()[:2]))

    #  A MISSING ROW — a blank cell in the strictest sense.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION.pop(53)
    found = failures()
    check("a control with NO row is refused", fired("CA-02"), str(found[:2]))
    check("...and the refusal distinguishes a missing row from a '—'",
          any("missing row" in f or "no row" in f for f in found), str(found[:2]))

    #  A ROW FOR A CONTROL THE REGISTER DOES NOT HAVE. This direction went unchecked until
    #  2026-08-12, so a retired control's row would have sat here describing nothing.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[999] = dict(scope=ca.NOT_CODE, reason="A row for a control nobody registered.")
    found = failures()
    check("a row for a control NOT in the register is refused", fired("CA-01"), str(found[:2]))

    #  '—' WITH NO REASON. The cell says "does not apply" and says nothing else, which is the
    #  shape control 44 names: not applicable and omitted must not look alike.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.NOT_CODE, reason="")
    found = failures()
    check("a '—' row with NO structural reason is refused", len(found) == 1, str(found))
    check("...and it is THAT guard, not another one firing for the same row",
          fired("CA-04"), str(found))

    #  THE SHAPE THE CONTROL IS ACTUALLY ABOUT, on this matrix. It was tested only against
    #  self_application, and control_application had no such check — while this table's own C44
    #  row claimed both matrices rejected these. Codex injected all three and got no objection.
    for label, reason in (("'n/a'", "n/a"),
                          ("'not applicable'", "Not applicable."),
                          ("'none'", "none"),
                          ("a reason too short to state a structure", "Doesn't apply here.")):
        ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
        ca.APPLICATION[53] = dict(scope=ca.NOT_CODE, reason=reason)
        found = failures()
        check(f"a '—' row whose reason is {label} is refused", len(found) == 1, str(found))
        check("...and it is the reason-quality guard specifically", fired("CA-05"), str(found))

    #  '—' THAT NAMES CODE ANYWAY. Self-contradiction inside one cell.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.NOT_CODE, reason="Structurally cannot occur in this "
                                                        "repository for the following reason.",
                              files=("tools/land.py",))
    found = failures()
    check("a '—' row that nonetheless names code is refused", fired("CA-06"), str(found))

    #  A CODE ROW NAMING NOTHING. The cell claims the control governs code and lists none.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.CODE, files=(), tests=(),
                              gap="Something remains and this row names no file at all.")
    found = failures()
    check("a code row naming NO file is refused", len(found) == 1, str(found))
    check("...and it is the names-no-file guard specifically", fired("CA-08"), str(found))

    #  A ROW POINTING AT A FILE THAT IS NOT THERE. The failure mode of every hand-maintained
    #  compliance matrix: the claim outlives the thing it claims about.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.CODE, files=("tools/zzqx_deleted_last_week.py",),
                              tests=("tools/tests/test_derive_counts.py",),
                              declared_complete=True)
    found = failures()
    check("a row naming a file that is NOT ON DISK is refused",
          fired("CA-03") and any("zzqx_deleted_last_week" in f for f in found), str(found[:2]))
    check("...so a deleted file cannot leave a row quietly ticked",
          not ca.row(53, {"name": "x"})["complete"])

    #  A TICK WITH NO TEST. Declared finished, nothing exercising it.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.CODE, files=("tools/land.py",), tests=(),
                              declared_complete=True)
    found = failures()
    check("a row DECLARED complete with no test is refused", len(found) == 1, str(found))
    check("...and it is the declared-with-no-test guard specifically", fired("CA-09"), str(found))

    #  THE CROSS-CHECK. self_application says the trigger cannot occur; this table says code
    #  complies with it. Code cannot comply with a control that has no trigger.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[11] = dict(scope=ca.CODE, files=("tools/land.py",),
                              tests=("tools/tests/test_derive_counts.py",),
                              gap="Claiming code work against a control whose trigger cannot "
                                  "occur, which the two tables must not both assert.")
    found = failures()
    check("a row contradicting self_application's NOT_APPLICABLE is refused",
          fired("CA-11"), str(found[:2]))

    #  THE OTHER DIRECTION OF THE CROSS-CHECK. self_application names a MECHANISM (ENFORCED) and
    #  this table says the control governs no code — they cannot both hold. Written because
    #  tools/guards.py reported CA-07 as declared and driven by nothing, which is precisely where
    #  an unreachable guard hides.
    enforced = next(r for r in ca.rows()
                    if ca.determinations().get(r["rank"], ("",))[0] == "ENFORCED")
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[enforced["rank"]] = dict(
        scope=ca.NOT_CODE,
        reason="Claiming no code governs a control that self_application says a mechanism "
               "enforces, which the two tables must not both assert.")
    found = failures()
    check("a '—' row for a control self_application records ENFORCED is refused",
          fired("CA-07"), str(found[:2]))

    #  A GAP TOO SHORT TO NAME WHAT REMAINS. Same reason: CA-10 had no fixture.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.CODE, files=("tools/derive_counts.py",),
                              tests=("tools/tests/test_derive_counts.py",), gap="Some work left.")
    found = failures()
    check("a gap too short to say what remains is refused", fired("CA-10"), str(found[:2]))

    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    check("...and every row substantiates again once restored", failures() == [])
finally:
    ca.APPLICATION = ORIGINAL_APPLICATION

print("\nthe page's own history must survive its own progress")

#  The paragraph recording that an earlier draft ticked fourteen and none survived was inside
#  `if ticked == 0`. The moment the first row was ticked it VANISHED — precisely when a reader
#  most needs it, because a table showing progress invites more trust than one showing none.
#  Both branches are exercised here so the regression cannot return quietly.
try:
    rendered_now = ca.markdown(ca.rows())
    check("the history is on the page at the current count",
          "earlier draft ticked **fourteen**" in rendered_now, rendered_now[:200])

    #  Force a ticked row, so the non-zero branch renders.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    ca.APPLICATION[53] = dict(scope=ca.CODE, files=("tools/derive_counts.py",),
                              tests=("tools/tests/test_derive_counts.py",),
                              declared_complete=True,
                              residue="A forced tick, to render the non-zero branch.")
    rows_ticked = ca.rows()
    assert any(r["complete"] for r in rows_ticked), "the fixture failed to force a tick"
    check("...and it survives when rows ARE ticked",
          "earlier draft ticked **fourteen**" in ca.markdown(rows_ticked))

    #  And with none ticked.
    ca.APPLICATION = copy.deepcopy(ORIGINAL_APPLICATION)
    for rank, entry in ca.APPLICATION.items():
        entry.pop("declared_complete", None)
    rows_zero = ca.rows()
    assert not any(r["complete"] for r in rows_zero)
    zero = ca.markdown(rows_zero)
    check("...and when none are", "earlier draft ticked **fourteen**" in zero)
    check("...with the zero case saying so in its first sentence",
          "Nothing is ticked, and that is the finding" in zero, zero[:300])
finally:
    ca.APPLICATION = ORIGINAL_APPLICATION

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
