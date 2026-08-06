# Codex second-pass review of the T-13 design, 2026-08-06

**Reviewer:** `codex-cli 0.146.0`, `--sandbox read-only`, session *Capture Path*.
**Reviewed:** the design at `6055915`, including §10–11, which are the response to its first pass.
**Asked specifically:** where did the revision OVER-correct?

It answered by **retracting its own first-pass finding E1** — the one the architecture was
rebuilt on. Disposition in `T13-capture-ui-design.md` §12.

---

The revision over-corrects the governance rationale, while under-specifying the controls needed to make quarantine, receipts, and split artifacts reliable.

1. Over-correction; §10.1

- The over-correction is in [§10.2](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:350): “AI-authored instrument” does not mean “AI holds decision authority.” The custodian adopts, runs, inspects, and commits tooling; that is human policy implemented in code. [GOVERNANCE §2–3](/home/reed/git/oagf-track-b/GOVERNANCE.md:44) prohibits unilateral model control, not deterministic gates adopted by the custodian. The evidence supports demoting G2 because its false-positive rate is unknown—not because model-authored code categorically lacks authority. My first-pass E1 overstated that point.

- [§11](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:447) also crosses D-16: it “restates” A6 and adds A11 without recording custodian adoption. The task still requires threshold-based refusal and an unchanged validator in [T13 §What it does/Acceptance](/home/reed/git/oagf-track-b/record/tasks/T13-capture-ui.md:22). Unlike the earlier Pages amendment, §11 has no custodian direction. These are proposed criteria, not revised criteria. See [D-16](/home/reed/git/oagf-track-b/corpus/deficiencies.md:300) and the [round-02 prompt](/home/reed/git/oagf-track-b/record/review-round-02-prompt.md:19).

- The [§10.1](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:339) threat-model decline is correct narrowly: deliberate token insertion is not an accidental clipboard paste, and G2 is now only diagnostic. But invocation ledgers and signatures do not solve B1; they authenticate who emitted the evasive bytes, not whether those bytes defeated the detector.

2. Quarantine relocates the governance problem

[§10.2](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:373) preserves bytes but does not ensure consideration. Nothing requires that quarantine be committed, displayed as outstanding work, reviewed by a deadline, or dispositioned. Indefinite quarantine is de facto exclusion.

A11 only guarantees a write to a directory; it does not guarantee:

- public preservation;
- custodian acknowledgement;
- accept/reject disposition;
- escalation for stale items;
- inclusion in completeness accounting.

The response should enter an immutable `returned_pending_review` state visible in the round view and manifest, with every later disposition preserved. A private side directory is insufficient.

3. Send receipts establish testimony, not delivery

A receipt adds something the manifest lacks: a timestamped custodian assertion about what the custodian believes was sent. It turns plan into contemporaneous testimony. It is not independent delivery evidence.

[§10.5](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:409) is wrong when:

- the receipt is copied from manifest defaults rather than the actual send;
- the wrong account, conversation, party, or attachment was used;
- the provider truncated or transformed the pasted text;
- a retry or second send occurred and the response cannot be bound to one receipt;
- the receipt is reconstructed later;
- its “append-only” JSONL file is edited before or after commit.

It also records a prompt-file hash even though [G2 validation §5](/home/reed/git/oagf-track-b/record/designs/T13-g2-rule-validation.md:119) established that the file contains material never sent. Therefore it still does not hash the delivered bytes. “Records delivery” and “makes history truthful” should read “records the custodian’s delivery attestation.”

4. The artifact split creates an orphan/disagreement failure

Yes. [§10.3](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:382) specifies a “hash-linked” pair but no direction, completeness invariant, cross-check, or atomic write.

Current mechanics expose the gap:

- [`capture_response.py`](/home/reed/git/oagf-track-b/tools/capture_response.py:241) writes raw, contribution, then manifest—no audit artifact and no atomic pair.
- [`validate_provenance.py`](/home/reed/git/oagf-track-b/tools/validate_provenance.py:80) has no capture-audit artifact type.
- P7 is applied only to `artifact_type == "annotation"` in [`validate_file()`](/home/reed/git/oagf-track-b/tools/validate_provenance.py:351), so the claim that the audit “already owes” P7 is currently false.

A contribution could therefore exist without an audit; an audit could reference the wrong digest; or its override could contradict the contribution’s `gate_results`. A hash link proves association and immutability, not semantic agreement. Both artifacts need one transaction plus validator-enforced referential and field invariants.

5. Claims exceeding the evidence

- “Exact predicates … cannot produce a false positive” — [§10.2](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:369). Equality is exact as a string relation, not as proof that the bytes were not genuinely emitted as a response. Normalized equality is especially interpretive.
- “No model decides what the record contains” — [§10.2](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:373). True only if quarantine review is mandatory and enforced.
- “The score separates cleanly enough” — [§10.2](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:378). It separated the measured, non-held-out cases; the validation itself admits the threshold is underdetermined and most positives synthetic.
- “Transactional per capture” — [§10.6](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:425). The described/current write sequence is not transactional; manifest failure leaves raw and provenance committed locally but unanchored.
- “Cannot be the intent” — [§10.7](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:433). That infers authority over an explicit acceptance criterion instead of obtaining an amendment.
- “No path exists” for discard — [A11](/home/reed/git/oagf-track-b/record/designs/T13-capture-ui-design.md:456). The unreviewed/uncommitted-quarantine path still exists operationally.

The common correction is a single durable capture lifecycle—`planned → sent_attested → returned_pending → accepted/rejected`—with event IDs, immutable response bytes, mandatory disposition, and validator-enforced links. That removes the three new loosely coupled records whose agreement is currently assumed.
