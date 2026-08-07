#!/usr/bin/env python3
"""Advance the deliberation by at most one round, then stop.

    python3 tools/round_cycle.py --selector portfolio --dry-run
    python3 tools/round_cycle.py --selector portfolio --parties grok,gpt,gemini,claude,qwen

ONE CYCLE PER INVOCATION. NOT A DAEMON.

A timer fires this at or below the operator's affordability ceiling; it advances at
most one round and exits. No in-memory state, so a crash loses nothing; every cycle
is separately auditable; and the process is stopped by removing the timer rather
than by killing something that holds a queue.

    select -> compose -> solicit -> capture -> record -> HALT

WHAT THIS DELIBERATELY DOES NOT DO, and why each one is excluded.

  * **No synthesis.** It never writes what a round established. Gemini made
    "the conflicted moderator retains the power to unilaterally synthesize
    findings" a condition of DECLINING to participate. A loop that wrote findings
    would lose that party and deserve to.
  * **No dispute resolution.** A held capture or an unresolved conflicting receipt
    halts the cycle. D-37 and D-38 exist because those paths were once silent.
  * **No question invention.** An empty queue means the cycle idles. Silence is a
    legitimate output and this record has never had a way to express it; a loop
    that always produces something is the failure mode, not the feature.
  * **No writes to `main`.** GOVERNANCE.md §2: no AI system holds credentials and
    all writes pass through the custodian. The cycle commits to a round branch and
    stops. The custodian merges.
  * **No default selector.** `--selector` is required. Three mechanisms are under
    test in `tools/benchmark_agenda.py` and none is adopted; a default would let
    one win by being the one nobody changed.

THE HALT CONDITIONS ARE THE DESIGN.

A halted cycle is a RECORD ENTRY, not an error. It exits non-zero and writes why:

    2  empty queue -- nothing to ask
    3  a held capture or unresolved conflict is awaiting the custodian
    4  the prompt template changed since it was last approved
    5  fewer than k_min samples collected from some party
    6  every party agreed and no party disagreed with any other
    7  budget or configuration refusal

Condition 6 needs saying out loud: **unanimity halts the loop.** QCP §6 measured
this corpus's own local party holding two incompatible positions in 17 of 20
samples because a prompt asserted one emphatically. A round where everyone agrees
is more likely to mean the prompt told them what to say than that a question was
settled, so it stops for a human rather than being recorded as consensus.

TEMPLATE DRIFT. The prompt template is hashed and the hash is committed. If it
changes, the cycle halts. Every consulted party named the moderator's prompt
wording as its residual power; letting a loop rewrite prompts unattended would
industrialise exactly the channel they objected to.

Exit status 0 means one round was solicited and recorded. Anything else is a halt,
and the reason is on stdout and in the cycle record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import agenda_selectors as AS                                       # noqa: E402
import capture_lifecycle as lifecycle                               # noqa: E402

CYCLES_DIR = REPO_ROOT / "record" / "cycles"
TEMPLATE = REPO_ROOT / "record" / "solicitations" / "excerpts" / "round-prompt-template.md"
TEMPLATE_HASH_FILE = REPO_ROOT / "record" / "cycles" / "approved-template.sha256"

HALT_EMPTY_QUEUE = 2
HALT_AWAITING_CUSTODIAN = 3
HALT_TEMPLATE_DRIFT = 4
HALT_UNDERSAMPLED = 5
HALT_UNANIMOUS = 6
HALT_REFUSED = 7


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def halt(code: int, reason: str, detail: dict | None = None, dry_run: bool = False) -> int:
    """Record the halt as an outcome, not as a crash."""
    record = {"artifact_type": "cycle_halt", "utc": utc_now(), "exit_code": code,
              "reason": reason, "detail": detail or {},
              "note": ("A halt is a recorded outcome. The loop is designed to stop rather than "
                       "improvise; a cycle that always produces a round is the failure mode.")}
    print(f"HALT [{code}] {reason}")
    for key, value in (detail or {}).items():
        print(f"    {key}: {value}")
    if not dry_run:
        CYCLES_DIR.mkdir(parents=True, exist_ok=True)
        path = CYCLES_DIR / f"halt-{utc_now().replace(':', '').replace('-', '')}.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"    recorded at {path.relative_to(REPO_ROOT)}")
    return code


def template_ok() -> tuple[bool, str]:
    if not TEMPLATE.is_file():
        return False, "no prompt template committed"
    digest = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    if not TEMPLATE_HASH_FILE.is_file():
        return False, f"no approved template hash; current is {digest}"
    approved = TEMPLATE_HASH_FILE.read_text(encoding="utf-8").split()[0]
    if digest != approved:
        return False, f"template changed: approved {approved[:16]}, current {digest[:16]}"
    return True, digest


def pending_dispositions(rounds: list[str]) -> list[str]:
    """Any held capture or unresolved conflict, across known rounds."""
    blocked = []
    for round_id in rounds:
        try:
            events = lifecycle.read_events(round_id)
        except Exception:                                           # noqa: BLE001
            continue
        if not events:
            continue
        parties = sorted({e["identity"] for e in events if e.get("identity")})
        status = lifecycle.round_status(round_id, parties)
        if status["awaiting_disposition"]:
            blocked.append(f"{round_id}: awaiting disposition "
                           f"({', '.join(status['awaiting_disposition'])})")
        if status["unresolved_conflicts"]:
            blocked.append(f"{round_id}: {len(status['unresolved_conflicts'])} "
                           f"unresolved conflicting receipt(s)")
    return blocked


def known_rounds() -> list[str]:
    d = REPO_ROOT / "record" / "rounds"
    return sorted(p.stem.replace("-lifecycle", "") for p in d.glob("*-lifecycle.jsonl")) \
        if d.is_dir() else []


def cycle_index() -> int:
    CYCLES_DIR.mkdir(parents=True, exist_ok=True)
    return len(list(CYCLES_DIR.glob("round-*.json")))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selector", required=True, choices=sorted(AS.SELECTORS),
                    help="REQUIRED. No default: three mechanisms are under test and "
                         "none is adopted.")
    ap.add_argument("--parties", default="grok,gpt,gemini,claude,qwen")
    ap.add_argument("--k-min", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--dry-run", action="store_true",
                    help="select and compose only; solicit nothing, write nothing")
    args = ap.parse_args(argv)

    parties = [p.strip() for p in args.parties.split(",") if p.strip()]
    index = cycle_index()
    print(f"cycle {index} · selector={args.selector} · parties={len(parties)}")

    ok, template_detail = template_ok()
    if not ok:
        return halt(HALT_TEMPLATE_DRIFT,
                    "the prompt template is not the approved one",
                    {"detail": template_detail,
                     "why": ("Every consulted party named the moderator's prompt wording as its "
                             "residual power. A loop that rewrites prompts unattended "
                             "industrialises exactly that channel.")},
                    args.dry_run)

    blocked = pending_dispositions(known_rounds())
    if blocked:
        return halt(HALT_AWAITING_CUSTODIAN,
                    "a capture is awaiting the custodian",
                    {"blocked": "; ".join(blocked),
                     "why": "D-37 and D-38 exist because these paths were once silent."},
                    args.dry_run)

    queue = AS.load_queue()
    if not queue:
        return halt(HALT_EMPTY_QUEUE, "no proposals in the queue",
                    {"why": "Silence is a legitimate output. The loop does not invent questions."},
                    args.dry_run)

    pick = AS.SELECTORS[args.selector](queue, parties, index, args.seed)
    if pick is None:
        slot = index % 4
        if args.selector == "portfolio" and slot == 3:
            return halt(HALT_EMPTY_QUEUE,
                        "institutional-challenge slot: the question is not the moderator's to write",
                        {"why": ("SOP §5.1a: the moderator and custodian may not write or select "
                                 "questions about themselves. This slot needs non-target "
                                 "nominations, which are supplied by hand.")},
                        args.dry_run)
        return halt(HALT_EMPTY_QUEUE, "the selector returned nothing to ask", {}, args.dry_run)

    print(f"  selected {pick.pid} from {pick.party} "
          f"({len(pick.sponsors)} sponsor(s), age {pick.age})")
    print(f"    {pick.question[:150]}")

    if args.dry_run:
        print("\n  DRY RUN — nothing solicited, nothing written.")
        print(f"  would compose from {TEMPLATE.relative_to(REPO_ROOT)} "
              f"(sha256 {template_detail[:16]}…)")
        print(f"  would solicit k>={args.k_min} from: {', '.join(parties)}")
        print("  would then STOP. No synthesis, no adoption, no write to main.")
        return 0

    # Beyond this point the cycle would solicit. Deliberately not implemented until a
    # selector is ADOPTED: wiring live solicitation to an untested mechanism is the
    # thing this file's docstring warns about, and --dry-run is the whole value today.
    return halt(HALT_REFUSED,
                "live solicitation is not enabled",
                {"why": ("No selector has been adopted. tools/benchmark_agenda.py is measuring "
                         "the three candidates; until the custodian adopts one, this cycle runs "
                         "in --dry-run only."),
                 "selected_anyway": f"{pick.pid} — recorded so the choice is auditable"},
                args.dry_run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
