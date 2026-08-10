#!/usr/bin/env python3
"""Conformance for verify_negative_control.py.

The verifier is subject to its own requirement: a verifier only ever run against valid
attestations has never been observed to fail. These are its negative controls.
"""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import verify_negative_control as v                                      # noqa: E402

PASSED = FAILED = 0


def check(label: str, ok: bool) -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


print("\nthe shipped fixtures behave as the spec requires")
proc = subprocess.run([sys.executable, str(ROOT / "verify_negative_control.py"), "--fixtures"],
                      capture_output=True, text=True, cwd=ROOT)
check("every must-reject fixture is rejected and every must-accept accepted",
      proc.returncode == 0)
check("there is at least one must-reject fixture per normative requirement",
      len(list((ROOT.parent / "spec" / "ncp" / "fixtures").glob("reject-*.json"))) >= 7)

print("\nthe requirement that does the work: surviving your own control is a violation")
doc = json.loads((ROOT.parent / "spec" / "ncp" / "fixtures" / "accept-minimal.json").read_text())
doc["checks"][0]["negative_control"]["run"]["outcome"] = "PASS"
check("a check that PASSES under its negative control is non-conforming",
      any("N3" in p for p in v.problems_for(doc)))

print("\nan absent control is not a pass")
doc = json.loads((ROOT.parent / "spec" / "ncp" / "fixtures" / "accept-minimal.json").read_text())
del doc["checks"][0]["negative_control"]
check("no negative_control at all is N1", any("N1" in p for p in v.problems_for(doc)))

print("\ntransport perturbation does not count")
doc = json.loads((ROOT.parent / "spec" / "ncp" / "fixtures" / "accept-minimal.json").read_text())
doc["checks"][0]["negative_control"]["how_produced"] = "block the port with a firewall rule"
check("a transport-only control is N5", any("N5" in p for p in v.problems_for(doc)))

print("\nthe verifier does not pass vacuously")
check("an empty attestation is refused", v.problems_for({"ncp_version": "0.1"}) != [])
check("an attestation with zero checks is refused",
      v.problems_for({"ncp_version": "0.1", "checks": []}) != [])

print("\nthe live attestation's verdict matches its own recorded outcomes")
#  This asserted the attestation was NON-conforming with four N3 violations. That was true on
#  2026-08-10 and stopped being true the same day, when the implementer remediated all four and
#  every negative control was RE-EXECUTED here against the fixed build. A test that pins a
#  verdict goes red when the world improves; what is worth pinning is that the verifier's answer
#  and the attestation's recorded outcomes cannot disagree.
import json                                                             # noqa: E402
att = ROOT.parent / "record" / "attestations" / "ncp-2026-08-10-consullo.json"
code, problems = v.verify(att)
doc = json.loads(att.read_text())
survivors = [c["check_id"] for c in doc["checks"]
             if str(c["negative_control"]["run"].get("outcome", "")).upper() != "FAIL"]
check("the verdict agrees with the recorded outcomes",
      (code == 0) == (survivors == []))
check("every N3 violation names a check that actually survived its control",
      all(any(cid in p for cid in survivors) for p in problems if "N3" in p))
check("no check is recorded as conforming while surviving its control",
      len([p for p in problems if "N3" in p]) == len(survivors))
check("every negative control run says whether it was executed or inferred",
      all(c["negative_control"]["run"].get("method") for c in doc["checks"]))

print("\nan unreadable file is refused, not skipped")
tmp = Path(tempfile.mkdtemp()) / "bad.json"
tmp.write_text("{not json")
check("unparseable input exits non-zero", v.verify(tmp)[0] != 0)

#  KEEP THE SUMMARY AND EXIT LAST.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
