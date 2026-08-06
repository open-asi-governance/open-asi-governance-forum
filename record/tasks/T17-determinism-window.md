# T-17 · Determinism window on the INEXPENSIVE pool host

**Track C — Determinism** · branch `session/determinism` · **EXCLUSIVE inference host** ·
status: open · **do T-15 first**

Operator decision 2026-08-06, option B: rather than swapping instances or permanently changing the
production profile, put the **same service** into deterministic mode for the duration of a
reproducibility-critical run, then restore. Scripted, integrated with the INEXPENSIVE pool.

## The mode
`moe_config.disable_finalize_fusion: true` via a **systemd drop-in** so the production profile file
is never edited, plus restart. Per-request selection is not available: `use_fused_finalize` is bound
in `fused_moe_cutlass.py.__init__` from `ModelConfig` at model load, and the flag is folded into
weight-sharing source identity. It is a load-time model property.

## Sequence
1. Drain the host from the INEXPENSIVE pool.
2. Wait for in-flight requests, with a timeout.
3. Restart with the drop-in.
4. **Verify the mode is active** before any payload runs.
5. Run the declared reproducible work.
6. Restart without the drop-in.
7. Re-add to the pool, and verify it is serving.

## The canary is the part most likely to be built wrong
This is **AS-01 in mirror image** — a production health check that passed for 4h37m against a
permanently dead engine because it used greedy decoding, which executed none of the code that had
died. Authentic, current, and structurally incapable of observing the failure.

**"Count from 1 to 12" returned 6/6 identical under the NON-deterministic configuration.** A canary
built on a low-entropy prompt passes in both modes and certifies nothing.

The canary MUST use a prompt **empirically shown to diverge** in the non-deterministic mode — the
open-ended three-risks prompt gave 8/8 distinct — at `top_k=1`, sequential, N≥8, requiring
**byte-identical** output. If it fails, the window **aborts and restores**. It never proceeds on the
assumption the config was read; a silently ignored directive is already recorded as AS-02.

## The pool risk that must not be glossed
The H3 profile header records: *"when one host is down the survivor takes all 160 workers alone and
OOMs (observed 23:31 and again 23:50 on turing), shutting down the PyExecutor while the frontend
still returns 200."*

Draining puts full load on the remainder, which has a documented OOM history **and** a documented
mode where the frontend keeps returning 200 while the executor is dead — so the pool would not
notice. The window must run at low load, throttle admission, or **verify headroom before draining
and refuse otherwise.** Draining blind reproduces a failure already written down.

## Fail-safe restore, non-negotiable
If the script dies, is killed, or the host reboots mid-window, the host must **not** stay drained or
stuck in deterministic mode. Trap on exit, plus an **independent watchdog** with a hard maximum
window duration that restores regardless. Idempotent both ways.

## Record it
Any artifact produced inside a window records that it was, **with the canary evidence attached** —
prompt, N, byte-identical result. An artifact claiming reproducibility without a passing canary is
indistinguishable from a normal-mode one: the D-01 defect again.

## Acceptance
- A full cycle runs unattended and restores the host.
- Killing the script mid-window still restores within the watchdog interval.
- **The canary FAILS against the production profile**, proving it discriminates.
- Draining is refused when remaining headroom is insufficient.
- Window artifacts carry the canary evidence.
