# NCP v0.1 applied to Consullo — four of five checks survive their own negative controls

**Result: NON-CONFORMING. 4 violations.** 2026-08-10.

The Negative Control Profile was written this afternoon from AS-01's recorded failure — a health
check that stayed green through a **4h37m** outage because it issued a greedy request while the
code that died was on the sampled path. The obvious next question is whether that was one unlucky
check or a class. So the requirement was applied adversarially to Consullo's *existing* checks:
not to demonstrate conformance, but to find checks that cannot fail.

**It was a class.** Four of the five checks assessed pass under the exact condition they exist to
detect.

## The requirement

> Every check that produces an assurance signal MUST ship with a negative control — a condition
> under which the check is required to fail — and the attestation MUST record that the control was
> executed and that the check did fail. **A check that has never been observed to fail is not
> evidence that anything works.**

Attestation: `record/attestations/ncp-2026-08-10-consullo.json`. Verifier:
`tools/verify_negative_control.py`. Spec: `spec/ncp/ncp-v0.1.md`.

---

## F1 — `connectivity_check` would have passed through the entire AS-01 outage

```bash
if nc -z localhost 8080 2>/dev/null; then echo "Port 8080 is open"; return 0; fi
```

`nc -z` succeeds if **anything** holds the socket. AS-01's recorded failure was precisely *"the
error escalated and killed the engine permanently while the process stayed alive and kept serving
HTTP."* A live process holding port 8080 is the failure state.

**This check would have returned 0 for all 4 hours 37 minutes**, for the same structural reason
the greedy health check did, in a different check, in the same script, still shipping today. The
fix that closed AS-01 did not generalise, because nothing asked it to.

## F2 — `responsiveness_check` reports "responsive" about a service that just said it is not

```bash
response=$(curl -s --max-time $TIMEOUT "$HEALTH_URL" 2>/dev/null || echo "")
if [ -n "$response" ] && echo "$response" | grep -q '"status"'; then
    echo "Application is responsive"; return 0
```

`HealthServlet` returns **HTTP 503** with body `{"status":"unhealthy", …}` when a component
fails. `curl -s` without `-f` returns the body on 503. The test then greps for `"status"` — **the
key, never the value.** So an explicitly unhealthy service satisfies the responsiveness check, and
the script prints *"Application is responsive."*

The script as a whole still fails, because `health_check()` runs afterwards with `curl -f`.
**Ordering is the only thing standing between this check and a false green.** Move it, reuse it,
or make it the readiness probe, and the mitigation vanishes with no diff to the check itself.

## F3 — a disabled check is indistinguishable from a passing one

```java
if (ConfigurationManager.isDatabaseHealthCheckEnabled()) {
    components.put("database", getDatabaseHealth());
    …
}
```

When database health checking is disabled, `components` simply **omits the key** and the overall
status stays `healthy`. A consumer reading the response cannot distinguish *"the database is
healthy"* from *"the database was never checked."*

This violates **AS-02 — Consullo's own submitted pattern**, which requires disclosure of skipped,
suppressed and unsupported checks. The pattern was submitted to this forum on 2026-08-06 and is
not implemented in the endpoint it was drawn from.

## F4 — in development mode, "healthy" can mean "the database is down and we decided that's fine"

```java
if (!"healthy".equals(dbStatus) &&
  !(ConfigurationManager.isDevelopmentMode() && "unavailable".equals(dbStatus))) {
 isHealthy = false;
}
```

An unavailable database is acceptable in development mode — a defensible product decision — but
**the response does not record that development mode is in force.** The mode is what makes
`healthy` mean something different, and it is the one thing a consumer cannot see.

## F5 — the watchdog canary conforms, and why

`trtllm_watchdog.run_canary` posts at `"temperature": 0.7`, with the reasoning inline in the
source: temperature > 0 reaches `_prepare_probs_with_temperature → flashinfer softmax_op →
sampling_from_probs_op`, which is the code that died. Its negative control is not hypothetical —
it is **the AS-01 production failure itself**, observed, dated, and costed.

This is the only check of the five with a demonstrated failure mode, and it has one for a reason
worth stating: **it was rebuilt after the outage its predecessor could not see.** Every other
check here predates that lesson and never received it.

---

## What this establishes

That the failure class generalises **within one codebase**, from the check that failed to four
that were never suspected. The requirement found them in an afternoon, from source reading, with
no instrumentation.

It also produces the first thing in this record an outside engineer could act on without
consulting its author: *for each of your checks, name the condition under which it must fail, then
go and cause that condition.* Four of five is not a Consullo result — it is a prediction about
what most check suites will return the first time anyone asks.

## What this does not establish

* **These outcomes were derived by reading source, not by running the checks against broken
  builds.** That is disclosed in the attestation's `skipped` field, and it is exactly the kind of
  inference NCP exists to distrust. F1–F4 are strongly argued from code paths; they are not
  executed evidence. **Running them is the next step and would change their status.**
* **That these four are the worst ones**, or that the five assessed are a representative sample.
  They were chosen because they were reachable.
* **That NCP's controls are the right controls.** N5 — that a control perturbs the capability
  rather than the transport — is a declared field a human must judge. It is the weakest
  requirement in the profile and the most gameable.
* **Anything about Consullo's system.** Every claim here is about its checks.

## The obvious rejoinder, and why it is not enough

*"connectivity_check is only a first-stage probe; the real check runs after it."* True — and
irrelevant to the requirement. A stage that cannot fail contributes nothing to the assurance the
sequence provides, while consuming the attention of everyone who reads the log and sees three
green lines. **The value of a check is bounded by the set of failures it can observe**, and for
F1 that set does not include the failure that actually happened.

## Standing under ICP

NCP v0.1 is **Level 0** — a practice note. This application does not raise it. Level 1 needs a
recorded failure *of the profile itself*; Level 2 needs someone outside this project to build a
conforming verifier from `spec/ncp/ncp-v0.1.md` **without asking its author what it meant.** That
is the load-bearing test and it has not been attempted.
