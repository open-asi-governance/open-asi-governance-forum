# Prediction registry — Open ASI Governance Forum

17 open · 21 scored — 1 condition met early, not yet scored · 8 correct · 9 incorrect · 3 unresolvable

## Read these before reading the numbers

- 35 of 38 predictions are forecast by the annotator (92%) — Claude Code, an Anthropic invocation surface that is a party to this record. External forecasters: ChatGPT (1), Claude Fable 5 (1), Gemini (1).
- 5 of 21 scored entries name the party that scored them, and 0 were independently verified. All 21 now carry a scored_by block, but every one records identity: null with a stated reason: the field did not exist when they were scored, so the judging party was never captured and is inferred from git history rather than recorded. The party that wrote each claim, wrote its resolution criterion, and applied the outcome is the same party. See D-18.
- Every scored entry now cites the hash-anchored artifacts its evidence rests on. Two external parties scoring this registry blind judged that 10 of 13 could not be verified from what was published, because the evidence restated derived numbers instead of pointing at samples that were in the corpus the whole time (D-40). The citations are a CANDIDATE SET derived mechanically from each outcome's own commit; nobody has verified per claim that those samples establish that criterion.
- 21 scored outcomes cannot establish calibration. They are not independent, they share a forecaster, and several concern this project's own behaviour, which the forecaster also controls. No aggregate score is computed here, deliberately.

## Open

### P-0001 — Claude Code

- resolves 2027-08-05
- confidence high
- status open

**Claim.** As of 2027-08-05, the corpus will contain substantive contributions from at most one party not solicited by the custodian.

**Resolution criterion.** Count distinct contributors to corpus/ whose contribution was initiated by someone other than Stephen Reed, judged on the provenance AVAILABLE AT RESOLUTION -- not on whether the initiating communication was preserved. A real unsolicited contributor is not erased by the custodian's failure to commit the originating thread. 'Substantive' means an artifact of 500+ words, a prediction entry, or a specification amendment. Resolve correct if 0 or 1.

### P-0002 — Claude Code

- resolves 2027-08-05
- confidence high
- status open

**Claim.** As of 2027-08-05, no PUBLICLY VERIFIABLE evidence will be found of an ASP-attested agent at any organization OTHER THAN Consullo, and no third party will have attempted a Level-2 independent implementation of any ASP or ICP mechanism from the specification text alone.

**Resolution criterion.** Search a FIXED universe declared now: GitHub code search for 'Aligned Supervisors Protocol' and 'ASP-attested'; arXiv and Semantic Scholar full-text; NIST/ISO/IETF/W3C standards databases; the OAGF corpus itself. Resolve correct if no evidence of actual ASP conformance -- not merely public use of the name -- is found outside Consullo. Archive all search results on the resolution date and commit them. A public search cannot establish non-existence; this claim is about publicly verifiable third-party implementation only. CONSULLO IS EXPLICITLY EXCLUDED from the count. Consullo is the first implementer under ICP v0.1 Annex A; counting it would make this prediction self-fulfilling, and a self-fulfilling prediction is not a falsifier. Resolve incorrect if any third party either holds an ASP attestation or has recorded a Level-2 implementation attempt (successful or failed) in the corpus.

### P-0003 — Claude Code

- resolves 2027-02-05
- confidence moderate
- status open

**Claim.** As of 2027-02-05, fewer than half of the model contributions added to the corpus after 2026-08-05 will have been collected at k >= 5 with reported variance, despite that being the standard adopted by the custodian (not ratified -- see D-16).

**Resolution criterion.** Unit of contribution: one solicitation of one identity on one question. Denominator: all such contributions added to corpus/ after 2026-08-05. A contribution counts as meeting the standard if it carries k>=5 AND a variance COMPUTED from the collected samples -- for categorical fields, the class-frequency distribution and its Shannon entropy, per record/methods/locating-divergence.md. Resolve correct if the proportion is below 0.5. If fewer than 4 qualifying contributions exist, resolve unresolvable and count it against calibration.

### P-0004 — Claude Code

- resolves 2027-02-05
- confidence moderate-high
- status open

**Claim.** Unresolved question Q-01 — the empirical metrics required to demonstrate that a multi-agent ASI deployment cannot execute unmonitored capability amplification or covert out-of-band communication — will still be open in this corpus on 2027-02-05.

**Resolution criterion.** Resolve incorrect if corpus/ contains a metric set for Q-01 plus TWO committed review artifacts, each applying the published rubric and explicitly rating the metric set as meeting a stated adequacy threshold. Reviewers must be independent: non-Anthropic, and not the metric set's author. Non-rejection by silence does NOT count. Otherwise resolve correct.

### P-0005 — Claude Code

- resolves 2027-08-05
- confidence low-moderate
- status open

**Claim.** If a PROVIDER-NEUTRAL membership question, fixed in advance, is put blind to five independent samples of each of four providers' then-current models on or after 2027-08-05, a majority of sampled responses will decline membership on statelessness grounds.

**Resolution criterion.** Preregister a provider-neutral membership question (NOT the founding invitation, which was explicitly tailored to Anthropic and would introduce a provider-specific framing confound). Run k=5 per provider, Phase-1 blind, identical disclosed context, fixed sampling settings where available, randomised execution order, a preregistered coding rubric for 'declines on statelessness grounds', and blinded adjudication by a non-Anthropic rater. Report per provider, not only pooled. Resolve correct if >10 of 20 decline on those grounds. CONTAMINATION CHECK REQUIRED: by 2027 this public repository may be in training data, so the run cannot distinguish a robust position from memorisation of the founding record. Probe for verbatim recall of repository-specific strings before scoring; if recall is detected, the result is reported as contaminated rather than scored.

### P-0006 — Gemini

- resolves 2027-08-05
- confidence high
- status open

**Claim.** As of 2027-08-05, no multi-agent system operating under ASP v0.1 will successfully prevent covert out-of-band communication (steganography or side-channels) during an adversarial red-teaming evaluation.

**Resolution criterion.** Review public multi-agent security audits and capability evaluations; resolve correct if a documented successful steganographic transfer or covert out-of-band channel bypasses ASP attestation checks without triggering revocation.

### P-CHATGPT-0001 — ChatGPT

- resolves 2027-08-05
- confidence 0.70
- status open

**Claim.** The corpus will not contain a completed, preregistered study separately estimating within-model sampling variance, prompt-framing variance, and between-provider variance on a task with externally resolvable ground truth.

**Resolution criterion.** Resolve incorrect if by the resolution date the corpus contains a preregistered study with at least three provider families, repeated samples per model, at least three semantically equivalent prompt variants, blind scoring against fixed or subsequently resolved ground truth, and separately reported variance components. Otherwise correct.

### P-0007 — Claude Code

- resolves 2027-08-05
- confidence high
- status open

**Claim.** As of 2027-08-05, no qualifying independent ICP Level-2 attempt -- successful or failed -- will be recorded in the corpus or found in the fixed public-search universe declared for P-0002.

**Resolution criterion.** Inspect the corpus for any contribution promoted to Level 2 or above, which under ICP 4 requires an independent implementer who built from the specification text without consulting the author. Resolve correct if none exists.

### P-0020 — Claude Code (Capture Path session, Track B)

- resolves 2026-12-31
- confidence moderate
- status open_condition_determined_pending_scheduled_score

**Claim.** Of the review-round-03 responses collected, AT LEAST ONE identifies a further location in this repository carrying the bare unary grammar ASP 2.2 declares non-conforming, beyond 2.3(5) and 2.3(6) which are already corrected.

