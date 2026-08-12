#!/usr/bin/env python3
"""Prose triage for absence, novelty, dependence and quantitative-attribution claims.

    python3 tools/check_claims.py              # triage changed prose against HEAD
    python3 tools/check_claims.py --fixtures   # this tool's own negative control
    python3 tools/check_claims.py --baseline   # freeze the legacy debt list

WHAT THIS IS. A **detector**, not an enforcer. It finds sentence-shaped candidates in prose that
has CHANGED, and requires each to receive a disposition. It cannot read, and it cannot tell a true
absence claim from a false one.

WHAT PASSING ESTABLISHES, exactly:

    Detected candidate spans in changed prose each received a disposition.
    Recall over unrestricted prose is UNKNOWN.

It does **not** establish that controls 35, 36 or 41 are satisfied, that the claims are true, or
that no unlabelled claim was published. An external review named the worst failure mode of this
tool before it existed: *`land.py` was green, therefore there were no unsupported claims.* That
sentence must never be written, and the gate is called `prose-triage` rather than `claim-validity`
so that writing it requires ignoring the name.

WHY THESE FOUR RULE FAMILIES. Five self-favouring factual errors were published in this record in
three days. **Not one was a wrong arithmetic result.** Every one was an absence, a novelty claim,
a dependence claim, or a number attributed to a source that did not say it. The families are drawn
from the incidents, and the incidents ship as fixtures in `spec/claims/fixtures/` with their exact
pre-correction wording, recovered from git rather than reconstructed from the corrections.

WHY A DISPOSITION AND NOT A LABEL. Requiring a label would let an author satisfy the gate by
typing one. A disposition binds to the exact text hash: editing the sentence invalidates it, so a
claim cannot be relabelled by rewording. There is deliberately **no cap and no expiry** on
dispositions -- a cap makes the first N unsupported claims free, and an expiry creates renewal work
without creating evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DISPOSITIONS = REPO_ROOT / "record" / "claims" / "dispositions.jsonl"
LEGACY = REPO_ROOT / "record" / "claims" / "legacy-unreviewed.json"
FIXTURES = REPO_ROOT / "spec" / "claims" / "fixtures"

DETECTOR_VERSION = "0.1"

#  Prose surfaces only. Code comments are excluded deliberately: they are not published claims,
#  and including them buries the signal under a decade of explanatory text.
SCANNED = (".md",)
#  `record/executive/codex-transcripts/` holds VERBATIM third-party output, hash-stamped by
#  codex_call.py. It is raw material like `corpus/`, not this project's claims: a reviewer's
#  sentences are quotation by construction and dispositioning them would be this workbench
#  adjudicating someone else's words. Excluded after one transcript produced 90 of 101
#  candidates and would have forced a bulk rubber-stamp -- the snooze button this gate is
#  built to avoid.
SKIP_PARTS = ("corpus/", "docs/", "record/claims/", "spec/claims/fixtures/", "third-party/",
              "record/executive/codex-transcripts/")
#
#  `record/controls/` WAS SKIPPED HERE ON 2026-08-12 AND THE SKIP WAS WRONG. The generated
#  control-application table tripped this gate on every regeneration, content-keyed dispositions
#  would go stale each time a number moved, and exempting the directory made that stop. Codex
#  refused it on two grounds and the second is the one that matters: scanning the file finds 16
#  undispositioned spans, and several are not generator churn but FALSE CLAIMS -- "no refused
#  proposal has yet been re-proposed" and "no rollback mechanism exists", both contradicted by
#  this repository's own self-application table. The exemption would have published them.
#
#  Kept as a comment rather than deleted, because the reasoning that produced it was plausible
#  and someone will produce it again: the artifact was new, it was mine, and the exemption made
#  my own work pass. Churn in a disposition is review pressure, not a defect.

#  Narrow dispositions. A general "acknowledged" bucket is a snooze button; these each say
#  something specific about WHY the span is not an unsupported claim.
VALID_DISPOSITIONS = (
    "labelled",                 # carries its evidence: corpus, query, date, or a record path
    "quotation_of_false_claim", # quoting a claim in order to correct it
    "hypothetical",             # "if no verifier existed…"
    "negated",                  # asserts the opposite
    "detector_false_positive",  # not a claim of this kind at all
    "narrowed",                 # the claim was removed or reduced rather than supported
)

RULES: dict[str, tuple[str, ...]] = {
    #  ABSENCE -- two of the five incidents. "A scan that cannot see a file reports absence."
    "absence": (
        r"\bno (?:prior art|verifier|mechanical test|record|evidence|such|other|general one)\b",
        r"\bnothing (?:here|in this|else|exists|prevents|constrains)\b",
        r"\bnobody (?:has|runs|does|checks|looks)\b",
        r"\b(?:does|do|did) not exist\b",
        r"\bnone (?:has|have|of (?:them|these|the))\b",
        r"\bnone recorded\b",
        #  Added after historical-02 was MISSED by the first rule set. "no clear path to a
        #  verifier" carries no absence keyword this detector knew. The general shape is
        #  "no <adjective> <noun-of-means>", which is how an absence claim hides in a sentence
        #  that reads as a caveat.
        r"\bno (?:\w+ ){0,2}(?:path|route|way|means|method|mechanism|test|check|verifier)\b",
        r"\bnever been (?:observed|attempted|checked|claimed)\b",
        r"\bunclaimed\b", r"\bno one (?:has|else)\b",
        r"\bis not (?:claimed|recorded|documented) anywhere\b",
        #  SELF-REFERENTIAL ABSENCE -- added 2026-08-11 after a page of new prose full of
        #  "we had never searched" and "has not been established" produced ZERO candidates.
        #  These are usually TRUE absence claims, which is the point: a true one still has to
        #  carry its evidence, and this is the shape the workbench reaches for when confessing.
        r"\bnever (?:searched|looked|checked|run|recorded|been done|asked)\b",
        r"\b(?:had|has|have) never\b",
        r"\bno (?:such )?search\b",
        r"\b(?:has|have|had|was|were) not been (?:established|checked|recorded|searched|"
        r"verified|attempted|measured|run)\b",
        r"\bwe have not (?:checked|searched|established|verified|looked)\b",
        r"\bnot (?:yet )?established\b",
    ),
    #  NOVELTY -- control 35. "almost nobody runs it" was the load-bearing sentence.
    "novelty": (
        r"\b(?:is|are) (?:new|novel|original|unique|the first)\b",
        r"\bnot (?:new|novel)\b",
        r"\bfirst (?:thing|time|attempt|result) (?:in|to|that)\b",
        r"\bprior art\b", r"\balmost nobody\b", r"\bno[- ]one else\b",
    ),
    #  DEPENDENCE -- control 41. "two independent codebases" when both were one implementer.
    "dependence": (
        r"\b(?:two|three|four|five|\d+) (?:independent|unrelated|separate|distinct)\b",
        r"\bindependent(?:ly)? (?:confirm|verif|replicat|implement|derive|arriv)",
        r"\bunanimous\b", r"\bconsensus\b",
        r"\ball (?:five|four|three|\d+) (?:parties|models|agreed)\b",
        r"\bcorroborat", r"\bagreement (?:between|among|across)\b",
    ),
    #  QUANTITATIVE ATTRIBUTION -- Codex's fourth family, and the one that covers "4h37m of
    #  undetected outage" and "0 searches across 83 tool calls". Neither is governed by 35/36/41,
    #  which is why the three controls the custodian named do not cover the five incidents.
    "quantitative": (
        r"\b\d+ of \d+\b", r"\b\d+/\d+\b",
        r"\b\d+h\d+m\b", r"\b\d+ (?:hours?|minutes?) of\b",
        r"\b(?:zero|0) (?:searches|calls|results|hits|records|files)\b",
        r"\b\d+ (?:tool calls|samples|rounds|agents|records|files|checks)\b",
    ),
}
COMPILED = {kind: [re.compile(p, re.I) for p in pats] for kind, pats in RULES.items()}


def sentences(text: str) -> list[str]:
    """Rough sentence split. Deliberately crude: a missed split yields a longer span, not a
    missed candidate, and over-splitting costs only noise."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)          # fenced code is not prose
    parts = re.split(r"(?<=[.!?])\s+|\n\s*\n|\n[-*|]\s*", text)
    return [p.strip() for p in parts if p.strip()]


