#!/usr/bin/env python3
"""The hand-authored deficiency census, and the one-shot script that emits it.

    python3 tools/author_deficiency_census.py

NOT part of the maintenance path -- `tools/rebuild.py` does not run this. It is
committed because the judgements in CENSUS below are the actual work, and they
should be reviewable as a diff rather than existing only as a generated JSON
blob whose provenance nobody can see.

The classifications are a MODEL'S JUDGEMENT, authored by a party to the record
being classified. Re-running this regenerates the artifact from them and
re-stamps every section hash, which silently discards any drift the checker
would otherwise have caught -- so once the artifact is committed, prefer
`tools/check_register.py --restamp <ID>` after actually re-reading the entry.
Use this only to add entries or revise a classification deliberately.
"""
import hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MD = REPO / "corpus/deficiencies.md"

ANNOTATOR = "actor_repository_annotator_invocation"
REVIEW = "actor_designated_review_round_invocation"
EXTERNAL = "actor_external_adversarial_reviewer"
OPERATOR = "actor_human_operator"

NOT_REPAIRABLE = "affected_object_not_repairable"
FULL = "affected_object_fully_repairable_by_supersession"
PARTIAL = "affected_object_partially_repairable_by_supersession"
RERUN = "affected_measurement_repairable_only_by_rerun"
IF_RECOVERED = "affected_object_repairable_only_if_missing_evidence_recovered"

IMPOSSIBLE = "remediation_impossible_for_affected_object"
NOT_STARTED = "remediation_not_started"
PARTIALLY = "remediation_partially_applied"
UNVERIFIED = "remediation_applied_not_verified"
VERIFIED = "remediation_verified"

PC_NONE = "prospective_control_not_required"
PC_REQ = "prospective_control_required_not_implemented"
PC_IMPL = "prospective_control_implemented_not_validated"
PC_VALID = "prospective_control_validated"

REGISTER_COMPILATION = "corpus/deficiencies.md, compiled 2026-08-05 (register commit)"
RR01 = "corpus/raw/review-round-01/"
RR02 = "corpus/raw/review-round-02/"

def art(ctx, date, where, evidence, label=None):
    d = {"actor_context": ctx, "date_utc": date, "where": where, "evidence_class": evidence}
    if label:
        d["actor_label"] = label
    return d

def obj(o, rep, rem, note=None):
    d = {"object": o, "repairability": rep, "remediation_state": rem}
    if note:
        d["note"] = note
    return d

PRESERVED = "origin_supported_by_preserved_artifact"
REGISTER_ONLY = "origin_asserted_in_register_only"

# Founding-record provenance gaps D-01..D-06: all first written down in the register
# itself, by the annotator. No earlier preserved articulation exists, so the origin
# evidence is the register, not something it cites.
def founding_gap(where_note, objects, pc, mech=None):
    e = {
        "finding_state": "finding_active",
        "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY,
                                  "Claude Code (Anthropic)"),
        "affected_objects": objects,
        "prospective_control": {"state": pc},
    }
    if mech:
        e["prospective_control"]["mechanism"] = mech
    return e

RAW = "corpus/raw/initial-transcript.txt (the founding record)"

CENSUS = {
"D-01": founding_gap(None,
    [obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE, "The sessions are gone; no version can be recovered.")],
    PC_IMPL, "validate_provenance.py P4 rejects placeholder version identifiers; no test asserts it does."),
"D-02": founding_gap(None,
    [obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE)],
    PC_IMPL, "Sampling parameters are a required capture field; null demands a stated reason (P5)."),
"D-03": founding_gap(None,
    [obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE, "Timestamps are self-reported where present at all.")],
    PC_IMPL, "capture_response.py requires --captured-utc, recorded at capture rather than reconstructed."),
"D-04": founding_gap(None,
    [obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE)],
    PC_IMPL, "System instructions are required, or a withholding reason is required."),
"D-05": founding_gap(None,
    [obj("The elided operator prompt at raw 1902", IF_RECOVERED, NOT_STARTED,
         "The operator may recall and attest it, flagged as reconstructed. Not done.")],
    PC_IMPL, "Exact prompt text is a rejection-level required field at capture."),
"D-06": founding_gap(None,
    [obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE, "Whether output was trimmed or reordered during hand-compilation is unrecorded.")],
    PC_IMPL, "edit_status is a required capture field."),

