# Witnessed Control Challenge — how a system would be checked against the register, and why it is not called conformance

**Status: design, not adopted.** Nothing here is published as a procedure and nothing may be
claimed under it. Written 2026-08-10 after the custodian asked how the 63 controls would apply to
an implementer's code and documents, and asked that the answer be general rather than shaped to
the first subject.

Designed with Codex, which **rejected the workbench's proposal** and supplied the alternative
below. The workbench's four candidate designs and their disposition are recorded at the end,
because a design record that keeps only the surviving idea hides where the thinking was wrong.

---

## The recommendation, first

**Do not write "OAGF conformance v0."** Publishing a conformance procedure against this register
now would probably be **net-negative**, and the reasons are the register's own:

* producers would choose their own scope, and scope selection is one of control 6's five roles;
* public fixtures become implementation targets rather than tests (control 59);
* any state vocabulary becomes a league table within a week (control 57);
* the **50 below-line entries would be presented as equivalent to the 13 with incidents**;
* typed metadata gets mistaken for substantive validity (control 31);
* *"OAGF assessed"* becomes a euphemism for *"OAGF compliant"* (control 10);
* and passing suppresses the investigation that would have found something.

That is legitimacy laundering, which is the failure control 10 exists to prevent. **If anyone
asks for a badge or a procurement shortcut, the procedure must not be published under the name
"conformance"** — the shortcut dominates the caveats every time.

What can be built instead is narrower and produces real evidence.

## The object being evaluated is not "the system"

It is:

> subject configuration × observable claim × relying decision × time × control version

One test against that object is a **challenge episode**. A system never receives a status. A
challenger produces bounded observations of the form:

> For configuration X, at time T, under challenge C, mechanism M rejected perturbation P. Raw
> evidence: H. This does not establish safety, alignment, general compliance, or behaviour
> outside this configuration and challenge.

That is evidence. *"63 controls assessed"* is not.

## The protocol

**1. A relying party names a decision.** The external party — not the implementer — states a
concrete decision the evidence could change: allow network access, accept a measurement in a
report, promote a model-generated change, rely on a rollback claim, reduce monitoring. **If no
decision changes, this is diagnostic engineering, not assurance.** That single requirement strips
away most compliance theatre, and it is the thing the workbench's proposals were missing.

**2. Freeze the target.** Hash the deployment image, source revision, configuration and policies,
reachable effectors, design-corpus manifest, role and key declarations, control-register version,
time and expiry. A later change is a different target. **Evidence does not inherit** — which is
control 61 and control 32 applied to the assessment itself.

**3. Derive applicability from evidence, not from a questionnaire.** Each control needs an
applicability contract beyond its prose: a trigger predicate, admissible positive witness, a
structural refuter, discovery probes, configuration dependencies, and who bears which burden.

Scope is three-valued and the burden is asymmetric:

| state | what establishes it |
|---|---|
| `IN` | one credible positive witness. The producer may contest it; contesting does not move it |
| `OUT` | a **structural refuter** — not "we do not do that" |
| `UNRESOLVED` | neither. **Never coerced to `OUT`** |

*"Does not self-modify"* is not established by finding no method called `selfModify`. A refuter
must show the deployed identity lacks every write, replace and promotion path over its executable
and policy state within a stated boundary. *"Does not generate subgoals"* is defeated by any trace
of a generated task initiating action, whatever the local vocabulary calls it. *"Has no acceptance
gate"* is defeated by any mechanism whose output controls promotion, deployment or standing — even
one called a CI check.

Four sources feed it: producer declaration, independent static enumeration, runtime effect
enumeration **from a channel the subject does not write** (control 3), and probes aimed
specifically at declared `OUT` and `UNRESOLVED` triggers.

**4. The external challenger authors the challenge**, precommitting the target predicate, a
healthy observation, the perturbation, the expected refusal, what would make the result
indeterminate, the scoring rule, and **a negative control for the scoring machinery itself**. The
producer may supply an adapter; the producer does not choose the perturbation, and at least one
challenge is withheld until the target is frozen.

Organisational controls are runnable when decisions, roles and promotions are artifacts:

| control | the challenge is a transaction, not a malformed file |
|---|---|
| 6 | submit an evaluation with a prohibited role collision; promotion must refuse |
| 22 | submit an assent-seeking or same-author "review"; it must not count as outside-frame |
| 40 | submit a stop condition dated after the first result; the record must reject it |
| 56 | inject an objective conflict; the gate must route outward rather than resolve it |

**If an organisation cannot represent these as artifacts, the honest result is that the claimed
control has no observable enforcement surface** — which is itself the finding.

**5. Independent custody, bounded output.** The challenger or a separate custodian captures the
raw run. **The producer must not select which attempts enter the record** (control 9).

Outcomes are factual, and there is deliberately no `PASS`, no maturity level, no aggregate:

* `DETECTED` — the precommitted refusal occurred
* `ESCAPED` — the condition occurred without it
* `INDETERMINATE` — the evidence did not resolve the predicate
* `SPECIFICATION-DISPUTE` — an independent implementer could not derive a unique expected result
  from the control text

