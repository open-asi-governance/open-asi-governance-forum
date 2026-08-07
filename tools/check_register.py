#!/usr/bin/env python3
"""Check the deficiency register against its structured artifact.

    python3 tools/check_register.py
    python3 tools/check_register.py --restamp D-25 [D-26 ...]
    python3 tools/check_register.py --restamp-all

Three artifacts of this repository stated three different counts of its own
defects at the same moment on 2026-08-06: `README.md` and the published page
said 21, `corpus/deficiencies.md`'s own status line said 24, and the document
held 28 `### D-NN` headings. Nobody noticed until an external reviewer counted.
A register that miscounts itself is evidence about how carefully it is
maintained, and the number is the cheapest possible thing to check.

WHAT THIS CHECKS, precisely, because overstating a check is the defect this
repository keeps filing against itself:

  R1  the count declared in the status line equals the number of D-NN headings
  R2  every heading matches the declared `### D-NN — title` grammar
  R3  ids are unique
  R4  no id is skipped between D-01 and the highest id present
  R5  the OTHER serially-numbered namespaces -- P-NNNN, T-NN -- are also unique
  R11 every scored prediction records who scored it, or a reason it is unrecorded
  R12 every scored prediction cites supporting artifacts that exist and still hash
  R6  corpus/artifacts/deficiency-register.json validates against its schema
  R7  entries and headings are one-to-one -- no entry without a heading, no
      heading without an entry
  R8  each entry's title is byte-equal to its heading's title
  R9  each entry's section_sha256 matches that section's current markdown
  R10  the recorded source hash matches corpus/deficiencies.md

R5 exists because of D-32. Two sessions working the same day each read the
register, saw D-28 as the highest entry, incremented, and filed a different
defect as D-29 -- this session was one of them. R3 caught it at merge.

**R9 IS THE POINT.** It does not establish that any judgement in the artifact
was ever correct. It establishes that the judgements were made against exactly
the text that is there now, so that editing an entry's prose FAILS THE BUILD
until a human re-reads the entry and re-stamps it. Metadata quietly describing
text it no longer matches is how a register starts lying slowly.

WHAT THIS DOES NOT CHECK, and what no deterministic rule could. It does not
read the prose. It cannot tell whether an entry's classification is accurate,
whether its stated finder is who actually found it, or whether its remediation
claim is true. Those are semantic judgements, and asserting otherwise would be
D-25 again -- a reproducible coder mistaken for a correct one. The artifact
carries a `human_review` field for exactly this reason, and its honest default
is `not_reviewed`.

`--restamp` recomputes section hashes for named entries and **resets their
human_review status to `not_reviewed`**, because the prose changed and any
earlier review of it is stale. Re-stamping records "the metadata now describes
this text". It does not record that anyone approved it.

Exit status is 0 when every check passes and 1 otherwise.
"""

from __future__ import annotations

import hashlib
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
ARTIFACT = REPO_ROOT / "corpus" / "artifacts" / "deficiency-register.json"
SCHEMA = REPO_ROOT / "tools" / "schemas" / "deficiency-register.schema.json"