def span_id(path: str, sentence: str) -> str:
    """Bind a disposition to the exact text. Rewording invalidates it, which is the point."""
    normalised = " ".join(sentence.split())
    return hashlib.sha256(f"{path}\n{normalised}".encode()).hexdigest()[:16]


def candidates_in(path: str, text: str) -> list[dict]:
    found = []
    for sentence in sentences(text):
        kinds = sorted(k for k, pats in COMPILED.items()
                       if any(p.search(sentence) for p in pats))
        if kinds:
            found.append({"id": span_id(path, sentence), "path": path, "kinds": kinds,
                          "text": " ".join(sentence.split())[:300]})
    return found


def prose_files() -> list[Path]:
    out = []
    for path in REPO_ROOT.rglob("*"):
        if path.suffix not in SCANNED or not path.is_file():
            continue
        rel = str(path.relative_to(REPO_ROOT))
        if rel.startswith(".") or any(part in rel for part in SKIP_PARTS):
            continue
        out.append(path)
    return sorted(out)


def changed_files() -> list[Path] | None:
    """Prose changed against HEAD. None when git is unavailable -- in which case we scan all and
    say so, rather than scanning nothing and reporting clean."""
    try:
        result = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=REPO_ROOT,
                                capture_output=True, text=True, check=True)
        staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=REPO_ROOT,
                                capture_output=True, text=True, check=True)
        #  UNTRACKED TOO. `git diff` never mentions a file that has never been added, so the
        #  first version of this gate passed green over two brand-new findings documents it had
        #  not opened -- a new document being precisely where a new claim appears. Caught by
        #  asking what the detector actually scanned rather than reading its exit code.
        untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                                   cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    except Exception:                                                    # noqa: BLE001
        return None
    names = set(result.stdout.split()) | set(staged.stdout.split()) | set(untracked.stdout.split())
    return [REPO_ROOT / n for n in sorted(names)
            if (REPO_ROOT / n).suffix in SCANNED and (REPO_ROOT / n).is_file()
            and not any(part in n for part in SKIP_PARTS)]


