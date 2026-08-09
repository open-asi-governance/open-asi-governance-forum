#!/usr/bin/env python3
"""Conformance tests for the shadow executive's completion gate and action log.

    python3 tools/tests/test_executive_log.py

Each profile encodes a failure that ACTUALLY HAPPENED on 2026-08-08, so these tests replay the
real shapes rather than invented ones. If a test here passes for a reason unrelated to the
failure it names, the gate is decorative.

The log is tested for the property that makes it auditable rather than promotional: refusals are
recorded too. An executive that logs only its successes has a log that cannot be used against it.
"""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import executive_log as ex                                                # noqa: E402

PASSED = FAILED = 0
def check(label, cond):
    global PASSED, FAILED
    if cond: PASSED += 1; print(f"  \033[32m✓\033[0m {label}")
    else: FAILED += 1; print(f"  \033[31m✗ {label}\033[0m")

def refuses(label, action, claim):
    saved = ex.LOG_PATH
    ex.LOG_PATH = Path(tempfile.mkdtemp()) / "log.jsonl"
    try:
        ex.attest(action, claim); check(f"{label} — NOT refused", False)
    except ex.AttestationFailed: check(label, True)
    except Exception as e: check(f"{label} — raised {type(e).__name__}", False)
    finally: ex.LOG_PATH = saved

def accepts(label, action, claim):
    saved = ex.LOG_PATH
    ex.LOG_PATH = Path(tempfile.mkdtemp()) / "log.jsonl"
    try:
        ex.attest(action, claim); check(label, True)
    except ex.AttestationFailed as e: check(f"{label} — refused: {e}", False)
    finally: ex.LOG_PATH = saved

print("\npush: the commit must reach the REMOTE ref, not just a local one")
refuses("a commit on no ref at all is refused", "push",
        {"target_ref": "main", "commit": "0"*40})
refuses("a claim without a commit is refused", "push", {"target_ref": "main"})
refuses("a claim without a target ref is refused", "push", {"commit": "0"*40})
src = (REPO_ROOT / "tools" / "executive_log.py").read_text()
check("the profile checks origin/<ref>, not only the local ref",
      "origin/{ref}" in src and "the push did not carry it" in src)

print("\ntest: the status must come from the suite, not a later command")
refuses("status sourced from basename is refused — the 2026-08-08 shape", "test",
        {"suite": "run_all.py", "exit_status": 0, "status_from": "basename"})
refuses("a non-zero exit is not a pass", "test",
        {"suite": "run_all.py", "exit_status": 1, "status_from": "direct"})
refuses("a claim with no exit_status is refused", "test", {"suite": "run_all.py"})
refuses("a claim with no suite identity is refused", "test",
        {"exit_status": 0, "status_from": "direct"})
accepts("a directly captured zero is accepted", "test",
        {"suite": "run_all.py", "exit_status": 0, "status_from": "direct"})

print("\nmerge: governed files must be free of conflict markers")
check("the governed set covers the manifest and the anchor log",
      "corpus/MANIFEST.sha256" in ex.GOVERNED
      and "record/anchors/manifest-anchors.jsonl" in ex.GOVERNED)
check("...and the deficiency register, which is also load-bearing",
      "corpus/deficiencies.md" in ex.GOVERNED)
problems = ex._check_merge({})
check("on a clean tree the merge profile reports nothing", problems == [])

print("\nan unknown action is refused, never waved through")
refuses("an action with no postcondition profile is refused", "publish", {"anything": 1})

print("\nrefusals are LOGGED, not only successes")
saved = ex.LOG_PATH
ex.LOG_PATH = Path(tempfile.mkdtemp()) / "log.jsonl"
try:
    ex.attest("test", {"suite": "s", "exit_status": 1, "status_from": "direct"})
except ex.AttestationFailed:
    pass
entries = ex.read_log()
check("a refused attestation still appends an entry", len(entries) == 1)
check("...marked verified=False", entries[0]["verified"] is False)
check("...carrying the problems that caused it", bool(entries[0]["problems"]))
check("every entry disclaims authority",
      "none" in entries[0]["authority"] and "adopts nothing" in entries[0]["authority"])
ex.attest("test", {"suite": "s", "exit_status": 0, "status_from": "direct"})
entries = ex.read_log()
check("the log is hash-chained", entries[0]["prev_sha256"] == "0"*64
      and entries[1]["prev_sha256"] != "0"*64)
ex.LOG_PATH = saved

print("\nquota is stamped, and fails OPEN")
q = ex.quota_now()
check("quota is queryable or explicitly unavailable", "available" in q)
if q.get("available"):
    check("it reports a rolling window", "five_hour" in q or "seven_day" in q)
    check("...with a reset time", (q.get("five_hour") or {}).get("resets_at") is not None)
saved_cred = ex.CREDENTIALS
ex.CREDENTIALS = Path("/nonexistent/creds.json")
#  CLEAR THE CACHE FIRST. This test predates the TTL cache added after the endpoint rate-limited
#  the trial, and inside run_all the cache is warm from an earlier call -- so quota_now() was
#  correctly returning a cached reading without touching credentials, and the assertion about
#  the fail-open path was testing a cache hit. force=True bypasses the TTL; clearing the value
#  removes the stale reading the failure path would otherwise attach.
ex._QUOTA_CACHE["value"], ex._QUOTA_CACHE["at"] = None, 0.0
ex._QUOTA_COOLDOWN_UNTIL = 0.0
bad = ex.quota_now(force=True)
check("an unreadable quota fails OPEN rather than refusing", bad["available"] is False)
check("...and says why it is not evidence of a full quota",
      "not evidence" in bad.get("fail_open", ""))
ex.CREDENTIALS = saved_cred

import time as _t
ex._QUOTA_CACHE["value"] = {"available": True, "five_hour": {"utilization": 7.0}}
ex._QUOTA_CACHE["at"] = _t.monotonic()
ex.CREDENTIALS = Path("/nonexistent/creds.json")
warm = ex.quota_now()
check("a WARM cache is served without touching credentials", warm.get("cached") is True)
check("...and carries the reading's age", "age_seconds" in warm)
ex._QUOTA_CACHE["at"] = _t.monotonic() - 10_000
ex._QUOTA_COOLDOWN_UNTIL = _t.monotonic() + 300
cold = ex.quota_now()
check("under a 429 cooldown it does not call again",
      cold["available"] is False and "cooldown_remaining_seconds" in cold)
check("...and attaches the LAST KNOWN reading with its age",
      (cold.get("last_known") or {}).get("five_hour", {}).get("utilization") == 7.0
      and cold.get("last_known_age_seconds", 0) > 0)
ex._QUOTA_CACHE["value"], ex._QUOTA_CACHE["at"] = None, 0.0
ex._QUOTA_COOLDOWN_UNTIL = 0.0
ex.CREDENTIALS = saved_cred

print("\nthe trial declares what it is not")
charter = (REPO_ROOT / "record/designs/shadow-executive-trial.md").read_text()
check("the charter states it has no authority", "NO AUTHORITY" in charter)
check("it records that review rejected the 'below the parties' framing",
      "not \"below the parties\"" in charter or "not \"below the parties\"" in charter.replace("“","\"").replace("”","\""))
check("it names legitimacy laundering as the danger it cannot see",
      "Legitimacy laundering" in charter)
check("it carries a sunset", "sunset" in charter)
check("it states the deletion duty, with the live test case",
      "0 searches" in charter and "83 tool calls" in charter)

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
