#!/usr/bin/env python3
"""The capture lifecycle: an append-only event log per round, and the state machine over it.

Replaces three loosely coupled records the design previously proposed -- a round
manifest tracking progress, a separate send receipt, and a split capture-audit
artifact. A hash link between artifacts proves association and immutability, not
semantic agreement: a contribution could exist with no audit, an audit could cite
the wrong digest, and an override could contradict the contribution's own gate
results with nothing detecting it. One artifact with one write has no pair to
disagree.

    planned ──▶ sent_attested ──▶ returned_pending_review ──▶ accepted
                                            │                      ▲
                                            └──▶ returned_clean ───┘
                                            │
                                            └──▶ rejected

WHY BYTES ARE WRITTEN BEFORE ANYTHING IS VALIDATED
--------------------------------------------------
`capture_response.py` has seventeen refusal sites. Today they are harmless: it
reads `--response` from a file the custodian already holds, so a refusal loses
nothing. Under the capture UI **the paste is the only copy**, and seventeen
refusal sites become seventeen ways to lose a frontier model's reply.

So `receive()` writes the bytes to `record/quarantine/` FIRST and validates after.
Validation gates *promotion into the corpus*; it never gates *preservation*. That
is GOVERNANCE.md section 3 read directly: the secretary must not hold unilateral
control over what evidence is preserved, and "original outputs must remain
available alongside any summary."

WHY A PENDING CAPTURE BLOCKS ROUND COMPLETION
---------------------------------------------
Quarantine that nobody opens is a silent refusal with extra steps, and preserving
bytes into a directory nobody reads achieves nothing. So `returned_pending_review`
is a first-class state that appears in the round's completeness accounting, and
`round_status()` reports a round holding one as NOT complete. Disposition is
mandatory: accepted or rejected, with an actor and a reason. A rejected capture
keeps its bytes -- rejection is a recorded state, never a deletion.

APPEND-ONLY, AND WHAT THAT DOES NOT MEAN
-----------------------------------------
The log is append-only by construction here -- nothing in this module rewrites a
line. It is a plain file in a git repository, so it can be edited by anyone who can
edit the repository. It records history; it does not enforce it. Tamper-evidence is
Track D's signing work (T-16), and until that lands this log is testimony by the
custodian, not proof. Saying otherwise would be D-13: a field asserting a property
the system does not have.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

LIFECYCLE_VERSION = "oagrc-capture-lifecycle-0.1"

#  Terminal states are `accepted` and `rejected`. Everything else owes a disposition.
TRANSITIONS: dict[str, set[str]] = {
    "planned":                {"sent_attested"},
    "sent_attested":          {"returned_clean", "returned_pending_review"},
    "returned_clean":         {"accepted", "rejected"},
    "returned_pending_review": {"accepted", "rejected"},
    "accepted":               set(),
    "rejected":               set(),
}
OPEN_STATES = {"planned", "sent_attested", "returned_clean", "returned_pending_review"}
NEEDS_DISPOSITION = {"returned_clean", "returned_pending_review"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def log_path(round_id: str) -> Path:
    return REPO_ROOT / "record" / "rounds" / f"{round_id}-lifecycle.jsonl"


def quarantine_path(round_id: str, party_slug: str, index: int, suffix: str = ".md") -> Path:
    return REPO_ROOT / "record" / "quarantine" / round_id / f"{party_slug}-{index:02d}{suffix}"


def read_events(round_id: str) -> list[dict]:
    path = log_path(round_id)
    if not path.exists():
        return []
    events = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise ValueError(f"{path.name} line {line_no} is not valid JSON: {error}") from error
    return events


def append_event(round_id: str, event: dict) -> dict:
    """Append one event. Never rewrites, never reorders, never deduplicates."""
    existing = read_events(round_id)
    event = {
        "event_id": f"{round_id}-{len(existing) + 1:04d}",
        "lifecycle_version": LIFECYCLE_VERSION,
        "ts_utc": utc_now(),
        **event,
    }
    path = log_path(round_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def current_state(round_id: str, identity: str) -> str | None:
    """Last recorded state for a party, or None if the party has no events."""
    state = None
    for event in read_events(round_id):
        if event.get("identity") == identity and "state" in event:
            state = event["state"]
    return state


def check_transition(round_id: str, identity: str, new_state: str) -> tuple[bool, str]:
    """Validate a transition without performing it."""
    if new_state not in TRANSITIONS:
        return False, f"unknown state {new_state!r}"
    old = current_state(round_id, identity)
    if old is None:
        if new_state != "planned":
            return False, f"first event for {identity!r} must be 'planned', not {new_state!r}"
        return True, ""
    if new_state not in TRANSITIONS[old]:
        allowed = ", ".join(sorted(TRANSITIONS[old])) or "none — this is a terminal state"
        return False, f"{identity!r} is {old!r}; cannot move to {new_state!r}. Allowed: {allowed}"
    return True, ""


def transition(round_id: str, identity: str, new_state: str, actor: str, **detail) -> dict:
    ok, why = check_transition(round_id, identity, new_state)
    if not ok:
        raise ValueError(why)
    if new_state in ("accepted", "rejected") and not detail.get("reason"):
        raise ValueError(f"a disposition to {new_state!r} requires a stated reason")
    return append_event(round_id, {"identity": identity, "state": new_state, "actor": actor, **detail})


def receive(round_id: str, identity: str, party_slug: str, response_text: str,
            actor: str, gate_results: list[dict], state: str, index: int = 1, **detail) -> dict:
    """Preserve the bytes, THEN record the outcome. Order is the point.

    Writes the response to record/quarantine/ before any validation runs, so no
    refusal path can destroy a paste that exists nowhere else. Refuses to overwrite
    an existing quarantine file: response bytes are immutable from first receipt,
    under every later disposition.
    """
    target = quarantine_path(round_id, party_slug, index)
    if target.exists():
        raise ValueError(
            f"{target.relative_to(REPO_ROOT)} already exists. Response bytes are immutable from "
            f"first receipt; a correction is a new capture, never an overwrite."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(response_text, encoding="utf-8")

    return transition(
        round_id, identity, state, actor,
        preserved_at=str(target.relative_to(REPO_ROOT)),
        response_sha256=sha256_of_text(response_text),
        response_bytes=len(response_text.encode("utf-8")),
        gate_results=gate_results,
        **detail,
    )


def round_status(round_id: str, expected_parties: list[str]) -> dict:
    """Per-party state and whether the round may be reported complete.

    A round is complete only when every expected party has reached a terminal
    state. Anything pending review keeps the round open and visible -- that is what
    stops quarantine from becoming a silent refusal.
    """
    states = {p: current_state(round_id, p) or "planned" for p in expected_parties}
    pending = sorted(p for p, s in states.items() if s in NEEDS_DISPOSITION)
    outstanding = sorted(p for p, s in states.items() if s in OPEN_STATES)
    return {
        "round": round_id,
        "states": states,
        "outstanding": outstanding,
        "awaiting_disposition": pending,
        "complete": not outstanding,
        "complete_blocked_by": pending,
        "accepted": sorted(p for p, s in states.items() if s == "accepted"),
        "rejected": sorted(p for p, s in states.items() if s == "rejected"),
    }


def validate_log(round_id: str, expected_parties: list[str] | None = None) -> list[str]:
    """Replay the log and report every violation. Used by validate_provenance.py."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    state_by_party: dict[str, str] = {}

    for event in read_events(round_id):
        eid = event.get("event_id", "<missing>")
        if eid in seen_ids:
            errors.append(f"duplicate event_id {eid}")
        seen_ids.add(eid)

        identity, new_state = event.get("identity"), event.get("state")
        if new_state is None:
            continue
        if identity is None:
            errors.append(f"{eid}: event carries a state but no identity")
            continue
        old = state_by_party.get(identity)
        if old is None:
            if new_state != "planned":
                errors.append(f"{eid}: {identity!r} first appears as {new_state!r}, not 'planned'")
        elif new_state not in TRANSITIONS.get(old, set()):
            errors.append(f"{eid}: {identity!r} moved {old!r} -> {new_state!r}, which is not a legal transition")
        if new_state in ("accepted", "rejected") and not event.get("reason"):
            errors.append(f"{eid}: disposition to {new_state!r} carries no reason")
        preserved = event.get("preserved_at")
        if preserved:
            path = REPO_ROOT / preserved
            if not path.exists():
                errors.append(f"{eid}: preserved response is missing: {preserved}")
            elif sha256_of_text(path.read_text(encoding="utf-8")) != event.get("response_sha256"):
                errors.append(f"{eid}: preserved response no longer matches its recorded hash: {preserved}")
        state_by_party[identity] = new_state

    for party in expected_parties or []:
        if party not in state_by_party:
            errors.append(f"declared party {party!r} has no lifecycle events")
    return errors
