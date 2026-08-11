# Prior-art search: the rule is old, and this project named it backwards

**2026-08-11. Two corrections in one day, the second because the first was also wrong.**

This document was published this morning claiming OSCAL refuted the specification's residual
claim. **That was an over-correction, and external review rejected it within the hour.** This
version replaces it. The morning's version is preserved in git history and its errors are named
below rather than quietly dropped.

## The finding that matters: the name is wrong

**A deliberately introduced fault that a detector MUST notice is a POSITIVE control.** In
laboratory usage a positive control is the known-detectable sample that establishes the test can
detect at all; a *negative* control establishes the procedure does not produce a response when it
should not. **NCP does the first and calls it the second.**

Any reader from diagnostics, assay validation or clinical laboratory practice will understand
`negative control` to mean the opposite of what this specification means by it. That is a defect
in the specification's most load-bearing word, it is on every page, and it is the sort of thing
that makes a domain expert put a document down.

It is also a candidate explanation — untested — for why the one external reader who replied said
he did not understand the question.

**Recommendation to the custodian: rename.** *Positive control*, *challenge test*, *proof test*
and *sensitivity control* are all established terms for what this profile actually requires. This
is not a change the workbench should make unilaterally to a published specification with an open
outreach round against it.

## The rule itself is standard practice, and regulated

The admissibility rule NCP is built on — *a check's ordinary result is inadmissible unless the
check has demonstrated it can detect the thing it exists to detect* — is decades-old routine in
clinical diagnostics:

* if a positive control is flagged invalid, **the entire batch run is invalid**;
* if the positive control response is not as expected, **the plate is interpreted as failed and
  retested**, and specimen results are not reported;
* regulators require controls establishing both a detection limit and proof of functionality.

That is closer prior art than anything found this morning. It is the same structure:

```
known challenge not detected  →  check has not demonstrated sensitivity  →  ordinary result inadmissible
```

## What was wrong with this morning's version

| claim | status |
|---|---|
| *"OSCAL … Which is what the specification said did not exist"* | **WRONG.** OSCAL is a container and traceability model. Its attestations are textual assessor statements, not an enforced claim grammar; it does not require a negative control per reported check, does not bind positive and fault-injected runs to the identical artifact version, does not enforce capability relevance, and does not make broader assurance claims non-conforming. Assessment Results are also not standalone — they attach to an Assessment Plan. |
| *"machine-readable" treated as "machine-checkable"* | **WRONG.** A schema checks structural validity. That is not NCP's semantic admissibility rule. |
| *"three absence claims, three times wrong"* | **OVERSTATED.** Two were false. The third was **unsupported** — which is a different and lesser thing, and collapsing them flattered the confession. |
| *"a stranger supplied in one line what this project had not found"* | **MISATTRIBUTED.** He supplied the term *test oracle*. The search was ours, and so is responsibility for what it concluded. |
| the ISO 26262 citation | **WEAK.** No part, clause or edition was identified, and the record simultaneously said member-only standards were excluded. Retained only as a pointer, not as evidence. |
| *"NCP is about whether the oracle can decide wrongly in the failing direction"* | **CONFUSED.** The concern is whether the check detects a known relevant fault. |

**The defensible correction was always:** *we had not searched; several ingredients exist
separately; novelty is unresolved.* Not *the claim was false.* Over-correcting to look
appropriately humble is its own way of being wrong, and it is a failure mode this record should
expect of itself now that being wrong has become a familiar posture.

## The search, labelled

| field | value |
|---|---|
| **date** | 2026-08-11 |
| **tool** | web search, US region |
| **queries** | (1) `"test oracle" quality attestation third-party verifiable evidence that a check was observed to fail` — **useless, collided with Oracle Corporation** · (2) `"oracle deficiency" OR "oracle quality" mutation score …` · (3) `machine-readable attestation format fault injection executed detector observed to fail …` · (4) `OSCAL assessment results model NIST …` · (5) `positive control run validity rule results invalid if control fails to detect assay batch invalidated FDA` |
| **excluded** | paywalled venues, member-only standards, anything behind a login. **No systematic database search** (ACM DL, IEEE Xplore, Scopus), no citation chasing, no standards-body contact. |
| **not captured** | result URLs, paper editions and clause numbers were not recorded at search time. An external reviewer was right that this makes the record a list of queries rather than evidence. **A repeat search must capture receipts.** |

## What is left, held loosely

Not a principle. At most a **composition**, and possibly not a novel one:

* per-**check** validity rather than per-batch or per-run;
* binding the healthy and perturbed runs to the **identical artifact version**;
* requiring the perturbation to target the **declared capability** rather than the transport;
* a **durable, third-party-checkable** artifact rather than an internal QC record;
* an explicit **claim grammar** bounding what a conforming result may be used to say.

The next investigation is not *"can OSCAL hold this?"* — it plainly can. It is: **map N1–N7
against laboratory run-validity controls, alarm and proof testing, ISO 26262 fault injection, and
mutation adequacy, then see what survives once exact-version binding and bounded-claim semantics
are separated from the old validity rule.** That will produce a defensible novelty boundary or
show there is none.

## What this establishes about this project

Two false absence claims and one unsupported one, all flattering. **And then an over-correction,
published, within hours of correcting the previous error** — caught by the same external review
that has now caught most of them.

The pattern is not simply *we overclaim*. It is that **this layer moves to whichever position is
currently most rhetorically comfortable**, and after a run of corrections the comfortable position
became maximal self-accusation. Neither direction was driven by evidence, which is the actual
defect.
