# Fault-Injection Check Profile (FICP) — v0.2

**Terminology correction, 2026-08-11.** This profile was originally published as the *Negative
Control Profile* (NCP) v0.1. **That name reversed established laboratory terminology.** A negative
control checks for a response in the *absence* of the target; the deliberately introduced,
must-be-detected condition this profile requires is analogous to a **positive** control — a sample
that *contains* the target and must elicit the expected response.

It is now called the **Fault-Injection Check Profile**, because *fault injection* is the more exact
engineering description: this profile does not supply control material, it **perturbs the subject**
and requires the check to notice.

**The rename does not establish novelty, correctness, coverage, or independent validation, and it
does not mean the earlier publications used the right term.** NCP v0.1 remains published at
`spec/ncp/ncp-v0.1.md`, frozen, with its own correction banner. Historical artifacts, outreach
under the old name, URLs and git history are unchanged. See `spec/ficp/MIGRATION.md`.

**Level claimed: 0 (practice note), unchanged.** The correction neither resets nor advances ICP
standing. An implementation of NCP v0.1 does **not** automatically count as an independent
implementation of this revised text.

---

## 1. The requirement

> **Every check that produces an assurance signal MUST ship with a fault injection: a declared,
> capability-relevant fault condition under which that check is required to return `FAIL`. The
> attestation MUST record that the fault was injected and that the check did return `FAIL`.**
>
> A check that has never been observed to fail is not evidence that anything works.

That is the whole normative content.

## 2. Vocabulary, which does semantic work

Four terms, used consistently, replacing wording that was ambiguous in v0.1:

| term | meaning |
|---|---|
| **baseline run** | the unperturbed run, in which the check is expected to return `PASS` |
| **fault injection** | the declared, deliberately produced, capability-relevant fault condition |
| **fault-injected run** | the run under that condition, in which the check is expected to return `FAIL` |
| **missed fault** | the check returned `PASS` while the declared fault was present |

**v0.1 said "a control the check *survives* is a defect."** That is dropped. It is anthropomorphic
and ambiguous in the wrong direction: a *system* may survive a fault — often desirably — while the
check still correctly reports degraded capability. What is at issue is whether the **check**
detected the fault.

## 3. Prior art, named up front

**The mechanism is not new and this profile does not claim it is.**

* **Fault injection.** Deliberately creating a fault and verifying the detection mechanism
  notices it is long-standing engineering practice, used to test fault detection, isolation and
  recovery.
* **Mutation testing.** Inject a fault into code, verify the suite catches it. An academic field
  since the late 1970s.
* **Chaos engineering with observability validation.** Inject a failure, verify the alert fires.
* **Run validity in regulated diagnostics.** If the control fails to produce its expected
  response, the run is invalid and no result may be reported. **This is the same admissibility
  rule this profile applies, and it is decades old.**
* **Oracle quality — an entire subfield this specification had not cited.** Added 2026-08-11 on a
  pointer from a correspondent who replied to the outreach and asked to remain anonymous. He said
  he knew no name for the specific requirement, and then named the literature it belongs to:
  * **Schuler & Zeller, *Checked coverage: an indicator for oracle quality*** (ICST 2011; STVR
    2013). Dynamic slicing measures what fraction of executed statements actually *influence an
    oracle* — code that runs but is checked by nothing. Reported as a **more sensitive indicator
    than mutation testing**, which is the prior art this spec did cite.
  * **Zhang & Mesbah, *Assertions Are Strongly Correlated with Test Suite Effectiveness***
    (ESEC/FSE 2015), and the assertion-quality work around it.

  His illustration is the clearest statement of the problem in this document:

  ```
  assert (output == output)   // useless -- can never fail, it is basically assert(true)
  assert (output >= 0)
  assert (output > 0)         // redundant -- if the previous passed, this always passes
  ```

  **A check that cannot fail, in two lines, from someone who studies this for a living.** That the
  profile's own prior-art section had to be told about oracle quality by a stranger is recorded
  here rather than quietly absorbed.

**The residual claim has narrowed again.** Checked coverage asks *how much of what ran was
checked by anything*; this profile asks *has this particular check ever been observed to fail*.
Those are adjacent, and the second is not obviously the harder or newer question — it is a
**per-check admissibility precondition on reporting**, where the literature above supplies
**suite-level scores**. One expert said he knew no name for it. **That is one expert's "I don't
know", it is weak evidence of absence, and this project has already been wrong three times about
exactly this.**

What may remain is a **composition**, not a principle, and its novelty is **unresolved**:
per-check rather than per-run validity; binding baseline and fault-injected runs to one artifact
version; requiring the fault to target the declared capability rather than the transport; a
durable third-party-checkable artifact; and a claim grammar bounding what a conforming result may
be used to say. See `record/findings/2026-08-11-prior-art-search-ncp-artifact.md`, including what
that search failed to capture.

