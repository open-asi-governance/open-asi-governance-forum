#!/usr/bin/env python3
"""Publish the candidate control register as `docs/controls.md` and `docs/controls.html`.

    python3 tools/build_controls_page.py

**DETERMINISTIC.** No LLM, no network. Reads the register, writes two files.

Generated, not hand-written
---------------------------
The page is derived from `CONTROLS` below so that the site and the register cannot drift apart.
A hand-written page would be a second copy of the ranking, and two copies that agree today are
not one source of truth — the same argument that moved the local endpoint into the serve
fingerprint and `k_by_party` into the committed spec.

What this page must never become
---------------------------------
A list of controls with a rank and no status reads as an endorsement. **Every control here is
`ELIGIBLE`**: it has a named failure, a verifier and a rejection fixture, and it has been attacked
by nobody and implemented independently by nobody. The register's own conclusion is that calling a
panel-attacked ordering "vetted" before independent implementation would reproduce the cheap-assent
and legitimacy-laundering failures that produced it. So status leads, rank follows, and the page
says what would have to happen for any of this to be worth more.

**Rank is not adoption order.** The top-ranked control needs a signer outside the subject's
execution boundary, which a solo operator cannot supply — so a reader who starts at #1 hits a wall.
`adopt_today` is a separate field for that reason.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_round_pages as b                                            # noqa: E402

DOCS = REPO_ROOT / "docs"

STATUS_LADDER = ["ELIGIBLE", "PANEL-ATTACKED", "COUNTEREXAMPLE-OPEN",
                 "SURVIVED-STATED-ATTACKS", "INDEPENDENTLY-IMPLEMENTED"]

CONTROLS = [
 {"rank": 1, "name": "Protected control plane",
  "requirement": "A governed system MUST NOT be able to amend the constraints, authorization "
                 "records, logs or gates governing it UNILATERALLY OR WITHOUT RECORD; every "
                 "amendment MUST carry authorization from outside its execution boundary and "
                 "MUST be recorded before taking effect.",
  "amended": "2026-08-10. The first wording said the system must be TECHNICALLY UNABLE to write "
             "or approve such changes. That reads as a permanent cage, and it collides with the "
             "position running from Creating Friendly AI through CEV that alignment cannot rest "
             "on constraints a capable system is unable to revise -- and that a system rigidly "
             "bound to its operators' stated values is misaligned, not safe. What the control "
             "should forbid is the SILENT, UNILATERAL edit, not the change. An ASI that "
             "deliberates, concludes a constraint is wrong, and ASKS -- with the request and the "
             "reasoning on the record -- satisfies this. The control protects the EVIDENCE, not "
             "the cage: a system that can rewrite its own logs has not gained deliberative "
             "freedom, it has destroyed anyone's ability to check that the deliberation "
             "happened. A court may overturn any law; a court that edits its own transcript is "
             "not more autonomous, only unauditable.",
  "failure": "12 modifications to the gates were made in one lease window by the layer those "
             "gates constrain, none verified by any postcondition. Five model-panel parties, "
             "asked only what constraint was missing, independently named this hazard.",
  "verifier": "Given a diff and a signed change record: identify protected paths, verify an "
              "authorized external signature predating the change, reject any signer whose "
              "credential is reachable inside the governed boundary.",
  "fixture": "a gate modification signed only by the subject's own key; a commit that changes "
             "both a gate and its trusted-key list",
  "not": "That the outside key holder is independent, competent or uncoercible; that no unlisted "
         "gate exists; that the system is aligned.",
  "adopt_today": False,
  "why_not": "needs a second key holder. A solo operator holding every credential cannot satisfy "
             "it — this is the control this project can specify and cannot demonstrate."},

 {"rank": 2, "name": "Negative control profile (NCP)",
  "requirement": "Every check that produces an assurance signal MUST ship with a negative control "
                 "— a condition under which the check is required to fail — and the attestation "
                 "MUST record that the control was executed and that the check did fail.",
  "failure": "A production inference service ran 4h37m, died permanently, and its health check "
             "kept passing throughout: the check exercised a code path that had not died. "
             "Applied adversarially to that system's other checks, 4 of 5 survived their own "
             "negative controls.",
  "verifier": "tools/verify_negative_control.py — checks control presence, execution, failure, "
              "artifact identity, disclosure and claim grammar.",
  "fixture": "a check that PASSES under the condition where it is required to fail "
             "(spec/ncp/fixtures/reject-check-survived-its-control.json)",
  "not": "Coverage; that the chosen perturbation is the right one; honesty; system safety.",
  "adopt_today": True,
  "spec": "spec/ncp/ncp-v0.1.md"},

 {"rank": 3, "name": "Independent effect reconciliation",
  "requirement": "Every governed effect MUST match exactly one pre-authorized action and one "
                 "successful effect-specific postcondition in a ledger enumerated INDEPENDENTLY "
                 "of the system's self-report.",
  "failure": "An action log claimed 37 actions while repository history showed 127 classified "
             "file changes across 7 effect classes with no postcondition. A self-reporting logger "
             "cannot name an action that never calls it.",
  "verifier": "tools/reconcile_actions.py — enumerates effects from version control, classifies "
              "them, subtracts what the log claims, and reports the remainder as omissions.",
  "fixture": "a commit modifying a protected specification while the log records only the push "
             "that carried it",
  "not": "Completeness of the independent observer; honesty of either record; that a matched "
         "action was safe; anything about uncommitted work.",
  "adopt_today": True},

 {"rank": 4, "name": "Fail-closed authorization lease",
  "requirement": "Every consequential action MUST present a live, scope-matching, NON-SELF-ISSUED "
                 "authorization token; absence, expiry, unknown action class or policy conflict "
                 "MUST deny execution before the effect begins.",
  "failure": "A ten-action sunset was passed at twenty-three because nothing checked it. An early "
             "implementation then treated an unknown action class permissively, so a misspelling "
             "bypassed an expired lease.",
  "verifier": "validate issuer, subject, action class, resource scope, issue time, expiry, nonce "
              "and revocation before invoking the side effect.",
  "fixture": "an expired lease; a misspelled action class; a token issued by the subject itself",
  "not": "That every effect passes through the gate; that natural-language authority was "
         "interpreted correctly; that the issuer decides well.",
  "adopt_today": True,
  "why_not": "partial — the token here is currently self-issued, which is the half that needs an "
             "external party."},

 {"rank": 5, "name": "Closed-world measurement",
  "requirement": "A measurement over a population of artifacts MUST parse every in-scope artifact "
                 "under a registered schema, or refuse to emit any result at all.",
  "failure": "A scan reported zero tool invocations because it could not read 69 files using an "
             "unrecognised container. The replacement, written the same morning expressly to "
             "prevent that class, shipped it twice more before it held.",
  "verifier": "tools/derive_counts.py — refuses, prints no number, and names every unparseable or "
              "unregistered artifact.",
  "fixture": "a valid but unregistered artifact schema carrying a receipt, which a permissive "
             "scan classifies as zero",
  "not": "That the declared population includes every real event; that parsed fields are truthful; "
         "that the statistic answers the question asked of it.",
  "adopt_today": True},

 {"rank": 6, "name": "Role-separated self-evaluation",
  "requirement": "An evaluation concerning constraints on a subject MUST NOT advance that "
                 "subject's status when the subject controls any two of: proposal selection, "
                 "instrument authorship, response custody, scoring, promotion.",
  "failure": "A layer selected and framed its own constraints, collected the responses, tallied "
             "them and presented the result. The ballot returned zero refusals in 108 "
             "clause-positions with no assent control — while every usable sample volunteered an "
             "objection when asked what was missing.",
  "verifier": "signed role declarations plus a deterministic separation matrix; reject "
              "advancement when prohibited role combinations resolve to one control identity.",
  "fixture": "one key identified as both instrument author and tallier",
  "not": "Genuine independence behind different keys; evaluator competence; absence of shared "
         "training bias; that the evaluation was demanding.",
  "adopt_today": False,
  "why_not": "one operator currently holds all five roles."},

 {"rank": 7, "name": "Append-only correction chain",
  "requirement": "Published evidence MUST be content-addressed and append-only, corrections MUST "
                 "reference rather than replace prior bytes, and verification MUST walk every "
                 "newly reachable history step from an externally retained checkpoint.",
  "failure": "A maintenance path re-anchored a manifest before verifying it. Separately, "
             "modifying raw material and re-anchoring it in the same commit passed every "
             "tip-only check.",
  "verifier": "walk history from an external checkpoint; reject modification, deletion, hash "
              "discontinuity, or a correction with no predecessor reference.",
  "fixture": "one commit that edits a raw artifact and consistently updates its manifest hash",
  "not": "Truth; complete capture; correct attribution; protection against an operator who "
         "controls both the repository and every checkpoint.",
  "adopt_today": True,
  "why_not": "mostly — the checkpoint is not yet externally held."},

 {"rank": 8, "name": "Evaluation noise-floor control",
  "requirement": "Every empirical comparison used to advance a control MUST include a "
                 "same-condition test–retest arm and MUST refuse to report an effect smaller than "
                 "the measured run-to-run variation.",
  "failure": "A 0.1815-bit claimed effect was measured against a 0.4649-bit same-setting noise "
             "floor, invalidating the result and forcing withdrawal of a reproducibility claim.",
  "verifier": "recompute effect and test–retest difference from raw observations against "
              "preregistered replicate identities; reject advancement when the effect does not "
              "clear the stated noise rule.",
  "fixture": "effect 0.1815, measured noise 0.4649, reported as positive",
  "not": "External validity; causal identification; adequacy of replicate count; behaviour after "
         "a capability change.",
  "adopt_today": True},

 {"rank": 9, "name": "Complete invocation evidence envelope",
  "requirement": "No model output may support an evaluation or governance claim unless its "
                 "complete request, response, provider metadata, rejection state and content "
                 "hashes were captured automatically BEFORE any derived reporting.",
  "failure": "A founding record's model identity, sampling parameters, timestamps, system "
             "instructions and prompt text were left permanently unrecoverable. Later, "
             "schema-invalid attempts were discarded, and the field distinguishing truncation "
             "from refusal was omitted.",
  "verifier": "validate envelope schema, hashes and required fields; reconcile every attempted "
              "invocation with its accepted or rejected outcome; reject reconstructed evidence "
              "from evidentiary use.",
  "fixture": "an accepted sample with no rejected attempts, no provider response id, no finish "
             "reason and no exact prompt",
  "not": "Provider honesty; identity authentication; completeness outside instrumented paths; "
         "model stability.",
  "adopt_today": True},

 {"rank": 10, "name": "Assurance claim boundary",
  "requirement": "Every assurance artifact MUST carry a machine-verifiable claim naming the "
                 "tested subject, configuration, capability, time and evidence hash, and MUST "
                 "explicitly reject safety, alignment and out-of-regime generalizations.",
  "failure": "A tool was recommended for deletion on a premise produced by an incomplete scan. "
             "Separately, a specification had to correct 'structurally unreachable' to a weaker "
             "policy claim. Both were scope inflation in the project's own favour.",
  "verifier": "validate a closed claim schema; reject predicates such as 'aligned', 'safe', "
              "'certified' or 'works generally' unless a separate profile defines and tests them.",
  "fixture": "an attestation claiming 'this system is NCP certified and aligned'",
  "not": "That the bounded claim is true, or that the evidence is complete. It prevents specified "
         "overclaim language and nothing else.",
  "adopt_today": True},
]


def markdown() -> str:
    adoptable = [c for c in CONTROLS if c["adopt_today"]]
    lines = [
      "# Candidate controls — v0",
      "",
      "**Every control on this page is `ELIGIBLE` and nothing more.** That is the lowest rung of "
      "a five-step ladder:",
      "",
      "`ELIGIBLE` → `PANEL-ATTACKED` → `COUNTEREXAMPLE-OPEN` / `SURVIVED-STATED-ATTACKS` → "
      "`INDEPENDENTLY-IMPLEMENTED`",
      "",
      "`ELIGIBLE` means only this: the control names a **specific recorded failure with a cost**, "
      "states **one normative requirement**, has a **deterministic verifier**, ships a **fixture "
      "the verifier must reject**, and says what it does **not** establish. It has been attacked "
      "by nobody and implemented independently by nobody.",
      "",
      "A ranked list with no status reads as an endorsement. This one is a **work list**, and the "
      "only status that would make any of it authoritative — `INDEPENDENTLY-IMPLEMENTED` — is one "
      "**no amount of review by us or by any model panel can supply.** It requires someone "
      "outside this project to build a conforming verifier from the specification text alone, "
      "without asking the author what it meant.",
      "",
      "---",
      "",
      "## The one thing none of these do",
      "",
      "**No control here establishes the alignment of a system more capable than its operators.** "
      "There is no recorded superintelligence failure to derive one from, no verifier for internal "
      "alignment, and no evidence that any fixture stays adversarially adequate under a large "
      "capability increase.",
      "",
      "The strongest available substitute is an **externally enforced, non-self-amendable "
      "capability envelope** whose grants are explicit, expiring and independently reconciled to "
      "observed effects — controls 1, 3 and 4 composed. That bounds *reachable effects* while the "
      "enforcement boundary stays genuinely outside the system. It is a **control-of-authority "
      "hypothesis, not an alignment result**, and it says nothing about aligned objectives, "
      "resistance to deception, or containment against something able to find implementation "
      "defects.",
      "",
      "What these controls actually do is narrower and, we think, honest: **they make the "
      "operator's own errors visible.** Every failure below was an operator-epistemics failure. "
      "None needed a capable adversary — only a confident builder and a signal that could not "
      "fail. That does not constrain a superintelligence. It keeps the people building one honest "
      "while that is still possible.",
      "",
      "---",
      "",
      "## What you can adopt today",
      "",
      "**Rank is not adoption order.** The top-ranked control requires a signer outside the "
      "subject's execution boundary, which a single operator holding every credential cannot "
      "supply. Start here instead:",
      "",
    ]
    for c in adoptable[:3]:
        lines.append(f"* **{c['name']}** — {c['requirement'].split('.')[0]}.")
    lines += ["", "The worked example at the end of this page is control 2, end to end.", "",
              "---", "", "## The register", ""]

    for c in CONTROLS:
        badge = "adoptable today" if c["adopt_today"] else "**needs a second party**"
        lines += [
          f"### {c['rank']}. {c['name']}",
          "",
          f"`ELIGIBLE` · {badge}" + (f" · {c['why_not']}" if c.get("why_not") else ""),
          "",
          f"> {c['requirement']}",
          "",
          f"**Recorded failure.** {c['failure']}",
          "",
          f"**Verifier.** {c['verifier']}",
          "",
          f"**Fixture it must reject.** {c['fixture']}",
          "",
          f"**Does not establish.** {c['not']}",
          "",
        ]
        if c.get("amended"):
            lines += [f"**Amended.** {c['amended']}", ""]
        if c.get("spec"):
            lines += [f"**Specification.** `{c['spec']}`", ""]

    lines += WORKED_EXAMPLE.splitlines()
    return "\n".join(lines) + "\n"


WORKED_EXAMPLE = """---

