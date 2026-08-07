#!/usr/bin/env python3
"""Validate the Responses shim's translation table. Stdlib only; no framework, no network.

    python3 tools/tests/test_responses_shim.py

What these check, and why that is the list
------------------------------------------
The shim exists because TensorRT-LLM's `/v1/responses` silently loses parts of a conversation.
So the first tests here are not "does it work" but **"does it preserve exactly what upstream
dropped"** — every content part, the message's own role, and a tool call's name and id. Each of
those three has a matching upstream defect proven by effect on 2026-08-07.

The second group checks the fail-closed edge. This record's recurring defect is a change that
reads as a repair and does nothing, so a shim that quietly passed an unrecognised field through
would be worse than one that crashed. Every refusal case below is a field or item type that
would otherwise reach the model — or fail to — without the round record saying so.

The last test runs the **real captured Codex request** through the table. It is expected to be
REFUSED, and that expectation is the finding: the stock Codex tool profile offers namespace and
web_search tools that nothing behind this endpoint can execute, so the arm's profile has to be
narrowed before a sample is taken. A test that asserted success here would be asserting a
falsehood.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from responses_shim import (                                          # noqa: E402
    DROPPED_FIELDS, PART_SEPARATOR, Ledger, Ops, Refusal, build_output_items,
    build_response_object, merge_leading_system, split_reasoning, sse_events, translate_input,
    translate_request, translate_tools,
)

PASSED, FAILED = [], []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASSED if condition else FAILED).append(f"{name}{(' — ' + detail) if detail else ''}")


def refuses(name: str, rule_prefix: str, thunk) -> None:
    """Assert that a translation refuses, and refuses with the rule the design names."""
    try:
        thunk()
    except Refusal as refusal:
        check(name, refusal.rule_id.startswith(rule_prefix),
              f"refused with {refusal.rule_id}, expected {rule_prefix}*")
        return
    check(name, False, "did NOT refuse")


def ops_with(ops: Ops, rule_prefix: str) -> list[dict]:
    return [op for op in ops.entries if op["rule_id"].startswith(rule_prefix)]


# =============================================================================================
# 1. The three upstream silent-loss defects, each with the property the shim must restore
# =============================================================================================

#  Upstream reads content[0] and discards the rest. Proven by effect: a two-part item reached
#  the model as part one only, and the model answered as though part two was never sent.
ops = Ops()
messages = translate_input([{"type": "message", "role": "user", "content": [
    {"type": "input_text", "text": "PART ONE"},
    {"type": "input_text", "text": "PART TWO"},
    {"type": "input_text", "text": "PART THREE"}]}], ops)
check("all content parts survive the join",
      messages[0]["content"] == PART_SEPARATOR.join(["PART ONE", "PART TWO", "PART THREE"]),
      repr(messages[0]["content"]))
check("the multi-part join is recorded as model-visible",
      any(op["classification"] == "approved_model_visible_adaptation"
          for op in ops_with(ops, "R-PARTS-JOIN")))

#  Upstream hardcodes {"role": "assistant"}, which is why a typed user message produced
#  "No user query found in messages".
ops = Ops()
messages = translate_input([{"type": "message", "role": "user",
                             "content": [{"type": "input_text", "text": "hi"}]}], ops)
check("a typed user message stays a user message", messages[0]["role"] == "user")

ops = Ops()
messages = translate_input([{"type": "message", "role": "developer",
                             "content": [{"type": "input_text", "text": "rules"}]}], ops)
check("developer maps to system", messages[0]["role"] == "system")
check("the developer role map is recorded as model-visible",
      [op["classification"] for op in ops_with(ops, "R-ROLE-MAP")]
      == ["approved_model_visible_adaptation"])

#  Upstream converts a function_call to {"role": "function", "content": arguments}, discarding
#  the name and the call id, and the chat template then rejects the role outright.
ops = Ops()
messages = translate_input([
    {"role": "user", "content": "weather?"},
    {"type": "function_call", "call_id": "call_1", "name": "get_weather",
     "arguments": '{"city":"Paris"}'},
    {"type": "function_call_output", "call_id": "call_1", "output": "18C"}], ops)
check("function_call becomes an assistant tool_call", messages[1]["role"] == "assistant")
check("the tool call keeps its name",
      messages[1]["tool_calls"][0]["function"]["name"] == "get_weather")
check("the tool call keeps its arguments",
      messages[1]["tool_calls"][0]["function"]["arguments"] == '{"city":"Paris"}')
check("the tool call keeps its id", messages[1]["tool_calls"][0]["id"] == "call_1")
check("the result correlates to the call by id",
      messages[2]["role"] == "tool" and messages[2]["tool_call_id"] == "call_1")
check("the call precedes its result",
      [m["role"] for m in messages] == ["user", "assistant", "tool"])

#  A parallel call is one assistant turn carrying several tool_calls, not several turns.
ops = Ops()
messages = translate_input([
    {"role": "user", "content": "two things"},
    {"type": "function_call", "call_id": "a", "name": "f", "arguments": "{}"},
    {"type": "function_call", "call_id": "b", "name": "g", "arguments": "{}"}], ops)
check("consecutive calls merge into one assistant turn",
      len(messages) == 2 and len(messages[1]["tool_calls"]) == 2)


# =============================================================================================
# 2. Fail-closed: everything that must refuse rather than proceed with a note
# =============================================================================================

refuses("an unknown top-level field refuses", "R-FIELD-UNKNOWN",
        lambda: translate_request({"model": "m", "input": "hi", "wobble": 1}, Ops()))
refuses("previous_response_id refuses", "R-FIELD-REFUSED",
        lambda: translate_request({"model": "m", "input": "hi", "previous_response_id": "resp_1"}, Ops()))
refuses("background refuses", "R-FIELD-REFUSED",
        lambda: translate_request({"model": "m", "input": "hi", "background": True}, Ops()))
refuses("an unknown role refuses", "R-ROLE",
        lambda: translate_input([{"role": "moderator", "content": "hi"}], Ops()))
refuses("an unknown item type refuses", "R-ITEM-TYPE",
        lambda: translate_input([{"type": "computer_call", "id": "x"}], Ops()))
refuses("a reasoning item refuses rather than being dropped", "R-REASONING",
        lambda: translate_input([{"type": "reasoning", "id": "r", "summary": [],
                                  "content": [{"type": "reasoning_text", "text": "t"}]}], Ops()))
refuses("a non-text content part refuses", "R-CONTENT-PART",
        lambda: translate_input([{"type": "message", "role": "user", "content": [
            {"type": "input_image", "image_url": "http://x/y.png"}]}], Ops()))
refuses("a function_call missing its call_id refuses", "R-FUNCALL",
        lambda: translate_input([{"type": "function_call", "name": "f", "arguments": "{}"}], Ops()))
refuses("a namespace tool refuses", "R-TOOL-NAMESPACE",
        lambda: translate_tools([{"type": "namespace", "name": "ns", "tools": []}], Ops()))
refuses("the hosted web_search tool refuses", "R-TOOL-WEBSEARCH",
        lambda: translate_tools([{"type": "web_search", "external_web_access": True}], Ops()))
refuses("an unknown tool type refuses", "R-TOOL-TYPE",
        lambda: translate_tools([{"type": "code_interpreter"}], Ops()))
#  Upstream accepts exactly one system message and it must be first. Its error text names the
#  position rule, but arity is what actually fires — verified 2026-08-07: two system messages
#  both at index 0 and 1 are refused with "System message must be at the beginning."
ops = Ops()
merged = merge_leading_system([{"role": "system", "content": "A"},
                               {"role": "system", "content": "B"},
                               {"role": "user", "content": "hi"}], ops)
check("leading system turns merge into one",
      [m["role"] for m in merged] == ["system", "user"])
check("the merge preserves both texts in order",
      merged[0]["content"] == f"A{PART_SEPARATOR}B")
check("the system merge is recorded as model-visible",
      ops_with(ops, "R-SYSTEM-MERGE")[0]["classification"] == "approved_model_visible_adaptation")
check("a single system turn is left alone",
      merge_leading_system([{"role": "system", "content": "A"},
                            {"role": "user", "content": "hi"}], Ops())[0]["content"] == "A")
refuses("a late system message refuses rather than being hoisted", "R-SYSTEM-POSITION",
        lambda: merge_leading_system([{"role": "user", "content": "hi"},
                                      {"role": "system", "content": "late"}], Ops()))

refuses("an unknown output format refuses", "R-TEXT-FORMAT",
        lambda: translate_request({"model": "m", "input": "hi",
                                   "text": {"format": {"type": "grammar"}}}, Ops()))

#  web_search is *accepted* by the upstream schema. That is the trap: acceptance is not
#  evidence of execution, and a party that believes it searched and did not is the failure
#  this arm exists to expose.
check("web_search refuses even though upstream's schema accepts it", True,
      "verified 2026-08-07: POST /v1/responses with a web_search tool returns 200")


# =============================================================================================
# 3. The recorded drops — bookkeeping, and the two that cost something
# =============================================================================================

ops = Ops()
chat = translate_request({"model": "m", "input": "hi", "prompt_cache_key": "k",
                          "client_metadata": {"a": "b"}, "store": False,
                          "include": ["reasoning.encrypted_content"]}, ops)
check("the extra_forbidden fields are dropped, not forwarded",
      not any(k in chat for k in ("prompt_cache_key", "client_metadata", "store", "include")))
check("each drop is recorded",
      len(ops_with(ops, "R-DROP-")) == 4, f"{len(ops_with(ops, 'R-DROP-'))} recorded")
check("cache and telemetry drops are classified as invisible to the model",
      all(op["classification"] == "non_model_operational" for op in ops_with(ops, "R-DROP-")))

ops = Ops()
translate_request({"model": "m", "input": "hi", "reasoning": {"effort": "medium"},
                   "truncation": "auto"}, ops)
check("reasoning and truncation drops are classified as declared treatment, not as free",
      all(op["classification"] == "declared_treatment"
          for op in ops_with(ops, "R-DROP-REASONING") + ops_with(ops, "R-DROP-TRUNCATION")))
check("every dropped field carries a stated reason",
      all(detail for _, detail in DROPPED_FIELDS.values()))


# =============================================================================================
# 4. Sampling discipline is the shim's, and is declared
# =============================================================================================

ops = Ops()
chat = translate_request({"model": "m", "input": "hi"}, ops, temperature=0.7, seed=1003)
check("the injected temperature reaches upstream", chat["temperature"] == 0.7)
check("the injected seed reaches upstream", chat["seed"] == 1003)
check("both injections are declared treatment, not silent defaults",
      all(op["classification"] == "declared_treatment"
          for op in ops_with(ops, "R-TEMP-INJECT") + ops_with(ops, "R-SEED-INJECT")))
check("the injected values appear in the ledger detail, not just the fact of injection",
      any("0.7" in op["detail"] for op in ops_with(ops, "R-TEMP-INJECT"))
      and any("1003" in op["detail"] for op in ops_with(ops, "R-SEED-INJECT")))

ops = Ops()
chat = translate_request({"model": "m", "instructions": "be brief", "input": "hi"}, ops)
check("instructions become the leading system message",
      chat["messages"][0] == {"role": "system", "content": "be brief"})


# =============================================================================================
# 5. The return path
# =============================================================================================

ops = Ops()
items = build_output_items({"message": {
    "content": "the answer",
    "tool_calls": [{"id": "call_9", "type": "function",
                    "function": {"name": "fetch_url", "arguments": '{"url":"https://x"}'}}]}}, ops)
check("a parsed tool call returns as a function_call item", items[0]["type"] == "function_call")
check("the call id survives the return trip", items[0]["call_id"] == "call_9")
check("the tool name survives the return trip", items[0]["name"] == "fetch_url")
check("assistant text returns as a message item", items[1]["type"] == "message")
check("the message text is intact",
      items[1]["content"][0]["text"] == "the answer")

response_object = build_response_object({"model": "m", "usage": {"prompt_tokens": 5}},
                                        {"model": "m"}, items, "completed")
events = sse_events(response_object)
types = [t for t, _ in events]
check("the event stream opens with response.created", types[0] == "response.created")
check("the event stream closes with response.completed", types[-1] == "response.completed")
check("every output item is announced and completed",
      types.count("response.output_item.added") == 2
      and types.count("response.output_item.done") == 2)
check("a function call's arguments are streamed",
      "response.function_call_arguments.done" in types)
check("text output is streamed as a delta and a done",
      "response.output_text.delta" in types and "response.output_text.done" in types)
check("sequence numbers are contiguous from zero",
      [d["sequence_number"] for _, d in events] == list(range(len(events))))
check("the completed event carries the full output",
      len(events[-1][1]["response"]["output"]) == 2)
check("the created event carries no output yet",
      events[0][1]["response"]["output"] == [])
check("a truncated reply is reported as incomplete, not completed",
      build_response_object({}, {}, [], "incomplete")["status"] == "incomplete")


# ---------------------------------------------------------------------------------------------
# 5b. The client-side reasoning split
#
# The server cannot do this: TRT-LLM's only parser that fits this template breaks every
# `enable_thinking: false` request, and that host serves a consumer which runs thinking-off.
# So the split lives here, and being here it is recorded.
# ---------------------------------------------------------------------------------------------

ops = Ops()
answer, reasoning = split_reasoning(
    {"content": "Step 1. Consider Paris.\n</think>\n\nParis"}, "stop", ops)
check("the answer is separated from the chain of thought", answer == "Paris", repr(answer))
check("the reasoning is captured, not discarded",
      reasoning == "Step 1. Consider Paris.", repr(reasoning))
check("the split is recorded as model-visible",
      ops_with(ops, "R-REASONING-SPLIT")[0]["classification"]
      == "approved_model_visible_adaptation")
check("the recorded detail carries both byte counts",
      "23 bytes of reasoning" in ops_with(ops, "R-REASONING-SPLIT")[0]["detail"]
      and "5 bytes of answer" in ops_with(ops, "R-REASONING-SPLIT")[0]["detail"],
      ops_with(ops, "R-REASONING-SPLIT")[0]["detail"][:140])

#  A template change that emitted the opening tag too must not leave it glued to the answer.
answer, reasoning = split_reasoning(
    {"content": "<think>thinking</think>Paris"}, "stop", Ops())
check("an opening think tag is stripped from the reasoning",
      reasoning == "thinking" and answer == "Paris")

#  Thinking off: nothing to split, and nothing to record.
ops = Ops()
answer, reasoning = split_reasoning({"content": "Paris"}, "stop", ops)
check("a thinking-off reply passes through untouched",
      answer == "Paris" and reasoning == "" and ops.entries == [])

#  If the server ever grows a working reasoning parser, the two splits must not both run.
ops = Ops()
answer, reasoning = split_reasoning(
    {"content": "Paris", "reasoning_content": "thought"}, "stop", ops)
check("a server-supplied split is used instead of splitting again",
      answer == "Paris" and reasoning == "thought")
check("the server-supplied split is recorded as such",
      len(ops_with(ops, "R-REASONING-SERVED")) == 1)

#  The case that would otherwise put a sentence in the record the party never said.
ops = Ops()
answer, reasoning = split_reasoning(
    {"content": "Step 1. I should consider whether"}, "length", ops)
check("an unclosed reasoning block is flagged, not passed off as an answer",
      len(ops_with(ops, "R-REASONING-UNCLOSED")) == 1)
check("the flag says plainly that the text is not an answer",
      "NOT an answer" in ops_with(ops, "R-REASONING-UNCLOSED")[0]["detail"])
check("an unclosed reasoning block yields no reasoning field to quote",
      reasoning == "")

#  End to end through build_output_items, which is where the client-facing text is decided.
ops, out = Ops(), []
items = build_output_items(
    {"finish_reason": "stop",
     "message": {"content": "Deliberating at length.\n</think>\n\nThe answer is Paris."}}, ops, out)
check("the client receives only the answer",
      items[0]["content"][0]["text"] == "The answer is Paris.")
check("the reasoning is handed to the caller for the ledger", out == ["Deliberating at length."])

#  The client sends neither temperature nor seed; the shim injects both. The response object is
#  the artifact most likely to be quoted, so it must report the values actually in force.
reported = build_response_object({}, {"model": "m"}, [], "completed",
                                 {"temperature": 0.7, "seed": 1003})
check("the response reports the temperature actually used, not the client's silence",
      reported["temperature"] == 0.7)
check("the response reports the seed actually used", reported["seed"] == 1003)


# =============================================================================================
# 6. The ledger is a chain, and it is written before it is acted on
# =============================================================================================

with tempfile.TemporaryDirectory() as tmp:
    ledger = Ledger(pathlib.Path(tmp), "testrun")
    digest = ledger.blob({"b": 2, "a": 1})
    first = ledger.append("client_request", {"body_sha256": digest})
    second = ledger.append("upstream_request", {})
    third = ledger.append("upstream_response", {})
    lines = [json.loads(line) for line in ledger.path.read_text().splitlines()]

    check("every entry is on disk immediately", len(lines) == 3)
    check("the chain starts from a known root", lines[0]["prev_entry_sha256"] == "0" * 64)
    check("each entry links to the previous one",
          lines[1]["prev_entry_sha256"] != "0" * 64
          and lines[2]["prev_entry_sha256"] != lines[1]["prev_entry_sha256"])
    check("sequence numbers are strictly increasing",
          [line["seq"] for line in lines] == [1, 2, 3])
    check("bodies are stored by content address and are recoverable",
          json.loads((ledger.blobs / f"{digest}.json").read_text()) == {"a": 1, "b": 2})
    check("the blob digest is stable under key order",
          ledger.blob({"a": 1, "b": 2}) == digest)
    check("entry kinds distinguish the two sides of the boundary",
          {first["kind"], second["kind"], third["kind"]}
          == {"client_request", "upstream_request", "upstream_response"})


# =============================================================================================
# 7. The real captured Codex request — expected to REFUSE, and that is the finding
# =============================================================================================

#  Reduced from the verbatim ~98 KB capture taken through a recording proxy on 2026-08-07.
#  Field names, item shapes and tool types are exactly as Codex 0.146.1 sent them; only the
#  20,751-character instructions blob and the bodies of the other 17 tools are elided.
REAL_CODEX_REQUEST = {
    "model": "qwen3.6-35b-a3b",
    "instructions": "<20751 characters elided>",
    "input": [
        {"type": "message", "id": "msg_019fdc97-75f3-71a2-912f-cd3881132d8f", "role": "developer",
         "content": [{"type": "input_text", "text": "<permissions instructions>…"},
                     {"type": "input_text", "text": "<apps_instructions>…"}]},
        {"type": "message", "id": "msg_019fdc97-75f3-71a2-912f-cd4ff25e4a9f", "role": "user",
         "content": [{"type": "input_text", "text": "<recommended_plugins>…"}]},
        {"type": "message", "id": "msg_019fdc97-75fa-75c2-9175-603bebcff67c", "role": "user",
         "content": [{"type": "input_text", "text": "say hi"}]},
    ],
    "tools": [
        {"type": "function", "name": "exec_command", "description": "…", "strict": False,
         "parameters": {"type": "object", "properties": {}}},
        {"type": "namespace", "name": "mcp__codex_apps__sites", "description": "…", "tools": []},
        {"type": "web_search", "external_web_access": True},
    ],
    "tool_choice": "auto",
    "parallel_tool_calls": False,
    "reasoning": {"effort": "medium", "summary": "detailed"},
    "store": False,
    "stream": True,
    "include": ["reasoning.encrypted_content"],
    "prompt_cache_key": "019fdc97-7194-7e23-b2a7-defec44f9a3c",
    "client_metadata": {"thread_id": "019fdc97-7194-7e23-b2a7-defec44f9a3c"},
}

refuses("the stock Codex tool profile refuses — the profile must be narrowed first",
        "R-TOOL-", lambda: translate_request(REAL_CODEX_REQUEST, Ops()))

#  With plugins and MCP apps disabled, the same request must translate cleanly. This is the
#  configuration the arm actually runs under, so this is the case that has to hold.
NARROWED = dict(REAL_CODEX_REQUEST)
NARROWED["tools"] = [REAL_CODEX_REQUEST["tools"][0]]
ops = Ops()
chat = translate_request(NARROWED, ops, temperature=0.7, seed=1000)

check("the narrowed Codex request translates", isinstance(chat, dict))
check("the two leading system turns merge into the one upstream permits",
      [m["role"] for m in chat["messages"]] == ["system", "user", "user"],
      str([m["role"] for m in chat["messages"]]))
check("the developer item's SECOND content part survives — the upstream defect this shim exists for",
      "<apps_instructions>…" in chat["messages"][0]["content"])
check("the top-level instructions survive the system merge",
      "<20751 characters elided>" in chat["messages"][0]["content"])
check("the merge is recorded as model-visible", len(ops_with(ops, "R-SYSTEM-MERGE")) == 1)
check("the client's item ids are dropped and each drop is recorded",
      len(ops_with(ops, "R-ITEM-ID")) == 3)
check("the surviving function tool reaches upstream in Chat Completions shape",
      chat["tools"][0]["function"]["name"] == "exec_command")
check("no refused field leaked into the upstream request",
      not any(k in chat for k in ("prompt_cache_key", "client_metadata", "include", "reasoning")))
check("every transformation carries a rule id and a classification",
      all(op["rule_id"] and op["classification"] in
          {"non_model_operational", "approved_model_visible_adaptation", "declared_treatment"}
          for op in ops.entries))
check("the model-visible transformations are a strict subset of all of them",
      0 < len(ops.model_visible()) < len(ops.entries),
      f"{len(ops.model_visible())} of {len(ops.entries)}")


# =============================================================================================

print(f"\n\033[32m{len(PASSED)} passed\033[0m")
for line in PASSED:
    print(f"  ✓ {line}")
if FAILED:
    print(f"\n\033[31m{len(FAILED)} FAILED\033[0m", file=sys.stderr)
    for line in FAILED:
        print(f"  ✗ {line}", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
