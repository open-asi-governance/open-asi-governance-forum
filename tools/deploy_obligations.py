#!/usr/bin/env python3
"""Every verified push owes a deployment. Reconcile the debt before mutating anything else.

    python3 tools/deploy_obligations.py --status        # what is owed, satisfied, or open
    python3 tools/deploy_obligations.py --reconcile     # observe the outstanding ones
    python3 tools/deploy_obligations.py --resolve <id>  # close incidents, with evidence
    python3 tools/deploy_obligations.py --check         # exit non-zero if anything blocks work

WHY THIS EXISTS — D-58, and it is the second half of it
--------------------------------------------------------
On 2026-08-11 the Pages deploy failed and eight consecutive commits went unpublished. `land.py`
**observed six of those failures** and attested every one honestly: six action-log entries reading
`verified: false`, `conclusion: "failure"`, and a `deployed_sha` still pointing at the last good
commit. The remaining two landings were interrupted mid-wait and wrote no attestation at all. So
the eight unpublished commits are six observed failures plus two unobserved waits — a distinction
worth keeping, because the two halves need different mechanisms and an earlier draft of this
docstring collapsed them.

Logging was never the failure. The failure was that there was **no transition from "an observed
violation" to "work is now constrained"**. Control 50 meters overrides and control 57 reports gate
health as a vector; neither stops the next landing. External review placed this under **control
23** — an observed invariant violation must open an incident and prevent further work in the
affected class — and declined the new control this workbench was inclined to write.

THE MODEL: AN OBLIGATION, NOT AN ALARM
---------------------------------------
An alarm can only fire when someone is there to hear it, and the two landings that mattered most
were killed before their deploy wait finished:

    a verified push
        └── deployment obligation: PENDING
                ├── observed success, and the served SHA is that commit  → SATISFIED
                ├── observed failure, or the served SHA is another commit → INCIDENT
                └── cannot observe (still running, no token, API down)    → still PENDING

The push entry is written to the action log **before** the risky wait, so an interruption cannot
hide anything: the obligation is already recorded and the next preflight reconciles it. Nothing
depends on a process that just died writing a record of dying.

TWO IDENTITIES, AND THE SECOND ONE WAS A DEFECT
------------------------------------------------
A pending obligation is about a **publication frontier**; an incident is about a **failure
event**. Conflating them broke the ledger twice during construction, both times found by review
rather than by reading:

* Pending obligations collapse to the newest verified descendant. If two pushes are interrupted
  in a row and the tip then deploys, the earlier commit's content is published — **but only if
  the later commit is a descendant of it**, which is now checked with `git merge-base` rather
  than presumed. A non-descendant tip discharges nothing.
* Incidents do **not** collapse, and are keyed on the ATTESTATION that observed the failure, not
  on the commit. Keying on the commit meant that once any incident named a commit — even a
  resolved one — a second failure of that same commit became invisible. Codex reproduced it:
  fail, resolve, fail again, land something else, and the ledger reported no blockers.

PENDING IS NOT A VIOLATION, AND IT STILL BLOCKS. "Unknown is not success" does not make unknown
an incident — but the publication postcondition is undischarged either way, and that is enough to
stop the next ordinary landing. An interrupted-but-successful wait clears itself at the next
preflight for the cost of two API reads, which is what keeps this sharp rather than something to
route around. This repository's one other floor is overridden 88% of the time, and that number
was the argument for few sharp interlocks over many soft ones.

WHAT CLOSES AN INCIDENT
------------------------
Only evidence. `--resolve` observes the commit given (HEAD by default), requires a successful
Pages run and requires the deployment to be serving that exact full SHA, and only then writes a
recovery artifact. There is no acknowledgement path and no force.

A successful remediation does not close anything by itself. That is deliberate: an automatic
close means nobody ever has to look, which is how six correct attestations were passed over.

Recovery artifacts live in `incidents/recoveries/` and **each one may resolve several incident
ids**, because one observed recovery genuinely is one fact. The six historical failures were
dispositioned by a single recovery: the commit that restored publication is a descendant
containing all of their content. That does **not** establish that those six exact commits were
ever served, and the artifact says so in those words.

Resolutions are separate artifacts and the incident file is never edited — corrections attach,
they do not edit. Both incidents and recoveries are SCHEMA-VALIDATED on every read, because a
resolution file containing `{"garbage": true}` closed an incident in the first version of this
tool, which made "only evidence closes an incident" false while the sentence was sitting in this
docstring.

WHAT THIS IS NOT
-----------------
**It does not constrain a determined operator.** The custodian can edit this file, the action
log, the workflow and the repository settings, and holds every credential involved. It prevents
inattentive repetition when the sanctioned path is used; it is not independent governance, and
calling it that would be the theatre this project exists to object to.

`--remediating` on `land.py` links a landing to the incident it claims to fix. **The link is
accountability, not proof**: nothing here can tell whether the diff actually remedies anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INCIDENTS = REPO_ROOT / "record" / "executive" / "incidents"
LOG = REPO_ROOT / "record" / "executive" / "action-log.jsonl"
REPO_SLUG = "open-asi-governance/open-asi-governance-forum"
WORKFLOW_FILE = "pages.yml"
TARGET_BRANCH = "main"

PENDING = "PENDING"
SATISFIED = "SATISFIED"
INCIDENT = "INCIDENT"

INCIDENT_SCHEMA = "oagrc-deploy-incident-0.2"
RECOVERY_SCHEMA = "oagrc-deploy-recovery-0.1"
FULL_SHA = re.compile(r"\A[0-9a-f]{40}\Z")


class StateUnknown(Exception):
    """The ledger cannot be interpreted. FAIL CLOSED.

    An unreadable or schema-invalid artifact, a duplicate id, an orphan resolution or a broken
    `follows` chain means the state is unknown — and unknown must never be rendered as "no open
    incidents", which is the same false zero this whole deficiency is about.
    """


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _api(path: str) -> dict | list | None:
    """GitHub API GET. None on ANY failure, and the caller must treat that as unobserved."""
    #  ONE CREDENTIAL NAME. This briefly also accepted GH_TOKEN_OAGF, which meant a test that
    #  removed GITHUB_TOKEN to check the no-token path did not actually remove the credential --
    #  so the waiter polled a nonexistent commit for nine minutes instead of returning at once.
    #  A second accepted name is a second way for "unauthenticated" to be quietly false.
    token = os.environ.get("GITHUB_TOKEN")
    request = urllib.request.Request(f"https://api.github.com/repos/{REPO_SLUG}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except Exception:                                                    # noqa: BLE001
        return None


def is_ancestor(older: str, newer: str) -> bool | None:
    """Is `older` an ancestor of `newer`? None when git cannot say.

    NOT PRESUMED. A pending obligation is discharged by a later successful deploy only if the
    later commit actually contains the earlier one. Two pushes to different lines of history
    discharge nothing, and assuming otherwise would drop an obligation silently.
    """
    if older == newer:
        return True
    proc = subprocess.run(["git", "merge-base", "--is-ancestor", older, newer],
                          cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    return None                       # unknown object, shallow clone, not a repository


#  ── observation ────────────────────────────────────────────────────────────────────────────

def observe(sha: str) -> dict:
    """What is the deployment state of this exact commit?

    FULL SHA EQUALITY THROUGHOUT. A short sha is for display only; prefix matching as the
    substantive check would let a different commit satisfy an obligation, and a one-character
    "sha" would match almost anything.

    THE RUN IS PINNED to the Pages workflow, a push event and the target branch. The waiter this
    replaced asked for "the latest run for this sha" and would have accepted a run from any
    workflow — including one added later that publishes nothing. `land.py` now calls this rather
    than keeping a second, subtly different verifier.
    """
    #  `retriable` separates a PENDING that waiting can resolve (the run has not finished) from
    #  one it cannot (there is no token). Without the distinction `land.py` polled for nine
    #  minutes on a missing credential -- caught by a test that simply stopped returning.
    if not FULL_SHA.match(sha or ""):
        return {"state": PENDING, "commit": sha, "retriable": False,
                "why": "not a full 40-character sha, so nothing can be compared against it"}
    if not os.environ.get("GITHUB_TOKEN"):
        return {"state": PENDING, "retriable": False, "commit": sha,
                "why": "no token in the environment, so nothing can be observed"}
    runs = _api(f"/actions/workflows/{WORKFLOW_FILE}/runs"
                f"?head_sha={sha}&event=push&branch={TARGET_BRANCH}&per_page=5")
    if runs is None:
        return {"state": PENDING, "retriable": True, "commit": sha,
                "why": "the workflow API could not be read"}
    items = [r for r in (runs.get("workflow_runs") or []) if r.get("head_sha") == sha]
    if not items:
        return {"state": PENDING, "retriable": True, "commit": sha,
                "why": "no qualifying Pages run for this commit yet"}
    run = items[0]
    if run.get("status") != "completed":
        return {"state": PENDING, "retriable": True, "commit": sha,
                "why": f"the run is {run.get('status')}", "run_url": run.get("html_url")}
    if run.get("conclusion") != "success":
        return {"state": INCIDENT, "commit": sha, "conclusion": run.get("conclusion"),
                "run_url": run.get("html_url"),
                "why": f"the Pages workflow concluded {run.get('conclusion')}"}

    #  A workflow concluding is not the site serving it.
    deployments = _api("/deployments?environment=github-pages&per_page=1")
    served = (deployments[0].get("sha") if isinstance(deployments, list) and deployments
              else None)
    if served is None:
        return {"state": PENDING, "retriable": True, "commit": sha,
                "run_url": run.get("html_url"),
                "why": "the run succeeded but the deployment API could not be read, so what is "
                       "actually served is unknown"}
    if served != sha:
        return {"state": INCIDENT, "commit": sha, "served_sha": served,
                "run_url": run.get("html_url"),
                "why": f"the run succeeded but the site serves {served[:12]}, not this commit"}
    return {"state": SATISFIED, "commit": sha, "served_sha": served,
            "run_url": run.get("html_url"), "conclusion": "success"}


#  ── the action log ─────────────────────────────────────────────────────────────────────────

def log_rows() -> list[dict]:
    if not LOG.is_file():
        return []
    rows = []
    for number, line in enumerate(LOG.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                #  StateUnknown, not a traceback: an unreadable log is unknown state, and a
                #  traceback here would exit 1, which is the code that means "blocked" and would
                #  be indistinguishable from a real finding.
                raise StateUnknown(f"the action log is unreadable at line {number}: {exc}") from exc
    return rows


def attestation_id(row: dict) -> str:
    """A stable identity for one attestation, so an incident names an EVENT and not a commit.

    The log has no ids of its own. This digests the fields that make an attestation what it is.
    `prev_sha256` is deliberately not used: it changes if the chain is ever rebuilt, and the
    identity of a failure event should not.
    """
    claim = row.get("claim") if isinstance(row.get("claim"), dict) else {}
    material = json.dumps({"utc": row.get("utc"), "action": row.get("action"),
                           "commit": claim.get("commit"),
                           "conclusion": claim.get("conclusion"),
                           "deployed_sha": claim.get("deployed_sha")},
                          sort_keys=True)
    return hashlib.sha256(material.encode()).hexdigest()[:16]


#  ── the incident store ─────────────────────────────────────────────────────────────────────

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StateUnknown(message)


def load_incidents() -> dict[str, dict]:
    """Read and VALIDATE every incident and recovery. Anything malformed is StateUnknown.

    The first version attached any truthy JSON found in a resolution file, so `{"garbage": true}`
    closed an incident while this module's docstring claimed only evidence could. Codex
    reproduced it. Validation is not decoration here; it is the difference between the sentence
    being true and being a wish.
    """
    if not INCIDENTS.is_dir():
        return {}
    incidents: dict[str, dict] = {}
    for path in sorted(INCIDENTS.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise StateUnknown(f"{path.name} is not readable JSON: {exc}") from exc
        _require(isinstance(doc, dict), f"{path.name} is not an object")
        _require(doc.get("schema_version") == INCIDENT_SCHEMA,
                 f"{path.name} declares schema {doc.get('schema_version')!r}, "
                 f"not {INCIDENT_SCHEMA!r}")
        _require(doc.get("id") == path.stem,
                 f"{path.name} calls itself {doc.get('id')!r}; the filename and the id must agree")
        _require(bool(FULL_SHA.match(str(doc.get("commit", "")))),
                 f"{path.name}: commit is not a full 40-character sha")
        _require(isinstance(doc.get("source_attestation"), str) and doc["source_attestation"],
                 f"{path.name}: no source_attestation, so it names no observed event")
        _require(path.stem not in incidents, f"duplicate incident id {path.stem}")
        doc["_id"] = path.stem
        doc["_resolution"] = None
        incidents[path.stem] = doc

    resolved_by: dict[str, dict] = {}
    recoveries = INCIDENTS / "recoveries"
    if recoveries.is_dir():
        for path in sorted(recoveries.glob("*.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise StateUnknown(f"recoveries/{path.name} is not readable JSON: {exc}") from exc
            _require(isinstance(doc, dict), f"recoveries/{path.name} is not an object")
            _require(doc.get("schema_version") == RECOVERY_SCHEMA,
                     f"recoveries/{path.name} declares schema {doc.get('schema_version')!r}, "
                     f"not {RECOVERY_SCHEMA!r}")
            ids = doc.get("resolves")
            _require(isinstance(ids, list) and ids and all(isinstance(i, str) for i in ids),
                     f"recoveries/{path.name}: resolves must be a non-empty list of incident ids")
            _require(doc.get("id") == path.stem,
                     f"recoveries/{path.name} calls itself {doc.get('id')!r}; the filename and "
                     f"the id must agree, or one artifact can silently replace another")
            _require(bool(FULL_SHA.match(str(doc.get("resolving_commit", "")))),
                     f"recoveries/{path.name}: resolving_commit is not a full 40-character sha")
            evidence = doc.get("evidence")
            _require(isinstance(evidence, dict) and evidence.get("state") == SATISFIED,
                     f"recoveries/{path.name}: evidence does not record a SATISFIED observation, "
                     f"so it is an assertion rather than a closure")
            _require(evidence.get("commit") == doc["resolving_commit"],
                     f"recoveries/{path.name}: the evidence is about a different commit than the "
                     f"one it claims resolved these incidents")
            _require(evidence.get("served_sha") == doc["resolving_commit"],
                     f"recoveries/{path.name}: the evidence does not show that commit SERVED")
            for ident in ids:
                _require(ident in incidents,
                         f"recoveries/{path.name} resolves {ident}, which does not exist")
                #  NOT an f-string inside _require for this one. The message would index
                #  resolved_by[ident], and Python evaluates the argument BEFORE the call -- so
                #  the PASSING case raised KeyError. Found by the suite, in validation code
                #  written to make failures legible.
                if ident in resolved_by:
                    raise StateUnknown(
                        f"{ident} is resolved twice, by recoveries/{path.name} and by "
                        f"{resolved_by[ident].get('_file')}")
                doc["_file"] = path.name
                resolved_by[ident] = doc
    for ident, doc in resolved_by.items():
        incidents[ident]["_resolution"] = doc

    for ident, doc in incidents.items():
        follows = doc.get("follows")
        _require(follows is None or follows in incidents,
                 f"{ident} follows {follows}, which does not exist")
    for ident in incidents:
        seen, cursor = set(), ident
        while cursor:
            _require(cursor not in seen, f"cycle in the follows chain at {cursor}")
            seen.add(cursor)
            cursor = incidents[cursor].get("follows")
    return incidents


def open_incidents(incidents: dict[str, dict]) -> list[dict]:
    return [doc for doc in incidents.values() if not doc.get("_resolution")]


def chain_length(incidents: dict[str, dict], ident: str) -> int:
    n, cursor = 0, ident
    while cursor:
        n += 1
        cursor = incidents[cursor].get("follows")
    return n


def open_or_find(sha: str, source_attestation: str, observation: dict,
                 note: str = "") -> tuple[str, bool]:
    """Returns (id, created). Idempotent on the ATTESTATION, not on the commit.

    `follows` points at the most recent incident for the same commit whether it is open or
    resolved, so a recurrence after a resolution still reads as a recurrence. Chaining only to
    open incidents understated repetition, which is the statistic most worth not understating.
    """
    INCIDENTS.mkdir(parents=True, exist_ok=True)
    existing = load_incidents()
    for ident, doc in existing.items():
        if doc.get("source_attestation") == source_attestation:
            return ident, False
    prior = [ident for ident, doc in existing.items() if doc["commit"] == sha]
    follows = sorted(prior, key=lambda i: existing[i].get("opened_utc", ""))[-1] if prior else None
    utc = _utc()
    ident = f"{utc[:10]}-deploy-{sha[:12]}"
    suffix = 1
    while (INCIDENTS / f"{ident}.json").exists():
        suffix += 1
        ident = f"{utc[:10]}-deploy-{sha[:12]}-{suffix}"
    (INCIDENTS / f"{ident}.json").write_text(json.dumps({
        "schema_version": INCIDENT_SCHEMA,
        "artifact_type": "deploy_incident",
        "id": ident,
        "opened_utc": utc,
        "commit": sha,
        "source_attestation": source_attestation,
        "observation": observation,
        "follows": follows,
        "note": note or "The publication postcondition for this commit is false. Ordinary "
                        "landing is refused until this is resolved with evidence.",
        "what_this_does_not_establish":
            "That the cause is known, that the site is broken for readers, or that any later "
            "commit is affected. It records one observed violation of one postcondition.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ident, True


def resolve(idents: list[str], head: str) -> tuple[int, str]:
    """Close one or more incidents with ONE observation. Evidence only.

    Several ids per artifact because one observed recovery is one fact. Writing the same evidence
    into six files would have made six artifacts out of it and read as six independent closures.
    """
    incidents = load_incidents()
    missing = [i for i in idents if i not in incidents]
    if missing:
        return 1, f"no such incident: {', '.join(missing)}"
    already = [i for i in idents if incidents[i].get("_resolution")]
    todo = [i for i in idents if i not in already]
    if not todo:
        return 0, f"already resolved: {', '.join(already)}"
    observation = observe(head)
    if observation["state"] != SATISFIED:
        return 1, (f"REFUSED. Resolving requires {head[:12]} to be successfully deployed and "
                   f"served. It is {observation['state']}: {observation.get('why', '')}\n"
                   f"  An incident is closed by evidence that publication works now, never by "
                   f"asserting it.")
    #  Is the resolving commit actually downstream of what failed? Recorded per incident rather
    #  than assumed, because "a later commit deployed" only publishes an earlier commit's content
    #  when it contains it.
    contains = {i: is_ancestor(incidents[i]["commit"], head) for i in todo}
    recoveries = INCIDENTS / "recoveries"
    recoveries.mkdir(parents=True, exist_ok=True)
    utc = _utc()
    #  UNIQUE PER RECOVERY EVENT, not per (day, head). Two resolutions on the same day against
    #  the same head wrote the same filename, the second OVERWROTE the first, and the incidents
    #  the first had closed silently REOPENED — a correction editing a correction, in the tool
    #  whose rule is that corrections attach. Codex reproduced it. The digest covers the exact
    #  set resolved and the timestamp, and the file is created exclusively so a collision raises
    #  rather than clobbers.
    recovery_id = (f"{utc[:10]}-recovery-{head[:12]}-"
                   f"{hashlib.sha256((utc + ',' .join(sorted(todo))).encode()).hexdigest()[:8]}")
    path = recoveries / f"{recovery_id}.json"
    if path.exists():
        return 1, f"REFUSED: a recovery artifact already exists at {path.name}"
    with open(path, "x", encoding="utf-8") as handle:
        handle.write(json.dumps({
        "schema_version": RECOVERY_SCHEMA,
        "artifact_type": "deploy_incident_recovery",
        "id": recovery_id,
        "resolves": todo,
        "resolved_utc": utc,
        "resolving_commit": head,
        "evidence": observation,
        "contains_incident_commit": contains,
        "basis": "The Pages workflow for this commit concluded success and the github-pages "
                 "deployment serves this exact commit. Both were observed, not assumed.",
        "what_this_does_not_establish":
            "That the commits these incidents name were ever themselves served. Where "
            "contains_incident_commit is true, this commit publishes their CONTENT as a "
            "descendant; where it is false or null, not even that. One observed recovery "
            "dispositions these failure events; it does not retroactively deploy them.",
        }, indent=2, ensure_ascii=False) + "\n")
    load_incidents()                                   # validate what was just written
    return 0, (f"resolved {len(todo)} incident(s) against {head[:12]}, which is deployed and "
               f"served: {', '.join(todo)}")


#  ── obligations derived from the action log ────────────────────────────────────────────────

def outstanding_pushes(rows: list[dict]) -> list[str]:
    """Pushed commits with no evidence that their content reached the site — the FRONTIER.

    ORDER IS PART OF THE FACT. This walked the log twice — every push into one set, every
    successful deploy into another — and asked whether any served commit was a descendant. That
    is wrong, not merely loose: a deployment that happened BEFORE a push cannot discharge it.
    Codex reproduced the sequence that breaks it:

        push A ; deploy B successfully (B descends from A) ; push A again

    The re-push of A owes a deployment, and the unordered version reported nothing outstanding,
    because a deploy of B was somewhere in the set and B contains A. So the walk is now single-
    pass and in log order, and a deploy only discharges obligations opened before it.

    Pending obligations then collapse to the FRONTIER: among what is still outstanding, a commit
    contained by another outstanding commit is not separately actionable. That reduction is only
    sound after causal discharge, which is why it comes last.

    A VERIFIED push only. An attestation with verified:false means the push did not carry the
    commit, so nothing is owed — and the real log holds exactly one, a 2026-08-09 probe of the
    push profile using an all-zero sha. Counting it created a permanent obligation on a commit
    that does not exist.

    Observed FAILURES are not handled here and do not collapse; `unreconciled_failures` keys them
    on the attestation that saw them.
    """
    open_obligations: list[str] = []
    for row in rows:
        claim = row.get("claim")
        if not isinstance(claim, dict) or not claim.get("commit"):
            continue
        verified = str(row.get("verified")).lower() == "true"
        if row.get("action") == "push" and verified:
            #  A re-push of a commit already outstanding is the same obligation, not a second.
            if claim["commit"] not in open_obligations:
                open_obligations.append(claim["commit"])
        elif (row.get("action") == "deploy" and verified
              and claim.get("deployed_sha") == claim["commit"]):
            served = claim["commit"]
            #  Only obligations opened BEFORE this deploy, and only those it actually contains.
            #  `None` from git — unknown object, shallow clone — is not a discharge.
            open_obligations = [sha for sha in open_obligations
                                if not (sha == served or is_ancestor(sha, served) is True)]
    return [sha for sha in open_obligations
            if not any(other != sha and is_ancestor(sha, other) is True
                       for other in open_obligations)]


def unreconciled_failures(rows: list[dict], incidents: dict[str, dict]) -> list[dict]:
    """OBSERVED deploy failures that no incident accounts for, keyed on the ATTESTATION.

    Codex required this backstop: `land.py` can die between writing the failed attestation and
    creating the incident, leaving the evidence in the log with nothing enforcing it — the same
    shape as the original defect, one layer down.

    It scans EVERY deploy row rather than only the most recent push, because the historical
    sequence was failure, land again, failure. A reconciler reading only the last push would have
    walked past all six.

    KEYED ON THE ATTESTATION, NOT THE COMMIT. Commit-keying meant a commit that failed, was
    resolved, and failed again was treated as accounted for, and the ledger reported no blockers.
    """
    accounted = {doc.get("source_attestation") for doc in incidents.values()}
    out = []
    for row in rows:
        claim = row.get("claim")
        if (row.get("action") == "deploy" and isinstance(claim, dict)
                and claim.get("observed") is True
                and str(row.get("verified")).lower() != "true"
                and claim.get("commit")):
            ident = attestation_id(row)
            if ident not in accounted:
                out.append({"attestation": ident, **claim})
                accounted.add(ident)
    return out


def _ex():
    """executive_log, imported lazily and by path — the same lesson as D-64: a bare module import
    resolves only if the CALLER happens to have tools/ on sys.path, and this module is loaded by
    path from several places."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_executive_log_for_obligations", pathlib.Path(__file__).resolve().parent
        / "executive_log.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def blocking(reconcile: bool = False) -> tuple[list[str], dict]:
    """Everything that must stop an ordinary landing. An empty list means nothing does."""
    reasons: list[str] = []
    detail: dict = {}
    try:
        incidents = load_incidents()
        rows = log_rows()
    except StateUnknown as exc:
        return [f"the ledger cannot be interpreted: {exc}. State is UNKNOWN, which is not the "
                f"same as clear, so work stops until a human looks."], {}
    still_open = open_incidents(incidents)
    for doc in still_open:
        n = chain_length(incidents, doc["_id"])
        reasons.append(f"open incident {doc['_id']} on {doc['commit'][:12]}"
                       + (f" (chain of {n})" if n > 1 else ""))
    detail["open"] = [d["_id"] for d in still_open]

    #  BACKSTOP FIRST. An observed failure sitting in the log with no incident is the crash
    #  window between attesting and enforcing, and it must be closed before anything else is
    #  judged — otherwise a later successful push makes the earlier failure invisible, which is
    #  the exact sequence that produced eight unpublished commits.
    for claim in unreconciled_failures(rows, incidents):
        ident, created = open_or_find(
            claim["commit"], claim["attestation"],
            {"state": INCIDENT, "commit": claim["commit"],
             "conclusion": claim.get("conclusion"), "served_sha": claim.get("deployed_sha"),
             "why": "reconstructed from an action-log attestation that no incident accounted for"},
            note="Reconstructed at preflight. The failure was attested when it happened and the "
                 "process did not live to enforce it; this is the backstop for that window.")
        if created:
            reasons.append(f"reconstructed incident {ident} from an unenforced failed "
                           f"attestation on {claim['commit'][:12]}")
            detail.setdefault("reconstructed", []).append(ident)
    if detail.get("reconstructed"):
        incidents = load_incidents()
        still_open = open_incidents(incidents)
        detail["open"] = [d["_id"] for d in still_open]

    #  One commit, one line. The backstop and the push reconciler can both reach the same commit,
    #  and reporting it twice with two verbs makes a single failure look like two.
    already_reported = {doc["commit"] for doc in still_open}

    outstanding = outstanding_pushes(rows)
    detail["outstanding_pushes"] = outstanding
    for sha in outstanding:
        if sha in already_reported:
            continue
        if not reconcile:
            reasons.append(f"push {sha[:12]} has no record that it was served; run --reconcile")
            continue
        observation = observe(sha)
        detail.setdefault("observations", {})[sha] = observation
        if observation["state"] == SATISFIED:
            #  ATTEST IT, rather than merely returning no reason. `continue` cleared the blocker
            #  for THIS call and wrote nothing, so the push stayed outstanding forever: every
            #  later `--status` reported BLOCKING on a commit that had demonstrably been served,
            #  every landing re-queried the API for it, and — the part that matters for a record
            #  whose thesis is that evidence lives in the record — the discharge existed only in
            #  GitHub's live API and never here. Found when a harness timeout cut a landing off
            #  mid-wait and the obligation would not clear afterwards. See D-70.
            #
            #  The claim shape is the one land.py files, so the two paths write the same fact and
            #  `outstanding_pushes` cannot tell them apart. The note says which observed it.
            try:
                #  The profile's OWN fields, not a reshuffle of the observation. `observed:
                #  True` is the one it checks first — "an unobserved deploy is not a successful
                #  one" — and the first version of this call omitted it, so the attestation
                #  refused and the obligation correctly stood. That refusal is the profile
                #  working, and it is why the write is inside a try rather than assumed.
                _ex().attest("deploy",
                             {"observed": True,
                              "conclusion": observation.get("conclusion"),
                              "commit": sha,
                              "deployed_sha": observation.get("served_sha"),
                              "run_url": observation.get("run_url")},
                             note="deploy observed at reconcile, after a landing did not live "
                                  "to record it")
                detail.setdefault("attested", []).append(sha)
            except Exception as exc:                                    # noqa: BLE001
                #  An attestation that will not write is not a discharge. Say so and keep the
                #  obligation, rather than clearing a blocker on the strength of a failed write.
                reasons.append(f"push {sha[:12]} WAS served, and the discharge could not be "
                               f"recorded ({exc}). The obligation stands until the record "
                               f"carries the evidence.")
            continue
        if observation["state"] == INCIDENT:
            #  KEYED ON THE RUN. `{sha}:{conclusion}` was stable across different observations
            #  of the same commit, so once such an incident was resolved while its push stayed
            #  outstanding, every later observation kept finding the resolved incident instead of
            #  recording a new one. The run url is stable within a run and different across runs,
            #  which is exactly the identity an observation has.
            ident, created = open_or_find(
                sha,
                f"observed-at-reconcile:{sha}:"
                f"{observation.get('run_url') or observation.get('conclusion')}",
                observation)
            reasons.append(f"{'opened' if created else 'open'} incident {ident}: "
                           f"{observation.get('why')}")
        else:
            reasons.append(f"push {sha[:12]} is {observation['state']}: "
                           f"{observation.get('why')}. Undischarged, so ordinary landing waits.")
    return reasons, detail


