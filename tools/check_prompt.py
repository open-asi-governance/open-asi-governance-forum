#!/usr/bin/env python3
"""Check a solicitation prompt for the defects this project has actually committed.

    python3 tools/check_prompt.py                      # every committed prompt
    python3 tools/check_prompt.py path/to/prompt.md
    python3 tools/check_prompt.py --list-rules

WHAT THIS IS, AND THE THING IT IS NOT.

**This is a denylist of phrasings this repository has been caught using, plus a
structural check on the round template. It is NOT a detector of leading prompts.**

That distinction is the whole reason this file can exist honestly. A general
"detect bias in a prompt" checker would be D-25 exactly: an unvalidated classifier
published as authoritative, whose errors are asymmetric and invisible. A novel
leading phrasing will sail straight through this, and the moderator can write one
without trying. What this catches is **recurrence** -- the specific mistakes made
here, made again.

THE DEFECTS IT ENCODES, each with the entry it came from:

  D-23  a "Phase-1 blind" arm whose task instruction carried the annotator's own
        hypothesis, then read as independent
  D-31  requirement 2: a review prompt must not name the direction of the error it
        expects. Committed ONE DAY after D-23 was filed, in the instrument built to
        catch D-23's class
  D-05  operator prompt text elided after the fact, so what was asked is unknown
  D-40  evidence that restates numbers instead of pointing at the artifacts

Two live examples, both mine, both from prompts sent or nearly sent:

    "Where did the revision OVER-CORRECT?"        -- names the direction expected
    "Disagreement is more useful than endorsement" -- prescribes posture

The second was removed after external review and before the prompt was sent. The
first was sent.

STRUCTURAL RULES apply only to the round template, which has named slots. A prompt
that is missing a slot is missing something a party needs -- most importantly the
answer space, because without an explicit way to say "the evidence is insufficient"
a forced choice manufactures agreement. Measured: given that exit, one party used
it on 10 of 13 judgements.

Exit status is 0 when every checked prompt passes, 1 otherwise. Warnings do not
fail the build; they are heuristics and are labelled as such.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "record" / "solicitations" / "excerpts" / "round-prompt-template.md"
PROMPT_DIRS = [REPO_ROOT / "record" / "solicitations" / "excerpts"]

REQUIRED_SLOTS = ["standing", "who_is_asking", "forum_reference", "operative_text",
                  "context", "question", "answer_space", "ground_rules"]

#  Phrases this project has actually used. Each entry is (pattern, defect, why).
#  Nothing speculative belongs here: a denylist that grows by imagination becomes a
#  style guide enforced as a defect check.
DENYLIST = [
    (r"\bover[- ]?correct", "D-31",
     "names the direction of the expected error; the round-02 review prompt opened "
     "with 'Where did the revision OVER-CORRECT?' and the reply was then read as "
     "independent"),
    (r"disagreement is more useful", "D-31",
     "prescribes posture. Telling a party that dissent is valued shapes the answer "
     "as surely as telling it agreement is"),
    (r"do not soften", "D-31", "prescribes posture"),
    (r"do not manufacture agreement", "D-31",
     "prescribes posture; asking for candour is asking for a performance of candour"),
    (r"read it that way", "D-31",
     "instructs how to weigh a disclosed conflict rather than disclosing it"),
    (r"\bmost dangerous\b", "D-23",
     "characterises the item under review; the annotator's judgement of severity "
     "belongs in the record, not in the instruction"),
    (r"\byou will (?:think of|find|notice)\b", "D-23",
     "predicts the party's conclusion inside the instruction"),
    (r"\bobviously\b|\bclearly the\b", "D-23", "asserts the conclusion emphatically"),
    (r"\bconfirm (?:that|whether) (?:this|the) .{0,40}(?:is correct|holds)", "D-23",
     "frames the task as confirmation"),
]

#  Heuristics. WARN only -- each has a legitimate use and this cannot tell them apart.
WARNINGS = [
    (r"(?<![\w/])(?:D-\d{2})(?![\w])", "cites a deficiency by number",
     "a citation the party cannot resolve is not disclosure. Reproduce the operative "
     "text, or state that the number is for the record's readers rather than the party."),
    (r"§\s?\d", "cites a section by number",
     "same as above: reproduce the passage if the party needs it to answer."),
]


def sent_prompts() -> set[str]:
    """Prompts already put to a party, derived from what the artifacts anchor.

    A SENT PROMPT IS IMMUTABLE. D-36 is the entry: a prompt that misattributed a
    review round was found after it had gone to four parties, and correcting it
    would have falsified the record of what they were actually asked. The check
    that enforces this fired for real when an unrelated edit was attempted.

    So a violation in a sent prompt cannot be repaired and must not fail a build --
    demanding an impossible fix trains people to disable the check. It is reported
    as a RECORDED VIOLATION instead: visible, permanent, and attached to the prompt
    it describes.

    Derived, not listed by hand: any prompt an artifact names in prompt_path, or
    whose bytes match a recorded prompt_sha256.
    """
    import hashlib
    import json as _json
    named, hashes = set(), set()
    for base in ("corpus/artifacts", "record/rounds"):
        root = REPO_ROOT / base
        if not root.is_dir():
            continue
        for path in root.rglob("*.json"):
            try:
                doc = _json.loads(path.read_text(encoding="utf-8"))
            except Exception:                                       # noqa: BLE001
                continue
            for blob in (doc if isinstance(doc, list) else [doc]):
                if not isinstance(blob, dict):
                    continue
                stack = [blob]
                while stack:
                    node = stack.pop()
                    if isinstance(node, dict):
                        for key, value in node.items():
                            if key in ("prompt_path", "common_prompt") and isinstance(value, str):
                                named.add(value)
                            if key == "prompt_sha256" and isinstance(value, str):
                                hashes.add(value)
                            if key == "source_excerpt" and isinstance(value, dict):
                                if value.get("path"):
                                    named.add(value["path"])
                            if isinstance(value, (dict, list)):
                                stack.append(value)
                    elif isinstance(node, list):
                        stack.extend(node)
    out = set(named)
    for d in PROMPT_DIRS:
        for path in d.glob("*.md") if d.is_dir() else []:
            if hashlib.sha256(path.read_bytes()).hexdigest() in hashes:
                out.add(str(path.relative_to(REPO_ROOT)))
    return out


def slots_in(text: str) -> list[str]:
    return re.findall(r"<!--\s*SLOT:\s*([a-z_]+)\s*-->", text)


def check_text(text: str, path: Path, is_template: bool) -> tuple[list[str], list[str]]:
    errors, warns = [], []

    for pattern, defect, why in DENYLIST:
        for m in re.finditer(pattern, text, re.I):
            line = text[:m.start()].count("\n") + 1
            snippet = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            errors.append(f"{path.name}:{line} [{defect}] {why}\n"
                          f"      …{snippet.strip()}…")

    # Whitespace-normalised for CONTENT checks. The first version tested substrings
    # against the raw text and a line wrap defeated it: the template said
    # "you reject a\npremise" and the check for "reject a premise" failed on a
    # template that plainly contained it. A content check that a line break can
    # defeat is testing the formatting, not the content.
    flat = " ".join(text.replace("**", "").split()).lower()

    if is_template:
        found = slots_in(text)
        missing = [s for s in REQUIRED_SLOTS if s not in found]
        if missing:
            errors.append(f"{path.name}: missing slot(s): {', '.join(missing)}")
        elif found != [s for s in REQUIRED_SLOTS if s in found]:
            errors.append(f"{path.name}: slots are out of order: {found}")

        # The answer space must offer a way out, or forced choice manufactures agreement.
        if "insufficient" not in flat or "reject a premise" not in flat:
            errors.append(
                f"{path.name}: the answer space must let a party say the evidence is "
                f"insufficient AND that it rejects a premise. Without an exit, a forced "
                f"choice manufactures agreement.")
        if "not agreement, consent, ratification" not in flat:
            errors.append(
                f"{path.name}: missing the standing disclaimer that a reply is not "
                f"agreement, consent or ratification. A consulted party made this a "
                f"condition of participating.")

    for pattern, what, why in WARNINGS:
        hits = len(re.findall(pattern, text))
        if hits:
            warns.append(f"{path.name}: {hits}× {what} — {why}")
    return errors, warns


def targets(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(a) for a in argv]
    out = []
    for d in PROMPT_DIRS:
        if d.is_dir():
            out.extend(sorted(d.glob("*.md")))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--list-rules", action="store_true")
    args = ap.parse_args(argv)

    if args.list_rules:
        print("DENYLIST — phrasings this repository has been caught using:\n")
        for pattern, defect, why in DENYLIST:
            print(f"  [{defect}] /{pattern}/\n      {why}\n")
        print("WARNINGS — heuristics, never fatal:\n")
        for pattern, what, why in WARNINGS:
            print(f"  /{pattern}/  {what}\n      {why}\n")
        return 0

    files = targets(args.paths)
    if not files:
        print("no prompts to check.")
        return 0

    already_sent = sent_prompts()
    all_errors, all_warns, recorded = [], [], []
    for path in files:
        if not path.is_file():
            all_errors.append(f"{path}: not found")
            continue
        e, w = check_text(path.read_text(encoding="utf-8"), path,
                          is_template=(path.resolve() == TEMPLATE.resolve()))
        try:
            rel = str(path.resolve().relative_to(REPO_ROOT))
        except ValueError:
            rel = str(path)
        if rel in already_sent:
            recorded += [f"{x}  (SENT — immutable, cannot be repaired)" for x in e]
        else:
            all_errors += e
        all_warns += w

    for w in all_warns:
        print(f"  warn  {w}")
    for r in recorded:
        print(f"  RECORDED VIOLATION  {r}")
    if all_errors:
        print()
        for e in all_errors:
            print(f"FAIL  {e}")
        print(f"\nFAILED — {len(all_errors)} problem(s) in {len(files)} prompt(s).")
        print("This is a denylist of mistakes already made here, not a bias detector.")
        print("Passing it does not mean a prompt is neutral.")
        return 1

    print(f"{len(files)} prompt(s) checked, {len(all_warns)} warning(s), "
          f"{len(recorded)} recorded violation(s) in sent prompts.")
    print("Denylist and structure only. A NOVEL leading phrasing passes this "
          "unnoticed, and nothing here measures neutrality.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
