#!/usr/bin/env python3
"""`fetch-url-v1` — the one guarded URL fetcher every solicited party shares.

**Not maintenance code.** It runs only while a party is being solicited; `rebuild.py` never
calls it. It is deterministic given a response, but the network is not, so nothing derived from
the corpus depends on it.

Why one executor and not one per arm
------------------------------------
Routed parties (`solicit_api`) and the locally-served party (`solicit_local`) must resolve a
citation the *same* way, or their answers are not comparable and the record cannot say why they
differ. Comparability requires that this be literally the same code, not two implementations that
agree today. The capability is frozen and hashed as `fetch-url-v1`; a change to the tool schema,
the limits, or the loop protocol is a new profile and therefore a new party under D-09.

Why a party needs it at all
---------------------------
D-52: no party has ever read this record. Search is retrieval-by-resemblance and the site is not
in the index a router queries. Measured 2026-08-07: no OpenRouter web engine — `exa`, `native`,
`parallel`, `perplexity` — fetches a named URL, and the plugin exposes no URL-fetch mode at all.
Every party tested *will* call a tool when offered one. So the repair was never a better search;
it was a tool.

The guard, and the one it replaces
----------------------------------
An earlier guard (`fetch_tool_mcp.py`) resolved the host, checked the addresses, and then handed
the URL to `urllib` — **which resolved it again**. Between those two resolutions a hostile or
merely rebinding DNS answer could change, so the address checked was not necessarily the address
connected to. That is textbook DNS rebinding and the guard's docstring claimed protection it did
not provide.

Here the vetted address is the address used: the socket is connected to that literal IP, and for
HTTPS the TLS handshake still carries the original hostname for SNI and certificate validation,
so pinning costs no authentication. Every redirect hop is re-resolved and re-vetted the same way.

What else it refuses or bounds, each because the absence bit somewhere
----------------------------------------------------------------------
* `http`/`https` only; no credentials in the URL; ambient proxies disabled, since a proxy would
  make the pinned address meaningless.
* Loopback, private, link-local, multicast, reserved, unspecified and cloud-metadata addresses.
  This matters most for the LOCAL party: the executor runs on the host that serves it, where
  `127.0.0.1:5001` is the inference server and the ledger sits on the filesystem. The guard is
  what stops a party reading the apparatus that measures it.
* The body is read **incrementally against a cap**, not slurped and then trimmed.
* Truncation happens on BYTES and is reported in bytes; the previous version decoded first and
  sliced characters while calling the result a byte count.
* The declared charset is honoured rather than assuming UTF-8.
* A wall-clock deadline spans the whole fetch including redirects; a socket timeout does not.
* A refusal that happens after redirects keeps the partial chain, because where it was refused is
  the interesting part.

What a receipt establishes, and what it does not
------------------------------------------------
A receipt records what was **delivered to the model**: the requested URL, every hop, the status,
the SHA-256 of the raw bytes, and the exact text handed over. It does not establish that the model
read it, attended to it, or that anything in it is true. `sources_supported_by_receipts()` exists
so a claim of having read something can be *falsified* — a party citing a URL with no matching
receipt is a finding, and the point of recording refusals is that a blocked fetch which left no
trace is indistinguishable from a fetch never attempted.
"""

from __future__ import annotations

import hashlib
import http.client
import ipaddress
import json
import pathlib
import re
import socket
import ssl
import time
import urllib.parse

PROFILE = "fetch-url-v1"

MAX_BODY_BYTES = 200_000
MAX_REDIRECTS = 5
DEADLINE_SECONDS = 45
SOCKET_TIMEOUT = 20
USER_AGENT = f"oagf-{PROFILE} (governance record; read-only)"

#  The tool as the model sees it. Part of the frozen profile: change this and the party changes.
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_url",
        "description": (
            "Fetch one public http(s) URL and return its text. This RESOLVES A CITATION — it is "
            "not a search engine and cannot find pages by topic. You are given the SHA-256 of the "
            "bytes retrieved. Only claim to have read a document you actually fetched."),
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "Absolute http(s) URL"}},
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}


def profile_sha256() -> str:
    """Hash of the frozen capability, for the round record to cite.

    Binds the EXECUTOR SOURCE as well as the constants. The docstring says a change to the loop
    or the limits is a new profile and therefore a new party; hashing only the constants left
    that claim unenforced, so an executor rewrite could have kept the same profile id.
    """
    source = pathlib.Path(__file__).read_bytes()
    frozen = {"profile": PROFILE, "tool": TOOL_SCHEMA, "max_body_bytes": MAX_BODY_BYTES,
              "max_redirects": MAX_REDIRECTS, "deadline_seconds": DEADLINE_SECONDS,
              "executor_sha256": hashlib.sha256(source).hexdigest()}
    return hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()


class Blocked(Exception):
    """A URL this executor will not fetch. The reason goes into the receipt."""


# ---------------------------------------------------------------------------------------------
# The guard
# ---------------------------------------------------------------------------------------------

