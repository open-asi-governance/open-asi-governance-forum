# Session handoff

How work in this repository is divided between concurrent sessions, and what a fresh session must
read before it starts.

A session here is an agent instance with no memory of any other session. Everything it needs is in
the repository or it is lost. This file exists because that is a real constraint and not a
theoretical one.

---

## 1. Read this before doing anything

**`corpus/deficiencies.md`, entries D-23 through D-28.** Not optional, and not for background.

Six deficiencies were filed on 2026-08-06, all by the annotator against its own instruments, all
within a single day's work. They are not history — they are the accumulated knowledge of how to
build a measurement in this project that is not silently broken:

| | What it cost |
|---|---|
| **D-23** | A "blind" probe whose prompt contained the answer, flattering the annotator's own provider |
| **D-24** | A model asked to classify its own reasoning, disagreeing with its own free text a third of the time |
| **D-25** | A deterministic coder trusted without validation, wrong three separate ways, one of which scored 9/10 where the truth was 0/10 |
| **D-26** | Temperature treated as a fixed constant when it controls the quantity being measured |
| **D-27** | An enum whose values did not name their referent, so accurate answers landed on opposite labels |
| **D-28** | An apparatus never run twice, which turned out not to reproduce, voiding an already-published effect |

A session that skips these will rebuild a contaminated probe within its first hour. Every one of
them was found late, by reading free text after trusting a category.

Then read, in order: `README.md`, `GOVERNANCE.md`, `CONTRIBUTING.md`, and the specification your
task concerns.

## 2. Standing rules that bind every session

1. **The custodian merges.** `GOVERNANCE.md` §2 states that no AI system holds credentials and all
   writes pass through the human custodian. Sessions push a **branch**; Stephen Reed merges. A
   session that pushes to `main` has violated the document it is maintaining.
2. **Never commit over a red build.** `python3 tools/rebuild.py && git commit` as an `&&` chain, not
   as separate commands. This was violated twice on 2026-08-06, the second time after the lesson
   had been written into a commit message and not acted on.
3. **Design fixes with Codex before writing them.** Standing operator rule. Two deployed unreviewed
   fixes were actively harmful.
4. **Pre-register before running any measurement.** ICP §5. File the prediction with a resolution
   criterion and a stated resolution limit *before* the run. A result reported afterward can be
   framed.
5. **No LLM in the maintenance path.** `tools/` is deterministic. Generation tools
   (`solicit_local.py`) are labelled as such and are not part of the build.
6. **Raw material is immutable.** Corrections are superseding artifacts, never edits.

## 3. Resource claims — the part that causes real damage

| Resource | Rule |
|---|---|
| **The inference host** | **EXCLUSIVE.** One session at a time. It restarts services and drains the INEXPENSIVE pool. Two sessions here corrupt each other's measurements and can OOM the surviving pool host |
| **The OAGF repo** | Shared, but by branch. Pull before starting; never rebase another session's branch |
| **Codex** | Shared working tree is a known hazard. Run `codex exec` with `--sandbox read-only` and `-C` pointed at this repo |
| **The task list** | Claim a task by setting its owner before starting |

## 4. Assignment

Four independent tracks. Territories are disjoint by design; where they are not, the overlap is
named.

### Custodian actions no session can perform

These are blockers, not preferences. A session will hit them and stop.

| Action | Why a session cannot do it | Blocks |
|---|---|---|
| **Enable GitHub Pages** — Settings → Pages → Deploy from a branch → `main` → `/docs` | The org token holds `administration=write` but not `pages=write`; the API returns **403**. `docs/index.html` is built and committed, and the site is **404** until this is done | Track A |
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
