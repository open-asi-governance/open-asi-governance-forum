#!/usr/bin/env python3
"""Meta-tests over the test files themselves. Closes holes that have opened twice.

A test suite that silently fails to run some of its tests is worse than no suite, because it
reports a green total either way. Both instances here were found by accident.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


def files() -> list[Path]:
    return sorted(p for p in TESTS.glob("test_*.py") if p.name != Path(__file__).name)


print("\nnothing executable sits after the summary line")
#  Instance 1: eight tests once sat after `sys.exit(0)` and never ran at all.
#  Instance 2 (2026-08-10): fifteen tests landed after the summary `print`, so the file
#  reported `67 passed` and then ran fifteen more whose results were never counted.
#  Suites here use three different report idioms and there is no reason to force one. What
#  matters is the LAST point at which results are reported or the process exits -- anything
#  executable after that is uncounted whatever the idiom.
REPORT = re.compile(r"^\s*(print\(.*(passed|FAILED).*\)|sys\.exit\(|raise SystemExit\()", re.M)
for path in files():
    text = path.read_text(encoding="utf-8")
    matches = list(REPORT.finditer(text))
    if not matches:
        check(f"{path.name}: reports a result at all", False)
        continue
    after = text[matches[-1].end():]
    #  Only the exit may follow. Anything that defines or runs a test is uncounted.
    offenders = [ln.rstrip() for ln in after.splitlines()
                 if re.match(r"^(def test_|\s*check\(|test_[a-z_]+\()", ln)]
    check(f"{path.name}: no test defined or run after the summary",
          not offenders)

print("\nevery suite ends by exiting on its own failure count")
for path in files():
    text = path.read_text(encoding="utf-8")
    #  Any route that turns a failure into a non-zero status counts. Several suites collect
    #  FAILED as a list and exit inside main(); one exits 1 in an `if FAILED:` block.
    #  The counter is spelled FAILED in most suites and `failures` in two; neither spelling is
    #  the point, so match either rather than making six files agree on a name.
    counter = r"(FAILED|failures)"
    exits = bool(re.search(rf"(sys\.exit|SystemExit|return)\s*\(?\s*1 if {counter}", text)) or \
            bool(re.search(rf"if {counter}:(?s:.{{0,400}}?)(sys\.exit\(1|return 1)", text))
    check(f"{path.name}: exits non-zero when FAILED", exits)

print("\nevery suite is reachable from the runner")
runner = (TESTS / "run_all.py").read_text(encoding="utf-8")
for path in files():
    #  A suite the runner never invokes is a suite that cannot go red. If the runner globs,
    #  that satisfies this; if it lists names, the name must be there.
    globbed = "glob(" in runner and "test_" in runner
    check(f"{path.name}: run by run_all.py", globbed or path.name in runner)

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
