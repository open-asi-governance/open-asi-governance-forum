#!/usr/bin/env python3
"""Run every test suite. Stdlib only, no test framework, no network.

    python3 tools/tests/run_all.py

Deliberately NOT wired into `tools/rebuild.py` yet. Every track runs rebuild, and
adding a step that can fail another track's build is a change to a shared path that
should be adopted rather than assumed. Proposed to the custodian in
`record/designs/T13-capture-ui-design.md`.

Exit status is non-zero if any suite fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITES = sorted(p for p in HERE.glob("test_*.py"))


def main() -> int:
    failed = []
    for suite in SUITES:
        print(f"\n\033[1m▸ {suite.name}\033[0m")
        if subprocess.run([sys.executable, str(suite)]).returncode != 0:
            failed.append(suite.name)

    print()
    if failed:
        print(f"\033[31mFAILED: {', '.join(failed)}\033[0m", file=sys.stderr)
        return 1
    print(f"\033[32mAll {len(SUITES)} suites passed.\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
