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
  R5  the OTHER serially-numbered namespaces -- P-NNNN, T-NN -- are also unique

R5 exists because of D-32. Two sessions working the same day each read the
register, saw D-28 as the highest entry, incremented, and filed a different
defect as D-29. Both followed the only procedure there was. R3 caught it at
merge, which is the one piece of luck in that story: R3 was written by one of
those two sessions, days before the collision, for an unrelated reason.

Predictions are the acute case and are why R5 is not deferred. ICP §5 requires a
prediction to be filed BEFORE its run, so two sessions can register P-0009
against different hypotheses, each validly, each cited in its own run record --
and unlike a deficiency, the collision is baked into a result that was already
reported before any merge existed to catch it. A duplicate id there does not
merely confuse a citation; it makes two pre-registrations unfalsifiable as a
pair.

R5 checks uniqueness only, NOT gaps. A gap in `P-` or `T-` is ordinary: task
numbers here come from an external list where not every number becomes a file,
and there is nothing to infer from an absence. Claiming otherwise would produce
a check that fails on correct repositories, which trains people to ignore it.

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

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTER = REPO_ROOT / "corpus" / "deficiencies.md"
PREDICTIONS = REPO_ROOT / "predictions" / "predictions.json"
TASKS_DIR = REPO_ROOT / "record" / "tasks"

TASK_FILE = re.compile(r"^(T\d+)-")

HEADING = re.compile(r"^### (D-\d+) — (.+)$", re.MULTILINE)
# The status line states the total. Written as a bolded count so it reads as prose
# and still parses: "**Status:** open — **30 entries** (D-01 … D-30)."
DECLARED = re.compile(r"\*\*Status:\*\*\s*open\s*—\s*\*\*(\d+) entries\*\*")


def duplicates(ids: list[str]) -> list[str]:
    return sorted(entry for entry, count in Counter(ids).items() if count > 1)


def check_predictions() -> list[str]:
    """R5 for `P-NNNN`. A missing or malformed file is a failure, not a skip.

    Returning silently when the file cannot be read is the fail-open shape this
    repository has now filed three times (D-29, D-31, and the jsonschema
    ImportError). A check that reports nothing wrong because it did not run is
    indistinguishable, to the caller, from a check that passed.
    """
    if not PREDICTIONS.is_file():
        return [f"R5  predictions file not found: {PREDICTIONS.relative_to(REPO_ROOT)}"]
    try:
        data = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"R5  predictions file is not valid JSON: {error}"]

    entries = data.get("predictions", data) if isinstance(data, dict) else data
    if not isinstance(entries, list):
        return ["R5  predictions file does not hold a list of predictions."]

    missing = [i for i, entry in enumerate(entries)
               if not isinstance(entry, dict) or not entry.get("id")]
    if missing:
        return [f"R5  {len(missing)} prediction(s) have no id, at index "
                + ", ".join(str(i) for i in missing)]

    ids = [entry["id"] for entry in entries]
    return [
        f"R5  duplicate prediction id: {entry}\n"
        f"      Two pre-registrations sharing an id are unfalsifiable as a pair —\n"
        f"      each run cites {entry} and they resolve differently. See D-32."
        for entry in duplicates(ids)
    ]


def check_tasks() -> list[str]:
    """R5 for `T-NN`, read from the brief filenames in record/tasks/.

    Uniqueness only. Gaps are expected here — task numbers come from an external
    list and not every number becomes a committed brief.
    """
    if not TASKS_DIR.is_dir():
        return [f"R5  task directory not found: {TASKS_DIR.relative_to(REPO_ROOT)}"]

    seen: dict[str, list[str]] = {}
    for path in sorted(TASKS_DIR.glob("*.md")):
        match = TASK_FILE.match(path.name)
        if match:
            seen.setdefault(match.group(1), []).append(path.name)

    return [
        f"R5  duplicate task id {entry} in: " + ", ".join(names)
        for entry, names in sorted(seen.items()) if len(names) > 1
    ]


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

    # R5 — the other serially-numbered namespaces. See the module docstring: this
    # is D-32's forward requirement, and predictions are the case that motivates it.
    failures.extend(check_predictions())
    failures.extend(check_tasks())

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print()
        print(f"FAILED — {len(failures)} discrepanc{'y' if len(failures) == 1 else 'ies'} "
              f"in the deficiency register's self-description.")
        return 1

    print(f"register self-description consistent — {len(ids)} entries, "
          f"{ids[0]} … D-{max(numbers):02d}, no gaps, no duplicates.")
    print("identifiers unique across D-NN, P-NNNN and T-NN (Q-NN is not covered).")
    print("Structural only: this does not check that any entry's content is accurate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
