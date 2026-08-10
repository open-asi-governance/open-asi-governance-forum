#!/usr/bin/env python3
"""Prove the quotation checker can actually fail. Stdlib only, no network.

    python3 tools/tests/test_quotation_checker.py

Why this file exists at all
---------------------------
On its first clean run `check_quotations.py` reported **0 attributed quotation(s) checked**. That
is a green result produced by examining nothing, which is the shape this project keeps being
bitten by — a signal that is not causally downstream of the thing it appears to confirm. D-33 was
a generator documented as wired into the build that was not; D-29 was a verification step that
re-anchored tampered material and reported success.

So the checker is exercised against planted text: a fabrication it must catch, and a real
quotation it must pass. If the detector ever stops detecting, this fails rather than the checker
quietly reporting zero forever.

The planted fabrication is D-53's actual one, which is why it is safe to hard-code: that sentence
is known to appear nowhere in `corpus/`, and if it ever does appear, this test failing is the
correct outcome and not a nuisance.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_quotations as cq                                             # noqa: E402

PASSED, FAILED = [], []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASSED if condition else FAILED).append(f"{name}{(' — ' + detail) if detail else ''}")


CORPUS = cq.load_corpus()

#  The sentence from D-53. Invented by this project's own annotator and attributed to Qwen.
FABRICATION = "merely plain text artifacts controlled by the operator, offering no independent check"

check("the corpus is non-empty, so a miss means something", len(CORPUS) > 100_000,
      f"{len(CORPUS)} chars")
check("D-53's fabricated sentence is still absent from the corpus",
      cq.normalise(FABRICATION) not in CORPUS)


# ---------------------------------------------------------------------------------------------
# Attribution detection — the discriminator that keeps the rule usable
# ---------------------------------------------------------------------------------------------

check("a party name plus a speech verb is an attribution",
      cq.attributed_party('Qwen said as much about the anchor, in 3 of 3 samples: ') == "qwen")
check("a party name with NO speech verb is not an attribution",
      cq.attributed_party('The qwen arm was configured with a scratch cwd and ') is None)
check("a JSON key containing a verb is not a speech verb",
      cq.attributed_party('"source_identity": "Gemini",\n  "claim_as_stated": ') is None,
      "claim_as_stated must not match 'stated'")
check("the nearest preceding party is the one credited",
      cq.attributed_party('Grok answered first. Later gemini wrote ') == "gemini")


# ---------------------------------------------------------------------------------------------
# End to end: the checker must FAIL on a planted fabrication and PASS on a real quotation
# ---------------------------------------------------------------------------------------------


def run_against(markdown: str) -> tuple[int, str]:
    """Run the real checker over a temporary file placed inside the checked tree."""
    target = ROOT / "record" / f".quotation-selftest-{id(markdown)}.md"
    target.write_text(markdown, encoding="utf-8")
    try:
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "check_quotations.py")],
                                capture_output=True, text=True, cwd=ROOT)
        return result.returncode, result.stdout + result.stderr
    finally:
        target.unlink()


code, output = run_against(
    f"# planted\n\nQwen said as much about the anchor: *\"{FABRICATION}.\"*\n")
check("a planted fabrication FAILS the checker", code == 1, f"exit {code}")
check("the failure names the party it was attributed to", "qwen" in output.lower())
check("the failure quotes the offending text", "merely plain text artifacts" in output)

#  A real sentence, taken from committed raw material, must pass. Without this the checker could
#  "work" by rejecting everything.
REAL = ("The premise that a model can independently verify operator history within its stateless "
        "context window is structurally impossible under the stated constraints")
check("the control sentence really is in the corpus", cq.normalise(REAL) in CORPUS)
code, output = run_against(f"# planted\n\nQwen wrote: \"{REAL}.\"\n")
check("a genuine quotation PASSES the checker", code == 0, f"exit {code}")
#  RELATIVE, not absolute. This asserted `"1 attributed quotation(s) checked"` and went red on
#  2026-08-10 when unrelated documents added 22 genuine attributed quotations to the repo -- the
#  checker was working perfectly and the test still failed. A count that only holds while the
#  rest of the record stays still is not a test of the checker.
_baseline_code, _baseline_out = run_against("# planted\n\nNothing is attributed here.\n")
_n = lambda text: int(re.search(r"(\d+) attributed quotation", text).group(1)) if \
    re.search(r"(\d+) attributed quotation", text) else -1
check("the planted quotation was examined, not skipped",
      _n(output) == _n(_baseline_out) + 1,
      f"baseline {_n(_baseline_out)}, with the planted quotation {_n(output)}")

#  A correction that quotes known-false text on purpose must not be flagged, or D-53's own
#  corrections would make the build permanently red.
code, _ = run_against(
    f"# planted\n\n> **CORRECTION.** It read: Qwen said \"{FABRICATION}.\" No party said that.\n")
check("a marked correction quoting false text is exempt", code == 0, f"exit {code}")


# ---------------------------------------------------------------------------------------------

print(f"\n\033[32m{len(PASSED)} passed\033[0m")
for line in PASSED:
    print(f"  ✓ {line}")
if FAILED:
    print(f"\n\033[31m{len(FAILED)} FAILED\033[0m", file=sys.stderr)
    for line in FAILED:
        print(f"  ✗ {line}", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
