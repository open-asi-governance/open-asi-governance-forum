#!/usr/bin/env python3
"""Regression tests for held-capture disposition and conflict resolution.

    python3 tools/tests/test_disposition.py

Capture Defect 1: `returned_pending_review -> {accepted, rejected}` was PERMITTED by
the state machine and performed by nothing. `"rejected"` appeared in tools/ only
inside membership tests. One held capture blocked a round permanently.

The existing lifecycle suite could not catch it, and the reason is the point: it
tested that the transition is *permitted*, which is a different claim from anything
*invoking* it. These tests drive the actual command-line entry points against a
synthetic round on disk, because that is the only level at which "nothing calls
this" is visible.

Runs against a throwaway repository built in a temp directory. Nothing here touches
the real corpus.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REAL_ROOT = Path(__file__).resolve().parent.parent.parent
LONG_PROMPT = (
    "Consider the normative definition in section two of the specification and explain "
    "whether the correction resolves the contradiction, relocates it, or introduces a new "
    "one. Attend to the qualifier list and to any partial propagation elsewhere in the "
    "document. Answer in your own terms and state what you could not check. " * 4
)

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASSED if ok else FAILED).append(name)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  — ' + detail if detail and not ok else ''}")


def run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=repo, capture_output=True, text=True)


def build_repo(tmp: Path) -> Path:
    """A minimal repository with one declared round and one party."""
    repo = tmp / "repo"
    (repo / "tools").mkdir(parents=True)
    for name in ("capture_lifecycle.py", "capture_gates.py", "capture_response.py",
                 "ingest_capture.py", "resolve_held_capture.py", "resolve_conflict.py",
                 "build_manifest.py", "validate_provenance.py"):
        shutil.copy(REAL_ROOT / "tools" / name, repo / "tools" / name)
    shutil.copytree(REAL_ROOT / "tools" / "schemas", repo / "tools" / "schemas")

    (repo / "record" / "rounds").mkdir(parents=True)
    (repo / "corpus" / "raw").mkdir(parents=True)
    prompt = repo / "record" / "test-prompt.md"
    # LONG on purpose. G2c-prompt-saturation compares shingles, and a short prompt
    # produces too few for the gate to fire at all -- the first version of this
    # fixture used a one-line prompt, nothing was ever held, and eleven cases
    # "passed" by testing the wrong path. A fixture that cannot reach the state
    # under test is worse than a missing test.
    prompt.write_text(LONG_PROMPT, encoding="utf-8")

    (repo / "record" / "rounds" / "t-round.json").write_text(json.dumps({
        "schema_version": 1, "artifact_type": "round", "round": "t-round",
        "question": "A test question?", "phase": "Phase-2 (informed)",
        "common_prompt": "record/test-prompt.md", "frozen": True,
        "parties": [{
            "identity": "TestParty", "provider": "TestProvider",
            "delivery": "direct", "prior_context_template": "None.",
            "prompt_override": None, "bundle": None,
            "sampling_unknown_reason": "not exposed",
            "effort_unknown_reason": "not exposed",
            "system_instructions_unknown_reason": "not exposed",
            "version_unknown_reason": "not exposed",
        }],
    }), encoding="utf-8")

    subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "--quiet", "-m", "base"], cwd=repo, check=True, capture_output=True)
    return repo


def bundle(repo: Path, name: str, text: str) -> Path:
    sys.path.insert(0, str(REAL_ROOT / "tools"))
    import capture_lifecycle as L
    prompt = (repo / "record" / "test-prompt.md").read_text(encoding="utf-8")
    path = repo / name
    path.write_text(json.dumps({
        "bundle_version": 1, "round": "t-round", "identity": "TestParty",
        "response_text": text, "prompt_path": "record/test-prompt.md",
        "prompt_sha256": L.sha256_of_text(prompt),
        "attested_answers_round_question": True, "attested_by": "custodian",
        "captured_utc": "2026-08-06T19:00:00Z", "phase": "Phase-2",
    }), encoding="utf-8")
    return path


def status(repo: Path) -> dict:
    out = run(repo, "-c", (
        "import sys,json;sys.path.insert(0,'tools');import capture_lifecycle as L;"
        "print(json.dumps(L.round_status('t-round',['TestParty'])))"))
    return json.loads(out.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        repo = build_repo(tmp)

        # A response that is mostly the prompt trips G2c and is HELD.
        held_text = LONG_PROMPT[:1200] + "\n\nA brief additional remark from the reviewer."
        run(repo, "tools/ingest_capture.py", str(bundle(repo, "held.json", held_text)))

        st = status(repo)
        check("a gate failure holds the capture", st["states"]["TestParty"] == "returned_pending_review")
        check("a held capture blocks completion", st["complete"] is False)
        check("a held capture blocks closure too", st["closed"] is False)

        # ---------------------------------------------------- reject --
        r = run(repo, "tools/resolve_held_capture.py", "t-round", "TestParty",
                "--reject", "--reason", "Quotation of the prompt, not a reply.")
        check("reject succeeds", r.returncode == 0, r.stdout + r.stderr)

        st = status(repo)
        check("rejection CLOSES the round", st["closed"] is True)
        check("rejection does NOT complete the round", st["complete"] is False)
        check("the round names what is owed", st["replacement_required"] == ["TestParty"])
        check("rejected bytes are kept",
              (repo / "record/quarantine/t-round/testparty-01.md").exists())
        check("rejection writes nothing to the corpus",
              not list((repo / "corpus" / "raw").rglob("*.md")))

        # ---------------------------------------------------- accept --
        repo2 = build_repo(tmp / "second")
        run(repo2, "tools/ingest_capture.py", str(bundle(repo2, "held.json", held_text)))
        check("second fixture is held",
              status(repo2)["states"]["TestParty"] == "returned_pending_review")

        r = run(repo2, "tools/resolve_held_capture.py", "t-round", "TestParty",
                "--accept", "--reason", "Custodian judged it a genuine reply.")
        check("accept succeeds", r.returncode == 0, (r.stdout + r.stderr)[-400:])

        st = status(repo2)
        check("acceptance marks the party accepted", st["states"]["TestParty"] == "accepted")
        check("acceptance completes the round", st["complete"] is True)
        check("acceptance PUBLISHES into the corpus",
              bool(list((repo2 / "corpus" / "raw" / "t-round").glob("*.md"))))

        # Acceptance must be derived from the corpus, not from the label: the
        # published bytes have to be the preserved bytes.
        published = next((repo2 / "corpus" / "raw" / "t-round").glob("*.md"))
        preserved = repo2 / "record/quarantine/t-round/testparty-01.md"
        check("published bytes equal preserved bytes",
              published.read_text(encoding="utf-8") == preserved.read_text(encoding="utf-8"))

        # ------------------------------------------ refusals on accept --
        repo3 = build_repo(tmp / "third")
        run(repo3, "tools/ingest_capture.py", str(bundle(repo3, "held.json", held_text)))
        target = repo3 / "record/quarantine/t-round/testparty-01.md"
        target.write_text(held_text + "\nTAMPERED after preservation.", encoding="utf-8")
        r = run(repo3, "tools/resolve_held_capture.py", "t-round", "TestParty",
                "--accept", "--reason", "should not work")
        check("accept refuses when the preserved bytes were altered", r.returncode == 1)
        check("and says why", "no longer matches its recorded hash" in r.stdout)
        check("and does not publish",
              not list((repo3 / "corpus" / "raw").rglob("*.md")))

        r = run(repo3, "tools/resolve_held_capture.py", "t-round", "TestParty", "--accept")
        check("a disposition with no reason is refused", r.returncode == 1)
        r = run(repo3, "tools/resolve_held_capture.py", "t-round", "TestParty",
                "--accept", "--reject", "--reason", "x")
        check("accept and reject together are refused", r.returncode == 1)

        # ------------------------------- the conflict resolver's own bug --
        # `--supersede-with-conflicting` used to clear the block on the DECISION,
        # leaving the disowned text published and the round reporting COMPLETE.
        # It must now stay blocked until the corpus actually holds the new bytes.
        conflicting = "A completely different corrected reply, long enough to be a real answer."
        run(repo2, "-c", (
            "import sys;sys.path.insert(0,'tools');import capture_lifecycle as L;"
            f"L.record_conflict('t-round','TestParty','custodian',{conflicting!r},"
            "L.latest_response_event('t-round','TestParty')['response_sha256'])"))
        check("a conflict re-blocks a completed round", status(repo2)["complete"] is False)

        r = run(repo2, "tools/resolve_conflict.py", "t-round", "TestParty",
                "--supersede-with-conflicting", "--reason", "the correction is the real reply")
        check("supersede is recorded", r.returncode == 0, r.stdout + r.stderr)
        check("SUPERSEDE ALONE DOES NOT COMPLETE THE ROUND",
              status(repo2)["complete"] is False,
              "the disowned text is still what is published")

        r = run(repo2, "tools/resolve_conflict.py", "t-round", "TestParty",
                "--confirm-recorded", "--reason", "actually the original stands")
        check("confirm_recorded DOES clear immediately",
              status(repo2)["complete"] is True, r.stdout + r.stderr)


        # ------------------------------------- Defect 4: batch containment --
        # A mistyped path is the first thing a custodian gets wrong. It used to raise
        # out of a list comprehension in main(): bundles before it had ALREADY
        # written, bundles after were never processed, and the summary and
        # round-status table -- everything after that line -- never printed.
        repo4 = build_repo(tmp / "fourth")
        good = bundle(repo4, "good.json", "A genuine reply about the specification, "
                                          "long enough to clear every gate comfortably.")
        # b"\xff" is a lone byte that cannot begin a UTF-8 sequence. The first version
        # of this fixture used b"\xf0\x9f\x92\xa9", which is VALID UTF-8 (an emoji), so
        # it decoded cleanly and failed as invalid JSON instead -- the test passed on
        # the wrong path. Second fixture today that could not reach the state it named.
        (repo4 / "binary.json").write_bytes(b"\xff\xfe not utf-8 at all")
        (repo4 / "notjson.json").write_text("{ this is not json", encoding="utf-8")

        r = run(repo4, "tools/ingest_capture.py", str(good),
                "/nonexistent-path.json", ".", "binary.json", "notjson.json")
        out = r.stdout + r.stderr
        check("a batch with bad paths does not traceback", "Traceback" not in out, out[-300:])
        check("a missing path is reported", "No such file or directory" in out)
        check("a directory is reported", "Is a directory" in out)
        check("a non-UTF-8 file is reported", "not UTF-8 text" in out)
        check("bad input is INPUT ERROR, not a governance refusal",
              out.count("INPUT ERROR") == 3)
        check("invalid JSON is still a refusal", "REFUSED: not valid JSON" in out)
        check("the summary still prints", "input_error" in out)
        check("the round-status table still prints", "t-round:" in out)
        check("the good bundle in the batch was still processed",
              (repo4 / "record/quarantine/t-round").exists())
        check("exit is non-zero when inputs failed", r.returncode != 0)

        # ------------------------------ Defect 6: the capture page filename --
        page = (REAL_ROOT / "tools" / "capture_ui" / "index.html").read_text(encoding="utf-8")
        check("the page no longer prints a glob ingest command",
              "oagf-capture-*" not in page,
              "a glob makes shell collation decide which response becomes canonical")
        check("the download filename carries a response hash",
              "responseSha.slice(0,16)" in page)
        check("the printed command is filled in from the name actually used",
              'ingest-command' in page and "ingest_capture.py \"$HOME/Downloads/" in page)
        check("the page calls the filename SUGGESTED, because a browser may suffix",
              "suggested" in page.lower())
        check("the bundle hash is recomputed at download, not read from async state",
              "const responseSha = await sha256(text)" in page
              and "response_sha256_at_paste: responseSha" in page)

    print()
    print(f"{len(PASSED)} passed, {len(FAILED)} failed")
    for name in FAILED:
        print(f"  FAIL  {name}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