def load_dispositions() -> dict[str, dict]:
    if not DISPOSITIONS.is_file():
        return {}
    out = {}
    for line in DISPOSITIONS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        record = json.loads(line)
        out[record["id"]] = record
    return out


def load_legacy() -> set[str]:
    """Frozen debt, not acknowledgement. Spans present at the baseline commit are excluded from
    the gate so it can be adopted at all -- and the file is named so nobody mistakes it for
    conformance."""
    if not LEGACY.is_file():
        return set()
    return set(json.loads(LEGACY.read_text(encoding="utf-8")).get("spans", []))


def triage(paths: list[Path], scanned_all: bool) -> int:
    dispositions, legacy = load_dispositions(), load_legacy()
    undisposed, seen = [], 0
    for path in paths:
        rel = str(path.relative_to(REPO_ROOT))
        for candidate in candidates_in(rel, path.read_text(encoding="utf-8", errors="replace")):
            seen += 1
            if candidate["id"] in legacy:
                continue
            record = dispositions.get(candidate["id"])
            if record and record.get("disposition") in VALID_DISPOSITIONS:
                continue
            if record:
                undisposed.append((candidate, f"disposition "
                                              f"{record.get('disposition')!r} is not one of "
                                              f"{VALID_DISPOSITIONS}"))
            else:
                undisposed.append((candidate, "no disposition"))

    print(f"  detector {DETECTOR_VERSION}; {len(paths)} prose file(s) "
          f"{'(ALL -- git unavailable)' if scanned_all else '(changed against HEAD)'}; "
          f"{seen} candidate span(s); {len(legacy)} frozen as legacy debt")
    if undisposed:
        for candidate, why in undisposed[:25]:
            print(f"\n  \033[31m✗\033[0m {candidate['path']}  [{','.join(candidate['kinds'])}]  "
                  f"{why}\n      {candidate['text'][:150]}\n      id: {candidate['id']}")
        if len(undisposed) > 25:
            print(f"\n  … and {len(undisposed) - 25} more")
        print(f"\n  {len(undisposed)} candidate span(s) with no disposition. Add one to "
              f"{DISPOSITIONS.relative_to(REPO_ROOT)}, or narrow the claim.", file=sys.stderr)
        print(f"  Valid dispositions: {', '.join(VALID_DISPOSITIONS)}", file=sys.stderr)
        return 1

    #  THE NONCLAIM, PRINTED ON EVERY SUCCESS. An external review predicted that a green result
    #  here would be restated as "there were no unsupported claims". It is not that.
    print("\n  Detected candidate spans in changed prose each received a disposition.")
    print("  Recall over unrestricted prose: UNKNOWN.")
    print("  This does NOT establish that controls 35, 36 or 41 are satisfied, that any claim is")
    print("  true, or that no unlabelled claim was published.")
    return 0


