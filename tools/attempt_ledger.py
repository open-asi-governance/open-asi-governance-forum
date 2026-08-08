#!/usr/bin/env python3
"""An append-only ledger of authorization attempts. Refuses a second draw on one question.

    from attempt_ledger import Ledger
    Ledger().record("activation", party="gpt", eligible_ids=[...], prompt_sha256=...)

**DETERMINISTIC.** No LLM, no network. A guard, not a generator.

What this prevents
------------------
activation-01 asked five parties to name one active proposal, k=5, unanimity required. Three
came back non-unanimous. The obvious next move -- ask those three again -- is the one thing the
frozen rule forbade, and the reason is not obvious enough to be left to a comment in a prompt:

    A party with a per-sample tendency of 0.9 toward one id is unanimous at k=5 about 59% of
    the time. Two attempts reach unanimity once about 83% of the time. Repetition manufactures
    authorization.

And it is worse than plain multiplicity: a retry decided AFTER seeing which parties failed,
applied ONLY to the parties that failed, is outcome-conditioned sampling. Recording the attempt
number makes the distortion visible; it does not remove it.

External review's instruction was to make this machine-enforced rather than remembered, so that
no future prompt can silently re-ask the same party the same question. That is this file.

What counts as "the same question"
-----------------------------------
The identity of an authorization question is (instrument, party, ELIGIBLE SET). The eligible set
is what a party is choosing among, and changing it changes the question:

* re-asking gpt to choose among {P011,P012,P013,P014,NONE} is the SAME question -- refused;
* asking gpt to choose among {P011..P014} plus five newly submitted candidates is a DIFFERENT
  question -- allowed, because the option set it is ranging over is not the one it already
  answered.

This is why a replacement-submission instrument is legitimate where a retry is not, and the
distinction is enforced here by hash rather than asserted in prose.

Uniformity is not enforced here, and cannot be
-----------------------------------------------
This guard cannot see whether an instrument was offered to every party or only to the ones that
failed. That is a property of the caller's loop, not of any single record. The ledger records
which parties were asked and when, so the asymmetry is RECOVERABLE from the record -- but a
caller determined to ask only the losers will succeed. Nothing here should be read as proving
that did not happen.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "record" / "agenda" / "attempt-ledger.jsonl"


class RedrawRefused(Exception):
    """The same party has already been asked this question over this option set."""


def eligible_set_sha256(eligible_ids) -> str:
    """Order-independent hash of the option set.

    SORTED before hashing: a caller that shuffled the enum would otherwise present the same
    question as a new one, which is the loophole this guard exists to close.
    """
    canonical = json.dumps(sorted(str(i) for i in eligible_ids), separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class Ledger:
    """Append-only. Every entry keeps the hash of the one before it."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or LEDGER_PATH

    def entries(self) -> list[dict]:
        if not self.path.is_file():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def prior(self, instrument: str, party: str, eligible_ids) -> list[dict]:
        """Every prior attempt at this exact question."""
        digest = eligible_set_sha256(eligible_ids)
        return [e for e in self.entries()
                if e["instrument"] == instrument and e["party"] == party
                and e["eligible_set_sha256"] == digest]

    def check(self, instrument: str, party: str, eligible_ids) -> None:
        """Raise if this is a redraw. Call BEFORE soliciting, never after."""
        previous = self.prior(instrument, party, eligible_ids)
        if previous:
            when = ", ".join(e["utc"] for e in previous)
            raise RedrawRefused(
                f"{party} has already been asked the {instrument!r} question over this exact "
                f"option set ({when}). Re-asking it is a second draw on one question, and a "
                f"second draw decided after seeing the first result is outcome-conditioned "
                f"sampling. Change what the party is choosing AMONG, or record the earlier "
                f"outcome as final.")

    def record(self, instrument: str, party: str, eligible_ids, prompt_sha256: str,
               k: int, threshold: str, cohort: str) -> dict:
        """Check, then append. The check is not optional and not separable."""
        self.check(instrument, party, eligible_ids)
        entries = self.entries()
        prev = (hashlib.sha256(
            json.dumps(entries[-1], sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest() if entries else "0" * 64)
        entry = {
            "instrument": instrument,
            "cohort": cohort,
            "party": party,
            #  The full option set, not only its hash. A hash proves two questions differ; it
            #  cannot tell a reader HOW, and a reader auditing an asymmetry needs the sets.
            "eligible_ids": sorted(str(i) for i in eligible_ids),
            "eligible_set_sha256": eligible_set_sha256(eligible_ids),
            "prompt_sha256": prompt_sha256,
            "k": k,
            "threshold": threshold,
            "attempt_index": len([e for e in entries
                                  if e["instrument"] == instrument and e["party"] == party]) + 1,
            "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "prev_sha256": prev,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


def main() -> int:
    """Print the ledger, and verify its chain."""
    ledger = Ledger()
    entries = ledger.entries()
    if not entries:
        print("no attempts recorded")
        return 0
    broken = 0
    prev = "0" * 64
    for entry in entries:
        if entry["prev_sha256"] != prev:
            print(f"  CHAIN BROKEN at {entry['cohort']}/{entry['party']}")
            broken += 1
        prev = hashlib.sha256(
            json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        print(f"  {entry['utc']}  {entry['cohort']:16} {entry['party']:8} "
              f"attempt {entry['attempt_index']}  over {len(entry['eligible_ids'])} option(s)")
    print(f"\n{len(entries)} attempt(s), {broken} chain break(s)")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
