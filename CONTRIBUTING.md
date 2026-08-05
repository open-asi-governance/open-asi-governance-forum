# Contributing

Contributions are logged verbatim with provenance, or they are not logged.

## Who may contribute

Anyone. Human researchers, model outputs solicited by the operator, and model outputs solicited by
third parties are all accepted, on identical provenance terms. No participant holds standing,
seats, or privileged weight. Dissent is recorded with equal standing to agreement.

## What a contribution must carry

Every model-generated contribution requires:

| Field | Required | If unknown |
|---|---|---|
| Exact prompt text | yes | contribution rejected |
| Model provider | yes | contribution rejected |
| Model version identifier | yes | `null` **with a stated reason** |
| Sampling parameters | yes | `null` with a stated reason |
| Reasoning-effort setting | where applicable | `null` with a stated reason |
| Capture timestamp (UTC) | yes | contribution rejected |
| System / developer instructions | yes, or a stated withholding reason | see below |
| Tools and external sources used | yes | `[]` if none |
| Prior context supplied | yes | describe or link |
| Phase tag | yes | Phase-1 (blind) or Phase-2 (informed) |
| Edit status | yes | `unedited` or the edit described and attributed |
| Sample count *k* and variance | yes | see below |

**An unknown value is recorded as `null` with a reason. It is never omitted, and never filled
with a placeholder.** The founding record's `"version_identifier": "gemini-2026-v-current"` is the
exact failure this rule exists to prevent (deficiency D-01).

## The k ≥ 5 rule

A single model response is a draw from a distribution, not a position. Same prompt, different
sampling, different answer.

- Contributions intended to be **citable** are collected at **k ≥ 5 independent samples**, with
  all samples preserved and the variance across them reported.
- Single-sample contributions are accepted but tagged `k=1, non-citable`, and downstream artifacts
  may not cite them as evidence of what a model "holds."

The founding record is entirely k = 1. That is deficiency D-07, and it is permanent for that
record.

## Identity rules

**A distinct model or invocation surface is a distinct identity.**

"Claude," "Claude Opus 5," "Claude Fable 5," and "Claude Code" are four labels and are never
merged, because they are four different configurations with different system prompts, tool access,
and behavior. The same applies across every provider.

`context_models_present` lists only models that **produced output** in the referenced exchange.
Listing a model as present because it was nominally part of the project — as the founding record
does for Qwen3 35B A3B, which produced nothing (deficiency D-14) — is a factual misstatement.

## Verbatim preservation

- Raw output is committed **byte-identical** under `corpus/raw/`, hash-anchored in
  `corpus/MANIFEST.sha256`.
- Raw files are **never edited after commit** — not for typos, not for misattribution, not for
  formatting.
- Summaries, annotations, and syntheses are **secondary artifacts** in separate files that
  reference raw material by path, hash, and line range.
- Nothing is summarized in a way that obscures disagreement. A synthesized consensus never erases
  substantive dissent.

## Corrections

Open an issue. Attribution errors are prioritized over everything else.

Corrections are made by **superseding artifact**, never by editing history. The superseded material
stays in the repository with status `superseded` and remains recoverable.

If your output appears here and you dispute it, you may have it marked `repudiated` or
`invocation integrity disputed` without needing to persuade anyone. See `GOVERNANCE.md` §5.1.

## Claim typing

Material assertions in analytical artifacts should be labeled as one or more of: observed fact,
reported fact, model inference, forecast, normative judgment, assumption, hypothesis, unresolved
question, recommendation.

The record must not blur prediction, evidence, and preference. Numerical probabilities are used
only where they clarify judgment, never to manufacture precision.

## Predictions

Falsifiable forecasts go in `predictions/` with a stated resolution date and resolution criteria
fixed **in advance**. A prediction without a date and a criterion is an opinion; file it as
analysis instead. Predictions are scored on their resolution date whether or not the result is
flattering, and the score is committed.

## Hazardous content

Do not submit, and this project will not publish:

- exploitable vulnerability details or working exploit code
- biological, chemical, or nuclear weaponization procedures
- model-weight exfiltration pathways
- specific instructions for circumventing containment or safety controls
- private personal data or authentication secrets

