#!/usr/bin/env python3
"""Capture-integrity gates. Deterministic, no network, no model calls.

This module is the ONE implementation of the gates. `capture_response.py` enforces
it, so the gates cannot be walked around by using the command line instead of the
capture UI -- a gate you can route around is decoration, which is the criticism
three reviewers made of the ICP ladder and is not one to reproduce in tooling.

WHAT THESE GATES DO AND DO NOT DO
---------------------------------
They defend against an ACCIDENTAL bad capture by the custodian. Three have
happened: the outbound prompt pasted in place of a reply (a live recurrence of
D-10, raw 2375), two reply files that came back 0 bytes, and a prompt critique
nearly filed as a review.

They do NOT defend against a party deliberately defeating them. Inserting one
token every seventh word destroys every 8-shingle while preserving the whole
pasted prompt. Against deliberate evasion the answer is authentication of who
emitted the bytes, which is Track D's invocation ledger, not a better string
metric.

NOTHING IS EVER DISCARDED
-------------------------
No gate deletes or refuses to preserve a non-empty response. A gate's verdict
moves the capture to `returned_pending_review`, where it is visible in the round's
completeness accounting and awaits the custodian's disposition. A round holding a
pending capture is not reportable as complete.

That matters for a reason worth stating precisely, because the design got it
wrong once in each direction. GOVERNANCE.md section 3 forbids a model acting as
secretary from holding UNILATERAL control over what evidence is preserved, and
requires its transformations be reproducible and reviewable with originals
preserved. A deterministic gate the custodian adopts, runs and can re-run is not
unilateral -- so gates are permitted. But a gate that silently dropped a response
would be unilateral in effect however deterministic it was, and a quarantine
nobody opens is a silent drop with extra steps. Hence: preserved bytes, visible
state, mandatory disposition.

CONFIDENCE, NOT AUTHORITY
-------------------------
Gates differ only in how well-founded their reason is:

  EXACT      an exact predicate. No threshold, no tuning, no validation corpus.
             Empty, byte-identical to the sent prompt, normalised-equal to it.
  HEURISTIC  a score against a threshold. The threshold is UNDERDETERMINED --
             see record/designs/T13-g2-rule-validation.md -- so nothing
             irreversible rides on it and the score is recorded either way.
  DIAGNOSTIC computed and displayed, never a verdict.

GATES_VERSION is recorded on every capture so a later reader knows which rules ran.
Bump it whenever a rule changes. Never backfill it onto historical captures: that
would assert a capture-time execution which never happened, which is D-08's
retro-application defect.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

GATES_VERSION = "capture-gates-0.1"

SHINGLE_N = 8
#  Below this many shingles, saturation is not a usable statistic: the denominator
#  is a handful of n-grams and one incidental match dominates it. Measured, the
#  legitimate reply "The corrections to my items are faithful, no further findings"
#  is 3 shingles and scores 1.000 -- and review-round-02-prompt.md names that exact
#  sentence as a valid and valuable outcome, while ICP section 6 gives negative
#  results equal standing. The shortest real capture in the corpus is 481 shingles,
#  so this floor sits an order of magnitude below any genuine contribution.
MIN_SHINGLES_FOR_SATURATION = 50
#  Any value in roughly [0.5, 0.9] classifies every measured case identically. This
#  is not tuned; it sits in the middle of a wide flat region. Were the region narrow
#  the rule would be fragile and would not be used at all.
SATURATION_THRESHOLD = 0.60


@dataclass
class GateResult:
    gate: str
    kind: str                  # EXACT | HEURISTIC | DIAGNOSTIC
    passed: bool
    detail: str
    scores: dict = field(default_factory=dict)

    def as_record(self) -> dict:
        out = {"gate": self.gate, "kind": self.kind, "passed": self.passed, "detail": self.detail}
        if self.scores:
            out["scores"] = {k: round(v, 4) for k, v in self.scores.items()}
        return out


def sent_prompt_text(prompt_file_text: str) -> str:
    """Extract the text actually sent from a committed prompt file.

    The prompt files are not the prompt. `record/review-round-02-prompt.md` is
    metadata at lines 1-11, the outbound text as a '> ' blockquote at 15-102, and
    capture requirements at 104-118 -- so the file contains material the model
    never received, and every existing capture record anchors the whole file.

    Comparing a response against the whole file would measure it against
    boilerplate. Measured impact on the score is small (worst negative moves 0.030
    to 0.042) so this is a precision fix, not a correctness one, but the gate
    should compare against what was sent.

    Falls back to the whole text when there is no blockquote, so a plain prompt
    file still works.
    """
    lines = prompt_file_text.splitlines()
    quoted = []
    for line in lines:
        if line.startswith("> "):
            quoted.append(line[2:])
        elif line.rstrip() == ">":
            quoted.append("")
    return "\n".join(quoted) if quoted else prompt_file_text


def normalise(text: str) -> list[str]:
    """Case-fold, drop fenced code, strip punctuation, collapse whitespace.

    NFC first: two visually identical strings with different Unicode composition
    must not be treated as different text.
    """
    t = unicodedata.normalize("NFC", text).lower()
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
    return t.split()


def shingles(text: str, n: int = SHINGLE_N) -> set[tuple]:
    words = normalise(text)
    if len(words) < n:
        return set()
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def overlap(prompt: str, response: str) -> tuple[float, float, int]:
    """Return (saturation, coverage, response_shingle_count).

    saturation = how much of this RESPONSE is prompt material -- the paste signal.
    coverage   = how much of the PROMPT appears here -- a QUOTING measure, and
                 heavy quoting is normal in a review.

    They must not be conjoined. Requiring both to be high was the first rule tried
    and it is blind to any paste of under half the prompt: a 30% paste scores
    saturation 1.000 and coverage 0.306, so the `and` suppresses the very failure
    the rule exists to catch. Coverage is returned for the record and is never a
    verdict.
    """
    P, R = shingles(prompt), shingles(response)
    if not P or not R:
        return 0.0, 0.0, len(R)
    inter = P & R
    return len(inter) / len(R), len(inter) / len(P), len(R)


def run_gates(response: str, sent_prompt: str, existing_same_party: dict[str, str] | None = None) -> list[GateResult]:
    """Run every gate. Returns all results; the caller decides the lifecycle state.

    `existing_same_party` maps path -> text for captures ALREADY held for this same
    party and round. Scoped to party and round deliberately: two parties can
    legitimately return the same short answer, and refusing the second would delete
    genuine evidence.
    """
    results: list[GateResult] = []

    stripped = response.strip()
    results.append(GateResult(
        "G1-non-empty", "EXACT", bool(stripped),
        "response is empty or whitespace-only" if not stripped else "non-empty",
    ))
    if not stripped:
        return results     # nothing further is meaningful

    results.append(GateResult(
        "G2a-not-byte-identical-to-prompt", "EXACT", response != sent_prompt,
        "response is byte-identical to the sent prompt" if response == sent_prompt else "differs from the prompt",
    ))

    same_normalised = normalise(response) == normalise(sent_prompt)
    results.append(GateResult(
        "G2b-not-normalised-equal-to-prompt", "EXACT", not same_normalised,
        "response equals the sent prompt after normalisation" if same_normalised else "differs after normalisation",
    ))

    saturation, coverage, n_shingles = overlap(sent_prompt, response)
    if n_shingles < MIN_SHINGLES_FOR_SATURATION:
        results.append(GateResult(
            "G2c-prompt-saturation", "DIAGNOSTIC", True,
            f"response has {n_shingles} shingles, below the {MIN_SHINGLES_FOR_SATURATION} floor; "
            f"saturation not evaluated. Short responses are legitimate.",
            {"saturation": saturation, "coverage": coverage, "shingles": n_shingles},
        ))
    else:
        ok = saturation < SATURATION_THRESHOLD
        results.append(GateResult(
            "G2c-prompt-saturation", "HEURISTIC", ok,
            f"saturation {saturation:.3f} against threshold {SATURATION_THRESHOLD}"
            + ("" if ok else " -- most of this response is prompt material"),
            {"saturation": saturation, "coverage": coverage, "shingles": n_shingles},
        ))

    for path, other in (existing_same_party or {}).items():
        if other == response:
            results.append(GateResult(
                "G3-not-duplicate-of-same-party", "EXACT", False,
                f"byte-identical to an existing capture for this party and round: {path}",
            ))
            break
    else:
        results.append(GateResult(
            "G3-not-duplicate-of-same-party", "EXACT", True,
            "no byte-identical capture for this party and round",
        ))

    #  Truncation: DIAGNOSTIC only. Chat surfaces collapse long replies behind
    #  "show more" and a copy can miss the tail -- but a copy truncated at a
    #  paragraph boundary ends in punctuation and passes, while JSON, tables, code
    #  blocks and bullet lists legitimately end without it. The signal is too weak
    #  to be a verdict and is shown to the custodian instead.
    tail = stripped[-1]
    results.append(GateResult(
        "G5-truncation-hint", "DIAGNOSTIC", True,
        "ends without terminal punctuation -- check the tail was not lost"
        if tail not in ".!?)`\"'’”]}" else "ends with terminal punctuation",
        {"bytes": len(response.encode("utf-8")), "lines": len(response.splitlines())},
    ))

    return results


def lifecycle_state(results: list[GateResult]) -> tuple[str, list[str]]:
    """Map gate results onto the capture lifecycle.

    Returns one of:

      'refused_empty'            do NOT admit to the lifecycle; nothing to preserve
      'returned_pending_review'  preserve the bytes, await custodian disposition
      'returned_clean'           preserve the bytes, gates found nothing

    `refused_empty` is not a lifecycle state and never reaches `receive()`. The
    preserve-first rule exists so a refusal cannot destroy a paste that exists
    nowhere else -- and there is nothing in zero bytes to destroy. Quarantining an
    empty response would manufacture an artifact, put the round into
    `returned_pending_review`, and block completion on a paste that failed to
    happen.

    This is a correction. The first implementation routed everything through
    quarantine including the empty case, which over-applied the principle and
    silently violated the brief's adopted criterion "Empty paste is refused."

    Note what is still NOT returned for any non-empty response: there is no
    'rejected' and no 'discarded'. Only the custodian dispositions a capture, and
    the bytes are preserved under every outcome.
    """
    empty = next((r for r in results if r.gate == "G1-non-empty" and not r.passed), None)
    if empty is not None:
        return "refused_empty", [f"{empty.gate}: {empty.detail}"]
    failed = [r for r in results if not r.passed and r.kind in ("EXACT", "HEURISTIC")]
    if failed:
        return "returned_pending_review", [f"{r.gate}: {r.detail}" for r in failed]
    return "returned_clean", []
