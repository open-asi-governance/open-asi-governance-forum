#!/usr/bin/env python3
"""Bundle repository files into one pasteable document for models that cannot browse.

Several model environments block outbound fetches, so a reviewer may have to be
given the material directly. That makes the bundle *supplied context*, and the
provenance standard requires recording exactly what context a model received.
So the bundle is a committed, hash-anchored artifact rather than an ad-hoc paste:
the capture record for any response produced from it references the bundle by
hash, and anyone can regenerate it and confirm the bytes.

Each included file is delimited and carries its own SHA-256, so a reader can
verify any fragment against the repository independently.

Files that are deliberately NOT included are listed in the bundle too. Recording
what a reviewer was not shown matters as much as recording what they were.

Usage:
    python3 tools/build_bundle.py review-round-01

Deterministic: same inputs, byte-identical output.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ordered by the review priority stated in the round-01 prompt.
BUNDLES = {
    "review-round-01": {
        "include": [
            "corpus/deficiencies.md",
            "corpus/artifacts/segments.json",
            "spec/asp/asp-v0.1.md",
            "record/FDR-0001-founding-deliberation.md",
            "predictions/predictions.json",
        ],
        "exclude": [
            ("corpus/raw/initial-transcript.txt",
             "108 KB. The founding record itself. Omitted for length; request it if a "
             "judgement depends on the original wording rather than on the annotation of it."),
            ("corpus/index.md",
             "A generated rendering of corpus/artifacts/segments.json, which is included above "
             "in canonical form. Omitted as redundant."),
            ("GOVERNANCE.md, CONTRIBUTING.md, README.md",
             "Process documents, not under review in this round. Available on request."),
        ],
    },
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fence_for(text: str, path: str) -> str:
    """Choose a fence long enough that nothing inside the file can close it early."""
    longest = 0
    run = 0
    for char in text:
        run = run + 1 if char == "`" else 0
        longest = max(longest, run)
    ticks = "`" * max(3, longest + 1)
    lang = "json" if path.endswith(".json") else "markdown"
    return f"{ticks}{lang}", ticks


def build(round_name: str) -> str:
    spec = BUNDLES[round_name]
    parts: list[str] = [
        f"# Supplied-context bundle — {round_name}",
        "",
        "You are reading this because your environment could not fetch the repository directly.",
        "Every file below is reproduced **verbatim** from",
        "`https://github.com/open-asi-governance/open-asi-governance-forum` at the commit noted",
        "by the operator, with its SHA-256 so you can verify any part independently later.",
        "",
        "This bundle is itself a committed artifact of the record. The provenance entry for your",
        "response will reference it by hash, so what you were shown is part of the permanent",
        "record alongside what you said.",
        "",
        "## Contents",
        "",
    ]

    for relative in spec["include"]:
        path = REPO_ROOT / relative
        parts.append(f"- `{relative}` — {path.stat().st_size:,} bytes — `{sha256_of(path)}`")

    parts.extend(["", "## Deliberately not included", ""])
    for name, reason in spec["exclude"]:
        parts.append(f"- `{name}` — {reason}")

    parts.extend(["", "---", ""])

    for relative in spec["include"]:
        path = REPO_ROOT / relative
        text = path.read_text(encoding="utf-8")
        open_fence, close_fence = fence_for(text, relative)
        parts.extend([
            f"## FILE: `{relative}`",
            "",
            f"SHA-256 `{sha256_of(path)}`",
            "",
            open_fence,
            text.rstrip("\n"),
            close_fence,
            "",
            "---",
            "",
        ])

    parts.extend([
        "## End of bundle",
        "",
        "Reproduce with `python3 tools/build_bundle.py " + round_name + "` against the same commit.",
        "",
    ])
    return "\n".join(parts)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in BUNDLES:
        print(__doc__)
        print("known bundles: " + ", ".join(sorted(BUNDLES)))
        return 2

    round_name = argv[1]
    missing = [f for f in BUNDLES[round_name]["include"] if not (REPO_ROOT / f).exists()]
    if missing:
        print("missing files: " + ", ".join(missing), file=sys.stderr)
        return 1

    target = REPO_ROOT / "record" / f"{round_name}-bundle.md"
    content = build(round_name)
    target.write_text(content, encoding="utf-8")

    print(f"wrote {target.relative_to(REPO_ROOT)}")
    print(f"  {len(content):,} characters  (~{len(content) // 4:,} tokens)")
    print(f"  sha256 {hashlib.sha256(content.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
