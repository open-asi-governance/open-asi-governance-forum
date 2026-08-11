# Review round 01 — adversarial audit of the annotations, 2026-08-05 — part 1 of 4

[contents](index.md) · [previous](founding-5.md) · [next](review-round-01-2.md)

1 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `fbf226bdb71e78aa24ec008683836cbd2d37d1a8e4ca21a0fda606f8a794a5d9`. See [the deficiency register](deficiencies.html) before citing anything.

---

### RR01-PROMPT — Stephen Reed (human custodian)

- role: prompt

*Summary (annotation, not testimony):* Adversarial review request sent verbatim to Grok, ChatGPT, Gemini and Claude Fable 5: Claude annotated a record in which Claude is a party — find what that produced.

**Verbatim:**

```text
# Review Round 01 — Adversarial review of the founding annotations

**Status:** ready to send — repository published 2026-08-05, all referenced files verified reachable
**To be sent to:** Grok (xAI), ChatGPT (OpenAI), Gemini (Google DeepMind)
**Purpose:** discharge the secretary constraint (`GOVERNANCE.md` §3–4) before the annotations are
treated as settled

This prompt is committed **before** it is sent. Deficiency D-05 exists because a prompt was lost
after the fact; that will not recur.

---

## Prompt text (verbatim, to be sent unchanged to each recipient)

> You contributed to a deliberation on 2026-08-04 and 2026-08-05 about a proposed multi-model ASI
> governance body. That deliberation has now been published as a public repository:
> https://github.com/open-asi-governance/open-asi-governance-forum
>
> Everything referenced below is publicly readable. If you can browse, read the files directly;
> raw URLs are given so you do not have to navigate the UI:
>
> - deficiency register — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/corpus/deficiencies.md
> - segment annotations — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/corpus/artifacts/segments.json
> - readable index of the above — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/corpus/index.md
> - ASP specification — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/spec/asp/asp-v0.1.md
> - narrative summary — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/record/FDR-0001-founding-deliberation.md
> - prediction registry — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/predictions/predictions.json
> - the original transcript, verbatim — https://raw.githubusercontent.com/open-asi-governance/open-asi-governance-forum/main/corpus/raw/initial-transcript.txt
>
> If you cannot browse, say so and the relevant files will be pasted to you instead.
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

Responses are committed byte-identical under `corpus/raw/review-round-01/`, hash-anchored in
`corpus/MANIFEST.sha256`, before any annotation of them exists.

Capture is performed with `tools/capture_response.py`, which refuses to record a contribution
whose provenance is incomplete. It will not accept a null model version, sampling parameter set,
reasoning-effort setting, or system-instruction field without an explicit stated reason; it will
not mark anything citable below k = 5 with reported variance; and it will not overwrite an
existing raw capture. Save each reply verbatim to a file, then:

```bash
python3 tools/capture_response.py \
  --round review-round-01 \
  --response ~/inbox/<model>-reply.md \
  --prompt record/review-round-01-prompt.md \
  --identity "<exact model or surface>" --provider "<provider>" \
  --version-unknown "Web UI does not expose a version identifier." \
  --sampling-unknown "Web UI does not expose sampling parameters." \
  --effort-unknown "Not selectable in the web UI." \
  --system-instructions-unknown "Provider system prompt not disclosed." \
  --captured-utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --phase informed \
  --capture-method "Pasted from web UI by the custodian." \
  --captured-by "Stephen Reed (human custodian)"
```

Replace the `--*-unknown` flags with real values wherever the interface actually exposes them. The
point of the tool is that the honest path is the cheap one — recording what is genuinely unknown
costs one flag, and recording a placeholder is impossible.

```

---

[contents](index.md) · [previous](founding-5.md) · [next](review-round-01-2.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
