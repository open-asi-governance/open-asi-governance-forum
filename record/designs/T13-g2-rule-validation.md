# G2 rule validation — the prompt-paste detector

**Status:** validation complete, 2026-08-06 · session *Capture Path* (Track B) ·
**the rule this validates is not yet implemented**

D-25 requires that a coding rule be validated against a hand-checked subset **before** it scores
anything, that the validation be committed, and that **both the rejected and the adopted rules be
published so the correction is checkable.** This document is that record.

Reproduce with `python3 tools/tests/measure_g2_overlap.py`.

---

## What the rule has to do

Refuse a capture whose "response" is actually the outbound prompt. Observed twice: D-10 in the
founding record (raw 2377–2431 duplicating the operator's message at 2319–2373), and live during
review round 01, caught only because a human recognised the content.

## The metric

Word 8-grams over normalised text (case-folded, fenced code stripped, punctuation removed,
whitespace collapsed). For prompt shingles `P` and response shingles `R`:

- **saturation** = `|P ∩ R| / |R|` — *how much of this response is prompt material*
- **coverage** = `|P ∩ R| / |P|` — *how much of the prompt appears here*

The prompt side is the **text actually sent**, not the whole committed file: the prompt files wrap
the outbound text in a `> ` blockquote surrounded by metadata and capture requirements that were
never sent. See §5.

## Rules tried, in order

### R1 — REJECTED. Refuse when coverage **and** saturation both exceed 0.5

This was the rule specified in `record/designs/T13-capture-ui-design.md` §6.1 before measurement.

**It passes a partial prompt paste.** Copying the first 30% of the prompt as the "reply" yields
saturation 1.000 — every 8-gram in the response is prompt material — but coverage only 0.306, so
the `and` suppresses the refusal:

| fraction of prompt pasted | coverage | saturation | R1 verdict |
|---|---|---|---|
| 0.05 | 0.049 | **1.000** | pass |
| 0.10 | 0.098 | **1.000** | pass |
| 0.30 | 0.306 | **1.000** | pass |
| 0.50 | 0.504 | **1.000** | refuse |

R1 is blind to any paste of less than roughly half the prompt. The failure it was written to catch
is a scroll-and-copy that misses the tail — exactly the fraction it lets through.

**Diagnosis:** the two signals measure different things and must not be conjoined. Saturation is
the paste detector. Coverage is a *quoting* measure, and heavy quoting is normal in a review.
Conjoining them lets the normal signal veto the diagnostic one.

### R2 — REJECTED. Refuse when saturation ≥ 0.6, alone

Correct on every paste, and it **refuses the one reply the project most wants to make easy to
give**:

> "The corrections to my items are faithful, no further findings."

10 words → 3 shingles, all 3 drawn from the prompt's own wording → **saturation 1.000 → REFUSED.**

`record/review-round-02-prompt.md` names that exact sentence as "a legitimate and valuable outcome
[that] will be logged as such," and ICP §6 gives negative results equal standing. A gate that
suppresses the cheapest negative result is worse than no gate.

**Diagnosis:** saturation is not a usable statistic when the denominator is a handful of shingles.

### R3 — ADOPTED. Saturation ≥ 0.6, with a floor of 50 response shingles; coverage diagnostic only

```
if   len(R) < 50            → saturation not evaluated; route to the short-response
                              warning and require the custodian's attestation
elif saturation >= 0.60     → REFUSE, naming the matched span
else                        → pass; record saturation and coverage as diagnostics
```

Coverage is **recorded and never used to refuse.**

## Validation results

Reproduce: `python3 tools/tests/measure_g2_overlap.py`

| Class | n | worst-case saturation | R3 verdict |
|---|---|---|---|
| Genuine captures vs. their own prompt | 9 | **0.030** (Gemini, round 01) | pass ✓ |
| Genuine review with the **entire** prompt appended | 2 | **0.455** | pass ✓ |
| Pure paste, any fraction ≥ 5% of the prompt | 7 | **1.000** | refuse ✓ |
| **D-10, genuine historical case** | 1 | **1.000** | refuse ✓ |
| Prompt file pasted as its own reply (synthetic) | 2 | 1.000 | refuse ✓ |
| Short legitimate reply, < 50 shingles | 4 | n/a | not refused; attested ✓ |

**Margin:** worst legitimate case 0.455 (pathological — a real review with the whole prompt
appended) against weakest paste 1.000. Separation **+0.545**.

Every real capture in the corpus carries ≥ 481 shingles; the shortest is
`review-round-02-prompt-critique/gemini-01.md` at 585 words / 481 shingles. The 50-shingle floor
sits an order of magnitude below the smallest genuine capture and well above every pathological
short case measured (3, 20, 21 shingles).

## What this validation does **not** establish

Stated so a later reader does not read more into it than it holds.

- **The threshold is under-determined, and that is fine.** Any value in roughly `[0.5, 0.9]`
  classifies all measured cases identically. 0.60 is not tuned; it sits in the middle of a wide
  flat region. Were the region narrow, the rule would be fragile and this document would say so.
- **Four of the six positives are synthetic**, constructed by the same party that chose the rule —
  the D-23 shape. The genuine D-10 case is the only positive not authored here, and it is the one
  that carries the result.
- **The sub-floor region is uncovered by design.** A paste of fewer than ~57 words passes G2. It
  trips the short-response warning and requires attestation instead. Pasting a 50-word fragment of
  a 3,000-word prompt is not the observed failure mode; pasting the whole thing is.
- **No effect here is near the margin**, so per D-28's operational rule this is a lopsided result
  of the kind that survives a noisy apparatus. It is not a fraction-of-a-bit comparison.

## §5 — an incidental provenance finding

The `prompt` anchor on every existing capture hashes the **whole prompt file**, which contains
material the model never received: `record/review-round-02-prompt.md` is metadata at lines 1–11,
the sent text as a blockquote at 15–102, and capture requirements at 104–118.

So the recorded prompt hash does not hash what was sent. It hashes a document containing what was
sent. Measured impact on this gate is negligible — worst negative moves 0.030 → 0.042 between the
two readings — so **this is a provenance-precision issue, not a gate-correctness one.** Recorded
here rather than fixed, because changing what `prompt` anchors would invalidate the hash cited by
all nine existing capture records, and superseding artifacts are the project's mechanism for that
kind of change.
