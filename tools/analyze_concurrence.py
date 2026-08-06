#!/usr/bin/env python3
"""Measure reviewer redundancy from a coded finding matrix.

Answers one question: how much did the four-reviewer panel add over its members?

WHAT THIS IS NOT
----------------
This is an agreement-on-findings analysis, not an error-correlation analysis.
ChatGPT drew the distinction in review round 01 and it is the load-bearing caveat:

    Construct the cross-model error-correlation matrix, not merely an
    answer-agreement matrix. Models that repeatedly agree when correct may be
    corroborating; models that repeatedly make the same errors share a bias
    channel.
        -- corpus/raw/review-round-01/chatgpt-01.md:365

Computing rho, and therefore n_eff as defined at corpus/deficiencies.md:234,
requires ground truth about which findings were CORRECT. This corpus has none:
the findings were adjudicated by the same interested annotator who is also the
coder. So this script deliberately does NOT emit n_eff. It emits redundancy
statistics, which bound the panel's value from one side only.

Usage:
    python3 tools/analyze_concurrence.py corpus/artifacts/review-round-01/finding-coding.json
"""

from __future__ import annotations

import json
import sys
from itertools import combinations


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def raised_sets(coding):
    """reviewer -> set of finding ids it affirmatively raised."""
    out = {r: set() for r in coding["reviewers"]}
    for finding in coding["findings"]:
        for reviewer, position in finding["positions"].items():
            if position == "raised":
                out[reviewer].add(finding["id"])
    return out


def engaged_sets(coding):
    """reviewer -> set of finding ids it took ANY position on (raised or contra)."""
    out = {r: set() for r in coding["reviewers"]}
    for finding in coding["findings"]:
        for reviewer, position in finding["positions"].items():
            if position in ("raised", "contra"):
                out[reviewer].add(finding["id"])
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    coding = load(sys.argv[1])
    reviewers = coding["reviewers"]
    findings = coding["findings"]
    raised = raised_sets(coding)
    engaged = engaged_sets(coding)

    print(f"Round      : {coding['round']}")
    print(f"Reviewers  : {len(reviewers)}  ({', '.join(reviewers)})")
    print(f"Findings   : {len(findings)} distinct")
    print()

    print("--- Findings raised, per reviewer ---")
    for r in reviewers:
        solo = {f for f in raised[r]
                if sum(1 for x in reviewers if f in raised[x]) == 1}
        print(f"  {r:<16} raised {len(raised[r]):>2}   "
              f"sole-raiser of {len(solo):>2}   engaged {len(engaged[r]):>2}")
    print()

    print("--- Coverage by number of reviewers raising ---")
    hist = {}
    for f in findings:
        n = sum(1 for p in f["positions"].values() if p == "raised")
        hist.setdefault(n, []).append(f["id"])
    for n in sorted(hist):
        ids = ", ".join(hist[n])
        print(f"  raised by {n}: {len(hist[n]):>2} finding(s)   {ids}")
    print()

    singles = len(hist.get(1, []))
    total = len(findings)
    print(f"  {singles}/{total} findings ({100*singles/total:.0f}%) were raised by exactly ONE reviewer.")
    print()

    print("--- Pairwise overlap on raised findings (Jaccard) ---")
    for a, b in combinations(reviewers, 2):
        inter = raised[a] & raised[b]
        union = raised[a] | raised[b]
        j = len(inter) / len(union) if union else 0.0
        print(f"  {a:<16} vs {b:<16} shared {len(inter):>2} / union {len(union):>2}   J = {j:.2f}")
    print()

    print("--- Explicit disagreements (one raised, another took the opposing position) ---")
    disagreements = 0
    for f in findings:
        pro = [r for r, p in f["positions"].items() if p == "raised"]
        con = [r for r, p in f["positions"].items() if p == "contra"]
        if pro and con:
            disagreements += 1
            print(f"  {f['id']}: raised by {', '.join(pro)}")
            print(f"         opposed by {', '.join(con)}")
    print()
    print(f"  {disagreements}/{total} findings drew an explicit split.")
    print()

    print("--- Leave-one-out: findings that would have been LOST ---")
    for r in reviewers:
        others = set()
        for x in reviewers:
            if x != r:
                others |= raised[x]
        lost = sorted(raised[r] - others)
        print(f"  without {r:<16} lose {len(lost):>2}   {', '.join(lost) if lost else '-'}")
    print()

    best = max(reviewers, key=lambda r: len(raised[r]))
    union_all = set()
    for r in reviewers:
        union_all |= raised[r]
    print(f"  Best single reviewer ({best}) raised {len(raised[best])} of {len(union_all)} "
          f"findings the panel raised ({100*len(raised[best])/len(union_all):.0f}%).")
    print()
    print("REMINDER: these are redundancy statistics, not n_eff. See the module docstring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
