#!/usr/bin/env python3
"""Resolve a conflicting capture receipt. Custodian action; deterministic; no network.

    python3 tools/resolve_conflict.py <round> <identity> --confirm-recorded --reason "..."
    python3 tools/resolve_conflict.py <round> <identity> --supersede-with-conflicting --reason "..."
    python3 tools/resolve_conflict.py <round> [--list]

WHY THIS SHIPS IN THE SAME COMMIT AS THE DETECTION.

`ingest_capture.py` now preserves a differing capture instead of discarding it
(Defect 7), records a `conflicting_receipt`, and blocks the round from reporting
COMPLETE. That is a strictly better failure than silence -- but only if the
custodian can then get out of it.

This repository already has the counter-example. Defect 1: a *held* capture cannot
be dispositioned at all, because nothing anywhere calls `rejected`. So a state that
was designed to be temporary became permanent, and a round with one held party is
permanently INCOMPLETE. Adding a second blocking state with no exit would repeat
that, one week later, in the same subsystem -- which the external reviewer said
plainly and which is the reason this file exists rather than being a follow-up task.

THE TWO RESOLUTIONS, and why there is no third.

  --confirm-recorded
      The recorded response stands. The conflicting bytes were a mistake -- wrong
      window, wrong party, wrong paste. The quarantined file is KEPT and the event
      is marked resolved. Nothing in the corpus changes.

  --supersede-with-conflicting
      The conflicting bytes are correct and what is in the corpus is not. This
      records the decision and points at both hashes. It does NOT rewrite
      corpus/raw/, and that restraint is the point: raw material is never edited,
      so a correction is a SUPERSEDING artifact that cites the original by hash.
      The command prints exactly what remains to be done by hand, because doing it
      automatically would mean this tool silently replacing text attributed to a
      real party -- the failure Defect 7 already produced once.

There is deliberately no `--discard-conflicting`. Deleting preserved bytes is the
behaviour that was just removed; re-adding it under a flag would restore it with a
confirmation prompt in front.

Exit status is 0 on a recorded resolution and 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import capture_lifecycle as lifecycle                            # noqa: E402


def show(round_id: str) -> int:
    conflicts = lifecycle.unresolved_conflicts(round_id)
    if not conflicts:
        print(f"{round_id}: no unresolved conflicting receipts.")
        return 0
    print(f"{round_id}: {len(conflicts)} unresolved conflicting receipt(s)\n")
    for conflict in conflicts:
        print(f"  {conflict['identity']}")
        print(f"    recorded    {conflict['recorded_sha256']}")
        print(f"    conflicting {conflict['conflicting_sha256']}")
        print(f"    preserved   {conflict['preserved_at']}")
        print(f"    {conflict['conflicting_bytes']:,} bytes offered by {conflict.get('actor')!r}")
        print()
    print("Resolve each with --confirm-recorded or --supersede-with-conflicting, and a reason.")
    return 0


def resolve(round_id: str, identity: str, decision: str, reason: str, actor: str) -> int:
    conflicts = [c for c in lifecycle.unresolved_conflicts(round_id)
                 if c["identity"] == identity]
    if not conflicts:
        print(f"no unresolved conflicting receipt for {identity!r} in {round_id}.")
        return 1
    if len(conflicts) > 1:
        # Resolve one at a time and name which. Settling several disputes with one
        # reason would attach that reason to decisions it was not written about.
        print(f"{identity!r} has {len(conflicts)} unresolved conflicts. Resolve them one at a "
              f"time; pass --conflicting-sha256 to name which.")
        for conflict in conflicts:
            print(f"    {conflict['conflicting_sha256']}  {conflict['preserved_at']}")
        return 1

    conflict = conflicts[0]
    event = {
        "event": "conflict_resolved",
        "round": round_id,
        "identity": identity,
        "actor": actor,
        "decision": decision,
        "reason": reason,
        "recorded_sha256": conflict["recorded_sha256"],
        "conflicting_sha256": conflict["conflicting_sha256"],
        "preserved_at": conflict["preserved_at"],
    }
    path = lifecycle.log_path(round_id)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"recorded: {identity} — {decision}")
    print(f"  reason: {reason}")
    print(f"  the quarantined bytes are KEPT at {conflict['preserved_at']}")

    if decision == "supersede_with_conflicting":
        print()
        print("  NOT DONE AUTOMATICALLY, and this is deliberate:")
        print("  the corpus still holds the ORIGINAL response for this party. Raw material is")
        print("  never edited, so replace it with a superseding artifact that cites the original")
        print(f"  by hash ({conflict['recorded_sha256'][:16]}…). A tool that rewrote text")
        print("  attributed to a real party is exactly the failure this whole path exists to stop.")
        return 0

    print("  the corpus is unchanged, which is what confirming the recorded response means.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("round")
    parser.add_argument("identity", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--confirm-recorded", action="store_true")
    parser.add_argument("--supersede-with-conflicting", action="store_true")
    parser.add_argument("--reason")
    parser.add_argument("--actor", default="custodian")
    args = parser.parse_args()

    if args.list or not args.identity:
        return show(args.round)

    chosen = [d for d, on in (("confirm_recorded", args.confirm_recorded),
                              ("supersede_with_conflicting", args.supersede_with_conflicting)) if on]
    if len(chosen) != 1:
        print("choose exactly one of --confirm-recorded or --supersede-with-conflicting.")
        return 1
    if not (args.reason or "").strip():
        # Same rule the lifecycle already applies to accepted/rejected: a disposition
        # without a reason records that someone clicked, not why.
        print("--reason is required. A disposition without a stated reason is not a record.")
        return 1

    return resolve(args.round, args.identity, chosen[0], args.reason.strip(), args.actor)


if __name__ == "__main__":
    sys.exit(main())
