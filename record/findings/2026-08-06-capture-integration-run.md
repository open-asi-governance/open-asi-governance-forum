# Finding handed to Track B — the capture path's first integration run

**From:** Corpus Surface session (Track A), 2026-08-06, at the custodian's request.
**Run against:** `origin/main` @ `4ac673e`, and `origin/session/capture` @ `dfe5d3c`.
**Not fixed here**, because `tools/ingest_capture.py`, `tools/capture_lifecycle.py` and
`tools/capture_ui/` are Track B's. Filed the way Track B handed Track A the rebuild-diff finding.

**Conflict of interest.** The author is a party to the record, wrote the manifest change this run
also exercises, and has already misread this track's work once today — an earlier pass reported two
gates as "not refusing" when the real cause was the author's own test-fixture contamination. Every
claim below is stated with the command that produces it, so it can be checked rather than believed.

**Nothing entered the corpus.** Every response used was fabricated by the author and every run
happened in a throwaway `git archive` extraction. Mock replies must never reach `corpus/`: a
fabricated reply committed as a contribution is **D-10** — a block attributed to a party that did not
write it — which is the most serious attribution defect in this register.

---

## What was run

A full four-party round for `review-round-03`, with fabricated but plausible replies from Grok,
ChatGPT, Gemini and Claude Fable 5, driven through `tools/ingest_capture.py` into artifacts, then
through the whole maintenance path.

```bash
git archive origin/main | tar -x -C "$SCRATCH"      # throwaway; never the working repo
cd "$SCRATCH"
python3 tools/ingest_capture.py b-Grok.json b-ChatGPT.json b-Gemini.json b-Claude-Fable-5.json
python3 tools/rebuild.py
python3 tools/build_manifest.py corpus/raw/
```

Bundles carried: `schema_version`, `bundle_version`, `round`, `identity`, `response_text`,
`response_sha256_at_paste`, `prompt_path`, `prompt_sha256`, `attested_answers_round_question`,
`attested_by`, `captured_utc`.

## What passed

```
review-round-03: COMPLETE
  ChatGPT           accepted
  Claude Fable 5    accepted
  Gemini            accepted
  Grok              accepted
```

- Four artifacts written with correct provenance: `k=1`, `citability: citable_artifact`,
  `distributional_inference: insufficient_k`, `phase: Phase-2 (informed)`, `edit_status: unedited`,
  and `raw.sha256` matching the preserved bytes.
- `tools/validate_provenance.py corpus/` — passes.
- `tools/rebuild.py` — exit 0.
- `tools/build_manifest.py corpus/raw/` — verifies afterwards.

**Cross-track integration is intact, and this is the part neither branch could show alone.**
`capture_response.py` on `main` invokes `build_manifest.py corpus/raw/ --add`, the append-only mode
introduced with D-29 accepts the newly captured file, and the manifest still verifies after the
capture. Track B's capture and Track A's manifest repair compose correctly on the merged state.

## A gate caught a real cross-branch difference

The first attempt on `main` **refused**, correctly:

```
bundle:     f55ceb576ef99635…
repository: 39fced21b0ba07a3…
The prompt changed after the page was built, or the bundle was edited.
Recording a capture against a prompt the party did not receive is D-05 in reverse.
```

The bundles had been built against `session/capture`'s prompt; `main`'s differs. Worth recording as
a *positive* result — the prompt-hash binding survives a real branch divergence, which no unit test
demonstrates.

---

## Defect 1 — `rejected` is unreachable, and a held capture cannot be dispositioned

**Severity: this is what blocks a live round.**

`capture_lifecycle.TRANSITIONS` permits the exits:

```
returned_clean           -> ['accepted', 'rejected']
returned_pending_review  -> ['accepted', 'rejected']
accepted                 -> []
rejected                 -> []
```

**No code path performs either transition from a held state, and `"rejected"` has no caller
anywhere.** Verified three ways on `origin/main`:

1. Every `lifecycle.transition(...)` call site is in `ingest_capture.py` — lines 238, 240 and 279 —
   setting `planned`, `sent_attested`, and `accepted` **only on the clean path**.
