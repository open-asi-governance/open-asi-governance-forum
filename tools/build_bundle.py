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
    "review-round-02": {
        "include": [
            "corpus/raw/review-round-01/grok-01.md",
            "corpus/raw/review-round-01/chatgpt-01.md",
            "corpus/raw/review-round-01/gemini-01.md",
            "corpus/raw/review-round-01/claude-fable-5-01.md",
            "spec/icp/icp-v0.1.md",
            "spec/asp/asp-v0.1.md",
            "corpus/deficiencies.md",
            "predictions/predictions.json",
            "record/FDR-0001-founding-deliberation.md",
            "corpus/artifacts/segments.json",
            "CONTRIBUTING.md",
            "corpus/raw/initial-transcript.txt",
        ],
        "exclude": [
            ("README.md, GOVERNANCE.md",
             "Process documents not under review in this round. Available on request."),
            ("tools/",
             "Maintenance code. ChatGPT's round-02 review raises defects in capture_response.py, "
             "validate_provenance.py and contribution.schema.json; request them to assess those "
             "directly rather than through its report."),
        ],
    },
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def last_commit_for(relative: str) -> str:
    """Commit that last changed this file, so a reader can pin what they were shown."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", relative],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
        return result.stdout.strip() or "uncommitted"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unavailable"


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
        "`https://github.com/open-asi-governance/open-asi-governance-forum`, each pinned to the",
        "commit that last changed it and carrying its SHA-256, so you can verify any part",
        "independently later without trusting this bundle.",
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
        parts.append(
            f"- `{relative}` — {path.stat().st_size:,} bytes — "
            f"sha256 `{sha256_of(path)}` — commit `{last_commit_for(relative)[:12]}`"
        )

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
            f"SHA-256 `{sha256_of(path)}` · last changed in commit `{last_commit_for(relative)}`",
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

    # A bundle is a record of what a reviewer was SHOWN, not a derived view of
    # current files. Once a round has used it, capture records cite it by hash,
    # and regenerating it would silently invalidate those citations -- the same
    # immutability rule the raw corpus follows. Delete it deliberately to rebuild.
    if target.exists():
        print(f"REFUSED: {target.relative_to(REPO_ROOT)} already exists.", file=sys.stderr)
        print("A bundle is frozen once a round has used it; capture records cite it by hash.",
              file=sys.stderr)
        print("To rebuild deliberately, delete the file first or use a new round name.",
              file=sys.stderr)
        return 1

    content = build(round_name)
    target.write_text(content, encoding="utf-8")

    print(f"wrote {target.relative_to(REPO_ROOT)}")
    print(f"  {len(content):,} characters  (~{len(content) // 4:,} tokens)")
    print(f"  sha256 {hashlib.sha256(content.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
