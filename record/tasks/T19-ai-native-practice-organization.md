# T-19 · Organize the AI-native practice standard, with OAGF as its first implementation

> **Renumbered from T-18 at merge, 2026-08-06 — and caught by a control, not by a human.**
> Two sessions filed a T-18 the same day: the Innovation Record (committed 11:52, cited in
> `HANDOFF.md`) and this one. That is **D-32** in the task namespace, which is precisely the
> namespace `check_register.py` R5 was extended to cover after the D-29 collision.
>
> The session renumbering here was one of the two parties to that original collision. The control
> written in response to its mistake then caught the same session repeating the mistake in a
> different namespace, at merge, before either identifier was published. Recorded rather than
> quietly renamed, because the entry is more useful than the fix.

**Unassigned** · branch TBD · no GPU except for §4 · status: open

Turn `record/designs/ai-native-development-practice-draft.md` from a draft into a standard the
repository actually runs against, and organize the repository so that a reader — human or agent —
can see whether it complies.

**Depends on:** the draft (`ec2e838`, sharpened `3e05c66`). **Read that first.** Its eleven
requirements are each derived from a defect observed here on 2026-08-06; do not re-derive them.

---

## 1. The conflict, named before anything is built

The custodian's framing is **"OAGF as the aspiring reference implementation."** That phrasing runs
directly into this repository's own rules, and the collision should be resolved mechanically rather
than left in the adjective.

- `README.md`: *"Consullo is designated **a** first implementer — never *the* reference
  implementation."*
- ICP: *"An implementer may never promote its own contribution above Level 1, declare its own
  implementation conformant, or design the adversarial evaluation applied to its own mechanism."*
- ICP §3.1 records that all six separable roles held by one party is **a defect rather than a
  design.**

A practice standard authored here, implemented here, evaluated here and published here reproduces
exactly that structure — this time for the standard that is supposed to prevent it.

**Required resolution: give the standard its own promotion ladder, and cap this repository at the
bottom of it.**

| Level | Meaning |
|---|---|
| **L1 — self-implemented** | The author's own repository conforms, self-reported. **OAGF may never exceed this.** |
| **L2 — independently implemented** | A party unaffiliated with the author implements the standard from its text alone, without asking the author what it meant. |
| **L3 — independently evaluated** | Someone other than the author designs and runs the conformance evaluation. |
| **L4 — collectively ratified** | Structurally unreachable. No ratification procedure exists (D-16). |

"Aspiring" then means something checkable: **L1, aspiring to L2.** Write that on the standard, not
in a conversation.

## 2. Where the standard lives

Currently `record/designs/`, deliberately, because naming a fourth protocol alongside ASP/ICP/QCP
asserts standing and is the act D-16 was filed about. **A custodian decision, not a session's:**

- promote to `spec/<name>/` with a name, or
- keep it in `record/designs/` until an independent party implements it, which is the more honest
  option and costs nothing.

## 3. Organize the repository against the standard

### 3.1 Settle what a "project" is

The custodian's proposal is a `docs/` description per project. This repository is not obviously
several projects, so the unit must be decided before descriptions are written. Proposed split by
**role**, with sizes measured:

