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
    md = (REPO_ROOT / "CHALLENGE.md").read_text(encoding="utf-8")
    docs = REPO_ROOT / "docs"
    (docs / "challenge.md").write_text(md, encoding="utf-8")
    (docs / "challenge.html").write_text(
        b.md_to_html(md, "Implementation challenge — OAGF", alternate="challenge.md"),
        encoding="utf-8")
    print(f"  docs/challenge.md   {len(md):,} chars (~{int(len(md)/4.08):,} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
