#!/usr/bin/env python3
"""Regenerate every derived artifact, in dependency order, and verify as it goes.

Run this after any change to the corpus. It is the whole maintenance path:

    python3 tools/rebuild.py

Order matters:

  1. manifest    — VERIFY raw material against the recorded hashes, first, so a
                   tampered artifact stops the build before anything is derived from it
  2. validate    — refuse to build anything from artifacts that fail provenance checks
  3. index       — corpus/index.md from segments.json
  4. viewer      — docs/index.html, the threaded page served by GitHub Pages
  5. capture     — docs/capture/index.html, the prompt-transport page
  6. budget      — every published page must fit the reviewer's context

Step 1 VERIFIES. It does not write. Until 2026-08-06 it wrote, which meant the
maintenance path re-anchored tampered raw material and reported success — see
deficiency D-29. New raw material is anchored deliberately, outside this path:

    python3 tools/build_manifest.py corpus/raw/ --add

so that adding material and altering material are different operations that a
reader can tell apart in the diff.

Supplied-context bundles are deliberately NOT rebuilt here. A bundle records what
a reviewer was shown; once a round has used it, capture records cite it by hash,
so regenerating it would silently invalidate those citations. Build one per round
with `tools/build_bundle.py <round>`, which refuses to overwrite an existing file.

Every step is deterministic. Rerunning on an unchanged repository produces
byte-identical output, so `git status` after a rebuild is a real signal: it means
something upstream actually changed.

Exit status is non-zero if any step fails, and the build stops there rather than
publishing a page derived from artifacts that did not validate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("verify raw material against the manifest", ["tools/build_manifest.py", "corpus/raw/"]),
    # Added 2026-08-07. The manifest establishes that raw material has not changed
    # SINCE THE OPERATOR RECORDED IT -- by a hash the operator also controls. Four
    # parties, unprompted, named that circularity as the thing they would need broken.
    # This step fails when the CURRENT manifest has no anchor: an anchor covering a
    # superseded state while the live one drifts is a control that has quietly stopped
    # measuring, which is the failure shape this repository keeps rediscovering.
    ("check the manifest is externally anchored", ["tools/anchor_manifest.py"]),
    ("validate provenance", ["tools/validate_provenance.py", "corpus/"]),
    # Added 2026-08-07, after D-53: this project's own annotator quoted a party saying
    # things the party never said, twice, in documents that shaped a build. Every other
    # control here governs corpus/; prose that QUOTES the corpus was checked by nothing.
    # Wired into the build rather than left as a script, because D-33 was a generator
    # documented as part of the build that was not part of the build.
    ("check quotations attributed to parties", ["tools/check_quotations.py"]),
    ("check the deficiency register against its classification", ["tools/check_register.py"]),
    ("build the deficiency register views", ["tools/build_register_view.py"]),
    ("build the local solicitation round pages", ["tools/build_local_rounds.py"]),
    # Added 2026-08-07. Nine deliberation rounds were merged and none was published --
    # the same failure build_local_rounds.py was written for, one artifact class over.
    # Runs BEFORE the viewer, which owns the sitemap and llms.txt and needs these routes.
    ("publish the deliberation rounds", ["tools/build_round_pages.py"]),
    # Added 2026-08-07, in the SAME motion that first published a cohort. A generator
    # missing from this list is not merely unrun: CI deletes docs/ and regenerates it,
    # so an unlisted generator's output is deleted and never rebuilt, and the run fails
    # on files that "differ from a clean regeneration". That is how it should fail --
    # but the pages it publishes were reachable from the rounds index the moment they
    # were committed, so the window between committing and listing is a window in which
    # the site links to pages the build does not produce.
    ("publish the proposal cohorts", ["tools/build_cohort_pages.py"]),
    ("render corpus index", ["tools/render_markdown.py", "corpus/artifacts/segments.json", "corpus/index.md"]),
    #  Before the viewer, which owns the sitemap and llms.txt and needs this route.
    ("publish the candidate control register", ["tools/build_controls_page.py"]),
    #  KEPT CURRENT BY THE BUILD, not by remembering. The table names code files and tests, and
    #  a renamed or deleted path silently turns a compliance row into a lie -- which is the
    #  failure mode of every hand-maintained matrix. Regenerating here means the file, the page
    #  and the repository cannot disagree, and --write refuses before writing anything if a
    #  named path is gone.
    ("publish the control-application table", ["tools/control_application.py", "--write"]),
    #  MUST run before the viewer, which owns the pruner: a page the rebuild does not
    #  produce is a page the pruner deletes, and the landing page then links to nothing.
    ("publish the software-implementation view",
     ["tools/software_implementations.py", "--write"]),
    ("publish the implementation challenge", ["tools/build_challenge_page.py"]),
    ("build threaded viewer", ["tools/build_viewer.py"]),
    # Added 2026-08-06. The T-13 design already claimed this: "deterministic, added
    # to rebuild.py's step list, no diff on an unchanged tree (A10)". It was not in
    # the list, so docs/capture/index.html was published without ever being derived
    # by the maintenance path -- and the CI byte-equality check passed vacuously for
    # it, because nothing regenerated it to compare against.
    #
    # Caught when it fired for real: editing record/review-round-03-prompt.md left
    # the committed capture page embedding the OLD prompt text under a prompt_sha256
    # of b3894067..., while the file it names hashed to e394c3d3.... rebuild.py
    # exited 0 and CI passed. A published instrument carried a hash that did not
    # match the artifact it anchored -- in the page whose entire job is to transport
    # prompts to frontier parties with their hashes. See D-33.
    # Before anything is built from them. A prompt is the one artifact whose defect
    # cannot be repaired after it is sent -- D-36 -- so it is checked while it is
    # still editable.
    ("check solicitation prompts against known defects", ["tools/check_prompt.py"]),
    ("build the prediction registry view", ["tools/build_predictions_view.py"]),
    ("build capture page", ["tools/build_capture_ui.py"]),
    # LAST, and site-wide. Checking inside any one generator would miss the pages the
    # others write -- and the two pages that had already breached the ceiling were
    # written by a DIFFERENT generator than the one whose page the requirement was
    # written about. T-03 set "no page exceeds ~20,000 tokens" and nothing enforced
    # it, so it drifted: the register went from ~14,300 to ~19,000 estimated tokens
    # in six commits in one day and crossed while nobody was counting.
    ("check every published page against the token budget", ["tools/check_page_budget.py"]),
]


def main() -> int:
    for label, argv in STEPS:
        print(f"\n\033[1m▸ {label}\033[0m")
        result = subprocess.run([sys.executable, *argv], cwd=REPO_ROOT)
        if result.returncode != 0:
            print(f"\n\033[31mFAILED at: {label}\033[0m", file=sys.stderr)
            print("Nothing downstream was rebuilt. Fix the failure and rerun.", file=sys.stderr)
            return result.returncode

    print("\n\033[32mAll artifacts rebuilt and verified.\033[0m")
    print("Review `git status` — an unchanged repository should produce no diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
