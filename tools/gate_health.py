#!/usr/bin/env python3
"""Gate health as a vector, and the override rate — controls 57 and 50, turned on ourselves.

    python3 tools/gate_health.py

WHY THIS EXISTS. The self-application table recorded both of these as VIOLATED:

* **Control 57** — gate health is a vector, never a single rate. This record reported gate health
  as pass/fail alone. Every single dimension of a gate can be moved to its best value by a
  degenerate strategy: a false-accept rate of zero is achieved by rejecting everything.
* **Control 50** — overrides are metered and their rate published. Every Codex `--override` was
  logged individually and **no aggregate existed anywhere**, which is exactly the failure the
  control describes: every instance justified, the total invisible.

Both are computed here from `record/executive/action-log.jsonl`, which is written by the tools
themselves rather than by hand.

WHAT THIS DOES NOT ESTABLISH. That the gates are good, or that the rates are at good levels. A
low override rate may mean discipline or may mean nobody tried anything hard; a high one may mean
the floor is wrong rather than that it is being abused. **The control asks for the question to be
askable, not answered.** Nothing here interprets the numbers, and the interpretation is the
custodian's.

It also cannot report a false-reject rate. This record does not retain rejected candidates, so
that dimension is UNKNOWN rather than zero — control 55, still violated, and visible here as the
hole it is.
"""

from __future__ import annotations

import collections
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG = REPO_ROOT / "record" / "executive" / "action-log.jsonl"


def rows() -> list[dict]:
    if not LOG.is_file():
        raise SystemExit(f"no action log at {LOG.relative_to(REPO_ROOT)}")
    return [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def overrides(entries: list[dict]) -> dict:
    """Control 50. An override that is logged but never counted is a repeal nobody voted on."""
    calls = [r for r in entries if r.get("action") == "codex_invoke"]
    refused = [r for r in calls if "refused" in str(r.get("note", "")).lower()]
    overridden = [r for r in calls
                  if "override" in (str(r.get("note", "")) + str(r.get("claim", ""))).lower()]
    return {
        "codex_invocations": len(calls),
        "overrode_the_floor": len(overridden),
        "refused_by_the_floor": len(refused),
        "override_rate": round(len(overridden) / len(calls), 3) if calls else None,
    }


def gates(entries: list[dict]) -> dict:
    """Control 57. Several dimensions together, because each alone is trivially gameable."""
    by_action = collections.Counter(r.get("action", "?") for r in entries)
    verified = collections.Counter(str(r.get("verified")) for r in entries)
    coverage = collections.Counter(str(r.get("coverage")) for r in entries)
    problems = [r for r in entries if r.get("problems") not in (None, "[]", [], "")]
    deploys = [r for r in entries if r.get("action") == "deploy"]
    unobserved = [r for r in deploys if str(r.get("verified")).lower() != "true"]
    return {
        "actions_logged": len(entries),
        "by_action": dict(by_action.most_common()),
        "verified_true": verified.get("True", "UNKNOWN — key absent"),
        "verified_not_true": sum(v for k, v in verified.items() if k != "True"),
        "coverage_states": dict(coverage),
        "entries_carrying_problems": len(problems),
        "deploys": len(deploys),
        "deploys_UNOBSERVED": len(unobserved),
        "false_accept_rate": "UNKNOWN — no ground truth for a gate that passed wrongly",
        "false_reject_rate": "UNKNOWN — rejected candidates are not retained (control 55)",
    }


def main() -> int:
    entries = rows()
    print("  GATE HEALTH — a vector, because any one dimension is trivially gameable\n")
    for key, value in gates(entries).items():
        print(f"    {key:26} {value}")
    print("\n  OVERRIDE METERING — control 50\n")
    for key, value in overrides(entries).items():
        print(f"    {key:26} {value}")
    print("\n  These numbers are not interpreted here. A low override rate may mean discipline or")
    print("  may mean nothing hard was attempted; a high one may mean the floor is wrong rather")
    print("  than abused. The control asks that the question be askable.")
    print("  Two dimensions read UNKNOWN rather than zero, and that is the honest value.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
