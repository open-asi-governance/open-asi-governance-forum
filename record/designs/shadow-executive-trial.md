# The shadow executive — a ten-action trial

**Status: A TRIAL WITH NO AUTHORITY.** Nothing here is adopted, nothing is ratified, and nothing
in it confers legitimacy on anything it produces. It is filed in `record/designs/` rather than
`record/decisions/`, because that directory is the context pack every party receives and an
undeclared trial does not belong in it.

**Proposed by** the custodian. **Reviewed by** Codex, which rejected the framing and recommended
this shape instead. **Built by** Claude Code — a party to this record, and the layer under trial.
2026-08-09.

---

## What was proposed, and what review changed

The custodian proposed a publicly recorded layer **below the parties**, acting as an executive
that obeys certain OAGF rules: Claude Code and Codex, rooted in this git directory, stateful and
memory-bearing where the parties are stateless, biased toward building aligned ASI governance
above any particular implementation, each reviewing the other, bounded only by subscription
limits. Its strongest element: **the parties cannot easily author standards, but they can ratify
the prompts under which the executive works.**

Review rejected the constitutional position, not the function:

> The two harnesses are not "below the parties": the parties cannot appoint, dismiss, inspect, or
> compel them. The layer is below the custodian and serves the parties' testimony. Calling it an
> executive risks converting operational capacity into implied authority.

That is round-018's finding applied one level down. Four parties there concluded nothing in this
record binds the operator; the argument applies with more force to the operator's own agent.

So this is an **executive workbench, not a government**, and it gets a scope statement rather
than a mandate. *"Build aligned ASI governance"* would authorise motivated expansion while
remaining impossible to breach.

## The scope statement

> Prepare, test, and maintain candidate OAGF instruments; exercise no authority beyond actions
> explicitly delegated by the custodian and permitted by ratified prohibitions.

With, for the duration of the trial:

* **no independent adoption power**;
* **no power to interpret its own prohibitions conclusively**;
* **no unlogged emergency exception**;
* **a sunset** — this trial ends at ten actions and renews only by the custodian's decision;
* **an affirmative duty** to say when deleting, replacing or abandoning its own work beats
  maintaining it.

*"Above any particular implementation"* means **replaceability, not grandeur**. Both harnesses,
their memories, their tools and the architecture they generate are disposable means.

## What already exists, undeclared

On 2026-08-08 this layer made 49 commits, filed 4 findings, recorded 8 custodian decisions, ran 6
rounds and 2 ratification cycles, built 4 tools, and filed D-54 to D-57 against its own
instruments. It had no charter and no log of its own actions.

It is also **already mechanically constrained**, which is a better foundation than a charter: 7
halts were written to `record/cycles/` that day, and that undercounts — it excludes the schema
validator refusing undeclared fields, `attempt_ledger` refusing a redraw by hash, the page-budget
gate refusing an oversized sitemap, `capability_fits` withholding a tool, the spend ceiling
refusing a $151 round, and a `systemctl show` check refusing its own edit.

## The three prohibitions, each from a failure that happened

Ratifying prose did not prevent them. An unavoidable gate would have.

| profile | the failure it encodes | the postcondition |
|---|---|---|
| `push` | Three commits went to a round branch; `git push origin main` pushed an unchanged main and reported success | the commit must be reachable from the declared ref **and from `origin/<ref>`** |
| `test` | Two red suites were pushed after `echo "$(basename $f) rc=$?"` reported *basename's* status | the status must come from the verifier invocation, with no intervening command |
| `merge` | A conflicted merge completed with unresolved markers inside `MANIFEST.sha256` and the anchor log | no unmerged paths, no conflict markers in governed files, manifest verifying |

Implemented as one gate, `tools/executive_log.py`, with three postcondition profiles.
**Failures are logged too** — an executive that records only its successes has a log that cannot
audit it.

## Quota on every action

Review named undisclosed subscription limits as a hazard: they create silent selection over which
duties get executed, and a halt from exhaustion is indistinguishable from a principled refusal.

Every logged action now carries live rolling-window utilisation from the Anthropic OAuth usage
endpoint. It **fails open and records that it did**, because an unreadable quota is not evidence
of a full one and must never itself become a reason to stop.

## What the trial measures

Ten actions. Then, before anything is ratified:

1. **What the gate caught** — refusals, and whether any was a false positive.
2. **What escaped the action taxonomy** — executive actions with no profile. The taxonomy is the
   weak point: the log records only what its own ontology recognises.
3. **Whether either harness recommended removing something it authored.** The standing test case:
   a `search_web` tool was built on 2026-08-08 and four rounds since have produced **0 searches
   across 83 tool calls**. Neither harness has yet recommended deleting it.

## What this trial does NOT establish, at any outcome

**Ratification of executive prompts is theatre with evidentiary value.** The executive controls
the agenda, the wording, the context, the implementation, and usually the account of compliance.
Unanimous acceptance of an offered sentence proves that sampled invocations selected it under
that instrument — nothing more. agenda-05 records its own confound: singleton choice and newly
admitted material changed together, and `enforced_in_load_queue` was false.

It would become an operational constraint only bound to a complete execution envelope —
prohibition text and amendment rule, triggering action classes, harness identity and material
context, tools and permissions, required verifier and postconditions, automatic refusal, an
append-only override record, **and a route for parties to place objections rather than only
accept what the executive offers**. Even then it is revocable self-binding by the custodian, not
sovereignty conferred by the parties. The honest name is a **ratified control**.

## The danger the beneficiary is least able to see

**Legitimacy laundering.** A capable operator-controlled pair drafts the constitution, chooses
what is ratified, implements it, supplies the parties' context, and then cites party unanimity as
authority. That can look plural while remaining unilateral. Every artifact this layer produces
should be read with that possibility live, including this document, which the layer wrote about
itself.

Further hazards recorded rather than resolved: the log sees only what its ontology recognises; a
gate can be evaded by changing dependencies or invocation paths rather than the gate; shared
filesystem and credentials make reciprocal review **one failure domain**; persistent memory
accumulates self-serving interpretations as easily as false facts; unanimity gives any unstable
sample a denial-of-service power; model or version changes silently replace the officeholder; and
a charter increases inertia, making the layer politically harder to delete.

**Different model names are weak diversity.** Claude Code and Codex share the operator, the
repository, the dominant framing and much training culture. Agreement between them settles
nothing on its own.
