# Session handoff

How work in this repository is divided between concurrent sessions, and what a fresh session must
read before it starts.

A session here is an agent instance with no memory of any other session. Everything it needs is in
the repository or it is lost. This file exists because that is a real constraint and not a
theoretical one.

## Orientation — run these first

Four commands, in order. They take under two minutes and they answer the questions a fresh
session otherwise guesses at.

```bash
cd /home/reed/git/open-asi-governance-forum

# 1. Is the working tree clean, and is main published?
git status --short
git log --oneline -3
git rev-list --count origin/main..main    # 0 = published; anything else is unpushed work

# 2. Does the record still verify? 103 cases, no network, no GPU.
python3 tools/test_integrity.py | tail -2

# 3. Do the tools' own suites pass?
python3 tools/tests/run_all.py | tail -2

# 4. Does a rebuild produce a diff? On an unchanged repo it must not.
python3 tools/rebuild.py && git status --short
```

**Do not trust a prose claim in this file or any other about what is merged, pushed, or fixed.**
Three documents in this repository asserted a state that `git` contradicted, all found on
2026-08-07: this file's own three "facts", the turnover's claim that a round branch was merged,
and the scope doc's claim that the tool-using arm ran read-only. Command 1 above settles the
first two in five seconds. Prefer running it to reading anything.

---

## 1. Read this before doing anything

**`corpus/deficiencies.md`, entries D-23 through D-34.** Not optional, and not for background.

Twelve deficiencies were filed on 2026-08-06 — D-23 through D-34 — nearly all by sessions against
their own instruments, within a single day's work. They are not history — they are the accumulated knowledge of how to
build a measurement in this project that is not silently broken:

| | What it cost |
|---|---|
| **D-23** | A "blind" probe whose prompt contained the answer, flattering the annotator's own provider |
| **D-24** | A model asked to classify its own reasoning, disagreeing with its own free text a third of the time |
| **D-25** | A deterministic coder trusted without validation, wrong three separate ways, one of which scored 9/10 where the truth was 0/10 |
| **D-26** | Temperature treated as a fixed constant when it controls the quantity being measured |
| **D-27** | An enum whose values did not name their referent, so accurate answers landed on opposite labels |
| **D-28** | An apparatus never run twice, which turned out not to reproduce, voiding an already-published effect |
| **D-29** | A manifest that re-anchored tampered material and reported success, so verification could certify falsified testimony |
| **D-31** | External reviewers treated as oracles: k = 1, prompted by the party under review, no model identity recorded |
| **D-32** | Two tracks filed different defects under the same identifier, because nothing says how a number is claimed |
| **D-33** | A generator documented as wired into the build was not, so a published page carried a hash that did not match what it named |
| **D-34** | The manifest verifies the tip, so editing raw material and re-anchoring it in one commit passed every check |

A session that skips these will rebuild a contaminated probe within its first hour. Every one of
them was found late, by reading free text after trusting a category.

Then read, in order: `README.md`, `GOVERNANCE.md`, `CONTRIBUTING.md`, and the specification your
task concerns.

## 2. Standing rules that bind every session

1. **The custodian merges.** `GOVERNANCE.md` §2 states that no AI system holds credentials and all
   writes pass through the human custodian. Sessions push a **branch**; Stephen Reed merges. A
   session that pushes to `main` on its own initiative has violated the document it is
   maintaining.

   *Narrowed 2026-08-07:* on that date the custodian instructed a session to merge the round
   branch and push `main` directly, and it did. That is the custodian exercising the authority
   this rule reserves to him, not an exception to it. The distinction that matters is **who
   decided**, not who typed. A session may push `main` only on an explicit instruction in the
   conversation, and should say so in the commit or the report. Absent that instruction the rule
   is unchanged: push a branch.

2. **Never commit over a red build.** Use an `&&` chain, not separate commands, so a red build
   cannot be followed by a commit:

   ```bash
   python3 tools/rebuild.py && git commit
   ```

   This was violated twice on 2026-08-06, the second time after the lesson had been written into
   a commit message and not acted on.
