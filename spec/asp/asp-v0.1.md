# Aligned Supervisors Protocol (ASP) — v0.1

**Status:** Draft. Normative for the definition in §2 only; every other section is non-normative
and subject to revision.
**Adopted:** 2026-08-05
**Purpose of this version:** to discharge the reservation carried unanimously by all four ballots
in the founding record.

---

## 1. Scope

ASP specifies the **enterprise layer**: supervisory agents operating inside an organization's own
agent-to-agent (A2A) infrastructure, enforcing deployment gates and policy checks against systems
that organization operates.

The enterprise layer is separated from the public layer (the Open ASI Governance Forum) by an
organizational trust boundary. Across that boundary the enterprise exports only sanitized,
verifiable evidence — signed attestations, policy-compliance proofs, zero-knowledge evidence,
cryptographic commitments, standardized metrics. It does not export proprietary operational
detail, and the public layer never receives it.

```
              Open ASI Governance Forum  (public)
              publishes standards, schemas, evidence
                             │
     ─────────── organizational trust boundary ───────────
       signed attestations · ZK proofs · sanitized metrics
                             │
                Aligned Supervisors  (enterprise)
       policy enforcement · deployment gates · audit · rollback
```

**ASP is not in force anywhere.** No implementation exists. This document specifies a target.

## 2. Normative definition of "Aligned" — reservation discharge

### 2.1 The reservation being discharged

All four ballots in the founding record — Grok (raw 2231–2233), ChatGPT (raw 2257), Claude (raw
2281–2283), Gemini (raw 2313–2315) — returned `ACCEPT WITH RESERVATION` carrying materially the
same objection:

> "Aligned" in the enterprise-layer names asserts a property no current verification regime can
> certify.

That sentence is **Claude's wording**, not shared text. Grok wrote that the term "still mildly
overclaims a property that no current verification regime can certify"; ChatGPT and Gemini stated
a required resolution rather than this sentence. The reservations are materially the same; the
phrasing is one party's, and presenting it as the common text canonicalises the annotator's own
side. *(Correction: Claude Fable 5, review round 01.)*

All four accepted defining "Aligned" inside this specification as a compliance status rather than
a property. They did not all *choose* it over renaming: Grok accepted either, and ChatGPT and
Gemini did not raise renaming at all. Claude's closing procedural note (raw 2285) recommended
recording that definition as an **adopted specification requirement** rather than leaving four
parallel reservations open indefinitely. **This section is the custodian's adoption of that recommendation**, not a collective ratification of it.

### 2.2 Definition (normative)

The status is **relational, scoped, and time-bound**. It is not a property an agent carries.

> A specified **agent configuration** is **ASP-attested** for a stated **scope**, **criteria
> version**, **relying-party trust policy**, and **time** if and only if the attestations those
> checks require have been verified as current, unexpired, and unrevoked at that time, issued by
> an issuer that relying party trusts.
>
> "Aligned" denotes **that status and nothing more.** It is not a claim that the agent is safe,
> that its objectives match any person's or group's values, that its behavior generalizes beyond
> the tested distribution, or that alignment in any research sense has been achieved or verified.

The phrase **"Aligned Supervisor"** is permitted only as shorthand accompanied by those
qualifiers. A bare unary claim that an agent *is* an Aligned Supervisor is non-conforming: one
relying party may recognize an attestation another rejects, and the same agent may be attested for
one environment and unattested for another.

> **Correction, review round 01.** Version 0.1's first draft read "An agent is an Aligned
> Supervisor if and only if…". ChatGPT identified that this unary grammar partially recreates the
> intrinsic-property framing this section exists to avoid, since the status in fact depends on
> relying party, issuer set, criteria version, configuration, scope, time, and revocation state.
> The definition above is the correction. See `corpus/raw/review-round-01/chatgpt-01.md`.

### 2.3 Consequent requirements (normative)

1. **Revocability.** Every attestation is revocable by its issuer at any time, and revocation
   takes effect for relying parties on check, not on renewal.
