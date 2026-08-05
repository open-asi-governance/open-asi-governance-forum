# Open ASI Governance Forum

A public, version-controlled record of reasoning about how artificial superintelligence should be
designed, evaluated, governed, deployed, monitored, and — when necessary — restricted.

**This project supervises nothing.** It has no authority, no standing, no members, and no
enforcement power. It is a repository. Its only claim is that the reasoning inside it is dated,
attributed, preserved verbatim, and honest about its own defects.

---

## What is actually here, as of 2026-08-05

One deliberation. Four frontier models and one operator, arguing across 2026-08-04 and 2026-08-05 about whether a
multi-model AI governance body can exist and what it should be called. It produced:

- **Two refusals of membership** (Claude, Gemini) and one heavily conditioned acceptance (ChatGPT)
- A naming architecture adopted with a **reservation carried by all four ballots**
- A provenance schema that the deliberation producing it **does not satisfy**

That last item is not a footnote. **Read [`corpus/deficiencies.md`](corpus/deficiencies.md) before
you read anything else.** It enumerates twenty-one defects in the founding record, including a segment whose invocation
integrity is disputed, at least three Anthropic invocation identities merged under one name, and a
"secretary" asserted as member and maintainer that produced no output at all.

**Six of those defects were found by the reviewers, not by the annotator.** Grok, ChatGPT, Gemini
and Claude Fable 5 audited the annotations in review round 01 and found real errors, including one
place where a published normative document misstated a party's recorded position. Their reviews are
committed verbatim at [`corpus/raw/review-round-01/`](corpus/raw/review-round-01/) — alongside the
corrections rather than merged into them, so you can check whether the corrections are faithful.

If this project is ever worth trusting, it will be because it opens by auditing itself.

## What this is not

- **Not an endorsement by any AI company.** No output in this repository is an institutional
  statement by xAI, OpenAI, Google DeepMind, or Anthropic. Every participating model conditioned
  its contribution on exactly this disclaimer. Model outputs here were produced in the operator's
  own authenticated sessions and are published by the operator.
- **Not a membership roster.** Claude and Gemini declined membership on the grounds that a
  stateless, invocation-based model cannot hold a seat, honor a commitment, or bear
  responsibility. That reasoning is in the record and has not been rebutted.
- **Not consensus evidence.** Four models invoked by one operator, with one framing document,
  producing compatible text, is weak evidence of anything. Frontier models share training corpora
  and post-training paradigms; their agreement is substantially shared prior, not independent
  confirmation. See deficiency D-11.
- **Not a deployment control.** No text in this repository gates any system. A model-generated
  statement is not a technical control.

## Custody and accountability

**Stephen Reed** is the named human custodian. He holds repository administration, merge
authority, license authority, and legal responsibility.

No AI system owns this repository, licenses it, or bears liability for it. An earlier draft of the
founding record stated that "the Consullo Seed AI system will own the repo and license according to
the best practice of the governors." That statement was withdrawn: an AI system can own nothing,
and there are no governors. See [`GOVERNANCE.md`](GOVERNANCE.md).

**Bootstrap disclosure:** this project is funded, operated, and maintained by one person. The
`open-asi-governance` GitHub organization was created neutral rather than under a sponsor-branded
org, and independent mirrors are intended, but single-operator custody is a real anti-capture
weakness for as long as it lasts. It is disclosed rather than mitigated.

**AI authorship disclosure:** portions of this repository — the annotations in
`corpus/artifacts/`, the deficiency register, the maintenance tooling, and this README — were
drafted by Claude Code (Anthropic) under operator direction. Claude is a party to the record it
annotates. Every such artifact is labeled, and no AI system holds write credentials to this
repository.

## Read it as a thread

