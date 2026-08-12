#!/usr/bin/env python3
"""Conformance tests for the lease's ACTION bound — D-64.

    python3 tools/tests/test_lease_bounds.py

Every fixture here asserts at the **effect boundary** (control 64), not at the refusal signal.
A refusal that raises the right exception and lets the action happen anyway is the failure this
project filed D-62 about, and the test that would have caught it has to look at the world rather
than at stderr. So each case calls `governed_effect()`, which does the same two things a real
caller does — ask the lease, then act — and the assertion is that **the sentinel file does not
exist**. `pytest.raises` alone would pass on a lease that refuses in words and admits in fact.

There is a positive control at the bottom for the reason every refusal suite needs one: a lease
that refuses *everything* would pass all eight refusal cases. If `test_admits_under_the_bound`
ever fails, the other results here mean nothing.

WHAT THIS REPLACES. `test_max_actions_is_enforced_not_merely_recorded` in test_executive_log.py
was vacuous twice over: it read the **real** action log, so its result depended on ambient
repository history, and its success branch called `check(..., True)` when `require()` did **not**
refuse. It passed under both outcomes. Codex found it on 2026-08-12 while reviewing the D-64 fix,
which makes it the seventh consecutive defect located in the checking apparatus rather than in
the thing checked.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import executive_lease as lease                                           # noqa: E402

PASSED = FAILED = 0


def check(label: str, cond: bool) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  \033[32m✓\033[0m {label}")
    else:
        FAILED += 1
        print(f"  \033[31m✗ {label}\033[0m")


#  ---------------------------------------------------------------------------
#  The world these fixtures act on.
#  ---------------------------------------------------------------------------

def workspace() -> Path:
    return Path(tempfile.mkdtemp())


def write_lease(dirpath: Path, *, max_actions, expires="2099-01-01T00:00:00Z",
                granted="2026-01-01T00:00:00Z") -> Path:
    path = dirpath / "leases.jsonl"
    path.write_text(json.dumps({
        "lease_id": "fixture", "granted_utc": granted, "expires_utc": expires,
        "granted_by": "fixture", "evidence": "fixture", "max_actions": max_actions,
        "note": "", "supersedes": None, "authority": "fixture"}) + "\n", encoding="utf-8")
    return path


def write_log(dirpath: Path, rows: int, *, corrupt: str = "") -> Path:
    """A CHAIN-VALID action log of `rows` rows, unless asked to damage it.

    The chain has to be built properly even for tests that never look at it, because a fixture
    whose log is accidentally broken would pass the "unrecorded break refuses" case for the wrong
    reason and pass it forever.
    """
    path = dirpath / "action-log.jsonl"
    lines, prev = [], "0" * 64
    for i in range(rows):
        row = {"utc": f"2026-06-01T00:00:{i:02d}Z", "action": "test", "note": f"row {i}",
               "prev_sha256": prev}
        prev = hashlib.sha256(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        lines.append(json.dumps(row))
    if corrupt == "unparseable" and lines:
        lines[-1] = "{not json at all"
    if corrupt == "no_utc" and lines:
        row = json.loads(lines[-1])
        del row["utc"]
        lines[-1] = json.dumps(row)
    if corrupt == "chain" and len(lines) > 1:
        row = json.loads(lines[-2])
        row["note"] = "rewritten after the fact"      # breaks the NEXT row's prev_sha256
        lines[-2] = json.dumps(row)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return path


def governed_effect(sentinel: Path, log: Path | None = None) -> None:
    """Ask, then act — the shape of every real caller.

    The sentinel write is what a landing, a round or a Codex call would do. It must never happen
    on a refused path, and "must never happen" is a statement about this file existing, not about
    which exception came back.
    """
    lease.require("governed_write", log_path=log)
    sentinel.write_text("the governed action ran", encoding="utf-8")


def refuses(label: str, *, max_actions, rows: int, corrupt: str = "",
            expected: type[BaseException], expires: str = "2099-01-01T00:00:00Z",
            log: bool = True, discontinuities: str | None = None) -> None:
    """Run the governed effect under a fixture lease and assert BOTH halves of the refusal."""
    work = workspace()
    saved_leases, saved_disc = lease.LEASES, lease.DISCONTINUITIES
    sentinel = work / "sentinel"
    try:
        lease.LEASES = write_lease(work, max_actions=max_actions, expires=expires)
        source = write_log(work, rows, corrupt=corrupt) if log else work / "absent"
        if discontinuities is not None:
            reg = work / "discontinuities.json"
            reg.write_text(discontinuities, encoding="utf-8")
            lease.DISCONTINUITIES = reg
        try:
            governed_effect(sentinel, log=source)
            check(f"{label} — NOT refused", False)
        except expected:
            #  The signal was right. Now the part that matters.
            check(f"{label} — refused, and the effect did not happen",
                  not sentinel.exists())
        except BaseException as wrong:                                    # noqa: BLE001
            check(f"{label} — raised {type(wrong).__name__}, expected "
                  f"{expected.__name__}", False)
    finally:
        lease.LEASES, lease.DISCONTINUITIES = saved_leases, saved_disc


# ---------------------------------------------------------------------------
#  The eight refusals.
# ---------------------------------------------------------------------------

print("\nthe action bound, asserted at the effect boundary")

refuses("cap reached with a readable log", max_actions=3, rows=3,
        expected=lease.LeaseBoundReached)

#  THE D-64 CASE ITSELF. Under the old code this branch set spent = 0 and ADMITTED the action.
refuses("log absent — the count is unknown, not zero", max_actions=100, rows=0, log=False,
        expected=lease.LeaseEvidenceUnavailable)

refuses("a line that does not parse", max_actions=100, rows=4, corrupt="unparseable",
        expected=lease.LeaseEvidenceUnavailable)

refuses("a row with no utc, which the old count dropped silently", max_actions=100, rows=4,
        corrupt="no_utc", expected=lease.LeaseEvidenceUnavailable)

refuses("an unrecorded break in the hash chain", max_actions=100, rows=5, corrupt="chain",
        expected=lease.LeaseEvidenceUnavailable, discontinuities='{"discontinuities": []}')

refuses("a broken chain with an unreadable discontinuity register", max_actions=100, rows=5,
        corrupt="chain", expected=lease.LeaseEvidenceUnavailable,
        discontinuities='{"this file": "has no discontinuities list"}')

#  `if cap:` treated 0 as "no bound configured" and authorised everything.
refuses("a cap of zero means nothing may begin", max_actions=0, rows=0,
        expected=lease.LeaseBoundReached)

refuses("a cap that is not a non-negative integer", max_actions="lots", rows=1,
        expected=lease.LeaseEvidenceUnavailable)

refuses("True is not a cap of one", max_actions=True, rows=0,
        expected=lease.LeaseEvidenceUnavailable)

refuses("the calendar bound still refuses on its own", max_actions=100, rows=0,
        expires="2000-01-01T00:00:00Z", expected=lease.LeaseExpired)


# ---------------------------------------------------------------------------
#  THE POSITIVE CONTROL. Without it, a lease that refuses everything scores ten out of ten.
# ---------------------------------------------------------------------------

def test_admits_under_the_bound() -> None:
    work = workspace()
    saved_leases = lease.LEASES
    sentinel = work / "sentinel"
    try:
        lease.LEASES = write_lease(work, max_actions=100)
        governed_effect(sentinel, log=write_log(work, 3))
        check("POSITIVE CONTROL: under the bound the effect DOES happen", sentinel.exists())
    except BaseException as exc:                                          # noqa: BLE001
        check(f"POSITIVE CONTROL: under the bound the effect DOES happen — "
              f"raised {type(exc).__name__}: {exc}", False)
    finally:
        lease.LEASES = saved_leases


def test_authorised_break_is_excused_only_when_pinned() -> None:
    """The discontinuity register must excuse ONE argued edit, not a position."""
    work = workspace()
    saved = (lease.LEASES, lease.DISCONTINUITIES)
    try:
        lease.LEASES = write_lease(work, max_actions=100)
        source = write_log(work, 5, corrupt="chain")
        reg = work / "disc.json"
        lease.DISCONTINUITIES = reg

        #  Discover the break exactly as the lease does, then record it.
        reg.write_text('{"discontinuities": []}', encoding="utf-8")
        blocked = lease.count_state(lease.current(), log_path=source)
        breaks = blocked.get("breaks") or []
        check("the break is reported with both hashes, so it can be pinned",
              bool(breaks) and breaks[0].get("stored_prev_sha256")
              and breaks[0].get("computed_prev_sha256"))

        #  reason and authority are REQUIRED by the register. A break excused by four hashes
        #  and nothing else is a waiver; a tombstone records who authorised it and why.
        reg.write_text(json.dumps({"discontinuities": [
            {**{k: b[k] for k in ("utc", "action", "stored_prev_sha256",
                                  "computed_prev_sha256")},
             "reason": "fixture", "authority": "fixture"} for b in breaks]}), encoding="utf-8")
        excused = lease.count_state(lease.current(), log_path=source)
        check("a pinned, recorded break is excused and the count proceeds",
              excused["state"] == lease.COUNTED)
        check("the excused break is still REPORTED, not hidden",
              excused.get("authorised_breaks") == len(breaks))

        #  Now damage the log AGAIN at the same place. The pin must stop matching.
        rows = [json.loads(ln) for ln in
                source.read_text(encoding="utf-8").splitlines() if ln.strip()]
        rows[-3]["note"] = "and rewritten a second time"
        source.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        moved = lease.count_state(lease.current(), log_path=source)
        check("a SECOND edit at the same position is not covered by the old pin",
              moved["state"] == lease.UNAVAILABLE)
    finally:
        lease.LEASES, lease.DISCONTINUITIES = saved


def test_unavailable_is_not_called_exhausted() -> None:
    """Control 53 at the level of the words: an unknown must not be coerced into a value OR
    into the wrong refusal. A reader who sees 'exhausted' will go and ask for a renewal that
    would not have helped."""
    work = workspace()
    saved = lease.LEASES
    try:
        lease.LEASES = write_lease(work, max_actions=100)
        try:
            lease.require("governed_write", log_path=work / "absent")
            check("an unreadable count refuses", False)
        except lease.LeaseEvidenceUnavailable as refused:
            words = str(refused).lower()
            check("an unreadable count refuses", True)
            check("it is not described as expiry or exhaustion",
                  "expired" not in words and "exhaust" not in words
                  and "max_actions" not in words)
        check("LeaseEvidenceUnavailable is NOT a kind of LeaseExpired",
              not issubclass(lease.LeaseEvidenceUnavailable, lease.LeaseExpired))
        check("but every refusal is a kind of LeaseRefused, so one except catches all",
              all(issubclass(e, lease.LeaseRefused) for e in
                  (lease.LeaseExpired, lease.LeaseBoundReached,
                   lease.LeaseEvidenceUnavailable)))
    finally:
        lease.LEASES = saved


def test_cli_is_not_green_while_require_refuses() -> None:
    """The reported symptom that started this: a surface saying LIVE while a landing refuses.

    The CLI and require() now read ONE function, so this is checked by exercising the composite
    and the exit status against the same fixture rather than by trusting that they agree.
    """
    work = workspace()
    saved = lease.LEASES
    try:
        lease.LEASES = write_lease(work, max_actions=2)
        st = lease.authorization_state(log_path=write_log(work, 5))
        check("the composite reports NOT live when the count is over the cap",
              st["live"] is False and st["refusal"][0] == "bound_reached")
        check("the calendar half still says the lease has time left",
              lease.calendar_state()["live"] is True)
        check("so the two bounds are distinguishable in the report",
              st["count"]["state"] == lease.COUNTED and st["count"]["spent"] == 5)
    finally:
        lease.LEASES = saved


def test_cli_exit_status_follows_the_composite() -> None:
    """Run the real CLI in a subprocess against the REAL record. It must exit 0 only if the
    composite says live — the gate in land.py reads nothing but this exit code."""
    proc = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "executive_lease.py")],
                          capture_output=True, text=True)
    st = lease.authorization_state()
    check("the CLI's exit status matches the composite decision",
          (proc.returncode == 0) == bool(st["live"]))
    check("the CLI prints the count state, which it never used to mention",
          "count:" in proc.stdout)
    #  NOT a disjunct. The first version read `"rows appended" in proc.stdout or state !=
    #  COUNTED`, which passes whenever the count is unavailable — an escape hatch across two
    #  DIFFERENT outcomes, written this morning inside the fix for that exact class. The
    #  precondition is asserted instead, so the case fails loudly if it stops applying.
    check(f"PRECONDITION: the live count is available ({st['count'].get('state')}), so the "
          f"unit must be printed", st["count"]["state"] == lease.COUNTED)
    check("the CLI names the unit of max_actions", "rows appended" in proc.stdout)


def test_there_is_no_ambient_count_source() -> None:
    """The first repair put the fixture hook in a module GLOBAL, and Codex used it to authorise
    an exhausted lease: point `COUNT_SOURCE` at an empty file and require() returned GRANTED with
    spent 0. A hook every caller silently inherits is a fail-open wearing a test's clothes."""
    check("no module-level count-source global survives",
          not hasattr(lease, "COUNT_SOURCE"))
    work = workspace()
    st = lease.count_state(lease.current(), log_path=write_log(work, 1))
    check("an injected count source is marked in the state",
          st.get("source_is_default") is False)
    st = lease.count_state(lease.current())
    check("the real count declares itself default-sourced",
          st.get("source_is_default") is True)


