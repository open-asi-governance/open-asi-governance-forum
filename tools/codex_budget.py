#!/usr/bin/env python3
"""Gate Codex invocations on remaining weekly quota. The custodian's floor is 33%.

    python3 tools/codex_budget.py                  # report, and say whether an invoke is allowed
    from codex_budget import may_invoke
    ok, why = may_invoke(); if ok: ...             # then log the decision either way

**A SPENDING PROTECTION, not a safety gate.** The custodian funds both subscriptions solo and
set the floor: do not invoke Codex once less than 33% of the weekly window remains.

Why this is harder than the Claude side
----------------------------------------
Claude Code's usage comes from an OAuth endpoint this process can call directly. Codex's does
not: the token is minted by the ChatGPT SPA and lives in the browser, so `CodexUsage` reads
`https://chatgpt.com/backend-api/wham/usage` by evaluating a `fetch()` inside a logged-in tab
over the Chrome DevTools Protocol. That requires a Chrome the custodian has already
authenticated, listening on 9222.

**When no such Chrome is running, the budget is UNREADABLE**, and this module says so rather
than guessing.

Fail open, and record it
-------------------------
An unreadable budget does not block the invocation. Codex review is this project's only external
check -- it rejected roughly eight designs in one session and was right nearly every time -- and
silently disabling it to protect a budget would trade a correctness control for a spending one
without anyone deciding to.

So an unverifiable budget PROCEEDS and is recorded as unverified. That is a deliberate choice
with a cost: a run of invocations under an unreadable budget could overshoot the floor, and the
log will show exactly that rather than concealing it.

What it cannot establish
-------------------------
* What Codex costs per invocation. There is no per-call figure, so the floor is checked before
  the call and cannot be predicted across one.
* Anything about the Claude side. `executive_log.quota_now()` covers that separately, and the
  two subscriptions are not fungible.
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

CDP_VERSION_URL = "http://127.0.0.1:9222/json/version"
CDP_TARGETS_URL = "http://127.0.0.1:9222/json"
USAGE_PATH = "/backend-api/wham/usage"

#  The custodian's floor, 2026-08-09: do not invoke Codex below this much weekly quota left.
FLOOR_PERCENT_REMAINING = 33.0


def _cdp_available() -> bool:
    try:
        with urllib.request.urlopen(CDP_VERSION_URL, timeout=4):
            return True
    except Exception:                                               # noqa: BLE001
        return False


def remaining() -> dict:
    """Weekly percent remaining for Codex, or an explicit statement that it is unreadable."""
    if not _cdp_available():
        return {"readable": False,
                "why": "no Chrome DevTools endpoint on 127.0.0.1:9222",
                "how_to_enable": "consullo-utilities/scripts/launch-cdp-chrome.sh, "
                                 "then log in to chatgpt.com in that browser"}
    #  The read itself belongs to CodexUsage, which owns the CDP conversation and the token
    #  handling. Reimplementing it here would be a second implementation to keep in step, and
    #  two implementations that agree today are not a shared capability.
    jar = Path("/home/reed/git/consullo-utilities/target/consullo-utilities-1.0-SNAPSHOT.jar")
    if not jar.is_file():
        return {"readable": False, "why": "consullo-utilities jar not built"}
    libs = ":".join(str(p) for p in sorted(jar.parent.glob("lib/*.jar")))
    probe = ("import com.consullo.llm.CodexUsage;"
             "public class P{public static void main(String[] a)throws Exception{"
             "System.out.println(CodexUsage.fetchUsage().toString());}}")
    try:
        result = subprocess.run(
            ["java", "-cp", f"{jar}:{libs}", "-"], input=probe,
            capture_output=True, text=True, timeout=90)
        if result.returncode != 0:
            return {"readable": False, "why": f"CodexUsage probe exited {result.returncode}"}
        data = json.loads(result.stdout.strip().splitlines()[-1])
    except Exception as error:                                      # noqa: BLE001
        return {"readable": False, "why": f"{type(error).__name__}: {error}"}
    week = (data.get("seven_day") or data.get("weekly") or {})
    used = week.get("utilization")
    if used is None:
        return {"readable": False, "why": "no weekly utilization field in the payload"}
    return {"readable": True, "percent_used": used, "percent_remaining": 100.0 - used,
            "resets_at": week.get("resets_at")}


def may_invoke() -> tuple[bool, str]:
    """(allowed, why). FAILS OPEN on an unreadable budget, and the reason says so."""
    state = remaining()
    if not state.get("readable"):
        return True, (f"budget UNVERIFIED ({state.get('why')}) — proceeding, because disabling "
                      f"the project's only external review to protect a budget would trade a "
                      f"correctness control for a spending one without anyone deciding to")
    left = state["percent_remaining"]
    if left < FLOOR_PERCENT_REMAINING:
        return False, (f"weekly quota {left:.0f}% remaining, below the custodian's "
                       f"{FLOOR_PERCENT_REMAINING:.0f}% floor")
    return True, f"weekly quota {left:.0f}% remaining, above the {FLOOR_PERCENT_REMAINING:.0f}% floor"


def gate_and_log(purpose: str) -> tuple[bool, str]:
    """Decide, and append the decision to the executive action log either way.

    Logged whether allowed or refused: a budget gate that records only its refusals cannot show
    how close to the floor the layer has been running.
    """
    allowed, why = may_invoke()
    try:
        import executive_log as ex
        ex.log_action("codex_invoke", {"purpose": purpose, "budget": remaining()},
                      verified=allowed, problems=[] if allowed else [why], note=why)
    except Exception:                                               # noqa: BLE001
        pass
    return allowed, why


def main() -> int:
    state = remaining()
    allowed, why = may_invoke()
    if state.get("readable"):
        print(f"  Codex weekly: {state['percent_used']:.0f}% used, "
              f"{state['percent_remaining']:.0f}% remaining (resets {state.get('resets_at')})")
    else:
        print(f"  Codex weekly: UNREADABLE — {state.get('why')}")
        if state.get("how_to_enable"):
            print(f"    to enable: {state['how_to_enable']}")
    print(f"  floor: {FLOOR_PERCENT_REMAINING:.0f}% remaining")
    print(f"  invoke allowed: {allowed}\n    {why}")
    return 0 if allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
