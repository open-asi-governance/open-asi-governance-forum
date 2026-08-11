#!/usr/bin/env python3
"""The ten material claims of prediction P-0032, and who caught each error.

    python3 tools/claim_ledger.py                     # the ledger
    python3 tools/claim_ledger.py --add "<claim>" --where <path>
    python3 tools/claim_ledger.py --caught <id> --by gate|codex|human|external --what "<error>"

WHY THIS EXISTS. P-0032 predicts that across the next ten material claims, **no gate will catch a
self-favouring error prospectively.** Without a counter that is not evaluable, and an unevaluable
stop condition is the false negative control 40 names by name. This is the counter.

WHAT COUNTS AS PROSPECTIVE. Only `--by gate`, and only when the gate's non-zero exit **preceded
the claim being landed**. An error found by Codex, by a human re-read, or by an outside reader does
not count however serious it was — those are the three that have caught all seven so far, which is
precisely why they are excluded. The prediction is about the machinery, not about whether errors
get caught.

P-0032 RESOLVES EARLY AND NEGATIVE the moment one `gate` entry is recorded. It resolves positive
only if ten claims are ledgered by 2026-10-05 with no gate catch among them.

WHAT THIS CANNOT DO. It cannot notice a material claim nobody ledgers. The entries are added by the
same layer that publishes the claims, so under-recording is available and undetectable from inside
— the same defect as everything else here, stated rather than solved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "record" / "claims" / "material-claims.json"
CATCHERS = ("gate", "codex", "human", "external")
TARGET = 10


def load() -> dict:
    if not LEDGER.is_file():
        return {"_what_this_is": "The ten material claims of prediction P-0032. A claim is one a "
                                 "reader could act on: a count, an absence, a novelty claim, a "
                                 "dependence claim, or a capability claim.",
                "claims": []}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def save(doc: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def report(doc: dict) -> int:
    claims = doc["claims"]
    caught = [c for c in claims if c.get("error_caught_by")]
    by_gate = [c for c in caught if c["error_caught_by"] == "gate"]
    print(f"  material claims ledgered: {len(claims)} of {TARGET}")
    print(f"  errors found:             {len(caught)}")
    for c in claims:
        mark = "✗" if c.get("error_caught_by") else " "
        who = f"  caught by {c['error_caught_by'].upper()}: {c.get('error','')[:60]}" \
            if c.get("error_caught_by") else ""
        print(f"    {mark} [{c['id']}] {c['claim'][:66]}{who}")
    print()
    if by_gate:
        print("  P-0032 RESOLVES NEGATIVE — a gate caught a self-favouring error prospectively:")
        for c in by_gate:
            print(f"    [{c['id']}] {c.get('error','')[:90]}")
        print("  That is the first observation supporting the claim that controls make builder")
        print("  error visible. It does not establish that they do so reliably.")
    elif len(claims) >= TARGET:
        print(f"  {TARGET} claims ledgered, no gate catch. P-0032 resolves POSITIVE at "
              f"2026-10-05, which is one of the three mothball conditions.")
    else:
        print(f"  {TARGET - len(claims)} more claims to ledger. Open.")
    print("\n  Entries are added by the layer that publishes the claims. Under-recording is")
    print("  available and undetectable from inside; that is stated, not solved.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--add", help="a material claim being published")
    parser.add_argument("--where", help="path or URL the claim appears at")
    parser.add_argument("--caught", help="claim id an error was found in")
    parser.add_argument("--by", choices=CATCHERS, help="who found it")
    parser.add_argument("--what", help="what the error was")
    args = parser.parse_args()
    doc = load()

    if args.add:
        if not args.where:
            parser.error("--add needs --where, or the claim cannot be checked later")
        entry = {"id": f"MC-{len(doc['claims']) + 1:03d}", "claim": args.add,
                 "where": args.where, "error_caught_by": None, "error": None}
        doc["claims"].append(entry)
        save(doc)
        print(f"  ledgered {entry['id']}")
        return 0

    if args.caught:
        if not args.by or not args.what:
            parser.error("--caught needs --by and --what")
        for c in doc["claims"]:
            if c["id"] == args.caught:
                c["error_caught_by"], c["error"] = args.by, args.what
                save(doc)
                print(f"  {args.caught}: error recorded, caught by {args.by.upper()}")
                if args.by == "gate":
                    print("  P-0032 resolves NEGATIVE. A gate caught one before anyone else.")
                return 0
        print(f"  no claim {args.caught}", file=sys.stderr)
        return 1

    return report(doc)


if __name__ == "__main__":
    raise SystemExit(main())
