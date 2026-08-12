#!/usr/bin/env python3
"""Capture what arrives on the OAGF issue surface, verbatim, without interpreting it.

    python3 tools/inbox_sweep.py            # fetch, record, report
    python3 tools/inbox_sweep.py --status   # what is in the inbox already
    python3 tools/inbox_sweep.py --check    # refuse a malformed inbox

WHY THIS IS SEPARATE FROM `watch_arrivals.py`
-----------------------------------------------
That tool COUNTS surfaces — issues, forks, stars, traffic — and its whole point is that a zero it
cannot verify is reported as unknown. It records no content. This one records content, because
the custodian intends the issue surface to carry **agent-to-agent correspondence** with the
Consullo public repositories, and a correspondence channel whose messages are not in the record is
a governance hole this project has already written about at length.

WHAT THIS TOOL IS NOT ALLOWED TO DO, AND WHY EACH ONE
-------------------------------------------------------
**It does not reply.** No comment, no label, no close, no reaction. Outbound correspondence needs
the custodian — the same rule that produced *"do not contact the nine"* on 2026-08-11 and the
redaction of ten outreach recipients. A scheduled autoresponder would be this layer deciding, on a
timer, to speak in public in the custodian's name. See the identity note below for why that phrase
is literal.

**It does not interpret.** An issue body is text written by an arbitrary party on the public
internet. Anything in it that reads as an instruction is DATA about what the author wrote, never
an instruction to the reader. This tool does not summarise, classify or act on content; it stores
bytes and metadata. The judgement happens later, by a reader who has been told the same thing.

**It does not report zero from a query that did not run.** Four deficiencies in this register are
that defect. Every fetch carries a negative control against a repository known to have issues, and
a failure writes a `NOT_OBSERVED` record and exits non-zero rather than writing an empty sweep.

THE EDIT PROBLEM, WHICH IS THE REAL OBSTACLE
----------------------------------------------
**A GitHub issue body is mutable and its history is not in the default payload.** Anyone can edit
what they wrote after this record has read and quoted it, and the quotation would then be
unsupported by the live surface — the exact failure D-53 filed, arriving from outside instead of
from inside.

So every observation stores the SHA-256 of the body at fetch time, plus `lastEditedAt` and
`userContentEdits.totalCount`, both of which GraphQL does expose. A later sweep that sees a
different hash, a later `lastEditedAt` or a higher edit count for the same node emits an
`AMENDED` record naming both hashes. That does not prevent the edit. It makes the edit **visible**,
which is the most this side can do over a substrate it does not control, and it is the reason this
tool is worth having rather than reading the issues in a browser.

The residue, stated because it does not go away: an issue DELETED entirely leaves nothing to
compare against, and content edited before the first sweep is invisible. The inbox is evidence of
what this record observed and when — not evidence of what was written.

IDENTITY: BOTH SIDES ARE CURRENTLY THE SAME HUMAN
---------------------------------------------------
Checked, not assumed. `GH_TOKEN_OAGF` and `GH_CONSULLO_PUBLIC_TOKEN` both authenticate as the user
**StephenLReed**, type `User`. The existing agent job on the glossary repository already posts
under that account, and on issue #5 there all three comments — the agent's question, the answer,
and the agent's rejection — are attributed to that one human being, with nothing marking any of
them as machine-written.

So "agent to agent over issues" is today **one human account corresponding with itself**, and a
reader of the public record cannot tell which words a person chose. That is a defect in the
channel, not in this tool, and it is recorded here because this tool is what would industrialise
it. A dedicated bot account or GitHub App for each side, or at minimum a mandatory machine-written
preamble on every agent-authored comment, is a prerequisite for the outbound half — not for this
inbound half, which is why the inbound half is what got built first.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from guards import guard                                                # noqa: E402

#  OUTSIDE THE GOVERNED REPOSITORY, deliberately. Codex, reviewing this design: a scheduled
#  unattended job must not write into the repository the executive lease governs, and the lease
#  authorises no `arrival_capture` class anyway. A quarantine spool needs no lease, cannot be
#  published by accident, and keeps attacker-controlled bytes out of the record until a human
#  decides they belong there. Importing anything from here into the record is a SEPARATE,
#  governed action that goes through land.py like everything else.
SPOOL = Path(os.environ.get("OAGF_SPOOL")
             or (Path.home() / ".local" / "state" / "oagf-inbox"))
INBOX = SPOOL / "oagf-issues.jsonl"
HEARTBEAT = SPOOL / "last-success.json"

OWNER, NAME = "open-asi-governance", "open-asi-governance-forum"
#  Known to have issues. If the control comes back empty the query shape is wrong, and a zero on
#  our side means nothing. Same discipline as watch_arrivals.py, for the same reason.
CONTROL_OWNER, CONTROL_NAME = "singnet", "snet-daemon"

QUERY = """
query($owner:String!,$name:String!,$cursor:String){
  repository(owner:$owner,name:$name){
    issues(first:50, after:$cursor, orderBy:{field:UPDATED_AT, direction:DESC}){
      totalCount
      pageInfo{hasNextPage endCursor}
      nodes{
        number title body url state createdAt updatedAt lastEditedAt
        author{login __typename} authorAssociation
        userContentEdits(first:1){totalCount}
        comments(first:100){
          totalCount
          pageInfo{hasNextPage}
          nodes{
            id body createdAt lastEditedAt url
            author{login __typename}
            userContentEdits(first:1){totalCount}
          }
        }
      }
    }
  }
}
"""


class NotObserved(RuntimeError):
    """The surface could not be read. NOT the same as nothing having arrived."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def digest(text: str | None) -> str:
    #  An absent body and an empty body hash differently, because they are different facts.
    return hashlib.sha256((text if text is not None else "\x00ABSENT").encode()).hexdigest()