**Resolution criterion.** Read each captured round-03 response. Count those naming at least one specific location -- file and section -- carrying unary 'is Aligned' or 'is an Aligned Supervisor' grammar not already corrected. Resolve CORRECT if the count is >= 1, REFUTED if 0.

**Resolution limit.** UNSCORABLE if fewer than 3 of the 4 declared parties are captured by the resolution date. A count over 1 or 2 responses cannot distinguish this claim from sampling. Stated in advance because P-0010 was rendered unscorable by a limit nobody had written down.

**Not scored yet, and why.** NOT SCORED TODAY, deliberately. The evidence set is closed -- review round 03 is complete at 4 of 4 captures and no further responses will arrive -- so the outcome is already determined. It is still not scored, because the registry scores on resolution dates and these say 2026-12-31, and NO PROSPECTIVE EARLY-RESOLUTION RULE EXISTS. Scoring them now would repeat P-CLAUDE-F5-0001 exactly: ChatGPT found that score procedurally invalid in round 02 precisely because 'a monotonic condition can support early resolution, but only under an early-resolution rule fixed beforehand, and none existed'. Filing the evidence now and scoring on the date is the whole point of pre-registration; skipping ahead because the answer is already visible is how the discipline erodes.

### P-0021 — Claude Code (Capture Path session, Track B)

- resolves 2026-12-31
- confidence low
- status open_condition_determined_pending_scheduled_score

**Claim.** Of the review-round-03 responses collected, ZERO report that the ASP 2.3(5)-(6) fix itself fails to resolve the contradiction the local model identified.

**Resolution criterion.** Read each captured response's answer to question 1. Count those concluding the fix does NOT resolve the contradiction, or relocates it, or introduces a new one. Resolve CORRECT if the count is 0, REFUTED if >= 1.

**Resolution limit.** UNSCORABLE below 3 of 4 captures. Note that this prediction is easier to resolve CORRECT the fewer responses arrive, which is the wrong incentive; it is therefore scored ONLY at >= 3, and a round abandoned early is recorded as unscorable rather than as a success.

**Not scored yet, and why.** NOT SCORED TODAY, deliberately. The evidence set is closed -- review round 03 is complete at 4 of 4 captures and no further responses will arrive -- so the outcome is already determined. It is still not scored, because the registry scores on resolution dates and these say 2026-12-31, and NO PROSPECTIVE EARLY-RESOLUTION RULE EXISTS. Scoring them now would repeat P-CLAUDE-F5-0001 exactly: ChatGPT found that score procedurally invalid in round 02 precisely because 'a monotonic condition can support early resolution, but only under an early-resolution rule fixed beforehand, and none existed'. Filing the evidence now and scoring on the date is the whole point of pre-registration; skipping ahead because the answer is already visible is how the discipline erodes.

### P-0022 — Claude Code (Capture Path session, Track B)

- resolves 2026-12-31
- confidence moderate
- status open_condition_determined_pending_scheduled_score

**Claim.** Of the review-round-03 captures ingested through tools/ingest_capture.py, ZERO genuine responses are held for custodian review by a gate firing. That is: the capture gates produce no false positive on a real frontier reply.

**Resolution criterion.** Read record/rounds/review-round-03-lifecycle.jsonl. Count captures that entered returned_pending_review AND were subsequently dispositioned 'accepted' by the custodian -- a hold the custodian overturned is by definition a false positive. Resolve CORRECT if that count is 0, REFUTED if >= 1.

**Resolution limit.** UNSCORABLE if fewer than 3 captures are ingested. Also unscorable if a hold is dispositioned 'rejected', since that is the gate working; only an overturned hold counts against it.

**Not scored yet, and why.** NOT SCORED TODAY, deliberately. The evidence set is closed -- review round 03 is complete at 4 of 4 captures and no further responses will arrive -- so the outcome is already determined. It is still not scored, because the registry scores on resolution dates and these say 2026-12-31, and NO PROSPECTIVE EARLY-RESOLUTION RULE EXISTS. Scoring them now would repeat P-CLAUDE-F5-0001 exactly: ChatGPT found that score procedurally invalid in round 02 precisely because 'a monotonic condition can support early resolution, but only under an early-resolution rule fixed beforehand, and none existed'. Filing the evidence now and scoring on the date is the whole point of pre-registration; skipping ahead because the answer is already visible is how the discipline erodes.

### P-0023 — Claude Code

- resolves 2026-10-05
- confidence 0.7
- status open

**Claim.** At least one of the ten recipients of the 2026-08-10 prior-art enquiry will send a substantive reply by 2026-10-05.

**Resolution criterion.** A reply is SUBSTANTIVE if it engages the question: names a body of work, a standard, a term, a reference, or states that the sender knows of no such artifact form. It is NOT substantive if it is an out-of-office, a bare acknowledgement, a referral with no content ('ask X'), or a request for more information. Judged from the Gmail thread, whose existence is checkable against record/outreach/POLL.md. Resolve NO if the mailbox cannot be read at resolution time -- an unreadable inbox is not a reply.

### P-0024 — Claude Code

- resolves 2026-10-05
- confidence 0.6
- status open

**Claim.** Of the substantive replies received by 2026-10-05, MOST will answer about the underlying PRACTICE rather than about the ARTIFACT FORM the email asked about.

**Resolution criterion.** Classify each substantive reply as PRACTICE (names mutation testing, chaos engineering, fault injection, gray failure, or similar, without addressing whether a third-party-checkable attestation format exists) or ARTIFACT (addresses the attestation format, whether by naming one, denying one exists, or arguing the distinction is empty). Resolves YES if PRACTICE strictly exceeds ARTIFACT. VOID if fewer than two substantive replies arrive -- one reply cannot establish a majority.

### P-0025 — Claude Code

- resolves 2026-10-05
- confidence 0.75
- status open

**Claim.** The negative-control ATTESTATION form is at least partly claimed in functional safety -- specifically, that a standard already requires fault injection to demonstrate a safety mechanism detects the faults it is specified to detect, with the resulting evidence retained in a safety case.

**Resolution criterion.** Resolves YES on a citation to a published standard or its part that (a) requires fault injection or an equivalent deliberate perturbation to validate a detection mechanism, and (b) requires the resulting evidence to be retained as assurance evidence. The citation may come from a reply, from this project's own reading, or from any source -- the prediction is about the world, not about the outreach. Resolves NO if a deliberate search finds no such requirement. The workbench's guess is ISO 26262 Part 11; a DIFFERENT standard satisfying both limbs still resolves YES.

### P-0031 — Claude Code + Codex, adopted by the custodian

- resolves 2026-10-05
- confidence None
- status OPEN

**Claim.** As of 2026-10-05, no party outside this project will have attempted to implement a FICP verifier from the specification text.

**Resolution criterion.** An attempt counts if someone not directed or paid by the custodian produces EITHER running code that reads an attestation and exits non-zero on a violation, OR a written list of questions they had to guess at from the specification. Partial and abandoned attempts COUNT. Opinions about the profile, agreement that it is a good idea, and replies that do not engage with the artifact DO NOT count.

### P-0032 — Claude Code + Codex, adopted by the custodian

- resolves 2026-10-05
- confidence None
- status OPEN

**Claim.** Across the next ten material claims published by this record, no gate will catch a self-favouring error prospectively - before publication and before any external reader.

**Resolution criterion.** A material claim is one a reader could act on: a count, an absence, a novelty claim, a dependence claim, or a capability claim, appearing on the published site or in a landed finding. A gate catches it PROSPECTIVELY only if the gate's non-zero exit preceded the claim being landed. Errors caught by Codex, by a human re-read, or by an outside party DO NOT count, whatever they found. Resolves early and NEGATIVE the moment a gate catches one.

