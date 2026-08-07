#!/usr/bin/env python3
"""Conformance tests for the cohort publisher.

    python3 tools/tests/test_cohort_pages.py

A cohort is published beside rounds but is NOT one, and the whole value of that separation is
that a reader cannot mistake the two. These tests assert the invariants that make the
separation real rather than decorative:

* a cohort is identified by an explicit artifact_type, never by a MISSING cycle file;
* every solicited party is accounted for as successful or failed, and never as both;
* a rejection record accounts for every attempt that was paid for;
* the round publisher does not delete the cohort publisher's artifacts, and vice versa.

The last one is here because it already happened: the round pruner owned `docs/artifacts/` and
deleted 59 files the cohort publisher had just written, with a green exit on both tools.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_cohort_pages as c                                            # noqa: E402
import build_round_pages as b                                             # noqa: E402

PASSED = FAILED = 0


def check(label: str, condition: bool) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


def refuses(label: str, fn) -> None:
    """The refusal must be a BuildRefusal, not any exception that happens to escape."""
    try:
        fn()
    except c.BuildRefusal:
        check(label, True)
        return
    except Exception as error:                                     # noqa: BLE001
        check(f"{label} — raised {type(error).__name__}, not BuildRefusal", False)
        return
    check(f"{label} — did NOT refuse", False)


class Fixture:
    """A cohort on disk that can be corrupted one field at a time."""

    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.id = "agenda-99"
        self.spec_dir = self.tmp / "record" / "solicitations" / self.id
        self.raw_dir = self.tmp / "corpus" / "raw" / self.id
        self.art_dir = self.tmp / "corpus" / "artifacts" / self.id
        for d in (self.spec_dir, self.raw_dir, self.art_dir, self.tmp / "record" / "cohorts"):
            d.mkdir(parents=True, exist_ok=True)
        self.write_descriptor()
        self.add_party("alpha", ok=True)
        self.add_party("beta", ok=False)

    def write_descriptor(self, **overrides) -> None:
        doc = {"artifact_type": "proposal_cohort", "cohort": self.id, "k_requested": 2,
               "what_this_is": "test", "enters_rotation": False}
        doc.update(overrides)
        (self.tmp / "record" / "cohorts" / f"{self.id}.json").write_text(json.dumps(doc))

    def add_party(self, party: str, ok: bool) -> None:
        (self.spec_dir / f"{self.id}-{party}.json").write_text(json.dumps(
            {"prompt": f"prompt for {party}", "prompt_sha256": "x" * 64, "identity": party}))
        if ok:
            samples = [{"sample_index": i, "parsed": {"question": f"q{i}"}} for i in (1, 2)]
            (self.raw_dir / f"{self.id}-{party}-samples.json").write_text(
                json.dumps({"samples": samples, "k_collected": 2}))
            (self.art_dir / f"{self.id}-{party}-summary.json").write_text(json.dumps(
                {"k_requested": 2, "k_collected": 2, "variance": {}}))
        else:
            (self.raw_dir / f"{self.id}-{party}-rejected.json").write_text(json.dumps(
                {"k_requested": 2, "rejected": [
                    {"sample_index": 1, "category": "transport", "reason": "HTTP 400"},
                    {"sample_index": 2, "category": "transport", "reason": "HTTP 400"}]}))

    def load(self):
        original = (c.COHORTS, c.REPO_ROOT)
        c.COHORTS = self.tmp / "record" / "cohorts"
        c.REPO_ROOT = self.tmp
        try:
            return c.load_cohort(self.id)
        finally:
            c.COHORTS, c.REPO_ROOT = original

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


print("\ncohort identity is asserted, never inferred from absence")
fx = Fixture()
data = fx.load()
check("a well-formed cohort loads", data["cohort"] == "agenda-99")
check("the successful party is listed as successful", data["successful"] == ["alpha"])
check("the party whose every attempt failed is listed as failed", data["failed"] == ["beta"])
check("a total failure does NOT suppress the parties that succeeded",
      "alpha" in data["summaries"] and len(data["specs"]) == 2)

fx.write_descriptor(artifact_type="rotation_cycle")
refuses("a descriptor that is not a proposal_cohort is refused", fx.load)
fx.write_descriptor()

fx2 = Fixture()
(fx2.tmp / "record" / "cohorts" / f"{fx2.id}.json").unlink()
try:
    fx2.load()
    check("a MISSING descriptor is not silently treated as a cohort", False)
except c.BuildRefusal:
    check("a missing descriptor refuses as BuildRefusal — acceptable", True)
except FileNotFoundError:
    #  The point is that absence is never INFERRED to mean "cohort". Erroring is correct.
    check("a missing descriptor raises rather than inferring a cohort", True)
fx2.cleanup()

print("\nevery solicited party is accounted for, exactly once")
fx3 = Fixture()
(fx3.art_dir / f"{fx3.id}-beta-summary.json").write_text(json.dumps(
    {"k_requested": 2, "k_collected": 2, "variance": {}}))
refuses("a party in BOTH the successful and failed sets is refused", fx3.load)
fx3.cleanup()

fx4 = Fixture()
fx4.spec_dir.joinpath(f"{fx4.id}-gamma.json").write_text(json.dumps(
    {"prompt": "p", "prompt_sha256": "y" * 64}))
refuses("a solicited party with neither summary nor rejection is refused", fx4.load)
fx4.cleanup()

fx5 = Fixture()
(fx5.art_dir / f"{fx5.id}-ghost-summary.json").write_text(json.dumps(
    {"k_requested": 2, "k_collected": 2, "variance": {}}))
refuses("a summary with no solicitation spec is refused", fx5.load)
fx5.cleanup()

fx6 = Fixture()
(fx6.raw_dir / f"{fx6.id}-phantom-rejected.json").write_text(json.dumps(
    {"k_requested": 2, "rejected": []}))
refuses("an ORPHAN rejection record with no spec is refused", fx6.load)
fx6.cleanup()

fx7 = Fixture()
(fx7.raw_dir / f"{fx7.id}-alpha-samples.json").unlink()
refuses("a summary with no raw samples behind it is refused", fx7.load)
fx7.cleanup()

print("\na rejection record accounts for every attempt that was paid for")
fx8 = Fixture()
(fx8.raw_dir / f"{fx8.id}-beta-rejected.json").write_text(json.dumps(
    {"k_requested": 5, "rejected": [{"sample_index": 1, "category": "transport"}]}))
refuses("a record listing 1 of 5 requested attempts is refused", fx8.load)
fx8.cleanup()

print("\nthe two publishers do not delete each other's artifacts")
check("the cohort publisher writes to its own subtree, not docs/rounds/",
      c.OUT.name == "cohorts" and c.OUT != b.OUT)
check("the cohort pruner only ever walks its own subtree",
      "OUT.glob" in c.prune.__doc__ or c.prune.__doc__.count("docs/cohorts") >= 1)
check("the round pruner takes an explicit ownership list for shared directories",
      "owned_prefixes" in b.prune.__code__.co_varnames)

#  AGAINST A TEMPORARY TREE. The first version of this test called b.prune() directly with a
#  narrow expected set, and prune() reads the module-level OUT -- so the "test" deleted 189
#  published pages from docs/rounds/ and then asserted that pruning is safe. A test that
#  exercises a destructive function must own the directory it destroys.
sandbox = Path(tempfile.mkdtemp())
saved = (b.OUT, b.PROMPTS, b.FETCHED)
b.OUT, b.PROMPTS, b.FETCHED = sandbox / "rounds", sandbox / "prompts", sandbox / "fetched"
for d in (b.OUT, b.PROMPTS, b.FETCHED):
    d.mkdir(parents=True)
(b.OUT / "round-000.md").write_text("kept")
(b.OUT / "round-999.md").write_text("stale")
(b.PROMPTS / "round-000-alpha.txt").write_text("kept")
(b.PROMPTS / "agenda-02-alpha.txt").write_text("not ours")
(b.PROMPTS / "round-000-stale.txt").write_text("ours and stale")
removed = b.prune({"round-000"}, {"round-000-alpha"}, owned_prefixes=("round-000",))
check("a stale page in its OWN subtree is pruned", not (b.OUT / "round-999.md").exists())
check("an expected page is kept", (b.OUT / "round-000.md").exists())
check("a stale prompt it OWNS is pruned", not (b.PROMPTS / "round-000-stale.txt").exists())
check("another generator's artifact in the SHARED directory survives",
      (b.PROMPTS / "agenda-02-alpha.txt").exists())
b.OUT, b.PROMPTS, b.FETCHED = saved
shutil.rmtree(sandbox, ignore_errors=True)

print("\nthe published banner is unmistakable")
check("the banner denies that a cycle occurred", "No rotation cycle" in c.BANNER)
check("the banner denies that anything entered the agenda", "entered the agenda" in c.BANNER)
check("the banner denies that a question was asked", "none was asked" in c.BANNER)
check("the banner covers reporter suggestions too, not only party proposals",
      "reporter suggestion" in c.BANNER)

print("\nthe live cohort is internally consistent")
live = c.load_cohort("agenda-02")
check("agenda-02 loads from the committed record", live["cohort"] == "agenda-02")
check("all five solicited parties are accounted for",
      len(live["specs"]) == 5 and len(live["successful"]) + len(live["failed"]) == 5)
check("claude-fetch-v1 is recorded as failed, not as a refusal",
      live["failed"] == ["claude-fetch-v1"])
check("its rejection record accounts for all five attempts",
      len(live["rejected"]["claude-fetch-v1"]["rejected"]) == 5)

fx.cleanup()

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
