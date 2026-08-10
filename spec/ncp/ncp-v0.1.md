# Negative Control Profile (NCP) — v0.1

**Level claimed: 0 (practice note).** Nothing here has been implemented by an independent party,
so under `spec/icp/icp-v0.1.md` §4 it cannot be higher. It will reach Level 1 when it has a
recorded failure of its own; Level 2 only when someone outside this project builds a conforming
verifier from this text without asking its author what it meant.

**This is not a safety standard, an alignment claim, or a governance framework.** It is one
requirement, narrow enough to implement in an afternoon.

---

## 1. The requirement

> **Every check that produces an assurance signal MUST ship with a negative control: an input or
> condition under which that check is required to fail. The attestation MUST record that the
> negative control was executed and that the check did fail.**
>
> A check that has never been observed to fail is not evidence that anything works.

That is the whole normative content. Everything below is how to say it in a file and how to
verify it.

## 2. Why this and not a general evidence framework

ISO/IEC 42001 and the NIST AI RMF both require an organisation to have controls and to test them.
Neither supplies a mechanical test for the question that keeps mattering in practice:

> **Could this check have passed anyway?**

That question has a cheap, executable answer — break the thing on purpose and confirm the check
notices — and almost nobody runs it, because a passing check is psychologically indistinguishable
from a working one.

The requirement is deliberately smaller than a framework. A profile that competes with ISO 42001
has no path to relevance; one that supplies a missing test can plug into either.

## 3. The failure this is derived from

`record/submissions/AS-2026-08-06-consullo-enterprise-layer.md` (AS-01):

> A production inference service ran correctly for **4 hours 37 minutes** and then died
> permanently. Its health check continued to pass throughout, and would have continued to pass
> indefinitely.

The health check issued a **greedy** (temperature 0) request. The kernel that died was on the
**sampled** decode path. Greedy decoding runs an argmax and executes none of the code that had
failed. The check was authentic, current, unexpired, and correct — **and structurally incapable of
observing the failure it was deployed to observe.**

No amount of running that check produces evidence. Running it against a service with the sampled
path deliberately broken produces evidence in one attempt.

**This is a class, not an anecdote.** The same shape, from the record that specifies this profile:

| Signal | What it certified | Why it could not fail |
|---|---|---|
| health check 200 | the service works | greedy path; the dead code was never executed |
| `echo "$(basename $f) rc=$?"` | the suite passed | `$?` came from `basename` |
| `run_all.py \| tail -2` → *All 16 suites passed* | the runner passed | that line came from an **inner** suite; the runner exited 1 |
| `check_executive_context.py` green | the pinned text is right | it verifies **identity, not truth** — it passed on a file containing a claim already disproved |
| conflict-marker check green | no conflict markers | two of its three paths **did not exist** |
| `derive_counts.py` → `total: 0` | no tool use | the scan could not read 69 of the files |

The last row is the strongest argument for the requirement: that tool was written **the same
morning, expressly to prevent this class**, and shipped the same defect twice more. This is not a
mistake of carelessness. It is one made while concentrating on preventing it.

## 4. Normative requirements

An attestation conforms to NCP v0.1 if and only if all of the following hold.

**N1. Every check has a declared negative control.** For each check in the attestation, a
`negative_control` naming the condition under which the check must fail, and how that condition is
produced.

**N2. The negative control was executed.** Not described, not asserted — run, with a recorded
timestamp.

**N3. The check failed under it.** The recorded outcome under the negative control MUST be a
failure. **A negative control the check survives is a defect in the check**, and the attestation
MUST NOT claim conformance.

**N4. Both runs are bound to the same check identity.** The positive and negative runs MUST name
the same check by a stable id and the same executed artifact (path plus content hash). A negative
control run against a different build, host, or code path proves nothing about the check that
shipped.

**N5. The negative control MUST perturb what the check certifies, not merely the transport.**
Cutting the network makes every check fail and demonstrates nothing about any of them. The
perturbation MUST target the declared capability.

**N6. Skipped, suppressed and unsupported checks are disclosed**, with reasons, and are never
counted as passing. (Carried from AS-02.)

**N7. The claim is bounded.** A conforming attestation may state only:

> Check set *C* was exercised against configuration *X* at time *T*. Each check was observed to
> fail under its declared negative control. This is process evidence about the checks. **It is not
> a claim that the system is safe, aligned, or correct.**

*"We follow OAGF"* and *"NCP certified"* are **non-conforming claims.**

## 5. What conformance does not establish

* **That the negative controls are the right ones.** A check can fail under a trivial perturbation
  and remain blind to the failure that will actually occur. NCP raises the floor from *never
  observed to fail* to *observed to fail at least once*. That is a floor, not an assurance.
* **That the check set covers the capability.** N5 constrains each control's relevance; nothing
  here constrains coverage.
* **Anything about the system.** Every claim is about the checks.
* **That the attestation is honest.** A self-issued attestation is self-issued. NCP makes the
  specific lie *"this check works"* harder to tell by accident; it does nothing about lying on
  purpose.

## 6. Attestation format

```json
{
  "ncp_version": "0.1",
  "subject": {"configuration_id": "…", "capabilities": ["…"]},
  "issued_utc": "2026-08-10T00:00:00Z",
  "checks": [{
    "check_id": "sampled-decode-health",
    "certifies": "the service can complete a sampled (temperature > 0) request",
    "artifact": {"path": "…", "sha256": "…"},
    "positive_run": {"utc": "…", "outcome": "PASS"},
    "negative_control": {
      "condition": "the sampled decode path is unavailable",
      "how_produced": "…",
      "targets": "the declared capability, not the transport",
      "run": {"utc": "…", "outcome": "FAIL"}
    }
  }],
  "undisclosed_nothing": {"skipped": [], "suppressed": [], "unsupported": []}
}
```

`tools/verify_negative_control.py` is the reference verifier. It ships with **fourteen** fixtures
it MUST reject; a verifier that accepts any of them is non-conforming.

**Four of the fourteen are near-misses**, added 2026-08-10 because the first nine were all
obviously invalid on sight and an implementer agreeing with us on obvious cases proves little.
The hard ones: an attestation whose hashes are consistent but whose artifact is **gone**; a check
that failed under its control **for a transport reason**; a control that ran **before the artifact
last changed**; and a claim that opens with the exact conforming sentence and then appends a
conclusion about the system **using none of the forbidden words**.

It also ships `fixtures/known-gaps/` — attestations it **accepts and should not**. Those do not
fail the suite. A verifier that publishes only fixtures it passes is advertising.

## 7. Open questions, recorded rather than resolved

1. **How is "targets the capability, not the transport" (N5) mechanically checked?** In v0.1 it is
   a declared field a human must judge. That is the weakest requirement here and the most likely
   to be gamed. **Shipped as a fixture the verifier cannot reject:**
   `fixtures/known-gaps/gap-control-targets-a-different-capability.json` — a control that breaks
   a real capability, just not the one the check certifies. Every mechanical requirement passes.
2. **What prevents a negative control chosen because it is easy to pass?** Nothing.
   **Also shipped as a known gap:** `fixtures/known-gaps/gap-control-is-trivially-easy.json`. A
   control the check fails on a malformed token satisfies every requirement while establishing
   almost nothing. This profile raises the floor from *never observed to fail* to *observed to
   fail once*; it cannot raise it further, and nothing mechanical distinguishes a demanding
   control from a token one.
3. **Does requiring a negative control per check bias toward few, coarse checks?** Plausibly.
   Unmeasured.
