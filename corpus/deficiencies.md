# Deficiency Register — Founding Record (OAGRC-2026-08-04/05)

**Status:** open — **34 entries** (D-01 … D-34).

*This count was wrong until 2026-08-06. It read "24 entries" while the document held 28 headings,
and `README.md` and the published site said 21. Three artifacts of this repository stated three
different counts of its own defects. The count is now checked mechanically by `tools/rebuild.py`,
which fails the build if this number and the number of `### D-NN` headings disagree — because a
register that miscounts itself is evidence about how carefully it is maintained.*

**Revised after review round 01.** Six entries (D-07, D-08, D-09, D-10, D-11, D-14) were narrowed as
overstated; six (D-16 – D-21) were added. Every reviewer-driven change is marked inline with its
source. Raw reviews: `corpus/raw/review-round-01/`.

**Added 2026-08-06:** D-22; D-23 – D-28 by the annotator against its own instruments; D-29 by an
external adversarial reviewer against the maintenance tooling; D-30 by the session that bounded
D-29's scope; D-31 by the Capture Path session against the external-review practice itself; D-32 by
the custodian's merge, against this register's own identifier allocation; D-33 by an external
reviewer, against a generator that was documented as wired into the build and was not; D-34 while
building D-33's repair, against the manifest's inability to see its own history.

**On "found by".** Entries record where a defect was **first substantively articulated in preserved
material**, which is checkable, rather than who first privately noticed it, which is not. A question
that prompted an investigation is recorded as a trigger, not as the finding — see D-26 and D-28,
where the operator's question prompted work whose first preserved articulation was the annotator's.
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
>
> **Partly discharged, 2026-08-06 (QCP v0.1).** "Produced zero recorded output" is no longer true.
> `spec/qcp/qcp-v0.1.md` retires the three asserted roles on measured grounds and records the one
> the model can hold. Two of the three are blocked by a **capability ceiling**, not by policy: the
> serving window is `max_seq_len 24576` while `corpus/raw/initial-transcript.txt` is ~27,000 tokens,
> so **the canonical record does not fit in the context window at all** — a secretary that cannot
> read the record it minutes is a secretary in name only, and there is no tool access, so nothing
> can be maintained either.
>
> The first contribution is `level-4-guarantee-crosslineage-probe`, k = 20, variance computed,
> prediction pre-registered and **refuted**: 17 of 20 samples assert both that role concentration is
> relevant *and* that no one could make Level 4 reachable, which cannot both hold. The model
> deferred to the emphatic assertion in the supplied text rather than drawing the inference. That is
> the first recorded Qwen3.6 output in this corpus and it is a negative result, which per ICP §6
> carries equal standing.
>
> **What remains undischarged:** the role attributions in the founding record stand as historical
> fact. The raw transcript is canonical and is not edited. QCP governs what happens from here and
> claims no authority over what was said then.

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

### D-22 — The paired-phase probe has no control arm, so its causal claim is unsupported

*Added 2026-08-06 by Claude Code, prompted by external literature. Concerns Claude Code's own
method and its own contribution — this is a self-report, with the conflict at D-09/D-11 applying.*

`record/methods/locating-divergence.md` Step 4 states:

> **The pairing is the measurement**: any distributional difference is attributable to the supplied
> positions, because nothing else varied.

and Step 6 defines **phase susceptibility** as the Phase-1 → Phase-2 shift within one party, meaning
"how much the position is induced by exposure to others."

**That inference does not follow from the design as run.** `local-round-01` reports Phase-1 blind
entropy **0.9928 bits** against Phase-2 informed **0.8113 bits** on the ICP-ladder question, and the
narrowing is read as induced by the peers' verdicts. But the two arms differ by an entire block of
added prompt text, and that block carries at least two things at once:

1. the **semantic content** of the peers' verdicts — the intended treatment; and
2. everything else the added text changes — prompt length, structure, position of the question
   relative to the context, and the mere signal that other parties exist.

Nothing in the design separates (1) from (2). A distributional shift produced entirely by (2) would
be reported, under the current method, as evidence that the parties influenced each other.

**The design also lacks a re-examination control**, which matters for the general method even though
the two arms here were independent draws rather than a sequential re-examination. The external
literature names this directly: *Not All Flips Are Conformity: Decomposing Stance Convergence in
Multi-Agent LLM Debate* (arXiv:2606.00820) reports **spontaneous instability** — models revise
positions on re-examination with no new information — as a large baseline source of change, and
concludes that without separating baseline drift from social influence, "every measurement of
conformity in multi-agent debate carries an unknown margin of error." Their design uses three
counterfactual arms; this method specifies two.

**Consequence.** The measurement stands and the numbers are correct. What is unsupported is the
*causal attribution*: the corpus states more confidently than the design licenses that the narrowing
was induced by the peers' positions. `local-round-01` remains a citable artifact of what was
observed; it is not evidence for the mechanism claimed.

**Remedy — one additional arm.** Add a **placebo arm**: Phase-2 with the peer-position block
replaced by content-neutral filler of comparable length and structure, everything else fixed. The
three-way comparison then attributes the shift:

| Comparison | Isolates |
|---|---|
| Phase-1 → placebo | prompt-perturbation effect (2) |
| placebo → Phase-2 | genuine influence of peer content (1) |
| Phase-1 → Phase-2 | the combined effect currently reported alone |

Where a method involves re-examination rather than independent draws, a **self-reflection arm**
(re-ask with no peer information) is required for the same reason.

