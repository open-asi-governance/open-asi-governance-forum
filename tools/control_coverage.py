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
import json
import ast
import io
import tokenize
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import closed_world                                                    # noqa: E402
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


#  DECLARED, NOT INFERRED. What this replaces was a regex over the tool's whole source text for
#  `--fixtures`, `must reject` and friends — and on 2026-08-12 Codex showed it was wrong RIGHT
#  THEN, not merely fragile. Five of the eight tools it scored on this path matched on PROSE:
#
#    build_controls_page.py   a control's register text, "a fixture it must reject"
#    build_viewer.py          that same register text rendered into a page
#    test_integrity.py        a comment quoting it
#    control_coverage.py      ITS OWN DOCSTRING, describing this very heuristic
#
#  The measure counted itself as covered on the strength of a paragraph explaining how it
#  measures coverage. That is the mention-is-not-an-exercise defect, in the file whose docstring
#  records having fixed that defect twice already. See D-68.
#
#  Two obvious repairs were tried and each failed differently, which is why this is a hand
#  declaration and not a cleverer detector:
#
#    an AST shape — look for `add_argument("--fixtures")` or a `run_fixtures` def — produced a
#    FALSE NEGATIVE on verify_negative_control.py, which imports run_fixtures from a shared core.
#
#    running the flag and checking exit 0 — build_controls_page.py, build_viewer.py and
#    test_integrity.py all EXIT 0 on `--fixtures` while ignoring it entirely and doing their
#    ordinary work, so a zero exit is not evidence of a fixtures mode. Only control_coverage.py
#    rejected the unknown flag.
#
#  So each entry is a human's assertion with a place to look, and it is labelled as an assertion
#  in the output rather than presented as a measurement.
SELF_HOSTED = {
    "verify_fault_injection.py": "ships 14 must-reject fixtures; `--fixtures` runs them and "
                                 "prints whether each was rejected",
    "verify_negative_control.py": "`--fixtures` runs the same must-reject/must-accept cases "
                                  "through run_fixtures(), imported from the shared core",
    "check_claims.py": "`--fixtures` runs spec/claims/fixtures/*.json, each labelled clean or "
                       "flagged, so a detector that stopped detecting fails",
    "scan_own_code.py": "`--fixtures` runs one must-flag case per detector (D-A, D-B, D-E, "
                        "C53a, C53b, D-F)",
}


def self_hosted_fixtures(path: pathlib.Path) -> bool:
    """Does the tool ship its own must-fail cases? DECLARED above, never inferred from text."""
    return path.name in SELF_HOSTED


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

    #  THE PROXIMITY FALLBACK IS GONE. It scored a tool covered when a refusal assertion sat
    #  within 600 characters of the tool's NAME anywhere in a test's executable text — inference,
    #  not evidence, and it carried 21 of 41 determinations. Codex, asked whether this measure was
    #  fit to become a landing gate: it is wrong NOW, not merely fragile, and a baseline stamped
    #  from its output would give temporal force to the errors. See D-68.
    #
    #  Each of the 21 was read by hand. Seventeen were genuine and are now DECLARED in the suite
    #  that exercises them. Four were not, and they fall to NONE where they belong:
    #
    #    agenda_selectors.py      matched prose inside a check LABEL about a different component
    #    build_controls_page.py   matched an assertion unrelated to it
    #    ingest_capture.py        matched a `shutil.copy` list of file names
    #    round_cycle.py           matched an assertion about party_key
    #
    #  A tool with a real refusal case and no declaration now reads NONE. That is a false
    #  negative, and it is the direction to be wrong in: it under-reports coverage instead of
    #  claiming coverage nobody wrote. The remedy is one line in the suite that already tests it.
    return (False, f"no suite DECLARES it in COVERS. If a test does require it to refuse, say so "
                   f"there; proximity to the tool's name is no longer read as evidence (D-68)")


