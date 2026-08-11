# Workspace Session Guidance

## Standing Problem-Solving Doctrine

Treat investigations, experiments, debugging, and other goal-directed work as evidence-driven
problem reduction when that framing applies. Define the goal and acceptance criteria first; represent
alternative hypotheses or remedies as OR branches and jointly required work as AND or ordered
branches. Prefer discriminating, bounded experiments, change one controlled parameter at a time,
record observations separately from inferences, preserve every failed attempt, and verify a mitigation
against the original acceptance criteria before calling the problem solved. Backtrack to remaining
plausible branches after failure. Mark a problem or experiment failure `EXHAUSTED` only when every
known justified branch is terminal and no evidence-supported, affordable variation remains. A model's
diagnosis is a hypothesis to test, never causal proof.

## TensorRT-LLM Defect Campaign — Standing Objective

The goal is to **find TensorRT-LLM defects, diagnose them to root cause, and land complete upstream
PRs**. The AgentBuilder bulk regeneration is the **load generator** that surfaces those defects; it is
not the objective, and its agent output is not the deliverable.

**A crash or wedge under load is a FINDING, not merely an outage.** On one, the first action is to
*capture*, not to mitigate: record the error signature, the journal excerpt around it, the serving
config in force, the concurrency and KV state at the time, and whether the frontend stayed up while
the executor died. Then reproduce if cheap, diagnose to root cause, design the fix with Codex, and
draft the patch.

Do **not** reduce the load target merely to stop a defect from recurring — that hides the very
signal being hunted. Reduce load only to protect the hosts (thermal, driver wedge, repeated
unrecoverable restarts, or a second host endangered), and when you do, record explicitly what
evidence was given up and what target would surface it again. Prefer fixing TRT-LLM over configuring
around it; a config workaround is a stopgap to be noted in the defect record, never the resolution.

Monitor `ALERT`/`INFO` events are **defect telemetry**, not pager duty. Route a crash to "open or
update a defect record," not to "restore green." Repeated identical routine events (backpressure
pauses, absorbed OOMs within a healthy margin) need no action, but a *new* signature or a worsening
trend does — and the action is investigation.

**Fix every surfaced issue immediately, reviewing with Codex.** A defect that has surfaced is worked
now, not queued: diagnose to root cause, **collaborate with Codex on the best fix before writing or
testing it** (see the Codex-design-review rule), implement, have Codex review the implementation,
then deploy and verify. Do not batch surfaced defects into a later "PR day" — the backlog *is* the
regression risk. Only defer when the fix genuinely depends on absent authority, hardware, or an
upstream capability, and say so explicitly with what unblocks it.

**Verify a suspected defect is still live before treating it as one, and check whether our own
patches caused it.** Confirm from logs that the signature still occurs after the most recent
deploy, and distinguish a real crash from an operator/supervisor `kill -9`, a config reload, or a
restart. Attributing our own regression to upstream — or reporting a fixed defect as open — wastes
the campaign's core output.

## Failed-Prompt Diagnostic Interviews

Before challenging or interviewing an LLM about a failed prompt, first consult the applicable
diagnostic-interview catalog if one exists in the repository. For Consullo AgentBuilder prompt
experiments, read
`Consullo/docs/designs/technical-reports/small-model-agent-building/failed-prompt-diagnostic-interview-catalog.md`
before composing the challenge. Select or adapt cataloged techniques, record the technique IDs used,
and preserve any one-off interaction pattern that produced a reusable lesson. Do not rely on
conversation memory alone for this step; re-open the durable catalog after context compaction or in a
fresh session.