2. `grep -rn '"rejected"' tools/ --include=*.py` outside `capture_lifecycle.py` returns nothing but
   a membership test.
3. `tools/build_capture_ui.py` emits no disposition control; its `accept`/`reject` matches are all
   about `navigator.clipboard`.

Re-running ingest on a held capture reports *"already returned_pending_review, awaiting the
custodian's disposition. Nothing to do."* — correct, and there is nothing that does it.

**Consequence.** The gates are sensitive by design, so a real round will produce at least one held
capture. Since a round is "not reportable as complete" while anything awaits disposition, **one held
capture blocks the round permanently.** The design is right — preserve first, disposition mandatory
— and the exit is missing.

**This is D-29's shape.** The capability exists in the state machine and nothing reaches it. Unit
tests cannot find it: `test_capture_lifecycle.py` correctly tests that the transition is
*permitted*, which is a different claim from anything *invoking* it. Only composition finds this
class, which is the argument for the next defect.

**Reproduce:**
```bash
# any bundle whose response is the prompt text, or whose response_sha256_at_paste is wrong
python3 tools/ingest_capture.py held-bundle.json     # -> HELD
python3 tools/ingest_capture.py held-bundle.json     # -> "Nothing to do." forever
```

## Defect 2 — `ingest_capture.py` has no test coverage

`git grep -l ingest_capture -- tools/tests/` returns nothing. It is the **only component that
writes into `corpus/`**, and it composes gates and lifecycle that are themselves well covered — 29
gate cases, 21 lifecycle cases, 21-case Python↔JS parity, 21-case in-page hash parity, all green.
The composition is the untested layer, and defect 1 lives exactly there.

Every result in this document was established by hand, once, by a party with a declared conflict.
That is weaker than a suite the build re-runs.

## Defect 3 — exit status does not separate held from accepted

`accepted` → 0. `held` → **0**. `refused` → 1.

A script cannot distinguish a clean capture from a contaminated one held for review. Anything wiring
ingest into CI and checking the exit code will treat a saturated prompt-echo as success.

## Defect 4 — an unreadable path aborts the batch mid-way, with no status report

**Found by the custodian, at the keyboard, on the first real attempt.** The path was mistyped; the
tool produced a fourteen-line Python traceback.

`ingest_one()` wraps the file read in a `try`, but catches **only** `json.JSONDecodeError`:

```python
try:
    bundle = json.loads(path.read_text(encoding="utf-8"))
except json.JSONDecodeError as error:
    print(f"      REFUSED: not valid JSON: {error}")
```

`FileNotFoundError` propagates, as would `IsADirectoryError`, `PermissionError` and
`UnicodeDecodeError` on a binary file. The traceback appears *after* the `▸ filename` header, so it
reads as though processing had begun.

**The traceback is the cosmetic half. This is the substantive half:**

```python
outcomes = [ingest_one(Path(b).expanduser(), args.dry_run) for b in args.bundles]
```

A list comprehension, evaluated left to right, with **no per-item error containment**. An
unreadable path at position *n* aborts the batch: items after it are never processed, items before
it have **already written**, and the summary block and round-status table — everything after that
line — **never print**.

Demonstrated with a good bundle followed by a bad path:

```
python3 tools/ingest_capture.py good.json /nonexistent.json
  -> traceback, exit 1
  -> record/quarantine/review-round-03/grok-01.md   EXISTS  (side effect committed)
  -> round status printed: 0 lines
```

So a four-party round with a typo in the third path leaves two parties ingested, two not, and the
operator holding a traceback that says nothing about which. Recovering means reading the lifecycle
log by hand.

**Why this one matters beyond its size.** This tool's design is *refuse early, refuse legibly, leave
nothing partial* — `CONTRIBUTING.md` states that refusals happen before anything is written so a
rejected capture never leaves a partial artifact behind. A mistyped path is the **first thing a
custodian will get wrong**, and it produces the one outcome the design promises cannot happen. It is
also the least reassuring possible failure in the only component that writes into `corpus/`.

