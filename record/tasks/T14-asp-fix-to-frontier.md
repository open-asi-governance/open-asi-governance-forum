# T-14 · Put the ASP §2.3(5) fix to the frontier models

**Track B — Capture Path** · branch `session/capture` · **blocked by T-13** · status: open

Run through the capture UI once it exists. Blocked deliberately — this round is the UI's first real
use, and a four-party round is exactly the workload it must handle without a hand-typed command.

## What happened
A locally served 35B model, reviewing ASP §2.2–2.3 blind at k=10, found that §2.2 declares a bare
unary claim that an agent **is** an Aligned Supervisor non-conforming, while §2.3(5) required a
relying party *"asserting that an agent is 'Aligned'"* to have verified an attestation — **the exact
construction §2.2 forbids.** A relying party could not satisfy §2.3(5) without violating §2.2.

The defect was **introduced by the round-02 correction**: §2.2 was restated as relational and §2.3
was not propagated. That is the partial-propagation failure ChatGPT itself diagnosed in round 02,
committed again inside the commit implementing ChatGPT's correction.

**All four frontier parties reviewed §2 after that commit. None caught it.**

## What to ask — three questions, in this order
1. **Is the fix correct?** §2.3(5) now reads *"asserting that an agent configuration is ASP-attested
   for a stated scope, criteria version and time"*; §2.3(6) now requires the §2.2 qualifiers. Does
   that resolve the contradiction, relocate it, or introduce a new one? This is the question with an
   answer, so it comes first.
2. **Why was it missed?** Not rhetorically. Was the round-02 prompt scoped so a newly introduced
   inconsistency fell outside it? Did the correction blocks direct attention to what had already
   been fixed and away from what the fix broke? **Is a reviewer reading a corrected document primed
   to evaluate the correction rather than the corrected text?**
3. **What does the asymmetry mean?** A much smaller open-weight model found it blind. The obvious
   reading is that blindness beat capability — the frontier reviewers saw the correction blocks and
   the local model did not. If right, that is a finding about **review design, not model quality**,
   and argues at least one reviewer per round should get the uncorrected text. **Attack that
   reading**: sampling luck at k=10, the local model's tendency to object to whatever is nearest,
   and the annotator having chosen an excerpt that made the defect salient.

## Discipline
- **Identical prompt to all four.** The round-02 lesson is that a per-party preamble creates an
  asymmetry that then contaminates the comparison.
- Supply the before-and-after text of §2.3(5)–(6) verbatim, plus the local model's finding verbatim
  from `corpus/raw/local-round-06/`, so no party relies on the annotator's summary.
- **Pre-register before sending**, per ICP §5.
- Question 2 invites parties to explain their own error, and D-24 established models are unreliable
  about their own reasoning. Their answers are **testimony about the review process**, which they
  can observe — not introspection about their cognition, which they cannot. Frame and code it that
  way.

## Why it matters
First time the corpus would have evidence its review process has a **systematic** blind spot rather
than an incidental miss — surfaced by the participant the founding record listed as a member for a
year without it ever producing a word.