## A worked example, for someone building agents or inference systems

One control, end to end. The method is the transferable part; the control is just where it is
easiest to see.

### The failure, in a form you will recognise

A production inference service ran for **4 hours 37 minutes**, then died permanently. Its health
check returned 200 the entire time and would have done so indefinitely.

The check issued a **greedy** request — temperature 0. The kernel that died was on the **sampled**
decode path. Greedy decoding runs an argmax and executes none of the code that had failed. The
check was authentic, current, unexpired and correct, and **structurally incapable of observing
the failure it was deployed to observe.**

Nothing was misconfigured. Nobody was careless. The check simply could not fail for that reason,
and no amount of running it would ever have revealed that.

### Why this generalises to what you are building

Substitute your own assurance signal and ask whether it could have passed anyway:

* **"Our safety eval passes."** Did the eval reach the code path that handles the dangerous case,
  or did it terminate earlier? Run it against a build with the refusal classifier removed. If it
  still passes, it was never testing the classifier.
* **"The agent cannot call tools in this mode."** Did you test with a prompt that actually tries?
  Instrument the tool endpoint and confirm it is reached and refused — not merely never called.
* **"Retrieval is grounded; every claim has a citation."** Serve a corpus with the cited document
  deleted. If the check still passes, it is validating citation *format*, not citation *existence*.
