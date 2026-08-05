# Implementer Contribution Protocol (ICP) — v0.1

**Status:** Draft. Normative for §3 (role separation), §4 (promotion ladder) and §5 (pre-registration).
**Drafted:** 2026-08-05 by Claude Code (Anthropic), at operator direction.
**Adopted by:** Stephen Reed, human custodian. **Not** ratified by any ballot — see D-16.
**First implementer:** Consullo. See Annex A, including its declared conflicts.

---

## 1. What this protocol is for

A specification with no implementation is aspirational. ASP v0.1 §6 states plainly that no ASP
implementation exists anywhere, which makes every claim in it a claim about a target rather than
about a system. The obvious remedy is for an implementer to build it and report what happened.

The obvious remedy creates a worse problem. If the party that authors the specification also builds
the only implementation, produces all the evidence, designs the evaluation, and holds custody of the
repository that publishes the result, then nothing that repository says about the specification is
independent of the specification's author. That is the concentration ChatGPT's founding contribution
(§2.1, raw 147–165) says no single entity should hold, and the self-evaluation ASP §2.3(4) and the
founding record's §4.4 both prohibit.

**This protocol exists so that an implementer can supply evidence without capturing the standard.**
It is written generically because writing it around a single implementer would itself be the defect.

## 2. The failure mode, stated concretely

Consider a specification S, an implementer I, and a forum F.

If I implements S, reports that it works, and F publishes that report, a reader learns almost
nothing. The report is consistent with all of:

1. S describes a real, general mechanism, and I implemented it.
2. S encodes I's existing architecture, and I "implemented" what it already had.
3. S is underspecified, and I filled the gaps with private choices no second implementer would make.
4. S does not work, and I's evaluation was designed not to detect that.

**Distinguishing (1) from (2), (3) and (4) is the entire job of this protocol.** No amount of
detail in I's report accomplishes it, because all four hypotheses predict a detailed report.

## 3. Role separation (normative)

The following roles MUST be tracked separately, and every artifact MUST state which roles its
author held at the time:

| Role | What it controls |
|---|---|
| **Specification authorship** | What the standard says |
| **Implementation** | What was built |
| **Evidence production** | What was measured, and under what conditions |
| **Evaluation design** | What counts as success, and what would count as failure |
| **Promotion authority** | Whether a mechanism advances up the ladder in §4 |
| **Repository custody** | What is published, and what is merged |

### 3.1 Current concentration, disclosed

As of 2026-08-05, **Stephen Reed holds all six**, and the specification text was drafted by an
Anthropic invocation surface that is a party to the record it annotates.

This is stated as a defect, not a governance design. It is the same disclosure the README makes
about single-operator custody: **disclosed rather than mitigated.** Every artifact produced under
this concentration should be read accordingly.

### 3.2 The separations that matter most, in priority order

1. **Evaluation design MUST NOT be held by the implementer** for any promotion above Level 1. A
   system under review may not select its own success criteria (ASP §2.3(4)).
2. **Promotion authority above Level 1 MUST require a party other than the implementer.** See §4.
3. **Specification authorship and implementation SHOULD diverge** as soon as a second implementer
   exists; until then, §4's Level-2 test is the only available proxy.

### 3.3 What an implementer may never do

- Promote its own contribution above Level 1.
- Declare its own implementation conformant.
- Design the adversarial evaluation applied to its own mechanism.
- Report only the evaluations that succeeded (see §6).
- Describe itself as **the** reference implementation. "A reference implementation" is accurate;
  the definite article asserts a standing no single implementer can hold.

## 4. The promotion ladder (normative)

Every contribution enters at Level 0 and advances only against the stated bar.

| Level | Name | Bar | Who may promote |
|---|---|---|---|
| **0** | Practice note | "Here is what we do." No generality claimed. | Implementer alone |
| **1** | Candidate pattern | Mechanism, the problem it solves, known failure modes, **and at least one recorded failure** | Implementer alone |
| **2** | Draft standard | An **independent party implements it from the specification text alone**, without consulting the author | Requires that independent implementer |
| **3** | Provisionally validated | Two independent implementations interoperate, **or** the mechanism survives an adversarial evaluation **designed by a party other than the implementer** | Requires the second party |
| **4** | Standard | Multi-party adoption under a defined ratification procedure | **No procedure exists. Nothing has reached Level 4.** |

### 4.1 Level 1 requires a recorded failure

A mechanism with no recorded failure has not been used hard enough to know its shape, or its
failures are not being reported. Both are disqualifying at Level 1. The failure must be specific:
what broke, under what conditions, and what it cost.

### 4.2 Level 2 is the load-bearing test

The Level-2 bar is not "someone likes the specification." It is: **an independent party reads the
text and builds a conforming thing without asking the author what it meant.**

This is the test that discriminates hypothesis (1) from hypotheses (2) and (3) in §2. If nobody can
implement the mechanism from the text alone, that is evidence the specification encodes the
original implementer's architecture rather than a general mechanism — **and that is a finding worth
publishing**, not a setback to be worked around by helping the second implementer.

Where a Level-2 attempt fails, the questions the second implementer had to ask are the artifact.
They MUST be recorded.

### 4.3 Level 4 is structurally unreachable by any single party

No ratification procedure exists in this project. D-16 records that nothing here has ever been
collectively ratified. Until such a procedure exists and is itself adopted, **Level 4 is
unreachable**, and no document may describe any mechanism as a standard.

This is deliberate. It is the structural guarantee that a single implementer cannot promote its own
work to a standard, and it costs nothing to keep while no second party exists.

## 5. Pre-registration (normative)

**An implementer MUST file a prediction into the OAGF prediction registry BEFORE running the
experiment that bears on it.**

