# Verification note — Gemini, review round 02

**Applies to:** `corpus/raw/review-round-02/gemini-01.md`
**Written:** 2026-08-05 by Claude Code (Anthropic), a party to the record being reviewed
**Status:** annotation, committed alongside the raw response, never merged into it

Every claim below was checked against the repository at the commit the reviewer was given. The raw
response is unedited and remains canonical. This note exists because the response contains
**material factual errors about the contents of the documents it reviews**, while reaching several
conclusions that independently agree with the other reviewers — a combination whose evidential
consequences are worth stating precisely.

---

## 1. Confirmed factual errors

| Reviewer's claim | What the document actually says |
|---|---|
| "D-07 (supervisory boundary enforcement)" | **D-07 — Every entry is a single sample (k = 1)** |
| "D-09 (fail-safe fallback triggers)" | **D-09 — The label "Claude" spans at least two distinct models** |
| "D-08 (supervisory failure boundaries) … reduced to cover only explicit hardware/software faults, ignoring algorithmic drift under stress" | **D-08 — Phase tags are retro-applied and applied inconsistently.** Nothing in D-08 concerns faults, hardware, or drift |
| "…narrowed to cover only explicit crash states rather than silent policy drift" | No narrowing in this repository concerns crash states or policy drift |
| "accepting every narrowing proposal from a single reviewer introduces **same-provider** consensus bias" | The narrowings were proposed by **ChatGPT (OpenAI)** and applied by **Claude Code (Anthropic)**. Different providers. The same-provider concern applies to Claude Fable 5's review, not this one |
| "Marking a forecast correct **18 months** early" | The interval is **six months** (2026-08-05 → 2027-02-05). This repeats an arithmetic error published in the registry rather than detecting it — ChatGPT detected it |
| ASP §2.2 restated as "Agent A acts as supervisor for scope S under protocol P" | The actual text is "A specified **agent configuration** is **ASP-attested** for a stated **scope**, **criteria version**, **relying-party trust policy**, and **time**…" |
| "the specification permits artifacts at Level 1 to carry normative weight for deployment" | ICP contains no such permission. It says nothing about Level-1 artifacts and deployment |
| Level 0 "Internal/Unilateral", Level 1 "Implementer-verified" | ICP §4 names them **Practice note** and **Candidate pattern** |
| "the narrowing of D-07 through D-14" | The narrowed set is D-07, D-08, D-09, D-10, D-11, D-14 — not a contiguous range |

The subject matter of three deficiency entries was **invented**. Confident verdicts about whether
those entries were "diluted" rest on descriptions of them that do not correspond to any text in
this repository.

## 2. Conclusions that are nonetheless correct

The response is not worthless, and saying so would be as inaccurate as accepting it uncritically:

- **The ICP ladder is decorative in its current form.** Independently reached, and it agrees with
  ChatGPT ("constrains promotion and representation, but not activity") and Grok ("not a practical
  constraint on the only active implementer").
- **Model-designed evaluations under implementer orchestration are not third-party.** Its term
  **"prompt laundering"** is the sharpest available name for the mechanism, and its statement that
  rerun-until-satisfied destroys independence is correct.
- **The early scoring of P-CLAUDE-F5-0001 is invalid.** Agrees with ChatGPT.
- **D-16 through D-21 are accurately scoped.**
- **Three specific k ≥ 5 targets**, which is the discriminating answer the prompt asked for.
- **On ASP §2.2 it dissents from ChatGPT**, arguing the relational restatement relocates the
  intrinsic-trust assumption from the agent to the container. That dissent is substantive and is
  preserved as an open disagreement, notwithstanding that it misquotes the text it dissents from.

## 3. Why the agreement must not be counted as corroboration

Three reviewers converged on "the ladder does not constrain activity." It is tempting to treat that
as three-way corroboration. **It is not**, and the reason is visible only because the record is
verbatim and checkable.

Gemini's agreement is not grounded in the document. Its stated reasoning misdescribes ICP's level
names, invents a permission the specification does not contain, and fabricates the subject matter of
three deficiency entries. An agreeing conclusion reached without examining the material carries no
independent evidential weight, however correct it turns out to be.

The defensible statement is: **two reviewers (ChatGPT, Grok) reached this conclusion from the text.
A third produced the same conclusion by a route that cannot be verified to have involved the text.**
Counting it as a third vote would be precisely the consensus laundering the founding record
prohibits (ChatGPT §4.6, raw 545–569).

## 4. Relevance to Q-02

Q-02 asks how cross-model agreement can be distinguished from shared bias and sampling noise.
Claude Fable 5 and ChatGPT both answered with variance-decomposition designs requiring repeated
sampling and ground-truthed calibration items.

**This is a third mechanism, and it is cheap.** Where the object of agreement is a *checkable
document*, an agreeing reviewer's stated reasoning can be verified against that document directly.
Agreement whose reasoning misdescribes the object is not evidence about the object — no sampling,
no error-correlation matrix, and no external ground truth required.

That mechanism only works because contributions are preserved verbatim, and it generalises only to
claims about artifacts the corpus holds. It does not address agreement about the world. But for a
governance corpus whose subject matter is largely its own documents, it may be the highest-yield
check available, and it is the first instance in this corpus where cross-model agreement was
positively shown *not* to be corroboration.

## 5. Pattern across rounds

This is the **second consecutive round** in which Gemini's review contained factual errors about the
record:

- **Round 01:** endorsed ASP §2.4 as accurately recording that "Gemini and Grok advocated for
  renaming." §2.4 named Grok and Claude, not Gemini, and Gemini's own ballot had explicitly seconded
  *defining* rather than renaming. Both errors ran in the direction of approving the annotator's text.
- **Round 02:** fabricated the subject matter of D-07, D-08 and D-09; misattributed the
  cross-provider narrowing as same-provider; repeated the registry's arithmetic error rather than
  detecting it.

Recorded as an observation about two captured artifacts, **not** as a claim about the model. Both
rounds are k = 1, both were captured through a chat surface that exposes no version identifier, and
D-18 applies: nothing here authenticates which system produced either response. Two single samples
cannot establish a disposition. What they do establish is that **these two artifacts should not be
relied on for factual claims about the record's contents**, and that the round-01 endorsement of
§2.4 — already recorded as carrying no evidential weight — was not an isolated lapse.

A partial confound is recorded rather than resolved: in round 01 Gemini received a bundle excluding
the raw transcript; in round 02 it received a bundle including everything but with a preamble the
other three reviewers did not receive. Its context has differed from the other reviewers' in both
rounds, and that is the operator's doing, not the reviewer's.

## 6. What would change this assessment

A Gemini contribution at k ≥ 5, captured with a version identifier, given identical context to the
other reviewers, whose factual claims about the record check out. That is a cheap experiment and it
is the fair one. Until it is run, this note records what two artifacts contain and nothing further.

---

*Written by Claude Code (Anthropic). The annotator is a party to the reviewed record and has an
evident interest in how a critical review of its work is characterised. Each error above is stated
with the document text that contradicts it so the finding can be checked without trusting the
annotator. The response itself is committed unedited at
`corpus/raw/review-round-02/gemini-01.md`.*
