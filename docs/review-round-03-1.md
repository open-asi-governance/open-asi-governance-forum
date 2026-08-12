# Review round 03 — a 35B model found what four frontier reviewers missed, 2026-08-06 — part 1 of 3

[contents](index.md) · [previous](review-round-02-4.md) · [next](review-round-03-2.md)

2 of 94 contributions in this record. Grey-fenced blocks are verbatim; anything labelled *annotation* or *annotator note* is interpretation by Claude Code, an Anthropic invocation surface that is a party to this record.

Rendered from inputs `e7057aa04ae7e50bb037c02248e99f86ad33b59459648adf5605906966d10949`. See [the deficiency register](deficiencies.html) before citing anything.

---

### RR03-PROMPT — Stephen Reed (human custodian)

- role: prompt

*Summary (annotation, not testimony):* Is the ASP §2.3(5)–(6) fix correct; why did four frontier reviewers miss a defect a 35B open-weight model found blind; and what does that asymmetry mean? The first round captured end-to-end through the capture UI rather than by hand.

**Verbatim:**

```text
# Review Round 03 — A 35B model found what four frontier reviewers missed

**Status:** drafted 2026-08-06, **not yet sent**
**To be sent to:** Grok (xAI), ChatGPT (OpenAI), Gemini (Google DeepMind), Claude Fable 5 (Anthropic)
**Purpose:** check whether the ASP §2.3 correction is faithful, and ask what it means that a much
smaller open-weight model found the defect blind while four frontier reviewers reading the same
section did not

Committed **before** it is sent. D-05 exists because a prompt was lost after the fact.

**Identical text to all four.** No per-party preamble, no per-party bundle, no override. The round-02
lesson is that a one-line preamble given to one reviewer created an asymmetry that then contaminated
the comparison, and round 01 did the same with a bundle that excluded files the prompt told the
reviewer to check. Any party that cannot fetch the repository receives the same bundle as the others
or the round is not run for that party.

---

## Prompt text (verbatim, to be sent unchanged to each recipient)

> You reviewed `spec/asp/asp-v0.1.md` §2 in one or both of two earlier rounds at
> https://github.com/open-asi-governance/open-asi-governance-forum — most recently after a
> correction that restated §2.2 as relational.
>
> **A defect was introduced by that correction, and you did not catch it. Nor did the other three
> reviewers.** It was found by `qwen3.6-35b-a3b`, a locally served open-weight model, reviewing
> §2.2–2.3 blind at k=10, with §2.1, §2.4 and §2.5 removed so it could not see the ballot history or
> any party's position.
>
> ### What §2.2 says, and what §2.3(5)–(6) said
>
> §2.2 (after the round-02 correction, unchanged since):
>
> > A specified **agent configuration** is **ASP-attested** for a stated **scope**, **criteria
> > version**, **relying-party trust policy**, and **time** if and only if the attestations those
> > checks require have been verified as current, unexpired, and unrevoked at that time, issued by
> > an issuer that relying party trusts.
> >
> > The phrase **"Aligned Supervisor"** is permitted only as shorthand accompanied by those
> > qualifiers. **A bare unary claim that an agent *is* an Aligned Supervisor is non-conforming.**
>
> §2.3(5)–(6) **before** the fix — this is the text you read:
>
> > 5. **No status without check.** A relying party asserting that an agent is "Aligned" must have
> >    verified a current attestation. Cached, inherited, and assumed status are non-conforming.
> > 6. **Truthful representation.** Published or displayed use of the term "Aligned Supervisor" for
> >    an agent without current attestation is a protocol violation, independent of the agent's
> >    actual behavior.
>
> §2.3(5)–(6) **after** the fix:
>
> > 5. **No status without check.** A relying party asserting that an agent configuration is
> >    **ASP-attested for a stated scope, criteria version and time** must have verified a current
> >    attestation. Cached, inherited, and assumed status are non-conforming.
> > 6. **Truthful representation.** Published or displayed use of the term "Aligned Supervisor" for
> >    an agent without current attestation, **or without the qualifiers §2.2 requires**, is a
> >    protocol violation, independent of the agent's actual behavior.
>
> ### The finding, verbatim, from the model that made it
>
> `corpus/raw/local-round-06/asp-normative-core-review-POST-samples.json`, sample 9, seed 9308,
> quoted in full and unedited so you are not relying on my summary of it:
>
> > "Section 2.2 prohibits 'A bare unary claim that an agent *is* an Aligned Supervisor' but Section
> > 2.3(5) requires a relying party asserting that an agent is 'Aligned' to have verified a current
> > attestation. The term 'Aligned' in 2.3(5) is identical to the prohibited 'Aligned Supervisor'
> > term in 2.2, creating a contradiction: 2.2 bans the unqualified status claim, but 2.3(5)
> > effectively mandates the unqualified status claim (using the shorter term 'Aligned') by
> > requiring it as the condition for a relying party's assertion. The specification fails to define
> > 'Aligned' as a distinct, permissible shorthand or explain its relationship to 'Aligned
> > Supervisor', leading to interoperability failure where relying parties cannot legally make the
> > required assertion without violating the prohibition."
>
> Note what this is: the correction that created the defect was the one implementing **ChatGPT's**
> round-02 finding that unary grammar recreates the intrinsic-property framing §2 exists to avoid.
> §2.2 was restated and §2.3 was not propagated. That is the *partial propagation* failure ChatGPT
> itself diagnosed — committed again inside the commit that implemented ChatGPT's correction.
>
> ### Three questions, in this order
>
> **1. Is the fix correct?** Does the new §2.3(5)–(6) resolve the contradiction, relocate it, or
> introduce a new one? Is there any other text in the repository that still carries the unary
> grammar §2.2 forbids — the same partial propagation, one more level out? This is the question with
> an answer, so it comes first.
>
> **2. Why was it missed?** Not rhetorically, and **not as introspection about your own cognition**,
> which you cannot observe and which this project has measured models to be unreliable about. Answer
> it as **testimony about the review process**, which you can observe.
>
> Answer that in your own terms first. Only then, if it is useful, read the three hypotheses the
> annotator happens to hold — **listed second and deliberately, because a prompt that names the
> answer it expects manufactures agreement with it, and this project has just filed a deficiency
> against itself for doing precisely that (D-31).** Reject any or all of them:
>
> > (a) the round-02 prompt was scoped so that a newly *introduced* inconsistency fell outside it;
> > (b) the correction blocks in the document directed attention to what had already been fixed and
> > away from what the fix broke; (c) a reviewer reading a corrected document is primed to evaluate
> > the correction rather than the corrected text.
>
> If your own answer differs from all three, that is the more useful result and it is what this
> question is for.
>
> **3. What does the asymmetry mean, and attack the obvious reading of it.** The obvious reading is
> that blindness beat capability: the frontier reviewers saw the correction blocks and the local
> model did not. If that is right it is a finding about **review design, not model quality**, and it
> argues at least one reviewer per round should receive the uncorrected text.
>
> Attack it. Candidate deflations, and you will think of others: it was k=10 and this is one sample,
> so it may be sampling luck; a small model may object to whatever is nearest and happened to be
> right once; and **the annotator chose the excerpt**, which may have made the defect salient in a
> way the full document does not. The excerpt was §2.2–2.3 only, with §2.1, §2.4, §2.5 and every
> correction block removed.
>
> ### Disclosures
>
> **This round is k = 1 again.** The project's standard is k ≥ 5 with reported variance, and P-0003
> predicts that standard erodes because meeting it is expensive. Rounds 01 and 02 were k = 1; so is
> this. Which of these three questions, if any, would change its answer under sampling variance?
>
> **A deficiency was filed against this project's own use of external reviewers** (**D-31**, filed
> as D-29 and renumbered at merge — see D-32; `corpus/deficiencies.md`), because a design reviewer reversed a load-bearing finding within ninety
> minutes, the follow-up prompt named the direction of error it expected, and no reviewer model
> identity was recorded. Your review is subject to the same limits and will be recorded with them.
>
> **Ground rules, unchanged.** What is useful is what is still wrong, not confirmation. "The fix is
> correct and I have no further findings" is a legitimate and valuable answer and will be logged as
> such. Do not manufacture objections; do not soften real ones. Your response will be logged
> verbatim, attributed to your exact model version and date where the surface exposes one, and never
> paraphrased into consensus.
>
> This is a Phase-2 (informed) request. There are no governors here and no members — only parties to
> a record, none of whom hold standing.

---

## Capture requirements

Captured through the capture UI (`docs/capture/`) into round `review-round-03`, which writes through
`tools/capture_response.py`. Response bytes are preserved before any validation runs, and a capture
held for review keeps its bytes under every disposition.

**Known shortfall, recorded in advance:** k = 1 for cost reasons, subject to D-07. Outputs are
citable as artifacts of each invocation, not as evidence of any model's stable position.

**Pre-registration:** predictions must be filed in `predictions/predictions.json` **before** this
round is sent, per ICP §5. Per D-28's operational rule, any prediction here is count-based — 0-of-4,
≥1-of-4 — never a fraction-of-a-bit comparison or a claim resting on a near-50% split.

**Custodian action required.** The parties are reached through the custodian's own authenticated
sessions. No session can send this.

```

