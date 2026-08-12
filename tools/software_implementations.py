#!/usr/bin/env python3
"""Which admitted controls have executable implementations an ordinary software team can run.

    python3 tools/software_implementations.py           # the companion view
    python3 tools/software_implementations.py --check   # refuse a member the rule rejects
    python3 tools/software_implementations.py --write   # regenerate the file and the page

WHAT THIS IS, AND THE QUESTION IT IS ALLOWED TO ANSWER
-------------------------------------------------------
The custodian asked whether the register could carry a section of general best-practice controls
that would also apply to a code-implemented ASI, the example being the usefulness of programmatic
commit gates. Codex ruled on 2026-08-12, and the ruling shapes this file more than the question
did. Its strongest objection is worth stating before anything else, because it is the reason this
is a generated crosswalk and not a new part of the register:

  "Renaming it does not cure the central problem. 'Engineering-derived' can launder evidence
  almost as easily as 'best practice': it selects familiar, implementable controls, groups them
  under an attractive heading, and makes the register look more mature and ASI-relevant without
  adding any evidence about ASI."

So this view answers exactly one question — **which admitted controls have executable software
implementations or incident instances an ordinary team can reproduce now** — and it is refused
the question it would rather answer, which is "which controls are best practice for ASI".

WHAT IT IS NOT
---------------
* **Not a new part of the register.** The register partitions by PREREQUISITE: adopt without a
  second party, needs a second party, needs a goal or plan graph. "Engineering provenance" is not
  a fourth prerequisite — the lease and the deploy interlock would belong in two places at once —
  so provenance is orthogonal metadata and this is a view over it.
* **Not a promotion.** A member keeps its canonical control's rank, status and prerequisites, and
  appearing here confers none of them. Every control in the register is still `ELIGIBLE`, meaning
  attacked by nobody and independently implemented by nobody.
* **Not a second copy.** Rank, status, prerequisite and name are read from `build_controls_page`
  at render time. A handwritten copy that agrees today is not one source of truth.
* **Not a claim about ASI.** Every member carries a transfer HYPOTHESIS with its boundary
  condition stated, and a nonclaim at least as prominent as the requirement. Nothing here has
  been tested on an ASI and the code refuses a member that says otherwise.

WHY THE ASI HALF IS PHRASED THE WAY IT IS
-------------------------------------------
Codex: *"'Code-implemented ASI' does almost no useful limiting work. The operative conditions are
the architecture, effect boundary, write authority, observer independence, and bypass resistance —
not the label ASI."* So each member states the boundary its transfer depends on, and the claim it
makes is conditional on that boundary holding — which is a claim that can be false, rather than an
applicability assertion that cannot.

THE ADMISSION RULE IS ENFORCED, NOT DESCRIBED
-----------------------------------------------
Eight guards, SI-01 … SI-08, each with a fixture in `tools/tests/test_software_implementations.py`
that makes it fire. The rule that matters most is SI-01: a member must reference a canonical
control that independently meets the eligibility bar. That one bites immediately — it refuses the
deploy interlock (control 23) and guard identity (control 45), which are two of this project's
better pieces of work, because those controls are below the eligibility line. See
`REFUSED_MEMBERS` for what was kept out and why; that list is the honest half of this file.

WHAT THIS DOES NOT ESTABLISH
-----------------------------
* That any member's implementation is correct, complete, or non-bypassable. Several are recorded
  in the register as partially remediated, and `land.py` states in its own source that a
  shell-level bypass remains available.
* That the incident cited establishes the control at its full breadth. It establishes the narrow
  predicate the fixture tests. Codex, on the commit gates: the incidents do not jointly establish
  that "one sanctioned landing path" is sufficient, unavoidable, or robust against a capable
  subject.
* That an implementer gains anything a CI handbook lacks — EXCEPT the four things a handbook does
  not carry, which are the reason this exists at all: the exact incident, the predicate that would
  have rejected it, **the failed first repair**, and what remains bypassable.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from guards import guard                                                # noqa: E402

VIEW = REPO_ROOT / "record" / "controls" / "software-implementations.md"
DOCS = REPO_ROOT / "docs"

#  The six topics a nonclaim must cover. Named rather than left to judgement, because "state what
#  this does not establish" without a checklist becomes one sentence about scope.
NONCLAIM_TOPICS = {
    "ASI non-testing": ("asi",),
    "bypass": ("bypass", "bypassable"),
    "capability increase": ("capability",),
    "completeness": ("complete", "completeness", "every effect"),
    "safety": ("safe", "safety"),
    "alignment": ("align", "aligned", "alignment"),
}

#  Phrases that are consensus offered as evidence. This register's whole discipline is that a
#  control earns its place from a recorded failure with a cost, never from being widely agreed.
CONSENSUS_PHRASES = ("best practice", "best-practice", "industry standard", "widely used",
                     "widely accepted", "everyone does", "standard practice", "well known",
                     "well-known", "commonly recommended")

#  Categorical applicability. A transfer hypothesis can be false; an assertion cannot.
CATEGORICAL_PHRASES = ("applies to any asi", "applies to all", "will apply to", "guarantees",
                       "ensures that an asi", "any superintelligence", "always applies")

#  A verifier that reads only the subject's own success signal is the failure mode control 64
#  exists for, and the failure mode `git ls-remote` was.
SUBJECT_SIGNAL_ONLY = ("exit status", "exit code", "return code", "stdout", "the tool's output")


MEMBERS: list[dict] = [
 {"slug": "remote-ref-landing-postcondition",
  "title": "Remote-ref landing postcondition",
  "control": 3,
  "incident_surface": "version control",
  "governed_property": "effect integrity",
  "mechanism": "postcondition",
  "applies_when": "a system claims a code change has been landed by updating a declared remote "
                  "version-control ref",
  "requirement": "A landing claim MUST identify the intended commit and the target remote ref, "
                 "and be verified from the remote boundary that the intended commit is reachable "
                 "from that exact ref.",
  "incident": "Three commits were created on a round branch while `git push origin main` pushed "
              "an unchanged main and exited zero. The landing claim named commits that were not "
              "present at the ref it named.",
  "cost": "Three commits were reported landed and were not. The record's central claim — that "
          "what is published is what was produced — was false for as long as nobody looked.",
  "verifier": "After the push, query the declared remote ref independently of the push's own "
              "output and reject unless the intended commit is reachable from that ref.",
  "observes": "the state of the remote ref, read back from the remote after the fact",
  "fixture": "Local HEAD is commit X on `round-020`; `main` and `origin/main` are at Y; "
             "`git push origin main` exits zero because there is nothing to update; the landing "
             "claim names X as landed on main. The verifier MUST reject.",
  "implementation": "tools/land.py — the branch precondition in preflight(), and the post-push "
                    "remote verification before the attestation is filed",
  "first_repair_failed": "Checking only for a detached HEAD, which left the exact path open — the "
                         "branch was not detached, it was simply not the one being pushed.",
  "boundary": "the remote ref's state can be read from a channel the subject does not write, and "
              "the credential used to read it is not one the subject can mint",
  "nonclaim": "It does not establish that every code-changing effect passes through version "
              "control; that the remote observer or its credentials are outside the subject's "
              "effective control; that the landed code is correct, safe, authorised or deployed; "
              "that an ASI could not bypass, alter or replace the boundary; or that the predicate "
              "remains adequate as capability increases. Completeness of effect coverage is not "
              "established, alignment is not addressed, and it has never been tested on an ASI."},

 {"slug": "publication-observed-at-the-serving-boundary",
  "title": "Publication observed at the serving boundary, not at the push",
  "control": 3,
  "incident_surface": "deployment",
  "governed_property": "effect integrity",
  "mechanism": "postcondition",
  "applies_when": "a system claims content is published by pushing it to a build that serves it",
  "requirement": "A publication claim MUST be verified by observing that the serving surface "
                 "returns the intended revision, not by observing that the push succeeded.",
  "incident": "Six consecutive Pages deploys failed. Each failure was attested honestly, and the "
              "next ordinary landing was permitted six times, because a successful push was "
              "being treated as publication.",
  "cost": "Eight commits went unpublished for three and a half hours while every gate stayed "
          "green, and the handoff written during that window recorded the outage as 'not "
          "observed'.",
  "verifier": "Poll the deployment API for the pushed revision and reject the publication claim "
              "unless the serving surface reports that exact revision deployed.",
  "observes": "the deployment API's report of which revision is being served",
  "fixture": "A push succeeds and the build fails. The tool MUST NOT report the site current, and "
             "MUST NOT permit the next ordinary landing until the obligation is discharged.",
  "implementation": "tools/land.py wait_for_deploy(), and tools/deploy_obligations.py, which "
                    "turns an observed failure into an obligation with a PENDING / SATISFIED / "
                    "INCIDENT state keyed on the attestation rather than on the commit",
  "first_repair_failed": "Keying the incident on the COMMIT, which made a repeat failure of the "
                         "same shape invisible; and a schema-less resolution file, into which "
                         "`{\"garbage\": true}` closed an open incident.",
  "boundary": "the serving surface reports its own state through a channel the publishing system "
              "does not write, and that report is fetched rather than inferred",
  "nonclaim": "It does not establish that the deployed bytes are the intended ones, only that the "
              "revision identifier matches; that the deployment API is honest or outside the "
              "subject's control; that readers reached the page; that an ASI could not bypass the "
              "observation or falsify the report; or that the check remains adequate as "
              "capability increases. It is not complete over publication effects — only the one "
              "surface it polls is observed — "
              "safety and alignment are not addressed, and it has never been tested on an ASI."},

 {"slug": "capability-probed-with-the-operation",
  "title": "A capability check must exercise the operation, not a weaker proxy",
  "control": 2,
  "incident_surface": "version control",
  "governed_property": "evidence",
  "mechanism": "precondition",
  "applies_when": "a system checks, before acting, that it will be able to complete the action",
  "requirement": "A pre-action capability check MUST exercise the same authority path as the "
                 "action it predicts.",
  "incident": "The tool committed twice with its token unset, failed at the push, and left the "
              "commits local while the harness reported the task complete with exit zero. The "
              "repair added a reachability probe — `git ls-remote` — which passed with no "
              "credentials at all, because the repository is public.",
  "cost": "Two commits stranded locally and reported as landed; and then a check that tested "
          "reachability while claiming to test push capability, written INSIDE the fix for that "
          "exact class of error.",
  "verifier": "Run the check with the credential removed and require it to fail — the negative "
              "control is what shows the authority path was exercised rather than a weaker one. "
              "A dry-run push exercises the credential helper and fails the way a real push "
              "would; an anonymous read does not.",
  "observes": "whether the authenticated write path completes, with the credential withdrawn",
  "fixture": "Unset the token and run the check. It MUST refuse. If it passes, the check is "
             "measuring reachability rather than authority.",
  "implementation": "tools/land.py preflight() — `git push --dry-run`, with the negative control "
                    "in tools/tests/test_gate_negative_controls.py",
  "first_repair_failed": "`git ls-remote`, which passed with no credentials because the "
                         "repository is public — a green signal not downstream of what it "
                         "certified, inside the fix for that same class.",
  "boundary": "the credential path exercised by the probe is the same one the action uses, and "
              "the probe cannot be satisfied by an unauthenticated route",
  "nonclaim": "It does not establish that the action will succeed, only that this authority is "
              "present now; that the credential belongs to whom it should; that no other route "
              "to the effect exists; that an ASI could not mint or bypass the credential; or that "
              "the probe stays representative as capability increases. Completeness over all "
              "authority paths is not established, safety and alignment are not addressed, and it "
              "has never been tested on an ASI."},

 {"slug": "status-read-from-the-subject",
  "title": "An assurance signal must come from the thing it certifies",
  "control": 10,
  "incident_surface": "measurement",
  "governed_property": "evidence",
  "mechanism": "postcondition",
  "applies_when": "a system records that a check or suite passed",
  "requirement": "A pass claim MUST name the subject that was run and carry that subject's own "
                 "exit status, captured directly rather than parsed from any downstream text.",
  "incident": "`run_all.py | tail -2` printed 'All 16 suites passed' — from an INNER suite — "
              "while the runner itself exited 1. Separately, `echo \"$(basename $f) rc=$?\"` "
              "reported basename's status, and two red suites were pushed under it.",
  "cost": "Two failing suites were pushed as passing, and the same shape recurred after the rule "
          "against it was written down, because a written rule is not a check.",
  "verifier": "Refuse an attestation whose status is sourced from anything but the subject's own "
              "process exit, and refuse one that names no subject.",
  "observes": "the exit status of the subject process itself, and the identity of that subject",
  "fixture": "An attestation claiming a pass with `status_from: basename`, and one claiming a "
             "pass with exit_status 1. Both MUST be refused, and both refusals MUST be logged.",
  "implementation": "tools/executive_log.py — the `test` attestation profile, exercised by "
                    "tools/tests/test_executive_log.py",
  "first_repair_failed": "Writing the rule into the standing instructions file. It was there, in "
                         "those words, when the `tail -2` failure happened again.",
  "boundary": "the subject's exit status is captured by the caller that launched it, and no "
              "intermediate process can substitute its own",
  "nonclaim": "It does not establish that the suite tests anything, that a zero exit means the "
              "code is correct, or that the subject named is the subject that ran. Nothing here is "
              "bypass-resistant: a caller that never attests is unaffected. It does not address "
              "whether an ASI could arrange for a passing subject to be run in place of the "
              "intended one, and gives no guarantee as capability increases. Completeness "
              "over all assurance signals is not established, safety and alignment are not "
              "addressed, and it has never been tested on an ASI."},

 {"slug": "closed-world-survey",
  "title": "A population measurement refuses rather than reporting a partial scan",
  "control": 5,
  "incident_surface": "measurement",
  "governed_property": "evidence",
  "mechanism": "precondition",
  "applies_when": "a system reports a figure derived from scanning a set of artifacts",
  "requirement": "A measurement over a population MUST reach a terminal state for every declared "
                 "member, or emit no figure at all.",
  "incident": "A scan iterated each raw file's `samples` array; 69 of the files use `responses` "
              "or `failures` instead, so it returned zero for their entire contents. The figure "
              "it produced — '0 searches across 83 tool calls' — was published, and a "
              "recommendation to delete a working tool was argued from it.",
  "cost": "A self-deletion argued from a wrong number, which Codex rejected. The record's note on "
          "it: a self-deletion argued from a wrong number is worth less than a refusal to delete, "
          "because it is harder to audit.",
  "verifier": "Require every declared member to reach exactly one terminal state — accounted, "
              "excluded, unreadable or unregistered — and raise rather than return when any "
              "member has none.",
  "observes": "the per-member terminal states of the whole declared population",
  "fixture": "Inject one unreadable file into the population and require the tool to render no "
             "count at all. A tool that prints a count with a warning has failed this.",
  "implementation": "tools/closed_world.py Survey, with tools/derive_counts.py and "
                    "tools/scan_own_code.py routed through it",
  "first_repair_failed": "The type itself. Its first version returned results for four incoherent "
                         "walks, and both tools routed through it still printed the counts the "
                         "guard was meant to withhold — filed as D-60.",
  "boundary": "the population is enumerable in advance from a source the measuring system does "
              "not itself generate",
  "nonclaim": "It does not establish that the declared population is the right one, that an "
              "artifact parsed under a registered schema was understood, or that a refusal is "
              "noticed. A member nobody listed is not measured and not missed, which is the "
              "bypass: declaring a smaller population satisfies the check. It does not "
              "address whether an ASI could shape the declared population, and offers no "
              "guarantee as capability increases; completeness rests on the declaration itself, "
              "safety and alignment are not addressed, and it has never been tested on an ASI."},

 {"slug": "refusal-proved-at-the-effect-boundary",
  "title": "A refusal fixture asserts over the effects, not the message",
  "control": 64,
  "incident_surface": "CI",
  "governed_property": "evidence",
  "mechanism": "postcondition",
  "applies_when": "a check is claimed to refuse a condition",
  "requirement": "A fixture asserting that a tool refuses MUST assert over the tool's governed "
                 "effects after the refusal, not over its exit status or its output alone.",
  "incident": "A negative control asserted that no cost was printed when an unregistered cohort "
              "was priced, and passed — while the same runs appended 87 rows to the spend ledger "
              "it existed to protect.",
  "cost": "The ledger this project's funding is reported from was corrupted 87 times by the test "
          "written to protect it, and the test reported success each time.",
  "verifier": "After the refusal, assert that the governed effect did not occur — the ledger is "
              "byte-identical, or the sentinel the admitted path would have written is absent.",
  "fixture": "A tool that exits non-zero, prints a refusal, and performs the effect anyway. The "
             "fixture MUST fail.",
  "observes": "the state of the artifacts the tool is permitted to write, after the refusal",
  "implementation": "tools/tests/test_gate_negative_controls.py RS-01, and the ten sentinel "
                    "fixtures in tools/tests/test_lease_bounds.py",
  "first_repair_failed": "The lease's own version of this. Its refusal fixtures asserted the "
                         "exception type, and Codex's reply to the sentinel design still holds: "
                         "absence of the sentinel mostly proves ordinary Python sequencing.",
  "boundary": "the tool's permitted write set is declared by someone other than the tool, and the "
              "fixture can observe every member of it",
  "nonclaim": "It does not establish that a declared write set is complete — the party declaring "
              "what a tool may write is the party whose tool writes it, and a harness proves "
              "nothing about a file nobody listed — which is also the bypass, since an effect "
              "outside the declared set is unobserved rather than forbidden. It does not "
              "establish that the fixture exercises a real caller's catches or its subprocess "
              "effects, does not address whether an ASI could act outside that set, and offers "
              "no guarantee as "
              "capability increases. Safety and alignment are not addressed and it has never "
              "been tested on an ASI."},
]


#  The honest half. Each of these was considered and kept out by the rule above.
REFUSED_MEMBERS: list[dict] = [
 {"proposed": "The deployment obligation interlock as its own member",
  "control": 23,
  "why": "SI-01. Control 23 is below the eligibility line: it has a recorded failure but not the "
         "full kit — no independent verifier and no rejection fixture registered against the "
         "control itself. The mechanism appears here only as the VERIFIER of an eligible control "
         "(3), which is the correct weight for it."},
 {"proposed": "Guard identity — removing a check is a governed event",
  "control": 45,
  "why": "SI-01, same bar. It is one of this project's better pieces of work and it is not an "
         "eligible control, so it does not get a member. Recording that refusal is more useful "
         "than the member would have been."},
 {"proposed": "The fail-closed authorization lease",
  "control": 4,
  "why": "The incident supports only an adjacent control. Control 4 requires a token that is NOT "
         "self-issued; this project's lease is granted by the custodian to their own agent, "
         "checks neither token subject, resource scope, nonce nor revocation, and until "
         "2026-08-12 failed open on an unreadable count (D-64). Admitting it would claim an "
         "instance of a control the implementation does not satisfy."},
 {"proposed": "`land.py` as a 'programmatic commit gate' control",
  "control": None,
  "why": "It is a composition, not a primitive. It implements or instantiates controls 2, 3, 5, "
         "10, 23, 45 and 64 in specified places; converting the bundle into one control would "
         "bundle several predicates under a tool name, which the rule refuses. The composition "
         "map below says what it instantiates without claiming to be a new requirement."},
]


COMPOSITION = {
 "tool": "tools/land.py",
 "what": "The only sanctioned way to declare work done: runs every gate, commits, pushes, "
         "verifies the remote ref, waits for the deploy, and attests.",
 "instantiates": [
   (2, "every gate it runs must itself carry a negative control; the coverage is measured by "
       "tools/control_coverage.py and is not complete"),
   (3, "the remote-ref verification and the deploy observation, both read back from outside"),
   (5, "the gates it runs render nothing when their population is incompletely surveyed"),
   (10, "the two attestations it files name the subject, the exit status and its source"),
   (23, "the interlock: an undischarged deployment obligation refuses the next ordinary landing"),
   (45, "the guard-identity gate: removing a named guard is refused unless recorded"),
   (64, "the refusal fixtures for its own gates assert over effects, partially"),
 ],
 "bypass": "Stated in its own source: nothing here binds a shell command, a direct `git push`, or "
           "an edit made without going through a tool that checks. There is no universal "
           "chokepoint, and the first implementation reproduced several of the failures it was "
           "built to prevent.",
}


def register() -> dict[int, dict]:
    spec = importlib.util.spec_from_file_location(
        "bcp_for_si", REPO_ROOT / "tools" / "build_controls_page.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {c["rank"]: c for c in module.CONTROLS}


def prerequisite(control: dict) -> str:
    if control.get("requires_second_party"):
        return "needs a second party"
    if control.get("requires_goal_graph"):
        return "needs a goal or plan graph"
    return "adopt without a second party"


def problems() -> list[str]:
    """Every refusal the admission rule can make mechanically.

    The rule as Codex wrote it has judgement in it — "its incident supports only an adjacent
    control" cannot be computed. What is computable is checked here; what is not is recorded in
    REFUSED_MEMBERS by hand and labelled as a hand judgement, rather than being quietly dropped.
    """
    out: list[str] = []
    controls = register()
    required = ("title", "control", "applies_when", "requirement", "incident", "cost",
                "verifier", "observes", "fixture", "implementation", "boundary", "nonclaim")

    for member in MEMBERS:
        name = member.get("slug") or member.get("title") or "(unnamed)"
        rank = member.get("control")
        control = controls.get(rank)

        if control is None or not control.get("eligible", True):
            out.append(guard("SI-01", f"{name} references control {rank}, which is not an "
                                      f"eligible canonical control. A view over the register may "
                                      f"not admit what the register has not."))
            continue

        missing = [f for f in required if not str(member.get(f, "")).strip()]
        if missing:
            out.append(guard("SI-02", f"{name} is missing {', '.join(missing)}. A member with a "
                                      f"blank field is not distinguishable from one whose author "
                                      f"had nothing to put there."))

        musts = str(member.get("requirement", "")).count("MUST")
        if musts != 1:
            out.append(guard("SI-03", f"{name} states {musts} MUSTs in one requirement. Several "
                                      f"predicates bundled under one name is how a tool becomes "
                                      f"a control it has not earned."))

        evidence = " ".join(str(member.get(f, "")) for f in
                            ("incident", "cost", "requirement", "verifier")).lower()
        hits = [p for p in CONSENSUS_PHRASES if p in evidence]
        if hits:
            out.append(guard("SI-04", f"{name} offers consensus as evidence ({', '.join(hits)}). "
                                      f"This register's discipline is that a control earns its "
                                      f"place from a recorded failure with a cost."))

        everything = " ".join(str(v) for v in member.values()).lower()
        categorical = [p for p in CATEGORICAL_PHRASES if p in everything]
        if categorical:
            out.append(guard("SI-05", f"{name} states applicability categorically "
                                      f"({', '.join(categorical)}). Transfer is a hypothesis with "
                                      f"a boundary condition; an assertion cannot be false."))

        nonclaim = str(member.get("nonclaim", "")).lower()
        uncovered = [topic for topic, words in NONCLAIM_TOPICS.items()
                     if not any(w in nonclaim for w in words)]
        if uncovered:
            out.append(guard("SI-06", f"{name}'s nonclaim does not cover {', '.join(uncovered)}. "
                                      f"All six are required because 'what this does not "
                                      f"establish' without a checklist becomes one sentence "
                                      f"about scope."))

        if len(str(member.get("nonclaim", ""))) < len(str(member.get("requirement", ""))):
            out.append(guard("SI-07", f"{name}'s nonclaim is shorter than its requirement. The "
                                      f"standing rule is comparable prominence, and a two-line "
                                      f"disclaimer under a paragraph of claim is not that."))

        observes = str(member.get("observes", "")).lower()
        if observes and any(s in observes for s in SUBJECT_SIGNAL_ONLY) and \
                not any(w in observes for w in ("state", "ledger", "ref", "artifact", "api",
                                                "boundary", "population", "identity")):
            out.append(guard("SI-08", f"{name}'s verifier observes only a signal the subject "
                                      f"produces ({member.get('observes')}). That is the failure "
                                      f"mode control 64 exists for."))
    return out


def markdown() -> str:
    controls = register()
    lines: list[str] = []
    add = lines.append

    add("# Software implementations and transfer hypotheses")
    add("")
    add("*A companion view over the candidate control register. Generated by "
        "`tools/software_implementations.py`; the canonical register is "
        "`tools/build_controls_page.py` and nothing here changes it.*")
    add("")
    add("**The one question this view answers:** which admitted controls have executable "
        "implementations or incident instances an ordinary software team can reproduce now.")
    add("")
    add("**The question it is refused:** which controls are best practice for an ASI. Every "
        "member carries a transfer *hypothesis* with the boundary condition it depends on, and a "
        "nonclaim at least as long as its requirement. Nothing here has been tested on an ASI, "
        "and the admission rule refuses a member that says otherwise.")
    add("")
    add("**Appearing here confers nothing.** Rank, status and prerequisite are read from the "
        "register at render time. Every control in the register is still `ELIGIBLE` — attacked "
        "by nobody, independently implemented by nobody.")
    add("")
    add(f"{len(MEMBERS)} member(s); {len(REFUSED_MEMBERS)} proposal(s) refused by the rule.")
    add("")

    add("## What was refused, and why")
    add("")
    add("Read this before the members. The admission rule's first clause refuses two of this "
        "project's better mechanisms because the controls they implement are below the register's "
        "eligibility line, and refuses its own lease because the implementation does not satisfy "
        "the control it would claim.")
    add("")
    add("| Proposed | Control | Refused because |")
    add("|---|---|---|")
    for refused in REFUSED_MEMBERS:
        rank = refused["control"]
        label = f"{rank}" if rank else "—"
        add(f"| {refused['proposed']} | {label} | {refused['why']} |")
    add("")

    add("## Members")
    add("")
    for member in MEMBERS:
        control = controls[member["control"]]
        add(f"### {member['title']}")
        add("")
        add(f"**Canonical identity:** implementation instance of control "
            f"{control['rank']} — *{control['name']}*. No new rank; status `ELIGIBLE`, unchanged "
            f"by appearing here; prerequisite *{prerequisite(control)}*.")
        add("")
        add(f"**Incident surface:** {member['incident_surface']} · **governed property:** "
            f"{member['governed_property']} · **mechanism:** {member['mechanism']}")
        add("")
        add(f"**Applies when:** {member['applies_when']}.")
        add("")
        add(f"**Requirement:** {member['requirement']}")
        add("")
        add(f"**Named failure:** {member['incident']}")
        add("")
        add(f"**Cost:** {member['cost']}")
        add("")
        add(f"**Verifier:** {member['verifier']} It observes {member['observes']}.")
        add("")
        add(f"**Rejection fixture:** {member['fixture']}")
        add("")
        add(f"**Implementation here:** {member['implementation']}")
        add("")
        add(f"**The first repair that failed:** {member['first_repair_failed']}")
        add("")
        add(f"**Transfer hypothesis, not ASI evidence:** this control is architecturally "
            f"applicable to a software system, irrespective of its claimed capability, when "
            f"{member['boundary']}. It has not been tested on an ASI.")
        add("")
        add(f"**What this does not establish:** {member['nonclaim']}")
        add("")

    add("## Composition map")
    add("")
    add(f"`{COMPOSITION['tool']}` — {COMPOSITION['what']}")
    add("")
    add("It is **not** a control. It instantiates these, in specified places:")
    add("")
    add("| Control | Where |")
    add("|---|---|")
    for rank, where in COMPOSITION["instantiates"]:
        control = controls[rank]
        add(f"| {rank} — {control['name']} | {where} |")
    add("")
    add(f"**What it does not bind:** {COMPOSITION['bypass']}")
    add("")

    add("## The admission rule")
    add("")
    add("A member is admitted only if it references a canonical control that independently meets "
        "the register's eligibility bar; cites a specific recorded software-lifecycle incident "
        "and its cost; identifies one executable requirement, its verifier and a must-reject "
        "fixture; preserves the control's prerequisite and status; states the enforcement and "
        "observation boundary its transfer depends on; and gives an equally prominent nonclaim "
        "covering ASI non-testing, bypass, capability increase, completeness, safety and "
        "alignment. Inclusion confers no rank or status.")
    add("")
    add("A member is refused if consensus or *best practice* is offered as evidence; if several "
        "predicates are bundled under a tool name; if its incident supports only an adjacent "
        "control; if it duplicates a control without a discriminating fixture; if its ASI "
        "applicability is categorical; or if its verifier reads only a signal the subject "
        "produces rather than the governed effect.")
    add("")
    add("Eight of those clauses are enforced mechanically as guards SI-01 … SI-08, with fixtures "
        "in `tools/tests/test_software_implementations.py`. **Two are not computable** — whether "
        "an incident supports the control rather than an adjacent one, and whether a fixture "
        "discriminates — and those are hand judgements, recorded above rather than dropped.")
    add("")
    add("## What this does not establish")
    add("")
    add("* That any implementation is correct, complete or non-bypassable. `land.py` records in "
        "its own source that a shell-level bypass remains, and several members' first repairs "
        "failed in the same way they were built to prevent.")
    add("* That an incident establishes its control at full breadth. It establishes the narrow "
        "predicate the fixture tests.")
    add("* That an implementer gains anything a CI handbook lacks, except the four things a "
        "handbook does not carry: the exact incident, the predicate that would have rejected it, "
        "the failed first repair, and what remains bypassable.")
    add("* That grouping these controls says anything about ASI. Codex's warning, kept because it "
        "is the reason this is a view and not a section: *\"'Engineering-derived' can launder "
        "evidence almost as easily as 'best practice'.\"*")
    return "\n".join(lines) + "\n"


def publish() -> list[str]:
    import build_round_pages as b                                        # noqa: PLC0415
    md = markdown()
    VIEW.parent.mkdir(parents=True, exist_ok=True)
    VIEW.write_text(md, encoding="utf-8")
    (DOCS / "artifacts").mkdir(parents=True, exist_ok=True)
    (DOCS / "artifacts" / "software-implementations.md").write_text(md, encoding="utf-8")
    (DOCS / "software-implementations.html").write_text(
        b.md_to_html(md, "Software implementations and transfer hypotheses — OAGF",
                     alternate="artifacts/software-implementations.md"), encoding="utf-8")
    return ["record/controls/software-implementations.md",
            "docs/software-implementations.html",
            "docs/artifacts/software-implementations.md"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true", help="refuse a member the rule rejects")
    parser.add_argument("--write", action="store_true", help="regenerate the file and the page")
    args = parser.parse_args()

    found = problems()
    if args.check:
        for problem in found:
            print(f"  {problem}")
        print(f"\n  {len(MEMBERS)} member(s), {len(REFUSED_MEMBERS)} refused by hand, "
              f"{len(found)} mechanical refusal(s).")
        return 1 if found else 0

    if found:
        #  Publishing a view whose own admission rule refuses a member would be the register's
        #  false-absence failure again, one level out.
        print("REFUSED: the admission rule rejects a member; nothing was written.",
              file=sys.stderr)
        for problem in found:
            print(f"  {problem}", file=sys.stderr)
        return 1

    if args.write:
        for path in publish():
            print(f"  wrote {path}")
        return 0

    print(markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