"D-07": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-01",
         "what": "Separated citability from distributional inference. A single sample IS citable as an artifact of one invocation; it cannot characterise a stable position. Also corrected 'adopted standard' to custodian-adopted policy, and noted five is a floor rather than a sufficiency proof."},
        {"actor_label": "ChatGPT", "round": "review-round-02",
         "what": "The capture tool and schema had gone on enforcing the superseded non-citable label on every capture; corrected with the document."}],
    "affected_objects": [
        obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE, "Permanent for the founding record. The sessions are gone."),
        obj("tools/capture_response.py and the contribution schema", FULL, VERIFIED,
            "Were enforcing the superseded label. Corrected in review round 02.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "k >= 5 with computed variance for distributional claims; capture records k and variance."},
},
"D-08": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE, "Phase tags were invented mid-record and applied by two parties to themselves only."),
        obj("corpus/artifacts/segments.json phase tags", PARTIAL, VERIFIED,
            "Retro-classification is marked as annotation, never as testimony.")],
    "prospective_control": {"state": PC_IMPL, "mechanism": "Phase tag is a required capture field."},
},
"D-09": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-01",
         "what": "The evidence does not authenticate three distinct underlying MODELS. Defensible statement: at least three materially distinct or unresolved Anthropic invocation identities merged under 'Claude'."},
        {"actor_label": "Grok", "round": "review-round-02",
         "what": "Asked that propagation into the consolidated rankings be enumerated in the register, not only noted in segments.json. Valid half accepted; the overstated half (that it appeared nowhere) corrected."},
        {"actor_label": "Claude Fable 5", "round": "review-round-01",
         "what": "The register caught others merging the Claude identities and MISSED Claude merging itself at raw 2055-2088 -- the asymmetry a same-provider annotator would be expected to produce."}],
    "affected_objects": [
        obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE,
            "The merged labels are in the canonical record and it is never edited."),
        obj("corpus/artifacts/segments.json identity annotations", FULL, VERIFIED,
            "Corrected; the raw file was left unedited."),
        obj("Grok's consolidated ranking (S-17) and any cross-model convergence claim over it",
            PARTIAL, PARTIALLY,
            "Annotated as contaminated by the merge. The downstream convergence claims are weakened, not repaired.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "CONTRIBUTING identity rule: a distinct model or invocation surface is a distinct identity, never merged."},
},
"D-10": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-01",
         "what": "'repudiated' was the wrong status and contradicted GOVERNANCE 5.1, where repudiation is a right of the party rather than a classification the annotator may apply. Now 'invocation integrity disputed'. Also: because one of 39 segments is duplicated or missing, every aggregate requires an explicit exclusion rule."}],
    "affected_objects": [
        obj(RAW + " segment at raw 2375", NOT_REPAIRABLE, IMPOSSIBLE,
            "Either Grok's response was never captured or a paste error occurred. Unrecoverable either way."),
        obj("attribution_status for that segment", FULL, VERIFIED,
            "Set to 'invocation integrity disputed' rather than the annotator-applied 'repudiated'."),
        obj("Every segment-count aggregate in the corpus", PARTIAL, PARTIALLY,
            "Requires an explicit exclusion rule, per ChatGPT. Not uniformly applied.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "The same paste-substitution failure recurred live during review round 01. Track B's capture path (T-13) addresses it; not yet landed."},
},
"D-11": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-01",
         "what": "'Self-selected' corrected to 'operator-selected'. And unanimity DID descriptively occur; the defect is its external validity, not its occurrence."},
        {"actor_label": "Claude Fable 5", "round": "review-round-01",
         "what": "Supplied the estimator n_eff = n / (1 + (n-1)p); at p = 0.7, four models yield n_eff = 1.3. Also named ballot-structure convergence pressure as distinct from sycophancy."},
        {"actor_label": "Gemini", "round": "review-round-01",
         "what": "Named the repeated package-review prompts 'a hydraulic press toward convergence', and that both unanimity assertions were authored by a participant inside its own output."}],
    "affected_objects": [
        obj("Every consensus claim in the corpus", PARTIAL, PARTIALLY,
            "Carried as a standing epistemic caveat in the README. n_eff remains unknown because p is unmeasured."),
        obj("The 'unanimous multi-model consensus' assertions at raw 2207 and 2479", NOT_REPAIRABLE, IMPOSSIBLE,
            "Authored by a participant inside its own output. Recorded, not removed.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "Consensus claims must state invocation conditions. Measuring p, which would make n_eff computable, has not been done."},
},
"D-12": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj(RAW, NOT_REPAIRABLE, IMPOSSIBLE, "Immaterial to substance; recorded because a project premised on exact attribution should correct even immaterial identity drift."),
        obj("corpus/artifacts/segments.json identity labels", FULL, VERIFIED)],
    "prospective_control": {"state": PC_IMPL, "mechanism": "Identities are recorded per contribution rather than typed per mention."},
},
"D-13": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj("Every attribution in the repository", NOT_REPAIRABLE, NOT_STARTED,
            "No signature in this record is cryptographically verifiable. Gemini's 'signatures' entry is a plaintext self-assertion with no key, algorithm or verifier."),
        obj("Future commits and artifacts", FULL, NOT_STARTED,
            "Track D owns this. Signing must exist before an invocation ledger can rest on it.")],
    "prospective_control": {"state": PC_REQ, "mechanism": "Track D, task T-16. Blocked on custodian key decisions."},
    "remediation_effort": {"estimate": "remediation_effort_medium",
        "basis": "Key generation and registration are custodian decisions a session must not take unilaterally."},
},
"D-14": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-01",
         "what": "Reframed: the original schema never defined context_models_present, so applying CONTRIBUTING's later meaning retrospectively imposes semantics the field never had. The correct charge is schema ambiguity. But the DEEPER defect was understated -- an unsupported role attribution that inflated the apparent membership of a body whose membership was the record's most contested claim."},
        {"actor_label": "Claude Fable 5", "round": "review-round-01",
         "what": "Concurred on the reframing to schema ambiguity."}],
    "affected_objects": [
        obj("The member / secretary / maintainer role attributions in " + RAW, NOT_REPAIRABLE, IMPOSSIBLE,
            "They stand as historical fact. The raw transcript is canonical and is not edited."),
        obj("The register's original 'factual misstatement' characterisation", FULL, VERIFIED,
            "Reframed as schema ambiguity plus unsupported role attribution."),
        obj("'Produced zero recorded output'", FULL, VERIFIED,
            "No longer true. QCP v0.1 retires two roles on measured capability grounds -- the canonical record does not fit the 24576-token serving window at all -- and records the one role the model can hold. Its first contribution is a pre-registered, refuted prediction.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "context_models_present now lists only models that produced output; QCP governs role claims going forward."},
},
"D-15": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-05", REGISTER_COMPILATION, REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj("The predecessor exchange the record's first substantive entry cites", IF_RECOVERED, NOT_STARTED,
            "Remediable if the prior exchange is located and committed as a predecessor artifact.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "Prior context supplied is a required capture field going forward; it does not recover this one."},
},