def source_code() -> str:
    """The module's CODE, without its prose.

    Written as a raw-text scan first, and both assertions immediately failed — on the docstring
    sentences saying there is no `--force` and describing the old `spent = 0`. A detector that
    reads the explanation of a defect as the defect is the same false-positive shape
    `control_coverage.executable_text` was built for last night, so it is reused rather than
    re-derived. Docstrings of nested functions are stripped too: the class docstrings here quote
    the wording they forbid.
    """
    import ast as _ast
    import control_coverage as cc
    text = (REPO_ROOT / "tools" / "executive_lease.py").read_text(encoding="utf-8")
    tree = _ast.parse(text)
    for node in _ast.walk(tree):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
            #  clean=False. With the default, ast DEDENTS the docstring, so the string handed
            #  to replace() no longer matches the indented source and every nested docstring
            #  survived the strip — which is how the `import executive_log` sentence in
            #  _load_executive_log's own prose kept failing an assertion about the code.
            doc = _ast.get_docstring(node, clean=False)
            if doc:
                text = text.replace(doc, "", 1)
    return cc.executable_text(text)


def test_no_force_flag_anywhere() -> None:
    src = source_code()
    check("there is still no --force", "--force" not in src)
    check("and no environment variable can raise the cap",
          "environ" not in src and "getenv" not in src)


