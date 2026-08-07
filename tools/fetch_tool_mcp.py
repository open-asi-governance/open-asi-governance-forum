#!/usr/bin/env python3
"""An MCP server giving the tool-using party ONE capability: fetch a named URL, with receipts.

STATUS 2026-08-07: WORKS END TO END, AND DELIBERATELY NOT USED. Read this before re-enabling it.
------------------------------------------------------------------------------------------------
Routing is solved. Codex advertises MCP tools only inside a `namespace` tool, and the shim
flattens the member so a Chat Completions backend can carry it. The return trip then failed under
every spelling tried — `mcp__oagf_fetch__fetch_url`, `fetch_url`, `oagf_fetch__fetch_url` — all
`error=unsupported call`, because Codex resolves a call on the (namespace, name) **pair** and a
flattened function call is a bare string. The Responses `function_call` item has a separate
`namespace` field; the shim now rehydrates it from the mapping it cached while flattening, and
the call routes. Verified: `mcp: oagf_fetch/fetch_url (completed)`, with a receipt written
(status 200, sha256 ff67a9d7…, 559 bytes).

**The blocker is approvals, not routing.** In `codex exec` there is no one to approve an MCP tool
call, so it is auto-cancelled — `default_tools_approval_mode = "auto"` on the server does not
suppress it (tried), and openai/codex#24135 records that the only path is
`--dangerously-bypass-approvals-and-sandbox`. That flag is how the run above succeeded.

**So this is not used, and the reason is the whole point of the arm.** Bypassing approvals also
bypasses the sandbox, and the sandbox is what `tools/arm_acceptance.py` exists to prove is
holding — a party asked whether the record can be trusted must not be able to write to the
record. Trading that guarantee for a nicer fetch tool would forfeit the one thing that makes the
arm's verification mean anything, to gain a content hash. That is a bad trade and it is not
close.

The arm therefore browses through `exec_command` with sandbox network access. The loss is real
and is stated rather than papered over: the SSRF guard below, the content SHA-256 and the
truncation disclosure are all forfeited, and provenance narrows to *"the exact command issued and
the exact bytes returned to the model"* — both of which the shim's ledger does capture. The
moment #24135 lands, this file and the shim's rehydration make the better path available with no
further work.


Why this exists rather than Codex's own `web_search`
----------------------------------------------------
The record's open question (P006) asks what a stateless party can verify. Three rounds handed
parties the record's address and none of them read it — search is retrieval-by-resemblance and
the site is not indexed. The repair is a party that can **resolve a citation**, which is a
different capability from search and has to be provided as such.

Codex's hosted `web_search` tool is accepted by TensorRT-LLM's schema and executed by nobody
behind this endpoint, so the shim refuses it. That refusal is the point: a party that believes
it searched and did not is precisely the failure this arm exists to expose. This program is the
honest replacement — a tool that actually runs, in a process we wrote, that emits a receipt for
every request whether it succeeded or not.

What a receipt is for
---------------------
`A party that says "I verified X" and a log showing it never read X is a finding the record must
be able to produce.` So every call appends a hash-chained receipt carrying the requested URL, the
full redirect chain, the status, the SHA-256 of the **raw bytes** received, their length, and
whether the text handed to the model was truncated. The model is told the digest in its own tool
result, so a claim in an answer can be tied to — or falsified against — a receipt.

The receipt records what was *retrieved*, not what was *true*. A page fetched from a host the
operator controls is still operator-served; resolving a citation is not independent verification,
and the round artifacts must keep saying so.

What it refuses, and why refusing is part of the design
-------------------------------------------------------
Read-only means read-only at every layer. This tool:

* serves `http`/`https` only — no `file:`, no `ftp:`, no `data:`;
* refuses loopback, private, link-local, multicast and reserved addresses, and the cloud metadata
  address, so the party cannot reach the inference server, the ledger, or anything else on this
  host or its network;
* **re-resolves and re-checks every redirect hop** rather than trusting the first check, because
  a public hostname that redirects to `127.0.0.1`, or one whose DNS answer changes between the
  check and the connect, is the ordinary way an SSRF guard is defeated;
* sends no credentials, no cookies, and no ambient headers;
* caps the body and says so explicitly in the result, because undisclosed truncation is the exact
  shape of failure this record keeps finding.

Every refusal is itself a receipt. A blocked fetch that left no trace would be indistinguishable
from a fetch never attempted.

Usage
-----
Configured as a stdio MCP server in the arm's isolated `CODEX_HOME`:

    [mcp_servers.oagf_fetch]
    command = "python3"
    args = ["/home/reed/git/open-asi-governance-forum/tools/fetch_tool_mcp.py"]
    env = { OAGF_FETCH_RECEIPTS = "/home/reed/.oagf-shim-ledger/<run>/fetch-receipts.jsonl" }
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SERVER_NAME = "oagf_fetch"
SERVER_VERSION = "0.1.0"
RECEIPT_SCHEMA = "oagf-fetch-receipt-0.1"

MAX_BODY_BYTES = 200_000
MAX_REDIRECTS = 5
TIMEOUT_SECONDS = 30
USER_AGENT = f"oagf-fetch/{SERVER_VERSION} (governance record; read-only)"

ALLOWED_SCHEMES = {"http", "https"}


# ---------------------------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------------------------


class Receipts:
    """Append-only, hash-chained record of every fetch attempt, including refusals."""

    def __init__(self, path: str | None) -> None:
        self.path = path
        self._seq = 0
        self._prev = "0" * 64
        self._lock = threading.Lock()

    def write(self, payload: dict) -> str:
        with self._lock:
            self._seq += 1
            entry = {"schema_version": RECEIPT_SCHEMA, "server_version": SERVER_VERSION,
                     "seq": self._seq, "recorded_at": time.time(),
                     "prev_entry_sha256": self._prev, **payload}
            line = json.dumps(entry, sort_keys=True, ensure_ascii=False)
            self._prev = hashlib.sha256(line.encode("utf-8")).hexdigest()
            if self.path:
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                with open(self.path, "a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
            return self._prev


RECEIPTS = Receipts(os.environ.get("OAGF_FETCH_RECEIPTS"))


# ---------------------------------------------------------------------------------------------
# The guard
# ---------------------------------------------------------------------------------------------


class Blocked(Exception):
    """A URL this tool will not fetch. Carries the reason, which goes into the receipt."""


def check_address(host: str) -> list[str]:
    """Resolve a host and refuse if ANY answer is an address the party must not reach.

    Every resolved address is checked, not just the first: a name that answers with one public
    and one loopback address would otherwise pass the check and connect to whichever the stack
    picked. Refusing on any bad answer is the conservative reading and the right one here.
    """
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as error:
        raise Blocked(f"host {host!r} does not resolve: {error}") from error

    addresses = sorted({info[4][0] for info in infos})
    for raw in addresses:
        address = ipaddress.ip_address(raw)
        if (address.is_private or address.is_loopback or address.is_link_local
                or address.is_multicast or address.is_reserved or address.is_unspecified):
            raise Blocked(
                f"{host!r} resolves to {raw}, which is loopback/private/link-local/reserved. "
                f"This tool may not reach the host it runs on or its network.")
        #  The cloud metadata address is link-local and already caught above; named explicitly
        #  because it is the single most common SSRF target and a reader should see it handled.
        if raw in ("169.254.169.254", "fd00:ec2::254"):
            raise Blocked(f"{host!r} resolves to the cloud metadata address {raw}")
    return addresses


def check_url(url: str) -> tuple[str, list[str]]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise Blocked(f"scheme {parsed.scheme!r} is not permitted; only http and https are")
    if not parsed.hostname:
        raise Blocked("url has no host")
    if parsed.username or parsed.password:
        raise Blocked("url embeds credentials; this tool sends none")
    return parsed.hostname, check_address(parsed.hostname)


# ---------------------------------------------------------------------------------------------
# The fetch
# ---------------------------------------------------------------------------------------------


class NoRedirects(urllib.request.HTTPRedirectHandler):
    """Stop urllib following redirects so each hop can be re-checked before it is taken."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url: str) -> dict:
    """Fetch a URL, re-validating every redirect hop. Returns the receipt body."""
    chain: list[dict] = []
    current = url

    opener = urllib.request.build_opener(NoRedirects)
    for hop in range(MAX_REDIRECTS + 1):
        host, addresses = check_url(current)
        request = urllib.request.Request(current, method="GET", headers={
            "User-Agent": USER_AGENT, "Accept": "*/*"})
        started = time.time()
        try:
            response = opener.open(request, timeout=TIMEOUT_SECONDS)
            status, headers, body = response.status, dict(response.headers), response.read()
        except urllib.error.HTTPError as error:
            status, headers, body = error.code, dict(error.headers), error.read()
        except Exception as error:                                        # noqa: BLE001
            raise Blocked(f"transport error for {current!r}: "
                          f"{type(error).__name__}: {error}") from error

        chain.append({"url": current, "host": host, "resolved": addresses, "status": status,
                      "elapsed_seconds": round(time.time() - started, 3)})

        if status in (301, 302, 303, 307, 308) and headers.get("Location"):
            if hop == MAX_REDIRECTS:
                raise Blocked(f"more than {MAX_REDIRECTS} redirects starting from {url!r}")
            #  Resolve relative Locations against the hop that issued them, then loop so the
            #  next iteration re-runs the full address check on the new target.
            current = urllib.parse.urljoin(current, headers["Location"])
            continue

        raw_sha256 = hashlib.sha256(body).hexdigest()
        text = body.decode("utf-8", errors="replace")
        truncated = len(body) > MAX_BODY_BYTES
        return {
            "requested_url": url,
            "final_url": current,
            "redirect_chain": chain,
            "status": status,
            "content_type": headers.get("Content-Type"),
            "raw_sha256": raw_sha256,
            "raw_byte_length": len(body),
            "truncated": truncated,
            "returned_byte_length": min(len(body), MAX_BODY_BYTES),
            "text": text[:MAX_BODY_BYTES],
        }

    raise Blocked("redirect loop")                                        # pragma: no cover


