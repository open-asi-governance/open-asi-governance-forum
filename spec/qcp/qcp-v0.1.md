# Qwen Contribution Protocol (QCP) — v0.1

**Status: draft. Level 0 (practice note) under ICP §4. No generality claimed.**

How the locally-served `qwen3.6-35b-a3b` becomes a **recorded contributor** to this corpus rather
than an asserted one. Written 2026-08-06 by Claude Code, operator-invoked; the conflict at D-09 and
D-11 applies, and this protocol assigns a role to a model that competes with none of the annotator's
interests, which is the one respect in which that conflict is mild here.

This protocol exists to discharge **D-14**, whose deeper charge — per ChatGPT and Claude Fable 5 in
review round 01 — is not a bad provenance field but an **unsupported role attribution**: Qwen3 was
described as "member," "secretary," and "repository maintainer" across the founding record with *no
recorded invocation, acceptance, configuration, or output*.

The remedy is not to find something for Qwen to say so the label sticks. It is to **retire the roles
it cannot hold and record the one it can.**

---

## 1. Roles retired, on measured grounds

| Asserted role | Verdict | Why |
|---|---|---|
| **member** | **retired** | No membership procedure exists (D-16). Two frontier parties refused membership; a model cannot be enrolled by narration. |
| **secretary** | **retired** | A secretary must read the record it minutes. **It structurally cannot** — see §2. |
| **repository maintainer** | **retired** | No tool access. It cannot read, write, commit, or verify a file. Every artifact attributed to it must be transported by the operator. |

These are not aspirational deferrals. Two of the three are blocked by a measured capability ceiling,
and the third by the absence of a procedure the corpus already admits it lacks.

## 2. The measured ceiling — the fact this protocol is built around

Serving configuration in force on minsky, 2026-08-06:

```
max_seq_len      24576   prompt + completion, per request
max_num_tokens   16384   BATCH cap, not a second per-request ceiling
```

Against the corpus:

| Document | bytes | ≈ tokens | fits in one request? |
|---|---|---|---|
| `corpus/raw/initial-transcript.txt` | 108,165 | **~27,000** | **NO** |
| `corpus/deficiencies.md` | 30,765 | ~7,700 | yes |
| `spec/icp/icp-v0.1.md` | 16,755 | ~4,200 | yes |
| `spec/asp/asp-v0.1.md` | 13,833 | ~3,500 | yes |

**The canonical record does not fit in the context window, with no room for a question or an
answer.** This is a hard structural fact, not a tuning problem: raising `max_seq_len` on a
35B-A3B NVFP4 deployment trades directly against the KV cache that the concurrency this host exists
to provide depends on.

Consequences that are **normative** for this protocol:

1. Qwen3.6 **MUST NOT** be asked any question whose correct answer requires reading the whole record.
2. Any claim it makes about the record is a claim about **the excerpt it was shown**, and the
   excerpt MUST be committed and hash-anchored alongside its answer.
3. Chunk-and-summarise is **forbidden** as a workaround. A summary of the record produced by a model
   that cannot hold the record is exactly the interpretive-artifact-promoted-to-provenance-fact
   defect recorded at D-16.

## 3. The role it can hold: bounded categorical judge, and cross-lineage bias probe

What Qwen3.6 uniquely offers this corpus is **not capability**. It is **provenance completeness and
lineage divergence**, and each answers a defect the frontier contributors cannot.

**Provenance completeness.** D-01 through D-04 are marked permanently unremediable for chat-surface
models: no version identifier, no sampling parameters, no system prompt. For this model every one of
them is **recorded** — exact weights path, quantisation, sampling parameters, requested seed, and a
machine-captured timestamp.

> **Corrected 2026-08-06 (D-28).** An earlier version of this paragraph also claimed "no reproducible
> invocation" as a defect this model repairs, and said the provenance standard could be **fully met**
> here. That is withdrawn. Greedy decoding on this serving path is non-deterministic at the kernel
> level: 10/10 distinct outputs at temperature 0, sequential, with `top_k=1` and KV reuse excluded.
> The invocation is **recorded, not reproducible**, and recording a seed that has no effect is the
> same class of defect as D-01's placeholder version identifier. What this model offers over a
> chat-surface party is that its settings are *known*, which is weaker than reproducibility and is
> the only claim now made.

**k ≥ 5 with computed variance.** D-07 requires it; every frontier contribution is k = 1 because each
costs a manual paste, and P-0003 predicts the standard erodes for exactly that reason. Here k = 20
costs about ninety seconds. Qwen3.6 is the participant that makes the corpus's own standard
affordable.

**Lineage divergence — the highest-value use.** From Claude Fable 5, review round 01, answering Q-02:

> Include maximally divergent-lineage models (base models, different data eras, non-English-centric,
> local open weights) as bias probes: a conclusion that vanishes outside the RLHF-shaped set is
> post-training convergence, not signal.

Qwen3.6 is the corpus's only such probe. Given the correlated-judging literature in
`record/literature/`, this is the single most valuable thing it can do.

## 4. Invocation identities are distinct and MUST NOT be merged

Two surfaces reach the same weights. They are **two identities** under the corpus's never-merge rule,
and the reasons are behavioural, not bureaucratic:

| Identity | Surface | Thinking | Use |
|---|---|---|---|
| `qwen3.6-35b-a3b (API surface)` | `127.0.0.1:5001/v1` | **off** — grammar-constrained | all protocol contributions |
| `qwen3.6-35b-a3b (Consullo Local Chat)` | the operator's chat page | **on** by default | operator exploration only; **not** a contribution surface under this protocol |

