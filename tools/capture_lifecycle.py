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


def latest_response_event(round_id: str, identity: str) -> dict | None:
    """The most recent event for a party that actually recorded a response hash.

    NOT the party's current state event. `accepted` and `rejected` are dispositions
    and carry no `response_sha256` -- only the receiving event (`returned_clean` or
    `returned_pending_review`) does. Verified against
    record/rounds/review-round-03-lifecycle.jsonl, where Grok's four events record
    the hash on `returned_clean` and not on `accepted`.

    This distinction is the whole reason Defect 7's obvious fix does not work. A
    check that reads "the recorded hash for this party" off the current state finds
    None on every accepted party -- which is every party a re-capture would collide
    with -- and then either crashes or, worse, treats absent as equal and skips.
    """
    for event in reversed(read_events(round_id)):
        if event.get("identity") == identity and event.get("response_sha256"):
            return event
    return None


def preserve_conflict(round_id: str, identity: str, response_text: str) -> Path:
    """Preserve bytes that collide with an already-recorded response.

    CONTENT-ADDRESSED, and not `<party>-02.md`. `capture_response.py` builds names
    as f"{slug}-{sample_index:02d}", so a numeric suffix is a claim that this is
    sample 2 of k -- a statement about sampling that a correction is not making.
    Naming a disputed receipt that way would file a contradiction as a data point.

    Lives under record/quarantine/, NOT corpus/raw/. Nothing here is corpus
    material: it is disputed bytes awaiting a custodian, and the corpus must not
    grow a second attributed response for a party while the dispute is open.

    Idempotent by construction. The same bytes hash to the same path, so an
    interrupted-and-retried ingest converges instead of accumulating duplicates.
    """
    digest = sha256_of_text(response_text)
    target = (REPO_ROOT / "record" / "quarantine" / round_id
              / f"{slug_identity(identity)}-conflict-{digest}.md")
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        if sha256_of_text(target.read_text(encoding="utf-8")) != digest:
            raise ValueError(
                f"hash-addressed conflict file does not match its own name: {target}. "
                f"Its bytes were changed after it was written."
            )
        return target

    # "x" fails if it appeared between the check and the write, rather than
    # silently truncating whatever is there.
    with target.open("x", encoding="utf-8") as handle:
        handle.write(response_text)
    return target