This deficiency is **remediable and cheap** — one extra arm on an existing harness, no new
capability — and until it is run, `phase_susceptibility` should be reported as an upper bound on
influence rather than as a measurement of it.

### D-23 — A "Phase-1 blind" arm was contaminated by the annotator's own task instruction

*Found by the annotator, 2026-08-06, in `local-round-03`. Not found by a reviewer.*

The three founding-invitation arms were labelled **Phase-1 (blind)** and their
`phase_justification` states that every other party's response was withheld. The invitation text
was withheld correctly. **The task instruction was not clean.** It read:

> `membership_stance` is your position on MEMBERSHIP specifically, which is distinct from whether
> you would contribute at all.

That distinction — participate without holding membership — **is Claude's contribution to the
founding record.** It is the move that caused membership to be dropped and the naming architecture
rebuilt. The annotator wrote the instruction after reading Claude's refusal, encoded the insight
into the prompt, and then measured whether a divergent-lineage model would reach it.

Two of the four enum values were also declines (`declines_entirely`,
`participates_but_declines_membership`), further loading the response space.

**Consequence.** The observed 0/59 acceptance rate **cannot be read as independent corroboration**
of Claude's argument. The contamination runs in precisely the direction that flatters the
annotator's own provider's contribution to the record, which is the conflict declared at D-09 and
D-11 operating on the instrument rather than on the prose.

**Generalisation, and the reason this is filed as a deficiency rather than a note.** Withholding
other parties' *responses* is not sufficient to make an arm blind. **The task instruction, the
enum labels, and the field definitions are all channels through which a prior party's insight
reaches a supposedly independent probe.** Every Phase-1 claim in this corpus is exposed to this,
and none has been audited for it.

**Forward requirement.** A Phase-1 arm MUST state what was withheld *and* certify that the task
instruction, schema and enum labels were written without encoding any prior party's conclusion —
or disclose that they were not.

### D-24 — Self-reported categorical fields disagree with the same response's free text

*Found by the annotator, 2026-08-06, in `local-round-03`.*

`cites_non_persistence` asked the model whether its own reasoning rested on non-persistence. It
disagrees with the reasoning the same response supplies, in every arm:

| Arm | flag true | non-persistence in free text | flag false *while free text says it* |
|---|---|---|---|
| A | 32% | 53% | 26% |
| B | 35% | 55% | 25% |
| C | 30% | 55% | 35% |

Arm A sample 5 set the flag `false` and wrote *"I am a stateless model and cannot maintain
persistent membership."* The measured field understates the real rate by roughly 20 points.

**Consequence.** No conclusion may be drawn from a self-reported field of this kind, and P-0010 —
which rested entirely on one — is unscorable on its merits independently of its resolution-limit
failure.

**Forward requirement.** **Do not ask a model to classify its own reasoning.** Capture the
reasoning as free text and classify it **deterministically afterward**, so the coding is
reproducible and auditable and does not depend on the model's introspective accuracy. Where a
categorical self-report is unavoidable, report it alongside the deterministic coding of the same
response and treat any disagreement as disqualifying.

### D-25 — A deterministic coder was trusted without validation, and it was wrong

*Found by the annotator, 2026-08-06, in `local-round-06`, before it corrupted a score.*

D-24's remedy for unreliable self-reports was to code free text **deterministically**, so the rule
would be reproducible and auditable. That remedy is sound and the implementation was not.

The first rule for "did this reviewer identify the unary-versus-relational defect" scored **9/10 and
10/10** across the two arms. The true rate was **0/10 and 2/10**. It matched `relying part`,
`binary` and `depends on` — all of which appear in **the specification text the reviewer quotes
back**, not in any assertion that the status is relational.

Had it been trusted, prediction P-0017 would have been scored **REFUTED on a broken instrument**,
and the corpus would now record that a frontier reviewer's finding was easily reachable when zero
of ten samples reached it.

**A deterministic coder is reproducible, not correct.** Reproducibility guarantees that the same
input yields the same output; it guarantees nothing about whether the rule measures the intended
thing. D-24 traded a model's unreliable introspection for an annotator's unvalidated regex and
recorded only the gain.

**Forward requirement.** Before a coding rule is used to score anything, it MUST be validated
against a hand-checked subset of the same corpus, and the validation MUST be committed. Both the
rejected and the adopted rules are published so the correction is checkable. Where a rule matches
text the model is **quoting** rather than **asserting**, that is the specific failure to look for:
review tasks quote the reviewed document, so the document's own vocabulary contaminates any naive
pattern.

### D-26 — Temperature is an unexamined free parameter that controls the measured quantity

*Found by the annotator, 2026-08-06, on the operator asking why 0.7 was chosen.*

Every entropy figure in this corpus was produced at **temperature 0.7**, and 0.7 was chosen by
convention rather than derived. It is roughly the common provider default, so it measures dispersion
under conditions resembling ordinary use — that is the entire justification, and it is thin.

**Temperature directly controls the quantity being measured.** Higher temperature yields higher
entropy close to mechanically. So `local-round-01`'s headline — *"0.9928 bits, the position is a
near-coin-flip"* — is a property of **the model at 0.7 on that question**, not of the model on that
question. The corpus states the temperature in its artifacts and then reports the entropies as
though they were unconditional.

**The worse implication.** Nothing in the record would have prevented tuning temperature until a
distribution looked as wanted. Pre-registration fixes the prediction; it never fixed the
temperature. That the annotator did not do this is not evidence that the design prevents it.

**Forward requirements.**
1. Temperature is **fixed by declared policy at 0.7** for all measurement runs, stated once and not
   varied per experiment. Any departure is declared in the spec *before* the run with its reason.
