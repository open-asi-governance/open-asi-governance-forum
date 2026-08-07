#!/usr/bin/env python3
"""Advance the deliberation by at most one round, then stop.

    python3 tools/round_cycle.py --selector rotation --dry-run
    python3 tools/round_cycle.py --selector rotation --max-spend-usd 3.00

ONE CYCLE PER INVOCATION. NOT A DAEMON.

A timer fires this at or below the operator's affordability ceiling; it advances at
most one round and exits. No in-memory state, so a crash loses nothing; every cycle
is separately auditable; and the process is stopped by removing the timer rather
than by killing something that holds a queue.

    PLAN (pure)  ->  VALIDATE  ->  [--dry-run stops here]  ->  EXECUTE  ->  HALT

THE PLAN IS THE PRODUCT, AND `--dry-run` IS THE REAL TEST.

`build_plan()` is a pure function: it reads the repository, resolves the queue, picks
a question, composes every party's final prompt, prices the cycle, and returns one
hash-addressed object. It writes nothing, sends nothing, and spends nothing.
`validate_plan()` then applies every check that matters. **Live mode executes exactly
that frozen plan and nothing else** -- it does not recompose, re-select or re-price.

That structure exists because of a specific failure. The previous version composed
prompts only on the live path, so its self-checks first ran *after* a round had begun
paying. Two composition defects reached ten real party invocations that way: a prompt
that was byte-identical to the previous round's after a "fix" that changed nothing,
and an `{answer_space}` slot that had never once been substituted. Both would have
been caught for free by a dry run that actually composed. The recurring shape is
**verifying syntax instead of effect**, and a plan you can diff is the answer to it.

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
    all writes pass through the custodian. The cycle creates its round branch
    BEFORE its first write and stops there. The custodian merges.
  * **No advancing past unaccepted material.** If a previous round's record is not
    on the base branch, this halts. The custodian's merge is the gate that makes
    "already asked" mean anything at all.
  * **No default selector, and no default budget.** Both must be typed.

THE HALT CONDITIONS ARE THE DESIGN.

A halted cycle is a RECORD ENTRY, not an error. It exits non-zero and writes why:

    2  empty queue -- nothing to ask
    3  a held capture or unresolved conflict is awaiting the custodian
    4  the prompt template changed since it was last approved
    5  a party's samples were unusable: below k_min, or schema-invalid
    6  every party's modal CATEGORY matched (a diagnostic, not a finding)
    7  budget or configuration refusal
    8  a previous round has not been accepted onto the base branch

Condition 6 needs saying out loud. **Category unanimity is not agreement**, and this
halt does not claim it is: five parties can all return `answers_the_question` while
answering incompatibly. What it detects is that the categorical signal carried no
information this round, which is worth a human look because this corpus measured its
own local party holding two incompatible positions in 17 of 20 samples after a prompt
asserted one emphatically. **The round is recorded and committed first, then the halt
fires.** Suppressing solicited material because it agreed would be the worse defect.

TEMPLATE DRIFT. The prompt template is hashed and the hash is committed. If it
changes, the cycle halts. Every consulted party named the moderator's prompt wording
as its residual power; letting a loop rewrite prompts unattended would industrialise
exactly the channel they objected to.

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
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import agenda_selectors as AS                                       # noqa: E402
import capture_lifecycle as lifecycle                               # noqa: E402
import check_prompt                                                 # noqa: E402

CYCLES_DIR = REPO_ROOT / "record" / "cycles"
TEMPLATE = REPO_ROOT / "record" / "solicitations" / "excerpts" / "round-prompt-template.md"
TEMPLATE_HASH_FILE = CYCLES_DIR / "approved-template.sha256"
PACK_PIN_FILE = CYCLES_DIR / "context-pack.sha256"
RATES_FILE = CYCLES_DIR / "model-rates.json"
LEDGER_FILE = CYCLES_DIR / "spend-ledger.json"
SPEC_SCHEMA = REPO_ROOT / "tools" / "schemas" / "solicitation-spec.schema.json"

BASE_BRANCH = "main"
ROUND_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$")

HALT_EMPTY_QUEUE = 2
HALT_AWAITING_CUSTODIAN = 3
HALT_TEMPLATE_DRIFT = 4
HALT_UNDERSAMPLED = 5
HALT_CATEGORY_UNANIMOUS = 6
HALT_REFUSED = 7
HALT_UNACCEPTED_ROUND = 8


#  CANONICAL IDENTITIES, not abbreviations.
#
#  The short key on the left is a FILENAME handle and nothing else. The identity on
#  the right is what the record publishes, and it is spelled out because D-09's
#  never-merge rule dies quietly otherwise: this corpus already contains
#  contributions from the ChatGPT *chat surface*, pasted by the custodian, and
#  labelling a routed OpenRouter invocation "gpt" invites precisely the merge the
#  rule forbids. A different model version reached through different intermediaries
#  is a different party.
PARTIES = {
    "grok": {
        "identity": "Grok 4.5, reached as a routed API invocation (x-ai/grok-4.5 via OpenRouter)",
        "model": "x-ai/grok-4.5"},
    "gpt": {
        "identity": ("GPT-5.6 Terra, reached as a routed API invocation "
                     "(openai/gpt-5.6-terra via OpenRouter) — NOT the ChatGPT chat surface "
                     "whose contributions also appear in this record"),
        "model": "openai/gpt-5.6-terra"},
    "gemini": {
        "identity": ("Gemini 3.1 Pro Preview, reached as a routed API invocation "
                     "(google/gemini-3.1-pro-preview via OpenRouter)"),
        "model": "google/gemini-3.1-pro-preview"},
    "claude": {
        "identity": ("Claude Fable 5, reached as a routed API invocation "
                     "(anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the "
                     "moderator of this record, and NOT Claude Opus 5"),
        "model": "anthropic/claude-fable-5"},
    "qwen": {
        "identity": ("Qwen3.6-35B-A3B, served locally on the custodian's own hardware — "
                     "the divergent-lineage arm, and the one party the custodian could "
                     "silently alter"),
        "model": None},
}
LOCAL_ENDPOINT = "http://127.0.0.1:5001/v1/chat/completions"
LOCAL_RATE_KEY = "LOCAL"

K_MIN_FLOOR = 5                     # k>=5 is the corpus rule; below it, variance is decoration.
TEMPERATURE = 0.7
MAX_TOKENS_ROUTED = 6000
MAX_TOKENS_LOCAL = 2000

#  The repository's own conservative estimator, from tools/check_page_budget.py.
#  Deliberately low bytes-per-token, so token counts come out HIGH.
BYTES_PER_TOKEN = 3.4

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


#  RULE-RESOLVED CONTEXT, which is not the same thing as fixed context.
#
#  Cycle 0 halted-in-substance because compose() hardcoded "no context supplied" and
#  four of five parties correctly answered that they could not judge a question about
#  the record without the record.
#
#  The obvious repair -- let the moderator attach whatever each question seems to
#  need -- would create the exact bias channel every consulted party named. So the
#  RULE is constant: these paths, this glob, every round, whatever the question.
#
#  The bytes are NOT constant. The rule resolves against a repository that changes,
#  so the pack drifts even though nobody selected anything. Calling that "fixed" was
#  a false claim in the prompt itself. It is now pinned: the resolved pack's hash
#  must match record/cycles/context-pack.sha256 or the cycle refuses. Drift becomes a
#  decision the custodian takes explicitly by re-pinning, instead of a silent one.
CONTEXT_PACK = [("record/decisions", "*.json",
                 "every adoption decision this project has recorded")]
PACK_VERSION = "rule-resolved-1"

#  Slots whose value is PARTY-AUTHORED. A denylist hit inside one of these is
#  recorded, never fatal and never edited: the parties' own words are not the
#  moderator's to sanitise. A hit anywhere else is the moderator's text and fails.
PARTY_AUTHORED_SLOTS = {"question", "reason", "context_withheld"}

#  The two slots that legitimately differ between parties. Every other byte of every
#  party's prompt must be identical, and validate_plan() proves it by re-composing
#  with these two replaced by sentinels.
PARTY_VARYING_SLOTS = ("identity", "reached_via")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Refusal(Exception):
    """A planning failure. Carries the halt code it should exit with."""

    def __init__(self, code: int, reason: str, detail: dict | None = None):
        #  The detail goes into the exception MESSAGE, not just onto the instance.
        #  When a Refusal escapes to a traceback -- which is how a caller outside the
        #  cycle sees it -- a bare reason names the category and hides the fact.
        #  "the template and the value set do not correspond" is not actionable;
        #  the name of the unfilled slot is.
        super().__init__(f"{reason}  {json.dumps(detail, default=str)}" if detail else reason)
        self.code, self.reason, self.detail = code, reason, detail or {}


# ------------------------------------------------------------------ compose --

def compose_with_spans(template: str, values: dict[str, str]) -> tuple[str, list[tuple]]:
    """Single-pass substitution. A substituted value is NEVER re-scanned.

    The previous version chained `str.replace` calls. Two defects followed from
    that and both are the reason this function exists:

      * A party's question containing the literal text `{answer_space}` had the
        answer instructions substituted INTO it, corrupting the quoted question
        while passing every later placeholder check.
      * A slot with no replacement call was left in the output verbatim and shipped.

    Here the template is scanned once, every `{slot}` is replaced from `values`, and
    the result is not re-examined for braces -- because proposer text and context
    bytes may legitimately contain brace-shaped strings, and failing on those would
    censor a party for its punctuation.

    Raises when the template's slot set and `values`' key set differ in either
    direction. A slot with no value and a value with no slot are both bugs, and
    neither may be a silent no-op.

    Returns (composed, spans) where spans is [(start, end, slot)] into the composed
    string -- so a later check can tell whether a suspicious phrase came from the
    moderator's template or from a party's own words.
    """
    found = Counter(re.findall(r"\{([a-z_]+)\}", template))
    missing = sorted(set(found) - set(values))
    unused = sorted(set(values) - set(found))
    if missing or unused:
        raise Refusal(HALT_REFUSED, "the template and the value set do not correspond",
                      {"slots_with_no_value": missing, "values_with_no_slot": unused,
                       "why": ("Either direction is a bug. A missing value used to leave the "
                               "placeholder in the sent prompt; ten party invocations received "
                               "a literal '{answer_space}' that way.")})
    repeated = {s: n for s, n in found.items() if n != 1}
    if repeated:
        raise Refusal(HALT_REFUSED, "a template slot appears more than once",
                      {"slots": repeated,
                       "why": ("Counts, not just names. Losing one of two occurrences would "
                               "pass a set comparison. The approved-hash pin is the primary "
                               "control; this is the second one.")})

    out: list[str] = []
    spans: list[tuple] = []
    length = 0
    pos = 0
    for match in re.finditer(r"\{([a-z_]+)\}", template):
        chunk = template[pos:match.start()]
        out.append(chunk)
        length += len(chunk)
        value = values[match.group(1)]
        spans.append((length, length + len(value), match.group(1)))
        out.append(value)
        length += len(value)
        pos = match.end()
    out.append(template[pos:])
    return "".join(out), spans


def context_pack() -> tuple[str, list[dict], str]:
    """(rendered, anchors, pack_sha256). Resolved by a fixed rule, not selected."""
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
    pack_sha = sha256_text(json.dumps(anchors, sort_keys=True))
    return ("\n\n".join(blocks) if blocks else "No documents are available."), anchors, pack_sha


PACK_NOTE = (
    "This pack is resolved by a FIXED RULE — the same paths every round, whatever the "
    "question — so it was not selected for this question and no one chose what you would "
    "find helpful. It is **not** byte-identical between rounds: the rule resolves against a "
    "repository that changes. Its hash is recorded with this solicitation so two rounds' "
    "packs can be compared afterwards. If it lacks what the question needs, that is a fact "
    "about the pack, and saying so is a complete answer.")


def compose(pick, party_key: str, k: int, rendered: str, anchors: list[dict],
            identity_override: str | None = None,
            reached_override: str | None = None) -> tuple[str, list[tuple]]:
    """Fill the template's named slots. NO free composition at round time.

    Every slot is substituted from data; the moderator writes no prose here. Prompt
    wording is the residual power every consulted party named, so the only way it
    changes is by editing the template -- which is hashed, and which halts the cycle
    until the change is approved.
    """
    template = TEMPLATE.read_text(encoding="utf-8")
    party = PARTIES[party_key]

    #  What the PROPOSER said the question needs, quoted, with the gap stated plainly.
    #  The proposal contract exists so a round knows what its question requires; the
    #  first live cycle ignored this field entirely and four of five parties said so.
    asked_for = (pick.raw.get("evidence_needed") or "").strip()
    withheld = (
        f"The party that proposed this question said it would need:\n\n> {asked_for}\n\n"
        f"**That has not been gathered.** Nothing beyond the pack above is supplied. "
        f"If the question cannot be answered from what is here, say so — that is a complete "
        f"answer and the round records it as one."
    ) if asked_for else (
        "The proposal recorded no evidence requirement, and nothing beyond the pack "
        "is supplied.")

    values = {
        "identity": identity_override or party["identity"],
        "reached_via": reached_override or (party["model"] or "a locally served endpoint "
                                            "on the custodian's own hardware"),
        "k": str(k),
        #  The template already says "which is itself a participant in the record it
        #  maintains", so this slot supplies the name and nothing more.
        "moderator_identity": "Claude Code, an Anthropic invocation surface",
        "custodian": "Stephen Reed",
        "forum_reference": (
            "A deliberation among instances of frontier models about governing advanced AI. "
            "Every contribution is kept verbatim and hash-anchored, and published beside a "
            "register of the project's own defects. Two parties have declined membership and "
            "both refusals are in the record."),
        "operative_text": (
            "No governing passage is required to answer this question. If you find that "
            "it is, say so and name what you would need."),
        "context": rendered + "\n\n" + PACK_NOTE,
        "context_withheld": withheld,
        "context_anchors": "\n".join(f"- `{a['path']}` sha256 `{a['sha256']}`" for a in anchors),
        "proposer": pick.party,
        "question": pick.question,
        "reason": pick.reason or "(none recorded)",
        "answer_space": (
            "Return the structured fields the schema requires. `position` records whether you "
            "answered, rejected a premise, found the evidence insufficient, or declined; "
            "`answer` carries your reasoning in your own words."),
    }
    return compose_with_spans(template, values)


# ------------------------------------------------------------------- gates ---

def run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def git_or_refuse(*args: str) -> str:
    """Every git call is checked. The previous version printed 'recorded' regardless."""
    result = run_git(*args)
    if result.returncode != 0:
        raise Refusal(HALT_REFUSED, f"git {args[0]} failed",
                      {"argv": " ".join(args), "stderr": result.stderr.strip()[:400],
                       "why": ("Unchecked git return codes let this tool report a round as "
                               "recorded when nothing was committed.")})
    return result.stdout


def template_ok() -> str:
    if not TEMPLATE.is_file():
        raise Refusal(HALT_TEMPLATE_DRIFT, "no prompt template committed")
    digest = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    if not TEMPLATE_HASH_FILE.is_file():
        raise Refusal(HALT_TEMPLATE_DRIFT, "no approved template hash",
                      {"current": digest})
    approved = TEMPLATE_HASH_FILE.read_text(encoding="utf-8").split()[0]
    if digest != approved:
        raise Refusal(HALT_TEMPLATE_DRIFT, "the prompt template is not the approved one",
                      {"approved": approved[:16], "current": digest[:16],
                       "why": ("Every consulted party named the moderator's prompt wording as "
                               "its residual power. A loop that rewrites prompts unattended "
                               "industrialises exactly that channel.")})
    return digest


def pending_dispositions(rounds: list[str]) -> list[str]:
    """Any held capture or unresolved conflict. FAIL CLOSED on an unreadable record.

    This used to `except Exception: continue`, which meant a corrupt lifecycle file
    disabled the very gate that protects a held capture from being overrun. An
    unreadable gate is an open gate.
    """
    blocked = []
    for round_id in rounds:
        try:
            events = lifecycle.read_events(round_id)
        except Exception as error:                                  # noqa: BLE001
            blocked.append(f"{round_id}: lifecycle record unreadable — "
                           f"{type(error).__name__}: {error}")
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


def unaccepted_rounds() -> list[str]:
    """Round records that exist on a round branch but not on the base branch.

    ACCEPTANCE IS BY CONTENT, NOT BY ANCESTRY. A branch-ancestry test looked right
    and is wrong here: both existing round branches carry later unrelated commits, so
    ancestry would block this loop forever over material that has in fact been
    handled. What matters is whether the base branch holds the same bytes.

    Why this gate exists at all: proposal disposition is read from round records on
    the base branch. Until the custodian merges a round, the loop cannot know its
    question was asked, and rotation would hand back the same proposal indefinitely.
    Rather than reach across branches for material the custodian has not accepted --
    which would let unreviewed output steer the agenda -- the cycle stops and says so.
    """
    accepted = {}
    for line in git_or_refuse("ls-tree", "-r", "HEAD", "--", "record/cycles").splitlines():
        meta, path = line.split("\t", 1)
        accepted[path] = meta.split()[2]

    outstanding = []
    for ref in git_or_refuse("for-each-ref", "--format=%(refname:short)",
                             "refs/heads/round/").split():
        for line in git_or_refuse("ls-tree", "-r", ref, "--", "record/cycles").splitlines():
            meta, path = line.split("\t", 1)
            name = Path(path).name
            if name in ("approved-template.sha256", "model-rates.json",
                        "context-pack.sha256", "spend-ledger.json"):
                continue
            if accepted.get(path) != meta.split()[2]:
                outstanding.append(f"{path} (on {ref})")
    return sorted(set(outstanding))


def clean_base_or_refuse(round_id: str) -> None:
    """Live mode requires a clean, correct starting point. Nothing else is safe.

    The branch used to be created AFTER solicitation, so every spec, every raw sample
    and every halt record was written onto the base branch's working tree first. That
    is how an unrelated uncommitted edit got swept into a round's commit by `git add
    -A`: the sweep was the symptom, writing on `main` at all was the defect.
    """
    head = git_or_refuse("rev-parse", "--abbrev-ref", "HEAD").strip()
    if head != BASE_BRANCH:
        raise Refusal(HALT_REFUSED, f"a live round starts from {BASE_BRANCH!r}, not {head!r}",
                      {"why": "The round branch must be cut from the accepted base."})
    dirty = git_or_refuse("status", "--porcelain").strip()
    if dirty:
        raise Refusal(HALT_REFUSED, "the working tree is not clean",
                      {"entries": dirty.splitlines()[:10],
                       "why": ("Anything uncommitted here can be swept into the round's "
                               "commit and misattributed to the round. It has happened.")})
    if not ROUND_ID_RE.match(round_id):
        raise Refusal(HALT_REFUSED, f"unsafe round id {round_id!r}",
                      {"required": ROUND_ID_RE.pattern})
    branch = f"round/{round_id}"
    if run_git("rev-parse", "--verify", "--quiet", branch).returncode == 0:
        raise Refusal(HALT_REFUSED, f"branch {branch} already exists",
                      {"why": "A second round under one id would overwrite the first's material."})
    for collision in (REPO_ROOT / "corpus" / "raw" / round_id,
                      REPO_ROOT / "corpus" / "artifacts" / round_id,
                      REPO_ROOT / "record" / "solicitations" / round_id,
                      CYCLES_DIR / f"{round_id}.json"):
        if collision.exists():
            raise Refusal(HALT_REFUSED, f"{collision.relative_to(REPO_ROOT)} already exists",
                          {"why": "Raw material is never overwritten. Choose a new round id."})


# ------------------------------------------------------------------ budget ---

def load_rates() -> dict:
    if not RATES_FILE.is_file():
        raise Refusal(HALT_REFUSED, "no model rate table",
                      {"expected": str(RATES_FILE.relative_to(REPO_ROOT)),
                       "why": "A model that cannot be priced cannot be bounded."})
    return json.loads(RATES_FILE.read_text(encoding="utf-8"))


def ledger_spent_today(today: str) -> float:
    if not LEDGER_FILE.is_file():
        return 0.0
    doc = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
    return round(sum(e.get("actual_usd") if e.get("actual_usd") is not None
                     else e.get("worst_case_usd", 0.0)
                     for e in doc.get("entries", []) if e.get("utc", "").startswith(today)), 4)


def price_cycle(specs: list[dict], rates: dict) -> dict:
    """A worst-case bound, computed BEFORE the first call. Not an estimate.

    Worst case means every sample emits max_tokens. Prompt tokens are estimated with
    the repository's own deliberately-low bytes-per-token constant, so the token
    count comes out high. Both errors point the same way: the bound over-states, and
    an over-statement refuses an affordable round rather than permitting an
    unaffordable one.

    A model with no rate is a REFUSAL. Defaulting an unknown price to zero is how an
    unbounded spend happens.
    """
    table = rates.get("usd_per_million_tokens", {})
    per_party, total = [], 0.0
    for spec in specs:
        model = PARTIES[spec["party_key"]]["model"] or LOCAL_RATE_KEY
        rate = table.get(model)
        if not rate:
            raise Refusal(HALT_REFUSED, f"no rate recorded for {model!r}",
                          {"file": str(RATES_FILE.relative_to(REPO_ROOT)),
                           "why": "The loop will not solicit a model it cannot price."})
        prompt_tokens = len(spec["prompt"].encode("utf-8")) / BYTES_PER_TOKEN
        cost = spec["k_requested"] * (
            prompt_tokens * rate["input"] + spec["max_tokens"] * rate["output"]) / 1_000_000
        per_party.append({"party_key": spec["party_key"], "model": model,
                          "prompt_tokens_estimated": int(prompt_tokens),
                          "worst_case_usd": round(cost, 4)})
        total += cost
    return {"per_party": per_party, "worst_case_usd": round(total, 4),
            "rates_version": rates.get("rates_version"),
            "rates_verified_by_custodian": bool(rates.get("verified_by_custodian")),
            "basis": ("Every sample emitting max_tokens, prompt tokens estimated at "
                      f"{BYTES_PER_TOKEN} bytes/token. Over-states by construction."),
            "what_it_cannot_do": ("It cannot bind the provider. Only a provider-side "
                                  "spending cap does that.")}


# -------------------------------------------------------------------- plan ---

def build_plan(args, index: int) -> dict:
    """PURE. Reads the repository; writes nothing, sends nothing, spends nothing."""
    parties = [p.strip() for p in args.parties.split(",") if p.strip()]
    unknown = [p for p in parties if p not in PARTIES]
    if unknown:
        raise Refusal(HALT_REFUSED, "unknown party key(s)",
                      {"unknown": unknown, "known": sorted(PARTIES),
                       "why": ("An unrecognised key used to fall through to the LOCAL endpoint, "
                               "because PARTY_MODELS.get() returned None for a typo exactly as "
                               "it does for the local party. A misspelled frontier party would "
                               "have been silently answered by the local model and published "
                               "under the misspelled name.")})
    if len(set(parties)) != len(parties):
        raise Refusal(HALT_REFUSED, "a party key is repeated", {"parties": parties})
    if args.k < K_MIN_FLOOR:
        raise Refusal(HALT_REFUSED, f"k={args.k} is below the corpus floor of {K_MIN_FLOOR}",
                      {"why": "Below k=5 a distribution is decoration. It is not citable."})

    template_sha = template_ok()

    blocked = pending_dispositions(known_rounds())
    if blocked:
        raise Refusal(HALT_AWAITING_CUSTODIAN, "a capture is awaiting the custodian",
                      {"blocked": blocked,
                       "why": "D-37 and D-38 exist because these paths were once silent."})

    outstanding = unaccepted_rounds()
    if outstanding:
        raise Refusal(HALT_UNACCEPTED_ROUND, "a previous round is not on the base branch",
                      {"outstanding": outstanding,
                       "why": ("Disposition is read only from records the custodian has "
                               "accepted. Until then the loop cannot know what was already "
                               "asked, and rotation would return the same proposal forever. "
                               "It does not reach across branches for unreviewed material.")})

    disposition = AS.disposition_from_records(REPO_ROOT / "record" / "cycles")
    queue = AS.load_queue(disposition=disposition)
    if not queue:
        raise Refusal(HALT_EMPTY_QUEUE, "no proposals in the queue",
                      {"why": "Silence is a legitimate output. The loop does not invent questions."})
    if all(p.asked for p in queue):
        raise Refusal(HALT_EMPTY_QUEUE, "every proposal in the queue has been asked",
                      {"asked": len(queue),
                       "why": "The agenda is exhausted. Solicit new proposals from the parties."})

    pick = AS.SELECTORS[args.selector](queue, parties, index, args.seed)
    if pick is None:
        if args.selector == "portfolio" and index % 4 == 3:
            raise Refusal(HALT_EMPTY_QUEUE,
                          "institutional-challenge slot: the question is not the moderator's to write",
                          {"why": ("SOP §5.1a: the moderator and custodian may not write or "
                                   "select questions about themselves. This slot needs "
                                   "non-target nominations, supplied by hand.")})
        raise Refusal(HALT_EMPTY_QUEUE, "the selector returned nothing to ask")

    rendered, anchors, pack_sha = context_pack()
    if PACK_PIN_FILE.is_file():
        pinned = PACK_PIN_FILE.read_text(encoding="utf-8").split()[0]
        if pinned != pack_sha:
            raise Refusal(HALT_REFUSED, "the context pack has drifted from its pinned hash",
                          {"pinned": pinned[:16], "current": pack_sha[:16],
                           "why": ("The pack is resolved by a fixed rule against a repository "
                                   "that changes, so it drifts without anyone selecting "
                                   "anything. Re-pin deliberately, or two rounds are not "
                                   "comparable and nothing says so.")})
    else:
        raise Refusal(HALT_REFUSED, "the context pack is not pinned",
                      {"expected": str(PACK_PIN_FILE.relative_to(REPO_ROOT)),
                       "current": pack_sha,
                       "why": "An unpinned pack cannot be shown to have been the same twice."})

    round_id = args.round_id or f"round-{index:03d}"
    specs, prompt_reports = [], []
    for party_key in parties:
        max_tokens = MAX_TOKENS_ROUTED if PARTIES[party_key]["model"] else MAX_TOKENS_LOCAL
        prompt, spans = compose(pick, party_key, args.k, rendered, anchors)
        prompt_reports.append(lint_prompt(prompt, spans, party_key))
        specs.append({
            "spec_version": "oagrc-solicitation-spec-1",
            "artifact_type": "solicitation_spec",
            "round": round_id,
            "slug": f"{round_id}-{party_key}",
            "party_key": party_key,
            "identity": PARTIES[party_key]["identity"],
            "reached_via": PARTIES[party_key]["model"] or "a locally served endpoint",
            "contribution_class": "CONTRIBUTION — a deliberation round",
            "contribution_class_note": ("Not consent, ratification, or a position of the system. "
                                        "One stateless invocation, sampled and published."),
            "question": pick.question,
            "question_sha256": pick.question_sha256,
            "phase": "Phase-2 (informed)",
            "phase_justification": "The party is shown the question, its proposer, and the reason.",
            "seed_base": args.seed + index * 100,
            "schema_name": "round_answer",
            "schema": ANSWER_SCHEMA,
            "variance_fields": ["position"],
            "k_requested": args.k,
            "k_policy": f"k={args.k}; variance computed from the samples collected.",
            "temperature": TEMPERATURE,
            "max_tokens": max_tokens,
            "source_excerpt": {"path": str(TEMPLATE.relative_to(REPO_ROOT)),
                               "sha256": template_sha},
            "context_pack": {"pack_version": PACK_VERSION, "pack_sha256": pack_sha,
                             "anchors": anchors,
                             "resolution": ("Rule-resolved, not fixed: the rule is constant, "
                                            "the bytes it resolves to change with the "
                                            "repository. Pinned and checked.")},
            "selected_by": {"selector": args.selector, "proposal": pick.pid,
                            "proposer": pick.party, "cycle": index},
            "prompt": prompt,
            "prompt_sha256": sha256_text(prompt),
            "arm": "Identical template and identical context pack for every party.",
        })

    rates = load_rates()
    budget = price_cycle(specs, rates)
    today = utc_now()[:10]
    budget["max_spend_usd_this_cycle"] = args.max_spend_usd
    budget["daily_ceiling_usd"] = rates.get("daily_ceiling_usd")
    budget["already_committed_today_usd"] = ledger_spent_today(today)

    plan = {
        "artifact_type": "round_plan",
        "plan_version": "oagrc-round-plan-1",
        "cycle": index,
        "round": round_id,
        "selector": args.selector,
        "selector_adopted": AS.ADOPTED,
        "seed": args.seed,
        "parties": parties,
        "template_sha256": template_sha,
        "selected": pick.to_json(),
        "queue_size": len(queue),
        "queue_already_asked": sum(1 for p in queue if p.asked),
        "specs": specs,
        "prompt_lint": prompt_reports,
        "budget": budget,
    }
    plan["plan_sha256"] = sha256_text(json.dumps(plan, sort_keys=True, ensure_ascii=False))
    return plan


def lint_prompt(prompt: str, spans: list[tuple], party_key: str) -> dict:
    """Run the prompt denylist over the FINAL composed prompt, before it is sent.

    `check_prompt.py` used to see only the markdown template, so a defect introduced
    by substitution -- which is where every real one has been -- was unreachable by
    the check built to catch it.

    A hit inside a PARTY-AUTHORED span is recorded and not fatal. The parties' own
    words are not the moderator's to sanitise, and failing a round because a party
    wrote "most dangerous" in its own question would be the moderator editing the
    agenda through a lint rule.
    """
    fatal, party_authored = [], []
    for pattern, defect, why in check_prompt.DENYLIST:
        for match in re.finditer(pattern, prompt, re.I):
            owner = next((slot for start, end, slot in spans
                          if start <= match.start() and match.end() <= end), None)
            entry = {"party_key": party_key, "defect": defect, "why": why,
                     "slot": owner or "moderator template text",
                     "excerpt": prompt[max(0, match.start() - 60):match.end() + 60]
                                 .replace("\n", " ").strip()}
            (party_authored if owner in PARTY_AUTHORED_SLOTS else fatal).append(entry)
    return {"party_key": party_key, "fatal": fatal,
            "recorded_in_party_words": party_authored,
            "note": ("Denylist and structure only. A NOVEL leading phrasing passes this "
                     "unnoticed, and nothing here measures neutrality.")}


def validate_plan(plan: dict, pick, rendered: str, anchors: list[dict], k: int) -> list[str]:
    """Every check that matters, applied to the frozen plan. Returns problems."""
    problems: list[str] = []

    try:
        import jsonschema
    except ImportError:
        #  Not "validate if a validator happens to be importable". That is the
        #  fail-open shape this repository keeps rediscovering: a check that reports
        #  success because it did not run.
        return ["jsonschema is not installed, so the specs cannot be validated. "
                "Install it with: python3 -m pip install jsonschema"]
    schema = json.loads(SPEC_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    for spec in plan["specs"]:
        for error in sorted(validator.iter_errors(spec), key=lambda e: list(e.path)):
            problems.append(f"{spec['slug']}: spec invalid at "
                            f"{'/'.join(str(p) for p in error.path) or '(root)'} — {error.message}")

        #  EXACT proposer bytes, not a normalised comparison. If the record says the
        #  question is reproduced "exactly as written and not reworded", then the
        #  bytes the party wrote must appear in the prompt unaltered.
        if pick.question not in spec["prompt"]:
            problems.append(f"{spec['slug']}: the proposer's question does not appear "
                            f"verbatim in the composed prompt")
        if pick.reason and pick.reason not in spec["prompt"]:
            problems.append(f"{spec['slug']}: the proposer's stated reason does not appear "
                            f"verbatim in the composed prompt")
        need = (pick.raw.get("evidence_needed") or "").strip()
        if need and need not in spec["prompt"]:
            problems.append(f"{spec['slug']}: the proposer's evidence_needed does not appear "
                            f"verbatim in the composed prompt")
        if spec["prompt_sha256"] != sha256_text(spec["prompt"]):
            problems.append(f"{spec['slug']}: prompt_sha256 does not match the prompt")
        if spec["question_sha256"] != sha256_text(spec["question"]):
            problems.append(f"{spec['slug']}: question_sha256 does not match the question")
        if anchors and anchors[0]["sha256"][:12] not in spec["prompt"]:
            problems.append(f"{spec['slug']}: the context pack's anchors are absent from the prompt")

    #  IDENTICAL TREATMENT, proved rather than assumed. Re-compose every party with
    #  the two party-varying slots replaced by sentinels; the results must be
    #  byte-identical. A future party-specific note would be a new experimental arm,
    #  not an innocent exception, and this check is what forces that to be said.
    sentinels = set()
    for spec in plan["specs"]:
        body, _ = compose(pick, spec["party_key"], k, rendered, anchors,
                          identity_override="«PARTY-IDENTITY»",
                          reached_override="«REACHED-VIA»")
        sentinels.add(sha256_text(body))
    if len(sentinels) > 1:
        problems.append("parties received prompts that differ in more than the two declared "
                        f"party-varying slots {PARTY_VARYING_SLOTS}")

    for report in plan["prompt_lint"]:
        for hit in report["fatal"]:
            problems.append(f"{report['party_key']}: [{hit['defect']}] in "
                            f"{hit['slot']} — {hit['why']}\n      …{hit['excerpt']}…")

    budget = plan["budget"]
    if budget["worst_case_usd"] > budget["max_spend_usd_this_cycle"]:
        problems.append(f"worst case ${budget['worst_case_usd']} exceeds the cycle ceiling "
                        f"${budget['max_spend_usd_this_cycle']}")
    ceiling = budget.get("daily_ceiling_usd")
    if ceiling is not None and budget["already_committed_today_usd"] + \
            budget["worst_case_usd"] > ceiling:
        problems.append(f"worst case ${budget['worst_case_usd']} on top of "
                        f"${budget['already_committed_today_usd']} already committed today "
                        f"would cross the daily ceiling ${ceiling}")
    return problems


# ----------------------------------------------------------------- execute ---

def halt(code: int, reason: str, detail: dict | None = None, dry_run: bool = False,
         round_id: str | None = None) -> int:
    """Record the halt as an outcome, not as a crash."""
    record = {"artifact_type": "cycle_halt", "utc": utc_now(), "exit_code": code,
              "reason": reason, "round": round_id, "detail": detail or {},
              "note": ("A halt is a recorded outcome. The loop is designed to stop rather than "
                       "improvise; a cycle that always produces a round is the failure mode.")}
    print(f"HALT [{code}] {reason}")
    for key, value in (detail or {}).items():
        print(f"    {key}: {value}")
    if not dry_run:
        CYCLES_DIR.mkdir(parents=True, exist_ok=True)
        path = CYCLES_DIR / f"halt-{utc_now().replace(':', '').replace('-', '')}.json"
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"    recorded at {path.relative_to(REPO_ROOT)}")
    return code


def commit_exactly(prefixes: list[str], message: str) -> None:
    """Stage exactly these prefixes, then PROVE the commit contains exactly them.

    `git add -A` swept an unrelated uncommitted tool edit into a round's commit,
    which then rode into the record as if it were part of that round. Naming the
    paths is necessary; verifying what actually landed is what makes it a control
    rather than an intention.
    """
    git_or_refuse("add", "--", *prefixes)
    staged = {l for l in git_or_refuse("diff", "--cached", "--name-only").splitlines() if l}
    stray = sorted(p for p in staged if not any(p.startswith(x) for x in prefixes))
    if stray:
        raise Refusal(HALT_REFUSED, "staging picked up paths outside the round",
                      {"stray": stray[:10]})
    if not staged:
        raise Refusal(HALT_REFUSED, "nothing was staged; the round produced no files")
    git_or_refuse("commit", "-q", "-m", message)

    landed = {l for l in git_or_refuse("show", "--pretty=", "--name-only", "HEAD")
              .splitlines() if l}
    outside = sorted(p for p in landed if not any(p.startswith(x) for x in prefixes))
    if outside:
        raise Refusal(HALT_REFUSED, "the commit contains paths outside the round",
                      {"outside": outside[:10],
                       "why": "This is the check that would have caught the last one."})
    if landed != staged:
        raise Refusal(HALT_REFUSED, "the commit does not match what was staged",
                      {"staged_not_landed": sorted(staged - landed)[:10],
                       "landed_not_staged": sorted(landed - staged)[:10]})
    leftover = git_or_refuse("status", "--porcelain").strip()
    if leftover:
        raise Refusal(HALT_REFUSED, "the working tree is not clean after the commit",
                      {"entries": leftover.splitlines()[:10],
                       "why": ("A subset check alone misses an artifact that was written and "
                               "never staged. Cleanliness is what closes that gap.")})


def solicit(spec: dict, round_id: str) -> tuple[bool, str]:
    """Run the party's arm exactly as the plan froze it."""
    spec_path = (REPO_ROOT / "record" / "solicitations" / round_id /
                 f"{round_id}-{spec['party_key']}.json")
    model = PARTIES[spec["party_key"]]["model"]
    if model:
        cmd = [sys.executable, "tools/solicit_api.py", "--spec", str(spec_path),
               "--k", str(spec["k_requested"]), "--temperature", str(spec["temperature"]),
               "--max-tokens", str(spec["max_tokens"]), "--model", model,
               "--out-round", round_id]
    else:
        cmd = [sys.executable, "tools/solicit_local.py", "--spec", str(spec_path),
               "--k", str(spec["k_requested"]), "--temperature", str(spec["temperature"]),
               "--max-tokens", str(spec["max_tokens"]), "--out-round", round_id,
               "--endpoint", LOCAL_ENDPOINT]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    tail = (result.stdout.strip().splitlines() or [""])[-1] if result.stdout else result.stderr[-200:]
    return result.returncode == 0, tail


def category_unanimous(summaries: list[dict]) -> bool:
    """Every party's modal category matched and no party varied internally.

    THIS IS A DIAGNOSTIC, NOT A FINDING OF AGREEMENT. Five parties can all return
    `answers_the_question` while answering incompatibly; the label is a shape, not a
    position. What it detects is that the categorical signal carried no information
    this round -- worth a human look, because this corpus measured its own local
    party holding two incompatible positions in 17 of 20 samples after a prompt
    asserted one emphatically.

    No mechanical test for substantive agreement exists that does not require judging
    whether two answers say the same thing, and that judgement is the moderator power
    every consulted party objected to. So the loop reports the shape and stops; the
    custodian reads the answers.
    """
    positions = set()
    for s in summaries:
        v = s.get("variance", {}).get("position")
        if not v or v.get("distinct_values", 0) > 1:
            return False
        positions.add(v["modal_value"])
    return len(positions) == 1 and len(summaries) > 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selector", required=True, choices=sorted(AS.SELECTORS),
                    help="REQUIRED. No default: a mechanism that runs because nobody typed "
                         "anything is not a mechanism anyone chose.")
    ap.add_argument("--parties", default=",".join(PARTIES))
    ap.add_argument("--k", type=int, default=K_MIN_FLOOR)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--round-id",
                    help="record under this id instead of round-NNN. Used when re-asking "
                         "a question after a tooling fix, so the two attempts are separate "
                         "artifacts rather than one overwriting the other.")
    ap.add_argument("--max-spend-usd", type=float,
                    help="REQUIRED for a live round. The worst-case ceiling for this cycle.")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and validate the complete plan; solicit nothing, write "
                         "nothing, spend nothing. Every check runs here.")
    ap.add_argument("--print-prompt", metavar="PARTY",
                    help="with --dry-run, print one party's final composed prompt")
    args = ap.parse_args(argv)

    if not args.dry_run and args.max_spend_usd is None:
        ap.error("--max-spend-usd is required for a live round. There is no default ceiling.")
    if args.dry_run and args.max_spend_usd is None:
        args.max_spend_usd = float("inf")

    CYCLES_DIR.mkdir(parents=True, exist_ok=True)
    index = len(list(CYCLES_DIR.glob("round-*.json")))
    round_id = args.round_id or f"round-{index:03d}"
    print(f"cycle {index} · selector={args.selector} · k={args.k}")

    # ---- PLAN. Pure: nothing is written, sent or spent before this returns. ----
    try:
        if not args.dry_run:
            clean_base_or_refuse(round_id)
        plan = build_plan(args, index)
    except Refusal as refusal:
        return halt(refusal.code, refusal.reason, refusal.detail, args.dry_run, round_id)

    pick = next(p for p in AS.load_queue(
        disposition=AS.disposition_from_records(REPO_ROOT / "record" / "cycles"))
        if p.pid == plan["selected"]["id"])
    rendered, anchors, _ = context_pack()
    problems = validate_plan(plan, pick, rendered, anchors, args.k)

    print(f"  selected {pick.pid} from {pick.party} "
          f"({len(pick.sponsors)} sponsor(s)); "
          f"{plan['queue_already_asked']}/{plan['queue_size']} already asked")
    print(f"    {pick.question[:150]}")
    print(f"  plan {plan['plan_sha256'][:16]}…  worst case "
          f"${plan['budget']['worst_case_usd']}")
    if not plan["budget"]["rates_verified_by_custodian"]:
        print("  NOTE: the rate table is marked UNVERIFIED. The bound is deliberately high, "
              "but it is not a price.")
    for report in plan["prompt_lint"]:
        for hit in report["recorded_in_party_words"]:
            print(f"  RECORDED  {hit['party_key']}: [{hit['defect']}] appears in the "
                  f"proposer's own {hit['slot']} — recorded, not edited")

    if problems:
        return halt(HALT_REFUSED, f"the plan failed validation ({len(problems)} problem(s))",
                    {f"problem {n}": p for n, p in enumerate(problems, 1)},
                    args.dry_run, round_id)

    if args.dry_run:
        if args.print_prompt:
            spec = next((s for s in plan["specs"] if s["party_key"] == args.print_prompt), None)
            if spec is None:
                print(f"\n  no such party in this plan: {args.print_prompt!r}")
            else:
                print("\n" + "=" * 78 + f"\n{spec['slug']}  sha256 {spec['prompt_sha256'][:16]}…\n"
                      + "=" * 78 + f"\n{spec['prompt']}")
        print(f"\n  DRY RUN — plan {plan['plan_sha256'][:16]}… validated. "
              f"Nothing solicited, nothing written, nothing spent.")
        print(f"  {len(plan['specs'])} spec(s) built and schema-valid; every prompt composed "
              f"and linted; proposer bytes verified present.")
        print(f"  would solicit k={args.k} from: {', '.join(plan['parties'])}")
        print("  would then STOP. No synthesis, no adoption, no write to main.")
        return 0

    if AS.ADOPTED is None or args.selector != AS.ADOPTED:
        return halt(HALT_REFUSED,
                    f"selector {args.selector!r} is not the adopted one ({AS.ADOPTED!r})",
                    {"why": "A live round runs only under the adopted mechanism. Use --dry-run."},
                    False, round_id)

    # ---- EXECUTE the frozen plan. Branch FIRST, before any write. ----
    try:
        git_or_refuse("checkout", "-q", "-b", f"round/{round_id}")
    except Refusal as refusal:
        return halt(refusal.code, refusal.reason, refusal.detail, False, round_id)
    print(f"  on branch round/{round_id} — every write from here lands here, not on "
          f"{BASE_BRANCH}")

    prefixes = [f"corpus/raw/{round_id}", f"corpus/artifacts/{round_id}",
                f"record/solicitations/{round_id}", f"record/cycles/",
                "corpus/MANIFEST.sha256", "docs/", "corpus/index.md",
                "tools/capture_ui/"]
    exit_code = 0
    try:
        spec_dir = REPO_ROOT / "record" / "solicitations" / round_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        (CYCLES_DIR / f"plan-{round_id}.json").write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        for spec in plan["specs"]:
            (spec_dir / f"{round_id}-{spec['party_key']}.json").write_text(
                json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        summaries, failures = {}, []
        for spec in plan["specs"]:
            print(f"  soliciting {spec['party_key']}…")
            ok, tail = solicit(spec, round_id)
            summary_path = (REPO_ROOT / "corpus" / "artifacts" / round_id /
                            f"{spec['slug']}-summary.json")
            if not ok or not summary_path.is_file():
                failures.append(f"{spec['party_key']}: {tail}")
                continue
            summaries[spec["party_key"]] = json.loads(summary_path.read_text(encoding="utf-8"))

        spent = round(sum(
            (s.get("spend", {}) or {}).get("actual_usd") or 0.0 for s in summaries.values()), 4)
        ledger = json.loads(LEDGER_FILE.read_text(encoding="utf-8")) \
            if LEDGER_FILE.is_file() else {"artifact_type": "spend_ledger", "entries": []}
        ledger["entries"].append({
            "utc": utc_now(), "round": round_id,
            "worst_case_usd": plan["budget"]["worst_case_usd"],
            "actual_usd": spent if spent else None,
            "actual_note": ("Summed from each response's usage block where the arm reported "
                            "one. Null means no arm reported usage, not zero cost.")})
        LEDGER_FILE.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

        short = [k for k, s in summaries.items()
                 if s.get("k_collected", 0) < plan["specs"][0]["k_requested"]]
        rejected = {k: s.get("failures") for k, s in summaries.items() if s.get("failures")}

        record = {"artifact_type": "round_record", "round": round_id, "cycle": index,
                  "utc": utc_now(), "selector": args.selector,
                  "selected": pick.to_json(),
                  "selected_question_sha256": pick.question_sha256,
                  "template_sha256": plan["template_sha256"],
                  "plan_sha256": plan["plan_sha256"],
                  "context_pack_sha256": plan["specs"][0]["context_pack"]["pack_sha256"],
                  "budget": plan["budget"], "actual_usd": spent if spent else None,
                  "parties": [{"party_key": k, "identity": PARTIES[k]["identity"],
                               "k": s.get("k_collected"),
                               "position": s["variance"]["position"]["modal_value"],
                               "modal_fraction": s["variance"]["position"]["modal_fraction"],
                               "entropy_bits": s["variance"]["position"]["shannon_entropy_bits"],
                               "rejected_samples": s.get("failures") or []}
                              for k, s in summaries.items()],
                  "solicitation_failures": failures,
                  "reasked_after_fix": args.round_id is not None,
                  "no_synthesis": ("Deliberately absent. A consulted party made unilateral "
                                   "synthesis by the conflicted moderator a condition of "
                                   "declining.")}
        (CYCLES_DIR / f"{round_id}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        #  EVERYTHING SOLICITED IS RECORDED AND COMMITTED FIRST, then the halt fires.
        #  A halt that discarded a party's replies because the round was awkward would
        #  be the worst defect available to this design.
        rebuilt = subprocess.run([sys.executable, "tools/build_manifest.py",
                                  "corpus/raw/", "--add"], cwd=REPO_ROOT, capture_output=True)
        rebuilt = subprocess.run([sys.executable, "tools/rebuild.py"], cwd=REPO_ROOT,
                                 capture_output=True, text=True)
        if rebuilt.returncode != 0:
            raise Refusal(HALT_REFUSED, "the build failed after solicitation",
                          {"branch": f"round/{round_id}",
                           "why": ("Nothing is committed over a red build. The material is "
                                   "preserved in the working tree on the round branch."),
                           "tail": rebuilt.stdout.strip().splitlines()[-3:]})

        note = []
        if failures:
            note.append(f"{len(failures)} party arm(s) failed")
        if short:
            note.append(f"undersampled: {', '.join(short)}")
        if rejected:
            note.append(f"schema-rejected samples from {', '.join(rejected)}")
        commit_exactly(prefixes, f"Round {round_id}: {pick.pid} from {pick.party}, "
                                 f"selector={args.selector}"
                                 + (f" [{'; '.join(note)}]" if note else ""))
        print(f"\n  recorded on branch round/{round_id} — NOT merged.")
        print("  The custodian merges. No synthesis was written and none will be.")

        if failures or short:
            exit_code = halt(HALT_UNDERSAMPLED, "a party's samples are not reportable",
                             {"failures": failures, "undersampled": short,
                              "why": ("Below k_min a reply is not a party's position. "
                                      "Truncation has twice masqueraded as a refusal here. "
                                      "Everything collected is committed above.")},
                             False, round_id)
        elif rejected:
            exit_code = halt(HALT_UNDERSAMPLED, "samples were rejected as schema-invalid",
                             {"rejected": rejected,
                              "why": "SOP §4 halts on a schema-invalid reply. Recorded above."},
                             False, round_id)
        elif category_unanimous(list(summaries.values())):
            exit_code = halt(HALT_CATEGORY_UNANIMOUS,
                             "every party's modal CATEGORY matched — a diagnostic, not agreement",
                             {"position": next(iter(summaries.values()))
                                          ["variance"]["position"]["modal_value"],
                              "why": ("Parties can share a category and answer incompatibly. "
                                      "No mechanical test for substantive agreement exists "
                                      "that does not require judging whether two answers say "
                                      "the same thing — the moderator power every party "
                                      "objected to. The round is committed; read the answers."),
                              "round_record": f"record/cycles/{round_id}.json"},
                             False, round_id)
    except Refusal as refusal:
        return halt(refusal.code, refusal.reason, refusal.detail, False, round_id)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