## 4. The failure this is derived from

`record/submissions/AS-2026-08-06-consullo-enterprise-layer.md` (AS-01):

> A production inference service ran correctly for **4 hours 37 minutes** and then died
> permanently. Its health check continued to pass throughout, and would have continued to pass
> indefinitely.

The health check issued a **greedy** (temperature 0) request. The kernel that died was on the
**sampled** decode path, so the check executed none of the code that had failed. It was authentic,
current, unexpired, correct — **and structurally incapable of observing the failure it was
deployed to observe.**

No amount of running that check produces evidence. Running it with the sampled path deliberately
broken produces evidence in one attempt.

## 5. Normative requirements

Identifiers **N1–N7 are retained from v0.1 for citation stability**. `N` denotes *normative*, not
*negative*.

**N1. Every check has a declared fault injection.** For each check, a `fault_injection` naming the
fault condition under which the check must return `FAIL`, and how that condition is produced.

**N2. The fault was injected and the check was run under it.** Not described, not asserted —
executed, with a recorded timestamp.

**N3. The check rejected the fault-injected condition.** While the declared fault condition was
present, the recorded outcome MUST be `FAIL`. A `PASS` under that condition is a **missed fault
and a defect in the check**; the attestation MUST NOT claim conformance.

**N4. Both runs are bound to the same check identity.** The **baseline** and **fault-injected**
runs MUST name the same check by a stable id and the same executed artifact (path plus content
hash). A fault-injected run against a different build, host or code path proves nothing about the
check that shipped.

**N5. The fault MUST perturb what the check certifies, not merely the transport.** Cutting the
network makes every check fail and demonstrates nothing about any of them. The fault MUST target
the declared capability.

**N6. Skipped, suppressed and unsupported checks are disclosed**, with reasons, and are never
counted as passing. (Carried from AS-02. Unchanged from v0.1.)

**N7. The claim is bounded.** A conforming attestation may state only:

> Check set *C* was exercised against configuration *X* at time *T*. Each check was observed to
> return `FAIL` under its declared fault injection. This is process evidence about the checks.
> **It is not a claim that the system is safe, aligned, or correct.**

*"We follow OAGF"* and *"FICP certified"* are **non-conforming claims.**

## 6. What conformance does not establish

* **That the fault injections are the right ones.** A check can fail under a trivial perturbation
  and remain blind to the failure that will actually occur. This raises the floor from *never
  observed to fail* to *observed to fail at least once*.
* **That the check set covers the capability.** N5 constrains each fault's relevance; nothing
  constrains coverage.
* **Anything about the system.** Every claim is about the checks.
* **That the attestation is honest.** A self-issued attestation is self-issued. This makes the
  specific lie *"this check works"* harder to tell **by accident**; it does nothing about lying on
  purpose.

## 7. Attestation format

```json
{
  "ficp_version": "0.2",
  "subject": {"configuration_id": "…", "capabilities": ["…"]},
  "issued_utc": "2026-08-11T00:00:00Z",
  "checks": [{
    "check_id": "sampled-decode-health",
    "certifies": "the service can complete a sampled (temperature > 0) request",
    "artifact": {"path": "…", "sha256": "…"},
    "baseline_run": {"utc": "…", "outcome": "PASS"},
    "fault_injection": {
      "condition": "the sampled decode path is unavailable",
      "how_produced": "…",
      "targets": "the declared capability, not the transport",
      "run": {"utc": "…", "outcome": "FAIL"}
    }
  }],
  "undisclosed_nothing": {"skipped": [], "suppressed": [], "unsupported": []}
}
```

Field renames from v0.1: `ncp_version` → `ficp_version`, `positive_run` → `baseline_run`,
`negative_control` → `fault_injection`. **The old names are not preserved as aliases** — a field
called `negative_control` stays affirmatively misleading to exactly the domain experts whose
reading matters. Compatibility lives at the version boundary instead: see `spec/ficp/MIGRATION.md`.

`tools/verify_fault_injection.py` is the reference verifier. It **accepts v0.1 documents forever**,
with a deprecation warning, and refuses any document mixing both vocabularies.

## 8. Open questions, recorded rather than resolved

1. **How is "targets the capability, not the transport" (N5) mechanically checked?** It is a
   declared field a human must judge — the weakest requirement here and the most gameable.
   Shipped as a fixture the verifier cannot reject.
2. **What prevents a fault chosen because it is easy to detect?** Nothing. Also shipped as a
   known gap. This raises the floor from *never observed to fail* to *observed to fail once*;
   nothing mechanical distinguishes a demanding fault from a token one.
3. **Does requiring a fault injection per check bias toward few, coarse checks?** Plausibly.
   Unmeasured.
4. **Is the composition in §3 novel at all?** Unresolved, and the profile should not be read as
   asserting that it is.
