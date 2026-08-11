# What this repository may publish about an implementer — draft

**Status: DRAFT, NOT ADOPTED.** Written 2026-08-10 after the workbench published four unfixed
defects in a private codebase, with source, file paths and configuration keys, to a public
repository — because no rule said not to.

---

## The gap

`spec/icp/icp-v0.1.md` §3.3 states what an **implementer may never do**. Nothing anywhere states
what **this repository may publish about an implementer**. That asymmetry went unnoticed until it
was exercised.

The comparison that makes it concrete: Consullo's own submission,
`record/submissions/AS-2026-08-06-consullo-enterprise-layer.md`, names **no internal file and no
configuration key**. It describes its failure as *"a production inference service"* whose *"health
check issued a greedy request."* The implementer disclosed with discipline. The workbench then
published, about the same system, a level of detail the implementer had never chosen — and did so
in a commit whose own message described the work as careful.

**Nothing was leaked that mattered**: no credentials, no customer data, no absolute paths. That is
luck and habit, not a control.

## Why this blocks the roadmap, not just this incident

`record/designs/roadmap-2026-08.md` proposes an implementation challenge: put NCP in front of
outside engineers and ask them to apply it. **No commercial lab will let this repository assess
their code and publish the result without a rule about what gets published.** "We will be careful"
is not a rule, and this repository has just demonstrated why.

The workstream that most needs external adopters is therefore gated on a policy that does not
exist.

## Proposed rule

**The implementer controls disclosure about their own system. The forum controls disclosure about
its own methods and findings.**

1. **Default abstract.** An assessment publishes outcomes, perturbations and reasoning by ROLE —
   "a port-liveness probe", "a component-health aggregator". Files, classes, configuration keys
   and source are named only with the implementer's explicit consent.
2. **The implementer may always be named** if they have already published under their own name.
   Concealing an identity the implementer has disclosed is incoherent, and pretending an
   assessment is anonymous when one submission identifies it is worse than naming it.
3. **Unfixed defects are held.** Detail sufficient to exploit or reproduce an unfixed defect is
   not published until it is fixed, or until the implementer releases it. Abstract outcomes may be
   published immediately — *"four of five checks survived their negative controls"* discloses
   nothing exploitable.
4. **Remediation requests live with the implementer**, never in the forum record. They are work
   orders with paths and code, and they carry no evidentiary value to anyone else.
5. **Reproductions are published abstractly.** The negative controls are the transferable part;
   they reproduce a *shape* and need not name anyone's code to do it.
6. **Abstraction is declared, not silent.** Any abstracted artifact says it was abstracted, what
   class of detail was removed, and that **git history retains the prior version** — because it
   does, and a redaction note that implies otherwise is a false assurance of exactly the kind this
   project keeps finding.

## What this rule costs

**Reproducibility.** An abstracted finding cannot be independently checked against the codebase it
describes. A reader must take the outcome on the forum's word — which is precisely the kind of
unverifiable claim the record elsewhere refuses to accept. That is a real loss and this rule
accepts it.

The mitigation is partial: the *reproductions* stay concrete and runnable, so the method is
checkable even when the subject is not. Anyone can run the negative controls against their own
system and see whether the class holds. What they cannot do is verify the Consullo numbers.

## What it does not solve

* **The forum is the assessor, the publisher and the beneficiary of the result.** A rule about
  what it publishes does not change who decides. An implementer's only real protection is that
  they can refuse to submit.
* **Consent from a solo operator assessing his own system is not consent.** Today's implementer
  and today's custodian are the same person, so rule 1's "explicit consent" is currently
  self-granted and worth nothing as a control. It becomes meaningful only with an external
  implementer.
* **History is not reachable.** Rule 6 discloses this rather than fixing it.

## Standing authorization for mining, granted 2026-08-10

**The custodian has granted standing authorization to mine confidentially-marked implementer
documents and publish the resulting controls in abstracted form, without seeking approval per
source.** It was granted after three batches had been approved individually, on the workbench's
own request, because the alternative was six further interruptions across a queue of documents all
carrying the same marking.

What it changes: the workbench no longer stops between sources.

What it does not change, and this is the whole of it:

* **Abstraction remains the default and the marking remains irrelevant to it.** Absence of a
  confidentiality notice is still not permission.
* **The rules above are unaltered.** This authorises the *asking*, not the *standard*.
* **The custodian and the implementer are the same person.** So this is self-granted, like rule
  1's consent, and worth the same as a control: nothing. It is recorded because an authorization
  that is not written down is one the workbench assumed, and the difference between those two is
  not visible afterwards.
* **It is revocable and it is not a precedent for anything else.** It covers mining for the
  candidate-control register. No other publication inherits it.

The failure this creates: the workbench can now publish abstracted material from a confidential
source without a human reading the abstraction first. The abstraction is checked by the same layer
that wrote it — the arrangement control 6 exists to forbid. Nothing here mitigates that, and the
custodian accepted it knowingly to keep the queue moving.

## Status

Not adopted. It is the custodian's decision whether this becomes a normative section of ICP, and
whether it should be put to the model panel — noting that the panel has no stake in an
implementer's confidentiality and that its assent would be, as ever, cheap.
