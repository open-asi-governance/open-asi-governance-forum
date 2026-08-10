#!/usr/bin/env python3
"""Every quotation attributed to a party must appear in `corpus/raw/`. Stdlib only, no network.

    python3 tools/check_quotations.py            # check
    python3 tools/check_quotations.py --list     # show every attributed quotation found

Why this exists
---------------
D-53. Two documents written by this project's own annotator quoted a party saying things the
party never said. One invented a sentence outright and reported it as "3 of 3 samples" when
there were four samples saying close to the opposite; the other attributed to a party a phrase
that came from the *prompt* that party received. Both were load-bearing — they were the cited
evidence for a claim that shaped a build — and both flattered the argument they supported, which
is the direction fabrication runs when nothing checks.

Neither was caught here. An external reviewer found them, asked to be hostile, on the day one was
about to be published to parties.

The structural gap this closes
------------------------------
Every other safeguard in this repository governs `corpus/`: the manifest, the append-only history
check, the provenance validator, the capture gates. **Design notes, session turnovers and
handoffs are prose, and prose that quotes the corpus was checked against it by nothing.** A
quotation in a design document was, until this program, exactly as verified as a quotation in a
blog post.

What it checks, and what it deliberately does not
-------------------------------------------------
Checking every quoted string would drown in false positives — this repository quotes filenames,
error text, its own documents, and external reviewers who are not parties. So the rule is
narrow and aimed at the defect that actually occurred:

    A quoted string of at least MIN_LENGTH characters, preceded within ATTRIBUTION_WINDOW
    characters by a party's name AND a speech verb crediting that party with saying it, must
    appear in corpus/raw/.

The speech verb is what makes the rule usable. Requiring only a nearby party name flagged 152
passages on first run — template placeholders, field-value examples, questions a design document
proposes to ask — none of them claims about what a party said. A checker that fails 152 times is
one nobody reads, which is worse than no checker. "Qwen SAID as much: ..." and "Qwen CALLED it
theatre" are the shape that actually went wrong, and both carry a verb.

It will not catch a fabrication attributed to nobody, one paraphrased without quotation marks, or
one whose attribution is implied by layout rather than stated. Those remain unguarded, and saying
so is better than implying this program makes prose trustworthy.

Ellipsis is handled by checking each fragment: an elided quotation is legitimate, but every
surviving fragment still has to be real.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
#  Verified against the WHOLE corpus, not just raw/. The review bundles quote annotation
#  artifacts verbatim -- real committed material that simply is not a party utterance -- and
#  failing 32 times on those would have made this unusable. Both D-53 fabrications appear
#  nowhere in corpus/ at all, so the widened source still catches the defect this exists for.
#
#  The cost is honest and worth stating: a sentence written BY the annotator into an artifact
#  now satisfies a quotation attributed to a party. This checks that quoted words exist in the
#  corpus, not that the right speaker said them.
CORPUS = REPO_ROOT / "corpus"

#  Shorter than this and a "quotation" is usually a term, a field name, or a label.
MIN_LENGTH = 40

#  How far before a quotation to look for the party being credited with it.
ATTRIBUTION_WINDOW = 240

#  Party names as they are written in prose. Keys of PARTIES/CHAT_PARTIES plus the display names
#  used in identity strings. Matched case-insensitively on a word boundary.
#  A quotation is a claim about what a party SAID only when something says so. Without this the
#  rule flags every quoted string that happens to sit near a party's name.
SPEECH_VERBS = [
    "said", "says", "saying", "wrote", "writes", "called", "calls", "put it", "answered",
    "answers", "replied", "replies", "noted", "notes", "objected", "objects", "observed",
    "observes", "argued", "argues", "reported", "reports", "described", "describes", "stated",
    "states", "claimed", "claims", "responded", "warned", "insisted", "concluded", "concludes",
    "quoted", "quotes", "told", "asserts", "asserted", "in its own words", "verbatim",
    "of 3 samples", "of 5 samples", "of 20 samples", "samples:",
]

PARTY_NAMES = [
    "qwen", "grok", "gemini", "chatgpt", "claude", "gpt-5", "gpt",
    "claudeai", "geminiapp", "grokapp",
]

#  Directories whose prose is checked. corpus/ itself is excluded: it IS the source, and its
#  artifacts legitimately quote the raw material they annotate.
SEARCH_ROOTS = ["record"]
SEARCH_FILES = ["README.md", "HANDOFF.md", "CONTRIBUTING.md", "GOVERNANCE.md", "FOR-PARTIES.md"]

#  A quotation inside one of these is a statement ABOUT a fabricated or corrected quotation, not
#  a fresh claim that a party said it. D-53's own corrections quote the false text on purpose, so
#  that a reader who saw the original can recognise it.
EXEMPT_MARKERS = [
    "CORRECTION", "fabricat", "no party said", "never said", "D-53",
    "did not say", "misattribut",
]

QUOTE_PATTERNS = [
    re.compile(r'"([^"\n]{%d,})"' % MIN_LENGTH),
    re.compile(r'“([^”\n]{%d,})”' % MIN_LENGTH),
]


def normalise(text: str) -> str:
    """Fold the differences that survive a copy-paste but do not change the words."""
    text = unicodedata.normalize("NFKC", text)
    text = (text.replace("’", "'").replace("‘", "'")
                .replace("“", '"').replace("”", '"')
                .replace("—", "-").replace("–", "-"))
    return " ".join(text.split()).lower()


def load_corpus() -> str:
    """One normalised blob of every raw byte. Crude, and crude is right here.

    Raw material is JSON, markdown and plain text; a party's words may sit inside a JSON string
    with escapes. Searching the decoded text of everything avoids caring which.
    """
    parts = []
    for path in sorted(CORPUS.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:                                                 # noqa: BLE001
            continue
        parts.append(text)
        if path.suffix == ".json":
            #  Also append the decoded form, so `\n` inside a JSON string matches prose that
            #  quotes it with a real newline.
            try:
                parts.append(json.dumps(json.loads(text), ensure_ascii=False))
                parts.append(re.sub(r"\\n", " ", text))
            except Exception:                                             # noqa: BLE001
                pass
    return normalise("\n".join(parts))


def attributed_party(before: str) -> str | None:
    """The party CREDITED WITH SAYING a quotation, from the text preceding it.

    Requires both a party name and, after it, a verb crediting that party with the words. The
    ordering matters: "Codex said Qwen was wrong" should not make Qwen the speaker, and a party
    named after the verb is usually the subject of the sentence rather than its author.
    """
    window = before[-ATTRIBUTION_WINDOW:].lower()
    best, best_at = None, -1
    for name in PARTY_NAMES:
        for match in re.finditer(r"\b" + re.escape(name) + r"\b", window):
            if match.start() > best_at:
                best, best_at = name, match.start()
    if best is None:
        return None
    after_party = window[best_at:]
    #  Word boundaries, and never inside an identifier: the JSON key `claim_as_stated` matched
    #  "stated" and made every field value in a reproduced file look like a party's utterance.
    for verb in SPEECH_VERBS:
        for hit in re.finditer(r"(?<![\w_])" + re.escape(verb) + r"(?![\w_])", after_party):
            return best
    return None


def fragments(quotation: str) -> list[str]:
    """Split an elided quotation; every surviving fragment must still be real."""
    parts = re.split(r"\s*(?:…|\.\.\.)\s*", quotation)
    return [p for p in (part.strip(" .,;:") for part in parts) if len(p) >= MIN_LENGTH]


FENCE = re.compile(r"(?ms)^```.*?^```")


def strip_fenced(text: str) -> str:
    """Blank out fenced blocks, preserving offsets so reported line numbers stay true.

    The supplied-context bundles reproduce whole repository files verbatim inside fences for
    reviewers who cannot fetch the repo. That is embedded material, not prose making a claim
    about what a party said, and treating it as prose produced 22 findings that were all the
    checker misreading JSON.
    """
    return FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


#  CAPTURED, NOT AUTHORED. D-53 is about this layer fabricating a party quotation in a document
#  it wrote. A Codex transcript is verbatim external output, stored so a review can be re-read --
#  the same category as corpus/raw, and equally not something to edit to satisfy a checker. It
#  quotes code and clause drafts near party names, which this checker reads as attribution.
#
#  This is a scope rule, not a silencer: nothing this layer AUTHORS is exempt, and if a claim
#  from a transcript is repeated in a document, that document is still checked.
NOT_AUTHORED_HERE = ("record/executive/codex-transcripts",)


def files_to_check() -> list[Path]:
    found = [REPO_ROOT / name for name in SEARCH_FILES]
    for root in SEARCH_ROOTS:
        found.extend(sorted((REPO_ROOT / root).rglob("*.md")))
    return [p for p in found
            if p.is_file()
            and not any(str(p.relative_to(REPO_ROOT)).startswith(skip)
                        for skip in NOT_AUTHORED_HERE)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true",
                        help="print every attributed quotation and where it was verified")
    args = parser.parse_args()

    corpus = load_corpus()
    if not corpus:
        print("REFUSED: corpus/ is empty or unreadable; a check that cannot fail is not a "
              "check.", file=sys.stderr)
        return 2

    checked = 0
    unverified: list[tuple[Path, int, str, str]] = []

    for path in files_to_check():
        text = strip_fenced(path.read_text(encoding="utf-8"))
        lines = text.splitlines(keepends=True)
        offsets, running = [], 0
        for line in lines:
            offsets.append(running)
            running += len(line)

        for pattern in QUOTE_PATTERNS:
            for match in pattern.finditer(text):
                quotation = match.group(1)
                before = text[:match.start()]
                party = attributed_party(before)
                if not party:
                    continue
                context = before[-ATTRIBUTION_WINDOW:] + quotation
                if any(marker.lower() in context.lower() for marker in EXEMPT_MARKERS):
                    continue

                #  A template placeholder is not a quotation of anything.
                if "{" in quotation and "}" in quotation:
                    continue
                checked += 1
                missing = [f for f in fragments(quotation) if normalise(f) not in corpus]
                if missing:
                    line_no = sum(1 for off in offsets if off <= match.start())
                    unverified.append((path, line_no, party, missing[0]))
                elif args.list:
                    rel = path.relative_to(REPO_ROOT)
                    print(f"  ok   {rel}  [{party}]  {quotation[:70]}…")

    rel = lambda p: p.relative_to(REPO_ROOT)                              # noqa: E731
    if unverified:
        print(f"\n\033[31mFAILED — {len(unverified)} attributed quotation(s) do not appear in "
              f"corpus/\033[0m", file=sys.stderr)
        for path, line_no, party, missing in unverified:
            print(f"\n  {rel(path)}:{line_no}", file=sys.stderr)
            print(f"    attributed to: {party}", file=sys.stderr)
            print(f"    not in corpus: \"{missing[:150]}\"", file=sys.stderr)
        print(f"\nEither the quotation is wrong, or it is not a quotation and should not be in "
              f"quotation marks. If it is a correction quoting known-false text on purpose, it "
              f"needs one of these markers nearby: {', '.join(EXEMPT_MARKERS[:4])}…",
              file=sys.stderr)
        return 1

    print(f"{checked} attributed quotation(s) checked against corpus/ — all found.")
    print("Scope: quotations of >= %d characters within %d characters after a party's name. "
          "A fabrication attributed to nobody, or paraphrased without quotation marks, is NOT "
          "caught by this." % (MIN_LENGTH, ATTRIBUTION_WINDOW))
    return 0


if __name__ == "__main__":
    sys.exit(main())
