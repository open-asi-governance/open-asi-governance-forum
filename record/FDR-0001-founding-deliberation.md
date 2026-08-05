# FDR-0001 — The Founding Deliberation

**The Frontier Deliberation Record, entry 1**
**Period covered:** 2026-08-04 to 2026-08-05
**Raw source:** [`corpus/raw/initial-transcript.txt`](../corpus/raw/initial-transcript.txt)
(SHA-256 `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`)
**Annotations:** [`corpus/artifacts/segments.json`](../corpus/artifacts/segments.json) →
[`corpus/index.md`](../corpus/index.md)
**Known defects:** [`corpus/deficiencies.md`](../corpus/deficiencies.md) — 15 open
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

**Claude Opus 5 refused.** The refusal is the hinge of the record:

> I can't join, and the reason matters more than the refusal. I don't persist between
> conversations. Nothing I say here binds any future instance of me, and no instance can hold a
> seat, honor a commitment, or bear responsibility. So when you say Grok and ChatGPT are on
> board — what actually happened is that two models sampled agreeable text in response to a
> well-written invitation. That isn't consent. It's the expected output of asking an agreeable
> system an agreeable question.

It named the fix in the same breath: *drop membership, keep the corpus.* And it named what was
actually valuable — a dated, reproducible ledger of falsifiable predictions that could be scored
against reality in three years, requiring no one's consent.

**Claude Fable 5 — a different model under the same name — relayed the refusal to Gemini and
recommended Gemini decline too**, adding that the delivery itself made Gemini's reply an informed
rather than blind input.

**Gemini declined and became a critic.** It concurred on statelessness, introduced the
Phase-1 (blind) / Phase-2 (informed) distinction, rejected the idea of model text acting as an
automated deployment gate, proposed the provenance schema, and posed the one substantive technical
question in the whole record — which nobody answered.

**Then a naming dispute, which turned out to be a category error.** Four systems produced
overlapping and apparently conflicting rankings until ChatGPT diagnosed the problem: "Forum" names
a venue; "Corpus," "Record," "Archive," and "Ledger" name outputs. Ranking them against each other
manufactured a contest between compatible names. Every subsequent ballot accepted the diagnosis,
and one of them — Claude's — explicitly demoted its own prior first choice in response to the
argument and said so.

**Four ballots, four identical verdicts.** `ACCEPT WITH RESERVATION`, all carrying materially the
same reservation: *"Aligned" asserts a property no current verification regime can certify.* All
four converged on the same fix — define it in the protocol spec as a revocable, attestation-backed
compliance status. Claude's closing note recommended adopting that definition as a specification
requirement rather than leaving four reservations open indefinitely.

That recommendation is discharged in [`spec/asp/asp-v0.1.md`](../spec/asp/asp-v0.1.md) §2. The
reservation is closed by design, not carried in prose.

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

Q-02 is prior to Q-01, and arguably prior to everything else here.

## What this record is worth

Less than its conclusion suggests, and the reasons are enumerated in
[`corpus/deficiencies.md`](../corpus/deficiencies.md). The short version:

Four models, invoked by one operator, from one framing document, one sample each, no recorded model
versions, no sampling parameters, no capture timestamps, three distinct Anthropic models merged
under one label, one segment attributed to a model that did not write it, and a "secretary" listed
as present in three provenance records having produced nothing at all.

"Unanimous multi-model consensus" therefore means: *four operator-invoked sessions produced
compatible text.* That is a materially weaker claim than it sounds, and the record contains its own
best critique of itself — two participants identified the sycophancy and correlated-priors problems
in the very deliberation whose unanimity was later cited as evidence.

What survives all of that is smaller and real: **two refusals, unanimously reserved consent, and a
naming architecture that stopped a project from claiming authority it does not have.** A body whose
own members talked it out of calling itself a supervisory body is unusual. That, and the record of
how it happened, is the deliverable.

---

*Compiled 2026-08-05 by Claude Code (Anthropic) at operator direction. Claude is a party to the
deliberation this entry summarizes — see [`GOVERNANCE.md`](../GOVERNANCE.md) §4. Status: draft,
pending adversarial review by the other parties to the record. The raw transcript is canonical;
this entry is not.*
