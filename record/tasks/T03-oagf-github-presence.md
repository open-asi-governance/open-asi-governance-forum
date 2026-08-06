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
