#!/usr/bin/env python3
"""Scan this repository's own tools for defect classes the register names.

    python3 tools/scan_own_code.py              # scan tools/*.py
    python3 tools/scan_own_code.py --fixtures   # this scanner's own negative control

WHAT THIS IS NOT — read this before quoting its output.

**It is not a compliance check against the register.** `tools/self_application.py` records a
determination PER CONTROL; this scans PER FILE for a handful of syntactic defect classes. Neither
establishes that the code complies with the 63 controls, and together they still do not:

* only 4 of 7 defect classes from the Consullo handoff are implemented here — the semantic ones
  (comment/code divergence, unconditional success literal, unused discriminating field) are not,
  and they are the ones that found the real defects in the file that prompted all this;
* a control ENFORCED somewhere is not the code complying everywhere. Control 5 is enforced inside
  `derive_counts.py`, and the "0 searches" error happened in a different script that never called
  it. This scanner does not check routing;
* 17 controls are VIOLATED structurally — one operator holding every role — and no scan repairs
  that.

WHY IT EXISTS ANYWAY. Detector classes were written for someone else's codebase in
`HANDOFF-agentbuilder-output-quality.md` and were never run on this one. That is the shape of
defect the register exists to catch, so the least that could be done was to run them here.

THE SCANNER'S OWN NEGATIVE CONTROL, and why it is not optional: the first version of D-E tested
`value in (0, None, True)`, and **`1 in (0, None, True)` is True in Python because `True == 1`**.
It reported 19 hits, every one a function returning exit code 1 — correct failure behaviour. An
unvalidated detector lied on its first run. `--fixtures` runs a must-flag and a must-not-flag case
for each class, and the suite fails if either arm is wrong.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCANNED = REPO_ROOT / "tools"


def empty_conditional(tree: ast.AST) -> list[int]:
    """D-A. `if cond: pass` — a branch that evaluates a condition and does nothing."""
    return [n.lineno for n in ast.walk(tree)
            if isinstance(n, ast.If) and len(n.body) == 1 and isinstance(n.body[0], ast.Pass)]


def constant_guard(tree: ast.AST) -> list[int]:
    """D-B. A name bound to a bool literal and later used as a bare condition."""
    #  ONLY names assigned exactly ONCE, to a bool literal. The first version kept the last
    #  literal assignment and ignored reassignment, so it flagged `in_table` -- an ordinary
    #  mutable state flag set True and False in different branches. Two false positives, on a
    #  detector whose fixtures both passed. Fixture agreement is not correctness on real code.
    assigned: dict[str, list] = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    assigned.setdefault(t.id, []).append(n)
    consts = {name: nodes[0].value.value for name, nodes in assigned.items()
              if len(nodes) == 1 and isinstance(nodes[0], ast.Assign)
              and isinstance(nodes[0].value, ast.Constant)
              and isinstance(nodes[0].value.value, bool)}
    return [n.lineno for n in ast.walk(tree)
            if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id in consts]


def success_from_except(tree: ast.AST) -> list[int]:
    """D-E. An except handler returning a success-shaped value.

    `is` and an exact type check, never `in (0, None, True)` — see the module docstring.

    A HIT IS NOT A DEFECT. Returning None from an except to mean "unavailable" is correct when
    the caller checks for it, which is control 53 done right. This cannot see the caller, so
    every hit needs reading.
    """
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Constant) and (
                    sub.value.value is None
                    or sub.value.value is True
                    or (type(sub.value.value) is int and sub.value.value == 0)):
                out.append(sub.lineno)
    return out


def unknown_defaults_to_number(tree: ast.AST) -> list[int]:
    """C53a. `d.get(key, 0)` — a MISSING value becomes a NUMBER.

    This is the '0 searches across 83 tool calls' defect in one expression: the scan could not
    see 69 files, absence defaulted to zero, and zero is indistinguishable from a true count.
    A default of 0 asserts "none" about something nobody looked at.

    `.get(key)` with NO default is correct and is not flagged: it yields None, which arithmetic
    refuses loudly. A string or list default is a different question and is out of scope here.
    """
    #  EXCLUDE THE COUNTER ACCUMULATOR. `d.get(k, 0) + 1` is the idiomatic way to count, and
    #  there "absent" genuinely DOES mean zero-so-far. Hand-reading the first sample found three
    #  of four hits were this, and one was the real thing: a value formatted straight into
    #  published prose, where a missing key prints as a true-looking zero. Flagging the idiom
    #  would have buried the defect under it.
    accumulators = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub)):
            for side in (n.left, n.right):
                if (isinstance(side, ast.Call) and isinstance(side.func, ast.Attribute)
                        and side.func.attr == "get"):
                    accumulators.add(id(side))
    out = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get" and len(n.args) == 2
                and id(n) not in accumulators
                and isinstance(n.args[1], ast.Constant)
                and type(n.args[1].value) in (int, float)
                and n.args[1].value is not True and n.args[1].value is not False):
            out.append(n.lineno)
    return out


def none_coerced_by_or(tree: ast.AST) -> list[int]:
    """C53b. `x or 0` — None, 0 and "" all collapse to 0, and the three mean different things.

    "not measured", "measured as zero" and "empty" are distinct findings. This operator erases
    the distinction silently, and the erased value reads downstream as a real measurement.
    """
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or):
            for value in n.values[1:]:
                if (isinstance(value, ast.Constant)
                        and type(value.value) in (int, float)
                        and value.value is not True and value.value is not False):
                    out.append(n.lineno)
    return out


CLASSES = {"D-A empty conditional body": empty_conditional,
           "D-B constant guard": constant_guard,
           "D-E success returned from an except": success_from_except,
           "C53a missing value defaults to a number": unknown_defaults_to_number,
           "C53b None coerced to a number by `or`": none_coerced_by_or}

FIXTURES = {
    "D-A empty conditional body": (
        "if x:\n    pass\n",
        "if x:\n    do_something()\n"),
    "D-B constant guard": (
        "allowed = True\nif allowed:\n    keep()\n",
        #  A reassigned state flag must NOT flag. This is the case the first version got wrong.
        "flag = False\nfor x in y:\n    if x:\n        flag = True\nif flag:\n    keep()\n"),
    "D-E success returned from an except": (
        "def f():\n    try:\n        g()\n    except Exception:\n        return 0\n",
        "def f():\n    try:\n        g()\n    except Exception:\n        return 1\n"),
    "C53a missing value defaults to a number": (
        "n = d.get('count', 0)\n",
        #  No default: yields None, which arithmetic refuses. Correct, must not flag.
        #  The counter idiom must NOT flag: absent genuinely means zero-so-far here.
        "counts[k] = counts.get(k, 0) + 1\n"),
    "C53b None coerced to a number by `or`": (
        "n = measured or 0\n",
        "n = measured if measured is not None else fail()\n"),
}


def run_fixtures() -> int:
    failures = 0
    for label, fn in CLASSES.items():
        must, must_not = FIXTURES[label]
        if not fn(ast.parse(must)):
            print(f"  \033[31mMISSED\033[0m {label} — did not flag the case it must flag")
            failures += 1
        elif fn(ast.parse(must_not)):
            print(f"  \033[31mFLAGGED\033[0m {label} — flagged the case it must not flag")
            failures += 1
        else:
            print(f"  \033[32mok\033[0m {label}")
    print()
    if failures:
        print(f"  {failures} detector(s) wrong. NOT FIT TO SCAN.", file=sys.stderr)
        return 1
    print("  Both arms pass for each class. That says the detectors behave on cases chosen to")
    print("  test them; it says nothing about their recall over real code, which is UNKNOWN.")
    return 0


DISPOSITIONS = REPO_ROOT / "record" / "claims" / "code-scan-dispositions.json"


def load_dispositions() -> dict:
    """Per-site dispositions, keyed by a hash of file + the line's text.

    Keyed by CONTENT, not line number: editing the line invalidates its disposition, so a site
    cannot be silently reworked under an old judgement. Line numbers drift on every insert and
    would let a stale disposition attach to whatever moved into the slot.
    """
    if not DISPOSITIONS.is_file():
        return {}
    return json.loads(DISPOSITIONS.read_text(encoding="utf-8")).get("sites", {})


def site_key(path: pathlib.Path, line_text: str) -> str:
    return hashlib.sha256(f"{path}\n{line_text.strip()}".encode()).hexdigest()[:16]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--fixtures", action="store_true")
    args = parser.parse_args()
    if args.fixtures:
        return run_fixtures()

    if run_fixtures() != 0:
        return 1
    print()
    files = unparsed = 0
    disp = load_dispositions()
    for label, fn in CLASSES.items():
        hits, dispositioned = [], 0
        for path in sorted(SCANNED.rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
                tree = ast.parse(text)
            except Exception:                                            # noqa: BLE001
                unparsed += 1
                continue
            source_lines = text.splitlines()
            for n in fn(tree):
                line_text = source_lines[n - 1] if n <= len(source_lines) else ""
                if site_key(path.relative_to(REPO_ROOT), line_text) in disp:
                    dispositioned += 1
                    continue
                hits.append(f"{path.relative_to(REPO_ROOT)}:{n}")
        print(f"  {label}: {len(hits)} undispositioned"
              f"{f', {dispositioned} dispositioned' if dispositioned else ''}")
        for h in hits[:8]:
            print(f"      {h}")
        if len(hits) > 8:
            print(f"      … {len(hits) - 8} more")
    files = len(list(SCANNED.rglob("*.py")))
    print(f"\n  {files} file(s) scanned, {unparsed} unparsed.")
    print("  A HIT IS A CANDIDATE, NOT A DEFECT. On 2026-08-11 all six D-E hits were functions")
    print("  returning a typed unknown that the caller checks — correct, not broken.")
    print("  This is not a compliance check against the register. See the module docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
