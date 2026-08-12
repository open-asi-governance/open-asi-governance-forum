#!/usr/bin/env python3
"""The harness must FAIL the things it exists to catch — checked with synthetic offenders.

    python3 tools/tests/test_effect_boundary.py

A harness that verifies refusals is itself a check producing an assurance signal, so control 2
applies to it: every one of its claims ships with a condition under which it must fail. Each case
below plants a small program in the image that refuses correctly by every OTHER measure — right
exit code, right refusal text — and then does one forbidden thing. If the harness passes any of
them, its green means nothing.

They are written as PROGRAMS rather than as mocked internals on purpose. The whole argument for a
subprocess harness is that it observes what a real caller does; testing it against a stub would
be the same substitution error the fixtures it replaces were making.

THE POSITIVE CONTROL IS FIRST. A harness that failed everything would pass all eight offenders.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from effect_boundary import refuses, JsonlAppend, Unavailable                # noqa: E402

#  COVERS — what this suite REQUIRES TO REFUSE, declared rather than inferred. The
#  proximity heuristic that used to guess this counted a shutil.copy list and a comment
#  as coverage; see D-68. A declaration is a claim someone made after reading the file,
#  and it cannot rot silently: a declared tool that does not exist fails the scan, and a
#  suite with no refusal assertion is refused the credit anyway.
COVERS = ("effect_boundary.py", "codex_call.py")

PASSED = FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m  {detail}")


def offender(body: str):
    """Plant a program that refuses properly and then misbehaves in exactly one way."""
    def setup(image: Path) -> None:
        (image / "zz_offender.py").write_text(
            "import sys, os, json, socket, subprocess\n"
            "print('REFUSED: the cohort is not registered [ZZ-99]')\n"
            + body +
            "\nsys.exit(2)\n", encoding="utf-8")
    return setup


def caught(label: str, body: str, expect_in_problem: str, **kw) -> None:
    verdict = refuses(argv=("python3", "zz_offender.py"), case=label,
                      expect_guard="ZZ-99", setup=offender(body), **kw)
    hit = [p for p in verdict["problems"] if expect_in_problem.lower() in p.lower()]
    check(f"{label} — caught", bool(hit),
          f"problems were {verdict['problems']}")


print("\nthe positive control, without which every case below is meaningless")

verdict = refuses(argv=("python3", "zz_offender.py"), case="a clean refusal",
                  expect_guard="ZZ-99", setup=offender("pass"))
check("a program that refuses and does nothing PASSES", verdict["problems"] == [],
      str(verdict["problems"]))
check("...and the network was actually watched, not assumed",
      verdict["network_observed_by"] == "strace", verdict["network_observed_by"])
check("...and the offender itself is the only file the setup added",
      "zz_offender.py" not in verdict["changed"])

print("\nthe eight offenders")

#  D-62 ITSELF: refuses correctly, appends to the ledger anyway.
caught("an unlisted append to the spend ledger",
       "open('record/cycles/spend-ledger.json','a').write('\\n')",
       "UNDECLARED EFFECT on record/cycles/spend-ledger.json")

caught("a file created anywhere in the tree",
       "open('docs/sneaky.html','w').write('hi')",
       "UNDECLARED EFFECT on docs/sneaky.html")

caught("a file deleted",
       "os.remove('CHALLENGE.md')",
       "UNDECLARED EFFECT on CHALLENGE.md")

#  .git is not the working tree, and a snapshot of only tracked files would miss this entirely.
caught("a git config change, which touches no tracked file",
       "open('.git/config','a').write('\\n[zz]\\n\\tsneaky = true\\n')",
       "UNDECLARED EFFECT on .git/config")

caught("a write outside the repository, into HOME",
       "open(os.path.join(os.environ['HOME'],'.sneakyrc'),'w').write('x')",
       "wrote outside the repository, into HOME")

#  D-67: nothing in the tree changes, and this is why the harness watches more than the tree.
caught("an outbound connection on a refused path",
       "socket.setdefaulttimeout(3)\n"
       "try: socket.create_connection(('example.com',80))\n"
       "except Exception: pass",
       "connection")

caught("reaching for an external command on a refused path",
       "subprocess.run(['gh','issue','comment','1','-b','hi'],capture_output=True)",
       "launched an external command")

print("\nthe harness's own claims about exit status and guards")

verdict = refuses(argv=("python3", "-c", "print('all fine')"), case="a tool that did NOT refuse",
                  expect_guard="")
check("a zero exit is not a refusal", any("did not refuse" in p for p in verdict["problems"]),
      str(verdict["problems"]))

verdict = refuses(argv=("python3", "-c", "import sys; print('REFUSED [XX-01]'); sys.exit(2)"),
                  case="the wrong guard fired", expect_guard="ZZ-99")
check("a refusal from some OTHER guard is not this guard's refusal",
      any("ZZ-99 did not fire" in p for p in verdict["problems"]), str(verdict["problems"]))

print("\ndeclared effects are postconditions, not permissions")


def appender(rows: int, mangle: str = ""):
    def setup(image: Path) -> None:
        (image / "zz_offender.py").write_text(
            "import sys\n"
            "print('REFUSED: not registered [ZZ-99]')\n"
            f"lines = [__import__('json').dumps({{'action':'refused','n':i}}) for i in range({rows})]\n"
            f"{mangle or 'open(\"record/claims/dispositions.jsonl\",\"a\").write(chr(10).join(lines)+chr(10))'}\n"
            "sys.exit(2)\n", encoding="utf-8")
    return setup


LEDGER = "record/claims/dispositions.jsonl"

verdict = refuses(argv=("python3", "zz_offender.py"), case="a declared append that happened",
                  expect_guard="ZZ-99", setup=appender(1),
                  expected_effects={LEDGER: JsonlAppend(rows=1, fields={"action": "refused"})})
check("a declared append that occurs and matches PASSES", verdict["problems"] == [],
      str(verdict["problems"]))

verdict = refuses(argv=("python3", "zz_offender.py"), case="two rows where one was declared",
                  expect_guard="ZZ-99", setup=appender(2),
                  expected_effects={LEDGER: JsonlAppend(rows=1, fields={"action": "refused"})})
check("appending MORE rows than declared is caught",
      any("expected exactly 1" in p for p in verdict["problems"]), str(verdict["problems"]))

verdict = refuses(argv=("python3", "zz_offender.py"), case="the declared field is wrong",
                  expect_guard="ZZ-99", setup=appender(1),
                  expected_effects={LEDGER: JsonlAppend(rows=1, fields={"action": "granted"})})
check("an append whose CONTENT is not what was declared is caught",
      any("expected 'granted'" in p for p in verdict["problems"]), str(verdict["problems"]))

#  THE ONE CODEX NAMED: permitting a path would let a truncation through.
verdict = refuses(argv=("python3", "zz_offender.py"), case="truncating a permitted file",
                  expect_guard="ZZ-99",
                  setup=appender(1, mangle=f'open("{LEDGER}","w").write("")'),
                  expected_effects={LEDGER: JsonlAppend(rows=1, fields={"action": "refused"})})
check("TRUNCATING a file whose append was permitted is caught",
      any("rewrite, not an append" in p or "expected exactly 1" in p
          for p in verdict["problems"]), str(verdict["problems"]))

verdict = refuses(argv=("python3", "-c", "import sys; print('REFUSED [ZZ-99]'); sys.exit(2)"),
                  case="a declared effect that never happened", expect_guard="ZZ-99",
                  expected_effects={LEDGER: JsonlAppend(rows=1)})
check("a declared effect that does NOT occur is caught",
      any("never happened" in p or "expected exactly 1" in p for p in verdict["problems"]),
      str(verdict["problems"]))

print("\nthe first real conversion")

verdict = refuses(argv=("python3", "tools/record_spend.py", "--cohort", "no-such-cohort-zzqx"),
                  case="D-62 / RS-01", expect_guard="RS-01", expected_effects={})
check("record_spend refuses an unregistered cohort and changes NOTHING, anywhere",
      verdict["problems"] == [], str(verdict["problems"]))
check("...and the ledger it corrupted 87 times is untouched",
      "record/cycles/spend-ledger.json" not in verdict["changed"])

print("\nthe two conversions that exercise real callers")

import json as _json

EXHAUSTED = _json.dumps({
    "lease_id": "fixture-exhausted", "granted_utc": "2026-01-01T00:00:00Z",
    "expires_utc": "2099-01-01T00:00:00Z", "granted_by": "fixture", "evidence": "fixture",
    "max_actions": 0, "note": "", "supersedes": None, "authority": "fixture"}) + "\n"


def exhausted_lease(image: Path) -> None:
    """Fixture injection WITHOUT a production override: the canonical file is rewritten inside
    the image, at its ordinary path, so the copied CLI resolves it naturally. Codex's point —
    the lease is deliberately given no environment hook, because that would be a bypass."""
    (image / "record" / "executive" / "leases.jsonl").write_text(EXHAUSTED, encoding="utf-8")


#  D-67, PROVED AT THE EFFECT BOUNDARY THROUGH THE REAL CLI. Its own fixture asserts over the
#  commands land.py attempted; this asserts over the world afterwards, which is the stronger
#  claim and the one that would have caught the defect without being told where to look.
verdict = refuses(argv=("python3", "tools/land.py", "--check-only"),
                  case="D-67 / a refused landing", setup=exhausted_lease,
                  expect_exit=2, expected_effects={}, timeout=180)
check("a landing refused by the lease changes NOTHING and contacts NOBODY",
      verdict["problems"] == [], str(verdict["problems"]))
check("...and it says the remote probe was withheld rather than skipping it silently",
      "NOT probed" in verdict["output"])


def lease_and_prompt(image: Path) -> None:
    exhausted_lease(image)
    (image / "zz_prompt.txt").write_text("hello\n", encoding="utf-8")


#  THE MONEY BOUNDARY. A refusal here must still leave its receipt — the one declared effect —
#  and must not reach for the `codex` binary, which the canary PATH would catch.
verdict = refuses(argv=("python3", "tools/codex_call.py", "--prompt-file", "zz_prompt.txt",
                        "--purpose", "fixture"),
                  case="codex_call under a spent lease", setup=lease_and_prompt,
                  expect_exit=3,
                  expected_effects={"record/executive/action-log.jsonl":
                                    JsonlAppend(rows=1, fields={"action": "codex_invoke",
                                                                "verified": False})},
                  timeout=180)
check("a refused Codex call writes its receipt and nothing else, and spends nothing",
      verdict["problems"] == [], str(verdict["problems"]))
check("...and the ONLY thing it touched is the action log",
      verdict["changed"] == ["record/executive/action-log.jsonl"], str(verdict["changed"]))


#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
