#!/usr/bin/env python3
"""Fail the build when a published page is too large for the corpus's own reviewer.

    python3 tools/check_page_budget.py
    python3 tools/check_page_budget.py --report      # sizes for every page, no gate

WHY THIS IS A BUILD GATE AND NOT A NOTE.

`record/tasks/T03-oagf-github-presence.md` sets the requirement and the reason:
`qwen3.6-35b-a3b` serves this corpus with a 24,576-token context, and
`docs/index.html` reached ~107,000 tokens. **The project's own contributing party
could not read the project's own website.** The acceptance criterion is "no single
page exceeds ~20,000 tokens."

That criterion was written and then not enforced, and it drifted immediately.
Measured from git history on 2026-08-06, `docs/deficiencies.html` across six
commits in one day:

    14,292 -> 15,976 -> 17,105 -> 17,703 -> 18,408 -> 19,012

Every deficiency filed adds roughly 600-1,100 tokens. The page crosses 20,000
within one or two more entries, and nothing would have said so -- the next defect
filed would have pushed a published page out of budget as a side effect of
recording that some *other* thing was out of specification.

`docs/deficiencies.md` was **already over at 25,023** when this was written, and
that is the worse miss: the `.md` is the PLAIN-TEXT ALTERNATE, the artifact an
agent fetches instead of the HTML. The agent-readable variant was itself
unreadable to the agent it exists for.

So the budget is checked by the path that runs, per D-29's forward requirement.

WHAT THE NUMBER IS, STATED HONESTLY.

**This is an ESTIMATE, not a token count, and it is deliberately conservative.**
No tokenizer is installed here and none is pinned, so nothing in this repository
can produce the real number for any specific model. Calling a byte ratio a "token
count" would be D-01's shape -- a value that looks precise and resolves to
nothing.

The estimator is bytes / `BYTES_PER_TOKEN`, with `BYTES_PER_TOKEN = 3.4` rather
than the usual 4.0. Markup, escaped entities, hex digests and JSON tokenize far
worse than prose, so 4.0 flatters HTML. A page passing this check is very likely
under the real budget; a page failing it might be marginally under. **Erring
toward refusing a page that would have fit is the correct direction**, because the
cost of being wrong the other way is a party that cannot read the record.

The ceiling is 20,000 with a WARN band from 16,000, so a page that is drifting is
visible before it fails. Qwen3.6 needs room for instructions and its own output
inside 24,576; a page that exactly fills 20,000 leaves almost none.

WHAT THIS DOES NOT CHECK. Whether a page is *useful* at its size, whether chunk
boundaries fall in sensible places, or whether the plain-text alternates say the
same thing as the HTML. Those are judgements; this is a size gate with a size
gate's name.

Exit status is 0 when every page is within budget and 1 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

BYTES_PER_TOKEN = 3.4
CEILING = 20_000
WARN_AT = 16_000

#  Exact artifacts served for verification, not pages meant to be read in one
#  request. corpus/raw/initial-transcript.txt alone is ~107,000 characters, and
#  serving it whole is the point -- an agent checking a hash needs the WHOLE file,
#  not a slice of it. Exempting these is a real decision with a real cost, so it is
#  named here rather than hidden in a glob: anything under docs/artifacts/ is a
#  download, is linked as one, and is not counted as a page.
EXEMPT_DIRS = ("artifacts",)

TEXT_SUFFIXES = (".html", ".md", ".txt", ".json", ".xml")


def estimate(path: Path) -> int:
    return int(len(path.read_bytes()) / BYTES_PER_TOKEN)


def pages() -> list[Path]:
    if not DOCS.is_dir():
        return []
    out = []
    for path in sorted(DOCS.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in EXEMPT_DIRS for part in path.relative_to(DOCS).parts[:-1]):
            continue
        out.append(path)
    return out


def broken_links() -> list[str]:
    """Internal hrefs pointing at files that do not exist.

    Chunking multiplied the pages from 1 to 35 and moved the register mirror under
    docs/artifacts/. That broke 36 links in one edit, and nothing would have said
    so -- the byte-equality gate only proves a page is what its generator produces,
    which a page full of dead links satisfies perfectly. It also caught a
    rel="alternate" declared for a plain-text file that was never generated: a link
    telling an agent a readable version exists when none did.
    """
    import re
    out = []
    for path in sorted(DOCS.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for href in re.findall(r'href="([^"#:]+\.(?:html|md|txt|xml))"', text):
            if not (path.parent / href).resolve().exists():
                out.append(f"{path.relative_to(DOCS)} -> {href}")
    return sorted(set(out))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--report", action="store_true",
                        help="print every page's size and exit 0")
    args = parser.parse_args(argv)

    found = pages()
    if not found:
        print("no pages under docs/ to check.")
        return 0

    sized = sorted(((estimate(p), p) for p in found), reverse=True)
    over = [(n, p) for n, p in sized if n > CEILING]
    warn = [(n, p) for n, p in sized if WARN_AT < n <= CEILING]

    if args.report:
        print(f"{len(sized)} pages under docs/  (estimate: bytes / {BYTES_PER_TOKEN}, "
              f"ceiling {CEILING:,})\n")
        for n, p in sized:
            mark = "OVER" if n > CEILING else ("warn" if n > WARN_AT else "")
            print(f"  {n:>8,}  {p.relative_to(REPO_ROOT)}  {mark}")
        return 0

    for n, p in warn:
        print(f"  approaching the ceiling: {p.relative_to(REPO_ROOT)}  ~{n:,} "
              f"(ceiling {CEILING:,})")

    dead = broken_links()
    for entry in dead:
        print(f"BROKEN LINK  {entry}")

    if over or dead:
        print()
        for n, p in over:
            print(f"OVER BUDGET  {p.relative_to(REPO_ROOT)}")
            print(f"             ~{n:,} estimated tokens against a {CEILING:,} ceiling")
        print()
        if dead:
            print(f"FAILED — {len(dead)} broken internal link(s).")
        if not over:
            return 1
        print(f"FAILED — {len(over)} published page(s) exceed the budget.")
        print("The corpus's own contributing party serves a 24,576-token context. A page")
        print("larger than this ceiling cannot be read by the participant the record depends")
        print("on, which is the reason T-03 set the criterion. Split the page, or move the")
        print("artifact under docs/artifacts/ if it is a download rather than a page.")
        print(f"Sizes are ESTIMATES (bytes / {BYTES_PER_TOKEN}), deliberately conservative;")
        print("no tokenizer is pinned in this repository, so no exact count is available.")
        return 1

    largest, where = sized[0]
    print(f"every published page is within budget — largest is "
          f"{where.relative_to(REPO_ROOT)} at ~{largest:,} of {CEILING:,}.")
    print(f"Estimated as bytes / {BYTES_PER_TOKEN}, not tokenized. Conservative by design.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
