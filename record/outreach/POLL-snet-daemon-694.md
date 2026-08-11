# Polling singnet/snet-daemon#694 — the first FICP defect report to a third party

**Any session can run this. It needs no scheduler and no state.**

Submitted **2026-08-11T14:51:24Z** by the custodian (`StephenLReed`), from
`record/attestations/ficp-2026-08-11-snet-daemon.json` and the executed reproduction recorded in
that day's landing.

https://github.com/singnet/snet-daemon/issues/694

## The query

```bash
source /home/reed/environment-secrets-agi-agents.sh
GH_TOKEN="$GH_TOKEN_OAGF" gh api repos/singnet/snet-daemon/issues/694 \
  --jq '{state, comments, labels:[.labels[].name], updated_at}'
GH_TOKEN="$GH_TOKEN_OAGF" gh api repos/singnet/snet-daemon/issues/694/comments \
  --jq '.[] | {who:.user.login, at:.created_at, body:.body[0:400]}'
```

## Negative-control it before trusting a zero

**An empty result and a broken query are indistinguishable.** Run the identical comments query
against an issue known to have comments; if that also returns 0, the query is broken, not the
issue quiet.

```bash
GH_TOKEN="$GH_TOKEN_OAGF" gh api repos/singnet/snet-daemon/issues/682/comments --jq 'length'   # expect 2
```

**Done 2026-08-11:** the control returned **2**, the real query returned **0**. The zero was real.

A weaker control was tried first and rejected: issue #693 also has 0 comments, so comparing
against it would have proved only that the query discriminates *state*. Recorded because picking
the first available control rather than a discriminating one is how a negative control becomes
decoration.

## What counts

| observation | meaning |
|---|---|
| a maintainer reproduces it | **the strongest available outcome.** The method found a real defect in a system this project did not build, confirmed by someone who did |
| a fix, or a status change for the unconfigured case | the defect was real and is closed. Record it, and record that the profile is not thereby validated |
| **"working as intended"** | **a result, not a rejection.** Anticipated when the issue was drafted. The narrow reply is that the ping's result is reported in the same field, with the same value, as a verified check — but do not argue past that. A maintainer saying "we know, it's fine" is a finding about how the profile lands |
| *"this is just fault injection"* | **exactly what the method note asks for**, and it is worth more than a fix. Record it verbatim |
| labelled and ignored | weak signal; note the label |
| **silence after 6 weeks (2026-09-22)** | the adverse outcome for THIS route. Record it. It does not extend or replace the 2026-10-05 outreach prediction, which is a separate claim about a separate channel |

## What a response would and would not establish

**Would:** that the profile finds defects outside the single implementer it was derived from —
currently supported by one execution, ours, which is not the same as a maintainer agreeing.

**Would not:** ICP standing. That still requires a stranger building a conforming verifier from the
specification text. A maintainer fixing a bug we reported is not an independent implementation, and
counting it as one would be the assent-inflation this record exists to avoid.
