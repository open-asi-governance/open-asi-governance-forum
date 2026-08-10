#!/usr/bin/env python3
"""Record what a solicitation cohort actually cost, from the usage in its raw material.

    python3 tools/record_spend.py --cohort ratification-02
    python3 tools/record_spend.py --backfill          # every unrecorded cohort
    python3 tools/record_spend.py --report            # what is recorded, and what is missing

**DETERMINISTIC.** No LLM, no network. Reads raw usage blocks and the rate table.

Why this exists
---------------
`record/cycles/spend-ledger.json` is the artifact that answers "what has this project spent". On
2026-08-10 its most recent entry was **round-019, from the previous day**, while three routed
cohorts had run that morning consuming **189,807 tokens**. Only `round_cycle.py` ever wrote to
it; every instrument built since — the qualification gate, both ratification ballots — spends the
custodian's money and records none of it.

That is the class this project keeps finding: **an artifact that claims to record something, and
does not record it, while looking complete.** A reader consulting the ledger would have concluded
the project spent nothing that day.

What it does
------------
Sums `usage.prompt_tokens` and `usage.completion_tokens` from every raw sample in a cohort,
prices them against the recorded rate table, and appends one ledger entry per cohort. It counts
**rejected and failed attempts too** — a sample that came back schema-invalid was still paid for,
and a spend figure that silently drops failures understates exactly the runs that went wrong.

What it cannot establish
-------------------------
* **That the price is right.** Rates come from a dated table, not from an invoice. A provider
  that changed pricing since is not detected, so `actual_usd` is an estimate and is labelled one.
* **That every cost is here.** Local-arm inference is free at the point of use and consumes
  electricity and a GPU nobody bills for. Codex and Claude subscription usage is prepaid monthly
  and appears nowhere in this ledger.
* **That an unreported usage block means zero.** Where an arm reports no usage the entry records
  `null` and says so, because zero and unknown are different and only one of them is honest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "corpus" / "raw"
LEDGER = REPO_ROOT / "record" / "cycles" / "spend-ledger.json"
RATES = REPO_ROOT / "record" / "cycles" / "model-rates.json"


def load_rates() -> dict:
    if RATES.is_file():
        return json.loads(RATES.read_text(encoding="utf-8"))
    return {}


def usage_for(cohort: str) -> dict:
    """Token usage for a cohort, counting failures and rejections as well as accepted samples."""
    directory = RAW / cohort
    per_model: dict[str, dict] = {}
    units = reported = 0
    for path in sorted(directory.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:                                               # noqa: BLE001
            continue
        for container in ("samples", "responses", "failures", "rejected"):
            for unit in (doc.get(container) or []):
                if not isinstance(unit, dict):
                    continue
                units += 1
                usage = unit.get("usage")
                if not isinstance(usage, dict):
                    continue
                reported += 1
                model = ((unit.get("delivery_chain") or {}).get("served_model")
                         or (doc.get("spec") or {}).get("reached_via") or "unknown")
                bucket = per_model.setdefault(model, {"prompt": 0, "completion": 0, "n": 0})
                bucket["prompt"] += usage.get("prompt_tokens") or 0
                bucket["completion"] += usage.get("completion_tokens") or 0
                bucket["n"] += 1
    return {"per_model": per_model, "units_seen": units, "units_reporting_usage": reported}


def price(per_model: dict, rates: dict) -> tuple[float | None, list]:
    #  The table is keyed by router model id under `usd_per_million_tokens`, with `input` and
    #  `output` rates. Reading `models` -> `prompt_usd_per_mtok` found nothing and priced 37 of
    #  54 cohorts at null -- a ledger that says "unknown" everywhere is only marginally better
    #  than one that says nothing, and it was MY guess at the schema, not the schema.
    table = rates.get("usd_per_million_tokens") or {}
    total, priced, unpriced = 0.0, 0, []
    for model, u in per_model.items():
        entry = table.get(model)
        if not isinstance(entry, dict):
            unpriced.append(model)
            continue
        total += (u["prompt"] / 1_000_000) * float(entry.get("input", 0) or 0)
        total += (u["completion"] / 1_000_000) * float(entry.get("output", 0) or 0)
        priced += 1
    return (round(total, 4) if priced else None), unpriced


def recorded_cohorts() -> set:
    if not LEDGER.is_file():
        return set()
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    return {e.get("round") for e in (doc.get("entries") or [])}


def solicited_cohorts() -> list:
    return sorted(d.name for d in RAW.iterdir()
                  if d.is_dir() and any(d.glob("*samples*.json")))


def append(cohort: str, rates: dict) -> dict:
    u = usage_for(cohort)
    actual, unpriced = price(u["per_model"], rates)
    prompt = sum(v["prompt"] for v in u["per_model"].values())
    completion = sum(v["completion"] for v in u["per_model"].values())
    entry = {
        "utc": "2026-08-10T18:00:00Z",
        "round": cohort,
        "worst_case_usd": None,
        "actual_usd": actual,
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "units_seen": u["units_seen"],
        "units_reporting_usage": u["units_reporting_usage"],
        "rates_version": rates.get("rates_version") or "unknown",
        "rates_recorded_utc": rates.get("recorded_utc"),
        "unpriced_models": unpriced,
        "actual_note": (
            "Summed from each sample's usage block, INCLUDING failures and rejections -- a "
            "schema-invalid sample was still paid for, and dropping it would understate exactly "
            "the runs that went wrong. null means no arm reported usage, not zero. Priced from a "
            "dated rate table rather than an invoice, so this is an estimate. Local-arm "
            "inference and prepaid subscription usage are NOT in this ledger at all."),
        "backfilled": True,
    }
    doc = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.is_file() else {"entries": []}
    doc.setdefault("entries", []).append(entry)
    LEDGER.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--cohort")
    parser.add_argument("--backfill", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    rates = load_rates()

    if args.report or not (args.cohort or args.backfill):
        have, all_c = recorded_cohorts(), solicited_cohorts()
        missing = [c for c in all_c if c not in have]
        print(f"  cohorts with raw material: {len(all_c)}")
        print(f"  recorded in the ledger:    {len(all_c) - len(missing)}")
        print(f"  UNRECORDED:                {len(missing)}")
        for c in missing:
            u = usage_for(c)
            tok = sum(v["prompt"] + v["completion"] for v in u["per_model"].values())
            print(f"    {c:34s} {tok:>9,} tokens across {u['units_seen']} unit(s)")
        if missing:
            print("\n  An artifact that claims to record spend and does not record it looks "
                  "exactly\n  like a project that spent nothing. Run --backfill.")
        return 1 if missing else 0

    targets = [args.cohort] if args.cohort else \
        [c for c in solicited_cohorts() if c not in recorded_cohorts()]
    for cohort in targets:
        e = append(cohort, rates)
        print(f"  {cohort:34s} {e['prompt_tokens']:>8,}p {e['completion_tokens']:>8,}c  "
              f"usd={e['actual_usd']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
