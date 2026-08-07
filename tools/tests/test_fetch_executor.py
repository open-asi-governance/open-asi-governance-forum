#!/usr/bin/env python3
"""The conformance suite that DEFINES `fetch-url-v1`. Stdlib only, no network.

    python3 tools/tests/test_fetch_executor.py

External review put it plainly: the conformance suite, not the executor's docstring, is what
defines the profile. Two docstrings in this repository this week asserted guarantees the code did
not implement, and the guard this executor replaces claimed SSRF protection while resolving the
host twice — checking one address and connecting to whatever the second resolution returned.

So every guarantee in that docstring is asserted here against the code, and the cases are the
adversarial ones: rebinding, mixed answers, redirects into private space, ambient proxies,
oversized bodies, charset truncation, malformed arguments, and a citation with no receipt behind
it.

No test reaches the network. Anything needing a server would have to bind loopback, which the
guard refuses by design — so the transport is exercised through injected fakes and the guard
through real resolution of names that are supposed to fail.
"""

from __future__ import annotations

import pathlib
import socket
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import fetch_executor as fe                                               # noqa: E402

PASSED, FAILED = [], []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASSED if condition else FAILED).append(f"{name}{(' — ' + detail) if detail else ''}")


def blocks(name: str, thunk, expect: str = "") -> None:
    try:
        thunk()
    except fe.Blocked as blocked:
        check(name, expect.lower() in str(blocked).lower(), f"blocked with: {str(blocked)[:80]}")
        return
    check(name, False, "was NOT blocked")


# =============================================================================================
# 1. The guard — every address family that must never be reachable
# =============================================================================================

for label, address in [("loopback v4", "127.0.0.1"), ("loopback v6", "::1"),
                       ("private 10/8", "10.0.0.1"), ("private 192.168", "192.168.12.192"),
                       ("private 172.16", "172.17.0.1"), ("link-local", "169.254.1.1"),
                       ("cloud metadata", "169.254.169.254"), ("multicast", "224.0.0.1"),
                       ("unspecified", "0.0.0.0")]:
    blocks(f"refuses {label} ({address})", lambda a=address: fe.vet_address(a, "probe"))

check("permits an ordinary public address", fe.vet_address("93.184.216.34", "example.com") is None)

#  The whole point of the guard on a host that also serves the model.
blocks("refuses the inference server's own address",
       lambda: fe.vet_address("127.0.0.1", "localhost"), "apparatus")


# =============================================================================================
# 2. URL-level refusals
# =============================================================================================

blocks("refuses file:", lambda: fe.check_url("file:///etc/passwd"), "scheme")
blocks("refuses ftp:", lambda: fe.check_url("ftp://example.com/x"), "scheme")
blocks("refuses embedded credentials", lambda: fe.check_url("http://u:p@example.com/"),
       "credentials")
blocks("refuses a url with no host", lambda: fe.check_url("http:///path"), "host")
scheme, host, port, path = fe.check_url("https://example.com/a/b?c=d")
check("preserves the query string", path == "/a/b?c=d", path)
check("infers the default https port", port == 443)


# =============================================================================================
# 3. Mixed DNS answers, and the rebinding hole this executor exists to close
# =============================================================================================

real_getaddrinfo = socket.getaddrinfo


def fake_dns(answers):
    def _fake(host, port, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)) for ip in answers]
    return _fake


socket.getaddrinfo = fake_dns(["93.184.216.34", "127.0.0.1"])
blocks("refuses a host answering with BOTH a public and a loopback address",
       lambda: fe.resolve_and_vet("mixed.example", 443), "loopback")

socket.getaddrinfo = fake_dns(["93.184.216.34"])
address, family, addresses = fe.resolve_and_vet("public.example", 443)
check("returns a vetted address to connect to", address == "93.184.216.34")
check("reports every answer it vetted", addresses == ["93.184.216.34"])

#  The rebinding guarantee: the address is chosen and vetted in ONE place, and connect_pinned
#  uses that address rather than re-resolving. Asserted structurally, since a real rebinding race
#  cannot be staged without a hostile resolver.
import inspect                                                            # noqa: E402
source = inspect.getsource(fe.connect_pinned)
check("connect_pinned vets and pins in one step (no second resolution)",
      "resolve_and_vet(" in source and "create_connection((address" in source)
check("TLS still validates against the hostname, not the pinned address",
      "server_hostname=host" in source)
socket.getaddrinfo = real_getaddrinfo


