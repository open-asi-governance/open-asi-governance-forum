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

Two propositions, two fields — they are not the same claim:

- `citability` — **a single sample IS citable as an artifact** of one identified invocation. It is
  evidence that this text was produced.
- `distributional_inference` — whether the contribution can support a claim about the model's
  *distribution of positions*. At k = 1 this is `insufficient_k`, always.

Contributions supporting a distributional claim are collected at **k ≥ 5 independent samples**,
all samples preserved, with the variance **computed from them** — not asserted. Required sample
size is chosen from observed variance; five is a floor, not a sufficiency proof.

The founding record is entirely k = 1. That is deficiency D-07, permanent for that record.

*An earlier version of this section tagged single samples `non-citable`, conflating the two
propositions. Corrected per ChatGPT, review round 02 — and the capture tool and schema, which had
gone on enforcing the superseded label on every capture, were corrected with it.*

## Identity rules

**A distinct model or invocation surface is a distinct identity.**

"Claude," "Claude Opus 5," "Claude Fable 5," and "Claude Code" are four labels and are never
merged, because they are four different configurations with different system prompts, tool access,
and behavior. The same applies across every provider.

`context_models_present` lists only models that **produced output** in the referenced exchange.

*This definition is forward-looking. The founding record's schema never defined the field, so its
listing of Qwen3 35B A3B — which produced nothing — is **schema ambiguity**, not a violation of a
definition that did not yet exist. The substantive defect there is the unsupported attribution of
the member, secretary and maintainer roles. See D-14, reframed per ChatGPT and Claude Fable 5,
review round 02.*

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

This shows the end-to-end capture path and its separate operator actions.

```text
PARTY REPLY
    |
    +-- local JSON capture bundle
    |       |
    |       | ACTION 1A - DELIBERATE: run ingest_capture.py
    |       v
    |   [AUTOMATIC] reconcile with frozen round; run capture gates
    |       |
    |       +-- empty or invalid --> REFUSED; no lifecycle entry
    |       v
    |   record/quarantine/<round>/<party>-NN.md (non-empty bytes)
    |   record/rounds/<round>-lifecycle.jsonl
    |       |
    |       +-- gate concern --> HELD for a separate operator disposition
    |       |                       |
    |       | ACTION 1B - DELIBERATE: accept or reject with a reason
    |       |                       +-- reject: bytes remain in quarantine
    |       |                       +-- accept ---------------------+
    |       +-- clean ---------------------------------------------+
    |                                                               |
    +-- response file                                               |
            |                                                       |
            | ACTION 1C - DELIBERATE: run capture_response.py       |
            | Direct use bypasses the gates and lifecycle.          |
            +-------------------------------------------------------+
                                                                    v
                       [AUTOMATIC] capture_response.py
                             single corpus writer
                                      |
                         +------------+-------------+
                         v                          v
          corpus/raw/<round>/<party>-NN.md   corpus/artifacts/<round>/
          byte-identical canonical reply     <party>-NN.json provenance
                         |                   records raw + prompt hashes
                         v                          |
          [AUTOMATIC] build_manifest.py --add       |
          verify old hashes; add only new raw hash  |
                         |                          |
                         v                          |
               corpus/MANIFEST.sha256               |
                         |                          |
          ACTION 2 - DELIBERATE:                    |
          run anchor_manifest.py --stamp            |
                         |                          |
                         v                          |
          OpenTimestamps calendars                  |
                         |                          |
                         v                          |
          digest-named .ots receipt                 |
          + manifest-anchors.jsonl                  |
          Later DELIBERATE --upgrade fetches        |
          the Bitcoin attestation.                  |
                         |                          |
                         +------------+-------------+
                                      |
              ACTION 3 - DELIBERATE: run rebuild.py
                                      v
          [AUTOMATIC] verify raw (do not write manifest)
                      check the current manifest has an anchor record
                      validate provenance; regenerate derived pages
                                      |
                                      v
                 corpus/index.md + docs/ published pages
                                      |
            ACTION 4 - DELIBERATE: review the diff, then commit

NORMAL ADD DIFF: A new raw + A provenance + one new manifest entry.
ALTERATION DIFF: M/D/R an old raw file. Capture cannot produce this;
                 --add and rebuild refuse it. --force-rewrite is a
                 separate governance action, never part of rebuild.
```

This maps each safeguard to its failure and to whom it can constrain.