def run_fixtures() -> int:
    """This tool's own negative control (control 2), on four populations (control 45):
    historical false accepts, must-flag cases, must-NOT-flag prose, and known gaps."""
    if not FIXTURES.is_dir():
        print(f"  no fixtures at {FIXTURES.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 2
    failures = 0
    for path in sorted(FIXTURES.glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        hits = candidates_in("fixture", case["text"])
        kinds = sorted({k for h in hits for k in h["kinds"]})
        expected = case.get("must_flag")
        if expected is True and not hits:
            print(f"  \033[31mMISSED\033[0m {path.name} — {case.get('why', '')[:90]}")
            failures += 1
        elif expected is False and hits:
            print(f"  \033[31mFLAGGED\033[0m {path.name} — must not flag; got {kinds}")
            failures += 1
        else:
            state = "flagged" if hits else "clean"
            print(f"  \033[32m{state}\033[0m {path.name}  {kinds if hits else ''}")
    gaps = FIXTURES / "known-gaps"
    if gaps.is_dir():
        print("\n  KNOWN GAPS — claims this detector does not catch:")
        for path in sorted(gaps.glob("*.json")):
            case = json.loads(path.read_text(encoding="utf-8"))
            hits = candidates_in("gap", case["text"])
            state = "still missed (as expected)" if not hits else \
                    "NOW CAUGHT — move it into fixtures/"
            print(f"    {path.name}: {state}\n      {case.get('why', '')[:120]}")
    print()
    if failures:
        print(f"  {failures} fixture(s) behaved wrongly. THIS DETECTOR IS NOT FIT TO GATE.",
              file=sys.stderr)
        return 1
    historical = len(list(FIXTURES.glob("historical-*.json")))
    print(f"  historical incident sensitivity: {historical}/{historical} of the published errors")
    print("  are flagged as candidates. That is SENSITIVITY ON KNOWN CASES, tuned after the fact.")
    print("  It is not recall, and it is not evidence about the errors nobody has found yet.")
    return 0


def write_baseline() -> int:
    spans = []
    for path in prose_files():
        rel = str(path.relative_to(REPO_ROOT))
        spans += [c["id"] for c in
                  candidates_in(rel, path.read_text(encoding="utf-8", errors="replace"))]
    LEGACY.parent.mkdir(parents=True, exist_ok=True)
    LEGACY.write_text(json.dumps({
        "_what_this_is": "DEBT, not acknowledgement and not conformance. Candidate spans present "
                         "when the detector was adopted, frozen so the gate could be turned on at "
                         "all. Every one is an unreviewed claim. Removing entries is progress; "
                         "adding entries is not permitted.",
        "detector_version": DETECTOR_VERSION,
        "spans": sorted(set(spans)),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"  froze {len(set(spans))} legacy candidate span(s) as debt")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--fixtures", action="store_true", help="run this tool's negative control")
    parser.add_argument("--baseline", action="store_true", help="freeze the legacy debt list")
    parser.add_argument("--all", action="store_true", help="scan every prose file, not just changed")
    args = parser.parse_args()

    if args.fixtures:
        return run_fixtures()
    if args.baseline:
        return write_baseline()
    changed = None if args.all else changed_files()
    if changed is None:
        return triage(prose_files(), scanned_all=True)
    return triage(changed, scanned_all=False)


if __name__ == "__main__":
    raise SystemExit(main())
