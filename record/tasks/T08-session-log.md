# T-08 · Deterministic session/decision log (recurring)

**Track A — Corpus Surface** · branch `session/site` · no GPU · status: open · **do this first**

Trigger: at the end of every working session, and before any material is put before the OAGF.

## Form
`record/sessions/YYYY-MM-DD-<n>.md`, generated as far as possible from evidence already in the
repository rather than composed from memory:
- commits in the window (hash, subject, files touched) — derived from git, not narrated
- artifacts created or changed, with hashes
- solicitations run: spec hash, k requested, k collected, variance, phase
- predictions filed and resolved, with outcomes **including the misses**
- defects found, by whom, and where each was corrected
- decisions taken, and **who took them** — custodian vs annotator vs reviewer, per D-16
- what was attempted and abandoned, and why

Add `tools/build_session_log.py` so the narrative surface is small and the derived surface large.
*A log a party writes freehand about its own work is testimony; a log derived from committed
evidence is closer to record.*

## Sanitisation — the trust-boundary sense, per ASP §1
Two categories are withheld:
1. **Secrets** — token values and their hashes, credentials, private keys.
2. **Non-public information** — internal infrastructure topology, host names, absolute paths,
   Tailscale addresses, and non-public content of Consullo's own experiment documentation:
   unpublished results, internal technical reports, agent specifications, unreleased measurements.

Per CONTRIBUTING and ChatGPT §6, **withholding is itself recorded**: that material was withheld,
its category, the reason, and the maximum safe abstraction publishable. Silent omission is not
sanitisation.

## What sanitisation is *not*
Selection for presentation. Failures, reversals, abandoned approaches and scored-incorrect
predictions are not non-public information and stay at the same prominence as successes.
**A log containing no failures is evidence it is being curated rather than sanitised.**

## Why
- D-05 exists because a prompt was lost after the fact.
- ICP §6 requires an implementer's failures to be recorded; failures are what vanishes between
  sessions.
- Three capture-integrity incidents on 2026-08-06 were each caught by accident.

## Acceptance
- Mechanical sections derived by tool, not hand-written.
- No secrets or non-public information; every withholding declared with category, reason and
  maximum safe abstraction.
- Misses and reversals at equal prominence to successes.
- Stated at the top: who wrote it, that they are a party to the record, and that it is secondary to
  the artifacts and commit history it summarises.

## Open question for the custodian
Scheduled run (cron/loop) or session-triggered? Automatic is more reliable and less selective; it
also produces logs nobody reads. **Recommend session-triggered** until there is evidence anyone
reads them.

---

## Session state — Corpus Surface, 2026-08-06. **T-08 is DONE, with the brief amended.**

### Done
- `tools/build_session_log.py` — **7786f1c**
- `record/sessions/2026-08-06-A.manifest.json` + generated `record/sessions/2026-08-06-A.md` — **7786f1c**

### The brief was amended, not merely implemented
Codex reviewed the design before it was written and rejected **both** of the brief's central asks.
The custodian was asked and adopted the rescope.

1. **Sanitisation is not implemented, and should not be.** The brief specifies deterministic
   withholding of secrets and non-public information. `tools/` runs no LLM, and "is this an internal
   hostname / a non-public result" is a judgement. A regex denylist is D-25 in its purest form — an
   unvalidated classifier published as authoritative — and its errors are **asymmetric**: a false
   negative leaks into public git history permanently, a false positive silently erases adverse
   evidence. Worse, "withholding must itself be recorded" **cannot be mechanically enforced at all**,
   because no tool can distinguish "nothing was withheld" from "something was withheld silently."
   The renderer therefore emits only typed values and quoted commit subjects, redacts nothing, and
   says so in its own header. **The trust boundary is custodian review of the outgoing commit.**
2. **It is not an audit log.** Derivation proves lineage, not truth. The party that writes the log
   controls session boundaries, commit granularity, commit messages, and what reaches git at all.
   The honest claim is: *"a deterministic renderer transformed a declared set of repository objects
   into this document."* Not that the set is complete or its contents true.

### Design decisions worth not re-deriving
- **The window is declared, not inferred.** Git holds commits and reachability, not sessions. Four
  concurrent branches cannot be expressed as one `A..B` range, and a single `tips --not bases`
  erases commits belonging to one lane but ancestral to another lane's later base. A manifest names
  an exclusive base and inclusive tip **per lane**, each range computed separately. Declaring tips
  also means the log can never fall inside its own window.
- **Trust classes are printed on every fact**: `[1]` observed git objects, `[2]` declared by the
  session about itself, `[3]` independently witnessed. **`[3]` is always empty** — this project has
  no such control, and the emptiness is the point rather than an oversight.
- **Commit subjects are kept, labelled `[2]`.** Codex argued for omitting them as untrusted author
  metadata. Overruled: a log the custodian will not read protects nothing, and labelling is the
  mechanism this repository already uses everywhere else.
- **Derived sections are recomputed, never copied.** Predictions are diffed between committed
  endpoints. Declared `k_collected` is checked against samples actually present in the committed raw
  file — 25 solicitations, 0 disagreements, two rounds that collected 19 of 20 and say so.
- Content is read from commit trees via `git show`, **never the working tree**, so a later edit
  cannot change a rendered window. Verified.

### Remaining
- **Open question from the brief is still open:** scheduled vs session-triggered. Still recommend
  session-triggered until there is evidence anyone reads them. No cron has been set up.
- Commit ordering is git's topological order, which is stable for fixed endpoints but is not a
  canonical cross-implementation guarantee. Mitigated by also emitting a digest over the sorted
  commit set, so the **set** is the claim and the order is for the reader. If that is not enough,
  switch to lexical full-hash ordering and accept the loss of chronology.
