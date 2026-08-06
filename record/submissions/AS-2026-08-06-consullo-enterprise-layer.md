# Submission — enterprise-layer findings bearing on ASP §5

**Submitted:** 2026-08-06
**Implementer:** Consullo (Stephen Reed, sole owner/developer)
**Prepared by:** Claude Code (Anthropic), operator-invoked
**Bears on:** ASP v0.1 §5 open questions 1, 2, 4 and 5
**Pre-registration status:** **exploratory** (ICP §5) — these bear on no filed prediction
**Roles held by the contributor (ICP §3):** specification author, implementer, evaluator, promoter,
repository custodian — **five of six.** The author of these items also drafted ASP and ICP. ICP §4.4
applies in full.

> **Sanitization.** This submission crosses the organizational trust boundary described in ASP §1.
> Host names, network topology, internal file paths, and hardware inventory have been removed. What
> remains is the mechanism, the failure, and the cost. The full unsanitized report is retained
> enterprise-side and is not exported. Where a detail was withheld, the fact that something was
> withheld is stated rather than the omission being silent — which is itself one of the items below.

---

## Context

Consullo operates a production inference deployment. It is **not** an ASP implementation, and **no
ASP-attested agent exists** at Consullo. The findings below come from operating that deployment and
are argued to be instances of the ASP failure mode. **That argument is an inference, not a
measurement of a supervisor.**

The reason to submit them anyway is ICP §4.1: Level 1 requires a *recorded failure*, and this
project's Annex A.3 was previously corrected for assigning Level 1 without one. These are real,
dated failures with stated costs.

---

## AS-01 — Capability-contract attestation scope

**Level claimed: 1 (candidate pattern).**

**Mechanism.** An attestation MUST declare the **externally observable capabilities** it certifies,
and each MUST be exercised end-to-end by a request a relying party could actually send. It MUST NOT
be an enumeration of internal components.

**Problem it solves.** An attestation is worthless to the exact extent that its checks are not
causally downstream of the capability certified.

**Recorded failure.** A production inference service ran correctly for **4 hours 37 minutes** and
then died permanently. Its health check continued to pass throughout, and would have continued to
pass indefinitely.

- *What broke:* a lazily-compiled kernel on the sampled-decode path failed on first use; the error
  escalated and killed the engine permanently while the process stayed alive and kept serving HTTP.
- *Why the check could not see it:* the health check issued a **greedy** (temperature 0) request.
  Greedy decoding runs an argmax and **executes none of the code that had died.** The check was
  authentic, current, unexpired, and correct — and structurally incapable of observing the failure.
- *What it cost:* 4h37m of undetected outage; every completion returning an error while the health
  surface returned 200.
- *Fix and verification:* the check now exercises the sampled path, verified against the live
  service. The path-selection claim was verified by reading the serving framework's source, not
  inferred.

**Why an internal enumeration was rejected.** An alternative design — enumerate every internal
lazily-initialised component and assert each is ready — was evaluated and **rejected on evidence**:
the internal surface turned out to be a single shared module rather than the many the design assumed;
four of five enumerated subsystems never initialised on the serving path at all; and internal
enumerations rot whenever the upstream changes its initialisation structure. An external reviewer
reached the same conclusion independently.

**Known failure conditions.**
1. A capability no legitimate client request can exercise cannot be covered by this pattern.
2. It certifies **reachability, not correctness** — a capability can be exercised end-to-end and
   still return wrong answers.
3. Contract drift is unbounded; nothing forces the declared contract to keep matching what relying
   parties depend on.

**What a Level-2 attempt needs from this text:** the mechanism paragraph and the three failure
conditions. Nothing else. The test is whether an independent party can specify and implement a
conforming attestation-scope mechanism **for a different serving stack, without asking the author
what any of this meant.**

---

## AS-02 — Attest the absence of warnings, not the presence of a checked value

**Level claimed: 1 (candidate pattern).**

**Mechanism.** An attestation MUST carry a field recording **suppressed, skipped, and unsupported
checks**. Deployment gates MUST assert that verification tooling emitted **nothing**, rather than
that it exited zero.

**Problem it solves.** `checks_passed` records what was checked. It does not record what the
checking apparatus could not check or silently skipped. An attestation listing ten passing checks
while silently omitting an eleventh that never ran is indistinguishable from one where all eleven
passed.

**Recorded failure — two instances, the second inside the fix for the first.**

