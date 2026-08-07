#!/usr/bin/env python3
"""Refresh the model rate table from OpenRouter's published pricing.

    python3 tools/fetch_rates.py            # show what would change
    python3 tools/fetch_rates.py --write    # rewrite record/cycles/model-rates.json

WHY THIS IS A TOOL AND NOT A HAND-EDIT.

The first rate table was hand-written placeholders — deliberately high, clearly
labelled unverified, and **wrong by roughly an order of magnitude**. That was the
safe direction, but a ceiling that over-states by 9x is barely a ceiling: it passes
spends it was meant to catch. The first live round bounded at $12.45 and cost $1.39.

Prices also change without telling anyone. A hand-maintained table decays silently,
and a silently decayed ceiling is the fail-open shape this repository keeps
rediscovering: a control that reports success because it is no longer measuring
anything. So the rates carry the date they were fetched, and `round_cycle.py` prints
their age.

WHAT THIS DOES NOT ESTABLISH.

The numbers are **what OpenRouter's API said its list prices were, at one moment**.
That is the router's testimony (D-18), exactly like the served-model string and the
provider name it reports. It is not a statement about what was billed, it excludes
router surcharges and cache pricing, and it cannot bind the provider. **Only a
provider-side spending cap is a real limit.** The preflight bound is a refusal
mechanism on this side of the wire and nothing more.

Exit status is 0 when every configured model was priced, 1 when any was missing —
because a model with no rate is refused by the loop rather than defaulted to zero.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

RATES_FILE = REPO_ROOT / "record" / "cycles" / "model-rates.json"
SOURCE = "https://openrouter.ai/api/v1/models"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def wanted_models() -> list[str]:
    """The models the loop actually solicits, read from the loop — not restated.

    A second hand-maintained list of party models would drift from the first, and
    the drift would show up as a model the ceiling silently does not cover.
    """
    import round_cycle as rc
    return sorted({p["model"] for p in rc.PARTIES.values() if p["model"]})


def fetch(models: list[str]) -> tuple[dict, list[str]]:
    with urllib.request.urlopen(urllib.request.Request(SOURCE), timeout=60) as response:
        catalogue = json.loads(response.read().decode("utf-8"))
    priced, limits = {}, {}
    for entry in catalogue.get("data", []):
        if entry["id"] not in models:
            continue
        pricing = entry.get("pricing") or {}
        priced[entry["id"]] = {
            "input": round(float(pricing["prompt"]) * 1_000_000, 4),
            "output": round(float(pricing["completion"]) * 1_000_000, 4)}
        limits[entry["id"]] = {
            "context_length": entry.get("context_length"),
            "max_completion_tokens": (entry.get("top_provider") or {})
                                     .get("max_completion_tokens")}
    for model, limit in limits.items():
        priced[model]["provider_limits"] = limit
    return priced, sorted(set(models) - set(priced))


def build(priced: dict) -> dict:
    return {
        "artifact_type": "model_rate_table",
        "rates_version": f"openrouter-list-{utc_now()[:10]}",
        "recorded_utc": utc_now(),
        "recorded_by": "tools/fetch_rates.py",

        "what_this_is": ("Per-million-token LIST prices, fetched from OpenRouter's public "
                         "model catalogue, used ONLY to compute a preflight upper bound on "
                         "what one cycle can cost so the loop can refuse before it spends."),
        "source": SOURCE,

        "this_is_the_router_s_testimony": (
            "These are what OpenRouter's API reported its list prices to be at "
            f"{utc_now()}. That is testimony (D-18), exactly like the served-model string "
            "and the provider name it reports. It is not a statement of what was billed, "
            "it excludes router surcharges and cache pricing, and prices change without "
            "notice. Refresh with tools/fetch_rates.py --write."),

        "verified_by_custodian": False,
        "verified_note": ("Fetched from the provider's own API rather than typed by hand, "
                          "which is stronger than the placeholder table it replaced and is "
                          "still not a human confirming a bill."),

        "what_a_preflight_bound_cannot_do": [
            "It cannot bind the provider. Only a provider-side spending cap does that.",
            "It cannot account for router surcharges, cache pricing, or reasoning tokens "
            "billed separately.",
            "It bounds the WORST case: every sample emitting max_tokens. Actual spend is "
            "recorded from each response's usage block and reconciled into the ledger.",
        ],

        "usd_per_million_tokens": dict(sorted(priced.items())) | {
            "LOCAL": {"input": 0.0, "output": 0.0,
                      "note": ("Served on the custodian's own hardware. Zero marginal API "
                               "cost; electricity and wear are real and not modelled here.")}},

        "daily_ceiling_usd": 25.0,
        "daily_ceiling_note": ("SOP §4 requires a hard spend ceiling per day, with the run "
                               "refusing rather than truncating. Committed and actual spend "
                               "accumulate in record/cycles/spend-ledger.json on the accepted "
                               "branch; a cycle whose worst case would cross this ceiling "
                               "refuses before its first call."),

        "a_model_with_no_entry_here_is_refused": (
            "The loop will not solicit a model it cannot price. A missing rate is the "
            "condition under which an unbounded spend happens, so it is a refusal rather "
            "than a default."),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="rewrite the rate table; without it, only report")
    args = ap.parse_args(argv)

    models = wanted_models()
    priced, missing = fetch(models)

    old = json.loads(RATES_FILE.read_text(encoding="utf-8")).get("usd_per_million_tokens", {}) \
        if RATES_FILE.is_file() else {}
    for model in models:
        was, now = old.get(model), priced.get(model)
        if not now:
            print(f"  MISSING  {model} — not in the catalogue")
            continue
        change = ""
        if was:
            factor = (was["input"] + was["output"]) / max(now["input"] + now["output"], 1e-9)
            change = f"  (was {was['input']}/{was['output']} — {factor:.1f}x over-stated)" \
                if abs(factor - 1) > 0.05 else "  (unchanged)"
        limits = now.get("provider_limits") or {}
        print(f"  {model:34} in={now['input']:>8}/M  out={now['output']:>8}/M"
              f"  max_out={limits.get('max_completion_tokens')}{change}")

    if missing:
        print(f"\nFAILED — no price for: {', '.join(missing)}")
        print("The loop refuses to solicit a model it cannot price, so this must be resolved.")
        return 1

    if args.write:
        RATES_FILE.write_text(json.dumps(build(priced), indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
        print(f"\nwrote {RATES_FILE.relative_to(REPO_ROOT)}")
    else:
        print("\nreport only — pass --write to update the table.")
    print("List prices as the router reported them. Not a bill, and not a limit: only a "
          "provider-side spending cap is that.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