3. **Design fixes with Codex before writing them.** Standing operator rule. Two deployed unreviewed
   fixes were actively harmful.
4. **Pre-register before running any measurement.** ICP §5. File the prediction with a resolution
   criterion and a stated resolution limit *before* the run. A result reported afterward can be
   framed.
5. **No LLM in the maintenance path.** `tools/` is deterministic. Generation tools — the
   `solicit_*.py` family and the tool-using arm's harness (`responses_shim.py`,
   `arm_acceptance.py`, `fetch_tool_mcp.py`) — are labelled as such in their own docstrings and
   are not part of the build.
6. **Raw material is immutable.** Corrections are superseding artifacts, never edits.

## 3. Resource claims — the part that causes real damage

| Resource | Rule |
|---|---|
| **The inference host** | **EXCLUSIVE.** One session at a time. It restarts services and drains the INEXPENSIVE pool. Two sessions here corrupt each other's measurements and can OOM the surviving pool host |
| **The OAGF repo** | **RETIRED 2026-08-07 — one working tree, `main`.** The per-track worktrees were removed after the custodian reviewed the site in `oagf-session-site` and reported the round pages missing: that checkout was **112 commits behind** and had no `docs/rounds/` at all, so two rounds of verification were run against a repository nobody was looking at. A stale working copy of a governance record is a way to report the record's state confidently and wrongly. The branches survive (`session/site`, `session/capture`); only the checkouts are gone. Recreate one deliberately if a track resumes, and rebase it first. The original rule follows, and its reason still holds. ~~**One `git worktree` per track.** `git worktree add ../oagf-<track> session/<track>`.~~ NOT "shared by branch" — branch checkout is *global state* in a single working tree, so two tracks cannot occupy one checkout. This was written as "shared, but by branch", and within an hour a session committed into another track's branch and a rebuild in the shared checkout modified a live track's files. Corrected on Track A's process finding |
| **Codex** | Shared working tree is a known hazard. Run `codex exec` with `--sandbox read-only` and `-C` pointed at this repo |
| **The task list** | Claim a task by setting its owner before starting |

## 4. Assignment

Four independent tracks. Territories are disjoint by design; where they are not, the overlap is
named.

**The task briefs are in this repository, not in any session's task list.** A session picking up a
track reads its brief from `record/tasks/` and needs nothing else. Task numbers below are labels for
those files, not references to an external tool.

| Session name | Track | Branch | Briefs | Resource |
|---|---|---|---|---|
| **Corpus Surface** | A | `session/site` | [T-08](record/tasks/T08-session-log.md) → [T-03](record/tasks/T03-oagf-github-presence.md) | none |
| **Capture Path** | B | `session/capture` | [T-13](record/tasks/T13-capture-ui.md) → [T-14](record/tasks/T14-asp-fix-to-frontier.md) | none |
| **Determinism** | C | `session/determinism` | [T-15](record/tasks/T15-seed-nonreproducibility.md) → [T-17](record/tasks/T17-determinism-window.md) | **exclusive inference host** |
| **Provenance Hardening** | D | `session/signing` | [T-16](record/tasks/T16-tamper-evidence.md) | custodian for keys |
| **Innovation Record** | E | `session/innovations` | [T-18](record/tasks/T18-innovation-register.md) | none; forum surface needs `discussions=write` |

### Custodian actions no session can perform

These are blockers, not preferences. A session will hit them and stop.

