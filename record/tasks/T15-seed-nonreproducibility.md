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
