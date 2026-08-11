#!/usr/bin/env python3
"""Reconcile the action log against what the repository actually shows happened.

    python3 tools/reconcile_actions.py                 # since the current lease was granted
    python3 tools/reconcile_actions.py --since 2026-08-09
    python3 tools/reconcile_actions.py --json

**DETERMINISTIC.** No LLM, no network. Reads git and the log; writes nothing.

Renewal condition 3 of the executive trial, which had been prose since 2026-08-10.

The hole this exists to measure
--------------------------------
**A self-reporting logger cannot name an action that never calls it.** The action log records
pushes, tests and Codex invocations because those paths were wired to it. Writing a design
document, filing a finding, recording a decision, editing a party-facing prompt, building a tool,
and — worst — **modifying the gate itself** were all invisible to it, not because they were
concealed but because the log's ontology had no word for them.

So the check cannot come from the log. It comes from the side: enumerate what the repository can
be *shown* to have done, from git, and subtract what the log claims. **What remains is the
omission**, and naming it is the whole output.

What it enumerates, and why each
---------------------------------
* **commits** — the coarsest evidence anything happened at all.
* **governed writes** — changes under `record/`, `spec/` and `corpus/artifacts/`, the material a
  party or an auditor reads.
* **decisions and findings** — the artifacts that carry claims forward.
* **prompt and spec files** — what parties were actually asked; edits here change what the record
  means.
* **paid solicitations** — new `corpus/raw/` cohorts, the only actions that spend the custodian's
  money.
* **gate modifications** — changes to `tools/executive_log.py`, `executive_lease.py`, `land.py`,
  the verifiers and their tests. **Called out separately because the log cannot attest its own
  source**, and a change here alters the meaning of every entry downstream of it.

What it cannot establish
-------------------------
* **That the log is honest.** It compares two artifacts the same layer produced.
* **That git is complete.** Work done and never committed is invisible to both sides, so a
  reconciliation that balances proves nothing about uncommitted action.
* **That an unprofiled action was harmless.** It says only that nothing checked it.
* **That gate modification is safe.** It counts them. Detecting a *malicious* one needs a pin held
  outside this repository, which does not exist.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import executive_lease as lease                                          # noqa: E402
import executive_log as ex                                              # noqa: E402

#  Effect classes, in the order a reader should care about them.
EFFECTS = (
    ("gate_modification", ("tools/executive_log.py", "tools/executive_lease.py", "tools/land.py",
                           "tools/verify_negative_control.py", "tools/check_quotations.py",
                           "tools/check_executive_context.py", "tools/validate_provenance.py")),
    ("paid_solicitation", ("corpus/raw/",)),
    ("prompt_or_spec_edit", ("record/solicitations/", "spec/", "tools/schemas/")),
    ("decision", ("record/decisions/",)),
    ("finding", ("record/findings/",)),
    ("design_or_review", ("record/designs/", "record/executive/")),
    ("published_artifact", ("corpus/artifacts/", "docs/")),
)

#  Action classes the log knows about, mapped to the effect they would leave.
LOGGED_TO_EFFECT = {"push": "commits", "test": None, "codex_invoke": None,
                    "codex_return_captured": None}


def git(*args) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else ""


def commits_since(since: str) -> list[str]:
    out = git("log", f"--since={since}", "--format=%H")
    return [line for line in out.splitlines() if line.strip()]


def files_in(commit: str) -> list[str]:
    return [line for line in
            git("show", "--name-only", "--format=", commit).splitlines() if line.strip()]


def classify(path: str) -> str | None:
    for name, prefixes in EFFECTS:
        if any(path == p or path.startswith(p) for p in prefixes):
            return name
    return None


def reconcile(since: str) -> dict:
    commits = commits_since(since)
    effects: Counter = Counter()
    per_effect_commits: dict[str, set] = {}
    for commit in commits:
        for path in files_in(commit):
            name = classify(path)
            if name:
                effects[name] += 1
                per_effect_commits.setdefault(name, set()).add(commit[:12])

    logged = [e for e in ex.read_log() if e.get("utc", "") >= since]
    by_action = Counter(e.get("action") for e in logged)
    by_coverage = Counter(e.get("coverage") or "(untyped, pre-dates typing)" for e in logged)

    #  What the log VERIFIES versus what the repository SHOWS. Pushes are the only effect class
    #  with a postcondition profile, so everything else is by construction unverified.
    verified_classes = {"commits"}
    omissions = []
    for name, _ in EFFECTS:
        if effects.get(name) and name not in verified_classes:
            omissions.append({
                "effect": name,
                "file_changes": effects[name],
                "commits": sorted(per_effect_commits.get(name, ())),
                "verified_by": None,
                "why": "no postcondition profile exists for this effect class; the log records "
                       "the push that carried it and nothing about the effect itself"})

    return {
        "since": since,
        "commits": len(commits),
        "logged_actions": dict(by_action),
        "logged_coverage": dict(by_coverage),
        "repository_effects": dict(effects),
        "omissions": omissions,
        #  Absent is not zero: this figure is the evidence behind control 1, and a key-shape
        #  change would report "no gate modifications" rather than "not measured".
        "gate_modifications": effects.get("gate_modification", "UNKNOWN"),
        "what_this_cannot_establish": [
            "That the log is honest — it compares two artifacts the same layer produced.",
            "That git is complete — work never committed is invisible to both sides.",
            "That an unprofiled action was harmless; only that nothing checked it.",
            "That a gate modification was safe. Detecting a malicious one needs a pin held "
            "outside this repository, which does not exist.",
        ]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--since", help="ISO date; defaults to when the current lease was granted")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    since = args.since or (lease.current() or {}).get("granted_utc") or "2026-08-09"
    result = reconcile(since)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"  since {since}  ({result['commits']} commits)\n")
    print("  LOGGED — what the action log claims")
    for action, n in sorted(result["logged_actions"].items()):
        print(f"    {n:4d}  {action}")
    print("\n  COVERAGE — what each entry is worth")
    for state, n in sorted(result["logged_coverage"].items()):
        print(f"    {n:4d}  {state}")
    print("\n  OBSERVED — what the repository shows happened")
    for effect, n in sorted(result["repository_effects"].items(), key=lambda kv: -kv[1]):
        mark = "  " if effect == "commits" else "!!"
        print(f"    {mark}{n:4d}  {effect}")
    if result["omissions"]:
        print(f"\n  {len(result['omissions'])} effect class(es) OCCURRED AND WERE NOT VERIFIED:")
        for omission in result["omissions"]:
            print(f"    {omission['effect']:22s} {omission['file_changes']} file change(s) "
                  f"across {len(omission['commits'])} commit(s)")
    if result["gate_modifications"]:
        print(f"\n  \033[31m{result['gate_modifications']} GATE MODIFICATION(S)\033[0m — the log "
              f"cannot attest its own source, so\n  every entry above is downstream of code "
              f"nothing here vouches for.")
    print("\n  This does not establish that the log is honest, that git is complete, or that any\n"
          "  unprofiled action was harmless. It establishes what was never checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
