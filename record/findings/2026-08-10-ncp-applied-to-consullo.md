# NCP v0.1 applied to Consullo — four of five checks survive their own negative controls

**Result: NON-CONFORMING. 4 violations, every one executed.** 2026-08-10.

**ABSTRACTED 2026-08-10, at the implementer's direction.** The first version of this finding
quoted source, named files, classes and configuration keys, and described four *unfixed* defects
in a private codebase. It was pushed to a public repository. This version keeps every outcome and
removes the identifying detail.

Two things about that, stated rather than glossed:

* **The implementer is still named.** Consullo published its own submission under its own name, so
  concealing whose system this is would be incoherent as well as pointless. What is removed is
  *how the code works*.
* **Abstraction does not reach git history.** The prior version remains in this repository's
  history and this note does not pretend otherwise.

The underlying gap is that no rule existed. See `record/designs/implementer-disclosure.md`.

---

## What was done

The Negative Control Profile (`spec/ncp/ncp-v0.1.md`) was written from AS-01's recorded failure —
a health check that stayed green after the service died, because it exercised a code path that had
not died.

**CORRECTED 2026-08-10, before the finding was cited in outreach.** This sentence, and F1 below,
said the outage lasted **4h37m**. That is not what the source records. AS-01 states the service
*"ran correctly for 4 hours 37 minutes and then died permanently"*, and again that the fault
*"surfaced only after 4h37m of correct operation"*. **4h37m is the period of CORRECT OPERATION
before the failure. The duration of the undetected outage is not stated anywhere in the record.**
The source contains one line that says otherwise — *"4h37m of undetected outage"* — which
contradicts its own two other statements; reconciling it is the implementer's call, not ours.

The error ran in this project's favour: an undetected outage of 4h37m is a worse-sounding fact
than a service that worked for 4h37m and then died. It was caught by external review while
drafting an email that would have asserted it to ten researchers. That is the fourth
self-favouring factual error here in two days, and the fourth caught by someone other than the
gates.

The obvious next question was whether that was one unlucky check or a class, so the requirement
was applied adversarially to Consullo's *existing* checks — not to demonstrate conformance, but to
find checks that cannot fail.

> Every check that produces an assurance signal MUST ship with a negative control — a condition
> under which the check is required to fail — and the attestation MUST record that the control was
> executed and that the check did fail. **A check that has never been observed to fail is not
> evidence that anything works.**

**It was a class.** Four of the five checks assessed pass under the exact condition they exist to
detect. Every negative control was **executed against a deliberately broken build**; nothing below
was inferred from reading source.

| check | negative control | outcome |
|---|---|---|
| port-liveness probe | a process holding the service port that accepts connections and serves nothing | **PASS** |
| responsiveness probe | an endpoint answering HTTP 503 with an *unhealthy* status | **PASS** |
| component-health aggregator, database | the database check disabled by configuration | **PASS** |
| component-health aggregator, dev mode | the database unavailable with development mode on | **PASS** |
| serving-engine liveness canary | the recorded production failure | **FAIL** — conforms |

Attestation: `record/attestations/ncp-2026-08-10-consullo.json`. Verifier:
`tools/verify_negative_control.py`. Reproductions: `spec/ncp/negative-controls/`.

## F1 — the port-liveness probe would have passed through the entire outage

The probe tests that the service port accepts a TCP connection. **Accepting a connection is
something a dead service does.** AS-01's recorded failure state was a process that stayed alive
and kept serving HTTP after its engine died — so this probe would have returned success for the
whole of that undetected period, **whose length the record does not state.**

Executed against a listener that accepts and serves nothing: **the probe reported the port open
and exited 0.** Same structural blindness as the check that caused AS-01, in a different check, in
the same script, still shipping. **The fix that closed AS-01 did not generalise, because nothing
asked it to.**

## F2 — the responsiveness probe reports "responsive" about a service that just said it is not

The probe matches on the *presence* of the status field and never reads its *value*, and it
fetches without failing on an HTTP error status — so a 503 body carrying an explicit *unhealthy*
verdict satisfies it.