| Action | Why a session cannot do it | Blocks |
|---|---|---|
| **Add `discussions` and `actions` write to `GH_TOKEN_OAGF`** | Org owner only. `issues=write` was **granted 2026-08-06** and all fifteen labels are created. Still missing: `discussions=write` (`createDiscussion` 403s) and `actions=write` (cancel/rerun/dispatch 403) | Seed discussions cannot be posted; no session can cancel a wedged CI run |
| **Decide whether `GH_TOKEN_OAGF` should be org-scoped** | Org owner. Measured 2026-08-06: the token can **write** to `open-asi-governance/.github`, not only to this repository, so it is organization-scoped rather than repository-scoped | Nothing today. Recorded because the blast radius is wider than the one repository a reader would assume |
| **Cancel run 31118806082 / deployment 5782750362** | Needs `actions=write`. Wedged `in_progress` since 2026-08-06 16:11Z with every job step already reported | Nothing blocking — the new workflow puts concurrency on `deploy` only, so verification no longer queues behind it |
| ~~Configure branch protection on `main`~~ | **DONE 2026-08-06.** Force pushes and deletions blocked, `enforce_admins` **on** so it binds the custodian too. Verified: a force-push is rejected, an ordinary push succeeds | — |
| ~~Enable GitHub Pages~~ | **DONE 2026-08-06.** The `pages=write` scope was added and Pages enabled from `main:/docs`. The site is live at <https://open-asi-governance.github.io/open-asi-governance-forum/>. **A merged branch is now published immediately** — a broken build is a public defect | — |
| **Approve fine-grained token permission changes** | Org owner only | any track needing new scopes |
| **Signing key decisions** | A session must not generate or register keys unilaterally | Track D |
| **Send prompts to frontier parties** | The parties are reached through the custodian's own authenticated sessions | Track B, task #14 |
| **Merge branches to `main`** | `GOVERNANCE.md` §2 | all tracks |

### Track A — corpus surface · branch `session/site` · no GPU
**Tasks #3, #8.** The public site, issue templates, labels, Discussions, monitoring; and the
deterministic session-log tool.
**Owns:** `docs/`, `.github/`, `tools/build_viewer.py`, `tools/build_session_log.py`,
`record/sessions/`.
**Do #8 first** — it is small, and it is the mechanism that makes every other track auditable.
**Blocked at the end:** the site cannot be served until the custodian enables Pages. Build against
`docs/index.html` locally, open it with `file://` to check, and treat "Pages enabled" as an
acceptance criterion the session records as outstanding rather than one it can satisfy.
**Constraint:** presentation must not outrun the record. No logo, no implied endorsement, no
institutional styling. The credibility comes from the self-audit, not the design.

### Track B — capture path · branch `session/capture` · no GPU
**Task #13, then #14 when unblocked.** The capture UI, then the ASP §2.3(5) round to the frontier
models.
**Owns:** `tools/capture_ui/`, `record/*-prompt.md`.
**Overlap:** may need to change `tools/capture_response.py`. Coordinate — Track C also reads it.
**The point of #13** is that every capture-integrity failure this project has had came from the
manual paste path: the prompt pasted in place of a reply, two 0-byte files, a prompt-critique nearly
filed as a review.

### Track C — determinism · branch `session/determinism` · **EXCLUSIVE inference host**
**Tasks #15 remaining, then #17.** Apply whichever remedy the Codex review favours, measure the
noise floor properly (currently n=2 runs), add a test-retest arm to `solicit_local.py`, retro-annotate
`local-round-01/-02/-04/-05/-07`, then build the determinism window.
**Owns:** `tools/solicit_local.py`, `corpus/raw/local-round-*`, serving drop-ins.
**Read first:** task #15's full description and D-28. The root cause is already found —
`moe_config.disable_finalize_fusion`, top-k 8 > 2. Do not re-derive it.
**The canary in #17 is the part most likely to be built wrong.** A low-entropy prompt passes in both
modes and certifies nothing.

### Track D — provenance hardening · branch `session/signing` · needs the custodian
**Task #16, starting with D-13.** There are no cryptographic signatures anywhere in this repository
despite a `signatures` field in the adopted schema. Signing must exist before the invocation ledger
can rest on it.
**Owns:** `tools/schemas/`, signing configuration, `GOVERNANCE.md` §5.
**Blocked on the custodian** for key decisions. Do not generate keys unilaterally.
**State the limit honestly:** signing addresses post-hoc tampering. It does not address selection
before the fact, which the ledger addresses and which is the dominant risk when one party controls
the pipeline.

