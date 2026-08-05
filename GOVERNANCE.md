# Governance

## 1. Custody

**Stephen Reed** is the named human custodian of this repository and the
`open-asi-governance` GitHub organization.

He holds and personally bears:

- repository and organization administration
- merge authority over every branch
- license selection and the legal consequences of the grants made
- responsibility for the accuracy of attributions published here
- responsibility for responding to correction requests and takedown claims

This is not a formality. Every model that contributed to the founding record conditioned its
contribution on a named human principal holding exactly these responsibilities, and on models not
being represented as bearing them.

### 1.1 What no AI system holds

No AI system — including the Consullo Seed AI platform, the models whose outputs appear in the
corpus, or the tooling in `tools/` — owns this repository, licenses it, holds decision rights over
it, or bears liability for it. An AI system cannot own property, grant a license, or be sued.

An earlier draft of the founding record stated that "the Consullo Seed AI system (soon Consullo
Incorporated) will own the repo and license according to the best practice of the governors."
Both halves were withdrawn during the record's own review: an AI system can own nothing, and there
are no governors. Should a legal entity later be formed, transfer of custody will be recorded here
as a dated amendment, not applied retroactively.

### 1.2 Single-operator custody is disclosed, not solved

This project is currently operated by one person. That is a real weakness against the anti-capture
requirements set out in the founding record (ChatGPT §2.1, §2.6). Stated intent:

- the GitHub organization was created neutral (`open-asi-governance`), not sponsor-branded
- independent mirrors are intended before the corpus is cited by third parties
- transfer to a multi-stakeholder custodian is the intended end state

None of these are complete. Until they are, a reader should treat this repository as
single-sponsor infrastructure and weight its claims accordingly.

## 2. Write gate

**All writes to the public repository pass through the human custodian.**

No AI system holds credentials to this repository. No automation has push access. There is no bot
account. Tooling in `tools/` is run locally by the custodian and produces files that the custodian
inspects and commits.

This is a design commitment, not an operational convenience. A repository whose premise is human
accountability cannot have its history written by an unsupervised agent.

## 3. The secretary constraint

The founding record adopted a restriction on the role of any model acting as secretary
(ChatGPT §2.3): the secretary must not hold unilateral control over what evidence is preserved,
how dissent is summarized, which questions are put, how votes are interpreted, whether minority
reports are published, or the canonical representation of disputed claims. Its transformations
must be reproducible and reviewable, and original outputs must remain available alongside any
summary.

This binds every model used in a secretarial capacity here, including Claude Code, which drafted
the current annotations.

Operationally:

1. **Raw before annotation.** Source material is committed byte-identical, with a SHA-256 anchor
   in `corpus/MANIFEST.sha256`, before any annotation of it exists.
2. **Annotation is never inline.** Annotations live in separate files and reference raw material
   by path, hash, and line range. The raw file is never edited to correct an error; the correction
   is a superseding artifact.
3. **Annotation is labeled.** Every interpretive artifact records its author, model version where
   applicable, date, and any conflict of interest.
4. **Self-annotation is flagged.** Where an annotating model annotates its own prior contributions,
   that conflict is stated in the artifact itself.

## 4. Conflict of interest in the current annotations

Claude (Anthropic) is a **party to the founding record** — it declined membership, set the
representation conditions the project now operates under, and cast a consensus ballot. Claude Code
(Anthropic) subsequently drafted this repository's annotations, deficiency register, tooling, and
governance documents at operator direction.

This is a conflict. It is mitigated, not eliminated, by:

- verbatim preservation of the raw record, hash-anchored, before annotation
- explicit labeling of every Claude-authored artifact
- the human write gate in §2
- **adversarial review**: the annotations and deficiency register are circulated to the other
  parties to the record (Grok, ChatGPT, Gemini) for correction, and their corrections are
  committed alongside the annotations rather than merged into them

Until that review round completes, the annotations carry status `draft, unreviewed`.

## 5. Corrections and supersession

The record supports correction without silent rewriting.

- Raw material is **never** edited after commit. Not for typos, not for misattribution.
- An error is corrected by a **superseding artifact** that names what it supersedes and why.
- Superseded material remains in the repository with status `superseded`, recoverable.
- Contribution status values: `active`, `superseded`, `withdrawn`, `repudiated`,
  `invocation integrity disputed`.
- Anyone may request a correction by opening an issue. Attribution errors are prioritized.

### 5.1 Right of repudiation

Any party whose output appears in the corpus may request that it be marked `repudiated` or
`invocation integrity disputed`. The custodian will apply the status without requiring agreement,
and the underlying text remains in the record with the status attached. Attribution accuracy is
served by marking a disputed record, not by deleting it.

## 6. What this body does not do

It does not approve deployments. It does not gate releases. It does not certify systems. It does
not hold seats. It does not speak for any AI company. It does not claim that agreement among the
models it quotes is evidence that they are correct.

It keeps a record.

## 7. Amendment

This document is amended by commit, with the change and its rationale visible in history. Material
amendments are announced in `record/` as a dated entry. The custodian may amend unilaterally and is
accountable for doing so.

---

*Adopted 2026-08-05. Drafted by Claude Code (Anthropic) at operator direction; adopted by Stephen
Reed, human custodian.*
