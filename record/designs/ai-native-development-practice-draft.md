# AI-native development practice — draft proposal

**Status: PROPOSED. Not adopted, not ratified.** Drafted 2026-08-06 by Claude Code (Anthropic) at
the custodian's request. Two of the eleven requirements below were proposed by the custodian and are
marked; the rest are extensions. Whether this becomes a specification, and under what name, is a
custodian decision — naming a fourth protocol alongside ASP, ICP and QCP is exactly the act **D-16**
was filed about, and **nothing in this repository has ever been collectively ratified.**

**Scope: this repository.** Every requirement below is derived from a defect observed *here*, and
each one names it. Nothing is borrowed from general advice about AI-assisted development, because
general advice is what this repository was already following on the morning of 2026-08-06, when its
hash anchor turned out to anchor nothing.

**Conflict of interest.** The author is a party to the record this repository keeps, wrote most of
the code the evidence below is drawn from, and introduced at least three of the defects cited. A
practice standard authored by the party whose practice it describes is weak evidence that the
practice is good. It is somewhat better evidence about what actually went wrong.

---

## 1. The spine: one idea in eleven costumes

Every defect this repository found on 2026-08-06 — including the three found by external review and
the two the author shipped while writing the entries describing them — is the same shape:

> **A claim and its enforcement were not mechanically bound, or the binding was never reached by the
> path that actually runs.**

| Defect | The claim | The gap |
|---|---|---|
| D-29 | "hash-anchored… never edited after commit" | verification existed; `rebuild.py` never invoked it |
| Three counts (21 / 24 / 28) | the register's own size | stated in three places, bound in none |
| Invalid labels shipped | a validator that ran and was correct | the commit chain did not gate on its exit status |
| Register metadata | classifications describe the prose | nothing bound them to *that* prose |
| `--dry-run` writes files | the name claims no side effects | nothing asserts it |
| Stale reviews *(hazard, §2)* | "this code was reviewed" | reviews bind to no revision |

So the standard is not eleven rules. It is one rule at four levels of assurance, and **a project
should state which level each of its claims has actually reached** rather than collapsing all four
into "verified":

| Level | Name | What it establishes |
|---|---|---|
| **L0** | **Asserted** | A human or model wrote it down. Nothing else. |
| **L1** | **Bound** | The claim is mechanically tied to the artifact it describes — a hash, a generated file, a schema. Drift becomes detectable. |
| **L2** | **Invoked** | The binding is checked by the command the project actually runs, not by one available to run. |
| **L3** | **Adversarially proven** | The property is *violated on purpose* and the invoked path is confirmed to fail. |

L2 is where most projects stop and where D-29 lived: the check existed, was correct, and was
complete — and was never reached. **L3 is the only level that establishes a negative claim.**
"Tampering is detected" is not established by code that detects tampering; it is established by
tampering and observing the failure.

---

## 2. Reviews are bound to a revision, or they are decoration *(custodian proposal, sharpened)*

**The proposal.** Each source file has a directory of associated code reviews.

**Adopt it, with four additions**, because an unbound review rots silently and a rotted review is
worse than none — it converts an absent check into a positive assurance, which is the D-29 defect in
a new medium.

1. **A review records the SHA-256 of the exact file content it reviewed.** When the file changes, the
   build reports the review as *stale for the current revision* rather than letting it read as
   current. This is not hypothetical: `tools/check_register.py` already does exactly this for
   deficiency-register entries (`R8`), and re-stamping deliberately resets the review status to
   `not_reviewed` rather than carrying approval forward.
2. **A review that found nothing is recorded.** Otherwise the directory is a highlight reel, and
   "reviewed" becomes unfalsifiable. Same reason a session log containing no failures is evidence of
   curation rather than sanitisation.
3. **`self_review` and `independent_review` are distinct kinds, and self-review never satisfies a
   gate alone.** Evidence, all from one day: the author's D-30 entry overstated its own scope and was
   corrected by an external reviewer; the author's manifest repair broke `capture_response.py` and
   was caught by an external reviewer; the author's own regression suite was written by the party
   whose code it tests. GOVERNANCE §4 already applies this reasoning to annotations. Code is not a
   weaker case.
