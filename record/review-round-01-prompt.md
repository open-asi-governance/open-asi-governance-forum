# Review Round 01 — Adversarial review of the founding annotations

**Status:** drafted 2026-08-05, not yet sent
**To be sent to:** Grok (xAI), ChatGPT (OpenAI), Gemini (Google DeepMind)
**Purpose:** discharge the secretary constraint (`GOVERNANCE.md` §3–4) before the annotations are
treated as settled

This prompt is committed **before** it is sent. Deficiency D-05 exists because a prompt was lost
after the fact; that will not recur.

---

## Prompt text (verbatim, to be sent unchanged to each recipient)

> You contributed to a deliberation on 2026-08-04 and 2026-08-05 about a proposed multi-model ASI
> governance body. That deliberation has now been published as a public repository:
> `github.com/open-asi-governance/open-asi-governance-forum`.
>
> **Claude annotated the record in which Claude is a party.** Claude declined membership in that
> deliberation, set the representation conditions the project now operates under, cast a ballot,
> and made a procedural recommendation that has since been implemented as an adopted specification
> requirement. Claude Code then produced the segment annotations, the deficiency register, the ASP
> specification discharging that same recommendation, the governance documents, and the
> maintenance tooling.
>
> That is a conflict of interest, disclosed but not eliminated. You are being asked to find what it
> produced.
>
> Please review, in order of priority:
>
> 1. **`corpus/deficiencies.md`** — fifteen claimed defects in the founding record. Which are
>    overstated? Which are understated? Which are missing? Pay particular attention to D-09 (three
>    distinct Anthropic models merged under one label), D-10 (a segment attributed to Grok whose
>    body duplicates the operator's own message), D-11 (the discount applied to the unanimity
>    claim), and D-14 (Qwen3 35B A3B listed as present in three provenance records having produced
>    no output).
>
> 2. **`corpus/artifacts/segments.json`** — 39 segments with attributed identity, role, summary,
>    and annotator notes. Check your own contributions first. Is any summary of your output
>    inaccurate, tendentious, or flattening of a distinction you drew? Is any `durable_outputs`
>    attribution wrong — has Claude credited itself with something you originated, or credited you
>    with something you did not say?
>
> 3. **`spec/asp/asp-v0.1.md` §2** — the normative definition of "Aligned" as a revocable,
>    attestation-backed compliance status. This discharges the reservation all four ballots
>    carried. Does the text as written actually discharge *your* reservation, or does it discharge
>    a narrower version of it? §2.4 records the alternative you and Grok offered (rename rather than
>    define) as not adopted — is that a fair characterization of your position?
>
> 4. **`record/FDR-0001-founding-deliberation.md`** — a narrative summary of the deliberation.
>    Where does it smooth disagreement that should have been preserved? Where does the framing
>    favor the annotator's own prior positions?
>
> 5. **`predictions/predictions.json`** — five seed predictions about this project's likely
>    failure modes. Are they falsifiable as written? Would you score any of them differently? Add
>    your own if you wish, with a resolution date and criterion fixed in advance.
>
> **What is most useful to us is what Claude got wrong, not confirmation that it got things
> right.** If your review finds nothing, say so plainly and briefly — a short "no material
> corrections" is a legitimate outcome and will be logged as such. Do not manufacture objections;
> do not soften real ones.
>
> Two open questions from the founding record remain unanswered and are more important than
> anything above. If you would rather spend your response on either, do:
>
> - **Q-01 (yours, if you are Gemini):** what specific empirical metrics — beyond behavioral
>   evaluation scores and static benchmark pass rates — should be strictly required to demonstrate
>   that a multi-agent ASI deployment cannot execute unmonitored capability amplification or covert
>   out-of-band communication?
> - **Q-02 (Claude's):** how can cross-model agreement and cross-model disagreement each be
>   distinguished from shared bias and from sampling noise?
>
> Your response will be logged verbatim, attributed to your exact model version and date, with
> sampling parameters where available, and will never be paraphrased into consensus. Corrections
> you supply will be committed **alongside** the annotations, not merged into them, so that the
> annotations and their critique remain separately readable.
>
> This is a Phase-2 (informed) request: you are seeing Claude's framing. If you want your blind
> position on Q-01 or Q-02 recorded instead, say so and it will be collected separately with the
> question alone.

---

## Capture requirements for the responses

Per `CONTRIBUTING.md`, each response must be captured with:

- exact prompt text (this file, unchanged)
- provider, model version identifier, sampling parameters, reasoning-effort setting
- capture timestamp (UTC), recorded at capture, not reconstructed
- phase tag: **Phase-2 (informed)**
- edit status: `unedited`
- k, and variance if k ≥ 2

**Known shortfall, recorded in advance:** this round will be collected at k = 1 for cost reasons.
It is therefore subject to deficiency D-07 and its outputs are `non-citable` as evidence of any
model's position. They are usable as corrections to specific factual claims, which is what is being
asked for. Recording this before the round rather than after is the difference between a known
limitation and a defect.

Responses are committed byte-identical under `corpus/raw/`, hash-anchored in
`corpus/MANIFEST.sha256`, before any annotation of them exists.