def survey_population() -> "closed_world.Survey":
    """The walk, under control 5: a rate this cannot compute is not reported as a rate.

    This tool publishes a PERCENTAGE over a population of files, which is exactly the shape
    control 5 governs — and it read the tests by `read_text(errors="replace")` and parsed them
    with `ast`, swallowing a SyntaxError into `pass`. A test file that would not parse simply
    contributed nothing, and the percentage came out looking like a measurement.

    That is not a hypothetical for this tool in particular. It has already been wrong in both
    directions in one day: counting a tool named only in a comment, and missing one exercised
    through a wrapper. A rate from an incomplete walk is the third way it could be wrong, and
    the only one nobody would see.
    """
    survey = closed_world.Survey("tools with a negative control", scope="tools/*.py")
    for path in tool_files():
        survey.seen(path.name)
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError) as error:
            survey.unreadable(path.name, f"{type(error).__name__}: {error}")
            continue
        if path.name in NO_SIGNAL:
            survey.excluded(path.name, NO_SIGNAL[path.name])
            continue
        ok, _why = has_negative_control(path.stem)
        survey.accounted(path.name)
        survey.count("has a negative control" if ok else "has none")
    for t in sorted(TESTS.rglob("*.py")):
        #  THE TESTS ARE IN SCOPE TOO. The verdict for every tool depends on reading them, so a
        #  test this cannot parse makes every "NONE" unreliable, not just its own.
        survey.seen(f"tests/{t.name}")
        try:
            ast.parse(t.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError) as error:
            survey.unreadable(f"tests/{t.name}", f"{type(error).__name__}: {error}")
            continue
        #  A test is EVIDENCE, not a member of the measured denominator. It is in scope because
        #  every tool's verdict depends on reading it — one unparseable test makes the whole NONE
        #  set unreliable, not just its own — but it is accounted separately so it never inflates
        #  the population the rate is computed over. Codex's distinction, 2026-08-12.
        survey.accounted(f"tests/{t.name}")
    return survey


#  Bumped whenever the RULE changes, never when a determination changes. A baseline that
#  records this can distinguish "the measure was corrected" from "a tool lost its coverage",
#  which are opposite events that look identical in a diff of the numbers.
DETECTOR_CONTRACT_VERSION = 2

BASELINE = REPO_ROOT / "record" / "executive" / "coverage-baseline.json"


def baseline() -> dict:
    if not BASELINE.is_file():
        return {"detector_contract_version": None, "determinations": {},
                "authorised_regressions": {}}
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def ratchet(current: list[tuple[str, str, str]]) -> list[str]:
    """NON-REGRESSION ONLY. It says nothing about whether coverage is adequate.

    Codex's ruling, and the name he insisted on: a gate called "coverage" whose green means only
    that nothing was lost would be a green signal not downstream of what a reader takes it to
    certify, which is this repository's dominant failure class. So the gate is
    `negative-control-ratchet`, and its success line says how much legacy debt remains.

    Three transitions, and only one of them is forbidden:

        NONE -> HAS            allowed, and the baseline must be restamped to lock it in
        a NEW tool -> NONE     forbidden; new debt does not enter
        HAS -> NONE            forbidden

    `authorised_regressions` exists and is deliberately narrow. Codex refused an ordinary
    HAS -> NONE exemption: a tool that still emits an assurance signal and has lost its negative
    control is a regression, not an exception. The only grounds are that the tool is GONE, or
    that its assurance signal is gone and it has become NOT_APPLICABLE with a reason.
    """
    committed = baseline()
    if not committed["determinations"]:
        return ["no baseline has been stamped; run --stamp deliberately, having read it"]

    out = []
    if committed.get("detector_contract_version") != DETECTOR_CONTRACT_VERSION:
        #  A measurement correction and a coverage regression look identical in a diff of the
        #  numbers. The version makes them different events.
        out.append(
            f"the baseline was stamped under detector contract "
            f"v{committed.get('detector_contract_version')} and this is v"
            f"{DETECTOR_CONTRACT_VERSION}. A determination that moved may be a corrected "
            f"MEASUREMENT rather than a lost negative control, and the two must not be "
            f"confused. Re-read the diff, then --stamp.")
        return out

    now = {name: status for name, status, _why in current}
    was = committed["determinations"]
    excused = committed.get("authorised_regressions") or {}

    for name, old_status in sorted(was.items()):
        new_status = now.get(name)
        if new_status is None:
            #  THE SAME GROUND FLOOR AS THE OTHER BRANCH. The first version accepted any truthy
            #  value here, so the word "because" excused a vanished tool while a 40-character
            #  minimum guarded the neighbouring case — caught by this ratchet's own fixture,
            #  which is the only reason the two branches now agree.
            ground = excused.get(name)
            if not ground or len(str(ground)) < 40:
                out.append(f"{name} was in the baseline ({old_status}) and is GONE. If the tool "
                           f"was withdrawn, record it under authorised_regressions with a ground "
                           f"that says who withdrew it and why.")
            continue
        if old_status == "HAS_NEGATIVE_CONTROL" and new_status != "HAS_NEGATIVE_CONTROL":
            ground = excused.get(name)
            if not ground or len(str(ground)) < 40:
                out.append(f"{name} HAD a negative control and now reads {new_status}. A tool "
                           f"that still emits an assurance signal and has lost its case-it-must-"
                           f"fail is a regression, not an exception.")
    for name, status in sorted(now.items()):
        if name not in was and status == "NONE":
            out.append(f"{name} is NEW and arrives with no negative control. New debt does not "
                       f"enter; give it a case it must fail, or record why it needs none.")
    return out


