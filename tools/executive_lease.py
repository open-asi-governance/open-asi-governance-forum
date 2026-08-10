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

The calendar bound is primary
------------------------------
Two bounds are recorded, and the DATE is the one that matters: a count of actions can be evaded by
not logging, while a deadline cannot be evaded by undercounting anything. It is stored and compared
in **UTC**, stated explicitly, because an unstated timezone is a free day of slack.

There is no override
---------------------
Deliberately no `--force`. Expiry is the checkpoint working as designed, not an outage to route
around, and a generic override would become habitual exactly when the review is most overdue.
Renewal appends a NEW lease to `record/executive/leases.jsonl` naming who renewed it, on what
evidence, and to what limit. That file is append-only: a superseded lease stays visible, so the
history of how often this layer asked for more time is part of the record rather than a diff.

What this does not do
----------------------
It does not bind anything that never calls it. A shell command, a direct `git push`, or an edit
made without going through a tool that checks is unaffected — the same limit every control in this
layer has. It also cannot attest that its own source is unmodified; that needs a pin held outside
this repository, which does not exist yet.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEASES = REPO_ROOT / "record" / "executive" / "leases.jsonl"

#  Every action class that must hold a live lease. Named rather than defaulted-open: a class
#  absent from this list is unchecked, and that should be visible here rather than inferred.
GOVERNED_ACTIONS = ("round", "governed_write", "commit", "push", "codex_invoke")


class LeaseExpired(RuntimeError):
    """Raised before an action begins. Not an error in the work — the sunset arriving."""


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


def state() -> dict:
    """Whether an action may begin, and on which bound it turns."""
    lease = current()
    if lease is None:
        return {"live": False, "why": "no lease has ever been written; the layer is unauthorised",
                "lease": None}
    expires = datetime.fromisoformat(lease["expires_utc"].replace("Z", "+00:00"))
    remaining = (expires - _now()).total_seconds()
    if remaining <= 0:
        return {"live": False, "lease": lease,
                "why": (f"lease {lease['lease_id']} expired at {lease['expires_utc']} "
                        f"({-remaining/3600:.1f} h ago); renewal is the custodian's decision")}
    return {"live": True, "lease": lease, "hours_remaining": remaining / 3600,
            "why": (f"lease {lease['lease_id']} runs to {lease['expires_utc']} "
                    f"({remaining/3600:.1f} h remaining)")}


def require(action_class: str) -> dict:
    """Call BEFORE the action. Raises LeaseExpired rather than returning a value to ignore."""
    if action_class not in GOVERNED_ACTIONS:
        #  Not silently permitted: an unrecognised class is recorded as unchecked so the gap
        #  appears in the log an auditor reads, not only in this module's tuple.
        return {"live": True, "why": f"{action_class!r} is not a leased action class",
                "coverage": "observed_unprofiled"}
    st = state()
    if not st["live"]:
        raise LeaseExpired(st["why"])
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
    st = state()
    lease = st.get("lease")
    if lease:
        print(f"  lease:    {lease['lease_id']}  granted {lease['granted_utc']} "
              f"by {lease['granted_by']}")
        print(f"  expires:  {lease['expires_utc']} (UTC, stated)")
        if lease.get("supersedes"):
            print(f"  supersedes: {lease['supersedes']}")
        print(f"  evidence: {lease['evidence']}")
    print(f"  live:     {st['live']}\n    {st['why']}")
    print(f"  leased action classes: {', '.join(GOVERNED_ACTIONS)}")
    return 0 if st["live"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
