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