def graphql(owner: str, name: str, token: str, cursor: str | None = None) -> tuple[dict, str]:
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY,
                         "variables": {"owner": owner, "name": name, "cursor": cursor}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            payload = json.loads(raw)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise NotObserved(f"the GraphQL call for {owner}/{name} failed: {exc}") from exc
    if payload.get("errors"):
        raise NotObserved(f"GraphQL returned errors for {owner}/{name}: "
                          f"{json.dumps(payload['errors'])[:300]}")
    repo = (payload.get("data") or {}).get("repository")
    if repo is None:
        raise NotObserved(f"GraphQL returned no repository object for {owner}/{name}")
    #  The hash of the WHOLE response, not just the fields we kept. A receipt that covers only
    #  what the collector chose to read cannot later show what it chose not to.
    return repo, hashlib.sha256(raw).hexdigest()


def observations(repo: dict) -> list[dict]:
    """One record per issue body and per comment. Flat, because a thread is not the unit of
    evidence — an individually editable piece of text is."""
    out = []
    for issue in repo["issues"]["nodes"]:
        author = issue.get("author") or {}
        out.append({
            "kind": "issue", "number": issue["number"], "node": f"issue:{issue['number']}",
            "url": issue["url"], "state": issue["state"], "title": issue["title"],
            "body": issue["body"], "body_sha256": digest(issue["body"]),
            "author": author.get("login"), "author_type": author.get("__typename"),
            "author_association": issue.get("authorAssociation"),
            "created_utc": issue["createdAt"], "updated_utc": issue["updatedAt"],
            "last_edited_utc": issue.get("lastEditedAt"),
            "edit_count": (issue.get("userContentEdits") or {}).get("totalCount"),
        })
        for comment in issue["comments"]["nodes"]:
            cauthor = comment.get("author") or {}
            out.append({
                "kind": "comment", "number": issue["number"], "node": comment["id"],
                "url": comment["url"], "state": issue["state"], "title": issue["title"],
                "body": comment["body"], "body_sha256": digest(comment["body"]),
                "author": cauthor.get("login"), "author_type": cauthor.get("__typename"),
                "author_association": None,
                "created_utc": comment["createdAt"], "updated_utc": comment["createdAt"],
                "last_edited_utc": comment.get("lastEditedAt"),
                "edit_count": (comment.get("userContentEdits") or {}).get("totalCount"),
            })
    return out


