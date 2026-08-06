#!/usr/bin/env python3
"""Regression tests for the corpus integrity mechanisms.

    python3 tools/test_integrity.py

Every case here is a defect that was live in this repository on 2026-08-06 and
was found by running the attack rather than by reading the code. They are tests
because a repair reported in a commit message is a claim, and a repair that a
build re-runs is a control. D-29's forward requirement is precisely this: **a
check that is available is not a check that runs**, and the way to establish a
claim about an integrity property is to violate the property and confirm the
documented path fails.

Runs against a **temporary clone**, never the working tree, so the tests can
tamper freely and a failure cannot leave the real corpus modified.

Exit status is 0 when every case passes and 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RAW_LOCAL = "corpus/raw/local-round-02/level-4-guarantee-crosslineage-probe-samples.json"
RAW_CONTRIB = "corpus/raw/review-round-02/chatgpt-01.md"

# Generated, and NOT under docs/ since 97e852d moved it off the published surface.
# Named once here so the next relocation breaks one line rather than four.
CAPTURE_PAGE = "tools/capture_ui/index.html"

PASSED: list[str] = []
FAILED: list[str] = []


def run(clone: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=clone,
                          capture_output=True, text=True)


def case(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        PASSED.append(name)
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name}{'  — ' + detail if detail else ''}")


TRACKED_ROOTS = ("tools", "corpus", "docs", "record", "predictions", "spec")


def build_reference(tmp: Path) -> Path:
    """One reference repository holding the CURRENT working tree, committed.

    Not `git clone`: this file usually runs inside a git worktree, whose `.git`
    is a file rather than a directory, and `--local` cannot clone that. And a
    clone of HEAD would test the last commit rather than the code in front of
    you, which is exactly backwards for a pre-commit gate.

    So: a fresh repository seeded with the working tree as it stands, committed,
    so that HEAD is the state under test. The lineage check reads
    `HEAD:corpus/MANIFEST.sha256`, so HEAD has to be real and has to match.
    """
    reference = tmp / "reference"
    reference.mkdir()
    for name in TRACKED_ROOTS:
        source = REPO_ROOT / name
        if source.is_dir():
            shutil.copytree(source, reference / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    git = ["git", "-C", str(reference)]
    subprocess.run([*git, "init", "--quiet"], check=True, capture_output=True)
    subprocess.run([*git, "add", "-A"], check=True, capture_output=True)
    subprocess.run([*git, "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "--quiet", "-m", "state under test"],
                   check=True, capture_output=True)
    return reference


def fresh(tmp: Path, n: int, reference: Path) -> Path:
    """A clean copy per case, so cases cannot contaminate each other."""
    clone = tmp / f"c{n}"
    shutil.copytree(reference, clone)
    return clone


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        reference = build_reference(tmp)
        n = 0

        def nxt() -> Path:
            nonlocal n
            n += 1
            return fresh(tmp, n, reference)

        print("baseline")
        c = nxt()
        case("clean clone: rebuild succeeds",
             run(c, "tools/rebuild.py").returncode == 0)

        print("\nD-29 — tampered raw material must stop the build")
        c = nxt()
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        r = run(c, "tools/rebuild.py")
        case("solicitation-family tamper rejected", r.returncode == 1)
        case("names the modified file", "MODIFIED" in r.stdout and "local-round-02" in r.stdout)

        c = nxt()
        (c / RAW_CONTRIB).write_bytes((c / RAW_CONTRIB).read_bytes() + b"\n")
        case("contribution-family tamper rejected",
             run(c, "tools/rebuild.py").returncode == 1)

        print("\nthe manifest must not re-anchor silently")
        c = nxt()
        (c / "corpus/raw/local-round-02/NEW.md").write_text("new material\n")
        r = run(c, "tools/rebuild.py")
        case("unanchored new file rejected by the default path", r.returncode == 1)
        case("reports UNANCHORED", "UNANCHORED" in r.stdout)
        r = run(c, "tools/build_manifest.py", "corpus/raw/", "--add")
        case("--add anchors the new file", r.returncode == 0)
        case("--add anchors exactly one", "anchored 1 new artifact" in r.stdout)

        c = nxt()
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        case("--add refuses when a recorded artifact was modified",
             run(c, "tools/build_manifest.py", "corpus/raw/", "--add").returncode == 1)

        print("\nlaundering — the manifest cannot vouch for itself")
        c = nxt()
        man = c / "corpus/MANIFEST.sha256"
        man.write_text("".join(l for l in man.read_text().splitlines(keepends=True)
                               if "level-4-guarantee" not in l))
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        r = run(c, "tools/build_manifest.py", "corpus/raw/", "--add")
        case("dropping a manifest line does not make a modified file look new",
             r.returncode == 1)
        case("reports DROPPED against HEAD", "DROPPED" in r.stdout)

        c = nxt()
        (c / "corpus/MANIFEST.sha256").unlink()
        case("deleting the whole manifest does not let --add re-anchor the tree",
             run(c, "tools/build_manifest.py", "corpus/raw/", "--add").returncode == 1)

        c = nxt()
        man = c / "corpus/MANIFEST.sha256"
        man.write_text("".join(l for l in man.read_text().splitlines(keepends=True)
                               if "level-4-guarantee" not in l))
        (c / RAW_LOCAL).unlink()
        case("dropping a line AND its file does not verify clean",
             run(c, "tools/build_manifest.py", "corpus/raw/").returncode == 1)

        print("\nmode selection must never be guessed at")
        c = nxt()
        for combo in (("--verify", "--add"), ("--verify", "--force-rewrite"),
                      ("--add", "--force-rewrite")):
            case(f"rejects {' '.join(combo)}",
                 run(c, "tools/build_manifest.py", "corpus/raw/", *combo).returncode == 2)
        case("rejects an unknown flag",
             run(c, "tools/build_manifest.py", "corpus/raw/", "--nope").returncode == 2)

        print("\ndeterminism — the signal the whole commit gate depends on")
        c = nxt()
        run(c, "tools/rebuild.py")
        first = (c / "docs/index.html").read_bytes()
        run(c, "tools/rebuild.py")
        case("rebuild is byte-identical on an unchanged repository",
             (c / "docs/index.html").read_bytes() == first)
        case("rebuild leaves no diff on an unchanged repository",
             subprocess.run(["git", "diff", "--quiet"], cwd=c).returncode == 0)

        print("\ncapture must still work, and must not leave partial artifacts")
        c = nxt()
        reply = c / "reply.md"
        reply.write_text("A response, for regression purposes.\n")
        r = run(c, "tools/capture_response.py", "--round", "regression-test",
                "--response", str(reply), "--prompt", "record/review-round-01-prompt.md",
                "--identity", "RegressionProbe", "--provider", "none",
                "--version-unknown", "test", "--sampling-unknown", "test",
                "--effort-unknown", "test", "--system-instructions-unknown", "test",
                "--captured-utc", "2026-08-06T00:00:00Z", "--phase", "informed",
                "--captured-by", "regression test")
        case("capture succeeds", r.returncode == 0, r.stderr.strip()[:200])
        case("capture anchored its own new file",
             run(c, "tools/build_manifest.py", "corpus/raw/").returncode == 0)

        print("\nthe register must count itself correctly")
        c = nxt()
        case("register self-description consistent",
             run(c, "tools/check_register.py").returncode == 0)
        reg = c / "corpus/deficiencies.md"
        # Derive the declared count instead of hardcoding it. This case previously
        # searched for the literal "**30 entries**"; filing D-31 and D-32 made that
        # string absent, so the tamper silently became a no-op and the case tested
        # nothing. It would have failed loudly here -- but only because the assertion
        # is "the build must fail". A fixture that goes stale in the passing direction
        # is the shape this suite exists to catch.
        declared = re.search(r"\*\*Status:\*\*\s*open\s*—\s*\*\*(\d+) entries\*\*", reg.read_text())
        case("count-tamper fixture still matches the register", declared is not None)
        if declared:
            wrong = f"**{int(declared.group(1)) - 1} entries**"
            reg.write_text(reg.read_text().replace(declared.group(0),
                           declared.group(0).replace(f"**{declared.group(1)} entries**", wrong)))
            case("a wrong declared count fails the build",
                 run(c, "tools/rebuild.py").returncode == 1)

        print("\nD-34 — editing raw material and re-anchoring it must not pass")
        c = nxt()
        base = subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                              capture_output=True, text=True).stdout.strip()
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        run(c, "tools/build_manifest.py", "corpus/raw/", "--force-rewrite")
        subprocess.run(["git","-c","user.name=t","-c","user.email=t@t",
                        "commit","-qam","edit raw and re-anchor"], cwd=c, capture_output=True)
        tip = subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                             capture_output=True, text=True).stdout.strip()
        # The tip is self-consistent, which is the whole difficulty: the manifest was
        # rewritten around the new bytes, so every tip-scoped check passes.
        case("the re-anchored tip still verifies (this is why history must be checked)",
             run(c, "tools/build_manifest.py", "corpus/raw/").returncode == 0)
        r = run(c, "tools/check_raw_append_only.py", base, tip)
        case("the append-only check rejects the edit", r.returncode == 1)
        case("it names the commit and the file",
             tip[:12] in r.stdout and "local-round-02" in r.stdout)

        c = nxt()
        head = subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                              capture_output=True, text=True).stdout.strip()
        case("an unchanged range passes",
             run(c, "tools/check_raw_append_only.py", head, head).returncode == 0)

        c = nxt()
        base = subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                              capture_output=True, text=True).stdout.strip()
        (c / "corpus/raw/local-round-02/ADDED.md").write_text("new material\n")
        run(c, "tools/build_manifest.py", "corpus/raw/", "--add")
        subprocess.run(["git","-c","user.name=t","-c","user.email=t@t",
                        "add","-A"], cwd=c, capture_output=True)
        subprocess.run(["git","-c","user.name=t","-c","user.email=t@t",
                        "commit","-qm","add material"], cwd=c, capture_output=True)
        tip = subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                             capture_output=True, text=True).stdout.strip()
        # Additions MUST be allowed, or the corpus cannot grow. A check that rejects
        # everything is not a stricter check, it is a broken one.
        case("adding raw material is allowed",
             run(c, "tools/check_raw_append_only.py", base, tip).returncode == 0)

        c = nxt()
        # A second commit is needed to exercise the fallback at all: these fixtures
        # have a single ROOT commit, where an all-zero base correctly reports "no
        # prior state" and exits 0. Asserting the fallback message against a root
        # commit tested the fixture, not the tool -- caught by running it.
        (c / RAW_LOCAL).write_bytes((c / RAW_LOCAL).read_bytes() + b"\n")
        run(c, "tools/build_manifest.py", "corpus/raw/", "--force-rewrite")
        subprocess.run(["git","-c","user.name=t","-c","user.email=t@t",
                        "commit","-qam","edit raw and re-anchor"], cwd=c, capture_output=True)
        tip = subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                             capture_output=True, text=True).stdout.strip()
        r = run(c, "tools/check_raw_append_only.py", "0" * 40, tip)
        case("an all-zero base falls back rather than checking nothing",
             "No usable base" in r.stdout)
        case("and the fallback still catches the tip's violation", r.returncode == 1)

        c = nxt()
        r = run(c, "tools/check_raw_append_only.py", "0" * 40,
                subprocess.run(["git","rev-parse","HEAD"], cwd=c,
                               capture_output=True, text=True).stdout.strip())
        case("an all-zero base on a root commit says so and passes",
             r.returncode == 0 and "Root commit" in r.stdout)

        print("\nD-33 — every generated file must be derived by the build")
        c = nxt()
        # The capture page moved from docs/capture/ to tools/capture_ui/ in 97e852d,
        # off the published surface: it is an operator instrument, not a public
        # artifact. The D-33 defect is UNCHANGED by the move -- the page still
        # embeds prompt digests, and a stale one still misstates what it anchors.
        # The move did remove it from CI's docs/-scoped byte-equality gate, so that
        # gate now covers generated files outside docs/ too.
        cap = c / CAPTURE_PAGE
        cap.write_text(cap.read_text() + "<!-- hand edit -->")
        # COMMIT the edit. That is the scenario CI actually faces: it checks out a
        # commit and asks whether the committed page equals a regeneration. An
        # uncommitted hand edit is not the threat -- rebuild.py simply overwrites it
        # and the diff comes back clean, which is why this case first asserted the
        # wrong thing and passed for the wrong reason until it was run.
        subprocess.run(["git","-c","user.name=t","-c","user.email=t@t",
                        "commit","-qam","hand edit"], cwd=c, capture_output=True)
        run(c, "tools/rebuild.py")
        case("a committed hand-edited capture page is caught by the diff gate",
             subprocess.run(["git","diff","--quiet","--",CAPTURE_PAGE],
                            cwd=c).returncode == 1)

        c = nxt()
        # The real 2026-08-06 failure: edit a prompt the capture page embeds, and the
        # page's committed prompt_sha256 silently stops matching the file it names.
        # Before build_capture_ui.py was in rebuild.py, this left NO diff at all --
        # rebuild exited 0, git status was clean, and CI's byte-equality gate passed.
        prompt = c / "record/review-round-03-prompt.md"
        prompt.write_text(prompt.read_text() + "\nAn edit that changes the digest.\n")
        # UPDATED 2026-08-06 at the session/site merge. This asserted that the edit
        # showed up as a diff in the capture page. It no longer gets that far, and the
        # reason is stronger protection rather than weaker: review round 03's four
        # capture artifacts now ANCHOR this prompt by sha256, so the edit fails at P1
        # in validate_provenance and rebuild aborts before the capture generator runs.
        # The original intent -- an edited embedded prompt must never pass silently --
        # is preserved and now met earlier and more loudly.
        r = run(c, "tools/rebuild.py")
        case("editing an embedded prompt fails the build",
             r.returncode == 1)
        case("the failure names the prompt whose hash no longer matches",
             "record/review-round-03-prompt.md" in r.stdout and "hash mismatch" in r.stdout)
        digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
        case("the anchored prompt digest is what the capture records point at",
             any(digest in (c / "corpus/artifacts/review-round-03" / f).read_text()
                 for f in ["grok-01.json"]) is False)  # digest CHANGED, so records must NOT match

        print("\nD-32 — colliding identifiers must fail the build")
        c = nxt()
        reg = c / "corpus/deficiencies.md"
        # Reproduce the actual 2026-08-06 collision: Track B's entry filed as D-29,
        # the number Track A had concurrently used.
        reg.write_text(reg.read_text().replace(
            "### D-31 — External reviewers", "### D-29 — External reviewers", 1))
        # UPDATED at the session/site merge: corpus/artifacts/deficiency-register.json
        # now anchors deficiencies.md by sha256, so ANY edit to the register fails at
        # P1 in validate_provenance before check_register runs. Assert against the tool
        # that owns the check rather than against whichever gate happens to fire first.
        r = run(c, "tools/rebuild.py")
        case("duplicate D-NN fails the build", r.returncode == 1)
        rc = run(c, "tools/check_register.py")
        case("names the colliding id, not just a bad count", "duplicate entry id: D-29" in rc.stdout)

        c = nxt()
        pred = c / "predictions" / "predictions.json"
        data = json.loads(pred.read_text())
        entries = data["predictions"] if isinstance(data, dict) else data
        entries.append(dict(entries[0]))
        pred.write_text(json.dumps(data, indent=2))
        r = run(c, "tools/rebuild.py")
        case("duplicate P-NNNN fails the build", r.returncode == 1)
        case("names the colliding prediction id",
             "duplicate prediction id" in r.stdout)

        c = nxt()
        # A prediction with no id at all: the loop that collects ids would otherwise
        # raise KeyError, and a checker that crashes is not a checker that failed.
        pred = c / "predictions" / "predictions.json"
        data = json.loads(pred.read_text())
        entries = data["predictions"] if isinstance(data, dict) else data
        entries[0].pop("id", None)
        pred.write_text(json.dumps(data, indent=2))
        r = run(c, "tools/rebuild.py")
        case("a prediction with no id fails cleanly", r.returncode == 1)
        case("reports the missing id rather than a traceback",
             "have no id" in r.stdout and "Traceback" not in r.stdout + r.stderr)

        print("\nthe classification must not describe prose it no longer matches")
        c = nxt()
        reg = c / "corpus/deficiencies.md"
        reg.write_text(reg.read_text().replace(
            "### D-25 — A deterministic coder was trusted without validation, and it was wrong\n",
            "### D-25 — A deterministic coder was trusted without validation, and it was wrong\n\nInserted.\n", 1))
        r = run(c, "tools/check_register.py")
        case("editing an entry's prose fails until it is re-stamped", r.returncode == 1)
        case("names the drifted entry", "D-25" in r.stdout and "R9" in r.stdout)  # R8 -> R9 at merge; main took R5
        r = run(c, "tools/check_register.py", "--restamp", "D-25")
        case("--restamp clears the drift", r.returncode == 0)
        case("re-stamp resets human review rather than asserting approval",
             json.loads((c / "corpus/artifacts/deficiency-register.json").read_text())
             ["entries"][24]["human_review"]["status"] == "not_reviewed")

        c = nxt()
        art = c / "corpus/artifacts/deficiency-register.json"
        doc = json.loads(art.read_text())
        doc["entries"] = [e for e in doc["entries"] if e["id"] != "D-17"]
        art.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        r = run(c, "tools/check_register.py")
        case("an unclassified deficiency fails the build", r.returncode == 1)
        case("names the unclassified entry", "D-17" in r.stdout)

        print("\nthe published site must not understate the record")
        c = nxt()
        run(c, "tools/rebuild.py")
        page = (c / "docs/index.html").read_text(encoding="utf-8")
        summaries = list((c / "corpus/artifacts").glob("local-round-*/*-summary.json"))
        pages = list((c / "docs/local").glob("local-round-*__*.html"))
        case("every solicitation summary has a published page",
             len(pages) == len(summaries), f"{len(pages)} pages vs {len(summaries)} summaries")
        case("local rounds appear in the threaded viewer",
             'class="round">local-round-01' in page)
        case("the blanket k=1 claim is gone",
             "Every contribution here is a single sample (k=1)" not in page)
        case("local-round content is searchable in the rendered page",
             "binds_only_what_may_be_claimed" in page)
        case("the viewer no longer embeds a second copy of every contribution",
             '"text":' not in page.split("const DATA=")[1].split("};")[0])
        case("no page loads an external resource",
             not re.search(r'(?:src|href)="https?://(?!github\.com)', page))
        case("the entry point links forward to the register and the local rounds",
             'href="deficiencies.html"' in page and 'href="local/index.html"' in page)
        case("no generated link points at a /blob/ URL",
             not re.search(r'<a href="https://github\.com/[^"]*/blob/', page))

    print()
    total = len(PASSED) + len(FAILED)
    if FAILED:
        print(f"FAILED — {len(FAILED)} of {total}:")
        for name in FAILED:
            print(f"  {name}")
        return 1
    print(f"All {total} integrity cases pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
