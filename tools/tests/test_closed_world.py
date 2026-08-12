#!/usr/bin/env python3
"""Control 5 as a type: a count you cannot read unless the walk accounted for everything.

The discipline existed, in one function, for one population. `tools/derive_counts.py` refuses
rather than emitting a number — and the error it was built for happened in a script that never
called it. *"0 `search_web` invocations across all 20 rounds"* was published, and the corpus
holds nine: the scan iterated each file's `samples` array, 69 raw files use `responses` and
`failures` instead, and **a scan that cannot see a file reports absence, which looks exactly like
a true zero**.

So the discipline is now a type in `tools/closed_world.py`, and two tools that walk a population
and publish a number are routed through it. These cases are the type's own negative controls, and
the routing's: injecting an unreadable file into each tool's population must WITHHOLD the number,
not report it beside a caveat.

WHAT THIS DOES NOT ESTABLISH. That the population is defined correctly. The 2026-08-10 error was
partly a scope error — the walk looked only where `samples` lived — and no type catches a
population drawn too narrowly. `Survey` makes an incomplete walk unreportable; it cannot make an
incomplete definition visible.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess as sp
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent

#  THE PROBE IS NOT NAMED `test_*.py`, and that is not cosmetic. It was, and
#  tools/tests/run_all.py globs `test_*.py` at import — so a CONCURRENT suite run picked the
#  probe up as a suite of its own and failed on a file the creating test had already deleted.
#  Two landings overlapped on 2026-08-12 and that is exactly what happened. control_coverage.py
#  globs `*.py` in this directory, so the probe is still in the population it must disturb.
#
#  What this suite drives to a REFUSAL, read by tools/control_coverage.py. A tool named here must
#  exist and this file must assert a refusal, or the scan fails — a declaration is a claim, not
#  a substitute for the case.
COVERS = ("closed_world.py", "scan_own_code.py", "control_coverage.py")

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


cw = load("closed_world")

print("\nthe type: a complete walk yields numbers, an incomplete one yields none")

survey = cw.Survey("a complete walk", scope="fixture")
for i in range(5):
    survey.seen(f"item-{i}")
    survey.accounted(f"item-{i}")
    survey.count("counted")
check("BASELINE: a complete walk is usable", survey.usable is True)
check("...and result() returns the counts", survey.result()["counts"] == {"counted": 5})
check("...and report() shows them", "5" in survey.report())

#  ONE UNREADABLE ARTIFACT, and the count is gone. Not caveated — gone.
survey = cw.Survey("a walk with one file it could not read", scope="fixture")
for i in range(5):
    survey.seen(f"item-{i}")
    survey.accounted(f"item-{i}")
    survey.count("counted")
survey.seen("item-6")
survey.unreadable("item-6", "SyntaxError: invalid syntax")
check("one UNREADABLE artifact makes the survey unusable", survey.usable is False)
raised = False
try:
    survey.result()
except cw.IncompleteSurvey:
    raised = True
check("...and result() RAISES rather than returning a partial count", raised,
      "a returned error object gets dropped; this repository has an action-log entry proving it")
check("...and report() is still safe to call", "NO COUNT" in survey.report())
check("...and names the artifact it could not read", "item-6" in survey.report())
#  EXACT ABSENCE OF THE BUCKET, not `"5" not in output` — which the string "5 artifact(s)" would
#  have satisfied or broken by accident. Assert the LABEL is gone, so no count line survives.
check("...and no count bucket appears anywhere in the report",
      "counted" not in survey.report(), survey.report())

print("\nthe accounting contract: an incoherent walk is worse than an incomplete one")

#  DECLARED AND NEVER DISPOSED. The first version ignored the key entirely, so one artifact
#  seen and none counted returned a result.
survey = cw.Survey("a walk that forgot an artifact", scope="fixture")
survey.seen("item-1")
survey.accounted("item-1")
survey.seen("item-2")
check("an artifact DECLARED and never disposed makes the survey unusable", survey.usable is False)
raised = False
try:
    survey.result()
except cw.IncompleteSurvey:
    raised = True
check("...and result() raises", raised)
check("...and the refusal says it was never disposed",
      "never disposed" in survey.report(), survey.report())

#  COUNTS WITH NOTHING ACCOUNTED. Codex reproduced 99 counted with zero artifacts seen.
survey = cw.Survey("a walk that counted without looking", scope="fixture")
survey.count("counted", 99)
check("counts with NO artifact accounted for are refused", survey.usable is False)
check("...and the refusal names that specifically",
      "counted with no artifact accounted" in survey.report(), survey.report())

#  DUPLICATES, both directions.
survey = cw.Survey("a walk that declared one thing twice", scope="fixture")
survey.seen("item-1")
for label, action in (("declaring the same key twice", lambda: survey.seen("item-1")),
                      ("disposing a key never declared",
                       lambda: survey.accounted("item-never-seen")),
                      ("disposing the same key twice",
                       lambda: (survey.accounted("item-1"), survey.unreadable("item-1", "x")))):
    misused = False
    try:
        action()
    except cw.SurveyMisuse:
        misused = True
    check(f"{label} raises SurveyMisuse at once", misused,
          "an incoherent walk must fail where it happens, not silently at the end")

#  A NEGATIVE COUNT.
survey = cw.Survey("a walk with a negative count", scope="fixture")
survey.seen("item-1")
survey.accounted("item-1")
misused = False
try:
    survey.count("counted", -5)
except cw.SurveyMisuse:
    misused = True
check("a NEGATIVE count is refused", misused)

#  AN EXPECTED MEMBER NEVER REACHED. This is the shape result() cannot otherwise see: a walk
#  that stops halfway looks identical to a walk that finished.
survey = cw.Survey("a walk that stopped halfway", scope="fixture",
                   expected=("item-1", "item-2", "item-3"))
survey.seen("item-1")
survey.accounted("item-1")
check("an EXPECTED member never reached makes the survey unusable", survey.usable is False)
check("...and the refusal names it",
      "never reached" in survey.report(), survey.report())

#  UNREGISTERED IS SEPARATE FROM UNREADABLE, because the repairs differ.
survey = cw.Survey("a walk with an unrecognised shape", scope="fixture")
survey.seen("item-1")
survey.unregistered("item-1", "artifact_type 'zzqx' is not registered")
check("an UNREGISTERED artifact also makes the survey unusable", survey.usable is False)
check("...and is reported distinctly from an unreadable one",
      "unregistered" in survey.report() and "unreadable   " not in survey.report(),
      survey.report())

#  AN EXCLUSION NEEDS A GROUND. An exemption with no reason is control 44's shape appearing
#  inside a control 5 mechanism, so the type refuses to record one.
survey = cw.Survey("a walk with exclusions", scope="fixture")
survey.seen("item-1")
survey.excluded("item-1", "a helper with no verdict of its own, excluded by a recorded decision")
check("an exclusion WITH a stated ground is accepted", len(survey.excluded_items) == 1)
check("...and does not make the survey unusable", survey.usable is True)
for bad in ("", "          ", "n/a", "skip", "excluded", "Not applicable."):
    refused = False
    try:
        survey.excluded("item-2", bad)
    except cw.SurveyMisuse:
        refused = True
    check(f"an exclusion with no ground ({bad!r}) is REFUSED", refused,
          "an exemption with no stated reason is indistinguishable from an omission")

print("\nthe routing: an unreadable file must withhold each tool's published number")


def run(tool: str, *args: str) -> sp.CompletedProcess:
    return sp.run([sys.executable, str(ROOT / tool), *args],
                  cwd=REPO, capture_output=True, text=True)


BROKEN = "def broken(:\n"

#  THE PHRASES THAT MUST NOT SURVIVE A REFUSAL are the tool's real count lines — not a phrase
#  that no longer exists. The first version asserted the absence of "file(s) scanned", which had
#  been removed in the same edit, so it forbade nothing while the per-class counts leaked.
for tool, probe, leaks in (
        ("scan_own_code.py", ROOT / "zzqx_unparseable_probe.py",
         ("undispositioned", "dispositioned")),
        ("control_coverage.py", ROOT / "tests" / "zzqx_unparseable_probe.py",
         ("HAS_NEGATIVE_CONTROL", "NOT_APPLICABLE", "total", "% of tools"))):
    #  BASELINE FIRST. A tool that refuses whatever happens is broken, not strict.
    r = run(tool)
    check(f"BASELINE: {tool} reports its number on a clean tree", r.returncode == 0,
          (r.stdout + r.stderr)[-200:])

    try:
        probe.write_text(BROKEN, encoding="utf-8")
        r = run(tool)
        output = r.stdout + r.stderr
        check(f"{tool} REFUSES when one file in its population cannot be read",
              r.returncode != 0, f"rc={r.returncode}")
        check(f"...and {tool} names the file it could not read",
              "zzqx_unparseable_probe" in output, output[-200:])
        leaked = [phrase for phrase in leaks if phrase in output]
        check(f"...and {tool} publishes NO count from the partial walk", leaked == [],
              f"leaked {leaked}; a count from an incomplete walk is the false zero with a "
              f"denominator attached")
    finally:
        probe.unlink(missing_ok=True)

    r = run(tool)
    check(f"...and {tool} reports again once the tree is clean", r.returncode == 0)

#  THE GATE PATH, SEPARATELY. `--check` did not consult the survey at all, so it passed on a
#  population it could not fully read — the gate wired into landing, blind to the thing the
#  normal path had just started refusing.
probe = ROOT / "tests" / "zzqx_unparseable_probe.py"
r = run("control_coverage.py", "--check")
check("BASELINE: control_coverage.py --check passes on a clean tree", r.returncode == 0,
      (r.stdout + r.stderr)[-200:])
try:
    probe.write_text(BROKEN, encoding="utf-8")
    r = run("control_coverage.py", "--check")
    check("control_coverage.py --check REFUSES on an unreadable population member",
          r.returncode != 0, f"rc={r.returncode}")
    check("...and reports no determination count from the partial walk",
          "every tool has a determination" not in (r.stdout + r.stderr))
finally:
    probe.unlink(missing_ok=True)

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
