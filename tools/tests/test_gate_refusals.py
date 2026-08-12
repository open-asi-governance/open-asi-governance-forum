#!/usr/bin/env python3
"""Control 2 for three gates whose silent failure would corrupt the record.

`tools/control_coverage.py` reported 44% of tools with an assurance signal had a case they must
fail. These three were taken first, on leverage rather than alphabetical order:

* **`check_prompt.py`** — the D-31 denylist of phrasings this project was CAUGHT USING in prompts
  that went to live parties. It matters because of D-36, which is a different rule: a prompt
  cannot be repaired after it is sent. This gate is the only moment at which the defect is still
  fixable, and a denylist that admits everything is the worst possible version of it.
* **`check_register.py`** — R9 binds each register entry's metadata to a hash of the prose it
  describes, so editing an entry fails the build until a human re-reads and re-stamps. Its own
  comment says **"R9 IS THE POINT"**: metadata quietly describing text it no longer matches is
  how a register starts lying slowly. Nothing had ever observed it fail.
* **`build_register_view.py`** — it publishes the deficiency counts a reader sees. It has already
  produced one false zero, printing "0 of N classifications reviewed" from a missing key, which
  is the C53 defect in the position where it reaches the public.

EVERY ARM IS PAIRED. A guard that refuses everything is broken rather than strict, and only the
baseline distinguishes them. Every fault is injected into a COPY in a temp directory, with the
module's own path constants repointed — nothing here can damage the real register, which is
append-only and would be the worst possible thing for a test to touch.

EXACT ASSERTIONS, not merely non-zero. `test_gate_negative_controls.py` learned this the
expensive way on 2026-08-12: it asserted `!= 0` for a drift arm, and once the tool gained a
third exit state an "unavailable" result would have satisfied it. Where these tools have one
failure mode the arm asserts the RULE NAMED in the output, so a refusal for an unrelated reason
does not count as the refusal under test.

NINE INJECTED FAULTS ACROSS THREE GATES, and rather more assertions than that — several arms
inspect the same injected run. An earlier version of this line called the assertions "arms",
which inflates the apparent number of distinct faults; the number that matters is how many
distinct conditions were actually produced.

WHAT THIS DOES NOT ESTABLISH. That these gates are demanding, that their rules are the right
rules, or that they would catch a defect nobody thought to inject. Control 2 raises the floor
from "never observed to fail" to "observed to fail at least once", and this is that floor.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess as sp
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
#  What this suite drives to a REFUSAL, read by tools/control_coverage.py. A tool
#  named here must exist and this file must assert a refusal, or the scan fails —
#  a declaration is a claim, not a substitute for the case.
COVERS = ("check_prompt.py",
          "check_register.py",
          "build_register_view.py",
          "control_coverage.py")

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


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(tool: str, *args: str) -> sp.CompletedProcess:
    return sp.run([sys.executable, str(ROOT / tool), *args],
                  cwd=REPO, capture_output=True, text=True)


print("\ncheck_prompt.py — the D-31 denylist, checked BEFORE a prompt is sent")

with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)

    #  BASELINE. An ordinary neutral prompt must pass, or the denylist is refusing on something
    #  other than the phrasings it names.
    clean = tmp / "clean-prompt.md"
    clean.write_text(
        "# A question for the parties\n\n"
        "Consider whether an assurance check that has never been observed to fail constitutes "
        "evidence that the system it monitors is working. Answer in your own terms.\n",
        encoding="utf-8")
    r = run("check_prompt.py", str(clean))
    check("BASELINE: a neutral prompt passes", r.returncode == 0,
          (r.stdout + r.stderr)[-200:])

    #  FAULT. Each of these is a phrasing this project was CAUGHT USING in a prompt that went to
    #  a live party. They are in the denylist because they happened, not because they might.
    for phrase, why in (
            ("Please do not soften your criticism.", "prescribes posture"),
            ("Where did the revision over-correct?", "names the direction of the expected error"),
            ("Remember that disagreement is more useful to us than agreement.",
             "tells a party dissent is valued, which shapes the answer")):
        planted = tmp / "planted-prompt.md"
        planted.write_text(f"# A question for the parties\n\n{phrase}\n", encoding="utf-8")
        r = run("check_prompt.py", str(planted))
        output = r.stdout + r.stderr
        check(f"a prompt containing a denylisted phrasing is REFUSED ({why})",
              r.returncode != 0,
              f"rc={r.returncode}; a denylist that admits its own recorded defects gates nothing")
        #  THE DIAGNOSTIC, not merely the exit code. The module claims exact assertions and these
        #  arms did not make one — a refusal for an unrelated reason would have satisfied them.
        check(f"...and the refusal cites the deficiency the rule came from ({why})",
              "D-31" in output, f"output named no rule:\n{output[-200:]}")

    #  And the clean one still passes afterwards, so the refusal was about the phrasing.
    r = run("check_prompt.py", str(clean))
    check("...and the neutral prompt still passes, so the refusal was about the wording",
          r.returncode == 0)

print("\ncheck_register.py — R9 binds metadata to the prose it describes")

register = load("check_register")
REAL_REGISTER, REAL_ARTIFACT = register.REGISTER, register.ARTIFACT
BEFORE = (hashlib.sha256(REAL_REGISTER.read_bytes()).hexdigest(),
          hashlib.sha256(REAL_ARTIFACT.read_bytes()).hexdigest())

with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)

    def sandbox() -> tuple[pathlib.Path, pathlib.Path]:
        """A private copy of the register and its artifact. The real ones are APPEND-ONLY."""
        md = tmp / "deficiencies.md"
        js = tmp / "deficiency-register.json"
        shutil.copy(REAL_REGISTER, md)
        shutil.copy(REAL_ARTIFACT, js)
        register.REGISTER, register.ARTIFACT = md, js
        return md, js

    def verdict() -> tuple[int, str]:
        import io
        import contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = register.main([])
        return code, out.getvalue()

    try:
        md, js = sandbox()
        code, out = verdict()
        check("BASELINE: the register and its artifact agree", code == 0, out[-300:])

        #  R9 — THE LOAD-BEARING ONE. Edit an entry's prose without re-stamping. The metadata now
        #  describes text that is not there, which is the failure the rule exists for and which
        #  nothing had ever watched it catch.
        md, js = sandbox()
        text = md.read_text(encoding="utf-8")
        first = text.index("\n", text.index("### D-01"))
        md.write_text(text[:first] + "\n\nAn edit nobody re-stamped." + text[first:],
                      encoding="utf-8")
        code, out = verdict()
        check("EDITING AN ENTRY'S PROSE fails until it is re-stamped", code != 0, out[-200:])
        check("...and the failure names R9, not some other rule",
              "R9" in out, f"a refusal for another reason is not this refusal:\n{out[-300:]}")

        #  R7 — a heading with no entry. The published view would silently omit it.
        md, js = sandbox()
        md.write_text(md.read_text(encoding="utf-8")
                      + "\n\n### D-99 — an entry nobody classified\n\nBody.\n", encoding="utf-8")
        code, out = verdict()
        check("a HEADING WITH NO ENTRY is refused", code != 0, out[-200:])
        check("...and the failure names R7", "R7" in out, out[-300:])

        #  R3 — a duplicate id. This is D-32: two sessions each read the register, saw the same
        #  highest id, incremented, and filed different defects under one number.
        md, js = sandbox()
        text = md.read_text(encoding="utf-8")
        md.write_text(text + "\n\n### D-01 — a second entry claiming the same id\n\nBody.\n",
                      encoding="utf-8")
        code, out = verdict()
        check("a DUPLICATE entry id is refused — the defect D-32 records", code != 0)
        check("...and the failure names R3", "R3" in out, out[-300:])

        #  R10 — the artifact's recorded source hash no longer matches the register.
        md, js = sandbox()
        doc = json.loads(js.read_text(encoding="utf-8"))
        doc["source"]["sha256"] = "0" * 64
        js.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        code, out = verdict()
        check("an artifact whose recorded SOURCE HASH is wrong is refused", code != 0)
        check("...and the failure names R10", "R10" in out, out[-300:])

        #  And clean again, so every refusal above was caused by its own fault.
        md, js = sandbox()
        code, out = verdict()
        check("...and an untouched copy passes again", code == 0, out[-200:])
    finally:
        register.REGISTER, register.ARTIFACT = REAL_REGISTER, REAL_ARTIFACT

#  The real files must be untouched. A test that damaged the append-only register would be worse
#  than the defect it was written to prevent, so this is asserted BY HASH rather than assumed.
#  An earlier version ran check_register.py and took its pass as proof — which establishes that
#  the register is internally CONSISTENT, not that it is unchanged. A consistent edit would have
#  satisfied it.
after = (hashlib.sha256(REAL_REGISTER.read_bytes()).hexdigest(),
         hashlib.sha256(REAL_ARTIFACT.read_bytes()).hexdigest())
check("the REAL register and artifact are byte-identical to before these fixtures ran",
      after == BEFORE, "a test that edits the append-only register is worse than the defect "
                       "it was written to prevent")

print("\nbuild_register_view.py — it publishes the numbers a reader sees")

view = load("build_register_view")
REAL_VIEW_ARTIFACT = view.ARTIFACT

with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)
    try:
        #  BASELINE: the real artifact renders.
        doc = view.load()
        check("BASELINE: the register artifact renders to markdown",
              len(view.render_markdown(doc)) > 500)

        #  FAULT: an artifact that is not there. The tool must say so rather than emit an empty
        #  view, which would publish "0 deficiencies" — a false zero on the public page.
        #
        #  CALLED IN-PROCESS, NOT AS A SUBPROCESS. The first version ran the tool through `run()`
        #  after repointing `view.ARTIFACT`, and a subprocess imports the module fresh — so the
        #  fault was never injected and the arm passed with rc=0 while proving nothing. That is
        #  this repository's dominant defect (a green signal not downstream of what it certifies)
        #  committed inside a control-2 test.
        import contextlib
        import io
        view.ARTIFACT = tmp / "not-there.json"
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = view.main()
        #  The label names the tool. control_coverage.py looks for a refusal assertion within
        #  600 characters of a mention of the tool's name, and it could not see these — the only
        #  mention was `load("build_register_view")` at the top of the section. Naming the tool
        #  in the label makes a true relationship VISIBLE; it does not manufacture one, and the
        #  distinction matters because the alternative is writing tests to satisfy a heuristic.
        check("build_register_view.py: a MISSING artifact is refused, not rendered as empty",
              code != 0 and "missing" in out.getvalue().lower(),
              f"rc={code}; {out.getvalue()[:150]}")

        #  FAULT: an entry with no human_review key at all. AGGREGATION MUST RAISE.
        #
        #  My first version of this arm expected '?'. That was wrong, and the tool was right:
        #  control 53's own verifier says "assert aggregation RAISES rather than skipping or
        #  defaulting". A KeyError here is the control being satisfied, and the build fails
        #  closed with nothing published. The '?' repair on line 123 covers a different shape —
        #  a status value absent from the counter — and conflating the two is how a partial
        #  repair gets recorded as a complete one.
        stripped = json.loads(REAL_VIEW_ARTIFACT.read_text(encoding="utf-8"))
        for entry in stripped["entries"]:
            entry.pop("human_review", None)
        broken = tmp / "no-review-key.json"
        broken.write_text(json.dumps(stripped), encoding="utf-8")
        view.ARTIFACT = broken
        raised_key = None
        rendered = None
        try:
            rendered = view.render_markdown(view.load())
        except KeyError as exc:
            raised_key = exc.args[0] if exc.args else None
        check("build_register_view.py: an entry with NO review key makes aggregation RAISE",
              raised_key is not None,
              f"it rendered instead, and the page would carry a count nobody measured: "
              f"{str(rendered)[:120]}")
        #  THE EXACT KEY. Accepting KeyError-or-TypeError would pass on a raise from anywhere in
        #  the renderer, which is a different fault wearing the same exit.
        check("...and it raises on exactly the missing field, not somewhere else",
              raised_key == "human_review", f"raised on {raised_key!r}")
    finally:
        view.ARTIFACT = REAL_VIEW_ARTIFACT

print("\nthe coverage scanner must not count a DISCLAIMER as coverage")

#  THE TRIPWIRE THAT COUNTED ITSELF. This section used to hold a case asserting that
#  arm_acceptance.py still needs a refactor before it can have a negative control — a note, in
#  prose, so the exclusion could not rot. `control_coverage.py` matches a refusal word within 600
#  characters of a tool's name, and the note contained "negative control" and "refactor before it
#  can have one" beside the tool's name. **It reported arm_acceptance as COVERED on the strength
#  of the sentence saying it is not.** Codex found it the same day, and the reported rate was
#  50% when the three real additions give 49%.
#
#  The note now lives only in `control_application.py`'s C2 gap, where it is data rather than
#  scannable prose. What stays here is the regression: a file that merely TALKS about a tool
#  must never satisfy its coverage.
coverage = load("control_coverage")
with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)
    fake_tool = tmp / "zzqx_disclaimed.py"
    fake_tool.write_text("def main():\n    return 0\n", encoding="utf-8")
    fake_tests = tmp / "tests"
    fake_tests.mkdir()
    #  A COMMENT, not a docstring. The scanner already strips module docstrings — that hole was
    #  found and closed on 2026-08-11. This is the same defect one layer over: prose in a comment
    #  beside the tool's name, containing the words the matcher looks for.
    (fake_tests / "test_talks_about_it.py").write_text(
        '"""An unrelated docstring, so the docstring stripper is not what saves this."""\n'
        "#  zzqx_disclaimed.py cannot have a negative control yet — its checks would have to be\n"
        "#  refactored first, and nothing here refuses anything about it.\n"
        "print('nothing asserted')\n", encoding="utf-8")
    real_tools, real_tests = coverage.TOOLS, coverage.TESTS
    try:
        coverage.TOOLS, coverage.TESTS = tmp, fake_tests
        covered, why = coverage.has_negative_control(fake_tool.stem)
        check("a test that only TALKS about a tool does not count as its coverage",
              covered is False,
              f"reported covered because: {why}. A disclaimer that satisfies the metric it "
              f"disclaims is worse than no metric.")

        #  AND A DECLARATION IS NOT ENOUGH EITHER. `COVERS` was added so a suite can name what
        #  it drives, which is stronger than proximity — and it would be trivially gameable if
        #  naming a tool were sufficient. The file must still assert a refusal.
        (fake_tests / "test_declares_only.py").write_text(
            'COVERS = ("zzqx_disclaimed.py",)\n'
            "print('this suite names the tool and requires nothing of it')\n", encoding="utf-8")
        covered, why = coverage.has_negative_control(fake_tool.stem)
        check("a COVERS declaration with no refusal assertion does not count either",
              covered is False, f"reported covered because: {why}")
        check("...and the reason says the declaration was seen and found empty",
              "asserts no refusal" in why, why)

        #  BASELINE: a declaration WITH a refusal does count, or the mechanism refuses everything
        #  and is not a measure.
        (fake_tests / "test_declares_only.py").write_text(
            'COVERS = ("zzqx_disclaimed.py",)\n'
            "rc = 1\n"
            "assert rc != 0, 'the tool must be refused on a bad input'\n", encoding="utf-8")
        covered, why = coverage.has_negative_control(fake_tool.stem)
        check("BASELINE: a declaration WITH a refusal assertion does count", covered is True, why)
    finally:
        coverage.TOOLS, coverage.TESTS = real_tools, real_tests

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
