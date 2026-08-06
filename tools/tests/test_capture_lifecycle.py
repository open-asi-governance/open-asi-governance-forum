#!/usr/bin/env python3
"""Validate the capture lifecycle state machine. Stdlib only.

    python3 tools/tests/test_capture_lifecycle.py

Runs against a temporary repo root so it never writes into the real record.
The invariants asserted here are the ones the design rests on, so a regression
in any of them silently reintroduces a failure this project has already had.
"""

from __future__ import annotations

import pathlib
import json
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import capture_lifecycle as L                                   # noqa: E402

PASSED, FAILED = [], []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASSED if condition else FAILED).append(f"{name}{(' — ' + detail) if detail else ''}")


def raises(fn, *a, **k) -> str | None:
    try:
        fn(*a, **k)
    except Exception as e:                                       # noqa: BLE001
        return str(e)
    return None


tmp = pathlib.Path(tempfile.mkdtemp(prefix="oagf-lifecycle-"))
L.REPO_ROOT = tmp
R, P = "test-round-01", "Claude Fable 5"
SLUG = "claude-fable-5"

# ----------------------------------------------------------- the happy path --
L.transition(R, P, "planned", "custodian")
check("first event must be planned", L.current_state(R, P) == "planned")

L.transition(R, P, "sent_attested", "Stephen Reed (human custodian)",
             prompt_path="record/x-prompt.md", prompt_sha256="a" * 64, delivery="direct_fetch")
check("send is attested", L.current_state(R, P) == "sent_attested")

ev = L.receive(R, P, SLUG, "A genuine review with real content.", "custodian", [], "returned_clean")
check("receive preserves bytes before anything else",
      (tmp / ev["preserved_at"]).read_text() == "A genuine review with real content.")
check("receive records the digest", ev["response_sha256"] == L.sha256_of_text("A genuine review with real content."))

L.transition(R, P, "accepted", "custodian", reason="Answers the round question; gates clean.")
check("accepted is terminal", L.TRANSITIONS["accepted"] == set())

# ------------------------------------------------------- illegal transitions --
err = raises(L.transition, R, P, "sent_attested", "custodian")
check("cannot leave a terminal state", err is not None, err or "")

R2 = "test-round-02"
err = raises(L.transition, R2, "Grok", "accepted", "custodian", reason="x")
check("cannot start anywhere but planned", err is not None and "planned" in (err or ""))

L.transition(R2, "Grok", "planned", "custodian")
err = raises(L.transition, R2, "Grok", "accepted", "custodian", reason="x")
check("cannot skip from planned straight to accepted", err is not None)

# --------------------------------------------------- disposition is mandatory --
L.transition(R2, "Grok", "sent_attested", "custodian")
L.receive(R2, "Grok", "grok", "x" * 400, "custodian", [], "returned_pending_review")
err = raises(L.transition, R2, "Grok", "rejected", "custodian")
check("a disposition without a reason is refused", err is not None and "reason" in (err or ""))

# ------------------------------------------------------ bytes are immutable --
err = raises(L.receive, R2, "Grok", "grok", "different bytes", "custodian", [], "returned_clean")
check("receive refuses to overwrite preserved bytes", err is not None and "immutable" in (err or ""))

# ------------------------------------- pending blocks the round from complete --
st = L.round_status(R2, ["Grok", "Gemini"])
check("a pending capture blocks round completion", st["complete"] is False)
check("pending is named in the blocker list", "Grok" in st["awaiting_disposition"])
check("a party with no events shows as outstanding", "Gemini" in st["outstanding"])

L.transition(R2, "Grok", "rejected", "custodian", reason="Prompt critique, not a review.")
check("a REJECTED capture keeps its bytes",
      (tmp / "record/quarantine/test-round-02/grok-01.md").exists())
st = L.round_status(R2, ["Grok"])
check("round completes once every party is terminal", st["complete"] is True)
check("rejection is recorded, not erased", st["rejected"] == ["Grok"])

# --------------------------------------------------------- log replay checks --
check("a clean log validates", L.validate_log(R2) == [])
check("a declared party with no events is reported",
      any("no lifecycle events" in e for e in L.validate_log(R2, ["Grok", "Ghost"])))

