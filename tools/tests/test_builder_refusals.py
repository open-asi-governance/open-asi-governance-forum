#!/usr/bin/env python3
"""The five remaining gate-run page builders must refuse rather than publish something wrong.

    python3 tools/tests/test_builder_refusals.py

These run inside `rebuild.py`, which is `land.py`'s first gate, so every landing's green depends
on them — and none had a case it must fail. A publisher's failure mode is not a crash; it is
publishing a page that is empty, stale or missing the thing it describes, and then reporting
success. `build_controls_page.py`'s refusal is the one that matters most: it is the gate that
made D-63, where adding a scope requirement silently emptied Part A of the published register.

EVERY CASE ASSERTS AT THE EFFECT BOUNDARY. A builder that refuses AFTER writing half its output
has left the record describing a publication that did not happen — which is D-69, found in
build_viewer.py by exactly this check one commit ago. So `expected_effects={}` here is not
ceremony: it is the assertion that the refusal came before the first byte.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from effect_boundary import refuses                                       # noqa: E402

COVERS = ("build_controls_page.py", "build_local_rounds.py", "build_predictions_view.py",
          "build_capture_ui.py", "build_challenge_page.py")

PASSED = FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


def case(label: str, tool: str, setup, *, says: str, argv_extra: tuple = ()) -> None:
    verdict = refuses(argv=("python3", f"tools/{tool}", *argv_extra), case=label, setup=setup,
                      expect_exit=1, expected_effects={}, timeout=300)
    check(f"{label} — refuses BEFORE writing anything",
          verdict["problems"] == [], str(verdict["problems"]))
    check(f"    ...and says why: {says!r}",
          says in verdict["output"], verdict["output"].strip()[-220:])


print("\nbuild_controls_page.py — the gate that made D-63, now with a case it must fail")


def control_without_a_scope(image: Path) -> None:
    """Remove one control's `applies_when`. The published register would then contain a control
    whose scope is absent, which cannot be distinguished from one that applies universally."""
    path = image / "tools" / "build_controls_page.py"
    text = path.read_text(encoding="utf-8")
    marker = '"applies_when": "any system that produces an assurance signal'
    start = text.index(marker)
    end = text.index('",\n', start) + len('",\n')
    path.write_text(text[:start] + text[end:], encoding="utf-8")


case("a control that states no scope", "build_controls_page.py", control_without_a_scope,
     says="cannot be distinguished from one that applies universally")


print("\nbuild_local_rounds.py — no summaries is not an empty page")


def no_summaries(image: Path) -> None:
    """The summaries live under corpus/artifacts/local-round-*/. The first version of this
    fixture removed record/solicitations/ — a directory the builder never reads — and the tool
    published 38 pages and exited 0 while the case claimed to be testing a refusal. Asserting
    the EXIT CODE caught it; a message-only assertion would have passed on the wrong outcome,
    which is D-66 twice in two days."""
    import shutil
    removed = 0
    for target in sorted(image.glob("corpus/artifacts/local-round-*")):
        shutil.rmtree(target)
        removed += 1
    assert removed, ("the fixture found no local-round artifact directories to remove; if they "
                     "moved, this case would silently become a test of the happy path")


case("there are no solicitation summaries to publish", "build_local_rounds.py", no_summaries,
     says="no solicitation summaries found")


print("\nbuild_predictions_view.py — a missing register is not zero predictions")


def no_prediction_source(image: Path) -> None:
    source = image / "predictions" / "predictions.json"
    assert source.is_file(), ("the fixture assumes predictions/predictions.json exists; if it "
                              "moved, this case would silently test the happy path")
    source.unlink()


case("the prediction register is missing", "build_predictions_view.py", no_prediction_source,
     says="missing")


print("\nbuild_capture_ui.py — a round whose parties have no prompt")


def round_without_a_prompt(image: Path) -> None:
    rounds = sorted((image / "record" / "rounds").glob("*.json"))
    assert rounds, "the fixture assumes at least one round declaration exists"
    doc = json.loads(rounds[0].read_text(encoding="utf-8"))
    doc.pop("common_prompt", None)
    for party in doc.get("parties", []):
        if isinstance(party, dict):
            party.pop("prompt_override", None)
    rounds[0].write_text(json.dumps(doc, indent=2), encoding="utf-8")


case("a round with no common prompt and no override", "build_capture_ui.py",
     round_without_a_prompt, says="REFUSED")


print("\nbuild_challenge_page.py — it had no refusal at all until this commit")


def emptied_challenge(image: Path) -> None:
    (image / "CHALLENGE.md").write_text("# gone\n", encoding="utf-8")


case("the challenge text has been emptied", "build_challenge_page.py", emptied_challenge,
     says="publishing it would replace the live page with a stub")


def absent_challenge(image: Path) -> None:
    (image / "CHALLENGE.md").unlink()


case("the challenge text is absent", "build_challenge_page.py", absent_challenge,
     says="the challenge page would be published empty")


print("\nthe positive controls, without which every case above is meaningless")

for tool in ("build_controls_page.py", "build_local_rounds.py", "build_predictions_view.py",
             "build_challenge_page.py"):
    verdict = refuses(argv=("python3", f"tools/{tool}"), case=f"{tool} on a sound repository",
                      setup=lambda image: None, expect_exit=0, expected_effects={}, timeout=300)
    check(f"POSITIVE CONTROL: {tool} PUBLISHES when nothing is wrong", verdict["exit"] == 0,
          verdict["output"].strip()[-200:])

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
