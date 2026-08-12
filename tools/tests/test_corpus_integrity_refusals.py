#!/usr/bin/env python3
"""Negative controls for the two tools that guard the corpus's central claim.

    python3 tools/tests/test_corpus_integrity_refusals.py

`build_manifest.py` anchors every raw artifact, and `validate_provenance.py` checks the
structured ones. Both are run by `rebuild.py`, which is `land.py`'s first gate — so a landing's
green depends on them — and until now **neither had a case it must fail**. They were two of the
eight tools that `control_coverage.py` scores NONE *and* that a gate actually runs, which is what
made them the highest-leverage entries in that list of thirty-five rather than the loudest.

EVERY CASE HERE ASSERTS AT THE EFFECT BOUNDARY. Not "it printed REFUSED" — that is the assertion
that let D-62 corrupt the spend ledger 87 times while passing. The claim is that the tool refused
AND that the image is byte-identical afterwards, over the whole namespace including `.git`, with
no connection attempted and no external command launched. `effect_boundary.refuses` does the
watching; these cases only have to be honest about what they doctor.

WHY A COPY. `build_manifest.py --add` WRITES the manifest. A fixture that ran it against the live
checkout would rewrite the repository's trust anchor to prove that it refuses to — which is
precisely the shape of the failure that produced D-62, and of the older one where a test deleted
189 published pages and then asserted that pruning is safe.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from effect_boundary import refuses                                       # noqa: E402

PASSED = FAILED = 0

MANIFEST = "corpus/MANIFEST.sha256"
ANCHORED = "corpus/raw/activation-01/activation-01-claude-samples.json"


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


def case(label: str, argv: tuple[str, ...], setup, *, says: str, exit_code: int = 1) -> None:
    verdict = refuses(argv=argv, case=label, setup=setup, expect_exit=exit_code,
                      expected_effects={}, timeout=240)
    check(f"{label} — refuses, and changes NOTHING anywhere",
          verdict["problems"] == [], str(verdict["problems"]))
    check(f"    ...and says why: {says!r}",
          any(says in line for line in verdict["output"].splitlines()),
          verdict["output"].strip()[-200:])


print("\nbuild_manifest.py — the raw corpus is append-only, and it must prove it refuses")


def modified_artifact(image: Path) -> None:
    """One byte appended to material that is ALREADY ANCHORED. The invariant this repository
    states first: raw material is never edited after commit."""
    path = image / ANCHORED
    path.write_bytes(path.read_bytes() + b"\n")


case("an already-anchored raw artifact was modified",
     ("python3", "tools/build_manifest.py", "corpus/raw", "--add"),
     modified_artifact,
     says="existing artifact(s) changed or absent")


def rewritten_manifest(image: Path) -> None:
    """Re-anchor an existing entry to a different hash — a rewritten history, not an append."""
    path = image / MANIFEST
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() and not line.startswith("#"):
            lines[index] = "0" * 64 + line[64:]
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


case("the manifest's own history was rewritten",
     ("python3", "tools/build_manifest.py", "corpus/raw", "--add"),
     rewritten_manifest,
     says="not an append-only extension of the one committed at HEAD")


def deleted_artifact(image: Path) -> None:
    (image / ANCHORED).unlink()


case("an anchored raw artifact is missing",
     ("python3", "tools/build_manifest.py", "corpus/raw", "--add"),
     deleted_artifact,
     says="changed or absent")


print("\nvalidate_provenance.py — an unreadable artifact is a failure, not a traceback")


def nothing(image: Path) -> None:
    return None


#  It used to raise out of main() on a target it could not read: only the PARSE failure was
#  caught, so `--help` produced a stack trace. A crash and a refusal look different to an
#  operator and only one of them is the control working.
case("a target that cannot be read",
     ("python3", "tools/validate_provenance.py", "no-such-file.json"),
     nothing, says="[UNREADABLE]")


def broken_json(image: Path) -> None:
    (image / "corpus" / "artifacts" / "deficiency-register.json").write_text(
        "{ this is not json", encoding="utf-8")


case("an artifact that does not parse",
     ("python3", "tools/validate_provenance.py", "corpus/artifacts"),
     broken_json, says="[PARSE]")


def wrong_source_hash(image: Path) -> None:
    """The check that matters most: the artifact claims to be derived from a source whose hash
    it records. Change the recorded hash and the derivation claim is unsupported."""
    import json as _json
    path = image / "corpus" / "artifacts" / "deficiency-register.json"
    doc = _json.loads(path.read_text(encoding="utf-8"))
    doc["source"]["sha256"] = "0" * 64
    path.write_text(_json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


case("an artifact whose recorded source hash is wrong",
     ("python3", "tools/validate_provenance.py", "corpus/artifacts"),
     wrong_source_hash, says="FAILED")


print("\nthe positive controls, without which every case above is meaningless")

verdict = refuses(argv=("python3", "tools/validate_provenance.py", "corpus/artifacts"),
                  case="an untouched corpus", setup=nothing, expect_exit=0,
                  expected_effects={}, timeout=240)
check("an untouched corpus PASSES validation", verdict["exit"] == 0,
      verdict["output"].strip()[-200:])
check("...and validation changes nothing either",
      not [p for p in verdict["problems"] if "UNDECLARED" in p or "outside" in p],
      str(verdict["problems"]))

verdict = refuses(argv=("python3", "tools/build_manifest.py", "corpus/raw", "--verify"),
                  case="an untouched manifest", setup=nothing, expect_exit=0,
                  expected_effects={}, timeout=240)
check("an untouched manifest verifies", verdict["exit"] == 0,
      verdict["output"].strip()[-200:])

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
