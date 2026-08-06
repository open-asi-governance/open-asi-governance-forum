# T-13 · Local capture UI for prompts and responses

**Track B — Capture Path** · branch `session/capture` · no GPU · status: open · **blocks T-14**

Every capture-integrity failure this project has had came from the manual copy-paste path, not from
the reasoning. Removing the hand-typed steps is the highest-leverage reliability work available.

## Failures it must prevent — all observed, none hypothetical
- The outbound **prompt was pasted in place of a model's reply** and nearly captured as one. A live
  recurrence of D-10, the founding record's misattributed segment.
- Two reply files came back **0 bytes**, caught only because sizes were checked by eye.
- An artifact that **critiqued the prompt** was nearly captured as a review, because the delivery
  framing lived in chat rather than attached to the prompt.
- Gemini received a bundle omitting files the prompt told it to check — flagged, then reproduced a
  round later.
- Capture metadata retyped into a long shell command every time, which is where a wrong timestamp
  or a missed `prior_context` enters.

## What it does
- Presents the exact **committed** prompt text for a round, one party at a time, with a copy
  control. Read from `record/solicitations/` or `record/*-prompt.md` — **never composed in the
  UI**, so what is sent is always what is committed.
- Tracks per round: sent, returned, outstanding. Round completeness becomes visible instead of
  remembered.
- Shows the supplied-context bundle path and SHA-256 where a party cannot fetch, and records that
  it was supplied.
- Collects capture metadata as form fields with committed defaults pre-filled, and **stamps
  `captured_utc` at paste time** rather than accepting a typed value.
- On paste, **refuses**: empty content; content whose similarity to the outbound prompt exceeds a
  threshold (the D-10 guard); content already captured for that party and round.
- Writes through `tools/capture_response.py` so there is exactly one capture path and its refusals
  still apply.

## Non-negotiable constraints
- **Self-contained and local.** No external requests, same as the viewer.
- **It proposes, the custodian commits.** GOVERNANCE.md §2. The UI must not push.
- A paste box is a place where a response could be edited. **Hash the pasted content at paste
  time, record `edit_status` honestly, and never offer a "clean up" or "reformat" action.**
- Any per-party deviation from the common prompt — a preamble, a bundle, a different delivery — is
  recorded in `prior_context` automatically. That asymmetry has twice gone unrecorded until after
  the fact.

## Overlap
May need to change `tools/capture_response.py`. Track C reads it. Coordinate.

## Acceptance
- A full four-party round runs without typing a shell command or a timestamp.
- Pasting the prompt back is refused, with the reason named.
- Empty paste is refused.
- The round view shows outstanding parties at a glance.
- Every artifact validates under `tools/validate_provenance.py` unchanged.