Executed against an endpoint returning 503 `{"status":"unhealthy"}`: **the probe reported the
application responsive and exited 0.**

The script as a whole still fails, because a later stage does check properly. **The ordering claim
was tested too:** the full script exits 1 — after printing two green lines from the two checks
that cannot fail. **Ordering is the sole thing between this probe and a false green.** Move it,
reuse it, or make it the readiness probe, and the mitigation vanishes with no diff to the check.

## F3 — a disabled check is indistinguishable from a passing one

Executed with the database check disabled: **the overall verdict stayed healthy and the database
component was absent from the output entirely** — not reported as skipped, simply not there.

A consumer cannot distinguish *"the database is healthy"* from *"the database was never
checked."* This violates **AS-02, Consullo's own submitted pattern**, which requires disclosure of
skipped, suppressed and unsupported checks. The pattern was submitted on 2026-08-06 and is not
implemented in the surface it was drawn from.

## F4 — development mode converts an unavailable database into a healthy verdict

Executed with the database unavailable: **development mode on → overall verdict healthy**, with
the database component reading *unavailable*. **Development mode off, same conditions → overall
verdict unhealthy.**

**CORRECTION — this finding's own claim was wrong, and execution caught it.** The first version
said the response *"does not record that development mode is in force."* It does: a nested
component message names it explicitly. I asserted its absence from reading the verdict logic and
never reading the message string — a smaller instance of the same reading error this whole finding
is about.

The surviving defect is narrower and real: **the top-level verdict is what consumers actually
read.** It selects the HTTP response code, and it is what the responsiveness probe matches on. A
consumer that reads the verdict never reaches the message.

## F5 — the liveness canary conforms, and why

The watchdog canary requests on the sampled decode path — the path that died — rather than the
path a greedy request would take. Its negative control is not hypothetical: it is **the AS-01
production failure itself**, observed, dated and costed.

This is the only check of the five with a demonstrated failure mode, and it has one for a reason
worth stating: **it was rebuilt after the outage its predecessor could not see.** Every other
check here predates that lesson and never received it.

---

## What this establishes

That the failure class generalises **within one codebase**, from the check that failed to four
that were never suspected. The requirement found them in an afternoon.

It also produces the first thing in this record an outside engineer could act on without
consulting its author: *for each of your checks, name the condition under which it must fail, then
go and cause that condition.* Four of five is not a Consullo result — it is a prediction about
what most check suites will return the first time anyone asks.

## What this does not establish

* **That these checks fail this way in production.** They were run on a workstation against
  synthetic broken builds that reproduce the *shape* of AS-01's failure, not the failure itself.
* **That reading source was adequate.** It was not: four of four predictions reproduced, but the
  F4 claim was wrong in a detail only execution surfaced. That is a datum about source-reading as
  evidence, and it is why the profile requires the control to be *run* rather than described.
* **That these four are the worst**, or that five is a representative sample. They were chosen
  because they were reachable.
* **That NCP's controls are the right controls.** N5 — that a control perturbs the capability
  rather than the transport — is a declared field a human must judge. It is the weakest
  requirement in the profile and the most gameable.
* **Anything about Consullo's system.** Every claim here is about its checks.

## The obvious rejoinder, and why it is not enough

*"The port probe is only a first-stage check; the real one runs after it."* True — and irrelevant.
A stage that cannot fail contributes nothing to the assurance the sequence provides, while
consuming the attention of everyone who reads three green lines. **The value of a check is bounded
by the set of failures it can observe**, and for F1 that set does not include the failure that
actually happened.

## Standing under ICP

NCP v0.1 is **Level 0** — a practice note. This application does not raise it. Level 1 needs a
recorded failure *of the profile itself*; Level 2 needs someone outside this project to build a
conforming verifier from the spec text **without asking its author what it meant.** That is the
load-bearing test and it has not been attempted.

**Remediation detail is not published here.** The defect-by-defect fix request, with file paths
and code, was written for the implementer and is held outside this repository.
