#!/usr/bin/env python3
"""Conformance tests for the measured capability gate.

    python3 tools/tests/test_capability_fits.py

A party handed a tool its endpoint cannot use does not decline gracefully -- it dies on the
prefill ceiling and takes the whole arm with it. Round-017 lost qwen 6/6 that way, and
round-016's local arm was unusable for the same reason without anyone noticing, because a party
that never calls a tool looks identical to a party that cannot.

The gate withholds by MEASUREMENT, and these tests hold the measurement honest:

* it withholds when the prompt plus ONE tool result exceeds the recorded ceiling;
* it permits when they fit, so the gate re-opens without anyone remembering to re-open it;
* absent or unrecorded ceilings never cause a withhold -- no evidence of a small context is not
  evidence of one;
* a party with no capability is untouched.
"""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import round_cycle as rc                                                  # noqa: E402

PASSED = FAILED = 0
def check(label, cond):
    global PASSED, FAILED
    if cond: PASSED += 1; print(f"  \033[32m✓\033[0m {label}")
    else: FAILED += 1; print(f"  \033[31m✗ {label}\033[0m")

CAP = rc.CAPABILITIES["search-fetch-v1"]

def with_ceiling(tokens, ratio=4.08):
    """Point the gate at a temporary fingerprint, so tests never depend on the live one."""
    p = Path(tempfile.mkdtemp()) / "fp.json"
    p.write_text(json.dumps({"endpoint": rc.LOCAL_ENDPOINT, "model_id": "m",
                             "max_prefill_tokens": tokens,
                             "chars_per_token_observed": ratio}))
    return p

saved = rc.SERVE_FINGERPRINT_PATH
one_result_tokens = rc.FETCH_RESULT_CHARS / 4.08

print("\nit withholds only when a single call cannot complete")
rc.SERVE_FINGERPRINT_PATH = with_ceiling(16384)
fits, why = rc.capability_fits(54191, CAP)
check("today's 54,191-char prompt does NOT fit", fits is False)
check("the reason names the ceiling, the prompt and the result size",
      "16,384" in why and "13,282" in why and "14,706" in why)
check("the reason says it was measured, not chosen",
      "by measurement, not by choice" in why)
check("the reason records that raising it was ATTEMPTED and failed",
      "would not start" in why and "GPU memory" in why)

#  The threshold, computed rather than guessed: ceiling minus one result, in characters.
allowed = int((16384 - one_result_tokens) * 4.08)
check(f"a prompt just under the threshold ({allowed:,} chars) fits",
      rc.capability_fits(allowed - 500, CAP)[0] is True)
check("a prompt just over it does not",
      rc.capability_fits(allowed + 500, CAP)[0] is False)

print("\nthe gate re-opens on its own when the numbers change")
rc.SERVE_FINGERPRINT_PATH = with_ceiling(65536)
check("a larger measured ceiling re-admits today's prompt",
      rc.capability_fits(54191, CAP)[0] is True)
rc.SERVE_FINGERPRINT_PATH = with_ceiling(16384)
smaller = dict(CAP, spec=dict(CAP["spec"]))
check("shrinking the PROMPT alone is not enough at the 60k cap",
      rc.capability_fits(20000, CAP)[0] is False,)

print("\nabsence of a measurement never causes a withhold")
rc.SERVE_FINGERPRINT_PATH = with_ceiling(0)
check("a fingerprint with no ceiling permits", rc.capability_fits(54191, CAP)[0] is True)
rc.SERVE_FINGERPRINT_PATH = Path("/nonexistent/fp.json")
check("a missing fingerprint permits rather than refusing",
      rc.capability_fits(54191, CAP)[0] is True)

print("\na party with no capability is untouched")
rc.SERVE_FINGERPRINT_PATH = with_ceiling(16384)
check("no capability -> fits, no reason", rc.capability_fits(999999, None) == (True, ""))
rc.SERVE_FINGERPRINT_PATH = saved

print("\nthe live fingerprint carries what the gate needs")
live = json.loads(rc.SERVE_FINGERPRINT_PATH.read_text())
check("it records a measured prefill ceiling", live.get("max_prefill_tokens") == 16384)
check("it records the observed chars/token, not an assumed one",
      abs(live.get("chars_per_token_observed", 0) - 4.08) < 0.01)
check("it records HOW it was measured", "binary search" in live.get("how_measured", "").lower())
check("it records that raising it was attempted and failed",
      "insufficient GPU memory" in live.get("why_this_is_recorded_here", ""))

print("\nthe withholding is recorded on the spec, never inferred from silence")
schema = json.loads((REPO_ROOT / "tools/schemas/solicitation-spec.schema.json").read_text())
check("the spec schema admits capability_withheld",
      "capability_withheld" in schema["properties"])
check("...and says why absence must not be inferred",
      "inferred from silence" in schema["properties"]["capability_withheld"]["description"])

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