**Fix:** catch `OSError` and `UnicodeDecodeError` alongside `JSONDecodeError` and return `"refused"`;
and contain per item so one bad path cannot suppress the status report for the rest of the batch.

**This is exactly what a headless run could not find.** Every bundle in the automated run was
constructed programmatically at a path known to exist.

## Defect 5 — the bundle does not record which hash implementation produced its hash

The bundle carries `gates_version: capture-gates-0.1`, and 21 other fields. It does **not** record
which SHA-256 implementation computed `response_sha256_at_paste`.

The page is opened over `file://` and deliberately supports two code paths — `crypto.subtle` where
the browser treats the origin as trustworthy, and a pure-JS fallback where it does not
(`tools/tests/test_page_hash_fallback.py` exists for exactly this). The page displays `HASH_IMPL`
to the operator on screen and then drops it. The artifact cannot say which path ran.

Same species as D-02, where sampling parameters were absent for every entry: the instrument's
configuration is not recorded alongside its output. Minor, and cheap — one field.

*Confirmed working in a real browser, 2026-08-06:* a custodian-driven capture over `file://`
produced `32ed84a7215d1f51…`, byte-identical to `hashlib` over the same text. The implementation is
correct; it is merely unrecorded.

## Defect 6 — the page prints an ingest command that is wrong after the first capture

Section 7 prints, verbatim:

```
Saved. Ingest it with:
python3 tools/ingest_capture.py ~/Downloads/oagf-capture-<round>-<party>.json
```

The filename is derived from round and identity, so **every capture for a given party in a given
round produces the same filename.** Browsers do not overwrite on collision; they suffix. A second
capture lands at `…-grok (1).json` while the printed command still names `…-grok.json`.

**A custodian following the page's own instructions therefore ingests the previous capture.**
Observed live: a 7,154-byte prompt-echo capture was saved as `(1)` while the printed command pointed
at the 55-byte capture from six minutes earlier.

**Fix:** put a short content hash or a UTC stamp in the filename, and print the command with the
actual name the page just used.

## Defect 7 — a different capture for a terminal party is silently discarded

**The most serious defect this run found.** Defect 1 blocks loudly; this one loses material quietly
while reporting success.

`accepted` and `rejected` are terminal. `ingest_one()` checks the lifecycle state *before* it looks
at the response, so any later bundle for that party in that round is dropped:

```
python3 tools/ingest_capture.py second-capture.json
      already accepted; nothing to do. Re-running ingest is a no-op.
  skipped 1        exit 0
```

Verified on `origin/main` with two genuinely different captures for Grok — 55 bytes and 7,154 bytes,
different SHA-256, different text:

- the 7,154-byte response is **not written to the corpus** — correct, the slot is taken;
- it is **not preserved in quarantine either** — `record/quarantine/` still holds only the 55-byte
  first capture;
- **nothing warns that the submitted content differed from the accepted content**;
- the message asserts *"Re-running ingest is a no-op"*, **which is false** — this was not a re-run,
  it was different material;
- exit status 0.

**This contradicts the principle the lifecycle was built on.** Track B's own design states *preserve
first, validate second*, and that *response bytes are immutable under every disposition*. Here the
bytes were never preserved at all. A capture the custodian believes is recorded does not exist
anywhere.

**Compounded with Defect 6, it is worse than either alone**, and the compound is what happened live:
the page tells the custodian to ingest path *X*; the browser has silently written the new capture to
*X (1)*; the custodian ingests *X*; the tool reports "nothing to do"; and the custodian has every
reason to believe the second capture is filed. **Every signal available to the operator says it
worked.**

**Fix:** compare the incoming `response_sha256_at_paste` against the accepted capture's hash before
declaring a no-op. Identical content is genuinely a re-run and may be skipped. **Differing content
must be preserved and refused with a distinct message** — the party's slot is taken, and the bytes
must not vanish.

## Note, not a defect — an acceptance criterion has drifted from the implementation

