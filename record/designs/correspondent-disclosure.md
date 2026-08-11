# Telling people before they answer

**The rule, in one sentence:**

> **Any outbound message whose reply might be recorded here MUST say so in the message itself, and
> MUST offer the choice at that point.** A correspondent who answers without being told has not
> consented to anything.

Written 2026-08-11, from a failure. `record/designs/implementer-disclosure.md` governs what may be
published about an **implementer's system**. It says nothing about the **people this project
writes to**, and that gap is not an oversight in the abstract — it is the reason ten researchers'
names and addresses were published without any of them being told, and one of them had to point it
out.

## What the message must say

Not a legal notice. Two sentences, before the ask:

> This project publishes its correspondence as evidence, including replies unflattering to it. If
> you reply, tell me whether you would prefer to be named, quoted anonymously, or not recorded at
> all — and if you say nothing, I will keep you anonymous.

The offer must be **all three options**. "May I quote you?" is not the offer; it presents recording
as settled and only attribution as open.

## The default before anyone answers

**Anonymous.** Not named, and not omitted.

Omission is not the safe default it looks like: it deletes the evidence that outreach happened at
all, which is the thing the adverse-outcome prediction turns on. Anonymity keeps the record
checkable and keeps the person out of it.

## What must never be published, choice or no choice

* **Email addresses.** They were published here to make a poll query reproducible. Reproducibility
  of a query is not worth a stranger's inbox, and a commitment hash over the list preserves
  everything the record actually needed.
* **A list of who was approached and why they were chosen**, in identifiable form. The count, the
  field and the rationale carry the claim; the names never did.

## The part that is easy to get wrong

**Redacting the source file is not redacting.** On 2026-08-11 a correspondent's name was removed
from the finding, and remained in 58 places: Codex transcripts quoting the prompts, the action log,
the recipient list, the saved poll query, and — in the file named *anonymised* — his own sign-off
inside the verbatim quotation. Each pass declared itself clean and the next pass found more.

**So: grep for the person, not for the string you happen to remember.** Full name, surname, first
name alone, address, institution, and any file that ever quoted a file that quoted them.

## What this rule does not fix

* **Git history.** Every redaction here leaves the original recoverable, and one commit message
  still names a correspondent. Removing that needs a history rewrite the custodian has not
  authorised, and this rule does not pretend otherwise.
* **The nine who were never asked.** The rule is prospective. It does not discharge an obligation
  already incurred, and nine of ten recipients still have not been told what happened.
* **Anything about implementers.** That is the other document, and the two do not substitute for
  each other.

## Status

Not adopted. Applied to the next outbound message regardless, because the alternative is
continuing to do the thing that produced `record/outreach/REDACTION.md`.