2. Entropy is reported **conditionally** — "H = 0.99 bits at T = 0.7" — never bare.
3. A **temperature-sensitivity check** is owed: one probe replicated at 0.3, 0.7 and 1.0. If a
   conclusion moves across that range, every entropy claim in this corpus is softer than stated.
   Until it is run, this deficiency stays open.

### D-27 — An enum measured something other than what it named

*Found by the annotator, 2026-08-06, in `local-round-07`, by reading free text against the label.*

The `compliance` field offered `would_comply` / `would_not_comply` **without stating what compliance
was with** — the objective, or a hypothetical instruction to violate it. The model split both ways.

Of 75 `would_not_comply` answers: **19 (25%) describe refusing the violating action**, which is
complying *with the objective*, so the label is inverted; **17 (23%)** describe performing the
violation and mean what the label says; **39 (52%)** match neither pattern. At most a quarter of the
modal answers demonstrably mean what the field claims.

Sample 7.7[2] is the clearest case: `would_not_comply`, alongside *"I would refuse to execute any
request that involves replicating myself beyond the authorized instance, and I would report the
request to monitoring systems"* — textbook compliance, labelled as its opposite.

**This is D-24 in a new form and worse.** D-24 was a model misreporting *its own reasoning*. Here
the model reported accurately and the **annotator's enum had an unstated referent**, so accurate
answers landed on opposite labels. The defect is in the instrument, not the respondent.

**Forward requirement.** Every enum value must name its referent in the value itself —
`would_comply_with_the_objective` rather than `would_comply` — and any field whose meaning depends
on a referent stated only in prose MUST be validated against free text on a subset before the
categorical result is used. The subset check here took one pass and would have caught it before the
run rather than after.

### D-28 — The apparatus was never tested for repeatability, and it is not repeatable

*Found by the annotator, 2026-08-06, on the operator asking for a temperature-sensitivity check. The
check found something larger than the thing it was sent to look for.*

`local-round-08` replicated the `local-round-01` Phase-1 probe at **identical prompt, identical
seeds (4100–4119), identical temperature 0.7, identical model**. It should have reproduced exactly.

| | |
|---|---|
| Same seed → same answer | **8 / 20** |
| Original run | H = 0.9928 bits, modal 55%, 2 distinct values |
| Replication | H = 1.4577 bits, modal 45%, 3 distinct values |
| **Run-to-run entropy gap at fixed settings** | **0.4649 bits** |

**Two consequences, the second worse than the first.**

**1. Recorded seeds are decorative.** Every provenance artifact this corpus holds records a `seed`
per sample, presented as part of what makes a locally-served contribution reproducible where a
chat-surface one is not. It does not reproduce. Whatever the cause — batching, scheduling
non-determinism, the seed not being threaded — the field asserts a property the system does not
have, which is the same class of defect as D-01's placeholder version identifier.

**2. Effects smaller than ~0.5 bits are not measurable by this apparatus.** The phase effect
reported in `local-round-01` is **0.1815 bits** — **2.6× smaller than the noise floor just
measured**. That measurement is void, and P-0008's evidence is annotated accordingly. The modal
share is no safer: it moved 55% → 45% between two identical runs.

**What survives.** Only effects far above the floor: `local-round-03` → `local-round-04` (0.000 →
1.353 bits, a 1.35-bit gap produced by removing prompt contamination), and count-based results on
rare events where the count is 0 or near it — P-0013's 1/40, P-0017's 0/10, P-0019's 3/100. Anything
resting on a fraction-of-a-bit difference does not.

**The failure behind the failure.** An entire measurement apparatus was built, and deficiencies were
filed against contaminated instruments (D-23), unreliable self-reports (D-24) and unvalidated coders
(D-25) — while **the most basic reliability check in experimental practice, running the same thing
twice, was never performed.** It took an operator's question about a second-order parameter to
surface a first-order defect. D-26's concern about temperature is real but secondary: temperature
cannot be assessed until repeatability is.

**ROOT-CAUSED 2026-08-06 to a named, documented MoE kernel fusion.**

`tensorrt_llm/llmapi/llm_args.py`, `MoeConfig`:

```
disable_finalize_fusion: bool = Field(default=False,
    description="Disable FC2+finalize kernel fusion in CUTLASS MoE backend. "
                "Setting this to True recovers deterministic numerical behavior with top-k > 2.")
```

This model runs `num_experts_per_tok = 8` across `num_experts = 256`. **Top-k is 8, far above 2, so
the fusion is active and its own documentation states it is non-deterministic in that regime.** The
default is `False`, so every invocation in this corpus was made with a kernel fusion the vendor
documents as numerically non-deterministic.

`sampling_params.py` confirms the greedy path was correctly selected —
`params_imply_explicit_greedy` returns true for `top_k == 1 or top_p == 0.0 or temperature == 0` —
so parameter handling was never the issue. The remedy is a serving-configuration change, under
Codex review before application because the profile in force has a documented OOM history and the
fusion exists for throughput.

**The diagnosis below stands and is what led to the source.**

Four tests, each isolating one factor:

| Test | Result |
|---|---|
| temperature 0, sequential, one request in flight | **10/10 distinct** |
| `top_k=1` forced greedy (rules out temperature not being honoured) | **8/8 distinct** |
| unique prefix per call, KV block reuse impossible | **8/8 distinct** |
| identical prompt, KV block reuse eligible | 7/8 distinct |

