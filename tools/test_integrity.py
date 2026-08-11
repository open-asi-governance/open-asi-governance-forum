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

#  ROOT FILES a build step reads. The reference repository copied DIRECTORIES only, so a page
#  generated from a root file was absent there and the rebuild failed inside the reference while
#  passing in the working tree -- the gate reporting a defect that existed only in its own copy.
TRACKED_FILES = ("CHALLENGE.md", "CLAUDE.md", "AGENTS.md", "FOR-PARTIES-THE-WORKBENCH.md",
                 "README.md")


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
    for name in TRACKED_FILES:
        source = REPO_ROOT / name
        if source.is_file():
            shutil.copy2(source, reference / name, follow_symlinks=True)
    git = ["git", "-C", str(reference)]
    subprocess.run([*git, "init", "--quiet"], check=True, capture_output=True)
    # DISABLE AUTO-GC. fresh() copies this repository's .git for every case, and
    # git's automatic gc fires after enough loose objects accumulate -- deleting
    # objects WHILE copytree is walking them. The result is a shutil.Error listing
    # dozens of vanished paths, on a run where nothing about the corpus is wrong.
    #
    # It failed twice in CI and never once locally, which is the worst shape a gate
    # can have: the integrity suite is the signal every other control is trusted
    # through, and a suite that fails at random teaches people to re-run it until it
    # passes. That habit would have hidden a real failure.
    subprocess.run([*git, "config", "gc.auto", "0"], check=True, capture_output=True)
    subprocess.run([*git, "config", "maintenance.auto", "false"], check=True,
                   capture_output=True)
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

        print("\ncompose must be verified by EFFECT, not by syntax")
        c = nxt()
        #  PROBE, not assertion. Every case below drives the real functions and reads
        #  what came out. Four fail-silent defects in two days were all of the shape
        #  "the code ran and reported success without doing anything", and none of
        #  them was reachable by a test that checked a return code.
        probe = r"""
import sys, json
sys.path.insert(0, "tools")
import round_cycle as RC, agenda_selectors as AS
out = {}
rendered, anchors, pack_sha = RC.context_pack()

class P:
    pid, party, sponsors = "P999", "grok", {"grok"}
    def __init__(s, q, r="a stated reason", e="the evidence it would need"):
        s.question, s.reason, s.raw = q, r, {"evidence_needed": e}

plain = P("Is the operator's control disclosed?")
prompt, spans = RC.compose(plain, "grok", 5, rendered, anchors)
out["prompt"] = prompt
out["template_len"] = len(open("record/solicitations/excerpts/"
                               "round-prompt-template.md").read())

# A party's question containing a literal placeholder must survive UNTOUCHED.
# Chained str.replace substituted the answer instructions INTO the quoted question.
hostile = P("Does the {answer_space} slot matter, and {question} too?")
hostile_prompt, _ = RC.compose(hostile, "grok", 5, rendered, anchors)
out["proposer_bytes_intact"] = hostile.question in hostile_prompt
out["real_slot_still_filled"] = "Return the structured fields" in hostile_prompt

# All parties must receive identical bytes apart from the two declared slots.
# Identical WITHIN AN ARM. Parties with search and parties without receive
# different, true, statements about what they can do; across that line the
# prompts SHOULD differ, and requiring them not to is what produced a false
# capability claim to the local party in the first place.
arms = {}
for kk in RC.PARTIES:
    armed = bool(RC.PARTIES[kk]["model"]) and bool(RC.WEB_SEARCH.get("id"))
    arms.setdefault(armed, set()).add(RC.sha256_text(RC.compose(
        plain, kk, 5, rendered, anchors, identity_override="X", reached_override="Y")[0]))
out["identical_within_arm"] = all(len(v) == 1 for v in arms.values())
out["arms"] = len(arms)
out["arms_differ"] = len({d for v in arms.values() for d in v}) == len(arms)

# A denylist phrase the PARTY wrote is recorded; the same phrase in the
# moderator's template is fatal. The parties' words are not ours to sanitise.
rep = RC.lint_prompt(*RC.compose(P("Which is the most dangerous defect?"), "grok", 5,
                                 rendered, anchors), "grok")
out["party_phrase_recorded_not_fatal"] = not rep["fatal"] and bool(
    rep["recorded_in_party_words"])

# A value with no slot is as much a bug as a slot with no value: the first is a
# silent no-op, and a silent no-op is what shipped a byte-identical round.
try:
    RC.compose_with_spans("hi {a}", {"a": "1", "b": "2"})
    out["orphan_value_raises"] = False
except RC.Refusal as e:
    out["orphan_value_raises"] = "b" in str(e.detail)

# An unpriced model must refuse, not cost zero.
try:
    RC.price_cycle([{"party_key": "grok", "prompt": "x", "k_requested": 5,
                     "max_tokens": 10}], {"usd_per_million_tokens": {}})
    out["unpriced_model_refuses"] = False
except RC.Refusal as e:
    out["unpriced_model_refuses"] = "no rate recorded" in e.reason

# A misspelled party key must NOT fall through to the local endpoint. It did:
# .get() returns None for a typo exactly as it does for the local party.
import argparse
try:
    RC.build_plan(argparse.Namespace(parties="grok,gtp", k=5, selector="rotation",
                  seed=1, round_id=None, max_spend_usd=99.0, capability=None), 0)
    out["typo_party_refuses"] = False
except RC.Refusal as e:
    out["typo_party_refuses"] = "gtp" in str(e.detail)

print(json.dumps(out))
"""
        (c / "zz_probe.py").write_text(probe, encoding="utf-8")
        res = run(c, "zz_probe.py")
        case("the compose probe runs at all", res.returncode == 0, res.stderr[-300:])
        out = json.loads(res.stdout) if res.returncode == 0 else {}
        prompt = out.get("prompt", "")
        case("no placeholder survives substitution",
             bool(prompt) and not re.findall(r"\{[a-z_]+\}", prompt),
             str(re.findall(r"\{[a-z_]+\}", prompt))[:120])
        case("the rule-resolved context pack reaches the prompt",
             "adopt-rotation" in prompt and "| D-" in prompt)
        case("the proposer's evidence_needed is quoted",
             "said it would need" in prompt)
        case("the composed prompt is materially larger than the template",
             len(prompt) > 2 * out.get("template_len", 10 ** 9))
        case("a literal placeholder in the proposer's question is not substituted into",
             out.get("proposer_bytes_intact") is True)
        case("and the real slot is still filled anyway",
             out.get("real_slot_still_filled") is True)
        case("within an arm, every party receives identical bytes but the two declared slots",
             out.get("identical_within_arm") is True, f"{out.get('arms')} arm(s)")
        # And the arms must actually DIFFER — otherwise a party without search would
        # be reading the sentence written for parties that have it, which is the
        # false capability claim this split exists to prevent.
        case("the no-search arm is told something different from the search arm",
             out.get("arms", 0) > 1 and out.get("arms_differ") is True)
        case("a denylist phrase in the party's own words is recorded, not fatal",
             out.get("party_phrase_recorded_not_fatal") is True)
        case("a value with no slot raises rather than silently doing nothing",
             out.get("orphan_value_raises") is True)
        case("a model with no rate refuses rather than costing zero",
             out.get("unpriced_model_refuses") is True)
        case("a misspelled party key refuses rather than reaching the local endpoint",
             out.get("typo_party_refuses") is True)
        (c / "zz_probe.py").unlink()

        # A slot the template adds but compose forgets must RAISE, not ship a literal
        # placeholder. It shipped one to ten party invocations across two live rounds.
        tpl = c / "record/solicitations/excerpts/round-prompt-template.md"
        tpl.write_text(tpl.read_text(encoding="utf-8") + "\n{a_new_slot_nobody_filled}\n",
                       encoding="utf-8")
        r = run(c, "-c", (
            "import sys;sys.path.insert(0,'tools');"
            "import round_cycle as RC, agenda_selectors as AS;"
            "rendered,anchors,_=RC.context_pack();"
            "q=AS.load_queue();p=AS.SELECTORS['rotation'](q,['grok'],0,1);"
            "RC.compose(p,'grok',5,rendered,anchors)"))
        case("an unfilled slot raises rather than shipping",
             r.returncode != 0 and "a_new_slot_nobody_filled" in (r.stderr + r.stdout))

        print("\nthe capture page must show the WHOLE prompt for a verbatim round")
        c = nxt()
        r = run(c, "-c",
                "import sys,json;sys.path.insert(0,'tools');"
                "import build_capture_ui as b;from pathlib import Path;"
                "out={};"
                "rs={x['round']:x for x in b.load_rounds()};"
                "v=[p for x in rs.values() for p in x['parties'] if p.get('prompt_is_verbatim')];"
                "out['verbatim_whole']=all(p['sent_text']==Path(p['prompt_path']).read_text() for p in v);"
                "out['n_verbatim']=len(v);"
                "l=[p for x in rs.values() for p in x['parties'] if not p.get('prompt_is_verbatim')];"
                "out['legacy_still_extracts']=all(len(p['sent_text'])<=len(Path(p['prompt_path']).read_text()) for p in l);"
                "print(json.dumps(out))")
        out = json.loads(r.stdout) if r.returncode == 0 else {}
        # A verbatim prompt file IS the sent bytes. Run through the blockquote
        # extractor built for the legacy review-round files it kept 3 lines of 254 --
        # and the response gates compared against those 3 lines too.
        case("a verbatim prompt is displayed and gated whole",
             out.get("verbatim_whole") is True and out.get("n_verbatim", 0) > 0,
             f"{out.get('n_verbatim')} verbatim parties")
        case("a legacy prompt still has its metadata stripped",
             out.get("legacy_still_extracts") is True)

        print("\nthe external anchor must fail when the manifest drifts past it")
        c = nxt()
        case("a correctly anchored manifest verifies",
             run(c, "tools/anchor_manifest.py").returncode == 0)
        # Every round adds raw material, so the manifest changes and the previous
        # anchor stops covering the live state. An anchor that keeps passing while
        # the thing it anchors moves is a control that has stopped measuring.
        man = c / "corpus/MANIFEST.sha256"
        man.write_text(man.read_text() + "0" * 64 + "  corpus/raw/zz/x.json\n")
        r = run(c, "tools/anchor_manifest.py")
        case("a drifted manifest fails the anchor check",
             r.returncode == 1 and "not anchored" in r.stdout)
        case("and the whole build refuses", run(c, "tools/rebuild.py").returncode == 1)
        man.write_text(man.read_text().replace("0" * 64 + "  corpus/raw/zz/x.json\n", ""))
        for receipt in (c / "record/anchors").glob("*.ots"):
            receipt.unlink()
        case("a missing receipt fails rather than passing by absence",
             run(c, "tools/anchor_manifest.py").returncode == 1)

        print("\nthe loop must not advance past what the custodian has not accepted")
        c = nxt()
        # Disposition: a question recorded as asked must not be selected again.
        r = run(c, "-c", (
            "import sys,json;sys.path.insert(0,'tools');"
            "import agenda_selectors as AS;"
            "q=AS.load_queue();first=AS.SELECTORS['rotation'](q,['claude'],0,1);"
            "d={first.question_sha256:'round-000'};"
            "q2=AS.load_queue(disposition=d);"
            "second=AS.SELECTORS['rotation'](q2,['claude'],0,1);"
            "print(json.dumps([first.pid, second.pid if second else None]))"))
        pids = json.loads(r.stdout) if r.returncode == 0 else [None, None]
        case("a question already asked is not selected again",
             pids[0] is not None and pids[0] != pids[1], f"{pids}")

        # And the disposition reader must FAIL on an unreadable record rather than
        # guess 'not asked', which would re-spend real money on a settled question.
        (c / "record/cycles/round-zz.json").write_text("{not json", encoding="utf-8")
        r = run(c, "-c", (
            "import sys;sys.path.insert(0,'tools');import agenda_selectors as AS;"
            "AS.disposition_from_records(__import__('pathlib').Path('record/cycles'))"))
        case("an unreadable round record fails loudly rather than reading as unasked",
             r.returncode != 0 and "disposition cannot be established" in r.stderr)
        (c / "record/cycles/round-zz.json").unlink()

        print("\nprompt construction — the defects must fail while a prompt is editable")
        c = nxt()
        bad = c / "record/solicitations/excerpts/zz-lint-probe.md"
        bad.write_text("Where did the revision OVER-CORRECT?\n", encoding="utf-8")
        r = run(c, "tools/check_prompt.py")
        case("a direction-naming prompt fails the check", r.returncode == 1)
        case("and cites the deficiency it violates", "D-31" in r.stdout)
        bad.write_text("Disagreement is more useful than endorsement.\n", encoding="utf-8")
        case("a posture-setting prompt fails too",
             run(c, "tools/check_prompt.py").returncode == 1)
        bad.unlink()
        case("the committed prompts pass",
             run(c, "tools/check_prompt.py").returncode == 0)

        tpl = c / "record/solicitations/excerpts/round-prompt-template.md"
        original = tpl.read_text(encoding="utf-8")
        tpl.write_text(original.replace("<!-- SLOT: answer_space -->", ""), encoding="utf-8")
        r = run(c, "tools/check_prompt.py")
        case("a template missing a slot fails", r.returncode == 1)
        case("and names the missing slot", "answer_space" in r.stdout)
        tpl.write_text(original.replace("insufficient to decide", "decide"), encoding="utf-8")
        r = run(c, "tools/check_prompt.py")
        case("a template with no way to say 'insufficient' fails", r.returncode == 1)
        tpl.write_text(original, encoding="utf-8")

        # A sent prompt is immutable, so its violation is recorded, never demanded-fixed.
        r = run(c, "tools/check_prompt.py")
        case("a violation in a SENT prompt does not fail the build", r.returncode == 0)
        case("but is reported as a recorded violation",
             "RECORDED VIOLATION" in r.stdout)

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
        #  READ THE EXIT CODE. This was `run(c, "tools/rebuild.py")` with the result discarded,
        #  and every case below then inspected whatever files happened to be present. The temp
        #  checkout is seeded from the working tree INCLUDING generated docs/, so a builder
        #  changed to write nothing would leave the seeded pages in place and the whole block
        #  would report green. An external review found this; it is the repository's dominant
        #  failure -- a check not causally downstream of what it certifies -- inside the suite
        #  written to catch it.
        _rebuild = run(c, "tools/rebuild.py")
        case("the site rebuilds", _rebuild.returncode == 0,
             (_rebuild.stderr or _rebuild.stdout)[-400:] if _rebuild.returncode else "")

        #  And the rebuild must have WRITTEN the controls pages, not merely left the seeded ones
        #  alone. Delete them first, rebuild, and require them back with the receipt's bytes.
        _docs = c / "docs"
        for _stale in sorted(_docs.glob("controls*.html")):
            _stale.unlink()
        _again = run(c, "tools/rebuild.py")
        case("...and a rebuild republishes the controls pages after they are deleted",
             _again.returncode == 0 and (_docs / "controls.html").is_file(),
             (_again.stderr or _again.stdout)[-400:] if _again.returncode else "")
        _receipt_path = _docs / "artifacts" / "controls-pages.json"
        case("...and issues a receipt naming every page it wrote", _receipt_path.is_file())
        _receipt = json.loads(_receipt_path.read_text(encoding="utf-8")) \
            if _receipt_path.is_file() else {"pages": {}}
        case("...whose recorded hashes match the bytes on disk",
             bool(_receipt.get("pages")) and all(
                 (_docs / _n).is_file() and
                 hashlib.sha256((_docs / _n).read_bytes()).hexdigest() == _h
                 for _n, _h in _receipt["pages"].items()))
        # index.html is now the TABLE OF CONTENTS, not the record. The record lives on
        # per-round pages, so assertions about contributions read the record pages and
        # assertions about routing read the index. Conflating them is how the previous
        # version of this block came to assert `const DATA=` against a page that no
        # longer carries one.
        # index.html is the LANDING page; record.html is the table of contents. They
        # were the same file until the landing page landed, and this block asserted
        # routing against whichever one happened to be index.html at the time.
        def is_record_page(f):
            """Record pages carry contributions. Landing, contents and the generated
            register/prediction views are not record pages and have their own tests.
            One predicate, because three separate exclusion lists drifted the moment
            the predictions view started chunking into predictions-2.html."""
            return (f.name not in ("index.html", "record.html")
                    and not f.stem.startswith("deficiencies")
                    and not f.stem.startswith("predictions")
                    #  controls.html is a generated view of the candidate control register, not
                    #  a page of contributions. It gets its own cases below, per this
                    #  predicate's own rule that generated views are tested separately.
                    and not f.stem.startswith("controls")
                    and not f.stem.startswith("challenge"))

        index = (c / "docs/index.html").read_text(encoding="utf-8")
        toc = (c / "docs/record.html").read_text(encoding="utf-8")
        record = "".join(f.read_text(encoding="utf-8")
                         for f in sorted((c / "docs").glob("*.html"))
                         if is_record_page(f))
        page = index + record
        summaries = list((c / "corpus/artifacts").glob("local-round-*/*-summary.json"))
        pages = list((c / "docs/local").glob("local-round-*__*.html"))
        case("every solicitation summary has a published page",
             len(pages) == len(summaries), f"{len(pages)} pages vs {len(summaries)} summaries")
        case("local rounds appear in the threaded viewer",
             "local-round-01" in record)
        case("the blanket k=1 claim is gone",
             "Every contribution here is a single sample (k=1)" not in page)
        case("local-round content is searchable in the rendered page",
             "binds_only_what_may_be_claimed" in record)
        case("record pages do not embed a second copy of every contribution",
             all('"text":' not in f.read_text(encoding="utf-8").split("const DATA=")[1].split("};")[0]
                 for f in sorted((c / "docs").glob("*.html"))
                 if "const DATA=" in f.read_text(encoding="utf-8")))
        case("no page loads an external resource",
             not re.search(r'(?:src|href)="https?://(?!github\.com)', page))
        case("the landing page routes to every top-level surface",
             all(link in index for link in ('href="record.html"', 'href="deficiencies.html"',
                                            'href="predictions.html"', 'href="llms.txt"')))
        case("the landing page is small enough to be read whole",
             len(index.encode()) / 3.4 < 6000, f"{int(len(index.encode())/3.4)} est-tokens")
        case("the prediction registry publishes its own weakness",
             "forecast by the annotator" in
             (c / "docs/predictions.html").read_text(encoding="utf-8"))
        # R11: a scored prediction must record who applied the outcome.
        pj = c / "predictions/predictions.json"
        original = pj.read_text(encoding="utf-8")
        doc = json.loads(original)
        doc["scored"][0].pop("scored_by", None)
        pj.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        r = run(c, "tools/check_register.py")
        case("a scored prediction with no scored_by fails the build", r.returncode == 1)
        case("and R11 names the entry", "R11" in r.stdout and doc["scored"][0]["id"] in r.stdout)

        doc["scored"][0]["scored_by"] = {"identity": None}
        pj.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        r = run(c, "tools/check_register.py")
        case("an unexplained null scorer fails too", r.returncode == 1)
        pj.write_text(original, encoding="utf-8")
        case("the registry restored cleanly",
             run(c, "tools/check_register.py").returncode == 0)
        case("no scored entry claims an independently verified score",
             not any((s.get("scored_by") or {}).get("independently_verified")
                     for s in json.loads(original)["scored"]))

        case("the prediction registry computes no aggregate calibration score",
             "No aggregate calibration score is computed" in
             (c / "docs/predictions.html").read_text(encoding="utf-8"))
        case("every record page is reachable from the contents",
             all(f'href="{f.stem}.html"' in toc
                 for f in sorted((c / "docs").glob("*.html"))
                 if is_record_page(f)))
        #  The candidate controls view. It is not a record page, so it needs its own cases --
        #  and it needs them because publishing it broke CI on the reachability check while
        #  every local gate stayed green.
        #  SPLIT BY PART at 27 controls. This asserted "Protected control plane" appeared on
        #  controls.html, which stopped being true when the register was partitioned: that
        #  control needs a second key holder, so it lives in Part B. The ordering claim belongs
        #  against the WHOLE register, which is the download.
        controls = (c / "docs/controls.html")
        whole = (c / "docs/artifacts/controls.md")
        case("Part A of the candidate controls is published", controls.is_file())
        case("...and is linked from the landing page", 'href="controls.html"' in index)
        #  Parts are asked of the builder, not listed. Part D outgrew a page and split into D1…Dn
        #  by subject; a literal ("b", "c", "d") would have gone on passing against a file the
        #  builder had stopped producing, which is this record's dominant failure wearing a
        #  different hat -- a green check not downstream of what it certifies.
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "_bcp_parts", c / "tools" / "build_controls_page.py")
        _bcp = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_bcp)
        _parts = [k for k, _t, _b, _i in _bcp.partitions() if k != "A"]
        case(f"...and every other part is published ({len(_parts)}: {', '.join(_parts)})",
             bool(_parts) and
             all((c / f"docs/controls-{k.lower()}.html").is_file() for k in _parts))
        case("...and no part page is orphaned by the split",
             not [p for p in (c / "docs").glob("controls-*.html")
                  if p.name not in {f"controls-{k.lower()}.html" for k in _parts}])
        case("...and the whole register is downloadable for hashing", whole.is_file())
        case("...and controls.md indexes the parts and the download",
             (c / "docs/controls.md").is_file() and
             "artifacts/controls.md" in (c / "docs/controls.md").read_text(encoding="utf-8"))
        case("...and status leads rank in the whole register",
             whole.is_file() and
             whole.read_text(encoding="utf-8").index("ELIGIBLE") <
             whole.read_text(encoding="utf-8").index("Protected control plane"))
        case("...and every part states that no control establishes alignment of a more "
             f"capable system (across {len(_parts) + 1} parts)",
             all("more capable than its operators" in
                 (c / f"docs/controls{sfx}.html").read_text(encoding="utf-8")
                 for sfx in [""] + [f"-{k.lower()}" for k in _parts]))

        challenge = (c / "docs/challenge.html")
        case("the implementation challenge is published", challenge.is_file())
        case("...and is linked from the landing page", 'href="challenge.html"' in index)
        case("...and has a markdown alternate", (c / "docs/challenge.md").is_file())
        #  Read the MARKDOWN, not the HTML: emphasis markup splits a phrase across tags, so a
        #  substring test against rendered HTML fails on content that is plainly present.
        challenge_md = (c / "docs/challenge.md")
        case("...and asks for the implementer's questions, not just the artifact",
             #  The document says "question you had to guess at" (singular). The first version
             #  of this case asserted the PLURAL, a phrase that appears nowhere -- a test written
             #  from what its author believed he had written rather than from the file.
             challenge_md.is_file() and "question you had to guess at" in
             challenge_md.read_text(encoding="utf-8"))
        case("...and tells the reader not to read our implementation first",
             challenge_md.is_file() and "Do not read" in
             challenge_md.read_text(encoding="utf-8"))

        case("no published page exceeds the token budget",
             run(c, "tools/check_page_budget.py").returncode == 0)
        case("every record page has a markdown alternate, declared and present",
             all('rel="alternate"' in f.read_text(encoding="utf-8")
                 and f.with_suffix(".md").exists()
                 for f in sorted((c / "docs").glob("*.html"))
                 if is_record_page(f)))
        case("hashes are published whole, not truncated",
             "…</code>" not in record and "sha256 <code" in record)
        case("a founding excerpt carries its slice provenance",
             "excerpt sha256" in record and "cut from" in record)
        # Written plainly. The first attempt at this was a one-liner whose condition
        # was `not path.write_text(...)` -- write_text returns a character count, so
        # the ternary always took its else branch and the case passed without
        # testing anything. A vacuous test is worse than no test: it reports a
        # control that does not exist.
        orphan = c / "docs/zz-orphan.html"
        orphan.write_text("<html>stale</html>", encoding="utf-8")
        case("a stale page exists before the build", orphan.exists())
        run(c, "tools/build_viewer.py")
        case("a stale page is removed by the next build", not orphan.exists())
        case("the record is readable without scripting",
             "<details>" in record and ".body{display:none}" not in record)
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