tampered = tmp / "record/quarantine/test-round-02/grok-01.md"
tampered.write_text("edited after the fact")
errs = L.validate_log(R2)
check("editing a preserved response is detected",
      any("no longer matches its recorded hash" in e for e in errs), "; ".join(errs))

# ------------------------------------------------------------- append-only --
path = L.log_path(R2)
before = path.read_text().splitlines()
L.transition("test-round-03", "X", "planned", "custodian")
check("appending to one round does not touch another", path.read_text().splitlines() == before)
check("every event carries a unique id",
      len({e["event_id"] for e in L.read_events(R2)}) == len(L.read_events(R2)))


# ------------------------------------- Defect 7: conflicting receipts (D-37) --
# A differing capture for a party whose slot is already taken used to be DISCARDED:
# exit 0, "nothing to do", bytes not preserved. A custodian re-capturing to correct
# a mispaste got silence while the wrong text stood in the corpus under a real
# party's name. Every case here failed before the fix.
R4 = "test-round-04"
L.transition(R4, "Grok", "planned", "custodian")
L.transition(R4, "Grok", "sent_attested", "custodian")
L.receive(R4, "Grok", "grok", "ORIGINAL response text.", "custodian", [], "returned_clean")
L.transition(R4, "Grok", "accepted", "custodian", reason="looks right")

check("the terminal disposition carries no response hash",
      L.current_state(R4, "Grok") == "accepted"
      and not [e for e in L.read_events(R4)
               if e.get("state") == "accepted" and e.get("response_sha256")])
check("latest_response_event finds the hash anyway",
      (L.latest_response_event(R4, "Grok") or {}).get("response_sha256")
      == L.sha256_of_text("ORIGINAL response text."))

st = L.round_status(R4, ["Grok"])
check("round is complete before any conflict", st["complete"] is True)

conflict = L.record_conflict(R4, "Grok", "custodian", "CORRECTED response text.",
                             L.sha256_of_text("ORIGINAL response text."))
preserved = tmp / conflict["preserved_at"]
check("conflicting bytes are preserved", preserved.read_text() == "CORRECTED response text.")
check("preserved under record/quarantine, not corpus/",
      conflict["preserved_at"].startswith("record/quarantine/"))
check("named by content hash, not a sample index",
      "-conflict-" in preserved.name and "-02." not in preserved.name)

st = L.round_status(R4, ["Grok"])
check("an unresolved conflict blocks COMPLETE", st["complete"] is False)
check("the disputed party is named", st["disputed"] == ["Grok"])
check("the party keeps its disposition", st["states"]["Grok"] == "accepted")

again = L.record_conflict(R4, "Grok", "custodian", "CORRECTED response text.",
                          L.sha256_of_text("ORIGINAL response text."))
check("re-preserving identical bytes is idempotent",
      again["preserved_at"] == conflict["preserved_at"])
check("still one unresolved conflict", len(L.unresolved_conflicts(R4)) == 1)

check("conflict_status reports unresolved",
      L.conflict_status(R4, "Grok", conflict["conflicting_sha256"]) == "unresolved")
check("conflict_status is keyed by bytes, not party",
      L.conflict_status(R4, "Grok", "0" * 64) == "none")

# Resolution, appended the way resolve_conflict.py appends it.
with L.log_path(R4).open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({
        "event": "conflict_resolved", "round": R4, "identity": "Grok",
        "actor": "custodian", "decision": "confirm_recorded", "reason": "wrong window",
        "recorded_sha256": conflict["recorded_sha256"],
        "conflicting_sha256": conflict["conflicting_sha256"],
        "preserved_at": conflict["preserved_at"],
    }, sort_keys=True) + "\n")

check("resolution clears the block", L.round_status(R4, ["Grok"])["complete"] is True)
check("conflict_status reports the decision",
      L.conflict_status(R4, "Grok", conflict["conflicting_sha256"]) == "resolved:confirm_recorded")
check("resolved bytes are KEPT, never deleted", preserved.exists())

shutil.rmtree(tmp, ignore_errors=True)

print(f"lifecycle {L.LIFECYCLE_VERSION}")
print(f"{len(PASSED)} passed, {len(FAILED)} failed")
for f in FAILED:
    print(f"  FAIL  {f}")
sys.exit(1 if FAILED else 0)
