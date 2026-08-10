#!/usr/bin/env python3
"""Conformance for the post-push deploy check.

It exists because a push verified cleanly, the Pages workflow FAILED, the site kept serving the
previous build, and a page was reported to the custodian as published while it 404'd. Push
verification and deploy verification are two different facts and only one was ever checked.

The load-bearing cases are the UNOBSERVED ones. A deploy check that passes when it could not look
is the defect it was built to catch.
"""
from __future__ import annotations
import inspect, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import executive_log as ex                                             # noqa: E402
import land                                                            # noqa: E402

PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


OK = {"observed": True, "conclusion": "success", "commit": "a" * 40, "deployed_sha": "a" * 40}

print("\na clean deploy passes")
check("matching sha and a successful conclusion", ex._check_deploy(OK) == [])

print("\nUNOBSERVED IS REFUSED — every path that could not look")
for why in ("no GITHUB_TOKEN in the environment", "the workflow API could not be read",
            "still queued after 900s -- not a failure, and not a success either",
            "the deployment API could not be read"):
    problems = ex._check_deploy({"observed": False, "why": why, "commit": "a" * 40})
    check(f"refused: {why[:44]}", bool(problems) and "not OBSERVED" in problems[0])

print("\na failed or mismatched deploy is refused")
check("a failed workflow conclusion is refused",
      ex._check_deploy({**OK, "conclusion": "failure"}) != [])
check("a cancelled workflow conclusion is refused",
      ex._check_deploy({**OK, "conclusion": "cancelled"}) != [])
bad = ex._check_deploy({**OK, "deployed_sha": "b" * 40})
check("serving a DIFFERENT commit is refused", bad != [])
check("...and the message names both shas",
      bad and "aaaaaaaaaaaa" in bad[0] and "bbbbbbbbbbbb" in bad[0])
check("a claim missing either sha is refused",
      ex._check_deploy({"observed": True, "conclusion": "success", "commit": "a" * 40}) != [])
check("an abbreviated sha still matches its full form",
      ex._check_deploy({**OK, "deployed_sha": "a" * 12}) == [])

print("\nthe waiter cannot report success without a token")
saved = land.os.environ.pop("GITHUB_TOKEN", None)
try:
    r = land.wait_for_deploy("a" * 40)
    check("no token yields observed=False", r.get("observed") is False)
    check("...and says why", "GITHUB_TOKEN" in r.get("why", ""))
finally:
    if saved is not None:
        land.os.environ["GITHUB_TOKEN"] = saved

print("\nthe check is wired into landing, and skipping it is explicit")
src = inspect.getsource(land.main)
check("land.py attests the deploy", 'ex.attest("deploy"' in src)
check("a refused deploy exits non-zero", "return 3" in src)
check("it says the commit cannot be unpushed", "cannot be unpushed" in src)
check("skipping is opt-in, not the default", "--no-deploy-check" in inspect.getsource(land))
check("deploy is a registered postcondition profile", "deploy" in ex.PROFILES)

#  KEEP THE SUMMARY AND EXIT LAST.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
