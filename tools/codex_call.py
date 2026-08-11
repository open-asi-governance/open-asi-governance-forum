#!/usr/bin/env python3
"""Invoke Codex through a rate limit. The floor lives in record/executive/spend-policy.json.

    python3 tools/codex_call.py --prompt-file design.md --purpose "review the X design"
    python3 tools/codex_call.py --status
    python3 tools/codex_call.py --prompt-file f.md --purpose "..." \
        --override "custodian asked for this now"

**A SPENDING CONTROL, not a safety gate.** Three money channels fund this project and they are
not interchangeable — see `record/executive/spend-policy.json`, which records each floor beside
its PROVENANCE:

* **OpenRouter** — per-token, priced before the call, already gated by `round_cycle --budget`.
  This is what the rounds spend, and it is the only channel with a per-call figure.
* **Claude subscription** — prepaid monthly, and **readable**: `executive_log.quota_now()` calls
  the OAuth usage endpoint directly. Every action-log entry already carries a reading. **No floor
  is set on it**, so those readings are a stamp and not yet a gate. The executive declines to
  invent the number: an invented floor sitting in the record beside a custodian-stated one would
  be indistinguishable from it a month later.
* **Codex subscription** — prepaid monthly, and readable only through an authenticated Chrome on
  the DevTools port, which is set aside. This module is what stands in for the reading.

The wall-clock floor is a PROXY, not the measurement
-----------------------------------------------------
Spacing calls bounds their rate; it never bounds their cost. One enormous prompt costs more than
three small ones and this permits it. The number that would actually bound spend is how fast
Codex exhausts the weekly window, and the custodian holds that from experience — so
`derived_from_measurement` is recorded in the policy and printed by `--status`. While it is
false, 600 seconds is **a floor honoured, not a rate justified**, and the tool says so on every
status line rather than letting the number acquire authority by sitting there.

What the floor costs
---------------------
This session made 25 Codex invocations. At ten minutes apart that is four hours of elapsed time,
so the limit changes how the work is done: it forces review into fewer, larger questions rather
than a stream of small ones, which is how the better reviews here have gone — the eight-finding
rejection of the search tool came from one large prompt. The cost is that some review which would
have caught something is not worth a ten-minute wait, and therefore will not happen.

State comes from the action log, not a side file
-------------------------------------------------
"When was Codex last called" is derived from `record/executive/action-log.jsonl`, already
hash-chained and already recording `codex_invoke`. A separate timestamp file would be a second
source of truth that could disagree with the log, and the log is what an auditor reads. A REFUSED
attempt does not reset the clock, and the call is logged BEFORE it runs, so a crashed invocation
is not an unrecorded one.

The floor does NOT apply to work the custodian just asked for
--------------------------------------------------------------
Owner, 2026-08-10: *"Ignore Codex rate limits when acting on my immediate direction. You then
call Codex without any wait."* The floor is a spending control on review this layer initiates on
its own. Making the custodian wait ten minutes for a review he just requested inverts its purpose
-- it spends his time to save his money. On immediate direction, pass `--override` with the
direction as the reason and proceed. The exemption is therefore visible in the action log rather
than silent, and the floor still binds self-initiated review.

The override is logged, always
-------------------------------
`--override` exists because the custodian said "unless I say otherwise". It never bypasses the
record: the reason is attached to the entry, because an unlogged exception is precisely what the
executive's scope statement forbids.

It cannot prevent bypass — and did not
----------------------------------------
Anything here can invoke `codex exec` directly, including me. This is not hypothetical: **23 of
the 25 Codex calls made on 2026-08-09 went straight through the shell and are absent from the
action log**, which holds two. The limit binds the path that records itself; it does not bind the
binary, and the log undercounts by construction. Same shape as gate modification being invisible
to the log that audits it.
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
import executive_lease as lease                                           # noqa: E402

CODEX_TIMEOUT_SECONDS = 1500
POLICY = REPO_ROOT / "record" / "executive" / "spend-policy.json"

#  Fallback only. The live value and -- more importantly -- whether it was MEASURED or merely
#  honoured come from the policy file, so the number and its provenance cannot drift apart.
_DEFAULT_MIN_SECONDS = 600


def policy() -> dict:
    try:
        doc = json.loads(POLICY.read_text(encoding="utf-8"))
        return doc["channels"]["codex_subscription"]["rate_limit"]
    except Exception:                                                    # noqa: BLE001
        return {"min_seconds_between_calls": _DEFAULT_MIN_SECONDS,
                "provenance": "policy file unreadable; using the built-in fallback",
                "derived_from_measurement": False}


def min_seconds() -> int:
    return int(policy().get("min_seconds_between_calls") or _DEFAULT_MIN_SECONDS)


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


def override_rate() -> tuple[int, int]:
    """(overrides, total Codex invocations) from the action log. Counted, never estimated."""
    log = REPO_ROOT / "record" / "executive" / "action-log.jsonl"
    if not log.is_file():
        return (0, 0)
    import json as _json
    calls = overrides = 0
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = _json.loads(line)
        except Exception:                                               # noqa: BLE001
            continue
        if row.get("action") != "codex_invoke":
            continue
        calls += 1
        if "override" in (str(row.get("note", "")) + str(row.get("claim", ""))).lower():
            overrides += 1
    return (overrides + 1, calls + 1)          # this call included; it is about to happen


def may_call(override: str = "") -> tuple[bool, str]:
    elapsed = seconds_since_last()
    if elapsed is None:
        return True, "no previous Codex call recorded"
    floor = min_seconds()
    if elapsed >= floor:
        return True, f"{elapsed/60:.1f} min since the last call, floor is {floor/60:.0f}"
    wait = (floor - elapsed) / 60
    if override:
        #  REPORT THE AGGREGATE AT THE MOMENT OF THE DECISION. Control 50 requires an override
        #  rate to appear wherever the control's effectiveness is claimed, and a rate that lives
        #  only in a report nobody runs is the failure the control names: every instance
        #  justified, the total invisible. Measured 2026-08-11 at 0.857 -- 18 of 21 invocations.
        #  A floor overridden that often is not governing anything, and whether the right response
        #  is to delete it or to reset it is a spend decision, so it sits with the custodian.
        rate = override_rate()
        aggregate = (f" — this is override {rate[0]} of {rate[1]} Codex calls "
                     f"({rate[0] / rate[1]:.0%} of them)") if rate[1] else ""
        return True, (f"OVERRIDDEN by the custodian with {wait:.1f} min still to wait — "
                      f"reason: {override}{aggregate}")
    return False, (f"only {elapsed/60:.1f} min since the last call; {wait:.1f} min remain of the "
                   f"{floor/60:.0f}-minute floor. Batch the question, or "
                   f"pass --override with a reason.")


TRANSCRIPTS = REPO_ROOT / "record" / "executive" / "codex-transcripts"


def call(prompt: str, purpose: str, override: str = "") -> tuple[int, str]:
    """Invoke Codex, ALWAYS persisting the transcript, and log start and completion separately.

    Two entries, not one, because they establish different things. The `codex_invoke` entry
    records that a call was permitted and started; it can verify nothing about the result,
    because the result does not exist yet. The `codex_return_captured` entry records that a
    process exited and these bytes came back.

    Neither is named `verified` in the sense the other profiles use, and the completion profile
    is deliberately called `codex_return_captured` rather than `codex_reviewed`: it establishes
    that a Codex process returned captured bytes. It establishes nothing about whether the
    review was independent, attentive, correct, or acted upon.

    THE TRANSCRIPT IS WRITTEN BEFORE ANYTHING IS PRINTED. On 2026-08-10 a review that cost
    123,731 tokens was lost because this function returned the output to a caller that printed
    `tail -120` of it and kept nothing. The first part of Codex's answer — its judgment on the
    ratification instrument — could not be recovered from any session file. A review nobody can
    re-read is not a review anyone can audit.
    """
    #  THE LEASE IS CHECKED FIRST, before the rate limit and before anything is spent. An
    #  expired lease is not a slow-down to wait out; it is the sunset, and there is no override.
    try:
        lease.require("codex_invoke")
    except lease.LeaseExpired as expired:
        ex.log_action("codex_invoke", {"purpose": purpose, "coverage": "refused_before_action"},
                      verified=False, problems=[str(expired)], note="refused by the lease")
        print(f"  REFUSED: {expired}", file=sys.stderr)
        return 3, ""
    allowed, why = may_call(override)
    if not allowed:
        ex.log_action("codex_invoke",
                      {"purpose": purpose, "override": None, "coverage": "refused_before_action"},
                      verified=False, problems=[why], note="refused by the rate limit")
        print(f"  REFUSED: {why}", file=sys.stderr)
        return 2, ""
    prompt_sha = ex.hashlib.sha256(prompt.encode()).hexdigest()
    #  LOGGED BEFORE THE CALL. Logging afterwards would leave a crashed or killed invocation
    #  unrecorded, and the clock would not advance for a call that was in fact made.
    started = ex.log_action("codex_invoke",
                            {"purpose": purpose, "override": override or None,
                             "prompt_sha256": prompt_sha, "prompt_chars": len(prompt),
                             "state": "started"},
                            verified=True, note=why)
    stamp = started["utc"].replace(":", "").replace("-", "")
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    path = TRANSCRIPTS / f"{stamp}-{prompt_sha[:12]}.md"
    problems: list[str] = []
    code, output = -1, ""
    try:
        result = subprocess.run(["codex", "exec", "-C", str(REPO_ROOT), prompt],
                                capture_output=True, text=True, timeout=CODEX_TIMEOUT_SECONDS,
                                stdin=subprocess.DEVNULL)
        code = result.returncode
        output = (result.stdout or "") + (result.stderr or "")
        if code != 0:
            problems.append(f"codex exited {code}")
        if not output.strip():
            problems.append("codex returned no output; there is nothing to review")
    except subprocess.TimeoutExpired:
        problems.append(f"codex timed out after {CODEX_TIMEOUT_SECONDS}s — recorded as a "
                        f"distinct failure, not as an exit status")
    except Exception as error:                                          # noqa: BLE001
        problems.append(f"transport failure: {type(error).__name__}: {error}")
    #  Written whatever happened, including the empty case: an invocation that returned nothing
    #  is evidence about the harness, and deleting it would leave only the claim that it failed.
    path.write_text(f"<!-- purpose: {purpose} -->\n"
                    f"<!-- prompt_sha256: {prompt_sha} -->\n"
                    f"<!-- exit: {code} -->\n\n{output}", encoding="utf-8")
    ex.log_action("codex_return_captured",
                  {"purpose": purpose, "prompt_sha256": prompt_sha, "exit_status": code,
                   "output_chars": len(output),
                   "output_sha256": ex.hashlib.sha256(output.encode()).hexdigest(),
                   "transcript": str(path.relative_to(REPO_ROOT)),
                   "establishes": "a codex process returned these bytes; nothing about the "
                                  "review's independence, attention, correctness or effect"},
                  verified=not problems, problems=problems,
                  note=f"transcript {path.name}")
    return code, output


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
        pol = policy()
        print(f"  floor: {min_seconds()/60:.0f} minutes between calls")
        print(f"  basis: {'MEASURED' if pol.get('derived_from_measurement') else 'NOT MEASURED'}"
              f" — {pol.get('provenance','(no provenance recorded)')}")
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