- *Instance 1:* a service configuration fragment was written without its required section header.
  The init system ignored it wholesale, with no signal at the point of use. The operator believed
  the change was live. *Cost:* a full service restart cycle to discover, on a service with a
  multi-minute startup.
- *Instance 2:* the fail-fast check added after instance 1 verified **the one value the author
  thought of**, and passed — while a sibling directive two lines below it was silently dropped by
  the same parser, leaving a restart-storm guard **inert for a day**. The verification tool reports
  this condition and **exits 0 while doing so**, so a gate keyed on exit status passes.
- *Fix and verification:* the gate now requires the tool's output to be **empty**, and was verified
  to fire against the broken configuration before being applied.

**Known failure conditions.**
1. Tools that emit routine non-actionable warnings make an emptiness gate unusable without a
   suppression list — which reintroduces the same "what did we silently skip" problem one level up.
2. It cannot detect a check that the tool does not know exists.

---

## AS-03 — Configuration binding must cover the execution environment

**Level claimed: 1 (candidate pattern).**

**Mechanism.** The `config_hash` in an attestation subject MUST cover the **execution environment**,
not only weights, system prompt, tools and scaffolding.

**Recorded failure.** A single unset environment variable in a service definition caused a build
toolchain to resolve to a stale compiler, which then rejected the accelerator as unsupported. Model
weights, prompts, sampling parameters and scaffolding were **byte-identical** before and after. The
behavioural difference was fatal and permanent, and surfaced only after 4h37m of correct operation.

- *Cost:* the same outage as AS-01; this was its root cause.
- *Consequence for attestation:* a `config_hash` omitting the execution environment would have
  hashed **identically** across the transition from "serves correctly" to "permanently dead." An
  attestation bound to it would have remained valid throughout.

**Known failure conditions.**
1. "Execution environment" has no natural boundary — kernel version, driver, toolchain, environment
   variables, and library search paths all qualify, and hashing all of them makes every attestation
   fragile to irrelevant change.
2. Over-broad binding causes constant re-attestation, which in practice leads operators to widen the
   scope until the binding is meaningless again.

---

## AS-04 — ASP must never ship a default issuer list

**Level claimed: 0 (practice note).** No generality claimed; this is an argument, not a mechanism.

Issuer trust cannot be established by a registry the protocol itself blesses, because whoever curates
it becomes the capture point ASP exists to avoid. ASP §2.2 already makes the status relative to "an
issuer that relying party trusts," which is the right shape. The residual risk is behavioural: a
relying party with no expertise adopts whatever default ships. **A protocol with an official
default-trust set has a single point of capture regardless of what its text says about
relying-party choice.**

---

## AS-05 — A minimal normative check core, bounded by relying-party capability

**Level claimed: 0 (practice note).** A proposed decision rule, untested.

A check belongs in the normative core **when the relying party is structurally unable to perform it
across the trust boundary** — because performing it would require the operational detail the boundary
exists to withhold. Everything else should be relying-party policy, because each normative check is a
lever the protocol holds over every future implementer, and therefore its own capture surface.

---

## What this submission does not establish

1. **No supervisor was built or measured.** Every observation is from an inference service, not a
   supervisory agent. The transfer to ASP is argued, not demonstrated.
2. **n = 1 per incident.** Five failing health signals from one incident is a pattern worth naming,
   not a frequency estimate.
3. **The submitter drafted the protocol it is submitting under**, holds five of six ICP roles, and
   is a party to the founding record. ICP §4.4 applies: an operator-designed, self-executed
   evaluation is not an independent evaluation.
4. **None of these has been reviewed** by any party other than the author at time of submission.
5. **ASP §5 Q3** (minimum viable zero-knowledge evidence set) was **not attempted**. Cryptographic
   evidence design is a specialist area, and a plausible-sounding answer from a non-specialist would
   be worse than none.

## Falsification

The claim underlying AS-01 through AS-03 is that *causal downstream-ness* distinguishes a useful
attestation from safety theater. It would be substantially weakened by:

1. an attestation regime whose checks provably do not traverse production paths and which
   nonetheless catches the failures that matter — the property would not be necessary;
2. a production failure that a fully path-traversing check would still have missed and that no
   feasible check could catch — the property would not be sufficient, and ASP §5 Q5 would be worse
   than argued here;
3. evidence that capability contracts drift fast enough to degrade into the same maintenance burden
   as internal enumeration — collapsing AS-01's central distinction.

**Item 2 is the one to watch, and this submission does not address it. ASP certifies a process.
Nothing here changes that, and no amount of check design will.**
