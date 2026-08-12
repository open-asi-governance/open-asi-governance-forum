#!/usr/bin/env python3
"""Negative controls for four tools that had none.

`tools/control_coverage.py` found 44 tools with no case they must fail. These four were taken
first for two different reasons:

* `check_executive_context.py` and `check_quotations.py` **run on every landing**. A gate that
  has never been observed to fail is the exact condition the register's flagship control forbids,
  and these two have gated every commit in this repository.
* `record_spend.py` and `reconcile_actions.py` **produce published numbers**. This record has
  published three wrong ones.

Each test breaks what the tool certifies and requires refusal, and each carries a **baseline**
arm — a guard that refuses everything is broken, not strict, and only the pair distinguishes them.

**The context-pin section was rebuilt on 2026-08-12** after its first version broke publication
for eight commits. It now builds a pins directory per case in a temp tree and asserts an EXACT
exit code, because the tool has four states rather than two and `!= 0` no longer means drift.
The reasoning is at the section itself.

**What these do NOT establish.** `check_executive_context.py` verifies **identity, not truth**: it
passed on a pinned file containing a claim already shown false. Its negative controls below target
**drift**, which is what it actually checks. No test here can make it notice a lie, because it was
never built to.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import subprocess as sp
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
#  What this suite drives to a REFUSAL, read by tools/control_coverage.py. A tool
#  named here must exist and this file must assert a refusal, or the scan fails —
#  a declaration is a claim, not a substitute for the case.
COVERS = ("check_executive_context.py",
          "check_quotations.py",
          "record_spend.py",
          "reconcile_actions.py",
          "land.py")

passed = FAILED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, FAILED
    if ok:
        passed += 1
        print(f"  \033[32m✓\033[0m {name}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {name}\033[0m")
        if detail:
            print(f"      {detail[:300]}")


def run(tool: str, *args: str) -> sp.CompletedProcess:
    return sp.run([sys.executable, str(ROOT / tool), *args],
                  cwd=REPO, capture_output=True, text=True)


guards = load_guards = None  # bound below, after load() is defined


def fired_in(output: str, code: str) -> bool:
    """Ask for a guard by name in a tool's PRINTED output.

    THE ABSTRACTION NEEDED ADAPTING HERE, which is what enrolling a second gate was for.
    `expect_guard(problems, code)` assumes an in-process list of refusal strings, and
    `control_application.py` returns exactly that. `check_quotations.py` is a different shape: it
    REFUSES BY PRINTING and exiting, so its fixture has to split the output into lines first.
    The wrapper still delegates to `expect_guard`, which is what the registry requires and what
    keeps the assertion raising rather than returning a discardable boolean.
    """
    try:
        guards.expect_guard(output.splitlines(), code)
    except guards.GuardNotActivated:
        return False
    return True


def load(name: str):
    """Import a tool as a module, to test a predicate rather than a subprocess exit code."""
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


guards = load("guards")

print("\ncheck_executive_context.py — four states, and the exit code must distinguish them")

#  WHY THIS IS BUILT ON FIXTURES AND NOT ON THE REAL TREE.
#
#  The first version of this section ran the real checker and asserted `returncode == 0` as its
#  baseline. On this workbench the three pinned files exist, so it passed. In CI two of them
#  never could, the tool read absence as drift, the verify job failed and **the deploy job was
#  skipped for eight consecutive commits**. A test that can only pass on one machine is not a
#  negative control; it is a machine-shaped assertion.
#
#  It also asserted `returncode != 0` for the drift arm. Now that exit 3 means "not checkable
#  here", any non-zero would satisfy that arm — an UNAVAILABLE result would have masqueraded as
#  a detected drift. Codex flagged both on 2026-08-12. Every case below asserts an EXACT code.
#
#  And it injected the fault by editing the operator's real governing file, restoring it in a
#  `finally`. An interrupt between the two leaves the workbench's own instructions modified.
#  These build a whole pins directory in a temp tree instead, so no arm can damage the record.

CTX = "check_executive_context.py"


def make_pins(tmp: pathlib.Path, pins: dict, copies: dict[str, str],
              repo_files: dict[str, str] | None = None) -> tuple[pathlib.Path, pathlib.Path]:
    """Build a pins directory and a repo root for one case. Returns (pins_dir, repo_root)."""
    pins_dir = tmp / "context"
    repo_root = tmp / "repo"
    pins_dir.mkdir(parents=True, exist_ok=True)
    repo_root.mkdir(parents=True, exist_ok=True)
    (pins_dir / "context-pins.json").write_text(
        json.dumps({"pins": pins}, indent=2), encoding="utf-8")
    for name, body in copies.items():
        (pins_dir / name).write_text(body, encoding="utf-8")
    for rel, body in (repo_files or {}).items():
        (repo_root / rel).write_text(body, encoding="utf-8")
    return pins_dir, repo_root


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def pin(kind: str, path: str, body: str) -> dict:
    return {"live_source": {"kind": kind, "path": path},
            "sha256": digest(body), "bytes": len(body.encode())}


def state(pins_dir: pathlib.Path, repo_root: pathlib.Path) -> tuple[int, str]:
    r = run(CTX, "--pins-dir", str(pins_dir), "--repo-root", str(repo_root))
    return r.returncode, r.stdout + r.stderr


GOVERNING = "# governing text\n"
DRIFTED = "# governing text, edited outside the record\n"
#  An absolute path that exists on no machine, so "unavailable" is genuinely unavailable rather
#  than an accident of whoever runs the suite.
ABSENT = "/zzqx-nonexistent-operator-path/AGENTS.md"

with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)

    #  1. Everything present and matching -> VERIFIED.
    live = tmp / "case1-live.md"
    live.write_text(GOVERNING, encoding="utf-8")
    d, root = make_pins(tmp / "c1",
                        {"external.md": pin("absolute_operator_path", str(live), GOVERNING),
                         "inrepo.md": pin("repo_relative", "CLAUDE.md", GOVERNING)},
                        {"external.md": GOVERNING, "inrepo.md": GOVERNING},
                        {"CLAUDE.md": GOVERNING})
    code, out = state(d, root)
    check("BASELINE: copies and live sources all match -> exit 0", code == 0, f"rc={code}\n{out}")

    #  2. The record's COPY differs while the live source is unavailable. Checkable everywhere,
    #     and the reason the copy check must not be skipped when the live file is missing —
    #     which is exactly what the replaced version did with an early `continue`.
    d, root = make_pins(tmp / "c2",
                        {"external.md": pin("absolute_operator_path", ABSENT, GOVERNING)},
                        {"external.md": DRIFTED})
    code, out = state(d, root)
    check("a COPY that does not match its own pin -> exit 1, even with live unavailable",
          code == 1, f"rc={code}; an internal check must not be skipped by an external absence")

    #  3. The record's copy missing entirely, live unavailable.
    d, root = make_pins(tmp / "c3",
                        {"external.md": pin("absolute_operator_path", ABSENT, GOVERNING)}, {})
    code, out = state(d, root)
    check("a MISSING copy -> exit 1, even with live unavailable", code == 1, f"rc={code}\n{out}")

    #  4. Copies valid, every external live source unavailable. THE CI CASE. This must be 3 and
    #     must never be 0 or 1: not 1 because nothing contradicted anything, not 0 because a
    #     dimension went unmeasured and 0 is what a caller reads as verified.
    d, root = make_pins(tmp / "c4",
                        {"a.md": pin("absolute_operator_path", ABSENT, GOVERNING),
                         "b.md": pin("absolute_operator_path", ABSENT + "2", GOVERNING)},
                        {"a.md": GOVERNING, "b.md": GOVERNING})
    code, out = state(d, root)
    check("all external live sources unavailable, copies valid -> exit 3, NOT 0 and NOT 1",
          code == 3, f"rc={code}\n{out}")
    check("...and it says so rather than printing a bare pass",
          "INCOMPLETE" in out and "not a pass" in out.lower(), out[-200:])

    #  5. PARTIAL coverage: one live source resolves, another does not. The design this replaced
    #     inferred the environment by counting resolved paths and would have called this a
    #     failure — and it is the ordinary CI shape the moment one pin is repo-relative.
    live5 = tmp / "case5-live.md"
    live5.write_text(GOVERNING, encoding="utf-8")
    d, root = make_pins(tmp / "c5",
                        {"here.md": pin("absolute_operator_path", str(live5), GOVERNING),
                         "gone.md": pin("absolute_operator_path", ABSENT, GOVERNING)},
                        {"here.md": GOVERNING, "gone.md": GOVERNING})
    code, out = state(d, root)
    check("one live source present and one absent -> exit 3 with a partial-coverage diagnostic",
          code == 3 and "gone.md" in out, f"rc={code}\n{out}")

    #  6. Precedence: a contradiction outranks an unavailability. If this ever returned 3 the
    #     tool would be hiding real drift behind a missing file.
    live6 = tmp / "case6-live.md"
    live6.write_text(DRIFTED, encoding="utf-8")
    d, root = make_pins(tmp / "c6",
                        {"drifted.md": pin("absolute_operator_path", str(live6), GOVERNING),
                         "gone.md": pin("absolute_operator_path", ABSENT, GOVERNING)},
                        {"drifted.md": GOVERNING, "gone.md": GOVERNING})
    code, out = state(d, root)
    check("DRIFT alongside an unavailable source -> exit 1; a contradiction outranks an unknown",
          code == 1, f"rc={code}\n{out}")

    #  7. A repo-relative source that drifts. This one is checkable in CI and in every clone.
    d, root = make_pins(tmp / "c7",
                        {"inrepo.md": pin("repo_relative", "CLAUDE.md", GOVERNING)},
                        {"inrepo.md": GOVERNING},
                        {"CLAUDE.md": DRIFTED})
    code, out = state(d, root)
    check("a REPO-RELATIVE live source that drifts -> exit 1 in any environment", code == 1,
          f"rc={code}\n{out}")

    #  8. Configuration errors -> exit 2, never a vacuous 0 and never 1. A broken checker must
    #     not be readable as a detection, and an empty pins doc must not pass having checked
    #     nothing.
    for label, pins_obj in (
            ("an EMPTY pins document", {}),
            ("a pin with no live_source", {"x.md": {"sha256": digest(GOVERNING), "bytes": 1}}),
            ("a pin whose kind is unknown",
             {"x.md": {"live_source": {"kind": "guess", "path": "/x"},
                       "sha256": digest(GOVERNING), "bytes": 1}}),
            ("a pin name that escapes the context directory",
             {"../x.md": pin("absolute_operator_path", ABSENT, GOVERNING)}),
            ("a malformed sha256",
             {"x.md": {"live_source": {"kind": "absolute_operator_path", "path": ABSENT},
                       "sha256": "not-a-hash", "bytes": 1}}),
            ("a repo_relative pin given an absolute path",
             {"x.md": pin("repo_relative", "/etc/passwd", GOVERNING)})):
        d, root = make_pins(tmp / f"c8-{abs(hash(label))}", pins_obj, {})
        code, out = state(d, root)
        check(f"{label} -> exit 2", code == 2, f"rc={code}\n{out[-200:]}")

    #  Invalid JSON, written directly because make_pins would serialise it.
    d = tmp / "c8-json" / "context"
    d.mkdir(parents=True)
    (d / "context-pins.json").write_text("{not json", encoding="utf-8")
    code, out = state(d, tmp / "c8-json")
    check("a pins document that is not JSON -> exit 2, not a traceback exiting 1", code == 2,
          f"rc={code}\n{out[-200:]}")

#  The real tree, retained. On the operator's workbench this must be 0; anywhere else the
#  external pins are unavailable and 3 is the honest answer. Both are accepted HERE because this
#  suite runs in both places — the policy that only 0 may land lives in land.py, and the policy
#  that CI may accept 3 lives in the workflow, where a reader can see each one.
r = run(CTX)
check("the real record evaluates to a state this suite recognises (0 here, 3 in a clone)",
      r.returncode in (0, 3), f"rc={r.returncode}\n{(r.stdout + r.stderr)[-300:]}")

#  AND THE ADMISSION POLICY ITSELF. Introducing exit 3 created a way for the whole apparatus to
#  go quiet: if land.py ever treated "not a contradiction" as good enough, drift in the
#  operator's governing files would stop blocking anything, on the one machine that can see it.
#  This tests the predicate directly rather than the constant, so widening it in either
#  direction fails here.
land = load("land")
check("land.py admits exit 0 from the context-pin gate", land.admitted("context-pins", 0) is True)
for refused in (1, 2, 3):
    check(f"land.py REFUSES exit {refused} from the context-pin gate",
          land.admitted("context-pins", refused) is False,
          "exit 3 is incomplete coverage, and admitting it here would retire the pin")
check("...and the same rule applies to every other gate",
      all(land.admitted(name, 3) is False and land.admitted(name, 0) is True
          for name, _cmd in land.GATES))

print("\ncheck_quotations.py — it must refuse a quotation that is in no corpus file")

r = run("check_quotations.py")
check("BASELINE: every published quotation is in the corpus", r.returncode == 0,
      (r.stdout + r.stderr)[-200:])

#  BOTH FORMS, retained permanently. On 2026-08-11 the inline form was refused and the SAME
#  sentence in a blockquote PASSED -- and this record quotes parties in blockquotes far more
#  often than inline. The checker built for D-53 did not cover the form a fabrication would
#  actually take here. Keeping both arms is control 45: a later rewrite must still catch what
#  this one catches.
#
#  The filename carries no exempting marker. The first fixture was called
#  "_negative-control-FABRICATED-quote.md" and "fabricat" is an EXEMPT_MARKER, so the fixture
#  risked exempting itself.
scratch = REPO / "record" / "findings" / "zzqx-quotation-negative-control.md"
INVENTED = "Zzqx invented sentence appearing in no raw sample anywhere in this corpus at all."
for label, body in (
        ("inline", f'The claude party wrote: "{INVENTED}"\n'),
        ("blockquote", f"The claude party wrote:\n\n> {INVENTED}\n")):
    try:
        scratch.write_text(f"# temporary, deleted by the test that wrote it\n\n{body}",
                           encoding="utf-8")
        r = run("check_quotations.py")
        check(f"a FABRICATED quotation is refused ({label})", r.returncode != 0,
              f"rc={r.returncode}; D-53 was a fabricated party quotation and this is that fault")
    finally:
        scratch.unlink(missing_ok=True)
r = run("check_quotations.py")
check("...and the tree is clean again after removing it", r.returncode == 0)

#  THE SHAPE THE FABRICATION ACTUALLY TAKES. Both arms above plant the quotation on ONE LINE,
#  and both patterns forbade a newline — so this gate could see only single-line quotations while
#  every design document here is wrapped markdown at ~98 columns. D-53 was a fabricated party
#  quotation IN A DESIGN DOCUMENT; a fabrication of any substance wraps; the gate could not have
#  caught the next one.
#
#  Measured before the repair: 235 candidates across 98 files, ONE attributed to a party, that
#  one exempted — zero quotations checked, every run, for months. The negative control passed the
#  whole time because the fault was injected in the form that works and never in the form that
#  occurs. Control 45: the single-line arms above are KEPT, because a repair must still catch
#  what the old gate caught.
WRAPPED = ("Zzqx invented sentence that runs on long enough to wrap the way\n"
           "prose actually wraps in this record, appearing in no raw sample.")
#  THE BLOCKQUOTE ARM DOES NOT TEST THE REPAIRED REGEX. It carries no quote delimiters, so it
#  exercises the pre-existing blockquotes() path — kept as a regression for that path, and NOT
#  counted as coverage of the pattern change. The curly arm is what covers the second pattern,
#  which had none: Codex found the new regex exercised only for straight quotes.
for label, body in (
        ("inline, wrapped, straight quotes", f'The claude party wrote: "{WRAPPED}"\n'),
        ("inline, wrapped, CURLY quotes",
         'The claude party wrote: \u201c' + WRAPPED + '\u201d\n'),
        ("blockquote, wrapped — the blockquote path, not the pattern",
         "The claude party wrote:\n\n> " + WRAPPED.replace("\n", "\n> ") + "\n")):
    try:
        scratch.write_text(f"# temporary, deleted by the test that wrote it\n\n{body}",
                           encoding="utf-8")
        r = run("check_quotations.py")
        check(f"a FABRICATED quotation that WRAPS is refused ({label})", r.returncode != 0,
              f"rc={r.returncode}; a gate blind to wrapped quotations is blind to the defect it "
              f"was built for")
        check(f"...and it is QT-02 that fired ({label})",
              fired_in(r.stdout + r.stderr, "QT-02"), (r.stdout + r.stderr)[-200:])
    finally:
        scratch.unlink(missing_ok=True)

#  AND A QUOTATION MUST NOT SWALLOW A PARAGRAPH BREAK. Allowing newlines without bounding them
#  would let one unclosed quote mark consume the rest of a document and match anything.
try:
    scratch.write_text('# temporary\n\nThe claude party wrote: "an unclosed quotation mark that '
                       'must not swallow\n\nthe entire rest of this document as one quotation."\n',
                       encoding="utf-8")
    r = run("check_quotations.py")
    check("a quote spanning a BLANK LINE is not treated as one quotation", r.returncode == 0,
          (r.stdout + r.stderr)[-200:])
finally:
    scratch.unlink(missing_ok=True)

#  QT-03 — BOUNDARY FIXTURES at the cap. An over-length attributed quotation was INVISIBLE, not
#  refused, and Codex found four real candidates at 5,350 characters sitting past it. 4,000 must
#  still be checked and 4,001 must refuse, or the bound is a silent exclusion.
quotations_mod = load("check_quotations")
CAP = quotations_mod.MAX_LENGTH
for label, size, must_refuse in (("at the cap", CAP, False), ("one past it", CAP + 1, True)):
    body = "z" * size
    try:
        scratch.write_text(f"# temporary\n\nThe claude party wrote: \"{body}\"\n",
                           encoding="utf-8")
        r = run("check_quotations.py")
        out = r.stdout + r.stderr
        if must_refuse:
            check(f"an attributed quotation {label} is REFUSED, not skipped", r.returncode != 0,
                  f"rc={r.returncode}; a bound that hides a quotation is a silent exclusion")
            check(f"...and it is QT-03 that fired ({label})", fired_in(out, "QT-03"), out[-200:])
        else:
            #  At the cap it is a normal candidate, so it is CHECKED — and being invented, it
            #  must fail as an unverified quotation rather than pass or be skipped.
            check(f"an attributed quotation {label} is still checked", r.returncode != 0,
                  f"rc={r.returncode}")
            check(f"...and it is QT-02, not the oversize guard ({label})",
                  fired_in(out, "QT-02"), out[-200:])
    finally:
        scratch.unlink(missing_ok=True)

r = run("check_quotations.py")
check("...and the tree is clean again after the boundary fixtures", r.returncode == 0)

#  QT-01 — the corpus itself unreadable. Its message says "a check that cannot fail is not a
#  check", which is control 2 stated inline and never once exercised.
quotations = load("check_quotations")
real_corpus = quotations.load_corpus
try:
    quotations.load_corpus = lambda: ""
    import contextlib
    import io
    out = io.StringIO()
    saved_argv = sys.argv
    try:
        sys.argv = ["check_quotations.py"]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = quotations.main()
    finally:
        sys.argv = saved_argv
    check("an EMPTY corpus is refused rather than passing every quotation", code == 2,
          f"rc={code}; with no corpus every quotation is unverifiable, not verified")
    check("...and it is QT-01 that fired", fired_in(out.getvalue(), "QT-01"),
          out.getvalue()[-200:])
finally:
    quotations.load_corpus = real_corpus

print("\nrecord_spend.py / reconcile_actions.py — they must refuse rather than emit a number")

#  THIS ARM CORRUPTED THE LEDGER 87 TIMES, and passed while doing it.
#
#  `record_spend.py` did not validate the cohort: it APPENDED a zero-unit row for
#  `no-such-cohort-zzqx` and exited 0. The assertion was `returncode != 0 or not emitted_cost`,
#  and because no dollar figure was printed the second disjunct held — so an append passed as a
#  refusal. 87 of the ledger's 141 entries were this fixture, written on every landing, and the
#  correction is at record/cycles/spend-ledger-correction-2026-08-12.md. See D-62.
#
#  Three things changed, and all three are needed. The tool refuses (RS-01). The arm requires a
#  NON-ZERO EXIT rather than the absence of a printed cost. And the ledger is asserted
#  BYTE-IDENTICAL afterwards — because "it printed no cost" was never evidence that it wrote
#  nothing, and a test that cannot see its own side effects is not testing a refusal.
spend = load("record_spend")
LEDGER = spend.LEDGER if hasattr(spend, "LEDGER") else None
ledger_path = REPO / "record" / "cycles" / "spend-ledger.json"
before_bytes = ledger_path.read_bytes()

r = run("record_spend.py", "--cohort", "no-such-cohort-zzqx")
check("record_spend REFUSES an unknown cohort", r.returncode != 0,
      f"rc={r.returncode}; stdout={r.stdout[:160]!r}")
check("...and it is RS-01 that fired", fired_in(r.stdout + r.stderr, "RS-01"),
      (r.stdout + r.stderr)[-200:])
check("...and the ledger is BYTE-IDENTICAL afterwards",
      ledger_path.read_bytes() == before_bytes,
      "a refusal that appends is not a refusal, and this arm could not see the difference")
check("...and it printed no cost either", "$" not in r.stdout)

r = run("record_spend.py", "--report")
check("BASELINE: the spend report still runs", r.returncode == 0, (r.stderr or r.stdout)[-160:])

#  THIS ARM WAS VACUOUS, in the same shape that caused D-62 and by the same author on the same
#  day: `r.returncode != 0 OR "0 unexplained" not in r.stdout`. A disjunct passes on its weaker
#  limb, and the weaker limb held — the tool exited 0, reported "0 commits", and the phrase it
#  looked for was never in the output in any run. So the arm asserted a refusal that had never
#  once happened, and the real behaviour was worse than the one it was written to catch:
#  `git log --since=<garbage>` exits 0 and matches nothing, the log filter compared timestamps as
#  STRINGS so every real entry sorted below "zzqx-...", and the tool that produced control 1's
#  evidence reported PERFECT RECONCILIATION from an input that resolved to nothing. See D-66.
r = run("reconcile_actions.py", "--since", "zzqx-not-a-revision")
check("reconcile_actions REFUSES an unresolvable revision", r.returncode != 0,
      f"rc={r.returncode}; stdout={r.stdout[:160]!r}")
check("...and prints no reconciliation figure at all",
      "unexplained" not in r.stdout and "commits)" not in r.stdout,
      f"stdout={r.stdout[:200]!r}")
check("...and says the input did not resolve, rather than reporting agreement",
      "not a parseable instant" in (r.stdout + r.stderr),
      (r.stdout + r.stderr)[-200:])

r = run("reconcile_actions.py")
check("BASELINE: reconciliation runs against the current lease", r.returncode == 0,
      (r.stderr or r.stdout)[-160:])

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
