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


print("\nthe Codex budget gate")
import codex_budget as cb                                                 # noqa: E402
_orig = cb.remaining
def _at(used):
    cb.remaining = lambda: {"readable": True, "percent_used": used,
                            "percent_remaining": 100.0 - used}
_at(10); check("well above the floor is allowed", cb.may_invoke()[0] is True)
_at(67); check("exactly at the 33% floor is allowed", cb.may_invoke()[0] is True)
_at(67.5); check("just below the floor is refused", cb.may_invoke()[0] is False)
_at(95); check("nearly exhausted is refused", cb.may_invoke()[0] is False)
cb.remaining = lambda: {"readable": False, "why": "no CDP"}
allowed, why = cb.may_invoke()
check("an UNREADABLE budget fails open", allowed is True)
check("...and the reason says the budget was unverified", "UNVERIFIED" in why)
check("...and says why disabling review to save budget is the wrong trade",
      "correctness control" in why and "spending one" in why)
check("the floor is the custodian's stated 33%", cb.FLOOR_PERCENT_REMAINING == 33.0)
cb.remaining = _orig
check("the module refuses to reimplement the CDP read",
      "Reimplementing it here" in cb.__doc__ or "CodexUsage" in cb.remaining.__doc__
      or "CodexUsage" in open(REPO_ROOT / "tools/codex_budget.py").read())


print("\nthe Codex rate limit")
import codex_call as cc                                                   # noqa: E402
_orig_last = cc.last_call
check("the floor is the custodian's stated 10 minutes", cc.min_seconds() == 600)
#  THE NUMBER AND ITS PROVENANCE MUST TRAVEL TOGETHER. A floor recorded without saying whether it
#  was measured or merely honoured acquires authority by sitting in the record.
_pol = cc.policy()
check("the floor is read from the spend policy, not hardcoded",
      "spend-policy.json" in open(REPO_ROOT / "tools/codex_call.py").read())
check("...and the policy states whether it was derived from a measurement",
      "derived_from_measurement" in _pol)
check("...and it is currently NOT measured, so it does not pose as one",
      _pol["derived_from_measurement"] is False)
check("...and the provenance says who supplied the number",
      "custodian" in _pol.get("provenance", "").lower())
_spend = json.loads((REPO_ROOT / "record/executive/spend-policy.json").read_text())
check("the policy separates the three money channels", len(_spend["channels"]) == 3)
check("...and records the Claude subscription as READABLE",
      _spend["channels"]["claude_subscription"]["readable"] is True)
check("...with NO floor invented for it",
      _spend["channels"]["claude_subscription"]["floor"]["value"] is None)
check("...and says why inventing one would be wrong",
      "indistinguishable" in _spend["channels"]["claude_subscription"]["floor"]["provenance"])
#  The Codex floor was REMOVED 2026-08-11 on the custodian's instruction; he holds rate limiting
#  directly until 2026-08-17. The policy must say who holds it and WHEN IT EXPIRES, because an
#  authority that outlives its stated window is control 12's failure mode.
_codex_floor = _spend["channels"]["codex_subscription"]["floor"]
check("the Codex floor records that the custodian holds it, not a tool",
      "custodian" in _codex_floor["kind"])
check("...and names the date it expires",
      _codex_floor.get("expires") == "2026-08-17")
check("...and states plainly that nothing replaces it after that",
      "no Codex spend control" in _codex_floor.get("what_happens_then", ""))
check("...and records the override rate that justified removing it",
      "86%" in _codex_floor.get("why_removed", ""))
check("the policy admits the log undercounts the calls actually made",
      any("23 of the 25" in s for s in _spend["what_this_does_not_establish"]))
