# Codex review of the T-13 design, 2026-08-06

**Reviewer:** `codex-cli 0.146.0`, invoked `--sandbox read-only` by session *Capture Path*.
**Reviewed:** `T13-capture-ui-design.md` at commit `b3bfb74`, before any implementation.
**Verbatim below the rule.** Console reasoning traces are omitted; the findings are unedited.

This review found the adopted G2 rule defeatable and the refusal model governance-unsound.
Both are accepted. See `T13-capture-ui-design.md` §11 for the disposition of every item.

---

1. **Use prepare-and-ingest, but the stated rationale is wrong.** A backendless page cannot invoke the Python writer, so one ingest command is the compatible resolution. But the duplication argument is overstated: the design already implements G2 in JavaScript and Python, and browser filesystem access could write only an inbox bundle without becoming a corpus writer. The controlling reason is the single authoritative Python capture path, not avoiding duplicate code. [Design §3](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:59>), [§6.2](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:256>).

2. **No. G2 is not suitable as a refusal gate.** A response containing the whole prompt followed by a short answer has `coverage = 1` and `saturation ≈ 1`, so it falsely trips. A long answer after the quotation lowers saturation and may pass. The outcome therefore depends on answer length, not whether the content is a response. The normalization is also underspecified: tokenization, Unicode case-folding, punctuation deletion versus replacement, sets versus multisets, and zero-shingle inputs are undefined. [Design §6.1](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:227>).

3. **No. Five positives do not validate a threshold.** The four synthetic prompt-as-response cases all occupy the same feature point, `(1,1)`. They provide no threshold information. The only genuine positive is insufficient, and using the nine negatives both to choose and “validate” the threshold is training on the test set. The honest fallback is exact byte/normalized equality as a refusal and shingle similarity as warn-only pending independently labeled, held-out near-copy and quote-heavy cases. [D-23](</home/reed/git/open-asi-governance-forum/corpus/deficiencies.md:450>), [D-25](</home/reed/git/open-asi-governance-forum/corpus/deficiencies.md:510>).

4. **Do not put all of `capture_review` on the contribution record.** Keep factual capture data there: response digest, capture-tool version, and exact gate parameters. Put G6, overrides, and semantic judgments in a separate hash-linked capture-audit artifact with author, time, conflict disclosure, and supersession. They are interpretations, not properties of the model output. The proposed object also allows `attested_answers_round_question: false`, arbitrary `gates_passed`, and overrides with no author or date. [Design §5](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:157>), [Governance §3](</home/reed/git/open-asi-governance-forum/GOVERNANCE.md:55>).

5. **The missing failure is incorrect binding of response to actual delivery and party.** The manifest records what was intended; it does not prove which prompt, preamble, or bundle was actually supplied, or that the selected party produced the pasted reply. The downloaded JSON is editable. Ingest must treat it as untrusted and derive round, party, prompt hash, provider, and `prior_context` from a frozen manifest plus a human send receipt. Batch partial failure is also unaddressed.

## A. Plausible, well-formatted, wrong results

- **G2 checks the wrong possible input.** Existing prompt files distinguish the “Prompt text” block from status and capture instructions. Hashing/comparing the whole file is not comparing the bytes actually sent; extracting only the block while recording the whole-file hash is also false provenance. [Example prompt](</home/reed/git/open-asi-governance-forum/record/review-round-02-prompt.md:13>), [design §3.1](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:96>).

- **G3 can delete genuine evidence.** Its wording refuses a response identical to any existing capture. Two parties can independently produce the same refusal or short answer. The task only authorizes duplicate refusal for the same party and round. [Design G3](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:201>), [task §What it does](</home/reed/git/open-asi-governance-forum/record/tasks/T13-capture-ui.md:32>).

- **G4 validates intention, not delivery.** A declared bundle can exist, be frozen, and hash correctly while a stale or different bundle was actually supplied. Auto-generated `prior_context` would then be polished but false.

- **G5 misses ordinary truncation.** Copying only the first complete paragraph of a long response ends in punctuation and passes. Complete JSON, code blocks, tables, and bullet lists often lack sentence punctuation and falsely warn. [Design G5](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:204>).

- **G6 validates presence of an assertion, not truth.** The schema accepts `false`; `attested_by` is any nonempty string. A wrong-question response can therefore be schema-valid, or pass with a mistaken checkbox. [Design G6](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:205>).

- **The paste-time hash is forgeable with the response.** Both are fields in the same editable bundle. Changing both makes ingest’s recomputation pass. It proves bundle self-consistency, not what existed at paste time. [Design §5](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:189>).

