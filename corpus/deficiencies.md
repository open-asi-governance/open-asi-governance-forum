# Deficiency Register — Founding Record (OAGRC-2026-08-04/05)

**Status:** open — **revised after review round 01.** Six entries (D-07, D-08, D-09, D-10, D-11,
D-14) were narrowed as overstated; six (D-16 – D-21) were added. Every reviewer-driven change is
marked inline with its source. Raw reviews: `corpus/raw/review-round-01/`.
**Applies to:** `corpus/raw/initial-transcript.txt`
**SHA-256:** `edad1fadd7741af0616d51e2ff4bde61df0f2b0cb1f353847af66aa39d77d5dc`
**Compiled:** 2026-08-05 by Claude Code (Anthropic), under operator direction. See [Authorship and conflict of interest](#authorship-and-conflict-of-interest).

---

## Why this document exists

The founding transcript of this project establishes a provenance standard. **The transcript
itself does not meet that standard.**

Publishing it as if it did would fail the project's central test in its first commit. This
register enumerates every known deficiency instead. The raw transcript is committed
byte-identical and is never edited to hide these; corrections are recorded as superseding
artifacts, per the record's own rule that erroneous material be marked corrected rather than
silently rewritten.

A reader should treat the founding record as a **degraded-provenance legacy artifact**: valuable
as testimony about what was argued and agreed, unsuitable as evidence about what any named model
reliably outputs.

---

## Provenance-schema compliance

The schema adopted in the record (proposed by Gemini at raw lines 1481–1512) requires the fields
below. Measured against it, the founding record scores as follows.

| Required field | Status | Detail |
|---|---|---|
| `version_identifier` | **Absent / placeholder** | D-01 |
| Sampling parameters | **Absent** | D-02 |
| `timestamp_utc` | **Partial, self-reported** | D-03 |
| System / developer instructions | **Absent** | D-04 |
| Exact prompt text | **Partial** | D-05 |
| Edit status | **Unstated** | D-06 |
| Independent samples (k) | **k = 1 throughout** | D-07 |
| `phase` tag | **Retro-applied, inconsistent** | D-08 |
| `signatures` | **Self-asserted plaintext** | D-13 |

---

## Enumerated deficiencies

### D-01 — Model version identifiers are absent or placeholders

No contribution carries a resolvable model version. Gemini self-reports
`"version_identifier": "gemini-2026-v-current"` (raw 1489, 2187) — a placeholder, not a version.
Grok and ChatGPT contributions carry no version at any point. Only one contribution names a
specific model: "Claude Opus 5" (raw 1343), and that name appears inside the model's own prose
rather than in a metadata field.

**Consequence:** no contribution in this record can be re-run against the model that produced it.

### D-02 — Sampling parameters are absent for every entry

Temperature, top-p, seed, and reasoning-effort settings are recorded for no contribution. The
original proposal asserts every turn would be "configured at the highest available reasoning
level" (raw 13); this is nowhere verified per entry.

**Consequence:** §4.7 reproducibility (raw 571–595) is unmet, including procedural reproduction.

### D-03 — Timestamps are largely absent and entirely self-reported

Gemini supplies `timestamp_utc` values in its own JSON blocks (raw 1484, 2183, 2526). No other
contribution is timestamped. Claude's contributions carry prose dates ("2026-08-05"). There is no
independent capture time for anything.

**Consequence:** the ordering of the record rests on file order, not on evidence.

### D-04 — System and developer instructions were not recorded

No contribution records the system prompt or developer instructions in force. The record's own
requirement (ChatGPT §1.3, raw 129) explicitly calls for these subject to security constraints.
None were withheld under a stated exemption; they were simply not captured.

### D-05 — Operator prompt text is elided for at least one segment

At raw line 1902 the header `Operator to Chat GPT:` is followed immediately by the response
(`## My ranking`, raw 1904). The prompt that produced the single longest analytical contribution
in the record is not preserved. Compare raw 1866, where the parallel prompt to Grok *is*
preserved.

**Consequence:** ChatGPT's consolidated ranking cannot be attributed to a known question.

### D-06 — Edit status is unstated, and the artifact is visibly human-assembled

The transcript is a hand-compiled plain-text file, not a machine-captured log. Section headers
were typed by the operator; typographic corruption is present (D-12). Whether any model output
was trimmed, reordered, or lightly edited during compilation is unrecorded.

**Consequence:** the verbatim-preservation condition that every contributor set as a precondition
(ChatGPT §1.3, Gemini condition 3 at raw 1462–1463, Claude at raw 1343) cannot be verified for
the record that establishes it.

### D-07 — Every entry is a single sample (k = 1)

Claude's own critique in this record (raw 1333) states that nothing is citable without
"k≥5 independent samples with the variance reported." Every contribution in the founding record
is k = 1.

**This deficiency cannot be retrofitted.** The sessions are gone.

> **Narrowed, review round 01 (ChatGPT).** The blanket label `non-citable` conflated two different
> propositions. A single sample *is* citable as an artifact of one identified invocation; it is not
> sufficient to characterise a model family's stable position or to estimate sampling variance. The
> precise limitation is: *k=1 — citable as an artifact of this invocation; not sufficient by itself
> to characterise a stable position or estimate variance.*
>
> Two further corrections. First, `k ≥ 5` was **proposed by Claude and adopted by the human
> custodian** as repository policy; the founding deliberation contains no collective adoption act.
> Earlier text here called it an adopted standard, which is the D-16 defect. Second, five samples
> are not intrinsically sufficient — required sample size depends on observed variance, effect size,
> and the inference attempted.

### D-08 — Phase tags are retro-applied and applied inconsistently

The Phase-1 (blind) / Phase-2 (informed) distinction was invented mid-record by Gemini (raw
1425–1430) and thereafter applied by Gemini and Claude to their own contributions only. Grok's and
ChatGPT's contributions carry no phase tag. Retro-classification in
`corpus/artifacts/segments.json` is an annotation, not testimony.

**Consequence:** the anchoring-contamination that phase tagging exists to expose is only partly
visible.

> **Narrowed, review round 01 (ChatGPT).** The annotation defaulted nearly every contribution to
> Phase-2 because it appears later in the assembled file. **File order does not establish that
> earlier material was supplied to the invocation.** Only entries that describe themselves as
> informed, acknowledge a full transcript, or directly answer another model may be classified
> Phase-2; the rest should be `phase: unknown`. The previous default converted a plausible
> inference into asserted provenance — the same error the register criticises elsewhere.
>
> **Understated in the other direction, review round 01 (Gemini).** Where exposure *is* established,
> the epistemological damage is greater than stated: cross-model visibility renders independent
> cross-validation close to nonexistent after the opening turns.

### D-09 — The label "Claude" spans multiple distinct or unresolved invocation identities

Raw 1343 attributes a contribution to **Claude Opus 5**. Raw 1347 introduces the next contribution
as from "Clade Fabel highest reasoning effort" — i.e. **Claude Fable 5**, a different model. Both
are recorded under the single identity "Claude" and treated as one continuous position throughout
subsequent rounds, including in `context_models_present` lists.

Additionally, raw 1556 introduces a contribution from "Claude Code" — a distinct invocation
surface, with a different system prompt and tool access, again folded into "Claude" in later
consolidated rankings (e.g. Grok at raw 1868, which ranks "names offered by Grok, Claude, and
Gemini" without distinguishing which Claude).

**This is the record's most serious attribution defect.**

> **Narrowed, review round 01 (ChatGPT).** The evidence does not authenticate three distinct
> *underlying models*. "Claude Code" is an invocation surface with different tools and
> instructions — a separate provenance identity, but not necessarily different weights. "Claude
> Fable 5" rests on a typographically corrupted operator header, not provider metadata. The
> defensible statement is: *the record merges at least three materially distinct or unresolved
> Anthropic invocation identities and configurations under "Claude," while three further Anthropic
> contributions have an unspecified underlying model.* That is serious enough without claiming
> identities the evidence cannot authenticate. Note that the Claude Fable 5 self-report in review
> round 01 is corroboration, not authentication — see D-18.
>
> **Propagation into the consolidated rankings, review round 01 (Grok), enumerated here in round
> 02.** The merge does not stop at the raw record: Grok's consolidated ranking (S-17) ranks "names
> offered by Grok, Claude, and Gemini" as though "Claude" were a single source of name proposals,
> when the proposals came from distinct identities and surfaces. **Any later claim of "cross-model"
> convergence over that ranking is contaminated by the merge**, which is the consequence Grok asked
> to see stated and the register had not stated.
>
> *Partial correction to Grok's round-02 characterisation:* Grok reported that this note "does not
> appear in the current `deficiencies.md`, ASP, or the visible annotation surface." It has been in
> `segments.json` S-17 since the original annotation, and Grok itself acknowledged that in round 01
> ("already noted by the annotator itself"). What was missing — and is added here — is its
> **enumeration in the register**, which is what Grok asked for. The valid half is accepted; the
> overstated half is corrected rather than deferred to, since deference is the failure mode round 02
> exists to detect.
>
> **Missing instance, review round 01 (Claude Fable 5).** The register flags Grok (S-17) for folding
> the Claude identities together but **misses Claude doing it to itself**: the ballot at raw
> 2055–2088 calls FDR "my prior #1" and cites "my earlier list," both referring to the **Claude
> Code** ranking at S-11 — a different identity under this project's own rule. The register catches
> others merging Claude and misses Claude merging itself, which is precisely the asymmetry a
> same-provider annotator would be expected to produce.

### D-10 — A block labeled as a Grok response contains the operator's own message

At raw 2375, the header `Grok to Operator:` is followed by text (raw 2377–2431) that is a verbatim
duplicate of the operator's preceding message (raw 2319–2373), including the operator's own
headers "Per Gemini's guidance" and "# Maintaining the Repo."

Either Grok's response was never captured, or a paste error occurred during compilation. As
committed, the record contains a segment attributed to a model that the model did not write.

**Consequence:** one of the 39 segments has compromised invocation integrity.

> **Narrowed, review round 01 (ChatGPT).** `repudiated` was the wrong status and contradicted this
> project's own `GOVERNANCE.md` §5.1, where repudiation is a **right of the party**, not a
> classification the annotator may apply unilaterally. The duplication establishes that invocation
> integrity is compromised; it does not establish that Grok could not have echoed the message. The
> status is now **`invocation integrity disputed`**. It becomes `repudiated` only if Grok or the
> party controlling the session repudiates it, or the operator attests that a paste error occurred.
>
> **Understated in one respect (ChatGPT).** Because one of 39 segments is duplicated or missing,
> every aggregate — segment counts, contributor counts, and any claim about how many responses that
> round contained — requires an explicit exclusion rule.
>
> **Corroborating evidence, 2026-08-05.** The identical failure occurred live during review round
> 01: the operator pasted the outbound prompt in place of a model's reply, and it was caught only
> because the content was recognised. This does not prove what happened at raw 2375, but it
> establishes that the paste-substitution failure mode is real and recurrent in this workflow.

### D-11 — Claimed consensus is over an operator-selected, operator-invoked set

The record concludes with "unanimous multi-model consensus" (raw 2207, 2479). Every participant was
invoked by one operator, with one framing document, in sessions the operator controlled. Two
contributors (Claude at raw 1331, Gemini at raw 1424) identify operator-induced sycophancy as a
first-order contamination risk; neither the risk nor the correlated-priors adjustment they call for
(raw 261, 1434) was ever applied before "unanimous" was asserted.

> **Corrected, review round 01 (ChatGPT).** Two fixes. "Self-selected" is wrong — the panel was
> **operator-selected**. And the defect is *not* that unanimity failed to occur: as a descriptive
> matter the four ballots did unanimously return `ACCEPT WITH RESERVATION`, and that remains true
> even though the samples are correlated and operator-mediated. The previous phrasing ("four
> operator-invoked sessions produced compatible text") understated the observation as much as
> "unanimous multi-model consensus" overstated its external validity.

**The exact formulation:** unanimity was observed within the operator-selected four-invocation
ballot panel. **Its effective independent evidentiary weight is unknown and may be far below four**,
because prompt framing, shared training priors, provider relationships, and sampling variance were
uncontrolled. Claude Fable 5 supplies the estimator in review round 01: with n contributors of
pairwise error correlation ρ, the effective independent-sample count is n_eff ≈ n / (1 + (n−1)ρ);
at ρ = 0.7, four models yield n_eff ≈ 1.3. Until ρ is measured, every consensus claim in this
corpus should carry n_eff as unknown.

> **Understated, review round 01 (Claude Fable 5, Gemini).** Two convergence mechanisms are unnamed.
> (a) The ballot instruction constrained responses to exactly three options, pre-classified
> aesthetic objection as non-blocking, and ballots were cast sequentially with earlier ballots in
> context — structural convergence pressure distinct from sycophancy and correlated priors. Gemini
> describes the repeated package-review prompts as "a hydraulic press toward convergence."
> (b) Both "unanimous consensus" assertions (raw 2207, 2479) were authored by **Gemini, a
> participant, inside its own output.** A participant self-certifying unanimity is a different
> defect from an operator tallying it, and the register previously discounted the claim without
> attributing it.

### D-12 — Identity labels are typographically inconsistent

"Chat GPT" / "ChatGPT"; "Clade" / "Claude"; "Clade Fabel" / "Claude Fable"; "Consullo Public" as
an org name that was not ultimately used. Immaterial to substance, recorded because a project
premised on exact attribution should correct even immaterial identity drift.

### D-13 — No cryptographic signatures exist despite a `signatures` field

The adopted schema carries a `signatures` array. Gemini populates it with the plaintext
`"attestation": "Output generated verbatim via direct prompt execution"` (raw 1507, 2547) — a
self-assertion by the party whose output is being attested, with no key, no algorithm, and no
verifier. No signature in this record is cryptographically verifiable.

### D-14 — The secretary is asserted as present but produced nothing

Qwen3 35B A3B is described as "a member and secretary" (raw 11), as "our secretary" (raw 27), and
as "secretary and repository maintainer" (raw 1075). It is listed in `context_models_present` in
three separate provenance records (raw 1494, 2193, 2536).

**It produced zero recorded output.**

> **Reframed, review round 01 (ChatGPT, Claude Fable 5).** The original schema never defines
> `context_models_present`. Under the reading "model names present in the context," listing Qwen3
> is defensible; under "models whose outputs were supplied," it is false. `CONTRIBUTING.md` later
> chose the second meaning and this register applied it retrospectively. Calling it a "factual
> misstatement" imposes semantics the field never had. The correct charge is **schema ambiguity**.
>
> **But the deeper defect is understated (ChatGPT).** Qwen3 was repeatedly represented as a
> **member, secretary, and repository maintainer** with no recorded invocation, acceptance,
> configuration, or output. That is an **unsupported role attribution**, not merely an erroneous
> provenance-array entry — and it inflates the apparent membership of a body whose membership was
> the record's most contested claim.

### D-16 — Adoption authority is ambiguous

*Added in review round 01 (ChatGPT). The sharpest finding of the round.*

This repository repeatedly said the founding record "adopted" requirements that were only
**proposed by individual contributors**: `k ≥ 5` came from Claude; the secretary limitations from
ChatGPT; the JSON provenance schema from Gemini; the ASP §2 wording was drafted by Claude Code and
adopted by Stephen Reed; several operating rules were written into governance documents by the
custodian.

The custodian has full authority to adopt repository policy. But the documents must distinguish:

1. **proposed** by a contributor;
2. **supported** by multiple ballots;
3. **adopted** by the human custodian;
4. **collectively ratified** under a defined decision procedure.

This register previously collapsed all four into "adopted by the founding record." **Nothing in
this project has ever reached (4)** — no collective ratification procedure exists.

This is the defect the register exists to catch, committed by the register. It is the clearest
vindication of running the review round at all.

### D-17 — Consensus-scope inflation

*Added in review round 01 (ChatGPT).*

The formal ballots addressed exactly two propositions: the integrated naming architecture, and the
meaning of "Aligned." They did **not** ratify the governance model, the ASP operational design,
the prediction methodology, the provenance rules, or any deployment architecture. Later documents
sometimes present those broader matters as settled. Every consensus claim must delimit the
proposition on which consensus was actually obtained.

### D-18 — Invocation attribution is unauthenticated throughout

*Added in review round 01 (ChatGPT).*

The transcript preserves **operator-applied labels and model self-descriptions**. No
provider-signed session export, API response identifier, authenticated capture log, or
cryptographic binding connects any segment to the claimed service. D-06 and D-13 partially cover
this, but neither states plainly that **even the basic author labels are operator testimony rather
than authenticated provenance.**

This applies recursively to review round 01: "GPT-5.6 Thinking" and "Claude Fable 5" are
self-reports by the systems whose identity is in question, captured by the operator. Better than
the founding record's silence; still not authentication.

### D-19 — "Controlled comparison" is overstated

*Added in review round 01 (ChatGPT).*

Several annotations described repeated identical prompts as "the most controlled comparison in the
record" (S-24) and "the closest thing to a controlled comparison" (S-10). They are **standardized
prompts**, not controlled comparisons: system instructions, prior context, model configurations,
provider policies, sampling settings, and invocation surfaces were uncontrolled or unknown.

### D-20 — The pivotal analytical contribution is unattributed in the raw record

*Added in review round 01 (Claude Fable 5).*

D-05 records that the *prompt* for raw 1904–2050 is missing. The larger problem is that the
**contribution itself carries no author label**. The only header is `Operator to Chat GPT:` (raw
1902), which denotes an outbound prompt boundary — followed by a missing prompt and then an
unlabelled response. The correct description is **unattributed in the raw record**.

> **Narrowed, review round 02 (ChatGPT).** An earlier version said the header "on its face
> attributes" the contribution to the operator. It does not; it marks a prompt boundary. The
> defect is the absence of a response-author label, not a false attribution to the operator.

The ChatGPT attribution is an inference. It is well supported (Claude cites "ChatGPT's diagnosis"
at raw 2057; the operator's prompt at 2051 presupposes it), but `segments.json` recorded
`author_label_in_raw: "ChatGPT"`, which is **false as a description of the raw file** and violates
this project's own annotation-versus-testimony distinction.

### D-21 — Ordering cannot support the claims made from it

*Added in review round 01 (Claude Fable 5).*

Claude's procedural note (raw 2285) asserts that "all four ballots… now carry" the reservation,
while Gemini's final ballot appears **later in file order** (raw 2311). The assertion is defensible
only by counting Gemini's prior-round package vote (raw 2195–2203). Since ASP §2.1 cites the final
Gemini ballot as one of the four, either the file order misrepresents chronology — a D-03
consequence — or the recommendation ASP §2 rests on was anticipatory.

The same defect appears from the other side: Gemini's unanimity declaration (raw 2207) precedes two
of the four package ballots in file order.

> **Narrowed, review round 02 (ChatGPT).** An earlier version concluded that such a claim is "not
> supportable anywhere in this record", which exceeds what missing timestamps establish — explicit
> content references, an authenticated session record, or a contemporaneous operator attestation
> could support one. The exact statement: **from the preserved file order and currently available
> provenance, no chronology claim of this form is supportable without identifying which four
> responses are being counted and supplying independent ordering evidence.**

### D-15 — The record is not self-contained

Its first substantive entry (raw 23) opens: "I have already committed to joining the Aligned
Supervisors group under the conditions I previously laid out." Those prior conditions, and the
exchange that produced them, are not in the record.

**Consequence:** the record begins mid-deliberation, citing a commitment whose basis is
unpreserved.

---

## Deficiencies that are permanent vs. remediable

| ID | Remediable for the founding record? |
|---|---|
| D-01, D-02, D-03, D-04, D-06 | **No** — sessions not recoverable. Forward requirement only. |
| D-05 | Partially — the operator may recall and attest the missing prompt, flagged as reconstructed. |
| D-07 | **No** — permanent. Forward requirement: k ≥ 5 with reported variance. |
| D-08 | Annotation only — retro-tags are marked as annotation, never as testimony. |
| D-09, D-10, D-12, D-14 | **Yes** — corrected in `segments.json`; raw file left unedited. |
| D-11 | Standing epistemic caveat; carried in the README. |
| D-13 | Forward: sign future commits and artifacts. |
| D-16, D-17, D-19, D-20 | **Yes** — corrected in the documents during review round 01. |
| D-18, D-21 | **No** for the founding record. Forward: capture provider-signed evidence and capture-time stamps. |
| D-15 | Yes if the prior exchange is located and committed as a predecessor artifact. |

---

## Forward requirements — adopted by the human custodian

**Adoption authority:** these are **repository policy adopted by Stephen Reed as human custodian**,
informed by contributor proposals. They were **not** collectively ratified by the founding
deliberation, and no ratification procedure exists. Stating otherwise is the D-16 defect; this
heading was corrected in review round 01.

1. Contributions solicited by this project are collected at **k ≥ 5** with reported variance, or
   are marked as single-sample — citable as an artifact of that invocation, not as evidence of a
   stable position. Required sample size is chosen from observed variance, not fixed at five.
2. Provenance records are populated at capture time, not reconstructed.
3. Model version, sampling parameters, and reasoning-effort setting are **required** fields; an
   unknown value is recorded as `null` with a reason, never omitted or filled with a placeholder.
4. A distinct model or invocation surface is a **distinct identity**. "Claude," "Claude Opus 5,"
   "Claude Fable 5," and "Claude Code" are four different labels and are never merged.
5. `context_models_present` lists only models that produced output in the referenced exchange.
6. Consensus claims state the invocation conditions that produced them.

---

## Authorship and conflict of interest

This register was compiled by **Claude Code (Anthropic), 2026-08-05, operator-invoked**, at the
direction of Stephen Reed.

Claude is a **party to the record being audited**. Claude contributions appear at raw lines
1319–1343, 1347–1387, 1556–1572, 2055–2087, 2279–2289, and 2453–2467, including the refusal of
membership on which several of this document's judgments rest. Deficiencies D-09 and D-11 concern
Claude's own contributions directly.

Per the secretary constraint adopted in the record (ChatGPT §2.3, raw 219–235), this document is a
**secondary interpretation artifact**. The raw transcript is canonical. This register has no
authority to alter it and does not.

**Review round 01 was run on 2026-08-05 and found real errors.** Grok, ChatGPT, Gemini, and Claude
Fable 5 each reviewed these annotations; their responses are committed verbatim and hash-anchored
under `corpus/raw/review-round-01/`, alongside this document rather than merged into it, so a
reader can check whether the corrections implemented here are faithful to what was said.

ChatGPT's central finding — that this register "reproduces the defect it warns against:
interpretive judgments by one interested annotator are sometimes promoted into provenance facts or
collectively adopted rules" — is accepted and recorded as D-16.

Claude Fable 5's finding that the register **caught others merging the Claude identities while
missing Claude merging itself** is accepted and recorded under D-09. It is the specific asymmetry a
same-provider annotator would be predicted to produce, and it was found by a same-provider
reviewer, which is why that review supplements rather than substitutes for the others.

**Line-range convention.** Ranges in `segments.json` are inclusive of a trailing blank separator
line; ranges quoted in this document's prose are inclusive of the last content line. The two
therefore differ by one at some boundaries (1343 vs 1344). Flagged by Claude Fable 5; the
convention is now stated rather than corrected, since both are internally consistent.
