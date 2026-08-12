#!/usr/bin/env python3
"""Control 45 mechanised: a fixture names the guard it activates, so a removed guard fails.

Control 45 says a modification to a gate must ship evidence that the new gate detects at least
what the old one did. Nothing mechanised that, so it depended on somebody remembering — and in
one week three guards turned out to be doing nothing while every suite stayed green:

* an UNREACHABLE guard in `control_application.py`, whose condition could never be true (D-59);
* a guard ADVERTISED on the published page and present only in the other matrix (D-59);
* a type that returned results for four incoherent walks, protected by a fixture asserting the
  absence of a string removed in the same edit (D-60).

All three share one shape: **a fixture that observes "some refusal happened" cannot tell a live
guard from a dead one beside it.** Another guard fired, the assertion passed, and the guard under
test was never exercised.

So guards carry codes and fixtures ask for them by name. Two things then become mechanical:
an unexercised guard is reported, and a fixture naming a code that no longer exists FAILS —
which is control 45's requirement, applied to the guard rather than to the gate as a whole.

WHAT THIS DOES NOT ESTABLISH. That a guard is correct, only that a fixture drives it. And it
cannot see a check that was never written: an absent guard has no code to be missing.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

#  What this suite drives to a REFUSAL, read by tools/control_coverage.py. A tool named here must
#  exist and this file must assert a refusal, or the scan fails — a declaration is a claim, not
#  a substitute for the case.
COVERS = ("guards.py",)

#  THESE CODES ARE FIXTURE DATA, not claims about guards that exist — they are the material the
#  mechanism is tested ON. Without the declaration each reads to the registry as a fixture naming
#  a guard that was removed, which is the very failure the registry exists to report.
#
#  AN EXPLICIT LIST, NOT `= True`. The first version exempted the whole FILE, so a real orphaned
#  expectation added here later would have vanished with the fixture data. Codex narrowed it, and
#  a case below asserts that an unlisted code in this same module is still counted.
#
#  Declared HERE rather than inside guards.py, so it is visible to whoever reads this file and
#  cannot be granted from a distance.
SYNTHETIC_GUARD_CODES = ("XX-01", "XX-02", "ZZ-01", "ZZ-02", "ZZ-03", "ZZ-09")

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


g = load("guards")

print("\nthe tag: a message carries which guard produced it")

tagged = g.guard("XX-01", "the thing that went wrong")
check("a tagged message still reads as a sentence first", tagged.startswith("the thing"))
check("...and carries the code at the end", tagged.endswith("[XX-01]"))
check("activates() finds the named guard", g.activates([tagged], "XX-01") is True)
#  THE WHOLE POINT. A neighbouring guard firing must NOT satisfy an assertion about this one.
check("...and does NOT match a different guard's message",
      g.activates([tagged], "XX-02") is False,
      "if this passed, naming the guard would add nothing over 'something was refused'")
check("...and does not match a bare mention of the code in the text",
      g.activates(["a message mentioning XX-01 without being tagged"], "XX-01") is False)
#  A BRACKETED code in another guard's PROSE. The first version used substring membership, so a
#  refusal tagged [XX-02] whose text discussed [XX-01] matched XX-01 — the wrong guard, with
#  brackets, which the bare-mention case above does not reach.
check("...and does not match another guard's tag quoted inside its message",
      g.activates(["a refusal that discusses [XX-01] at length [XX-02]"], "XX-01") is False,
      "substring membership matched the discussed code, not the terminal tag")
check("...while still matching the guard whose tag is terminal",
      g.activates(["a refusal that discusses [XX-01] at length [XX-02]"], "XX-02") is True)
for bad in ("nope", "X-1", "TOOLONGCODE-01", "xx-01", "XX-1"):
    refused = False
    try:
        g.guard(bad, "message")
    except ValueError:
        refused = True
    check(f"a malformed guard code ({bad!r}) is refused", refused)

print("\nthe registry: an unexercised guard and an orphaned expectation both refuse")

real_tools, real_tests, real_baseline = g.TOOLS, g.TESTS, g.BASELINE
with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)
    tools, tests = tmp / "tools", tmp / "tools" / "tests"
    tests.mkdir(parents=True)
    try:
        #  THE BASELINE IS REPOINTED TOO. Without this every sandbox case inherits the real
        #  repository's committed guards, none of which are declared in the temp tree, and
        #  reports eleven removals — the temporal check firing correctly on a fixture that never
        #  meant to exercise it.
        g.TOOLS, g.TESTS, g.BASELINE = tools, tests, tmp / "baseline.json"

        #  BASELINE: one guard, one fixture naming it.
        (tools / "thing.py").write_text(
            'def problems():\n    return [guard("ZZ-01", "it broke")]\n', encoding="utf-8")
        (tests / "test_thing.py").write_text(
            'expect_guard(problems(), "ZZ-01")\n', encoding="utf-8")
        check("BASELINE: a guard with a fixture naming it is clean", g.problems() == [],
              str(g.problems()))

        #  AN UNEXERCISED GUARD — where a dead one hides.
        (tests / "test_thing.py").write_text("assert something_else()\n", encoding="utf-8")
        found = g.problems()
        check("a guard NO fixture names is refused", len(found) == 1, str(found))
        check("...and the refusal says an unexercised guard is where an unreachable one hides",
              found and "unreachable" in found[0], str(found))

        #  A MENTION IN A COMMENT IS NOT AN ASSERTION. This repository has already had a comment
        #  count as its own coverage, in the tool measuring coverage.
        (tests / "test_thing.py").write_text(
            '#  ZZ-01 is not exercised here and this comment must not say otherwise.\n'
            "assert something_else()\n", encoding="utf-8")
        found = g.problems()
        check("a guard named only in a COMMENT is still unexercised", len(found) == 1, str(found))

        #  ...NOR IN A DOCSTRING.
        (tests / "test_thing.py").write_text(
            '"""This suite is about ZZ-01 and asserts nothing about it."""\n'
            "assert something_else()\n", encoding="utf-8")
        found = g.problems()
        check("a guard named only in a DOCSTRING is still unexercised", len(found) == 1, str(found))

        #  CONTROL 45 ITSELF: the guard is REMOVED in a rewrite and the fixture still names it.
        #  Without this the fixture would pass on a neighbouring guard's refusal.
        (tools / "thing.py").write_text(
            'def problems():\n    return [guard("ZZ-02", "a different guard entirely")]\n',
            encoding="utf-8")
        (tests / "test_thing.py").write_text(
            'expect_guard(problems(), "ZZ-01")\nexpect_guard(problems(), "ZZ-02")\n',
            encoding="utf-8")
        found = g.problems()
        check("a guard REMOVED in a rewrite, still named by a fixture, is refused",
              any("ZZ-01" in f and "declared nowhere" in f for f in found), str(found))
        check("...and the refusal cites control 45 by what it forbids",
              any("control 45" in f for f in found), str(found))

        #  ONE CODE, ONE GUARD. Two sites sharing a code make "which fired" unanswerable.
        (tools / "thing.py").write_text(
            'def problems():\n'
            '    return [guard("ZZ-01", "one thing"), guard("ZZ-01", "a different thing")]\n',
            encoding="utf-8")
        (tests / "test_thing.py").write_text(
            'expect_guard(problems(), "ZZ-01")\n', encoding="utf-8")
        found = g.problems()
        check("one code declared at TWO sites is refused",
              any("2 sites" in f for f in found), str(found))
        #  THE DECISIVE CONTROL-45 CASE, and the one the first version did not have. Removing a
        #  guard while KEEPING its fixture was already caught. A real rewrite removes both, and
        #  that passed silently — Codex reproduced it: baseline [], delete guard and fixture
        #  together, []. Present-time agreement between code and fixtures is not retention.
        (tools / "thing.py").write_text(
            'def problems():\n    return [guard("ZZ-01", "the original guard")]\n',
            encoding="utf-8")
        (tests / "test_thing.py").write_text('expect_guard(problems(), "ZZ-01")\n',
                                             encoding="utf-8")
        g.BASELINE.write_text(json.dumps(
            {"guards": {"ZZ-01": "thing.py:2"}, "authorised_removals": {}}), encoding="utf-8")
        check("BASELINE: a guard in the committed baseline and still declared is clean",
              g.problems() == [], str(g.problems()))

        #  BOTH GONE, replaced by something else — the shape of an actual rewrite.
        (tools / "thing.py").write_text(
            'def problems():\n    return [guard("ZZ-02", "a replacement that checks less")]\n',
            encoding="utf-8")
        (tests / "test_thing.py").write_text('expect_guard(problems(), "ZZ-02")\n',
                                             encoding="utf-8")
        found = g.problems()
        check("removing a guard AND its fixture together is REFUSED",
              any("ZZ-01" in f and "DECLARED NOWHERE" in f for f in found), str(found))
        check("...and the refusal names control 45 and what it forbids",
              any("control 45" in f for f in found), str(found))

        #  RENAMED, which is the same removal wearing a new label.
        g.BASELINE.write_text(json.dumps(
            {"guards": {"ZZ-01": "thing.py:2"},
             "authorised_removals": {"ZZ-01": "too short"}}), encoding="utf-8")
        found = g.problems()
        check("an authorised removal with a ground too short to be one is still refused",
              any("ZZ-01" in f for f in found), str(found))

        #  AND AN AUTHORISED REMOVAL, recorded with a ground, is permitted. Without this arm the
        #  rule would have no way out and would be routed around the first time it fired.
        g.BASELINE.write_text(json.dumps(
            {"guards": {"ZZ-01": "thing.py:2"},
             "authorised_removals": {
                 "ZZ-01": "superseded by ZZ-02, which subsumes it; recorded deliberately"}}),
            encoding="utf-8")
        check("...and a removal recorded WITH a ground is permitted", g.problems() == [],
              str(g.problems()))

        #  AN EMPTY REGISTRY MUST NOT PASS. --check would otherwise succeed by having nothing
        #  to look at, which is the vacuous green this repository keeps finding.
        (tools / "thing.py").write_text("def problems():\n    return []\n", encoding="utf-8")
        (tests / "test_thing.py").write_text("pass\n", encoding="utf-8")
        g.BASELINE.write_text(json.dumps({"guards": {}, "authorised_removals": {}}),
                              encoding="utf-8")
        found = g.problems()
        check("an EMPTY registry is refused rather than passing vacuously",
              any("empty registry" in f for f in found), str(found))

        #  A DISCARDED RESULT IS NOT AN ASSERTION. `activates(problems(), "ZZ-02")` on a line by
        #  itself registered as an expectation while asserting nothing.
        (tools / "thing.py").write_text(
            'def problems():\n    return [guard("ZZ-03", "a guard")]\n', encoding="utf-8")
        (tests / "test_thing.py").write_text('activates(problems(), "ZZ-03")\n',
                                             encoding="utf-8")
        g.BASELINE.write_text(json.dumps({"guards": {}, "authorised_removals": {}}),
                              encoding="utf-8")
        found = g.problems()
        check("a DISCARDED activates() call does not count as an expectation",
              any("ZZ-03" in f and "NO fixture names it" in f for f in found), str(found))

        #  A WRAPPER THAT DOES NOT DELEGATE must not launder a name into an expectation.
        (tests / "test_thing.py").write_text(
            "def fired(code):\n    return True\n"
            'assert fired("ZZ-03")\n', encoding="utf-8")
        found = g.problems()
        check("a wrapper that does NOT call expect_guard does not count either",
              any("ZZ-03" in f and "NO fixture names it" in f for f in found), str(found))

        #  ...and one that does delegate is accepted, or every suite would have to inline it.
        (tests / "test_thing.py").write_text(
            "def fired(code):\n    expect_guard(problems(), code)\n    return True\n"
            'assert fired("ZZ-03")\n', encoding="utf-8")
        check("...while a wrapper that DOES delegate is accepted", g.problems() == [],
              str(g.problems()))

        #  THE OPT-OUT MUST BE NARROW. A suite that does NOT declare its codes synthetic still
        #  has them counted, or the declaration would be a way to silence the registry.
        (tools / "thing.py").write_text(
            'def problems():\n    return [guard("ZZ-03", "a real guard")]\n', encoding="utf-8")
        (tests / "test_no_declaration.py").write_text(
            'expect_guard(problems(), "ZZ-09")\n', encoding="utf-8")
        (tests / "test_thing.py").write_text('expect_guard(problems(), "ZZ-03")\n',
                                             encoding="utf-8")
        found = g.problems()
        check("a suite WITHOUT the synthetic declaration still has its codes counted",
              any("ZZ-09" in f for f in found), str(found))
        (tests / "test_no_declaration.py").write_text(
            'SYNTHETIC_GUARD_CODES = ("ZZ-09",)\n'
            'expect_guard(problems(), "ZZ-09")\n', encoding="utf-8")
        check("...and declaring them synthetic exempts exactly that file", g.problems() == [],
              str(g.problems()))
    finally:
        g.TOOLS, g.TESTS, g.BASELINE = real_tools, real_tests, real_baseline

print("\nthe real repository")

found = g.problems()
check("every named guard here is declared once and driven by a fixture", found == [],
      "\n      ".join(found[:4]))

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