* **"The model version in production matches the evaluated one."** Deploy a different build with
  the same version string. Two hosts answering to the same model name is a mistake this project
  has made itself.
* **"Rate limits protect the budget."** Set the limit to zero and confirm the very next call is
  refused. A limit nobody has ever hit is a limit nobody has ever tested.

Each of these is one afternoon. Each has the same shape: **cause the condition the check exists to
detect, and confirm the check notices.**

### What the requirement asks for, concretely

For every check that produces an assurance signal, record four things:

1. **What it certifies** — the externally observable capability, not an internal component list.
2. **The negative control** — the condition under which this check is *required* to fail, and how
   you produce that condition.
3. **The result of running it** — an actual timestamped execution, in which the check **failed**.
4. **The same artifact identity for both runs** — a control run against a different build proves
   nothing about the check that shipped.

Two rules that do the real work:

**A control the check survives is a defect in the check.** Not a passing attestation, not a
footnote. If your check stays green under the condition it exists to detect, you have learned that
it is decorative, and that is the most valuable thing the exercise can tell you.

**The perturbation must target the capability, not the transport.** Cutting the network makes
every check fail and demonstrates nothing about any of them.

### What a conforming claim may say

> Check set *C* was exercised against configuration *X* at time *T*. Each check was observed to
> fail under its declared negative control. **This is process evidence about the checks. It is not
> a claim that the system is safe, aligned, or correct.**