HEADING = re.compile(r"^### (D-\d+) — (.+)$", re.MULTILINE)
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

    # R11 -- a scored prediction must say who scored it. The registry ran with no
    # scorer field at all: thirteen outcomes applied, and the party that judged them
    # recorded nowhere. The forecaster, the criterion author and the scorer were the
    # same surface, and that was not even capturable. D-18's shape.
    #
    # `identity: null` is ACCEPTABLE and is what the backfilled entries carry --
    # what is not acceptable is the field being absent, because absence cannot be
    # told apart from "nobody thought about it". A null with a stated reason is a
    # record; a missing key is a gap.
    scored = data.get("scored", []) if isinstance(data, dict) else []
    problems = []
    for entry in scored:
        if not isinstance(entry, dict):
            continue
        by = entry.get("scored_by")
        if by is None:
            problems.append(
                f"R11 {entry.get('id', '?')} is scored but has no scored_by. A scored "
                f"prediction must record who applied the outcome, or record null with a "
                f"reason. See D-18.")
        elif by.get("identity") is None and not by.get("identity_unrecorded_reason"):
            problems.append(
                f"R11 {entry.get('id', '?')} has scored_by.identity null with no "
                f"identity_unrecorded_reason. An unexplained null is a gap, not a record.")

    # R12 -- a scored prediction must cite the artifacts its evidence rests on, and
    # every cited path must exist and match its recorded hash. Two external parties
    # judged 10 of 13 scores unverifiable from what the registry published, because
    # the evidence restated derived numbers instead of pointing at the hash-anchored
    # samples that were sitting in corpus/raw/ the whole time. See D-40.
    for entry in scored:
        if not isinstance(entry, dict):
            continue
        sa = entry.get("supporting_artifacts")
        if not sa or not sa.get("paths"):
            problems.append(
                f"R12 {entry.get('id','?')} is scored but cites no supporting artifacts. "
                f"An evidence field that restates numbers without pointing at the material "
                f"asks to be trusted. See D-40.")
            continue
        for ref in sa["paths"]:
            target = REPO_ROOT / ref["path"]
            if not target.is_file():
                problems.append(f"R12 {entry.get('id','?')} cites a missing artifact: "
                                f"{ref['path']}")
            elif ref.get("sha256") and hashlib.sha256(
                    target.read_bytes()).hexdigest() != ref["sha256"]:
                problems.append(f"R12 {entry.get('id','?')} cites {ref['path']} at a hash "
                                f"that no longer matches the file.")

    ids = [entry["id"] for entry in entries]
    return problems + [
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


def sections(text: str) -> dict[str, tuple[str, str]]:
    """id -> (title, sha256 of the section's markdown).

    A section runs from its `### D-NN` heading to the next `### D-NN` heading or
    the next top-level `## ` heading, whichever comes first.
    """
    found = {}
    for part in re.split(r"(?m)^(?=### D-\d+ — )", text)[1:]:
        match = re.match(r"### (D-\d+) — (.+)\n", part)
        if not match:
            continue
        body = re.split(r"(?m)^## ", part)[0]
        found[match.group(1)] = (match.group(2).strip(),
                                 hashlib.sha256(body.encode("utf-8")).hexdigest())
    return found


def restamp(ids: list[str] | None) -> int:
    text = REGISTER.read_text(encoding="utf-8")
    current = sections(text)
    doc = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    targets = set(ids) if ids else {e["id"] for e in doc["entries"]}
    unknown = targets - set(current)
    if unknown:
        print(f"no such entry in the register: {' '.join(sorted(unknown))}")
        return 1

    changed = []
    for entry in doc["entries"]:
        if entry["id"] not in targets:
            continue
        title, digest = current[entry["id"]]
        if entry["title"] == title and entry["section_sha256"] == digest:
            continue
        entry["title"] = title
        entry["section_sha256"] = digest
        entry["human_review"] = {
            "status": "not_reviewed",
            "note": "Prose changed after the previous stamp; any earlier review of it is stale.",
        }
        changed.append(entry["id"])

    doc["source"]["sha256"] = hashlib.sha256(REGISTER.read_bytes()).hexdigest()
    ARTIFACT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if changed:
        print(f"re-stamped {len(changed)}: {' '.join(changed)}")
        print("Their human_review status is now `not_reviewed`. Re-stamping records that the")
        print("metadata describes this text. It does not record that anyone approved it.")
    else:
        print("nothing to re-stamp; every targeted entry already matches its section.")
    return 0


def main(argv: list[str]) -> int:
    if not REGISTER.is_file():
        print(f"register not found: {REGISTER.relative_to(REPO_ROOT)}")
        return 1

    if "--restamp-all" in argv:
        return restamp(None)
    if "--restamp" in argv:
        return restamp(argv[argv.index("--restamp") + 1:])

    text = REGISTER.read_text(encoding="utf-8")
    ids = [m[0] for m in HEADING.findall(text)]
    failures: list[str] = []

    for line in text.splitlines():
        if line.startswith("### D-") and not HEADING.match(line):
            failures.append(f"R2  heading does not match `### D-NN — title`:\n      {line}")

    seen = set()
    for entry_id in ids:
        if entry_id in seen:
            failures.append(f"R3  duplicate entry id: {entry_id}")
        seen.add(entry_id)

    numbers = sorted(int(entry_id.split("-")[1]) for entry_id in ids)
    if numbers:
        missing = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
        if missing:
            failures.append(
                "R4  gap in entry ids: " + ", ".join(f"D-{n:02d}" for n in missing)
                + "\n      An id present in no heading is usually an entry lost in an edit.")

    # R5 — the other serially-numbered namespaces. Ported from main; see D-32.
    failures.extend(check_predictions())
    failures.extend(check_tasks())

    declared_match = DECLARED.search(text)
    if not declared_match:
        failures.append("R1  could not find the declared count. Expected a status line of the form:\n"
                        '      **Status:** open — **NN entries**')
    elif int(declared_match.group(1)) != len(ids):
        failures.append(
            f"R1  the register declares {declared_match.group(1)} entries but contains {len(ids)} headings.\n"
            f"      Update the status line in corpus/deficiencies.md.")

    # ---- the structured artifact -------------------------------------------
    if not ARTIFACT.is_file():
        failures.append(f"R6  structured artifact missing: {ARTIFACT.relative_to(REPO_ROOT)}")
    else:
        doc = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        try:
            import jsonschema
        except ImportError:
            failures.append(
                "R6  jsonschema is not installed, so the artifact CANNOT be validated. "
                "This is a failure, not a skip: the build must not report a register as checked "
                "when its structure was never verified. Install with: pip install jsonschema")
        else:
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
            for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(doc),
                                key=lambda e: list(e.path)):
                location = "/".join(str(p) for p in error.path) or "<root>"
                failures.append(f"R6  {location}: {error.message}")

        current = sections(text)
        entry_ids = [e["id"] for e in doc.get("entries", [])]

        for orphan in sorted(set(entry_ids) - set(current)):
            failures.append(f"R7  artifact has entry {orphan} with no heading in the register")
        for unclassified in sorted(set(current) - set(entry_ids)):
            failures.append(
                f"R7  register heading {unclassified} has no entry in the artifact.\n"
                f"      Every deficiency must be classified, or the published view silently omits it.")

        drifted = []
        for entry in doc.get("entries", []):
            if entry["id"] not in current:
                continue
            title, digest = current[entry["id"]]
            if entry["title"] != title:
                failures.append(
                    f"R8  {entry['id']} title differs.\n"
                    f"      register: {title}\n      artifact: {entry['title']}")
            if entry["section_sha256"] != digest:
                drifted.append(entry["id"])

        if drifted:
            failures.append(
                "R9  prose changed since these entries were classified: " + ", ".join(drifted)
                + "\n      The metadata may no longer describe the text. Re-read each entry, then:"
                + f"\n        python3 tools/check_register.py --restamp {' '.join(drifted)}"
                + "\n      Re-stamping resets human_review to `not_reviewed`, deliberately.")

        recorded_source = doc.get("source", {}).get("sha256")
        actual_source = hashlib.sha256(REGISTER.read_bytes()).hexdigest()
        if recorded_source and recorded_source != actual_source and not drifted:
            failures.append(
                "R10  corpus/deficiencies.md changed outside any classified entry -- the header, the\n"
                "      summary tables, or the trailing sections. No entry classification is affected.\n"
                "      Refresh the recorded hash with: python3 tools/check_register.py --restamp-all")

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print()
        print(f"FAILED — {len(failures)} discrepanc{'y' if len(failures) == 1 else 'ies'} "
              f"between the deficiency register and its structured artifact.")
        return 1

    doc = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    reviewed = sum(1 for e in doc["entries"] if e["human_review"]["status"] == "reviewed_by_custodian")
    print(f"register consistent — {len(ids)} entries, D-01 … D-{max(numbers):02d}, no gaps, "
          f"no duplicates, all classified, all section hashes current.")
    print(f"Structural only. {reviewed} of {len(ids)} classifications have been read by a human "
          f"against the prose; nothing here checks that any of them is correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
