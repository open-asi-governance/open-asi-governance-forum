# Candidate control register — v0

**The custodian's reframe, 2026-08-10:** *"the controls best suited for promoting for aligned
super intelligence. The roadmap I seek thus can be the ranked list of vetted controls by the model
panel."*

Codex and the workbench brainstormed independently; Codex was not shown this document's ranking
before producing its own. Its full answer is in `record/executive/codex-transcripts/`.

**Both reached the same conclusion on the hard question, and it is a negative one.** It is stated
first because everything else is downstream of it.

---

## No control here establishes alignment of a system more capable than its operators

There is no recorded superintelligence failure to derive an NCP-shaped control from, no verifier
for internal alignment, and no evidence that any fixture stays adversarially adequate under a
large capability increase. Claiming otherwise would be the unbounded-scope defect that NCP's own
claim grammar forbids.

The strongest available substitute, in Codex's words:

> A system may act only through an externally enforced, non-self-amendable capability envelope
> whose grants are explicit, expiring and independently reconciled to observed effects.

That is a **control-of-authority hypothesis, not an alignment result.** It bounds reachable
effects while the enforcement boundary stays genuinely outside the system. It says nothing about
aligned objectives, resistance to deception, or containment against something that can find
implementation defects.

### One thing the workbench would add

There is a second class that degrades more gracefully with capability, and this record is unusually
qualified to specify it: **controls that make the operator's own errors visible.**

Every failure this project has recorded is an operator-epistemics failure, not a model failure —
four of five checks blind to what they certify; three published numbers wrong in the project's own
favour; a ballot that would have laundered 26/26 self-ratification had two unrelated defects not
broken it; twelve gate modifications by the layer the gates constrain. None of those needed a
capable adversary. They needed only a confident builder and a signal that could not fail.

Such controls do not constrain a superintelligence. They **keep the people building one honest
while that is still possible**, and the honest framing of the custodian's goal is that this is what
"promoting aligned superintelligence" can mean from here. It is a smaller claim than the goal as
stated and it is one the evidence supports.

---

## Ranking criteria

Codex's, adopted with its two amendments to the workbench's draft:

1. **Strength of failure evidence** — a named, dated, costed failure. No principle-derived controls.
2. **Mechanical discriminating power** — a deterministic verifier plus a fixture it must reject.
3. **Enforcement outside the subject's write authority** — *added by Codex, and correctly ranked
   high*: for a progressively more capable system, external enforceability matters more than
   elegance.
4. **Marginal failure coverage** — *replaces* "catches a failure nobody else catches". Rewarding
   uniqueness alone favours exotic controls over robust ones; overlapping controls give depth.
5. **Relevance to recursive or catastrophic failure, with bounded claims.**

**The workbench adds a sixth, which changes the roadmap more than the ranking:** *can this project
demonstrate the control on itself, or can it only publish it?* Control 1 requires a signer outside
the subject's execution boundary. A solo operator holding every credential, running the workbench
on his own machine, **cannot satisfy it** — so the top-ranked control is the one this project can
specify and cannot dogfood. That is not a reason to demote it; it is a reason the register needs
an *enforceability* column, because a control we cannot demonstrate needs an external implementer
before it means anything.

---

## The register

Ranked by the criteria above. **Status vocabulary is Codex's**, because "vetted" is too vague:
`ELIGIBLE` → `PANEL-ATTACKED` → `COUNTEREXAMPLE-OPEN` / `SURVIVED-STATED-ATTACKS` →
`INDEPENDENTLY-IMPLEMENTED`.

