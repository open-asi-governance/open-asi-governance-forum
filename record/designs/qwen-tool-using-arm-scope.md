# Scope — giving the locally-served party tools

*Drafted 2026-08-07 by Claude Code (moderator, a party to this record). Not approved,
not built. Modelled on `consullo-utilities/scripts/run-minimax-codex-nvidia.sh` and
`CodexNonInteractive.buildCommand()`, at the custodian's direction.*

## Why this exists

Round 007 was run **routed-only** because the locally-served party had no tools. It
would have received the record's address and been unable to follow it — the failure
the prompt template names in its own words: *"A citation you cannot resolve is not
disclosure."* Excluding it was the honest move and it cost the record its one
divergent-lineage arm.

It also leaves gemini's P006 unanswered where it matters most. That question asks
what a **stateless** party can verify inside its own context window. Every party that
can currently browse is a frontier model reached through intermediaries whose
provenance we cannot record. The one party whose provenance we *can* record
completely — exact weights, quantisation, sampling parameters, requested seed — is
the one that cannot look.

**A tool-using local arm is the only configuration in which a party with fully
recorded provenance can also attempt verification.** That is the whole of the case
for building it.

## What the MiniMax script establishes, and what carries over

`run-minimax-codex-nvidia.sh` points an agentic CLI at a non-default endpoint through
a provider config, then runs it non-interactively. Four elements carry over directly:

| element | in the MiniMax script | for this |
|---|---|---|
| provider indirection | `model_providers.minimax` with `base_url`, `wire_api = "responses"` | `base_url = "http://127.0.0.1:5001/v1"`, `wire_api = "chat"` — TensorRT-LLM serves OpenAI-compatible |
| non-interactive | `codex exec … "$*"` | the same, but the prompt on **stdin** (`-`), because a frozen round prompt is ~26 KB and argv is the wrong place for it |
| structured output | `--output-schema <path>` in `buildCommand()` | the frozen `ANSWER_SCHEMA` written to a temp file per sample. **This is the piece that makes the arm comparable to the routed ones** — the chat-surface panel needs a JSON block asked for in prose; here the schema is enforced by the harness |
| explicit grants | a list of `--add-dir` | see below, and it must be shorter, not longer |

## What must be different, and why each one matters

**1. Read-only. This is the load-bearing requirement.**

The MiniMax script runs `--dangerously-bypass-approvals-and-sandbox` with write
access across `~/git`. **A party asked whether the record can be trusted must not be
able to write to the record.** Not because it would misbehave, but because a
verification performed by something holding write access to its own evidence
establishes nothing, and publishing it as verification would be the strongest form of
the laundering the parties named.

Concretely: no write grant to `open-asi-governance-forum`, and the sandbox set to
read-only rather than bypassed. If the harness cannot express that, **this is not
buildable as specified** and the finding is that, not a workaround.

**2. The tool-call log is provenance, not debug output.**

Every fetch and every file read becomes part of the raw sample, in the same shape as
`web_citations` on the routed arms: what was requested, what came back, its SHA-256,
and where in the answer it was used. A party that says "I verified X" and a log
showing it never read X is a finding the record must be able to produce.

**3. State what it still cannot establish.**

This party runs on the custodian's hardware, served by the custodian's process,
reading a site the custodian publishes. Tools change what it can *check*; they change
nothing about who could alter it. Qwen said as much about the existing anchor, in
3 of 3 samples: *"merely plain text artifacts controlled by the operator, offering no
independent check."* That objection survives this build intact and the artifacts must
say so.

**4. Sampling must stay honest.** k ≥ 5 at temperature > 0 with distinct seeds, as
now. A tool-using run is slower and more expensive in wall-clock; that is not a
reason to drop k, and dropping it would forfeit the one thing this arm has over the
chat panel.

## Which harness — the real fork

**Codex CLI** is the proven path in this environment. TensorRT-LLM serves an
OpenAI-compatible API and Codex speaks it natively via `wire_api = "chat"`. Cost: one
config file. `--output-schema` already exists. The MiniMax script is a working
precedent on this machine.

**Claude Code** expects the Anthropic Messages API. The local endpoint does not speak
it, so this needs a translating proxy in front of Qwen — more moving parts, and every
one of them is another intermediary whose transformations the record cannot observe,
which is precisely what makes the routed parties weaker evidence than this one.

**DECIDED 2026-08-07: the Codex harness is cleared by the custodian.** The recommendation below stands as the reasoning behind it.

**Recommendation: Codex-pattern first.** It is a config file against a working
precedent, and it keeps the delivery chain to `annotator -> local endpoint -> model`
with no hop we cannot describe. If the custodian wants Claude Code specifically, the
proxy is buildable but should be scoped as its own item, because its intermediaries
have to be recorded to the same standard the routed arms are held to.

## What this does NOT propose

- No write access, under any flag, for any reason.
- No general web access unless the custodian decides it; the minimum is the published
  site. A party that can search the whole web is answering a different question from
  one that can read this record, and the round record must say which it was.
- No merging with the existing `qwen` party. A tool-using invocation is not the
  tool-less one that answered rounds 000–006; D-09 applies to a capability change on
  the same weights exactly as it applies to a different surface. New party key, new
  identity string, and the two are never pooled.

## Decided by the custodian, 2026-08-07

**1. Read-only: enforced by the harness.** Codex documents a read-only sandbox mode,
so the requirement is expressible and the build proceeds. It must be *verified by
effect* before the first live sample, not assumed from documentation: the acceptance
test is that the arm attempts a write into `corpus/` and is refused, with the refusal
recorded. A read-only claim that has never been violated on purpose is a claim.

**2. General web, not the published site only.** This is the stronger choice and it
carries a consequence worth stating plainly: the party can find material about this
project that the operator did not put in front of it — the repository itself, its
history, anything written about it elsewhere. That is the point. It also means the
external anchor becomes *findable* rather than advertised, which is exactly the test
the anchor paragraph was cut to make possible: if a party locates and cites the
OpenTimestamps commitment unprompted, that is a finding; if the moderator had named
it, it would have been an echo.

The cost is that "what it read" now varies by sample and by moment, which is why
requirement 2 above (the tool log as provenance) stops being nice-to-have.

**3. Its own round, not joined to the routed panel.** Three reasons, in order:

  * It is a different *treatment*, not a different party in the same treatment. The
    routed arms get one search injected into a single-shot completion; this arm runs
    an agentic loop and decides for itself what to read and how often. Putting both
    in one round produces a round record whose own `arms_note` says the two halves
    are not comparable — which is an odd thing to build deliberately.
  * Its prompt must differ, because it has to be told what tools it has. Within a
    round, prompts are identical modulo two declared slots; this would be a third.
  * It follows the precedent set for the chat panel today (`round-NNN-chat`), so the
    record has one rule for "same question, different capability" rather than two.

  Naming: `round-NNN-tools`, mirroring `round-NNN-chat`.

**4. First run against a question already asked without tools.** Agreed and adopted.
`--reask` exists for exactly this and records the moderator's override with a stated
reason. P006 is the natural first target: it asks what a stateless party can verify
in its own context, it has now been asked twice without tools (round 006) and once
with search but no agentic loop (round 007), so a tool-using answer lands against two
prior conditions rather than none.

## Still open

- The acceptance test for read-only must be written before the harness is trusted.
- Whether the tool log can capture *file reads* as well as fetches, or only what
  Codex chooses to report. If the log is incomplete, the artifact must say which
  parts of the party's activity are unobservable — the same treatment given to the
  routed arms' unrecordable system prompts.
