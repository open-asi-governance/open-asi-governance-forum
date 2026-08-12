#!/usr/bin/env python3
"""Per-file compliance with the registered controls that have a file-level surface.

    python3 tools/control_coverage.py            # the matrix
    python3 tools/control_coverage.py --check    # refuse if any tool has no determination

WHY PER FILE. `tools/self_application.py` records a determination PER CONTROL — a declaration that
control 5 is enforced *by derive_counts.py*. It says nothing about the other seventy tools, and the
"0 searches" error happened in a script that never called derive_counts. **A control enforced
somewhere is not the code complying everywhere**, and only a per-file view can show the difference.

WHICH CONTROLS HAVE A FILE-LEVEL SURFACE AT ALL. Most do not, and pretending otherwise would
manufacture 63 × 71 mostly-meaningless cells. Control 6 is not a property a file can have; control
1 needs a second key holder; the goal-graph and evolutionary families need structures this
repository lacks. Recorded here so the exclusion is an argument rather than an omission (control
44):

    C2   negative control            YES — a tool either has a case it must fail, or it does not
    C5   closed-world measurement    partial — needs semantics; not attempted here
    C10  bounded claim               partial — needs semantics; not attempted here
    C53  typed unknown               partial — `scan_own_code.py` covers one syntactic slice
    everything else                  NO file-level surface. System, organisational, or structural.

**Only C2 is measured here.** It is the register's flagship and the one with an unambiguous
file-level answer. The others are named as unmeasured rather than quietly dropped.

WHAT A PASS MEANS, EXACTLY. That some test referencing the tool asserts a refusal, a non-zero exit,
a raise, or a must-reject fixture. It does **not** mean the negative control is a good one, that it
targets the capability rather than the transport (N5), or that the tool is correct. A tool can hold
a demanding fixture and still be broken everywhere the fixture does not look.
"""

from __future__ import annotations

import argparse
import ast
import io
import tokenize
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
TESTS = TOOLS / "tests"

#  Ways this repository's tests assert that something REFUSED. Broad on purpose: a false pass
#  here understates the gap, and understating it is the failure mode that matters.
REFUSAL = re.compile(
    r"returncode\s*==\s*[1-9]|returncode\s*!=\s*0|rc\s*==\s*[1-9]|exit\s*[1-9]|"
    r"is False|assertRaises|pytest\.raises|except\s+\w*Error|"
    r"refus|reject|must[_ ]fail|must[_ ]be[_ ]rejected|non-?zero|REFUSED|BROKEN|NOT FIT",
    re.I)

#  Tools that are libraries or one-shot utilities with no assurance signal of their own. Each
#  needs a REASON, not a bare exemption.
NO_SIGNAL: dict[str, str] = {
    "codex_budget.py": "reads a budget number; emits no assurance signal of its own",
    "render_markdown.py": "pure formatting; no verdict to be wrong about",
    "code_freetext.py": "text extraction helper; no verdict",
}


def tool_files() -> list[pathlib.Path]:
    return sorted(p for p in TOOLS.glob("*.py") if p.name != "__init__.py")


