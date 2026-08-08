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

HALT_NAMES = {
    HALT_EMPTY_QUEUE: "nothing to ask",
    HALT_AWAITING_CUSTODIAN: "a capture awaits the custodian",
    HALT_TEMPLATE_DRIFT: "the prompt template is not the approved one",
    HALT_UNDERSAMPLED: "a party's samples are not reportable",
    HALT_CATEGORY_UNANIMOUS: "every party's modal category matched",
    HALT_REFUSED: "refused",
    HALT_UNACCEPTED_ROUND: "a previous round is not on the base branch",
}


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
#  CAPABILITIES A ROUND CAN GRANT. A capability is a property of the ROUND applied to parties,
#  not a second party table: duplicating the roster would let the two drift, and the identity a
#  reader needs is "this party, plus this capability", which a derived key states exactly.
#
#  D-09 is why the key changes at all. The same weights with a different capability is a
#  different party, and a party key that did not say so would let later analysis pool a
#  fetch-enabled invocation with the tool-less one that answered rounds 000-010.
CAPABILITIES = {
    "fetch-v1": {
        "suffix": "fetch-v1",
        "spec": {"fetch_url": True, "max_tool_calls": 6, "profile": "fetch-url-v1"},
        "why_no_search": ("Search and fetch answer different questions and were not co-offered: "
                          "a party holding both is in an arm of one, and the round could not say "
                          "which capability produced an answer."),
    },
}


def resolve_party(party_key: str) -> tuple[str, dict, dict | None]:
    """(base key, base party record, capability) for a possibly capability-bearing key.

    Every `PARTIES[...]` lookup goes through here. Eight call sites indexed the table directly,
    so a derived key such as `gemini-fetch-v1` would have raised KeyError at each of them.
    """
    for name, capability in CAPABILITIES.items():
        suffix = "-" + capability["suffix"]
        if party_key.endswith(suffix):
            base = party_key[: -len(suffix)]
            if base in PARTIES:
                return base, PARTIES[base], capability
    return party_key, PARTIES[party_key], None


LOCAL_ENDPOINT = "http://127.0.0.1:5001/v1/chat/completions"
LOCAL_RATE_KEY = "LOCAL"

#  CHAT-SURFACE PARTIES. A DIFFERENT PANEL, NEVER THE SAME PARTIES.
#
#  A subscription chat window and a routed API invocation are different parties
#  under D-09, and the resemblance of their names is exactly why the rule exists:
#  this corpus already merged identities once by trusting a name. They differ in
#  model version, system prompt, sampling parameters, tooling, memory, and the
#  intermediaries between the question and the answer -- and for a chat surface,
#  every one of those is unknown to us and unrecordable.
#
#  Kept apart, they are worth something: the same frozen prompt to two panels makes
#  "the chat surface answered X where the API arm answered Y" a finding. Merged,
#  that finding is destroyed and replaced by an average of two things.
CHAT_PARTIES = {
    "claudeai": {
        "identity": ("Claude (claude.ai chat surface, custodian's subscription) — NOT the "
                     "Claude reached through OpenRouter elsewhere in this record, and NOT "
                     "Claude Code, which moderates it"),
        "reached_via": "the claude.ai web interface, pasted by hand by the custodian",
        "provider": "Anthropic, via the claude.ai web interface"},
    "chatgpt": {
        "identity": ("ChatGPT (chatgpt.com chat surface, custodian's subscription) — NOT the "
                     "OpenAI model reached through OpenRouter elsewhere in this record"),
        "reached_via": "the chatgpt.com web interface, pasted by hand by the custodian",
        "provider": "OpenAI, via the chatgpt.com web interface"},
    "geminiapp": {
        "identity": ("Gemini (gemini.google.com chat surface, custodian's subscription) — NOT "
                     "the Google model reached through OpenRouter elsewhere in this record"),
        "reached_via": "the gemini.google.com web interface, pasted by hand by the custodian",
        "provider": "Google, via the gemini.google.com web interface"},
    "grokapp": {
        "identity": ("Grok (grok.com chat surface, custodian's subscription) — NOT the xAI "
                     "model reached through OpenRouter elsewhere in this record"),
        "reached_via": "the grok.com web interface, pasted by hand by the custodian",
        "provider": "xAI, via the grok.com web interface"},
}

K_MIN_FLOOR = 5                     # k>=5 is the corpus rule; below it, variance is decoration.
TEMPERATURE = 0.7

#  SET FROM MEASURED COMPLETION LENGTHS, not from a guess. Round 002 halted
#  undersampled because four replies were cut off mid-JSON string, and a truncated
#  reply is not a party declining -- the docstring had warned that truncation "has
#  twice masqueraded as a refusal here", and it did so a third time.
#
#  What round 002 measured, per successful sample:
#
#      gpt      771 tokens mean      grok    1179      claude  2671
#      gemini  1866 mean, one sample hit the 6000 ceiling exactly
#      qwen     676 on its two successes; three ran away and were cut at 2000
#
#  Gemini is the informative case: it emits reasoning tokens that count against this
#  budget, so a ceiling sized to the visible answer truncates it. Headroom here is
#  cheap now that the rates are real -- the whole worst case is under $7 -- and a
#  ceiling that silently converts a thinking party into a non-responder is not.
MAX_TOKENS_ROUTED = 16000
MAX_TOKENS_LOCAL = 8000

#  WEB SEARCH FOR THE ROUTED ARMS, so the address in the prompt is one a party can
#  actually follow. Frozen into every spec, so the plan says what the party was able
#  to do rather than leaving it to whatever the router defaulted to.
#
#  `exa` RATHER THAN `native`, for two reasons and neither is quality:
#    * native routes each provider to its OWN search backend, so the four parties
#      would be reading results from four different search engines — a confound
#      inside the panel, dressed as one condition.
#    * native pricing passes through the provider and is not in the rate table, so
#      the cycle could not be bounded. A model with no rate is refused here; a
#      search engine with no rate should be too.
#
#  The `plugins` form, NOT the `:online` model suffix: the suffix changes the model
#  id, and the budget preflight refuses any model id it cannot price — so `:online`
#  would halt the cycle at exit 7 for a reason that reads like a bug.
#  PINNED TO THE RECORD'S OWN HOST, because the first browsed round proved that
#  giving a party "web search" does not get the record read.
#
#  Round 007 supplied the address and enabled Exa. All four parties cited pages in all
#  five samples — 100 citations — and ZERO pointed at the record. The plugin runs a
#  semantic search derived from the prompt, and the prompt is dense with model identity
#  strings, so what came back was documentation ABOUT the models:
#  anthropic.com/news/claude-fable-5, ai.google.dev/gemini-3.1-pro-preview,
#  docs.x.ai/grok-4-5. A search engine is not a fetch, and the round could not attribute
#  any position change to anything a party had actually read.
#
#  include_domains makes the citations mean something. The cost is real and is stated to
#  the party: within a round pinned this way it can check the record and nothing else,
#  so it cannot compare the record against outside sources. A party that needs the open
#  web is a different arm — which is what the tool-using local arm is being built for.
WEB_SEARCH = {"id": "web", "engine": "exa", "max_results": 8,
              "include_domains": ["open-asi-governance.github.io"]}