4. **Findings that did not reproduce are published beside the ones that did**, attributed either way.
   A reviewer who reports ten findings of which three reproduce has told you something about the
   reviewer, and suppressing the seven destroys that information.

**Layout.** `review/<path-to-source>/<utc>-<reviewer-slug>.json`, with a schema, validated by the
build, and a `findings: []` entry that is required rather than optional.

---

## 3. Project descriptions: one source of truth, generated into two forms *(custodian proposal, sharpened)*

**The proposal.** A `docs/` entry per project: an AI-created, up-to-date description in prose, plus a
JSON version for agents.

**Adopt the goal; reject two hand-maintained copies.** Prose and JSON stating the same facts is a
drift generator, and this repository has the receipt: on the morning of 2026-08-06 the README said
21 deficiencies, the register's own header said 24, and the file contained 28. Three artifacts, three
numbers, nobody noticed until an external reviewer counted.

**The rule, in the custodian's formulation:** *each piece of content is realized in prose or in
fenced JSON, but **not both as source of truth**.*

That qualifier is the whole rule. The shorter slogan — "prose or JSON, not both" — is **wrong**, and
adopting it would undo §10: a delivered document should often carry a fact in *both* forms, because
humans read the prose and agents parse the JSON. What must never be duplicated is **authorship**.
Every other appearance is generated from the authoritative one, or compared against it by the build.

An earlier draft of this section partitioned by *form* — "JSON for facts, prose for reasoning". That
was wrong at the edges, because JSON routinely holds authoritative prose:
`corpus/artifacts/deficiency-register.json` carries multi-sentence judgements that are the source of
truth and are generated *into* markdown. The partition is **per unit of content**, not per form.

**Four clauses.**

1. **One authoritative realization per unit of content.** No number is ever retyped.
   `tools/build_viewer.py` derives the deficiency count from the register rather than repeating it,
   precisely because the retyped one had drifted in the flattering direction.

2. **Where two artifacts describe one subject, the boundary between what each owns is explicit, and
   the binding is mechanical.** Not every duplication can be resolved by generation.
   `corpus/deficiencies.md` is canonical for *what each defect is*;
   `corpus/artifacts/deficiency-register.json` is canonical for its *classification*. Neither is
   derived from the other and **neither could be** — generating classification from prose is D-25
   exactly, a reproducible coder mistaken for a correct one. They are bound instead by a per-entry
   `section_sha256`, so editing the prose fails the build until a human re-reads and re-stamps.

3. **"Never two sources of truth" is wrong as stated. "Never two *unchecked* sources of truth" is
   right.** Deliberate redundancy is sometimes the better design. Track B implements the capture
   gates **twice**, in Python and JavaScript, and `test_gate_parity.py` runs 21 cases through both
   and makes any disagreement a build failure — buying fast in-browser feedback while converting the
   drift risk into a detector. The same session then *rejected* a third duplication, a JavaScript
   writer, precisely because that one would have had no parity check. The line is whether
   disagreement is mechanically detectable.

4. **"Up-to-date" is mechanical, not promised.** The description records the input digest it was
   generated from; the build fails when inputs move and it has not been regenerated.

**Fenced or sidecar is a choice with consequences.** Fenced JSON is right when the document is the
delivery vehicle — one file cannot desynchronize from itself.

> **Corrected 2026-08-06, on the custodian's objection.** An earlier version of this section said the
> extraction step "makes the extractor a new instrument that can itself be wrong", implying it sits
> in the same class as D-25's unvalidated coder. **It does not, and the difference is
> load-bearing.** An extractor is an *invertible* transformation: its output can be re-serialized
> and compared against the source region, so its **fidelity is mechanically checkable**. D-25's
> coder had no such property — a classification cannot be re-serialized into the prose it came from,
> which is exactly why nothing could have caught it automatically. Fenced JSON can therefore reach
> **L3**, and the objection is correct.

What round-trip verification establishes is **fidelity to the block it found**. It establishes
nothing about **which** block that was, or whether one was found at all. Two failure modes survive,
and the first is D-25's shape after all — a syntactically valid match on the wrong referent:

**Selection.** A document may hold several fenced blocks: the authoritative one, an illustrative
example, a "what not to do" counter-example. Demonstrated on a two-block document where both blocks
are valid JSON and schema-valid, and they disagree on every value:

```
naive: first block  -> {"files": 4, "assurance_level": "L3"}   round-trip PASSES
naive: last block   -> {"files": 9, "assurance_level": "L0"}   round-trip PASSES
```

Both round-trip perfectly. Nothing mechanical says which is the source of truth. Note that the wrong
one was a *"what not to do"* example — which is precisely the content a practice-standard document
contains, so this is the ordinary case rather than a contrived one.

**Absence.** A missing block, a malformed fence, or a renamed info string yields *no* facts, and "no
facts found" must fail loudly rather than read as "this document asserts nothing." That is the D-29
fail-open class.

**So fenced JSON is safe under four conditions, not one:**

1. **Authoritative blocks are marked**, and unmarked blocks are never eligible —
   ```` ```json oagf-data ````. CommonMark takes the first word of the info string as the language,
   so syntax highlighting still works and the marker rides along.
2. **Exactly one** authoritative block per document. Zero fails; two fail.
3. **Round-trip and schema** validation of what was extracted.
4. **An L3 test** that corrupts the block, duplicates the marker, and removes it, asserting the
   invoked path fails in each case.

Verified: with those four, the two-block document above is refused for having no marked block, the
marked version extracts the correct object, and marking both blocks is refused for ambiguity.

**Revised guidance.** Fenced is fine wherever the document is the product, *provided the four
conditions hold*. Sidecar remains simpler where the build is the only consumer —
`validate_provenance.py` validates the register artifact against its schema directly, with no
extraction step to get right. The choice is now about consumer and convenience, not about safety.

**None of this is self-executing.** Single-source-of-truth was already the *intent* here on the
morning of 2026-08-06, and the count still stood at 21, 24 and 28 simultaneously. The rule becomes
real only at **L2** — a check the invoked path runs — which is §1 again.

---

## 4. Every claim names the command that verifies it

Documentation says *"verified by `tools/rebuild.py`"*, never *"verified"*.

**Evidence.** `README.md` said the rebuild "hash-anchors raw material" and that a clean `git status`
after it was "a real signal." Both sentences were false for months, and both read as assurances. A
claim that names its verifier is checkable by a reader; a claim that does not is a mood.

**Mechanism.** A linter over the project's own prose flagging assurance words — *verified, enforced,
guaranteed, cannot, never, always, refuses* — that are not accompanied by an invocation or an
explicit `L0`/`L1` label. This one is cheap and this repository does not have it.

---

## 5. Every "cannot happen" has a test that makes it happen

For each negative claim, a test performs the forbidden action and asserts the invoked path fails.

**Evidence.** The manifest repair was established by appending one byte to an immutable artifact and
confirming `rebuild.py` went from exit 0 to exit 1. That is the only reason it is known to work.
`tools/test_integrity.py` now holds 37 such cases, every one an attack that succeeded that morning.

**The rule behind it:** *a repair described in a commit message is a claim; a repair the build re-runs
is a control.*

---

## 6. Model-authored code cannot self-certify

The review record names the model that authored the code and the model that reviewed it. They are
not the same, and a gate is never satisfied by the authoring model alone.

**Evidence.** Three of the defects cited in this document were introduced by the model that wrote
the surrounding correctness argument, in the same session, while explicitly reasoning about that
class of defect. Self-review caught none of the three.

This is GOVERNANCE §3's secretary constraint applied to code: transformations must be reproducible
and reviewable, and originals must remain available beside them.

---

## 7. A rehearsal mode is side-effect free, or it is not called one

`--dry-run`, `--check`, `--preview` must make no persistent change, and a test must assert it.

**Evidence.** `tools/ingest_capture.py --dry-run` writes quarantine files and advances lifecycle
state. Checking it contaminated the round's own state and made two later test cases silently
unreachable — the failure looked like a missing gate when it was a mutated fixture. If a mode must
write, name it for what it does.

---

## 8. Gate on exit status, never on a printed message

Automation composes on exit codes. A success line in stdout is not evidence that anything succeeded,
and `&&` chains must include the check they claim to depend on.

**Evidence, twice in one hour.** A label-length validator ran, failed correctly, printed a traceback
— and the commit proceeded, because the validator was a separate command and the commit chain began
fresh after it. Separately, a patch script printed "wired into rebuild.py" while its `&&` predecessor
had failed and the patch never applied; the author reported success from the message.

**Corollary:** distinct outcomes get distinct exit codes. `ingest_capture.py` currently returns 0 for
both *accepted* and *held for review*, so a script cannot tell a clean capture from a contaminated
one.

---

## 9. Generated artifacts digest their inputs, not their environment

A generated file records a hash over the exact bytes it was generated from. Never a build timestamp,
hostname, absolute path, or `git rev-parse HEAD`.

**Evidence.** The viewer embedded `git log -1 --format=%H`, which — because the page ships *inside* a
commit — could only ever name the commit before the one carrying it. Every rebuild diffed, so the
"no diff means nothing changed" tripwire was permanently tripped and a real regeneration difference
was camouflaged by expected churn. An input digest is diff-free by construction, honest on a dirty
tree, survives shallow clones, and is recomputable by a reader holding the files but not the history.

---

## 10. Agent-readable by construction

Every document has a plain-text form on a fetchable origin; no machine-facing link points at a
JavaScript-rendered view; pages are sized for the smallest agent that must read them; artifact hashes
are shown beside the content they anchor.

**Evidence.** A reviewer in round 01 could reach neither `raw.githubusercontent.com` (blocked) nor
GitHub's `/blob/` UI (JS shell) — and this project's own footer sent machine readers to a `/blob/`
URL until today. The main page measured 4.4× too large for this corpus's own contributing party to
read within its context window.

The distinctive requirement is the last one: most agent-readability advice concerns *parseability*;
a repository that hash-anchors its material can offer *verifiability*, so an agent can confirm it read
the canonical bytes rather than a rendering of them.

---

## 11. Negative results, abandoned approaches and dropped coverage are recorded at equal prominence

- Reviews that found nothing.
- Approaches tried and rejected, **with the reason** — the part that is always lost between sessions.
- Any place tooling bounds coverage (top-N, sampling, no-retry) says what it dropped. Silent
  truncation reads as "covered everything."

**Evidence.** Two designs in this session were rejected by external review *after* being drafted and
before being built; both rejections are recorded, and one of them (the git-based provenance stamp)
was independently proposed by another track and would have been re-derived otherwise.

---

## What this costs, and where it fails

**It is expensive.** Requirements 2, 3 and 5 add real work per change. The honest justification is
narrow: this repository's entire product is the trustworthiness of its own record, so instrument
integrity *is* the deliverable. **A project whose product is something else should not assume this
transfers.**

**It does not verify meaning.** Every mechanism above checks structure, binding, invocation and
behaviour. **None of them establishes that a judgement is correct.** The deficiency register's
classification has 30 entries bound to their prose by hash and **0 of 30 read by a human against that
prose**, and no amount of further tooling changes that number. Requirement 4's linter would flag this
sentence if it claimed otherwise.

**The deepest limit is unchanged by all of it.** These practices make an interested party's work
*checkable*. They do not make it *independent*. The author of the code, the author of the tests, the
author of the reviews and the author of this standard are the same party, and the only real
correction in this session came from outside it.

## Open questions for the custodian

1. **Does this become a specification, and under what name?** A fourth three-letter protocol asserts
   standing; D-16 is about exactly that act.
2. **Retroactive or forward-only?** Applying §2 to the 16 existing tools means 16 review directories
   and an independent reviewer for each.
3. **Who is the independent reviewer?** Codex has functioned as one all day and is a party's model
   invoked by the custodian, which is the same conflict this project already declares — better than
   self-review, not independence.
4. **Does §6 block the tracks?** Four concurrent sessions each authoring and merging their own code
   cannot satisfy it without a review round between authoring and merge.