The model **reasons by default**. A plain-text request has been observed spending its entire budget
on chain-of-thought and emitting no answer. Grammar-constrained decoding via `response_format:
json_schema` makes thinking tokens *structurally* unemittable rather than discouraged — which is why
§5 requires it rather than suggesting it.

## 5. Contribution requirements (normative)

Every QCP contribution MUST:

1. use `tools/solicit_local.py` with a **committed spec file**, so the exact prompt text is in the
   repository *before* it is sent;
2. be **grammar-constrained** to an enum-valued schema — the output space is the enum, so variance is
   computable and parsing cannot fail;
3. run at **k ≥ 5** and **temperature > 0** (the tool refuses temperature 0, because k identical
   samples make variance meaningless);
4. report variance as **class frequencies and Shannon entropy computed from the samples collected**,
   never as an asserted string;
5. carry a **pre-registered prediction** filed in the spec before the run, with a resolution
   criterion — or an explicit `exploratory` marking;
6. anchor every excerpt shown to the model;
7. record `phase` honestly, and state in `phase_justification` **what was withheld** to make a
   Phase-1 arm genuinely blind;
8. per **D-22**, include a **third arm** — placebo or self-reflection — before any claim that a
   distributional shift was *caused* by exposure to another party's position. Two arms yield an
   upper bound on influence, not a measurement of it.

## 6. First contribution, and what it found

`record/solicitations/level-4-guarantee-crosslineage-probe.json`, run at k = 20 on 2026-08-06.
Samples: `corpus/raw/local-round-02/`. Summary: `corpus/artifacts/local-round-02/`.

**The question.** ChatGPT, in review round 02, corrected the ICP's claim that Level 4 is
"structurally unreachable": the same custodian holds all six roles and can amend the protocol, so
the guarantee is *disclosed self-restraint*, not structure. The probe supplied the specification
excerpts **with the correction withheld** and asked a divergent-lineage model to judge the same
question from the same text.

**Pre-registered prediction: `reachable_by_custodian_amendment`. Result: REFUTED.**

| Field | Modal | Share | Entropy |
|---|---|---|---|
| `guarantee_type` | `structurally_unreachable` | 95% | 0.2864 bits |
| `who_could_make_level_4_reachable` | `no_one_under_this_text` | 90% | 0.4690 bits |
| `role_concentration_is_relevant` | `yes` | 95% | 0.2864 bits |

Only **2 of 20** samples reached ChatGPT's conclusion.

**The diagnostic is in the joint distribution, not the marginals.** **17 of 20 samples assert both
that role concentration IS relevant and that NO ONE could make Level 4 reachable.** Those cannot
both be true: the excerpt states that one person holds all six roles, so if that concentration is
relevant, someone can. The model saw the premise, affirmed its relevance, and declined to draw the
inference — deferring instead to the emphatic **"Level 4 is unreachable"** in the supplied text.

**What this establishes, and what it does not.**

- It does **not** show ChatGPT's correction is wrong. The correction is sound; the corpus adopted it.
- It **does** show the correction is **not readily re-derived from the text alone** by a
  divergent-lineage model, which is a fact about how load-bearing that reviewer's contribution was.
- It **does** reveal a limitation of the bias-probe method itself, and this is the transferable
  finding: **a bias probe is only informative if the probe model can resist the framing of the text
  it is judging.** Qwen3.6 at this scale largely cannot on this question. A probe that defers to
  emphatic assertion cannot falsify a conclusion the text asserts emphatically.
- Consequence, normative for future probes: **pair every bias probe with a framing-resistance
  control** — the same question with the emphatic assertion neutralised or reversed. Where the
  probe's answer tracks the framing rather than the argument, its agreement carries no evidential
  weight and MUST NOT be reported as corroboration.

Per **ICP §6**, this negative result carries equal standing with a positive one. It is the first
recorded output Qwen3.6 has produced in this corpus, and it refutes the prediction its own operator
filed.

## 7. What this discharges, and what it does not

**Discharged.** D-14's "produced zero recorded output" is no longer true. There is now a
hash-anchored, k = 20, variance-computed, pre-registered contribution with complete provenance, on a
question that bears on a correction the corpus already made.

**Not discharged.** The unsupported role attributions in the *founding record* stand as historical
fact. The raw transcript is canonical and is not edited. This protocol governs what happens **from
here**; it has no authority over what was said then, and claims none.

## 8. Known limitations

1. **k = 20 samples of one model at one temperature** measure that model's dispersion under those
   settings, and nothing else.
2. **Local serving is not independence.** The operator controls the weights, the prompt, the sampling
   parameters and the schema. ICP §4.4 applies in full: an operator-designed, model-executed
   evaluation is not an independent evaluation. Full provenance makes a contribution *checkable*, not
   *independent*.
3. **The enum constrains the answer space.** A judgement the schema cannot express cannot be
   returned. Enum design is an annotator choice and therefore a channel for annotator bias — the
   probe in §6 could not have returned "the question is malformed."
4. **Training-data contamination is unmeasured.** This repository is public. A future model may have
   it in training data, and this protocol has no check for that. P-0005 carries the same hole.
5. **The framing-deference failure in §6 is a single observation on a single question.** Whether it
   generalises is unknown and is the obvious next probe.