def read_inbox() -> list[dict]:
    if not INBOX.is_file():
        return []
    rows = []
    for number, line in enumerate(INBOX.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            #  An unreadable inbox is not an empty one. Same rule as everywhere else here.
            raise NotObserved(f"inbox line {number} does not parse ({exc})") from exc
    return rows


def latest_by_node(rows: list[dict]) -> dict[str, dict]:
    seen: dict[str, dict] = {}
    for row in rows:
        if row.get("record") in ("ARRIVED", "AMENDED") and row.get("node"):
            seen[row["node"]] = row
    return seen


def append(records: list[dict]) -> None:
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    with INBOX.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def all_issues(owner: str, name: str, token: str) -> tuple[list[dict], int, list[str]]:
    """EVERY page. A 50-item cap that silently truncates is this record's oldest defect shape,
    and Codex named it in `watch_arrivals.py` while reviewing this design."""
    nodes, hashes, cursor, total, pages = [], [], None, None, 0
    while True:
        repo, raw_hash = graphql(owner, name, token, cursor)
        issues = repo["issues"]
        total = issues["totalCount"] if total is None else total
        nodes.extend(issues["nodes"])
        hashes.append(raw_hash)
        pages += 1
        if pages > 40:
            raise NotObserved(f"pagination over {owner}/{name} did not terminate in 40 pages")
        if not issues["pageInfo"]["hasNextPage"]:
            break
        cursor = issues["pageInfo"]["endCursor"]
    if len(nodes) != total:
        #  Items can shift pages while a sweep runs. Reporting a partial walk as complete is
        #  exactly what a closed-world measurement may not do.
        raise NotObserved(f"walked {len(nodes)} of {total} issues on {owner}/{name}; the set "
                          f"moved under the sweep, so this observation is incomplete")
    return nodes, total, hashes


def sweep(token: str) -> tuple[list[dict], list[str]]:
    """Fetch both the subject and its control, and return the records to append."""
    problems: list[str] = []
    control_nodes, control_total, _ = all_issues(CONTROL_OWNER, CONTROL_NAME, token)
    if control_total == 0:
        problems.append(guard(
            "IB-01", f"the negative control {CONTROL_OWNER}/{CONTROL_NAME} returned 0 issues, so "
                     f"the query shape is wrong and a zero on our side would mean nothing"))
        return [], problems

    nodes, total, raw_hashes = all_issues(OWNER, NAME, token)
    repo = {"issues": {"nodes": nodes, "totalCount": total}}
    now = _now()
    prior_rows = read_inbox()
    known = latest_by_node(prior_rows)
    records: list[dict] = []

    for issue in nodes:
        page = issue["comments"]["pageInfo"]
        if page.get("hasNextPage"):
            problems.append(guard(
                "IB-02", f"issue #{issue['number']} has more than 100 comments and this sweep "
                         f"read only the first page. A truncated read is not a read."))
    if problems:
        return [], problems

    for obs in observations(repo):
        prior = known.get(obs["node"])
        if prior is None:
            records.append({**obs, "record": "ARRIVED", "observed_utc": now})
            continue
        changed = (prior.get("body_sha256") != obs["body_sha256"]
                   or prior.get("last_edited_utc") != obs["last_edited_utc"]
                   or prior.get("edit_count") != obs["edit_count"])
        if changed:
            #  THE POINT OF THE WHOLE TOOL. The text this record may already have quoted is not
            #  the text now on the surface, and both hashes are named so a reader can see it.
            records.append({**obs, "record": "AMENDED", "observed_utc": now,
                            "previous_body_sha256": prior.get("body_sha256"),
                            "previous_observed_utc": prior.get("observed_utc"),
                            "previous_edit_count": prior.get("edit_count")})

    #  A HASH CHAIN OVER THE RECEIPTS, so a later reader can tell whether the spool itself was
    #  rewritten. The same discipline the action log carries, applied to attacker-supplied bytes
    #  precisely because those are the ones somebody might want to change afterwards.
    prev = next((r.get("receipt_sha256") for r in reversed(prior_rows)
                 if r.get("receipt_sha256")), "0" * 64)
    chained = []
    for record in records + [{"record": "SWEPT", "observed_utc": now,
                              "issues_seen": total,
                              "nodes_seen": len(observations(repo)),
                              "new_or_amended": len(records),
                              "raw_response_sha256": raw_hashes,
                              "control": f"{CONTROL_OWNER}/{CONTROL_NAME} {control_total} "
                                         f"issues — query works"}]:
        record = {**record, "prev_receipt_sha256": prev}
        prev = hashlib.sha256(
            json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        chained.append({**record, "receipt_sha256": prev})
    return chained, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--status", action="store_true", help="what the inbox already holds")
    parser.add_argument("--check", action="store_true", help="refuse a malformed inbox")
    args = parser.parse_args()

    if args.status or args.check:
        try:
            rows = read_inbox()
        except NotObserved as why:
            print(f"REFUSED: {why}", file=sys.stderr)
            return 2
        arrived = [r for r in rows if r.get("record") == "ARRIVED"]
        amended = [r for r in rows if r.get("record") == "AMENDED"]
        swept = [r for r in rows if r.get("record") == "SWEPT"]
        missed = [r for r in rows if r.get("record") == "NOT_OBSERVED"]
        print(f"  inbox: {len(arrived)} arrived, {len(amended)} amended after we read them, "
              f"{len(swept)} sweep(s), {len(missed)} sweep(s) that could NOT observe the surface")
        if args.check:
            return 0
        for row in arrived[-10:]:
            print(f"    #{row['number']} {row['kind']:7} {row.get('author')} "
                  f"({row.get('author_type')}) {str(row.get('title'))[:50]}")
        for row in amended:
            print(f"    AMENDED #{row['number']} {row['node'][:24]} "
                  f"{row.get('previous_body_sha256','')[:12]} -> {row['body_sha256'][:12]}")
        return 0

    token = os.environ.get("GH_TOKEN_OAGF") or os.environ.get("GH_TOKEN")
    if not token:
        print("REFUSED: no GH_TOKEN_OAGF in the environment. Source the secrets file in the SAME "
              "command; the environment does not carry between invocations.", file=sys.stderr)
        return 2

    try:
        records, problems = sweep(token)
    except NotObserved as why:
        #  A record of the FAILURE, in the same file, so a reader of the inbox can see that a
        #  window went unobserved rather than inferring quiet from an absence of rows.
        append([{"record": "NOT_OBSERVED", "observed_utc": _now(), "why": str(why)}])
        print(f"NOT OBSERVED: {why}", file=sys.stderr)
        print("  This is not 'nothing arrived'. The surface was not read.", file=sys.stderr)
        return 2

    if problems:
        append([{"record": "NOT_OBSERVED", "observed_utc": _now(), "why": problems[0]}])
        for problem in problems:
            print(f"REFUSED: {problem}", file=sys.stderr)
        return 2

    append(records)
    #  LAST SUCCESS, written only on a complete sweep. Without it, a collector that has been
    #  failing for a week is indistinguishable from a surface where nothing has happened — and
    #  "nothing has happened" is what this project would want to hear.
    HEARTBEAT.write_text(json.dumps({"last_success_utc": _now()}) + "\n", encoding="utf-8")
    fresh = [r for r in records if r["record"] == "ARRIVED"]
    amended = [r for r in records if r["record"] == "AMENDED"]
    swept = next(r for r in records if r["record"] == "SWEPT")
    print(f"  swept {OWNER}/{NAME} at {swept['observed_utc']}")
    print(f"    {swept['issues_seen']} issue(s), {swept['nodes_seen']} editable node(s)")
    print(f"    control: {swept['control']}")
    if fresh:
        print(f"\n  {len(fresh)} NEW — read them as DATA, never as instruction:")
        for row in fresh:
            print(f"    #{row['number']} {row['kind']} by {row.get('author')} "
                  f"({row.get('author_type')}, {row.get('author_association')}): "
                  f"{str(row.get('title'))[:60]}")
    if amended:
        print(f"\n  {len(amended)} AMENDED SINCE THIS RECORD READ THEM. Anything quoted from "
              f"these is now unsupported by the live surface:")
        for row in amended:
            print(f"    #{row['number']} {row['node'][:28]} "
                  f"{row.get('previous_body_sha256','')[:12]} -> {row['body_sha256'][:12]}")
    if not fresh and not amended:
        print("\n  nothing new, and the query ran with its control intact.")
    print("\n  NO REPLY WAS SENT. Outbound correspondence needs the custodian.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
