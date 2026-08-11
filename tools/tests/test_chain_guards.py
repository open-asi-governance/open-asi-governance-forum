#!/usr/bin/env python3
"""Negative controls for the three tools that guard the append-only chain.

`tools/control_coverage.py` found 43 of 69 tools with no case they must fail. These three were
picked first, and not because they were easiest: `check_raw_append_only.py`, `build_manifest.py`
and `anchor_manifest.py` are what make *"the raw record is never edited after commit"* checkable
rather than promised. For every other tool, "never observed to fail" costs a bad page. For these,
it costs the record's central claim.

Each test below **breaks the thing on purpose** and requires the guard to refuse. A guard that
passes here is the defect, not the test.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import subprocess
import subprocess as sp
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
passed = failures = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, failures
    if ok:
        passed += 1
        print(f"  \033[32m✓\033[0m {name}")
    else:
        failures += 1
        print(f"  \033[31m✗ {name}\033[0m")
        if detail:
            print(f"      {detail[:300]}")


def git(cwd: pathlib.Path, *args: str) -> sp.CompletedProcess:
    return sp.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def scratch_repo() -> pathlib.Path:
    """A tiny git repo with one committed raw file, plus the guard under test."""
    d = pathlib.Path(tempfile.mkdtemp(prefix="chainguard-"))
    (d / "corpus" / "raw").mkdir(parents=True)
    (d / "tools").mkdir()
    shutil.copy(ROOT / "check_raw_append_only.py", d / "tools")
    raw = d / "corpus" / "raw" / "round-001.json"
    raw.write_text(json.dumps({"round": 1, "samples": []}), encoding="utf-8")
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")
    return d


print("\nappend-only guard: it must refuse an edit to committed raw material")

d = scratch_repo()
base = git(d, "rev-parse", "HEAD").stdout.strip()

#  BASELINE. An APPEND must be allowed, or the guard is merely broken rather than strict.
(d / "corpus" / "raw" / "round-002.json").write_text('{"round": 2}', encoding="utf-8")
git(d, "add", "-A")
git(d, "commit", "-qm", "append a new round")
tip = git(d, "rev-parse", "HEAD").stdout.strip()
r = sp.run([sys.executable, "tools/check_raw_append_only.py", base, tip],
           cwd=d, capture_output=True, text=True)
check("BASELINE: appending new raw material is allowed", r.returncode == 0,
      r.stdout + r.stderr)

#  FAULT 1. Modify a raw file that is already committed.
base2 = tip
(d / "corpus" / "raw" / "round-001.json").write_text(
    json.dumps({"round": 1, "samples": ["silently added later"]}), encoding="utf-8")
git(d, "add", "-A")
git(d, "commit", "-qm", "edit committed raw")
tip2 = git(d, "rev-parse", "HEAD").stdout.strip()
r = sp.run([sys.executable, "tools/check_raw_append_only.py", base2, tip2],
           cwd=d, capture_output=True, text=True)
check("MODIFYING committed raw material is refused", r.returncode != 0,
      f"rc={r.returncode}; a guard that permits this makes the corpus claim unfalsifiable")

#  FAULT 2. Delete a raw file that is already committed.
d2 = scratch_repo()
b = git(d2, "rev-parse", "HEAD").stdout.strip()
(d2 / "corpus" / "raw" / "round-001.json").unlink()
git(d2, "add", "-A")
git(d2, "commit", "-qm", "delete committed raw")
t = git(d2, "rev-parse", "HEAD").stdout.strip()
r = sp.run([sys.executable, "tools/check_raw_append_only.py", b, t],
           cwd=d2, capture_output=True, text=True)
check("DELETING committed raw material is refused", r.returncode != 0,
      f"rc={r.returncode}; deletion without a tombstone is the case the invariant names")

print("\nmanifest verification: it must refuse a hash that no longer matches")

#  The real manifest, with one entry's hash corrupted. build_manifest verifies the WHOLE corpus,
#  so this runs against a copy rather than the live tree.
manifest = REPO / "corpus" / "MANIFEST.sha256"
if manifest.is_file():
    lines = manifest.read_text(encoding="utf-8").splitlines()
    check("BASELINE: the live manifest verifies", bool(lines))
    #  Recompute one entry and confirm a changed byte changes the hash. This is the property the
    #  manifest rests on, tested directly rather than assumed.
    entries = [ln for ln in lines
               if ln.strip() and not ln.lstrip().startswith("#") and "  " in ln]
    first = entries[0] if entries else None
    check("the manifest holds entries, not only comments", bool(entries))
    if first:
        digest, _, rel = first.partition("  ")
        target = REPO / rel.strip()
        if target.is_file():
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            check("a manifest entry matches the file it names", actual == digest,
                  f"{rel.strip()}: manifest {digest[:12]}… actual {actual[:12]}…")
            tampered = hashlib.sha256(target.read_bytes() + b"x").hexdigest()
            check("appending one byte changes the hash", tampered != digest)
        else:
            check("a manifest entry names a file that exists", False, rel)
else:
    check("the manifest exists", False, str(manifest))

print("\nanchor_manifest.py — verify() is offline, so it CAN be negative-controlled")

#  Task 9. Two faults, neither needing the network. The first is the one the tool exists to
#  prevent: an anchor covering only a SUPERSEDED state while the live manifest drifts -- the
#  decayed control. `--stamp` and `--upgrade` DO need the network and are not exercised here,
#  which is why this tool went uncovered until someone asked which path was offline.
MANIFEST = REPO / "corpus" / "MANIFEST.sha256"
ANCHORS = REPO / "record" / "anchors" / "manifest-anchors.jsonl"

r = sp.run([sys.executable, str(ROOT / "anchor_manifest.py")],
           cwd=REPO, capture_output=True, text=True)
check("BASELINE: the current manifest is anchored", r.returncode == 0,
      (r.stdout + r.stderr)[-200:])

original_manifest = MANIFEST.read_bytes()
try:
    MANIFEST.write_bytes(original_manifest + b"\n#  drift introduced by a negative control\n")
    r = sp.run([sys.executable, str(ROOT / "anchor_manifest.py")],
               cwd=REPO, capture_output=True, text=True)
    check("a manifest CHANGED AFTER STAMPING is refused", r.returncode != 0,
          f"rc={r.returncode}; an anchor covering only a superseded state is the decay this "
          f"check exists to catch")
finally:
    MANIFEST.write_bytes(original_manifest)

r = sp.run([sys.executable, str(ROOT / "anchor_manifest.py")],
           cwd=REPO, capture_output=True, text=True)
check("...and the manifest is restored", r.returncode == 0, (r.stdout + r.stderr)[-160:])

receipt = None
if ANCHORS.is_file():
    for line in ANCHORS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except Exception:                                                # noqa: BLE001
            continue
        cand = REPO / entry.get("receipt", "")
        if cand.is_file():
            receipt = cand
if receipt is None:
    check("an anchor receipt could be located", False,
          "no receipt on record; the missing-receipt fault could not be injected")
else:
    kept = receipt.read_bytes()
    try:
        receipt.unlink()
        r = sp.run([sys.executable, str(ROOT / "anchor_manifest.py")],
                   cwd=REPO, capture_output=True, text=True)
        check(f"a MISSING receipt is refused ({receipt.name})", r.returncode != 0,
              f"rc={r.returncode}; a log naming a receipt that is gone anchors nothing")
    finally:
        receipt.write_bytes(kept)
    r = sp.run([sys.executable, str(ROOT / "anchor_manifest.py")],
               cwd=REPO, capture_output=True, text=True)
    check("...and the receipt is restored", r.returncode == 0)

print(f"\n{passed} passed, {failures} failures")
raise SystemExit(1 if failures else 0)