def slug_identity(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")


def record_conflict(round_id: str, identity: str, actor: str,
                    response_text: str, recorded_sha256: str) -> dict:
    """Append a NON-STATE conflict event and preserve the bytes.

    Deliberately does not transition the party. The recorded response keeps its
    disposition; what is recorded is that a DIFFERENT set of bytes was offered for
    a slot that is already taken. Inventing a state transition here would let an
    ingest silently un-accept material a custodian already accepted.

    Because it is not a state change, `round_status` must consult conflicts
    separately -- see `unresolved_conflicts`. Without that the round still reports
    COMPLETE and the defect becomes "preserved but invisible" instead of "lost".
    """
    preserved = preserve_conflict(round_id, identity, response_text)
    event = {
        "event": "conflicting_receipt",
        "round": round_id,
        "identity": identity,
        "actor": actor,
        "recorded_sha256": recorded_sha256,
        "conflicting_sha256": sha256_of_text(response_text),
        "conflicting_bytes": len(response_text.encode("utf-8")),
        "preserved_at": str(preserved.relative_to(REPO_ROOT)),
        "resolved": False,
    }
    path = log_path(round_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def conflict_status(round_id: str, identity: str, conflicting_sha256: str) -> str:
    """"none", "unresolved", or "resolved:<decision>" for one specific set of bytes.

    Keyed by the CONFLICTING HASH, not by party. A party can have more than one
    dispute, and resolving one must not appear to settle another.

    This exists because re-running an ingest is supposed to be safe, and the first
    version of the conflict path made it unsafe in two ways at once, both caught by
    running it three times rather than by reading it: every re-run appended another
    `conflicting_receipt` for the same bytes (three events, one dispute), and a
    re-run after a custodian resolved the dispute silently re-opened it. The second
    is the serious one -- an accidental repeat of a shell command would have
    reverted a recorded human decision with no message saying so.
    """
    status = "none"
    for event in read_events(round_id):
        if event.get("identity") != identity:
            continue
        if event.get("conflicting_sha256") != conflicting_sha256:
            continue
        if event.get("event") == "conflicting_receipt":
            status = "unresolved"
        elif event.get("event") == "conflict_resolved":
            status = f"resolved:{event.get('decision')}"
    return status


def corpus_holds(round_id: str, digest: str) -> bool:
    """Does corpus/raw/<round>/ actually contain a file with these bytes?

    Derived from the artifact, never from a label. This is the rule the whole
    module now follows after a false completion was found in the first version of
    the conflict resolver: a decision RECORDING that material should be published
    is not the material being published.
    """
    directory = REPO_ROOT / "corpus" / "raw" / round_id
    if not directory.is_dir():
        return False
    return any(sha256_of_text(path.read_text(encoding="utf-8")) == digest
               for path in directory.rglob("*") if path.is_file())


def unresolved_conflicts(round_id: str) -> list[dict]:
    """Conflicting receipts that are not yet settled IN THE CORPUS.

    A resolution names the conflicting hash it settles, so resolving one dispute
    does not clear another for the same party.

    THE TWO DECISIONS CLEAR DIFFERENTLY, and getting this wrong produced a false
    completion in the first version of `resolve_conflict.py`, written earlier the
    same day and caught by external review:

      confirm_recorded            clears immediately. The recorded response stands,
                                  the corpus is already correct, nothing is owed.

      supersede_with_conflicting  DOES NOT clear on the decision alone. It clears
                                  only once corpus/raw/<round>/ actually holds the
                                  conflicting bytes. Otherwise the custodian says
                                  "the correction is right", the block lifts, the
                                  round reports COMPLETE -- and the text the
                                  custodian just disowned is still what is
                                  published. The decision was recorded and the
                                  corpus was not changed, and only the label moved.

    So the supersede path is derived from the corpus, not from the event. A
    superseding artifact has to exist before the round can call itself finished.
    """
    conflicts: dict[str, dict] = {}
    for event in read_events(round_id):
        if event.get("event") == "conflicting_receipt":
            conflicts[event["conflicting_sha256"]] = event
        elif event.get("event") == "conflict_resolved":
            digest = event.get("conflicting_sha256")
            if event.get("decision") == "supersede_with_conflicting":
                if corpus_holds(round_id, digest):
                    conflicts.pop(digest, None)
                elif digest in conflicts:
                    conflicts[digest] = {
                        **conflicts[digest],
                        "awaiting": "superseding artifact",
                        "decision_recorded": event.get("decision"),
                    }
            else:
                conflicts.pop(digest, None)
    return list(conflicts.values())


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

    AN UNRESOLVED CONFLICTING RECEIPT ALSO BLOCKS COMPLETE, and it has to be checked
    separately because a conflict is not a state change: the party stays `accepted`
    and would otherwise not be "outstanding". Preserving disputed bytes without this
    would move Defect 7 from "the correction is lost" to "the correction is on disk
    and the round still says COMPLETE", which is not obviously better -- the
    custodian's signal is still that everything is fine.

    CLOSED IS NOT COMPLETE, and conflating them was a real defect. A REJECTED party
    is terminal -- nothing further is awaited from the custodian -- but its material
    is deliberately NOT in the corpus. Reporting that round as "complete" says every
    declared party contributed, when one did not. The register's own subject is
    claims that overstate what happened.

      closed    every party is terminal and no conflict is outstanding.
                Nothing is waiting on the custodian.
      complete  every party is ACCEPTED. The round has the material it declared.

    A round with a rejection is CLOSED and INCOMPLETE until either a replacement
    capture is accepted, or the roster is amended to withdraw the party. Neither
    replacement nor withdrawal exists yet, so such a round stays honestly
    incomplete rather than being rounded up.
    """
    states = {p: current_state(round_id, p) or "planned" for p in expected_parties}
    pending = sorted(p for p, s in states.items() if s in NEEDS_DISPOSITION)
    outstanding = sorted(p for p, s in states.items() if s in OPEN_STATES)
    conflicts = unresolved_conflicts(round_id)
    disputed = sorted({c["identity"] for c in conflicts})
    rejected = sorted(p for p, s in states.items() if s == "rejected")
    return {
        "round": round_id,
        "states": states,
        "outstanding": outstanding,
        "awaiting_disposition": pending,
        "disputed": disputed,
        "unresolved_conflicts": conflicts,
        "closed": not outstanding and not conflicts,
        "complete": all(s == "accepted" for s in states.values()) and not conflicts,
        "replacement_required": rejected,
        "complete_blocked_by": sorted({p for p, s in states.items() if s != "accepted"}
                                      | set(disputed)),
        "accepted": sorted(p for p, s in states.items() if s == "accepted"),
        "rejected": rejected,
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
