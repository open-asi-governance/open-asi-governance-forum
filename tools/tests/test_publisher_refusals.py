#!/usr/bin/env python3
"""The publishers must refuse rather than publish, and refusing must change nothing.

    python3 tools/tests/test_publisher_refusals.py

`build_viewer.py` PRUNES `docs/`. It decides what to delete from a receipt written by
`build_controls_page.py`, and a receipt that has drifted from the disk would license deleting a
live page — which is not hypothetical here: a previous test called a pruner directly with a narrow
expected set and **deleted 189 published pages**, then asserted that pruning is safe. The guards
that stop that had no case they must fail until now.

`build_bundle.py` refuses to overwrite an existing bundle, because capture records cite bundles by
hash and regenerating one silently invalidates the citations — the same immutability rule the raw
corpus follows.

EVERY CASE ASSERTS AT THE EFFECT BOUNDARY, in a fresh copy of the repository, so the assertion is
not "it printed REFUSED" but "it refused AND deleted nothing, anywhere". For a tool whose failure
mode is deletion, an assertion over output would be the wrong assertion twice over.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from effect_boundary import refuses                                       # noqa: E402

COVERS = ("build_viewer.py", "build_bundle.py")

PASSED = FAILED = 0
RECEIPT = "docs/artifacts/controls-pages.json"


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


def case(label: str, argv: tuple[str, ...], setup, *, says: str) -> None:
    verdict = refuses(argv=argv, case=label, setup=setup, expect_exit=1,
                      expected_effects={}, timeout=300)
    check(f"{label} — refuses, and DELETES NOTHING",
          verdict["problems"] == [], str(verdict["problems"]))
    check(f"    ...and says why: {says!r}",
          says in verdict["output"], verdict["output"].strip()[-220:])


print("\nbuild_viewer.py prunes docs/. Every refusal here stands between it and a live page.")


def no_receipt(image: Path) -> None:
    (image / RECEIPT).unlink()


case("the controls receipt is missing entirely",
     ("python3", "tools/build_viewer.py"), no_receipt,
     says="it would delete every published controls page")


def empty_pages(image: Path) -> None:
    path = image / RECEIPT
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["pages"] = {}
    path.write_text(json.dumps(doc), encoding="utf-8")


case("the receipt names no pages",
     ("python3", "tools/build_viewer.py"), empty_pages,
     says="names no pages; refusing to prune")


def no_counts(image: Path) -> None:
    path = image / RECEIPT
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc.pop("counts", None)
    path.write_text(json.dumps(doc), encoding="utf-8")


case("the receipt carries no counts, so the landing page would quote a stale number",
     ("python3", "tools/build_viewer.py"), no_counts,
     says="carries no counts")


def receipt_names_a_missing_page(image: Path) -> None:
    path = image / RECEIPT
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["pages"]["controls-zzqx.html"] = "0" * 64
    path.write_text(json.dumps(doc), encoding="utf-8")


case("the receipt names a page that is not on disk",
     ("python3", "tools/build_viewer.py"), receipt_names_a_missing_page,
     says="which is not on disk")


def stale_receipt_hash(image: Path) -> None:
    """THE ONE THAT MATTERS MOST. A receipt whose hashes have drifted from the disk is how a
    live page gets deleted — the tool's own words."""
    path = image / RECEIPT
    doc = json.loads(path.read_text(encoding="utf-8"))
    name = sorted(doc["pages"])[0]
    doc["pages"][name] = "1" * 64
    path.write_text(json.dumps(doc), encoding="utf-8")


case("the receipt's hash has drifted from the published page",
     ("python3", "tools/build_viewer.py"), stale_receipt_hash,
     says="pruning against a stale receipt is how a live page gets deleted")


print("\nbuild_bundle.py — a bundle is frozen once a round has cited it by hash")


#  NO SETUP. `record/review-round-01-bundle.md` is already in the repository, cited by capture
#  records, so the refusal is the tool's ordinary answer for a real name — which is the honest
#  fixture. The first version invented a bundle id and got exit 2 (unknown round) instead of the
#  immutability refusal it claimed to test: a case passing on the WRONG refusal, which is the
#  shape D-66 was filed for. Asserting the exit code rather than only the message caught it.
def bundle_already_landed(image: Path) -> None:
    assert (image / "record" / "review-round-01-bundle.md").is_file(), (
        "the fixture assumes this bundle is committed; if it is not, the case below would "
        "silently become a test of the happy path")


case("a bundle that already exists is not regenerated",
     ("python3", "tools/build_bundle.py", "review-round-01"), bundle_already_landed,
     says="already exists")


def unknown_bundle(image: Path) -> None:
    return None


verdict = refuses(argv=("python3", "tools/build_bundle.py", "no-such-round-zzqx"),
                  case="an unknown bundle name", setup=unknown_bundle, expect_exit=2,
                  expected_effects={}, timeout=300)
check("an unknown bundle name is a DIFFERENT refusal, with its own exit code",
      verdict["problems"] == [], str(verdict["problems"]))
check("...so the immutability case above cannot pass on this one instead",
      "known bundles:" in verdict["output"])


print("\nthe positive control, without which every case above is meaningless")


def untouched(image: Path) -> None:
    return None


#  build_viewer WRITES on the happy path, so this one cannot assert an empty effect set — it
#  asserts the opposite: that on a sound receipt the tool proceeds instead of refusing.
verdict = refuses(argv=("python3", "tools/build_viewer.py"), case="a sound receipt",
                  setup=untouched, expect_exit=0, expected_effects={}, timeout=300,
                  allow_network=True)
check("POSITIVE CONTROL: on a sound receipt the viewer RUNS rather than refusing",
      verdict["exit"] == 0, verdict["output"].strip()[-220:])
check("...so the five refusals above are not a tool that refuses everything",
      not any("did not refuse" in p for p in verdict["problems"]))

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
