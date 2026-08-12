# Correction to the spend ledger, 2026-08-12

**87 of the ledger's 141 entries were written by a test and have been removed.**
This file is the record of them. Corrections attach; the removed rows are reproduced here in full
shape so that what the ledger said, and for how long, remains checkable.

## What happened

`tools/tests/test_gate_negative_controls.py` contains an arm asserting that `record_spend.py`
refuses an unknown cohort rather than emitting a cost. It ran:

    python3 tools/record_spend.py --cohort no-such-cohort-zzqx

`record_spend.py` did **not** validate the cohort. It appended a zero-unit row and exited 0. The
assertion was `returncode != 0 or not emitted_cost` — and because no dollar figure was printed,
the second disjunct held and the arm passed. **So the test proved nothing and polluted the ledger
on every run**, including every run inside `land.py`'s `tests` gate, which is every landing.

The rows are identical apart from being repeated: a single fixed timestamp, a cohort that was
never solicited, and zeros throughout.

```json
{
  "utc": "2026-08-10T18:00:00Z",
  "round": "no-such-cohort-zzqx",
  "worst_case_usd": null,
  "actual_usd": null,
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "units_seen": 0,
  "units_reporting_usage": 0,
  "rates_version": "openrouter-list-2026-08-07",
  "rates_recorded_utc": "2026-08-07T09:18:03Z",
  "unpriced_models": [],
  "actual_note": "Summed from each sample's usage block, INCLUDING failures and rejections -- a schema-invalid sample was still paid for, and dropping it would understate exactly the runs that went wrong. null means no arm reported usage, not zero. Priced from a dated rate table rather than an invoice, so this is an estimate. Local-arm inference and prepaid subscription usage are NOT in this ledger at all.",
  "backfilled": true
}
```

## What this means for anything computed from the ledger

Every removed row carried `worst_case_usd: null`, `actual_usd: null` and zero tokens, so **no
dollar total or token total was distorted** — a sum over the ledger was unaffected. What was
distorted is any COUNT of entries, any statement about how many cohorts have recorded spend, and
the ledger's own credibility as a record of what happened. `87` of `141` rows —
61% — described nothing.

The ledger before this correction hashed to `0332a099349984fb32665187b041edf3f3a05fa649f05200a7a177156bc02de5`.

## What was repaired

* `record_spend.py` now refuses a cohort that is not in `solicited_cohorts()` before appending
  anything, under guard `RS-01`.
* The negative control now runs against a temporary ledger, requires a non-zero exit, and asserts
  the ledger is **byte-identical** afterwards. Asserting only that no cost was printed is what let
  an append pass as a refusal.
* Filed as **D-62**.

## What this does not establish

That no other tool writes to this ledger without validating what it writes. Only `record_spend.py`
was examined, because it was the one the fixture invoked.
