#!/usr/bin/env python3
"""Guards with names, so a fixture can say WHICH one it activated — controls 45 and 2.

    from guards import guard

    out.append(guard("CA-07", f"C{rank}: declared complete and names no test."))

    # in the fixture
    check("...", activates(found, "CA-07"))

    python3 tools/guards.py            # every declared guard and whether a fixture names it
    python3 tools/guards.py --check    # refuse an unexercised guard or a fixture naming none

WHY, AND IT IS THE SAME REASON THREE TIMES
--------------------------------------------
Control 45 says a modification to a gate must ship evidence that the new gate detects at least
what the old one did. Nothing mechanised that here, so it depended on somebody remembering — and
in the same week, three separate guards turned out to be doing nothing while every suite was
green:

* `if r["complete"] and not r["tests"]` in `control_application.py` was **unreachable**, because
  `complete` is defined to require tests. Declaring a row finished with no test produced no
  objection at all (D-59).
* the same file's C44 row **advertised** a reason-quality check that existed only in the other
  matrix; three injected inputs produced nothing (D-59).
* `closed_world.Survey` returned successful results for four incoherent walks, and the fixture
  protecting it asserted the absence of a string removed in the same edit (D-60).

Each was found by a human writing a fixture and looking, or by external review. **A fixture that
observes "some refusal happened" cannot tell a live guard from a dead one beside it**, and that
is the hole all three fell through: another guard fired, the assertion passed, and the guard
under test was never exercised.

WHAT THIS ADDS. A guard carries a stable code. A fixture names the code it expects. Then two
things become mechanical rather than remembered:

    an UNEXERCISED guard      declared in the code, named by no fixture — where dead guards hide
    an ORPHANED expectation   named by a fixture, declared nowhere — a gate that lost a check

The second is control 45 directly: remove a guard in a rewrite and the fixture that named it
fails, rather than passing because a neighbouring guard happened to fire.

WHAT IT DOES NOT DO
--------------------
* It does not prove a guard is *correct*, only that some fixture drives it.
* It does not find guards that were never written. An absent check has no code to be missing.
* Codes are assigned by hand and mean nothing outside this repository. Two guards could share a
  code and this would not notice — `--check` refuses a duplicate for that reason, which is the
  most it can do about it.
* It finds expectations by AST — calls to `activates(...)` or `fired(...)` with a literal code —
  NOT by reading the source text. A lexical scan was written first and would have repeated this
  repository's own defect: `control_coverage.py` matched tool names lexically and counted a
  COMMENT as coverage, reading a note that a tool had no negative control as that tool's negative
  control. What AST does not establish is that the call's result is asserted rather than
  discarded; a fixture calling `activates(...)` and ignoring the answer would still register.
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
TESTS = TOOLS / "tests"

CODE = re.compile(r"\A[A-Z]{2,4}-\d{2}\Z")


def guard(code: str, message: str) -> str:
    """Tag a refusal message with the identity of the guard that produced it.

    The code goes at the END, in brackets, so the message still reads as a sentence to a human
    and the machine-readable part does not lead. A reader should see what went wrong before they
    see a label they have no use for.
    """
    if not CODE.match(code):
        raise ValueError(f"guard code {code!r} must look like 'CA-07'")
    return f"{message} [{code}]"


def activates(problems: list[str], code: str) -> bool:
    """Did THIS guard fire? Not 'did something fire', which is the distinction that matters.

    TERMINAL PARSE, not substring membership. `"[CA-07]" in p` matched a message that merely
    MENTIONED another guard's code — Codex's counterexample was a refusal tagged `[CA-08]` whose
    text discussed `[CA-07]`, which returned True for the wrong guard. The tag is the last thing
    on the line by construction, so the match anchors there.
    """
    return any(p.rstrip().endswith(f"[{code}]") for p in problems)


class GuardNotActivated(AssertionError):
    """The named guard did not fire. Raised, so the result cannot be discarded."""


def expect_guard(problems: list[str], code: str) -> None:
    """THE canonical way a fixture asks for a guard, and the only form the registry counts.

    It raises rather than returning a boolean, because `activates(problems(), "ZZ-02")` on a line
    by itself registered as an expectation while asserting nothing — Codex reproduced it. A
    predicate whose result can be discarded is not a test, and a registry that counts the call
    rather than the assertion inherits that.

    STATIC ANALYSIS STILL CANNOT PROVE THE LINE RAN. A call inside a branch nobody takes counts
    here. Runtime receipts or coverage would be needed for that, and neither exists.
    """
    if not activates(problems, code):
        raise GuardNotActivated(
            f"guard {code} did not fire. Problems seen: {problems if problems else '(none)'}")


def declared() -> dict[str, list[str]]:
    """Every `guard("CODE", ...)` call site, found by AST rather than by regex over source."""
    found: dict[str, list[str]] = {}
    for path in sorted(TOOLS.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "guard" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                found.setdefault(node.args[0].value, []).append(
                    f"{path.name}:{node.lineno}")
    return found


def expected() -> dict[str, list[str]]:
    """Every guard code a fixture ASKS FOR, found by AST rather than by reading the source text.

    AST, NOT LEXICAL, and the reason is this repository's own history: `control_coverage.py`
    matched tool names lexically and counted a COMMENT as coverage — a note saying a tool had no
    negative control was read as that tool's negative control. Doing the same here would have
    counted a code mentioned in a comment, in a docstring, or inside a fixture file written as a
    string literal by another test.

    So this looks for CALLS to `activates(...)` or `fired(...)` with a literal code. A code that
    appears anywhere else in a test is not an expectation, because asking for a guard by name is
    an act, not a mention.

    A suite whose codes are FIXTURE DATA rather than claims about real guards declares
    `SYNTHETIC_GUARD_CODES = True` at module level. Exactly one file does — the suite that tests
    this mechanism, whose XX-/ZZ- codes describe guards that do not and should not exist. The
    declaration is in the file rather than in a list here, so it is visible to whoever reads the
    file and cannot be granted from a distance.
    """
    found: dict[str, list[str]] = {}
    if not TESTS.is_dir():
        return found
    for path in sorted(TESTS.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        #  EXEMPT CODES, NOT AN EXEMPT FILE. This was `SYNTHETIC_GUARD_CODES = True`, which
        #  exempted the whole module — so a real orphaned expectation added to that file later
        #  would have vanished with the fixture data. Codex narrowed it: name the codes.
        synthetic: set[str] = set()
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "SYNTHETIC_GUARD_CODES"
                    and isinstance(node.value, (ast.Tuple, ast.List))):
                synthetic = {e.value for e in node.value.elts
                             if isinstance(e, ast.Constant) and isinstance(e.value, str)}
        #  A LOCAL WRAPPER IS ACCEPTED ONLY IF IT DEMONSTRABLY DELEGATES. Suites define a small
        #  `fired(code)` helper so the label and the outcome sit on one line, and counting the
        #  name blindly would let any function called `fired` register an expectation. So the
        #  wrapper's own body is parsed and must contain a call to `expect_guard`; otherwise only
        #  direct `expect_guard` calls count. Neither form proves the line executed — a call in a
        #  branch nobody takes still registers, and that needs runtime receipts this has not got.
        wrappers = {
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and any(isinstance(inner, ast.Call)
                    and (getattr(inner.func, "id", "") == "expect_guard"
                         or getattr(inner.func, "attr", "") == "expect_guard")
                    for inner in ast.walk(node))}
        accepted = {"expect_guard"} | wrappers
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and node.args):
                continue
            name = (node.func.id if isinstance(node.func, ast.Name)
                    else node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if name not in accepted:
                continue
            for arg in node.args:
                if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                        and CODE.match(arg.value) and arg.value not in synthetic):
                    found.setdefault(arg.value, []).append(path.name)
    return found


BASELINE = REPO_ROOT / "record" / "executive" / "guard-baseline.json"


def baseline() -> dict:
    """The guards this repository has COMMITTED to keeping, and the removals it has authorised.

    THE TEMPORAL HALF, and without it the mechanism proved nothing C45 asks for. Comparing
    current declarations against current expectations catches a guard removed while its fixture
    survives — and a real rewrite removes both, which passed silently. Codex reproduced it:
    baseline `[]`, delete guard and fixture together, `[]`.

    So the codes are committed to a file. A code in the baseline that is no longer declared is a
    REMOVAL, and a removal is refused unless it is recorded here with a ground — which makes
    weakening a governed event rather than a diff nobody reads. That is the property control 45
    is about: not that the code and its fixture agree today, but that today's gate still catches
    what yesterday's did.
    """
    if not BASELINE.is_file():
        return {"guards": {}, "authorised_removals": {}}
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def stamp() -> int:
    """Record the current guards as the baseline. Deliberate, and it says what it adds."""
    doc = baseline()
    current = declared()
    added = sorted(set(current) - set(doc["guards"]))
    doc["guards"] = {code: sites[0] for code, sites in sorted(current.items())}
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  baseline now holds {len(doc['guards'])} guard(s)"
          + (f"; added {', '.join(added)}" if added else "; nothing new"))
    print("  Adding a guard to the baseline is a commitment to keep catching what it catches.")
    return 0


def problems() -> list[str]:
    declared_codes, expected_codes = declared(), expected()
    out = []
    for code, sites in sorted(declared_codes.items()):
        if len(sites) > 1:
            out.append(f"{code} is declared at {len(sites)} sites ({', '.join(sites)}). One code "
                       f"per guard, or a fixture naming it cannot say which fired.")
        if code not in expected_codes:
            out.append(f"{code} at {sites[0]} is declared and NO fixture names it. An unexercised "
                       f"guard is where an unreachable one hides — three were found this week.")
    #  THE TEMPORAL CHECK. A guard in the baseline that is no longer declared has been removed,
    #  and removing both the guard and its fixture is exactly the rewrite control 45 governs.
    committed = baseline()
    for code, site in sorted(committed.get("guards", {}).items()):
        if code in declared_codes:
            continue
        ground = (committed.get("authorised_removals") or {}).get(code)
        if not ground or len(str(ground)) < 20:
            out.append(f"{code} was in the baseline (at {site}) and is DECLARED NOWHERE now. "
                       f"Removing a guard and its fixture together is the weakening control 45 "
                       f"forbids without evidence. Record it under authorised_removals with a "
                       f"ground, or restore it.")
    if not declared_codes:
        #  A registry with nothing enrolled passes every check by having nothing to check.
        out.append("no guards are declared anywhere. An empty registry is not a clean one — "
                   "--check would succeed by having nothing to look at.")

    for code, files in sorted(expected_codes.items()):
        if code not in declared_codes:
            out.append(f"{code} is named by {', '.join(files)} and is declared nowhere. Either "
                       f"the guard was removed in a rewrite — which is what control 45 forbids "
                       f"without evidence — or the fixture names a code that never existed.")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on an unexercised guard, an orphaned expectation, "
                             "or a baseline guard that has been removed")
    parser.add_argument("--stamp", action="store_true",
                        help="commit the current guards as the baseline this repository keeps")
    args = parser.parse_args()

    if args.stamp:
        return stamp()

    found = problems()
    if found:
        for p in found:
            print(f"  ✗ {p}", file=sys.stderr)
        print(f"\n  {len(found)} problem(s). A guard nobody drives is indistinguishable from a "
              f"guard that cannot fire.", file=sys.stderr)
        return 1

    declared_codes, expected_codes = declared(), expected()
    if args.check:
        print(f"  {len(declared_codes)} named guard(s), each declared once and each named by at "
              f"least one fixture.")
        return 0
    print("  NAMED GUARDS — each one a refusal a fixture can ask for by name\n")
    for code, sites in sorted(declared_codes.items()):
        print(f"    {code}  {sites[0]:34}  named by {', '.join(expected_codes[code])}")
    print(f"\n  {len(declared_codes)} named. This says a fixture DRIVES each one. It does not say")
    print("  the guard is correct, and it cannot see a check that was never written — an absent")
    print("  guard has no code to be missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