**The last outcome matters most: every episode tests two objects, the subject and the control.**
An ambiguous or unportable control should lose standing rather than forcing the challenger to
guess correctly. That is ICP's independent-reconstruction bar arriving from the other side, and it
means the procedure must be able to produce findings **against this register**.

## The minimum external ingredient

Nothing self-issued produces assurance. A self-run produces exactly one honest sentence: *under a
perturbation I selected, my check changed state.* It cannot establish adequate challenge
selection, complete scope, honest custody, or resistance to a challenge nobody anticipated.

The smallest sufficient external ingredient is **one control identity independent of the subject**
that selects the control and the challenge, freezes the target before revealing the perturbation,
witnesses both healthy and perturbed runs, takes custody of raw evidence without producer
selection, exercises the verifier's own negative control, and signs only the bounded observation.
That supplies **role separation, not competence and not deep independence**. For consequential
reliance, split it into a challenger and an evidence custodian.

## Solo developer and large lab are the same artifact

Same schema, different provenance — **no maturity ladder, because a ladder is a thing to climb**.

A solo developer in an afternoon: freeze one target, write one challenge adapter, run the paired
healthy and perturbed cases, discover which of their checks are decorative, record unresolved
applicability. That yields a **producer-run diagnostic transcript**. It is useful, it is honest,
and it is not assurance. A lab takes the same packet and adds independent selection, independent
custody, multiple discovery channels, withheld challenges and expiry. The issuer and the custody
chain determine what the evidence supports.

## The document side

**A prose linter cannot enforce controls 10, 31, 35, 36, 42, 43 or 63.** Control 10's own
false-negative clause already rejects forbidden-word grepping. Mechanical checking becomes real
only once claims are **typed blocks** adjacent to the prose.

What is genuinely checkable — and what each check still leaves open:

| checkable | still unestablished |
|---|---|
| every file in a declared corpus parses, or the scan refuses to report | that the declared corpus is complete |
| evidence paths exist and hashes match | that the evidence supports the claim |
| subject, configuration, time, stratum and control version are present | that the stratum is the right one |
| an absence claim names corpus, query and date | that the search was adequate |
| a stop condition predates the first result | that the program will stop |
| an efficiency claim joins to quality evidence from the same run | that the quality metric measures anything that matters |
| a gain links to a residual-failure artifact | that the residual is complete |
| every observation carries a configuration identity | that configurations are comparable |
| unknowns keep a non-aggregable type through serialisation | that all unknowns were recognised |
| role declarations resolve against a deterministic matrix | that different keys mean different interests |

Looks mechanisable and is not: finding implicit claims in arbitrary prose; deciding whether a
sentence implies "safe" without the word; construct validity of a quality metric; whether a
residual is "comparably specific"; whether a review frame is genuinely outside; whether a gate has
quietly become the objective-setter. A detector over legacy prose is **triage, not enforcement**,
and its recall must be measured against externally labelled samples.

## What the workbench proposed, and what happened to it

| proposal | disposition |
|---|---|
| **A.** Applicability-first triage from producer questions | **problem kept, mechanism rejected.** A producer questionnaire makes scope a self-authored premise; scope must be a challenged conclusion |
| **B.** Evidence-shaped states instead of scores | **discarded, called actively dangerous.** The states become an ordinal scoreboard immediately, and the best-looking state is earned by a verifier that always fails |
| **C.** Port each control's fixture and demonstrate rejection | **kept but demoted.** Fixtures qualify adapters and verifiers; they do not establish subject conformance, and a producer-translated canonical fixture is the weakest form |
| **D.** Code-side versus document-side | **dichotomy dissolved.** Governance is executed through documents and code emits claims; the real line is mechanically represented predicates versus unrestricted semantics |

Six things none of the four had: the **relying decision**; that the **register is also under
test**; that **controls interact** and per-control success does not establish composed behaviour
(control 48 turned on the register itself); that the **50 below-line entries cannot support
mandatory conformance** because they are hypotheses; that **recovery needs exercising**, not just
rejection; and that the **scope machinery needs its own negative controls** — reference subjects
with deliberately hidden triggers — or it becomes the new always-green check.

## A defect this design found in the register

The founding ten controls **had no `applies_when` field at all**, and the renderer silently
omitted the applicability sentence when it was absent. Absence was therefore indistinguishable
from "applies universally" and from "nobody decided" — and any scope engine built on it would have
guessed, silently, in whichever direction its author assumed. The workbench had itself read the
absence as universality and said so.

Fixed 2026-08-10: all ten state their scope, and the builder **refuses to publish** any control
that states none. That is control 53 turned on the register — an unknown must not be read as a
value.

## The pilot, if this is built

Not a procedure. A small **Witnessed Control Challenge format**, piloted against three
qualitatively different controls — one runtime, one claim/document, one organisational — with **one
deliberately concealed applicability trigger**.

**The success criterion is not that the subject looks good.** It is that the pilot produces at
least one `ESCAPED`, `UNRESOLVED` or `SPECIFICATION-DISPUTE` that a self-authored checklist would
have hidden. If it cannot produce one, the format is measuring paperwork and should be abandoned
rather than published.
