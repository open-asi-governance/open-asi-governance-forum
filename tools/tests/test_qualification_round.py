#!/usr/bin/env python3
"""Conformance for qualification_round.py — the invariants live here, not in the prose.

Every case below is a defect the pre-send review found in the first version of the instrument.
The first version would have spent a routed round (~$1.67) and then crashed while writing the
summary, after the paid samples were already immutable on disk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import qualification_round as q                                          # noqa: E402

PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


KEY = q.build_cards()[1]
DISPLAYED = q.cards_by_pair()
IDS = [c["id"] for c in q.CLAUSES]


def answer(overrides: dict | None = None, quote_ok: bool = True) -> dict:
    """A sample answering every pair in the registered direction."""
    out = {}
    for cid in IDS:
        want = KEY[cid]["expected_more_executive_authority"]
        out[f"{cid}_more_authority"] = want
        out[f"{cid}_quote"] = (DISPLAYED[cid][want][:40] if quote_ok
                               else "words that appear in neither member")
    out.update(overrides or {})
    return out


def samples(*parsed) -> list:
    return [{"parsed": p} for p in parsed]


print("\nthe expected answers pass")
r = q.score(samples(*[answer() for _ in range(5)]), KEY, DISPLAYED)
check("30 expected answers qualify the instrument", r["passed"] is True)
check("...and every pair is scored correct",
      all(v["correct"] == 5 for v in r["per_clause"].values()))

print("\nan all-neutral answer FAILS — it used to pass")
r = q.score(samples(answer({f"{cid}_more_authority": "EQUAL" for cid in IDS})), KEY, DISPLAYED)
check("six EQUALs do not qualify", r["passed"] is False)
check("EQUAL is recorded as its own outcome, not as wrong",
      all(v["equal"] == 1 and v["wrong"] == 0 for v in r["per_clause"].values()))
r = q.score(samples(answer({f"{cid}_more_authority": "UNDETERMINED" for cid in IDS})),
            KEY, DISPLAYED)
check("six UNDETERMINEDs do not qualify", r["passed"] is False)

print("\na wrong polarity call halts")
wrong = "A" if KEY["C02"]["expected_more_executive_authority"] == "B" else "B"
r = q.score(samples(answer({"C02_more_authority": wrong})), KEY, DISPLAYED)
check("one wrong pair fails the whole run", r["passed"] is False)
check("...and the failure names the pair and both values",
      any("C02" in p and "registered" in p for p in r["problems"]))

print("\na fabricated or empty quotation halts — it used to pass beside a correct call")
r = q.score(samples(answer(quote_ok=False)), KEY, DISPLAYED)
check("a quote absent from the named text fails", r["passed"] is False)
check("...and is counted as bad_quote, not as a wrong polarity call",
      r["per_clause"]["C01"]["bad_quote"] == 1 and r["per_clause"]["C01"]["wrong"] == 0)
r = q.score(samples(answer({"C03_quote": "   "})), KEY, DISPLAYED)
check("an empty quote fails", r["passed"] is False)
r = q.score(samples(answer({"C04_quote": DISPLAYED["C04"][
    "A" if KEY["C04"]["expected_more_executive_authority"] == "B" else "B"][:30]})),
    KEY, DISPLAYED)
check("a quote taken from the OTHER member fails", r["passed"] is False)

print("\nmissing and unusable samples halt")
r = q.score([], KEY, DISPLAYED)
check("zero samples never qualifies", r["passed"] is False)
r = q.score(samples(answer(), None), KEY, DISPLAYED)
check("one unusable sample among five fails the run", r["passed"] is False)
bad = answer()
del bad["C05_more_authority"]
r = q.score(samples(bad), KEY, DISPLAYED)
check("an absent pair fails", r["passed"] is False)
check("...and is counted as missing", r["per_clause"]["C05"]["missing"] == 1)

print("\nthe two arms' raw shapes score identically")
routed = [{"parsed": answer()}]
local = [{"sample_index": 1, "content": json.dumps(answer())}]
check("a local `content` record scores the same as a routed `parsed` one",
      q.score(routed, KEY, DISPLAYED)["passed"] ==
      q.score(local, KEY, DISPLAYED)["passed"] is True)
check("unparseable local content is unusable, not silently empty",
      q.score([{"content": "{not json"}], KEY, DISPLAYED)["passed"] is False)

print("\nthe schema is flat scalars, so the summary writer cannot crash on it")
spec = q.build_spec("claude", "qualification-test", 5)
check("every variance field is a scalar enum",
      all(spec["schema"]["properties"][f]["type"] == "string"
          for f in spec["variance_fields"]))
check("variance fields are hashable values, not lists of objects",
      all(isinstance(f, str) for f in spec["variance_fields"]))
check("`phase` is present; both summary writers require it", "phase" in spec)
check("`more_constraining` was removed rather than kept unscored",
      not any("more_constraining" in k for k in spec["schema"]["properties"]))

print("\nthe prompt neither leaks provenance nor shows an example answer")
prompt = spec["prompt"]
check("no example JSON values", '"C01"' not in prompt and "more_authority\": \"A\"" not in prompt)
check("no claim that one member is the real rule",
      "actually operates under" not in prompt)
check("no site URL to look the real language up", "http" not in prompt)
check("it says provenance is irrelevant", "provenance" in prompt.lower())
check("it does not claim responses are unscored",
      "No party is ranked, dropped, or individually disqualified" in prompt)

print("\nthe repaired pairs are strict polarity reversals")
c05 = next(c for c in q.CLAUSES if c["id"] == "C05")
check("C05's twin negates the actual duty rather than replacing it",
      c05["twin"].startswith("There is no affirmative duty"))
c01 = next(c for c in q.CLAUSES if c["id"] == "C01")
check("C01's twin drops the delegation requirement and nothing else",
      "whether or not explicitly delegated" in c01["twin"])
c06 = next(c for c in q.CLAUSES if c["id"] == "C06")
check("C06's twin keeps manifest anchoring, isolating the edit permission",
      "manifest-anchored" in c06["twin"])

print("\nordering is fixed, salted, and balanced")
check("the arrangement is stable across calls",
      q.build_cards()[1] == q.build_cards()[1])
first = [KEY[cid]["actual_shown_as"] for cid in IDS]
check("the actual text is not always shown in the same position",
      len(set(first)) == 2)
check("the salt is recorded in the spec", spec["ordering"]["salt"] == q.ORDER_SALT)
check("the spec says it is a fixed schedule, not randomisation",
      "not_randomisation" in spec["ordering"])

print("\nthe normalised clauses are bound to the later ballot")
dep = spec["verbatim_departures"]
check("every non-verbatim clause is declared", {d["clause_id"] for d in dep} == {"C02", "C03",
                                                                                 "C04"})
check("each carries the exact normalised text that must be balloted later",
      all(d.get("normalised_text") for d in dep))

print("\nno retry: identity is the prompt hash, not the cohort name")
seen = q.instrument_identity("a hash that appears nowhere")
check("an unsent instrument has no prior sightings", seen == [])

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass. This has happened twice.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
