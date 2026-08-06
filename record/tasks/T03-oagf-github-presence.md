# T-03 · Build out the OAGF GitHub presence

**Track A — Corpus Surface** · branch `session/site` · no GPU · status: open

Take the repository from a bare bootstrap to a credible public presence, without letting
presentation outrun what the record actually supports.

## Site (`docs/`, GitHub Pages)
- Landing page distinct from the raw thread viewer: what OAGF is, what it explicitly is not, the
  deficiency posture stated up front, and a path into the corpus for three audiences (alignment
  researchers, governance/policy readers, implementers).
- Navigation across the artifact families: corpus, FDR series, prediction registry, ASP spec,
  deficiency register, review rounds.
- **Prediction registry view**: open predictions with resolution dates, scored predictions with
  outcomes and evidence, calibration visible over time. This is the artifact that gets more
  valuable with age.
- **Deficiency register view**: entries with status, which were reviewer-found vs annotator-found,
  which are permanent vs remediable.
- Every page **self-contained with no external requests** — Gemini's round-01 environment could
  reach neither the raw CDN nor the blob UI. Deterministic generation, extending
  `tools/build_viewer.py` into a small site generator driven by `tools/rebuild.py`.
- **Tasteful means restrained**: no logos of AI companies, nothing implying endorsement, no
  institutional styling that overclaims standing. The credibility comes from the self-audit, not
  the design.

## Issue forums
- Templates: attribution correction (highest priority per CONTRIBUTING), deficiency report,
  prediction proposal, prediction resolution challenge, ASP spec comment, general contribution.
- Each template collects the provenance fields CONTRIBUTING requires, so an issue-originated
  contribution can be captured with `tools/capture_response.py` without a follow-up round trip.
- Labels in the record's own vocabulary: `attribution`, `deficiency`, `prediction`, `asp-spec`,
  `review-round`, `correction`, `superseded`, `invocation-integrity-disputed`.
- Enable Discussions for Q-01 and Q-02, seeded with both plus P-CHATGPT-0001 (the Q-02
  operationalisation).
- `CODEOWNERS` naming Stephen Reed, consistent with GOVERNANCE.md §2's human write gate.
- `SECURITY.md` scoping hazardous content **out** rather than claiming governance over it.

## Monitoring
- Attribution-correction issues answered fastest; prediction resolution dates tracked so a due
  prediction is scored on time whether or not the result flatters the project — **P-0003 predicts
  exactly this discipline eroding**; review rounds on a stated cadence.
- Consider a scheduled check flagging predictions whose resolution date has passed and remain
  unscored. A registry that quietly misses its own resolution dates is worse than no registry.

## Constraint
Nothing added here may imply standing, membership, authority or endorsement the project does not
have. Every prior naming decision in this record was made to avoid exactly that, and **a polished
site is the easiest place to lose it.**

## Pages — UNBLOCKED 2026-08-06
The custodian added the `pages=write` scope and enabled Pages via the API:
`gh api -X POST repos/.../pages -f 'source[branch]=main' -f 'source[path]=/docs'`.
The site serves from `main:/docs` at
<https://open-asi-governance.github.io/open-asi-governance-forum/>, HTTPS enforced.

**Consequence for this track:** every `tools/rebuild.py` run now changes what the public sees the
moment the branch is merged. Check the generated page before pushing, and treat a broken build as a
public defect rather than a local one.


---

## Amendment 2026-08-06 — agent-readability, and a link back that works

Added after the site went live. Three findings from auditing the deployed page, each with the
evidence in this corpus rather than borrowed from general advice.

### The immediate defect

The only links back to GitHub sit in the footer of a 435 KB page, after all 44 contributions. Worse,
one of them points at `github.com/.../blob/main/corpus/deficiencies.md` — **the exact URL form this
corpus documents as unreadable to agents.** Gemini, review round 02: *"The GitHub web UI
(/blob/main/...) renders content dynamically via JavaScript, returning only the HTML navigation
shell to automated web readers, while direct raw file endpoints are unreachable due to environment
network restrictions."*

We send agents to the one form our own record says fails for them. Fix the position **and** the
target.

### The finding that makes this urgent

The page is **435,339 bytes ≈ 109,000 tokens**. Qwen3.6's budget is **24,576**. The page is **4.4×
too large for the corpus's own contributing party to read.** Agent-readability here is not a
courtesy to hypothetical crawlers — the project's own participant is excluded from its own website.

### Principles, each grounded in evidence already in this record

1. **Serve the corpus as raw text at stable URLs on Pages itself.** Gemini could reach neither
   `raw.githubusercontent.com` (blocked) nor the blob UI (JS shell). GitHub Pages serves any file at
   a predictable path, from the same origin as the page. Mirror the corpus markdown into `docs/` and
   link *those*, never blob URLs. This single change would have made round-02's supplied-context
   bundle unnecessary.