def stamp() -> int:
    doc = baseline()
    current = {name: status for name, status, _ in rows()}
    gained = sorted(n for n, s in current.items()
                    if s == "HAS_NEGATIVE_CONTROL"
                    and doc["determinations"].get(n) != "HAS_NEGATIVE_CONTROL")
    doc["detector_contract_version"] = DETECTOR_CONTRACT_VERSION
    doc["determinations"] = dict(sorted(current.items()))
    doc.setdefault("authorised_regressions", {})
    doc["what_this_is"] = (
        "The determinations this repository commits to not losing. It is a RATCHET and not a "
        "target: a number that may not fall is also a number nobody has to raise, and the "
        "success line says how much legacy debt remains so that stagnation is visible rather "
        "than merely permitted.")
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    covered = sum(1 for s in current.values() if s == "HAS_NEGATIVE_CONTROL")
    print(f"  baseline holds {len(current)} determination(s), {covered} covered, under detector "
          f"contract v{DETECTOR_CONTRACT_VERSION}"
          + (f"; newly locked in: {', '.join(gained)}" if gained else ""))
    return 0


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
                        help="NON-REGRESSION ONLY: refuse a lost negative control or new debt")
    parser.add_argument("--stamp", action="store_true",
                        help="commit the current determinations as the baseline")
    args = parser.parse_args()

    survey = survey_population()

    #  CONTROL 5, BEFORE ANY NUMBER REACHES A READER. The first version consulted the survey
    #  only just before the PERCENTAGE, having already printed HAS / NONE / NOT_APPLICABLE and a
    #  total — which are the partial population counts the control protects, with the rate
    #  merely the most quotable of them. And `--check` did not consult it at all, so the gate
    #  passed on a population it could not fully read. Both found by Codex on 2026-08-12.
    try:
        survey.result()
    except closed_world.IncompleteSurvey as refusal:
        print(survey.report())
        print(f"\n  NO COUNT AND NO RATE IS REPORTED: {refusal}", file=sys.stderr)
        return 1

    if args.stamp:
        return stamp()

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
        regressions = ratchet(data)
        if regressions:
            for line in regressions:
                print(f"  REFUSED  {line}", file=sys.stderr)
            return 1
        covered = sum(1 for _n, s, _w in data if s == "HAS_NEGATIVE_CONTROL")
        debt = sum(1 for _n, s, _w in data if s == "NONE")
        #  THE SUCCESS LINE SAYS WHAT IT MEANS. Codex: do not describe this green as "control
        #  coverage passed". It is non-regression, and the remaining debt is printed beside it so
        #  a stagnant number is visible on every landing rather than merely permitted.
        print(f"  NON-REGRESSION ONLY — {covered} tool(s) hold a declared negative control and "
              f"{debt} legacy tool(s) still have none.")
        print(f"  This does not say the coverage is adequate, that any case is demanding, or "
              f"that the {debt} are unprotected — only that nothing was lost and no new debt "
              f"entered. Detector contract v{DETECTOR_CONTRACT_VERSION}.")
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
    #  EVERY ONE, not the first twenty. Truncating the debt list is how a stagnant number stops
    #  looking stagnant; Codex named the 20-item cap while ruling on the ratchet.
    for name, _s, why in none:
        print(f"    {name:34} {why}")
    print("\n  A pass means a suite DECLARES the tool in COVERS and asserts a refusal, or the")
    print("  tool ships its own must-fail fixtures. It does not")
    print("  mean the control is demanding, that it targets the capability rather than the")
    print("  transport, or that the tool is correct. Control 2 raises the floor from 'never")
    print("  observed to fail' to 'observed to fail at least once'. This measures that floor and")
    print("  nothing above it.")
    print("\n  Only control 2 is measured. C5, C10 and C53 need semantics and are NOT attempted;")
    print("  every other control has no file-level surface. See the module docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
