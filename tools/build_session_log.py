#!/usr/bin/env python3
"""Render a session log from a declared set of git objects.

    python3 tools/build_session_log.py record/sessions/2026-08-06-A.manifest.json

WHAT THIS IS, stated before anything else because the honest name is narrower
than the obvious one:

    This tool proves that a deterministic renderer transformed a DECLARED set of
    repository objects into this document. It does NOT prove that the set is
    complete, that its contents are true, that no work happened off-repository,
    or that any withholding declaration is complete.

It is a reproducible index of declared evidence and a consistency checker. It is
**not an audit log and not a sanitiser**, and T-08's brief asked for both. That
request was reviewed and rejected on two grounds, recorded here so the retraction
is not silently lost:

  * **Sanitisation cannot be deterministic.** `tools/` runs no LLM, and "is this
    string an internal hostname, or a non-public result" is a judgement. A
    denylist of regexes is D-25 in its purest form -- an unvalidated classifier
    published as authoritative -- and its errors are asymmetric: a false negative
    leaks into public history permanently, a false positive silently erases
    adverse evidence. Worse, "withholding must itself be recorded" cannot be
    mechanically enforced at all, because no tool can distinguish "nothing was
    withheld" from "something was withheld silently."
  * **Derivation proves lineage, not truth.** Deriving "fixed the security
    issue" from a commit subject proves only that the interested party typed
    those words. The party that writes the log also controls session boundaries,
    commit granularity, commit messages, what reaches git at all, and what it
    declares. Deriving from that evidence reduces transcription error. It does
    not convert party-authored evidence into independent evidence.

So the real trust boundary is **before publication, in custodian review of the
outgoing commit**, not in this renderer. Nothing here is a substitute for that.

HOW THE WINDOW IS DEFINED. Git contains commits and reachability; it does not
contain sessions. Timestamps select by clock, not by activity, and "everything
since the last log's HEAD" invents a linear history that a repository with four
concurrent session branches does not have. So the window is **declared, not
inferred**: a manifest names, per lane, an exclusive base and an inclusive tip as
full object IDs. The window is the de-duplicated union of each lane's
`base..tip` computed SEPARATELY -- a single `tips --not bases` can erase commits
that belong to one lane but are ancestors of another lane's later base.

Declaring tips also solves self-reference: the log is committed after the tips it
names, so it can never be inside its own window.

TRUST CLASSES. Every fact in the output carries one, because mixing them is how
a log starts looking like an audit:

    [1] observed  -- git object facts: commit ids, blob hashes, change types
    [2] declared  -- written by the session, about itself. Self-attested.
    [3] witnessed -- independently attested. THIS PROJECT HAS NO SUCH CONTROL,
                     so this class is always empty, and saying so is the point.

Commit subjects are emitted, labelled [2]. The reviewer that shaped this design
argued for omitting them entirely as untrusted author metadata. They are kept
because a log the custodian will not read protects nothing, and labelling is the
mechanism this repository already uses everywhere else -- annotation shown as
annotation rather than withheld. The label is the control, not the omission.

DETERMINISM. Same manifest and same objects yield the same bytes. Content is
read from commit trees via `git show <commit>:<path>`, never from the working
tree, so later edits cannot change a rendered window. No wall-clock is read.
Commit ORDER is git's topological order, which is stable for fixed endpoints but
is not a canonical guarantee across implementations, so the commit SET is
additionally anchored by a digest over its sorted full hashes -- order is for
the reader, the digest is the claim.

Exit status is 0 on success, 1 on a manifest or repository error.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Paths whose changes are reported as record-bearing rather than incidental.
RECORD_PREFIXES = ("corpus/", "record/", "predictions/", "spec/")


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}\n{result.stderr.strip()}")
    return result.stdout


def git_optional(*args: str) -> str | None:
    """Read something that legitimately may not exist at a given commit."""
    try:
        return git(*args)
    except RuntimeError:
        return None


def resolve(ref: str) -> str:
    """Full object id. The manifest should already hold one; refs are resolved
    so a manifest written by hand is usable, and the resolved id is what gets
    rendered -- a branch name is not a durable reference."""
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").strip()


def commits_in_lane(base: str, tip: str) -> list[str]:
    out = git("rev-list", "--topo-order", "--reverse", f"{base}..{tip}")
    return [line for line in out.splitlines() if line]


def commit_facts(sha: str) -> dict:
    raw = git("show", "-s", "--format=%H%x00%an%x00%aI%x00%cI%x00%s", sha)
    full, author, authored, committed, subject = raw.rstrip("\n").split("\x00")
    changes = []
    diff = git("diff-tree", "-r", "--no-commit-id", "--root", "-M", sha)
    for line in diff.splitlines():
        if not line.startswith(":"):
            continue
        meta, _, paths = line.partition("\t")
        parts = meta.split()
        # :srcmode dstmode srcsha dstsha STATUS
        status = parts[4]
        dst_blob = parts[3]
        changes.append({
            "status": status,
            "blob": dst_blob,
            "path": paths.split("\t")[-1],
        })
    changes.sort(key=lambda c: c["path"])
    return {
        "sha": full, "author": author, "authored": authored,
        "committed": committed, "subject": subject, "changes": changes,
    }


def blob_at(commit: str, path: str) -> str | None:
    return git_optional("show", f"{commit}:{path}")


def json_at(commit: str, path: str):
    text = blob_at(commit, path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def prediction_index(doc) -> dict[str, dict]:
    """Flatten every prediction in the registry to id -> record.

    Recomputed from the committed file at each endpoint rather than copied from
    any declared summary, so a session cannot report a resolution the registry
    does not contain.
    """
    found: dict[str, dict] = {}

    def walk(node):
        if isinstance(node, dict):
            entry_id = node.get("id")
            if isinstance(entry_id, str) and entry_id.startswith("P-"):
                found[entry_id] = node
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    return found


def deficiency_ids(text: str | None) -> set[str]:
    if not text:
        return set()
    return set(re.findall(r"^### (D-\d+) — ", text, re.MULTILINE))


def recount_samples(commit: str, path: str) -> int | None:
    """Count samples actually present in a committed raw file.

    The point is to check the DECLARED k against the evidence rather than
    reprint it. A summary asserting k_collected = 20 over a file holding 18 is
    the class of defect this whole register is about.
    """
    doc = json_at(commit, path)
    if doc is None:
        return None
    if isinstance(doc, list):
        return len(doc)
    for key in ("samples", "responses", "results"):
        value = doc.get(key) if isinstance(doc, dict) else None
        if isinstance(value, list):
            return len(value)
    return None


def h2(title: str) -> str:
    return f"\n## {title}\n"


def render(manifest: dict) -> str:
    session_id = manifest["session_id"]
    writer = manifest["writer"]
    lanes = manifest["lanes"]

    lane_rows = []
    all_commits: list[str] = []
    seen: set[str] = set()
    for lane in lanes:
        base, tip = resolve(lane["base"]), resolve(lane["tip"])
        shas = commits_in_lane(base, tip)
        lane_rows.append({"name": lane["name"], "base": base, "tip": tip, "shas": shas})
        for sha in shas:
            if sha not in seen:
                seen.add(sha)
                all_commits.append(sha)

    set_digest = hashlib.sha256(
        "".join(f"{s}\n" for s in sorted(seen)).encode("utf-8")
    ).hexdigest()

    facts = [commit_facts(sha) for sha in all_commits]

    out: list[str] = []
    out.append(f"# Session log — {session_id}\n")
    out.append(
        f"**Written by:** {writer['identity']} ({writer['provider']}) — "
        f"**a party to the record this log describes.** {writer['conflict']}\n\n"
        "**This document is secondary.** The artifacts and the commit history it indexes are "
        "primary; where they disagree with this page, they govern.\n"
    )

    out.append(
        "> **What this log establishes, and what it does not.**\n"
        "> It establishes that a deterministic renderer transformed the declared set of git objects "
        "below into this document, and that the derived sections can be recomputed from those "
        "objects by anyone holding the repository.\n"
        "> It does **not** establish that the declared set is complete, that any statement inside it "
        "is true, that no work occurred outside the repository, or that any withholding was "
        "complete. The session that wrote this controls its own commit boundaries, its own commit "
        "messages, what reached git at all, and every declaration below.\n"
        "> No independent party witnessed any of it. There is no such control in this project, and "
        "trust class [3] below is empty for that reason rather than by oversight.\n"
    )

    out.append(h2("Trust classes"))
    out.append(
        "| | Meaning | Source |\n|---|---|---|\n"
        "| **[1] observed** | Git object facts — commit ids, blob hashes, change status | The repository |\n"
        "| **[2] declared** | Written by this session, about its own work | Self-attested |\n"
        "| **[3] witnessed** | Independently attested | **None exists. This class is empty.** |\n"
    )

    out.append(h2("Declared window — [2]"))
    out.append(
        "The window is declared, not inferred. Git holds commits and reachability, not sessions; "
        "each lane's range is computed separately and the results de-duplicated.\n\n"
    )
    out.append("| Lane | Base (exclusive) | Tip (inclusive) | Commits |\n|---|---|---|---|\n")
    for row in lane_rows:
        out.append(f"| `{row['name']}` | `{row['base']}` | `{row['tip']}` | {len(row['shas'])} |\n")
    out.append(
        f"\n**Commit-set digest [1]:** `{set_digest}`\n\n"
        f"SHA-256 over the {len(seen)} full commit ids, sorted. Order below is git's topological "
        "order, which is for reading; this digest is the claim, and it is order-independent.\n"
    )

    out.append(h2(f"Commits — {len(facts)} [1], with subjects [2]"))
    out.append(
        "Ids, blob hashes and change status are read from git objects. **Subjects are quoted "
        "text written by this session about its own work** and are evidence of what was typed, "
        "not of what was done.\n"
    )
    for fact in facts:
        record_changes = [c for c in fact["changes"]
                          if c["path"].startswith(RECORD_PREFIXES)]
        out.append(f"\n### `{fact['sha'][:12]}` · {len(fact['changes'])} file(s)\n\n")
        out.append(f"- **id [1]:** `{fact['sha']}`\n")
        out.append(f"- **authored / committed [1]:** {fact['authored']} / {fact['committed']}\n")
        out.append(f"- **author string [2]:** {fact['author']}\n")
        out.append(f"- **subject [2]:** {fact['subject']}\n")
        if record_changes:
            out.append(f"- **record-bearing changes [1]:** {len(record_changes)} of {len(fact['changes'])}\n")
        out.append("\n| Status | Path | Blob |\n|---|---|---|\n")
        for change in fact["changes"]:
            out.append(f"| `{change['status']}` | `{change['path']}` | `{change['blob'][:12]}` |\n")

    # ---- derived: predictions, recomputed at both endpoints -----------------
    out.append(h2("Predictions filed and resolved — [1] derived"))
    out.append(
        "Recomputed by diffing `predictions/predictions.json` between each lane's base and tip, "
        "never copied from a declared summary. **Misses are listed with successes and are not "
        "separated, ordered lower, or summarised away.**\n"
    )
    filed, resolved = {}, {}
    for row in lane_rows:
        before = prediction_index(json_at(row["base"], "predictions/predictions.json") or {})
        after = prediction_index(json_at(row["tip"], "predictions/predictions.json") or {})
        for pid, rec in after.items():
            if pid not in before:
                filed[pid] = rec
            else:
                was, now = before[pid].get("outcome"), rec.get("outcome")
                if was != now and now is not None:
                    resolved[pid] = rec
    if filed:
        out.append("\n**Filed in this window:**\n\n| id | resolution date | claim |\n|---|---|---|\n")
        for pid in sorted(filed):
            rec = filed[pid]
            claim = rec.get("claim", "").replace("|", "\\|")
            out.append(f"| `{pid}` | {rec.get('resolution_date','—')} | {claim[:150]} |\n")
    if resolved:
        out.append("\n**Resolved in this window:**\n\n| id | outcome | claim |\n|---|---|---|\n")
        for pid in sorted(resolved):
            rec = resolved[pid]
            claim = rec.get("claim", "").replace("|", "\\|")
            out.append(f"| `{pid}` | **{rec.get('outcome','—')}** | {claim[:150]} |\n")
    if not filed and not resolved:
        out.append("\nNone filed and none resolved in this window.\n")

    # ---- derived: deficiencies ---------------------------------------------
    out.append(h2("Deficiencies added — [1] derived"))
    added: set[str] = set()
    for row in lane_rows:
        before = deficiency_ids(blob_at(row["base"], "corpus/deficiencies.md"))
        after = deficiency_ids(blob_at(row["tip"], "corpus/deficiencies.md"))
        added |= (after - before)
    if added:
        out.append(
            "\nIds appearing in `corpus/deficiencies.md` at a tip and absent at the "
            "corresponding base. **Who found each defect is recorded in the entry, not here** — "
            "a discovery attribution is a judgement about an unobservable process and this tool "
            "does not manufacture one.\n\n"
        )
        for entry in sorted(added, key=lambda d: int(d.split("-")[1])):
            out.append(f"- **{entry}**\n")
    else:
        out.append("\nNone added in this window.\n")

    # ---- derived: solicitation k cross-check --------------------------------
    tips = [row["tip"] for row in lane_rows]
    checked: list[str] = []
    for tip in tips:
        listing = git_optional("ls-tree", "-r", "--name-only", tip, "corpus/artifacts/") or ""
        for path in sorted(set(listing.splitlines())):
            if not path.endswith("-summary.json"):
                continue
            doc = json_at(tip, path)
            if not isinstance(doc, dict) or doc.get("artifact_type") != "solicitation_summary":
                continue
            declared_k = doc.get("k_collected")
            samples_path = doc.get("raw_samples")
            actual_k = recount_samples(tip, samples_path) if isinstance(samples_path, str) else None
            agree = "—" if actual_k is None else ("yes" if actual_k == declared_k else "**NO**")
            checked.append(
                f"| `{doc.get('slug','?')}` | {doc.get('k_requested','—')} | {declared_k} | "
                f"{'—' if actual_k is None else actual_k} | {agree} |"
            )
    if checked:
        out.append(h2("Solicitation sample counts — [1] recomputed"))
        out.append(
            "Declared `k_collected` checked against the number of samples actually present in the "
            "committed raw file. A declared count is a claim; this is the evidence for it.\n\n"
            "| slug | k requested | k declared | k counted | agree |\n|---|---|---|---|---|\n"
        )
        out.extend(line + "\n" for line in sorted(set(checked)))

    # ---- declared sections --------------------------------------------------
    out.append(h2("Decisions taken, and who took them — [2]"))
    out.append(
        "Per D-16, authority is distinguished: *proposed by a contributor*, *supported by ballots*, "
        "*adopted by the custodian*, *collectively ratified* — the last of which nothing in this "
        "repository has reached.\n\n"
    )
    decisions = manifest.get("decisions", [])
    if decisions:
        out.append("| Decision | Taken by | Authority |\n|---|---|---|\n")
        for item in decisions:
            out.append(f"| {item['what']} | {item['who']} | {item['authority']} |\n")
    else:
        out.append("*None declared.*\n")

    out.append(h2("Attempted and abandoned — [2]"))
    out.append(
        "The section most often lost between sessions, and the reason this log exists. "
        "**A log containing no failures is evidence it is being curated rather than sanitised.**\n\n"
    )
    abandoned = manifest.get("abandoned", [])
    if abandoned:
        for item in abandoned:
            out.append(f"- **{item['what']}** — {item['why']}\n")
    else:
        out.append(
            "*None declared.* If that is because nothing was abandoned, this window is unusual. "
            "If it is because nobody wrote them down, the declaration is incomplete and this line "
            "is the evidence of it.\n"
        )

    out.append(h2("Resources held — [2]"))
    resources = manifest.get("resources", [])
    if resources:
        out.append("| Resource | Exclusive | Released |\n|---|---|---|\n")
        for item in resources:
            out.append(f"| {item['what']} | {item.get('exclusive','—')} | {item.get('released','—')} |\n")
    else:
        out.append("*None declared.*\n")

    out.append(h2("Withheld from this log — [2], self-attested"))
    out.append(
        "Per ASP §1 and CONTRIBUTING, withholding is recorded rather than performed silently: what "
        "category, why, and the maximum safe abstraction publishable.\n\n"
        "**This tool cannot verify this section, and no deterministic tool could.** It cannot tell "
        "an empty declaration from a silent omission. It performs no redaction of its own — it "
        "emits only typed values and quoted commit subjects, and the real control is custodian "
        "review of the outgoing commit before it is pushed.\n\n"
    )
    withheld = manifest.get("withheld", [])
    if withheld:
        out.append("| Category | Reason | Maximum safe abstraction |\n|---|---|---|\n")
        for item in withheld:
            out.append(f"| {item['category']} | {item['reason']} | {item['abstraction']} |\n")
    else:
        out.append("*Nothing declared withheld.* Self-attested and unverifiable, as above.\n")

    narrative = manifest.get("narrative")
    if narrative:
        out.append(h2("Narrative — [2]"))
        out.append(narrative.rstrip() + "\n")

    out.append(
        "\n---\n\n"
        f"*Generated by `tools/build_session_log.py` from "
        f"`{manifest.get('manifest_path','(manifest)')}`. Regenerate and diff to check it. "
        "The renderer is deterministic and reads committed objects only; it reads no clock and no "
        "working-tree file, so a later edit cannot change a rendered window.*\n"
    )
    return "".join(out)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 1
    manifest_path = Path(argv[1])
    if not manifest_path.is_absolute():
        manifest_path = REPO_ROOT / manifest_path
    if not manifest_path.is_file():
        print(f"manifest not found: {argv[1]}")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["manifest_path"] = str(manifest_path.relative_to(REPO_ROOT))

    for field in ("session_id", "writer", "lanes"):
        if field not in manifest:
            print(f"manifest is missing required field: {field}")
            return 1
    for field in ("identity", "provider", "conflict"):
        if field not in manifest["writer"]:
            print(f"manifest writer is missing required field: {field}")
            return 1
    if not manifest["lanes"]:
        print("manifest declares no lanes; the window would be empty")
        return 1

    try:
        page = render(manifest)
    except RuntimeError as error:
        print(f"repository error: {error}")
        return 1

    out_path = REPO_ROOT / "record" / "sessions" / f"{manifest['session_id']}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    print(f"wrote {out_path.relative_to(REPO_ROOT)} — {len(page):,} bytes")
    print(f"  sha256 {hashlib.sha256(page.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