2. **Size every page for the smallest party that must read it.** Chunked, addressable,
   single-purpose pages — one per deficiency register, per FDR entry, per review round, per spec —
   rather than one page carrying everything. The 24,576-token budget is the design constraint, not
   an edge case.
3. **No substantive content behind interaction.** Node bodies are `display:none` until clicked. They
   are in the DOM, so a parser sees them, but a rendering-based reader sees nothing. Ship a
   `?expanded=1` or a `/plain/` variant where everything is visible without scripting.
4. **Publish `/llms.txt`** — a machine-readable index of what the site holds and where, per the
   emerging convention. This corpus is unusually well suited to it: the artifact families are
   already enumerated and stable.
5. **State ingestion permission explicitly.** The corpus is CC BY 4.0 and the code Apache-2.0. A
   cautious agent facing an ambiguous `robots.txt` skips. Say plainly that reading, quoting and
   ingestion are permitted, with the attribution terms named.
6. **Expose the hashes beside the content.** This is the distinctive one. Most agent-readability
   advice concerns *parseability*; this project can offer *verifiability*. Every raw artifact is
   hash-anchored in `corpus/MANIFEST.sha256`. If a page serves an artifact, it should serve that
   artifact's SHA-256 next to it, so an agent can confirm it read the canonical text rather than a
   rendering of it. An agent that can verify what it read is a strictly better reviewer, and this
   corpus's entire premise is that claims should be checkable without trusting the publisher.
7. **`<link rel="alternate" type="text/markdown">`** on each HTML page pointing at its plain source,
   plus a sitemap. Cheap, standard, and makes the plain variant discoverable rather than guessable.

### Acceptance for this amendment
- A link back to the repository is visible **without scrolling**, and no link intended for machine
  readers points at a `/blob/` URL.
- Every corpus document is reachable as plain text from the Pages origin.
- No single page exceeds ~20,000 tokens.
- `/llms.txt` exists and is accurate.
- Any page serving a hash-anchored artifact shows its SHA-256.

---

## Session state — Corpus Surface, 2026-08-06. **T-03 is PARTIALLY DONE.**

Two live defects in Track A's own territory were fixed before T-03's content work, deliberately.
Both were public and one broke the commit gate every track relies on. Recorded here so the ordering
is not read as drift.

### Done, with hashes

| | |
|---|---|
| **4cf5efa** | Six issue forms + `config.yml`, each field mapping onto `capture_response.py`'s flags |
| **9ccdc31** | **D-29 + D-30** filed; manifest verification repaired; `tools/check_register.py`; register count corrected (said 24, held 28); remediability table extended past D-22 |
| **6feb2e3** | Page provenance is a digest of its inputs, not a git commit hash |
| **7786f1c** | T-08 (see that brief) |
| **7470f9b** | Codex's review of the D-29 repair applied — 4 further defects, incl. one I introduced; 23 regression cases; CI publication gate; README counts corrected |
| **d64e0e0**, **f58cb2a** | `CODEOWNERS`, `.github/SECURITY.md`, `.github/labels.yml` |

### NOT done — the bulk of T-03's content work

**The site itself is untouched.** `docs/index.html` is still the single threaded viewer.

1. **Landing page** distinct from the viewer — not started.
2. **Navigation** across artifact families — not started.
3. **Prediction registry view** — not started. The data is good and unflattering, which is the point:
   8 open, 13 scored (**4 correct, 5 incorrect, 3 unresolvable, 1 satisfied early**). Read it from
   `predictions/predictions.json`; note scored entries live under a separate `scored` key, and
   `P-0008`'s evidence is void per D-28.
4. **DONE — d9ba035.** `corpus/artifacts/deficiency-register.json` classifies all 30 entries into
   **62 affected-object rows**; generated to `corpus/deficiency-register.md` and
   `docs/deficiencies.html`, with `docs/deficiencies.md` as a plain-text mirror on the Pages origin.
   `check_register.py` **R8** fails the build if an entry's prose changes since it was classified,
   and `--restamp` resets `human_review` to `not_reviewed` rather than asserting approval.
   **The open item is that 0 of 30 classifications have been read by a human against the prose.**
   Two numbers the census surfaced that no prose summary did: only **7 of 30** entries have an
   origin supported by a preserved artifact (23 are asserted in the register only), and exactly
   **1** forward control is validated rather than merely written down.

   *Superseded description:* **Deficiency register view** — not started, and **blocked on a design
   decision that was made but not built**: front-matter per entry was rejected by Codex (adjacency does not validate semantics;
   it would add a fourth independently-authored summary to a document that already had three
   disagreeing counts). The adopted approach is a **strict JSON artifact**,
   `corpus/artifacts/deficiency-register.json`, plus a *generated* human-readable register.
   - `remediable` **must not** be a single value. D-09 alone needs two rows: raw transcript **not**
     repairable, `segments.json` annotation **corrected**. Codex's proposed vocabulary is in the
     review; the axes are finding-state, per-affected-object repairability, remediation state,
     prospective control, and cost.
   - Attribution uses **first preserved substantive articulation**, adopted by the custodian. A
     question that prompted an investigation is a *trigger*, not a finding. The publishable headline
     is "six entries — D-16 through D-21 — were first substantively articulated in preserved
     review-round submissions," and README has been corrected to match.
   - The initial audit must be a **full 28-entry census**, not a subset; the statistic is load-bearing.
   - **No deterministic check can validate that the metadata agrees with the prose.** That is human
     review and must be labelled as such. `tools/check_register.py` is deliberately named and scoped
     structurally for this reason.