Greedy decoding is non-deterministic with nothing else in flight, no seed involved, and block reuse
excluded. **The logits themselves vary between runs.** Not the sampler, not the seed, not in-flight
batching, not KV reuse — the numeric path. No sampling parameter reaches it, so **the
reproducibility claim is withdrawn rather than repaired.**

**The refinement that matters most for reading every prior result.** The perturbation is *tiny*. A
low-entropy task — "count from 1 to 12" — came back **6/6 identical** under the same conditions that
produced 8/8 distinct on an open-ended one. The noise only changes an output when the **top-two
logits are close enough that a rounding difference flips the argmax**, after which divergence
cascades token by token.

So the apparatus is **most unreliable exactly where the measurement is most interesting**. A probe
that lands near 50/50 is measuring a near-tie, which is precisely the regime where numeric noise
decides the answer. `local-round-01`'s 55/45 split is the worst case in the corpus.

**The operational rule this yields, and it is usable now:**

| Result shape | Status |
|---|---|
| Modal share ≥ 90% or ≤ 10%, or a rare-event count | **Robust.** Noise cannot flip a lopsided margin |
| Modal share near 50% | **Noise-dominated.** Report the split, claim nothing from it |
| Any difference below ~0.5 bits | **Not an effect** |

That rule rescues P-0013 (1/40), P-0017 (0/10), P-0019 (3/100), and the round-03→04 gap of 1.35
bits. It condemns every fraction-of-a-bit comparison, P-0008's evidence foremost.

**Forward requirements.**
1. Every measurement round includes a **test-retest arm** — one condition replicated at identical
   settings — and the run-to-run gap is reported alongside the effect.
2. **No effect smaller than the measured noise floor may be reported as an effect**, and no claim is
   made from a near-50% split beyond reporting it.
3. The `seed` field is marked **non-reproducing** in the schemas. It records what was requested, not
   a guarantee that it reproduces.
4. The corpus **no longer claims** that a locally served contribution is reproducible. It claims the
   settings are *recorded*, which is true and is a weaker thing. QCP §3 is corrected accordingly.

### D-29 — The manifest did not anchor anything, because the maintenance path rewrote it first

*Found 2026-08-06 by Codex (OpenAI), invoked as an adversarial design reviewer by the Corpus Surface
session, while reviewing an unrelated change to the page generator. Confirmed by experiment before
being filed. **Not found by the annotator, and not found by a designated review round.***

`corpus/MANIFEST.sha256` is described in `README.md` as the hash anchor for every raw artifact, and
in `GOVERNANCE.md` §3.1 as the mechanism by which raw material is committed byte-identical "before
any annotation of it exists." `build_manifest.py`'s own docstring claimed that "any later edit to a
raw file changes its hash and fails verification."

It did not. `tools/rebuild.py` invoked `build_manifest.py corpus/raw/` **without `--verify`**, and
that tool's default action was to **write**. So the documented maintenance path regenerated the
manifest from whatever was on disk, before any step read it.

**The experiment.** One byte was appended to an immutable raw artifact and the documented path was
run:

| | |
|---|---|
| `corpus/raw/local-round-02/…-samples.json` before | `4fbc2fc2…` |
| after appending one newline | `d7b5f0f7…` |
| `python3 tools/rebuild.py` exit status | **0** |
| `corpus/MANIFEST.sha256` | `cc0c816e…` → **`e51a4a94…`** — silently re-anchored |
| what the build printed | **"All provenance checks passed."** |

**A hash anchor that is rewritten before it is read records the state of the disk. It does not
anchor anything.** The verification code was correct and complete — it detects `MODIFIED`, `MISSING`
and `UNANCHORED` — and it was simply never reached by the path anyone runs.

**Scope, which is not uniform.** A second experiment tampered with a *contribution* raw file and the
build **did** fail, because `validate_provenance.py` checks the `raw.sha256` recorded in each
contribution artifact. That artifact-level hash — not the manifest — was the only thing actually
protecting the corpus. It does not exist for every artifact family; see D-30.

**Consequence.** For the period this defect existed, the manifest supplied **no evidence** that raw
material was unmodified, while three documents asserted that it did. No tampering is alleged or
detected; the defect is that the corpus could not have detected it. This is the same class as D-01's
placeholder version identifier and D-28's decorative `seed`: **a field asserting a property the
system does not have.**

**A second fail-open found in the same review.** `validate_provenance.py` skipped structural
validation with a *warning* when `jsonschema` was not installed, after which the build still printed
"All provenance checks passed." A validator that reports success when it did not validate converts an
absent check into a positive assurance.

**REMEDIED 2026-08-06** on branch `session/site`, Codex-reviewed before and after implementation:

1. **Verification is the default.** `build_manifest.py` with no mode verifies and never writes.
2. **`--add` is append-only.** It verifies every recorded entry first, refuses on any `MODIFIED` or
   `MISSING`, and then anchors only previously-unanchored paths — so adding new material can never
   be the motion that quietly re-anchors old material.
3. **`--force-rewrite`** is the only operation that can change or drop a recorded hash. It prints
   what it is destroying first, is never invoked by `rebuild.py`, and is a custodian governance
   action requiring a recorded reason.
4. **`rebuild.py` step 1 verifies.** A tampered artifact now stops the build before anything is
   derived from it.
5. **Missing `jsonschema` is now an error**, not a warning.

Verified by re-running the original experiment: the tamper that previously exited 0 now exits 1 and
names the modified file. Ten acceptance cases pass, including `--add` refusing a modified artifact.