#  ── bootstrap ──────────────────────────────────────────────────────────────────────────────

def bootstrap(head: str) -> tuple[int, str]:
    """Materialise the historical failures rather than starting from installation time.

    Codex's requirement, and it is right: a mechanism that silently begins at its own
    installation reproduces the omission it was built for. The failures are in the action log;
    they become incidents, and ONE recovery artifact closes them, because one observed recovery
    is one fact rather than six.

    IDEMPOTENT. `open_or_find` keys on the attestation, so re-running creates nothing new — the
    first version keyed on the commit and skipped resolved ones, so a second run manufactured six
    fresh suffixed incidents.
    """
    rows = log_rows()
    incidents = load_incidents()
    pending = unreconciled_failures(rows, incidents)
    if not pending:
        return 0, "nothing to bootstrap; every observed failure already has an incident"
    observation = observe(head)
    if observation["state"] != SATISFIED:
        return 1, (f"REFUSED. Bootstrapping closes the historical chain against the current "
                   f"head, and {head[:12]} is {observation['state']}. Fix publication first.")
    created = []
    for claim in pending:
        ident, was_new = open_or_find(
            claim["commit"], claim["attestation"],
            {"state": INCIDENT, "commit": claim["commit"],
             "conclusion": claim.get("conclusion"), "served_sha": claim.get("deployed_sha"),
             "why": "reconstructed from the action-log attestation written at the time"},
            note=("Reconstructed from the attestation land.py wrote when it happened. This "
                  "incident was observed and recorded correctly at the time and no mechanism "
                  "read it — which is D-58, and the reason this ledger exists. It is "
                  "materialised rather than skipped so the ledger does not begin by omitting "
                  "the failures that caused it."))
        if was_new:
            created.append(ident)
    if not created:
        return 0, "nothing to bootstrap; every observed failure already has an incident"
    code, message = resolve(created, head)
    if code != 0:
        return code, message
    return 0, (f"materialised {len(created)} historical incident(s) and closed them with one "
               f"recovery against {head[:12]}: {', '.join(created)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--status", action="store_true", help="show the ledger")
    parser.add_argument("--reconcile", action="store_true",
                        help="observe outstanding pushes and open incidents for failures")
    parser.add_argument("--resolve", metavar="ID", nargs="+",
                        help="close incident(s) with one observed recovery")
    parser.add_argument("--bootstrap", action="store_true",
                        help="materialise the historical failures rather than starting from now")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if anything blocks an ordinary landing")
    parser.add_argument("--head", default=None,
                        help="commit to resolve against. Defaults to HEAD; naming another is "
                             "allowed and is still checked for a successful, served deploy.")
    args = parser.parse_args()

    head = args.head or subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                                       capture_output=True, text=True).stdout.strip()

    if args.resolve:
        code, message = resolve(list(args.resolve), head)
        print(f"  {message}", file=sys.stderr if code else sys.stdout)
        return code
    if args.bootstrap:
        code, message = bootstrap(head)
        print(f"  {message}", file=sys.stderr if code else sys.stdout)
        return code

    reasons, detail = blocking(reconcile=args.reconcile)
    if args.check or args.reconcile or args.status:
        if reasons:
            for reason in reasons:
                print(f"  BLOCKING  {reason}", file=sys.stderr)
            print("\n  An ordinary landing is refused. A remediation is not:", file=sys.stderr)
            print("      python3 tools/land.py -F msg.txt --remediating <incident-id>",
                  file=sys.stderr)
            print("  The link records what a landing claims to fix. It does not establish that "
                  "it does.", file=sys.stderr)
            return 1
        print("  nothing blocks an ordinary landing.")
        try:
            incidents = load_incidents()
        except StateUnknown as exc:
            print(f"  {exc}", file=sys.stderr)
            return 1
        resolved = [d for d in incidents.values() if d.get("_resolution")]
        print(f"  {len(incidents)} incident(s) on record, {len(resolved)} resolved, "
              f"{len(incidents) - len(resolved)} open.")
        if detail.get("outstanding_pushes"):
            print(f"  outstanding push(es) reconciled this run: "
                  f"{[s[:12] for s in detail['outstanding_pushes']]}")
        print("\n  This constrains the sanctioned landing path only. It does not constrain an")
        print("  operator who edits it, the action log, or the workflow — there is one custodian")
        print("  and they hold every credential. It prevents inattention, not intent.")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