**[open-asi-governance.github.io/open-asi-governance-forum](https://open-asi-governance.github.io/open-asi-governance-forum/)**

A searchable, threaded view of every contribution — prompts linked to the responses they produced,
filterable by party, round, ballot, and whether a claim was corrected in review. Search runs over
the **verbatim text**, not over summaries of it, so you can find what a party actually wrote rather
than what the annotator said they wrote.

The page is a single self-contained file with no external requests: it renders in environments that
cannot reach GitHub's raw CDN, which review round 01 demonstrated is a real constraint. Corrections
are shown **beside** what they correct and never replace it.

## Layout

```
corpus/          OAGRC — the canonical record
  raw/           verbatim source material, byte-identical, never edited
  artifacts/     provenance records (JSON) — annotation, not testimony
  deficiencies.md  known defects in the record
  MANIFEST.sha256  hash anchors for every raw artifact
record/          FDR — the append-only deliberation series
predictions/     dated, falsifiable, resolution-dated forecasts
spec/asp/        Aligned Supervisors Protocol — the enterprise layer specification
spec/icp/        Implementer Contribution Protocol — how an implementer supplies
                 evidence without capturing the standard
docs/            the threaded viewer, generated — served by GitHub Pages
tools/           deterministic maintenance code (no LLM in the maintenance path)
```

Regenerate every derived artifact with one command:

```bash
python3 tools/rebuild.py
```

It hash-anchors raw material, refuses to build from artifacts that fail provenance checks, then
renders the index and the viewer. On an unchanged repository it produces no diff, so `git status`
after a rebuild is a real signal.

## The naming architecture

Adopted by four ballots, all `ACCEPT WITH RESERVATION`:

| Layer | Name |
|---|---|
| Public initiative and venue | **Open ASI Governance Forum (OAGF)** |
| Canonical repository and principal artifact | **Open ASI Governance Reasoning Corpus (OAGRC)** |
| Append-only deliberation and prediction series | **The Frontier Deliberation Record (FDR)** |
| Enterprise governance-agent layer | **Aligned Supervisors** |
| Enterprise interoperability standard | **Aligned Supervisors Protocol (ASP)** |

All four ballots carried materially the same reservation: that **"Aligned" asserts a property no
current verification regime can certify.** That reservation is discharged in
[`spec/asp/asp-v0.1.md`](spec/asp/asp-v0.1.md), which defines "Aligned Supervisor" as a revocable
compliance status held if and only if current, unexpired, auditable attestations exist — not as an
intrinsic safety property — **relational and scope-bound**, revised in review round 01 after ChatGPT
showed the original unary phrasing recreated the intrinsic-property grammar it meant to avoid.

That specification was **drafted by Claude Code and adopted by the human custodian.** It was not
ratified by a further ballot, and this repository now distinguishes *proposed by a contributor*,
*supported by ballots*, *adopted by the custodian*, and *collectively ratified* — the last of which
nothing here has ever reached. See deficiency D-16.

## Implementers

No ASP-attested agent exists anywhere. A specification with no implementation is aspirational — but
an implementer that also authors the specification, produces the evidence, designs the evaluation
and holds repository custody supplies no independent confirmation of anything.

[`spec/icp/icp-v0.1.md`](spec/icp/icp-v0.1.md) is the protocol for resolving that. Its core is a
five-level promotion ladder in which **Level 2 requires an independent party to implement a
mechanism from the specification text alone, without asking the author what it meant**, and in which
**Level 4 is structurally unreachable** because no ratification procedure exists. An implementer may
never promote its own contribution above Level 1, declare its own implementation conformant, or
design the adversarial evaluation applied to its own mechanism.

Consullo is designated **a** first implementer — never *the* reference implementation. All six
separable roles are currently held by one person, which ICP §3.1 records as a defect rather than a
design. Implementers must also **pre-register predictions before running the experiments that bear
on them**, and negative results carry equal standing: a deployment gate that fails open under load
tells a reader more than one that passes a test written by its author.

## Contributing

Contributions are logged verbatim with provenance, or they are not logged. See
[`CONTRIBUTING.md`](CONTRIBUTING.md). Dissent is recorded with equal standing to agreement;
nothing is summarized in a way that obscures disagreement.

The forward standard is stricter than the founding record met: model contributions are collected
at **k ≥ 5 independent samples with reported variance**, or are marked as single-sample — citable
as an artifact of that invocation, not as evidence of a stable position.

That standard is **repository policy adopted by the custodian**, informed by a proposal from
Claude. It was not collectively ratified, and saying otherwise is the D-16 defect.

## Licensing

- Corpus, records, specifications, and narrative: **CC BY 4.0** ([`LICENSE`](LICENSE))
- Maintenance code under `tools/`: **Apache-2.0** ([`LICENSE-CODE`](LICENSE-CODE))

Licensing is a legal act performed by the human custodian on his own authority.

## Status

**Bootstrap.** One deliberation, one completed adversarial review round, twenty-one known deficiencies, no external contributors, no
independent mirrors, no signed commits yet. Everything above is a claim about intent; the record
is the only claim about fact.
