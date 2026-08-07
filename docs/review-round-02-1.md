# Review round 02 — audit of the corrections made after round 01, 2026-08-05 — part 1 of 4

[contents](index.md) · [previous](review-round-01-4.md) · [next](review-round-02-2.md)

1 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `4f2e3c79b81ef6bc8fb0fa32509bfbe26262d4c1d1f809d4a2473fd2f7a7cb5d`. See [the deficiency register](deficiencies.html) before citing anything.

---

### RR02-PROMPT — Stephen Reed (human custodian)

- role: prompt

*Summary (annotation, not testimony):* Second adversarial round: the round-01 corrections are themselves the subject. Whether a correction over-corrected, and whether the register still overstates or understates what the record supports.

**Verbatim:**

```text
# Review Round 02 — Were the round-01 corrections implemented faithfully?

**Status:** drafted 2026-08-05, not yet sent
**To be sent to:** Grok (xAI), ChatGPT (OpenAI), Gemini (Google DeepMind), Claude Fable 5 (Anthropic)
**Purpose:** verify that round-01 corrections were implemented as stated rather than softened or
over-applied, and adversarially review three documents written since, one of them normative and
entirely unreviewed

Committed **before** it is sent. Deficiency D-05 exists because a prompt was lost after the fact.

---

## Prompt text (verbatim, to be sent unchanged to each recipient)

> On 2026-08-05 you reviewed the annotations in
> https://github.com/open-asi-governance/open-asi-governance-forum and found errors in them. Those
> corrections have now been implemented — by Claude Code, the same party whose work you corrected.
>
> **This round asks whether that implementation is faithful.** Two failure modes are in scope, and
> the second is the one nobody but you can detect:
>
> 1. **Under-correction.** A correction you supplied was implemented narrowly, in a version easier
>    to accept than what you actually said, or was recorded as accepted while the underlying text
>    still carries the defect.
> 2. **Over-correction by deference.** ChatGPT reported that six deficiencies were overstated
>    (D-07, D-08, D-09, D-10, D-11, D-14). All six were narrowed. **Nobody has checked whether they
>    were narrowed correctly or merely deferred to.** A same-provider annotator over-accepting a
>    non-Anthropic reviewer's critique is a different failure from under-accepting it, and it
>    damages the record just as much. If a narrowing went too far — if a defect is now understated —
>    say so.
>
> Read the round-01 reviews at `corpus/raw/review-round-01/` — all four are committed verbatim —
> then check the corrected documents against them.
>
> ### What to check, in priority order
>
> **1. Your own corrections.** Find what you wrote in round 01. Was each item implemented as you
> stated it, narrower than you stated it, or recorded as accepted without the text actually
> changing? Where a correction was declined, was the declining stated?
>
> **2. `spec/icp/icp-v0.1.md` — new, normative, entirely unreviewed.** The Implementer Contribution
> Protocol governs how an implementer (currently Consullo, operated by this repository's custodian)
> supplies evidence without capturing the standard. Its core is a five-level promotion ladder where
> Level 2 requires an independent party to implement from the specification text alone, and Level 4
> is structurally unreachable.
>
> The question I most want attacked: **does the ladder constrain anything in practice, or does it
> supply the appearance of constraint while all real activity happens at Levels 0 and 1, which the
> implementer controls unilaterally?** If Consullo can sit at Level 1 indefinitely, publishing
> whatever it likes, the ladder may be decoration.
>
> Also §8 question 4, which the draft admits it cannot answer: **does an adversarial evaluation
> designed by a model count as "designed by a party other than the implementer," when the
> implementer chose the model, wrote the prompt, and can rerun until satisfied?** This very review
> round is fully exposed to that objection. If it is fatal, say so.
>
> **3. `spec/asp/asp-v0.1.md` §2.2 — restated as relational and scope-bound** after ChatGPT
> identified that the unary "an agent *is* an Aligned Supervisor" grammar recreated the
> intrinsic-property framing §2 exists to avoid. Does the new formulation actually fix that, or
> relocate it?
>
> **4. `corpus/deficiencies.md` — now 21 entries.** Six added in round 01 (D-16 adoption authority,
> D-17 consensus-scope inflation, D-18 unauthenticated attribution, D-19 controlled-comparison
> overstatement, D-20 the pivotal contribution has no author label, D-21 ordering cannot support
> "all four have now responded"). Are the new entries correctly scoped, or do any of them overclaim
> in the way the original fifteen did? Are the six narrowings right?
>
> **5. `predictions/predictions.json`.** P-0002 was rewritten to exclude Consullo explicitly, on the
> ground that naming Consullo an implementer would otherwise make it self-fulfilling. P-0007 was
> added, predicting that no Consullo contribution rises above ICP Level 1 by 2027-08-05.
> P-CLAUDE-F5-0001 was **scored correct on the day it was made**, eighteen months early, because
> your round-01 corrections resolved it — and logged as a miss in the optimistic direction against
> its stated confidence. Is that scoring honest, or is scoring a prediction correct on the day it
> was filed a form of self-congratulation?
>
> ### Two disclosures relevant to your judgement
>
> **This round is k = 1 again.** The project's own standard is k ≥ 5 with reported variance, and
> P-0003 predicts precisely that this standard erodes because it is expensive. Round 01 was k = 1;
> so is this. **Should any part of this round be re-run at k ≥ 5, and if so which questions
> specifically?** Answering "all of it" is unhelpful; naming the two or three questions where
> sampling variance would actually change a conclusion is useful.
>
> **A bug was found and fixed that bears on this record's integrity.** Regenerating the round-01
> supplied-context bundle silently invalidated the SHA-256 that Gemini's capture record cites — the
> record of what a reviewer was shown no longer matched what it claimed. Bundles are now frozen once
> a round has used them. Whether other artifacts carry the same class of defect is an open question
> you are invited to press on.
>
> ### Ground rules, unchanged
>
> What is most useful is what is still wrong, not confirmation that the corrections landed. A short
> "the corrections to my items are faithful, no further findings" is a legitimate and valuable
> outcome and will be logged as such. Do not manufacture objections; do not soften real ones.
>
> Your response will be logged verbatim, attributed to your exact model version and date, with
> sampling parameters where available, and will never be paraphrased into consensus. It will be
> committed **alongside** the corrections, not merged into them.
>
> This is a Phase-2 (informed) request. There are no governors here and no members — only parties
> to a record, none of whom hold standing. If you would rather spend this response on Q-01 or Q-02
> instead, do; both remain the more valuable work.

---

## Capture requirements

Per `CONTRIBUTING.md`, captured with `tools/capture_response.py --round review-round-02`, which
refuses to record a contribution whose provenance is incomplete.

**Known shortfall, recorded in advance:** this round is collected at k = 1 for cost reasons, and is
therefore subject to D-07. Its outputs are citable as artifacts of each invocation, not as evidence
of any model's stable position. Recording this before the round rather than after is the difference
between a known limitation and a defect.

Reviewers that cannot fetch the repository receive `record/review-round-02-bundle.md`, whose hash
is cited in their capture record. Bundles are frozen once used.

```

---

[contents](index.md) · [previous](review-round-01-4.md) · [next](review-round-02-2.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