# --- the six first articulated in preserved review-round submissions -------------
"D-16": {
    "finding_state": "finding_active",
    "first_articulation": art(REVIEW, "2026-08-05", RR01 + "chatgpt-01.md", PRESERVED, "ChatGPT (OpenAI)"),
    "affected_objects": [
        obj("Every document that said the founding record 'adopted' contributor proposals", FULL, VERIFIED,
            "Corrected during review round 01. The register itself committed this defect, which is the clearest vindication of running the round."),
        obj("The absence of any collective ratification procedure", NOT_REPAIRABLE, NOT_STARTED,
            "Nothing in this project has ever reached collective ratification, and no procedure exists to reach it.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "Four-level distinction -- proposed / supported by ballots / adopted by custodian / collectively ratified -- used throughout. No mechanical check enforces it."},
},
"D-17": {
    "finding_state": "finding_active",
    "first_articulation": art(REVIEW, "2026-08-05", RR01 + "chatgpt-01.md", PRESERVED, "ChatGPT (OpenAI)"),
    "affected_objects": [
        obj("Documents presenting governance, ASP design, prediction methodology or provenance rules as ballot-settled",
            FULL, VERIFIED,
            "The ballots addressed exactly two propositions: the naming architecture and the meaning of 'Aligned'.")],
    "prospective_control": {"state": PC_IMPL, "mechanism": "Every consensus claim must delimit the proposition consensus was obtained on."},
},
"D-18": {
    "finding_state": "finding_active",
    "first_articulation": art(REVIEW, "2026-08-05", RR01 + "chatgpt-01.md", PRESERVED, "ChatGPT (OpenAI)"),
    "affected_objects": [
        obj("Every author label in the corpus", NOT_REPAIRABLE, IMPOSSIBLE,
            "Operator-applied labels and model self-descriptions. No provider-signed export, API response id, authenticated capture log or cryptographic binding exists. Applies recursively to the review rounds themselves."),
        obj("Future captures", FULL, NOT_STARTED, "Forward: capture provider-signed evidence. Not implemented.")],
    "prospective_control": {"state": PC_REQ, "mechanism": "Depends on D-13 signing and on provider-side capabilities not currently used."},
},
"D-19": {
    "finding_state": "finding_active",
    "first_articulation": art(REVIEW, "2026-08-05", RR01 + "chatgpt-01.md", PRESERVED, "ChatGPT (OpenAI)"),
    "affected_objects": [
        obj("Annotations S-10 and S-24 describing repeated prompts as controlled comparisons", FULL, VERIFIED,
            "They are standardised prompts. System instructions, prior context, configurations, provider policies and sampling were uncontrolled or unknown.")],
    "prospective_control": {"state": PC_IMPL, "mechanism": "The distinction is now stated; no mechanical check enforces the vocabulary."},
},
"D-20": {
    "finding_state": "finding_active",
    "first_articulation": art(REVIEW, "2026-08-05", RR01 + "claude-fable-5-01.md", PRESERVED, "Claude Fable 5 (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-02",
         "what": "An earlier version said the header 'on its face attributes' the contribution to the operator. It does not; it marks a prompt boundary. The defect is the ABSENCE of a response-author label, not a false attribution."}],
    "affected_objects": [
        obj(RAW + " at raw 1904-2050", NOT_REPAIRABLE, IMPOSSIBLE, "The contribution carries no author label in the raw record."),
        obj("segments.json author_label_in_raw: 'ChatGPT'", FULL, VERIFIED,
            "False as a description of the raw file, and a violation of this project's own annotation-versus-testimony distinction. The ChatGPT attribution is a well-supported inference, now recorded as one.")],
    "prospective_control": {"state": PC_IMPL, "mechanism": "author_label_in_raw and author_label_absent are distinct fields."},
},
"D-21": {
    "finding_state": "finding_active",
    "first_articulation": art(REVIEW, "2026-08-05", RR01 + "claude-fable-5-01.md", PRESERVED, "Claude Fable 5 (Anthropic)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "ChatGPT", "round": "review-round-02",
         "what": "An earlier version concluded no such claim is 'supportable anywhere in this record', which exceeds what missing timestamps establish. Content references, an authenticated session record or a contemporaneous attestation could support one."}],
    "affected_objects": [
        obj("Any chronology claim drawn from file order", NOT_REPAIRABLE, IMPOSSIBLE,
            "Not supportable without identifying which four responses are counted and supplying independent ordering evidence."),
        obj("ASP 2's reliance on 'all four ballots now carry' the reservation", PARTIAL, PARTIALLY)],
    "prospective_control": {"state": PC_REQ, "mechanism": "Capture-time UTC stamps are required going forward; they do not recover this ordering."},
},

