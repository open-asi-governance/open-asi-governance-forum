#!/usr/bin/env python3
"""Solicit a contribution from a routed API party at k samples, with computed variance.

    python3 tools/solicit_api.py --spec <spec.json> --k 5 --model openai/gpt-5.6-terra \\
        --out-round <round>

**GENERATION code, not maintenance code**, exactly like `solicit_local.py`. Nothing
in `tools/` that the build runs calls a model.

WHY THIS IS A DIFFERENT PARTY FROM THE CHAT SURFACE, and why that matters here.

This corpus already contains contributions from **ChatGPT (OpenAI chat surface)**,
pasted by the custodian. A model reached over an API through a router is **NOT that
party** and must never be merged with it, under the same never-merge rule that keeps
Claude Opus 5, Claude Fable 5 and Claude Code separate (D-09). It is a different
model version, a different invocation surface, and it arrives through
intermediaries the chat surface does not have.

The delivery chain is recorded on every sample because each hop is a party that
could alter what was sent or returned, and none of them is the annotator's to
vouch for:

    annotator  ->  OpenRouter  ->  serving provider (e.g. Azure)  ->  the model

`provider` and the generation id come back from the router and are recorded as the
router reported them. That is the router's testimony, not proof -- D-18 applies to
it exactly as it applies to a model self-reporting its version.

WHAT THIS BUYS THAT THE LOCAL MODEL DOES NOT. The local party is divergent in
lineage but is served by the annotator's own operator on the annotator's own
hardware. This party is not. For the specific question of "did anyone other than
the party that wrote these claims ever check them", a routed frontier model is a
materially stronger answer than a locally-served one -- and still not an
independent evaluation in ICP section 4.4's sense, because the annotator chose the
question, the schema and the excerpt.

Sampling parameters, the requested model, the served model, the router's generation
id, and a machine-captured timestamp are recorded per sample. What CANNOT be
recorded is the provider's system prompt or any router-side transformation, and
those absences are written into the artifact rather than left to be assumed.

Exit status is 0 when at least one sample was collected and recorded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error

import fetch_executor as fx
import search_executor as sx
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from math import log2
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    return -sum((n / total) * log2(n / total) for n in counts.values() if n)


def call_once(key: str, body: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))



def validate_sample(parsed, schema: dict) -> str | None:
    """Return a rejection reason, or None if the sample conforms.

    THE ROUTER'S STRICT MODE IS NOT EVIDENCE. This tool asked OpenRouter for
    `json_schema` with `strict: true` and then treated "it parsed as JSON" as
    conformance -- so a reply with a missing required field, or a `position` outside
    the enum, was recorded as a good sample and counted toward k. The SOP halts on a
    schema-invalid reply; that halt could not fire, because nothing checked.

    Validation happens HERE, on the annotator's side, against the same schema the
    spec froze. A provider's compliance is a claim like any other.
    """
    try:
        import jsonschema
    except ImportError:                                             # pragma: no cover
        return ("jsonschema is not installed, so this sample could not be validated. "
                "Install it with: python3 -m pip install jsonschema")
    try:
        jsonschema.Draft202012Validator(schema).validate(parsed)
    except jsonschema.ValidationError as error:
        path = "/".join(str(p) for p in error.path) or "(root)"
        return f"schema-invalid at {path}: {error.message}"
    return None


def spend_from(samples: list[dict], model: str, rates_path: Path,
               web_search: dict | None = None) -> dict:
    """Actual cost, summed from what each response reported it used.

    Reported usage is the provider's testimony, exactly like the served model string
    and the provider name. It is recorded as such and is not proof of what was
    billed; only the provider's own statement is that.
    """
    entry = {"actual_usd": None, "input_tokens": 0, "output_tokens": 0,
             "basis": "Summed from each response's usage block — the provider's testimony.",
             "rates_version": None}
    for sample in samples:
        usage = sample.get("usage") or {}
        #  ABSENT IS NOT ZERO: a missing token count understates spend. Counted separately so
        #  the figure carries its own incompleteness, as record_spend.py now does.
        if usage.get("prompt_tokens") is None or usage.get("completion_tokens") is None:
            entry["usage_unknown"] = entry.get("usage_unknown", 0) + 1
        else:
            entry["input_tokens"] += usage["prompt_tokens"]
            entry["output_tokens"] += usage["completion_tokens"]
    if not rates_path.is_file():
        return entry
    rates = json.loads(rates_path.read_text(encoding="utf-8"))
    entry["rates_version"] = rates.get("rates_version")
    rate = rates.get("usd_per_million_tokens", {}).get(model)
    #  SEARCH FEES ARE PART OF WHAT A ROUND COST. Pricing tokens only understated a
    #  browsed 20-request round by the whole search fee, and the ledger inherited it —
    #  so the daily ceiling would have been computed against a number that omits a
    #  charge the round definitely incurred.
    engine = (web_search or {}).get("engine")
    fee = (rates.get("web_search_usd_per_request") or {}).get(engine) if engine else None
    entry["web_search_engine"] = engine
    entry["web_search_requests"] = len(samples) if engine else 0
    entry["web_search_usd"] = round(len(samples) * fee, 4) if fee else (0.0 if not engine else None)
    if entry["web_search_usd"] is None:
        entry["web_search_unpriced_reason"] = (
            f"no per-request rate recorded for {engine!r}; the fee is real and is not counted "
            f"in actual_usd, which therefore UNDERSTATES this round")
    if rate and (entry["input_tokens"] or entry["output_tokens"]):
        entry["actual_usd"] = round(
            (entry["input_tokens"] * rate["input"]
             + entry["output_tokens"] * rate["output"]) / 1_000_000
            + (entry["web_search_usd"] or 0.0), 4)
        entry["rates_are_verified"] = bool(rates.get("verified_by_custodian"))
    return entry


def write_summary(spec: dict, args, samples: list[dict], raw_path: Path,
                  rejected: list[dict]) -> None:
    """Conform to tools/schemas/solicitation.schema.json, exactly as the local arm does.

    The first version of this invented its own summary shape and the build refused
    it -- correctly. Two solicitation families writing two different summary shapes
    is how a corpus ends up unable to compare its own arms, and the schema exists to
    prevent that.
    """
    art_dir = REPO_ROOT / "corpus" / "artifacts" / args.out_round
    art_dir.mkdir(parents=True, exist_ok=True)
    served = {s["delivery_chain"]["served_model"] for s in samples}
    #  null means the router did not say, which is NOT the same as a provider named
    #  "None". str() on the missing value produced exactly that string and put it in
    #  the published record as though it were a provider's name.
    providers = sorted({p for p in (s["delivery_chain"]
                                    ["serving_provider_as_reported_by_router"]
                                    for s in samples) if p is not None})
    provider_unreported = any(s["delivery_chain"]["serving_provider_as_reported_by_router"]
                              is None for s in samples)
    variance = {}
    for field in spec["variance_fields"]:
        counts = Counter(s["parsed"].get(field) for s in samples)
        top, n = counts.most_common(1)[0]
        variance[field] = {
            "distribution": dict(counts), "n": len(samples),
            "distinct_values": len(counts), "modal_value": top,
            "modal_fraction": round(n / len(samples), 4),
            "shannon_entropy_bits": round(entropy(counts), 4),
            "unanimous": len(counts) == 1,
        }
        print(f"  {field}: modal={top!r} ({n/len(samples):.0%}), "
              f"{len(counts)} distinct, H={variance[field]['shannon_entropy_bits']} bits")

    summary = {
        "schema_version": "oagrc-local-solicitation-0.1",
        "artifact_type": "solicitation_summary",
        "round": args.out_round,
        "slug": spec["slug"],
        #  OMITTED, not null, when there is no question -- see below. Written as a key with a
        #  null value it fails the provenance schema (`question` is optional but typed), and it
        #  publishes `"question": null` as though the question were empty rather than absent.
        #  A proposal cohort has no question PUT to it: the parties are asked to propose one.
        #  Reading spec["question"] here raised KeyError AFTER the samples were collected and
        #  paid for, losing three arms' summaries while their raw material sat on disk intact.
        "phase": spec["phase"],
        "k_requested": args.k,
        "k_collected": len(samples),
        #  EVERY attempt is accounted for. Rejected samples used to vanish: a
        #  transport error, an empty completion or unparseable JSON simply reduced
        #  k_collected, so "nothing solicited is discarded" was false and a
        #  schema-invalid reply was indistinguishable from a call that never
        #  happened. Each rejection now carries its category and its raw bytes.
        "failures": [r["reason"] for r in rejected],
        "attempts": args.k,
        "rejected": rejected,
        "variance": variance,
        "citability": "citable" if len(samples) >= 5 else "non-citable (k<5)",
        "contributor": {
            "identity": spec["identity"],
            # The router's report of what it served. Testimony, not authentication.
            "version_identifier": ", ".join(sorted(served)) or args.model,
            "sampling_parameters": {"temperature": args.temperature,
                                    "max_tokens": args.max_tokens,
                                    "seed": None,
                                    "seed_unsupported_reason":
                                        "The router does not expose a seed parameter."},
        },
        "spend": spend_from(samples, args.model,
                            REPO_ROOT / "record" / "cycles" / "model-rates.json",
                            spec.get("web_search")),
        "serve_configuration": {
            "captured": True,
            "router": "openrouter.ai",
            "serving_provider_as_reported_by_router": providers,
            "provider_not_reported_for_some_samples": provider_unreported,
            "delivery_chain": "annotator -> OpenRouter -> serving provider -> model",
            "not_captured": ["provider system prompt", "router-side transformation",
                             "weights or build identifier"],
        },
        "prompt_sha256": hashlib.sha256(spec["prompt"].encode("utf-8")).hexdigest(),
        "spec_sha256": hashlib.sha256(Path(args.spec).read_bytes()).hexdigest(),
        "raw_samples": str(raw_path.relative_to(REPO_ROOT)),
    }
    #  Present only when a question was actually put. See the note above `phase`.
    question = spec.get("question") or spec.get("task")
    if question:
        summary["question"] = question
    (art_dir / f"{spec['slug']}-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--spec", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--model", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--out-round", required=True)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    args = parser.parse_args()

    import os
    key = os.environ.get(args.api_key_env)
    if not key:
        print(f"REFUSED: {args.api_key_env} is not set.")
        return 1

    if args.temperature <= 0:
        # Same rule solicit_local.py enforces: k identical samples make variance
        # meaningless, and reporting a distribution over them would be a number
        # that looks like variance and is not.
        print("REFUSED: temperature must be > 0, or the k samples measure nothing.")
        return 1

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec_sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    print(f"soliciting k={args.k} from {args.model} at temperature {args.temperature}")
    print(f"  spec      {spec_path}  sha256 {spec_sha[:16]}…")

    samples: list[dict] = []
    rejected: list[dict] = []

    def reject(index: int, category: str, reason: str, bytes_seen: str | None = None,
               raw: dict | None = None) -> None:
        """Every attempt that did not become a sample is recorded, with its bytes.

        `finish_reason` is recorded because it is the field that decides the
        diagnosis: 'length' means the reply was cut off by max_tokens, and a
        truncated reply is not a party declining. The first version of this omitted
        it, and a round then reported two parties as undersampled without recording
        the one fact that said why.
        """
        choice = ((raw or {}).get("choices") or [{}])[0]
        rejected.append({"sample_index": index, "category": category, "reason": reason,
                         "captured_utc": utc_now(),
                         "finish_reason": choice.get("finish_reason"),
                         "usage": (raw or {}).get("usage"),
                         "response_bytes": (bytes_seen or "")[:8000] or None,
                         "response_byte_length": len(bytes_seen) if bytes_seen else None})
        print(f"  [{index:2}/{args.k}] REJECTED ({category}, "
              f"finish={choice.get('finish_reason')!r}): {reason[:120]}")

    #  fetch-url-v1 comes from the FROZEN SPEC, exactly like search: the plan decides what a
    #  party could do. A CLI flag could diverge from the plan, and the record would then describe
    #  a capability the party did not have, or omit one it did.
    fetch_enabled = bool((spec.get("capability") or {}).get("fetch_url"))
    #  The routed arm must offer whatever the capability declares. Without this a routed party
    #  in a search-fetch arm would silently get fetch only, while its spec, its party key and
    #  the round record all said it had both.
    search_enabled = bool((spec.get("capability") or {}).get("search_web"))
    tools_enabled = fetch_enabled or search_enabled
    max_tool_calls = int((spec.get("capability") or {}).get("max_tool_calls", 6))

    for index in range(1, args.k + 1):
        messages = [{"role": "user", "content": spec["prompt"]}]
        receipts: list = []
        #  Separate from fetch receipts, so "which tool produced this" is a fact.
        search_receipts: list = []
        body = {
            "model": args.model,
            "messages": messages,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": spec["schema_name"], "strict": True,
                                "schema": spec["schema"]},
            },
        }
        #  SEARCH COMES FROM THE FROZEN SPEC, never from a flag. The plan decides what
        #  a party could do; a CLI argument could diverge from the plan and the record
        #  would then describe a capability the party did not have, or omit one it did.
        #
        #  The `plugins` form rather than the `:online` suffix: the suffix changes the
        #  model id, and the budget preflight refuses a model id it cannot price.
        search = spec.get("web_search") or {}
        if search.get("id"):
            body["plugins"] = [{k: v for k, v in search.items()
                                if k in ("id", "engine", "max_results",
                                         "include_domains", "exclude_domains")}]
        if tools_enabled:
            body["tools"] = ([fx.TOOL_SCHEMA] if fetch_enabled else []) + \
                            ([sx.TOOL_SCHEMA] if search_enabled else [])
            body["tool_choice"] = "auto"
            #  A structured answer cannot be demanded while the model still needs turns to call
            #  tools: the format is imposed only on the FINAL turn, below.
            response_format = body.pop("response_format", None)

        #  THE TOOL LOOP. Bounded by max_tool_calls: an unbounded loop is a way to spend a
        #  budget the preflight approved for k samples, and a party that will not stop is a
        #  finding rather than something to accommodate silently.
        tool_error = None
        calls_made = 0
        #  Counts CALLS, not turns. One turn can request several URLs, so a turn budget is not a
        #  call budget and "12" would not have meant twelve fetches.
        for turn in range(max_tool_calls + 2 if fetch_enabled else 1):
            try:
                raw = call_once(key, body, args.timeout)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
                #  READ THE BODY. An HTTPError IS the response, and a bare "HTTP Error 400: Bad
                #  Request" says only that the provider rejected us -- not what it objected to.
                #  A whole arm failed 5/5 and the record kept no evidence of WHY, which is the
                #  same defect as reading `tail -1` of a failing suite: a signal that is not
                #  causally downstream of the thing it is taken to describe.
                detail = ""
                if isinstance(error, urllib.error.HTTPError):
                    try:
                        detail = " :: " + error.read().decode("utf-8", "replace")[:600]
                    except Exception:                             # noqa: BLE001 -- best effort
                        detail = " :: <body unreadable>"
                tool_error = ("transport", f"{type(error).__name__}: {error}{detail}")
                break
            if "error" in raw:
                tool_error = ("provider_error", str(raw["error"])[:400])
                break
            message = raw["choices"][0]["message"]
            calls = message.get("tool_calls") or []
            if not (fetch_enabled and calls):
                #  Same as the local arm: a party that declines to fetch still owes a
                #  schema-valid answer, and the format was popped for the tool turns.
                if fetch_enabled and response_format and "response_format" not in body:
                    body["response_format"] = response_format
                    body["tools"] = []
                    body["tool_choice"] = "none"
                    continue
                break
            if calls_made + len(calls) > max_tool_calls:
                #  Recorded, not hidden: the answer that follows was produced under a truncated
                #  loop and a reader must be able to see that.
                receipts.append({"outcome": "BUDGET_EXHAUSTED",
                                 "reason": f"the party requested more than {max_tool_calls} "
                                           f"tool calls; the loop stopped and asked it to answer"})
                messages.append(message)
                for call in calls:
                    messages.append({"role": "tool", "tool_call_id": call["id"],
                                     "content": json.dumps({"ok": False,
                                                            "error": "tool budget exhausted"})})
                body["tools"] = []
                body["tool_choice"] = "none"
                if response_format:
                    body["response_format"] = response_format
                body["messages"] = messages
                continue
            messages.append(message)
            for call in calls:
                try:
                    arguments = json.loads(call["function"].get("arguments") or "{}")
                except json.JSONDecodeError:
                    arguments = {}
                name = (call.get("function") or {}).get("name")
                search_name = sx.TOOL_SCHEMA["function"]["name"]
                fetch_name = fx.TOOL_SCHEMA["function"]["name"]
                enabled = ({search_name} if search_enabled else set()) | \
                          ({fetch_name} if fetch_enabled else set())
                if name not in enabled:
                    (search_receipts if search_enabled else receipts).append(
                        {"outcome": "TOOL_DISPATCH_REFUSED", "requested_tool": name,
                         "reason": f"{name!r} is not an enabled tool in this arm",
                         "enabled_tools": sorted(enabled)})
                    result = {"ok": False, "refused": True,
                              "reason": f"{name!r} is not an enabled tool in this arm"}
                elif name == search_name:
                    result = sx.run_tool_call(call["function"].get("arguments") or "{}",
                                              search_receipts,
                                              sequence=len(search_receipts) + 1)
                else:
                    result = fx.run_tool_call(arguments.get("url"), receipts)
                calls_made += 1
                delivered = json.dumps(result, ensure_ascii=False)[:60000]
                if name == search_name:
                    if search_receipts:
                        search_receipts[-1]["message_delivered_to_model"] = delivered
                        search_receipts[-1]["message_delivered_sha256"] = sx.sha256_text(delivered)
                else:
                    fx.record_delivery(receipts, delivered)
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": delivered})
            body["messages"] = messages
            if response_format:
                #  Once the party has read something, require the structured answer again.
                body["response_format"] = response_format
        if tool_error:
            #  Receipts attached even on rejection: a sample that fetched three pages and then
            #  failed to parse still tells a reader what the party read, and dropping it would
            #  hide the most expensive part of the attempt.
            reject(index, tool_error[0], tool_error[1])
            if receipts and rejected:
                rejected[-1]["fetch_receipts"] = receipts
            continue
        text = raw["choices"][0]["message"].get("content")
        if not text:
            # A provider can return an empty completion -- a filter, a refusal, or a
            # response that spent its budget before emitting content. This used to
            # raise out of the loop and lose every sample already collected in the
            # batch, which is D-39's shape: one bad item destroying the rest.
            reject(index, "empty_completion",
                   f"finish_reason={raw['choices'][0].get('finish_reason')!r}", raw=raw)
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as error:
            reject(index, "malformed_json", str(error), text, raw=raw)
            if receipts and rejected:
                rejected[-1]["fetch_receipts"] = receipts
            continue
        invalid = validate_sample(parsed, spec["schema"])
        if invalid:
            reject(index, "schema_invalid", invalid, text, raw=raw)
            if receipts and rejected:
                rejected[-1]["fetch_receipts"] = receipts
            continue
        samples.append({
            "sample_index": index,
            "captured_utc": utc_now(),
            "parsed": parsed,
            "raw_text": text,
            "delivery_chain": {
                "requested_model": args.model,
                "served_model": raw.get("model"),
                "router": "openrouter.ai",
                "serving_provider_as_reported_by_router": raw.get("provider"),
                "router_generation_id": raw.get("id"),
                "note": ("Each hop could alter what was sent or returned and none is the "
                         "annotator's to vouch for. provider and id are the ROUTER'S "
                         "testimony, not proof -- D-18."),
            },
            #  The receipts ARE the provenance: what was requested, what came back, its hash,
            #  and the exact text handed to the model. A party saying "I verified X" against a
            #  log showing it never fetched X is a finding this record can now produce.
            "fetch": ({"profile": fx.PROFILE, "profile_sha256": fx.profile_sha256(),
                       "receipts": receipts,
                       "fetched": sum(1 for r in receipts if r.get("outcome") == "FETCHED"),
                       "refused": sum(1 for r in receipts if r.get("outcome") == "REFUSED"),
                       "sources_check": fx.sources_supported_by_receipts(
                           parsed.get("sources") if isinstance(parsed, dict) else None, receipts),
                       "stratum": ("fetched_successfully"
                                   if any(r.get("outcome") == "FETCHED" for r in receipts)
                                   else "fetch_attempted_refused"
                                   if any(r.get("outcome") == "REFUSED" for r in receipts)
                                   else "budget_exhausted"
                                   if any(r.get("outcome") == "BUDGET_EXHAUSTED" for r in receipts)
                                   else "no_fetch")}
                      if fetch_enabled else None),
            "sampling": {"temperature": args.temperature, "max_tokens": args.max_tokens},
            "search": ({"profile": sx.PROFILE_SHA256, "receipts": search_receipts,
                            "queries": sx.queries_issued(search_receipts),
                            "zero_result_queries":
                                sx.zero_result_queries(search_receipts)}
                           if search_enabled else None),
                 "finish_reason": raw["choices"][0].get("finish_reason"),
            "usage": raw.get("usage"),
            #  WHAT THIS PARTY ACTUALLY READ. The prompt now gives an address and the
            #  means to fetch it, so "did it look?" becomes a question the record can
            #  answer instead of infer. Each url_citation carries the page, its title,
            #  the extracted text, and the character span of the reply where it was
            #  used -- so a claim in an answer can be traced to the page behind it.
            #
            #  AN EMPTY LIST DOES NOT MEAN THE PARTY CHOSE NOT TO SEARCH. The web
            #  plugin runs a search on every request; empty annotations mean nothing
            #  was cited in the answer, which is a different claim entirely. Reading
            #  it as "the party did not look" would be an inference dressed as a
            #  record. Nor is this fetching a URL: it is a search engine's results.
            "web_citations": [
                {"url": (a.get("url_citation") or {}).get("url"),
                 "title": (a.get("url_citation") or {}).get("title"),
                 "used_at": [(a.get("url_citation") or {}).get("start_index"),
                             (a.get("url_citation") or {}).get("end_index")],
                 #  Two hashes, because one over bytes nobody kept is unverifiable.
                 #  The first covers the stored excerpt and can be recomputed from
                 #  this artifact; the second covers what the router returned and can
                 #  only ever be compared, never reproduced from here.
                 "content_stored_sha256": hashlib.sha256(
                     (((a.get("url_citation") or {}).get("content") or "")[:4000])
                     .encode("utf-8")).hexdigest(),
                 "content_full_sha256": hashlib.sha256(
                     ((a.get("url_citation") or {}).get("content") or "").encode("utf-8")
                 ).hexdigest(),
                 "content_full_length": len((a.get("url_citation") or {}).get("content") or ""),
                 "content": ((a.get("url_citation") or {}).get("content") or "")[:4000]}
                for a in (raw["choices"][0]["message"].get("annotations") or [])
                if a.get("type") == "url_citation"],
            "web_search": {k: v for k, v in (spec.get("web_search") or {}).items()
                           if k in ("id", "engine", "max_results")},
            "citations_are_the_router_s_report": (
                "Which pages were fetched, and their extracted text, are reported by the "
                "router. That is testimony (D-18), exactly like the served model string. "
                "Nothing here proves the page said what the extract says it said."),
        })
        print(f"  [{index:2}/{args.k}] {raw['choices'][0].get('finish_reason')} "
              f"{raw.get('usage',{}).get('completion_tokens','?')}tok")

    if not samples:
        #  Nothing conformed. The rejections are still written, because "no usable
        #  sample" and "the call was never made" must not look the same in the
        #  record -- a party that returned five schema-invalid replies said
        #  something, and erasing it would be the strongest possible form of the
        #  discard this tool is supposed to have stopped doing.
        raw_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
        raw_dir.mkdir(parents=True, exist_ok=True)
        reject_path = raw_dir / f"{spec['slug']}-rejected.json"
        if not reject_path.exists():
            reject_path.write_text(json.dumps({
                "artifact_type": "rejected_samples",
                "slug": spec["slug"], "identity": spec["identity"],
                "spec_path": str(spec_path), "spec_sha256": spec_sha,
                "k_requested": args.k, "k_collected": 0,
                "note": ("Every attempt failed validation, transport or the provider. "
                         "No summary is written because there is no distribution to "
                         "compute, but what happened is recorded."),
                "rejected": rejected,
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"REFUSED: no usable samples. {len(rejected)} rejection(s) recorded at "
                  f"{reject_path.relative_to(REPO_ROOT)}")
        else:
            print(f"REFUSED: no usable samples, and {reject_path.name} already exists.")
        return 1

    raw_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{spec['slug']}-samples.json"
    # RAW MATERIAL IS NEVER OVERWRITTEN. This tool had no guard, and a re-run of the
    # same slug silently replaced an ALREADY-COMMITTED sample file -- the corpus's
    # central rule, broken by its own instrument. The manifest caught it as MODIFIED,
    # which is the control working, but the bytes were already gone from the working
    # tree and only git had them.
    #
    # A second solicitation is a NEW artifact, not a correction. Choose a distinct
    # slug and record why, so the record shows that the parameter mattered rather
    # than hiding the first attempt.
    if raw_path.exists():
        print(f"REFUSED: {raw_path.relative_to(REPO_ROOT)} already exists.")
        print("  Raw material is immutable once written. A re-solicitation is a new")
        print("  artifact: change the spec's slug and state why in the new file.")
        return 1

    raw_path.write_text(json.dumps({
        "artifact_type": "raw_samples",
        "slug": spec["slug"],
        "identity": spec["identity"],
        "spec_path": str(spec_path),
        "spec_sha256": spec_sha,
        "k_requested": args.k,
        "k_collected": len(samples),
        "rejected": rejected,
        "unrecorded": {
            "system_prompt": "Not disclosed by the provider or the router.",
            "router_side_transformation": "Cannot be observed from the client.",
            "version_identifier": ("The served model string is what the router reported; "
                                   "no build or weights identifier is exposed."),
        },
        "samples": samples,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_summary(spec, args, samples, raw_path, rejected)
    print(f"\ncollected {len(samples)}/{args.k}  →  {raw_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
