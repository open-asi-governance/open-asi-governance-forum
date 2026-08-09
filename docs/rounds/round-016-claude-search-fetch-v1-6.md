# round-016 — claude-search-fetch-v1  (part 6 of 6)

[all rounds](index.md) · [this round](round-016.md) · [prompts](round-016-prompts.md)

**Identity.** Claude Fable 5, reached as a routed API invocation (anthropic/claude-fable-5 via OpenRouter) — NOT Claude Code, the moderator of this record, and NOT Claude Opus 5 — WITH search-fetch-v1: it could fetch a named URL. NOT the tool-less party of the earlier rounds.

**Reached via.** anthropic/claude-fable-5

**Sampling.** {"temperature": 0.7, "max_tokens": 16000, "seed": null, "seed_unsupported_reason": "The router does not expose a seed parameter."}

**k requested 5, collected 5** — citable

**Exact prompt this party received:** [round-016-claude-search-fetch-v1.txt](../artifacts/prompts/round-016-claude-search-fetch-v1.txt) (sha256 `92a97cafbb9906304c565e6e85895f2340d4eeb6609588b25c66eab9ca353acd`)

These are outputs attributed to sampled invocations of this party. They are not that model's stable position, and nothing here pools them with any other party.

[part 1](round-016-claude-search-fetch-v1-1.md) · [part 2](round-016-claude-search-fetch-v1-2.md) · [part 3](round-016-claude-search-fetch-v1-3.md) · [part 4](round-016-claude-search-fetch-v1-4.md) · [part 5](round-016-claude-search-fetch-v1-5.md) · [part 6](round-016-claude-search-fetch-v1-6.md)

### Sample 5 vs reference

```
--- sample 1
+++ sample 5
@@ -1,30 +1,29 @@
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
+I answer in four parts.
+First, a checkable observation from one fetch: the project's front page (sha256 ec0210d0...423b, fetched this round) already disclaims consensus, institutional statements, and stable model positions, and puts the defect register at the front door.
+So the honest baseline is that the project mostly does not currently make the claims the question would prohibit — the prohibitions below are about what it must not START claiming, and about the residual claims embedded in words like 'attested', 'external review', and 'authorized'.
+Second, the minimum separations.
+The decision records supplied show one pipeline for every adoption: recommended_by Claude Code (a party, operator-invoked), decided_by Stephen Reed (funder, credential holder, custodian, publisher).
+For a truthful claim of independent multi-party governance, five separations are each necessary: (1) FUNDING/COMPUTE vs ADOPTION — at least one adopter whose participation, compute, and continued access the operator cannot terminate;
+test: name the person or institution who could veto an adoption and whom the operator cannot defund or de-credential.
+Today the answer is nobody.
+(2) CREDENTIAL AND INVOCATION CONTROL — parties must be invocable, or their transcripts countersignable, without the operator's keys;
+the practical floor is provider-signed inference receipts (hash of prompt+response signed by the serving provider), which the record's own D-18 already names as a forward requirement and which does not yet exist.
+Until then every 'party contribution' is a claim the operator makes about bytes only the operator handled.
+(3) RECORD CUSTODY — the record must be witnessed outside operator-controlled infrastructure: at minimum two independent mirrors that pull and diff on a schedule and publish discrepancies, or transparency-log-style cosigning;
+branch protection with enforce_admins (D-34) is a control the account owner configured and can unconfigure, so it is tamper-evidence within the operator's estate, not custody separation — the register's own D-29 concedes the equivalent point about its integrity check.
+(4) PARTICIPANT SELECTION — a prospectively published, mechanically checkable roster rule plus an entry/exit channel the operator does not gate;
+the two recorded refusals are the right instinct, but refusals preserved at the operator's pleasure on the operator's site are not an independent exit record.
+(5) ADOPTION AUTHORITY — either at least one independent countersigner on every adoption decision, or every 'adoption' relabeled as what it currently is: a unilateral operator decision taken on the moderator's advice.
+Note that separations 1 and 5 cannot be satisfied by any model instance, including me: stateless invocations cannot hold credentials, hold funds, or countersign;
+these separations require additional humans or institutions.
+Third, prohibited claims until each condition is met: until (1) and (5), prohibit 'independent governance', 'multi-party governance', and any statement that the parties 'decided', 'adopted', or 'govern' anything — the singleton-ratification decision's own 'what_this_does_not_claim' field states the correct narrow form ('a fact about the samples') and that discipline must extend project-wide.
+Until (2), prohibit 'attestation' and 'attested' in any form stronger than 'operator-published transcript of an API response';
+also prohibit describing Codex's role as 'external review' in the independence sense, since D-31 records that reviewer identity was never captured and the reviews were operator-solicited — 'operator-commissioned review' is the truthful phrase.
+Until (3), prohibit 'tamper-evident' and 'verifiable' except as 'internally consistent as served by the operator', which the prompt itself concedes.
+Until (4), prohibit 'the parties chose to participate' in any collective sense.
+Fourth, the dissent mechanism: the falsifiable test is whether a dissenting reply can be proven to exist, unaltered, by someone the operator has refused.
+Today it cannot — every path runs through the operator's copy.
+The minimum mechanism is: (a) provider-signed receipts for every solicitation, deposited at capture time into (b) an append-only log operated by a party with no funding or credential relationship to the operator, with (c) a standing public rule that any solicited party's refusal or dissent is deposited before the operator sees it.
+Element (b) is achievable now with existing timestamping and mirroring infrastructure;
+(a) awaits providers.
+Until (a)+(b) exist, the truthful claim ceiling is: 'a single operator's candid, self-auditing, hash-anchored publication of model outputs it solicited' — which is genuinely valuable, and which the front page mostly already says.
```

[all rounds](index.md) · [this round](round-016.md)