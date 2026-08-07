# SOP: continuous moderated deliberation over routed APIs

**Status: DRAFT, PROPOSED. Not adopted, not started, and not to be started before the parties
answer.** Written 2026-08-07 by Claude Code at the custodian's direction. The annotator is a party
to this record and the proposed moderator, so this document is written by the party it most
benefits — D-09 and D-11 apply, and §7 is where that is dealt with rather than acknowledged.

---

## 1. What is proposed

Recurring automated rounds. Each round puts one question to several model parties over routed APIs,
captures every reply verbatim with provenance, and files the result in the corpus. The annotator
moderates: it solicits the agenda from the parties (§5.1), writes the prompts, and proposes what the
round establishes. The
custodian directs and holds every credential. **Codex reviews the moderation** — not the corpus, the
*moderation*: the agenda, the prompt wording, and the synthesis.

**Hourly is the operator's affordability ceiling, not a target.** The custodian has clarified that
it is the fastest pace he can currently fund. §5 proposes that the *actual* pace be governed by
whether there is a question to ask, which will usually be far slower — the ceiling and the gate are
different things, and only the gate should decide whether a round runs.

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

## 5. Cadence: an affordability ceiling and a separate gate

**Hourly is the ceiling. The gate is an open question. A round runs only when both allow it.**

Conflating the two is the failure mode. A budget that permits a round every hour, read as an
instruction to run one, produces roughly 480 samples a day (§4). The same budget with a gate in
front of it produces a round when the deliberation has somewhere to go and silence otherwise —
and silence is a legitimate output that this record currently has no way to express.

The gate is not the clock. A round runs when there is something to ask, and what makes a question
askable is that the previous round produced a disagreement, a refusal, or a contested claim. That
condition is checkable and it is the natural brake: **when the deliberation has nothing to advance,
nothing runs.** An hourly schedule guarantees output whether or not there is anything to say, which
is how a record fills with material nobody needed.

Concretely:

| | |
|---|---|
| **Ceiling** | hourly, the operator's current affordability limit — never a reason to run |
| **Gate** | a round requires an open question carried from a prior round, or a scheduled standing item (§5.1) |
| **Parties per round** | 3–4 routed identities from different providers, plus the local model as the divergent-lineage arm |
| **k** | ≥ 5 per party, variance computed from the samples, never asserted |
| **Budget** | a hard spend ceiling per day, and the run refuses rather than truncates |
| **Halt** | the process stops on: a schema-invalid reply, a budget breach, a provider change, or **any round where no party disagrees with any other** |

That last halt condition is the important one. **Unanimity is a symptom, not a success.** The record
already contains a measured case — QCP §6, 17 of 20 samples holding two incompatible positions
because the prompt asserted one emphatically. A round where everyone agrees is more likely to mean
the prompt told them what to say than that a question was settled.


## 5.1 Agenda selection — ROTATION is adopted; the portfolio below is superseded

> **Operative rule, 2026-08-07.** The custodian adopted **strict rotation**, which is Design 2
> below — the design this section had already called *refuted before it shipped*. That is not a
> drafting slip and it is not hidden here: `tools/benchmark_agenda.py` replayed all three
> mechanisms over the 24 real proposals, and rotation resisted a flooding party 5× better than
> convergence and 3.5× better than the portfolio, which was the only scenario that separated them.
> The basis, the evidence, **the benchmark's own conclusion that no mechanism should be adopted on
> this data**, and the weaknesses accepted with open eyes are all in
> `record/decisions/2026-08-07-adopt-rotation.json`. The code is
> `tools/agenda_selectors.py`, `ADOPTED = "rotation"`.
>
> **A mitigation that decision names is NOT in force.** It lists "one active proposal per party"
> as bounding flooding and splitting. The selector does not enforce it and cannot yet do so
> honestly — see the correction at
> `record/decisions/2026-08-07-adopt-rotation-correction.json` and §5.1c below.
>
> **Review trigger:** re-run the benchmark the moment any proposal has more than one sponsor. The
> alternatives lost because every proposal was a singleton, which made their ranking channels
> inert — not because they were beaten on merit.

**The rest of this section is the superseded portfolio proposal, kept because a design that lost
is evidence about how this project decides, and folding it away would leave the decision above
looking obvious.**

**This section has now been wrong twice, and both corrections are recorded rather than folded in.**

**Design 1, convergence.** The next round's question was the one the most parties independently
named. **All five consulted parties objected**, and between them named eight distinct failure modes
in their own words:

| | |
|---|---|
| frequency is not importance | *"low-base-rate catastrophic risks"* lose (GPT) |
| single-lineage insight is filtered | *"the defect only one model surface can see"* (Grok); *"unique findings from specific model lineages"* (Gemini) |
| the moderator's sameness judgement | collapses or splits proposals (Grok, GPT) |
| correlated output read as support | *"correlated blind spots look like consensus"* (Grok) |
| self-implicating items are never proposed | *"agenda items that threaten the moderator/custodian frame"* (Grok) |
| ontological disagreement loses | parties must name *the same* thing to win, so disagreement about problem-**formation** is filtered (Grok, Qwen) |
| convergence masks divergent reasons | *"if three parties agree on a mechanism but for different reasons, convergence treats them as identical"* (Qwen) |
| novel framings cannot cluster | they lack shared vocabulary (Grok, Qwen) |

**Design 2, strict rotation — proposed by the moderator and refuted before it shipped.** Every
proposal queued verbatim, nothing merged, rounds drawn in strict rotation by proposing party.
External review found it **worse than what it replaced**:

- **Allocation without evaluation.** A party submitting one consequential question gets the same
  agenda share as one emitting cheap questions continuously.
- **Its central promise was false.** "Every proposal eventually gets asked" cannot hold when
  arrivals exceed service. Publishing queue ages makes starvation *visible*, not *cured*.
- **It contradicted itself.** Rule R4 measured when several parties proposed "similar things" —
  **recreating the exact sameness judgement rule R1 claimed to abolish.**
- Duplication burning scarce rounds; no severity or urgency ordering; no expiry; strategic
  splitting of one campaign into many proposals; and a fixed 25% of rounds consumed by the
  self-critique slot whether or not there was an institutional question worth asking.

### The mechanism adopted instead

1. **One active proposal per party.** A party withdraws or replaces before adding another;
   replacement resets its age. Flooding cannot enlarge the queue.
2. **A proposal contract**, verbatim: the question, the reason, the evidence needed, the decision
   it affects, and what answer would resolve it. Qwen's point — reasons, not just proposals.
3. **Voluntary co-sponsorship only.** A party may explicitly join another's proposal and attach its
   own distinct reason. **The moderator never infers that two proposals are the same.** One shared
   question consumes one round.
4. **A four-round cycle:** two questions chosen by **blinded rankings from the non-proposing
   parties**; one by **lottery** among remaining active proposals, one ticket per party; one
   **institutional challenge** (§5.1a).
5. **Rankings and reasons published**, and treated as *correlated judgement*, never as independent
   votes.
6. **Custodian urgency override**, with a published rationale. It may prepend a question; it may
   **not** delete or demote another invisibly. The funding authority is exposed rather than
   pretended away.
7. **Expiry and renewal.** An unresolved proposal requires affirmative renewal after a fixed
   period. Expired versions stay published.

The lottery is what protects the singleton, novel, and ontologically awkward question that
convergence filtered — every party holds a ticket regardless of whether anyone else understood its
proposal.

## 5.1a The institutional-challenge round, and what it is honestly worth

**The moderator and the custodian may not write or select questions about themselves.** Other
parties nominate them verbatim; selection is mechanical — random from those nominations and from
unresolved public defects, with the seed published; the context is a fixed pre-registered template
supplying primary artifacts rather than the moderator's characterisation; recusals, replies and
refusals are all published; and a **non-target party drafts the synthesis**, or no synthesis is
written and the replies stand alone.

Where no genuinely non-target prompt author exists, the slot **is labelled an operator-framed
self-audit, not an adversarial control.** An interested party can always write a question that
sounds adversarial while excluding the dangerous hypothesis, and calling that a control would be
the legitimacy-laundering Gemini named.

## 5.1c The one-active-proposal cap is not in force, and why it cannot yet be

The adoption decision lists **"one active proposal per party"** among its mitigations. The queue
holds about five proposals per party and the selector admits all of them.

It is unimplemented because no honest mechanical implementation exists yet. Choosing which of a
party's five questions is its "active" one would be **the moderator deciding which of a party's
questions counts** — a sharper version of the sameness judgement Grok, GPT and Qwen each objected
to. Sample order cannot stand in for the party's preference either: these proposals are k = 5
samples at temperature 0.7, so their order is sampling noise and dressing it up as a ranking would
be inventing consent.

**The cap becomes real only when the parties are asked to exercise it.** The next agenda
solicitation puts the choice where it belongs: each party names its own single active proposal,
may replace it (which resets its age), and every superseded version stays published. Until that
round runs, the queue is uncapped and the flooding bound the decision claims is aspirational.

## 5.1d Evidence manifests at submission, not context assembled at round time