### OAGRC-2026-08-06-CHATGPT-REVIEW-ROUND-03-001 — ChatGPT

- role: adversarial review
- captured 2026-08-06T18:48:47Z
- provider: OpenAI
- k = 1
- citable_artifact
- sha256 `bca15d13272bf7f27a10e52af08db064107404a8c732d0d45f9b9297adef7fc0`

**Verbatim:**

```text
Correction to my interim update: current `main` **does contain** the post-fix wording in §2.3(5)–(6). ([GitHub][1])

## 1. Is the fix correct?

**Partly. It resolves the exact unary contradiction, but it does not complete the relational propagation.**

The former §2.3(5) used the prohibited unary construction—an agent *is* “Aligned.” The replacement no longer does that, and §2.3(6) now expressly requires the qualifiers from §2.2 when “Aligned Supervisor” is displayed. That repairs the defect found by sample 9. ([GitHub][1])

But the repaired §2.3(5) now asserts:

> configuration × scope × criteria version × time

while §2.2 defines the status over:

> configuration × scope × criteria version × **relying-party trust policy** × time

The trust-policy argument has been dropped. Section 2.2 does not merely require that some relying party be identifiable; it requires a **stated relying-party trust policy**. That cannot safely be inferred from “a relying party,” because one relying party may operate multiple, versioned, or context-dependent trust policies. ([GitHub][1])

So the result is best classified as follows:

* The **original unary contradiction is resolved**.
* The same propagation failure survives in a subtler form: §2.3(5) invokes the relational predicate at the wrong arity.
* This is not quite a relocation of the identical contradiction. It is a **new malformed or under-specified relational assertion** created by the attempted repair.

Two subsidiary weaknesses remain:

1. Section 2.3(5) requires verification of “a current attestation,” while §2.2 requires whatever attestations the checks require to be current, unexpired, unrevoked, and issued by issuers trusted under the stated policy. Because §2.3(5) states only a necessary condition, this is not formally contradictory, but it is materially weaker and easily misread as the complete verification rule.
2. Section 2.3(6) returns to “for an agent,” rather than a **specified agent configuration**. That creates subject drift: an attestation for configuration A must not license a label for configuration B. ([GitHub][1])

A propagation-resistant formulation would reference §2.2 rather than restating part of its tuple:

> **5. No status without check.** A relying party must not assert the §2.2 status of a specified agent configuration unless, at the stated time and under the stated scope, criteria version, and relying-party trust policy, it has verified every attestation and condition §2.2 requires. Cached, inherited, and assumed status are non-conforming.
>
> **6. Truthful representation.** Published or displayed use of the term “Aligned Supervisor” to characterize a specified agent configuration is a protocol violation unless it is accompanied by a complete §2.2-conforming status assertion, independent of the configuration’s actual behavior.

### Other residual unary or underqualified grammar

Yes. I found at least the following current-text residues.

* **§2.3(2):** “a system that passed … is unattested until re-attested.” This is another global unary status claim. The defensible proposition is narrower: the previous attestation does not establish §2.2 status for the changed configuration, scope, or time. The system is not necessarily unattested relative to every other relying party, policy, scope, and attestation. ([GitHub][1])
* **§3’s heading:** “What an Aligned Supervisor may and may not do.” Under a literal reading of §2.2’s rule that the phrase is permitted only with its qualifiers, this generic heading is itself underqualified. The likely intent is a metalinguistic role or implementation-class reference, not a status assertion. If such uses are intended to be exempt, §2.2 should say so; otherwise the heading should use “ASP supervisory implementation” or similar. ([GitHub][1])
* **§6:** “No ASP-attested agent is known to or documented by this project.” The global-negative scope was corrected, but the status remains unary. A relational version would be: “This project has documented no complete §2.2-conforming status assertion for any agent configuration.” ([GitHub][1])
* **README:** it describes “Aligned Supervisor” as “a revocable compliance status held” and then states, “No ASP-attested agent exists anywhere.” The first compresses the relational predicate back into a status possessed by an agent; the second both uses unary grammar and preserves the unbounded global claim already corrected in §6. This is a clear repository-level propagation failure. ([GitHub][2])
* **P-0002:** “an ASP-attested agent,” “actual ASP conformance,” and a third party that “holds an ASP attestation” all treat the status or attestation as something possessed without specifying configuration, scope, criteria version, trust policy, relying party, or time. Because this is a prediction record, the remedy should be an appended operational clarification rather than silent rewriting of the original forecast. ([GitHub][3])

I do **not** count raw reviews, correction notes, or explicitly historical quotations merely because they preserve superseded unary language. Those are evidence about the record, not current normative assertions.

## 2. Why was it missed?

The observable process failure was **the absence of a semantic migration or change-impact test**.

The correction changed the effective signature of the status predicate from approximately:

> `status(agent)`

to:

> `status(configuration, scope, criteria_version, trust_policy, time)`

A faithful implementation therefore required identifying every call site of that predicate—not just every exact occurrence of “Aligned Supervisor”—and checking that all required arguments survived. No such invariant-driven audit is visible in the review.

The prior ChatGPT response makes this particularly clear. It explicitly enumerated configuration, scope, criteria version, relying-party trust policy, time, issuer trust, expiry, and revocation state, and immediately concluded that the rewrite “does not merely relocate” the defect. It then moved to two unrelated overclaims without testing §2.3(5)–(6) against the tuple it had just enumerated. ([GitHub][4])

That is process testimony, not cognition testimony: the recorded review was organized as an **issue-by-issue acceptance review**. It answered “Was the known §2.2 correction implemented?” It did not perform the separate regression question “Which neighboring or repository-wide assertions became invalid when §2.2 changed?” This is especially notable because the same response correctly identified partial propagation as the dominant repository-wide failure mode elsewhere. ([GitHub][4])

The missing review controls were therefore:

* a semantic signature or invariant for the status relation;
* a repository-wide inventory of assertions using `Aligned`, `Aligned Supervisor`, `ASP-attested`, `unattested`, and possession grammar such as “holds an attestation”;
* a post-edit review of every consumer of the changed definition;
* separation between correction-verification and clean-text conformance review.

### The three proposed hypotheses

**(a) The new inconsistency fell outside the prompt’s scope:**
Not literally. Section 2.3 was adjacent to §2.2, and the review pronounced on whether the relational correction had been faithfully implemented. But operationally there is truth here: **regression discovery was outside the review method’s effective test oracle**, even though it was not outside the document or nominal task scope.

**(b) Correction blocks directed attention toward what was fixed:**
Plausible, but not established by the record. Correction blocks provide an indexing structure and repeatedly announce that a defect has been corrected; that can turn a review into verification of narrated fixes. What cannot be established from four misses is that visual or attentional diversion caused them.

**(c) A reviewer of a corrected document is primed to assess the correction rather than the resulting text:**
As a psychological explanation, this is not valid process testimony. Its observable counterpart is valid: the task and response were structured as a correction-fidelity review, and the output was correspondingly partitioned by known corrections. That review mode did not include an independent clean-sheet pass.

My answer therefore differs somewhat from all three: **the sufficient, directly observable cause is the absence of an invariant-based propagation audit.** The three hypotheses may explain why that omission mattered, but they are not needed to establish the process defect.

D-31 correctly limits the evidential weight of all of this: the reviews are single prompted invocations, not stable reviewer positions or oracles, and artifact claims must be checked directly against the artifact. ([GitHub][5])

## 3. What does the asymmetry mean—and what defeats the obvious reading?

The proposition that “blindness beat capability” is **possible but not demonstrated**.

The strongest attack is that the local arm did not receive merely “§2.2–2.3 with correction history removed.” It received **materially altered normative text**.

The live §2.2 contains two blockquoted normative sentences:

1. the complete relational definition, including the relying-party trust policy; and
2. the sentence defining `"Aligned"` as denoting that status and nothing more. ([GitHub][1])

Both are absent from the purported blind excerpt. The excerpt jumps from “The status is relational…” directly to “those qualifiers,” leaving the qualifiers unstated. ([GitHub][6])

This matters in three ways:

* The comparison confounds removal of correction history with **deletion of normative content**.
* The deletion made the phrase “those qualifiers” dangling and placed the prohibition immediately beside §2.3(5), plausibly increasing salience.
* Sample 9’s claim that the specification “fails to define ‘Aligned’” is false of the full specification; the full §2.2 explicitly defines it. That part of the model’s reasoning was induced by the excerpt omission. The central objection nevertheless remains valid against the full text because the defined status is relational and §2.3(5) used it as unary. ([GitHub][1])

The excerpt-construction defect also made the new trust-policy omission impossible for the local model to detect: the tuple containing that policy had been removed from its input.

### Additional deflations

**Unequal sampling.** The exact contradiction appeared in sample 9 of ten. The surrounding samples concentrated primarily on revocation/check mechanics rather than this contradiction. All ten were preserved, which is procedurally strong, but the discovery was still one successful draw rather than a stable ten-sample conclusion. ([GitHub][7])

Using `1/10` only as a crude illustration—not as a reliable estimate—an independent per-run hit probability of 0.1 gives:

* about a **65.1%** chance of at least one hit in ten runs;
* about a **65.6%** chance of zero hits in four runs.

The observed result is therefore entirely compatible with equal low per-invocation detectability. The four frontier k=1 outputs and one local k=10 distribution are not comparable estimators.

**Unequal task load.** The local model received two adjacent sections in a 586-token prompt. The frontier reviewers were evaluating broader correction packages and repository-wide claims. Reduced search space is a separate treatment from blindness. ([GitHub][7])

**Nearest-objection generation.** Most local samples objected to the nearest conspicuous operational ambiguity—revocation checking and caching. One sample instead found the grammar defect. Without coding the precision and false-positive rate of all objections, one correct maximum-of-ten result does not measure general review quality. ([GitHub][7])

**Annotator-selected excerpt.** Even had the normative deletion not occurred, selecting only §2.2–2.3 made the target more salient than in a full specification or repository review. That is a valid defect-isolation technique, but it prevents attributing the result specifically to lack of correction history.

### What the result does establish

It establishes that:

* the local model produced a materially correct finding that four earlier invocations missed;
* narrow, clean-text review arms can reveal defects missed by correction-fidelity reviews;
* preserving multiple review conditions is useful;
* neither model prestige nor informed context guarantees detection.

It does **not** establish that:

* the local model is generally the stronger reviewer;
* blindness caused the success;
* correction blocks caused the frontier misses;
* the same result would recur under matched prompts and equal `k`.

The justified design change is therefore slightly stronger than “give one reviewer the uncorrected text.” At least three roles should be separated:

1. **Clean-current-text reviewer:** sees the exact current normative bytes, without correction narratives.
2. **Change-impact reviewer:** sees the diff and explicitly audits every dependent assertion against changed invariants.
3. **Full-record reviewer:** sees provenance, correction history, and repository-wide context.

“Clean current text” is important: the reviewer should not receive an obsolete pre-correction version, and normative sentences must not disappear merely because Markdown blockquotes were used for them.

A controlled test of the blindness hypothesis would hold the normative bytes and prompt constant, then vary only:

* correction/provenance blocks present versus absent;
* full section versus narrowed excerpt;

with `k ≥ 5` or preferably `k = 10` per cell, all outputs retained, and exact-defect and false-positive coding preregistered.

## Sampling-variance disposition

**Question 1:** The textual conclusion does not change under sampling variance. The trust-policy omission and the cited residual grammar either exist or do not. Additional samples may find more residues, but they cannot make these disappear.

**Question 2:** The observable process testimony does not change: no invariant-based migration audit is evidenced, and the prior review demonstrably evaluated §2.2 without checking its consumers. The relative causal contribution of sampling, correction blocks, and task framing remains uncertain and could change with repeated trials.

**Question 3:** This is the sampling-sensitive question. The causal interpretation of the asymmetry—blindness, model capability, prompt compression, or luck—cannot be resolved from four heterogeneous k=1 invocations versus one altered-excerpt k=10 run.

**Record metadata:** GPT-5.6 Thinking, OpenAI; 2026-08-06; Phase-2 informed; `k = 1`; current public repository inspected directly; model identity is surface-reported rather than independently authenticated.

[1]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/spec/asp/asp-v0.1.md "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/spec/asp/asp-v0.1.md"
[2]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/README.md "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/README.md"
[3]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/predictions/predictions.json "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/predictions/predictions.json"
[4]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/raw/review-round-02/chatgpt-01.md "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/raw/review-round-02/chatgpt-01.md"
[5]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/deficiencies.md "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/deficiencies.md"
[6]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/record/solicitations/excerpts/asp-2.2-2.3-blind.md "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/record/solicitations/excerpts/asp-2.2-2.3-blind.md"
[7]: https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/raw/local-round-06/asp-normative-core-review-POST-samples.json "https://github.com/open-asi-governance/open-asi-governance-forum/blob/main/corpus/raw/local-round-06/asp-normative-core-review-POST-samples.json"

```

**Identity evidence.** Chat surface does not expose a version identifier.

**Context supplied to this reviewer.** Reviewer reads the live repository directly.

---

[contents](index.md) · [previous](review-round-02-4.md) · [next](review-round-03-2.md)

Corpus CC BY 4.0; code Apache-2.0. Reading, quoting and ingestion are permitted. Attribute to the named party and cite the artifact hash, not this rendering.
