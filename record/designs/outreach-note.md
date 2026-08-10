# The outreach note — for the custodian to send

**This is yours to send, not the workbench's.** It uses your name and your relationships, and a
cold approach from an automated layer would be both less effective and less honest.

Target: **ten** engineers or research groups, at least one commercial and one academic. Codex's
adverse outcome is *no serious attempt after 6–8 weeks* **with the outreach actually done** — the
outreach being skipped is not a result, it is an absence of evidence.

---

## Who

The people most likely to bite are not governance people. They are **infrastructure and
reliability engineers** who have personally been burned by a check that stayed green — and that is
nearly all of them. The pitch is not "help govern AI"; it is *"four of five of our health checks
could not fail, and here is the afternoon that found out."*

Rough shape of a list worth ten slots:

* two or three people running inference or agent-serving infrastructure at labs of any size
* one or two academic systems groups — ML systems, dependable computing, empirical SE
* one or two people who work on assurance cases or safety cases outside AI (avionics, medical
  devices, nuclear); this control is old news in those fields and their criticism is the most
  valuable you can get
* one or two AI-evals people, for whom the "safety eval that never reached the classifier" example
  will land hardest
* one skeptic who will tell you it is trivial or already solved. If they are right, that is the
  cheapest finding available.

---

## The note

> Subject: a check that stayed green through a 4h37m outage — would you break ours?
>
> Hello —
>
> One of my inference services ran for four hours thirty-seven minutes after it had permanently
> died, with its health check returning 200 the whole time. The check issued a greedy request; the
> code that failed was on the sampled path, so the check executed none of it. It was authentic,
> current, and structurally incapable of noticing.
>
> I wrote up the one-sentence rule that would have caught it — every check must ship with a
> condition under which it is *required* to fail, and you must have run that condition and watched
> it fail — and then applied it adversarially to my own remaining checks. **Four of five survived
> the condition they existed to detect.** All four are now fixed.
>
> What I do not know is whether the write-up is a general mechanism or just a description of my
> own architecture. The only way to find out is for someone else to build a verifier from the text
> without asking me what it meant.
>
> That is the ask: **read the spec, build a verifier, and send me every question you had to guess
> at.** The questions are what I actually want — they are the evidence about whether the
> specification is any good. An afternoon, not a project.
>
> https://github.com/open-asi-governance/open-asi-governance-forum — `CHALLENGE.md`
>
> If you read it and think it is trivial or long-solved in your field, I would genuinely rather
> hear that than not, and I will publish it.
>
> — Stephen

---

## What not to say

* **Do not say "governance framework."** It is one requirement with a verifier, and the word
  invites a category the reader already has opinions about.
* **Do not mention alignment or ASI.** Nothing in this control bears on either, our own register
  says so in its first section, and leading with it would be the overclaim the profile forbids.
* **Do not ask them to join, endorse, or adopt anything.** Ask for an implementation and a list of
  questions.
* **Do not offer to help them past a confusion.** That destroys exactly the measurement — an
  implementation completed with the author's help is a port, not evidence. Answer publicly, as a
  specification defect, or not at all.

## What counts as a result

| outcome | what it establishes |
|---|---|
| a conforming verifier built from the text alone | the control reaches ICP Level 2. **The first thing in this record that has.** |
| an attempt that fails, with the questions recorded | the specification encodes our architecture. Publishable, and more useful than silence. |
| their fixture that our verifier gets wrong | a defect in our verifier or our spec. Best single outcome per hour spent. |
| **no attempt after 6–8 weeks, outreach done** | the adverse result. Record it. |
| no attempt, outreach not done | **nothing.** Not a result, and not something to report as one. |

## After sending

Record who was approached and when, in a form that makes the last row of that table checkable.
Otherwise "we did outreach" becomes another claim not causally downstream of anything.