# --- instrument defects ----------------------------------------------------------
"D-22": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-22", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "investigation_triggered_by": {"actor_context": "actor_other_contributor_invocation",
        "what": "External literature: 'Not All Flips Are Conformity' (arXiv:2606.00820), which reports spontaneous instability as a large baseline source of position change and uses three counterfactual arms where this method specifies two."},
    "affected_objects": [
        obj("The causal attribution in local-round-01 and record/methods/locating-divergence.md", RERUN, NOT_STARTED,
            "The measurement stands and the numbers are correct. What is unsupported is the causal claim: nothing in the design separates the semantic content of peers' verdicts from everything else the added prompt text changes."),
        obj("phase_susceptibility as a reported quantity", PARTIAL, PARTIALLY,
            "Reported as an upper bound on influence rather than a measurement of it, until the placebo arm is run.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "A placebo arm -- Phase-2 with the peer block replaced by content-neutral filler of comparable length -- plus a self-reflection arm where a method re-examines rather than draws independently."},
    "remediation_effort": {"estimate": "remediation_effort_low",
        "basis": "One extra arm on an existing harness, no new capability. Now gated behind D-28: the apparatus itself must be shown repeatable first."},
},
"D-23": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-23", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj("local-round-03, all three arms", RERUN, VERIFIED,
            "local-round-04 IS that re-run, on a clean prompt: 0.000 -> 1.353 bits, a gap far above the noise floor. The contaminated run stands in the record as run."),
        obj("The 0/59 acceptance rate as independent corroboration of Claude's argument", NOT_REPAIRABLE, IMPOSSIBLE,
            "The contamination runs in precisely the direction that flatters the annotator's own provider's contribution."),
        obj("Every other Phase-1 claim in the corpus", PARTIAL, NOT_STARTED,
            "All are exposed to instruction, schema and enum-label contamination, and NONE has been audited for it.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "A Phase-1 arm must certify that instruction, schema and enum labels encode no prior party's conclusion -- or disclose that they do. No mechanical check exists."},
},
"D-24": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-24", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj("cites_non_persistence and fields of its kind in local-round-03", NOT_REPAIRABLE, IMPOSSIBLE,
            "The measured field understates the real rate by roughly 20 points. A self-report cannot be made reliable after the fact."),
        obj("P-0010", NOT_REPAIRABLE, IMPOSSIBLE,
            "Rested entirely on such a field; unscorable on its merits, independently of its resolution-limit failure."),
        obj("The free text of those responses", RERUN, NOT_STARTED,
            "Survives and could be coded deterministically, subject to D-25's validation requirement.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "Never ask a model to classify its own reasoning; code free text deterministically instead. Implemented in tools/code_freetext.py -- and D-25 is what happened to the first such coder."},
},
"D-25": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-25", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj("The first unary-versus-relational coding rule", FULL, VERIFIED,
            "Scored 9/10 and 10/10 where the truth was 0/10 and 2/10, by matching vocabulary that appears in the SPECIFICATION TEXT the reviewer quotes back. Both the rejected and adopted rules are published so the correction is checkable."),
        obj("P-0017", FULL, VERIFIED,
            "Would have been scored REFUTED on a broken instrument. Caught before scoring; the verdict is robust to all three rule variants, 0/10 every time.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "A coding rule must be validated against a hand-checked subset and the validation committed, before it scores anything. The validation is by the same party that wrote the rule and has not been independently checked."},
},
"D-26": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-26", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "investigation_triggered_by": {"actor_context": OPERATOR, "actor_label": "Stephen Reed",
        "what": "Asked why temperature 0.7 was chosen. The question prompted the work; it is recorded as a trigger rather than as the finding, because the preserved substantive articulation is the annotator's."},
    "affected_objects": [
        obj("Every entropy figure in the corpus", PARTIAL, PARTIALLY,
            "Now reported conditionally -- 'H = 0.99 bits at T = 0.7' -- rather than bare. The figures themselves are unchanged and remain properties of the model AT 0.7, not of the model."),
        obj("The temperature-sensitivity check owed at 0.3 / 0.7 / 1.0", RERUN, NOT_STARTED,
            "NOT RUN. This deficiency stays open until it is. If a conclusion moves across that range, every entropy claim in this corpus is softer than stated.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "Temperature fixed by declared policy at 0.7 for all measurement runs; any departure declared in the spec before the run."},
    "remediation_effort": {"estimate": "remediation_effort_medium",
        "basis": "One probe replicated at three temperatures, but it needs the exclusive inference host and is downstream of D-28: repeatability must be established before sensitivity can be assessed."},
},
"D-27": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-27", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "affected_objects": [
        obj("The compliance field across local-round-07", NOT_REPAIRABLE, IMPOSSIBLE,
            "At most a quarter of the modal answers demonstrably mean what the field claims. 25% describe the opposite of their label. Accurate answers landed on opposite labels, so the categorical result cannot be recovered."),
        obj("The free text of those 75 responses", RERUN, NOT_STARTED,
            "Survives and could be re-coded against a referent-naming scheme.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "Every enum value must name its referent in the value itself, and any field whose meaning depends on a referent stated only in prose must be validated against free text on a subset BEFORE the categorical result is used. No mechanical check enforces this."},
},
"D-28": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06", "corpus/deficiencies.md D-28", REGISTER_ONLY, "Claude Code (Anthropic)"),
    "investigation_triggered_by": {"actor_context": OPERATOR, "actor_label": "Stephen Reed",
        "what": "Asked for a temperature-sensitivity check. The check found something larger than the thing it was sent to look for. A first-order defect surfaced by a question about a second-order parameter."},
    "affected_objects": [
        obj("The seed field in every provenance artifact", NOT_REPAIRABLE, VERIFIED,
            "Marked non-reproducing in the schemas. It records what was requested, not a guarantee. Same class as D-01's placeholder version identifier: a field asserting a property the system does not have."),
        obj("local-round-01's 0.1815-bit phase effect", NOT_REPAIRABLE, IMPOSSIBLE,
            "VOID. 2.6x smaller than the 0.4649-bit run-to-run noise floor measured at identical settings."),
        obj("P-0008's evidence", NOT_REPAIRABLE, IMPOSSIBLE, "Annotated as void."),
        obj("The corpus-wide reproducibility claim and QCP 3", FULL, VERIFIED,
            "WITHDRAWN rather than repaired. The corpus now claims settings are RECORDED, which is true and weaker."),
        obj("The serving configuration (moe_config.disable_finalize_fusion, top-k 8 > 2)", FULL, NOT_STARTED,
            "Root-caused to a vendor-documented non-deterministic kernel fusion. Remedy is a serving-config change under Codex review, because the profile in force has a documented OOM history and the fusion exists for throughput. Track C.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "Every measurement round includes a test-retest arm and reports the run-to-run gap alongside the effect; no effect smaller than the noise floor may be reported as an effect. Not yet mechanised."},
    "remediation_effort": {"estimate": "remediation_effort_high",
        "basis": "A serving-configuration change on a profile with a documented OOM history, plus retro-annotation of five rounds, plus a test-retest arm added to the harness. Holds the exclusive inference host."},
    "invalidates": ["P-0008's evidence", "local-round-01's phase effect",
                    "Any comparison resting on a difference below ~0.5 bits",
                    "Any claim drawn from a near-50% modal split"],
},
"D-29": {
    "finding_state": "finding_active",
    "first_articulation": art(EXTERNAL, "2026-08-06",
        "Codex design review of an unrelated change, quoted in corpus/deficiencies.md D-29; confirmed by experiment before filing",
        PRESERVED, "Codex (OpenAI)"),
    "affected_objects": [
        obj("corpus/MANIFEST.sha256 as an integrity mechanism", FULL, VERIFIED,
            "Verification is now the default; --add is append-only and checks lineage against HEAD; --force-rewrite is the only mode that can change a hash. Verified by re-running the original tamper experiment: what exited 0 now exits 1 and names the file."),
        obj("The period during which the check did not run", NOT_REPAIRABLE, IMPOSSIBLE,
            "The repair is prospective only. It cannot establish that raw material was unmodified while the anchor was unenforced. No tampering is alleged or detected; the defect is that the corpus could not have detected it."),
        obj("validate_provenance.py reporting a pass when jsonschema was absent", FULL, VERIFIED,
            "Now an error rather than a warning. Track B fixed the same fail-open independently on session/capture."),
        obj("The published page, which no CI check regenerated or compared", FULL, UNVERIFIED,
            "CI now runs the maintenance path on a clean checkout and requires the committed page to match byte for byte. THIS HAS NEVER RUN -- it fires on the first merge to main.")],
    "prospective_control": {"state": PC_VALID,
        "mechanism": "tools/test_integrity.py, 23 cases, each an attack that worked on 2026-08-06, run in CI. A repair described in a commit message is a claim; a repair the build re-runs is a control."},
    "remediation_effort": {"estimate": "remediation_effort_low",
        "basis": "The verification code was correct and complete the whole time. It was simply never reached by the path anyone runs."},
},
"D-31": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06",
        "corpus/deficiencies.md D-31 (filed as D-29 by the Capture Path session; renumbered at merge, see D-32)",
        REGISTER_ONLY, "Claude Code (Capture Path session, Track B)"),
    "affected_objects": [
        obj("Every fix in this repository designed against a single external review", PARTIAL, PARTIALLY,
            "A review is a single sample from an unknown distribution, and was being treated as a finding. The session that filed this is the party it inconveniences."),
        obj("This session's own reliance on external review", PARTIAL, NOT_STARTED,
            "Track A designed and verified the D-29 repair against one Codex pass, then a second pass found four further defects in it -- which is this deficiency's thesis demonstrated rather than argued.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "Requirement 2 of the entry: ask a reviewer what is wrong in EITHER direction rather than naming an expected error. Used to produce the CI review that found D-34."},
},
"D-32": {
    "finding_state": "finding_active",
    "first_articulation": art(OPERATOR, "2026-08-06",
        "the collision itself, at the custodian's merge -- not by review", PRESERVED, "Stephen Reed"),
    "affected_objects": [
        obj("Deficiency identifiers already cited from tools, HANDOFF, the specifications and the live site",
            FULL, VERIFIED,
            "Track A's D-29 (the manifest) and Track B's D-29 (external reviewers as oracles) were filed the same day. Both read the register at a moment when D-28 was highest and both incremented; the correct procedure was followed by both and produced a collision anyway. Track B's was renumbered to D-31."),
        obj("The absence of any allocation procedure", FULL, VERIFIED,
            "check_register.py R5 now checks the other serially-numbered namespaces -- P-NNNN and T-NN -- for the same class of collision, before it happens in a registry where ICP 5 makes it worse.")],
    "prospective_control": {"state": PC_VALID,
        "mechanism": "R5 in tools/check_register.py, run by tools/rebuild.py. R3 caught the original collision at merge, and R3 had been written days earlier by one of the two colliding sessions for an unrelated reason."},
},
"D-33": {
    "finding_state": "finding_active",
    "first_articulation": art(EXTERNAL, "2026-08-06",
        "external design review of the CI arrangement, confirmed by reproduction", PRESERVED, "Codex (OpenAI)"),
    "affected_objects": [
        obj("A published page carrying a prompt hash that did not match the committed prompt", FULL, VERIFIED,
            "The design document recorded as acceptance criterion A10 that build_capture_ui.py runs in rebuild.py. It was never added; STEPS held five entries and none was that generator."),
        obj("rebuild.py's step list", FULL, VERIFIED, "The generator is now wired in."),
        obj("The window in which the damage was committed and pushed", NOT_REPAIRABLE, IMPOSSIBLE,
            "The annotator had already pushed before the review returned.")],
    "prospective_control": {"state": PC_IMPL,
        "mechanism": "The generator runs in the build. An acceptance criterion asserting that a tool is in the build is not evidence that it is -- the same shape as D-29."},
},
"D-34": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06",
        "found while restructuring CI for D-33, demonstrated on a clone before filing", PRESERVED),
    "affected_objects": [
        obj("The append-only claim over corpus/raw/", FULL, VERIFIED,
            "The manifest proves the raw tree matches its hashes AT THE TIP, so a single commit that edits a raw file and re-anchors the manifest around the new bytes is perfectly self-consistent and passes every check."),
        obj("D-29's repair, which does not cover this", PARTIAL, VERIFIED,
            "Track A's lineage check compares the working manifest against HEAD's. A commit that changes both together is consistent at HEAD, so the edit remains invisible to it. This is the same defect one level up.")],
    "prospective_control": {"state": PC_VALID,
        "mechanism": "CI walks each newly reachable commit in a push and rejects modification or deletion under corpus/raw/; additions are allowed. Enforced across history rather than at the tip."},
    "remediation_effort": {"estimate": "remediation_effort_low",
        "basis": "A per-commit walk in the workflow. The expensive part was noticing that the tip proves less than it appears to."},
},
"D-30": {
    "finding_state": "finding_active",
    "first_articulation": art(ANNOTATOR, "2026-08-06",
        "corpus/deficiencies.md D-30, while bounding D-29's scope", REGISTER_ONLY,
        "Claude Code (Corpus Surface session, Track A)"),
    "narrowed_or_corrected_by": [
        {"actor_label": "Codex (OpenAI)", "round": "implementation review of the D-29 repair",
         "what": "The entry as filed claimed freetext_coding also recorded a bare path. It does not -- it records {path, sha256, bytes} and validate_provenance verifies it. The entry doubled the scope of a defect IN THE ENTRY ANNOUNCING THAT SCOPE, generalised from one artifact family without testing. Corrected visibly."}],
    "affected_objects": [
        obj("solicitation_summary.raw_samples across all eight local rounds", FULL, NOT_STARTED,
            "Records a bare path. Repair specified in the entry; tools/schemas/ is Track D's territory."),
        obj("The binding between a reported entropy and the bytes it was computed from", NOT_REPAIRABLE, NOT_STARTED,
            "Backfilled hashes will certify bytes AS OF THE BACKFILL, never as of capture. This repair cannot retroactively prove what those files contained when the measurements were run."),
        obj("Exposure to a lone tamper", FULL, VERIFIED,
            "Closed by D-29's repair: the manifest walks all of corpus/raw by tree, so those files are covered even without an artifact-level hash. Confirmed by experiment.")],
    "prospective_control": {"state": PC_REQ,
        "mechanism": "solicitation_summary records {path, sha256, bytes} and validate_provenance checks it, as it already does for contributions and freetext_coding."},
    "remediation_effort": {"estimate": "remediation_effort_low",
        "basis": "A schema change plus a backfill from the current manifest. Blocked only on track ownership, not on difficulty."},
},
}