METADATA_ADDRESSES = {"169.254.169.254", "fd00:ec2::254", "100.100.100.200"}


def vet_address(raw: str, host: str) -> None:
    address = ipaddress.ip_address(raw)
    if (address.is_private or address.is_loopback or address.is_link_local
            or address.is_multicast or address.is_reserved or address.is_unspecified
            or raw in METADATA_ADDRESSES):
        raise Blocked(f"{host!r} resolves to {raw}, which is loopback/private/link-local/"
                      f"reserved/metadata. This executor may not reach the host it runs on, its "
                      f"network, or the apparatus measuring the party.")


def resolve_and_vet(host: str, port: int) -> tuple[str, int, list[str]]:
    """Resolve, vet EVERY answer, and return one vetted address to connect to.

    Every answer is checked, not just the one chosen: a name answering with one public and one
    loopback address would otherwise pass while the stack connected to whichever it preferred.
    """
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as error:
        raise Blocked(f"host {host!r} does not resolve: {error}") from error
    addresses = sorted({info[4][0] for info in infos})
    for raw in addresses:
        vet_address(raw, host)
    return addresses[0], socket.AF_INET6 if ":" in addresses[0] else socket.AF_INET, addresses


def connect_pinned(scheme: str, host: str, port: int, deadline: float):
    """Connect to the VETTED address itself, keeping TLS bound to the hostname.

    The address checked must be the address used. Resolving, checking, and then letting a client
    library resolve again leaves a window in which the answer can change — the rebinding hole in
    the guard this replaces.
    """
    address, family, _ = resolve_and_vet(host, port)
    remaining = max(1.0, deadline - time.monotonic())
    sock = socket.create_connection((address, port), timeout=min(SOCKET_TIMEOUT, remaining))
    if scheme == "https":
        context = ssl.create_default_context()
        #  server_hostname keeps SNI and certificate validation against the NAME while the
        #  socket is pinned to the vetted ADDRESS. Pinning costs no authentication.
        sock = context.wrap_socket(sock, server_hostname=host)
    connection = http.client.HTTPConnection(host, port, timeout=min(SOCKET_TIMEOUT, remaining))
    connection.sock = sock
    return connection


