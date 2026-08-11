#!/usr/bin/env python3
"""Reference verifier for the Fault-Injection Check Profile (FICP) v0.2.

    python3 tools/verify_fault_injection.py attestation.json
    python3 tools/verify_fault_injection.py --fixtures     # run the must-reject fixtures

Accepts NCP v0.1 documents forever, with a deprecation warning, normalising them internally.
Refuses any document mixing both vocabularies -- a hybrid is an authoring error, and silently
reinterpreting one as the other is how a rename becomes a data-corruption event.

**DETERMINISTIC.** No LLM, no network. Reads a file, applies `spec/ncp/ncp-v0.1.md`, exits
non-zero on any violation.

The one requirement
-------------------
Every check that produces an assurance signal must ship with a negative control — a condition
under which the check is REQUIRED to fail — and the attestation must record that the control was
run and that the check did fail. A check never observed to fail is not evidence that anything
works.

Why this verifier ships with fixtures it must reject
-----------------------------------------------------
Because it is subject to its own requirement. A verifier that has only ever been run against
valid attestations has never been observed to fail, which is the exact condition NCP exists to
forbid. `--fixtures` is this tool's negative control: eight attestations that are wrong in eight
different ways, each of which the verifier must reject for the stated reason. **A verifier that
accepts any of them is non-conforming**, and that includes this one.

What a pass does not establish
-------------------------------
* That the negative controls are the right ones. A check can fail under a trivial perturbation
  and stay blind to the failure that will actually happen. This raises the floor from "never
  observed to fail" to "observed to fail once".
* That the check set covers the capability. N5 constrains each control's relevance; nothing here
  constrains coverage.
* Anything about the system. Every claim is about the checks.
* That the attestation is honest. It makes one lie harder to tell by accident.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "spec" / "ficp" / "fixtures"
LEGACY_FIXTURES = REPO_ROOT / "spec" / "ncp" / "fixtures"

#  v0.1 -> v0.2. The old names are NOT accepted as aliases in new documents: `negative_control`
#  reversed established laboratory terminology and stays misleading to the readers who matter.
RENAMED = {"ncp_version": "ficp_version", "positive_run": "baseline_run",
           "negative_control": "fault_injection"}

#  Transport-level perturbations. N5: cutting the network makes every check fail and demonstrates
#  nothing about any of them, so a control described only in these terms is refused.
TRANSPORT_ONLY = ("unplug", "network down", "cut the network", "firewall", "kill the process",
                  "stop the container", "shut down the host", "block the port", "power off")


class Violation(Exception):
    pass


def normalise(doc: dict) -> tuple[dict, list[str]]:
    """Return the document in v0.2 vocabulary, plus any notes about what was translated.

    A v0.1 document is accepted forever -- it was published, people were asked to build against
    it, and breaking it to tidy our own naming error would put the cost of the mistake on them.
    A HYBRID is refused: a document carrying both vocabularies is an authoring error, and
    guessing which one the author meant is how a rename turns into silent data corruption.
    """
    notes: list[str] = []
    old_keys, new_keys = set(RENAMED), set(RENAMED.values())

    def seen(node, keys) -> bool:
        if isinstance(node, dict):
            return any(k in keys for k in node) or any(seen(v, keys) for v in node.values())
        if isinstance(node, list):
            return any(seen(v, keys) for v in node)
        return False

    has_old, has_new = seen(doc, old_keys), seen(doc, new_keys)
    if has_old and has_new:
        return doc, ["MIXED VOCABULARY: this document uses both v0.1 and v0.2 field names. "
                     "Pick one. Guessing which was meant is how a rename corrupts a record."]
    if not has_old:
        return doc, notes

    def convert(node):
        if isinstance(node, dict):
            return {RENAMED.get(k, k): convert(v) for k, v in node.items()}
        if isinstance(node, list):
            return [convert(v) for v in node]
        return node

    converted = convert(doc)
    if str(converted.get("ficp_version")) == "0.1":
        converted["ficp_version"] = "0.2"
    notes.append("DEPRECATED VOCABULARY: this is an NCP v0.1 document. It is still valid and "
                 "always will be, but the profile was renamed on 2026-08-11 because "
                 "'negative control' reversed established laboratory terminology. New "
                 "attestations should use FICP v0.2. See spec/ficp/MIGRATION.md.")
    return converted, notes


def problems_for(doc: dict) -> list[str]:
    """Every FICP violation in this attestation. Empty means conforming.

    NORMALISES FIRST. A caller handing this a v0.1 document used to get a clean-looking answer
    computed against field names the document does not use -- a function returning "no problems"
    about input it did not understand, which is this record's dominant failure with a different
    surface. Normalisation is idempotent for v0.2, so calling it here costs nothing.
    """
    doc, notes = normalise(doc)
    if any(n.startswith("MIXED") for n in notes):
        return notes
    out = []
    if str(doc.get("ficp_version")) != "0.2":
        out.append(f"ficp_version {doc.get('ficp_version')!r} is not '0.2'")
    checks = doc.get("checks")
    if not isinstance(checks, list) or not checks:
        out.append("no checks: an attestation certifying nothing conforms to nothing")
        return out

    seen_ids = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            out.append(f"check {index}: not an object")
            continue
        cid = check.get("check_id") or f"<check {index}>"
        if cid in seen_ids:
            out.append(f"{cid}: duplicate check_id; identity must be stable and unique")
        seen_ids.add(cid)
        if not check.get("certifies"):
            out.append(f"{cid}: does not say what it certifies, so no control can be judged "
                       f"relevant to it")

        #  N1 — a declared negative control at all.
        control = check.get("fault_injection")
        if not isinstance(control, dict):
            out.append(f"{cid}: N1 — no fault_injection. A check that has never been observed "
                       f"to fail is not evidence that anything works.")
            continue
        if not control.get("condition"):
            out.append(f"{cid}: N1 — fault_injection names no condition")
        if not control.get("how_produced"):
            out.append(f"{cid}: N1 — fault_injection does not say how the condition is produced, "
                       f"so it cannot be reproduced or challenged")

        #  N2 — executed, not described.
        run = control.get("run")
        if not isinstance(run, dict) or not run.get("utc"):
            out.append(f"{cid}: N2 — the fault was described but never injected. A declared "
                       f"control that was never executed is a plan, not evidence.")
            continue

        #  N3 — and the check failed under it.
        outcome = str(run.get("outcome", "")).upper()
        if outcome != "FAIL":
            out.append(f"{cid}: N3 — MISSED FAULT: the check returned {outcome or 'nothing'} while "
                       f"its declared fault was present. That is a defect in the check, not a "
                       f"passing attestation.")

        #  N4 — same identity across both runs.
        baseline = check.get("baseline_run")
        if not isinstance(baseline, dict) or not baseline.get("utc"):
            out.append(f"{cid}: N4 — no baseline run recorded")
        artifact = check.get("artifact")
        if not isinstance(artifact, dict) or not artifact.get("sha256"):
            out.append(f"{cid}: N4 — no artifact hash; a control run against a different build "
                       f"proves nothing about the check that shipped")
        else:
            for label, side in (("baseline", baseline), ("fault-injected", run)):
                if isinstance(side, dict) and side.get("artifact_sha256") not in (
                        None, artifact.get("sha256")):
                    out.append(f"{cid}: N4 — the {label} run names artifact "
                               f"{side['artifact_sha256'][:12]}… but the check declares "
                               f"{artifact['sha256'][:12]}…")

        #  N3b — it must have failed for the RIGHT REASON. A check that fails because the
        #  harness could not reach it has still never been observed to fail for the reason it
        #  exists, and N3 alone is satisfied on its face.
        because = str(run.get("failed_because", "")).lower()
        if outcome == "FAIL" and because and any(t in because for t in TRANSPORT_ONLY + (
                "connection refused", "unreachable", "timed out", "could not reach")):
            out.append(f"{cid}: N3 — it failed under the control, but for a TRANSPORT reason "
                       f"({because[:60]}…), not for the capability the control perturbed")

        #  N4b — the control must have run against the artifact that SHIPPED. Matching hashes do
        #  not establish that, if the run predates the artifact's last change.
        changed = artifact.get("changed_utc") if isinstance(artifact, dict) else None
        if changed and run.get("utc") and str(run["utc"]) < str(changed):
            out.append(f"{cid}: N4 — the fault-injected run was at {run['utc']}, BEFORE the "
                       f"artifact last changed at {changed}. It exercised a predecessor of the "
                       f"check that shipped.")

        #  N4c — a referent that is gone cannot be re-verified. A thin pointer to a vanished
        #  artifact looks identical to a sound attestation until someone tries to check it.
        if isinstance(artifact, dict) and artifact.get("present") is False:
            out.append(f"{cid}: N4 — the attestation points at an artifact recorded as no longer "
                       f"present; nothing here can be re-verified")

        #  N5 — perturb the capability, not the transport.
        blob = " ".join(str(control.get(k, "")) for k in ("condition", "how_produced")).lower()
        if any(phrase in blob for phrase in TRANSPORT_ONLY):
            out.append(f"{cid}: N5 — the fault perturbs the transport ({blob[:60]}…). Cutting "
                       f"the network makes every check fail and demonstrates nothing about any "
                       f"of them; it must target the declared capability.")

    #  N6 — disclosure of what did not run.
    disclosure = doc.get("undisclosed_nothing")
    if not isinstance(disclosure, dict) or not all(
            isinstance(disclosure.get(k), list) for k in ("skipped", "suppressed", "unsupported")):
        out.append("N6 — skipped, suppressed and unsupported checks are not disclosed. An "
                   "absent disclosure is indistinguishable from a concealed one.")

    #  N7 — bounded claim.
    claim = str(doc.get("claim", ""))
    #  N7b — CLAIM SMUGGLING. A claim can open with the exact conforming sentence and then append
    #  a conclusion about the system, using none of the forbidden words. N7 bounds what may be
    #  claimed, not which words appear.
    for smuggled in ("the service is", "the system is", "demonstrate that the", "in production",
                     "is reliable", "works correctly", "is secure"):
        if smuggled in claim.lower():
            out.append(f"N7 — the claim contains {smuggled!r}, which asserts something about the "
                       f"SUBJECT. A conforming claim is about the CHECKS and stops there.")
            break
    for forbidden in ("FICP certified", "NCP certified", "we follow OAGF", "certified safe", "aligned"):
        if forbidden.lower() in claim.lower():
            out.append(f"N7 — the claim contains {forbidden!r}. A conforming claim is about the "
                       f"CHECKS and says so.")
    return out


def verify(path: Path) -> tuple[int, list[str]]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:                                          # noqa: BLE001
        return 2, [f"unreadable: {type(error).__name__}: {error}"]
    if not isinstance(doc, dict):
        return 2, ["top level is not an object"]
    _normalised, notes = normalise(doc)
    for note in notes:
        print(f"  \033[33m!\033[0m {note}", file=sys.stderr)
    problems = problems_for(doc)
    return (1 if problems else 0), problems


GAPS = FIXTURES / "known-gaps"


def report_gaps() -> int:
    """Attestations this verifier CANNOT reject, published as its own blind spots.

    A verifier that ships only fixtures it passes is advertising. These are cases the profile
    genuinely fails to catch -- a control aimed at a different capability than the check
    certifies, and a control so easy the check fails it trivially. Both satisfy every mechanical
    requirement. Both establish almost nothing.

    They do NOT fail the suite. Pretending a known gap is a failure would make the suite red
    forever and teach everyone to ignore it; pretending it is absent would be worse.
    """
    if not GAPS.is_dir():
        return 0
    print("\n  KNOWN GAPS — attestations this verifier accepts and should not:")
    for path in sorted(GAPS.glob("*.json")):
        code, _ = verify(path)
        doc = json.loads(path.read_text(encoding="utf-8"))
        state = "accepted (as expected — this is the gap)" if code == 0 else \
                "now REJECTED — the gap has closed; move this fixture into fixtures/"
        print(f"    {path.name}\n      {state}")
        print(f"      {doc.get('_should_be_rejected_but_is_not', '')[:150]}…")
    return 0


def run_fixtures() -> int:
    """This verifier's own negative control. Every fixture MUST be rejected."""
    if not FIXTURES.is_dir():
        print(f"  no fixtures at {FIXTURES.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 2
    failures = 0
    for path in sorted(FIXTURES.glob("reject-*.json")):
        code, problems = verify(path)
        expected = json.loads(path.read_text(encoding="utf-8")).get("_must_be_rejected_because", "")
        if code == 0:
            print(f"  \033[31mACCEPTED\033[0m {path.name} — it must be rejected: {expected}")
            failures += 1
        else:
            print(f"  \033[32mrejected\033[0m {path.name}  ({problems[0][:78]})")
    for path in sorted(FIXTURES.glob("accept-*.json")):
        code, problems = verify(path)
        if code != 0:
            print(f"  \033[31mREJECTED\033[0m {path.name} — it must be accepted: {problems}")
            failures += 1
        else:
            print(f"  \033[32maccepted\033[0m {path.name}")
    print()
    if failures:
        print(f"  {failures} fixture(s) behaved wrongly. THIS VERIFIER IS NON-CONFORMING.",
              file=sys.stderr)
        return 1
    report_gaps()
    print("\n  every must-reject fixture was rejected and every must-accept fixture accepted.")
    print("  That is this tool's own negative control. It does not establish that the")
    print("  requirement is the right requirement.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("attestation", nargs="?", help="path to an NCP attestation")
    parser.add_argument("--fixtures", action="store_true",
                        help="run the fixtures this verifier must reject")
    args = parser.parse_args()

    if args.fixtures:
        return run_fixtures()
    if not args.attestation:
        parser.error("give an attestation path, or --fixtures")
    code, problems = verify(Path(args.attestation))
    if problems:
        for problem in problems:
            print(f"  \033[31m✗\033[0m {problem}", file=sys.stderr)
        print(f"\nNON-CONFORMING — {len(problems)} violation(s) of NCP v0.1.", file=sys.stderr)
        return code
    print("  conforming to NCP v0.1.")
    print("  This says every check was observed to FAIL under its declared negative control.")
    print("  It says nothing about whether the controls are the right ones, whether the check")
    print("  set covers the capability, or whether the system is safe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