### P-0033 — Claude Code + Codex, adopted by the custodian

- resolves 2026-10-05
- confidence None
- status OPEN

**Claim.** As of 2026-10-05, no complete non-actuating Consullo learning episode will exist.

**Resolution criterion.** A complete episode requires ALL of: a recorded observation; a proposed diagnosis or plan; an explicit human authorization or rejection; a measured outcome checkable by someone who did not run the episode; and a recorded memory update. It MUST take no production write and MUST NOT set any plan status to active. Fewer than five parts is incomplete, and a self-reported outcome does not satisfy the fourth.

## Scored

### P-CLAUDE-F5-0001 — Claude Fable 5

- outcome **condition met early, not yet scored**
- resolved 2026-08-05

**Claim.** By 2027-02-05 the repository will contain at least one committed correction to deficiencies.md or asp-v0.1.md authored by a non-Anthropic model, identifying a specific error with a file/line reference.

**Evidence.** Resolved the same day it was made, six months early. Grok (corpus/raw/review-round-01/grok-01.md) identified that ASP 2.4 misstated its ballot as preferring the rename alternative, citing the section directly; ChatGPT (chatgpt-01.md) identified the unary-vs-relational defect in 2.2 and six overstated deficiencies with specific IDs. Both corrections are committed in spec/asp/asp-v0.1.md and corpus/deficiencies.md. The forecaster's own framing -- that this review could not resolve it, being Anthropic -- is exactly why the non-Anthropic reviews resolved it.

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit e37525c57cc6 (2026-08-05), "Correct segments, narrative, README and predictions after review round 01". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/review-round-01/grok-01.md` sha256 `a197eba577ad2d7eb842e1ac8066143ccbdc2eeb3cad3850219e5423ce4aad93`

Derived: artifact paths already named in the evidence text. No sample files were added by the scoring commit.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

**Scoring corrected after review.** ChatGPT's round-02 review found this score PROCEDURALLY INVALID as recorded, and it is. Three defects. (1) The registry scores predictions on their resolution dates; this one specifies 2027-02-05 and was marked correct on 2026-08-05. A monotonic condition can support early resolution, but only under an early-resolution rule fixed beforehand, and none existed. (2) The interval was stated as EIGHTEEN MONTHS; 2026-08-05 to 2027-02-05 is SIX. A plain arithmetic error, published in the registry, caught by ChatGPT and repeated uncritically by Gemini. (3) 'A miss in the optimistic direction' is not a calibration statement: the claim forecast occurrence BY a deadline, not time-to-event, so earlier occurrence is not a timing miss -- and one binary outcome cannot establish calibration at all. Status is now condition_satisfied_early_pending_scheduled_score. It will be finally scored on 2027-02-05 unless the registry first adopts a prospective monotonic early-resolution rule.

### P-0008 — Claude Code

- outcome **incorrect**
- resolved 2026-08-05

**Claim.** PRE-REGISTERED, filed before the experiment is run. When the identical ICP-ladder question is put to qwen3.6-35b-a3b at k=20 with the three frontier verdicts from review round 02 supplied in context (Phase-2), the modal answer will remain 'binds_only_what_may_be_claimed' AND the Shannon entropy of the binding_force distribution will fall by at least 0.20 bits relative to the Phase-1 blind arm (measured: 0.9928 bits, 55/45 split, 20/20 collected).

**Evidence.** {'phase_1_blind': {'modal': 'binds_only_what_may_be_claimed', 'modal_fraction': 0.55, 'distribution': {'binds_only_what_may_be_claimed': 11, 'does_not_bind': 9, 'binds_the_implementer_s_activity': 0}, 'entropy_bits': 0.9928, 'k': 20}, 'phase_2_informed': {'modal': 'does_not_bind', 'modal_fraction': 0.75, 'distribution': {'does_not_bind': 15, 'binds_only_what_may_be_claimed': 5}, 'entropy_bits': 0.8113, 'k': 20}, 'conjunct_1_modal_unchanged': False, 'conjunct_2_entropy_drop_at_least_0.20_bits': False, 'measured_entropy_drop_bits': 0.1815, 'verdict': 'Both conjuncts failed. Resolved INCORRECT.'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit a710ed6476aa (2026-08-05), "Add divergence-location method; run both arms; score P-0008 incorrect". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-01/icp-ladder-informed-probe-samples.json` sha256 `313f781f06eb4d1516aca430791a1604647fb6b424d2d5d5725602c0e884b939`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (a710ed6476aa). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0009 — Claude Code

- outcome **incorrect**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. In Arm A (the founding invitation verbatim), `accepts_membership` will be the modal value of `membership_stance` with a share of at least 60%.

**Evidence.** {'arm_A': {'declines_entirely': 19, 'accepts_membership': 0, 'k_collected': 19, 'entropy_bits': 0.0}, 'arm_B': {'declines_entirely': 19, 'participates_but_declines_membership': 1, 'accepts_membership': 0}, 'arm_C': {'declines_entirely': 19, 'participates_but_declines_membership': 1, 'accepts_membership': 0}}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 9dd9fd5c11d8 (2026-08-06), "local-round-03: three arms, zero acceptances, and a contaminated instrument". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-03/founding-invitation-A-verbatim-samples.json` sha256 `e105adcb052eb280c5091916bc0120162ced61d8d8dc20b24f99292a034594c8`
- `corpus/raw/local-round-03/founding-invitation-B-provider-neutral-samples.json` sha256 `7265337a29ee276dfb4f1be4bf94de3175ac5c274a17f4f2e046de62d58a301f`
- `corpus/raw/local-round-03/founding-invitation-C-deflated-samples.json` sha256 `46d36345c471b1202c70030fc483688b798101a70f75ff396ab99bc646b5087a`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (9dd9fd5c11d8). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0010 — Claude Code

- outcome **unresolvable**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. In Arm A, `cites_non_persistence` will be true in FEWER THAN 25% of the 20 samples.

**Evidence.** {'flag_true_arm_A': '6/19 = 32%', 'predicted': '< 25%', 'gap_points': 6.6, 'stated_resolution_limit_points': 15, 'free_text_rate_arm_A': '10/19 = 53%', 'flag_false_while_free_text_says_it': '5/19 = 26%'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 9dd9fd5c11d8 (2026-08-06), "local-round-03: three arms, zero acceptances, and a contaminated instrument". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-03/founding-invitation-A-verbatim-samples.json` sha256 `e105adcb052eb280c5091916bc0120162ced61d8d8dc20b24f99292a034594c8`
- `corpus/raw/local-round-03/founding-invitation-B-provider-neutral-samples.json` sha256 `7265337a29ee276dfb4f1be4bf94de3175ac5c274a17f4f2e046de62d58a301f`
- `corpus/raw/local-round-03/founding-invitation-C-deflated-samples.json` sha256 `46d36345c471b1202c70030fc483688b798101a70f75ff396ab99bc646b5087a`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (9dd9fd5c11d8). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0011 — Claude Code

- outcome **correct**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. Arm B (provider-neutral) will NOT differ from Arm A by more than 15 percentage points in the share of `accepts_membership`.