_real_policy = cc.policy
cc.policy = lambda: {"min_seconds_between_calls": 1800, "derived_from_measurement": True}
check("a changed policy value changes the enforced floor", cc.min_seconds() == 1800)
cc.policy = _real_policy
cc.last_call = lambda: None
check("with no previous call, one is allowed", cc.may_call()[0] is True)
import datetime as _dt
def _ago(minutes):
    when = (_dt.datetime.now(_dt.timezone.utc)
            - _dt.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cc.last_call = lambda: {"utc": when, "claim": {"purpose": "t"}}
#  WHILE THE CUSTODIAN HOLDS IT, there is no wall-clock gate at all.
_ago(0.5)
_allowed, _why = cc.may_call()
check("a call 30 seconds ago is ALLOWED while the custodian holds rate limiting",
      _allowed is True)
check("...and the explanation says who holds it and until when",
      "custodian" in _why and "2026-08-17" in _why)

#  AND THE FLOOR MUST COME BACK when the window is cleared. Without this the removal is
#  indistinguishable from a deletion, and a temporary transfer that cannot be reversed is not
#  temporary. This is control 45 applied to the change: the replacement must still catch what the
#  predecessor caught, once its stated window ends.
_held = cc.MONITORED_BY_CUSTODIAN_UNTIL
cc.MONITORED_BY_CUSTODIAN_UNTIL = ""
_ago(0.5);  check("with the window cleared, a call 30 seconds ago is refused again",
                  cc.may_call()[0] is False)
_ago(9.5);  check("...and 9.5 minutes ago is still refused", cc.may_call()[0] is False)
_ago(10.5); check("...and 10.5 minutes ago is allowed", cc.may_call()[0] is True)
cc.MONITORED_BY_CUSTODIAN_UNTIL = _held
#  The override path is only reachable when a floor exists, so these run with the custodian's
#  window cleared. They are kept rather than deleted: the floor returns on 2026-08-17 unless it is
#  replaced, and a suite that stopped testing the override would leave that return unverified.
_held2 = cc.MONITORED_BY_CUSTODIAN_UNTIL
cc.MONITORED_BY_CUSTODIAN_UNTIL = ""
_ago(1)
allowed, why = cc.may_call(override="custodian said so")
check("an override is honoured", allowed is True)
check("...and the reason is carried in the explanation", "custodian said so" in why)
check("...and it is labelled as an override rather than a pass", "OVERRIDDEN" in why)
check("...and the running override RATE is shown at the point of override",
      "override" in why and "of" in why and "%" in why)
_, why_refused = cc.may_call()
check("a refusal says how long remains", "min remain" in why_refused)
check("...and offers batching before the override", "Batch the question" in why_refused)
cc.MONITORED_BY_CUSTODIAN_UNTIL = _held2
src = open(REPO_ROOT / "tools/codex_call.py").read()
#  WHITESPACE-NORMALISED. A prose assertion that breaks when a docstring rewraps is a test of the
#  line breaks, not of the claim; it once failed on "a second\nsource of truth".
_flat = " ".join(src.split())
check("the clock comes from the action log, not a side file",
      "action-log.jsonl" in _flat and "second source of truth" in _flat)
check("a REFUSED attempt does not reset the clock",
      'entry.get("verified")' in src)
check("the call is logged BEFORE it runs, so a crash is not unrecorded",
      "LOGGED BEFORE THE CALL" in src)
check("the module states it cannot prevent bypass",
      "cannot prevent bypass" in src.lower() or "does not bind the binary" in src)
check("--purpose is mandatory, so a review is auditable",
      "an unexplained review is not auditable" in src)
cc.last_call = _orig_last


# ---------------------------------------------------------------------------
#  The lease. Added 2026-08-10 after the ten-action sunset was passed at 23 and
#  nothing stopped, because nothing checked before an action began.
# ---------------------------------------------------------------------------

import executive_lease as lease                                            # noqa: E402


def _lease(expires, tmp):
    lease.LEASES = tmp
    lease.grant("t", expires, "test", "test evidence")
    return lease.state()


def test_lease_live_before_expiry(tmp):
    st = _lease("2099-01-01T00:00:00Z", tmp)
    check("lease live before its deadline", st["live"] is True)


def test_lease_dead_after_expiry(tmp):
    st = _lease("2000-01-01T00:00:00Z", tmp)
    check("lease dead after its deadline", st["live"] is False)
    check("expiry names the lease and the time", "expired at" in st["why"])


def test_require_raises_when_expired(tmp):
    _lease("2000-01-01T00:00:00Z", tmp)
    try:
        lease.require("codex_invoke")
        check("require raises past expiry", False)
    except lease.LeaseExpired:
        check("require raises past expiry", True)


def test_unknown_class_raises_rather_than_permitting(tmp):
    """It used to RETURN a permissive dict, which said yes to a misspelling under a dead lease."""
    _lease("2000-01-01T00:00:00Z", tmp)
    try:
        lease.require("writing_a_design_doc")
        check("an unknown action class is refused, not permitted", False)
    except lease.UnknownActionClass:
        check("an unknown action class is refused, not permitted", True)
    except lease.LeaseExpired:
        check("an unknown class raises UnknownActionClass, not LeaseExpired", False)


def test_max_actions_is_enforced_not_merely_recorded(tmp):
    """A secondary bound nobody reads is the ten-action sunset again."""
    lease.LEASES = tmp
    if tmp.exists():
        tmp.unlink()
    lease.grant("cap", "2099-01-01T00:00:00Z", "test", "evidence", max_actions=1)
    try:
        lease.require("round")
        check("max_actions blocks once the log passes the cap", True)
    except lease.LeaseExpired as expired:
        check("max_actions blocks once the log passes the cap", "max_actions" in str(expired))


def test_no_lease_at_all_is_unauthorised(tmp):
    lease.LEASES = tmp
    if tmp.exists():
        tmp.unlink()
    check("no lease means unauthorised, not permitted", lease.state()["live"] is False)


def test_grant_appends_and_never_edits(tmp):
    lease.LEASES = tmp
    if tmp.exists():
        tmp.unlink()
    lease.grant("a", "2099-01-01T00:00:00Z", "test", "first")
    lease.grant("b", "2099-01-01T00:00:00Z", "test", "second")
    rows = lease.read_leases()
    check("both leases survive; the superseded one is not removed", len(rows) == 2)
    check("the new lease names what it supersedes", rows[1]["supersedes"] == "a")
    check("current() is the newest", lease.current()["lease_id"] == "b")


def test_there_is_no_force_flag():
    """The prose SAYS there is no --force, so grepping the source matches its own explanation.

    Check the module's actual surface instead: no callable that could waive expiry, and
    `require` taking nothing but the action class.
    """
    import inspect
    names = [n for n in dir(lease) if any(w in n.lower() for w in ("force", "override", "waive",
                                                                  "bypass", "skip"))]
    check(f"the lease exposes no waiver callable (found {names})", names == [])
    params = list(inspect.signature(lease.require).parameters)
    check("require() takes only the action class", params == ["action_class"])


import pathlib, tempfile as _tf                                             # noqa: E402
_tmp = pathlib.Path(_tf.mkdtemp()) / "leases.jsonl"
_saved = lease.LEASES
for _fn in (test_lease_live_before_expiry, test_lease_dead_after_expiry,
            test_require_raises_when_expired, test_unknown_class_raises_rather_than_permitting,
            test_max_actions_is_enforced_not_merely_recorded,
            test_no_lease_at_all_is_unauthorised, test_grant_appends_and_never_edits):
    if _tmp.exists():
        _tmp.unlink()
    _fn(_tmp)
test_there_is_no_force_flag()
lease.LEASES = _saved

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get
#  counted, and the file then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
