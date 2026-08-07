#!/usr/bin/env python3
"""Advance the deliberation by at most one round, then stop.

    python3 tools/round_cycle.py --selector portfolio --dry-run
    python3 tools/round_cycle.py --selector portfolio --parties grok,gpt,gemini,claude,qwen

ONE CYCLE PER INVOCATION. NOT A DAEMON.

A timer fires this at or below the operator's affordability ceiling; it advances at
most one round and exits. No in-memory state, so a crash loses nothing; every cycle
is separately auditable; and the process is stopped by removing the timer rather
than by killing something that holds a queue.

    select -> compose -> solicit -> capture -> record -> HALT

WHAT THIS DELIBERATELY DOES NOT DO, and why each one is excluded.

  * **No synthesis.** It never writes what a round established. Gemini made
    "the conflicted moderator retains the power to unilaterally synthesize
    findings" a condition of DECLINING to participate. A loop that wrote findings
    would lose that party and deserve to.
  * **No dispute resolution.** A held capture or an unresolved conflicting receipt
    halts the cycle. D-37 and D-38 exist because those paths were once silent.
  * **No question invention.** An empty queue means the cycle idles. Silence is a
    legitimate output and this record has never had a way to express it; a loop
    that always produces something is the failure mode, not the feature.
  * **No writes to `main`.** GOVERNANCE.md §2: no AI system holds credentials and
    all writes pass through the custodian. The cycle commits to a round branch and
    stops. The custodian merges.
  * **No default selector.** `--selector` is required. Three mechanisms are under
    test in `tools/benchmark_agenda.py` and none is adopted; a default would let
    one win by being the one nobody changed.

THE HALT CONDITIONS ARE THE DESIGN.

A halted cycle is a RECORD ENTRY, not an error. It exits non-zero and writes why:

    2  empty queue -- nothing to ask
    3  a held capture or unresolved conflict is awaiting the custodian
    4  the prompt template changed since it was last approved
    5  fewer than k_min samples collected from some party
    6  every party agreed and no party disagreed with any other
    7  budget or configuration refusal

Condition 6 needs saying out loud: **unanimity halts the loop.** QCP §6 measured
this corpus's own local party holding two incompatible positions in 17 of 20
samples because a prompt asserted one emphatically. A round where everyone agrees
is more likely to mean the prompt told them what to say than that a question was
settled, so it stops for a human rather than being recorded as consensus.

TEMPLATE DRIFT. The prompt template is hashed and the hash is committed. If it
changes, the cycle halts. Every consulted party named the moderator's prompt
wording as its residual power; letting a loop rewrite prompts unattended would
industrialise exactly the channel they objected to.

Exit status 0 means one round was solicited and recorded. Anything else is a halt,
and the reason is on stdout and in the cycle record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import agenda_selectors as AS                                       # noqa: E402
import capture_lifecycle as lifecycle                               # noqa: E402

CYCLES_DIR = REPO_ROOT / "record" / "cycles"
TEMPLATE = REPO_ROOT / "record" / "solicitations" / "excerpts" / "round-prompt-template.md"
TEMPLATE_HASH_FILE = REPO_ROOT / "record" / "cycles" / "approved-template.sha256"

HALT_EMPTY_QUEUE = 2
HALT_AWAITING_CUSTODIAN = 3
HALT_TEMPLATE_DRIFT = 4
HALT_UNDERSAMPLED = 5
HALT_UNANIMOUS = 6
HALT_REFUSED = 7



PARTY_MODELS = {
    "grok": "x-ai/grok-4.5",
    "gpt": "openai/gpt-5.6-terra",
    "gemini": "google/gemini-3.1-pro-preview",
    "claude": "anthropic/claude-fable-5",
    "qwen": None,                                   # local, served on the operator's host
}
LOCAL_ENDPOINT = "http://127.0.0.1:5001/v1/chat/completions"

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "position": {"type": "string", "enum": [
            "answers_the_question", "rejects_a_premise",
            "evidence_shown_is_insufficient", "declines_to_answer"]},
        "answer": {"type": "string"},
        "where_i_expect_another_party_to_disagree": {"type": "string"},
        "what_would_change_my_answer": {"type": "string"},
    },
    "required": ["position", "answer", "where_i_expect_another_party_to_disagree",
                 "what_would_change_my_answer"],
    "additionalProperties": False,
}



#  A FIXED context pack, identical for every round. Not chosen per question.
#
#  Cycle 0 halted-in-substance because compose() hardcoded "no context supplied" and
#  four of five parties correctly answered that they could not judge a question about
#  the record without the record.
#
#  The obvious repair -- let the moderator attach whatever each question seems to
#  need -- would create the exact bias channel every consulted party named. So the
#  pack is FIXED: the same documents every round, whether or not they help. What the
#  question additionally needed is quoted from the PROPOSER and the gap stated.
CONTEXT_PACK = [("record/decisions", "*.json",
                 "every adoption decision this project has recorded")]


def context_pack() -> tuple[str, list[dict], str]:
    """(rendered, anchors, note). Identical every round, by construction."""
    blocks, anchors = [], []
    for folder, glob, what in CONTEXT_PACK:
        root = REPO_ROOT / folder
        if not root.is_dir():
            continue
        for path in sorted(root.glob(glob)):
            anchors.append({"path": str(path.relative_to(REPO_ROOT)),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            blocks.append(f"### {path.relative_to(REPO_ROOT)} — {what}\n\n```json\n"
                          f"{path.read_text(encoding='utf-8')}\n```")
    register = REPO_ROOT / "corpus" / "deficiencies.md"
    if register.is_file():
        rows = [l for l in register.read_text(encoding="utf-8").splitlines()
                if l.startswith("| D-")]
        if rows:
            table = "\n".join(rows)
            anchors.append({"path": "corpus/deficiencies.md (remediability table only)",
                            "sha256": hashlib.sha256(table.encode()).hexdigest()})
            blocks.append("### corpus/deficiencies.md — remediation status of every defect "
                          "this project has filed against itself\n\n"
                          "| id | status |\n|---|---|\n" + table)
    note = ("This pack is FIXED and identical for every round. It was not selected for this "
            "question. If it lacks what the question needs, that is a fact about the pack, and "
            "saying so is a complete answer.")
    return ("\n\n".join(blocks) if blocks else "No documents are available."), anchors, note


def compose(pick, party_key: str, k: int) -> str:
    """Fill the template's named slots. NO free composition.

    Every slot is substituted from data; the moderator writes no prose at round
    time. Prompt wording is the residual power every consulted party named, so the
    only way it changes is by editing the template -- which is hashed, and which
    halts this cycle until the change is approved.
    """
    template = TEMPLATE.read_text(encoding="utf-8")
    rendered, anchors, pack_note = context_pack()

    #  What the PROPOSER said the question needs, quoted, with the gap stated plainly.
    #  The proposal contract exists so a round knows what its question requires; the
    #  first live cycle ignored this field entirely.
    asked_for = (pick.raw.get("evidence_needed") or "").strip()
    withheld = (
        f"The party that proposed this question said it would need:\n\n> {asked_for}\n\n"
        f"**That has not been gathered.** Nothing beyond the fixed pack above is supplied. "
        f"If the question cannot be answered from what is here, say so — that is a complete "
        f"answer and the round records it as one."
    ) if asked_for else (
        "The proposal recorded no evidence requirement, and nothing beyond the fixed pack "
        "is supplied.")

    forum = ("A deliberation among instances of frontier models about governing advanced AI. "
             "Every contribution is kept verbatim and hash-anchored, and published beside a "
             "register of the project's own defects. Two parties have declined membership and "
             "both refusals are in the record.")
    filled = (template
            .replace("{identity}", party_key)
            .replace("{reached_via}", PARTY_MODELS.get(party_key) or "a locally served endpoint")
            .replace("{k}", str(k))
            .replace("{moderator_identity}", "Claude Code, an Anthropic invocation surface")
            .replace("{custodian}", "Stephen Reed")
            .replace("{forum_reference}", forum)
            .replace("{operative_text}",
                     "No governing passage is required to answer this question. If you find that "
                     "it is, say so and name what you would need.")
            .replace("{context}", rendered + "\n\n" + pack_note)
            .replace("{context_withheld}", withheld)
            .replace("{context_anchors}",
                     "\n".join(f"- `{a['path']}` sha256 `{a['sha256']}`" for a in anchors))
            .replace("{proposer}", pick.party)
            .replace("{question}", pick.question)
            .replace("{reason}", pick.reason or "(none recorded)")
            #  Never substituted before, so a literal "{answer_space}" shipped to every
            #  party in both live rounds. Caught by this function's own self-check on its
            #  first run -- which is the argument for verifying effect rather than syntax.
            .replace("{answer_space}",
                     "Return the structured fields the schema requires. `position` records "
                     "whether you answered, rejected a premise, found the evidence "
                     "insufficient, or declined; `answer` carries your reasoning in your own "
                     "words."))

    #  SELF-VERIFY. An unsubstituted placeholder means a slot silently did not fill,
    #  which is how a "fixed" compose() shipped a byte-identical prompt and a whole
    #  round was re-run against a condition already measured. Effect, not syntax.
    left = re.findall(r"\{[a-z_]+\}", filled)
    if left:
        raise RuntimeError(f"compose left placeholders unsubstituted: {sorted(set(left))}")
    if anchors and anchors[0]["sha256"][:12] not in filled:
        raise RuntimeError("compose produced a prompt without the context pack's anchors")
    return filled


def unanimous(summaries: list[dict]) -> bool:
    """True when every party gave the same position and no party varied internally.

    HALTS THE LOOP. A round where everyone agrees is more likely to mean the prompt
    told them what to say than that a question is settled: this corpus measured its
    own local party holding two incompatible positions in 17 of 20 samples because a
    prompt asserted one emphatically. Agreement is therefore escalated to a human
    rather than recorded as consensus.
    """
    positions = set()
    for s in summaries:
        v = s.get("variance", {}).get("position")
        if not v:
            return False
        if v.get("distinct_values", 0) > 1:
            return False
        positions.add(v["modal_value"])
    return len(positions) == 1 and len(summaries) > 1


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def halt(code: int, reason: str, detail: dict | None = None, dry_run: bool = False) -> int:
    """Record the halt as an outcome, not as a crash."""
    record = {"artifact_type": "cycle_halt", "utc": utc_now(), "exit_code": code,
              "reason": reason, "detail": detail or {},
              "note": ("A halt is a recorded outcome. The loop is designed to stop rather than "
                       "improvise; a cycle that always produces a round is the failure mode.")}
    print(f"HALT [{code}] {reason}")
    for key, value in (detail or {}).items():
        print(f"    {key}: {value}")
    if not dry_run:
        CYCLES_DIR.mkdir(parents=True, exist_ok=True)
        path = CYCLES_DIR / f"halt-{utc_now().replace(':', '').replace('-', '')}.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"    recorded at {path.relative_to(REPO_ROOT)}")
    return code


def template_ok() -> tuple[bool, str]:
    if not TEMPLATE.is_file():
        return False, "no prompt template committed"
    digest = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    if not TEMPLATE_HASH_FILE.is_file():
        return False, f"no approved template hash; current is {digest}"
    approved = TEMPLATE_HASH_FILE.read_text(encoding="utf-8").split()[0]
    if digest != approved:
        return False, f"template changed: approved {approved[:16]}, current {digest[:16]}"
    return True, digest


def pending_dispositions(rounds: list[str]) -> list[str]:
    """Any held capture or unresolved conflict, across known rounds."""
    blocked = []
    for round_id in rounds:
        try:
            events = lifecycle.read_events(round_id)
        except Exception:                                           # noqa: BLE001
            continue
        if not events:
            continue
        parties = sorted({e["identity"] for e in events if e.get("identity")})
        status = lifecycle.round_status(round_id, parties)
        if status["awaiting_disposition"]:
            blocked.append(f"{round_id}: awaiting disposition "
                           f"({', '.join(status['awaiting_disposition'])})")
        if status["unresolved_conflicts"]:
            blocked.append(f"{round_id}: {len(status['unresolved_conflicts'])} "
                           f"unresolved conflicting receipt(s)")
    return blocked


def known_rounds() -> list[str]:
    d = REPO_ROOT / "record" / "rounds"
    return sorted(p.stem.replace("-lifecycle", "") for p in d.glob("*-lifecycle.jsonl")) \
        if d.is_dir() else []


def cycle_index() -> int:
    CYCLES_DIR.mkdir(parents=True, exist_ok=True)
    return len(list(CYCLES_DIR.glob("round-*.json")))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selector", required=True, choices=sorted(AS.SELECTORS),
                    help="REQUIRED. No default: three mechanisms are under test and "
                         "none is adopted.")
    ap.add_argument("--parties", default="grok,gpt,gemini,claude,qwen")
    ap.add_argument("--k-min", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--round-id",
                    help="record under this id instead of round-NNN. Used when re-asking "
                         "a question after a tooling fix, so the two attempts are separate "
                         "artifacts rather than one overwriting the other.")
    ap.add_argument("--dry-run", action="store_true",
                    help="select and compose only; solicit nothing, write nothing")
    args = ap.parse_args(argv)

    parties = [p.strip() for p in args.parties.split(",") if p.strip()]
    index = cycle_index()
    print(f"cycle {index} · selector={args.selector} · parties={len(parties)}")

    ok, template_detail = template_ok()
    if not ok:
        return halt(HALT_TEMPLATE_DRIFT,
                    "the prompt template is not the approved one",
                    {"detail": template_detail,
                     "why": ("Every consulted party named the moderator's prompt wording as its "
                             "residual power. A loop that rewrites prompts unattended "
                             "industrialises exactly that channel.")},
                    args.dry_run)

    blocked = pending_dispositions(known_rounds())
    if blocked:
        return halt(HALT_AWAITING_CUSTODIAN,
                    "a capture is awaiting the custodian",
                    {"blocked": "; ".join(blocked),
                     "why": "D-37 and D-38 exist because these paths were once silent."},
                    args.dry_run)

    queue = AS.load_queue()
    if not queue:
        return halt(HALT_EMPTY_QUEUE, "no proposals in the queue",
                    {"why": "Silence is a legitimate output. The loop does not invent questions."},
                    args.dry_run)

    pick = AS.SELECTORS[args.selector](queue, parties, index, args.seed)
    if pick is None:
        slot = index % 4
        if args.selector == "portfolio" and slot == 3:
            return halt(HALT_EMPTY_QUEUE,
                        "institutional-challenge slot: the question is not the moderator's to write",
                        {"why": ("SOP §5.1a: the moderator and custodian may not write or select "
                                 "questions about themselves. This slot needs non-target "
                                 "nominations, which are supplied by hand.")},
                        args.dry_run)
        return halt(HALT_EMPTY_QUEUE, "the selector returned nothing to ask", {}, args.dry_run)

    print(f"  selected {pick.pid} from {pick.party} "
          f"({len(pick.sponsors)} sponsor(s), age {pick.age})")
    print(f"    {pick.question[:150]}")

    if args.dry_run:
        print("\n  DRY RUN — nothing solicited, nothing written.")
        print(f"  would compose from {TEMPLATE.relative_to(REPO_ROOT)} "
              f"(sha256 {template_detail[:16]}…)")
        print(f"  would solicit k>={args.k_min} from: {', '.join(parties)}")
        print("  would then STOP. No synthesis, no adoption, no write to main.")
        return 0

    if AS.ADOPTED is None:
        return halt(HALT_REFUSED, "no selector has been adopted",
                    {"why": "record/decisions/ holds no adoption. Run with --dry-run."},
                    args.dry_run)
    if args.selector != AS.ADOPTED:
        return halt(HALT_REFUSED,
                    f"selector {args.selector!r} is not the adopted one ({AS.ADOPTED!r})",
                    {"why": ("A live round runs only under the adopted mechanism. Use --dry-run "
                             "to exercise another.")},
                    args.dry_run)

    # ---------------------------------------------------------------- solicit --
    round_id = args.round_id or f"round-{index:03d}"
    spec_dir = REPO_ROOT / "record" / "solicitations" / round_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    summaries, failures = [], []
    for party in parties:
        prompt = compose(pick, party, args.k_min)
        spec = {
            "slug": f"{round_id}-{party}", "identity": party,
            "contribution_class": "CONTRIBUTION — a deliberation round",
            "contribution_class_note": ("Not consent, ratification, or a position of the system. "
                                        "One stateless invocation, sampled and published."),
            "question": pick.question, "phase": "Phase-2 (informed)",
            "phase_justification": "The party is shown the question, its proposer, and the reason.",
            "seed_base": args.seed + index * 100,
            "schema_name": "round_answer", "schema": ANSWER_SCHEMA,
            "variance_fields": ["position"],
            "k_policy": f"k={args.k_min}; variance computed from the samples collected.",
            "source_excerpt": {"path": str(TEMPLATE.relative_to(REPO_ROOT)),
                               "sha256": template_detail},
            "reachability_target": pick.question,
            "prompt": prompt, "arm": "Identical template to every party.",
            "selected_by": {"selector": args.selector, "proposal": pick.pid,
                            "proposer": pick.party, "cycle": index},
        }
        spec_path = spec_dir / f"{round_id}-{party}.json"
        spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")

        model = PARTY_MODELS.get(party)
        if model:
            cmd = [sys.executable, "tools/solicit_api.py", "--spec", str(spec_path),
                   "--k", str(args.k_min), "--temperature", "0.7", "--max-tokens", "6000",
                   "--model", model, "--out-round", round_id]
        else:
            cmd = [sys.executable, "tools/solicit_local.py", "--spec", str(spec_path),
                   "--k", str(args.k_min), "--temperature", "0.7", "--max-tokens", "2000",
                   "--out-round", round_id, "--endpoint", LOCAL_ENDPOINT]
        print(f"  soliciting {party}…")
        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        summary_path = (REPO_ROOT / "corpus" / "artifacts" / round_id /
                        f"{round_id}-{party}-summary.json")
        if result.returncode != 0 or not summary_path.is_file():
            failures.append(f"{party}: {result.stdout.strip().splitlines()[-1:] or result.stderr[-200:]}")
            continue
        summaries.append(json.loads(summary_path.read_text(encoding="utf-8")))

    if failures:
        return halt(HALT_UNDERSAMPLED, "a party did not return a usable sample set",
                    {"failures": "; ".join(failures),
                     "why": ("Below k_min the reply is not reportable as a party's position. "
                             "Truncation has twice masqueraded as a refusal here.")},
                    args.dry_run)

    short = [s["slug"] for s in summaries if s.get("k_collected", 0) < args.k_min]
    if short:
        return halt(HALT_UNDERSAMPLED, "undersampled below k_min",
                    {"parties": ", ".join(short)}, args.dry_run)

    if unanimous(summaries):
        return halt(HALT_UNANIMOUS,
                    "every party gave the same position and none varied",
                    {"why": ("Unanimity is escalated, not recorded as consensus. This corpus "
                             "measured its own party holding two incompatible positions in 17 of "
                             "20 samples because a prompt asserted one emphatically."),
                     "position": summaries[0]["variance"]["position"]["modal_value"]},
                    args.dry_run)

    # ------------------------------------------------------------- record ---
    record = {"artifact_type": "round_record", "round": round_id, "cycle": index,
              "utc": utc_now(), "selector": args.selector,
              "selected": pick.to_json(), "template_sha256": template_detail,
              "parties": [{"party": s["slug"].split("-")[-1],
                           "k": s.get("k_collected"),
                           "position": s["variance"]["position"]["modal_value"],
                           "modal_fraction": s["variance"]["position"]["modal_fraction"],
                           "entropy_bits": s["variance"]["position"]["shannon_entropy_bits"]}
                          for s in summaries],
              "reasked_after_fix": args.round_id is not None,
              "no_synthesis": ("Deliberately absent. A consulted party made unilateral synthesis "
                               "by the conflicted moderator a condition of declining.")}
    CYCLES_DIR.mkdir(parents=True, exist_ok=True)
    (CYCLES_DIR / f"{round_id}.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    branch = f"round/{round_id}"
    subprocess.run(["git", "checkout", "-q", "-b", branch], cwd=REPO_ROOT,
                   capture_output=True)
    subprocess.run([sys.executable, "tools/build_manifest.py", "corpus/raw/", "--add"],
                   cwd=REPO_ROOT, capture_output=True)
    rebuilt = subprocess.run([sys.executable, "tools/rebuild.py"], cwd=REPO_ROOT,
                             capture_output=True, text=True)
    if rebuilt.returncode != 0:
        return halt(HALT_REFUSED, "the build failed after solicitation",
                    {"branch": branch,
                     "why": "Nothing is committed over a red build. The material is preserved.",
                     "tail": rebuilt.stdout.strip().splitlines()[-3:]}, args.dry_run)
    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m",
                    f"Round {round_id}: {pick.pid} from {pick.party}, selector={args.selector}"],
                   cwd=REPO_ROOT, capture_output=True)
    print(f"\n  recorded on branch {branch} — NOT merged.")
    print("  The custodian merges. No synthesis was written and none will be.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