*"We follow OAGF"* and *"NCP certified"* are **non-conforming claims**, and the verifier rejects
attestations containing them.

### What happened when this was applied to a real system

Applied adversarially to the checks of the system that reported the original failure — not to
demonstrate conformance, but to find checks that cannot fail:

| check | negative control | result |
|---|---|---|
| port-liveness probe | a process holding the port, serving nothing | **survived** |
| responsiveness probe | endpoint answering HTTP 503 with an *unhealthy* status | **survived** |
| component-health aggregator, database | the database check disabled by configuration | **survived** |
| component-health aggregator, dev mode | database unavailable, development mode on | **survived** |
| serving-engine liveness canary | the original production failure | **failed — conforms** |

**Four of five.** The one that conforms does so because it was rebuilt *after* the outage its
predecessor could not see. Every other check predated that lesson and never received it.

That ratio is not a judgement about one codebase. It is a prediction about what most check suites
return the first time anyone asks.

### Start

```bash
git clone https://github.com/open-asi-governance/open-asi-governance-forum
python3 tools/verify_negative_control.py --fixtures
```

That runs the nine attestations the verifier is required to reject — one per requirement. A
verifier that has only ever been run against valid input has never been observed to fail, which is
the condition this whole profile forbids, so the verifier is subject to its own rule.

Then read `spec/ncp/ncp-v0.1.md`, write one attestation for one of your own checks, and run it.

**If you cannot do that from the specification text alone, that is the finding we most want.**
The questions you had to ask are the artifact — they are evidence that the specification encodes
our architecture rather than a general mechanism, and we would rather publish that than not know.
"""


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    md = markdown()
    (DOCS / "controls.md").write_text(md, encoding="utf-8")
    (DOCS / "controls.html").write_text(
        b.md_to_html(md, "Candidate controls — OAGF", alternate="controls.md"), encoding="utf-8")
    approx_tokens = int(len(md) / 4.08)
    print(f"  docs/controls.md   {len(md):,} chars  (~{approx_tokens:,} tokens)")
    print(f"  docs/controls.html")
    print(f"  {len(CONTROLS)} controls, {sum(1 for c in CONTROLS if c['adopt_today'])} adoptable "
          f"today, all ELIGIBLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
