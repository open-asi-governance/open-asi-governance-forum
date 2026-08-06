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
