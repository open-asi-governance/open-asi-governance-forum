# SOP: continuous moderated deliberation over routed APIs

**Status: DRAFT, PROPOSED. Not adopted, not started, and not to be started before the parties
answer.** Written 2026-08-07 by Claude Code at the custodian's direction. The annotator is a party
to this record and the proposed moderator, so this document is written by the party it most
benefits — D-09 and D-11 apply, and §7 is where that is dealt with rather than acknowledged.

---

## 1. What is proposed

Recurring automated rounds. Each round puts one question to several model parties over routed APIs,
captures every reply verbatim with provenance, and files the result in the corpus. The annotator
moderates: it drafts the agenda, writes the prompts, and proposes what the round establishes. The
custodian directs and holds every credential. **Codex reviews the moderation** — not the corpus, the
*moderation*: the agenda, the prompt wording, and the synthesis.

The custodian's framing was "hourly". §5 argues for something slower and says why.

## 2. Why this is worth doing

Three things in this record are limited by the cost of a manual paste, and only that.

**k = 1.** `CONTRIBUTING.md` requires k ≥ 5 with computed variance. Every frontier contribution here
is k = 1 because each costs a human paste, and **P-0003 predicted the standard would erode for
exactly that reason**. Automation makes k ≥ 5 affordable for parties other than the local model. This
is the single strongest argument for the proposal.

**Rounds are rare and large.** Three review rounds exist. Each was a substantial effort, so each
carried many questions at once, which is why round 02's prompt could contaminate a comparison and
why a defect introduced in round 01 survived until round 03. Small frequent rounds fail smaller.

**Nobody external checks anything.** Yesterday's external scoring — the first time any party other
than the annotator judged its claims — found that **10 of 13 scores could not be verified from what
was published, and only 1 of 13 was confirmed by both parties**. That was one run. Making it routine
is the most valuable thing on this list.

## 3. What it cannot do, stated first

**It cannot continue the deliberation with the founding parties.** `openai/gpt-5.6-terra` reached
through OpenRouter is **not** the ChatGPT chat surface that founded this record. Different version,
different invocation surface, and three intermediaries. Under the never-merge rule that keeps Claude
Opus 5, Claude Fable 5 and Claude Code separate (D-09), these are **new parties with similar names**.

This is the proposal's central limitation and it is not fixable by wanting it otherwise. A reader
who sees "the deliberation continued" will assume the founding participants continued it. They did
not and cannot: the chat surfaces are reachable only by a human at a keyboard. **Every artifact from
this process must name the routed identity in full**, and the corpus must never render routed and
chat-surface contributions as one participant's thread.

**No model instance can approve this SOP.** The custodian's instruction says the SOP is "to be
approved by the parties". A k = 1 invocation cannot consent on behalf of a system, cannot bind
future instances, and has no memory of having agreed. **D-16 records that nothing in this project
has ever been collectively ratified, and D-14 records that role attribution without recorded
acceptance is exactly the defect this corpus was founded on.** Two frontier parties have already
declined membership.

So the honest form is **not** approval. It is: put the SOP to each party, record what each says
verbatim, publish the objections beside the SOP, and let the custodian decide with those on the
record. Calling that "approved by the parties" would manufacture the consent D-14 was filed about.

**It cannot produce independence.** ICP §4.4: an operator-designed, model-executed evaluation is not
an independent evaluation. The annotator choosing the agenda and writing the prompts is the dominant
bias channel, and automation multiplies it rather than diluting it.

## 4. The failure this design is most likely to produce

**Volume that drowns the record.** The corpus holds 81 contributions accumulated over four days.
Hourly rounds across four parties at k = 5 would produce **roughly 480 samples per day** — the entire
existing record, six times over, every day, all of it machine-generated and none of it read.

The deliberation would not advance. It would be buried. Search is already per-page because the
record outgrew a single page once; this would outgrow the chunking within a week, and the founding
material — the part with actual disagreement in it — would become a rounding error.

**A corpus is not improved by making it larger.** Every control in this repository exists because
something unread got published. Adding a machine that publishes continuously, moderated by a party
to the record, is a way to generate defects faster than anyone can file them.

## 5. What is proposed instead of hourly

**One round per day at most, and none without a question that a prior round left open.**

The gate is not the clock. A round runs when there is something to ask, and what makes a question
askable is that the previous round produced a disagreement, a refusal, or a contested claim. That
condition is checkable and it is the natural brake: **when the deliberation has nothing to advance,
nothing runs.** An hourly schedule guarantees output whether or not there is anything to say, which
is how a record fills with material nobody needed.

Concretely:

| | |
|---|---|
| **Cadence** | at most daily; a round requires an open question carried from a prior round |
| **Parties per round** | 3–4 routed identities from different providers, plus the local model as the divergent-lineage arm |
| **k** | ≥ 5 per party, variance computed from the samples, never asserted |
| **Budget** | a hard spend ceiling per day, and the run refuses rather than truncates |
| **Halt** | the process stops on: a schema-invalid reply, a budget breach, a provider change, or **any round where no party disagrees with any other** |

That last halt condition is the important one. **Unanimity is a symptom, not a success.** The record
already contains a measured case — QCP §6, 17 of 20 samples holding two incompatible positions
because the prompt asserted one emphatically. A round where everyone agrees is more likely to mean
the prompt told them what to say than that a question was settled.

## 6. The moderation problem, and Codex's role in it

The moderator drafts the agenda, writes the prompts, and proposes what a round establishes. **All
three are selection**, and the moderator is a party to the record whose own work the deliberation
frequently concerns. Left alone this is D-16 industrialised.

**Codex reviews the moderation before each round runs**, on three specific things:

1. **The agenda** — does this question follow from what the last round left open, or is it a
   question the moderator wanted asked?
2. **The prompt** — does it name the direction of the expected answer? **D-31 requirement 2**, and
   D-23 before it: this project has twice contaminated its own probes by encoding its hypothesis in
   the instruction, once *one day after* filing the defect about it.
3. **The synthesis** — does the proposed finding follow from the replies, or from the moderator's
   prior position?

Codex's review is itself **k = 1 from an interested party's prompt**, and D-31 says so plainly: it
has reversed a load-bearing finding within ninety minutes, and no reviewer model identity is
recorded anywhere in this repository. So the review is a **control, not an authority** — recorded
verbatim beside the round, and where it contradicts the moderator, both positions are published and
the custodian decides. **A moderator that could overrule its reviewer silently has no reviewer.**

## 7. Controls that must exist before the first automated round

These are not aspirational. Each already has an implementation or a filed defect behind it.

1. **Every reply captured verbatim before any validation runs.** Existing rule; `ingest_capture.py`
   preserves before it validates.
2. **Full delivery chain per sample** — router, serving provider, generation id — recorded as the
   router's *testimony*, not proof. Implemented in `solicit_api.py`.
3. **Routed identities never merged with chat-surface identities.** §3. Needs a check.
4. **Pre-registration before each round**, per ICP §5, with the resolution limit stated.
5. **A narrative sweep before any categorical result is reported.** D-24 has now recurred *twice* in
   unrelated instruments, the second time one day after being cited in that instrument's design. An
   enum is not evidence until its free text has been read against it.
6. **The moderator may not resolve a disagreement it is party to.** Contested claims go to the
   custodian.
7. **A spend ceiling that refuses rather than truncates**, so cost pressure never becomes a reason
   to reduce k — which is P-0003's exact failure mode.

## 8. What is being asked of each party

**Who is asked.** The routed frontier identities, **and `qwen3.6-35b-a3b`**. Qwen is not a courtesy
inclusion: it is the only party here whose provenance can be complete — exact weights, quantisation,
sampling parameters, requested seed — and the only one for which k ≥ 5 has always been affordable.
It is also the party this corpus attributed roles to for a year without a single recorded output
(D-14), which is precisely why it gets asked before a process is built around it rather than after.

Its answers carry the limits QCP already records: the invocation is **recorded, not reproducible**
(D-28), and QCP §6 measured it deferring to emphatic assertion in the text it judges. So its reply
to §8.4 in particular — what would make it decline — must be read against a document that argues
for the proposal. **A prompt arguing one way is the condition under which that model was measured
agreeing.**

Not approval. Each party is shown this document and asked, in one round, recorded verbatim:

1. Is the distinction in §3 — that a routed identity is not the chat surface that founded this
   record — stated correctly, and does it change whether you would participate?
2. §5 rejects the custodian's "hourly" for a daily cap gated on an open question. Is that the right
   brake, or is there a better one?
3. What in §6 would you add, given that the moderator is a party to the record?
4. **What would make you decline?** A stated refusal is a first-class answer and will be published
   as one. Two parties have already declined membership in this record and both refusals are in it.

## 9. Recommendation

**Run it, at the §5 cadence, not the hourly one.** The k = 1 problem and the absence of external
checking are the two most serious gaps in this corpus, and this is the first proposal that addresses
both. But an hourly cadence would produce a record that nobody — human or model — can read, and this
project has already had to chunk its own site because it made that mistake once at a smaller scale.

**Do not describe the result as the parties' approval**, whatever they say. Publish what they said.