def check_url(url: str) -> tuple[str, str, int, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise Blocked(f"scheme {parsed.scheme!r} is not permitted; only http and https are")
    if not parsed.hostname:
        raise Blocked("url has no host")
    if parsed.username or parsed.password:
        raise Blocked("url embeds credentials; this executor sends none")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    return parsed.scheme, parsed.hostname, port, path


def read_capped(response, cap: int) -> tuple[bytes, bool, int]:
    """Read incrementally against a cap. Returns (bytes, truncated, bytes_seen).

    `response.read()` with no argument is unbounded, so a hostile or merely large document could
    exhaust memory before any limit applied.
    """
    chunks, total = [], 0
    while total <= cap:
        chunk = response.read(min(65536, cap + 1 - total))
        if not chunk:
            return b"".join(chunks), False, total
        chunks.append(chunk)
        total += len(chunk)
    body = b"".join(chunks)[:cap]
    #  Drain a little further only to learn whether more existed, bounded so this cannot hang.
    extra = response.read(65536)
    return body, True, total + len(extra)


def decode(body: bytes, content_type: str | None) -> str:
    """Honour the declared charset. Assuming UTF-8 mangles anything else."""
    charset = "utf-8"
    if content_type:
        match = re.search(r"charset=([A-Za-z0-9_.\-]+)", content_type)
        if match:
            charset = match.group(1)
    try:
        return body.decode(charset, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------------------------
# The fetch
# ---------------------------------------------------------------------------------------------


def fetch(url: str) -> dict:
    """Fetch one URL under the guard. Returns a receipt body, or raises Blocked.

    Every redirect hop is re-resolved and re-vetted: a public host redirecting to `127.0.0.1` is
    the ordinary way an SSRF guard is defeated, and checking only the first URL would miss it.
    """
    deadline = time.monotonic() + DEADLINE_SECONDS
    chain: list[dict] = []
    current = url

    for hop in range(MAX_REDIRECTS + 1):
        if time.monotonic() > deadline:
            raise Blocked(f"deadline of {DEADLINE_SECONDS}s exceeded after {len(chain)} hop(s)",
                          )
        scheme, host, port, path = check_url(current)
        _, _, addresses = resolve_and_vet(host, port)
        started = time.time()
        try:
            connection = connect_pinned(scheme, host, port, deadline)
            connection.request("GET", path, headers={
                "Host": host, "User-Agent": USER_AGENT, "Accept": "*/*", "Connection": "close"})
            response = connection.getresponse()
            status = response.status
            headers = {k.lower(): v for k, v in response.getheaders()}
            location = headers.get("location")
            if status in (301, 302, 303, 307, 308) and location:
                chain.append({"url": current, "resolved": addresses, "status": status,
                              "elapsed_seconds": round(time.time() - started, 3)})
                connection.close()
                if hop == MAX_REDIRECTS:
                    raise Blocked(f"more than {MAX_REDIRECTS} redirects from {url!r}",
                                  )
                current = urllib.parse.urljoin(current, location)
                continue
            body, truncated, seen = read_capped(response, MAX_BODY_BYTES)
            connection.close()
        except Blocked:
            raise
        except Exception as error:                                        # noqa: BLE001
            #  Keep the chain: WHERE it failed is the interesting part, and the previous
            #  implementation discarded it on any post-redirect refusal.
            raise Blocked(f"transport error at {current!r} after {len(chain)} hop(s): "
                          f"{type(error).__name__}: {error}") from error

        chain.append({"url": current, "resolved": addresses, "status": status,
                      "elapsed_seconds": round(time.time() - started, 3)})
        text = decode(body, headers.get("content-type"))
        return {
            "requested_url": url,
            "final_url": current,
            "redirect_chain": chain,
            "status": status,
            "content_type": headers.get("content-type"),
            "raw_sha256": hashlib.sha256(body).hexdigest(),
            "returned_byte_length": len(body),
            "bytes_seen": seen,
            "truncated": truncated,
            "text": text,
        }
    raise Blocked("redirect loop")                                        # pragma: no cover


def record_delivery(receipts: list, delivered: str) -> None:
    """Record the bytes the CALLER actually put in the tool message.

    The executor returns full text; the solicitation tool serialises it into a tool message and
    caps that. Without this the receipt claimed to hold "the exact text handed to the model"
    while the model saw less — a difference invisible to any reader.
    """
    if receipts and receipts[-1].get("outcome") == "FETCHED":
        receipts[-1]["delivered_char_length"] = len(delivered)
        receipts[-1]["delivered_sha256"] = hashlib.sha256(delivered.encode("utf-8")).hexdigest()
        receipts[-1]["delivered_in_full"] = (
            len(delivered) >= len(receipts[-1].get("text_given_to_model") or ""))


def run_tool_call(url, receipts: list) -> dict:
    """Execute one `fetch_url` call, append a receipt either way, and shape the model's result.

    A refusal is a receipt too. A blocked fetch that left no trace would be indistinguishable
    from a fetch never attempted, and the difference is exactly what a reader needs.
    """
    if not isinstance(url, str) or not url.strip():
        receipts.append({"outcome": "REFUSED", "requested_url": url,
                         "reason": "the `url` argument was missing or not a string"})
        return {"ok": False, "error": "url must be a non-empty string"}
    try:
        result = fetch(url)
    except Blocked as blocked:
        receipts.append({"outcome": "REFUSED", "requested_url": url, "reason": str(blocked)})
        return {"ok": False, "refused": True, "requested_url": url, "reason": str(blocked),
                "note": ("This fetch did not happen. Do not describe its target as read and do "
                         "not infer its contents.")}
    text = result["text"]
    #  The receipt carries the EXACT text handed to the model, not only a digest of the body.
    #  Without it a reader cannot tell what the party was actually shown.
    receipts.append({"outcome": "FETCHED", "text_given_to_model": text,
                     **{k: v for k, v in result.items() if k != "text"}})
    out = {"ok": True, "url": result["final_url"], "status": result["status"],
           "raw_sha256": result["raw_sha256"], "content": text}
    if result["truncated"]:
        out["truncation_notice"] = (
            f"TRUNCATED: at least {result['bytes_seen']} bytes exist and the first "
            f"{result['returned_byte_length']} are shown. The SHA-256 is of the SHOWN bytes. "
            f"Do not claim the document contains nothing beyond this point.")
    return out


def normalise_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url.strip())
    netloc = parsed.netloc.lower().rstrip(":80").rstrip(":443")
    path = (parsed.path or "/").rstrip("/") or "/"
    return f"{parsed.scheme.lower()}://{netloc}{path}"


def sources_supported_by_receipts(sources, receipts: list) -> dict:
    """Which cited sources are backed by a successful receipt — and which are not.

    A receipt proves delivery, not reading. What this catches is the opposite failure: a party
    that says "I verified X" with no fetch of X in its own log. That is the failure this arm
    exists to expose, so it is computed rather than trusted.
    """
    fetched = set()
    for receipt in receipts:
        if receipt.get("outcome") != "FETCHED":
            continue
        fetched.add(normalise_url(receipt.get("requested_url", "")))
        fetched.add(normalise_url(receipt.get("final_url", "")))
        for hop in receipt.get("redirect_chain") or []:
            fetched.add(normalise_url(hop.get("url", "")))
    supported, unsupported = [], []
    for source in (sources or []):
        url = source.get("url") if isinstance(source, dict) else str(source)
        if not url:
            continue
        (supported if normalise_url(url) in fetched else unsupported).append(url)
    return {"supported": supported, "unsupported": unsupported,
            "claimed_unobserved_fetch": bool(unsupported)}
