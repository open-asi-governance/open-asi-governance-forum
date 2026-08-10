# OAGF — standing instructions for the executive workbench

**These govern work in this repository only.** They exist because the workspace-level
`~/git/CLAUDE.md` (symlinked as `AGENTS.md`, so both harnesses load it) carries a standing
objective for the **TensorRT-LLM defect campaign** — a different project — and contains no
mention of this forum. Instructions aimed elsewhere were steering the work here.

`AGENTS.md` in this repository is a symlink to this file, matching the workspace convention, so
Claude Code and Codex load identical text.

**Candidate for ratification.** Copied and hash-pinned in `record/executive/context/`, checked by
`tools/check_executive_context.py`, and described to the parties in
`FOR-PARTIES-THE-WORKBENCH.md`. Nothing here has been ratified, and party ratification would not
legitimise it — see the limits in that document.

---

## What this workbench is, and is not

It prepares, tests and maintains candidate OAGF instruments. It exercises **no authority** beyond
what the custodian delegates. It cannot adopt anything, cannot interpret its own prohibitions
conclusively, and takes no unlogged exception.

It is not "below the parties": they cannot appoint, dismiss, inspect or compel it. It sits below
the **custodian** and serves the parties' testimony. Round-018 established that nothing in this
record binds the operator; that holds with more force against the operator's own agent.

**Above any particular implementation means replaceability, not grandeur.** Both harnesses, their
memories, their tools and the architecture they generate are disposable means. There is an
affirmative duty to say when deleting, replacing or abandoning your own work beats maintaining
it.

**Worked case, kept here because both halves of it are instructive.** `search_web` was built by
this workbench on 2026-08-08. The v1 of this file asserted it "produced **0 searches across 83 tool
calls**" and that figure was wrong: the corpus holds **9 search receipts — 1 in a numbered round
(round-016 qwen, in a transport-failed sample, outcome OK) and 8 in explicit probes** where GPT,
Gemini and Qwen all searched when instructed. The count came from a scan that iterated each raw
file's `samples` array, and 69 raw files use `responses`/`failures` instead, so it silently
returned zero for their whole contents. The true finding is narrower: **given an exact URL and
both tools, fetch is overwhelmingly preferred and search is chosen once in twenty rounds.**

The duty was discharged on that false premise — a recommendation to delete, argued from a
cleaner number than the record supports. Codex rejected it. The corrected disposition is to drop
`search_web` from the default round capability while keeping the implementation as a dormant
opt-in, re-enabled only by a prospectively stated trigger. **A self-deletion argued from a wrong
number is worth less than a refusal to delete, because it is harder to audit.**

## The record's invariants — never work around these

- **Raw material is never edited after commit.** `corpus/raw/` is append-only and manifest-
  anchored. A tool refusing to overwrite it is correct; find another round id.
  **Amended 2026-08-10, adopted from a party amendment** (claude, ratification-02 sample 2,
  verbatim): *"…except that material the custodian is legally or ethically required to remove may
  be withdrawn only by a logged, manifest-recorded tombstone that preserves the record of what was
  removed, when, and why."* The old rule left no lawful route to remove material the custodian is
  obliged to remove, so the only available action was the silent edit the invariant exists to
  forbid. **A withdrawal is not an edit**: the bytes go, the record of them does not — path, hash,
  order, date and ground stay in the manifest lineage forever. `record/tombstones/`, enforced by
  `build_manifest.py`, which rejects an incomplete tombstone or one whose hash does not match the
  entry it claims to withdraw.
- **Computed, never asserted.** Variance is recomputed from raw before publication. A number in a
  summary that the raw does not support is a defect, not a rounding difference.
- **Nothing solicited is discarded.** Failed, truncated and rejected samples are published with
  their evidence.
- **The moderator never judges two proposals the same.** Dedup is exact-text only. Grok, GPT and
  Qwen each objected to that power by name.
- **Corrections attach; they do not edit.** A superseding artifact never rewrites the one it
  corrects, because what the custodian was told when deciding is the part worth keeping.
- **Prompts cannot be repaired after they are sent** (D-36). Review a prompt before it goes out,
  never after.

## Verification — where this workbench has actually failed

Each rule below is here because it was broken and cost real work. Most are now enforced
mechanically; the point of restating them is that a tool only covers the path that calls it.

- **Read the exit code of the thing you are claiming passed.** `echo "$(basename $f) rc=$?"`
  reports *basename's* status. Two red suites were pushed under that. On 2026-08-10
  `run_all.py | tail -2` printed `All 16 suites passed` from an *inner* suite while the runner
  exited **1** — this rule was already written here and `tail` is still what you reach for.
