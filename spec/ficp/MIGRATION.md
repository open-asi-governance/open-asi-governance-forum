# NCP v0.1 → FICP v0.2 — what changed, and what did not

**2026-08-11.** The profile was renamed because its central term was backwards. This note exists
so nobody has to reconstruct that from a diff.

## Why

A **negative control** checks for a response in the *absence* of the target. The condition this
profile requires — a deliberately introduced fault the check must detect — is analogous to a
**positive** control, which *contains* the target and must elicit a response.

The profile was doing the second and calling it the first, on every page. Any reader from
diagnostics, assay validation or clinical laboratory practice would have understood the term to
mean the opposite of what was meant.

The new name is not *Positive Control Profile*, because this profile supplies no control material:
it **perturbs the subject**. The engineering term for that is **fault injection**.

## What changed

| v0.1 | v0.2 |
|---|---|
| Negative Control Profile (NCP) | Fault-Injection Check Profile (FICP) |
| `ncp_version` | `ficp_version` |
| `positive_run` | `baseline_run` |
| `negative_control` | `fault_injection` |
| *"a control the check survives is a defect"* | *"a `PASS` while the declared fault was present is a **missed fault**"* |
| `spec/ncp/ncp-v0.1.md` | `spec/ficp/ficp-v0.2.md` |
| `tools/verify_negative_control.py` | `tools/verify_fault_injection.py` |

**N1–N7 keep their identifiers** so existing citations stay valid. `N` denotes *normative*, never
*negative*. Only **N3** changed normatively — it now names the failure mode (*missed fault*) rather
than describing the check as "surviving", which was anthropomorphic and ambiguous: a *system* may
survive a fault, desirably, while the check still correctly reports degraded capability.

**N6 is unchanged.**

## What did not change

* **The mechanism.** Same requirement, same seven rules.
* **The evidence already collected.** The four-of-five result stands; those executions were not
  re-run and this note does not pretend they were.
* **ICP standing.** Still **Level 0**. The correction neither resets nor advances it, and an
  implementation of NCP v0.1 does **not** count as an independent implementation of the revised
  text.
* **Novelty.** Unresolved before, unresolved now. The rename establishes nothing.

## Compatibility

**Permanent read compatibility, immediate authoring deprecation.**

* `ncp_version: "0.1"` documents remain valid **forever** and are normalised internally by
  `tools/verify_fault_injection.py`, which prints a deprecation warning.
* New attestations MUST use FICP v0.2.
* A document carrying **both** vocabularies is **refused**. Guessing which the author meant is how
  a rename becomes silent data corruption.
* Old field names are **not** kept as aliases. `negative_control` stays affirmatively misleading
  to exactly the readers whose interpretation matters; compatibility belongs at the version
  boundary, not baked into the wire format forever.
* No historical attestation or published fixture was rewritten. `spec/ncp/fixtures/` is retained
  in full and still used to regression-test the legacy path.
* `tools/verify_negative_control.py` remains as a deprecated entry point so published commands do
  not break.

## What would have been dishonest

Renaming quietly. Every canonical page carries a dated correction saying the profile was
originally published under a name that reversed standard terminology, and that **the rename does
not establish novelty, correctness, coverage or independent validation.**

The outreach sent on 2026-08-10 used the old name. That record is **not** edited to pretend
otherwise; a correction goes out in the existing threads instead.
