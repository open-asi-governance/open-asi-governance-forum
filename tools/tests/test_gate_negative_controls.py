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

**What these do NOT establish.** `check_executive_context.py` verifies **identity, not truth**: it
passed on a pinned file containing a claim already shown false. Its negative control below targets
**drift**, which is what it actually checks. No test here can make it notice a lie, because it was
never built to.
"""

from __future__ import annotations

import json
import pathlib
import subprocess as sp
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
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


print("\ncheck_executive_context.py — it must notice DRIFT (not falsity; it cannot see falsity)")

r = run("check_executive_context.py")
check("BASELINE: the live tree matches its pins", r.returncode == 0,
      (r.stdout + r.stderr)[-200:])

#  The pin metadata is context-pins.json -> "pins" -> <name> -> "live_path", an ABSOLUTE path.
#  The first version guessed at "path"/"live"/"source", found nothing, and reported that the
#  fault could not be injected -- which is the honest failure, but it was my key names that were
#  wrong, not the tool's.
pins_doc = json.loads((REPO / "record" / "executive" / "context" / "context-pins.json")
                      .read_text(encoding="utf-8"))
pinned_live = None
for name, pin in (pins_doc.get("pins") or {}).items():
    candidate = pathlib.Path(pin.get("live_path", ""))
    if candidate.is_file():
        pinned_live = candidate
        break

if pinned_live is None:
    check("a pinned live file could be located", False,
          "could not resolve a pinned path; the fault could not be injected")
else:
    original = pinned_live.read_bytes()
    try:
        pinned_live.write_bytes(original + b"\n<!-- drift -->\n")
        r = run("check_executive_context.py")
        check(f"DRIFT in a pinned file is refused ({pinned_live.name})", r.returncode != 0,
              f"rc={r.returncode}; a context check that ignores drift gates nothing")
    finally:
        pinned_live.write_bytes(original)
    r = run("check_executive_context.py")
    check("...and the tree is clean again after restoring", r.returncode == 0)

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