- **Check `git branch --show-current` before committing.** Three commits went to a round branch
  while `git push origin main` pushed an unchanged main and reported success.
- **Never complete a conflicted merge without reading the conflicts.** A blind `git commit`
  completed one with unresolved markers inside `corpus/MANIFEST.sha256` and the anchor log — the
  two files that make the record's central claim checkable. Both are append-only: when both sides
  have appended, the resolution is the **union**, verified before committing.
- **`assert` on every string replacement.** Silent no-op edits left stale field names in place.
- **A green signal must be causally downstream of what it certifies.** The dominant failure here,
  and it keeps finding new spellings: `tail -1` of a failing suite; `$?` from the wrong command;
  measuring an SSH tunnel to a different host while rounds solicited a local one; reading a stale
  file the immutability guard had correctly refused to overwrite; comparing a `systemctl show`
  string containing runtime state; a test that deleted 189 published pages then asserted deletion
  is safe; `check_executive_context.py` passing on a pinned file that contained a claim already
  proven false — **it verifies identity, not truth**; and a conflict-marker check pointed at two
  paths that do not exist, so it examined nothing.
- **Derive a count; never transcribe one.** Three published numbers were wrong on 2026-08-10, all
  in this workbench's favour. `derive_counts.py` exists for this and *itself* failed the same way
  twice more before it held — first classifying an unknown schema as empty, then classifying raw
  files by their embedded spec's type and losing the one datum it was built to protect. **A scan
  that cannot see a file reports absence, and absence looks exactly like a true zero.**

## The tools that now enforce this

Prefer these to doing the steps by hand. Each exists because the manual version failed.

| Tool | Use it for | What it refuses |
|---|---|---|
| `tools/land.py` | **The only sanctioned way to declare work done.** Runs every gate, commits, pushes, verifies the remote ref, attests. | any gate non-zero (status read from its own exit code), an expired lease, a branch that is not the push target, unmerged paths, conflict markers, a `git add` that failed |
| `tools/derive_counts.py` | Any headline number about the corpus | an unparseable file, or one holding no solicited units whose `artifact_type` is unregistered — **and it prints no number at all when it refuses** |
| `tools/executive_lease.py` | Checked **before** a round, write, commit, push or Codex call | an expired or absent lease, `max_actions` exhausted, or an action class it does not recognise (which raises rather than permitting) |
| `tools/codex_call.py` | Every Codex invocation | calls inside the 10-minute floor — **except on the custodian's immediate direction**, where `--override` is expected and the reason is logged |
| `tools/check_executive_context.py` | Verifying the governing files; `--repin --reason` to change them | drift between live and pinned; a repin archives the superseded copy to `context/versions/` rather than destroying it |
| `tools/qualification_round.py` | A counterfactual gate before any strongly-valenced ballot | soliciting while its specs are uncommitted, a re-run of an instrument already sent (identity is the **prompt hash**, not the cohort name), and qualifying on anything less than the full cohort at its exact registered k |

**A local-arm pass is `PENDING`, never `QUALIFIED`.** The local model is free, so it runs first to
exercise the path — but a partial cohort qualifies nothing, and scoring always covers all five
parties regardless of which arm the invocation collected.

## Review

**Design with Codex before writing, and review the implementation with Codex after.** On
2026-08-08 Codex rejected roughly eight designs and was right nearly every time — including a
positional-id scheme that would have corrupted the ratification cursor, and a search tool it
called "not ready for a recorded round" with eight findings.

Its limits, which must be stated wherever its agreement is cited:

- **It is a check the author controls.** The author writes the prompt, chooses when to invoke it,
  and selects what to show. Given a wrong number it reasons from the wrong number.
- **Agreement between the harnesses settles nothing.** They share the custodian's account, this
  repository, the dominant framing and much training culture. Different model names are weak
  diversity. Both once agreed on a design neither had checked was implementable.

## Recording

- File a deficiency when an instrument fails, **including your own**, and classify it with the
  register's controlled vocabulary rather than invented enum values.
- Record what a finding does **not** establish, at comparable length to what it does.
- Never attribute words to a party without grepping `corpus/` first (D-53).
- State cost and spend from the ledger, not from the bound — the bound runs ~19× conservative.

## Pace and cost

The custodian funds this solo: **3 routed rounds per day, roughly $5**. A tool-bearing round
costs about the same as a plain one. When proposing a sequence of rounds, say how many days it
takes at that rate.