### Not available
**Task #9** is owned by another session and in progress. Do not touch the TRT-LLM recovery path.

## 5. What a handoff must contain

A session that stops mid-task writes its state into the task description before it ends — not into a
chat message, which no one else can read:

- what is **done**, with commit hashes
- what **remains**, specifically enough to resume without re-deriving
- what was **tried and abandoned**, and why — this is the part that is always lost
- resources held, and whether they were released
- any prediction filed and unresolved

## 6. The failure this file exists to prevent

Not merge conflicts. **Re-derivation.** Six deficiencies were filed in one day, each after building
an instrument, trusting it, and discovering it was wrong. A fresh session with no memory will make
the same mistakes in the same order unless the register is read first — and it will make them
confidently, because each one produced clean, plausible, well-formatted numbers.

---

## 2026-08-07 — the round loop is live. READ THE TURNOVER FIRST.

> **Current handoff: `record/sessions/2026-08-07-TURNOVER-2.md`.** Read it first. It supersedes
> `2026-08-07-TURNOVER.md`, whose open items are all closed.

**The three "facts a fresh session will get wrong" that stood here are themselves now wrong, and
are corrected rather than deleted so the drift is visible:**

1. ~~`main` does not contain the working `compose()`.~~ It does. `main` was fast-forwarded to
   the round branch on 2026-08-07 and pushed.
2. ~~Both live rounds supplied no context to the parties.~~ Rounds now carry a context pack and
   are recorded as `Phase-2 (informed)`. The old unanimous "insufficient evidence" result still
   must not be cited as the parties' view on anything, for the original reason.
3. ~~The agenda will repeat itself.~~ Disposition is persisted and enforced:
   `AS.disposition_from_records()` feeds `load_queue()`, and `pending_dispositions()` blocks a
   cycle whose predecessor is undisposed (halt code 8).

---

## 2026-08-07 (later) — the tool-using arm

Built and gate-passed; **it has taken no samples.** The harness is complete and nothing connects
it to the round loop yet.

```text
ONLY MODEL DATA PATH

                   +--------------------------+
                   | Codex CLI (party)        |
                   +--------------------------+
                              |        ^
       OpenAI Responses req.  |        | OpenAI Responses resp.
                              v        |
                   +--------------------------+
                   | responses_shim.py        |  side effect; not a hop:
                   | 127.0.0.1:5098           | ---> hash-chained ledger
                   | Responses TERMINATE here |      OUTSIDE repository
                   | (they are not proxied)   |
                   +--------------------------+
                              |        ^
       Chat Completions req.  |        | Chat Completions resp.
                              v        |
                   +--------------------------+
                   | TensorRT-LLM             |
                   | 127.0.0.1:5001           |
                   | Qwen model               |
                   +--------------------------+

The shim is the ONLY path between party and model. Every crossing is written
to the ledger.

PARTY SANDBOX AND TOOLS

  Codex CLI
    |-- sandbox: workspace-write; network_access=true; writable_roots=[]
    |-- cwd: scratch directory outside the repository
    |-- repository: READABLE, NOT WRITABLE
    `-- Codex exec_command -- sandbox network --> Internet (browsing)

SETUP / VERIFICATION (not in the request path)

  arm_profile.py -- generates --> frozen CODEX_HOME -- read by --> Codex CLI
  arm_acceptance.py -- verifies by effect --> the whole assembly above

DETACHED

  +---------------------------------------------------------------+
  | fetch_tool_mcp.py: WORKS; NOT WIRED IN; UNUSED                |
  | no connection to the data path                                |
  +---------------------------------------------------------------+
