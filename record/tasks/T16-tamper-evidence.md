# T-16 · Tamper-evident Qwen3 invocation path

**Track D — Provenance Hardening** · branch `session/signing` · **needs the custodian** ·
status: open

Operator proposal 2026-08-06: record Qwen3 API use with its settings as an immutable record, sign
and hash the code, and mitigate every way the custodian could personally corrupt its use in a
tamper-evident manner.

## Why this is worth more than it sounds
It does not merely mitigate the hosted-party asymmetry — **it can invert it.** No one can instrument
OpenAI's server, so every frontier contribution rests on an unverifiable claim that a text came from
a given system with given settings; **D-18** records that as permanently unfixable for them. For a
locally served model it is fixable. Fully instrumented, the party the custodian controls becomes the
only party whose invocations can be checked at all.

## The threat model splits, and signing covers only half
- **Class A — post-hoc tampering.** Editing a result after seeing it, deleting a run, altering a
  recorded setting. Hash-anchored raw, the manifest, append-only history and signed commits handle
  this. Most already exists.
- **Class B — selection before the fact.** Run a probe twenty times and commit the one you like;
  pick the temperature after seeing which distribution reads better; reword until the answer
  arrives. **Nothing is tampered with.** Every artifact is genuine and correctly signed, and the
  *set* is curated. With one party controlling the pipeline this is the dominant risk, and **signing
  does not touch it.**

## And a local signature does not bind the signer
The custodian holds the key. A locally signed record proves he produced it — which nobody doubts. It
cannot show he did not produce three others and discard them. **What binds is external anchoring**:
a third party attesting a hash existed at a time. Pushing to GitHub is a weak form; publishing the
chain head to an independent timestamping service is stronger.

## Build, in dependency order
1. **Discharge D-13 first.** There are **no cryptographic signatures anywhere in this repository**
   despite a `signatures` field in the adopted schema. Everything below presupposes signing that
   does not exist. SSH commit signing, an `allowed_signers` file committed so signatures verify for
   anyone cloning, branch protection requiring signed commits.
2. **Server-side invocation ledger** — the mechanism that addresses Class B. Instrument
   `trtllm-serve`, **not the client**: a client tool is bypassed with one `curl`. Append-only,
   hash-chained, written at request time, covering **every** invocation whether or not the result is
   ever committed. Each entry: prompt hash, full settings, output hash, timestamp, chain position,
   and the hash of the tool that issued it.
3. **Corpus artifacts cite their chain position.**
4. **Publish the chain head** to the repository on a schedule.
5. **A gap report**: invocations in the ledger versus artifacts in the corpus, per spec. Curation
   becomes arithmetic a reader can see rather than a matter of trust. Unexplained gaps are the
   finding.

## What stays irreducible — record it, do not paper over it
- **Question selection.** The custodian chooses what is asked. No cryptography reaches it, and D-23
  was an answer built into a prompt that would have been perfectly signed.
- **Spec authorship.** Prompts, enums and coding rules are written by an interested party; D-25 and
  D-27 were defects in instruments, not records.
- **A second unlogged server.** Possible. Detectable only by cross-checking GPU utilisation against
  ledger volume.

## Custodian-blocked
Key decisions. **Do not generate or register keys unilaterally.**

## Acceptance
- Commits verify as signed **for a third party cloning the repository**, not merely for GitHub.
- Every Qwen invocation appears in the ledger; ledger integrity checkable by a committed tool.
- **Running a probe and discarding the result leaves a visible gap.**
- The irreducible residue is stated in the corpus rather than implied to be covered.
- The goal is stated honestly as making corruption **evidenced-against, not impossible**.
