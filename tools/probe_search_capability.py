#!/usr/bin/env python3
"""Probe what the round's search provider can retrieve of this record. Four endpoints.

    EXA_API_KEY=... python3 tools/probe_search_capability.py
    EXA_API_KEY=... python3 tools/probe_search_capability.py --json

**NOT deterministic and NOT part of rebuild.py.** It calls a third-party API whose index
changes, so two runs on different days can disagree — which is the point. A capability claim
about a provider is a measurement with a date on it, not a property.

Why this exists
---------------
The round prompt asserted, for months, that the site "is not in the index it queries". That is a
causal claim about a provider's internals and nothing had ever tested it. Four probes on
2026-08-08 do not support it:

    /search  includeDomains=[the site]   0 results
    /search  unrestricted, by name       5 results, all other organisations
    /contents  urls=[the exact URL]      1 result, the page's text
    /findSimilar  url=the exact URL      5 neighbours

The failure is real and reproducible; the explanation was not. What the record can say is that
those searches returned nothing, and that a different endpoint of the same provider returned
text when handed the address.

What a green run does NOT mean
-------------------------------
That a party can read the record. The party is given a search that takes a question; `/contents`
is a different endpoint and is not exposed to it. Conflating provider capability with party
capability is the error this script was written to stop repeating, so its output separates them
and refuses to summarise them into one verdict.

A `/contents` call returning bytes also authenticates nothing. The page is served from a
repository the operator controls, so what comes back is the operator's copy of the operator's
record.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.exa.ai"
SITE_URL = "https://open-asi-governance.github.io/open-asi-governance-forum/"
SITE_DOMAIN = "open-asi-governance.github.io"


def call(path: str, body: dict, key: str, timeout: int = 60) -> dict:
    request = urllib.request.Request(
        f"{ENDPOINT}{path}", data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-api-key": key})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        #  Read the body. A bare status says the provider refused us, not what it objected to.
        detail = ""
        try:
            detail = error.read().decode("utf-8", "replace")[:400]
        except Exception:                                           # noqa: BLE001
            detail = "<body unreadable>"
        return {"error": f"HTTP {error.code}", "detail": detail}
    except Exception as error:                                      # noqa: BLE001
        return {"error": f"{type(error).__name__}: {error}"}


def probe(key: str) -> list[dict]:
    out = []

    r = call("/search", {"query": "Open ASI Governance Forum deliberation record",
                         "includeDomains": [SITE_DOMAIN], "numResults": 5}, key)
    out.append({"endpoint": "/search", "input": f"query + includeDomains=[{SITE_DOMAIN}]",
                "n_results": len(r.get("results") or []),
                "urls": [x.get("url") for x in (r.get("results") or [])],
                "error": r.get("error"),
                "supports": "This query, so configured, returned this many results on this date.",
                "does_not_support": ("That the site is absent from any index. A failed query is "
                                     "a failed query.")})

    r = call("/search", {"query": "Open ASI Governance Forum deliberation record frontier models",
                         "numResults": 5}, key)
    out.append({"endpoint": "/search", "input": "unrestricted query naming this forum",
                "n_results": len(r.get("results") or []),
                "urls": [x.get("url") for x in (r.get("results") or [])],
                "error": r.get("error"),
                "supports": "What an unrestricted semantic query surfaces instead.",
                "does_not_support": "Anything about why."})

    r = call("/contents", {"urls": [SITE_URL], "text": True}, key)
    results = r.get("results") or []
    text = (results[0].get("text") or "") if results else ""
    out.append({"endpoint": "/contents", "input": "urls=[the exact site URL]",
                "n_results": len(results), "chars": len(text),
                "title": results[0].get("title") if results else None,
                "error": r.get("error"),
                "supports": "The provider returned text when supplied that URL on this date.",
                "does_not_support": ("That the page is generally reachable, that the bytes are "
                                     "authentic, that they match what is published, or that they "
                                     "are complete. THIS ENDPOINT IS NOT EXPOSED TO A PARTY.")})

    r = call("/findSimilar", {"url": SITE_URL, "numResults": 5}, key)
    out.append({"endpoint": "/findSimilar", "input": "url=the exact site URL",
                "n_results": len(r.get("results") or []),
                "urls": [x.get("url") for x in (r.get("results") or [])],
                "error": r.get("error"),
                "supports": "The call returned results.",
                "does_not_support": ("That the provider holds an index representation of the "
                                     "page. Neighbours could come from a representation built on "
                                     "demand, from cached content, or from URL metadata. The "
                                     "provider does not document which, so nothing is claimed.")})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit the raw probe record")
    args = parser.parse_args()

    key = os.environ.get("EXA_API_KEY")
    if not key:
        print("EXA_API_KEY is not set. This probe calls a third-party API and cannot be "
              "simulated: a capability claim with no call behind it is what it exists to "
              "replace.", file=sys.stderr)
        return 2

    probes = probe(key)
    if args.json:
        print(json.dumps({"probed": probes}, indent=2, ensure_ascii=False))
        return 0

    for p in probes:
        detail = f"{p['n_results']} result(s)"
        if p.get("chars"):
            detail += f", {p['chars']} chars, title {p.get('title')!r}"
        print(f"  {p['endpoint']:14} {p['input'][:44]:44} {detail}")
        if p.get("error"):
            print(f"                 error: {p['error']}")
        for url in (p.get("urls") or [])[:3]:
            print(f"                 - {url[:74]}")
    print("\n  These describe the PROVIDER. The party is given a search that takes a question;")
    print("  /contents is a different endpoint and is not exposed to it. A fetch that returns")
    print("  bytes authenticates nothing: the page is served from a repository the operator")
    print("  controls, so it is the operator's copy of the operator's record.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
