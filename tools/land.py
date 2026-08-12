#!/usr/bin/env python3
"""Run every gate, then commit, push, verify and attest — or refuse without touching git.

    python3 tools/land.py -m "the commit message"
    python3 tools/land.py -F message.txt
    python3 tools/land.py --check-only          # run the gates, change nothing

**DETERMINISTIC.** No LLM, no network beyond the push itself.

Why this exists
---------------
Landing work is five gates and four git steps in a fixed order, each individually skippable, and
skipping one is silent. The record of doing it by hand:

* `run_all.py | tail -2` printed `All 16 suites passed` from an inner suite while the runner
  exited **1**. The rule against reading a verdict from output text was already written down, in
  a file loaded at the start of every session, and `tail` is still what you reach for.
* `echo "$(basename $f) rc=$?"` reported *basename's* status. Two red suites were pushed.
* Three commits went to a round branch while `git push origin main` pushed an unchanged main and
  reported success.
* A conflicted merge was completed blind, leaving conflict markers inside `MANIFEST.sha256` and
  the anchor log — the two files that make the record's central claim checkable.
* `check_quotations.py` caught a bad quotation on 2026-08-10 only because `rebuild.py` happened
  to be run first. Nothing required it.

So the order stops being a habit and becomes a program. **Every gate's status is taken from its
own exit code**, captured directly — never parsed out of its output, which is what failed.

What it refuses on
-------------------
Any gate exiting non-zero; an expired lease; a detached HEAD; unmerged paths; conflict markers in
a governed file; a push whose commit is not reachable from `origin/main` afterwards. Refusal
happens **before** `git commit` wherever possible, so a rejected run leaves the tree exactly as it
was rather than a commit needing to be undone.

What it cannot establish
-------------------------
* **That the gates test the right thing.** All green means the checks that exist passed. The
  quotation checker verifies a quotation appears in the corpus, not that a document's argument is
  sound; `check_executive_context.py` verifies identity, not truth — it passed on a pinned file
  containing a claim already proven false.
* **That the commit message is accurate.** Nothing here reads it.
* **That this was the right work to land.**
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import deploy_obligations as obligations                                # noqa: E402
import executive_lease as lease                                          # noqa: E402
import executive_log as ex                                              # noqa: E402

#  Ordered. `rebuild` first because it regenerates what the later checks read; the quotation
#  check runs inside it and again here, because relying on that coincidence is what happened.
#  THESE MUST BE THE GATES CI RUNS, or a green landing means nothing about whether the site
#  will deploy. On 2026-08-10 land.py reported all gates green, the push verified, and the
#  custodian was told a page was published -- while the Pages workflow FAILED on
#  `tools/test_integrity.py`, a suite land.py did not run because it does not live under
#  tools/tests/. The site kept serving the previous deploy and the page 404'd.
#
#  That is this project's own failure class inside the tool built to prevent it: a green signal
#  not causally downstream of what it certifies. "Gates green" certified the local checks; it
#  was reported as "published".
GATES = (
    ("rebuild", ["python3", "tools/rebuild.py"]),
    ("tests", ["python3", "tools/tests/run_all.py"]),
    #  Run by CI at .github/workflows step "Integrity regression suite". Slow, and worth it.
    ("integrity", ["python3", "tools/test_integrity.py"]),
    ("quotations", ["python3", "tools/check_quotations.py"]),
    #  NAMED `prose-triage`, NOT `claim-validity`, and the name is load-bearing. An external
    #  review predicted the worst failure mode of this gate before it existed: "land.py was
    #  green, therefore there were no unsupported claims." A green result here means detected
    #  candidates in CHANGED prose each received a disposition. Recall is UNKNOWN, and the tool
    #  prints that on every success so the sentence above cannot be written honestly.
    ("prose-triage", ["python3", "tools/check_claims.py"]),
    #  Control 44 turned on this repository: the self-application table must have a determination
    #  for every control in the register. It checks COMPLETENESS, not correctness -- the party
    #  that wrote the determinations is the party they describe.
    ("self-application", ["python3", "tools/self_application.py", "--check"]),
    #  The control-application table names code files and tests per control. A row pointing at a
    #  deleted or renamed file is a compliance claim about something that is not there, so this
    #  refuses rather than letting the table decay into decoration. It checks SUBSTANTIATION --
    #  that every row can be backed -- not that any control is satisfied.
    #  CONTROL 45, MECHANISED. A guard declared in the code and named by no fixture is where an
    #  unreachable one hides -- three were found in one week, each by a human happening to look.
    #  And a fixture naming a guard that no longer exists FAILS here, rather than passing because
    #  a neighbouring guard fired, which is what control 45 forbids without evidence.
    ("guard-identity", ["python3", "tools/guards.py", "--check"]),
    ("control-application", ["python3", "tools/control_application.py", "--check"]),
    #  NON-REGRESSION ONLY, and the name says so. It took three days and D-68 to get here: the
    #  measure underneath was counting prose as evidence and 21 of 41 determinations rested on a
    #  600-character proximity heuristic, so wiring the check in earlier would have given a
    #  landing gate's authority to numbers that were wrong. Codex refused four things by name,
    #  and "a gate called coverage" was one of them. Green here means nothing was LOST and no new
    #  debt entered; it prints the remaining debt beside every success so a stagnant number
    #  cannot look like a healthy one.
    ("negative-control-ratchet", ["python3", "tools/control_coverage.py", "--check"]),
    ("context-pins", ["python3", "tools/check_executive_context.py"]),
    ("lease", ["python3", "tools/executive_lease.py"]),
)

#  PATHS VERIFIED TO EXIST. Two of these were `record/deficiencies.md` and
#  `record/deficiency-register.json`, which are not files -- the real one is
#  `corpus/deficiencies.md`. The conflict-marker check silently examined nothing for them, which
#  is the same class of defect as a gate reading the wrong exit code.
GOVERNED = ("corpus/MANIFEST.sha256", "record/anchors/manifest-anchors.jsonl",
            "corpus/deficiencies.md")


REPO_SLUG = "open-asi-governance/open-asi-governance-forum"
#  540, NOT 900. The harness that drives this tool kills a call at 10 minutes, so a 15-minute
#  wait could never complete inside one: two landings were cut off mid-wait and wrote no deploy
#  attestation at all, which is half of D-58. The wait is now shorter than the ceiling, and what
#  it no longer covers is recovered rather than lost -- the push entry is an OBLIGATION, and the
#  next preflight reconciles it. Waiting longer was never the fix; making the wait resumable was.
DEPLOY_TIMEOUT_S = 540
DEPLOY_POLL_S = 20


def _api(path: str) -> dict | list | None:
    """GitHub API GET. Returns None on any failure -- the caller must treat that as UNOBSERVED."""
    token = os.environ.get("GITHUB_TOKEN")
    request = urllib.request.Request(f"https://api.github.com/repos/{REPO_SLUG}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except Exception:                                                   # noqa: BLE001
        return None


def wait_for_deploy(sha: str) -> dict:
    """Poll the PINNED observer until the Pages run for `sha` completes, then report.

    ONE OBSERVER, NOT TWO. This function used to run its own query --
    `/actions/runs?head_sha=...&per_page=1` -- which is not restricted to the Pages workflow, the
    push event or the target branch, and would happily take a conclusion from some unrelated
    workflow and open an incident from it. The ledger's `observe()` is pinned to all three, and
    keeping a second subtly different verifier beside it is how the two drift apart.

    UNOBSERVED IS NOT SUCCESS. Every path that cannot look -- no token, API error, still running
    at the deadline -- returns observed=False, and the attestation profile refuses it. A check
    that passes when it cannot see is the exact defect it exists to catch.
    """
    deadline = time.time() + DEPLOY_TIMEOUT_S
    result = obligations.observe(sha)
    while (result["state"] == obligations.PENDING and result.get("retriable")
           and time.time() < deadline):
        time.sleep(DEPLOY_POLL_S)
        result = obligations.observe(sha)
    if result["state"] == obligations.SATISFIED:
        return {"observed": True, "commit": sha, "conclusion": "success",
                "deployed_sha": result.get("served_sha"), "run_url": result.get("run_url")}
    if result["state"] == obligations.INCIDENT:
        return {"observed": True, "commit": sha, "conclusion": result.get("conclusion", "failure"),
                "deployed_sha": result.get("served_sha"), "run_url": result.get("run_url"),
                "why": result.get("why")}
    return {"observed": False, "commit": sha, "why": result.get("why", "not observed"),
            "run_url": result.get("run_url")}


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a command and return ITS OWN exit status. The status is never inferred from output."""
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def preflight(target_branch: str) -> list[str]:
    """Everything that must hold before git is touched at all."""
    problems = []
    #  BOTH classes. The push is separately governed and was never checked.
    for action_class in ("commit", "push"):
        try:
            lease.require(action_class)
        except (lease.LeaseRefused, lease.UnknownActionClass) as refused:
            problems.append(f"lease ({action_class}): {refused}")
    #  THE LEASE IS A PRECONDITION OF THE REST, not one problem among several. D-67: this
    #  function accumulated refusals and kept going, so a landing REFUSED BY THE LEASE still ran
    #  `git push --dry-run origin HEAD:main` — an authenticated network operation against the
    #  remote, on a denied path, inside the tool that enforces control 64. Codex found it while
    #  reviewing a harness designed to catch exactly this class, and observed that a filesystem
    #  snapshot would never have seen it: nothing in the working tree changes.
    #
    #  The LOCAL checks below still run and still report, because refusing to say what else is
    #  wrong turns one refusal into several round trips. Only the external probe is withheld.
    leased = not problems
    code, branch = run(["git", "branch", "--show-current"])
    branch = branch.strip()
    if not branch:
        problems.append("HEAD is detached; a commit here is not on any branch")
    elif branch != target_branch:
        #  THE ACTUAL HISTORICAL DEFECT. Three commits went to a round branch while
        #  `git push origin main` pushed an unchanged main and reported success. Checking only
        #  for a detached HEAD left that exact path open, in the tool whose docstring cites it.
        problems.append(f"on branch {branch!r} but asked to push {target_branch!r}; "
                        f"committing here and pushing there is how three commits were lost")
    #  CAN WE ACTUALLY PUSH? Checked BEFORE committing, because on 2026-08-11 this tool committed
    #  twice with GH_TOKEN_OAGF unset, failed at the push, and left the commits local while the
    #  harness reported the background task complete with exit 0. A commit that cannot be pushed
    #  is not "landed", and discovering that after the commit is the wrong order. Shell state does
    #  not persist between tool invocations here, so an env var present a minute ago proves
    #  nothing about this process.
    #  `git push --dry-run`, NOT `git ls-remote`. The first version of this check used ls-remote
    #  and passed with no credentials at all, because this repository is PUBLIC and anonymous
    #  read succeeds. It tested reachability while claiming to test push capability -- a green
    #  signal not downstream of what it certifies, written inside the fix for that exact class.
    #  A dry-run push exercises the credential helper and fails the way a real push would.
    if not leased:
        problems.append(
            "the remote push capability was NOT probed, because the lease refused first. A "
            "dry-run push is an authenticated network operation, and performing one after an "
            "authorization refusal is the effect-boundary failure this repository filed D-67 for.")
        return problems
    code, dry = run(["git", "push", "--dry-run", "origin", f"HEAD:{target_branch}"])
    if code != 0:
        problems.append(
            f"a dry-run push to origin/{target_branch} failed, so a real one would too and the "
            f"commit would be stranded: {dry.strip().splitlines()[-1][:160] if dry.strip() else 'no output'}. "
            f"If the credential helper needs a token, source it in the SAME command as this one; "
            f"the environment does not carry between tool invocations.")

    code, status = run(["git", "status", "--porcelain"])
    unmerged = [ln for ln in status.splitlines() if ln[:2] in
                ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
    if unmerged:
        problems.append(f"{len(unmerged)} unmerged path(s) remain")
    for rel in GOVERNED:
        path = REPO_ROOT / rel
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            if "\n<<<<<<< " in text or "\n>>>>>>> " in text:
                problems.append(f"conflict markers in {rel}")
    return problems


def admitted(name: str, code: int) -> bool:
    """Which exit states this caller accepts from a gate. **Only zero, from every one of them.**

    Named rather than inlined into an `all(...)` because it is a POLICY and a policy that exists
    only as an expression cannot be tested, cited, or argued with.

    It matters most for `context-pins`. Since 2026-08-12 `check_executive_context.py` has four
    states, and exit 3 means *no contradiction found, and coverage was incomplete* — a live
    governing file that could not be examined in this environment. CI admits 3, declared in the
    workflow, because two of the three pinned files are absolute paths on the operator's machine
    and a runner genuinely cannot see them.

    **This caller must not.** Landing happens on the workbench that holds those files, which is
    the one place the comparison is meaningful; admitting 3 here would let the operator's
    governing instructions drift out of the record unnoticed, which is the entire hazard the pin
    exists for. So the rule stays: every gate, exactly zero.
    """
    return code == 0


def gates() -> tuple[bool, list[tuple[str, int, str]]]:
    results = []
    for name, cmd in GATES:
        code, output = run(cmd)
        results.append((name, code, output))
    return all(admitted(name, code) for name, code, _ in results), results


def interlock(check_only: bool, remediating: str, no_deploy_check: bool) -> list[str]:
    """CONTROL 23: an observed violation must constrain the next action in its class.

    Returns the refusal lines, or an empty list to proceed. **A function, not an inline block**,
    for the same reason `admitted` is one: a policy that exists only as control flow inside
    `main` cannot be tested without performing the very action it governs.

    D-58. This tool observed six consecutive Pages deploy failures, attested every one of them
    honestly, and then permitted the next ordinary landing six times. Eight commits went
    unpublished for three and a half hours while every gate stayed green. The logging was never
    the failure; there was no transition from "observed violation" to "work is now constrained".

    DIAGNOSTIC PATHS STAY OPEN. `--check-only`, and the ledger's own status and resolve commands,
    work while blocked. An interlock that also prevents looking at itself turns an incident into
    an outage, and the operator's next move would be to disable it.
    """
    if check_only:
        return []

    #  THE LEASE COMES FIRST. Reconciliation is not read-only -- it materialises incident files
    #  when it observes a failure -- and this repository requires the lease to be checked before
    #  a governed write. Codex caught the ordering: the lease was a GATE, and gates run after
    #  this point, so reconciliation could have written under an expired lease.
    try:
        lease.require("governed_write")
    except Exception as exc:                                            # noqa: BLE001
        return [f"REFUSED  {exc}"]

    blockers, _detail = obligations.blocking(reconcile=True)

    if remediating:
        try:
            incidents = obligations.load_incidents()
        except obligations.StateUnknown as exc:
            return [f"REFUSED  {exc}"]
        still_open = {d["_id"] for d in obligations.open_incidents(incidents)}
        if remediating not in incidents:
            return [f"REFUSED  no incident {remediating}"]
        if remediating not in still_open:
            #  A resolved incident would otherwise be a permanent skeleton key: name any old
            #  closed id and the interlock never applies again.
            return [f"REFUSED  incident {remediating} is already resolved, so naming it does "
                    f"not license a landing"]
        if no_deploy_check:
            return ["REFUSED  --no-deploy-check is unavailable while remediating. Not observing "
                    "the result is how the obligation went undischarged in the first place."]
        return []

    if not blockers:
        return []
    if no_deploy_check:
        #  The one flag that could turn the interlock off from the inside.
        return ["REFUSED  --no-deploy-check is unavailable while a deployment obligation is "
                "undischarged. Skipping the observation is what left it undischarged."]
    return [f"REFUSED  {reason}" for reason in blockers] + [
        "",
        "An ordinary landing is refused while a deployment obligation is undischarged.",
        "To land the FIX for it, name the incident:",
        "    python3 tools/land.py -F msg.txt --remediating <incident-id>",
        "To see the ledger:  python3 tools/deploy_obligations.py --status",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("-m", "--message", help="commit message")
    parser.add_argument("-F", "--file", help="file holding the commit message")
    parser.add_argument("--check-only", action="store_true", help="run the gates, change nothing")
    parser.add_argument("--branch", default="main", help="branch to push (default main)")
    parser.add_argument("--note", default="", help="note recorded on the attestations")
    parser.add_argument("--no-deploy-check", action="store_true",
                        help="skip waiting for the Pages deploy. The run then says so explicitly "
                             "rather than implying the site is current. UNAVAILABLE while a "
                             "deployment obligation is undischarged.")
    parser.add_argument("--remediating", metavar="INCIDENT_ID", default="",
                        help="land as a REMEDIATION of an open deploy incident. Required while "
                             "one is open; recorded on the attestation. The link says what this "
                             "landing claims to fix, not that it does.")
    args = parser.parse_args()

    refusal = interlock(check_only=args.check_only, remediating=args.remediating,
                        no_deploy_check=args.no_deploy_check)
    if refusal:
        for line in refusal:
            print(f"  {line}", file=sys.stderr)
        return 2

    problems = preflight(args.branch)
    if problems:
        for p in problems:
            print(f"  REFUSED  {p}", file=sys.stderr)
        return 2

    print("  gates:")
    ok, results = gates()
    for name, code, output in results:
        mark = "\033[32mpass\033[0m" if code == 0 else "\033[31mFAIL\033[0m"
        print(f"    {mark}  {name}  (exit {code})")
    if not ok:
        for name, code, output in results:
            if code:
                print(f"\n--- {name} exit {code} ---\n{output[-2500:]}", file=sys.stderr)
        print("\nREFUSED: a gate failed. Nothing was committed.", file=sys.stderr)
        return 1
    if args.check_only:
        print("\n  all gates green; --check-only, so nothing was committed")
        return 0
    if not (args.message or args.file):
        parser.error("-m or -F is required unless --check-only")

    code, output = run(["git", "add", "-A"])
    if code != 0:
        #  Its exit status was discarded. A failed stage followed by a "successful" commit of
        #  whatever was already staged is precisely the wrong-signal class this tool exists for.
        print(f"  REFUSED: git add exited {code}\n{output}", file=sys.stderr)
        return 1
    commit = ["git", "commit", "-q"] + (["-F", args.file] if args.file else ["-m", args.message])
    code, output = run(commit)
    if code != 0:
        print(f"  REFUSED: git commit exited {code}\n{output}", file=sys.stderr)
        return 1
    _, sha = run(["git", "rev-parse", "HEAD"])
    sha = sha.strip()
    code, output = run(["git", "push", "origin", args.branch])
    if code != 0:
        print(f"  push exited {code}\n{output}", file=sys.stderr)

    #  BOTH attestations, and they verify against the remote ref rather than the push's exit
    #  status -- a push can exit 0 having carried nothing, which is how an unchanged main was
    #  reported as a successful push three times.
    suite_code = dict((n, c) for n, c, _ in results)["tests"]
    note = args.note or "landed by land.py"
    if args.remediating:
        #  Permanent in the log: this landing CLAIMED to remedy that incident. Whether it did is
        #  not something any tool here can establish, and the wording says so.
        note = f"{note} | remediating {args.remediating} (claimed, not verified)"
    ex.attest("test", {"suite": "tools/tests/run_all.py", "exit_status": suite_code,
                       "status_from": "direct"}, note=note)
    try:
        ex.attest("push", {"target_ref": args.branch, "commit": sha}, note=note)
    except ex.AttestationFailed as failed:
        print(f"  ATTESTATION FAILED: {failed}", file=sys.stderr)
        return 1
    print(f"\n  landed {sha[:12]} on {args.branch}, gates green, both attestations filed")

    if args.no_deploy_check:
        print("  deploy NOT checked (--no-deploy-check). This commit is pushed and may or may "
              "not be served.")
        return 0

    print(f"  waiting for the Pages deploy (up to {DEPLOY_TIMEOUT_S // 60} min)…")
    result = wait_for_deploy(sha)
    try:
        ex.attest("deploy", result, note=args.note or "deploy check by land.py")
    except ex.AttestationFailed as failed:
        print(f"\n  \033[31mDEPLOY NOT CONFIRMED\033[0m — {failed}", file=sys.stderr)
        if result.get("run_url"):
            print(f"  {result['run_url']}", file=sys.stderr)
        #  NO SECOND CODE PATH. `ex.attest` writes the row BEFORE it raises, so the failure
        #  is already in the log; reconciling here opens the incident through exactly the same
        #  function the next preflight would use. An earlier version created the incident inline
        #  and had to invent an attestation identity to do it, which is how a duplicate identity
        #  scheme gets born.
        reasons, _ = obligations.blocking(reconcile=False)
        for reason in reasons:
            print(f"  {reason}", file=sys.stderr)
        print("  The NEXT ordinary landing is refused until this is resolved.", file=sys.stderr)
        print("  The commit is pushed and cannot be unpushed. What is NOT established is that "
              "the site serves it.\n  Do not tell anyone a page is live.", file=sys.stderr)
        return 3
    print(f"  deployed {(result.get('deployed_sha') or '')[:12]} — the site serves this commit")
    if args.remediating:
        #  RECOVERED IS NOT RESOLVED. The deploy working again says publication is healthy now;
        #  it does not say the earlier violation was ever looked at. Closing automatically here
        #  would mean nobody has to — which is how six correct attestations were passed over.
        print(f"\n  {args.remediating} is now RECOVERED, and still OPEN. Ordinary landing stays "
              f"refused until it is resolved with evidence:")
        print(f"      python3 tools/deploy_obligations.py --resolve {args.remediating}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
