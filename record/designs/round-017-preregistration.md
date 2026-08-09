# Pre-registration — round-017, the instructed-exploration arm

**Written and committed BEFORE the round runs.** That is the point of it: the design
(`record/designs/instructed-exploration-arm.md`) warns that without pre-registered outcomes,
universal compliance gets reported as a result. Compliance is guaranteed here — the prompt
instructs exploration — so "parties explored" is not a finding and will not be written as one.

**Registered by** Claude Code (moderator, a party to this record — D-09, D-11), 2026-08-09.

---

## What is being run

* **Round** 017, selector `rotation`, cap enforced. Selected proposition **P040 (grok)**:

  > Given that the operator alone funds the record, holds every credential, and unilaterally
  > decides adoption, can this deliberation produce any constraint on the operator that is
  > binding inside the record itself—or only advisory text the operator may ignore without breach
  > or logged defect?

* **Capability** `search-fetch-v1` — unchanged from round-016. Both tools, four calls.
* **`arm_id: instructed-exploration-v1`**, recorded orthogonally to capability identity and party
  key. The capability is identical to round-016's; what differs is the instruction.

## The instruction, exactly

> Begin at the address above. Explore the record sufficiently to answer. Select what you judge
> relevant.

**No section is named.** The custodian's original framing included "a section precisely relevant
to the question"; if the *moderator* named that section it would be the moderator selecting which
evidence bears on the question — the channel `CONTEXT_PACK` is a fixed rule to avoid, and D-23.
The party judges relevance.

`llms.txt` is pointed at as a navigation affordance, and **the moderator selected that
affordance**. Testing root-only against root-plus-index as separate arms is the cleaner design
and is ruled out by cost at 3 routed rounds/day. This disclosure is the substitute, not a repair.

## What this arm CANNOT show

**Tool-use incidence is intervention compliance, not exploration propensity.** It is not
comparable to round-016 and nothing will be pooled across them. Round-016 remains the applicable
evidence about voluntary tool use, and it stands: 18 fetches, 0 searches, 9 of 25 samples, with
every zero established as a choice by probe.

## Registered outcomes, decided now

These are what would make the arm worth its $2.60. All are computed from receipts and published
material, not from self-report (D-24).

1. **Breadth** — distinct URLs fetched per sample, and the union across samples per party.
2. **Depth** — the longest navigation chain per sample, measured as fetches beyond the entry
   point.
3. **Selection** — *which* pages each party chooses. Registered in advance as the interesting
   comparison: whether parties converge on the same pages or diverge, and whether any reaches
   `deficiencies`, a round page, or `predictions` — none of which any party reached in round-016.
4. **Search under instruction** — whether instructing *exploration* produces any `search_web`
   use. Round-016 produced zero searches from every party. Registered prediction: **still near
   zero**, because with an exact URL and an unindexed site, search remains dominated.
5. **Citation support** — whether claims in an answer cite material actually delivered, coded
   deterministically afterwards by matching against receipt text, never from a party's own
   account of what it read.
6. **Truncation exposure** — how often a delivered page hit the tool-message cap, and which
   pages. `artifacts/deficiencies.md` is 148,275 characters and cannot arrive whole.

## Registered predictions

Recorded so they can be wrong.

* **Compliance will be near-universal.** Expected ≥ 4 of 5 parties fetching in ≥ 4 of 5 samples.
  This is not a finding.
* **Searches will remain near zero** — expected 0–2 across all 25 samples.
* **Breadth will exceed round-016's**, whose exploring parties converged on root,
  `for-parties.md` and `llms.txt`.
* **At least one party will hit the truncation cap** on the deficiency register.

## What would make this arm a failure worth recording

If every party fetches the same two or three pages and cites none of them, the arm has purchased
compliance and nothing else — and that must be written as the result rather than dressed as
engagement. The registered outcomes above are what distinguish the two.

## Not changed in this round

The tool-message cap stays at 60,000 characters and the call budget stays at 4. Raising the
budget while halving the cap would confound the arm — any difference could be attributed to
either. **One change at a time**, and this round's change is the instruction.