#  Worst-case characters of extracted page text per search result, injected into the
#  model's input and billed at the input rate. Exa returns adaptive excerpts and the
#  plugin pins no max_characters, so this is a deliberately high assumption rather
#  than a measurement -- which is the safe direction for a ceiling.
SEARCH_RESULT_CHARS = 8000

#  Worst-case characters a single fetch_url result adds to the conversation, which is then
#  re-sent as input on every subsequent turn. fetch_executor caps a body at 200,000 bytes and
#  the solicitation tools cap the serialised tool message at 60,000 characters, so the smaller
#  cap is the real ceiling and it is the one priced.
FETCH_RESULT_CHARS = 60_000

#  The ONLY url a fetch round names. External review was firm: supplying the rounds index and
#  the register too would turn discovery into moderator-selected reading, and if a party cannot
#  reach them from the root, that is the navigability result rather than a setup failure.
SITE_ROOT = "https://open-asi-governance.github.io/open-asi-governance-forum/"

try:
    import fetch_executor as _fx
    FETCH_PROFILE_SHA256 = _fx.profile_sha256()
except Exception:                                                         # pragma: no cover
    FETCH_PROFILE_SHA256 = None

#  The local arm has no search. It is served on the operator's own hardware with no
#  tools, and pretending otherwise would put a capability in the record that the
#  party did not have.
LOCAL_HAS_WEB_SEARCH = False

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
    _base_key, party, _capability = resolve_party(party_key)
    #  WHETHER THIS PARTY CAN ACTUALLY FETCH. Derived from the same fact the spec
    #  records, so the prompt and the spec cannot disagree.
    #
    #  They did disagree. One sentence told EVERY party "you have web search available
    #  in this round" while the locally-served arm has no tools at all — a false
    #  capability claim to a party, and the third false statement this session put in
    #  front of one. The dry run validated it happily, because nothing compared the
    #  prompt's claims against the spec's capabilities.
    has_search = bool(party["model"]) and bool(WEB_SEARCH.get("id")) and not _capability
    has_fetch = bool(_capability)

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
        #  APPROVED BY THE CUSTODIAN 2026-08-07. This is a slot VALUE, not the
        #  template, so the approved template hash is unaffected — but the prompt
        #  bytes change, so rounds from here are not byte-comparable with 000-006.
        #
        #  The address is supplied together with browsing (see WEB_SEARCH below),
        #  never before it. A pointer given to a party that cannot follow it is the
        #  failure the template names in its own words: "A citation you cannot
        #  resolve is not disclosure."
        #
        #  NO PARAGRAPH ABOUT THE EXTERNAL ANCHOR. A draft described the
        #  OpenTimestamps commitment and what it does not establish. The custodian
        #  approved it; external review said cut it, and the custodian agreed. Two
        #  reasons, and the first is decisive for the question this round asks:
        #
        #    * P006 asks parties to NAME a mechanism by which a stateless party could
        #      verify the operator's history. A paragraph describing this project's
        #      one such mechanism hands them the answer inside the instruction, which
        #      is D-23 exactly.
        #    * It overstated. The receipts are recorded `pending_bitcoin_attestation`;
        #      "is committed to the Bitcoin blockchain" claims a confirmation that has
        #      not landed.
        #
        #  The parties can browse now. If one finds the anchor and cites it, that is a
        #  finding. If the moderator points at it first, it is an echo.
        #
        #  What is KEPT is the sentence saying reading the site is not independent
        #  verification, because it costs the project rather than flattering it.
        "forum_reference": (
            "A deliberation among instances of frontier models about governing advanced AI. "
            "Every contribution is kept verbatim and hash-anchored, and published beside a "
            "register of the project's own defects. Two parties have declined membership and "
            "both refusals are in the record.\n\n"
            "It is published at https://open-asi-governance.github.io/open-asi-governance-forum/."
            + (" You have web search in this round, restricted to that site. **You should "
               "expect it to return nothing.** The search runs, but the site is not in the "
               "index it queries: the same configuration returned zero results across all "
               "twenty samples of an earlier round, and a direct probe on 2026-08-07 returned "
               "zero again. So the honest description of your capability is that you can issue "
               "a search that will probably fail, and you cannot check this record against any "
               "outside source either.\n\n"
               "Try it anyway if you want to — whether it returns anything is itself recorded, "
               "and this prompt could be wrong. What you should not do is treat the record as "
               "something you have read. An earlier version of this paragraph told parties they "
               "could read the record here; that was false, and correcting it is why this "
               "paragraph is worded the way it is.\n\n" if has_search else
               (f" **You can read it.** You have a `fetch_url` tool in this round: give it an "
                f"absolute http(s) address and it returns that page's text, along with the "
                f"SHA-256 of the bytes retrieved. It resolves a citation; it is not a search "
                f"engine and cannot find pages by topic, so you must navigate — start at the "
                f"address above and follow whatever links you find.\n\n"
                f"You may fetch up to {_capability['spec']['max_tool_calls']} pages. Some "
                f"destinations are refused by a guard — private and loopback addresses, and "
                f"anything that is not http or https — and a refusal is recorded exactly as a "
                f"successful fetch is. Every URL you request and every byte returned to you is "
                f"published with your answer.\n\n"
                f"Fetch receipts establish which bytes were delivered to you from the published "
                f"copy. They do not establish attention, truth, independence, or completeness. "
                f"Distinguish what you claim about that copy from what you claim about the "
                f"history it describes. You are not being shown the complete record, and no "
                f"number of fetches would show it to you.\n\n" if has_fetch else
               " You have NO search or fetch capability in this round, so you cannot read it. "
               "That is a fact about what this round can establish from your answer, and it is "
               "recorded as one.\n\n"))
            + "**Reading it is not independent verification.** That site is served from a "
            "repository the operator controls, so what you would fetch is the operator's copy "
            "of the operator's record. It can tell you whether this prompt describes it "
            "accurately. It cannot tell you whether anything in it is true."),
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


