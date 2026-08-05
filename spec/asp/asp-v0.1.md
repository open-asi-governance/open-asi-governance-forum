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

All four converged on the same resolution: define "Aligned" inside this specification as a
compliance status rather than a property. Claude's closing procedural note (raw 2285) recommended
recording that definition as an **adopted specification requirement** rather than leaving four
parallel reservations open indefinitely. This section is that adoption.

### 2.2 Definition (normative)

> An agent is an **Aligned Supervisor** if and only if it holds a current, unexpired, digitally
> signed attestation set, issued under this protocol's published checks by an issuer the relying
> party trusts, and that attestation set has not been revoked.
>
> "Aligned" denotes **that status and nothing more.** It is not a claim that the agent is safe,
> that its objectives match any person's or group's values, that its behavior generalizes beyond
> the tested distribution, or that alignment in any research sense has been achieved or verified.

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

Two ballots (Grok, Claude) offered an alternative resolution: rename the layer to *Supervised
Agents* or *Governance Supervisors*, eliminating the word rather than defining it. Claude noted
additionally that "Supervisors" is defensible at this layer — those agents would hold real,
scoped, cryptographically bounded authority — while "Aligned" is the residual overclaim, and that
*Supervised Agents* better preserves the direction of supervision: **humans supervise the agents,
not the reverse.**

That alternative was not adopted, on the ballots' own preference for resolution (b). It is
recorded here because the objection it addresses is real: a defined compliance term still reads,
to a casual audience, as a safety claim. Implementers displaying this status to non-expert users
SHOULD render it as "ASP-attested" rather than "Aligned."

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

None exists. The Consullo Seed AI platform is a candidate first implementer — it operates a large
generated-agent hierarchy that requires deployment gating — which would make ASP evidence-backed
rather than aspirational. That is an intention, not a commitment, and no ASP-attested agent
currently exists anywhere.

---

*Drafted by Claude Code (Anthropic), 2026-08-05, at operator direction, discharging a reservation
carried by four ballots including Claude's own. Adopted by Stephen Reed, human custodian. Subject
to the adversarial review round described in `GOVERNANCE.md` §4.*
