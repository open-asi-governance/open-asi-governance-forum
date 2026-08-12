#!/usr/bin/env python3
"""The orchestrator must STOP at a failing step, not carry on and report a rebuild.

    python3 tools/tests/test_rebuild_halts.py

`rebuild.py` is `land.py`'s first gate and it runs twenty-one steps in a fixed order, each of
which can fail. It prints *"Nothing downstream was rebuilt"* when one does, and until now nothing
checked that the sentence was true. A green landing rests on it: if the orchestrator continued
past a failure, every later artifact would be rebuilt from state the failing step was supposed to
have validated, and the gate would still be red — so the operator would fix the named step, rerun,
and never learn that the intervening run had published anything.

THE CLAIM IS ABOUT WHAT DID NOT HAPPEN. It is asserted over the step labels the orchestrator
prints as it STARTS each step, because those are downstream of the loop actually reaching them —
and NOT over the filesystem, which cannot carry it here: the rebuild is deterministic and the
repository is already built, so a successful run changes nothing and an assertion that a late
artifact is unchanged would pass either way. That vacuous version is what this file contained
first, and the note beside the fix says so.

`test_integrity.py` gets its case here too, for the same reason: it is CI's own gate, 142
assertions about the published record, and nothing had ever required it to fail.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from effect_boundary import refuses                                       # noqa: E402

COVERS = ("rebuild.py", "test_integrity.py")

PASSED = FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


print("\nrebuild.py — 'Nothing downstream was rebuilt' must be true, not consoling")


def break_a_late_step(image: Path) -> None:
    """Empty CHALLENGE.md. That fails `publish the implementation challenge`, which sits three
    steps from the end — so the viewer, the prediction view, the capture page and the page-budget
    check must all be skipped."""
    (image / "CHALLENGE.md").write_text("# gone\n", encoding="utf-8")


verdict = refuses(argv=("python3", "tools/rebuild.py"), case="a step fails mid-sequence",
                  setup=break_a_late_step, expect_exit=1, timeout=600,
                  expected_effects={}, allow_network=True)

check("the orchestrator exits non-zero when a step fails", verdict["exit"] == 1,
      verdict["output"].strip()[-200:])
check("...and names the step that failed",
      "FAILED at: publish the implementation challenge" in verdict["output"],
      verdict["output"].strip()[-300:])
check("...and says nothing downstream was rebuilt",
      "Nothing downstream was rebuilt" in verdict["output"])

#  THE CLAIM IS ABOUT CONTROL FLOW, so it is asserted over the step labels the orchestrator
#  prints as it STARTS each step — which are downstream of the loop actually reaching them.
#
#  Why not the filesystem: the rebuild is deterministic and the repository is already built, so a
#  successful run changes nothing at all. `"docs/capture.html" not in changed` would therefore
#  pass on an empty change set whether or not the step ran — a vacuous assertion, and the first
#  version of this file contained exactly that. Recorded rather than quietly replaced, because
#  spotting it required noticing that a PASSING assertion was passing for the wrong reason.
LATER_STEPS = ("build threaded viewer",
               "check solicitation prompts against known defects",
               "build the prediction registry view",
               "build capture page",
               "check every published page against the token budget")
ran_after = [s for s in LATER_STEPS if s in verdict["output"]]
check("no step AFTER the failure was started", ran_after == [], f"these ran: {ran_after}")
check("...and the failing step itself was started, so the case is live",
      "publish the implementation challenge" in verdict["output"])
check("the tree is unchanged too — a deterministic rebuild of a built repository writes nothing",
      verdict["changed"] == [], str(verdict["changed"])[:200])


print("\nthe positive control — without it, a rebuild that always failed would score full marks")

verdict = refuses(argv=("python3", "tools/rebuild.py"), case="a sound repository",
                  setup=lambda image: None, expect_exit=0, timeout=600,
                  expected_effects={}, allow_network=True)
check("POSITIVE CONTROL: on a sound repository the rebuild COMPLETES", verdict["exit"] == 0,
      verdict["output"].strip()[-200:])
check("...and says so", "All artifacts rebuilt and verified" in verdict["output"])


print("\ntest_integrity.py — CI's own gate, and nothing had required it to fail")


def unrebuildable_source(image: Path) -> None:
    """Break a SOURCE, not an output.

    The first version of this case deleted `docs/controls.html` and the suite passed — correctly.
    It works against a clean clone and REBUILDS inside it, so a deleted output is regenerated
    before anything is asserted. That is the suite testing reproducibility rather than the state
    of a checkout, and the fixture had aimed at the wrong property. The discriminating break is
    one the rebuild cannot repair."""
    (image / "CHALLENGE.md").write_text("# gone\n", encoding="utf-8")


verdict = refuses(argv=("python3", "tools/test_integrity.py"),
                  case="the record cannot be rebuilt from source", setup=unrebuildable_source,
                  expect_exit=1, expected_effects={}, timeout=600)
check("the integrity suite FAILS when the record cannot be rebuilt from its sources",
      verdict["problems"] == [], str(verdict["problems"]))
check("...and it fails loudly rather than by absence",
      "FAILED" in verdict["output"], verdict["output"].strip()[-200:])

verdict = refuses(argv=("python3", "tools/test_integrity.py"), case="an intact record",
                  setup=lambda image: None, expect_exit=0, expected_effects={}, timeout=600)
check("POSITIVE CONTROL: on an intact record the integrity suite passes", verdict["exit"] == 0,
      verdict["output"].strip()[-200:])

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