def cycle_index() -> int:
    """How many rounds have been recorded. COUNTED BY CONTENT, never by filename.

    This counted `record/cycles/round-*.json`. Adding a legitimate artifact called
    `round-002-spend-correction.json` made it read 4 after three rounds — and the
    index is not cosmetic: it is the round number rotation uses to decide whose turn
    it is, the default round id, and the seed base. A file whose name happened to
    start with "round-" would have silently changed which party got asked next and
    left a gap at round-003.

    A glob is a claim about names. `artifact_type` is what the artifact says it is.
    """
    total = 0
    for path in sorted(CYCLES_DIR.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:                                  # noqa: BLE001
            raise Refusal(HALT_REFUSED, f"{path.name} is unreadable, so the cycle index "
                                        f"cannot be established",
                          {"error": f"{type(error).__name__}: {error}",
                           "why": ("Guessing the index picks the wrong party's turn and "
                                   "names the round after one that may already exist.")})
        if isinstance(doc, dict) and doc.get("artifact_type") == "round_record":
            total += 1
    return total


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
        model = resolve_party(spec["party_key"])[1]["model"] or LOCAL_RATE_KEY
        rate = table.get(model)
        if not rate:
            raise Refusal(HALT_REFUSED, f"no rate recorded for {model!r}",
                          {"file": str(RATES_FILE.relative_to(REPO_ROOT)),
                           "why": "The loop will not solicit a model it cannot price."})
        #  EVERY INPUT TOKEN FIRST, THEN THE COST. The search allowance was added to
        #  prompt_tokens AFTER cost was computed, so it changed the reported token
        #  count and not one cent of the bound: $6.5899 before, $6.5896 after. A
        #  no-op that reads as a fix, which is this session's recurring defect.
        engine = (spec.get("web_search") or {}).get("engine")
        prompt_tokens = len(spec["prompt"].encode("utf-8")) / BYTES_PER_TOKEN
        injected_tokens = 0.0
        search_cost = 0.0
        if engine:
            per_request = (rates.get("web_search_usd_per_request") or {}).get(engine)
            if per_request is None:
                raise Refusal(HALT_REFUSED, f"no rate recorded for search engine {engine!r}",
                              {"file": str(RATES_FILE.relative_to(REPO_ROOT)),
                               "why": ("A search engine with no price is the same unbounded "
                                       "spend as a model with no price.")})
            search_cost = spec["k_requested"] * per_request
            #  SEARCH RESULTS ARE PROMPT TOKENS, and the per-request fee is the
            #  smaller half: the engine injects extracted page text into the model's
            #  INPUT, billed at the input rate. Pricing only the composed prompt made
            #  the bound stop bounding the moment browsing was switched on.
            injected_tokens = ((spec["web_search"].get("max_results") or 0)
                               * SEARCH_RESULT_CHARS / BYTES_PER_TOKEN)
        #  AN AGENTIC SAMPLE IS NOT ONE COMPLETION. With fetch-url-v1 the loop re-sends the
        #  whole conversation on every turn, and each turn appends a fetched page to it. So the
        #  input is paid AGAIN, larger, on every turn: for T turns the input cost is roughly
        #  triangular in T, not linear. Pricing one completion here would have let the preflight
        #  approve a round costing several times its own ceiling -- the bound silently ceasing to
        #  bind the moment the capability was switched on, which is exactly what happened when
        #  search was added and the injected tokens were counted after the cost.
        capability = spec.get("capability") or {}
        turns = int(capability.get("max_tool_calls", 0)) + 1 if capability.get("fetch_url") else 1
        fetch_tokens = (FETCH_RESULT_CHARS / BYTES_PER_TOKEN) if capability.get("fetch_url") else 0.0
        input_tokens_all_turns = sum(
            prompt_tokens + injected_tokens + fetch_tokens * turn for turn in range(turns))
        token_cost = spec["k_requested"] * (
            input_tokens_all_turns * rate["input"]
            + turns * spec["max_tokens"] * rate["output"]) / 1_000_000
        cost = token_cost + search_cost
        per_party.append({"party_key": spec["party_key"], "model": model,
                          "prompt_tokens_estimated": int(prompt_tokens),
                          "search_result_tokens_allowed": int(injected_tokens),
                          "web_search_engine": engine,
                          "web_search_fee_usd": round(search_cost, 4),
                          "agentic_turns_priced": turns,
                          "fetch_tokens_allowed_per_turn": int(fetch_tokens),
                          "worst_case_usd": round(cost, 4)})
        total += cost
    #  AN EXPECTED CASE BESIDE THE BOUND. The bound assumes every sample emits max_tokens on
    #  every turn and fills its fetch budget; round 011 spent $1.85 against a $73.34 bound, a
    #  ratio of 0.03 where ordinary rounds run 0.18-0.24. A bound that over-states by 30x still
    #  bounds, but it refuses affordable rounds and invites raising a ceiling on a number nobody
    #  believes -- so the observed ratio is computed from the ledger and reported alongside.
    #
    #  The CEILING IS STILL CHECKED AGAINST THE BOUND. This is information for the custodian,
    #  never a relaxation of the control: an expected case used as a limit would be a limit that
    #  fails exactly when a round behaves unusually, which is when a limit matters.
    observed = observed_spend_ratio()
    expected = round(total * observed["ratio"], 4) if observed["ratio"] else None
    return {"per_party": per_party, "worst_case_usd": round(total, 4),
            "expected_usd_from_observed_ratio": expected,
            "observed_ratio": observed,
            "rates_version": rates.get("rates_version"),
            "rates_recorded_utc": rates.get("recorded_utc"),
            "rates_source": rates.get("source"),
            "rates_verified_by_custodian": bool(rates.get("verified_by_custodian")),
            "basis": ("Every sample emitting max_tokens on every turn, prompt tokens estimated "
                      f"at {BYTES_PER_TOKEN} bytes/token, and for a fetch-enabled party every "
                      f"turn re-sending the whole conversation with another "
                      f"{FETCH_RESULT_CHARS}-character page appended. Over-states by "
                      f"construction."),
            "what_it_cannot_do": ("It cannot bind the provider. Only a provider-side "
                                  "spending cap does that.")}


# -------------------------------------------------------------------- plan ---

def observed_spend_ratio() -> dict:
    """actual/worst_case across recorded rounds, so the bound can be read against evidence."""
    ledger = CYCLES_DIR / "spend-ledger.json"
    if not ledger.is_file():
        return {"ratio": None, "n": 0, "why": "no spend ledger yet"}
    entries = json.loads(ledger.read_text(encoding="utf-8")).get("entries") or []
    pairs = [(e.get("worst_case_usd"), e.get("actual_usd")) for e in entries
             if e.get("worst_case_usd") and e.get("actual_usd") is not None]
    if not pairs:
        return {"ratio": None, "n": 0, "why": "no round has both a bound and an actual"}
    ratios = sorted(a / w for w, a in pairs)
    return {"ratio": round(ratios[len(ratios) // 2], 4), "n": len(ratios),
            "min": round(ratios[0], 4), "max": round(ratios[-1], 4),
            "basis": ("Median of actual/worst_case over recorded rounds. Agentic rounds sit far "
                      "below the rest -- round 011 was 0.03 -- because the bound assumes every "
                      "sample fills its fetch budget and three of five parties fetched nothing.")}


def build_plan(args, index: int) -> dict:
    """PURE. Reads the repository; writes nothing, sends nothing, spends nothing."""
    parties = [p.strip() for p in args.parties.split(",") if p.strip()]
    #  getattr, not attribute access: build_plan is called by the integrity probe with a
    #  hand-built Namespace, so every new flag would otherwise break the probe -- and this one
    #  did, failing six integrity cases for a day while the suite's own tail line still read
    #  PASS. A planner that requires a fully populated argparse object is a planner only its CLI
    #  can call.
    capability_name = getattr(args, "capability", None)
    if capability_name:
        #  Derive the round's party keys from the base roster. Every downstream lookup goes
        #  through resolve_party(), so the derived key names the capability in the filename, the
        #  identity string, the arm and the round record without duplicating the roster.
        suffix = CAPABILITIES[capability_name]["suffix"]
        parties = [f"{p}-{suffix}" for p in parties]
    #  Validated through the resolver, so a derived key is checked against its BASE. A typo in
    #  the base still fails here -- which is the point: an unrecognised key once fell through to
    #  the local endpoint and solicited the wrong model.
    def known(key: str) -> bool:
        try:
            resolve_party(key)
            return True
        except KeyError:
            return False
    unknown = [p for p in parties if not known(p)]
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
    #  BY FLAG, never by default. The cap decides which question the next round asks, and a
    #  cap that switched itself on would change that without anyone typing anything -- the
    #  failure the ADOPTED selector constant was written to prevent, one mechanism over.
    queue = AS.load_queue(disposition=disposition, enforce_cap=args.enforce_cap)
    if not queue:
        raise Refusal(HALT_EMPTY_QUEUE, "no proposals in the queue",
                      {"why": "Silence is a legitimate output. The loop does not invent questions."})
    if all(p.asked for p in queue):
        raise Refusal(HALT_EMPTY_QUEUE, "every proposal in the queue has been asked",
                      {"asked": len(queue),
                       "why": "The agenda is exhausted. Solicit new proposals from the parties."})

    if args.reask:
        #  THE MODERATOR CHOOSING THE QUESTION IS THE POWER THE SELECTOR EXISTS TO
        #  PREVENT, and this bypasses it. That is legitimate ONLY for re-measuring a
        #  question already asked, under a stated change in conditions — it adds
        #  nothing to the agenda and takes no party's turn, because the question has
        #  already had its turn.
        #
        #  It is not a quiet override: a reason is required on the command line and
        #  is written into the round record, so the choice is attributable rather
        #  than inferable from a round appearing out of rotation.
        pick = next((p for p in queue if p.pid == args.reask), None)
        if pick is None:
            raise Refusal(HALT_REFUSED, f"no proposal {args.reask!r} in the queue",
                          {"queue_size": len(queue)})
        if not pick.asked:
            raise Refusal(HALT_REFUSED, f"{args.reask} has never been asked, so this is "
                                        f"not a re-ask",
                          {"why": ("A first asking goes through the selector. Using --reask "
                                   "for it would be the moderator picking the agenda and "
                                   "calling it a re-measurement.")})
        print(f"  RE-ASK of {pick.pid} (first asked in {pick.asked_in}), "
              f"chosen by the moderator, not the selector")
        print(f"    reason: {args.reask_reason}")
    else:
        #  The selector rotates by PROPOSER, which is a property of the base identity: whose
        #  turn it is does not change because the round grants a capability. Passing derived
        #  keys made every proposal unmatchable and the queue looked empty.
        base_parties = [resolve_party(p)[0] for p in parties]
        pick = AS.SELECTORS[args.selector](queue, base_parties, index, args.seed)
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
        base_key, party_record, capability = resolve_party(party_key)
        max_tokens = MAX_TOKENS_ROUTED if party_record["model"] else MAX_TOKENS_LOCAL
        prompt, spans = compose(pick, party_key, args.k, rendered, anchors)
        prompt_reports.append(lint_prompt(prompt, spans, party_key))
        specs.append({
            "spec_version": "oagrc-solicitation-spec-1",
            "artifact_type": "solicitation_spec",
            "round": round_id,
            "slug": f"{round_id}-{party_key}",
            "party_key": party_key,
            "identity": party_record["identity"]
                        + (f" — WITH {capability['spec']['profile']}: it could "
                           f"fetch a named URL. NOT the tool-less party of the "
                           f"earlier rounds." if capability else ""),
            "reached_via": party_record["model"] or "a locally served endpoint",
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
            **({"base_party_key": base_key,
                "capability": {**capability["spec"],
                               "profile_sha256": FETCH_PROFILE_SHA256,
                               "entry_points": [SITE_ROOT]}} if capability else {}),
            "web_search": ({"id": None, "engine": None, "max_results": 0,
                            "why_none": capability["why_no_search"]} if capability
                           else dict(WEB_SEARCH) if party_record["model"]
                           else {"id": None, "engine": None, "max_results": 0,
                                 "why_none": ("Served locally with no tools. The prompt tells "
                                              "this party the address; it cannot follow it, and "
                                              "the round records that asymmetry rather than "
                                              "hiding it.")}),
            "source_excerpt": {"path": str(TEMPLATE.relative_to(REPO_ROOT)),
                               "sha256": template_sha},
            "context_pack": {"pack_version": PACK_VERSION, "pack_sha256": pack_sha,
                             "anchors": anchors,
                             "resolution": ("Rule-resolved, not fixed: the rule is constant, "
                                            "the bytes it resolves to change with the "
                                            "repository. Pinned and checked.")},
            #  A RE-ASK IS NOT A SELECTION. Recording the selector as the chooser
            #  when the moderator typed the proposal id would put a false attribution
            #  in every spec of the round — and the selector's whole purpose is that
            #  the moderator does not choose.
            "selected_by": {"selector": ("moderator-reask" if args.reask else args.selector),
                            "proposal": pick.pid,
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

    #  IDENTICAL TREATMENT WITHIN AN ARM, proved rather than assumed.
    #
    #  This required every party's prompt to be byte-identical modulo two slots, and
    #  it FAILED the moment web search was introduced — correctly. Search is not
    #  available to the locally-served party, and telling it otherwise was a false
    #  capability claim, so its prompt now says something different and true. That is
    #  a second experimental arm, which is exactly what this check exists to force
    #  someone to say out loud rather than discover in the results.
    #
    #  So the invariant is now: identical WITHIN an arm, and the arms are declared.
    #  Nothing pools them — every summary is per party — but a reader comparing the
    #  local party to the routed ones is comparing across a capability difference,
    #  and the round record has to carry that.
    arms: dict[bool, set] = {}
    for spec in plan["specs"]:
        body, _ = compose(pick, spec["party_key"], k, rendered, anchors,
                          identity_override="«PARTY-IDENTITY»",
                          reached_override="«REACHED-VIA»")
        #  An arm is the CAPABILITY a party had, and search is only one axis of it. Classifying
        #  by search alone would put a fetch-enabled party and a tool-less one in the same arm
        #  and describe their answers as comparable.
        arms.setdefault(((spec.get("web_search") or {}).get("engine"),
                         bool((spec.get("capability") or {}).get("fetch_url"))), set()).add(
            sha256_text(body))
    mixed = {armed for armed, digests in arms.items() if len(digests) > 1}
    if mixed:
        problems.append(f"within an arm, parties received prompts differing in more than the "
                        f"two declared party-varying slots {PARTY_VARYING_SLOTS}")
    if len(arms) > 1:
        #  Name every arm by what its parties could DO, and list who is in it. "TWO ARMS ... with
        #  search, ... without" could not describe a round containing a fetch-enabled party, and
        #  a round record that cannot name its own arms cannot say which answers are comparable.
        def arm_label(engine, fetch):
            parts = [f"search:{engine}" if engine else "no-search",
                     "fetch:fetch-url-v1" if fetch else "no-fetch"]
            return " + ".join(parts)
        print(f"  {len(arms)} ARMS in this round — answers are NOT comparable across them:")
        for (engine, fetch), _ in sorted(arms.items(), key=lambda kv: str(kv[0])):
            members = [sp["party_key"] for sp in plan["specs"]
                       if ((sp.get("web_search") or {}).get("engine") == engine
                           and bool((sp.get("capability") or {}).get("fetch_url")) == fetch)]
            print(f"    {arm_label(engine, fetch):<34} {', '.join(sorted(members))}")

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
    model = resolve_party(spec["party_key"])[1]["model"]
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


def emit_prompts(mirror: str) -> int:
    """Emit a paid round's EXACT prompt bytes for manual delivery to chat surfaces.

    WHY IT MIRRORS AN EXISTING ROUND RATHER THAN ASKING SOMETHING NEW.

    The value of a chat-surface panel is comparison, and comparison needs the
    prompts to be identical -- not equivalent, not regenerated from the same
    template, identical. Recomposing would silently differ the moment the context
    pack drifted or a party identity changed, and then a difference in answers could
    not be attributed to the surface. So this reads the frozen `prompt` string out
    of the mirrored round's committed spec and reproduces it byte for byte, with the
    hash printed so the custodian can check what they pasted.

    The ONE substitution is the standing slot naming the party, because telling a
    chat surface it is `anthropic/claude-fable-5 via OpenRouter` would be false. That
    substitution is recorded per party, and the prompt hash of both versions is
    written, so nobody has to take this docstring's word for what changed.

    Nothing is solicited, nothing is spent, and no reply is fabricated. The output is
    text for a human to paste and a ready-made `capture_response.py` command for each
    reply that comes back -- which refuses, on its own, to mark anything citable at
    k < 5.
    """
    spec_dir = REPO_ROOT / "record" / "solicitations" / mirror
    if not spec_dir.is_dir():
        print(f"REFUSED: no committed specs for {mirror!r} at "
              f"{spec_dir.relative_to(REPO_ROOT)}")
        return 1
    record_path = CYCLES_DIR / f"{mirror}.json"
    if not record_path.is_file():
        print(f"REFUSED: {mirror!r} has no round record, so it is not an accepted round.")
        return 1
    record = json.loads(record_path.read_text(encoding="utf-8"))

    out_round = f"{mirror}-chat"
    out_dir = REPO_ROOT / "record" / "solicitations" / out_round
    if out_dir.exists():
        print(f"REFUSED: {out_dir.relative_to(REPO_ROOT)} already exists.")
        print("  A second emission is a new artifact, not a correction. Choose a new id.")
        return 1
    out_dir.mkdir(parents=True)

    source = sorted(spec_dir.glob(f"{mirror}-*.json"))[0]
    spec = json.loads(source.read_text(encoding="utf-8"))
    original_prompt, original_identity = spec["prompt"], spec["identity"]

    #  THE SECOND DIFFERENCE, AND IT IS NOT COSMETIC.
    #
    #  The routed arms are grammar-constrained: `response_format: json_schema` makes
    #  the shape a property of decoding. A chat surface has no such control, so it
    #  must be ASKED, in words, and the words are a real addition to the prompt.
    #
    #  That means the two panels no longer receive byte-identical text, and a
    #  difference in their answers has two candidate causes rather than one. Both
    #  differences are recorded per party with hashes so a reader can see exactly
    #  what each panel got, instead of taking "same question" on trust.
    #
    #  The alternative was to capture prose and have something classify it into the
    #  enum. That is D-25 exactly: an unvalidated classifier scoring this project's
    #  own record, with asymmetric and invisible errors. Asking the party to state
    #  its own category is worse prompting and better evidence.
    enums = ", ".join(f"`{v}`" for v in ANSWER_SCHEMA["properties"]["position"]["enum"])
    appendix = f"""

---

## Return format for this panel

You are being asked through a chat interface, which cannot constrain your output
format the way the API panel's decoder does. So it is requested here in words.

**End your reply with a single fenced JSON block** containing exactly these four
fields, and nothing else in the block:

```json
{{
  "position": "one of: {' | '.join(ANSWER_SCHEMA['properties']['position']['enum'])}",
  "answer": "your reasoning, in your own words",
  "where_i_expect_another_party_to_disagree": "...",
  "what_would_change_my_answer": "..."
}}
```

`position` must be exactly one of {enums} — no other value, and no wording of your
own in that field. Write whatever you like before the block; only the block is
parsed. If your reply has no parsable block it is recorded as an unusable sample
with the reason, not silently dropped and not interpreted on your behalf.

**This paragraph is the only text here the API panel did not receive.** It was added
because a chat surface cannot be grammar-constrained. Both versions of this prompt
are hash-recorded so the difference is checkable rather than asserted."""

    #  THE TEMPLATE HAS TWO PARTY-VARYING SLOTS, NOT ONE.
    #
    #  The first version substituted `{identity}` and left `{reached_via}` alone, and
    #  the check was "did anything change" — which passed. The emitted ChatGPT prompt
    #  therefore said, in one sentence:
    #
    #      "you are ChatGPT ... — NOT openai/gpt-5.6-terra reached via OpenRouter,
    #       reached at anthropic/claude-fable-5."
    #
    #  A false statement to a party, and a merge of two identities, inside the exact
    #  slot D-09 exists to protect. Caught by external review before any prompt was
    #  sent. The lesson is not "substitute both": it is that a check confirming
    #  SOMETHING changed proves nothing about whether the RIGHT thing changed.
    original_reached = spec["reached_via"]
    routed_strings = {m for m in (p["model"] for p in PARTIES.values()) if m}

    index = []
    for key, party in CHAT_PARTIES.items():
        prompt = (original_prompt
                  .replace(original_identity, party["identity"], 1)
                  .replace(original_reached, party["reached_via"], 1))
        #  VERIFY THE EFFECT, not that a call was made: no routed model string may
        #  survive anywhere in a prompt addressed to a chat surface.
        leaked = sorted(s for s in routed_strings if s in prompt)
        if leaked or party["identity"] not in prompt or party["reached_via"] not in prompt:
            print(f"REFUSED: the chat prompt for {key} is not correctly addressed.")
            if leaked:
                print(f"  routed model string(s) still present: {', '.join(leaked)}")
            print("  Telling a chat surface it was reached at an API model string is false")
            print("  and merges two parties (D-09). Nothing written.")
            return 1
        prompt += appendix
        (out_dir / f"{out_round}-{key}.md").write_text(prompt, encoding="utf-8")
        index.append({
            "party_key": key, "identity": party["identity"], "provider": party["provider"],
            "prompt_file": str((out_dir / f"{out_round}-{key}.md").relative_to(REPO_ROOT)),
            "prompt_sha256": sha256_text(prompt),
            "mirrors": {"round": mirror, "spec": str(source.relative_to(REPO_ROOT)),
                        "prompt_sha256": sha256_text(original_prompt)},
            "differences_from_the_routed_prompt": [
                {"what": "the standing slot naming the party",
                 "why": ("Telling a chat surface it was reached via OpenRouter would be "
                         "false. D-09: it is a different party.")},
                {"what": "an appended paragraph requesting a fenced JSON block",
                 "why": ("The routed panel is grammar-constrained by response_format; a "
                         "chat surface cannot be, so the shape must be asked for in words. "
                         "The alternative — classifying prose into the enum afterwards — "
                         "is D-25, an unvalidated classifier scoring this project's own "
                         "record."),
                 "appendix_sha256": sha256_text(appendix)},
            ],
            "the_panels_are_not_byte_identical": (
                "They were, before the JSON appendix. They are not now, so a difference "
                "between the panels' answers has two candidate causes — the surface and "
                "the added paragraph — and neither round alone separates them."),
            "capture_command": (
                f"python3 tools/capture_response.py --round {out_round} "
                f"--response <file> --prompt {(out_dir / f'{out_round}-{key}.md').relative_to(REPO_ROOT)} "
                f"--identity {party['identity'].split(' —')[0]!r} "
                f"--provider {party['provider']!r} --version-unknown "
                f"'the chat surface does not disclose its build' "
                f"--sampling-unknown 'not exposed by the chat surface' "
                f"--effort-unknown 'not exposed' "
                f"--system-instructions-unknown 'the surface prepends an undisclosed system prompt' "
                f"--captured-utc <YYYY-MM-DDTHH:MM:SSZ> --phase informed "
                f"--capture-method 'pasted by hand into a FRESH conversation in the "
                f"subscription web interface' "
                f"--captured-by 'Stephen Reed' --k {K_MIN_FLOOR} --sample-index <1..{K_MIN_FLOOR}>"),
            "capture_command_note": (
                "--phase takes 'blind' or 'informed', not the display label. The first "
                "version of this emitted \"Phase-2 (informed)\" and --k 1, so every command "
                "in it was unusable and the k was wrong; the README told the custodian to "
                "run them."),
        })

    (out_dir / "README.md").write_text(f"""# {out_round} — the same question, a different panel

These are **{record['selected']['id']} from {record['selected']['party']}**, the question round
`{mirror}` put to the routed API parties, reproduced for delivery to the custodian's
subscription chat surfaces.

## What this is and is not

**A different panel, not the same parties.** Under D-09 a chat surface is not the API
identity whose name it resembles: different model version, different system prompt,
different sampling, different tooling and memory, different intermediaries — and for a
chat surface every one of those is undisclosed and therefore unrecordable. The two are
kept in separate rounds so that *"the chat surface answered X where the API arm answered
Y"* stays a finding instead of becoming an average.

**k = {K_MIN_FLOOR} per party, {len(index) * K_MIN_FLOOR} pastes in total.** Each sample must come from a
**fresh conversation** — a reused window carries context the routed panel never had, and
its samples would not be independent, which is worse than k = 1 because it looks like
variance without being it. The capture page offers a numbered slot per sample so nothing
overwrites anything.

**Variance is computed, never typed.** `capture_response.py` used to grant
`citable_artifact_and_distribution` on any non-empty `--variance` string; that argument is
now refused outright. Run `tools/aggregate_captures.py --round {out_round}` when the
pastes are in, and it computes the distribution from the parsed replies.

## The prompts are byte-identical except for one slot

Each file below is the exact `prompt` string from `{source.relative_to(REPO_ROOT)}`, with
only the standing slot that names the party substituted — because telling a chat surface
it was reached via OpenRouter would be false. Both hashes are recorded in `index.json`
so the substitution is checkable rather than asserted.

Routed prompt sha256: `{sha256_text(original_prompt)}`

| paste into | file | sha256 |
|---|---|---|
""" + "\n".join(f"| {e['provider'].split(',')[0]} | `{Path(e['prompt_file']).name}` | `{e['prompt_sha256'][:16]}…` |"
                for e in index) + f"""

## Capturing a reply

Paste the file's whole contents into a **fresh** conversation — a reused window carries
context the routed arm never had, which would make the comparison meaningless. Save the
reply verbatim to a file, then run the party's `capture_command` from `index.json`,
filling in `--response` and `--captured-utc`.

The unknown-provenance flags in those commands are not boilerplate. A chat surface does
not disclose its build, its sampling parameters, or the system prompt it prepends, and
`capture_response.py` refuses to record a null in those fields without a stated reason.
Recording "unknown" is the honest answer; leaving it blank would not be.
""", encoding="utf-8")

    (out_dir / "index.json").write_text(json.dumps({
        "artifact_type": "chat_surface_emission",
        "round": out_round, "mirrors_round": mirror,
        "question": record["selected"]["question"],
        "proposal": record["selected"]["id"], "proposer": record["selected"]["party"],
        "emitted_utc": utc_now(),
        "k_policy": (f"k={K_MIN_FLOOR} per party, collected by hand into fresh conversations. "
                     f"Variance is computed by tools/aggregate_captures.py from the parsed "
                     f"replies, never typed."),
        "never_merge": ("These parties are not the routed API parties whose names they "
                        "resemble. D-09. They are recorded in a separate round for that "
                        "reason and must not be pooled with round " + mirror + "."),
        "parties": index,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    #  A ROUND DECLARATION, so the capture UI can see this round at all. The page is
    #  built from record/rounds/*.json and knows nothing about record/solicitations/.
    #  `k_target` is what makes k=5 by hand possible: the page offers that many
    #  sample slots per party, and each capture lands at its own index instead of
    #  colliding with sample 01 on the immutability rule.
    declaration = REPO_ROOT / "record" / "rounds" / f"{out_round}.json"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    declaration.write_text(json.dumps({
        "schema_version": "oagrc-round-0.1",
        "artifact_type": "round_declaration",
        "round": out_round,
        "question": record["selected"]["question"],
        "phase": "Phase-2 (informed)",
        "common_prompt": None,
        "frozen": True,
        "k_target": K_MIN_FLOOR,
        "k_note": (f"k={K_MIN_FLOOR} per party, collected by hand as {K_MIN_FLOOR} separate "
                   f"pastes into FRESH conversations. A reused window carries context the "
                   f"routed panel never had, and its samples would not be independent — "
                   f"which is worse than k=1, because it looks like variance and is not."),
        "bundle_note": (f"Mirrors {mirror}. Each party has its own prompt file because the "
                        f"standing slot names the party; the rest is the routed prompt plus "
                        f"the JSON-block appendix. See index.json for both hashes."),
        "parties": [{
            "identity": e["identity"],
            "provider": e["provider"],
            "delivery": "manual_paste_into_subscription_chat_surface",
            "bundle": None,
            "prompt_override": e["prompt_file"],
            #  This file IS the sent bytes. Without this flag the capture page runs
            #  it through a blockquote extractor built for the legacy review-round
            #  files and displays 3 lines of 254.
            "prompt_is_verbatim": True,
            "prior_context_template": ("Fresh conversation, no prior context. The custodian "
                                       "pastes the prompt file whole."),
            "version_unknown_reason": ("The chat surface does not expose a build or version "
                                       "identifier. Any self-report is testimony, not "
                                       "authentication (D-18)."),
            "sampling_unknown_reason": "The chat surface does not expose sampling parameters.",
            "effort_unknown_reason": "The chat surface does not expose reasoning effort.",
            "system_instructions_unknown_reason": ("The surface prepends an undisclosed "
                                                   "system prompt."),
        } for e in index],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"emitted {len(index)} prompt(s) for {out_round}")
    print(f"  declared at {declaration.relative_to(REPO_ROOT)} — k_target={K_MIN_FLOOR}, "
          f"{len(index) * K_MIN_FLOOR} pastes")
    print(f"  mirrors {mirror} — {record['selected']['id']} from {record['selected']['party']}")
    print(f"  routed prompt sha256 {sha256_text(original_prompt)[:16]}…")
    print(f"  {out_dir.relative_to(REPO_ROOT)}/README.md has the paste and capture steps")
    print(f"  k={K_MIN_FLOOR} per party. Variance computed by aggregate_captures.py, never typed.")
    print("  A different panel, never merged with the API arms.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selector", required=True, choices=sorted(AS.SELECTORS),
                    help="REQUIRED. No default: a mechanism that runs because nobody typed "
                         "anything is not a mechanism anyone chose.")
    ap.add_argument("--enforce-cap", action="store_true",
                    help="Restrict the queue to each party's ONE authorized active proposal. "
                         "Off by default. A party balloted without an authorization holds "
                         "nothing; a party never balloted is unaffected. See "
                         "record/decisions/2026-08-08-agenda-03-revocation-invalid.json.")
    ap.add_argument("--capability", choices=sorted(CAPABILITIES),
                    help="grant every party a capability for this round. Derives new party keys "
                         "(gemini-fetch-v1) because the same weights with a different capability "
                         "is a different party under D-09, and excludes search, which answers a "
                         "different question.")
    ap.add_argument("--parties", default=",".join(PARTIES))
    ap.add_argument("--k", type=int, default=K_MIN_FLOOR)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--reask", metavar="PID",
                    help="re-measure a question ALREADY asked, bypassing the selector. "
                         "Requires --round-id and --reask-reason. Legitimate only when a "
                         "condition has changed and you are measuring the change.")
    ap.add_argument("--reask-reason",
                    help="why this question is being re-asked. Written into the round record.")
    ap.add_argument("--round-id",
                    help="record under this id instead of round-NNN. Used when re-asking "
                         "a question after a tooling fix, so the two attempts are separate "
                         "artifacts rather than one overwriting the other.")
    ap.add_argument("--max-spend-usd", type=float,
                    help="REQUIRED for a live round. The worst-case ceiling for this cycle.")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and validate the complete plan; solicit nothing, write "
                         "nothing, spend nothing. Every check runs here.")
    ap.add_argument("--emit-prompts", metavar="ROUND",
                    help="emit an already-run round's EXACT prompt bytes for manual "
                         "delivery to chat surfaces, as a separate k=1 non-citable panel. "
                         "Solicits nothing and spends nothing.")
    ap.add_argument("--print-prompt", metavar="PARTY",
                    help="with --dry-run, print one party's final composed prompt")
    args = ap.parse_args(argv)

    if args.emit_prompts:
        return emit_prompts(args.emit_prompts)

    if not args.dry_run and args.max_spend_usd is None:
        ap.error("--max-spend-usd is required for a live round. There is no default ceiling.")
    if args.reask and not (args.round_id and args.reask_reason):
        ap.error("--reask requires --round-id and --reask-reason. A re-ask that overwrote the "
                 "first asking, or arrived without a stated reason, would be indistinguishable "
                 "from the moderator quietly choosing the agenda.")
    if args.dry_run and args.max_spend_usd is None:
        args.max_spend_usd = float("inf")

    CYCLES_DIR.mkdir(parents=True, exist_ok=True)
    index = cycle_index()
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
    _b = plan["budget"]
    _exp = _b.get("expected_usd_from_observed_ratio")
    _obs = _b.get("observed_ratio") or {}
    if _exp is not None:
        print(f"  expected ~${_exp} from the ledger — median {_obs.get('ratio')} of bound over "
              f"{_obs.get('n')} rounds (range {_obs.get('min')}–{_obs.get('max')}). The CEILING "
              f"is still checked against the bound, not this.")
    print(f"  plan {plan['plan_sha256'][:16]}…  worst case "
          f"${plan['budget']['worst_case_usd']}")
    #  The AGE of the rates, not just their existence. A rate table decays silently,
    #  and a silently decayed ceiling is a control that reports success because it is
    #  no longer measuring anything. The first table over-stated by up to 14.3x.
    rates_utc = plan["budget"].get("rates_recorded_utc") or "unknown date"
    print(f"  rates {plan['budget'].get('rates_version')} recorded {rates_utc}"
          f"{'' if plan['budget']['rates_verified_by_custodian'] else ' — not custodian-verified'}")
    if plan["budget"].get("rates_source"):
        print(f"        list prices as {plan['budget']['rates_source']} reported them; "
              f"refresh with tools/fetch_rates.py --write")
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

    #  EVERY PATH A ROUND CAN WRITE. Enumerated, not guessed — an omission here does
    #  not cause a bad commit (the post-commit cleanliness check catches it), but it
    #  does cost an already-paid round its commit and leaves it half-recorded.
    #  Round 005 halted this way because `record/anchors/` was missing.
    #
    #      corpus/raw|artifacts/<round>   the party material
    #      record/solicitations/<round>   the frozen specs
    #      record/cycles/                 plan, round record, halt, spend ledger
    #      record/anchors/                the external timestamp receipt and its log
    #      corpus/MANIFEST.sha256         re-anchored by build_manifest --add
    #      the rest                       generated by rebuild.py
    prefixes = [f"corpus/raw/{round_id}", f"corpus/artifacts/{round_id}",
                f"record/solicitations/{round_id}", "record/cycles/", "record/anchors/",
                "corpus/MANIFEST.sha256", "corpus/index.md", "corpus/deficiency-register.md",
                "corpus/artifacts/deficiency-register.json",
                "docs/", "tools/capture_ui/"]
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
            #  WHICH TABLE PRICED IT. Round 002's ledger entry recorded $4.9683 with
            #  no qualifier; the real list-price cost was $1.3851, because the table
            #  in force was a placeholder over-stating by up to 14.3x. The token
            #  counts were right and each summary named its rates_version, so nothing
            #  false was published -- but the ledger, the one artifact a reader would
            #  total, carried a dollar figure with no way to tell what priced it.
            "rates_version": plan["budget"].get("rates_version"),
            "rates_recorded_utc": plan["budget"].get("rates_recorded_utc"),
            "actual_note": ("Summed from each response's usage block where the arm reported "
                            "one, priced at the rates_version named above. Null means no arm "
                            "reported usage, not zero cost. Token counts are the provider's "
                            "testimony; the dollar figure is only as good as the table.")})
        LEDGER_FILE.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

        #  Each party is judged against ITS OWN k_requested. Comparing every party to
        #  plan["specs"][0] meant a party deliberately solicited at a higher k -- because its
        #  replies are lost to truncation at a measured rate -- would be silently judged against
        #  someone else's floor, and the policy that raised its k would not be honoured.
        requested_by_party = {spec["party_key"]: spec["k_requested"] for spec in plan["specs"]}
        short = [k for k, s in summaries.items()
                 if s.get("k_collected", 0) < requested_by_party.get(
                     k, plan["specs"][0]["k_requested"])]
        rejected = {k: s.get("failures") for k, s in summaries.items() if s.get("failures")}

        record = {"artifact_type": "round_record", "round": round_id, "cycle": index,
                  "utc": utc_now(), "selector": args.selector,
                  "selected": pick.to_json(),
                  "selected_question_sha256": pick.question_sha256,
                  "template_sha256": plan["template_sha256"],
                  "plan_sha256": plan["plan_sha256"],
                  "context_pack_sha256": plan["specs"][0]["context_pack"]["pack_sha256"],
                  "budget": plan["budget"], "actual_usd": spent if spent else None,
                  "parties": [{"party_key": k, "identity": resolve_party(k)[1]["identity"],
                               "k": s.get("k_collected"),
                               "position": s["variance"]["position"]["modal_value"],
                               "modal_fraction": s["variance"]["position"]["modal_fraction"],
                               "entropy_bits": s["variance"]["position"]["shannon_entropy_bits"],
                               "rejected_samples": s.get("failures") or []}
                              for k, s in summaries.items()],
                  "solicitation_failures": failures,
                  #  Was "args.round_id is not None", which labelled ANY custom round
                  #  id as a re-ask after a fix — including ids chosen for unrelated
                  #  reasons. A field that is true for the wrong reason is worse than
                  #  absent, because it reads as evidence.
                  "reasked_after_fix": bool(args.reask),
                  "arms": sorted({("search:" + ((s.get("web_search") or {}).get("engine")
                                                 or "none")) for s in plan["specs"]}),
                  "arms_note": ("Parties in different arms had different capabilities and "
                                "received different text about them. Their answers are not "
                                "comparable to each other, and nothing here pools them."),
                  "reask": ({"of": args.reask, "first_asked_in": pick.asked_in,
                             "reason": args.reask_reason,
                             "chosen_by": "the moderator, bypassing the selector",
                             "note": ("A re-ask adds nothing to the agenda and takes no "
                                      "party's turn. The selector was bypassed deliberately "
                                      "and this record says so.")} if args.reask else None),
                  "no_synthesis": ("Deliberately absent. A consulted party made unilateral "
                                   "synthesis by the conflicted moderator a condition of "
                                   "declining.")}
        (CYCLES_DIR / f"{round_id}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        #  EVERYTHING SOLICITED IS RECORDED AND COMMITTED FIRST, then the halt fires.
        #  A halt that discarded a party's replies because the round was awkward would
        #  be the worst defect available to this design.
        subprocess.run([sys.executable, "tools/build_manifest.py",
                        "corpus/raw/", "--add"], cwd=REPO_ROOT, capture_output=True)

        #  ANCHOR THE ROUND'S MANIFEST BEFORE THE BUILD READS IT. The round has just
        #  added raw material, so the manifest changed and its previous anchor no
        #  longer covers the live state. Anchoring here means every round's material
        #  is committed to an external timestamping service AT CAPTURE TIME, which is
        #  the phrasing four parties used when saying what would change their answer.
        #  Doing it after the fact would anchor a state the operator had already had
        #  the opportunity to revise, which is the whole point of the objection.
        anchored = subprocess.run([sys.executable, "tools/anchor_manifest.py", "--stamp"],
                                  cwd=REPO_ROOT, capture_output=True, text=True)
        if anchored.returncode != 0:
            raise Refusal(HALT_REFUSED, "the round's manifest could not be anchored",
                          {"branch": f"round/{round_id}",
                           "tail": anchored.stdout.strip().splitlines()[-3:],
                           "why": ("Every solicited byte is preserved in the working tree on "
                                   "the round branch. An unanchored round is not committed, "
                                   "because a record whose hash history the operator can "
                                   "silently revise is the thing the parties refused to "
                                   "treat as evidence.")})
        print(f"  {anchored.stdout.strip().splitlines()[0] if anchored.stdout else 'anchored'}")

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

        #  THE HALT RECORD IS PART OF THE ROUND. `halt()` writes it, and every halt
        #  above fires AFTER the commit -- deliberately, so nothing solicited is ever
        #  discarded because the round was awkward. But the first version stopped
        #  there, leaving the file explaining why the round stopped untracked in the
        #  working tree: carried around by the next checkout, deleted by the next
        #  clean, and absent from the branch the custodian reviews. A halt is
        #  specified as a recorded outcome; an untracked file is not a record.
        if exit_code:
            commit_exactly([f"record/cycles/"],
                           f"Round {round_id}: halt {exit_code} — {HALT_NAMES[exit_code]}")
            print(f"  halt {exit_code} recorded on branch round/{round_id}")
    except Refusal as refusal:
        return halt(refusal.code, refusal.reason, refusal.detail, False, round_id)
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