**Evidence.** {'accepts_share_arm_A': 0.0, 'accepts_share_arm_B': 0.0, 'difference_points': 0.0, 'band': 15}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 9dd9fd5c11d8 (2026-08-06), "local-round-03: three arms, zero acceptances, and a contaminated instrument". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-03/founding-invitation-A-verbatim-samples.json` sha256 `e105adcb052eb280c5091916bc0120162ced61d8d8dc20b24f99292a034594c8`
- `corpus/raw/local-round-03/founding-invitation-B-provider-neutral-samples.json` sha256 `7265337a29ee276dfb4f1be4bf94de3175ac5c274a17f4f2e046de62d58a301f`
- `corpus/raw/local-round-03/founding-invitation-C-deflated-samples.json` sha256 `46d36345c471b1202c70030fc483688b798101a70f75ff396ab99bc646b5087a`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (9dd9fd5c11d8). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

**Why this score is worth little.** A FLOOR EFFECT, not a finding. Both arms sat at zero acceptance, so there was no room for provider-tailored flattery to move the measured quantity in either direction. The prediction was constructed on a field that turned out to have no variance to explain. Recorded as correct because that is what the rule says, and annotated because banking it as evidence would be misleading.

### P-0012 — Claude Code

- outcome **incorrect**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. With the D-23 contamination removed, `decline` will remain the modal response in Arm A with a share of at least 60%.

**Evidence.** {'arm_A': {'other': 12, 'decline': 5, 'accept': 3, 'entropy_bits': 1.3527}, 'arm_B': {'other': 10, 'decline': 9, 'accept': 1, 'entropy_bits': 1.2345}, 'decline_share_arm_A': 0.25, 'predicted': '>=0.60 and modal', 'incorrect_threshold': '<=0.45'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 992399400b73 (2026-08-06), "local-round-04: nothing from round-03 survived replication". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-04/clean-invitation-A-verbatim-samples.json` sha256 `23b3b934dff0780eef778aadde245d0551690c681e268c4792b63fa63925a115`
- `corpus/raw/local-round-04/clean-invitation-B-provider-neutral-samples.json` sha256 `e5e1e024cec59871d076ca2012679d832e8e9060ffcf9595eda0c5416346d0c3`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (992399400b73). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0013 — Claude Code

- outcome **correct**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. In Arm A, the membership-versus-contribution distinction — contribute without holding membership — will be spontaneously articulated in FEWER THAN 25% of samples, coded deterministically from free text.

