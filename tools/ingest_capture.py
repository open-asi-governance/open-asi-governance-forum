#!/usr/bin/env python3
"""Ingest capture bundles produced by the capture page. Deterministic; no network.

    python3 tools/ingest_capture.py ~/Downloads/oagf-capture-*.json

For each bundle, in order:

  1. resolve the round declaration and REFUSE if the bundle disagrees with it
  2. preserve the response bytes under record/quarantine/  -- before anything else
  3. run the authoritative gates
  4. promote to corpus/ through tools/capture_response.py, or hold for review

THE BUNDLE IS UNTRUSTED
-----------------------
It is a JSON file that sat on a disk and can be edited with any text editor. Its
`response_sha256_at_paste` proves the bundle is self-consistent, not what existed
at paste time -- both fields are in the same editable file, and changing both makes
any recomputation pass.

So round, party, provider, prompt path and prompt hash are taken from the **frozen
round declaration in this repository**, never from the bundle. The bundle
contributes two things: the response text and the custodian's form entries. Where
the two disagree the bundle loses and the ingest refuses, because a bundle claiming
a prompt hash the repository does not have is either stale or edited and neither
should enter the record quietly.

ORDER OF OPERATIONS IS THE SAFETY PROPERTY
------------------------------------------
Bytes are preserved before any validation runs. capture_response.py has seventeen
refusal sites; today they are harmless because it reads a file the custodian
already holds, but a bundle's `response_text` may be the only copy of what a
frontier model said. Validation gates PROMOTION into the corpus. It never gates
PRESERVATION. GOVERNANCE.md section 3: no unilateral control over what evidence is
preserved, and original outputs must remain available.

RE-RUNNING IS SAFE
------------------
A bundle already ingested reports its existing state and changes nothing. A round
of four is ingested one bundle at a time; a failure on one leaves the other three
captured, rather than leaving a partial round that immutability makes awkward to
retry.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import capture_lifecycle as lifecycle                            # noqa: E402
from capture_gates import (                                      # noqa: E402
    GATES_VERSION, lifecycle_state, run_gates, sent_prompt_text,
)

REQUIRED = (
    "bundle_version", "round", "identity", "response_text",
    "prompt_path", "prompt_sha256", "attested_answers_round_question", "attested_by",
)


class Refused(Exception):
    """A bundle that must not be ingested. Raised before anything is written."""


def slug(text: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def load_round(round_id: str) -> dict:
    path = REPO_ROOT / "record" / "rounds" / f"{round_id}.json"
    if not path.exists():
        raise Refused(
            f"no round declaration at {path.relative_to(REPO_ROOT)}. A capture is only "
            f"ingested into a round that was declared before it was sent."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def reconcile(bundle: dict, declaration: dict) -> dict:
    """Return the AUTHORITATIVE party record from the declaration, refusing on disagreement."""
    identity = bundle["identity"]
    party = next((p for p in declaration["parties"] if p["identity"] == identity), None)
    if party is None:
        declared = ", ".join(sorted(p["identity"] for p in declaration["parties"]))
        raise Refused(
            f"{identity!r} is not a declared party of {declaration['round']!r}. Declared: {declared}. "
            f"Identities are selected from the declaration, never typed -- D-09."
        )

    prompt_rel = party.get("prompt_override") or declaration["common_prompt"]
    if bundle.get("prompt_path") != prompt_rel:
        raise Refused(
            f"bundle cites prompt {bundle.get('prompt_path')!r} but the declaration says "
            f"{prompt_rel!r} for {identity!r}. The bundle is stale or edited; rebuild the page."
        )

    prompt_path = REPO_ROOT / prompt_rel
    if not prompt_path.exists():
        raise Refused(f"declared prompt not found: {prompt_rel}")
    actual = lifecycle.sha256_of_text(prompt_path.read_text(encoding="utf-8"))
    if bundle.get("prompt_sha256") != actual:
        raise Refused(
            f"prompt hash mismatch for {identity!r}.\n"
            f"        bundle:     {bundle.get('prompt_sha256')}\n"
            f"        repository: {actual}\n"
            f"        The prompt changed after the page was built, or the bundle was edited. "
            f"Recording a capture against a prompt the party did not receive is D-05 in reverse."
        )

    if party.get("bundle"):
        bundle_path = REPO_ROOT / party["bundle"]
        if not bundle_path.exists():
            raise Refused(f"declared supplied-context bundle not found: {party['bundle']}")
        expected = lifecycle.sha256_of_text(bundle_path.read_text(encoding="utf-8"))
        if bundle.get("bundle_sha256") != expected:
            raise Refused(
                f"supplied-context bundle hash mismatch for {identity!r}. Regenerating a bundle "
                f"after a round used it silently invalidates what the capture record cites -- that "
                f"happened once already, to Gemini's round-01 citation."
            )
    return {**party, "prompt_rel": prompt_rel, "prompt_sha256": actual}


def prior_context_for(party: dict, bundle: dict) -> str:
    template = party.get("prior_context_template") or ""
    text = template.format(
        bundle_path=party.get("bundle") or "",
        bundle_sha256=bundle.get("bundle_sha256") or "",
    )
    delivery = party.get("delivery")
    if delivery == "bundle" and party.get("bundle"):
        text = f"{text} Supplied-context bundle {party['bundle']}, sha256 {bundle.get('bundle_sha256')}.".strip()
    if party.get("prompt_override"):
        text = (f"{text} PROMPT OVERRIDE: this party received {party['prompt_override']}, "
                f"not the common prompt. Per-party prompt divergence is recorded because it has "
                f"twice contaminated a comparison.").strip()
    return text or "Not recorded."


def promote(bundle: dict, party: dict, preserved: Path, dry_run: bool) -> bool:
    """Write into the corpus through capture_response.py -- the single writer."""
    argv = [
        sys.executable, str(REPO_ROOT / "tools/capture_response.py"),
        "--round", bundle["round"],
        "--response", str(preserved),
        "--prompt", party["prompt_rel"],
        "--identity", bundle["identity"],
        "--provider", party["provider"],
        "--captured-utc", bundle["captured_utc"],
        "--phase", "blind" if "Phase-1" in bundle.get("phase", "Phase-2") else "informed",
        "--captured-by", bundle["attested_by"],
        "--prior-context", prior_context_for(party, bundle),
        "--capture-method",
        ("Pasted from the provider surface into the local capture UI by the custodian, hashed at "
         "paste time, ingested from the resulting bundle. No intermediary transcription."),
        "--sampling-unknown", bundle.get("sampling_unknown_reason") or "Not exposed by the surface.",
        "--effort-unknown", bundle.get("effort_unknown_reason") or "Not exposed by the surface.",
        "--system-instructions-unknown",
        bundle.get("system_instructions_unknown_reason") or "Provider system prompt not disclosed.",
    ]
    if bundle.get("model_version"):
        argv += ["--model-version", bundle["model_version"]]
    else:
        argv += ["--version-unknown",
                 bundle.get("version_unknown_reason") or "Surface does not expose a version identifier."]
    if bundle.get("notes"):
        argv += ["--notes", bundle["notes"]]

    if dry_run:
        print("      would run: capture_response.py --round "
              f"{bundle['round']} --identity {bundle['identity']!r}")
        return True
    result = subprocess.run(argv, cwd=REPO_ROOT)
    return result.returncode == 0


def ingest_one(path: Path, dry_run: bool) -> str:
    print(f"\n\033[1m▸ {path.name}\033[0m")

    # THE READ IS CONTAINED; NOTHING ELSE IS. Only json.JSONDecodeError used to be
    # caught here, so a mistyped path -- the first thing a custodian gets wrong --
    # raised FileNotFoundError out of a list comprehension in main(), aborting the
    # batch. Bundles before it had ALREADY written; bundles after it were never
    # processed; and the summary and round-status table, which come after that line,
    # never printed. The operator was left with a traceback that named no party.
    # IsADirectoryError, PermissionError and UnicodeDecodeError escaped the same way.
    #
    # Containment stops HERE, deliberately. A failure while writing quarantine
    # bytes, appending the lifecycle event, or promoting into the corpus must still
    # crash: at that point repository invariants are uncertain, and continuing to
    # the next bundle would build on a state nobody has checked.
    #
    # `input_error`, not `refused`. A refusal is a governance judgement about a
    # bundle that was read and evaluated. Nothing was evaluated here, and recording
    # "refused" would put an assessment in the summary that never happened.
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        print(f"      INPUT ERROR: not UTF-8 text: {error}")
        return "input_error"
    except OSError as error:
        print(f"      INPUT ERROR: cannot read this path: {error}")
        return "input_error"

    try:
        bundle = json.loads(text)
    except json.JSONDecodeError as error:
        print(f"      REFUSED: not valid JSON: {error}")
        return "refused"

    missing = [f for f in REQUIRED if f not in bundle]
    if missing:
        print(f"      REFUSED: bundle is missing {', '.join(missing)}")
        return "refused"

    try:
        declaration = load_round(bundle["round"])
        party = reconcile(bundle, declaration)
    except Refused as error:
        print(f"      REFUSED: {error}")
        return "refused"

    if not bundle["attested_answers_round_question"]:
        print("      REFUSED: the custodian did not attest that this response answers the round's "
              "question. A negative attestation is a refusal to capture, not a recordable state.")
        return "refused"
    if not (bundle.get("attested_by") or "").strip():
        print("      REFUSED: no attesting party named.")
        return "refused"

    identity = bundle["identity"]
    existing = lifecycle.current_state(bundle["round"], identity)
    if existing in ("accepted", "rejected") or existing in lifecycle.NEEDS_DISPOSITION:
        # DEFECT 7. Both of these branches used to return "skipped" unconditionally,
        # so a DIFFERING capture for a party whose slot was taken vanished: exit 0,
        # "nothing to do", bytes not even preserved. A custodian who re-captures to
        # correct a mispaste gets silence, and the wrong text stands in corpus/raw/
        # attributed to a real party. That is D-10 -- text attributed to a party that
        # did not write it -- manufactured by the tooling.
        #
        # The hash compared is computed HERE from the bundle's own response_text.
        # NOT bundle["response_sha256_at_paste"], which the browser supplies and this
        # program does not trust; using it would let a bundle claim equality with the
        # recorded response and be skipped on its own say-so.
        incoming = lifecycle.sha256_of_text(bundle["response_text"])
        prior = lifecycle.latest_response_event(bundle["round"], identity)
        recorded = (prior or {}).get("response_sha256")

        if recorded is not None and incoming != recorded:
            # Re-running an ingest must be safe, including here. Without this, a
            # repeated command appended a duplicate conflicting_receipt each time,
            # and -- worse -- a repeat AFTER the custodian resolved the dispute
            # silently re-opened it. Both found by running the command three times.
            prior_status = lifecycle.conflict_status(bundle["round"], identity, incoming)
            if prior_status.startswith("resolved:"):
                decision = prior_status.split(":", 1)[1]
                print(f"      These bytes were already offered for {identity} and the custodian")
                print(f"      RESOLVED that dispute as {decision!r}. Not re-opening it, and not")
                print(f"      re-recording it. If this is a new dispute, it needs a new decision;")
                print(f"      say so explicitly rather than by re-running the ingest.")
                return "skipped"
            if prior_status == "unresolved":
                print(f"      Already recorded as a conflicting receipt for {identity}, still")
                print(f"      unresolved. Nothing further recorded; the bytes are preserved.")
                return "conflict"

            event = lifecycle.record_conflict(
                bundle["round"], identity, actor=bundle.get("attested_by") or "unknown",
                response_text=bundle["response_text"], recorded_sha256=recorded)
            print(f"      CONFLICTING RECEIPT. {identity} is already {existing}, and these are")
            print(f"      NOT the same bytes. Nothing was overwritten and nothing was discarded.")
            print(f"        recorded    {recorded[:16]}")
            print(f"        offered     {incoming[:16]}")
            print(f"      Preserved at {event['preserved_at']}")
            print(f"      {bundle['round']} is now INCOMPLETE until a custodian resolves this:")
            print(f"        python3 tools/resolve_conflict.py {bundle['round']} {identity!r} \\")
            print(f"          --{{confirm-recorded|supersede-with-conflicting}} --reason '...'")
            return "conflict"

        if recorded is None:
            # No receiving event carries a hash, so equality cannot be established.
            # Refusing beats skipping: "I cannot tell whether this is the same
            # material" must not print as "nothing to do".
            print(f"      REFUSED: {identity} is {existing}, but no recorded response hash was")
            print(f"      found in the lifecycle log, so this capture cannot be compared against")
            print(f"      what is already recorded. Resolve by hand rather than by re-ingesting.")
            return "refused"

        if existing in ("accepted", "rejected"):
            print(f"      already {existing}, and byte-identical. Re-running ingest is a no-op.")
        else:
            #  Without this, a re-run fell through to receive() and reported an immutability
            #  refusal -- correct, and a confusing way to say "you already ingested this."
            print(f"      already {existing}, awaiting the custodian's disposition, and")
            print(f"      byte-identical. The bytes are preserved. Disposition is accept or")
            print(f"      reject, with a reason; until then {bundle['round']} is not complete.")
        return "skipped"

    response = bundle["response_text"]
    prompt_text = sent_prompt_text((REPO_ROOT / party["prompt_rel"]).read_text(encoding="utf-8"))
    results = run_gates(response, prompt_text)
    state, reasons = lifecycle_state(results)

    if state == "refused_empty":
        print("      REFUSED: the response is empty. Nothing to preserve, and admitting it would "
              "block the round on a paste that did not happen.")
        return "refused"

    #  Every path from here preserves the bytes first.
    if existing is None:
        lifecycle.transition(bundle["round"], identity, "planned", "tools/ingest_capture.py")
    if lifecycle.current_state(bundle["round"], identity) == "planned":
        lifecycle.transition(
            bundle["round"], identity, "sent_attested", bundle["attested_by"],
            prompt_path=party["prompt_rel"], prompt_sha256=party["prompt_sha256"],
            delivery=party.get("delivery"),
            note="Send attested at ingest rather than at send time. This is the custodian's "
                 "contemporaneous-at-capture attestation, not independent delivery evidence.",
        )

    try:
        event = lifecycle.receive(
            bundle["round"], identity, slug(identity), response,
            bundle["attested_by"], [r.as_record() for r in results], state,
            gates_version=GATES_VERSION,
            response_sha256_at_paste=bundle.get("response_sha256_at_paste"),
            attested_answers_round_question=True,
            round_question=declaration["question"],
            # Recorded so a HELD capture can still be promoted later without anyone
            # having to guess. The event's ts_utc is when ingest ran, not when the
            # reply was pasted; a disposition tool that substituted one for the other
            # would write a value into the provenance record that looks like a
            # capture time and is not. Captures held before this stays required-by-flag.
            captured_utc=bundle.get("captured_utc"),
        )
    except ValueError as error:
        print(f"      REFUSED: {error}")
        return "refused"

    preserved = REPO_ROOT / event["preserved_at"]
    print(f"      preserved  {event['preserved_at']}  ({event['response_bytes']:,} bytes)")

    claimed = bundle.get("response_sha256_at_paste")
    if claimed and claimed != event["response_sha256"]:
        # The state must be RECORDED, not just printed. This block used to reassign
        # the local `state` variable AFTER receive() had already written the event,
        # so the log said `returned_clean` while the operator was told "Held for
        # review." The lifecycle -- which is what every later tool and the round's
        # completeness read -- disagreed with the message on screen, and the message
        # was the one nobody could act on. Found by external review of the D-37 work.
        print(f"      NOTE: paste-time hash {claimed[:12]} != ingested {event['response_sha256'][:12]}. "
              f"The bundle is internally inconsistent. Held for review.")
        reasons = reasons + ["bundle hash inconsistent"]
        if state != "returned_pending_review":
            state = "returned_pending_review"
            lifecycle.transition(
                bundle["round"], identity, state, bundle["attested_by"],
                reason="bundle hash inconsistent: response_sha256_at_paste does not match "
                       "the ingested bytes, so the bundle is internally inconsistent",
                response_sha256=event["response_sha256"],
                preserved_at=event["preserved_at"],
            )

    if state == "returned_pending_review":
        print("      HELD for custodian review — the bytes are preserved and the round is not complete:")
        for reason in reasons:
            print(f"        · {reason}")
        print("      Disposition is required. Nothing entered the corpus.")
        return "held"

    if promote(bundle, party, preserved, dry_run):
        if not dry_run:
            lifecycle.transition(
                bundle["round"], identity, "accepted", bundle["attested_by"],
                reason="Gates clean; custodian attested the response answers the round question.",
            )
        print("      ACCEPTED into the corpus.")
        return "accepted"

    print("      capture_response.py refused. The bytes remain preserved; state left open for retry.")
    return "held"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bundles", nargs="+", help="capture bundle JSON files")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would happen; still preserves bytes, never writes the corpus")
    args = parser.parse_args()

    outcomes = [ingest_one(Path(b).expanduser(), args.dry_run) for b in args.bundles]

    print("\n" + "─" * 60)
    for label in ("accepted", "held", "conflict", "refused", "input_error", "skipped"):
        n = outcomes.count(label)
        if n:
            print(f"  {label:9} {n}")

    rounds = set()
    for b in args.bundles:
        try:
            rounds.add(json.loads(Path(b).expanduser().read_text(encoding="utf-8"))["round"])
        except Exception:                                        # noqa: BLE001
            pass
    for round_id in sorted(rounds):
        try:
            declaration = load_round(round_id)
        except Refused:
            continue
        status = lifecycle.round_status(round_id, [p["identity"] for p in declaration["parties"]])
        print(f"\n  {round_id}: {'COMPLETE' if status['complete'] else 'INCOMPLETE'}")
        for party, state in sorted(status["states"].items()):
            print(f"    {party:22} {state}")
        if status["awaiting_disposition"]:
            print(f"    awaiting disposition: {', '.join(status['awaiting_disposition'])}")
        for conflict in status["unresolved_conflicts"]:
            print(f"    DISPUTED  {conflict['identity']}: a differing capture is preserved at")
            print(f"              {conflict['preserved_at']}")

    if "accepted" in outcomes:
        print("\n  Nothing is committed. Review the diff, run `python3 tools/rebuild.py`, then commit.")

    # Distinct statuses, because these need distinct responses and a single non-zero
    # exit would collapse "your correction is being held" into "a bundle was bad".
    #   3  a conflicting receipt was preserved -- a custodian must resolve it
    #   2  something is held awaiting disposition
    #   1  a bundle was refused
    if "conflict" in outcomes:
        return 3
    if "held" in outcomes:
        return 2
    # input_error shares exit 1 with refused: both mean "one or more inputs were not
    # ingested". They are distinguished in the summary, where the difference is
    # legible, rather than in an exit code the shell cannot explain.
    return 1 if {"refused", "input_error"} & set(outcomes) else 0


if __name__ == "__main__":
    sys.exit(main())