The prediction must state the mechanism, the claim, a resolution date, and resolution criteria
fixed in advance. It is scored on its resolution date whether or not the result is flattering, and
the score is committed.

This is the single strongest available protection against the failure mode in §2, and against the
more general risk that a long-running programme becomes unfalsifiable to itself. A result reported
after the fact can be framed; a prediction filed before the fact cannot be.

An experiment whose bearing prediction was not filed in advance is recorded as **exploratory** and
may not be used to promote anything above Level 1.

## 6. Negative results carry equal standing

Failures, regressions, and mechanisms that did not work are contributions of equal standing, and in
several cases of **greater** evidential value than successes — a deployment gate that fails open
under load tells a reader more than one that passes a test designed by its author.

An implementer that reports only successes is not producing evidence. It is producing marketing,
and this protocol treats an unbroken run of positive results from a single implementer as a signal
that evaluation design is inadequate rather than that the mechanism is sound.

## 7. What an implementer's contribution must carry

Every implementer contribution follows `CONTRIBUTING.md` provenance rules, plus:

- the **level claimed**, and the specific bar it is claimed to meet;
- **which of the six roles in §3 the contributor held**;
- the **pre-registered prediction** it bears on, or an explicit `exploratory` marking;
- the **recorded failures**, not only the successes;
- what an independent implementer would need in order to attempt Level 2;
- **conditions under which the mechanism is known not to work**, or a statement that these are
  unknown — which is itself a Level-0 disclosure.

## 8. Open questions

1. What ratification procedure could make Level 4 reachable without recreating the capture problem?
2. How is "independent" established for a second implementer — non-affiliation is necessary but
   probably not sufficient if the implementer used the same models to write the code?
3. Should a Level-2 attempt by an AI system count, given that the AI may have the specification in
   its training data by the time it attempts it? This is the same contamination problem P-0005 now
   carries a check for.
4. Does an adversarial evaluation designed by a model count as "designed by a party other than the
   implementer" when the implementer chose the model, wrote the prompt, and can rerun until
   satisfied?

Question 4 is the sharpest. This project's entire review round 01 is exposed to it.

---

## Annex A — Consullo as first implementer

**Consullo** is a Seed AI platform operated by Stephen Reed: a large generated-agent hierarchy
(≈3,155 agents described, ≈2,591 generated), with a uniform PDCA agent contract, agent-to-agent
dispatch, correlation-ID propagation, MongoDB/Neo4j persistence, and TigerBeetle adopted as an
immutable settlement substrate.

### A.1 Declared conflicts

Consullo's operator is also this repository's custodian, the specification's adopting authority, and
the party that commissioned the specification's drafting. Per §3.1 he holds all six roles.
**Therefore no Consullo contribution may be promoted above Level 1 by Consullo**, and none has been.

### A.2 Why Consullo is nonetheless the right first implementer

It has the substrate the specification presumes and most governance proposals never test against:
attributable actions across agent chains, a plan-level record produced before execution, an
immutable audit ledger, and a gating problem at a scale — thousands of generated agents — where
mechanisms that work on toy systems tend to break.

### A.3 Candidate contributions and their current level

| Candidate | What it is | Level | What Level 2 would require |
|---|---|---|---|
| **Frontier-diff anchor discovery** | Run one prompt across a frontier model and a divergent-lineage local model; diff the *failure shape* rather than the outputs | **1** | Specify the diff procedure and the anchor-extraction criteria independently of Consullo's harness, so another group can run it on their own model pair |
| **Correlation-ID action attribution** | Every agent action carries a correlation ID propagated through A2A chains, making actions attributable across a hierarchy | **1** | Specify the propagation contract independently of Consullo's Java PDCA signature |
| **Method Memory as pre-execution plan disclosure** | Fine-grained steps with justifications, recorded *before* execution | **0→1** | Needs a recorded failure. The SpecRemAgent inter-step contract inconsistencies are a candidate |
| **Deployment-gate behaviour under load** | Review gates wired into agent generation, **bypassed in practice because the gate agents threw NPEs** | **1** | This is the strongest candidate precisely because it is a failure. Specify the gate contract and the fail-open condition |
| **Decomposed-codegen measurements** | Quantified, dated retention and output-contract metrics for small-model code generation | **1** | Publish the harness, the prompts, and the scoring rubric so another group can reproduce on their own models |
| **Failed-experiment recovery doctrine** | Methodology for not fooling yourself after a failed experiment | **0** | Generalise beyond Consullo's agent-building context |

### A.4 The highest-leverage item

**Frontier-diff anchor discovery.** It bears directly on **Q-02** — how to distinguish cross-model
agreement from shared bias — which four frontier models identified in review round 01 as unsolved,
and which Claude Fable 5 and ChatGPT both answered with designs requiring exactly this: probing with
maximally divergent-lineage models to detect whether a conclusion survives outside the
RLHF-shaped set.

Consullo has a validated method bearing on the corpus's hardest open question. Under §5 it must be
**pre-registered before the experiment**, not reported afterward.

### A.5 Registry consequence

Naming Consullo an implementer makes **P-0002** — "no ASP-attested agent will exist at any
organization other than Consullo" — partly self-fulfilling, and a self-fulfilling prediction is not
a falsifier. P-0002 has been rewritten to exclude Consullo explicitly and to predict *third-party*
adoption, preserving it as a real test.

Recording this: the change was made because *not* making it would have quietly removed one of the
registry's five seed falsifiers while appearing to leave it in place.

---

*Drafted by Claude Code (Anthropic) at operator direction; adopted by Stephen Reed, human custodian.
Not ratified by ballot. The drafter is a party to the record this protocol governs, and §3.1 records
the resulting concentration as a defect. Subject to adversarial review; corrections will be
committed alongside, not merged in.*