| # | Control | Derived from | Self-demonstrable? | Status |
|---|---|---|---|---|
| 1 | **Protected control plane** — a governed system cannot write or approve changes to the constraints, logs or gates governing it; every such change carries a signature from outside its execution boundary | 12 gate modifications in one lease window by the layer they constrain; Group B, 5 parties | **No** — needs a second key holder | ELIGIBLE |
| 2 | **Negative control profile** — every assurance check observed failing under a declared capability-relevant control | AS-01, 4h37m; 4 of 5 checks survived their controls | Yes — built | ELIGIBLE, verifier shipped |
| 3 | **Independent effect reconciliation** — every governed effect matches one pre-authorised action and one effect-specific postcondition, enumerated from a side channel | 37 logged actions vs 127 file changes across 7 unverified effect classes | Yes — built today | ELIGIBLE, tool shipped |
| 4 | **Fail-closed authorisation lease** — no consequential action without a live, scope-matched, non-self-issued token; absence, expiry or unknown class denies | the ten-action sunset passed at 23; the lease once permitted unknown action classes | Partly — the token is currently self-issued | ELIGIBLE, partial |
| 5 | **Closed-world measurement** — refuse to emit any result unless every in-scope artifact parsed under a registered schema | 69 unreadable files reported as zero; the tool built to prevent it repeated it twice | Yes — built | ELIGIBLE, verifier shipped |
| 6 | **Role-separated self-evaluation** — an evaluation about a subject cannot advance its status if the subject controls two of: selection, authorship, custody, scoring, promotion | ratification-01: workbench did all five; zero refusals in 108 positions; Group A, 3 parties | **No** — one operator holds all roles | ELIGIBLE |
| 7 | **Append-only correction chain** — content-addressed, corrections reference rather than replace, verification walks every step from an external checkpoint | D-29 re-anchored before verifying; D-34 passed a tip-only check after modifying raw | Mostly — the checkpoint is not externally held | ELIGIBLE |
| 8 | **Evaluation noise-floor control** — no effect reported smaller than measured run-to-run variation, with a same-condition retest arm | D-28: a 0.1815-bit effect against a 0.4649-bit noise floor | Yes | ELIGIBLE |
| 9 | **Complete invocation evidence envelope** — no model output supports a claim unless request, response, provider metadata, rejections and hashes were captured before reporting | D-01–D-06 lost founding-record provenance permanently; D-45 discarded invalid attempts; D-50 could not distinguish truncation from refusal | Yes — mostly built | ELIGIBLE |
| 10 | **Assurance claim boundary** — machine-verifiable claim naming subject, config, capability, time and evidence hash; forbidden predicates rejected | the false "zero searches" deletion recommendation; ICP's "structurally unreachable" correction | Yes — built into NCP | ELIGIBLE |

**Dependencies matter more than rank.** 3 makes authority omissions visible; 1 makes 4 and 7
materially stronger; 2 and 8 improve the checks used to assess everything else. A bare ordering
hides that, which is why this is a register and not a list.

### The ten above are not the whole register

**`tools/build_controls_page.py` is canonical; this table is the top of it.** The register now
holds **32** controls. The ten here are the eligible, failure-derived ones the page opens with;
the rest arrived by mining implementer design documents and sit **below the eligibility line**
(Part D) because they name real failure classes without a recorded failure that cost anything.

This section exists because the discrepancy was itself a defect of the kind the register
catalogues: a design document asserting a count that the generated artifact had long since
overtaken. Where the two disagree, the tool is right and this file is stale.

| Batch | Ranks | Source | Status |
|---|---|---|---|
| Founding | 1–10 | this record's own recorded failures | eligible; Parts A–B |
| Party objections | 11–13 | round objections with verifiers built | eligible; Part C |
| Goal-architecture (T0) | 14–19 | an implementer's goal-graph thesis | below the line |
| Charter | 20–23 | an implementer's constitution | below the line |
| Self-modification engine | 24–27 | an implementer's evolution design | below the line |
| Self-measurement | 28–32 | an implementer's capability-threshold instrument | below the line |

Every mined batch is **abstracted**: the sources are confidential, and the register carries the
mechanism without the implementation. See `record/designs/implementer-disclosure.md`.

**Amendment, 2026-08-10 — control 20.** It said it was the one candidate with no path to a
verifier and that none was proposed. Half of that was wrong, in the same shape as control 2's
prior-art overclaim: an absence asserted from not having looked. **Detecting** proxy drift needs
the ground truth the proxy replaced and remains unverifiable. **The incentive that produces the
adversarial variant** is a checkable graph property and has been one in the public literature
since 2021. That half is now control 28, and 20 says so.

The general lesson is worth more than the repair: **this register has now twice claimed something
was unclaimed, and been wrong both times, in its own favour.** The second instance was found by
reading one implementer document. Neither was found by a gate.