# =============================================================================================
# 4. Body handling — the three the previous implementation got wrong
# =============================================================================================


class FakeResponse:
    """Yields a body in chunks, like a real socket does."""

    def __init__(self, body: bytes, chunk: int = 1000):
        self.body, self.chunk, self.pos = body, chunk, 0

    def read(self, n=-1):
        if n is None or n < 0:
            n = len(self.body) - self.pos
        out = self.body[self.pos:self.pos + min(n, self.chunk)]
        self.pos += len(out)
        return out


body, truncated, seen = fe.read_capped(FakeResponse(b"x" * 500), 200_000)
check("reads a small body whole", body == b"x" * 500 and not truncated)

body, truncated, seen = fe.read_capped(FakeResponse(b"y" * 50_000), 1_000)
check("caps an oversized body", len(body) == 1_000 and truncated)
check("reports that more existed than was returned", seen > 1_000, f"seen={seen}")

#  Truncation on BYTES, reported in bytes. The old version decoded first and sliced characters
#  while calling the result a byte count, which is wrong for anything non-ASCII.
multibyte = ("é" * 1000).encode("utf-8")          # 2 bytes per character
body, truncated, seen = fe.read_capped(FakeResponse(multibyte), 501)
check("truncates multibyte content by bytes, not characters", len(body) == 501)
check("a byte-truncated multibyte body still decodes without raising",
      isinstance(fe.decode(body, "text/html; charset=utf-8"), str))

check("honours a declared non-UTF-8 charset",
      fe.decode("café".encode("latin-1"), "text/html; charset=latin-1") == "café")
check("falls back to utf-8 on an unknown charset",
      isinstance(fe.decode(b"hi", "text/html; charset=nonsense-99"), str))
check("assumes utf-8 when no charset is declared", fe.decode(b"hi", None) == "hi")


# =============================================================================================
# 5. Tool-call handling and receipts
# =============================================================================================

receipts = []
out = fe.run_tool_call(None, receipts)
check("a missing url argument is refused, not crashed", out["ok"] is False)
check("and the refusal is still recorded", len(receipts) == 1
      and receipts[0]["outcome"] == "REFUSED")

receipts = []
out = fe.run_tool_call("http://127.0.0.1:5001/v1/models", receipts)
check("a party cannot fetch the inference server", out["ok"] is False)
check("the blocked fetch leaves a receipt", receipts[0]["outcome"] == "REFUSED",
      "a refusal with no trace is indistinguishable from a fetch never attempted")
check("and the model is told not to infer the contents",
      "do not infer" in out.get("note", "").lower())


# =============================================================================================
# 6. Citation claims must be falsifiable against the receipts
# =============================================================================================

receipts = [{"outcome": "FETCHED", "requested_url": "https://example.com/a",
             "final_url": "https://example.com/a", "redirect_chain": []},
            {"outcome": "REFUSED", "requested_url": "https://blocked.example/"}]

verdict = fe.sources_supported_by_receipts(
    [{"url": "https://example.com/a"}, {"url": "https://never-fetched.example/"}], receipts)
check("a cited source with a receipt is supported",
      verdict["supported"] == ["https://example.com/a"])
check("a cited source with NO receipt is flagged",
      verdict["unsupported"] == ["https://never-fetched.example/"])
check("and the flag is named for what it is", verdict["claimed_unobserved_fetch"] is True)

clean = fe.sources_supported_by_receipts([{"url": "https://example.com/a/"}], receipts)
check("trailing-slash and case differences do not manufacture a false accusation",
      clean["claimed_unobserved_fetch"] is False)

refused_only = fe.sources_supported_by_receipts([{"url": "https://blocked.example/"}], receipts)
check("a REFUSED receipt does not count as having read the page",
      refused_only["claimed_unobserved_fetch"] is True)

check("citing nothing is not an accusation",
      fe.sources_supported_by_receipts([], receipts)["claimed_unobserved_fetch"] is False)


# =============================================================================================
# 7. The profile is frozen and hashed
# =============================================================================================

check("the profile hash is stable across calls", fe.profile_sha256() == fe.profile_sha256())
check("the tool the model sees says it is not a search engine",
      "not a search engine" in fe.TOOL_SCHEMA["function"]["description"].lower())
check("the tool tells the party not to claim what it did not fetch",
      "only claim" in fe.TOOL_SCHEMA["function"]["description"].lower())
check("the tool schema forbids extra arguments",
      fe.TOOL_SCHEMA["function"]["parameters"]["additionalProperties"] is False)


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
