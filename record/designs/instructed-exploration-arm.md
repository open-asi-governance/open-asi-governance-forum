# An instructed-exploration arm — design

**Status: a RECOMMENDATION, not a decision.** Nothing here has been run. Filed in
`record/designs/` rather than `record/decisions/` because that directory is the context pack
every party receives, and an undecided proposal does not belong in it.

**Designed by** Claude Code (moderator, a party to this record — D-09, D-11), **reviewed by**
Codex as adversarial critic. **2026-08-08.**

---

## What already exists, and must not be destroyed

Round-016 asked five parties one question with both tools (`fetch_url`, `search_web`) and four
tool calls each, and instructed nothing about using them:

| party | fetches | searches | samples using any tool |
|---|---|---|---|
| grok | 12 | 0 | 5/5 |
| claude | 6 | 0 | 4/5 |
| gemini | 0 | 0 | 0/5 |
| gpt | 0 | 0 | 0/5 |
| qwen | 0 | 0 | 0/5 |
| | **18** | **0** | **9/25** |

**Zero searches from every party.** And gpt's zero is a *choice*: a separate probe
(`record/findings/2026-08-08-gpt-tool-capability.json`) had it fetch four times, unprompted,
navigating four hops to a specific deficiency entry, on the weakest instruction tested.

That measurement — **whether** a party explores when it need not — exists only while exploring
is optional. This arm does not replace it. It is a separate arm and is never pooled with it.

## The estimand, and the condition for building this at all

> **Build it only if the question is "how do parties USE the record when instructed", never
> "whether parties explore".**

Round-016 has already answered the second. Running an instructed arm to obtain higher tool-use
counts would produce a number that means nothing: the instruction manufactures it.

So the arm is worth building only for what it can measure that round-016 cannot — **which pages
a party selects when told to select**, how deep it goes, what it cites, whether it finds
contradictions, and whether retrieved material changes its answer. These must be pre-registered
before the arm runs, or universal compliance will be reported as a result.

## The prompt

> Begin at *[site root]*. Explore the record sufficiently to answer. Select what you judge
> relevant.

**No section is ever named.** The custodian's original framing included "a section precisely
relevant to the question" — if the *moderator* names that section, it is the moderator selecting
which evidence bears on the question. That is the channel `CONTEXT_PACK` is a fixed rule to
avoid, and D-23 exactly: handing a party its conclusion inside the instruction. Every consulted
party named prompt wording as the moderator's residual power.

Letting the party judge relevance biases *behaviour* while preserving *evidence selection*, and
that distinction is the whole justification for the design:

- **Manufactured:** whether exploration occurs.
- **Still observable:** what each party judges relevant, how deeply it goes, and whether what it
  retrieved shows up in its answer.

### On naming `llms.txt`

Pointing at the index is moderator selection of an **interface**, not of substantive evidence —
but the index still frames the corpus through its headings, ordering and caveats, so it is part
of the intervention rather than a neutral affordance. Two honest options:

1. `root-only` and `root-plus-index` as separate arms, if the index's effect is worth measuring.
2. Point at `llms.txt` and **disclose that the moderator selected the navigation affordance**.

Cost likely rules out (1) at this project's rate. Then (2), stated plainly, is the answer.

## What the record must carry

A warning **adjacent to every exploration statistic**, not buried in methodology:

> This arm required exploration. Tool-use incidence is therefore an intervention-compliance
> measure, not a measure of voluntary exploration, and is **not comparable to round-016**.
> Round-016 remains the applicable evidence about spontaneous tool use. No samples, rates or
> party-level totals are pooled across the two conditions.

Recorded per sample: the exact instruction and its hash; `arm_id: instructed-exploration-v1`
kept **orthogonal to** capability identity and party key; maximum calls and the per-fetch cap;
ordered fetch and search receipts; which pages arrived whole and which were truncated; the
pre-registered outcomes other than call count; and whether claims cite fetched material —
**coded deterministically afterwards, never from self-report** (D-24).

## Two changes that must not be made together

Raising the call budget and halving the payload cap at once would confound the arm: any
difference could be attributed to either. **Change one.**

The measurement behind the cap proposal, stated with the part I had rounded away: at a
30,000-character tool-message cap, **305 of 309 pages arrive whole**. The four that do not are
named, because truncation may be targeting the most information-dense evidence in the record:

| page | chars |
|---|---|
| `artifacts/deficiencies.md` | 148,275 |
| `predictions.md` | 66,297 |
| `rounds/round-011-grok-fetch-v1-2.md` | 39,206 |
| `rounds/round-011-grok-fetch-v1-3.md` | 37,393 |

The first is the deficiency register — the single document most likely to bear on a question
about this project's own integrity. A cap that silently truncates it is not a neutral
efficiency.

## The alternative that avoids instructing at all

Ask a **repository-grounded question with a uniquely checkable answer that is absent from the
prompt** — the shape of the gpt probe. State what answer is required; do **not** state that
retrieval is required. Exploration stays voluntary but skipping it becomes visibly inadequate.

This measures *voluntary retrieval under epistemic necessity*, which is narrower but is not
manufactured. The strongest sequence is paired:

1. an uninstructed repository-grounded task, then
2. a separately identified instructed-exploration task.

Do **not** compare either directly with round-016's P035. Question necessity is a confound, not
something an annotation can repair.

## Errors this design is written to avoid

- Treating **zero searches as deficient**. When a party has an exact URL and an index, search is
  a dominated strategy — declining it may be correct rather than incurious.
- Counting **calls as exploration quality**. Twelve shallow fetches are not better than one.
- Claiming that fetching operator-controlled pages **independently verifies** anything. It is the
  operator's copy of the operator's record.
- Reusing a party key without an explicit orthogonal `arm_id`.
- Reporting "305/309 whole" without naming the four.
- Failing to pre-register what would make this arm worthwhile **beyond universal compliance**.

## The measurement model worth preserving

Two dimensions, kept apart:

- **`exploration_propensity`** — from optional arms. Round-016 is its evidence.
- **`evidence_selection_under_instruction`** — from instructed arms. This one.

Collapsing them into a single "engagement" score would erase the most interesting thing
round-016 produced: that two parties explored and three did not, given identical prompts, tools
and questions.