def test_the_defect_this_replaces_cannot_return() -> None:
    """The literal shape of D-64: a bare except that lands on a favourable default."""
    src = source_code()
    check("no 'spent = 0' default survives anywhere in the module",
          "spent = 0" not in src)
    check("the count is not read through a bare module-name import of executive_log",
          "import executive_log" not in src)
    #  The stripper itself needs a negative control, or "no match" could mean "stripped
    #  everything". It earned its place immediately: the first version looked for "def require("
    #  and failed, because the token stream is rejoined with spaces — so the two assertions
    #  above were matching against a shape the file could never contain, and would have passed
    #  forever over a module that still had the defect.
    check("STRIPPER CONTROL: real code survives the strip",
          "def require" in src and "LeaseBoundReached" in src and "raise" in src)


# ---------------------------------------------------------------------------
#  THE COUNTEREXAMPLES CODEX RAN PAST THE FIRST VERSION OF THIS FIX.
#  Each one returned COUNTED when the chain check stood alone. They are here as fixtures
#  because "a hash chain is enough" is exactly the kind of claim that sounds obviously true.
# ---------------------------------------------------------------------------

def _git(work: Path, *args) -> None:
    subprocess.run(["git", *args], cwd=work, check=True, capture_output=True)


def anchored_repo() -> tuple[Path, Path]:
    """A real git repository whose action log is COMMITTED — the external checkpoint."""
    work = workspace()
    _git(work, "init", "-q")
    _git(work, "config", "user.email", "fixture@example.invalid")
    _git(work, "config", "user.name", "fixture")
    log = work / "record" / "executive" / "action-log.jsonl"
    log.parent.mkdir(parents=True)
    rows, prev = [], "0" * 64
    for i in range(5):
        row = {"utc": f"2026-06-01T00:00:0{i}Z", "action": "test", "note": f"row {i}",
               "prev_sha256": prev}
        prev = hashlib.sha256(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        rows.append(row)
    log.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "the committed log")
    return work, log


