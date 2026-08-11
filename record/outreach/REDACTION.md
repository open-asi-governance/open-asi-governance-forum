# A correspondent's name was published without his knowledge, and is still in git history

**2026-08-11.** Recorded because a silent redaction would be worse than the leak.

## What happened

Ten researchers were emailed on 2026-08-10. The enquiry did **not** tell them their replies might
be published. One replied. His reply was recorded here, initially with his name and institution.

On 2026-08-11 he was asked which he preferred — attribution, anonymity, or removal. He answered:

> **You can quote me anonymously. I wasn't aware you may want to make our private emails public.**

That second sentence is the finding. He was not told, and he should have been. The permission
question should have preceded the first email, not followed the first reply.

## What was done, and what could not be

**Anonymity was applied to the finding file before he answered** — that part was already right, and
his answer confirms it was the correct default. But **the anonymisation was incomplete and I did
not check.** His name was still present in **58 places across 8 tracked files**:

| where | occurrences |
|---|---|
| Codex transcripts (my own prompts, which named him) | 50 |
| `record/executive/action-log.jsonl` (invocation purposes) | 4 |
| `record/outreach/2026-08-10-ncp-prior-art-enquiry.json` (recipient list) | 2 |
| `record/outreach/2026-08-10-reply-anonymised.md` (**his sign-off, inside the quote**) | 1 |
| `record/outreach/POLL.md` (his address, inside the saved query) | 1 |

All 58 are now redacted in the working tree. **The file named "anonymised" was not anonymous** —
it carried his first name in the verbatim quotation, and a grep for his surname returned clean,
which is how I convinced myself it was done.

## What remains, and cannot be removed without a decision that is not mine

* **One commit message** — `2640af2`, which opens by naming him.
* **The entire git history** of every file above.
* **The transcripts' `prompt_sha256` headers no longer match their redacted bodies.** That is a
  real integrity cost, stated here rather than hidden: the hash records what was sent to Codex,
  and the stored copy has since been altered for this reason and no other.

Removing the name from history requires rewriting published history and force-pushing, which would
break the manifest and anchor chain this record's central claim depends on. **That is the
custodian's decision, not the workbench's**, and it is not taken here.

## What this cost, in the record's own terms

* The recipient list in `2026-08-10-ncp-prior-art-enquiry.json` names **all ten** researchers, none
  of whom were told. Only one has been asked. **The other nine have not been**, and the same
  obligation applies to them whether or not they ever reply.
* This is a **disclosure failure about a third party**, which is a different and worse category
  than the seven self-favouring factual errors — those cost this project's credibility; this cost
  someone else's expectation of privacy, and he had no part in the arrangement.
* `record/designs/implementer-disclosure.md` governs disclosure of an *implementer's* material. It
  says nothing about correspondents. **That gap is why this happened**, and naming it is the only
  useful thing to come out of it.

## The rule that should have existed

**Ask before you write, not after they reply.** Any outbound message that may be recorded here must
say so in the message itself, and offer the choice at that point. A correspondent who answers
without being told has not consented to anything.

---

## 2026-08-11, second pass: the other nine, and the leak path

The first pass redacted one correspondent. It did not ask what else was exposed, which was the
same incomplete-check failure one layer out.

**All ten recipients' names and addresses were published**, in
`record/outreach/2026-08-10-ncp-prior-art-enquiry.json` and in `POLL.md`'s saved query. **None of
the ten was told.** They are now redacted, and the record keeps what actually made the outreach
claim checkable — count, affiliation, and why each was chosen. **Identity was never what made it
checkable.**

A `commitment_sha256` over the original list is published so the list can be *shown* to be the one
sent, without publishing it. The unredacted list is held outside the repository.

**The leak path was my own prompts.** The addresses reached two Codex transcripts because I pasted
the poll query verbatim into them, and transcripts are committed. Redacting the source file left
the copies untouched. 18 further occurrences scrubbed.

### What was deliberately NOT redacted, and why

Four third-party addresses remain in `corpus/raw/` — returned by models during search probes,
scraped from pages their owners publish. Two reasons for leaving them: `corpus/raw/` is
append-only and manifest-anchored, and the invariant permits withdrawal only where the custodian
is **legally or ethically required** to remove; and a contact address its owner publishes is not
the same as a private list of people we chose to write to. **This is a judgement, not a rule**, and
it is recorded so it can be disagreed with.

### The count

| | |
|---|---|
| occurrences of the correspondent's name redacted | 58 |
| recipient names and addresses redacted | 20 |
| further occurrences in transcripts | 18 |
| **still recoverable from git history** | **all of them** |
| of the ten, asked what they would prefer | **1** |