5. **DONE — 587fe16, dc099b1.** All eight local rounds publish as **25 per-solicitation pages**
   under `docs/local/`, each carrying every sample collected, the prompt verbatim, and **D-28
   applied per field** so a reader sees "noise-dominated" beside a number rather than having to go
   and look it up. Phase-1 arms additionally carry D-23. The blanket k=1 footer claim is gone and
   regression-tested against reappearing.

   *Superseded description:* **PARTLY DONE — 587fe16.** `review-round-02` and `review-round-02-prompt-critique` now render;
   rounds are declared as data so adding one is an entry, not a function. Gemini's round-02
   verification note is attached beside the response it concerns. 51 contributions, up from 44.
   **Still absent: `local-round-01` … `08`** — the entire local measurement programme, and the
   source of D-23…D-28.
   Custodian decision on record: **publish them, with D-28's noise-floor finding attached per round**,
   void rounds at equal prominence. Withholding the failed rounds is the curated-log antipattern.
   - The contribution-round generalisation is done. `local-round-*` is a **different** shape
     (`solicitation_summary`, aggregate + variance table, k=20/100) and needs its own renderer.
   - **The footer line "Every contribution here is a single sample (k=1)" becomes FALSE the moment
     local rounds are rendered.** It is true today only because they are excluded.
6. **The agent-readability amendment** is PARTLY DONE. Delivered: a plain-text mirror on the Pages
   origin, `rel="alternate"` where a plain variant exists, the per-page token budget met everywhere
   **except `docs/index.html`**, artifact hashes shown beside the content they anchor on the
   local-round pages, and ingestion permission stated in page footers.
   **`docs/index.html` at ~92,000 tokens is now the single item blocking this amendment's
   acceptance criteria.** Still open: `/llms.txt`, plain-text
   mirrors on the Pages origin, ~20k-token page budget, link-back without scrolling, no substantive
   content behind `display:none`, `rel="alternate"`, sitemap, hashes shown beside served artifacts.
   My own measurement agrees with the amendment's, and the page has since grown to **606,812 bytes**
   (from 435,339) by publishing the two hidden rounds — further from the ~20k-token target, which is
   the right trade but raises the priority of chunking. The page still duplicates every
   contribution's text — once in the HTML body and again in the inlined `DATA` JSON.
   **Dropping that duplication roughly halves the page** and is the cheapest single win; search can
   read `.node pre` from the DOM instead of a parallel copy.

### Custodian actions this session could not perform
- **Create the labels.** `.github/labels.yml` is declarative; the API command is in the file.
- **Enable Discussions**, seeded with Q-01, Q-02 and P-CHATGPT-0001.
- **Merge `session/site`.** Nothing here is published until you do.

### Tried and abandoned
- **`git log -1 -- corpus/ record/ spec/` as the page's provenance stamp.** Broken for the mandated
  `rebuild && commit` workflow: at generation time the corpus change is still uncommitted, so the
  page names a stale record commit and the next rebuild diffs again. **Track B independently
  proposed the same fix** (their finding in `T13`); it is rejected for the same reason. Replaced by
  a content digest over the generator's actual inputs.
- **Front-matter in `deficiencies.md`** — see 4 above.
- **Deterministic sanitisation for T-08** — see that brief.
- **Running `tools/rebuild.py` in the shared checkout.** It rewrote `docs/index.html` underneath
  Track B, live in that tree. Nothing was lost. **HANDOFF §3's "shared, but by branch" is not
  achievable with one worktree** — branch checkout is global state. Use `git worktree add`.

### Known collision for the custodian at merge time
`tools/validate_provenance.py` — **Track B fixed the same `jsonschema` fail-open** on
`session/capture` (**8cbe398**) that I fixed here (**9ccdc31**). Same defect, same direction, both
correct, textual conflict only. Either version is fine; theirs cites the T-13 review, mine cites D-29.

### Unresolved predictions
None filed this session. **P-0003** — that resolution discipline in the registry erodes — is
directly relevant to item 3 and to the monitoring section, and remains open and unscored.

### Outstanding acceptance criterion, now satisfiable
The brief recorded "Pages enabled" as outstanding. Pages **is** live, and `.github/workflows/pages.yml`
now gates deployment on a clean-checkout rebuild matching the committed page byte for byte, plus the
23-case integrity suite. **This has never actually run** — it will fire on the first merge to `main`,
and that first run is the thing to watch.
