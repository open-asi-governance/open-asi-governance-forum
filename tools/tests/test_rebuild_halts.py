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

NO POSITIVE CONTROLS IN THIS FILE, deliberately, and this is the one place in the repository
where that is the right call. Both tools are run FOR REAL by `land.py` and by CI on every push —
`rebuild` and `integrity` are gates — so the happy path is demonstrated causally, by a different
invocation than the one these cases drive. Duplicating it here cost a full rebuild plus a nested
clone-and-rebuild per run, which took a CI run from about three minutes to over twenty.
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


def break_the_first_step(image: Path) -> None:
    """Modify an already-anchored raw artifact. That fails step ONE — `verify raw material
    against the manifest` — so all twenty steps after it must be skipped.

    Breaking a LATE step was the first version, and it was both weaker and slower: eighteen
    steps ran before the failure, proving less about the halt and costing an almost-complete
    rebuild on every CI run. Failing first proves more and costs almost nothing."""
    path = image / "corpus" / "raw" / "activation-01" / "activation-01-claude-samples.json"
    assert path.is_file(), ("the fixture assumes this anchored artifact exists; if it moved, "
                            "this case would silently test the happy path")
    path.write_bytes(path.read_bytes() + b"\n")


verdict = refuses(argv=("python3", "tools/rebuild.py"), case="a step fails mid-sequence",
                  setup=break_the_first_step, expect_exit=1, timeout=600,
                  expected_effects={}, allow_network=True)

check("the orchestrator exits non-zero when a step fails", verdict["exit"] == 1,
      verdict["output"].strip()[-200:])
check("...and names the step that failed",
      "FAILED at: verify raw material against the manifest" in verdict["output"],
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
#  A sample from across the remaining twenty, first to last.
LATER_STEPS = ("validate provenance",
               "build the deficiency register views",
               "publish the candidate control register",
               "publish the implementation challenge",
               "build threaded viewer",
               "build capture page",
               "check every published page against the token budget")
ran_after = [s for s in LATER_STEPS if s in verdict["output"]]
check("no step AFTER the failure was started", ran_after == [], f"these ran: {ran_after}")
check("...and the failing step itself was started, so the case is live",
      "verify raw material against the manifest" in verdict["output"])
check("the tree is unchanged too — a deterministic rebuild of a built repository writes nothing",
      verdict["changed"] == [], str(verdict["changed"])[:200])


#  THE POSITIVE CONTROL FOR rebuild.py IS THE `rebuild` GATE ITSELF, and it is not duplicated
#  here. `land.py` runs `tools/rebuild.py` as its first gate and CI runs the same steps, so every
#  landing and every push already demonstrates that a sound repository rebuilds — causally, on
#  the real tree, not on a copy. Re-running it inside the harness cost a full rebuild per suite
#  execution and established nothing the gate does not.
#
#  That is a real trade and it is stated rather than assumed: the positive evidence now comes
#  from a DIFFERENT invocation than the negative cases, so a change that broke the harness's
#  ability to run rebuild.py at all would show up as this suite erroring rather than as a silent
#  pass. Removed for COST, and the cost was not marginal — a CI run went from about three
#  minutes to over twenty and had not finished when it was found.


print("\ntest_integrity.py — CI's own gate, and nothing had required it to fail")


def unrebuildable_source(image: Path) -> None:
    """Break a SOURCE, not an output.

    The first version of this case deleted `docs/controls.html` and the suite passed — correctly.
    It works against a clean clone and REBUILDS inside it, so a deleted output is regenerated
    before anything is asserted. That is the suite testing reproducibility rather than the state
    of a checkout, and the fixture had aimed at the wrong property. The discriminating break is
    one the rebuild cannot repair.

    The SAME break as the case above, deliberately: an anchored raw artifact with one byte added.
    It fails the nested rebuild at its first step rather than its nineteenth, which is the
    difference between this suite costing ninety seconds and costing two hundred."""
    path = image / "corpus" / "raw" / "activation-01" / "activation-01-claude-samples.json"
    assert path.is_file(), "the fixture assumes this anchored artifact exists"
    path.write_bytes(path.read_bytes() + b"\n")


verdict = refuses(argv=("python3", "tools/test_integrity.py"),
                  case="the record cannot be rebuilt from source", setup=unrebuildable_source,
                  expect_exit=1, expected_effects={}, timeout=600)
check("the integrity suite FAILS when the record cannot be rebuilt from its sources",
      verdict["problems"] == [], str(verdict["problems"]))
check("...and it fails loudly rather than by absence",
      "FAILED" in verdict["output"], verdict["output"].strip()[-200:])

#  Same reasoning, and more forcefully: `test_integrity.py` is run DIRECTLY by land.py's
#  `integrity` gate and by CI's own step, on every landing and every push. Running it a third
#  time inside a copy — where it clones and rebuilds again, nested — was the single most
#  expensive thing in this repository's test suite.

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
