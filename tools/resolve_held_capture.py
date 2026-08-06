#!/usr/bin/env python3
"""Disposition a held capture. Custodian action; deterministic; no network.

    python3 tools/resolve_held_capture.py <round> [--list]
    python3 tools/resolve_held_capture.py <round> <identity> --accept  --reason "..." \\
        --captured-utc 2026-08-06T19:38:48Z
    python3 tools/resolve_held_capture.py <round> <identity> --reject  --reason "..."

THE DEFECT THIS CLOSES (capture Defect 1).

`capture_lifecycle.TRANSITIONS` permits returned_pending_review -> {accepted,
rejected}, and `check_transition(..., 'rejected')` returns True. **Nothing in
tools/ ever performed either transition.** `"rejected"` appeared only inside
membership tests. The gates are sensitive by design, so a real round produces held
captures; a round is not complete while one awaits disposition; therefore **one
held capture blocked a round permanently.** The design was right and the exit was
missing -- D-29's shape: a capability that exists and nothing reaches.

Unit tests could not find it. `test_capture_lifecycle.py` correctly tested that the
transition is PERMITTED, which is a different claim from anything INVOKING it.

ACCEPT MEANS PUBLISH, NOT RELABEL.
----------------------------------
A state-only transition would let a round report COMPLETE for a party whose
material is in `record/quarantine/` and not in the corpus -- a false completion
signal, the same shape as the conflict resolver's first version, which recorded
"supersede" and left the disowned text published.

So `--accept` runs the full promotion through `capture_response.py`, the single
corpus writer, and the ORDER IS THE SAFETY PROPERTY:

    1. verify the quarantined bytes still hash to what the log recorded
    2. promote into the corpus
    3. verify the corpus now actually holds those bytes
    4. only then append `accepted`

Appending first is unsafe: a promotion failure would leave a party marked accepted
with nothing published. Corpus-first can leave published material with a pending
lifecycle event if step 4 fails -- recoverable, and it reports INCOMPLETE while
unrecovered, which is the conservative direction.

REJECT DOES NOT MEAN COMPLETE.
------------------------------
Rejected bytes stay in `record/quarantine/` forever; rejection is a recorded state,
never a deletion. But the round is then CLOSED, not COMPLETE: nothing is awaited
from the custodian, and one declared party has no material in the corpus. Calling
that "complete" would assert every party contributed when one did not. See
`round_status`, which now reports both.

WHY `--captured-utc` IS REQUIRED ON ACCEPT, AND NOT GUESSED.
------------------------------------------------------------
`capture_response.py` requires the time the response was captured. The lifecycle's
receiving event does NOT store it -- it stores `ts_utc`, which is when ingest ran.
Those differ, and substituting one for the other would put a value in the
provenance record that looks like a capture time and is not. That is exactly D-01,
the placeholder version identifier. So it is asked for, and refused if absent.

Bundles ingested from here on DO record `captured_utc` on the receiving event, so
this argument becomes optional for them. It stays required for captures held before
that change, because nothing recovers a time nobody wrote down.

Exit status is 0 on a recorded disposition and 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import capture_lifecycle as lifecycle                            # noqa: E402
import ingest_capture as ingest                                  # noqa: E402


def held_parties(round_id: str, declaration: dict) -> list[tuple[str, str]]:
    out = []
    for party in declaration["parties"]:
        state = lifecycle.current_state(round_id, party["identity"])
        if state in lifecycle.NEEDS_DISPOSITION:
            out.append((party["identity"], state))
    return out


def show(round_id: str, declaration: dict) -> int:
    held = held_parties(round_id, declaration)
    status = lifecycle.round_status(round_id, [p["identity"] for p in declaration["parties"]])
    print(f"{round_id}: closed={status['closed']}  complete={status['complete']}")
    if status["replacement_required"]:
        print(f"  rejected, so a replacement or a roster amendment is owed: "
              f"{', '.join(status['replacement_required'])}")
    if not held:
        print("  no captures awaiting disposition.")
        return 0
    print()
    for identity, state in held:
        event = lifecycle.latest_response_event(round_id, identity) or {}
        print(f"  {identity}  [{state}]")
        print(f"    preserved  {event.get('preserved_at')}")
        print(f"    sha256     {event.get('response_sha256', '')[:32]}")
        failed = [g for g in event.get("gate_results", []) if not g.get("passed")]
        for gate in failed:
            print(f"    gate FAILED  {gate.get('gate')}: {gate.get('detail')}")
        print()
    print("Disposition each with --accept or --reject, and a reason.")
    return 0


def verify_preserved(round_id: str, identity: str) -> tuple[dict, Path]:
    event = lifecycle.latest_response_event(round_id, identity)
    if not event or not event.get("preserved_at"):
        raise ingest.Refused(f"no preserved response recorded for {identity!r}.")
    path = REPO_ROOT / event["preserved_at"]
    if not path.is_file():
        raise ingest.Refused(f"preserved response is missing: {event['preserved_at']}")
    actual = lifecycle.sha256_of_text(path.read_text(encoding="utf-8"))
    if actual != event["response_sha256"]:
        raise ingest.Refused(
            f"preserved response no longer matches its recorded hash.\n"
            f"        recorded {event['response_sha256']}\n"
            f"        on disk  {actual}\n"
            f"        Promoting these bytes would publish something other than what was received."
        )
    return event, path


def accept(round_id: str, declaration: dict, identity: str, reason: str,
           actor: str, captured_utc: str | None) -> int:
    event, path = verify_preserved(round_id, identity)

    captured = captured_utc or event.get("captured_utc")
    if not captured:
        print(f"REFUSED: --captured-utc is required for {identity!r}.")
        print("  capture_response.py records when the response was captured. This capture was")
        print("  held before the lifecycle recorded that, and the event's ts_utc is when INGEST")
        print("  ran, not when the reply was pasted. Substituting it would put a value in the")
        print("  provenance record that looks like a capture time and is not -- D-01 exactly.")
        return 1

    party = ingest.reconcile({"identity": identity,
                              "prompt_path": declaration["common_prompt"],
                              "prompt_sha256": lifecycle.sha256_of_text(
                                  (REPO_ROOT / declaration["common_prompt"]).read_text(encoding="utf-8"))},
                             declaration)

    bundle = {
        "round": round_id,
        "identity": identity,
        "captured_utc": captured,
        "attested_by": actor,
        "phase": declaration.get("phase", "Phase-2 (informed)"),
        "sampling_unknown_reason": party.get("sampling_unknown_reason"),
        "effort_unknown_reason": party.get("effort_unknown_reason"),
        "system_instructions_unknown_reason": party.get("system_instructions_unknown_reason"),
        "version_unknown_reason": party.get("version_unknown_reason"),
    }

    if not ingest.promote(bundle, party, path, dry_run=False):
        print("REFUSED: capture_response.py declined to promote. The bytes remain preserved and")
        print("  the capture remains held, which is the recoverable direction. Nothing was")
        print("  recorded as accepted for material that is not in the corpus.")
        return 1

    # Step 3. Derived from the artifact, never from the fact that promote() returned
    # True -- the rule this subsystem now follows everywhere after a false completion
    # was found in the conflict resolver.
    if not lifecycle.corpus_holds(round_id, event["response_sha256"]):
        print("REFUSED: promotion reported success but corpus/raw/ does not contain these bytes.")
        print("  The capture stays held. Investigate before re-running; do NOT mark it accepted.")
        return 1

    lifecycle.transition(round_id, identity, "accepted", actor,
                         reason=reason,
                         response_sha256=event["response_sha256"],
                         promoted_from=event["preserved_at"])
    print(f"ACCEPTED  {identity}")
    print(f"  published from {event['preserved_at']}")
    print(f"  verified: corpus/raw/{round_id}/ holds {event['response_sha256'][:16]}…")
    print("  Nothing is committed. Review the diff, run `python3 tools/rebuild.py`, then commit.")
    return 0


def reject(round_id: str, declaration: dict, identity: str, reason: str, actor: str) -> int:
    event, path = verify_preserved(round_id, identity)

    # Refuse if the corpus already holds these bytes. Rejecting material that is
    # already published would leave the record asserting two incompatible things.
    if lifecycle.corpus_holds(round_id, event["response_sha256"]):
        print(f"REFUSED: corpus/raw/{round_id}/ already contains these bytes, so rejecting them")
        print("  would record a decision the corpus contradicts. Withdraw the published artifact")
        print("  first, as a recorded custodian action.")
        return 1

    lifecycle.transition(round_id, identity, "rejected", actor,
                         reason=reason,
                         response_sha256=event["response_sha256"],
                         preserved_at=event["preserved_at"])
    print(f"REJECTED  {identity}")
    print(f"  the bytes are KEPT at {event['preserved_at']} — rejection is a recorded state,")
    print("  never a deletion.")
    print()
    print(f"  {round_id} is now CLOSED but NOT COMPLETE: nothing is awaited from you, and this")
    print("  party has no material in the corpus. It becomes complete only when a replacement")
    print("  capture is accepted, or the roster is amended to withdraw the party. Neither is")
    print("  automated; the round reports itself incomplete until one happens.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("round")
    parser.add_argument("identity", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--accept", action="store_true")
    parser.add_argument("--reject", action="store_true")
    parser.add_argument("--reason")
    parser.add_argument("--captured-utc")
    parser.add_argument("--actor", default="custodian")
    args = parser.parse_args()

    try:
        declaration = ingest.load_round(args.round)
    except ingest.Refused as error:
        print(f"REFUSED: {error}")
        return 1

    if args.list or not args.identity:
        return show(args.round, declaration)

    if args.accept == args.reject:
        print("choose exactly one of --accept or --reject.")
        return 1
    if not (args.reason or "").strip():
        print("--reason is required. A disposition without a stated reason is not a record.")
        return 1

    state = lifecycle.current_state(args.round, args.identity)
    if state not in lifecycle.NEEDS_DISPOSITION:
        print(f"{args.identity!r} is {state!r}, which is not awaiting disposition.")
        return 1

    try:
        if args.accept:
            return accept(args.round, declaration, args.identity, args.reason.strip(),
                          args.actor, args.captured_utc)
        return reject(args.round, declaration, args.identity, args.reason.strip(), args.actor)
    except ingest.Refused as error:
        print(f"REFUSED: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
