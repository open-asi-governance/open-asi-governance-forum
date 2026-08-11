#!/usr/bin/env python3
"""DEPRECATED alias. The verifier is now `verify_fault_injection.py`.

Kept because this name appears in published pages and in outreach sent to ten people on
2026-08-10. Breaking their copy-pasted command to tidy our own naming error would put the cost of
the mistake on them.

It re-exports the real module rather than reimplementing anything, so `import
verify_negative_control` and `python3 tools/verify_negative_control.py --fixtures` both keep
working and both exercise the same code. The first version of this shim used `runpy` and executed
the CLI at import time, which broke the test suite -- a forwarder that changes behaviour is not a
forwarder.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_fault_injection import *                                     # noqa: F401,F403,E402
from verify_fault_injection import (                                     # noqa: E402
    FIXTURES, GAPS, TRANSPORT_ONLY, Violation, main, normalise, problems_for,
    report_gaps, run_fixtures, verify,
)

_DEPRECATION = (
    "  ! tools/verify_negative_control.py is a deprecated alias. The profile was renamed on\n"
    "    2026-08-11 because 'negative control' reversed established laboratory terminology.\n"
    "    Use tools/verify_fault_injection.py. See spec/ficp/MIGRATION.md.\n"
)

if __name__ == "__main__":
    print(_DEPRECATION, file=sys.stderr)
    raise SystemExit(main())