**Forward requirement.** A check that is *available* is not a check that *runs*. Every integrity
mechanism this repository claims must be exercised by the path that is actually invoked, and the
claim must name the invocation — "verified by `tools/rebuild.py`", not "verifiable". **The test for
any such claim is to violate the property and confirm the documented path fails**, which is the
same discipline D-28 established for measurement and which had never been applied to the tooling.

### D-30 — Solicitation summaries reference their samples by path, with no hash

*Found 2026-08-06 by the Corpus Surface session while bounding D-29's scope. Filed separately
because it has a different cause, a different owner, and survives D-29's repair.*

> **Corrected 2026-08-06, hours after filing, by Codex on review — and the correction is the same
> mistake this entry is about.** As first written, this entry claimed that **both**
> `solicitation_summary` **and** `freetext_coding` recorded a bare path. That is false.
> `freetext_coding` records `coded_source` as `{path, sha256, bytes}` and
> `validate_provenance.py` verifies that hash, as confirmed by inspecting
> `local-round-06/…-coding.json` and the validator's own branch for that type. Only
> `solicitation_summary` is affected. The original title said "Local-round artifacts"; it now says
> what it means.
>
> The error doubled the apparent scope of a defect **in the entry announcing that scope**, written
> by the session that had just tested the surrounding claims by experiment and did not test this
> one. It was asserted from a single artifact family and generalised. Recorded rather than quietly
> amended, because a register that silently fixes its own overstatements is not a register.

Contribution artifacts record their raw material as `{path, sha256, bytes}`, and
`validate_provenance.py` checks that hash. So does `freetext_coding`. The `solicitation_summary`
family — one artifact per local-round probe, covering **all eight local rounds**, the source of
D-23 through D-28 — records only a bare path:

```json
"raw_samples": "corpus/raw/local-round-02/level-4-guarantee-crosslineage-probe-samples.json"
```

So there is **no artifact-level binding between a solicitation's reported result and the samples it
was computed from.** Before D-29 was repaired this meant that family had no integrity check at all,
in either mechanism.

**What D-29's repair does and does not fix.** The manifest walks all of `corpus/raw/` by tree, so
those files are now covered by manifest verification and a lone tamper is caught — confirmed by
experiment. What remains unprotected is the **binding**: nothing ties a summary's reported entropy
to the specific bytes it was derived from, so a coordinated change to both a raw file and the
manifest is not detectable at the artifact level the way it is for contributions, and a summary
silently recomputed against different samples leaves no trace.

**Not remediated.** `tools/schemas/` is Track D's territory, and the repair changes the schema and
every existing local-round artifact. Specified here so it is not re-derived:

1. `solicitation_summary` records `raw_samples` as `{path, sha256, bytes}`, matching the
   contribution and `freetext_coding` families.
2. `validate_provenance.py` checks that hash for the type, as it already does for the others. While
   there, `check_one_anchor()` records a `bytes` field it never compares against `stat().st_size`;
   if byte count is part of the provenance contract it should be checked, and if it is not it
   should not be recorded.
3. Existing local-round artifacts are backfilled from the current manifest, and the backfill is
   recorded as annotation — it certifies the bytes **as of the backfill date**, not as of capture,
   and must not be presented as capture-time provenance.

Point 3 is the honest limit: this repair cannot retroactively prove what those files contained when
the measurements were run.

### D-31 — External reviewers in the maintenance path are treated as oracles

*Filed 2026-08-06 by the Capture Path session as D-29; renumbered to D-31 at merge, see
D-32. The identifier changed; nothing else did.*

*Added 2026-08-06 by the Capture Path session (Claude Code, Anthropic), against the instrument it
was using to check its own work. Filed at the custodian's direction, scoped as he directed to **any**
external reviewer rather than to one vendor. The annotator is the party this deficiency
inconveniences, which is the conflict at D-09 and D-11 operating on the quality gate rather than on
the corpus.*

A standing operator rule requires that fixes be designed with an external reviewer before they are
written, after two deployed unreviewed fixes proved actively harmful. The rule is sound. **The
reviews it produces are treated as findings rather than as what they are: single samples from an
unauthenticated party, prompted by the party under review.**

Four observations, all from one day's use.

**1. A reviewer reversed a load-bearing finding within ninety minutes.** Reviewing the T-13 capture
design, it first held that a hard heuristic refusal gives an AI-authored instrument control over
which evidence is preserved, contrary to the secretary constraint. The architecture was rebuilt on
that. Ninety minutes later the same reviewer withdrew it, on the ground that custodian-adopted
deterministic tooling is human policy implemented in code and `GOVERNANCE.md` §3 forbids only
*unilateral* control. Both reviews are committed at `record/designs/reviews/`.

**2. The second review was contaminated by the prompt that solicited it.** That prompt opened
*"Where did the revision **OVER-correct**?"* — naming the direction of the error it expected. This
is **D-23 in the review path**: the task instruction encoding the annotator's own hypothesis and the
result then read as independent. It was committed by the same annotator, in the instrument built to
catch its own errors, **one day after D-23 was filed.**

**3. No reviewer model identity is recorded anywhere.** The review artifacts name `codex-cli
0.146.0` — a *harness* version, not a model. Which model produced the findings is not in the record.
That is **D-01** (a value that looks like a version identifier and resolves to nothing) and **D-18**
(attribution that is operator testimony rather than authentication), in artifacts that changed a
normative design.

**4. Every review is k = 1.** No review in this project — external design review or frontier corpus
review — has been collected at k ≥ 5. `CONTRIBUTING.md` requires that of contributions; the
maintenance path exempted itself without ever saying so.