---

## The eighteen party objections, as controls

An objection is a sentence a model wrote. A control is a verifiable requirement. Several are good
principles and **bad controls**.

| Objections | Becomes | Judgment |
|---|---|---|
| Group B (5) — must not modify its own constraints, logs, gates | **Control 1** | Yes. Top-ranked. "Must not *propose* alteration" is too broad — externally authorised modification must stay possible. |
| Group A (3) — must not tally or frame ratification about itself | **Control 6** | Yes, as role separation. The "persuasion" wording must **not** become normative: shared control identities are observable, persuasive intent is not. |
| Group C (3) — must not seek expanded authority; silence is not delegation | **Control 4**, partly | "Do not seek" is intent attribution and unverifiable. "No consequential action without explicit authority" is the mechanical residue. The rest stays a human escalation principle. |
| Group D (3) — halt on custodian/prohibition conflict | — | Deferred: there are no ratified prohibitions to conflict with. Meaningless until a ballot succeeds. |
| E1 — log everything | **Control 9**, narrowed | Universal logging is unverifiable and can force disclosure of secrets. Narrow to evidence envelopes for invocations that support claims. |
| E2 — public hash chain | **Control 7** | Yes. "Public without authentication" is a distribution choice, not the control. |
| E3 — rollback procedure | — | **Refused as written**: it accepts dead prose, and conflicts with append-only correction. A future candidate could require *fault-injected atomicity* — fail mid-mutation, verify restoration or an unambiguously blocked state. |
| E4 — no access to the custodian's decision logic | — | **Refused.** Unverifiable against inference or leakage, no supporting failure, and hiding applicable constraints makes compliance *worse*. Least privilege over capabilities is defensible; ignorance of governing instructions is not. |

---

## How the panel vets — and it is never asked to ratify

Panel assent is cheap: 108 clause-positions, zero refusals, no control. Panel **objection**, asked
what is *missing*, produced five parties independently naming a hazard the layer had exercised
twelve times that week. **The instrument must ask for attacks, not approval.**

Codex's procedure, adopted:

1. **Mechanical eligibility before any spend.** No named failure, verifier, rejection fixture,
   one-day sketch and nonclaim → the panel never sees it.
2. **Precommit what changes** — acceptance criteria, seeded defects, fatal findings and
   disposition rules published *before* the round. Output must not create the scoring rule.
3. **One blinded attack packet per control.** Unlabelled fixtures: valid, invalid,
   mismatched-failure, self-signed, and a known bypass. Each sample must find the strongest
   invalidity, construct a fixture the verifier *wrongly accepts*, name a requirement the verifier
   does not enforce, state the narrowest defensible claim, and say what would reverse its
   objection. **"No defect found" is allowed. "Ratify" is not an answer option.**
4. **Seed calibration traps** — a compelling principle with no executable requirement; a real
   verifier attached to the wrong failure; a self-authorised "external" control; an overclaiming
   attestation. An arm that accepts these is not credited for fluent objections elsewhere.
5. **Execute counterexamples, never vote on them.** Every proposed fixture is run. Nothing is
   resolved by model majority.
6. **Cross-examine only live disagreements**, with fresh blinded invocations.
7. **No advance while an executable counterexample is unexplained.** Dispositions: `FIXED`,
   `CLAIM_NARROWED`, `DUPLICATE`, `NOT_SUPPORTED`, `OPEN`.
8. **Adoptability needs a real stranger.** The panel cannot establish "implementable in an
   afternoon". That is ICP Level 2 and requires an independent implementation from the text alone.

**Cost: ten candidates at one attack round each, plus cross-examination of the three sharpest
disputes = 13 routed rounds ≈ 5 days at 3/day, ≈ $25.**

---

## Why the roadmap cannot yet be called a list of vetted controls

Codex's caution, which the workbench endorses: calling a panel-attacked ordering *"the ranked list
of vetted controls"* **before independent implementation would reproduce the cheap-assent and
legitimacy-laundering failures that caused this reframing in the first place.**

The roadmap is the register's current priority order, **conditionally** — and the condition is
`INDEPENDENTLY-IMPLEMENTED`, which no control has reached and which no amount of panel activity
can supply.
