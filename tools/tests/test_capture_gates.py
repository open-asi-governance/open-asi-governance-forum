#!/usr/bin/env python3
"""Validate the capture gates against the corpus. Stdlib only; no test framework.

    python3 tools/tests/test_capture_gates.py

D-25 requires a coding rule be validated against a hand-checked subset before it
scores anything, and that the validation be committed. This is that validation,
and it runs against the real corpus rather than against fixtures, so it fails if
the corpus changes in a way the rules did not anticipate.

Every NEGATIVE case is a real captured contribution. Every POSITIVE case is either
a real historical failure (D-10) or is constructed and LABELLED SYNTHETIC. Four of
the positives are synthetic and were authored by the same party that chose the
rules, which is the D-23 shape; the D-10 case is the only positive this design did
not author, and it is the one that carries the result.
"""

from __future__ import annotations

import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from capture_gates import (                                    # noqa: E402
    GATES_VERSION, MIN_SHINGLES_FOR_SATURATION, SATURATION_THRESHOLD,
    lifecycle_state, overlap, run_gates, sent_prompt_text, shingles,
)

PASSED, FAILED = [], []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASSED if condition else FAILED).append(f"{name}{(' — ' + detail) if detail else ''}")


def real_captures() -> list[tuple[str, str, str]]:
    """(label, response_text, sent_prompt_text) for every committed contribution."""
    out = []
    for f in sorted(glob.glob(str(ROOT / "corpus/artifacts/*/*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if d.get("artifact_type") != "contribution":
            continue
        resp = (ROOT / d["raw"]["path"]).read_text(encoding="utf-8")
        prompt = sent_prompt_text((ROOT / d["prompt"]["path"]).read_text(encoding="utf-8"))
        out.append((f"{d['round']}/{d['contributor']['identity']}", resp, prompt))
    return out


# ---------------------------------------------------------------- negatives --
CAPTURES = real_captures()
check("corpus has captures to validate against", len(CAPTURES) >= 9, f"found {len(CAPTURES)}")

for label, resp, prompt in CAPTURES:
    state, reasons = lifecycle_state(run_gates(resp, prompt))
    check(f"NEG genuine capture passes clean: {label}", state == "returned_clean", "; ".join(reasons))

# ---------------------------------------------------------------- positives --
_, _, P2 = next((c for c in CAPTURES if "review-round-02/" in c[0]), (None, None, None))

# POS-real: D-10. Raw 2377-2431 is a verbatim duplicate of the operator's own
# message at 2319-2373, committed under a header attributing it to Grok. The only
# positive in this suite that this design did not author.
TR = (ROOT / "corpus/raw/initial-transcript.txt").read_text(encoding="utf-8").splitlines()
d10_prompt, d10_response = "\n".join(TR[2318:2373]), "\n".join(TR[2376:2431])
state, reasons = lifecycle_state(run_gates(d10_response, d10_prompt))
check("POS-real D-10 duplicate is held for review", state == "returned_pending_review", "; ".join(reasons))

# POS-syn: the exact observed failures, constructed.
# Empty is REFUSED, not quarantined -- the brief's adopted criterion A3. There is
# nothing in zero bytes to preserve, and admitting it would manufacture an artifact
# and block round completion on a paste that failed to happen.
for name, resp in [("empty response", ""), ("whitespace-only response", "   \n\t  \n")]:
    results = run_gates(resp, P2)
    state, _ = lifecycle_state(results)
    check(f"POS-syn {name} is REFUSED, not quarantined", state == "refused_empty", state)
    check(f"POS-syn {name} fires G1", "G1-non-empty" in [r.gate for r in results if not r.passed])

results = run_gates(P2, P2)
state, _ = lifecycle_state(results)
fired = [r.gate for r in results if not r.passed]
check("POS-syn prompt pasted verbatim is held for review", state == "returned_pending_review")
check("POS-syn prompt pasted verbatim fires G2a",
      "G2a-not-byte-identical-to-prompt" in fired, f"fired: {fired}")

# POS-syn: partial paste. The rule this replaced was blind to these -- it required
# coverage AND saturation to be high, and a 30% paste has coverage 0.306.
for fraction in (0.10, 0.30, 0.50):
    words = P2.split()
    partial = " ".join(words[:int(len(words) * fraction)])
    state, _ = lifecycle_state(run_gates(partial, P2))
    check(f"POS-syn {int(fraction*100)}% partial paste is held for review",
          state == "returned_pending_review")

# ------------------------------------------------------- the false positives --
# Each of these is a LEGITIMATE response that an earlier rule refused. They are the
# reason the rules are what they are, and a regression here silently suppresses
# real contributions.

# review-round-02-prompt.md names this exact sentence as a legitimate and valuable
# outcome; ICP section 6 gives negative results equal standing. Saturation 1.000 on
# 3 shingles -- caught only by the floor.
short_legit = "The corrections to my items are faithful, no further findings."
state, reasons = lifecycle_state(run_gates(short_legit, P2))
check("FP-guard short 'no further findings' reply passes", state == "returned_clean", "; ".join(reasons))
check("FP-guard that reply is genuinely below the floor",
      len(shingles(short_legit)) < MIN_SHINGLES_FOR_SATURATION)

# A real review with the ENTIRE prompt appended: coverage 1.000, but the genuine
# content dilutes saturation to well under threshold.
heaviest = max(CAPTURES, key=lambda c: overlap(c[2], c[1])[0])
padded = heaviest[1] + "\n\n" + P2
sat, cov, _ = overlap(P2, padded)
state, _ = lifecycle_state(run_gates(padded, P2))
check("FP-guard review + entire prompt appended still passes",
      state == "returned_clean", f"saturation {sat:.3f}, coverage {cov:.3f}")

# ------------------------------------------------------------ same-party dup --
label, resp, prompt = CAPTURES[0]
state, _ = lifecycle_state(run_gates(resp, prompt, existing_same_party={"prior.md": resp}))
check("duplicate for the SAME party is held for review", state == "returned_pending_review")
other = next(c for c in CAPTURES if c[1] != resp)
state, _ = lifecycle_state(run_gates(other[1], other[2], existing_same_party={"prior.md": resp}))
check("a DIFFERENT response for the same party still passes", state == "returned_clean")

# ---------------------------------------------------------------- invariants --
check("no NON-EMPTY response can be discarded: only preserving states are reachable",
      {lifecycle_state(run_gates(r, p))[0] for _, r, p in CAPTURES} <= {"returned_clean", "returned_pending_review"})
check("refused_empty is reachable ONLY for empty content",
      lifecycle_state(run_gates("", P2))[0] == "refused_empty"
      and lifecycle_state(run_gates("a" * 5000, P2))[0] != "refused_empty")
check("sent_prompt_text strips the blockquote",
      "> " not in sent_prompt_text((ROOT / "record/review-round-02-prompt.md").read_text(encoding="utf-8"))[:400])
check("sent_prompt_text falls back when there is no blockquote",
      sent_prompt_text("plain prompt, no quoting") == "plain prompt, no quoting")

# --------------------------------------------------------------------- report --
print(f"gates {GATES_VERSION}  floor={MIN_SHINGLES_FOR_SATURATION}  threshold={SATURATION_THRESHOLD}")
print(f"{len(PASSED)} passed, {len(FAILED)} failed")
for f in FAILED:
    print(f"  FAIL  {f}")
sys.exit(1 if FAILED else 0)