T-13 still reads *"Pasting the prompt back is refused, with the reason named."* Implemented behaviour
is **held**, with the reason named and nothing entering the corpus. The intent is met and arguably
better met, since the bytes are preserved rather than discarded. The criterion's wording was not
updated when the detector was deliberately demoted from a gate to a diagnostic.

---

## Smallest change that unblocks a live round

0a. **Never silently drop a differing capture** (Defect 7). Compare hashes before declaring a
   no-op; preserve and refuse loudly when content differs. **Do this first** — it is the only defect
   here that loses material while reporting success.
0b. **Contain per-item errors in `ingest_capture.py`** (Defect 4). Smallest of the four and the one
   a custodian hits first.
1. **A disposition command.** `accept` / `reject` against a round and identity, with a **mandatory
   reason** recorded to the lifecycle log. Without it defect 1 stops the first real round.
2. **A test over `ingest_capture.py`** covering the five outcomes observed here: accepted,
   held-on-saturation, held-on-hash-mismatch, refused-on-empty, refused-on-prompt-mismatch. Small,
   because the gates beneath it are already tested — this is composition only.
3. **Distinct exit codes** for accepted / held / refused.

Items 1 and 3 are prerequisites for T-14. Item 2 is what makes this document unnecessary next time.

## Addendum — the page itself, driven headless

Added after the first version, which recorded the page as untested. `tools/capture_ui/index.html`
as built on `main` was loaded in Node under a DOM shim, its own `download()` called, and the bundle
it emitted fed **unmodified** into `ingest_capture.py`.

**Page -> bundle -> ingest -> corpus is intact.** 22 fields emitted, every entry in ingest's
`REQUIRED` tuple present, and the page's own output ACCEPTED without editing. This is the seam
nothing had exercised.

Also confirmed:

- **No free-text identity input.** Identities resolve from `window.OAGF_ROUNDS` through
  `r.parties.find(p => p.identity === state.party)` — selection, not typing, so D-09 identity
  merging cannot recur through the capture path.
- **Self-contained.** Two inline script blocks, zero `src=` attributes; `check_self_contained()`
  refuses to emit a page that would make a request.
- Page JavaScript syntax-checks clean.

**The advisory/authoritative split behaves as designed.** Pasting the prompt back as the response,
through the page:

```
G1-non-empty                          pass
G2a-not-byte-identical-to-prompt      FAIL
G2b-not-normalised-equal-to-prompt    FAIL
G2c-prompt-saturation                 FAIL  saturation 1.000 against threshold 0.6
G3-not-duplicate-of-same-party        pass
G5-truncation-hint                    pass
```

The page **still emits a bundle** — correct, the preview is advisory — and ingest then **held** it:
`Grok returned_pending_review, awaiting disposition`. Preview warns, ingest decides, nothing enters
the corpus.

That held capture then demonstrates **Defect 1** live: it cannot be cleared, and the round can never
report complete.

## Cosmetic — `build_capture_ui.py` reports characters as bytes

`print(f"... ({len(page):,} bytes)")` counts characters; the file is 58,533 bytes against 58,285
reported, because of UTF-8 multi-byte content. The `unchanged` determination is correct.
**Track A has the identical bug** in `build_viewer.py`, `build_local_rounds.py` and
`build_session_log.py`, and will fix its own.

## What this run did not test

- **The page in a real browser.** Everything above ran under a DOM shim. Untested in a real engine:
  `crypto.subtle` versus the pure-JS `sha256Fallback` (the reason `test_page_hash_fallback.py`
  exists), `navigator.clipboard` behaviour, the actual file download, and whether the round picker
  and party list render at all. **A shim proves the logic composes; it does not prove the page
  works.**
- Any real party. Every response was fabricated.
- **Fixture contamination bit this author three times**, each time by re-running against state left
  by a previous run and briefly misreading the result as a gate outcome. Three occurrences in one
  session is no longer an anecdote; it is the strongest argument here for making `--dry-run`
  genuinely side-effect free.
- `--dry-run`, beyond confirming previously that it is **not side-effect free**: it writes quarantine
  files and advances lifecycle state, which contaminated this author's first test sequence and made
  two later cases silently unreachable. There is currently no safe rehearsal against a real round.