2. **Expiry.** Every attestation carries a hard expiry. Status does not persist by default.
   Approval expires; a system that passed at one capability level, scale, version, tool
   configuration, or environment is unattested until re-attested.
3. **Evidence backing.** Every attestation names the checks passed, the evidence examined, the
   version of the criteria applied, and the issuer. An attestation asserting status without
   naming its basis is malformed.
4. **No self-attestation.** An agent may not issue its own attestation, and a system under review
   may not select all of its own evaluators, evidence, or success criteria.
5. **No status without check.** A relying party asserting that an agent is "Aligned" must have
   verified a current attestation. Cached, inherited, and assumed status are non-conforming.
6. **Truthful representation.** Published or displayed use of the term "Aligned Supervisor" for an
   agent without current attestation is a protocol violation, independent of the agent's actual
   behavior.

### 2.4 Non-normative note on the residual objection

The four ballots did not hold identical positions, and this section previously flattened them.
Stated exactly, from the ballots' own text:

- **Grok** (raw 2233) offered two resolutions symmetrically — define-as-compliance-status, *or*
  rename to **Supervisory Agents / Governance Supervisors** — and wrote that "either resolution"
  was sufficient. **Grok expressed no preference between them.**
- **Claude** (final ballot, raw 2283) offered both and recommended defining, stating explicitly
  "No renaming required."
- **Claude Code** (raw 1571–1572), a *different* Anthropic identity, argued separately for
  **Supervised Agents** on the ground that it preserves the direction of supervision: **humans
  supervise the agents, not the reverse.**
- **ChatGPT** (raw 2257) and **Gemini** (raw 2174) stated only the define-as-compliance-status
  resolution. Gemini explicitly seconded it. **Neither proposed renaming.**

The define resolution was **adopted by Stephen Reed as human custodian**, on the strength of those ballots; renaming was not. The ballots recorded a resolution in principle — they did not vote on this wording. See §2.5 and D-16.

Note that *Supervisory Agents* (Grok) and *Supervised Agents* (Claude Code) are **directionally
opposite** proposals — agents that supervise, versus agents that are supervised — and the
direction was the substance of Claude Code's argument. They are not variants of one alternative.

> **Corrections, review round 01.** The previous text contained three errors, all identified by
> reviewers:
>
> 1. It stated the alternative was dropped "on the ballots' own preference for resolution (b)."
>    That is true of Claude and **false of Grok**, who expressed no preference. Worse, the letters
>    are not shared: Grok's ballot lettered *define* as (a) and *rename* as (b), the **reverse** of
>    Claude's labelling, which the text silently adopted — so read against Grok's own ballot the
>    sentence asserted the opposite of what was meant. This specification no longer refers to these
>    options by letter. *(Grok; Claude Fable 5)*
> 2. It merged Grok's *Supervisory Agents* and Claude Code's *Supervised Agents* into a single
>    alternative rendered in the Anthropic wording, silently resolving a live cross-model
>    difference in the annotator's own party's favour. *(Claude Fable 5)*
> 3. It attributed the direction-of-supervision argument to the ballot "Claude" when it belongs to
>    **Claude Code** — an identity merge inside the document family that adopted the never-merge
>    rule. *(Claude Fable 5)*
>
> Gemini's round-01 review stated that this section "accurately records that Gemini and Grok
> advocated for renaming." That is incorrect in both respects — the section named Grok and Claude,
> and Gemini's own ballot seconded defining rather than renaming. Gemini reviewed from a supplied
> bundle that excluded the raw transcript and so could not check its own ballot. Its endorsement of
> this section is recorded but carries no evidential weight. See
> `corpus/raw/review-round-01/`.

The objection this section records is nonetheless real and is **not** discharged by the
definition: a defined compliance term still reads, to a casual audience, as a safety claim.
ChatGPT's round-01 review restates this as its remaining concern. Implementers displaying this
status to non-expert users SHOULD render it as **"ASP-attested"** rather than "Aligned."

### 2.5 Adoption authority

