#!/usr/bin/env python3
"""The control 23 interlock: an observed violation must constrain the next action in its class.

D-58's second half. `land.py` observed six consecutive Pages deploy failures, attested every one
of them honestly, and permitted the next ordinary landing six times. **The logging was never the
failure.** These cases exist so that the transition from "observed violation" to "work is now
constrained" is exercised rather than described.

WHAT EACH ARM IS FOR, and why the baseline arms are not filler: an interlock that blocks
everything is broken rather than strict, and an interlock that blocks nothing is a comment. Every
blocking case here is paired with a case that must NOT block.

THE CRASH CASES ARE THE POINT. The two landings that mattered most were killed mid-wait and wrote
no attestation at all, so any design that depends on the failing process recording its own
failure inherits the same hole. Codex required transitions be tested for a crash between every
pair of steps, and the four below are the ones where a crash loses information:

    after the push is logged, before the wait          -> the obligation must still be visible
    after a failed attestation, before the incident    -> the incident must be reconstructible
    after a successful remediation, before resolution  -> must stay OPEN, not silently close
    during resolution-file creation                    -> must fail closed, not read as resolved

None of these touch the network: `observe` is substituted, because a test that needs GitHub to be
reachable is a test that does not run when it matters.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
passed = FAILED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, FAILED
    if ok:
        passed += 1
        print(f"  \033[32m✓\033[0m {name}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {name}\033[0m")
        if detail:
            print(f"      {detail[:300]}")


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ob = load("deploy_obligations")

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


class Sandbox:
    """Point the module at a temp incident directory and action log, and stub observation."""

    def __init__(self, rows: list[dict], observations: dict[str, dict]):
        self.rows = rows
        self.observations = observations

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self.tmp.name)
        (base / "incidents").mkdir()
        log = base / "action-log.jsonl"
        log.write_text("".join(json.dumps(r) + "\n" for r in self.rows), encoding="utf-8")
        self.saved = (ob.INCIDENTS, ob.LOG, ob.observe)
        ob.INCIDENTS, ob.LOG = base / "incidents", log
        ob.observe = lambda sha: self.observations.get(
            sha, {"state": ob.PENDING, "commit": sha, "why": "stubbed: nothing known"})
        return base

    def __exit__(self, *exc):
        ob.INCIDENTS, ob.LOG, ob.observe = self.saved
        self.tmp.cleanup()
        return False


def push(sha: str) -> dict:
    return {"action": "push", "verified": True, "claim": {"target_ref": "main", "commit": sha}}


def deploy(sha: str, served: str | None, verified: bool, observed: bool = True) -> dict:
    return {"action": "deploy", "verified": verified,
            "claim": {"commit": sha, "deployed_sha": served, "observed": observed,
                      "conclusion": "success" if verified else "failure"}}


def satisfied(sha: str) -> dict:
    return {"state": ob.SATISFIED, "commit": sha, "served_sha": sha}


def failed(sha: str) -> dict:
    return {"state": ob.INCIDENT, "commit": sha, "why": "the Pages workflow concluded failure"}


print("\nthe ordinary case must NOT block — an interlock that always fires is not a control")

with Sandbox([push(SHA_A), deploy(SHA_A, SHA_A, True)], {SHA_A: satisfied(SHA_A)}):
    reasons, _ = ob.blocking(reconcile=True)
    check("BASELINE: a push that deployed and is served blocks nothing", reasons == [], str(reasons))

print("\nan OBSERVED failure must block the next ordinary landing")

with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    reasons, _ = ob.blocking(reconcile=True)
    check("a failed deploy blocks", len(reasons) == 1, str(reasons))
    check("...and an incident file was written",
          len(list((base / "incidents").glob("*.json"))) == 1)
    #  AND IT KEEPS BLOCKING. Six honest attestations did not stop the seventh landing; a check
    #  that only complains once would reproduce that exactly.
    reasons_again, _ = ob.blocking(reconcile=True)
    check("...and it STILL blocks on the next call, which is the whole defect",
          len(reasons_again) >= 1, str(reasons_again))
    check("...without opening a second incident for the same commit",
          len(list((base / "incidents").glob("*.json"))) == 1)

print("\nPENDING is not a violation, and it still blocks")

with Sandbox([push(SHA_A)], {}) as base:
    #  No deploy row at all: the interrupted-wait case, which wrote nothing.
    reasons, _ = ob.blocking(reconcile=True)
    check("a push with no deploy record blocks", len(reasons) == 1, str(reasons))
    check("...and does NOT open an incident, because nothing was observed to be wrong",
          list((base / "incidents").glob("*.json")) == [])

with Sandbox([push(SHA_A)], {SHA_A: satisfied(SHA_A)}) as base:
    reasons, _ = ob.blocking(reconcile=True)
    check("...and clears by itself once the deploy can be observed", reasons == [], str(reasons))
    check("...still opening no incident", list((base / "incidents").glob("*.json")) == [])

print("\nresolution takes evidence, and nothing else")

with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    ob.blocking(reconcile=True)
    ident = next(iter(ob.load_incidents()))

    #  The head is NOT deployed: refuse. This is the arm that stops an incident being closed by
    #  asserting it is fine.
    code, message = ob.resolve([ident], SHA_B)
    check("resolving against a head that is not deployed is REFUSED", code == 1, message)
    check("...and no recovery artifact was written",
          not (base / "incidents" / "recoveries").exists()
          or list((base / "incidents" / "recoveries").glob("*.json")) == [])
    check("...and it still blocks", len(ob.blocking()[0]) >= 1)

    #  Now the head IS deployed and served.
    ob.observe = lambda sha: satisfied(sha) if sha == SHA_B else failed(sha)
    code, message = ob.resolve([ident], SHA_B)
    check("resolving against a deployed, served head SUCCEEDS", code == 0, message)
    check("...and the incident file itself was NOT edited — corrections attach",
          "resolution" not in json.loads((base / "incidents" / f"{ident}.json")
                                         .read_text(encoding="utf-8")))
    #  The INCIDENT is closed. The obligation on SHA_A itself is still outstanding in this
    #  fixture -- its deploy row says it was never served -- and the tool is right to keep
    #  saying so. Assert the thing that was resolved, not a blanket silence.
    check("...and no incident remains open", ob.open_incidents(ob.load_incidents()) == [])
    remaining, _ = ob.blocking()
    check("...and what still blocks is the undischarged push, not the closed incident",
          len(remaining) == 1 and "incident" not in remaining[0].lower(), str(remaining))

print("\ncrash between transitions — the paths that lose information")

#  CRASH 1: after the push is logged, before the wait. This is the shape that killed two
#  landings. The obligation must be visible from the log alone.
with Sandbox([push(SHA_A)], {SHA_A: failed(SHA_A)}) as base:
    reasons, _ = ob.blocking(reconcile=True)
    check("crash after push, before the wait: reconciling still finds the failure",
          len(reasons) == 1 and "incident" in reasons[0].lower(), str(reasons))

#  CRASH 2: the failed attestation was written, the process died before creating the incident.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    check("crash after the attestation, before the incident: none exists yet",
          list((base / "incidents").glob("*.json")) == [])
    reasons, _ = ob.blocking(reconcile=True)
    check("...and the next preflight reconstructs it from the log", len(reasons) == 1,
          str(reasons))

#  CRASH 3: a remediation deployed successfully, and died before the resolution was written.
#  RECOVERED IS NOT RESOLVED. If this cleared itself, nobody would ever have to look at the
#  incident — which is precisely how six correct attestations were passed over.
#
#  This case also found a real gap. The reconciler originally examined only the LAST push, so a
#  failure followed by a successful landing was invisible to it: exactly the historical sequence,
#  six times over. `unreconciled_failures` now scans every deploy row.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False), push(SHA_B), deploy(SHA_B, SHA_B, True)],
             {SHA_A: failed(SHA_A), SHA_B: satisfied(SHA_B)}) as base:
    ob.blocking(reconcile=True)
    reasons, _ = ob.blocking(reconcile=True)
    check("crash after a successful remediation, before resolution: it STILL blocks",
          len(reasons) >= 1, str(reasons))
    check("...and the earlier failure was reconstructed even though a LATER push succeeded",
          len(list((base / "incidents").glob("*.json"))) == 1,
          "a reconciler that only reads the last push walks past every historical failure")
    check("...and a later successful deploy did not silently close it",
          list((base / "incidents").glob("*.resolution.json")) == [])

#  CRASH 4: a half-written resolution file. Fail closed.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    ob.blocking(reconcile=True)
    ident = next(iter(ob.load_incidents()))
    (base / "incidents" / "recoveries").mkdir()
    (base / "incidents" / "recoveries" / "half.json").write_text('{"resolves": ', encoding="utf-8")
    reasons, _ = ob.blocking()
    check("crash during resolution: a truncated resolution is STATE UNKNOWN, not resolved",
          len(reasons) == 1 and "cannot be interpreted" in reasons[0], str(reasons))

print("\nmalformed state fails CLOSED — unknown must never read as clear")

for label, write in (
        ("an unreadable incident",
         lambda d: (d / "2026-01-01-deploy-zzz.json").write_text("{oops", encoding="utf-8")),
        ("an incident naming no commit",
         lambda d: (d / "2026-01-01-deploy-zzz.json").write_text(json.dumps(
             {"schema_version": ob.INCIDENT_SCHEMA, "id": "2026-01-01-deploy-zzz",
              "source_attestation": "x"}), encoding="utf-8")),
        ("an incident whose internal id disagrees with its filename",
         lambda d: (d / "2026-01-01-deploy-zzz.json").write_text(json.dumps(
             {"schema_version": ob.INCIDENT_SCHEMA, "id": "someone-else", "commit": SHA_A,
              "source_attestation": "x"}), encoding="utf-8")),
        ("an incident declaring an unknown schema version",
         lambda d: (d / "2026-01-01-deploy-zzz.json").write_text(json.dumps(
             {"schema_version": "made-up", "id": "2026-01-01-deploy-zzz", "commit": SHA_A,
              "source_attestation": "x"}), encoding="utf-8")),
        ("an incident with no source_attestation, so it names no observed event",
         lambda d: (d / "2026-01-01-deploy-zzz.json").write_text(json.dumps(
             {"schema_version": ob.INCIDENT_SCHEMA, "id": "2026-01-01-deploy-zzz",
              "commit": SHA_A}), encoding="utf-8")),
        ("a recovery resolving an incident that does not exist",
         lambda d: [(d / "recoveries").mkdir(exist_ok=True),
                    (d / "recoveries" / "r.json").write_text(json.dumps(
                        {"schema_version": ob.RECOVERY_SCHEMA, "resolves": ["ghost"],
                         "resolving_commit": SHA_B,
                         "evidence": {"state": "SATISFIED", "commit": SHA_B,
                                      "served_sha": SHA_B}}), encoding="utf-8")]),
        ("a recovery whose evidence is not a SATISFIED observation",
         lambda d: [(d / "recoveries").mkdir(exist_ok=True),
                    (d / "recoveries" / "r.json").write_text(json.dumps(
                        {"schema_version": ob.RECOVERY_SCHEMA, "resolves": ["x"],
                         "resolving_commit": SHA_B, "evidence": {"state": "PENDING"}}),
                        encoding="utf-8")]),
        ("a follows pointer to nothing",
         lambda d: (d / "2026-01-01-deploy-zzz.json").write_text(json.dumps(
             {"schema_version": ob.INCIDENT_SCHEMA, "id": "2026-01-01-deploy-zzz",
              "commit": SHA_A, "source_attestation": "x", "follows": "nope"}), encoding="utf-8")),
        ("a cycle in the follows chain",
         lambda d: [(d / "2026-01-01-deploy-x.json").write_text(json.dumps(
             {"schema_version": ob.INCIDENT_SCHEMA, "id": "2026-01-01-deploy-x",
              "commit": SHA_A, "source_attestation": "x",
              "follows": "2026-01-01-deploy-y"}), encoding="utf-8"),
             (d / "2026-01-01-deploy-y.json").write_text(json.dumps(
                 {"schema_version": ob.INCIDENT_SCHEMA, "id": "2026-01-01-deploy-y",
                  "commit": SHA_B, "source_attestation": "y",
                  "follows": "2026-01-01-deploy-x"}), encoding="utf-8")])):
    with Sandbox([push(SHA_A), deploy(SHA_A, SHA_A, True)], {SHA_A: satisfied(SHA_A)}) as base:
        write(base / "incidents")
        reasons, _ = ob.blocking()
        check(f"{label} -> blocks with STATE UNKNOWN",
              len(reasons) == 1 and "cannot be interpreted" in reasons[0], str(reasons))

print("\nland.py's interlock — the policy itself, without performing a landing")

land = load("land")
check("land.py imports the ledger rather than reimplementing it",
      land.obligations is ob or land.obligations.__name__ == "deploy_obligations")
check("the deploy wait is shorter than the 10-minute harness ceiling that truncated two of them",
      land.DEPLOY_TIMEOUT_S < 600, f"{land.DEPLOY_TIMEOUT_S}s")

with Sandbox([push(SHA_A), deploy(SHA_A, SHA_A, True)], {SHA_A: satisfied(SHA_A)}):
    check("BASELINE: with nothing outstanding, an ordinary landing proceeds",
          land.interlock(check_only=False, remediating="", no_deploy_check=False) == [])
    check("...and --no-deploy-check is available when nothing is undischarged",
          land.interlock(check_only=False, remediating="", no_deploy_check=True) == [])

with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    ob.blocking(reconcile=True)
    ident = next(iter(ob.load_incidents()))

    refusal = land.interlock(check_only=False, remediating="", no_deploy_check=False)
    check("an ordinary landing is REFUSED while an incident is open", refusal != [])
    check("...and the refusal names the remediation route rather than just saying no",
          any("--remediating" in line for line in refusal), str(refusal))

    #  THE DIAGNOSTIC PATH. An interlock that also blocks looking at itself becomes an outage,
    #  and the operator's next move is to disable it.
    check("--check-only is NOT blocked, so the state can still be inspected",
          land.interlock(check_only=True, remediating="", no_deploy_check=False) == [])

    #  THE ONE FLAG THAT COULD SWITCH IT OFF FROM INSIDE.
    check("--no-deploy-check is REFUSED while blocked",
          land.interlock(check_only=False, remediating="", no_deploy_check=True) != [])
    check("...and refused even when remediating, because not looking is the original defect",
          land.interlock(check_only=False, remediating=ident, no_deploy_check=True) != [])

    check("naming the OPEN incident permits the landing",
          land.interlock(check_only=False, remediating=ident, no_deploy_check=False) == [])
    check("naming an incident that does not exist does NOT",
          land.interlock(check_only=False, remediating="no-such-id", no_deploy_check=False) != [])

    #  A RESOLVED ID MUST NOT BE A SKELETON KEY. Without this, one closed incident licenses every
    #  future landing forever and the interlock quietly stops existing.
    ob.observe = lambda sha: satisfied(sha) if sha == SHA_B else failed(sha)
    ob.resolve([ident], SHA_B)
    check("naming an ALREADY RESOLVED incident does not license a landing",
          land.interlock(check_only=False, remediating=ident, no_deploy_check=False) != [])


print("\nthe counterexamples external review reproduced against the first version")

#  1. A PARSEABLE BUT INVALID recovery closed an incident. `{"garbage": true}` was attached as a
#     resolution because the loader accepted any truthy JSON, which made "only evidence closes an
#     incident" false while that sentence sat in the module docstring.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    ob.blocking(reconcile=True)
    ident = next(iter(ob.load_incidents()))
    (base / "incidents" / "recoveries").mkdir()
    (base / "incidents" / "recoveries" / "r.json").write_text('{"garbage": true}',
                                                              encoding="utf-8")
    reasons, _ = ob.blocking()
    check("a truthy but INVALID recovery does not close an incident",
          len(reasons) == 1 and "cannot be interpreted" in reasons[0], str(reasons))

#  2. A SECOND FAILURE OF AN ALREADY-RESOLVED COMMIT, followed by a later successful push. The
#     first version keyed incidents on the COMMIT, so once any incident named it — resolved or
#     not — the recurrence was invisible and the ledger reported no blockers at all.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    ob.blocking(reconcile=True)
    first = next(iter(ob.load_incidents()))
    ob.observe = lambda sha: satisfied(sha) if sha == SHA_B else failed(sha)
    ob.resolve([first], SHA_B)
    check("setup: the first failure is resolved", ob.open_incidents(ob.load_incidents()) == [])

    #  Same commit fails AGAIN, at a different time, and something else lands after it.
    ob.LOG.write_text("".join(json.dumps(r) + "\n" for r in [
        push(SHA_A), deploy(SHA_A, "old", False),
        {**deploy(SHA_A, "old", False), "utc": "2026-08-12T09:00:00Z"},
        push(SHA_B), deploy(SHA_B, SHA_B, True)]), encoding="utf-8")
    reasons, _ = ob.blocking(reconcile=True)
    check("a SECOND failure of an already-resolved commit is not invisible",
          len(reasons) >= 1, str(reasons))
    incidents = ob.load_incidents()
    check("...it opens a second incident rather than reusing the resolved one",
          len(incidents) == 2, f"{len(incidents)} incident(s)")
    check("...and the recurrence is CHAINED to the resolved one, so repetition is not understated",
          any(d.get("follows") == first for d in incidents.values()),
          str({i: d.get("follows") for i, d in incidents.items()}))

#  3. TWO INTERRUPTED PUSHES, frontier semantics. `git merge-base` cannot relate two invented
#     shas, so neither discharges the other — the honest answer, and the one that keeps an
#     obligation rather than dropping it on an assumption about ancestry.
with Sandbox([push(SHA_A), push(SHA_B), deploy(SHA_B, SHA_B, True)],
             {SHA_A: satisfied(SHA_A), SHA_B: satisfied(SHA_B)}) as base:
    rows = ob.log_rows()
    outstanding = ob.outstanding_pushes(rows)
    check("a served push that is NOT an ancestor does not discharge the earlier one",
          SHA_A in outstanding, f"outstanding={[s[:8] for s in outstanding]}")

#  ...and with REAL commits, where ancestry is knowable, the frontier does collapse. This is the
#  arm that stops the rule from being "never discharge anything", which would block permanently.
import subprocess as _sp
head_sha = _sp.run(["git", "rev-parse", "HEAD"], cwd=ROOT.parent,
                   capture_output=True, text=True).stdout.strip()
parent_sha = _sp.run(["git", "rev-parse", "HEAD~1"], cwd=ROOT.parent,
                     capture_output=True, text=True).stdout.strip()
if len(head_sha) == 40 and len(parent_sha) == 40:
    with Sandbox([push(parent_sha), push(head_sha), deploy(head_sha, head_sha, True)], {}):
        outstanding = ob.outstanding_pushes(ob.log_rows())
        check("a served DESCENDANT does discharge the earlier push — the frontier collapses",
              outstanding == [], f"outstanding={[s[:8] for s in outstanding]}")
    check("...and ancestry is what did it, not the order of the rows",
          ob.is_ancestor(parent_sha, head_sha) is True)
    check("...while an unrelated invented sha is UNKNOWN, which is not a discharge",
          ob.is_ancestor(SHA_A, head_sha) is not True)

#  4. RE-RUNNING BOOTSTRAP must do nothing. The first version keyed on the commit and skipped
#     resolved ones, so a second run manufactured six fresh suffixed incidents out of nothing.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False)], {SHA_A: failed(SHA_A)}) as base:
    ob.observe = lambda sha: satisfied(sha) if sha == SHA_B else failed(sha)
    code, message = ob.bootstrap(SHA_B)
    check("bootstrap materialises the historical failure", code == 0, message)
    before = len(list((base / "incidents").glob("*.json")))
    code, message = ob.bootstrap(SHA_B)
    check("...and re-running it creates nothing", code == 0 and "nothing to bootstrap" in message,
          message)
    check("...leaving the incident count unchanged",
          len(list((base / "incidents").glob("*.json"))) == before)

#  5. A MALFORMED ACTION LOG is state unknown, not a traceback. A traceback exits 1, and 1 is the
#     code that means "blocked", so a crash would have been indistinguishable from a finding.
with Sandbox([push(SHA_A)], {}) as base:
    ob.LOG.write_text('{"action": "push"}\n{not json\n', encoding="utf-8")
    reasons, _ = ob.blocking(reconcile=True)
    check("a malformed action log blocks with STATE UNKNOWN rather than raising",
          len(reasons) == 1 and "cannot be interpreted" in reasons[0], str(reasons))

#  6. THE OBSERVER IS PINNED. It must not accept a conclusion from some other workflow that
#     happens to have run on the same commit. Asserted on the URL it builds, because the
#     alternative is a test that needs GitHub to be reachable.
seen = {}
saved_api, saved_env = ob._api, os.environ.get("GITHUB_TOKEN")
os.environ["GITHUB_TOKEN"] = "fixture"
try:
    ob._api = lambda path: seen.setdefault("path", path) and None
    ob.observe(SHA_A)
    path = seen.get("path", "")
    check("the observer is pinned to the Pages workflow", f"workflows/{ob.WORKFLOW_FILE}" in path)
    check("...to a push event", "event=push" in path)
    check("...and to the target branch", f"branch={ob.TARGET_BRANCH}" in path)
finally:
    ob._api = saved_api
    if saved_env is None:
        os.environ.pop("GITHUB_TOKEN", None)
    else:
        os.environ["GITHUB_TOKEN"] = saved_env

#  7. THE LEASE IS CHECKED BEFORE RECONCILIATION WRITES. Reconciliation materialises incident
#     files, and this repository requires the lease before a governed write. The interlock used
#     to reconcile first and leave the lease to a gate that runs later.
src = inspect.getsource(land.interlock)
check("the interlock requires the lease BEFORE it reconciles",
      src.index('lease.require') < src.index('obligations.blocking'),
      "reconciliation writes incident files; the lease must be checked first")

#  8. A REFUSED PUSH OWES NOTHING. The module's first sentence is "every VERIFIED push owes a
#     deployment" and the code counted every push row. The real log holds one attestation with
#     verified:false — a 2026-08-09 probe of the push profile using an all-zero sha — and it
#     produced a permanent obligation on a commit that does not exist, which would have blocked
#     every landing forever. Found by running the tool against the real log.
ZERO = "0" * 40
with Sandbox([{"action": "push", "verified": False,
               "claim": {"target_ref": "main", "commit": ZERO},
               "problems": ["00000000 is not reachable from main"]},
              push(SHA_A), deploy(SHA_A, SHA_A, True)], {SHA_A: satisfied(SHA_A)}):
    outstanding = ob.outstanding_pushes(ob.log_rows())
    check("a REFUSED push attestation owes no deployment",
          ZERO not in outstanding, f"outstanding={[s[:8] for s in outstanding]}")
    check("...and with it excluded, nothing blocks", ob.blocking(reconcile=True)[0] == [])

#  9. CHRONOLOGY. A deployment cannot discharge a push that had not happened yet. The first
#     version put every push in one set and every served commit in another and asked only about
#     ancestry, so a deploy of a descendant ANYWHERE in the log cleared a later re-push.
if len(head_sha) == 40 and len(parent_sha) == 40:
    with Sandbox([push(parent_sha), push(head_sha), deploy(head_sha, head_sha, True)], {}):
        check("BASELINE: push then a served descendant DOES discharge it",
              ob.outstanding_pushes(ob.log_rows()) == [])
    with Sandbox([push(parent_sha), deploy(head_sha, head_sha, True), push(parent_sha)], {}):
        outstanding = ob.outstanding_pushes(ob.log_rows())
        check("a deploy that happened BEFORE a re-push does not discharge it",
              parent_sha in outstanding,
              f"outstanding={[s[:8] for s in outstanding]}; order is part of the fact")

#  10. TWO RECOVERIES ON THE SAME DAY AGAINST THE SAME HEAD. Named by (date, head) alone, the
#      second overwrote the first and every incident the first had closed silently REOPENED —
#      a correction editing a correction, in the tool whose rule is corrections attach.
with Sandbox([push(SHA_A), deploy(SHA_A, "old", False),
              {**deploy(SHA_A, "old", False), "utc": "2026-08-12T09:00:00Z"}],
             {SHA_A: failed(SHA_A)}) as base:
    ob.blocking(reconcile=True)
    idents = sorted(ob.load_incidents())
    check("setup: two distinct failure events, two incidents", len(idents) == 2, str(idents))
    ob.observe = lambda sha: satisfied(sha) if sha == SHA_B else failed(sha)
    ob.resolve([idents[0]], SHA_B)
    ob.resolve([idents[1]], SHA_B)
    check("two SEPARATE recoveries on the same day against the same head both survive",
          len(list((base / "incidents" / "recoveries").glob("*.json"))) == 2)
    check("...and neither incident reopened", ob.open_incidents(ob.load_incidents()) == [])

#  A recovery whose filename and internal id disagree must be STATE UNKNOWN — the check that
#  makes the uniqueness above meaningful rather than a naming convention.
with Sandbox([push(SHA_A), deploy(SHA_A, SHA_A, True)], {SHA_A: satisfied(SHA_A)}) as base:
    (base / "incidents" / "recoveries").mkdir()
    (base / "incidents" / "recoveries" / "named-one-thing.json").write_text(json.dumps(
        {"schema_version": ob.RECOVERY_SCHEMA, "id": "called-another", "resolves": ["x"],
         "resolving_commit": SHA_B,
         "evidence": {"state": "SATISFIED", "commit": SHA_B, "served_sha": SHA_B}}),
        encoding="utf-8")
    reasons, _ = ob.blocking()
    check("a recovery whose id disagrees with its filename -> STATE UNKNOWN",
          len(reasons) == 1 and "cannot be interpreted" in reasons[0], str(reasons))

#  11. THE LEASE, BEHAVIOURALLY. The source-ordering assertion above documents the intent; this
#      proves it. An expired lease must refuse BEFORE reconciliation runs, because reconciliation
#      writes incident files and this repository requires the lease before a governed write.
called = []
saved_require, saved_blocking = land.lease.require, land.obligations.blocking


def _spy(*a, **k):
    called.append("reconciled")
    return [], {}


try:
    land.obligations.blocking = _spy
    land.lease.require = lambda cls: (_ for _ in ()).throw(RuntimeError("lease expired"))
    refusal = land.interlock(check_only=False, remediating="", no_deploy_check=False)
    check("an expired lease REFUSES the landing", refusal != [])
    check("...and reconciliation never ran, so nothing was written under it", called == [],
          "reconciliation materialises incident files; it must not run before the lease check")

    land.lease.require = lambda cls: {"live": True}
    land.interlock(check_only=False, remediating="", no_deploy_check=False)
    check("BASELINE: with a live lease, reconciliation does run", called == ["reconciled"])
finally:
    land.lease.require, land.obligations.blocking = saved_require, saved_blocking

print(f"\n{passed} passed, {FAILED} failed")
raise SystemExit(1 if FAILED else 0)