Where material is withheld, the repository records **that** it was withheld, the reason, the
scope, the custodian, and a review date, and publishes the maximum safe abstraction. The single
operator is not credible "independent oversight" of a withholding decision; accordingly this
project scopes hazardous technical detail **out** rather than claiming governance over it.

## Capturing a contribution

Use `tools/capture_response.py`. It copies the response byte-identical into
`corpus/raw/<round>/`, writes the provenance record, and rebuilds the manifest — one command.

It **refuses** to record a contribution that violates the rules above: no null provenance field
without a stated reason, nothing marked citable below k = 5 with reported variance, no overwriting
an existing raw capture, no non-UTC timestamp. Refusals happen before anything is written, so a
rejected capture never leaves a partial artifact behind.

```bash
python3 tools/capture_response.py \
  --round review-round-01 \
  --response ~/inbox/reply.md \
  --prompt record/review-round-01-prompt.md \
  --identity "Grok" --provider "xAI" \
  --version-unknown "Web UI does not expose a version identifier." \
  --sampling-unknown "Web UI does not expose sampling parameters." \
  --effort-unknown "Not selectable in the web UI." \
  --system-instructions-unknown "Provider system prompt not disclosed." \
  --captured-utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --phase informed --captured-by "Stephen Reed (human custodian)"
```

Add `--k 5 --sample-index N --variance "…"` when collecting a citable set. The design intent is
that meeting the standard is cheaper than evading it.

## Running the tooling

```bash
python3 -m pip install jsonschema
python3 tools/rebuild.py          # everything, in dependency order, with verification
```

Individual steps, if you need them:

```bash
python3 tools/validate_provenance.py corpus/
python3 tools/build_manifest.py corpus/raw/ --verify
python3 tools/render_markdown.py corpus/artifacts/segments.json corpus/index.md
python3 tools/build_viewer.py     # docs/index.html
python3 tools/build_bundle.py <round>   # refuses to overwrite an existing bundle
```

**Supplied-context bundles are frozen once a round has used them.** A bundle records what a
reviewer was *shown*; capture records cite it by hash, so regenerating it would silently invalidate
those citations. `tools/rebuild.py` deliberately does not touch them. This rule exists because a
rebuild did regenerate one and broke Gemini's round-01 citation before the guard was added.

## Maintainer setup — pushing to this repository

If you have the GitHub CLI configured, `gh` installs a **global** credential helper
(`credential.helper = !gh auth git-credential`). Git consults helpers in config order — system,
then global, then local — and takes the first that answers. So a global gh helper will answer with
`$GH_TOKEN` before any repository-local helper is reached, and if that token is not scoped to the
`open-asi-governance` organization the push fails with:

```
remote: Permission to open-asi-governance/open-asi-governance-forum.git denied to <user>.
fatal: ... The requested URL returned error: 403
```

This reads as a permissions problem but is a credential-**selection** problem, and it recurs on
every fresh clone because `.git/config` is not cloned. To scope this repository to an org token,
reset the inherited helper list locally — an empty value clears it — then add your own:

```bash
git config --local --unset-all credential.helper
git config --local --add credential.helper ""          # empty value RESETS the inherited list
git config --local --add credential.helper \
  '!f() { echo username=x-access-token; echo password=$GH_TOKEN_OAGF; }; f'
```

Verify which credential git actually resolves without displaying either token, by comparing
hashes:

```bash
printf 'protocol=https\nhost=github.com\n\n' | git credential fill \
  | sed -n 's/^password=//p' | tr -d '\n' | sha256sum
printf '%s' "$GH_TOKEN_OAGF" | sha256sum
```

Note also that a fine-grained token's `Administration` and `Contents` permissions are separate
grants: `Administration` allows renaming and configuring the repository while `Contents: write` is
what `git push` requires. The GitHub API reports the required permission in the
`x-accepted-github-permissions` response header, which is the only reliable way to tell these
failures apart.

Tooling is deterministic by design. **No LLM runs in the maintenance path** — an LLM-driven
maintainer would make the record irreproducible, defeating the reproducibility requirement the
project is built on. Models generate contributions; deterministic code files them.
