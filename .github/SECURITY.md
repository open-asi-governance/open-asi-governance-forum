# Security

This repository is a public record and a small set of deterministic Python tools that maintain it.
It runs no service, holds no user data, and gates no system. Its security surface is correspondingly
narrow, and this document tries to say what it actually is rather than to claim a posture.

## Reporting

Open an issue, or email the custodian, **Stephen Reed** — `stephenreed@yahoo.com`.

There is one person here. There is no on-call rotation and no response-time commitment, and saying
otherwise would be the kind of overclaim this project exists to avoid. Attribution corrections are
answered fastest, per `CONTRIBUTING.md`.

If a report would be hazardous to publish, say so in the first line and send it by email rather than
opening an issue.

## What is in scope

**Integrity of the record** is the real security property here, and it has already failed once:

- A defect that lets raw material be altered without the build detecting it. `corpus/raw/` is
  immutable, hash-anchored in `corpus/MANIFEST.sha256`, and verified by `tools/rebuild.py`.
  **On 2026-08-06 that verification did not run** — the maintenance path rewrote the manifest from
  disk before anything read it, so the anchor certified whatever was on disk. See **D-29**, which
  records the reproduction. A further review found that deleting a manifest line made its file look
  *new* rather than *modified*. Both are fixed and both are now regression-tested. **Reports of
  further paths of this kind are the most valuable thing you can send.**
- A defect that lets the published page differ from what the generator produces from verified
  inputs. CI regenerates on a clean checkout and compares byte for byte.
- A provenance record that can be made to assert something the underlying artifact does not support.
- Anything that would let an unsigned or unattributed contribution enter the corpus as attributed.

**The tooling**, to the extent it processes untrusted input: `tools/capture_response.py` ingests
model output that may be adversarial, and `tools/build_viewer.py` embeds corpus text into HTML.
Escaping defects there are in scope.

**The published site** is static, self-contained, and makes no external requests by design.

## What is out of scope, deliberately

**Hazardous technical content is scoped out rather than governed.** This project does not publish,
and asks you not to submit:

- exploitable vulnerability details or working exploit code
- biological, chemical, or nuclear weaponization procedures
- model-weight exfiltration pathways
- specific instructions for circumventing containment or safety controls
- private personal data or authentication secrets

This is not a claim of authority over such material. It is the opposite. **A single operator is not
credible independent oversight of a withholding decision**, so rather than assert a review process it
does not have, the project declines the category. Where something is withheld, the repository records
*that* it was withheld, the reason, the scope, the custodian, and a review date, and publishes the
maximum safe abstraction. Silent omission is not withholding.

## What this project does not secure

It does not approve deployments, gate releases, certify systems, or hold seats. **No text here is a
technical control.** A model-generated statement in this corpus does not constrain any system, and a
specification with no implementation constrains nothing at all — no ASP-attested agent exists
anywhere.

If you are looking for the security-relevant weakness in this project, it is not a vulnerability
class. It is disclosed in `GOVERNANCE.md` §1.2: **single-operator custody.** One person holds
repository administration, merge authority, and license authority, and that is an anti-capture
weakness for as long as it lasts. It is disclosed rather than mitigated.

## Cryptographic signing

There is none. `corpus/deficiencies.md` **D-13** records that a `signatures` field exists in the
adopted schema while no cryptographic signature exists anywhere in the repository. Commits are
unsigned.

Treat every attribution here as **unauthenticated**: the corpus records what the custodian states
was produced by a given model in a given session, and **D-18** records that this is unverified
throughout. Signing is intended and not done.
