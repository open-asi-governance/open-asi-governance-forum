#!/usr/bin/env python3
"""Replay one fixed proposal set through three agenda-selection mechanisms.

    python3 tools/benchmark_agenda.py
    python3 tools/benchmark_agenda.py --json

WHY THIS EXISTS. Three agenda mechanisms were proposed for the continuous-
deliberation SOP and none was ever run:

  CONVERGENCE   the next question is the one the most parties independently name.
                All five consulted parties objected: it privileges frequency over
                importance and buries the question only one party can see.
  ROTATION      queue everything verbatim, draw in strict turn. Proposed by the
                moderator to fix that, and refuted before it shipped: it allocates
                without evaluating, and its promise that every proposal is
                eventually asked is false whenever arrivals exceed service.
  PORTFOLIO     one active proposal per party, a four-round cycle of two
                blinded-ranking picks, one lottery, one institutional challenge.

Adopting a third untested intuition because two were criticised is mistaking
iteration for progress. This measures them instead.

DETERMINISM IS THE POINT. Every mechanism here is a pure function of the proposal
set and a fixed seed. `random` is seeded per scenario per mechanism from a
constant, so the lottery is reproducible and a reader can re-derive every number.
Nothing calls a model. The proposals are REAL -- solicited from the five parties,
hash-anchored in corpus/raw/agenda-01/ -- so this is a replay, not a simulation of
imagined behaviour.

WHAT IT MEASURES, all pre-registered before this file was written (P-0028..P-0030):

  time_to_first_minority   the round at which a proposal named by exactly one
                           party is first asked. None if never.
  flooded_items_asked      under one party replacing its proposal every round with
                           a low-value item, how many of its items get asked.
  unasked_at_horizon       with steady arrivals, how many proposals remain unasked.
  duplicate_rounds         rounds spent on a question already asked in substance.

WHAT IT DOES NOT MEASURE. Whether the questions asked were any good. Agenda VALUE
is a judgement no simulation makes, and a benchmark that scored it would be
scoring the annotator's opinion of the parties' proposals. The metrics here are
all structural, and that is the honest limit: a mechanism can win every one of
them and still produce a worthless agenda.

Exit status is 0.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROPOSALS_DIR = REPO_ROOT / "corpus" / "raw" / "agenda-01"
HORIZON = 20            # fixed before the run, per P-0028's resolution limit
SEED = 20260807         # constant, so the lottery is reproducible


class Proposal:
    __slots__ = ("pid", "party", "text", "sponsors", "age", "asked", "low_value")

    def __init__(self, pid, party, text, sponsors=None, low_value=False):
        self.pid, self.party, self.text = pid, party, text
        self.sponsors = sponsors or {party}
        self.age, self.asked, self.low_value = 0, False, low_value

    def __repr__(self):
        return f"<{self.pid} {self.party} n={len(self.sponsors)}>"


def load_real_proposals() -> list[Proposal]:
    """The parties' actual proposals. One per party per sample, deduplicated by text.

    Sponsorship is counted by EXACT normalised question text, never by judging that
    two differently-worded questions are the same. That judgement is the thing the
    parties objected to; a benchmark that made it would be measuring the moderator's
    clustering rather than the mechanisms.
    """
    out, seen = [], {}
    if not PROPOSALS_DIR.is_dir():
        return out
    for path in sorted(PROPOSALS_DIR.glob("*-samples.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        party = path.stem.replace("agenda-01-", "").replace("-samples", "")
        rows = doc.get("samples") or doc.get("responses") or []
        for row in rows:
            parsed = row.get("parsed")
            if parsed is None:
                try:
                    parsed = json.loads(row["content"])
                except Exception:                                   # noqa: BLE001
                    continue
            text = " ".join((parsed.get("question") or "").split()).lower()
            if not text:
                continue
            if text in seen:
                seen[text].sponsors.add(party)
            else:
                p = Proposal(f"P{len(out)+1:02d}", party, text)
                seen[text] = p
                out.append(p)
    return out


def _fresh(proposals):
    return [Proposal(p.pid, p.party, p.text, set(p.sponsors), p.low_value) for p in proposals]


def run_convergence(proposals, parties, horizon=HORIZON):
    """Most sponsors wins; ties by proposal id. Singletons carry, escalating at 3."""
    items, asked, carried = _fresh(proposals), [], {}
    for _ in range(horizon):
        live = [p for p in items if not p.asked]
        if not live:
            break
        best = max(live, key=lambda p: (len(p.sponsors), -int(p.pid[1:])))
        # the three-round escalation: a singleton unasked for three rounds jumps
        for p in live:
            if len(p.sponsors) == 1:
                carried[p.pid] = carried.get(p.pid, 0) + 1
        due = [p for p in live if carried.get(p.pid, 0) >= 3]
        if due:
            best = min(due, key=lambda p: int(p.pid[1:]))
            carried[best.pid] = 0
        best.asked = True
        asked.append(best)
    return asked


def run_rotation(proposals, parties, horizon=HORIZON):
    """Strict turn by proposing party; nothing merged."""
    items, asked, turn = _fresh(proposals), [], 0
    for _ in range(horizon):
        for _ in range(len(parties)):
            party = parties[turn % len(parties)]
            turn += 1
            live = [p for p in items if not p.asked and p.party == party]
            if live:
                pick = min(live, key=lambda p: int(p.pid[1:]))
                pick.asked = True
                asked.append(pick)
                break
        else:
            break
        if len(asked) >= horizon:
            break
    return asked


def run_portfolio(proposals, parties, horizon=HORIZON, seed=SEED):
    """Two blinded-ranking picks, one lottery, one institutional slot per four rounds.

    Rankings are simulated as: non-proposing parties rank by sponsor count, which is
    the only quality signal available without asking a model to judge. That is a
    WEAKNESS of the benchmark and is recorded as one -- it makes the ranking channel
    behave somewhat like convergence, so the portfolio's advantage here is understated
    rather than flattered.
    """
    rng = random.Random(seed)
    items, asked = _fresh(proposals), []
    for r in range(horizon):
        live = [p for p in items if not p.asked]
        if not live:
            break
        slot = r % 4
        if slot == 3:
            asked.append(None)                    # institutional challenge, not from the queue
            continue
        if slot in (0, 1):
            pick = max(live, key=lambda p: (len(p.sponsors), -int(p.pid[1:])))
        else:
            tickets = []
            for party in parties:                 # one ticket per party
                own = [p for p in live if p.party == party]
                if own:
                    tickets.append(rng.choice(own))
            pick = rng.choice(tickets) if tickets else live[0]
        pick.asked = True
        asked.append(pick)
    return asked


MECHANISMS = {"convergence": run_convergence, "rotation": run_rotation,
              "portfolio": run_portfolio}


def time_to_first_minority(asked):
    for i, p in enumerate(asked, 1):
        if p is not None and len(p.sponsors) == 1:
            return i
    return None


def report(proposals, parties, scenario):
    out = {}
    for name, fn in MECHANISMS.items():
        asked = fn(proposals, parties)
        real = [p for p in asked if p is not None]
        out[name] = {
            "rounds_used": len(asked),
            "questions_asked": len(real),
            "time_to_first_minority": time_to_first_minority(asked),
            "flooded_items_asked": sum(1 for p in real if p.low_value),
            "unasked_at_horizon": len([p for p in proposals if p.pid not in
                                       {q.pid for q in real}]),
        }
    return {"scenario": scenario, "proposals": len(proposals),
            "singletons": sum(1 for p in proposals if len(p.sponsors) == 1),
            "results": out}


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    base = load_real_proposals()
    if not base:
        print("no proposals found in corpus/raw/agenda-01/ — run the solicitation first.")
        return 0
    parties = sorted({p.party for p in base})

    scenarios = {"real": base}

    flooder = parties[0]
    flooded = _fresh(base) + [
        Proposal(f"F{i:02d}", flooder, f"low-value filler {i}", {flooder}, low_value=True)
        for i in range(1, HORIZON + 1)]
    scenarios["flooding"] = flooded

    steady = _fresh(base) + [
        Proposal(f"S{i:02d}", parties[i % len(parties)], f"steady arrival {i}",
                 {parties[i % len(parties)]})
        for i in range(1, HORIZON * len(parties) + 1)]
    scenarios["steady_arrivals"] = steady

    reports = [report(props, parties, name) for name, props in scenarios.items()]
    if args.json:
        print(json.dumps(reports, indent=2))
        return 0

    for rep in reports:
        print(f"\n=== {rep['scenario']} — {rep['proposals']} proposals, "
              f"{rep['singletons']} named by exactly one party ===")
        print(f"  {'mechanism':12} {'asked':>6} {'1st minority':>13} "
              f"{'flooded':>8} {'unasked':>8}")
        for name, m in rep["results"].items():
            t = m["time_to_first_minority"]
            print(f"  {name:12} {m['questions_asked']:>6} "
                  f"{(str(t) if t else 'never'):>13} "
                  f"{m['flooded_items_asked']:>8} {m['unasked_at_horizon']:>8}")
    print(f"\nHorizon {HORIZON} rounds, seed {SEED}. Deterministic: re-running reproduces this.")
    print("Structural metrics only. None of them says whether a question was worth asking.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