def self_hosted_fixtures(path: pathlib.Path) -> bool:
    """Does the tool SHIP its own must-fail cases?

    Added after validation: verify_fault_injection.py carries FOURTEEN must-reject fixtures and a
    --fixtures mode, and the first version of this measure scored it NONE because it only looked
    in tools/tests/ and because the test still references the pre-rename alias. A negative control
    that ships with the tool is a better negative control, not an absent one. Measuring only one
    location produced a false NONE on the repository's flagship verifier.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    return bool(re.search(r"--fixtures|must[_ ]be[_ ]rejected|must[_ ]reject|MUST be rejected|"
                          r"must_flag|run_fixtures", text))


def executable_text(text: str) -> str:
    """The test's CODE, with its docstring and every comment removed.

    A MENTION IS NOT AN EXERCISE, and prose keeps finding new places to hide. First it was the
    module docstring: test_chain_guards.py named anchor_manifest.py in its prose and never
    exercised it, and this measure counted that as coverage — a test's own docstring gaming the
    measure of that test, accidentally, within minutes of both being written. That was stripped
    via `ast`, not a regex, because the first attempt anchored at string start and every suite
    here begins with a shebang, so it stripped nothing and the false pass survived its own fix.

    Then it was a COMMENT. On 2026-08-12 a note in test_gate_refusals.py recorded that
    arm_acceptance.py CANNOT have a negative control yet — and because the note sat beside the
    tool's name and contained the words "negative control", this scanner reported the tool as
    COVERED on the strength of the sentence saying it is not. Codex found it the same day, in
    the batch of work whose entire subject was control 2.

    So comments go too. What is left is what the test actually executes.
    """
    try:
        doc = ast.get_docstring(ast.parse(text))
        if doc:
            text = text.replace(doc, "", 1)
    except SyntaxError:
        pass
    out = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                continue
            out.append(token.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        #  Untokenizable is UNKNOWN, not clean. Returning the raw text keeps the old (weaker)
        #  behaviour rather than silently reporting no references at all.
        return text
    return " ".join(out)


def resolve_aliases(text: str) -> str:
    """Substitute simple `NAME = "tool.py"` bindings back into their uses.

    STRIPPING COMMENTS MADE THIS NECESSARY, and finding out why is the useful part. With prose
    removed, `check_executive_context.py` — which has fifteen fixture-driven refusal cases —
    reported as UNCOVERED, because its suite binds the name once as `CTX =
    "check_executive_context.py"` and then drives everything through `CTX`. The only textual
    mention sat 600 characters away from the assertions.

    So the scanner had BOTH errors at once: it counted tools named only in prose, and missed
    tools exercised only through a variable. Removing the first exposed the second.

    This resolves the one binding shape that actually occurs here. It is still lexical, and
    Codex's standing recommendation is an explicit tool→test mapping or AST call detection —
    recorded in the module docstring rather than pretended away.
    """
    aliases: dict[str, str] = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
                and node.value.value.endswith(".py")):
            aliases[node.targets[0].id] = node.value.value
    for name, tool in aliases.items():
        text = re.sub(rf"\b{re.escape(name)}\b", tool, text)
    return text


def declared_coverage(text: str) -> tuple[str, ...]:
    """A module-level `COVERS = ("tool.py", ...)` — what this suite says it exercises.

    WHY DECLARATION BEAT PROXIMITY. The lexical heuristic below had both errors at once. It
    counted tools named only in a COMMENT, and it MISSED `check_executive_context.py`, which has
    fifteen fixture-driven refusal cases — because the suite binds the name once as a constant
    and drives it through a wrapper function, so no assertion sits within 600 characters of the
    tool's name. Resolving simple aliases did not fix that, and would not: the invocation is a
    call to `state()`, not to the constant.

    A declaration is explicit, lives beside the code, and CANNOT ROT SILENTLY: a declared tool
    that does not exist fails the scan, and a declaration is not enough on its own — the file
    must still contain a refusal assertion, or a suite could claim coverage it never wrote.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ()
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "COVERS"
                and isinstance(node.value, (ast.Tuple, ast.List))):
            return tuple(e.value for e in node.value.elts
                         if isinstance(e, ast.Constant) and isinstance(e.value, str))
    return ()


