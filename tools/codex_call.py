#!/usr/bin/env python3
"""Invoke Codex through a rate limit. The custodian's floor is 10 minutes between calls.

    python3 tools/codex_call.py --prompt-file design.md --purpose "review the X design"
    python3 tools/codex_call.py --status
    python3 tools/codex_call.py --prompt-file f.md --purpose "..." \
        --override "custodian asked for this now"

**A SPENDING CONTROL, not a safety gate.** The custodian funds both subscriptions solo. Reading
Codex's remaining quota needs an authenticated Chrome on the DevTools port and is set aside; a
wall-clock floor between calls is the control that works without it.

Why 10 minutes, and what it costs
----------------------------------
This session made **25 Codex invocations**. At a 10-minute floor that is 4 hours of elapsed
time, so the limit is not cosmetic — it changes how the work is done. That is the point: it
forces review to be batched into fewer, larger questions rather than spent on a stream of small
ones, which is also how the better reviews here have gone. The eight-finding rejection of the
search tool came from one large prompt, not from several small ones.

The cost is real and worth stating: a review that would have caught something is sometimes not
worth waiting ten minutes for, and will therefore not happen. Some defects will ship that a
free-running reviewer would have caught.

State comes from the action log, not a side file
-------------------------------------------------
"When was Codex last called" is derived from `record/executive/action-log.jsonl`, which is
already hash-chained and already records `codex_invoke`. A separate timestamp file would be a
second source of truth that could disagree with the log, and the log is the thing an auditor
reads.

The override is logged, always
-------------------------------
`--override` exists because the custodian said "unless I say otherwise". It never bypasses the
record: the call is logged with the override reason attached, because an unlogged exception is
precisely what the executive's scope statement forbids.

What this does NOT do
----------------------
* **It does not measure consumption.** A floor between calls bounds their rate, not their cost.
  One enormous prompt costs more than three small ones and this permits it.
* **It cannot prevent bypass.** Anything in this environment can invoke `codex exec` directly,
  including me. The limit binds the path that records itself; it does not bind the binary. That
  is the same shape as gate modification being invisible to the log that audits it, and it is a
  real limit rather than a hypothetical one.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import executive_log as ex                                                # noqa: E402

MIN_SECONDS_BETWEEN_CALLS = 600           # the custodian's floor, 2026-08-09
CODEX_TIMEOUT_SECONDS = 1500


def last_call() -> dict | None:
    """The most recent codex_invoke that actually ran. Refused attempts do not reset the clock."""
    for entry in reversed(ex.read_log()):
        if entry.get("action") == "codex_invoke" and entry.get("verified"):
            return entry
    return None


def seconds_since_last() -> float | None:
    entry = last_call()
    if not entry:
        return None
    when = datetime.strptime(entry["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - when).total_seconds()


def may_call(override: str = "") -> tuple[bool, str]:
    elapsed = seconds_since_last()
    if elapsed is None:
        return True, "no previous Codex call recorded"
    if elapsed >= MIN_SECONDS_BETWEEN_CALLS:
        return True, f"{elapsed/60:.1f} min since the last call, floor is {MIN_SECONDS_BETWEEN_CALLS/60:.0f}"
    wait = (MIN_SECONDS_BETWEEN_CALLS - elapsed) / 60
    if override:
        return True, (f"OVERRIDDEN by the custodian with {wait:.1f} min still to wait — "
                      f"reason: {override}")
    return False, (f"only {elapsed/60:.1f} min since the last call; {wait:.1f} min remain of the "
                   f"{MIN_SECONDS_BETWEEN_CALLS/60:.0f}-minute floor. Batch the question, or "
                   f"pass --override with a reason.")


def call(prompt: str, purpose: str, override: str = "") -> tuple[int, str]:
    allowed, why = may_call(override)
    if not allowed:
        ex.log_action("codex_invoke", {"purpose": purpose, "override": None},
                      verified=False, problems=[why], note="refused by the rate limit")
        print(f"  REFUSED: {why}", file=sys.stderr)
        return 2, ""
    #  LOGGED BEFORE THE CALL. Logging afterwards would leave a crashed or killed invocation
    #  unrecorded, and the clock would not advance for a call that was in fact made.
    ex.log_action("codex_invoke",
                  {"purpose": purpose, "override": override or None,
                   "prompt_sha256": ex.hashlib.sha256(prompt.encode()).hexdigest(),
                   "prompt_chars": len(prompt)},
                  verified=True, note=why)
    result = subprocess.run(["codex", "exec", "-C", str(REPO_ROOT), prompt],
                            capture_output=True, text=True, timeout=CODEX_TIMEOUT_SECONDS,
                            stdin=subprocess.DEVNULL)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prompt-file", help="file holding the prompt to send")
    parser.add_argument("--purpose", default="", help="what this review is for; goes in the log")
    parser.add_argument("--override", default="",
                        help="the custodian's reason for bypassing the floor; always logged")
    parser.add_argument("--status", action="store_true", help="report the clock and exit")
    parser.add_argument("--out", help="write Codex's output here instead of stdout")
    args = parser.parse_args()

    if args.status:
        elapsed = seconds_since_last()
        allowed, why = may_call()
        prev = last_call()
        print(f"  floor: {MIN_SECONDS_BETWEEN_CALLS/60:.0f} minutes between calls")
        if prev:
            print(f"  last call: {prev['utc']} — {prev.get('claim',{}).get('purpose','(no purpose)')}")
            print(f"  elapsed:   {elapsed/60:.1f} min")
        else:
            print("  last call: none recorded")
        print(f"  may call now: {allowed}\n    {why}")
        return 0 if allowed else 1

    if not args.prompt_file:
        parser.error("--prompt-file is required unless --status")
    if not args.purpose:
        parser.error("--purpose is required: an unexplained review is not auditable")
    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    code, output = call(prompt, args.purpose, args.override)
    if code == 2:
        return 2
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"  codex exited {code}; output -> {args.out}")
    else:
        print(output)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
