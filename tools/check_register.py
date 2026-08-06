#!/usr/bin/env python3
"""Check that the deficiency register's self-description matches the register.

Three artifacts of this repository stated three different counts of its own
defects at the same moment on 2026-08-06: `README.md` and the published page said
21, `corpus/deficiencies.md`'s own status line said 24, and the document held 28
`### D-NN` headings. Nobody noticed until an external reviewer counted.

A register that miscounts itself is evidence about how carefully it is
maintained, and the number is the cheapest possible thing to check. So it is
checked, by the path that actually runs, per D-29's forward requirement.

WHAT THIS CHECKS, precisely, because overstating a check is the defect this
repository keeps filing against itself:

  R1  the count declared in the status line equals the number of D-NN headings
  R2  every heading matches the declared `### D-NN — title` grammar
  R3  ids are unique
  R4  no id is skipped between D-01 and the highest id present

WHAT THIS DOES NOT CHECK. It does not read the prose. It cannot tell whether an
entry's content is accurate, whether its stated finder is who actually found it,
or whether its remediation claim is true. Those are human judgements and no
deterministic rule establishes them -- asserting otherwise would be D-25 again,
where a reproducible coder was mistaken for a correct one. This is a structural
check with a structural name.

Usage:
    python3 tools/check_register.py

Exit status is 0 when every check passes and 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTER = REPO_ROOT / "corpus" / "deficiencies.md"

HEADING = re.compile(r"^### (D-\d+) — (.+)$", re.MULTILINE)
# The status line states the total. Written as a bolded count so it reads as prose
# and still parses: "**Status:** open — **30 entries** (D-01 … D-30)."
DECLARED = re.compile(r"\*\*Status:\*\*\s*open\s*—\s*\*\*(\d+) entries\*\*")


def main() -> int:
    if not REGISTER.is_file():
        print(f"register not found: {REGISTER.relative_to(REPO_ROOT)}")
        return 1

    text = REGISTER.read_text(encoding="utf-8")
    headings = HEADING.findall(text)
    ids = [match[0] for match in headings]
    failures = []

    # R2 — every "### D-" line parses. A heading the grammar misses would be
    # silently uncounted, which is the failure this tool exists to prevent.
    for line in text.splitlines():
        if line.startswith("### D-") and not HEADING.match(line):
            failures.append(f"R2  heading does not match `### D-NN — title`:\n      {line}")

    # R3 — unique ids.
    seen = set()
    for entry_id in ids:
        if entry_id in seen:
            failures.append(f"R3  duplicate entry id: {entry_id}")
        seen.add(entry_id)

    # R4 — no gaps. A missing id usually means an entry was dropped in an edit.
    numbers = sorted(int(entry_id.split("-")[1]) for entry_id in ids)
    if numbers:
        missing = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
        if missing:
            failures.append(
                "R4  gap in entry ids: "
                + ", ".join(f"D-{n:02d}" for n in missing)
                + "\n      An id present in no heading is usually an entry lost in an edit."
            )

    # R1 — the declared count matches reality.
    declared_match = DECLARED.search(text)
    if not declared_match:
        failures.append(
            "R1  could not find the declared count. Expected a status line of the form:\n"
            '      **Status:** open — **NN entries**'
        )
    else:
        declared = int(declared_match.group(1))
        if declared != len(ids):
            failures.append(
                f"R1  the register declares {declared} entries but contains {len(ids)} headings.\n"
                f"      A register that miscounts itself is evidence about how carefully it is\n"
                f"      maintained. Update the status line in corpus/deficiencies.md."
            )

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print()
        print(f"FAILED — {len(failures)} discrepanc{'y' if len(failures) == 1 else 'ies'} "
              f"in the deficiency register's self-description.")
        return 1

    print(f"register self-description consistent — {len(ids)} entries, "
          f"{ids[0]} … D-{max(numbers):02d}, no gaps, no duplicates.")
    print("Structural only: this does not check that any entry's content is accurate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
