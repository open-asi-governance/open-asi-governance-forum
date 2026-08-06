#!/usr/bin/env python3
"""The page's in-page SHA-256 must equal a real SHA-256.

    python3 tools/tests/test_page_hash_fallback.py

The capture page hashes the pasted response at paste time, and that hash is its
central integrity claim. `crypto.subtle` needs a secure context and the page is
opened over file://, so the page carries a pure-JS fallback. Two implementations of
a hash is a drift hazard and the same discipline applies as to the gates: check it,
do not hope.

Runs the fallback extracted from the GENERATED page -- not from the source -- so a
build that mangles the function is caught, and compares it against hashlib over the
real corpus plus edge cases around the 55/56/64-byte padding boundaries where a
hand-written SHA-256 fails if it fails at all.

A wrong hash here would be silent: the page would display a plausible hex string,
ingest would compare it against a correctly-computed one, and every capture would
be flagged inconsistent for a reason nobody would look for in the hash function.
"""

from __future__ import annotations

import glob
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PAGE = ROOT / "tools" / "capture_ui" / "index.html"

NODE = shutil.which("node")
if NODE is None:
    print("SKIP  node unavailable; the in-page SHA-256 fallback was NOT verified.")
    print("      This is a skip, not a pass.")
    sys.exit(0)

if not PAGE.exists():
    print(f"FAIL  {PAGE.relative_to(ROOT)} does not exist. Run tools/build_capture_ui.py first.")
    sys.exit(1)

page = PAGE.read_text(encoding="utf-8")
match = re.search(r"function sha256Fallback\(bytes\)\{.*?\n\}", page, re.S)
if match is None:
    print("FAIL  sha256Fallback was not found in the generated page. The build dropped it.")
    sys.exit(1)

cases: list[str] = [
    "", "a", "abc",
    "a" * 55, "a" * 56, "a" * 57, "a" * 63, "a" * 64, "a" * 65, "a" * 119, "a" * 120,
    "café naïve résumé — em dash, ünïcödé",
    "line\nline\r\nline\ttab",
    "🙂 emoji and 中文 and العربية",
]
for f in sorted(glob.glob(str(ROOT / "corpus/raw/review-round-0*/*.md")))[:6]:
    cases.append(pathlib.Path(f).read_text(encoding="utf-8"))
cases.append((ROOT / "record/review-round-03-prompt.md").read_text(encoding="utf-8"))

runner = f"""
{match.group(0)}
const cases = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const enc = new TextEncoder();
process.stdout.write(JSON.stringify(cases.map(c => sha256Fallback(enc.encode(c)))));
"""

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    (tmp / "r.js").write_text(runner, encoding="utf-8")
    (tmp / "c.json").write_text(json.dumps(cases), encoding="utf-8")
    proc = subprocess.run([NODE, str(tmp / "r.js"), str(tmp / "c.json")],
                          capture_output=True, text=True)

if proc.returncode != 0:
    print("FAIL  node could not run the extracted fallback:")
    print(proc.stderr.strip()[:1500])
    sys.exit(1)

js_hashes = json.loads(proc.stdout)
failures = []
for case, got in zip(cases, js_hashes):
    want = hashlib.sha256(case.encode("utf-8")).hexdigest()
    if got != want:
        label = repr(case[:40]) + ("…" if len(case) > 40 else "")
        failures.append(f"{len(case):>7} chars {label}\n           want {want}\n           got  {got}")

print(f"in-page SHA-256 fallback vs hashlib over {len(cases)} cases")
print(f"{len(cases) - len(failures)} matched, {len(failures)} mismatched")
for f in failures:
    print(f"  FAIL  {f}")
sys.exit(1 if failures else 0)