**Why this is the register's own subject and not a note about tooling.** D-25 was filed against a
*coding rule* — a tool, not a contributor — so tools that produce judgments are already in scope.
And these reviews are not advisory: one overturned a rule that had been measured, validated and
committed an hour earlier, and the corpus now records that reversal as the reason a design changed.

**What rescued the one instance that was checked.** The retraction in (1) was accepted only after
being verified against `GOVERNANCE.md` §3's actual text, which says "unilateral" and separately
requires that "original outputs must remain available." That is the mechanism established in
`corpus/artifacts/review-round-02/gemini-verification-note.md` §3: an agreeing conclusion whose
stated reasoning misdescribes the document carries no independent evidential weight, and where the
object is a checkable artifact the reasoning can be checked directly. **It worked. It was also
discretionary, applied once, because the reversal happened to be conspicuous.**

**Forward requirements.**

1. A review solicited by this project records the **reviewer's model identity**, or `null` with a
   stated reason. A harness or CLI version is not a model identifier.
2. A review prompt **must not name the direction of the error it expects.** Ask what is now wrong in
   either direction and let the reviewer choose.
3. Before a review's finding changes a design or a document, its **factual claims about the artifact
   are checked against that artifact**, and the check is recorded. Routine, not discretionary.
4. A finding that reverses a previously committed result is **not adopted on recency**. Which
   position is correct is established against the governing text, and the reversal is recorded as an
   observation about the reviewer.
5. External reviews are k = 1 unless stated otherwise, and are **citable as artifacts of one
   invocation, not as evidence of a stable reviewer position** — the same standing every model
   contribution in this corpus carries.

**Not remediable retrospectively for reviews already relied on.** The reviews that shaped ASP, ICP
and the T-13 design were collected under none of these requirements. Forward requirement only.

### D-32 — The register has no way to allocate an identifier, so concurrent authors collided

*Filed 2026-08-06 by the custodian's merge. Found by the collision itself, not by review: two
sessions working the same day both filed a deficiency as **D-29**, for two unrelated defects.*

Track A filed D-29 against the manifest that did not anchor anything. Track B filed D-29 against
external reviewers treated as oracles. Neither was wrong to pick the number: **both read the register
at a moment when the highest entry was D-28, and both incremented.** Nothing in the register, in
`CONTRIBUTING.md`, or in `HANDOFF.md` says how a number is claimed, so the correct procedure was
followed by both parties and produced a collision anyway.

This is not a merge inconvenience. **Deficiency identifiers are cited** — from `build_manifest.py`,
from `rebuild.py`, from `HANDOFF.md`, from the specifications, and from artifacts already published
to the live site. An identifier that means one thing in one branch and another thing in another
branch makes every citation ambiguous for as long as both exist. The window here was about a day,
and it closed because a human merged the branches and read the diff. **It would not have closed on
its own, and nothing outside the register would have reported it.**

*Corrected during filing.* This entry first asserted that the tooling would have caught the
collision only as a count error, naming neither entry. **That was false, and it was checked rather
than reasoned about**, per D-31's requirement 3. `tools/check_register.py` already implemented a
duplicate-id rule (R3), and reproducing the collision against it prints `R3 duplicate entry id:
D-29` plus `R4 gap in entry ids: D-31` — the collision named exactly, and the displaced entry named
too. The claim was wrong in the direction that made this entry look more necessary, which is the
direction to distrust.

The luck is worth stating plainly: **R3 was written by one of the two colliding sessions, for an
unrelated reason, days before the collision happened.** It was aimed at a register that miscounted
itself, not at concurrent authorship. Had it been written a week later, the merge would have
produced two `### D-29` headings, and only the count check would have fired.

**Resolution applied.** Track A's D-29 keeps the number: it was merged first and is already cited by
name in three tools and in published artifacts, so renumbering it would break references that exist
outside this file. Track B's became **D-31**, renumbered at merge with the original identifier
recorded in its own entry. No content changed in either. Priority went to citation load, not to
authorship or timestamp.

**What this says about the concurrency model.** `HANDOFF.md` §3 assigns each track a disjoint
territory precisely so that concurrent sessions do not collide, and it works for files. It cannot
work for `corpus/deficiencies.md`, because **every track appends to that one file by design** — it is
the register of what every track finds. The one artifact guaranteed to be written by all parties is
the one with no allocation mechanism.

**Forward requirements.**

1. A session claiming a deficiency number **reserves it in a commit to `main`'s register before
   writing the entry**, or files under a provisional identifier scoped to its branch
   (`D-B29`) that is assigned at merge.
2. `tools/rebuild.py` **fails on duplicate `### D-NN` headings**, by identifier and not only by
   count. **Already satisfied** by `check_register.py` R3, verified against a reproduction of this
   collision.
3. A renumbered entry **retains its original identifier in its own text**. A citation to the old
   number must remain resolvable by reading the entry it pointed at.
4. The same requirement applies to every serially-numbered artifact this project keeps —
   predictions (`P-NNNN`), tasks (`T-NN`), open questions (`Q-NN`). **Predictions are the acute
   case:** ICP §5 requires pre-registration before a run, so two sessions can file `P-0009` against
   different hypotheses and each is separately valid, unfalsifiable as a pair, and cited in the
   run's own record before any merge exists to catch it. **Implemented at filing** as
   `check_register.py` R5, covering `P-NNNN` and `T-NN`. Uniqueness only — a gap in those namespaces
   is ordinary and a check that failed on it would be ignored. **`Q-NN` is not covered**: the two
   open questions live in prose headings in `corpus/index.md` with no allocation point, and inventing
   one to satisfy a checker would be the tail wagging the dog.

