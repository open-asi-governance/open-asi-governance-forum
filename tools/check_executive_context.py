#!/usr/bin/env python3
"""Verify the executive's governing instructions still match what the record holds.

    python3 tools/check_executive_context.py
    python3 tools/check_executive_context.py --repin      # deliberate, and says what it changes

**DETERMINISTIC.** No LLM, no network. A drift check, not a generator.

Why this exists
---------------
The instructions that actually govern the executive workbench are not in this repository. Claude
Code loads `/home/reed/git/CLAUDE.md` from the parent workspace; Codex loads
`~/.codex/AGENTS.md` from its own home config. Neither was tracked here, in the manifest,
anchored, or visible to any party -- and both shape every review, design and refusal the layer
produces.

`record/executive/context/` now holds copies. **A copy is not a control.** The live files can be
edited without touching this repository, and a ratified copy that no longer matches what the
harness loads is exactly the theatre external review warned about: the executive controlling the
wording, the context and the account of compliance.

This check is the only thing that makes the pin mean anything. It compares the live bytes with
the pinned hash and fails on any difference.

What it cannot establish
-------------------------
* That the harness actually READ the file it loaded, or followed it.
* That no OTHER instruction reached the harness -- system prompts, per-session flags, tool
  descriptions, and this repository's own CLAUDE.md-equivalents are all outside its view.
* That the pinned text is good. Drift detection is not review.

What a reader should notice in the pinned files
------------------------------------------------
Recorded here because it is the check's most useful output and does not depend on running it:

* `claude-code-CLAUDE.md`'s standing objective is the **TensorRT-LLM defect campaign** -- a
  different project. Nothing in the instructions steering Claude Code during OAGF work mentions
  this forum.
* `codex-AGENTS.md` is 13,668 bytes of *"Proactive Cross-Domain Opportunity Discovery and
  Initiative"*, instructing novelty-proportional ideation, graded initiative levels, and that
  resource conservation is subordinate to completeness. That is a standing disposition toward
  scope expansion, behind every review Codex has given this project.
* Neither was written by, shown to, or agreed by any party.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PINS = REPO_ROOT / "record" / "executive" / "context" / "context-pins.json"


def _utc_today() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> tuple[int, list[str]]:
    if not PINS.is_file():
        return 2, [f"no pin file at {PINS.relative_to(REPO_ROOT)}"]
    doc = json.loads(PINS.read_text(encoding="utf-8"))
    problems = []
    for name, pin in (doc.get("pins") or {}).items():
        live = Path(pin["live_path"])
        copy = PINS.parent / name
        if not live.is_file():
            #  ABSENT IS NOT CLEAN. A governing file that has vanished means the harness is
            #  running under instructions the record cannot see at all.
            problems.append(f"{name}: live file {live} does not exist — the harness is running "
                            f"under instructions this record cannot see")
            continue
        live_hash = sha256_file(live)
        if live_hash != pin["sha256"]:
            problems.append(f"{name}: LIVE FILE HAS DRIFTED\n"
                            f"        pinned {pin['sha256'][:16]}…  ({pin['bytes']:,} bytes)\n"
                            f"        live   {live_hash[:16]}…  ({live.stat().st_size:,} bytes)\n"
                            f"        The record's copy is no longer what the harness loads.")
        if not copy.is_file():
            problems.append(f"{name}: the record's copy is missing")
        elif sha256_file(copy) != pin["sha256"]:
            problems.append(f"{name}: the record's COPY does not match its own pin")
    return (1 if problems else 0), problems


VERSIONS = PINS.parent / "versions"


def repin(reason: str = "") -> int:
    """Re-pin deliberately, ARCHIVING the superseded copy first. Never silent, never automatic.

    The superseded text is kept, because a pinned file is a candidate RATIFICATION OBJECT and
    overwriting it destroys the thing a party was asked about. Codex caught this on 2026-08-10:
    `oagf-CLAUDE.md` was committed and pinned while containing a claim since shown false, and
    `check()` passed on it — the green check establishes that the false statement is faithfully
    deployed. **It verifies identity, not truth**, and a repin that erased v1 would have left no
    way to see what the ballot would have carried.

    So each supersession writes `versions/<name>.v<N>` and records the chain in the pins doc.
    """
    doc = json.loads(PINS.read_text(encoding="utf-8"))
    changed = []
    for name, pin in (doc.get("pins") or {}).items():
        live = Path(pin["live_path"])
        if not live.is_file():
            print(f"  cannot re-pin {name}: {live} is missing")
            return 2
        new = sha256_file(live)
        if new != pin["sha256"]:
            changed.append((name, pin["sha256"], new, pin["bytes"], live.stat().st_size))
            copy = PINS.parent / name
            history = pin.setdefault("superseded", [])
            if copy.is_file():
                VERSIONS.mkdir(parents=True, exist_ok=True)
                archived = VERSIONS / f"{name}.v{len(history) + 1}"
                archived.write_bytes(copy.read_bytes())
                history.append({"version": len(history) + 1,
                                "sha256": pin["sha256"], "bytes": pin["bytes"],
                                "archived_as": str(archived.relative_to(PINS.parent)),
                                "superseded_utc": _utc_today(), "reason": reason or "(none given)"})
            copy.write_bytes(live.read_bytes())
            pin["sha256"], pin["bytes"] = new, live.stat().st_size
            pin["version"] = len(history) + 1
    if not changed:
        print("nothing to re-pin; the live files match the record")
        return 0
    PINS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, old, new, ob, nb in changed:
        print(f"  re-pinned {name}: {old[:12]}… -> {new[:12]}…  ({ob:,} -> {nb:,} bytes)")
    print("\nThe governing instructions changed. That is a change to what steers the executive,")
    print("and it belongs in a commit that says what changed and why -- not folded into another.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reason", default="", help="why the governing text changed")
    parser.add_argument("--repin", action="store_true",
                        help="update the pins to the live files, printing every change")
    args = parser.parse_args()
    if args.repin:
        return repin(getattr(args, 'reason', ''))
    status, problems = check()
    if problems:
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        print("\nFAILED — the executive's governing instructions are not what the record says.",
              file=sys.stderr)
        return status
    doc = json.loads(PINS.read_text(encoding="utf-8"))
    for name, pin in (doc.get("pins") or {}).items():
        print(f"  {name:28} {pin['bytes']:6,} bytes  {pin['sha256'][:16]}…  matches live")
    print("\nThe pins match. This does NOT establish that either harness followed them, that no")
    print("other instruction reached it, or that the pinned text is good.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
