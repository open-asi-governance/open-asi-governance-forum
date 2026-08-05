#!/usr/bin/env python3
"""Regenerate every derived artifact, in dependency order, and verify as it goes.

Run this after any change to the corpus. It is the whole maintenance path:

    python3 tools/rebuild.py

Order matters:

  1. manifest    — hash-anchor raw material FIRST, so later steps verify against it
  2. validate    — refuse to build anything from artifacts that fail provenance checks
  3. index       — corpus/index.md from segments.json
  4. viewer      — docs/index.html, the threaded page served by GitHub Pages

Supplied-context bundles are deliberately NOT rebuilt here. A bundle records what
a reviewer was shown; once a round has used it, capture records cite it by hash,
so regenerating it would silently invalidate those citations. Build one per round
with `tools/build_bundle.py <round>`, which refuses to overwrite an existing file.

Every step is deterministic. Rerunning on an unchanged repository produces
byte-identical output, so `git status` after a rebuild is a real signal: it means
something upstream actually changed.

Exit status is non-zero if any step fails, and the build stops there rather than
publishing a page derived from artifacts that did not validate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("hash-anchor raw material", ["tools/build_manifest.py", "corpus/raw/"]),
    ("validate provenance", ["tools/validate_provenance.py", "corpus/"]),
    ("render corpus index", ["tools/render_markdown.py", "corpus/artifacts/segments.json", "corpus/index.md"]),
    ("build threaded viewer", ["tools/build_viewer.py"]),
]


def main() -> int:
    for label, argv in STEPS:
        print(f"\n\033[1m▸ {label}\033[0m")
        result = subprocess.run([sys.executable, *argv], cwd=REPO_ROOT)
        if result.returncode != 0:
            print(f"\n\033[31mFAILED at: {label}\033[0m", file=sys.stderr)
            print("Nothing downstream was rebuilt. Fix the failure and rerun.", file=sys.stderr)
            return result.returncode

    print("\n\033[32mAll artifacts rebuilt and verified.\033[0m")
    print("Review `git status` — an unchanged repository should produce no diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
