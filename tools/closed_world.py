#!/usr/bin/env python3
"""A count you cannot read unless every in-scope artifact was accounted for — control 5.

    from closed_world import Survey

    survey = Survey("tools with a negative control", scope="tools/*.py")
    for path in paths:
        survey.seen(path.name)
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError as exc:
            survey.unreadable(path.name, f"{type(exc).__name__}: {exc}")
            continue
        survey.accounted(path.name)          # EXACTLY ONE terminal state per member
        survey.count("covered" if covered(tree) else "uncovered")

    survey.result()   # the numbers, or REFUSES if anything was not accounted for
    survey.report()   # always safe: says what was seen and what was not

WHY A TYPE AND NOT A CONVENTION
--------------------------------
Control 5 says a measurement over a population MUST parse every in-scope artifact under a
registered schema, **or refuse to emit any result at all**. This repository already enforces that
inside `tools/derive_counts.py`, and that is exactly the problem: the discipline lives in one
function, for one population, and every other tool that walks a directory and prints a number
reimplements the walk without it.

That is not hypothetical. On 2026-08-10 this layer published *"0 `search_web` invocations across
all 20 rounds"* and recommended deleting its own tool on the strength of it. The corpus holds
**9**. The scan iterated each file's `samples` array; 69 raw files have no `samples` key — they
use `responses` and `failures` — so it returned zero for their entire contents, and **a scan that
cannot see a file reports absence, which looks exactly like a true zero**. `derive_counts.py` was
built to stop that, and the error had happened in a script that never called it.

So the discipline is a TYPE. `result()` raises when anything went unaccounted for; there is no
way to reach the numbers past it, and no default that quietly means "none". A caller that wants
to publish anyway must call `report()`, which states the coverage rather than the count.

WHAT IT DOES NOT DO
--------------------
* It does not know what "in scope" means. The caller decides which paths to walk, and a
  population defined too narrowly is a defect this cannot see — the 2026-08-10 error was partly
  that shape, and no type catches it.
* It does not validate a schema. `unregistered()` is how a caller reports an artifact whose type
  it does not recognise; recognising is the caller's job.
* It does not make the numbers correct. It makes them unavailable when the walk was incomplete,
  which is a smaller and more checkable claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class IncompleteSurvey(Exception):
    """The walk did not account for everything, so there is no number to report.

    Raised rather than returned. A caller that ignores a returned error object publishes the
    zero anyway, which is the failure this module exists for — and this repository has an
    action-log entry proving a returned status gets dropped.
    """


class SurveyMisuse(Exception):
    """The walk is not internally coherent, which is worse than incomplete.

    A disposition for a key never seen, a second disposition for the same key, or a count with
    no artifact behind it. The FIRST version of this type had none of these checks and Codex
    reproduced four passing surveys that were nonsense: 99 counted with zero artifacts seen; 99
    counted from one artifact; one seen and none counted; an exclusion whose stated ground was
    ten spaces. Every one returned a result. A type that accepts an incoherent walk is not a
    control, it is a shape.
    """


@dataclass
class Survey:
    """A population walk that refuses to yield counts unless every member reached an outcome.

    THE CONTRACT. Each artifact is declared with `seen(key)` and must then reach EXACTLY ONE
    terminal state — `accounted`, `excluded`, `unreadable` or `unregistered`. `result()` refuses
    if any member is still open, and `SurveyMisuse` is raised at once for a disposition of an
    unseen key or a second disposition of the same key.

    `count(bucket, n)` is separate from accounting on purpose: one artifact may legitimately
    contribute several events. But a bucket count with no accounted artifact behind it is
    refused, because that is precisely the "99 counted, nothing seen" shape.
    """

    name: str
    scope: str = ""
    expected: tuple[str, ...] | None = None
    _states: dict[str, str] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    unreadable_items: list[str] = field(default_factory=list)
    unregistered_items: list[str] = field(default_factory=list)
    excluded_items: list[str] = field(default_factory=list)

    #  ── declaring and disposing ─────────────────────────────────────────────────────────────

    def seen(self, key: str) -> None:
        """One in-scope artifact was reached. Call BEFORE trying to parse it."""
        if key in self._states:
            raise SurveyMisuse(f"{self.name}: {key!r} was declared twice. A population member "
                               f"counted twice is a denominator nobody can check.")
        self._states[key] = "open"

    def _dispose(self, key: str, state: str) -> None:
        if key not in self._states:
            raise SurveyMisuse(f"{self.name}: {key!r} was disposed as {state} without being "
                               f"declared with seen(). An outcome for an artifact the walk never "
                               f"reached is not an outcome.")
        if self._states[key] != "open":
            raise SurveyMisuse(f"{self.name}: {key!r} is already {self._states[key]} and cannot "
                               f"also be {state}. Exactly one terminal state per member.")
        self._states[key] = state

    def accounted(self, key: str) -> None:
        """Read, recognised and measured. The ordinary outcome."""
        self._dispose(key, "accounted")

    def unreadable(self, key: str, why: str) -> None:
        """It could not be parsed. This is what makes the survey unusable."""
        self._dispose(key, "unreadable")
        self.unreadable_items.append(f"{key}: {why}")

    def unregistered(self, key: str, why: str) -> None:
        """It parsed and its shape is not one this measurement knows. Also unusable.

        SEPARATE FROM `unreadable` on purpose. "I could not read it" and "I read it and do not
        know what it is" have different repairs — one is a corrupt file, the other a gap in the
        registry — and collapsing them sends the reader to the wrong place.
        """
        self._dispose(key, "unregistered")
        self.unregistered_items.append(f"{key}: {why}")

    def excluded(self, key: str, decision: str) -> None:
        """Out of scope BY A RECORDED DECISION, which is not the same as not being seen.

        `decision` is required and must name a ground. An exclusion with no stated reason is
        indistinguishable from an omission, which is control 44's shape appearing inside a
        control 5 mechanism. Whitespace does not count as a ground — the first version measured
        `len(decision)` and accepted ten spaces.
        """
        ground = (decision or "").strip()
        if len(ground) < 10 or ground.lower().rstrip(".") in {
                "n/a", "na", "none", "skip", "skipped", "not applicable", "excluded"}:
            raise SurveyMisuse(f"excluding {key!r} needs a stated ground, not {decision!r}")
        self._dispose(key, "excluded")
        self.excluded_items.append(f"{key}: {ground}")

    def count(self, bucket: str, n: int = 1) -> None:
        if n < 0:
            raise SurveyMisuse(f"{self.name}: a negative count ({n}) for {bucket!r}")
        self.counts[bucket] = self.counts.get(bucket, 0) + n

    #  ── the verdict ─────────────────────────────────────────────────────────────────────────

    @property
    def open_members(self) -> list[str]:
        return sorted(k for k, s in self._states.items() if s == "open")

    @property
    def missing_members(self) -> list[str]:
        """Declared up front and never reached at all. Only meaningful when `expected` is set."""
        return sorted(set(self.expected or ()) - set(self._states))

    @property
    def visited(self) -> int:
        return len(self._states)

    @property
    def usable(self) -> bool:
        return not (self.unreadable_items or self.unregistered_items
                    or self.open_members or self.missing_members
                    or (self.counts and not self._accounted_count))

    @property
    def _accounted_count(self) -> int:
        return sum(1 for s in self._states.values() if s == "accounted")

    def _refusals(self) -> list[str]:
        out = []
        if self.unreadable_items:
            out.append(f"{len(self.unreadable_items)} unreadable")
        if self.unregistered_items:
            out.append(f"{len(self.unregistered_items)} unregistered")
        if self.open_members:
            out.append(f"{len(self.open_members)} declared and never disposed "
                       f"({', '.join(self.open_members[:3])})")
        if self.missing_members:
            out.append(f"{len(self.missing_members)} expected and never reached "
                       f"({', '.join(self.missing_members[:3])})")
        if self.counts and not self._accounted_count:
            out.append(f"{sum(self.counts.values())} counted with no artifact accounted for")
        return out

    def result(self) -> dict:
        """The numbers — or REFUSE, naming everything that went unaccounted for."""
        if not self.usable:
            raise IncompleteSurvey(
                f"{self.name}: " + "; ".join(self._refusals())
                + f" — of {self.visited} in scope"
                + (f" ({self.scope})" if self.scope else "")
                + ". NO COUNT IS REPORTED: a scan that cannot account for an artifact reports "
                  "absence, and absence looks exactly like a true zero.\n  "
                + "\n  ".join(self.unreadable_items[:5] + self.unregistered_items[:5]))
        return {"name": self.name, "scope": self.scope, "visited": self.visited,
                "accounted": self._accounted_count, "counts": dict(self.counts),
                "excluded": list(self.excluded_items)}

    def report(self) -> str:
        """Always safe to call, including when the survey refuses. Coverage, not counts."""
        lines = [f"  {self.name}: {self.visited} artifact(s) in scope"
                 + (f" ({self.scope})" if self.scope else "")]
        if self.excluded_items:
            lines.append(f"    {len(self.excluded_items)} excluded by a recorded decision")
        if self.usable:
            for bucket, n in sorted(self.counts.items(), key=lambda kv: -kv[1]):
                lines.append(f"    {n:6d}  {bucket}")
        else:
            lines.append("    NO COUNT — the walk did not account for everything:")
            for reason in self._refusals():
                lines.append(f"      {reason}")
            for item in self.unreadable_items[:5]:
                lines.append(f"      unreadable   {item}")
            for item in self.unregistered_items[:5]:
                lines.append(f"      unregistered {item}")
        return "\n".join(lines)