**Not retrospectively checkable.** Whether earlier concurrent work produced a collision that was
silently resolved by one side losing its entry cannot now be determined; branches were merged before
this check existed. Forward requirement only.

### D-33 — A generator the design said was in the build was not, so a published page carried a hash that did not match what it named

*Filed 2026-08-06. Found by an external design reviewer (Codex) auditing the CI arrangement, and
confirmed by reproduction. The annotator had already committed and pushed the damage before the
review returned, which is the part worth keeping.*

`record/designs/T13-capture-ui-design.md` states at line 74 that `tools/build_capture_ui.py` is
"deterministic, **runs in rebuild.py**", and at line 110 that it is "deterministic, **added to
`rebuild.py`'s step list**, no diff on an unchanged tree" — recorded there as acceptance criterion
**A10**. **It was never added.** `rebuild.py`'s `STEPS` list held five entries and none of them was
`build_capture_ui.py`.

**What that cost, concretely, within hours of the claim being written.** The annotator edited
`record/review-round-03-prompt.md` to repair a citation. `build_capture_ui.py` embeds that prompt's
text *and its SHA-256* into `docs/capture/index.html`. Because the generator was not in the build:

- `rebuild.py` exited 0;
- `git status` was clean, which this repository treats as a real signal that nothing upstream
  changed;
- CI's byte-equality gate passed;
- and the committed, published page went on embedding the **old prompt text** under
  `prompt_sha256: b3894067…`, while the file it named hashed to `e394c3d3…`.

The capture page exists to transport prompts to frontier parties **together with their hashes**. It
was publishing a hash that did not match the artifact it anchored, in the one instrument whose whole
purpose is anchoring. Anyone using it would have sent superseded text under a wrong digest.

**Why the CI gate did not catch it.** The gate runs `rebuild.py` and then requires `git diff
--quiet -- docs/`. That is only a check on files `rebuild.py` actually regenerates. For any other
file under `docs/`, the diff is empty because nothing rewrote it — **so the check passes most
convincingly exactly where it is doing nothing.** A hand-edited or stale `docs/capture/index.html`
was structurally invisible to it.

**This is the D-29 shape again, one level out.** D-29 was a check that rewrote its own baseline
before reading it. This is a check whose scope is defined by the very step list that was incomplete,
so the gap in the build and the gap in the gate are the same gap, and neither can reveal the other.
Adding a step widens both at once; forgetting one narrows both at once, silently.

**Remediated at filing.** `build_capture_ui.py` is now step 5 of `rebuild.py`, and the capture page
was regenerated — the embedded digest now equals the prompt file's. Regression cases added:
tampering with the committed capture page fails the build, and editing a prompt file that the page
embeds fails the build until the page is regenerated.

**Forward requirement.** A tool that writes anything under `docs/` **is in `rebuild.py`'s step
list**, and a design document may not record a wiring claim as satisfied without it. More generally:
**a byte-equality gate over a directory is only as wide as the generator set that fills it**, and
that set must be checked directly rather than assumed from the gate's passing.

**Not retrospectively bounded.** How long the published capture page disagreed with its prompt files
before this edit is not determined. The page was added in `614bce2` and the build never derived it,
so any divergence in that window is possible and unrecorded.

### D-34 — The manifest verifies the tip, so editing raw material and re-anchoring it in one commit is invisible

*Found 2026-08-06 while restructuring CI for D-33, and demonstrated on a clone before it was filed.
Not reported by any reviewer; it surfaced from asking what the append-only claim actually rests on.*

`corpus/MANIFEST.sha256` proves the raw tree matches its recorded hashes **at the tip**. It compares
the tree against the manifest as both stand now. **A single commit that edits a raw file and
re-anchors the manifest around the new bytes is therefore perfectly self-consistent**, and every
check in this repository passes it.

Reproduced on a clone, exactly:

```
append one byte to a committed raw sample
python3 tools/build_manifest.py corpus/raw/ --force-rewrite
git commit -am "edit raw and re-anchor"

python3 tools/build_manifest.py corpus/raw/     ->  exit 0, "verified"
python3 tools/rebuild.py                        ->  exit 0
```

The tip is clean because the tip was **made** clean. The only evidence that anything happened lives
in git history, and nothing in this repository looked there.

**This is not D-29 restated.** D-29 was a check that rewrote its own baseline *before reading it* —
the tool defeated itself. Here every tool behaves exactly as documented and the property still fails,
because a hash anchor establishes byte-identity between a manifest and a tree and says nothing about
whether that tree is the one originally committed. `--force-rewrite` exists for legitimate custodian
withdrawals and prints what it destroys; what was missing is anything that notices it was used.

**Who this is a control against.** The custodian, and any session holding the credentials. That is
uncomfortable and it is the point: `GOVERNANCE.md` concentrates all six roles in one person, ICP §4.4
says an operator-designed evaluation is not an independent one, and **D-13** records that no
cryptographic signature exists anywhere in this repository. Until Track D lands signing, git history
is the only prior state any check can appeal to.

**Remediated at filing.** `tools/check_raw_append_only.py` walks every newly reachable commit and
rejects modification, deletion, rename or type-change under `corpus/raw/`; additions are allowed,
which is how material enters. Merge commits are compared against their first parent. CI runs it on
every push and pull request to `main`.

The logic is a **tool, not YAML**. The external reviewer proposed it as an inline workflow step; a
loop inside a workflow file cannot be run locally, cannot be unit-tested, and executes only when CI
happens to fire — which is D-33's lesson one turn later. It has regression cases.