def do_fetch_url(url: str) -> dict:
    """Run one fetch, write its receipt either way, and shape the model's tool result."""
    try:
        result = fetch(url)
    except Blocked as blocked:
        digest = RECEIPTS.write({"outcome": "REFUSED", "requested_url": url,
                                 "reason": str(blocked)})
        return {"ok": False, "refused": True, "requested_url": url, "reason": str(blocked),
                "receipt_sha256": digest,
                "note": ("This fetch did not happen. Do not describe its target as read, and do "
                         "not infer its contents.")}

    text = result.pop("text")
    digest = RECEIPTS.write({"outcome": "FETCHED", **result})
    out = {"ok": True, "receipt_sha256": digest, **result, "content": text}
    if result["truncated"]:
        out["truncation_notice"] = (
            f"TRUNCATED: {result['raw_byte_length']} bytes were retrieved and the first "
            f"{MAX_BODY_BYTES} are shown. The SHA-256 above is of the FULL body, not of the "
            f"excerpt. Do not claim the document contains nothing beyond this point.")
    return out


# ---------------------------------------------------------------------------------------------
# Minimal MCP over stdio
# ---------------------------------------------------------------------------------------------

TOOLS = [{
    "name": "fetch_url",
    "description": (
        "Fetch a single named http(s) URL and return its text. This resolves a citation; it is "
        "NOT a search engine and cannot find pages by topic. Returns the SHA-256 of the bytes "
        "retrieved along with the content. Only cite a document you actually fetched."),
    "inputSchema": {
        "type": "object",
        "properties": {"url": {"type": "string", "description": "Absolute http(s) URL"}},
        "required": ["url"],
        "additionalProperties": False,
    },
}]


def handle(message: dict) -> dict | None:
    method = message.get("method")
    request_id = message.get("id")

    if method == "initialize":
        params = message.get("params") or {}
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            #  Echo the client's protocol version rather than pinning one, so a Codex release
            #  that moves the version does not silently lose the only tool this arm has.
            "protocolVersion": params.get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}}}

    if method in ("notifications/initialized", "initialized"):
        return None

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = message.get("params") or {}
        if params.get("name") != "fetch_url":
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32601, "message": f"unknown tool {params.get('name')!r}"}}
        url = (params.get("arguments") or {}).get("url")
        if not isinstance(url, str) or not url:
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32602, "message": "argument 'url' must be a non-empty string"}}
        result = do_fetch_url(url)
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            "content": [{"type": "text",
                         "text": json.dumps(result, indent=2, ensure_ascii=False)}],
            "isError": not result["ok"]}}

    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id,
            "error": {"code": -32601, "message": f"unknown method {method!r}"}}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except Exception:                                                 # noqa: BLE001
            continue
        response = handle(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