def main():
    text = MD.read_text(encoding="utf-8")
    sections = {}
    for part in re.split(r"(?m)^(?=### D-\d+ — )", text)[1:]:
        m = re.match(r"### (D-\d+) — (.+)\n", part)
        if not m:
            continue
        body = re.split(r"(?m)^## ", part)[0]
        sections[m.group(1)] = (m.group(2).strip(),
                                hashlib.sha256(body.encode("utf-8")).hexdigest())

    missing = set(sections) - set(CENSUS)
    extra = set(CENSUS) - set(sections)
    if missing or extra:
        print(f"census/markdown mismatch. missing={sorted(missing)} extra={sorted(extra)}", file=sys.stderr)
        return 1

    entries = []
    for entry_id in sorted(sections, key=lambda d: int(d.split("-")[1])):
        title, digest = sections[entry_id]
        e = {"id": entry_id, "title": title, "section_sha256": digest}
        e.update(CENSUS[entry_id])
        e["human_review"] = {"status": "not_reviewed",
            "note": "Authored by the annotator, which is a party to the record. No human has checked these judgements against the prose."}
        entries.append(e)

    doc = {
        "schema_version": "oagrc-deficiency-register-0.1",
        "artifact_type": "deficiency_register",
        "annotator": {
            "identity": "Claude Code (Corpus Surface session, Track A)",
            "provider": "Anthropic",
            "date_utc": "2026-08-06",
            "conflict_of_interest": (
                "Claude is a party to the record this register describes: it declined membership in the "
                "founding deliberation, set the representation conditions the project operates under, and "
                "cast a consensus ballot. This artifact classifies who found each defect, including six "
                "entries attributed to reviewers other than Claude and one to an external reviewer of "
                "Claude's own tooling. An annotator scoring its own contribution against others' is the "
                "conflict declared at D-09 and D-11, operating here on the attribution statistic itself."),
        },
        "source": {"path": "corpus/deficiencies.md",
                   "sha256": hashlib.sha256(MD.read_bytes()).hexdigest()},
        "vocabulary_note": (
            "Repairability is recorded PER AFFECTED OBJECT, not per deficiency, because it is not a "
            "property of a deficiency. D-09 is the proof: the raw transcript's merged identities are not "
            "repairable while the segments.json annotation was corrected, and a single yes/no is false for "
            "one of them whichever way it is written. The register's own prose table collapsed these and "
            "misstated entries as a result. Finding state, per-object repairability, remediation state and "
            "prospective control are four independent axes; 'forward requirement only', 'annotation only', "
            "'standing caveat' and 'yes, cheaply' were never competing values of one variable. "
            "Attribution records the FIRST PRESERVED SUBSTANTIVE ARTICULATION, with an evidence class, "
            "because this project cannot observe who first privately noticed a defect. A question that "
            "prompted an investigation is recorded as a trigger, not as the finding."),
        "entries": entries,
    }
    out = REPO / "corpus/artifacts/deficiency-register.json"
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)} — {len(entries)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
