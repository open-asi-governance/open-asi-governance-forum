#!/usr/bin/env python3
"""Derive counts from corpus/raw MECHANICALLY, and refuse when it cannot see a file.

    python3 tools/derive_counts.py --tool search          # search_web receipts, with denominators
    python3 tools/derive_counts.py --tool fetch
    python3 tools/derive_counts.py --coverage             # just the denominators

**DETERMINISTIC.** No LLM, no network.

Why this exists
---------------
On 2026-08-10 this layer published "0 `search_web` invocations across all 20 rounds" and
recommended deleting its own tool on the strength of it. The corpus holds **9**. The count came
from a scan that iterated each file's `samples` array; **69 raw files have no `samples` key** —
they use `responses` and `failures` — so the scan returned zero for their entire contents and the
output looked exactly like a true zero.

That is the failure this module exists to make impossible: **an unrecognised schema must not
report absence.** If a file's disposition containers are not recognised, this refuses, prints the
files, and emits no number at all. A number that is missing is loud; a number that is wrong is
silent, and this project has now shipped two of the latter in one day.

What counts as a disposition
-----------------------------
All of them. `samples`, `responses`, `failures`, `rejected` — because the record's own invariant
is that nothing solicited is discarded, and a count that reaches zero only by excluding a failed
sample is not stricter, it is wrong. The single numbered-round search in the corpus is inside a
`failures` entry whose sample died on HTTP 400 *after* the search returned OK.

What it cannot establish
-------------------------
* **That a receipt means the party wanted the tool.** A receipt records an invocation, not a
  motive, and instructed probes are in here beside voluntary rounds — so `--tool` reports the
  split rather than one total.
* **That the corpus is complete.** It counts what was committed.
* **That the count answers the question someone will ask of it.** Denominators are printed for
  exactly this reason: a number without its denominator is the thing that went wrong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "corpus" / "raw"

#  Every container in which a solicited unit may sit.
DISPOSITIONS = ("samples", "responses", "failures", "rejected", "refusals")

#  Keys under which a tool receipt list appears. Both the flat form (`search_receipts`) used in
#  `failures` entries and the nested form (`search: {receipts: [...]}`) used in samples.
RECEIPT_KEYS = {
    "search": ("search_receipts", "search"),
    "fetch": ("fetch_receipts", "fetch"),
}

#  Directories whose parties were TOLD to use the tool. Counted, never merged with the rounds:
#  "parties never search" and "parties never search unless asked" are different claims.
INSTRUCTED_PREFIXES = ("toolprobe", "searchprobe", "fetchprobe")

#  RECOGNITION IS BY DECLARED TYPE, NOT BY SEARCHING FOR RECEIPT-LIKE WORDS.
#
#  The first version asked whether a known receipt spelling appeared anywhere in the serialised
#  document. Review broke it in one try with a schema this project has never used:
#
#      {"units": [{"tool_calls": [{"name": "browse", "receipt": {"ok": true}}]}]}
#
#  No known spelling, so it was classified "legitimately holds no solicited units" and the run
#  returned `usable: True, total: 0`. **That is the original silent zero under a new spelling, in
#  the tool built this morning to make it impossible.** The same test failed the other way too:
#  a metadata document merely mentioning "search" would have been refused.
#
#  So a file is recognised only if it DECLARES a type this module knows. Anything else refuses,
#  whether or not it looks like it holds receipts.
SOLICITATION_TYPES = frozenset({
    "solicitation", "solicitation_summary", "agenda_activation_solicitation",
    "qualification_solicitation", "ratification_ballot_solicitation",
    "raw_samples", "local_solicitation",
})

#  Artifacts that legitimately carry no solicited units. Each is listed BY TYPE with a reason,
#  so excluding one is a recorded decision rather than a silent classification.
NON_SOLICITATION_TYPES = {
    "solicitation_spec": "an outbound spec; the samples live in the raw file beside it",
    "agenda_activation_record": "computed from raw samples, does not hold them",
    "qualification_record": "computed from raw samples, does not hold them",
    "ratification_record": "computed from raw samples, does not hold them",
    "agenda_cohort_exposure": "a delivery record",
    "finding_coding": "coding over artifacts, not solicited units",
    "freetext_coding": "coding over artifacts, not solicited units",
    "annotation": "commentary on artifacts",
    "contribution": "a party contribution already summarised elsewhere",
    "deficiency_register": "the register, not a solicitation",
}


def _receipts(node: dict, kind: str) -> list:
    out = []
    for key in RECEIPT_KEYS[kind]:
        value = node.get(key)
        if isinstance(value, list):
            out += [r for r in value if isinstance(r, dict)]
        elif isinstance(value, dict):
            nested = value.get("receipts")
            if isinstance(nested, list):
                out += [r for r in nested if isinstance(r, dict)]
    return out


def scan(kind: str) -> dict:
    """Walk every raw file. Refuse rather than skip anything unrecognised."""
    counts = {"rounds": 0, "instructed": 0, "other": 0}
    per_file: dict[str, int] = {}
    visited = parsed = units = 0
    unparseable: list[str] = []
    unrecognised: list[str] = []
    for path in sorted(RAW.rglob("*.json")):
        visited += 1
        name = str(path.relative_to(RAW))
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:                                      # noqa: BLE001
            unparseable.append(f"{name}: {type(error).__name__}")
            continue
        parsed += 1
        if not isinstance(doc, dict):
            unrecognised.append(f"{name}: top level is {type(doc).__name__}, not an object")
            continue
        #  PRESENCE OF UNITS DECIDES FIRST, and the declared type only breaks the tie when there
        #  are none. The reverse order produced a THIRD silent zero within an hour of the second:
        #  raw sample files embed their outbound `spec`, so reading `spec.artifact_type` as a
        #  fallback classified them as `..._solicitation` and excluded them wholesale. The
        #  corpus-wide search count silently fell from 9 to 8 and the one numbered-round receipt
        #  disappeared -- the exact datum the whole module was built to stop losing.
        #
        #  A file holding solicited units is counted whatever it calls itself. Only a file with
        #  NO units needs a type, and an unknown one refuses rather than passing as empty.
        containers = [k for k in DISPOSITIONS if isinstance(doc.get(k), list)]
        if not containers:
            declared = doc.get("artifact_type")
            if declared in NON_SOLICITATION_TYPES:
                continue                      # excluded by a recorded decision, not by accident
            unrecognised.append(
                f"{name}: holds none of {DISPOSITIONS} and declares artifact_type {declared!r}, "
                f"which is not registered in NON_SOLICITATION_TYPES")
            continue
        bucket = ("instructed" if name.split("/")[0].startswith(INSTRUCTED_PREFIXES)
                  else "rounds" if name.split("/")[0].startswith("round-") else "other")
        for container in containers:
            for unit in doc[container]:
                if not isinstance(unit, dict):
                    continue
                units += 1
                found = len(_receipts(unit, kind))
                if found:
                    counts[bucket] += found
                    per_file[name] = per_file.get(name, 0) + found
    return {"kind": kind, "counts": counts, "total": sum(counts.values()), "per_file": per_file,
            "coverage": {"files_visited": visited, "files_parsed": parsed,
                         "solicited_units_seen": units,
                         "unparseable": unparseable, "unrecognised": unrecognised},
            "usable": not (unparseable or unrecognised)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--tool", choices=sorted(RECEIPT_KEYS), default="search")
    parser.add_argument("--coverage", action="store_true", help="print denominators only")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = scan(args.tool)
    cov = result["coverage"]
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["usable"] else 1

    print(f"  files visited {cov['files_visited']}, parsed {cov['files_parsed']}, "
          f"solicited units seen {cov['solicited_units_seen']}")
    if not result["usable"]:
        #  NO NUMBER IS PRINTED. The whole point: a count derived over a corpus this module
        #  could not fully read is the exact artifact that caused the failure it prevents.
        for entry in cov["unparseable"]:
            print(f"  UNPARSEABLE   {entry}", file=sys.stderr)
        for entry in cov["unrecognised"]:
            print(f"  UNRECOGNISED  {entry}", file=sys.stderr)
        print("\nREFUSING to report a count. A scan that cannot see a file reports absence,\n"
              "and absence is indistinguishable from a true zero in the output.", file=sys.stderr)
        return 1
    if args.coverage:
        return 0
    c = result["counts"]
    print(f"\n  {args.tool} receipts")
    print(f"    numbered rounds      {c['rounds']}")
    print(f"    instructed probes    {c['instructed']}   (parties were told to use the tool)")
    print(f"    other cohorts        {c['other']}")
    print(f"    TOTAL                {result['total']}")
    if result["per_file"]:
        print("\n  where they are:")
        for name, n in sorted(result["per_file"].items()):
            print(f"    {n:4d}  {name}")
    print("\n  A receipt records an invocation, not a motive. The rounds/probes split is kept\n"
          "  because 'parties never search' and 'parties never search unless asked' differ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