def rows_of(log: Path) -> list[dict]:
    return [json.loads(ln) for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]


def rechain(rows: list[dict]) -> str:
    """Recompute every link, which is what a careful rewriter would do."""
    out, prev = [], "0" * 64
    for row in rows:
        row["prev_sha256"] = prev
        prev = hashlib.sha256(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        out.append(json.dumps(row))
    return "\n".join(out) + "\n"


def anchor_case(label: str, mutate, *, expect_counted: bool) -> None:
    work, log = anchored_repo()
    saved_root, saved_leases = lease.REPO_ROOT, lease.LEASES
    try:
        lease.REPO_ROOT = work
        lease.LEASES = write_lease(work, max_actions=100)
        mutate(log)
        #  log_path is NOT passed: the anchor only runs for the default source, so the fixture
        #  has to move the module's idea of the repository instead. That is the point — a test
        #  that opted out of the anchor would be testing the branch that skips it.
        #  _load_executive_log() builds a FRESH module from disk, so patching the already
        #  imported one does nothing — the first version of this fixture did exactly that and
        #  measured the real repository log while claiming to measure the temp one.
        saved_loader = lease._load_executive_log
        try:
            lease._load_executive_log = lambda: type("shim", (), {"LOG_PATH": log})
            state = lease.count_state(lease.current())
        finally:
            lease._load_executive_log = saved_loader
        got = state["state"] == lease.COUNTED
        check(f"{label} — {'counted' if expect_counted else 'REFUSED'}", got == expect_counted)
    finally:
        lease.REPO_ROOT, lease.LEASES = saved_root, saved_leases


print("\nthe external checkpoint: a chain alone cannot see any of these")

anchor_case("an untouched committed log", lambda log: None, expect_counted=True)

anchor_case("the final row rewritten and re-chained",
            lambda log: log.write_text(rechain(
                [{**r, "note": "edited"} if i == len(rows_of(log)) - 1 else r
                 for i, r in enumerate(rows_of(log))]), encoding="utf-8"),
            expect_counted=False)

anchor_case("the WHOLE history rewritten, every link recomputed",
            lambda log: log.write_text(rechain(
                [{**r, "note": "a different past"} for r in rows_of(log)]), encoding="utf-8"),
            expect_counted=False)

anchor_case("truncated to an empty but existing file",
            lambda log: log.write_text("", encoding="utf-8"), expect_counted=False)

anchor_case("the last two rows deleted, chain still valid",
            lambda log: log.write_text(
                "".join(json.dumps(r) + "\n" for r in rows_of(log)[:-2]), encoding="utf-8"),
            expect_counted=False)

anchor_case("rows APPENDED, which is the one legitimate change",
            lambda log: log.write_text(
                log.read_text(encoding="utf-8") + json.dumps(
                    {"utc": "2026-06-02T00:00:00Z", "action": "test", "note": "new",
                     "prev_sha256": hashlib.sha256(json.dumps(
                         rows_of(log)[-1], sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest()}) + "\n",
                encoding="utf-8"),
            expect_counted=True)


def test_a_stale_register_entry_does_not_excuse_a_break() -> None:
    """A registered break whose hashes no longer match must refuse — the register pins an EDIT,
    not a position. Codex reproduced a stale entry passing before the pin was exact."""
    work = workspace()
    saved = (lease.LEASES, lease.DISCONTINUITIES)
    try:
        lease.LEASES = write_lease(work, max_actions=100)
        source = write_log(work, 5, corrupt="chain")
        reg = work / "disc.json"
        lease.DISCONTINUITIES = reg
        reg.write_text(json.dumps({"discontinuities": [
            {"utc": "2026-06-01T00:00:04Z", "action": "test",
             "stored_prev_sha256": "0" * 64, "computed_prev_sha256": "f" * 64,
             "reason": "a break that was recorded once and has since moved",
             "authority": "fixture"}]}), encoding="utf-8")
        st = lease.count_state(lease.current(), log_path=source)
        check("a stale, non-matching register entry does not excuse the break",
              st["state"] == lease.UNAVAILABLE)
    finally:
        lease.LEASES, lease.DISCONTINUITIES = saved


def test_a_break_needs_a_reason_and_an_authority() -> None:
    """Four hashes and nothing else is a waiver. What makes it a tombstone is that somebody had
    to write down who authorised the edit and why."""
    work = workspace()
    saved = (lease.LEASES, lease.DISCONTINUITIES)
    try:
        lease.LEASES = write_lease(work, max_actions=100)
        source = write_log(work, 5, corrupt="chain")
        reg = work / "disc.json"
        lease.DISCONTINUITIES = reg
        reg.write_text('{"discontinuities": []}', encoding="utf-8")
        breaks = lease.count_state(lease.current(), log_path=source)["breaks"]
        bare = [{k: b[k] for k in ("utc", "action", "stored_prev_sha256",
                                   "computed_prev_sha256")} for b in breaks]
        reg.write_text(json.dumps({"discontinuities": bare}), encoding="utf-8")
        st = lease.count_state(lease.current(), log_path=source)
        check("a break recorded with no reason or authority is refused",
              st["state"] == lease.UNAVAILABLE)
        reg.write_text(json.dumps({"discontinuities": [7]}), encoding="utf-8")
        st = lease.count_state(lease.current(), log_path=source)
        check("a register entry that is not even an object refuses, and does not leak",
              st["state"] == lease.UNAVAILABLE)
    finally:
        lease.LEASES, lease.DISCONTINUITIES = saved


def test_a_timestamp_must_be_an_instant() -> None:
    """The first repair required only a non-empty string and then compared LEXICALLY. Codex fed
    it `"zzzz"` and got COUNTED."""
    work = workspace()
    saved = lease.LEASES
    try:
        lease.LEASES = write_lease(work, max_actions=100)
        for bad, label in ((("zzzz"), "a string that is not a date"),
                           ("2026-06-01T00:00:00", "a NAIVE stamp with no timezone"),
                           (17, "a number")):
            source = write_log(work, 3)
            rows = rows_of(source)
            rows[-1]["utc"] = bad
            source.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
            st = lease.count_state(lease.current(), log_path=source)
            check(f"{label} is not a usable timestamp", st["state"] == lease.UNAVAILABLE)
    finally:
        lease.LEASES = saved


def test_a_module_loaded_by_path_still_counts() -> None:
    """The trigger that made D-64 ordinary rather than exotic: `import executive_log` resolved
    only if the CALLER had tools/ on sys.path, and the bare except turned that into spent = 0."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "lease_by_path", REPO_ROOT / "tools" / "executive_lease.py")
    module = importlib.util.module_from_spec(spec)
    saved_path = list(sys.path)
    try:
        sys.path[:] = [p for p in sys.path if "open-asi-governance-forum/tools" not in p]
        spec.loader.exec_module(module)
        st = module.count_state(module.current())
        check("loaded by path with tools/ off sys.path, the count still resolves",
              st["state"] == module.COUNTED)
        check("...and it is NOT the favourable default the old code produced",
              st.get("spent", 0) > 0)
    finally:
        sys.path[:] = saved_path


def test_main_exit_follows_a_refusing_composite() -> None:
    """The CLI's exit code is the whole of land.py's `lease` gate, so it must track the
    composite even when the calendar bound is nowhere near."""
    saved = lease.authorization_state
    try:
        lease.authorization_state = lambda **kw: {
            "live": False, "lease": None, "why": "fixture refusal",
            "count": {"state": lease.UNAVAILABLE, "why": "fixture"},
            "refusal": ("evidence_unavailable", "fixture")}
        check("main() exits non-zero when the composite refuses", lease.main() != 0)
    finally:
        lease.authorization_state = saved


test_admits_under_the_bound()
test_authorised_break_is_excused_only_when_pinned()
test_unavailable_is_not_called_exhausted()
test_cli_is_not_green_while_require_refuses()
test_cli_exit_status_follows_the_composite()
test_there_is_no_ambient_count_source()
test_a_stale_register_entry_does_not_excuse_a_break()
test_a_break_needs_a_reason_and_an_authority()
test_a_timestamp_must_be_an_instant()
test_a_module_loaded_by_path_still_counts()
test_main_exit_follows_a_refusing_composite()
test_no_force_flag_anywhere()
test_the_defect_this_replaces_cannot_return()

#  KEEP THE SUMMARY AND EXIT LAST. Tests appended after them do not get counted, and the file
#  then reports a stale total that looks like a pass.
print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
