# T-18 — An ongoing, linked record of innovations produced by building this forum

**Status:** open, unclaimed
**Owner:** unassigned
**Depends on:** `discussions=write` on `GH_TOKEN_OAGF` for the forum surface; nothing for the
committed artifact, which can be built first and should be.

---

## 1. What the custodian asked for

A standing forum topic that accumulates **innovations produced by the OAGF**, each with a linked
description. The typical entry is a **discovered solution to one of the many blocking issues that
arise during iterative design and build**, while exploring two things at once: the domain of
**counsel collaboration** (many models deliberating), and the **alignment-adjacent priority on data
and process provenance**.

That is a real category and this project is generating it faster than it is recording it. But the
obvious implementation of it is a mistake, and the reason is worth stating before any work starts.

## 2. The failure mode this task must be designed against

**An innovation register is a bragging surface.** It is the mirror image of
`corpus/deficiencies.md`, and it inherits the opposite bias. The deficiency register is credible
precisely because filing an entry costs the filer something; an innovations list costs nothing and
selects for whatever looks like a win. A corpus whose entire claim to seriousness is its self-audit
can lose that claim by publishing a parallel document with no adverse-evidence pressure.

Three concrete ways it goes wrong:

1. **Practices published as discoveries.** Most of what this project has "found" is ordinary
   engineering hygiene that it failed to apply and then applied. Calling that an innovation is a
   category error that a reader outside the project will catch immediately.
2. **Solutions with no evidence they work.** A repair described in a commit message is a claim.
   This repository already has the answer to that — a repair a build re-runs is a control — and the
   innovation register must inherit it rather than restate it.
3. **A fifth serial namespace.** D-32 was filed today because `D-NN` had no allocation procedure and
   two sessions collided. Minting `I-NN` without one repeats it, and D-32's forward requirement 4
   already names predictions, tasks and questions as carrying the same hole.

## 3. The design that avoids all three

**Do not build a new register. Use the ladder that already exists.**

`spec/icp/icp-v0.1.md` §4 defines exactly this object: Level 0 practice note → Level 1 candidate
pattern → Level 2 draft standard → Level 3 provisionally validated → Level 4 standard. An
"innovation" is a **Level 0 or Level 1 ICP entry**, and the forum topic is its *public surface*, not
a competing record.

This buys three things at once:

- **§4.1 already requires a recorded failure for Level 1.** So an innovation cannot be promoted past
  a practice note without naming what broke. That is the adverse-evidence pressure the register would
  otherwise lack, and it is already normative.
- **§4.2 makes Level 2 the load-bearing test** — an independent party implements it from the text
  alone. So "is this a general mechanism or just our architecture?" has a defined answer rather than
  an assertion.
- **No new namespace.** Entries are cited by the deficiency they came from.

### 3.1 Normative shape of an entry

Every entry MUST carry:

| Field | Why |
|---|---|
| **The blocking issue** | Cited as `D-NN` where one exists. An innovation with no recorded problem is a practice note at best, and says so |
| **The mechanism** | What was actually done, in enough detail to be implemented by someone else |
| **The evidence it works** | **A named regression case that fails without it.** Not a commit message |
| **ICP level** | L0 or L1 on entry. L2+ requires the independent implementer, per §4.2 |
| **Known limits** | What it does not do. Non-optional — every strong entry in this corpus carries one |
| **Transfer claim** | Whether it is asserted to generalise beyond this repository, and on what basis. Default: **none** |

An entry that cannot fill "evidence it works" with a test name is **not eligible**. That single rule
does most of the work, because it is checkable by a tool and it cannot be satisfied by writing well.

### 3.2 Where it lives

- **Committed artifact:** `record/innovations.md`, derived where possible rather than hand-authored —
  the regression-case names are already in `tools/test_integrity.py`, and a checker should verify
  every cited case exists. Build this **first**; it does not need any credential.
- **Forum surface:** a GitHub Discussion in a dedicated category, one thread per innovation, linking
  to the committed entry. Blocked on `discussions=write`.
- **Do not** put it on the published site as a feature list until at least one entry has reached
  ICP Level 2. Presentation must not outrun the record.

## 4. Seed candidates, with an honest grading

From this repository's own history. **Graded, because most of them are not innovations**, and a task
that starts by conceding that is more likely to produce a credible document.

| Candidate | Evidence | Honest grade |
|---|---|---|
| **Separate the verification signal from the availability signal** — CI's `verify` and `deploy` as distinct jobs, so an infrastructure outage cannot present as a failed integrity check | Six `failure` runs on 2026-08-06, five with `verify` cancelled at **0 steps executed**. Distinguishable only because the jobs are separate | **Strongest.** Generalises past CI to any governance system where an availability failure could be read as a compliance failure |
| **A byte-equality gate must be scoped to the generator set, not a directory** | D-33; the capture page moved out of `docs/` and would have silently left the gate | **Genuine.** Non-obvious, and it recurred within hours of being fixed |
| **A hash anchor over a tree does not establish that the tree is the one committed** | D-34, reproduced: edit raw material, `--force-rewrite`, commit — every check passes | **Genuine and the most transferable to provenance work generally** |
| **A check outside the runnable path cannot be verified to work** — hence logic in a tool, not in workflow YAML | D-33; and the reviewer's own draft put it in YAML | Strong practice note. Not novel outside this project |
| **Pair every bias probe with a framing-resistance control** | `spec/qcp/qcp-v0.1.md` §6 — a divergent-lineage probe deferred to emphatic assertion in the text it was judging, 17/20 samples holding two incompatible positions | **The best counsel-collaboration entry.** Directly about multi-model deliberation being informative |
| **A blind arm whose instruction contains the hypothesis is not blind** | D-23 | Ordinary experimental hygiene, applied late. **L0 at most** |
| **Serial identifiers need an allocation procedure under concurrent authorship** | D-32, with the collision reproduced | Real but small |

Two observations the task owner should not lose:

- **The three strongest candidates are all provenance mechanisms**, which is what the custodian
  predicted. That is mild evidence the priority is aimed correctly, and it is also exactly the area
  where this project is most likely to be reinventing something with a name in the literature.
- **Every candidate came from a defect.** Not one came from designing forward. That is itself the
  most interesting finding available here, and it belongs in the document's opening rather than
  being visible only to someone who reads the whole table.

## 5. Acceptance criteria

1. `record/innovations.md` exists, with every entry carrying all six fields of §3.1.
2. A checker verifies that **every cited regression case name actually exists** in the test suites,
   and fails the build otherwise. Same discipline as `check_register.py`; without it this document
   drifts exactly as the deficiency count did.
3. No entry claims a level above **L1** unless an independent implementer is named.
4. The document opens by stating what it is not: not a feature list, not evidence of generality, and
   authored by an interested party.
5. Prior art is checked for the three strongest candidates before any transfer claim is made. **A
   reinvention presented as a discovery is worse than silence**, and this project has no literature
   review behind any of them.
6. If a forum surface is created, each thread links to the committed entry and does not restate it —
   one record, one place.

## 6. Explicitly out of scope

- Promoting anything to ICP Level 2 or above. That requires an independent party, and the custodian
  cannot supply one by asking a model.
- Any claim that a mechanism here is novel **in the field**, absent the §5.5 prior-art check.
- Publishing to the site's front matter.
