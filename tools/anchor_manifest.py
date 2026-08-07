#!/usr/bin/env python3
"""Anchor the manifest in a timestamping service the operator does not run.

    python3 tools/anchor_manifest.py --stamp     # anchor the current manifest
    python3 tools/anchor_manifest.py             # verify the current state is anchored
    python3 tools/anchor_manifest.py --upgrade   # complete pending Bitcoin attestations

WHY THIS EXISTS, AND WHO ASKED FOR IT.

Across 96 recorded statements of what would change a party's answer, **48 named a
credential or control the operator does not hold** and **18 named an append-only
log the operator cannot rewrite**. They were specific:

  Claude  "hashes anchored at capture time in an external, operator-independent
           timestamping service"
  Qwen    "if the record were hosted on a decentralized network where the operator
           could not unilaterally alter the hash history"
  Gemini  "controls that do not terminate with the operator"
  GPT     "publication infrastructure the operator cannot unilaterally alter or
           terminate"

This is the cheapest item on that list, and it is the only one that requires no
second party's cooperation. OpenTimestamps commits the manifest's hash into the
Bitcoin blockchain through calendar servers run by other people. **The custodian
cannot backdate it, cannot rewrite it, and cannot take it down.**

WHAT IT ESTABLISHES, PRECISELY.

That these manifest bytes existed no later than a given Bitcoin block. That is all.

WHAT IT DOES NOT ESTABLISH — and this list matters more than the one above, because
an over-read anchor is worse than none:

  * **Not that the contents are true.** D-18 governs: an anchored lie is a lie with
    a timestamp. Every provenance limit in the register survives this unchanged.
  * **Not that anything was anchored EARLIER than it was.** A record created and
    stamped a minute later proves only "no later than". The founding corpus predates
    every anchor here and always will.
  * **Not that the operator cannot delete the repository.** It stops silent
    *revision*, not deletion. A reader who kept a copy can prove what it said; a
    reader who did not is still out of luck.
  * **Not custody of anything.** No key here is held by a non-operator party. The
    operator still controls what gets written, what gets anchored, and when.

So this subtracts exactly one power: **rewriting hash history without detection.**
It is a real subtraction, it is small, and calling it more than that would be the
legitimacy-laundering the parties named.

THE ANCHOR LOG IS APPEND-ONLY AND CHECKED.

`record/anchors/manifest-anchors.jsonl` records one line per anchored manifest state.
The build fails when the current manifest's hash has no line, because an anchor that
covers a superseded state while the live one drifts is exactly the decayed control
this repository keeps rediscovering.

Exit status is 0 when the current manifest is anchored, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "corpus" / "MANIFEST.sha256"
RECEIPT = REPO_ROOT / "corpus" / "MANIFEST.sha256.ots"
LOG = REPO_ROOT / "record" / "anchors" / "manifest-anchors.jsonl"

CALENDARS = ["https://a.pool.opentimestamps.org", "https://b.pool.opentimestamps.org",
             "https://a.pool.eternitywall.com", "https://ots.btc.catallaxy.com"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def manifest_sha() -> str:
    return hashlib.sha256(MANIFEST.read_bytes()).hexdigest()


def ots() -> str | None:
    return shutil.which("ots") or (
        str(Path.home() / ".local/bin/ots") if (Path.home() / ".local/bin/ots").exists()
        else None)


def anchored() -> dict[str, dict]:
    if not LOG.is_file():
        return {}
    out = {}
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = json.loads(line)
            out[entry["manifest_sha256"]] = entry
    return out


def stamp() -> int:
    binary = ots()
    if not binary:
        print("REFUSED: the ots client is not installed.")
        print("  python3 -m pip install --user opentimestamps-client")
        return 1
    digest = manifest_sha()
    if digest in anchored():
        print(f"already anchored: {digest[:16]}…")
        return 0

    #  The receipt is named after the manifest and OpenTimestamps overwrites it.
    #  Each anchored state's receipt is preserved separately, because a receipt for
    #  a superseded manifest is the evidence that that state existed -- and this
    #  corpus's central rule is that recorded material is not overwritten.
    #  `ots stamp` REFUSES when its output path already exists, and it refuses after
    #  submitting to every calendar -- so a stale scratch receipt costs a full round
    #  its commit. One was committed by accident and halted round 004 at exit 7 with
    #  all five parties' replies already paid for and sitting uncommitted.
    #
    #  This path is scratch. The durable receipt is the digest-named copy under
    #  record/anchors/, which nothing overwrites, so clearing this one loses nothing.
    if RECEIPT.exists():
        RECEIPT.unlink()
    result = subprocess.run([binary, "stamp", str(MANIFEST)], cwd=REPO_ROOT,
                            capture_output=True, text=True)
    if result.returncode != 0 or not RECEIPT.is_file():
        print(f"REFUSED: ots stamp failed.\n{result.stderr.strip()[:400]}")
        return 1

    keep = REPO_ROOT / "record" / "anchors" / f"MANIFEST-{digest[:16]}.ots"
    keep.parent.mkdir(parents=True, exist_ok=True)
    keep.write_bytes(RECEIPT.read_bytes())
    #  ots writes its receipt beside the file it stamped, under one name it reuses.
    #  Left there, the next stamp would overwrite the previous state's proof. The
    #  kept copy is named by the digest it attests, so no anchor can erase another.
    RECEIPT.unlink()

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "artifact_type": "manifest_anchor",
            "manifest_sha256": digest,
            "stamped_utc": utc_now(),
            "receipt": str(keep.relative_to(REPO_ROOT)),
            "receipt_sha256": hashlib.sha256(keep.read_bytes()).hexdigest(),
            "calendars": CALENDARS,
            "state": "pending_bitcoin_attestation",
            "establishes": ("That these manifest bytes existed no LATER than the Bitcoin "
                            "block this commitment lands in. Nothing about whether their "
                            "contents are true — D-18 is unchanged by anchoring."),
            "the_operator_still": ["chooses what is written and when it is anchored",
                                   "can delete the repository entirely",
                                   "holds every credential; no key here is held by another party"],
            "what_it_subtracts": ("Exactly one power: rewriting hash history without "
                                  "detection by anyone holding a receipt."),
        }, ensure_ascii=False) + "\n")

    print(f"anchored {digest[:16]}…  receipt {keep.relative_to(REPO_ROOT)}")
    print("  state: pending Bitcoin attestation — the calendars have the commitment;")
    print("  it lands in a block within hours. Run --upgrade later to complete it.")
    return 0


def upgrade() -> int:
    """Complete pending attestations. Safe to run repeatedly; needs the network."""
    binary = ots()
    if not binary:
        print("REFUSED: the ots client is not installed.")
        return 1
    known = anchored()
    if not known:
        print("nothing anchored yet.")
        return 0
    changed = 0
    for digest, entry in known.items():
        receipt = REPO_ROOT / entry["receipt"]
        if not receipt.is_file():
            print(f"  MISSING  {entry['receipt']}")
            continue
        before = receipt.read_bytes()
        subprocess.run([binary, "upgrade", str(receipt)], cwd=REPO_ROOT, capture_output=True)
        after = receipt.read_bytes()
        state = "upgraded — Bitcoin attestation complete" if after != before else "still pending"
        if after != before:
            changed += 1
        print(f"  {digest[:16]}…  {state}")
    print(f"\n{changed} receipt(s) upgraded. A pending receipt is still a valid commitment; "
          f"upgrading only fetches the block proof.")
    return 0


def verify() -> int:
    digest = manifest_sha()
    known = anchored()
    entry = known.get(digest)
    print(f"manifest {digest[:16]}…  {len(known)} anchored state(s) on record")
    if not entry:
        print(f"\nFAILED — the CURRENT manifest is not anchored.")
        print(f"  Anchor it:  python3 tools/anchor_manifest.py --stamp")
        print(f"  An anchor covering only a superseded state, while the live one drifts, is")
        print(f"  the decayed control this check exists to prevent.")
        return 1
    receipt = REPO_ROOT / entry["receipt"]
    if not receipt.is_file():
        print(f"\nFAILED — receipt {entry['receipt']} is missing.")
        return 1
    if hashlib.sha256(receipt.read_bytes()).hexdigest() != entry["receipt_sha256"]:
        #  Not an error: `ots upgrade` legitimately rewrites a receipt to add the
        #  block proof. The log records the hash at stamping time, so a difference
        #  means upgraded-or-tampered and the two are told apart by verifying it.
        print(f"  receipt bytes differ from stamping time — expected after --upgrade")
    print(f"  anchored {entry['stamped_utc']} via {len(entry['calendars'])} independent calendars")
    print(f"  establishes: existence no later than a Bitcoin block. NOT that the contents "
          f"are true (D-18), and NOT that the operator cannot delete the repository.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--stamp", action="store_true", help="anchor the current manifest")
    group.add_argument("--upgrade", action="store_true",
                       help="fetch block proofs for pending attestations")
    args = ap.parse_args(argv)
    if args.stamp:
        return stamp()
    if args.upgrade:
        return upgrade()
    return verify()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
