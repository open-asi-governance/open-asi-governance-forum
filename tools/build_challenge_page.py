#!/usr/bin/env python3
"""Publish CHALLENGE.md as docs/challenge.{md,html}.

**DETERMINISTIC.** The challenge lives at the repository root, where someone who clones will
trip over it, and on the site, where someone who is sent a link will. One source, two places.
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import build_round_pages as b                                            # noqa: E402


def main() -> int:
    #  A REFUSAL, because the alternative is publishing an empty challenge page and saying
    #  nothing. This tool is a copy with no judgement in it, which is why it had no case it must
    #  fail — but "no judgement" is not "no failure mode": a truncated or absent CHALLENGE.md
    #  would put a blank page at the address the record tells implementers to use, and the only
    #  signal would be a traceback if the file were missing and silence if it were empty. A crash
    #  and a refusal look different to an operator and only one of them is the control working.
    source = REPO_ROOT / "CHALLENGE.md"
    if not source.is_file():
        print(f"REFUSED: {source.name} is absent; the challenge page would be published empty "
              f"at the address the record tells implementers to use.", file=sys.stderr)
        return 1
    md = source.read_text(encoding="utf-8")
    if len(md.strip()) < 500:
        print(f"REFUSED: {source.name} is {len(md.strip())} characters. That is not a challenge; "
              f"publishing it would replace the live page with a stub.", file=sys.stderr)
        return 1
    docs = REPO_ROOT / "docs"
    (docs / "challenge.md").write_text(md, encoding="utf-8")
    (docs / "challenge.html").write_text(
        b.md_to_html(md, "Implementation challenge — OAGF", alternate="challenge.md"),
        encoding="utf-8")
    print(f"  docs/challenge.md   {len(md):,} chars (~{int(len(md)/4.08):,} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
