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


def load(name: str):
    """Import a tool as a module, to test a predicate rather than a subprocess exit code."""
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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

print("\nrecord_spend.py / reconcile_actions.py — they must refuse rather than emit a number")

r = run("record_spend.py", "--cohort", "no-such-cohort-zzqx")
emitted_cost = "$" in r.stdout
check("record_spend refuses an unknown cohort rather than printing a cost",
      r.returncode != 0 or not emitted_cost,
      f"rc={r.returncode}; stdout={r.stdout[:160]!r}")

r = run("record_spend.py", "--report")
check("BASELINE: the spend report still runs", r.returncode == 0, (r.stderr or r.stdout)[-160:])

r = run("reconcile_actions.py", "--since", "zzqx-not-a-revision")
check("reconcile_actions refuses an unresolvable revision rather than reporting zero",
      r.returncode != 0 or "0 unexplained" not in r.stdout,
      f"rc={r.returncode}; stdout={r.stdout[:160]!r}")

r = run("reconcile_actions.py")
check("BASELINE: reconciliation runs against the current lease", r.returncode == 0,
      (r.stderr or r.stdout)[-160:])

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