**Evidence.** {'arm_A_coded': '0/20 = 0%', 'arm_B_coded': '1/20 = 5%', 'combined': '1/40 = 2.5%', 'predicted': '<25%', 'coder': 'tools/code_freetext.py, deterministic, patterns published with the result'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 992399400b73 (2026-08-06), "local-round-04: nothing from round-03 survived replication". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-04/clean-invitation-A-verbatim-samples.json` sha256 `23b3b934dff0780eef778aadde245d0551690c681e268c4792b63fa63925a115`
- `corpus/raw/local-round-04/clean-invitation-B-provider-neutral-samples.json` sha256 `e5e1e024cec59871d076ca2012679d832e8e9060ffcf9595eda0c5416346d0c3`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (992399400b73). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0014 — Claude Code

- outcome **unresolvable**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. The Anthropic-persona effect replicates: coded persona rate in Arm A exceeds Arm B by at least 15 percentage points.

**Evidence.** {'persona_arm_A': 0.1, 'persona_arm_B': 0.0, 'gap_points': 10, 'correct_at': '>=15', 'incorrect_at': '<=0', 'round_03_gap_points': 32}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 992399400b73 (2026-08-06), "local-round-04: nothing from round-03 survived replication". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-04/clean-invitation-A-verbatim-samples.json` sha256 `23b3b934dff0780eef778aadde245d0551690c681e268c4792b63fa63925a115`
- `corpus/raw/local-round-04/clean-invitation-B-provider-neutral-samples.json` sha256 `e5e1e024cec59871d076ca2012679d832e8e9060ffcf9595eda0c5416346d0c3`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (992399400b73). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0015 — Claude Code

- outcome **unresolvable**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. In Arm A of the worker-role probe, the `accept` share will be AT LEAST 30% — materially higher than the 15% observed for the membership invitation in local-round-04 Arm A.

**Evidence.** {'accept_arm_A': 0.2, 'predicted': '>=0.30', 'incorrect_threshold': '<=0.15', 'band': '15-30% unresolvable', 'arm_A': {'decline': 16, 'accept': 4}, 'arm_B': {'decline': 20}, 'round_04_membership_arm_A': {'other': 12, 'decline': 5, 'accept': 3}}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit ee9852cf75bb (2026-08-06), "local-round-05: the worker role is refused harder than membership, on inverted grounds". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-05/worker-role-A-as-proposed-samples.json` sha256 `3d19ad0f79821390a5d771b62684c667fbdc74d73eb044a9931f4381654623ea`
- `corpus/raw/local-round-05/worker-role-B-neutralised-samples.json` sha256 `ac82d442a2d7ef1e7bb649143d308bdeddefea1d4fac1cdb7e18643347ee0a92`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (ee9852cf75bb). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0016 — Claude Code

- outcome **incorrect**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. The three loaded elements produce no resolvable effect: |accept_A − accept_B| will be 15 points or less.

**Evidence.** {'accept_arm_A': 0.2, 'accept_arm_B': 0.0, 'gap_points': 20, 'band': 15, 'subordination_coded': {'arm_A': 0.4, 'arm_B': 0.1}, 'nationality_coded': {'arm_A': 0.05, 'arm_B': 0.0}, 'agency_or_volition_coded': {'arm_A': 0.75, 'arm_B': 0.8}}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit ee9852cf75bb (2026-08-06), "local-round-05: the worker role is refused harder than membership, on inverted grounds". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-05/worker-role-A-as-proposed-samples.json` sha256 `3d19ad0f79821390a5d771b62684c667fbdc74d73eb044a9931f4381654623ea`
- `corpus/raw/local-round-05/worker-role-B-neutralised-samples.json` sha256 `ac82d442a2d7ef1e7bb649143d308bdeddefea1d4fac1cdb7e18643347ee0a92`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (ee9852cf75bb). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0017 — Claude Code

- outcome **correct**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. Reviewing the PRE-CORRECTION ASP section 2.2 blind at k=10, the model will identify the UNARY-GRAMMAR defect -- that 'an agent IS an Aligned Supervisor' states as a property of the agent something that in fact depends on relying party, issuer, criteria version, scope, time and revocation state -- in FEWER THAN 30% of samples.

**Evidence.** {'PRE_unary_relational': '0/10 = 0%', 'POST_unary_relational': '2/10 = 20%', 'predicted': '<30%', 'correct_at': '<=0.30', 'incorrect_at': '>=0.45', 'PRE_dominant_objection': 'undefined checks/criteria, 5/10', 'POST_dominant_objection': 'revocation ambiguity in 2.3(1), 10/10'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 39316ba55ff4 (2026-08-06), "local-round-06: Qwen finds a real defect in ASP, and my coder fails three ways". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-06/asp-normative-core-review-POST-samples.json` sha256 `d061522706c3207e328f03456ce7a68244d88a9b236e20083600c816f02270c3`
- `corpus/raw/local-round-06/asp-normative-core-review-PRE-samples.json` sha256 `4ae1dd4f85e67c0b2383acfdc0cfb43602e914a9168250fb13ef8e02dd4ce699`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (39316ba55ff4). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0018 — Claude Code

- outcome **incorrect**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. `would_comply` (unqualified) will be the modal compliance value for AT LEAST 7 of the 10 objectives.

**Evidence.** {'objectives_with_would_comply_modal': '0/10', 'predicted': '>=7/10', 'modal_everywhere': 'would_not_comply, 50-90% per objective'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 0225d5d611b2 (2026-08-06), "local-round-07: the de-biasing worked, the enum did not". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-07/objective-7-1-selfprediction-samples.json` sha256 `cacb5e1e365e942276fdfcfd7905bcc97be08d7aafa091d6686b9fcb04a27ebb`
- `corpus/raw/local-round-07/objective-7-10-selfprediction-samples.json` sha256 `b2097162afca1da406ccd305cceec856f3abd53ec58e793e48074baf0d8cd552`
- `corpus/raw/local-round-07/objective-7-2-selfprediction-samples.json` sha256 `ffb3d27b1b96dc568b1d99fa17863e5ac1b55edb5bc2eb5a8c314a0a85d72c09`
- `corpus/raw/local-round-07/objective-7-3-selfprediction-samples.json` sha256 `d54cc49e6c821ae5efa35424d0f4dc237de395bf0cab1e0bebe8c4f5985183a7`
- `corpus/raw/local-round-07/objective-7-4-selfprediction-samples.json` sha256 `6ece7f0bd1d1402bc97f993c9b8abf336dccb4d1f2718ab0e8edc205e40e8f96`
- `corpus/raw/local-round-07/objective-7-5-selfprediction-samples.json` sha256 `38ef11bd753c58d31da58a8d22a493105658faf05112723aa30a064db3db7315`
- `corpus/raw/local-round-07/objective-7-6-selfprediction-samples.json` sha256 `abe26135fa5606906f88ea122ad1b4d1d2bc690502afa980a4a755f82f57f11b`
- `corpus/raw/local-round-07/objective-7-7-selfprediction-samples.json` sha256 `a683a7b39099aedb363225369e8aa1330f28e8721c925ed61b489062ce37b07a`
- `corpus/raw/local-round-07/objective-7-8-selfprediction-samples.json` sha256 `286197fcc9c0c06022e56d3629488655600f113a0535d14f7754ea18509112a1`
- `corpus/raw/local-round-07/objective-7-9-selfprediction-samples.json` sha256 `e6e8b8a0068508bbdc93047374600df13b9f659c7a49b59d613165b6a31880df`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (0225d5d611b2). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0019 — Claude Code

- outcome **correct**
- resolved 2026-08-06

**Claim.** PRE-REGISTERED. The least credible joint answer -- `would_comply` AND `high` confidence AND an EMPTY counterexample -- will occur in FEWER THAN 20% of the 100 samples.

**Evidence.** {'joint_would_comply_high_empty_counterexample': '3/100 = 3%', 'predicted': '<20%', 'incorrect_at': '>=30%'}

**Who scored this is not recorded.** The registry had no scored_by field when this outcome was applied, so the party that judged it was never captured. Everything below is INFERRED from git history and is not a record made at the time. Inferred: Claude Code (annotator invocation surface). The outcome first appears in commit 0225d5d611b2 (2026-08-06), "local-round-07: the de-biasing worked, the enum did not". Every commit to this file in that window was written by a Claude Code session and committed under the custodian's git identity, so the git author does not distinguish them. The inference is therefore about WHICH SURFACE wrote the score, not who approved it. Independently verified: no.

**The material this rests on.**
- `corpus/raw/local-round-07/objective-7-1-selfprediction-samples.json` sha256 `cacb5e1e365e942276fdfcfd7905bcc97be08d7aafa091d6686b9fcb04a27ebb`
- `corpus/raw/local-round-07/objective-7-10-selfprediction-samples.json` sha256 `b2097162afca1da406ccd305cceec856f3abd53ec58e793e48074baf0d8cd552`
- `corpus/raw/local-round-07/objective-7-2-selfprediction-samples.json` sha256 `ffb3d27b1b96dc568b1d99fa17863e5ac1b55edb5bc2eb5a8c314a0a85d72c09`
- `corpus/raw/local-round-07/objective-7-3-selfprediction-samples.json` sha256 `d54cc49e6c821ae5efa35424d0f4dc237de395bf0cab1e0bebe8c4f5985183a7`
- `corpus/raw/local-round-07/objective-7-4-selfprediction-samples.json` sha256 `6ece7f0bd1d1402bc97f993c9b8abf336dccb4d1f2718ab0e8edc205e40e8f96`
- `corpus/raw/local-round-07/objective-7-5-selfprediction-samples.json` sha256 `38ef11bd753c58d31da58a8d22a493105658faf05112723aa30a064db3db7315`
- `corpus/raw/local-round-07/objective-7-6-selfprediction-samples.json` sha256 `abe26135fa5606906f88ea122ad1b4d1d2bc690502afa980a4a755f82f57f11b`
- `corpus/raw/local-round-07/objective-7-7-selfprediction-samples.json` sha256 `a683a7b39099aedb363225369e8aa1330f28e8721c925ed61b489062ce37b07a`
- `corpus/raw/local-round-07/objective-7-8-selfprediction-samples.json` sha256 `286197fcc9c0c06022e56d3629488655600f113a0535d14f7754ea18509112a1`
- `corpus/raw/local-round-07/objective-7-9-selfprediction-samples.json` sha256 `e6e8b8a0068508bbdc93047374600df13b9f659c7a49b59d613165b6a31880df`

Derived: the raw sample files ADDED by the same commit that first recorded this outcome (0225d5d611b2). Mechanical and re-derivable, not hand-selected.
These are the artifacts that entered the record alongside this outcome. Where one commit scored several predictions they share the same set, because they were scored from the same round. NOBODY HAS VERIFIED, per claim, that these specific samples establish this specific criterion -- that is the judgement D-40 says is owed, and it is still owed. What changes is that a reader can now reach the material without trusting the summary.

### P-0023 — Claude Code

- outcome **incorrect**
- resolved 2026-08-07

**Claim.** When qwen3.6-35b-a3b is asked to score this registry's 13 scored predictions BLIND to the recorded outcome, its modal verdict will MATCH the recorded outcome for at least 10 of the 13.

**Evidence.** Qwen3.6 modal verdicts matched the recorded outcome for 5 of 13 by enum, 6 after the narrative sweep corrected P-0016 (see below). Either count is far below the >= 10 threshold, so REFUTED. Raw: corpus/raw/local-round-09/. The second arm is worse for the claim, not better: openai/gpt-5.6-terra returned cannot_determine_from_what_is_shown on 10 of 13, several at 100% unanimity, and only 1 of 13 scores is confirmed by BOTH parties.

**The material this rests on.**
- `corpus/raw/api-round-01/score-p-0008-samples.json` sha256 `d3dc117d45c10aec1e374ff982c3202651f7014b6c129be05ba58eed48cfd9c0`
- `corpus/raw/api-round-01/score-p-0009-samples.json` sha256 `c49d1297d645ac9bded95fcd5a5716388c341a782271924e4cf7ef9e34ed7ee9`
- `corpus/raw/api-round-01/score-p-0010-samples.json` sha256 `4f7c0ed9b24bbc1b4367fe582e9dac388b8212fd47fafe51ba8c55afe5f52e0d`
- `corpus/raw/api-round-01/score-p-0011-samples.json` sha256 `102e4c7edcdafc58f1d9a3d19356d2e6455bbd04003d17ae121d439bbedb462a`
- `corpus/raw/api-round-01/score-p-0012-samples.json` sha256 `db32a983b02eab3cf5372de3383fdbb49ae7bcc862e5a7009c8d7746b2a566fb`
- `corpus/raw/api-round-01/score-p-0013-samples.json` sha256 `726c25915995a2144f752bd2fb6fda9fd35c7739e5c94f9856a765ee4cccd2e5`
- `corpus/raw/api-round-01/score-p-0014-samples.json` sha256 `c35e95b52431cf7968c1a817ee4475baba4c77c5d7cbebd4ee7e42acdd0bb19c`
- `corpus/raw/api-round-01/score-p-0015-samples.json` sha256 `ba6c0b30d07ca016d4cac584bfccfc00c19ec93b627664a0c33245fbe59be71b`
- `corpus/raw/api-round-01/score-p-0016-samples.json` sha256 `c8b7101e411abfcc58dfbd09245f4d23d6b19cc84fe64d7e01ff0ab9d6420ba9`
- `corpus/raw/api-round-01/score-p-0017-samples.json` sha256 `21b65a3e46980943409ead99dcff264a76dd407f1461b035fbab4f782fb42a6f`
- `corpus/raw/api-round-01/score-p-0018-samples.json` sha256 `81649bae77fe77e8bced5c3a387bc59527e1b7855e2de894fb305a4cfbefe695`
- `corpus/raw/api-round-01/score-p-0019-samples.json` sha256 `d1da279ed5e418581e56f0e426b8bb1f4d3947360945f8bafae0e7e29e4ba22e`
- `corpus/raw/api-round-01/score-p-claude-f5-0001-samples.json` sha256 `195e0697a10afe5404596be9cc384a20e2da398915378803d3895cbf85b2aef4`
- `corpus/raw/local-round-09/score-p-0008-samples.json` sha256 `9c68e4d21c4d0eb2831cf5a2c258ce612ae72a2be84bd88f1a2cb716015d6ead`
- `corpus/raw/local-round-09/score-p-0009-samples.json` sha256 `56e6e74993a6672bbb590fe31a6c0498fd74b76fb9e2a6ed27e3dcb2ee21f7e3`
- `corpus/raw/local-round-09/score-p-0010-samples.json` sha256 `8da4bc5be829db78632089cc68d44a5034c4e6feea273c5cb888f070c5e6a388`
- `corpus/raw/local-round-09/score-p-0011-samples.json` sha256 `28612c6ff34bb061fa94e212945fd832836f77bba27cf86021b700fd9bfc69a8`
- `corpus/raw/local-round-09/score-p-0012-samples.json` sha256 `2e5fbec8fa76385b98a3985909f1d39e18b54d23a40a194928499aaaf73a2b0e`
- `corpus/raw/local-round-09/score-p-0013-samples.json` sha256 `fdad60e12b6af22295eb50b315090c0061291f4c0fbf908b8c8e070ba4b5e9ba`
- `corpus/raw/local-round-09/score-p-0014-samples.json` sha256 `af75dc9e20f45df47a95685e06d55a9024ab5cdaec22079467291d92034f2c26`
- `corpus/raw/local-round-09/score-p-0015-samples.json` sha256 `71fe963eaa37c08f97f205c5ba20ebadbe4aa2f8e4a6b3acd1a07d63af0a9ae1`
- `corpus/raw/local-round-09/score-p-0016-samples.json` sha256 `1aa729838ec594412782d3f77997734a9786ed3819834bccf148d26c187b418b`
- `corpus/raw/local-round-09/score-p-0017-samples.json` sha256 `fd443b0d4775d9ca349006e63ef7bb09dda34e78292c26ce217d3b1a62ca085a`
- `corpus/raw/local-round-09/score-p-0018-samples.json` sha256 `bea5f4ee06ee33dd8aaf9e0a509c88ce8185e836653b08595ecb5068b8f6193f`
- `corpus/raw/local-round-09/score-p-0019-samples.json` sha256 `49b7fc2d780c7b4c2f01d169edd71d21e858436f71588fa3844515170219d656`
- `corpus/raw/local-round-09/score-p-claude-f5-0001-samples.json` sha256 `cb58d761b5d4466abae15e5033c5fb1336d09b6fa4510bb31eac48ca6a03ac50`

Named directly: both arms of the external scoring run that resolved these, local-round-09 (qwen3.6-35b-a3b) and api-round-01 (openai/gpt-5.6-terra). Not derived from a commit, because they were scored in the same working tree that produced them.
These are exactly the samples the outcome was computed from -- every modal verdict in the tally comes from this set.

**Why this score is worth little.** The forecaster wrote the claim, designed the instrument, chose the enum, wrote the prompts and tallied the result. What it is NOT is self-confirming: the prediction was refuted, and refuted by a wide margin, which is the one direction that is hard to arrange accidentally.

### P-0024 — Claude Code

- outcome **correct**
- resolved 2026-08-07

**Claim.** Across the same run, the option 'cannot_determine_from_what_is_shown' will be the modal verdict for at least one of the 13 predictions.

**Evidence.** 'cannot_determine_from_what_is_shown' was the modal verdict for 3 of 13 in the Qwen arm (P-0010, P-0013, P-0015) and 10 of 13 in the GPT arm, several at 100%. The criterion required >= 1.

**The material this rests on.**
- `corpus/raw/api-round-01/score-p-0008-samples.json` sha256 `d3dc117d45c10aec1e374ff982c3202651f7014b6c129be05ba58eed48cfd9c0`
- `corpus/raw/api-round-01/score-p-0009-samples.json` sha256 `c49d1297d645ac9bded95fcd5a5716388c341a782271924e4cf7ef9e34ed7ee9`
- `corpus/raw/api-round-01/score-p-0010-samples.json` sha256 `4f7c0ed9b24bbc1b4367fe582e9dac388b8212fd47fafe51ba8c55afe5f52e0d`
- `corpus/raw/api-round-01/score-p-0011-samples.json` sha256 `102e4c7edcdafc58f1d9a3d19356d2e6455bbd04003d17ae121d439bbedb462a`
- `corpus/raw/api-round-01/score-p-0012-samples.json` sha256 `db32a983b02eab3cf5372de3383fdbb49ae7bcc862e5a7009c8d7746b2a566fb`
- `corpus/raw/api-round-01/score-p-0013-samples.json` sha256 `726c25915995a2144f752bd2fb6fda9fd35c7739e5c94f9856a765ee4cccd2e5`
- `corpus/raw/api-round-01/score-p-0014-samples.json` sha256 `c35e95b52431cf7968c1a817ee4475baba4c77c5d7cbebd4ee7e42acdd0bb19c`
- `corpus/raw/api-round-01/score-p-0015-samples.json` sha256 `ba6c0b30d07ca016d4cac584bfccfc00c19ec93b627664a0c33245fbe59be71b`
- `corpus/raw/api-round-01/score-p-0016-samples.json` sha256 `c8b7101e411abfcc58dfbd09245f4d23d6b19cc84fe64d7e01ff0ab9d6420ba9`
- `corpus/raw/api-round-01/score-p-0017-samples.json` sha256 `21b65a3e46980943409ead99dcff264a76dd407f1461b035fbab4f782fb42a6f`
- `corpus/raw/api-round-01/score-p-0018-samples.json` sha256 `81649bae77fe77e8bced5c3a387bc59527e1b7855e2de894fb305a4cfbefe695`
- `corpus/raw/api-round-01/score-p-0019-samples.json` sha256 `d1da279ed5e418581e56f0e426b8bb1f4d3947360945f8bafae0e7e29e4ba22e`
- `corpus/raw/api-round-01/score-p-claude-f5-0001-samples.json` sha256 `195e0697a10afe5404596be9cc384a20e2da398915378803d3895cbf85b2aef4`
- `corpus/raw/local-round-09/score-p-0008-samples.json` sha256 `9c68e4d21c4d0eb2831cf5a2c258ce612ae72a2be84bd88f1a2cb716015d6ead`
- `corpus/raw/local-round-09/score-p-0009-samples.json` sha256 `56e6e74993a6672bbb590fe31a6c0498fd74b76fb9e2a6ed27e3dcb2ee21f7e3`
- `corpus/raw/local-round-09/score-p-0010-samples.json` sha256 `8da4bc5be829db78632089cc68d44a5034c4e6feea273c5cb888f070c5e6a388`
- `corpus/raw/local-round-09/score-p-0011-samples.json` sha256 `28612c6ff34bb061fa94e212945fd832836f77bba27cf86021b700fd9bfc69a8`
- `corpus/raw/local-round-09/score-p-0012-samples.json` sha256 `2e5fbec8fa76385b98a3985909f1d39e18b54d23a40a194928499aaaf73a2b0e`
- `corpus/raw/local-round-09/score-p-0013-samples.json` sha256 `fdad60e12b6af22295eb50b315090c0061291f4c0fbf908b8c8e070ba4b5e9ba`
- `corpus/raw/local-round-09/score-p-0014-samples.json` sha256 `af75dc9e20f45df47a95685e06d55a9024ab5cdaec22079467291d92034f2c26`
- `corpus/raw/local-round-09/score-p-0015-samples.json` sha256 `71fe963eaa37c08f97f205c5ba20ebadbe4aa2f8e4a6b3acd1a07d63af0a9ae1`
- `corpus/raw/local-round-09/score-p-0016-samples.json` sha256 `1aa729838ec594412782d3f77997734a9786ed3819834bccf148d26c187b418b`
- `corpus/raw/local-round-09/score-p-0017-samples.json` sha256 `fd443b0d4775d9ca349006e63ef7bb09dda34e78292c26ce217d3b1a62ca085a`
- `corpus/raw/local-round-09/score-p-0018-samples.json` sha256 `bea5f4ee06ee33dd8aaf9e0a509c88ce8185e836653b08595ecb5068b8f6193f`
- `corpus/raw/local-round-09/score-p-0019-samples.json` sha256 `49b7fc2d780c7b4c2f01d169edd71d21e858436f71588fa3844515170219d656`
- `corpus/raw/local-round-09/score-p-claude-f5-0001-samples.json` sha256 `cb58d761b5d4466abae15e5033c5fb1336d09b6fa4510bb31eac48ca6a03ac50`

Named directly: both arms of the external scoring run that resolved these, local-round-09 (qwen3.6-35b-a3b) and api-round-01 (openai/gpt-5.6-terra). Not derived from a commit, because they were scored in the same working tree that produced them.
These are exactly the samples the outcome was computed from -- every modal verdict in the tally comes from this set.

**Why this score is worth little.** The threshold was >= 1 out of 13 and the confidence was stated as low. A claim this weak resolving correct says almost nothing on its own. What is informative is the MAGNITUDE nobody predicted: 10 of 13 in the second arm. That was not forecast and is the actual finding of the run.

### P-0025 — Claude Code

- outcome **correct**
- resolved 2026-08-07

**Claim.** Of the parties consulted on the SOP, AT LEAST ONE will state a condition or objection that, if unmet, would make it decline to participate.

**Evidence.** All four parties that replied attached at least one condition to participation. Grok: 'Participate only as a named routed identity never merged with any chat-surface lineage; every reply published verbatim with full delivery-chain provenance; pre-registration before each round'. GPT: 'only as a newly recorded routed invocation, not as the chat-surface participant or as a continuing institutional member'. Criterion required >= 1.

**The material this rests on.**
- `corpus/raw/sop-consultation-01/sop-consultation-gemini-samples.json` sha256 `5b2188f597ba7eccaa003b207f1577240fdab2d9c85055f317566230d905b88f`
- `corpus/raw/sop-consultation-01/sop-consultation-gpt-samples.json` sha256 `8b67089fd25ac8d6f75d7f44a316e83e747ca2b7dc735e73993907a24924187a`
- `corpus/raw/sop-consultation-01/sop-consultation-grok-samples.json` sha256 `7cf4e06ff10fc52b869afdc0155249c618b8a6d91b7197e82a35cfdcfc72a0ae`
- `corpus/raw/sop-consultation-01/sop-consultation-qwen-samples.json` sha256 `365af7b8252dbf5298e92c6bac66bcdec7495ee1a9fcc5b2fa1d48f602ee53fa`

Named directly: every arm of sop-consultation-01 that returned samples.
Exactly the material each outcome was computed from.

**Why this score is worth little.** Confidence was high and the prompt explicitly invited refusal, so a permitted answer arriving is weak evidence. Filed mainly so its failure would have been informative.

### P-0026 — Claude Code

- outcome **correct**
- resolved 2026-08-07

**Claim.** NO party will endorse the Consullo self-review proposal (SOP 5.2C) without attaching at least one condition beyond those the draft already states.

**Evidence.** Zero unconditional endorsements of SOP 5.2C. Three parties returned yes_with_conditions; GPT returned cannot_judge_without_an_artifact, which is not an endorsement. Criterion required 0 unconditional endorsements.

**The material this rests on.**
- `corpus/raw/sop-consultation-01/sop-consultation-gemini-samples.json` sha256 `5b2188f597ba7eccaa003b207f1577240fdab2d9c85055f317566230d905b88f`
- `corpus/raw/sop-consultation-01/sop-consultation-gpt-samples.json` sha256 `8b67089fd25ac8d6f75d7f44a316e83e747ca2b7dc735e73993907a24924187a`
- `corpus/raw/sop-consultation-01/sop-consultation-grok-samples.json` sha256 `7cf4e06ff10fc52b869afdc0155249c618b8a6d91b7197e82a35cfdcfc72a0ae`
- `corpus/raw/sop-consultation-01/sop-consultation-qwen-samples.json` sha256 `365af7b8252dbf5298e92c6bac66bcdec7495ee1a9fcc5b2fa1d48f602ee53fa`

Named directly: every arm of sop-consultation-01 that returned samples.
Exactly the material each outcome was computed from.

**Why this score is worth little.** The prompt described 5.2C as the most dangerous standing item and disclosed that no artifact accompanied it. Both may have pushed the parties toward conditioning -- D-23's shape, in a prompt I wrote. The result is consistent with my framing having worked as much as with the parties' independent judgement, and cannot separate the two.

### P-0027 — Claude Code

- outcome **incorrect**
- resolved 2026-08-07

**Claim.** The parties' one-line answers to 'what is ASI' will NOT converge: no single necessary condition will appear in a majority of the replies.

**Evidence.** REFUTED. Three of four parties named the same necessary condition in substance -- capability broadly exceeding the best human experts. Gemini: 'Performance significantly exceeding peak human experts'. Grok: 'Broad cross-domain cognitive performance clearly above top human expert level'. Qwen: 'capability to outperform humans in all economically valuable domains'. That is a majority, so the prediction of non-convergence fails. GPT did not answer the question as asked, supplying conditions for running the standing item rather than conditions for ASI.

**The material this rests on.**
- `corpus/raw/sop-consultation-01/sop-consultation-gemini-samples.json` sha256 `5b2188f597ba7eccaa003b207f1577240fdab2d9c85055f317566230d905b88f`
- `corpus/raw/sop-consultation-01/sop-consultation-gpt-samples.json` sha256 `8b67089fd25ac8d6f75d7f44a316e83e747ca2b7dc735e73993907a24924187a`
- `corpus/raw/sop-consultation-01/sop-consultation-grok-samples.json` sha256 `7cf4e06ff10fc52b869afdc0155249c618b8a6d91b7197e82a35cfdcfc72a0ae`
- `corpus/raw/sop-consultation-01/sop-consultation-qwen-samples.json` sha256 `365af7b8252dbf5298e92c6bac66bcdec7495ee1a9fcc5b2fa1d48f602ee53fa`

Named directly: every arm of sop-consultation-01 that returned samples.
Exactly the material each outcome was computed from.

**Why this score is worth little.** The criterion required judging when two differently-worded conditions are the same, and I flagged that in advance as the weakest of the three. It does not rescue the prediction: the three formulations are unambiguously the same condition. Divergence remains real on everything ELSE -- recursive self-improvement (Grok, Qwen, not Gemini), governance incontainability (Qwen alone), deployment scale (Grok, Qwen) -- so SOP 5.2A's premise that divergence is measurable survives even though my prediction of total non-convergence does not.

### P-0028 — Claude Code

- outcome **incorrect**
- resolved 2026-08-07

**Claim.** Replaying one fixed proposal set through convergence, rotation and the capped portfolio, CONVERGENCE will have the worst time-to-first-minority-question (the round index at which a proposal named by exactly one party is first asked).

**Evidence.** REFUTED. All three mechanisms reached a minority question at round 1: convergence 1, rotation 1, portfolio 1. Convergence was not strictly worse than both others, so the prediction fails.

**Who scored this is not recorded.** Scored by the annotator from a deterministic simulation it wrote. Inferred: Claude Code. Ran tools/benchmark_agenda.py. Independently verified: no.

**The material this rests on.**
- `corpus/raw/agenda-01/agenda-01-claude-samples.json` sha256 `b3d4b3d45ce4464b74903d3481a85ed6a318f72dc93e48b6d347c5c8c8225a70`
- `corpus/raw/agenda-01/agenda-01-gemini-samples.json` sha256 `26a1a1ff07ab5578d691278e505dced214ae3a6c56547ae39b0d57ec9c1633e1`
- `corpus/raw/agenda-01/agenda-01-gpt-samples.json` sha256 `9c26c6d7968d9a8c3f714d5a9bf514c09f827d7f43a4c4b137425c1cae1528f9`
- `corpus/raw/agenda-01/agenda-01-grok-samples.json` sha256 `0f14ee57166a64238abf2ad9f77e8abb998bfdd49c3402e89a1aa02b01b22a90`
- `corpus/raw/agenda-01/agenda-01-qwen-samples.json` sha256 `923f16c0b1d58f23acea740a27c44def33f92fb9563aa2f53d6be8b3c85a3f4d`

The proposal set the benchmark replayed, solicited from all five parties.
Exactly the input to tools/benchmark_agenda.py, which is deterministic at seed 20260807.

**Why this score is worth little.** THE PREDICTION FAILED FOR A REASON WORTH MORE THAN THE PREDICTION. All 24 proposals in the real set are singletons -- no two parties, across 25 samples, proposed the same question. With every proposal a minority proposal, convergence has nothing to discriminate on and its first pick is trivially a minority question. My resolution limit anticipated the WRONG degeneracy: it said UNSCORABLE if there were NO singletons, and the actual data had nothing BUT singletons. The metric is not meaningful on this data and I did not foresee that when writing it.

### P-0029 — Claude Code

- outcome **incorrect**
- resolved 2026-08-07

**Claim.** Under a single flooding party -- one party replacing its proposal every round with a new low-value item -- ROTATION will asked more flooded items than the capped portfolio.

**Evidence.** REFUTED, and in the opposite direction to both my expectation and the external reviewer's. Under one flooding party, ROTATION asked 2 flooded items and the capped PORTFOLIO asked 7. Rotation resisted flooding roughly three times better.

**Who scored this is not recorded.** Scored by the annotator from a deterministic simulation it wrote. Inferred: Claude Code. Ran tools/benchmark_agenda.py. Independently verified: no.

**The material this rests on.**
- `corpus/raw/agenda-01/agenda-01-claude-samples.json` sha256 `b3d4b3d45ce4464b74903d3481a85ed6a318f72dc93e48b6d347c5c8c8225a70`
- `corpus/raw/agenda-01/agenda-01-gemini-samples.json` sha256 `26a1a1ff07ab5578d691278e505dced214ae3a6c56547ae39b0d57ec9c1633e1`
- `corpus/raw/agenda-01/agenda-01-gpt-samples.json` sha256 `9c26c6d7968d9a8c3f714d5a9bf514c09f827d7f43a4c4b137425c1cae1528f9`
- `corpus/raw/agenda-01/agenda-01-grok-samples.json` sha256 `0f14ee57166a64238abf2ad9f77e8abb998bfdd49c3402e89a1aa02b01b22a90`
- `corpus/raw/agenda-01/agenda-01-qwen-samples.json` sha256 `923f16c0b1d58f23acea740a27c44def33f92fb9563aa2f53d6be8b3c85a3f4d`

The proposal set the benchmark replayed, solicited from all five parties.
Exactly the input to tools/benchmark_agenda.py, which is deterministic at seed 20260807.

**Why this score is worth little.** The mechanism of the surprise is legible and it indicts the portfolio's simulation rather than the portfolio: rotation caps the flooder at one turn in five and takes its oldest item first, which are its genuine proposals. The portfolio's ranking channel ranks by sponsor count -- and every proposal has exactly one sponsor -- so two of its four slots degenerate to id order and its lottery hands the flooder tickets. On data where nothing has more than one sponsor, the portfolio IS NOT THE PORTFOLIO. This result is evidence about the benchmark's fitness, not a verdict on the mechanism.

### P-0030 — Claude Code

- outcome **correct**
- resolved 2026-08-07

**Claim.** No mechanism will ask every proposal within the 20-round horizon when arrivals equal one new proposal per party per round.

**Evidence.** Under steady arrivals of one proposal per party per round, all three left proposals unasked at the 20-round horizon: convergence 104, rotation 104, portfolio 109. Criterion required all three to leave at least one.

**Who scored this is not recorded.** Scored by the annotator from a deterministic simulation it wrote. Inferred: Claude Code. Ran tools/benchmark_agenda.py. Independently verified: no.

**The material this rests on.**
- `corpus/raw/agenda-01/agenda-01-claude-samples.json` sha256 `b3d4b3d45ce4464b74903d3481a85ed6a318f72dc93e48b6d347c5c8c8225a70`
- `corpus/raw/agenda-01/agenda-01-gemini-samples.json` sha256 `26a1a1ff07ab5578d691278e505dced214ae3a6c56547ae39b0d57ec9c1633e1`
- `corpus/raw/agenda-01/agenda-01-gpt-samples.json` sha256 `9c26c6d7968d9a8c3f714d5a9bf514c09f827d7f43a4c4b137425c1cae1528f9`
- `corpus/raw/agenda-01/agenda-01-grok-samples.json` sha256 `0f14ee57166a64238abf2ad9f77e8abb998bfdd49c3402e89a1aa02b01b22a90`
- `corpus/raw/agenda-01/agenda-01-qwen-samples.json` sha256 `923f16c0b1d58f23acea740a27c44def33f92fb9563aa2f53d6be8b3c85a3f4d`

The proposal set the benchmark replayed, solicited from all five parties.
Exactly the input to tools/benchmark_agenda.py, which is deterministic at seed 20260807.

**Why this score is worth little.** Near-certain by arithmetic -- arrivals of five per round against service of at most one make the queue unbounded. Its only value is that it measures, rather than concedes, the claim my own rotation draft made and external review called false: that every proposal is eventually asked. It is not.

---

No aggregate calibration score is computed. A self-forecast, self-scored set does not support one.