def has_negative_control(stem: str) -> tuple[bool, str]:
    """A test asserting a refusal, OR the tool shipping its own must-fail cases."""
    own = TOOLS / f"{stem}.py"
    if own.is_file() and self_hosted_fixtures(own):
        return (True, "ships its own must-fail fixtures")
    if not TESTS.is_dir():
        return (False, "no tests directory")
    #  A DECLARATION FIRST, and only when the file also asserts a refusal somewhere. The
    #  declaration says which tool; the refusal says something was actually required to fail.
    #  Neither alone is coverage.
    for t in sorted(TESTS.rglob("*.py")):
        raw = t.read_text(encoding="utf-8", errors="replace")
        if f"{stem}.py" in declared_coverage(raw):
            if REFUSAL.search(executable_text(raw)):
                return (True, f"{t.name} declares it in COVERS and asserts a refusal")
            return (False, f"{t.name} declares it in COVERS but asserts no refusal")

    referencing = []
    for t in sorted(TESTS.rglob("*.py")):
        text = t.read_text(encoding="utf-8", errors="replace")
        #  STRIP THE MODULE DOCSTRING. test_chain_guards.py named anchor_manifest.py in its
        #  prose and never exercised it, and this measure counted that as coverage -- a test's
        #  own docstring gaming the measure of that test, accidentally, within minutes of both
        #  being written. A mention is not an exercise.
        #
        #  Via ast, not a regex: the first attempt anchored at string start and every suite here
        #  begins with a shebang, so it stripped nothing and the false pass survived the fix.
        text = resolve_aliases(executable_text(text))
        if stem in text:
            referencing.append((t.name, text))
    if not referencing:
        return (False, "no test references it")
    for name, text in referencing:
        #  Only the portion of the test that mentions this tool, so a refusal assertion about a
        #  DIFFERENT tool in the same file is not counted. Crude window, deliberately narrow.
        for m in re.finditer(re.escape(stem), text):
            window = text[max(0, m.start() - 600): m.end() + 600]
            if REFUSAL.search(window):
                return (True, f"{name} asserts a refusal near a reference to it")
    return (False, f"referenced by {referencing[0][0]} but no refusal is asserted near it")


def rows() -> list[tuple[str, str, str]]:
    out = []
    for path in tool_files():
        stem = path.stem
        if path.name in NO_SIGNAL:
            out.append((path.name, "NOT_APPLICABLE", NO_SIGNAL[path.name]))
            continue
        ok, why = has_negative_control(stem)
        out.append((path.name, "HAS_NEGATIVE_CONTROL" if ok else "NONE", why))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if any tool has no determination")
    args = parser.parse_args()

    data = rows()
    has = [r for r in data if r[1] == "HAS_NEGATIVE_CONTROL"]
    none = [r for r in data if r[1] == "NONE"]
    na = [r for r in data if r[1] == "NOT_APPLICABLE"]

    if args.check:
        undetermined = [r for r in data if r[1] not in
                        ("HAS_NEGATIVE_CONTROL", "NONE", "NOT_APPLICABLE")]
        if undetermined:
            for r in undetermined:
                print(f"  no determination for {r[0]}", file=sys.stderr)
            return 1
        print(f"  every tool has a determination ({len(data)}).")
        return 0

    print("  CONTROL 2 PER FILE — does each tool have a case it must fail?\n")
    print(f"    HAS_NEGATIVE_CONTROL  {len(has):3d}")
    print(f"    NONE                  {len(none):3d}")
    print(f"    NOT_APPLICABLE        {len(na):3d}   (each with a stated reason)")
    print(f"    ---------------------------")
    print(f"    total                 {len(data):3d}")
    pct = len(has) / (len(has) + len(none)) if (has or none) else 0
    print(f"\n    {pct:.0%} of tools with an assurance signal have a negative control.\n")
    print("  WITHOUT ONE:")
    for name, _s, why in none[:20]:
        print(f"    {name:34} {why}")
    if len(none) > 20:
        print(f"    … {len(none) - 20} more")
    print("\n  A pass means SOME test asserts a refusal near a reference to the tool. It does not")
    print("  mean the control is demanding, that it targets the capability rather than the")
    print("  transport, or that the tool is correct. Control 2 raises the floor from 'never")
    print("  observed to fail' to 'observed to fail at least once'. This measures that floor and")
    print("  nothing above it.")
    print("\n  Only control 2 is measured. C5, C10 and C53 need semantics and are NOT attempted;")
    print("  every other control has no file-level surface. See the module docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