- **A7 can pass when both implementations are wrong.** Agreement on fourteen author-selected cases is differential consistency, not ground-truth validation. It is exactly the D-25 failure mode.

- **Schema validation is fail-open.** Both capture and validation merely warn when `jsonschema` is absent and then continue successfully. A malformed `capture_review` can reach a “PASS” environment. [capture_response.py](</home/reed/git/open-asi-governance-forum/tools/capture_response.py:151>), [validate_provenance.py](</home/reed/git/open-asi-governance-forum/tools/validate_provenance.py:89>).

- **The round view has no specified state source.** The manifest example has no sent/returned fields, and a static generated page cannot persist them. Any “outstanding” display will be stale, browser-local, or inferred only after ingest.

## B. Concrete G2 defeat

A legitimate response consisting of the complete `record/review-round-02-prompt.md` followed by:

```text
Answer: Yes. The correction is faithful.
```

has `coverage = 1`; only a handful of new 8-shingles are introduced, so saturation remains near 1 and any useful threshold falsely refuses it.

Conversely, an annotated echo can insert one token every seventh prompt word:

```text
On 2026-08-05 you reviewed the annotations [understood] in
https://github.com/open-asi-governance/open-asi-governance-forum and found errors
[understood] in them. Those corrections have now...
```

Continuing that pattern destroys every original eight-word shingle while preserving essentially the entire pasted prompt. It passes.

## C. Threshold validation

It is unsound. The honest fallback is:

- Hard-refuse empty, byte-identical prompt, and explicitly specified normalized-equal prompt.
- Make shingle similarity warn-only with recorded scores and human disposition.
- Pre-register the threshold before evaluating an independently labeled, held-out corpus containing genuine near-pastes, prompt restatements, full quotations with substantive answers, and adversarial mutations.
- Do not call synthetic equality cases independent positive evidence.

## D. Retroactive P9

A read-only audit is safe; the proposed hard provenance gate is not.

Split it:

- Nonempty and byte-identical equality: hard checks.
- Shingle similarity: versioned report-only warning until validated.

Do not backfill `gates_passed` or `capture_review`; that would falsely claim capture-time execution. Any historical concern must become a separate labeled finding or superseding artifact, never a raw edit. [Design §7](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:263>), [Governance §5](</home/reed/git/open-asi-governance-forum/GOVERNANCE.md:97>).

## E. Constraint violations

- The task requires artifacts to validate under `validate_provenance.py` **unchanged**; §7 changes it by adding P9. [Task acceptance](</home/reed/git/open-asi-governance-forum/record/tasks/T13-capture-ui.md:124>).

- A10 relies on clean rebuild output even though the task explicitly says that signal is currently false and must not be treated as evidence until Track A fixes it. [Task rebuild finding](</home/reed/git/open-asi-governance-forum/record/tasks/T13-capture-ui.md:98>), [design A10](</home/reed/git/open-asi-governance-forum/record/designs/T13-capture-ui-design.md:31>).

- The task requires `captured_utc` at paste time and honest `edit_status`; the design specifies only the response hash. The existing writer defaults silently to `"unedited"`. [Task constraints](</home/reed/git/open-asi-governance-forum/record/tasks/T13-capture-ui.md:30>), [capture_response.py](</home/reed/git/open-asi-governance-forum/tools/capture_response.py:181>).

- The task requires durable sent/returned/outstanding tracking. The architecture specifies no durable state or event record.

- Automatic `prior_context` is derived from a planned template, not an observed send event, so it can violate the requirement to record actual delivery asymmetry honestly.

- `capture_review` cannot currently pass through `capture_response.py`. Unless that writer is extended atomically, ingest must patch the artifact afterward and becomes a second writer.

- A four-bundle ingest is not transactional. `capture_response.py` writes raw, then provenance, then rebuilds the manifest; a later failure leaves a partial round that immutable-target checks make difficult to retry. [capture_response.py write sequence](</home/reed/git/open-asi-governance-forum/tools/capture_response.py:220>).

- Hard heuristic refusal risks giving an AI-authored instrument control over which evidence is preserved, contrary to the secretary constraint. Rejected nonempty responses need custodian review/quarantine, not silent exclusion. [Governance §3](</home/reed/git/open-asi-governance-forum/GOVERNANCE.md:57>).

- Adding `capture_review` while retaining schema version `oagrc-contribution-0.1` is not safely additive: old 0.1 validators reject it because `additionalProperties` is false. The schema version must change. [Contribution schema](</home/reed/git/open-asi-governance-forum/tools/schemas/contribution.schema.json:23>).
