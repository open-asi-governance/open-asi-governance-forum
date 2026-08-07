#!/usr/bin/env python3
"""Agenda selectors: the pluggable choice of which question a round asks.

    from agenda_selectors import SELECTORS, load_queue
    question = SELECTORS["portfolio"](queue, parties, round_index, seed)

WHY THIS IS A SEPARATE MODULE WITH A NARROW INTERFACE.

Three mechanisms have been proposed for choosing the next question and **none has
been run**:

  convergence  the question the most parties independently name. Rejected by all
               five consulted parties: it privileges frequency over importance and
               buries the question only one party can see.
  rotation     strict turn by proposing party, nothing merged. Proposed by the
               moderator to fix that; refuted before shipping -- it allocates
               without evaluating, and its promise that every proposal is
               eventually asked is false when arrivals exceed service.
  portfolio    one active proposal per party; a four-round cycle of two
               blinded-ranking picks, one lottery, one institutional slot.

`tools/benchmark_agenda.py` is measuring them. Until it reports and a custodian
adopts one, **the round loop must not hard-code a winner** -- wiring a loop around
an untested selector is how a third untested intuition gets shipped.

THE INTERFACE IS DELIBERATELY TOO NARROW TO CHEAT WITH.

    selector(queue, parties, round_index, seed) -> Proposal | None

A selector sees the queue, the party list, which round this is, and a seed. It
CANNOT reach the corpus, call a model, read the prompt template, or ask the
moderator anything. It returns one proposal or None.

That narrowness is the point. Every party consulted named the moderator's residual
powers -- solicitation wording, sameness judgement, gate, synthesis -- as the real
bias channel. A selector that could read anything else would become another one.
In particular **no selector here judges that two differently-worded proposals are
the same**; sponsorship is exact-text only, which is the objection Grok, GPT and
Qwen each raised in their own words.

Returning None means "nothing to ask". That is a legitimate outcome and the loop
treats it as one: silence is an output this record has never been able to express.

Deterministic: same queue, same round index, same seed -> same choice, always.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class Proposal:
    """One agenda proposal, as a party wrote it."""

    __slots__ = ("pid", "party", "question", "reason", "sponsors", "age", "asked", "raw")

    def __init__(self, pid, party, question, reason="", sponsors=None, raw=None):
        self.pid, self.party = pid, party
        self.question, self.reason = question, reason
        self.sponsors = set(sponsors or {party})
        self.age, self.asked, self.raw = 0, False, raw or {}

    @property
    def key(self) -> str:
        """Normalised question text. Equality is EXACT after whitespace collapse.

        Never fuzzy. The moderator judging that two proposals 'are the same' is the
        power the parties objected to, so it is not available to any selector.
        """
        return " ".join(self.question.split()).lower()

    def to_json(self) -> dict:
        return {"id": self.pid, "party": self.party, "question": self.question,
                "reason": self.reason, "sponsors": sorted(self.sponsors),
                "age_rounds": self.age, "asked": self.asked}

    def __repr__(self):
        return f"<{self.pid} {self.party} sponsors={len(self.sponsors)}>"


def load_queue(round_dir: Path | None = None) -> list[Proposal]:
    """Build the queue from solicited proposals, deduplicating by exact question text."""
    root = round_dir or (REPO_ROOT / "corpus" / "raw" / "agenda-01")
    out: list[Proposal] = []
    index: dict[str, Proposal] = {}
    if not root.is_dir():
        return out
    for path in sorted(root.glob("*-samples.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        party = path.stem.split("-samples")[0].split("-")[-1]
        for row in (doc.get("samples") or doc.get("responses") or []):
            parsed = row.get("parsed")
            if parsed is None:
                try:
                    parsed = json.loads(row["content"])
                except Exception:                                   # noqa: BLE001
                    continue
            question = (parsed.get("question") or "").strip()
            if not question:
                continue
            probe = Proposal("", party, question)
            if probe.key in index:
                index[probe.key].sponsors.add(party)
                continue
            item = Proposal(f"P{len(out) + 1:03d}", party, question,
                            parsed.get("reason", ""), raw=parsed)
            index[item.key] = item
            out.append(item)
    return out


# --------------------------------------------------------------- selectors --

def select_convergence(queue, parties, round_index, seed):
    """Most sponsors wins. A singleton unasked for three rounds escalates.

    Kept implemented, not deleted, because a mechanism every party rejected is the
    baseline the others have to beat. Removing it would make the benchmark a
    comparison between two options the same author preferred.
    """
    live = [p for p in queue if not p.asked]
    if not live:
        return None
    stale = [p for p in live if len(p.sponsors) == 1 and p.age >= 3]
    if stale:
        return min(stale, key=lambda p: p.pid)
    return max(live, key=lambda p: (len(p.sponsors), [-ord(c) for c in p.pid]))


def select_rotation(queue, parties, round_index, seed):
    """Strict turn by proposing party. Nothing merged, nothing evaluated."""
    live = [p for p in queue if not p.asked]
    if not live:
        return None
    order = sorted(parties)
    for offset in range(len(order)):
        party = order[(round_index + offset) % len(order)]
        own = [p for p in live if p.party == party]
        if own:
            return min(own, key=lambda p: p.pid)
    return None


def select_portfolio(queue, parties, round_index, seed):
    """Two ranking picks, one lottery, one institutional slot, per four rounds.

    Slot 3 returns None ON PURPOSE. The institutional-challenge round asks about
    this forum, and its question comes from non-target nominations -- never from
    this queue, and never chosen by the moderator. The loop handles that slot
    separately or halts; a selector that invented one would be the moderator
    writing its own audit question, which SOP §5.1a forbids.
    """
    live = [p for p in queue if not p.asked]
    if not live:
        return None
    slot = round_index % 4
    if slot == 3:
        return None
    if slot in (0, 1):
        return max(live, key=lambda p: (len(p.sponsors), [-ord(c) for c in p.pid]))
    rng = random.Random(f"{seed}:{round_index}")
    tickets = []
    for party in sorted(parties):                     # one ticket per party
        own = sorted((p for p in live if p.party == party), key=lambda p: p.pid)
        if own:
            tickets.append(rng.choice(own))
    return rng.choice(tickets) if tickets else None


SELECTORS = {
    "convergence": select_convergence,
    "rotation": select_rotation,
    "portfolio": select_portfolio,
}

#  Deliberately not a default. `round_cycle.py` requires --selector to be named
#  explicitly, so no mechanism becomes the winner by being the one nobody changed.
ADOPTED: str | None = None
