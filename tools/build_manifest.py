#!/usr/bin/env python3
"""Verify the SHA-256 manifest that anchors every raw corpus artifact.

The manifest is the mechanism by which "the raw record is never edited after
commit" becomes checkable rather than merely promised. Any later edit to a raw
file changes its hash and fails verification.

**VERIFICATION IS THE DEFAULT, and that is the whole point.** Until 2026-08-06
this tool wrote by default and `rebuild.py` invoked it that way, so the ordinary
maintenance path silently RE-ANCHORED tampered material instead of rejecting it:
appending one byte to a raw artifact and running `rebuild.py` exited 0, rewrote
the manifest around the new bytes, and printed "All provenance checks passed."
The manifest recorded the state of the disk rather than anchoring anything. That
is deficiency D-29; the reproduction is recorded there.

An anchor you rewrite before reading is not an anchor. So writing is no longer
something that happens incidentally — it must be asked for by name.

Usage:
    python3 tools/build_manifest.py corpus/raw/                 # verify (default)
    python3 tools/build_manifest.py corpus/raw/ --add           # anchor NEW files only
    python3 tools/build_manifest.py corpus/raw/ --force-rewrite # governance action

`--add` is append-only. It verifies every existing entry first and refuses if any
recorded artifact is modified or missing, so new material can never be committed
in the same motion that quietly re-anchors old material.

`--force-rewrite` discards the existing manifest and rebuilds it from the tree.
It is the only operation that can drop or change a recorded hash, it is never
invoked by `rebuild.py`, and it exists for deliberate custodian actions such as
withdrawing material. It prints what it is destroying before it does it.

Exit status is 0 on success and 1 on any discrepancy.

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


def add_new_only(entries: list[tuple[str, str]]) -> int:
    """Anchor previously unanchored files. Refuse if anything recorded has changed.

    Append-only by construction: an existing entry is never rewritten, so adding
    new raw material cannot be the motion that launders a change to old material.
    """
    recorded = parse_existing()
    actual = dict(entries)

    violations = []
    for relative, digest in sorted(recorded.items()):
        if relative not in actual:
            violations.append(f"MISSING   {relative}  (recorded in manifest, absent from tree)")
        elif actual[relative] != digest:
            violations.append(
                f"MODIFIED  {relative}\n          recorded: {digest}\n          actual:   {actual[relative]}"
            )

    if violations:
        for line in violations:
            print(line)
        print()
        print(f"REFUSED — {len(violations)} existing artifact(s) changed or absent.")
        print("--add anchors new material only. It will not re-anchor material already recorded.")
        print("A modified raw artifact is a governance defect, not a formatting issue.")
        return 1

    new_paths = sorted(set(actual) - set(recorded))
    if not new_paths:
        print(f"nothing to add — all {len(recorded)} raw artifacts already anchored and verifying.")
        return 0

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(render(entries), encoding="utf-8")
    print(f"verified {len(recorded)} existing artifact(s) unchanged.")
    print(f"anchored {len(new_paths)} new artifact(s):")
    for relative in new_paths:
        print(f"  {actual[relative][:16]}…  {relative}")
    return 0


def force_rewrite(entries: list[tuple[str, str]]) -> int:
    """Discard the manifest and rebuild it from the tree. A governance action."""
    recorded = parse_existing()
    actual = dict(entries)

    dropped = sorted(set(recorded) - set(actual))
    changed = sorted(r for r in recorded if r in actual and actual[r] != recorded[r])

    print("FORCE REWRITE — this discards recorded hashes and re-anchors whatever is on disk.")
    print("This is a custodian governance action. It is never part of the maintenance path.")
    print()
    if changed:
        print(f"{len(changed)} recorded artifact(s) will be RE-ANCHORED at new hashes:")
        for relative in changed:
            print(f"  {relative}")
            print(f"    was: {recorded[relative]}")
            print(f"    now: {actual[relative]}")
    if dropped:
        print(f"{len(dropped)} recorded artifact(s) will be DROPPED from the manifest:")
        for relative in dropped:
            print(f"  {relative}  (was {recorded[relative][:16]}…)")
    if not changed and not dropped:
        print("No recorded hash changes or drops — this rewrite only adds new material.")
    print()

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(render(entries), encoding="utf-8")
    print(f"wrote {MANIFEST_PATH.relative_to(REPO_ROOT)} — {len(entries)} artifact(s)")
    if changed or dropped:
        print()
        print("Record why in corpus/deficiencies.md or a superseding artifact. A hash that")
        print("changed without an explanation in the record is indistinguishable from tampering.")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    flags = set(argv[2:])
    unknown = flags - {"--verify", "--add", "--force-rewrite"}
    if unknown:
        print(f"unknown option(s): {' '.join(sorted(unknown))}")
        print(__doc__)
        return 2
    if len({"--add", "--force-rewrite"} & flags) > 1:
        print("--add and --force-rewrite are mutually exclusive.")
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

    if "--force-rewrite" in flags:
        return force_rewrite(entries)
    if "--add" in flags:
        return add_new_only(entries)
    return verify(entries)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