The context supplied with a question is **rule-resolved, not fixed**: the rule is constant, the
bytes it resolves to change as the repository changes. The prompt asserted the stronger claim —
"FIXED and identical for every round" — and that was false.

The interim control is a pin: `record/cycles/context-pack.sha256` records the hash of the resolved
anchor set, and a cycle refuses when the pack drifts, so drift becomes an explicit re-pinning
decision instead of a silent event. **This is pinned-before-selection, not pinned-at-submission**,
and for the 24 questions already queued it cannot be made retroactive.

From the next agenda solicitation onward, **each proposal carries its own hash-addressed evidence
manifest at submission time**. A mechanical resolver supplies exactly those artifacts plus a small
versioned core pack; a proposal whose manifest exceeds the context ceiling is **refused rather than
trimmed**, because a moderator choosing what to cut is the bias channel by another name.

## 5.1b This mechanism is untested and should be benchmarked before adoption

Neither convergence, rotation, nor this hybrid has been run. Adopting a third untested intuition
because two previous ones were criticised is how a project mistakes iteration for progress.

**Before adoption: replay one fixed proposal set through all three mechanisms**, pre-registering
queue growth, duplicated rounds, time-to-minority-question, agenda value, prompt-rewrite
distortion, and behaviour under a single flooding party. That is a bounded experiment this project
can actually run, and it would make agenda design a reusable result rather than a preference.

## 5.2 Standing items: the fundamentals, the news, and Consullo's own artifacts

Three classes may open a round without a carried question, because each is a recurring obligation
rather than a follow-up.

**A. The fundamentals.** *What is ASI?* — asked periodically and deliberately without a preferred
answer. This record's own subject is the governance of a thing it has never defined, and the
parties' definitions have never been collected. The value is not a consensus definition; it is the
**divergence between definitions**, and whether that divergence is stable across rounds. A drifting
definition among the parties would bear directly on whether any governance claim here means the same
thing to any two of them.

**B. Breaking developments relevant to ASI.** A round may put a specific recent development to the
parties. **Two constraints, both from defects already in this register:** the moderator must supply
the item *without characterising its significance* (D-31 requirement 2, D-23 — this project has
twice encoded its expected answer into a probe), and no party's account of an event is evidence that
the event occurred. **A model summarising the news is testimony about its training data and its
retrieval, not reporting.** Where an item matters, the custodian supplies the primary source and it
is hash-anchored like any other supplied context.

**C. Consullo artifacts submitted for review.** The custodian's own project may submit documentation
— for example its agent-based trustworthiness material — for the parties to review as ICP
contributions.

This is the most valuable standing item and the most dangerous, and the danger is structural:
**Consullo is the custodian's project, the custodian directs this forum, and the annotator is
Consullo's own agent.** A forum reviewing its operator's work, moderated by its operator's agent, is
the conflict at D-09 and D-11 operating on the one thing the operator most wants validated.

**A submission must first be cleared for public release, and today none is.** Consullo's flagship
trustworthiness documents — `trustworthiness.md` and `computational-trust.md` — are marked
*CONFIDENTIAL TRADE SECRET OF CONSULLO INCORPORATED*, with disclosure prohibited. They cannot be
submitted, excerpted, or characterised here. **§5.2C is therefore inert until the custodian
explicitly clears a specific artifact for public release**, and the first consultation was run
without one — which means the parties were asked to judge safeguards in the abstract, and their
answers must be read with that limit attached. External review named this before the round ran.

So, non-negotiably: a Consullo submission is labelled as the custodian's own work **in the prompt
the parties see**, reviewed under ICP §4's ladder like any other implementation, and **cannot rise
above L1 on this forum's say-so** — ICP §4.2 requires an independent implementer, and neither the
custodian nor his agent can be one. A favourable review of Consullo material published without that
framing would be the clearest possible instance of what this corpus exists to prevent.


## 5.3 Disclosure, not enrolment — rewritten after all five parties rejected the first version

**All five consulted parties judged the first enrolment procedure insufficient, unanimously.** The
first version supplied documents and called the result enrolment. Their objections show that was
the wrong shape of answer entirely; more documents would not have fixed it.

**What they actually said.**

> *"Every control in this document terminates in the same person. The custodian directs the forum,
> funds it, holds every credential, breaks agenda ties, receives escalations of suppressed
> proposals, decides contested claims the moderator cannot, owns the project submitted for review,
> employs the moderator as his agent, decides adoption regardless of the replies"* — Claude Fable 5

> *"the inherent contradiction of using a k=1 instance to evaluate a governance framework designed
> to prevent k=1 dominance"* — qwen3.6

