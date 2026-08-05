#!/usr/bin/env python3
"""Build the SHA-256 manifest that anchors every raw corpus artifact.

The manifest is the mechanism by which "the raw record is never edited after
commit" becomes checkable rather than merely promised. Any later edit to a raw
file changes its hash and fails verification.

Usage:
    python3 tools/build_manifest.py corpus/raw/            # write the manifest
    python3 tools/build_manifest.py corpus/raw/ --verify   # check, do not write

Exit status is 0 when the manifest is written or verifies, and 1 otherwise.

Deterministic: entries are sorted by path, so the same tree always yields a
byte-identical manifest.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "corpus" / "MANIFEST.sha256"

HEADER = """# OAGRC raw-artifact manifest
#
# Every file listed here is canonical source material and is NEVER edited after
# commit -- not for typos, not for misattribution, not for formatting. Errors are
# corrected by superseding artifacts that reference the original by hash.
#
# Verify with:  python3 tools/build_manifest.py corpus/raw/ --verify
# Or with:      sha256sum -c corpus/MANIFEST.sha256   (from the repository root)
#
"""


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def collect(root: Path) -> list[tuple[str, str]]:
    """Return (relative_path, sha256) pairs, sorted by path for determinism."""
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            entries.append((str(path.relative_to(REPO_ROOT)), sha256_of(path)))
    return entries


def render(entries: list[tuple[str, str]]) -> str:
    lines = [HEADER]
    lines.extend(f"{digest}  {relative}" for relative, digest in entries)
    return "\n".join(lines) + "\n"


def parse_existing() -> dict[str, str]:
    if not MANIFEST_PATH.exists():
        return {}
    recorded = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        digest, _, relative = stripped.partition("  ")
        if digest and relative:
            recorded[relative] = digest
    return recorded


def verify(entries: list[tuple[str, str]]) -> int:
    recorded = parse_existing()
    if not recorded:
        print(f"no manifest at {MANIFEST_PATH.relative_to(REPO_ROOT)}; nothing to verify")
        return 1

    actual = dict(entries)
    failures = 0

    for relative, digest in sorted(recorded.items()):
        if relative not in actual:
            print(f"MISSING   {relative}  (recorded in manifest, absent from tree)")
            failures += 1
        elif actual[relative] != digest:
            print(f"MODIFIED  {relative}")
            print(f"          recorded: {digest}")
            print(f"          actual:   {actual[relative]}")
            failures += 1
        else:
            print(f"OK        {relative}")

    for relative in sorted(set(actual) - set(recorded)):
        print(f"UNANCHORED {relative}  (present in tree, absent from manifest)")
        failures += 1

    print()
    if failures:
        print(f"FAILED — {failures} discrepanc{'y' if failures == 1 else 'ies'}.")
        print("A modified raw artifact is a governance defect, not a formatting issue.")
        return 1
    print(f"All {len(recorded)} raw artifacts verify.")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    root = Path(argv[1])
    if not root.is_absolute():
        root = REPO_ROOT / root
    if not root.is_dir():
        print(f"not a directory: {argv[1]}")
        return 2

    entries = collect(root)
    if not entries:
        print(f"no files found under {argv[1]}")
        return 1

    if "--verify" in argv[2:]:
        return verify(entries)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(render(entries), encoding="utf-8")
    print(f"wrote {MANIFEST_PATH.relative_to(REPO_ROOT)} — {len(entries)} artifact(s)")
    for relative, digest in entries:
        print(f"  {digest[:16]}…  {relative}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
