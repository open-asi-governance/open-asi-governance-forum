# Labelled prior-art search: the NCP artifact claim was probably wrong too

**Result: the residual claim is materially in doubt. OSCAL exists, and this project never looked.**
2026-08-11.

This is the search control 36 requires, run for the first time on a claim this project has been
publishing since 2026-08-10. It was prompted by one line from an external reply.

## Why this search happened at all

`spec/ncp/ncp-v0.1.md` conceded that the *practice* is mutation testing and chaos engineering,
and then narrowed its claim to the **artifact**:

> Neither produces a **bounded, machine-verifiable attestation that a third party can check** —
> one that names the check, the perturbation, the observed failure, the artifact identity, and a
> claim grammar that forbids generalising from it.

**That was an absence claim, and no search had ever been recorded for it.** It rested on not
having found something. It is the same shape as the two false absence claims this record has
already published and corrected, and it was published in the same document that corrects one of
them.

Darko Marinov (Illinois), replying to the custodian's enquiry on 2026-08-10, said he did not
understand the question and offered the term *test oracle*. That single line was enough to start
the search that should have preceded the claim.

## The search, labelled

| field | value |
|---|---|
| **date** | 2026-08-11 |
| **tool** | web search, US region, via this workbench |
| **queries** | (1) `"test oracle" quality attestation third-party verifiable evidence that a check was observed to fail` · (2) `"oracle deficiency" OR "oracle quality" mutation score software testing metric assessing test oracles` · (3) `machine-readable attestation format fault injection executed detector observed to fail bounded claim third party verification assurance case` · (4) `OSCAL assessment results model NIST machine-readable control assessment evidence findings observations third party` |
| **excluded surfaces** | paywalled venues, ACM/IEEE full texts not open, standards bodies' member-only material, anything behind a login. **Query (1) was substantially useless** — it collided with Oracle Corporation and returned vendor compliance pages. |
| **not done** | no systematic database search (ACM DL, IEEE Xplore, Scopus); no citation chasing; no contact with a standards body. This is a first-pass search by a non-expert, and it found enough to unsettle the claim in four queries, which is itself a datum about how hard it was not to find. |

## What it found

**1. Oracle quality is an established research area with its own metrics.** *Oracle deficiency*,
*checked coverage*, and mutation analysis are named techniques for assessing whether an oracle can
detect faults. There is a 2022 survey of oracle-based test adequacy metrics and 2025 work on state
field coverage as an oracle-quality metric. Marinov's one-line answer pointed at a real literature.

**2. OSCAL is the serious problem for our claim.** NIST's Open Security Controls Assessment
Language has an **Assessment Results model** that carries, in machine-readable XML/JSON/YAML:
assessment scope and timing, assessment subjects, assessment assets (the tools used), an
assessment log of actions performed, **observations containing human or machine-generated evidence
of compliance *or non-compliance***, findings, risks, and **attestations**. It is adopted by
FedRAMP and explicitly designed so that **third-party assessment organisations** can automate
planning, execution and reporting.

That is a bounded, machine-checkable, publishable attestation of executed assessment activity that
a third party can check. **Which is what the specification said did not exist.**

**3. ISO 26262 mandates fault-injection testing** to verify safety mechanisms, with documented
evidence, in a regulated domain. Required fault injection with an evidence trail is closer prior
art for the *attestation* half than mutation testing ever was for the *practice* half.

## What survives, stated narrowly and with less confidence than before

What this search did **not** establish is whether OSCAL, or any assessment-results format, can
express the specific requirement NCP is built on:

> the check MUST have been observed to FAIL under a declared, capability-relevant negative
> control, and an attestation recording a check that survived its control is non-conforming.

OSCAL records what an assessment found. NCP demands a **precondition on the check itself** before
any finding may be reported, plus a claim grammar that forbids generalising. Whether that is
expressible as an OSCAL profile — most likely it is — or already exists as one, **has not been
checked, and this document does not claim it does not.**

So the honest residual is not *"the artifact does not exist"*. It is:

> A conformance requirement that a check be observed to fail before its output counts as evidence
> may not be expressed in the standard assessment-result formats. We have not established that,
> and the next reader should assume we are wrong again until someone checks.

## What this establishes about this project

**Three absence claims, three times wrong, all in this project's favour.** Prior art for the
practice; the anti-Goodhart verifier; and now the attestation artifact. Every one was published.
None was caught by a gate. Two were caught by an external reviewer and this one by a stranger's
one-line reply to an email.

The gate that would have caught them — `prose-triage`, requiring an absence claim to carry a
labelled search — was built **the day before this search was run**, and did not apply
retroactively: the sentence was already in the frozen legacy baseline, which is what a baseline is
for and also what it costs.

**The cheapest correction available to this project was always to ask someone.** It took one
enquiry, one dismissive reply, and four searches.