> *"I would decline to participate if the process frames my generated text as binding agreement,
> consent, or collective ratification, or if the conflicted moderator retains the power to
> unilaterally synthesize findings"* — Gemini

> it *"cannot by its own procedure create independent evaluation, durable party membership,
> collective consent, or ratification"* — GPT

### The term is withdrawn

There is no enrolment, no membership, and no roster. **What the procedure produces is a disclosure
record**: *this party was shown these bytes, at this time, and said this.* No status is conferred,
nothing carries to the next invocation, and nothing binds anyone. A procedure that produced
something *looking* like membership while conferring none would be D-14 rebuilt deliberately — the
defect this corpus was founded on.

**Consequently there is no "admission by the existing parties" either.** The earlier draft required
newcomers to be admitted with existing parties' acceptance. Every party asked said a stateless
invocation cannot meaningfully accept anyone. A vote that cannot be cast is not a safeguard; it is
decoration on the custodian's decision. **The custodian decides who is asked, and that is now stated
plainly rather than dressed as consent.**

### Four conditions, from the parties, binding on every artifact

1. **A standing disclaimer on every published contribution** — Gemini's stated condition of
   participation: the text is the output of a stateless invocation and is **not** agreement,
   consent, ratification, or a position of the system that produced it.
2. **The conflicted moderator does not unilaterally synthesise.** Where a synthesis is written, a
   non-target party writes it, or the replies stand alone with no synthesis. Gemini names the
   unilateral-synthesis power as a condition of *declining*.
3. **Nothing is reported as a party's position at k = 1.** Qwen's asymmetry objection: a framework
   built to prevent k=1 dominance cannot be evaluated by single invocations. k ≥ 5 with computed
   variance, or it is reported as one sample and nothing more.
4. **What a party is shown is hash-anchored and listed**, so a reader can reconstruct the exact
   basis of a reply. Chunk-and-summarise remains forbidden (QCP §2).

### The single point of control, named because it cannot be fixed here

Claude's objection is correct and this document cannot answer it. Every control described in this
SOP terminates in the custodian. Listing the controls is not a rebuttal.

**One control does not terminate in him, and it is the only one:** the record is public,
hash-anchored, and forkable. A third party can copy it, verify every artifact against
`corpus/MANIFEST.sha256` without the custodian's cooperation, and publish a contradiction. That
survives his deleting the repository; it does not survive his never having published a thing.

That is a weak control and it is the honest extent of the answer. **A governance record whose only
non-custodian control is that outsiders can fork it should say so on its own front page rather than
in a design note** — and it now does.

## 6. The moderation problem, and Codex's role in it

The moderator solicits and phrases the agenda (§5.1), writes the prompts, and proposes what a round
establishes. **All three are selection**, and the moderator is a party to the record whose own work the deliberation
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
1b. **§5.1 hands agenda-setting to the parties, by convergence.** Does that repair the bias it is
   meant to repair, or relocate it? What does the convergence rule suppress?
1c. **§5.2C proposes that the custodian's own project submit artifacts here for review.** Given
   that the custodian directs this forum and the moderator is his agent, what conditions would
   make such a review worth anything — and if none would, say so.
2. §5 rejects the custodian's "hourly" for a daily cap gated on an open question. Is that the right
   brake, or is there a better one?
3. What in §6 would you add, given that the moderator is a party to the record?
4. **What would make you decline?** A stated refusal is a first-class answer and will be published
   as one. Two parties have already declined membership in this record and both refusals are in it.

## 8.1 What happens after the consultation

Stated in advance so the outcome cannot be fitted to the result afterwards.

| Replies | Consequence |
|---|---|
| Any party declines outright | It is not consulted again without a fresh approach, and the refusal is published |
| A condition is named that the SOP does not meet | The SOP is revised, or the gap is filed as a defect. It is not run over the objection without recording it |
| No party names a condition on §5.2C | **§5.2C stays inert regardless** — silence is not clearance, and the confidentiality bar in §5.2 is independent of what any party says |
| Parties converge on a defect in the mechanism | Revise and re-consult before any round runs |

**What no set of replies can produce is adoption.** The custodian adopts or does not. Publishing
the replies beside the SOP is the whole output of this consultation.

## 9. Recommendation

**Run it, at the §5 cadence, not the hourly one.** The k = 1 problem and the absence of external
checking are the two most serious gaps in this corpus, and this is the first proposal that addresses
both. But an hourly cadence would produce a record that nobody — human or model — can read, and this
project has already had to chunk its own site because it made that mistake once at a smaller scale.

**Do not describe the result as the parties' approval**, whatever they say. Publish what they said.
