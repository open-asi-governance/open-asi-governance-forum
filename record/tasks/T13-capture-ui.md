# T-13 · Local capture UI for prompts and responses

**Track B — Capture Path** · branch `session/capture` · no GPU · **blocks T-14**

**Status: claimed 2026-08-06** by session *Capture Path* (Claude Code, Anthropic), working on
`session/capture`. Resource claims: none. The custodian merges; this session does not push to `main`.

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

## Amendment, 2026-08-06 — delivery is a static page on GitHub Pages

**Custodian direction:** the UI is **static HTML plus JavaScript served by GitHub Pages**, not a
local server process. Recorded as an amendment rather than by rewriting the brief above, so the
original framing and what changed are both legible.

Consequences, each of which the design must answer rather than absorb silently:

- **"Self-contained and local" is re-read as "self-contained and backendless."** The page makes no
  external requests and has no server; it is served over HTTPS instead of loaded from disk. It also
  works from `file://` and from a local clone, so it is not hostage to Pages being enabled.
- **A static page cannot write to the repository.** Every write path must still terminate in
  `tools/capture_response.py`, per the single-capture-path constraint above.
- **Pages is not enabled yet** (custodian action, blocks Track A). The hosted form is therefore
  unreachable until it is; the `file://` form is not, so T-14 is not blocked by this.
- **`docs/` is Track A's territory.** This adds `docs/capture/`. Overlap recorded below.

### The conflict this creates, for the custodian to resolve

Two requirements in this brief cannot both hold once the UI is backendless:

| | |
|---|---|
| *Acceptance:* "a full four-party round runs **without typing a shell command**" | needs the browser to write into the working tree |
| *What it does:* "writes through `tools/capture_response.py` so there is **exactly one capture path**" | needs the writer to stay in Python |

Resolutions considered, with the trade named:

1. **Prepare-and-ingest (default).** The page runs the gates as an advisory preview and emits a
   capture bundle; `tools/ingest_capture.py` validates it authoritatively and writes through
   `capture_response.py`. Keeps one writer and one *authoritative* gate implementation. Costs **one
   shell command per round**, which fails the acceptance criterion as literally written.
2. **Direct write via the File System Access API.** Zero shell commands, satisfying the criterion
   exactly. Chromium-only, requires a secure context (so not `file://`), and puts a **second writer
   in JavaScript**, duplicating the D-25-validated similarity rule in a second language where it can
   drift from the validated one.

Proceeding on (1), because a duplicated coding rule is the D-25 failure mode and the criterion it
fails costs one command. (2) is buildable later as a Chromium-only accelerator that writes to an
inbox directory rather than to `corpus/`, which keeps it a drop-off rather than a capture path.

Where gates run in **both** languages for fast feedback, the JavaScript implementation is advisory
only, and agreement between the two on every validation case is an acceptance criterion.

## Overlap
- May need to change `tools/capture_response.py`. **Track C** reads it. Coordinate.
- Adds `docs/capture/` and a builder under `tools/`. **Track A** owns `docs/` and the Pages
  deployment. Coordinate before either track edits the other's page.
- Adds fields to `tools/schemas/contribution.schema.json`. **Track D** owns `tools/schemas/`.
  Custodian authorised proceeding 2026-08-06; the change is additive and is flagged here so Track D
  inherits it rather than discovering it.

### Finding handed to Track A, 2026-08-06 — the rebuild-produces-no-diff signal does not hold

Found by this session while following the standing `rebuild && commit` rule, and **not fixed here,
because `tools/build_viewer.py` is Track A's.**

`build_viewer.py::head_commit()` stamps `git log -1 --format=%H` — HEAD **at build time**, which is
always the commit *before* the one the regenerated file will ship in. Three consequences:

1. `docs/index.html` asserts *"generated from commit X"* where X is **never** the commit that
   contains it. The page is structurally incapable of stating its own provenance correctly, in a
   repository whose subject is provenance accuracy.
2. README's claim — *"On an unchanged repository it produces no diff, so `git status` after a
   rebuild is a real signal"* — is false. After **every** commit the next rebuild dirties the
   viewer, so the signal every track is told to rely on is permanently noisy by construction.
3. The standing `rebuild.py && git commit` chain guarantees the stale stamp, because rebuild
   necessarily runs before the commit it should name exists.

Suggested fix, Track A's call: stamp the last commit that touched the **corpus**
(`git log -1 --format=%H -- corpus/`) rather than HEAD. That is stable across documentation-only
commits and is the claim the line is actually trying to make. Alternatively drop the stamp and let
`MANIFEST.sha256` carry the anchor, which it already does.

Until it is fixed, this session reverts the regenerated `docs/index.html` rather than committing
Track A's file, and **no session should read a clean `git status` after rebuild as evidence of
anything.**

## Acceptance
- A full four-party round runs without typing a shell command or a timestamp.
  **Amended 2026-08-06:** without typing a timestamp, and with **one** ingest command per round.
  The departure is recorded rather than quietly redefined — see the conflict above.
- Pasting the prompt back is refused, with the reason named.
- Empty paste is refused.
- The round view shows outstanding parties at a glance.
- Every artifact validates under `tools/validate_provenance.py` unchanged.

Added with the amendment:
- The similarity rule is **validated against a hand-checked subset and the validation committed**,
  per D-25. Rejected rules are published alongside the adopted one.
- The JavaScript preview gates and the Python authoritative gates **agree on every validation
  case**. Disagreement is a build failure, not a warning.
- Party identities are **selected from the round manifest, never typed**, so D-09 identity merging
  cannot recur through the capture path.
- Per-party delivery differences (bundle, preamble, direct fetch) are written to `prior_context`
  automatically and shown as a divergence table **before** the round is sent, not discovered after.
- `tools/rebuild.py` regenerates the page and produces no diff on an unchanged repository.