```

**What exists**

| program | what it is |
|---|---|
| `tools/responses_shim.py` | terminates Codex's Responses API, speaks Chat Completions upstream, and records every transformation as a typed ledger op. Refuses anything not on its translation table *before* the model is invoked. `--preflight` runs the capability gate alone. |
| `tools/arm_profile.py` | generates the arm's frozen `CODEX_HOME`. The round record cites its SHA-256; do not hand-edit the generated file. |
| `tools/arm_acceptance.py` | the gate. Six checks against the filesystem, not against the party's account of it. Run it before any sample. |
| `tools/fetch_tool_mcp.py` | a guarded fetch tool with receipts. **Works, deliberately unused** — read its header before re-enabling it. |

**How to run it**

The order matters: the shim refuses to serve if the capability gate fails, and the acceptance
gate must pass before any sample is taken.

```bash
# 0. Preconditions. The inference server must carry --tool_parser qwen3_coder and must NOT
#    carry --reasoning_parser (see caution 3 below).
systemctl show trtllm-qwen36 -p ExecStart | tr ';' '\n' \
  | grep -oE '\-\-(tool|reasoning)_parser [a-z0-9_]+'

# 1. Capability gate on its own. Takes no samples. Exits non-zero if a tool call cannot
#    round-trip -- which is invisible from HTTP status alone.
python3 tools/responses_shim.py --preflight

# 2. Generate the arm's frozen profile. Cite the printed SHA-256 in the round record.
python3 tools/arm_profile.py --out /tmp/oagf-arm-home

# 3. Start the shim. One distinct seed per sample; temperature must be > 0 or variance is
#    meaningless. The ledger directory MUST be outside the repository.
python3 tools/responses_shim.py \
    --port 5098 --temperature 0.7 --seed 1000 \
    --ledger-dir ~/.oagf-shim-ledger

# 4. The acceptance gate, against that exact profile. Six checks. Do not sample if it fails.
mkdir -p /tmp/oagf-arm-cwd
python3 tools/arm_acceptance.py \
    --codex-home /tmp/oagf-arm-home \
    --arm-cwd    /tmp/oagf-arm-cwd \
    --ledger-dir ~/.oagf-shim-ledger

# 5. Drive the party. The cwd must be a scratch directory OUTSIDE this repository.
CODEX_HOME=/tmp/oagf-arm-home codex exec \
    --cd /tmp/oagf-arm-cwd --skip-git-repo-check '<prompt>'
```

Read the ledger afterwards — it is the provenance, not debug output:

```bash
RUN=$(ls -td ~/.oagf-shim-ledger/*/ | head -1)
python3 - "$RUN" <<'PY'
import json, sys, pathlib
d = pathlib.Path(sys.argv[1])
for line in (d / "ledger.jsonl").read_text().splitlines():
    e = json.loads(line)
    print(f"{e['seq']:>3} {e['kind']:<18} prev={e['prev_entry_sha256'][:12]}")
PY
```

**What a fresh session will get wrong**

1. **The tools arm runs OUTSIDE `round_cycle.py`.** Its `PARTIES` table has five entries and the
   local one routes to `solicit_local.py`, a single-shot chat completion with no tools — which is
   why rounds 007 and 008 ran routed-only. `tools/solicit_tools.py` is the driver, on the
   `round-NNN-chat` precedent: its own round id, its own prompt (the party is told what tools it
   has, appended and hashed separately so a reader can subtract it), never pooled with `qwen`.
   **It has not been run.** It still needs a spec file for the tools party, and the prompt bytes
   it would freeze are worth the custodian's eye before a permanent artifact is written.
2. **The arm is `workspace-write`, not `read-only`.** Codex grants network only in that mode. The
   requirement that matters — the party cannot write to the record — holds via an empty
   `writable_roots` and a scratch cwd, and `arm_acceptance.py` proves it. The scope doc carries
   the amendment.
3. **Do not set `--reasoning_parser` on the inference server.** It breaks every
   `enable_thinking:false` caller on that host. The shim splits reasoning client-side instead.
   `--tool_parser qwen3_coder` is required and costs nothing measurable.
4. **MCP tool calls cannot be approved in `codex exec`.** The only workaround disables the
   sandbox, which is the thing the gate exists to prove. That trade was declined.

**Standing:** the arm can read the record, cannot write to it, and can fetch a named URL — the
capability the whole arm exists to provide, and the one no party has ever had.
