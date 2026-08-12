#!/usr/bin/env python3
"""The trial's sunset, as a lease checked BEFORE an action begins.

    python3 tools/executive_lease.py                        # report the current lease
    from executive_lease import require; require("round")   # raises if the lease has expired

Why a lease and not an attestation refusal
-------------------------------------------
The first sunset was "this trial ends at ten actions". It was passed at twenty-three and nothing
stopped, because nothing checked. The obvious repair — make `executive_log.attest()` refuse past
the limit — was reviewed by Codex and rejected as too late by construction:

* attestation happens *after* the work, so the action has already occurred when the refusal fires;
* the actor can simply not attest;
* unprofiled paths never reach the gate at all;
* counting "attested actions" rewards under-logging, which is the opposite incentive;
* the same layer can edit the gate.

So the check moves to the front. `require()` is called before a paid round, a governed write, a
commit, a push, or a Codex invocation. A reserved action that has already begun may finish and
attest after expiry — killing work mid-flight would corrupt the record it is meant to protect —
but no new action may begin.

The calendar bound is primary — in ONE sense, and the two senses were being conflated
--------------------------------------------------------------------------------------
The claim used to be flat: "the DATE is the one that matters", because a count of actions can be
evaded by not logging while a deadline cannot be evaded by undercounting anything. That is true
and it is about **evadability**. It was being read as a second claim — that the date is the bound
which actually stops work — and *that* is false in practice: **trial-02 and trial-03 both ended
on the count**, trial-03 with about 275 calendar hours still unspent. Codex separated the two on
2026-08-12 and the docstring now separates them too. The calendar bound is the harder one to
cheat. The action bound is the one that has done the stopping, twice, which makes it a work
budget in effect whatever it is called.

WHAT max_actions ACTUALLY COUNTS, stated because it is not what the name suggests
---------------------------------------------------------------------------------
It counts **rows appended to the executive action log** inside the lease's epoch. It does not
count the action classes `require()` authorises. The 200 rows that exhausted trial-03 were 56
`test`, 56 `push`, 46 `deploy`, 21 `codex_invoke` and 21 `codex_return_captured`; a `commit`, a
`governed_write` and a `round` each contribute nothing at all, while `deploy` and
`codex_return_captured` — neither of them a governed class — consume the budget. So one landing
spends about three, one Codex call spends two, and a lease of 400 is roughly 130 landings' worth
of rows rather than 400 permitted actions.

That mismatch is a real defect (D-64) and it is **not fixed here**, deliberately. Careful about
why: the custodian said *"Renew the lease to 400"*, and the semantic mismatch was identified
AFTERWARDS — so it is wrong to say the grant was made "over the row unit" as though the unit had
been put to them. What is true is narrower: this preserves the metric that was implemented when
the grant was made, pending an explicit choice, because silently redefining it would change the
size of a permission without anyone deciding to. What is fixed here is the silent part —
the unit is now named in the report, and the mismatch is on the record for the custodian to rule
on. A pre-action *reservation* ledger, which is what would actually make the number mean
"actions", is designed in D-64 and not built.

An unreadable count is not a zero
----------------------------------
The count used to be computed inside `try: ... except Exception: spent = 0`. Any failure — a
truncated line, a permissions error, or merely importing this module by path so that
`import executive_log` did not resolve — handed an exhausted lease **unlimited actions**. That is
control 4 failing open inside the lease, and control 53 violated in the one mechanism whose job
is to refuse: an unreadable measurement rendered as the most favourable value.

So the count is now a **typed observation** with its own states, and only `COUNTED` is a number.
`UNAVAILABLE` refuses — with its own exception type and its own words, because "the count cannot
be read" and "the lease is exhausted" are different facts and control 53 forbids coercing the
first into the second.

Why a broken hash chain refuses, and why four breaks do not
------------------------------------------------------------
A count over a log that can be rewritten is not evidence. The chain is therefore verified before
the count is believed. But the live log has **four genuine breaks**, all from the 2026-08-11
redaction: the custodian was asked to remove a correspondent's name, four action rows carried it
in their `note`, and removing it changed those rows' bytes. Refusing outright there would have
converted an obligatory redaction into a total work stoppage — and the operator's next move,
predictably, is to disable the check.

The route out is the one the corpus already uses for material that must be removed: an
**authorised, recorded discontinuity**. `record/executive/action-log-discontinuities.json` names
each break by position and pins BOTH hashes — the one stored on the breaking row and the one its
predecessor now computes to. An unrecorded break refuses. A recorded one that has since moved
also refuses, because the pin no longer matches. What is excused is one exact, argued edit, not
"edits at this position".

There is no override
---------------------
Deliberately no `--force`. Expiry is the checkpoint working as designed, not an outage to route
around, and a generic override would become habitual exactly when the review is most overdue.
Renewal appends a NEW lease to `record/executive/leases.jsonl` naming who renewed it, on what
evidence, and to what limit. That file is append-only: a superseded lease stays visible, so the
history of how often this layer asked for more time is part of the record rather than a diff.

Codex called the recovery path for an unreadable log "defensible and not necessarily --force",
on one condition: the constrained layer gets no waiver argument and no repair command. It has
neither. Restoring readable evidence, or issuing a superseding lease that establishes a fresh
count epoch, is the custodian's move and is visible in an append-only file when made.

What this does not do
----------------------
It does not bind anything that never calls it. A shell command, a direct `git push`, or an edit
made without going through a tool that checks is unaffected — the same limit every control in this
layer has. It also cannot attest that its own source is unmodified; that needs a pin held outside
this repository, which does not exist yet.

It is **not a security boundary and not a runaway detector**, and saying so is part of the fix.
The count comes from a log this layer writes about itself: under-logging still shrinks it, one
authorised action can still append several rows, and two callers at `cap - 1` can still both be
admitted. It is a checkpoint that makes ordinary work stop and ask.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEASES = REPO_ROOT / "record" / "executive" / "leases.jsonl"
DISCONTINUITIES = REPO_ROOT / "record" / "executive" / "action-log-discontinuities.json"

#  Every action class that must hold a live lease. Named rather than defaulted-open: a class
#  absent from this list is unchecked, and that should be visible here rather than inferred.
GOVERNED_ACTIONS = ("round", "governed_write", "commit", "push", "codex_invoke")

#  What the number in `max_actions` is a number OF. Printed with every report, because the whole
#  D-64 finding is that a bound whose unit is unstated gets read as the unit its name suggests.
COUNT_UNIT = "rows appended to record/executive/action-log.jsonl within the lease epoch"

#  Typed states for the count. Only COUNTED carries a number; the rest are answers, not values.
NOT_CONFIGURED = "NOT_CONFIGURED"      # the lease sets no max_actions
NOT_EVALUATED = "NOT_EVALUATED"        # another bound already refused; the log was not read
COUNTED = "COUNTED"
UNAVAILABLE = "UNAVAILABLE"            # the count cannot be shown; this REFUSES


class LeaseRefused(RuntimeError):
    """Base for every refusal to admit an action. Callers should catch THIS.

    Introduced because `codex_call.py` caught `LeaseExpired` by name, so a refusal of any other
    kind would have escaped as a traceback rather than as a logged, attested refusal — the
    difference between a governed stop and a crash.
    """


class LeaseExpired(LeaseRefused):
    """The CALENDAR bound has passed. Kept as a distinct name because callers cite it."""


class LeaseBoundReached(LeaseRefused):
    """The action bound has been reached. The calendar bound may be nowhere near."""


class LeaseEvidenceUnavailable(LeaseRefused):
    """The bound cannot be shown to hold, so the action may not begin.

    Deliberately NOT a subclass of LeaseExpired and deliberately worded differently. Calling an
    unreadable count "exhausted" would be the same coercion of an unknown into a value that
    made the defect, moved one level up into the error message.
    """


class UnknownActionClass(RuntimeError):
    """A caller asked permission for a class this module does not recognise.

    Distinct from LeaseRefused because it means something different: the lease is not saying no,
    it is saying it does not know what was asked. The first version RETURNED a permissive dict
    here, marked `observed_unprofiled`, which permitted a misspelled class even under an expired
    lease — recreating the exact taxonomy hole the lease was built to close. `observed_unprofiled`
    is a fine label when reconciling an effect discovered after the fact; it is not an answer a
    pre-action permission API may give.
    """


def _now() -> datetime:
    return datetime.now(timezone.utc)


def read_leases() -> list[dict]:
    if not LEASES.is_file():
        return []
    return [json.loads(line) for line in LEASES.read_text().splitlines() if line.strip()]


def current() -> dict | None:
    """The most recently appended lease. Superseded ones stay in the file, unedited."""
    leases = read_leases()
    return leases[-1] if leases else None


def calendar_state() -> dict:
    """The date bound alone. A pure calculation over the lease and the clock — no I/O beyond
    the lease file, so it cannot fail in the ways the count can."""
    lease = current()
    if lease is None:
        return {"live": False, "lease": None,
                "why": "no lease has ever been written; the layer is unauthorised"}
    expires = datetime.fromisoformat(lease["expires_utc"].replace("Z", "+00:00"))
    remaining = (expires - _now()).total_seconds()
    if remaining <= 0:
        return {"live": False, "lease": lease,
                "why": (f"lease {lease['lease_id']} expired at {lease['expires_utc']} "
                        f"({-remaining/3600:.1f} h ago); renewal is the custodian's decision")}
    return {"live": True, "lease": lease, "hours_remaining": remaining / 3600,
            "why": (f"lease {lease['lease_id']} runs to {lease['expires_utc']} "
                    f"({remaining/3600:.1f} h remaining)")}


def _load_executive_log():
    """Locate `executive_log` RELATIVE TO THIS FILE, never via the caller's sys.path.

    The bare `import executive_log` this replaces only resolved when the caller happened to have
    `tools/` on the path. Several of our own tools load modules by path, and for those the import
    raised, the bare `except` swallowed it, and the cap silently vanished. Robustness here is a
    safety property rather than a convenience: a gate that refuses everyone who loads it the
    wrong way gets routed around within the day.
    """
    path = Path(__file__).resolve().parent / "executive_log.py"
    if not path.is_file():
        raise FileNotFoundError(f"executive_log.py is not beside this module at {path}")
    spec = importlib.util.spec_from_file_location("_executive_log_for_lease", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _row_hash(row: dict) -> str:
    """Must match `executive_log.attest`'s hashing exactly, or every row looks tampered with."""
    return hashlib.sha256(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _instant(value) -> datetime | None:
    """Parse a stamp into a timezone-aware instant, or None. NEVER a permissive fallback.

    The first version of this repair only required a non-empty string and then compared stamps
    LEXICALLY. Codex fed it a row stamped `"zzzz"` and got COUNTED. Lexical comparison is also
    wrong for valid RFC 3339 stamps carrying different offsets, where string order and
    chronological order come apart.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    #  A naive stamp is an unknown instant, not a UTC one. Assuming UTC here would be the same
    #  coercion this module exists to refuse, one field down.
    return parsed if parsed.tzinfo is not None else None


def authorised_discontinuities() -> list[dict]:
    """Chain breaks the custodian's record accounts for. An unreadable register is not an empty
    one: a malformed file raises here rather than quietly excusing nothing (or everything)."""
    if not DISCONTINUITIES.is_file():
        return []
    doc = json.loads(DISCONTINUITIES.read_text(encoding="utf-8"))
    entries = doc.get("discontinuities")
    if not isinstance(entries, list):
        raise ValueError(f"{DISCONTINUITIES.name} has no 'discontinuities' list")
    required = ("utc", "action", "stored_prev_sha256", "computed_prev_sha256",
                "reason", "authority")
    for position, entry in enumerate(entries):
        #  `{"discontinuities": [7]}` used to leak an AttributeError out of the caller's guarded
        #  read, because the shape was only assumed once the list itself had parsed.
        if not isinstance(entry, dict):
            raise ValueError(f"discontinuity {position} is {type(entry).__name__}, not an object")
        missing = [k for k in required if not str(entry.get(k, "")).strip()]
        if missing:
            #  reason and authority are REQUIRED, not decorative. A break excused by four hash
            #  values and nothing else is a waiver; what makes it a tombstone is that somebody
            #  had to write down who authorised it and why.
            raise ValueError(f"discontinuity {position} ({entry.get('utc')}) is missing "
                             f"{', '.join(missing)}")
    return entries


def _anchor(source: Path) -> tuple[bytes | None, str]:
    """The log as GIT last committed it, which is the only copy this layer did not just write.

    A hash chain detects an unrecomputed interior edit and NOTHING ELSE. Codex reproduced four
    ways past the first version of this check — rewrite the final row, rewrite the whole history
    and recompute every link, truncate the file to empty, or supply a stale register entry — all
    of which it returned COUNTED for. A chain without an external checkpoint is not evidence of
    anything; it is a checksum the writer controls.

    Git is the checkpoint available here: the log is committed and pushed, so `HEAD`'s blob is a
    copy that exists outside this working tree. The rule is APPEND-ONLY — the working file must
    begin with exactly the committed bytes. That catches truncation, a tail edit, a deleted
    suffix, and a full rechain. It does NOT catch an edit to a row appended since the last
    commit, and saying so is part of the check rather than a footnote.
    """
    try:
        rel = Path(source).resolve().relative_to(REPO_ROOT)
    except ValueError:
        return None, f"{source} is outside the repository, so git holds no copy of it"
    proc = subprocess.run(["git", "show", f"HEAD:{rel.as_posix()}"], cwd=REPO_ROOT,
                          capture_output=True)
    if proc.returncode != 0:
        return None, (f"git holds no committed copy of {rel.as_posix()} at HEAD "
                      f"({(proc.stderr or b'').decode(errors='replace').strip()[:120]}), so the "
                      f"log cannot be checked against anything outside this working tree")
    return proc.stdout, ""


def count_state(lease: dict | None, *, log_path: Path | None = None) -> dict:
    """Observe the action count. Returns a typed state; NEVER a bare number, never a default.

    Every way of failing to see the log ends in UNAVAILABLE with a reason, including the ones
    `read_log()` used to absorb: a missing file reads as an empty list there, which is the
    absence-as-zero pattern this repository has now filed four deficiencies about.
    """
    if lease is None:
        return {"state": NOT_EVALUATED, "why": "no lease to count against"}
    cap = lease.get("max_actions")
    if cap is None:
        return {"state": NOT_CONFIGURED, "cap": None,
                "why": "this lease sets no max_actions; only the calendar bound applies"}
    #  `if cap:` was the old test, so a cap of 0 — "you may begin nothing" — skipped the check
    #  entirely and authorised everything. bool is excluded explicitly because it is an int.
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 0:
        return {"state": UNAVAILABLE, "cap": cap,
                "why": f"max_actions is {cap!r}, which is not a non-negative integer, so no "
                       f"bound can be evaluated from it"}

    epoch = lease.get("granted_utc")
    epoch_at = _instant(epoch)
    if epoch_at is None:
        return {"state": UNAVAILABLE, "cap": cap,
                "why": f"the lease's granted_utc is {epoch!r}, which is not a parseable instant, "
                       f"so its epoch cannot be delimited"}

    #  A PARAMETER, NOT AN AMBIENT GLOBAL. The first version of this repair put the fixture hook
    #  in a module-level `COUNT_SOURCE`, and Codex immediately used it to authorise an exhausted
    #  lease: set it to an empty file and `require()` returned GRANTED with spent 0. A hook that
    #  every caller silently inherits is a fail-open by another name — a production caller that
    #  passes nothing now cannot be redirected by a stray assignment somewhere else in the
    #  process.
    source = log_path
    default_source = source is None
    if default_source:
        try:
            source = getattr(_load_executive_log(), "LOG_PATH", None)
        except Exception as exc:                                        # noqa: BLE001
            return {"state": UNAVAILABLE, "cap": cap, "source_is_default": True,
                    "why": f"the action log module could not be loaded ({exc}), so the count "
                           f"cannot be shown. THIS IS THE D-64 PATH: it used to be zero."}
    marks = {"cap": cap, "source": str(source), "source_is_default": default_source}
    if source is None or not Path(source).is_file():
        return {"state": UNAVAILABLE, **marks,
                "why": f"the action log {source} is absent, so the count cannot be shown. An "
                       f"absent log is not an empty one."}

    rows, stamps, prev, breaks = [], [], "0" * 64, []
    try:
        raw = Path(source).read_bytes()
    except OSError as exc:
        return {"state": UNAVAILABLE, **marks,
                "why": f"the action log could not be read ({exc}); a permissions or device error "
                       f"is not a count of zero"}

    #  THE EXTERNAL CHECKPOINT, before a single row is believed. Only for the real log: an
    #  injected fixture path is outside git by construction, and the marks already say so.
    if default_source:
        committed, why_not = _anchor(Path(source))
        if committed is None:
            return {"state": UNAVAILABLE, **marks, "why": why_not}
        if not raw.startswith(committed):
            return {"state": UNAVAILABLE, **marks,
                    "why": f"the working action log does not begin with the {len(committed)} "
                           f"bytes git committed at HEAD, so it has been truncated, rewritten or "
                           f"re-chained rather than appended to. A hash chain cannot detect that "
                           f"on its own; only a copy this layer did not write can."}

    for number, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            return {"state": UNAVAILABLE, **marks,
                    "why": f"action log line {number} does not parse ({exc}); a count over a log "
                           f"that cannot be read in full is not a count"}
        if not isinstance(row, dict):
            return {"state": UNAVAILABLE, **marks,
                    "why": f"action log line {number} is not an object"}
        stamp = _instant(row.get("utc"))
        if stamp is None:
            return {"state": UNAVAILABLE, **marks,
                    "why": f"action log line {number} has no usable utc ({row.get('utc')!r}), so "
                           f"it cannot be placed inside or outside the lease epoch. The old count "
                           f"dropped such rows silently via .get('utc', ''); the first version of "
                           f"this repair accepted any non-empty string and counted a row stamped "
                           f"'zzzz'."}
        #  NOT stored on the row. `_row_hash` hashes the row as written, so adding a derived
        #  field here would change every hash and break the chain this loop is verifying.
        stamps.append(stamp)
        if row.get("prev_sha256") != prev:
            breaks.append({"utc": row["utc"], "action": row.get("action"),
                           "stored_prev_sha256": row.get("prev_sha256"),
                           "computed_prev_sha256": prev, "line": number})
        prev = _row_hash(row)
        rows.append(row)

    if breaks:
        try:
            authorised = authorised_discontinuities()
        except Exception as exc:                                        # noqa: BLE001
            return {"state": UNAVAILABLE, **marks,
                    "why": f"the chain is broken and the discontinuity register could not be "
                           f"read ({exc}), so no break can be shown to be authorised"}
        pinned = {(a.get("utc"), a.get("action"), a.get("stored_prev_sha256"),
                   a.get("computed_prev_sha256")) for a in authorised}
        unrecorded = [b for b in breaks
                      if (b["utc"], b["action"], b["stored_prev_sha256"],
                          b["computed_prev_sha256"]) not in pinned]
        if unrecorded:
            first = unrecorded[0]
            return {"state": UNAVAILABLE, **marks, "breaks": breaks,
                    "why": f"{len(unrecorded)} unrecorded break(s) in the action-log hash chain, "
                           f"first at line {first['line']} ({first['utc']} {first['action']}). "
                           f"A count over a log that has been rewritten without a recorded, "
                           f"pinned reason is not evidence. Record it in "
                           f"{DISCONTINUITIES.name} or restore the log."}

    #  Compared as INSTANTS, not as strings. Lexical comparison of RFC 3339 stamps with
    #  different offsets orders them wrongly, and the epoch itself was never parsed at all.
    spent = sum(1 for stamp in stamps if stamp >= epoch_at)
    return {"state": COUNTED, **marks, "spent": spent, "remaining": cap - spent,
            "epoch": epoch, "unit": COUNT_UNIT, "authorised_breaks": len(breaks),
            "why": f"{spent} of {cap} ({COUNT_UNIT}) since {epoch}"}


def authorization_state(*, log_path: Path | None = None) -> dict:
    """The SOLE composite decision. Both `require()` and the CLI read this one function.

    They used to compute independently — `require()` looked at both bounds, the CLI at only the
    calendar — so the CLI could print a live lease while a landing was being refused. Two
    functions answering the same question differently is how a green signal stops being
    downstream of what it certifies.
    """
    cal = calendar_state()
    if not cal["live"]:
        #  The log is not read at all: one refusal is enough, and reading it here would let an
        #  unreadable log turn a plain expiry into a confusing evidence failure.
        return {**cal, "count": {"state": NOT_EVALUATED,
                                 "why": "the calendar bound already refuses"},
                "refusal": ("expired", cal["why"])}
    count = count_state(cal["lease"], log_path=log_path)
    out = {**cal, "count": count}
    if count["state"] == UNAVAILABLE:
        return {**out, "live": False,
                "refusal": ("evidence_unavailable", count["why"]),
                "why": f"{cal['why']}; but {count['why']}"}
    if count["state"] == COUNTED and count["spent"] >= count["cap"]:
        return {**out, "live": False,
                "refusal": ("bound_reached",
                            f"lease {cal['lease']['lease_id']} has {count['spent']} log "
                            f"rows against a max_actions of {count['cap']}. The calendar "
                            f"bound has not arrived, but this one has. Renewal is the "
                            f"custodian's decision. The unit is {COUNT_UNIT}."),
                "why": f"{cal['why']}; {count['why']}"}
    if count["state"] == COUNTED:
        #  ROWS, not actions. The old names continued the semantic error D-64 is about.
        out["rows_spent"], out["rows_remaining"] = count["spent"], count["remaining"]
    return {**out, "refusal": None}


#  Kept as the public name it has always had. It is now the composite, so every existing caller
#  that asked "may an action begin?" gets the answer to that question rather than half of it.
state = authorization_state


def require(action_class: str, *, log_path: Path | None = None) -> dict:
    """Call BEFORE the action. Raises rather than returning a value a caller can ignore.

    `log_path` exists for fixtures and is threaded explicitly rather than read from a module
    global, because a global every caller inherits is a fail-open: the first version of this
    repair had one, and Codex used it to authorise an exhausted lease by pointing it at an empty
    file. Production callers pass nothing and cannot be redirected from elsewhere in the process.
    """
    if action_class not in GOVERNED_ACTIONS:
        raise UnknownActionClass(
            f"{action_class!r} is not one of {GOVERNED_ACTIONS}. Add it deliberately, or call "
            f"the class that covers this action. A permission API that says yes to a name it "
            f"does not know is not a gate.")
    st = authorization_state(log_path=log_path)
    refusal = st.get("refusal")
    if refusal:
        kind, why = refusal
        raise {"expired": LeaseExpired,
               "bound_reached": LeaseBoundReached,
               "evidence_unavailable": LeaseEvidenceUnavailable}[kind](why)
    return st


def grant(lease_id: str, expires_utc: str, granted_by: str, evidence: str,
          max_actions: int | None = None, note: str = "") -> dict:
    """Append a new lease. Never edits or removes the one it supersedes."""
    lease = {"lease_id": lease_id, "granted_utc": _now().strftime("%Y-%m-%dT%H:%M:%SZ"),
             "expires_utc": expires_utc, "granted_by": granted_by, "evidence": evidence,
             "max_actions": max_actions, "note": note,
             "supersedes": (current() or {}).get("lease_id"),
             "authority": "delegated by the custodian; confers nothing on this layer"}
    LEASES.parent.mkdir(parents=True, exist_ok=True)
    with LEASES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(lease, sort_keys=True) + "\n")
    return lease


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit the authorization state")
    args = parser.parse_args()

    st = authorization_state()
    if args.json:
        print(json.dumps(st, indent=2, sort_keys=True, default=str))
        return 0 if st["live"] else 1

    lease = st.get("lease")
    if lease:
        print(f"  lease:    {lease['lease_id']}  granted {lease['granted_utc']} "
              f"by {lease['granted_by']}")
        print(f"  expires:  {lease['expires_utc']} (UTC, stated)")
        if lease.get("supersedes"):
            print(f"  supersedes: {lease['supersedes']}")
        print(f"  evidence: {lease['evidence']}")

    #  THE COUNT IS PRINTED. It was enforced and never reported, so this surface said "live" for
    #  the last twenty-three refusals of trial-03 and stayed exit 0 throughout.
    count = st.get("count") or {}
    print(f"  count:    {count.get('state')}")
    if count.get("state") == COUNTED:
        print(f"    {count['spent']} spent, {count['remaining']} remaining of {count['cap']}")
        print(f"    unit: {COUNT_UNIT}")
        print(f"    NOT the classes require() authorises — see D-64")
        if count.get("authorised_breaks"):
            print(f"    {count['authorised_breaks']} authorised chain discontinuity(ies)")
    else:
        print(f"    {count.get('why')}")

    print(f"  live:     {st['live']}\n    {st['why']}")
    print(f"  leased action classes: {', '.join(GOVERNED_ACTIONS)}")
    if st.get("refusal"):
        print(f"  REFUSING: {st['refusal'][0]}")
    return 0 if st["live"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