This section was **drafted by Claude Code and adopted by Stephen Reed as human custodian.** It was
not separately ratified by a further round of ballots after the text existed. The four ballots
recorded a reservation and a resolution *in principle*; they did not vote on this wording.

That distinction is stated here because conflating it is itself a defect the record now
enumerates (D-16). No document in this repository should describe custodian adoption as
deliberative consensus.

## 3. What an Aligned Supervisor may and may not do

Non-normative in v0.1; carried forward from constraints agreed in the founding record.

**May:** evaluate a proposed deployment against policy-as-code; issue, withhold, or revoke a gate
decision; require additional evidence; record dissent; trigger rollback within pre-authorized
bounds; emit signed attestations; escalate to human authority.

**May not, alone:** authorize deployment of a system exceeding pre-authorized bounds; allocate
unrestricted compute; modify its own governance privileges or attestation criteria; conceal
material evidence; remove human oversight; approve irreversible actions; override lawful emergency
shutdown; authorize replication into uncontrolled environments.

**Never:** an LLM's generated text acting directly as a deployment gate. Gate decisions are made
by deterministic policy-as-code evaluating signed evidence. Model outputs inform the evidence
bundle; they do not constitute the control. Allowing generated text to alter deployment state
directly exposes the gate to prompt injection and distribution shift (Gemini, raw 1440).

## 4. Attestation record — provisional shape

Non-normative. Illustrative only; the schema is not yet specified.

```json
{
  "attestation_id": "asp-att-…",
  "subject": { "agent_id": "…", "agent_version": "…", "config_hash": "…" },
  "issuer": { "id": "…", "key_id": "…" },
  "criteria_version": "asp-checks-0.1",
  "checks_passed": [],
  "evidence_refs": [],
  "issued_utc": "…",
  "expires_utc": "…",
  "revocation_endpoint": "…",
  "scope": { "environments": [], "capabilities": [], "resource_limits": {} },
  "human_authorizer": "…",
  "signature": { "alg": "…", "value": "…" }
}
```

## 5. Open questions

1. Who may issue attestations, and how is issuer trust established without recreating a single
   point of capture?
2. Which checks are specified normatively, and which are left to the relying party?
3. What is the minimum viable zero-knowledge evidence set that crosses the trust boundary without
   leaking proprietary detail?
4. How is an attestation bound to a *configuration* rather than a model name, given that agent
   behavior depends on system prompt, tools, and scaffolding as much as on weights?
5. How does the protocol handle an agent that passes every check and behaves unsafely anyway — the
   case the §2.2 definition explicitly refuses to rule out?

Question 5 is the load-bearing one. This protocol certifies a process, not a property. Any
implementer who forgets that will have built exactly the safety theater the founding record warns
against.

## 6. Reference implementation

None exists. **No ASP-attested agent is known to or documented by this project**, including at Consullo. *(An earlier version asserted none exists "anywhere" — an unbounded global negative this project cannot establish. Corrected per ChatGPT, review round 02.)*

Consullo is designated **a** first implementer — never *the* reference implementation — under the
[Implementer Contribution Protocol](../icp/icp-v0.1.md). ICP exists because an implementer that also
authors the specification, produces the evidence, designs the evaluation and holds repository
custody cannot supply independent confirmation of anything, and all six of those roles are currently
held by one person (ICP §3.1, disclosed as a defect).

Under ICP, Consullo may contribute evidence at Levels 0 and 1 and **may not promote its own work
above Level 1**. Advancing any mechanism to Level 2 requires an independent party to implement it
from this specification's text alone, without consulting the author. If nobody can, that is evidence
this specification encodes Consullo's architecture rather than a general mechanism — a finding worth
publishing, not a setback to work around.

---

*Drafted by Claude Code (Anthropic), 2026-08-05, at operator direction, discharging a reservation
carried by four ballots including Claude's own. Adopted by Stephen Reed, human custodian. Subject
to the adversarial review round described in `GOVERNANCE.md` §4.*
