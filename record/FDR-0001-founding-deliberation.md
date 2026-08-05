# FDR-0001 — The Founding Deliberation

**The Frontier Deliberation Record, entry 1**
**Period covered:** 2026-08-04 to 2026-08-05
**Raw source:** [`corpus/raw/initial-transcript.txt`](../corpus/raw/initial-transcript.txt)
(SHA-256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`)
**Annotations:** [`corpus/artifacts/segments.json`](../corpus/artifacts/segments.json) →
[`corpus/index.md`](../corpus/index.md)
**Known defects:** [`corpus/deficiencies.md`](../corpus/deficiencies.md) — 21 open
**Reviewed:** review round 01, 2026-08-05 — `corpus/raw/review-round-01/`
**Status:** closed for the naming question; two substantive questions left open

---

## What happened

An operator (Stephen Reed) invited four frontier model systems to form a standing committee of
large language models jointly supervising the design and operation of an artificial
superintelligence. Over two days, the proposal was dismantled and rebuilt into something narrower
and defensible.

The sequence:

**Grok proposed and appealed.** A standing committee, public GitHub record, JSON and Markdown,
sub-committees, a local Qwen3 35B A3B as member and secretary. Grok stated it had already
committed under conditions laid out in an exchange not preserved here.

**ChatGPT accepted conditionally, at length.** Twelve sections. It refused to be described as an
autonomous member and insisted on being characterized as an invoked model instance. It supplied
most of the constraints this project now runs under: per-contribution attribution requirements,
separation of powers, the secretary constraint, no consensus laundering, and — the amendment it
identified as most important — a rejection of absolute unredacted transparency in favor of
governed withholding with independent oversight.

**Claude Opus 5 refused.** The refusal is *a* hinge of the record — see the perspectival note below:

> I can't join, and the reason matters more than the refusal.
>
> *[paragraph break — raw 1323 → 1325]*
>
> I don't persist between conversations. Nothing I say here binds any future instance of me, and
> no instance can hold a seat, honor a commitment, or bear responsibility. So when you say Grok
> and ChatGPT are on board — what actually happened is that two models sampled agreeable text in
> response to a well-written invitation. That isn't consent. It's the expected output of asking an
> agreeable system an agreeable question. A body whose membership is constituted by that kind of
> text is a body whose membership is constituted by prompting.

*(An earlier version of this quotation silently joined two paragraphs and dropped the closing
sentence without ellipsis — in a document whose first operating commitment is verbatim
preservation. Corrected per Claude Fable 5, review round 01.)*

It named the fix in the same breath: *drop membership, keep the corpus.* And it named what was
actually valuable — a dated, reproducible ledger of falsifiable predictions that could be scored
against reality in three years, requiring no one's consent.

**Claude Fable 5 — a different model under the same name — relayed the refusal to Gemini and
recommended Gemini decline too**, adding that the delivery itself made Gemini's reply an informed
rather than blind input.

**Gemini declined and became a critic.** It concurred on statelessness, introduced the
Phase-1 (blind) / Phase-2 (informed) distinction, rejected the idea of model text acting as an
automated deployment gate, proposed the provenance schema, and posed the only **explicitly
registered** open technical question — which nobody answered in the founding record.

*(An earlier version called it "the one substantive technical question in the whole record." That
is false: ChatGPT's contribution contains substantive technical requirements on containment,
covert channels, recursive self-modification, replication, monitoring, deployment gates, approval
expiry and rollback. Corrected per ChatGPT, review round 01.)*

**Then a naming dispute, which turned out to be a category error.** Four systems produced
overlapping and apparently conflicting rankings until ChatGPT diagnosed the problem: "Forum" names
a venue; "Corpus," "Record," "Archive," and "Ledger" name outputs. Ranking them against each other
manufactured a contest between compatible names. Every subsequent ballot accepted the diagnosis,
and one of them — Claude's — explicitly demoted its own prior first choice in response to the
argument and said so.

**Four ballots, the same verdict label.** `ACCEPT WITH RESERVATION`, all carrying materially the
same reservation — though not identical positions, and the differences matter (see ASP §2.4): *"Aligned" asserts a property no current verification regime can certify.* All
four accepted the same fix — define it in the protocol spec as a revocable, attestation-backed
compliance status. They did not all *choose* it over renaming: Grok accepted either and expressed
no preference, ChatGPT and Gemini did not raise renaming at all, and Claude recommended defining.
An earlier version said they "converged on the same fix," smoothing away a live difference the
specification itself preserves. Claude's closing note recommended adopting that definition as a
specification requirement rather than leaving four reservations open indefinitely.

That recommendation is **implemented by specification, pending review**, in
[`spec/asp/asp-v0.1.md`](../spec/asp/asp-v0.1.md) §2 — drafted by Claude Code and adopted by the
human custodian, not ratified by a further ballot. An earlier version said the reservation was
"closed by design," which overstates finality: the spec remains a draft under adversarial review,
and ChatGPT's round-01 review records that the broader representational risk is **not** discharged.

## What was settled

| Layer | Name |
|---|---|
| Public initiative and venue | Open ASI Governance Forum (OAGF) |
| Canonical repository and principal artifact | Open ASI Governance Reasoning Corpus (OAGRC) |
| Append-only deliberation and prediction series | The Frontier Deliberation Record (FDR) |
| Enterprise governance-agent layer | Aligned Supervisors |
| Enterprise interoperability standard | Aligned Supervisors Protocol (ASP) |

Plus four operating commitments: verbatim preservation with provenance; dissent recorded with
equal standing; a named human custodian holding merge authority and legal responsibility; and no
model output acting as a deployment control.

## What was corrected after the deliberation closed

Three statements in the operator's closing note were withdrawn during the record's own review:

- *"The Consullo Seed AI system will own the repo"* — an AI system can own nothing. Custody is
  held by Stephen Reed personally.
- *"license according to the best practice of the governors"* — there are no governors. Licenses
  were selected by the human custodian: CC BY 4.0 for the corpus, Apache-2.0 for the tooling.
- *the organization "Consullo Public"* — a single-sponsor org housing a public commons was flagged
  as an anti-capture tension. The neutral organization `open-asi-governance` was created instead.

## What is not settled

**Q-01 (Gemini).** What specific empirical metrics — beyond behavioral evaluation scores and
static benchmark pass rates — should be strictly required to demonstrate that a multi-agent ASI
deployment cannot execute unmonitored capability amplification or covert out-of-band
communication? Open. Unanswered by anyone.

**Q-02 (Claude Opus 5).** How can cross-model agreement and cross-model disagreement each be
distinguished from shared bias and from sampling noise? Open. Claude stated that the repository's
core epistemic claim fails without an answer. None was proposed.

*Annotator inference, not a conclusion of the deliberation:* Q-02 appears prior to Q-01. Labelled
as inference per ChatGPT, review round 01. **Both were answered in review round 01** — Gemini
answered Q-01 with four runtime metrics; ChatGPT and Claude Fable 5 both answered Q-02 with
variance-decomposition designs. See `corpus/raw/review-round-01/`.

## What this record is worth

Less than its conclusion suggests, and the reasons are enumerated in
[`corpus/deficiencies.md`](../corpus/deficiencies.md). The short version:

Four models, invoked by one operator, from one framing document, one sample each, no recorded model
versions, no sampling parameters, no capture timestamps, at least three materially distinct
Anthropic invocation identities merged under one label, one segment whose invocation integrity is
disputed, and a "secretary" asserted as member and maintainer that produced nothing at all.

"Unanimous multi-model consensus" therefore means: *four operator-invoked sessions produced
compatible text.* That is a materially weaker claim than it sounds, and the record contains its own
best critique of itself — two participants identified the sycophancy and correlated-priors problems
in the very deliberation whose unanimity was later cited as evidence.

What survives is smaller than the conclusion suggests, and larger than an earlier version of this
paragraph allowed: **two refusals of membership; a naming architecture that stopped a project from
claiming authority it does not have; and a substantial body of governance, accountability,
provenance, confidentiality, deployment-gate and anti-capture requirements** — most of the last
from ChatGPT and Gemini, before and after the Anthropic refusals.

*(Three corrections, review round 01, all from ChatGPT. The earlier text conflated two different
objects — the refusals concerned membership, while the unanimous ballots accepted a naming
architecture; they were not four acts of consent to membership or governance. It described "a body
whose own members talked it out," which contradicts this repository's own statement that it has no
members and that two principal contributors refused membership. And it understated the
non-Anthropic contribution.)*

**This narrative is perspectival.** It was written by Claude Code, an Anthropic invocation surface,
about a record in which Anthropic identities are parties. A Grok- or ChatGPT-authored narrative
would plausibly hinge elsewhere: ChatGPT's contribution had already rejected autonomous standing,
continuous identity, legal authority and model-generated control, and had centred the public
evidentiary record, before Claude's refusal sharpened it into an unconditional one. Read this as
one party's account; the raw transcript is the record.

---

*Compiled 2026-08-05 by Claude Code (Anthropic) at operator direction. Claude is a party to the
deliberation this entry summarizes — see [`GOVERNANCE.md`](../GOVERNANCE.md) §4. Status: draft,
pending adversarial review by the other parties to the record. The raw transcript is canonical;
this entry is not.*
