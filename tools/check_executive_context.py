#!/usr/bin/env python3
"""Verify the executive's governing instructions still match what the record holds.

    python3 tools/check_executive_context.py
    python3 tools/check_executive_context.py --json
    python3 tools/check_executive_context.py --repin      # deliberate, and says what it changes

**DETERMINISTIC.** No LLM, no network. A drift check, not a generator.

Why this exists
---------------
The instructions that actually govern the executive workbench are not all in this repository.
Claude Code loads `/home/reed/git/CLAUDE.md` from the parent workspace; Codex loads
`~/.codex/AGENTS.md` from its own home config. Neither was tracked here, in the manifest,
anchored, or visible to any party -- and both shape every review, design and refusal the layer
produces.

`record/executive/context/` now holds copies. **A copy is not a control.** The live files can be
edited without touching this repository, and a ratified copy that no longer matches what the
harness loads is exactly the theatre external review warned about: the executive controlling the
wording, the context and the account of compliance.

This check is the only thing that makes the pin mean anything.

FOUR STATES, NOT TWO — and why the old two broke publication for three and a half hours
----------------------------------------------------------------------------------------
Until 2026-08-12 this tool had two outcomes and a comment that read *"ABSENT IS NOT CLEAN. A
governing file that has vanished means the harness is running under instructions this record
cannot see."* That is correct on the operator's workbench and false everywhere else. Two of the
three pinned files live at absolute paths under one person's home directory; in CI, in any
implementer's clone, on any reviewer's laptop, they were never going to exist. The tool reported
**not measurable here** as **measured and bad**.

That is control 53 — a typed unknown must never be coerced into a value — running in the fail
direction rather than the usual pass direction. Both destroy the same distinction. On 2026-08-11
a negative control was added that runs this tool in CI for the first time; it exited non-zero,
the verify job failed, the deploy job was skipped, and **eight consecutive commits were pushed
and none were published** while every local gate stayed green.

So the result is now a state, and the exit code carries it:

    0   every declared dimension was checked and matched
    1   a checked dimension CONTRADICTED its pin — a real failure in any environment
    2   the checker or its configuration is broken; nothing was evaluated
    3   no contradiction found, but COVERAGE IS INCOMPLETE — a live source is unavailable here

Precedence is 2, then 1, then 3, then 0. Absence never outranks a contradiction, and a
contradiction is never downgraded because something else was unavailable.

**Exit 3 is not a pass.** `tools/land.py` admits only 0, so the operator cannot quietly accept
incomplete coverage on the one machine where the check is meaningful. CI admits 3 explicitly, in
the workflow where a reader can see the policy, rather than the checker deciding for it. Codex
put the boundary well on 2026-08-12: *the checker reports evidence, including unknowns; the
caller declares which states it admits.*

Availability is declared, never inferred
-----------------------------------------
An earlier draft of this fix decided "this is a foreign environment" by counting how many pinned
paths resolved — none meant CI, some meant trouble. Codex rejected it, and was right twice over:
it silently downgrades a real alarm if the operator's files all vanish at once, and it breaks the
moment one pin is correctly made repository-relative, because then CI resolves exactly one.

Each pin instead declares what KIND of locator it has:

    repo_relative            resolved against this checkout; checkable in EVERY clone
    absolute_operator_path   an external file; availability is environment-bound

`oagf-CLAUDE.md` is repository-relative and had been hiding behind an absolute path, so CI could
not measure a dimension it was perfectly able to measure. It is checked everywhere now.

What it cannot establish
-------------------------
* That the harness actually READ the file it loaded, or followed it.
* That no OTHER instruction reached the harness -- system prompts, per-session flags and tool
  descriptions are all outside its view.
* That the pinned text is good. Drift detection is not review. It passed on a pinned file
  containing a claim already shown false: **it verifies identity, not truth**.

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
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = REPO_ROOT / "record" / "executive" / "context"

#  Exit codes. Named because a bare integer at a call site says nothing about which of the four
#  states it is, and the whole point of this change is that the states are distinguishable.
VERIFIED = 0
CONTRADICTED = 1
CONFIG_ERROR = 2
INCOMPLETE = 3

REPO_RELATIVE = "repo_relative"
OPERATOR_PATH = "absolute_operator_path"
KINDS = (REPO_RELATIVE, OPERATOR_PATH)

HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")


def _utc_today() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ConfigError(Exception):
    """The pins document cannot be evaluated. Exit 2, never a vacuous 0."""


def load_pins(pins_dir: Path) -> dict:
    """Read and VALIDATE the pins document.

    Every failure here is exit 2 rather than a traceback, because a traceback exits 1 and 1 is
    the code that means DRIFT. A broken checker must not be readable as a detection.
    """
    path = pins_dir / "context-pins.json"
    if not path.is_file():
        raise ConfigError(f"no pin file at {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"{path.name} is not readable JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise ConfigError(f"{path.name} is not an object")
    pins = doc.get("pins")
    if not isinstance(pins, dict) or not pins:
        #  A pins document with no pins verifies nothing, and would otherwise exit 0 having
        #  checked nothing at all -- the vacuous pass this project has published before.
        raise ConfigError("the pins document declares no pins, so a pass would verify nothing")
    for name, pin in pins.items():
        if not isinstance(pin, dict):
            raise ConfigError(f"pin {name!r} is not an object")
        #  The pin NAME becomes a path under the context directory. A name carrying a separator
        #  or a parent reference would read or write outside it.
        if "/" in name or "\\" in name or name in ("", ".", "..") or name.startswith("."):
            raise ConfigError(f"pin name {name!r} is not a plain file name")
        source = pin.get("live_source")
        if not isinstance(source, dict):
            raise ConfigError(
                f"pin {name!r} has no live_source. A bare live_path cannot say whether its "
                f"absence means drift or means this is not the machine that holds it.")
        if source.get("kind") not in KINDS:
            raise ConfigError(f"pin {name!r}: live_source.kind {source.get('kind')!r} "
                              f"is not one of {list(KINDS)}")
        if not isinstance(source.get("path"), str) or not source["path"]:
            raise ConfigError(f"pin {name!r}: live_source.path is missing or empty")
        if source["kind"] == REPO_RELATIVE and Path(source["path"]).is_absolute():
            raise ConfigError(f"pin {name!r}: declared {REPO_RELATIVE} but its path is absolute")
        if source["kind"] == OPERATOR_PATH and not Path(source["path"]).is_absolute():
            raise ConfigError(f"pin {name!r}: declared {OPERATOR_PATH} but its path is relative")
        if not HEX64.match(str(pin.get("sha256", ""))):
            raise ConfigError(f"pin {name!r}: sha256 is missing or not 64 hex characters")
        if not isinstance(pin.get("bytes"), int):
            raise ConfigError(f"pin {name!r}: bytes is missing or not an integer")
    return doc


def resolve_live(pin: dict, repo_root: Path) -> Path:
    source = pin["live_source"]
    if source["kind"] == REPO_RELATIVE:
        return repo_root / source["path"]
    return Path(source["path"])


def evaluate(pins_dir: Path, repo_root: Path) -> tuple[int, dict]:
    """Two independent dimensions per pin, then one aggregate.

    THE COPY CHECK RUNS FIRST AND UNCONDITIONALLY. The version this replaced did `continue` on an
    absent live file, so the record's own copy went unverified precisely when it was the only
    thing still verifiable. Codex flagged it on 2026-08-12: internal checks must not be skipped
    by an external unavailability.
    """
    doc = load_pins(pins_dir)
    findings: dict[str, dict] = {}
    for name, pin in doc["pins"].items():
        copy = pins_dir / name
        if not copy.is_file():
            copy_state, copy_detail = "MISSING", "the record's copy is not in the tree"
        elif sha256_file(copy) != pin["sha256"]:
            copy_state, copy_detail = "MISMATCH", "the record's COPY does not match its own pin"
        else:
            copy_state, copy_detail = "MATCH", ""

        live = resolve_live(pin, repo_root)
        kind = pin["live_source"]["kind"]
        if not live.is_file():
            #  UNAVAILABLE, not absent-and-therefore-bad. Which of those it is depends on the
            #  environment, and the environment is the caller's to know.
            live_state = "UNAVAILABLE"
            live_detail = (f"{live} is not present here"
                           + (" — and it is repository-relative, so this checkout is incomplete"
                              if kind == REPO_RELATIVE else
                              " — an external file, expected only on the operator's workbench"))
        else:
            live_hash = sha256_file(live)
            if live_hash != pin["sha256"]:
                live_state = "MISMATCH"
                live_detail = (f"LIVE FILE HAS DRIFTED\n"
                               f"        pinned {pin['sha256'][:16]}…  ({pin['bytes']:,} bytes)\n"
                               f"        live   {live_hash[:16]}…  "
                               f"({live.stat().st_size:,} bytes)\n"
                               f"        The record's copy is no longer what the harness loads.")
            else:
                live_state, live_detail = "MATCH", ""

        findings[name] = {"kind": kind, "live_path": str(live),
                          "copy": copy_state, "copy_detail": copy_detail,
                          "live": live_state, "live_detail": live_detail}

    contradicted = [n for n, f in findings.items()
                    if f["copy"] in ("MISMATCH", "MISSING") or f["live"] == "MISMATCH"]
    unavailable = [n for n, f in findings.items() if f["live"] == "UNAVAILABLE"]
    if contradicted:
        status = CONTRADICTED
    elif unavailable:
        status = INCOMPLETE
    else:
        status = VERIFIED
    return status, {"status": status, "findings": findings,
                    "contradicted": contradicted, "unavailable": unavailable,
                    "checked": len(findings)}


VERSIONS = CONTEXT_DIR / "versions"


def repin(reason: str = "") -> int:
    """Re-pin deliberately, ARCHIVING the superseded copy first. Never silent, never automatic.

    The superseded text is kept, because a pinned file is a candidate RATIFICATION OBJECT and
    overwriting it destroys the thing a party was asked about. Codex caught this on 2026-08-10:
    `oagf-CLAUDE.md` was committed and pinned while containing a claim since shown false, and the
    check passed on it — the green check establishes that the false statement is faithfully
    deployed. **It verifies identity, not truth**, and a repin that erased v1 would have left no
    way to see what the ballot would have carried.

    So each supersession writes `versions/<name>.v<N>` and records the chain in the pins doc.
    """
    pins_path = CONTEXT_DIR / "context-pins.json"
    try:
        doc = load_pins(CONTEXT_DIR)
    except ConfigError as exc:
        print(f"  cannot re-pin: {exc}", file=sys.stderr)
        return CONFIG_ERROR
    changed = []
    for name, pin in doc["pins"].items():
        live = resolve_live(pin, REPO_ROOT)
        if not live.is_file():
            #  Re-pinning to a file that is not there would write a hash of nothing. This stays a
            #  hard refusal: a repin is a deliberate act on a file the operator can see.
            print(f"  cannot re-pin {name}: {live} is not present here", file=sys.stderr)
            return CONFIG_ERROR
        new = sha256_file(live)
        if new != pin["sha256"]:
            changed.append((name, pin["sha256"], new, pin["bytes"], live.stat().st_size))
            copy = CONTEXT_DIR / name
            history = pin.setdefault("superseded", [])
            if copy.is_file():
                VERSIONS.mkdir(parents=True, exist_ok=True)
                archived = VERSIONS / f"{name}.v{len(history) + 1}"
                archived.write_bytes(copy.read_bytes())
                history.append({"version": len(history) + 1,
                                "sha256": pin["sha256"], "bytes": pin["bytes"],
                                "archived_as": str(archived.relative_to(CONTEXT_DIR)),
                                "superseded_utc": _utc_today(), "reason": reason or "(none given)"})
            copy.write_bytes(live.read_bytes())
            pin["sha256"], pin["bytes"] = new, live.stat().st_size
            pin["version"] = len(history) + 1
    if not changed:
        print("nothing to re-pin; the live files match the record")
        return VERIFIED
    pins_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, old, new, ob, nb in changed:
        print(f"  re-pinned {name}: {old[:12]}… -> {new[:12]}…  ({ob:,} -> {nb:,} bytes)")
    print("\nThe governing instructions changed. That is a change to what steers the executive,")
    print("and it belongs in a commit that says what changed and why -- not folded into another.")
    return VERIFIED


BANNER = {
    VERIFIED: "VERIFIED — every declared dimension was checked and matched.",
    CONTRADICTED: "FAILED — the executive's governing instructions are not what the record says.",
    CONFIG_ERROR: "CANNOT EVALUATE — the checker's own configuration is broken.",
    INCOMPLETE: "INCOMPLETE COVERAGE — nothing contradicted its pin, and not everything was "
                "checked. This is NOT a pass.",
}


def report(result: dict) -> None:
    for name, f in result["findings"].items():
        print(f"  {name:28} {f['kind']:24} copy={f['copy']:9} live={f['live']}")
        for detail in (f["copy_detail"], f["live_detail"]):
            if detail:
                print(f"        {detail}")
    status = result["status"]
    print()
    if status == INCOMPLETE:
        print(f"  {len(result['unavailable'])} of {result['checked']} live source(s) could not be "
              f"examined here: {', '.join(result['unavailable'])}")
        print("  Their state is UNKNOWN, which is neither drift nor agreement. land.py admits")
        print("  only exit 0; CI admits this state explicitly, in the workflow, where the")
        print("  policy is visible to a reader.")
    print(f"  {BANNER[status]}")
    if status == VERIFIED:
        print("\n  This does NOT establish that either harness followed the pinned text, that no")
        print("  other instruction reached it, or that the pinned text is good.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reason", default="", help="why the governing text changed")
    parser.add_argument("--repin", action="store_true",
                        help="update the pins to the live files, printing every change")
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    parser.add_argument("--pins-dir", default=None,
                        help="evaluate a different pins directory (used by the tests, so a "
                             "negative control never has to damage the real tree)")
    parser.add_argument("--repo-root", default=None,
                        help="root that repo_relative sources resolve against")
    args = parser.parse_args(argv)
    if args.repin:
        if args.pins_dir or args.repo_root:
            print("  --repin operates on the real record only", file=sys.stderr)
            return CONFIG_ERROR
        return repin(args.reason)

    pins_dir = Path(args.pins_dir) if args.pins_dir else CONTEXT_DIR
    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    try:
        status, result = evaluate(pins_dir, repo_root)
    except ConfigError as exc:
        if args.json:
            print(json.dumps({"status": CONFIG_ERROR, "error": str(exc)}, indent=2))
        else:
            print(f"  {exc}", file=sys.stderr)
            print(f"\n  {BANNER[CONFIG_ERROR]}", file=sys.stderr)
        return CONFIG_ERROR

    if args.json:
        print(json.dumps(result, indent=2))
        return status
    if status in (CONTRADICTED, CONFIG_ERROR):
        report(result)
        print(f"\n  {BANNER[status]}", file=sys.stderr)
    else:
        report(result)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