| Project | Files | ~tokens |
|---|---|---|
| maintenance path (integrity) | `rebuild`, `build_manifest`, `validate_provenance`, `check_register` | 11,081 |
| site generation | `build_viewer`, `build_register_view`, `build_local_rounds`, `render_markdown`, `build_bundle` | 23,501 |
| capture path | `capture_response` (+ Track B's `capture_gates`, `capture_lifecycle`, `ingest_capture`) | 3,168 |
| solicitation harness | `solicit_local`, `code_freetext`, `analyze_concurrence` | 5,833 |
| session record | `build_session_log`, `author_deficiency_census` | 14,708 |
| tests | `test_integrity` | 2,964 |

Note "site generation" already exceeds a 24,576-token window when described *and* read. Descriptions
must be sized so a description plus its subject fits the smallest agent that must read them, per §10
of the draft.

### 3.2 Per-project descriptions — §3 of the draft

Each project gets a description whose **facts have exactly one authoritative realization**, with the
other form generated or compared. Fenced when the document is the product; sidecar when the build
validates it; any extraction step carries its own tests.

Required contents: what it is, what it refuses to do, what it costs, which claims it enforces and at
**which assurance level** (L0 asserted / L1 bound / L2 invoked / L3 adversarially proven), its
inputs and outputs, and the input digest it was generated from.

### 3.3 Per-file review directories — §2 of the draft

`review/<path-to-source>/<utc>-<reviewer-slug>.json`, schema-validated, with `findings: []`
**required rather than optional**, each review bound to the SHA-256 of the file content it reviewed,
`self_review` and `independent_review` distinguished, and non-reproducing findings published beside
reproducing ones.

**Open, and it decides the size of the job:** retroactive over the 16 existing tools, or forward-only?
Retroactive means 16 review directories and an independent reviewer for each.

### 3.4 A conformance report

A generated page stating, per requirement and per project, which assurance level has actually been
reached. **It must be capable of reporting non-compliance**, or it is decoration — the repository's
own register currently shows exactly **1** validated forward control out of 30 entries, and a
conformance report that could not produce a number like that would be worthless.

---

## 4. The frontier-model question, and the trap in it

The custodian's observation: *frontier models can offer ideas about what repository organization
would best suit them — e.g. lowest prefill/thinking tokens expended.*

The idea is good and the direct form of the question is **not answerable by asking.**

### 4.1 Why asking is the wrong instrument

*"What layout minimizes your prefill and thinking tokens?"* asks a model to introspect on its own
processing and report the result. That is **D-24 exactly** — self-reported categorical fields
disagreed with the same response's free text in every arm, and the forward requirement adopted from
it was: **do not ask a model to classify its own reasoning.** A model's *belief* about what
minimises its prefill is not evidence about what minimises its prefill.

Two further hazards apply:

- **D-23.** A prompt that describes OAGF's current layout while asking what layout is best has
  encoded the answer. Any such arm must supply the task without supplying the incumbent design, or
  disclose that it did not.
- **D-11.** Four frontier models converging on repository-layout advice is close to a pure test of
  shared prior — this is exactly the material their training corpora are saturated with. Agreement
  here is weaker evidence than agreement anywhere else in this corpus.

### 4.2 It is directly measurable, and the outcome variable is already captured

`corpus/raw/local-round-*/…-samples.json` already records per sample:

```json
"usage": { "prompt_tokens": 694, "completion_tokens": 196, "total_tokens": 890,
           "prompt_tokens_details": { "cached_tokens": 0 } }
```

Prefill, completion **and prefix-cache hits**, on a host the operator controls, at k = 20. The
quantity the question is about is already in the record.

Note `cached_tokens: 0` throughout. Whether a layout that puts a stable preamble first and variable
content last actually earns cache hits is **an empirical question this corpus can answer and has
never asked.**

### 4.3 The design that follows

**Arm A — hypotheses, from the frontier parties.** Ask for *proposals*, not preferences: "given this
task and these constraints, propose repository organizations and say what each would reduce and how
you would test it." Their value is generating layouts nobody here thought of. Record as k = 1
artifacts, citable as proposals, **not** as evidence about what any model finds efficient.

**Arm B — measurement, on the local host.** Take the same fixed task, realize the material under each
proposed layout, run at k ≥ 20, and compare `prompt_tokens`, `completion_tokens` and `cached_tokens`.
This is the arm that answers the question.

**Pre-register before Arm B runs** (ICP §5), with a resolution criterion and a stated resolution
limit. Candidate: *no layout reduces mean total tokens by more than the run-to-run variation measured
on a repeated identical condition.* Given D-28's 0.4649-bit noise floor, **a test-retest arm is
mandatory** — completion tokens above already range 109–319 on an identical prompt, so a layout
effect smaller than that spread is not an effect.

**What Arm B cannot show:** that a result on a 35B locally-served model transfers to frontier models
on different serving stacks. State that as a limit rather than discovering it later.

### 4.4 The asset nobody has used

Every raw artifact here is hash-anchored. An agent that recorded *"I read `deficiencies.md` at hash
X"* can skip re-reading when the hash is unchanged — a prefill saving **available only to a
repository that publishes content hashes beside content**, which §10 of the draft already requires
for verifiability. Worth testing as one of Arm B's layouts, and it is a claim to OAGF's distinctness
that rests on a mechanism rather than on an aspiration.

---

## Acceptance

- The standard carries a promotion ladder, and **this repository is marked L1 with the reason.**
- Every project has a description with one authoritative realization per fact, and a mechanical
  staleness signal.
- The review-directory convention exists, is schema-validated, and records null findings.
- A conformance report is generated, and **demonstrably able to report non-compliance.**
- Arm A and Arm B are separated, Arm B is pre-registered with a test-retest arm, and no claim about
  token efficiency rests on a model's self-report.

## Territory

Cross-cutting; needs custodian routing. §3.3 touches every track's files. §4 Arm B needs Track C's
exclusive inference host. §4 Arm A needs the custodian to reach the frontier parties.

## Conflict of interest

Drafted by Claude Code (Anthropic), which authored the draft standard, wrote most of the code it
would be applied to, and introduced several of the defects the standard is derived from. **The author
of the standard, the implementation, the evaluation and this task is one party.** That is the
condition ICP §3.1 calls a defect, and no part of this task removes it — §1's ladder only makes it
visible and caps what may be claimed while it holds.
