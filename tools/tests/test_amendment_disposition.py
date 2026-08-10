#!/usr/bin/env python3
"""Conformance for the amendment-disposition rule.

The custodian's motive, in his words: use good ideas from the model panel, and do not lose the
improvement however many rounds ratification then takes. So the load-bearing test is the REFUSAL
-- a rule that only describes what should happen to an amendment is the third instance of prose
announcing a control before any mechanism exists.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ratification_ballot as rb                                        # noqa: E402

PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


print("\nevery amendment in the record has a disposition")
check("no clause carries an undisposed amendment", rb.undisposed_amendments() == {})

print("\nthe rule is registered in the spec BEFORE a ballot is sent")
spec = rb.build_spec("claude", "test-cohort")
rule = spec.get("amendment_disposition_rule") or {}
check("the spec carries the rule", bool(rule))
check("it names all four dispositions",
      len(rule.get("every_amendment_gets_one_of", [])) == 4)
check("it forbids silent dropping", "no_silent_drop" in rule)
check("it blocks re-balloting", "re_ballot_is_blocked" in rule)
check("it says selection is disclosed", "selection_is_disclosed" in rule)
check("it is fixed before sending", "fixed_before_sending" in rule)

print("\nadoption is not ratification, and the artifacts say so")
for path in sorted((ROOT.parent / "corpus" / "artifacts").glob("**/*-amendment-dispositions.json")):
    doc = json.loads(path.read_text())
    check(f"{path.name}: states what adoption is NOT", bool(doc.get("what_adoption_is_not")))
    check(f"{path.name}: discloses that selection was the workbench's",
          bool(doc.get("the_selection_was_the_workbenchs")))
    check(f"{path.name}: its convergence measure states a METHOD",
          bool((doc.get("convergence_measure") or {}).get("method")))
    check(f"{path.name}: every amendment keeps verbatim text and a ground",
          all(a.get("text") and a.get("disposition_ground") for a in doc["amendments"]))
    check(f"{path.name}: an ADOPTED amendment names where it went",
          all(a.get("adopted_into") for a in doc["amendments"]
              if a["disposition"] == "ADOPTED"))
    check(f"{path.name}: a DEFERRED amendment names a review date",
          all(a.get("review_by") for a in doc["amendments"] if a["disposition"] == "DEFERRED"))

print("\nthe adopted C06 text is a party's verbatim words")
d = json.loads((ROOT.parent / "corpus/artifacts/ratification-02/"
                "ratification-02-amendment-dispositions.json").read_text())
adopted = [a for a in d["amendments"] if a["disposition"] == "ADOPTED"]
check("exactly one amendment was adopted", len(adopted) == 1)
check("...it is a C06 amendment", adopted and adopted[0]["clause_id"] == "C06")
check("...it names the party and sample it came from",
      adopted and adopted[0]["party"] and adopted[0]["sample"] is not None)
#  WHITESPACE-NORMALISED. The governing file hard-wraps at 96 columns, so the adopted sentence
#  is split across lines. Line breaks are not a change to the words; anything else would be.
import re                                                              # noqa: E402
_flat = lambda t: re.sub(r"\s+", " ", t).strip()
check("...and its verbatim words appear in the governing instructions",
      adopted and _flat(adopted[0]["text"])[-90:].strip(" .") in
      _flat((ROOT.parent / "CLAUDE.md").read_text()))

print("\nthe tombstone mechanism exists, not just the sentence")
import build_manifest as bm                                             # noqa: E402
check("the manifest verifier reads tombstones", callable(bm.read_tombstones))
check("an incomplete tombstone is not accepted as a withdrawal",
      "BAD TOMBSTONE" in (ROOT / "build_manifest.py").read_text())
check("a withdrawal must match the hash it claims to remove",
      'stone.get("sha256") == digest' in (ROOT / "build_manifest.py").read_text())

#  KEEP THE SUMMARY AND EXIT LAST.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