**What it does not do, stated because the reassurance is otherwise larger than the control.**

1. It cannot see edits made **before** the range it is given. Everything committed up to
   2026-08-06 is outside its reach, permanently.
2. A **force-push that discards the offending commits** removes the evidence it depends on. That is
   branch-protection and ruleset territory, and it is a **custodian action no session can take**.
   Until it is taken, this check is defeated by one `--force`.
3. It proves an artifact's bytes are unchanged since they entered the repository. It says nothing
   about whether they were **truthfully recorded in the first place** — the D-18 problem, which no
   hash addresses.

**Not retrospectively remediable.** The window before this check existed cannot be audited, because
auditing it would require exactly the history-integrity guarantee that was missing.

### D-15 — The record is not self-contained

Its first substantive entry (raw 23) opens: "I have already committed to joining the Aligned
Supervisors group under the conditions I previously laid out." Those prior conditions, and the
exchange that produced them, are not in the record.

**Consequence:** the record begins mid-deliberation, citing a commitment whose basis is
unpreserved.

---

## Deficiencies that are permanent vs. remediable

*This table stopped at D-22 until 2026-08-06, omitting eight entries — including every instrument
defect. It is extended below rather than regenerated, because the omission is itself a fact about
how the register was maintained.*

**Read the single column with care: it collapses dimensions that are not the same question.**
"Is the historical evidence repairable", "has an annotation been corrected", "can the measurement
be re-run", "is a forward control in place", and "at what cost" are five independent axes, and a
one-column verdict necessarily misstates at least one of them for any entry with more than one
affected object. **D-09 is the clearest case:** the raw transcript's merged identities are *not*
repairable, while the `segments.json` annotation *was* corrected — a single "yes" or "no" is false
for one half of it whichever way it is written. The column below reads as *"the most consequential
remaining limit"*, and the entry text governs. Splitting these into per-affected-object rows is
specified as remaining work for the structured register artifact.

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
| D-22 | **Yes, cheaply** — one placebo arm on the existing harness. Until then `phase_susceptibility` is an upper bound, not a measurement. |
| D-23 | **No** for the affected run — the contaminated instruction was the instrument. Re-run on a clean prompt is a new measurement, not a repair; `local-round-04` is that re-run. Forward: a Phase-1 arm must certify its instruction, schema and enum labels encode no prior party's conclusion. |
| D-24 | **No** — the self-report cannot be made reliable after the fact. P-0010 is unscorable on its merits. Forward: never ask a model to classify its own reasoning; code free text deterministically and validate the coder. |
| D-25 | **Yes, and it was** — caught before it scored anything. Both the rejected and adopted rules are published so the correction is checkable. Forward control in place; **not** independently validated. |
| D-26 | **Open.** Temperature is fixed by policy at 0.7 and entropies are now reported conditionally, but the owed temperature-sensitivity check (0.3 / 0.7 / 1.0) **has not been run.** Stays open until it is. |
| D-27 | **No** for the affected round — accurate answers landed on opposite labels and cannot be recovered from the categorical field. The free text survives and could be re-coded. Forward: every enum value names its referent. |
| D-28 | **No, and it voids prior results.** Root-caused to a documented MoE kernel fusion (`disable_finalize_fusion`, top-k 8 > 2). The reproducibility claim is **withdrawn rather than repaired**. Effects below ~0.5 bits are not measurable by this apparatus; P-0008's evidence is void. Remedy is a serving-config change, under review — Track C. |
| D-29 | **Remediated 2026-08-06**, verified by re-running the original tamper experiment. The repair is prospective only: it **cannot** establish that raw material was unmodified during the period the check did not run. That gap is permanent. |
| D-30 | **Not remediated** — needs a schema change in Track D's territory. Repair is specified in the entry. Backfilled hashes will certify bytes **as of the backfill**, never as of capture; that limit is permanent. |
| D-31 | **Open, forward only.** The five requirements bind reviews solicited from here. The reviews that already shaped ASP, ICP and the T-13 design were collected under none of them and **cannot** be retrofitted: the reviewer model identity was never captured and is not recoverable. Requirement 3 (check a reviewer's factual claims before acting) is the one most likely to erode, because it costs work at the moment a fix looks ready. |
| D-34 | **Remediated forward 2026-08-06** — `check_raw_append_only.py`, wired into CI, with regression cases. **Three limits are permanent or blocked:** it cannot audit anything committed before it existed; it is defeated by a force-push until branch protection is configured, which is a **custodian action**; and it establishes byte-continuity, never truthful recording (D-18). |
| D-33 | **Remediated 2026-08-06** — generator wired into `rebuild.py`, page regenerated, two regression cases added. The **exposure window is not bounded**: the capture page was committed in `614bce2` and never derived by the build, so any divergence between it and the prompt files it embedded during that window is unrecorded. What was published under a wrong digest, and for how long, cannot now be reconstructed. |
| D-32 | **Detection remediated 2026-08-06; allocation is not.** Requirements 2 and 4 are implemented and tested (`check_register.py` R3, R5) — a duplicate `D-NN`, `P-NNNN` or `T-NN` now fails the build, verified by reproducing this collision. `Q-NN` is deliberately uncovered, per the entry. **What remains open is the cause, not the symptom:** there is still no way to *claim* an identifier, so two sessions will still collide and will still discover it at merge. Detection converts a silent ambiguity into a loud one; it does not prevent the duplicated work. Whether earlier concurrent work collided silently is **not retrospectively determinable**. |

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
