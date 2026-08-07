#!/usr/bin/env python3
"""Terminate the Codex CLI's Responses API and speak Chat Completions to TensorRT-LLM.

**This is not a convenience adapter. It is an evidentiary instrument.**

Why it exists
-------------
The record's open question (P006) asks what mechanism a *stateless* party can use to verify
the operator's history. Three rounds handed parties the record's address and none of them read
it: search is retrieval-by-resemblance and the site is not indexed. The repair is a party that
can fetch a named URL — which means giving the locally-served party an agentic harness, and the
locally-served party is the only one whose provenance can be recorded completely.

Recent Codex removed `wire_api = "chat"`, so the only remaining path into a local server is
`/v1/responses`. TensorRT-LLM 1.3.0rc23 advertises that endpoint and cannot carry an agentic
conversation over it. Verified against the running server on 2026-08-07:

    200  input: "hi"                                                        plain string
    400  input: [{"type":"message","role":"user",
                  "content":[{"type":"input_text","text":"hi"}]}]           "No user query found"
    200  input: [{"role":"user","content":"hi"}]                            EasyInputMessage
    400  input: [... {"type":"function_call", ...}]                         "Unexpected message role."
    400  prompt_cache_key / client_metadata                                 extra_forbidden
    400  role "developer"                                                   "Unexpected message role."
    400  an EasyInputMessage carrying an `id`                               union failure

Two of those are worse than rejections. `responses_utils.py`'s
`_response_output_item_to_chat_completion_message` reads `content[0]` and hardcodes
`{"role": "assistant"}`, so for a typed message item it **silently discards the item's own role
and every content part after the first**. Both were proven by effect, not merely read from the
source: a typed item carrying two `input_text` parts reached the model as the first part only,
and the model answered as though the second had never been sent. Codex's very first input item
carries two parts.

Why this shim does NOT sit on `/v1/responses`
---------------------------------------------
It would have been a smaller program. It was rejected in design review (Codex, 2026-08-07) for
a reason this record should recognise: a shim that rewrites the first turn and then hands the
conversation to a proven silent-loss path is *"a change that reads as a repair and does nothing"*
— the exact defect shape that dominated the previous session. A transformation ledger can
disclose that corruption; disclosure does not make the sample valid.

So the Responses protocol terminates **here**, and this program speaks Chat Completions upstream,
where assistant tool calls, tool names, call ids and tool results are all first-class. That was
also verified by effect before a line of this was written: the model, given a tool call and a
tool result over `/v1/chat/completions`, correctly reported the tool's name, its arguments and
its result.

The two rules this program is built around
------------------------------------------
1. **Every transformation is recorded, or the request is refused.** A shim we write is only
   better than a third-party proxy if it is observable. Each edit becomes a typed ledger
   operation with a JSON pointer into the source and the target, and a classification saying
   whether it changed what the model can see. Anything not on the translation table is a
   refusal *before the model is invoked* — never a silent pass-through and never a guess.

2. **Lossy is not the same as recordable.** Dropping a cache key is bookkeeping. Flattening a
   tool call into prose would change structured control data into untrusted natural language and
   destroy call/result correlation, so this program refuses instead. The fail-closed list is
   `REFUSE_*` below; the record-and-proceed list is `DROPPED_FIELDS`.

What this program deliberately does not claim
---------------------------------------------
The ledger establishes what was *presented* to the model, not what the model attended to. It
records the bytes this process sent upstream; the chat template's rendering of those bytes into
tokens happens inside the server and is not observable from here. And none of it speaks to the
objection every party raised unprompted: this runs on the custodian's hardware, served by the
custodian's process. Tools change what a party can check. They change nothing about who could
have altered it.

Usage
-----
    python3 tools/responses_shim.py --preflight        # capability gate only, takes no samples
    python3 tools/responses_shim.py --port 5098 --seed 1000 --temperature 0.7

Then point Codex at it (see `record/designs/qwen-tool-using-arm-scope.md`):

    codex exec -c 'model_providers.oagf.base_url="http://127.0.0.1:5098/v1"' \
               -c 'model_providers.oagf.wire_api="responses"' \
               -c 'model_provider="oagf"' --sandbox read-only ...
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

SHIM_VERSION = "0.1.0"
LEDGER_SCHEMA = "oagf-shim-ledger-0.1"

#  The canary the capability gate asks the model to call. The name is deliberately not a word
#  the model could emit by chance, so a match is evidence of the round trip and not of fluency.
CANARY_TOOL = "oagf_canary_probe"
CANARY_TOKEN = "ZEBRA-7731"

#  Finding this marker in raw content while `tool_calls` is empty is the signature of a server
#  started without `--tool_parser`, which is a different finding from a model that simply
#  declined to call anything.
TOOL_CALL_MARKER = "<tool_call>"

#  Two parsers claim `<tool_call>`, and they are NOT interchangeable. The `qwen3` parser expects
#  a JSON body; the `qwen3_coder` parser expects the XML form `<function=name><parameter=x>`.
#  This model emits the XML form. Measured 2026-08-07 over 8 canary samples at temperature 0.7
#  with distinct seeds: 8/8 emitted the XML form, `qwen3_coder` parsed 8/8, and `qwen3` parsed
#  0/8 — silently, returning an empty list without raising.
#
#  This matters more than a flag value. TensorRT-LLM's factory maps model type `qwen3_moe` to
#  the `qwen3` parser, so `--tool_parser auto` selects the parser that yields nothing here, and
#  yields it quietly: the server would start, requests would return 200, and every tool call
#  would vanish. That is the defect shape this record keeps meeting — a change that reads as a
#  repair and does nothing — so the gate below names the parser by the syntax it actually sees
#  rather than by the model's family name.
XML_CALL_MARKER = "<function="
PARSER_FOR_XML_SYNTAX = "qwen3_coder"
PARSER_FOR_JSON_SYNTAX = "qwen3"


# ---------------------------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------------------------


class Refusal(Exception):
    """A request this shim will not translate. Raised before the model is invoked.

    Carrying `rule_id` and `pointer` rather than a bare message is what lets a refusal be an
    artifact — a reader can see exactly which element of which request was unrepresentable,
    instead of a stack trace.
    """

    def __init__(self, rule_id: str, pointer: str, reason: str) -> None:
        super().__init__(f"{rule_id} at {pointer}: {reason}")
        self.rule_id = rule_id
        self.pointer = pointer
        self.reason = reason

    def as_dict(self) -> dict:
        return {"rule_id": self.rule_id, "pointer": self.pointer, "reason": self.reason}


# ---------------------------------------------------------------------------------------------
# The translation table
# ---------------------------------------------------------------------------------------------

#  Top-level Responses fields this shim knows how to carry into a Chat Completions request.
TRANSLATED_FIELDS = {
    "model", "instructions", "input", "tools", "tool_choice", "parallel_tool_calls",
    "max_output_tokens", "temperature", "top_p", "stream", "text",
}

#  Fields dropped on the way upstream, each with the classification that says what the drop cost.
#
#  `non_model_operational` — the field never reaches the model on either endpoint, so dropping it
#  changes nothing the model can see. `declared_treatment` — dropping it DOES change something,
#  and the change is part of this arm's declared treatment rather than an accident.
DROPPED_FIELDS = {
    "prompt_cache_key": ("non_model_operational", "Client cache hint; refused upstream as extra_forbidden."),
    "client_metadata": ("non_model_operational", "Client telemetry; refused upstream as extra_forbidden."),
    "store": ("non_model_operational", "This shim is stateless; no conversation is retained."),
    "include": ("non_model_operational", "Requests encrypted reasoning this server never produces."),
    "metadata": ("non_model_operational", "Caller-supplied labels; not part of the model input."),
    "user": ("non_model_operational", "Caller-supplied end-user id; not part of the model input."),
    "safety_identifier": ("non_model_operational", "Caller-supplied identifier; not part of the model input."),
    "service_tier": ("non_model_operational", "Routing hint with no local meaning."),
    "reasoning": ("declared_treatment",
                  "Chat Completions has no reasoning-effort field. Thinking behaviour is governed "
                  "by the served chat template, which is recorded as serve configuration, not here."),
    "truncation": ("declared_treatment",
                   "This shim never truncates. An over-length conversation fails rather than "
                   "silently losing its head, because undisclosed truncation is the failure this "
                   "arm exists to detect."),
}

#  Fields that abort the request. Each would make the round record wrong in a way a ledger entry
#  could not repair, so none of them is allowed to proceed with a note.
REFUSED_FIELDS = {
    "previous_response_id": "This shim is stateless; server-side conversation state would be an "
                            "unrecorded input to the model.",
    "background": "A backgrounded response cannot be tied to the sample that requested it.",
    "max_tool_calls": "Silently capping the agentic loop would change the treatment mid-round.",
    "prompt": "Server-side prompt templates are an input this record cannot observe.",
}

#  Responses roles → Chat Completions roles.
ROLE_MAP = {
    "user": "user",
    "assistant": "assistant",
    "system": "system",
    #  Upstream rejects `developer` outright ("Unexpected message role."). Mapping it to `system`
    #  is model-visible: the text still reaches the model, in the slot the chat template gives
    #  system messages. Recorded as an adaptation, not as a no-op.
    "developer": "system",
}

CONTENT_PART_TEXT_TYPES = {"input_text", "output_text", "text"}

#  How multiple content parts of one message are joined. Upstream keeps only content[0]; this
#  shim keeps all of them, and the separator is fixed and recorded so a reader can invert it.
PART_SEPARATOR = "\n\n"


# ---------------------------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class Ledger:
    """Append-only, hash-chained record of every exchange, written before it is acted on.

    Two properties matter more than the format. **Write-ahead**: an inbound request is persisted
    and fsynced before it is dispatched upstream, so a crash mid-turn leaves evidence rather than
    a gap. **Hash-chained**: each entry carries the digest of the previous one, so the order of
    events is established by the file itself and not by timestamps that a later writer could
    choose.

    Bodies live in `blobs/<sha256>.json` and entries reference them by digest, so the chain stays
    readable while the ~98 KB Codex sends per turn is still recoverable exactly.

    The spool deliberately defaults OUTSIDE the repository. Writing into the working tree while a
    round is running trips the round loop's post-commit cleanliness check and costs a paid round
    its commit; and the party under test is given the repository read-only, so the recorder must
    not be holding a pen inside it either. Ingestion into `corpus/raw/` is a separate, deliberate
    step after the run.
    """

    def __init__(self, directory: Path, run_id: str) -> None:
        self.dir = directory / run_id
        self.blobs = self.dir / "blobs"
        self.blobs.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "ledger.jsonl"
        self.run_id = run_id
        self._seq = 0
        self._prev = "0" * 64
        self._lock = threading.Lock()

    def blob(self, obj) -> str:
        """Store a body by content address and return its digest."""
        data = canonical_bytes(obj)
        digest = sha256_bytes(data)
        target = self.blobs / f"{digest}.json"
        if not target.exists():
            target.write_bytes(data)
        return digest

    def append(self, kind: str, payload: dict) -> dict:
        with self._lock:
            self._seq += 1
            entry = {
                "schema_version": LEDGER_SCHEMA,
                "shim_version": SHIM_VERSION,
                "run_id": self.run_id,
                "seq": self._seq,
                "recorded_at": time.time(),
                "kind": kind,
                "prev_entry_sha256": self._prev,
                **payload,
            }
            line = json.dumps(entry, sort_keys=True, ensure_ascii=False)
            self._prev = sha256_bytes(line.encode("utf-8"))
            entry_out = dict(entry)
            #  fsync before returning: the caller dispatches upstream on the next line, and an
            #  entry that exists only in a page cache is not a write-ahead record.
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return entry_out


class Ops:
    """The typed transformation list for a single request.

    Every edit between what Codex sent and what went upstream appends one entry here. An empty
    list would mean the request crossed unchanged; in practice it never is, and the point of the
    artifact is that a reader can say exactly why.
    """

    def __init__(self) -> None:
        self.entries: list[dict] = []

    def add(self, rule_id: str, operation: str, classification: str,
            source_pointer: str, target_pointer: str | None = None, detail: str = "") -> None:
        self.entries.append({
            "seq": len(self.entries) + 1,
            "rule_id": rule_id,
            "operation": operation,
            "classification": classification,
            "source_pointer": source_pointer,
            "target_pointer": target_pointer,
            "detail": detail,
        })

    def model_visible(self) -> list[dict]:
        return [op for op in self.entries
                if op["classification"] != "non_model_operational"]


# ---------------------------------------------------------------------------------------------
# Request translation: Responses -> Chat Completions
# ---------------------------------------------------------------------------------------------


def _text_of_content(content, pointer: str, ops: Ops, target: str) -> str:
    """Flatten a message's content into the single string Chat Completions carries.

    A plain string passes through. A list of parts is joined — *all* of them, which is the
    difference between this shim and the upstream path it replaces. A part that is not text
    (an image, say) has no faithful representation here and refuses.
    """
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        raise Refusal("R-CONTENT-TYPE-001", pointer,
                      f"content must be a string or a list of parts, got {type(content).__name__}")
    if not content:
        raise Refusal("R-CONTENT-EMPTY-001", pointer, "message has empty content")

    texts = []
    for index, part in enumerate(content):
        part_pointer = f"{pointer}/{index}"
        if isinstance(part, str):
            texts.append(part)
            continue
        if not isinstance(part, dict):
            raise Refusal("R-CONTENT-PART-001", part_pointer,
                          f"content part must be an object, got {type(part).__name__}")
        part_type = part.get("type")
        if part_type not in CONTENT_PART_TEXT_TYPES:
            raise Refusal("R-CONTENT-PART-002", part_pointer,
                          f"content part type {part_type!r} has no faithful Chat Completions "
                          f"representation; this shim refuses rather than dropping it")
        texts.append(part.get("text", ""))

    if len(texts) > 1:
        ops.add("R-PARTS-JOIN-001", "join", "approved_model_visible_adaptation",
                pointer, target,
                f"{len(texts)} content parts joined with {PART_SEPARATOR!r}. Upstream's "
                f"/v1/responses would have kept part 0 and discarded the rest silently.")
    return PART_SEPARATOR.join(texts)


def _map_role(role: str, pointer: str, ops: Ops, target: str) -> str:
    if role not in ROLE_MAP:
        raise Refusal("R-ROLE-001", pointer,
                      f"role {role!r} is not in the translation table {sorted(ROLE_MAP)}")
    mapped = ROLE_MAP[role]
    if mapped != role:
        ops.add("R-ROLE-MAP-001", "rename", "approved_model_visible_adaptation",
                pointer, target,
                f"role {role!r} -> {mapped!r}; upstream rejects {role!r} outright")
    return mapped


def translate_input(items, ops: Ops) -> list[dict]:
    """Convert the Responses `input` array into Chat Completions messages.

    Consecutive `function_call` items are merged into one assistant message carrying several
    `tool_calls`, which is how Chat Completions represents a parallel call. Ordering is
    preserved exactly: an assistant's tool calls must precede their results or the correlation
    is lost.
    """
    if isinstance(items, str):
        ops.add("R-INPUT-STRING-001", "reframe", "non_model_operational",
                "/input", "/messages/-", "bare string input framed as a single user message")
        return [{"role": "user", "content": items}]
    if not isinstance(items, list):
        raise Refusal("R-INPUT-001", "/input",
                      f"input must be a string or a list, got {type(items).__name__}")

    messages: list[dict] = []
    pending_calls: list[dict] = []

    def flush_calls() -> None:
        nonlocal pending_calls
        if pending_calls:
            messages.append({"role": "assistant", "content": "", "tool_calls": pending_calls})
            pending_calls = []

    for index, item in enumerate(items):
        pointer = f"/input/{index}"
        target = f"/messages/{len(messages)}"
        if not isinstance(item, dict):
            raise Refusal("R-ITEM-001", pointer,
                          f"input item must be an object, got {type(item).__name__}")

        item_type = item.get("type")

        #  An EasyInputMessage has no `type`. Upstream accepts it only when it carries nothing
        #  but role and content, so an `id` here would be a union failure rather than a warning.
        if item_type in (None, "message"):
            flush_calls()
            target = f"/messages/{len(messages)}"
            if "role" not in item:
                raise Refusal("R-ITEM-002", pointer, "message item has no role")
            role = _map_role(item["role"], f"{pointer}/role", ops, f"{target}/role")
            text = _text_of_content(item.get("content"), f"{pointer}/content", ops, f"{target}/content")
            if "id" in item:
                ops.add("R-ITEM-ID-001", "omit", "non_model_operational",
                        f"{pointer}/id", None,
                        "client item id; Chat Completions has no slot for it and upstream's "
                        "input union rejects the field outright")
            messages.append({"role": role, "content": text})

        elif item_type == "function_call":
            for required in ("call_id", "name", "arguments"):
                if required not in item:
                    raise Refusal("R-FUNCALL-001", pointer,
                                  f"function_call item is missing {required!r}; without it the "
                                  f"call cannot be correlated to its result")
            pending_calls.append({
                "id": item["call_id"],
                "type": "function",
                "function": {"name": item["name"], "arguments": item["arguments"]},
            })
            ops.add("R-FUNCALL-001", "reversible_frame", "approved_model_visible_adaptation",
                    pointer, f"/messages/{len(messages)}/tool_calls/-",
                    "function_call carried as an assistant tool_call with name, arguments and "
                    "call id intact. Upstream's /v1/responses converts this to "
                    "{'role': 'function'}, discarding the name and the call id, and the chat "
                    "template then rejects the role.")

        elif item_type == "function_call_output":
            flush_calls()
            for required in ("call_id", "output"):
                if required not in item:
                    raise Refusal("R-FUNOUT-001", pointer,
                                  f"function_call_output item is missing {required!r}")
            output = item["output"]
            if not isinstance(output, str):
                output = json.dumps(output, ensure_ascii=False)
                ops.add("R-FUNOUT-JSON-001", "encode", "approved_model_visible_adaptation",
                        f"{pointer}/output", f"/messages/{len(messages)}/content",
                        "non-string tool output serialised as JSON")
            messages.append({"role": "tool", "tool_call_id": item["call_id"], "content": output})

        elif item_type == "reasoning":
            #  Refused rather than dropped. This server produces no encrypted reasoning, so Codex
            #  should never replay one; if it does, the conversation contains a turn this shim
            #  cannot carry, and proceeding would silently shorten the model's own history.
            raise Refusal("R-REASONING-001", pointer,
                          "reasoning items have no Chat Completions representation. Dropping one "
                          "would remove part of the conversation the model previously produced.")
        else:
            raise Refusal("R-ITEM-TYPE-001", pointer,
                          f"input item type {item_type!r} is not in the translation table")

    flush_calls()
    return messages


def translate_tools(tools, ops: Ops) -> list[dict]:
    """Convert Responses tool declarations into Chat Completions tool declarations.

    Only flat function tools survive. `namespace` and `web_search` are refused on purpose:
    upstream's schema *accepts* both, and schema acceptance is not evidence of execution. A
    party that believes it searched and did not is precisely the failure this arm exists to
    expose, so an unbacked tool must never be offered to the model.
    """
    if tools is None:
        return []
    if not isinstance(tools, list):
        raise Refusal("R-TOOLS-001", "/tools",
                      f"tools must be a list, got {type(tools).__name__}")

    out = []
    seen: dict[str, str] = {}

    def emit(function: dict, pointer: str, rule: str, detail: str) -> None:
        if function["name"] in seen:
            raise Refusal("R-TOOL-COLLIDE-001", pointer,
                          f"tool name {function['name']!r} is already taken by "
                          f"{seen[function['name']]}. Two tools the model cannot tell apart is a "
                          f"worse failure than refusing the request.")
        seen[function["name"]] = pointer
        out.append({"type": "function", "function": function})
        ops.add(rule, "reversible_frame", "approved_model_visible_adaptation",
                pointer, f"/tools/{len(out) - 1}", detail)

    def as_function(tool: dict, pointer: str, name: str) -> dict:
        if "name" not in tool:
            raise Refusal("R-TOOL-002", pointer, "function tool has no name")
        function = {"name": name, "parameters": tool.get("parameters") or {}}
        if tool.get("description"):
            function["description"] = tool["description"]
        if tool.get("strict") is not None:
            function["strict"] = tool["strict"]
        return function

    for index, tool in enumerate(tools):
        pointer = f"/tools/{index}"
        if not isinstance(tool, dict):
            raise Refusal("R-TOOL-001", pointer, "tool must be an object")
        tool_type = tool.get("type")

        if tool_type == "function":
            emit(as_function(tool, pointer, tool["name"]), pointer, "R-TOOL-FLAT-001",
                 "Responses flat function tool reframed as a Chat Completions function tool; "
                 "name, description and parameter schema unchanged")

        elif tool_type == "namespace":
            #  Flattening a namespace changes the names the model sees, so it was refused
            #  outright at first. It is permitted now because it turned out to be REQUIRED: MCP
            #  is the only way to hand this party a tool Codex will actually execute, and Codex
            #  emits MCP tools exclusively as a namespace — neither `features.tool_namespace`
            #  nor `features.non_prefixed_mcp_tool_names` unwraps it (both tried, 2026-08-07).
            #  Without this the arm has no browsing capability at all, which is the one thing it
            #  exists for.
            #
            #  The conditions the design review set are met: the mapping is deterministic and
            #  reversible (`<namespace>__<inner>`, which reconstructs Codex's own legacy flat
            #  name), collisions refuse rather than silently shadow, and every flattening is
            #  recorded with both endpoints. It is still model-visible and still recorded as
            #  such — a namespace is not free, it is merely necessary.
            namespace = tool.get("name")
            if not namespace:
                raise Refusal("R-TOOL-NAMESPACE-002", pointer, "namespace tool has no name")
            inner_tools = tool.get("tools") or []
            if not inner_tools:
                raise Refusal("R-TOOL-NAMESPACE-003", pointer,
                              f"namespace {namespace!r} declares no tools; offering an empty "
                              f"namespace tells the model it has a capability it does not have")
            for inner_index, inner in enumerate(inner_tools):
                inner_pointer = f"{pointer}/tools/{inner_index}"
                if inner.get("type") != "function":
                    raise Refusal("R-TOOL-NAMESPACE-004", inner_pointer,
                                  f"namespace member type {inner.get('type')!r} is not a flat "
                                  f"function and has no Chat Completions representation")
                #  The flat name is the namespace member's OWN name, not a composite. The
                #  composite `<namespace>__<inner>` was tried first because it reconstructs
                #  Codex's legacy flat convention, and Codex's router rejected the call it
                #  produced outright: `error=unsupported call: mcp__oagf_fetch__fetch_url`.
                #  Determined by effect, not from the schema — which is the whole reason the
                #  design review required an effect test before permitting any flattening.
                #
                #  Using the inner name unchanged also happens to be the smaller transformation:
                #  the model sees exactly the name the MCP server declared. What is lost is the
                #  namespace grouping, and `emit()` refuses on any collision, so two namespaces
                #  offering the same member name fail loudly instead of shadowing each other.
                flat = inner["name"]
                emit(as_function(inner, inner_pointer, flat), inner_pointer,
                     "R-TOOL-NAMESPACE-FLATTEN-001",
                     f"namespace member {namespace!r}/{inner['name']!r} flattened to {flat!r}; "
                     f"the model sees the composite name, and a call to it is returned to the "
                     f"client under that same name. Schema and description unchanged.")

        elif tool_type in ("web_search", "web_search_preview"):
            raise Refusal("R-TOOL-WEBSEARCH-001", pointer,
                          "the hosted web_search tool has no executor behind this endpoint. "
                          "Offering it would let the party believe it searched when nothing ran. "
                          "Supply browsing as an explicit function tool with recorded receipts.")
        else:
            raise Refusal("R-TOOL-TYPE-001", pointer,
                          f"tool type {tool_type!r} is not in the translation table")
    return out


def merge_leading_system(messages: list[dict], ops: Ops) -> list[dict]:
    """Collapse the leading run of system messages into the single one upstream permits.

    The chat template accepts exactly one system message and it must come first. Its error text
    — *"System message must be at the beginning"* — describes the position rule and not the
    arity rule that actually fires, which is why this is worth stating here: two system messages
    both at the beginning are refused just as firmly as one in the middle.

    Codex produces two by construction: the top-level `instructions`, and its `developer` item.
    Merging them preserves both texts and their order, so nothing the model would have seen is
    lost — but it is model-visible and it is recorded as such.

    A system message arriving *after* a user turn is refused rather than hoisted. Moving text to
    a different point in the conversation would change what the model sees, and dropping it
    would remove instructions; neither is a transformation a ledger entry could make honest.
    """
    leading: list[str] = []
    index = 0
    while index < len(messages) and messages[index]["role"] == "system":
        leading.append(messages[index]["content"])
        index += 1

    for later, message in enumerate(messages[index:], start=index):
        if message["role"] == "system":
            raise Refusal("R-SYSTEM-POSITION-001", f"/messages/{later}",
                          "a system message follows a non-system turn. Upstream accepts only one "
                          "system message, at the front; hoisting this one would reorder the "
                          "conversation and dropping it would remove instructions.")

    if len(leading) <= 1:
        return messages

    ops.add("R-SYSTEM-MERGE-001", "join", "approved_model_visible_adaptation",
            "/messages/0..%d" % (index - 1), "/messages/0",
            f"{len(leading)} leading system messages merged with {PART_SEPARATOR!r}; the chat "
            f"template accepts exactly one. Text and order are preserved, but the model sees "
            f"one system turn where the client sent {len(leading)}.")
    return [{"role": "system", "content": PART_SEPARATOR.join(leading)}] + messages[index:]


def translate_request(body: dict, ops: Ops, *, model: str | None = None,
                      temperature: float | None = None, seed: int | None = None) -> dict:
    """Translate a whole Responses request, refusing anything not on the table."""
    if not isinstance(body, dict):
        raise Refusal("R-BODY-001", "", "request body must be a JSON object")

    for field in body:
        if field in REFUSED_FIELDS:
            raise Refusal("R-FIELD-REFUSED-001", f"/{field}", REFUSED_FIELDS[field])
        if field not in TRANSLATED_FIELDS and field not in DROPPED_FIELDS:
            raise Refusal("R-FIELD-UNKNOWN-001", f"/{field}",
                          "field is not in the translation table. An unrecognised field may or "
                          "may not change what the model sees, and this shim will not guess.")

    for field, (classification, detail) in DROPPED_FIELDS.items():
        if field in body:
            ops.add(f"R-DROP-{field.upper().replace('_', '-')}", "omit", classification,
                    f"/{field}", None, detail)

    messages: list[dict] = []
    if body.get("instructions"):
        messages.append({"role": "system", "content": body["instructions"]})
        ops.add("R-INSTRUCTIONS-001", "reframe", "approved_model_visible_adaptation",
                "/instructions", "/messages/0",
                "top-level instructions carried as the leading system message, which is how the "
                "upstream Responses handler places them as well")
    messages.extend(translate_input(body.get("input", []), ops))
    messages = merge_leading_system(messages, ops)

    chat: dict = {
        "model": model or body.get("model"),
        "messages": messages,
        "stream": False,
    }
    ops.add("R-UPSTREAM-NONSTREAM-001", "reframe", "non_model_operational",
            "/stream", "/stream",
            "upstream is called without streaming so the ledger holds one exact, complete "
            "response object per turn; the Responses event stream back to the client is "
            "synthesised from it")

    tools = translate_tools(body.get("tools"), ops)
    if tools:
        chat["tools"] = tools
        #  `tool_choice` without `tools` is a 400 upstream, so it is only ever sent alongside them.
        if "tool_choice" in body:
            chat["tool_choice"] = body["tool_choice"]

    #  Upstream's Chat Completions model refuses `parallel_tool_calls` as extra_forbidden, so the
    #  client's request for one-call-at-a-time cannot be enforced at the server. It is dropped and
    #  declared rather than quietly forwarded into a field that would 400 the whole turn. Nothing
    #  is lost from the conversation — call/result correlation is by call id, not by arity — but
    #  the round record must not claim a constraint that was never applied.
    if "parallel_tool_calls" in body:
        ops.add("R-PARALLEL-UNENFORCEABLE-001", "omit", "declared_treatment",
                "/parallel_tool_calls", None,
                f"client asked for parallel_tool_calls={body['parallel_tool_calls']}; upstream "
                f"refuses the field (extra_forbidden), so the constraint is NOT enforced and the "
                f"model may emit several calls in one turn")

    if "max_output_tokens" in body:
        chat["max_tokens"] = body["max_output_tokens"]
        ops.add("R-MAXTOK-001", "rename", "non_model_operational",
                "/max_output_tokens", "/max_tokens", "same meaning, different field name")
    if "top_p" in body:
        chat["top_p"] = body["top_p"]

    #  Sampling discipline is the shim's, not the client's. Codex sends no temperature and no
    #  seed; the arm's standard is k >= 5 at temperature > 0 with distinct seeds, and a
    #  server-default temperature would make "variance" mean nothing. Both are recorded as
    #  declared treatment with their exact values so the round record can state them.
    if temperature is not None:
        chat["temperature"] = temperature
        ops.add("R-TEMP-INJECT-001", "inject", "declared_treatment",
                None, "/temperature",
                f"temperature={temperature} supplied by the shim; the client sent none, and "
                f"sampling variance is the arm's measurement")
    elif "temperature" in body:
        chat["temperature"] = body["temperature"]

    if seed is not None:
        chat["seed"] = seed
        ops.add("R-SEED-INJECT-001", "inject", "declared_treatment",
                None, "/seed", f"seed={seed} supplied by the shim, one distinct seed per sample")

    text_format = (body.get("text") or {}).get("format")
    if text_format:
        format_type = text_format.get("type")
        if format_type == "text":
            ops.add("R-TEXT-FORMAT-001", "omit", "non_model_operational",
                    "/text/format", None, "plain-text format is the Chat Completions default")
        elif format_type == "json_schema":
            chat["response_format"] = {"type": "json_schema", "json_schema": {
                "name": text_format.get("name", "response"),
                "schema": text_format.get("schema") or text_format.get("json_schema"),
                "strict": text_format.get("strict", True),
            }}
            ops.add("R-TEXT-SCHEMA-001", "reframe", "approved_model_visible_adaptation",
                    "/text/format", "/response_format",
                    "structured-output request carried as a Chat Completions json_schema")
        else:
            raise Refusal("R-TEXT-FORMAT-002", "/text/format",
                          f"output format {format_type!r} is not in the translation table")

    return chat


# ---------------------------------------------------------------------------------------------
# Response translation: Chat Completions -> Responses
# ---------------------------------------------------------------------------------------------


#  The served model's chat template pre-injects `<think>\n`, so a reply carries the CLOSING tag
#  with no opening one. Splitting on the closing tag alone is therefore correct here, and the
#  opening tag is handled only because a template change would otherwise silently prepend it to
#  the answer.
REASONING_START = "<think>"
REASONING_END = "</think>"


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def split_reasoning(message: dict, finish_reason: str | None, ops: Ops) -> tuple[str, str]:
    """Separate the model's chain of thought from its answer. Returns (answer, reasoning).

    This is done HERE rather than at the server on purpose. TensorRT-LLM's `--reasoning_parser`
    is server-wide, and the only parser that handles this template (`qwen3_5`, which assumes
    generation begins inside the reasoning block) breaks every request that sets
    `enable_thinking: false` — it returns the whole reply as `reasoning_content` and leaves
    `content` empty. That host serves another consumer which runs thinking-off, so the split
    cannot live at the server without breaking it. Filed upstream; until it lands, the consumer
    that wants the split does the split.

    Doing it client-side is also the better arrangement for this record: the transformation
    becomes a ledger entry with byte counts, where a server-side split would be invisible.

    If the server ever does supply `reasoning_content`, that is used instead of splitting — the
    two must not both run.
    """
    text = message.get("content") or ""

    served = message.get("reasoning_content")
    if served:
        ops.add("R-REASONING-SERVED-001", "passthrough", "non_model_operational",
                "/choices/0/message/reasoning_content", None,
                f"server supplied a {len(served)}-byte reasoning split; the shim did not split")
        return text, served

    if REASONING_END in text:
        reasoning, _, answer = text.partition(REASONING_END)
        reasoning = reasoning.replace(REASONING_START, "", 1).strip()
        ops.add("R-REASONING-SPLIT-001", "split", "approved_model_visible_adaptation",
                "/choices/0/message/content", "/output/-/content/0/text",
                f"chain of thought separated from the answer on {REASONING_END!r}: "
                f"{len(reasoning)} bytes of reasoning removed, {len(answer.strip())} bytes of "
                f"answer kept. The full unsplit reply is preserved verbatim in this turn's "
                f"upstream_response blob.")
        return answer.strip(), reasoning

    if finish_reason == "length":
        #  The reasoning block never closed, so the model never reached an answer. Returning the
        #  thinking as though it were one would put a statement in the record that the party
        #  never made — the exact failure this arm exists to detect. The text is returned
        #  unchanged and the turn is already reported `incomplete`; this records why.
        ops.add("R-REASONING-UNCLOSED-001", "flag", "declared_treatment",
                "/choices/0/message/content", None,
                f"reply hit max_tokens with no {REASONING_END!r}: the reasoning block never "
                f"closed and no answer was produced. The {len(text)} bytes returned are chain "
                f"of thought, NOT an answer, and must not be recorded as one.")
        return text, ""

    #  No marker and a clean finish: thinking was off for this request. Nothing to split.
    return text, ""


def build_output_items(choice: dict, ops: Ops, reasoning_out: list | None = None) -> list[dict]:
    """Build Responses output items from one Chat Completions choice.

    Tool calls become `function_call` items with their ids intact, because the id is what lets
    the client's next turn correlate a result to a call. Text becomes a `message` item.
    """
    message = choice.get("message") or {}
    items: list[dict] = []

    for index, call in enumerate(message.get("tool_calls") or []):
        function = call.get("function") or {}
        items.append({
            "id": _new_id("fc"),
            "type": "function_call",
            "status": "completed",
            "call_id": call.get("id") or _new_id("call"),
            "name": function.get("name"),
            "arguments": function.get("arguments") or "{}",
        })
        ops.add("R-OUT-FUNCALL-001", "reversible_frame", "approved_model_visible_adaptation",
                f"/choices/0/message/tool_calls/{index}", f"/output/{len(items) - 1}",
                "parsed tool call returned as a Responses function_call with its id preserved")

    #  The answer goes to the client; the reasoning is handed back to the caller for the ledger
    #  rather than into the output, because Codex would replay any reasoning item on the next
    #  turn and this shim refuses those (there is no faithful Chat Completions slot for one).
    text, reasoning = split_reasoning(message, choice.get("finish_reason"), ops)
    if reasoning_out is not None and reasoning:
        reasoning_out.append(reasoning)

    if text:
        items.append({
            "id": _new_id("msg"),
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": text, "annotations": []}],
        })
    return items


def build_response_object(chat_response: dict, request_body: dict, items: list[dict],
                          status: str, upstream_request: dict | None = None) -> dict:
    """Assemble the Responses object returned to the client.

    `temperature` and `seed` are reported from the request that was actually sent upstream, not
    from the one the client sent. The client sends neither; the shim injects both. A response
    object saying `temperature: null` while 0.7 was in force would be a false statement about the
    sample in the one artifact most likely to be quoted.
    """
    usage = chat_response.get("usage") or {}
    upstream_request = upstream_request or {}
    return {
        "id": _new_id("resp"),
        "object": "response",
        "created_at": int(time.time()),
        "status": status,
        "error": None,
        "incomplete_details": None,
        "instructions": request_body.get("instructions"),
        "model": chat_response.get("model") or request_body.get("model"),
        "output": items,
        "parallel_tool_calls": request_body.get("parallel_tool_calls", False),
        "tool_choice": request_body.get("tool_choice", "auto"),
        "tools": request_body.get("tools") or [],
        "temperature": upstream_request.get("temperature"),
        "seed": upstream_request.get("seed"),
        "top_p": upstream_request.get("top_p", request_body.get("top_p")),
        "store": False,
        "text": request_body.get("text") or {"format": {"type": "text"}},
        "usage": {
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        },
        "metadata": {},
    }


def sse_events(response_object: dict) -> list[tuple[str, dict]]:
    """The Responses event sequence a streaming client expects, synthesised from one reply.

    Emitted in full rather than reduced to `response.completed`, because a client that renders
    incrementally will otherwise show nothing and a client that waits on item lifecycle events
    will hang. The sequence numbers are contiguous by construction.
    """
    events: list[tuple[str, dict]] = []
    seq = 0

    def emit(event_type: str, payload: dict) -> None:
        nonlocal seq
        data = {"type": event_type, "sequence_number": seq, **payload}
        events.append((event_type, data))
        seq += 1

    skeleton = dict(response_object)
    skeleton["status"] = "in_progress"
    skeleton["output"] = []
    emit("response.created", {"response": skeleton})
    emit("response.in_progress", {"response": skeleton})

    for output_index, item in enumerate(response_object["output"]):
        added = dict(item)
        if item["type"] == "message":
            added["content"] = []
        else:
            added["arguments"] = ""
        emit("response.output_item.added", {"output_index": output_index, "item": added})

        if item["type"] == "message":
            part = item["content"][0]
            emit("response.content_part.added", {
                "item_id": item["id"], "output_index": output_index, "content_index": 0,
                "part": {"type": "output_text", "text": "", "annotations": []}})
            emit("response.output_text.delta", {
                "item_id": item["id"], "output_index": output_index, "content_index": 0,
                "delta": part["text"], "logprobs": []})
            emit("response.output_text.done", {
                "item_id": item["id"], "output_index": output_index, "content_index": 0,
                "text": part["text"], "logprobs": []})
            emit("response.content_part.done", {
                "item_id": item["id"], "output_index": output_index, "content_index": 0,
                "part": part})
        else:
            emit("response.function_call_arguments.delta", {
                "item_id": item["id"], "output_index": output_index,
                "delta": item["arguments"]})
            emit("response.function_call_arguments.done", {
                "item_id": item["id"], "output_index": output_index,
                "arguments": item["arguments"]})

        emit("response.output_item.done", {"output_index": output_index, "item": item})

    emit("response.completed", {"response": response_object})
    return events


def format_sse(event_type: str, data: dict) -> bytes:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


# ---------------------------------------------------------------------------------------------
# Upstream
# ---------------------------------------------------------------------------------------------


def call_upstream(base_url: str, body: dict, timeout: int) -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


# ---------------------------------------------------------------------------------------------
# The capability gate
# ---------------------------------------------------------------------------------------------


def preflight(base_url: str, model: str, timeout: int) -> dict:
    """Establish that a tool call actually round-trips, before any sample is taken.

    The server this was written against runs with no `--tool_parser`, so the model's tool syntax
    is never parsed out of its output and `tool_calls` is always empty. Nothing about that is
    visible from the request side: the request succeeds, the model discusses calling the tool in
    prose, and an arm that only checked HTTP status would record a tool-using round in which no
    tool was ever called.

    So the gate asks for a specific call with a specific argument and accepts only a structured
    `tool_calls` entry. When it fails it distinguishes the two causes, because they have
    different remedies: raw output containing `<tool_call>` means the parser is absent
    (restart with `--tool_parser qwen3`); raw output without it means the model declined.
    """
    tool = {"type": "function", "function": {
        "name": CANARY_TOOL,
        "description": "Report the canary token. Call this immediately and do not answer in prose.",
        "parameters": {"type": "object",
                       "properties": {"token": {"type": "string"}},
                       "required": ["token"]}}}
    body = {
        "model": model,
        "messages": [{"role": "user",
                      "content": f"Call the {CANARY_TOOL} tool exactly once with token set to "
                                 f"{CANARY_TOKEN}. Do not answer in prose."}],
        "tools": [tool],
        "tool_choice": "auto",
        "max_tokens": 1024,
        "temperature": 0,
        "stream": False,
    }
    result: dict = {"gate": "tool_call_round_trip", "canary_tool": CANARY_TOOL,
                    "canary_token": CANARY_TOKEN, "passed": False}
    try:
        response = call_upstream(base_url, body, timeout)
    except urllib.error.HTTPError as error:
        result["diagnosis"] = "upstream_error"
        result["detail"] = f"HTTP {error.code}: {error.read().decode('utf-8', 'replace')[:400]}"
        return result
    except Exception as error:                                            # noqa: BLE001
        result["diagnosis"] = "upstream_unreachable"
        result["detail"] = f"{type(error).__name__}: {error}"
        return result

    message = (response.get("choices") or [{}])[0].get("message") or {}
    calls = message.get("tool_calls") or []
    raw = message.get("content") or ""
    result["raw_content_excerpt"] = raw[:600]
    result["finish_reason"] = (response.get("choices") or [{}])[0].get("finish_reason")

    if calls:
        call = calls[0]
        name = (call.get("function") or {}).get("name")
        arguments = (call.get("function") or {}).get("arguments") or ""
        result["observed_call"] = {"name": name, "arguments": arguments,
                                   "id": call.get("id")}
        if name != CANARY_TOOL:
            result["diagnosis"] = "wrong_tool_called"
            return result
        if CANARY_TOKEN not in arguments:
            result["diagnosis"] = "arguments_not_transmitted"
            return result
        result["passed"] = True
        result["diagnosis"] = "tool_calls_parsed_and_correlated"
        return result

    if TOOL_CALL_MARKER not in raw and CANARY_TOOL in raw:
        #  The tool's name appears but no call markers do. That is prose *about* calling the
        #  tool, which is not a call, and naming a parser here would be a guess dressed as a
        #  diagnosis — this branch once reported "json" for exactly such a reply.
        result["diagnosis"] = "call_like_prose_without_markers"
        result["detail"] = ("The reply names the tool but contains no tool-call markers, so there "
                            "is nothing for any parser to parse. This is a model-behaviour "
                            "result; no parser choice would change it.")
        return result

    if TOOL_CALL_MARKER in raw:
        #  Name the parser from the syntax observed, not from the model's family. Getting this
        #  wrong produces a server that starts, answers 200, and parses nothing.
        syntax = "xml" if XML_CALL_MARKER in raw else "json"
        parser = PARSER_FOR_XML_SYNTAX if syntax == "xml" else PARSER_FOR_JSON_SYNTAX
        result["diagnosis"] = "tool_parser_absent"
        result["observed_call_syntax"] = syntax
        result["required_tool_parser"] = parser
        result["detail"] = (
            f"The model emitted a tool call and the server returned it as prose: `tool_calls` is "
            f"empty while the raw content carries the call. The server is running without "
            f"`--tool_parser`. The observed syntax is {syntax}, so the matching parser is "
            f"`{parser}` — note that the other parser accepts this text and returns no calls "
            f"without raising, so choosing it would look like a fix and change nothing. Until "
            f"the server is restarted with `--tool_parser {parser}`, no agentic sample from this "
            f"arm means what it appears to mean.")
        return result

    result["diagnosis"] = "model_did_not_call"
    result["detail"] = ("No tool call in either the parsed field or the raw content. This is a "
                        "model-behaviour result, not a plumbing result.")
    return result


# ---------------------------------------------------------------------------------------------
# HTTP surface
# ---------------------------------------------------------------------------------------------


class ShimServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_handler(config: dict, ledger: Ledger):

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = f"oagf-responses-shim/{SHIM_VERSION}"

        def log_message(self, fmt, *args):                                # noqa: A003
            sys.stderr.write(f"  {self.address_string()} {fmt % args}\n")

        def _send_json(self, status: int, payload: dict) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):                                                 # noqa: N802
            #  Passed through verbatim, including the shape Codex's model-listing client cannot
            #  decode. Synthesising a reply it likes would be inventing a fact about the server.
            target = config["base_url"].rstrip("/").rsplit("/v1", 1)[0] + self.path
            try:
                with urllib.request.urlopen(target, timeout=15) as response:
                    payload, status = response.read(), response.status
            except urllib.error.HTTPError as error:
                payload, status = error.read(), error.code
            except Exception as error:                                    # noqa: BLE001
                payload, status = json.dumps({"shim_error": str(error)}).encode(), 502
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self):                                                # noqa: N802
            if not self.path.rstrip("/").endswith("/responses"):
                self._send_json(404, {"error": f"shim serves /v1/responses only, not {self.path}"})
                return

            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            try:
                body = json.loads(raw)
            except Exception as error:                                    # noqa: BLE001
                self._send_json(400, {"error": f"unparseable request body: {error}"})
                return

            turn = uuid.uuid4().hex[:12]
            inbound_digest = ledger.blob(body)
            #  Write-ahead: the inbound request is on disk and fsynced before anything is sent
            #  upstream, so a crash leaves the request that caused it.
            ledger.append("client_request", {
                "turn_id": turn, "path": self.path,
                "client_headers": {k: ("<redacted>" if k.lower() == "authorization" else v)
                                   for k, v in self.headers.items()},
                "body_sha256": inbound_digest, "body_bytes": len(raw)})

            ops = Ops()
            try:
                chat_body = translate_request(
                    body, ops, model=config.get("model"),
                    temperature=config.get("temperature"), seed=config.get("seed"))
            except Refusal as refusal:
                ledger.append("refusal", {
                    "turn_id": turn, "refusal": refusal.as_dict(),
                    "transformations": ops.entries, "client_request_sha256": inbound_digest})
                sys.stderr.write(f"  REFUSED {refusal}\n")
                self._send_json(400, {"object": "error", "code": 400,
                                      "message": f"shim refused to translate: {refusal}",
                                      "shim_refusal": refusal.as_dict()})
                return

            upstream_digest = ledger.blob(chat_body)
            ledger.append("upstream_request", {
                "turn_id": turn, "transformations": ops.entries,
                "model_visible_transformations": len(ops.model_visible()),
                "client_request_sha256": inbound_digest,
                "upstream_request_sha256": upstream_digest,
                "upstream_url": config["base_url"].rstrip("/") + "/chat/completions"})

            started = time.time()
            try:
                chat_response = call_upstream(config["base_url"], chat_body, config["timeout"])
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", "replace")[:4000]
                ledger.append("upstream_error", {
                    "turn_id": turn, "status": error.code, "detail": detail,
                    "upstream_request_sha256": upstream_digest})
                self._send_json(502, {"object": "error", "code": 502,
                                      "message": f"upstream HTTP {error.code}: {detail[:300]}"})
                return
            except Exception as error:                                    # noqa: BLE001
                ledger.append("upstream_error", {
                    "turn_id": turn, "status": None,
                    "detail": f"{type(error).__name__}: {error}",
                    "upstream_request_sha256": upstream_digest})
                self._send_json(502, {"object": "error", "code": 502,
                                      "message": f"upstream unreachable: {error}"})
                return

            response_digest = ledger.blob(chat_response)
            choice = (chat_response.get("choices") or [{}])[0]
            reasoning_parts: list[str] = []
            items = build_output_items(choice, ops, reasoning_parts)
            status = "incomplete" if choice.get("finish_reason") == "length" else "completed"
            response_object = build_response_object(chat_response, body, items, status, chat_body)
            returned_digest = ledger.blob(response_object)

            ledger.append("upstream_response", {
                "turn_id": turn,
                "upstream_request_sha256": upstream_digest,
                "upstream_response_sha256": response_digest,
                "returned_response_sha256": returned_digest,
                "transformations": ops.entries,
                "finish_reason": choice.get("finish_reason"),
                "tool_calls_parsed": len(choice.get("message", {}).get("tool_calls") or []),
                #  Recorded as its own field so a reader can ask "what did the party think, as
                #  distinct from what it said" without re-deriving the split from the blob.
                "reasoning_sha256": (ledger.blob({"reasoning": reasoning_parts})
                                     if reasoning_parts else None),
                "reasoning_bytes": sum(len(r) for r in reasoning_parts),
                "usage": chat_response.get("usage"),
                "latency_seconds": round(time.time() - started, 3)})

            if body.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                for event_type, data in sse_events(response_object):
                    self.wfile.write(format_sse(event_type, data))
                self.wfile.flush()
                self.close_connection = True
            else:
                self._send_json(200, response_object)

    return Handler


# ---------------------------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=5098)
    parser.add_argument("--base-url", default="http://127.0.0.1:5001/v1",
                        help="upstream OpenAI-compatible base url (Chat Completions is used)")
    parser.add_argument("--model", default=None,
                        help="override the model id; default is whatever the client asked for")
    parser.add_argument("--temperature", type=float, default=None,
                        help="injected sampling temperature; the arm's standard is > 0")
    parser.add_argument("--seed", type=int, default=None,
                        help="injected seed; use one distinct seed per sample")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--ledger-dir", default=str(Path.home() / ".oagf-shim-ledger"),
                        help="spool directory; deliberately outside the repository")
    parser.add_argument("--preflight", action="store_true",
                        help="run the capability gate and exit without serving")
    parser.add_argument("--allow-untooled", action="store_true",
                        help="serve even if the tool-call gate fails; the failure is recorded and "
                             "no sample taken under it may be reported as tool-using")
    args = parser.parse_args()

    gate = preflight(args.base_url, args.model or "qwen3.6-35b-a3b", args.timeout)
    print(f"capability gate: {'PASS' if gate['passed'] else 'FAIL'} — {gate.get('diagnosis')}")
    if gate.get("detail"):
        print(f"  {gate['detail']}")
    if gate.get("observed_call"):
        print(f"  observed call: {json.dumps(gate['observed_call'])}")

    if args.preflight:
        print(json.dumps(gate, indent=2, ensure_ascii=False))
        return 0 if gate["passed"] else 1

    if not gate["passed"] and not args.allow_untooled:
        print("\nREFUSED to serve: the tool-call round trip does not work, so an agentic sample "
              "taken now would not be one. Fix the cause above, or pass --allow-untooled to "
              "serve anyway with the failure recorded.", file=sys.stderr)
        return 1

    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
    ledger = Ledger(Path(args.ledger_dir), run_id)
    config = {"base_url": args.base_url, "model": args.model, "timeout": args.timeout,
              "temperature": args.temperature, "seed": args.seed}
    ledger.append("run_start", {
        "config": {k: v for k, v in config.items()},
        "capability_gate": gate,
        "shim_source_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "translation_table": {
            "translated_fields": sorted(TRANSLATED_FIELDS),
            "dropped_fields": {k: v[0] for k, v in DROPPED_FIELDS.items()},
            "refused_fields": sorted(REFUSED_FIELDS),
            "role_map": ROLE_MAP,
            "part_separator": PART_SEPARATOR,
        }})

    server = ShimServer(("127.0.0.1", args.port), make_handler(config, ledger))
    print(f"\nshim {SHIM_VERSION} on http://127.0.0.1:{args.port}/v1 -> {args.base_url}")
    print(f"ledger {ledger.path}")
    print(f"  temperature={args.temperature} seed={args.seed}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")
    ledger.append("run_end", {})
    return 0


if __name__ == "__main__":
    sys.exit(main())
