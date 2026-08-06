# T-15 · Seed non-reproducibility on the TRT-LLM serving path (D-28)

**Track C — Determinism** · branch `session/determinism` · **EXCLUSIVE inference host** ·
status: **diagnostic half complete, remedy not applied**

## Do not re-derive this. It is already found.

### Measured 2026-08-06, four isolating tests against the live server
| Test | Result |
|---|---|
| temperature 0, sequential, one request in flight | **10/10 distinct** |
| `top_k=1` forced greedy (rules out temperature not honoured) | **8/8 distinct** |
| unique prefix per call (KV block reuse impossible) | **8/8 distinct** |
| identical prompt (KV reuse eligible) | 7/8 distinct |
| same seed, same prompt, same temperature, two runs | same answer **8/20** |

Not the sampler. Not the seed. Not in-flight batching. Not KV reuse. **The logits vary.**

### Root cause, in vendor source
`tensorrt_llm/llmapi/llm_args.py`, `MoeConfig`:
```
disable_finalize_fusion: bool = Field(default=False,
    description="Disable FC2+finalize kernel fusion in CUTLASS MoE backend. Setting this to
                 True recovers deterministic numerical behavior with top-k > 2.")
```
This model is `num_experts_per_tok=8` over `num_experts=256`. **Top-k is 8, far above 2**, the
fusion is active in exactly the regime the vendor documents as non-deterministic, and the default
leaves it on. `sampling_params.py` confirms greedy was correctly selected —
`params_imply_explicit_greedy` returns true for `top_k == 1 or top_p == 0.0 or temperature == 0` —
so parameter handling was never implicated.

### The refinement that governs every prior result
The perturbation is **tiny**. *"Count from 1 to 12"* returns **6/6 identical** under conditions
giving 8/8 distinct on an open-ended prompt. It flips output only where the top-two logits are close
enough that rounding changes the argmax, after which divergence cascades.

**So the apparatus is least reliable exactly where the measurement is most interesting.** The rule,
now in the register: modal share at or beyond 90/10 and rare-event counts are robust; splits near
50% are noise-dominated and support no claim; differences below ~0.5 bits are not effects.

### Already done
D-28 root-caused with the source quoted · QCP's "fully met" provenance claim withdrawn · schema
marks the seed **non-reproducing** · P-0008's evidence annotated void.

## Remaining
1. Apply whichever remedy the Codex review favours — **not a one-line change.** The profile in force
   is H3, whose header records an OOM history: a 32 GiB host cache left 160–255 MiB device-free and
   killed the PyExecutor while the frontend still returned 200. The fusion exists for throughput.
2. **Measure the noise floor properly.** Currently n=2 runs.
3. Add a **test-retest arm** to `tools/solicit_local.py` as a first-class option, so skipping it is
   a decision rather than an oversight.
4. **Retro-annotate** `local-round-01`, `-02`, `-04`, `-05`, `-07` — all carry entropy figures whose
   run-to-run component is unmeasured.

## Open question that may make the remedy unnecessary
Codex was asked whether determinism is even the right goal: the corpus samples k=20 at temperature
0.7 and reports distributions, so determinism matters for **reproducing a run**, not for the
distributional claims. Accepting non-determinism, measuring the floor and refusing to report effects
below it may be the better design. **If `disable_finalize_fusion` removes only one non-determinism
source among several, T-17's canary can never pass and this is the answer.**

## Upstream
Worth an issue regardless: TRT-LLM **accepts a `seed` on a MoE model with top-k > 2 and cannot
honour it, silently.** The caveat lives in a `MoeConfig` field description a user would never read.
Minimal reproducer: same prompt, same seed, temperature 0, `top_k=1`, sequential → distinct outputs.
Same class as D-01 — a field asserting a guarantee the system does not provide.


---

## Lead recorded 2026-08-06 — the top-2 logprob margin may replace k-sampling for this problem

Found while waiting on the Codex review; **measured, not speculated**, but not developed. Recorded
here because it would otherwise be lost with the session that found it, which is the category
HANDOFF.md names as always lost.

### What was measured

The server returns `logprobs` with `top_logprobs`. The **top-2 logprob margin** is directly
observable per call:

| Probe regime | mean margin | min |
|---|---|---|
| Low-entropy task — *"count from 1 to 12"*, previously **6/6 identical** under non-determinism | **8.146 nats** | 6.875 |
| Near-tie judgement — the Level-4 structural-vs-self-restraint question | **0.417 nats** | **0.000** |

A ~20× separation, and one sample returned an **exact 0.000 tie**.

### Why this matters for D-28

D-28's finding is that numeric noise flips an output **only where the top-two logits are close
enough that rounding changes the argmax**. The margin *is that quantity*, and it is observable
directly rather than inferred from a distribution.

Three consequences, none of which requires the determinism remedy:

1. **A probe can be screened before it is run.** One call reveals whether the question sits in the
   noise-dominated regime. At present a probe costs 20 calls and the corpus discovers afterward that
   it measured a coin flip — which is what `local-round-01` did.
2. **It separates "genuinely torn" from "noise-flipped" at the level of a single answer**, which
   k-sampling cannot: a 55/45 split is consistent with both a real internal near-tie and pure
   numeric jitter, and D-28 is precisely the discovery that the corpus could not tell them apart.
3. **It is cheaper by a factor of twenty**, which matters because P-0003 forecasts the k≥5 standard
   eroding under exactly that cost.

### What is NOT established

- Whether the margin predicts the *observed* k=20 dispersion quantitatively — the obvious test is to
  correlate first-token margin against measured entropy across the seven local rounds already
  committed. **That test has not been run.**
- The margin itself varies run-to-run (spread 3.125 nats on the low-entropy case, 0.625 on the
  near-tie case), being subject to the same numerics. The *scale separation* is robust; a precise
  margin value is not.
- Only the **first token** was measured. A judgement may hinge on a later token, and the enum's
  discriminating token is not always first.
- Nothing here has been reviewed by anyone.

### Why it may make the determinism remedy unnecessary

If the margin reliably identifies noise-dominated questions, the corpus does not need reproducible
runs — it needs to know **which results to disbelieve**, and it can learn that for one call instead
of twenty. That is the same conclusion Codex was asked to argue for in question 5, reached from a
different direction and with a measurement behind it.

**Run the correlation test before building anything on this.** The seven committed local rounds
supply the data at no additional inference cost.
