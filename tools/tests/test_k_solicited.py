#!/usr/bin/env python3
"""Conformance tests for k_solicited vs k_min_usable, and the serve fingerprint.

    python3 tools/tests/test_k_solicited.py

Two numbers were one number. `k_requested` meant both "attempts scheduled" and "how many must
survive", so scheduling a spare attempt to absorb a known loss rate bought nothing: five usable
of six halted exactly as four of five had. These tests keep them apart.

The fingerprint tests exist because two truncation measurements were taken against an SSH tunnel
to a different host on 2026-08-08, while the round solicits a local server. Both answer to the
same model name, so nothing in either result looked wrong.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import round_cycle as rc                                                 # noqa: E402
import build_round_pages as b                                            # noqa: E402

PASSED = FAILED = 0
def check(label, cond):
    global PASSED, FAILED
    if cond: PASSED += 1; print(f"  \033[32m✓\033[0m {label}")
    else: FAILED += 1; print(f"  \033[31m✗ {label}\033[0m")

print("\nthe two numbers are separate")
check("the local arm schedules six attempts", rc.K_SOLICITED_BY_ARM["local"] == 6)
check("routed arms schedule five", rc.K_SOLICITED_BY_ARM["routed"] == 5)
check("the usable floor is five for everyone", rc.K_MIN_FLOOR == 5)
check("scheduled and floor are different numbers for the local arm",
      rc.K_SOLICITED_BY_ARM["local"] != rc.K_MIN_FLOOR)

print("\nthe undersample gate tests USABLE, not scheduled")
src = (REPO_ROOT / "tools" / "round_cycle.py").read_text()
i = src.index("short = [k for k, s in summaries.items()")
window = src[i:i+260]
check("the gate compares against a floor, not against k_requested",
      "floor_by_party" in window and "k_requested" not in window)

print("\nthe published page agrees with the gate")
psrc = (REPO_ROOT / "tools" / "build_round_pages.py").read_text()
j = psrc.index("undersampled = sorted(")
check("the publisher also uses k_min_usable",
      "k_min_usable" in psrc[j:j+320])
#  A page that labelled 5-of-6 undersampled would contradict the gate that let the round run.
def undersampled(summaries):
    return sorted(p for p, sm in summaries.items()
                  if (sm.get("k_collected") or 0)
                  < (sm.get("k_min_usable") or sm.get("k_requested") or 0))
check("5 usable of 6 scheduled is NOT undersampled",
      undersampled({"qwen": {"k_collected": 5, "k_solicited": 6, "k_min_usable": 5}}) == [])
check("4 usable of 6 scheduled IS undersampled",
      undersampled({"qwen": {"k_collected": 4, "k_solicited": 6, "k_min_usable": 5}}) == ["qwen"])
check("6 usable of 6 is not undersampled",
      undersampled({"qwen": {"k_collected": 6, "k_solicited": 6, "k_min_usable": 5}}) == [])
check("a spec with only the old field still works",
      undersampled({"gpt": {"k_collected": 4, "k_requested": 5}}) == ["gpt"])

print("\nthe serve fingerprint fails closed")
pin = json.loads((REPO_ROOT / "record" / "cycles" / "serve-fingerprint.json").read_text())
check("the pinned endpoint is the one the round solicits",
      pin["endpoint"] == rc.LOCAL_ENDPOINT)
check("the pin names a model id", bool(pin.get("model_id")))
check("the pin disclaims what it cannot establish",
      "does_not_establish" in json.dumps(pin))

saved = rc.SERVE_FINGERPRINT_PATH
import tempfile                                                          # noqa: E402
tmp = Path(tempfile.mkdtemp()) / "fp.json"
tmp.write_text(json.dumps({"endpoint": rc.LOCAL_ENDPOINT, "model_id": "a-different-model"}))
rc.SERVE_FINGERPRINT_PATH = tmp
try:
    rc.verify_serve_fingerprint()
    check("a mismatched model id is refused", False)
except rc.Refusal:
    check("a mismatched model id is refused", True)
except Exception as e:                                                   # noqa: BLE001
    check(f"a mismatched model id raised {type(e).__name__}, not Refusal", False)

tmp.write_text(json.dumps({"endpoint": "http://127.0.0.1:9/v1/chat/completions",
                           "model_id": "qwen3.6-35b-a3b"}))
try:
    rc.verify_serve_fingerprint()
    check("a pin for a different endpoint is refused", False)
except rc.Refusal:
    check("a pin for a different endpoint is refused", True)
rc.SERVE_FINGERPRINT_PATH = saved

print("\nthe decisions that authorise all this are recorded")
d = REPO_ROOT / "record" / "decisions"
check("singleton ratification is a recorded decision",
      (d / "2026-08-08-adopt-singleton-ratification.json").is_file())
check("k=6 is a recorded decision", (d / "2026-08-08-adopt-k6-local-arm.json").is_file())
k6 = json.loads((d / "2026-08-08-adopt-k6-local-arm.json").read_text())
check("the k=6 decision states the projection's uncertainty, not just the plug-in figure",
      "95%" in k6["the_projection_and_its_uncertainty"])
check("the k=6 decision states what it does NOT fix",
      "censored" in k6["what_this_does_not_fix"])
sr = json.loads((d / "2026-08-08-adopt-singleton-ratification.json").read_text())
check("the singleton decision records agenda luck as accepted",
      any("AGENDA LUCK" in w for w in sr["known_weaknesses_accepted"]))
check("the singleton decision says no instrument implements it yet",
      "not_yet_built" in sr)

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
