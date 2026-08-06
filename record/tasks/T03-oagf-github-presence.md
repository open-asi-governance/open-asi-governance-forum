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