```text
Legend
  [A] catches accidents in the supplied path; operator can bypass it
  [P] constrains the operator procedurally; operator still owns the process
  [E] creates an external fact the operator cannot later backdate

CAPTURE BUNDLE
    |
    +-- [A] CAPTURE GATES at ingest, before corpus promotion [D-10]
    |      Catch: empty reply; exact or normalized prompt-as-reply;
    |      prompt saturation >= 0.60 when there are >= 50 shingles.
    |      Empty is refused. Non-empty suspects are preserved and held;
    |      truncation is diagnostic only. This avoids silently losing text.
    |      Limit: direct capture_response.py bypasses every gate. Gates
    |      target accidental paste errors, not identity fraud or deliberate
    |      evasion; changing every eighth word can defeat the heuristic.
    v
QUARANTINE
    |
    +-- [A] IMMUTABLE-WRITER RULE
    |      Catch: overwrite of an existing quarantine or raw path.
    |      Corrections require a new or superseding artifact.
    |      Limit: repository access can edit files outside these writers.
    v
CANONICAL RAW + PROVENANCE
    |
    +-- [A] k >= 5 AGGREGATION
    |      Catch: typed variance is refused; only schema-valid,
    |      self-reported JSON samples count. Counts, modal share, and
    |      Shannon entropy are computed, never asserted.
    |      Limit: this is observed dispersion, not proven sampling
    |      variance. Independence is unverified, and five is a floor,
    |      not a sufficiency proof. Unusable samples remain preserved.
    |
    +-- [A] MANIFEST --add
    |      Catch: changed or missing old raw; HEAD lineage changes.
    |      Only new raw hashes are added. An explicit --force-rewrite
    |      can create a new baseline, but is a separate governance action.
    v
CURRENT MANIFEST
    |
    +-- [A] REBUILD GATE 1: manifest verification [D-29]
    |      Rebuild VERIFIES; it never writes the manifest. A mismatch or
    |      unanchored raw file stops the build before anything is derived.
    |      D-29 was the opposite: rebuild wrote a new baseline first,
    |      re-anchored tampered bytes, and then reported success.
    |
    +-- [E] EXTERNAL TIMESTAMP; [A] local rebuild check
    |      A genuine OpenTimestamps receipt can prove the manifest bytes
    |      existed no later than a Bitcoin block. It constrains later
    |      backdating or silent revision for a reader retaining the proof.
    |      Limit: rebuild checks the local anchor log and receipt; it does
    |      not run an OpenTimestamps cryptographic verification. The
    |      operator chooses what and when to stamp, and can delete the repo.
    |
    +-- [A] REBUILD GATE 2: provenance validation
    |      Catch: schema failure and raw or prompt bytes that differ from
    |      the hash in a contribution artifact.
    |      Limit: co-edited records can be self-consistent; no hash proves
    |      truthful origin, correct attribution, or truthful contents.
    |
    +-- [A] DECLARED GENERATORS
    |      Rebuild regenerates the index, viewer, capture page, register
    |      views, and other declared outputs from validated inputs.
    v
DERIVED OUTPUTS
    |
    v
COMMIT / PULL REQUEST
    |
    +-- [P] APPEND-ONLY HISTORY CHECK on corpus/raw [D-34]
    |      Catch: every in-range commit that modifies, deletes, renames,
    |      or retypes old raw; additions are allowed. This catches raw
    |      edit + re-anchor in one commit. Tip verification does NOT catch
    |      it after that self-consistent commit becomes HEAD.
    |      Limits: only the supplied range; not pre-check or discarded
    |      history, nor false bytes captured initially. Branch protection
    |      binds the custodian today; the operator can change that control.
    |
    +-- [P] CLEAN REGENERATION CHECK [D-33]
    |      CI deletes checked generated outputs, rebuilds, and rejects a
    |      diff. It catches stale or hand-edited output, including the
    |      capture page that once carried a mismatched prompt hash.
    |      Limit: only the declared generators and checked output paths.
    v
PUBLISH

No path is tamper-proof: the operator controls the hardware, capture, code,
repository, and publication. [A] limits accidents; [P] raises the cost and
visibility of operator revision; only the narrow timestamp fact is external.
```

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

## Concurrent sessions

Work is divided between sessions by track and by branch. See [`HANDOFF.md`](HANDOFF.md) before
starting, and read `corpus/deficiencies.md` D-23 through D-28 before building any measurement — they
record six ways an instrument in this project was silently wrong, all found late.

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
