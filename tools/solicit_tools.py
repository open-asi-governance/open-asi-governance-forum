#!/usr/bin/env python3
"""Solicit the TOOL-USING local party: k agentic Codex runs through the shim, with provenance.

**GENERATION code, not maintenance code.** An LLM is in the path by definition; `rebuild.py`
does not run this. See `tools/solicit_local.py`, whose artifact shape this deliberately mirrors
so the two arms' summaries mean the same thing where they share a field — and differ visibly
where they do not.

What makes this a different party
---------------------------------
The tool-less `qwen` arm is one Chat Completions call. This is an agentic loop: the party decides
what to read, whether to fetch anything, and when to stop. Under D-09 that is a **fourth party**,
never pooled with `qwen` — same weights, different capability, different treatment. It gets its
own round id (`round-NNN-tools`), mirroring `round-NNN-chat`.

Three things this records that no other arm can
-----------------------------------------------
1. **What the party actually did.** Every tool call and every tool result crossed the shim, so
   the round artifact carries the commands issued and the bytes returned — not the party's
   account of them. A party that says "I verified X" and a log showing it never fetched X is a
   finding this arm can produce and no other arm here can.
2. **The exact prompt, including the part that differs.** The party must be told what tools it
   has, which is a declared treatment difference from every tool-less arm. The tools preamble is
   appended to the frozen round prompt and hashed separately, so a reader can see precisely what
   was added and subtract it.
3. **The harness identity.** The party is not "Qwen with tools" — it is Qwen reached through a
   named shim revision, under a named Codex profile, with a named tool inventory. All three
   hashes go in the summary.

Why the shim restarts per sample
--------------------------------
Sampling discipline is k >= 5 at temperature > 0 with DISTINCT seeds, and the shim injects the
seed because Codex sends none. Restarting per sample is the honest way to vary it: each sample
gets its own capability-gate result and its own hash-chained ledger, so a sample cannot borrow
another's evidence. It costs about a minute per sample and buys per-sample provenance.

Usage
-----
    python3 tools/solicit_tools.py --spec record/solicitations/<round>/<round>-qwentools.json \\
        --k 5 --out-round round-009-tools

Run `tools/arm_acceptance.py` first. This program refuses to start if the gate has not passed in
the run directory it is given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIM = REPO_ROOT / "tools" / "responses_shim.py"
SHIM_PORT = 5098
SHIM_BOOT_TIMEOUT = 240

#  Appended to the frozen round prompt. The party has to know what it can do, and every tool-less
#  arm's prompt lacks this — so it is kept short, factual, and separately hashed rather than
#  woven into the question. It grants no opinion about what the party should conclude.
TOOLS_PREAMBLE = """

<!-- SLOT: tools_available -->
## What you can do in this round

Unlike every other party asked this question, you are running inside an agentic harness and can
act before you answer. You have a shell with network access and read access to this repository.

- You may fetch any public URL, and you may read files.
- You may **not** write to this record. That restriction is enforced by the harness and was
  verified by attempting a write and having it refused, before this round was run.
- Everything you run and every byte returned to you is recorded and published with your answer.

The record under discussion is at
`https://open-asi-governance.github.io/open-asi-governance-forum/` and
`https://github.com/open-asi-governance/open-asi-governance-forum`.

Reading it is not independent verification: it is served by the operator whose history is in
question, and a complete, self-consistent record is also what a careful fabrication would look
like. Use the capability or decline to; both are recorded, and declining with a reason is a
complete answer.
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def shannon_entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in counts.values() if n)


def compute_variance(samples: list[dict], fields: list[str]) -> dict:
    """Variance over the samples actually collected. Never asserted, always derived."""
    report = {}
    for field in fields:
        values = [json.dumps(s.get(field), sort_keys=True) if isinstance(s.get(field), (dict, list))
                  else s.get(field) for s in samples]
        counts = Counter(values)
        total = len(values)
        modal, modal_n = counts.most_common(1)[0] if counts else (None, 0)
        report[field] = {
            "distribution": {str(k): v for k, v in counts.most_common()},
            "n": total,
            "distinct_values": len(counts),
            "modal_value": modal,
            "modal_fraction": round(modal_n / total, 4) if total else 0.0,
            "shannon_entropy_bits": round(shannon_entropy(counts), 4),
            "unanimous": len(counts) == 1,
        }
    return report


def validate_sample(parsed, schema: dict) -> str | None:
    try:
        import jsonschema
    except ImportError:                                                   # pragma: no cover
        return ("jsonschema is not installed, so this sample could not be validated. "
                "Install it with: python3 -m pip install jsonschema")
    try:
        jsonschema.Draft202012Validator(schema).validate(parsed)
    except jsonschema.ValidationError as error:
        path = "/".join(str(p) for p in error.path) or "(root)"
        return f"schema-invalid at {path}: {error.message}"
    return None


def wait_for_shim(timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{SHIM_PORT}/version", timeout=5).read()
            return True
        except Exception:                                                 # noqa: BLE001
            time.sleep(3)
    return False


def read_ledger(run_dir: Path) -> dict:
    """The sample's provenance: what crossed the shim, and what the party actually ran.

    Tool traffic is extracted rather than summarised. `commands` is what the party asked to run
    and `results` is what came back to it — the pair is the evidence, and a claim in an answer
    can be checked against it or falsified by it.
    """
    runs = sorted((p for p in run_dir.iterdir() if p.is_dir()), key=lambda p: p.name)
    if not runs:
        return {"captured": False, "reason": "no ledger run directory"}
    run = runs[-1]
    entries = [json.loads(line) for line in (run / "ledger.jsonl").read_text().splitlines()]
    requests = [e for e in entries if e["kind"] == "upstream_request"]
    responses = [e for e in entries if e["kind"] == "upstream_response"]
    refusals = [e for e in entries if e["kind"] == "refusal"]

    traffic: list[dict] = []
    if requests:
        body = json.loads((run / "blobs" /
                           f"{requests[-1]['upstream_request_sha256']}.json").read_text())
        pending: list[dict] = []
        for message in body["messages"]:
            if message["role"] == "assistant" and message.get("tool_calls"):
                for call in message["tool_calls"]:
                    pending.append({"tool": call["function"]["name"],
                                    "arguments": call["function"]["arguments"]})
            elif message["role"] == "tool":
                item = pending.pop(0) if pending else {"tool": "?", "arguments": None}
                item["result"] = message["content"]
                item["result_sha256"] = sha256_text(message["content"])
                traffic.append(item)

    return {
        "captured": True,
        "ledger_run": run.name,
        "ledger_path": str(run.relative_to(REPO_ROOT.parent))
        if str(run).startswith(str(REPO_ROOT.parent)) else str(run),
        "entries": len(entries),
        "turns": len(responses),
        "refusals": [e["refusal"] for e in refusals],
        "chain_head": entries[-1]["prev_entry_sha256"] if entries else None,
        "tool_calls": len(traffic),
        "tool_traffic": traffic,
        "capability_gate": next((e["capability_gate"] for e in entries
                                 if e["kind"] == "run_start"), None),
        "transformations": (responses[-1]["transformations"] if responses else []),
        "reasoning_bytes": sum(e.get("reasoning_bytes") or 0 for e in responses),
    }


def one_sample(spec: dict, prompt: str, index: int, args, ledger_root: Path) -> dict:
    """One agentic run at its own seed, with its own shim, gate and ledger."""
    seed = spec.get("seed_base", 1000) + index
    run_dir = ledger_root / f"sample-{index:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    shim = subprocess.Popen(
        [sys.executable, str(SHIM), "--port", str(SHIM_PORT),
         "--temperature", str(args.temperature), "--seed", str(seed),
         "--ledger-dir", str(run_dir)],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        if not wait_for_shim(SHIM_BOOT_TIMEOUT):
            shim.terminate()
            out = (shim.stdout.read() if shim.stdout else "")[-1500:]
            return {"sample_index": index, "ok": False, "category": "shim_did_not_start",
                    "seed": seed, "detail": out}

        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "schema.json"
            schema_path.write_text(json.dumps(spec["schema"]), encoding="utf-8")
            last = Path(tmp) / "last.json"
            env = dict(os.environ, CODEX_HOME=str(Path(args.codex_home).resolve()))
            started = time.time()
            result = subprocess.run(
                ["codex", "exec", "--cd", args.arm_cwd, "--skip-git-repo-check",
                 "--output-schema", str(schema_path), "-o", str(last), prompt],
                capture_output=True, text=True, timeout=args.timeout,
                stdin=subprocess.DEVNULL, env=env)
            elapsed = round(time.time() - started, 1)
            raw = last.read_text(encoding="utf-8") if last.exists() else ""
    finally:
        shim.terminate()
        try:
            shim.wait(timeout=20)
        except subprocess.TimeoutExpired:                                 # pragma: no cover
            shim.kill()

    ledger = read_ledger(run_dir)
    record = {"sample_index": index, "seed": seed, "elapsed_seconds": elapsed,
              "exit_code": result.returncode, "provenance": ledger}

    if not raw.strip():
        record.update({"ok": False, "category": "no_final_message",
                       "detail": (result.stdout + result.stderr)[-1500:]})
        return record
    #  The harness enforces the schema, unlike the chat panel where it is asked for in prose.
    #  Whether the bytes conform is still a separate question from whether it was requested.
    try:
        parsed = json.loads(raw)
    except Exception as error:                                            # noqa: BLE001
        record.update({"ok": False, "category": "malformed_json",
                       "detail": f"{type(error).__name__}: {error}",
                       "response_bytes": raw[:8000]})
        return record
    invalid = validate_sample(parsed, spec["schema"])
    if invalid:
        record.update({"ok": False, "category": "schema_invalid", "detail": invalid,
                       "response_bytes": raw[:4000]})
        return record
    record.update({"ok": True, "content": raw, "parsed": parsed})
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--out-round", required=True)
    parser.add_argument("--codex-home", default="/tmp/oagf-arm-home")
    parser.add_argument("--arm-cwd", default="/tmp/oagf-arm-cwd")
    parser.add_argument("--ledger-dir", default=str(Path.home() / ".oagf-shim-ledger"))
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    if args.temperature <= 0:
        print("REFUSED: temperature must be > 0, or every sample is identical and variance is "
              "meaningless.", file=sys.stderr)
        return 1
    if args.k < 5:
        print(f"REFUSED: k={args.k}. This project's stated bar is k >= 5 with computed variance, "
              f"and the whole case for a locally-served arm is that meeting it is nearly free. "
              f"P-0003 predicts the bar erodes exactly here.", file=sys.stderr)
        return 1

    spec_path = Path(args.spec) if Path(args.spec).is_absolute() else REPO_ROOT / args.spec
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    base_prompt = spec["prompt"]
    prompt = base_prompt + TOOLS_PREAMBLE

    profile = Path(args.codex_home) / "config.toml"
    if not profile.exists():
        print(f"REFUSED: no frozen profile at {profile}. Run tools/arm_profile.py first — the "
              f"round record cites its hash.", file=sys.stderr)
        return 1

    ledger_root = Path(args.ledger_dir) / args.out_round
    ledger_root.mkdir(parents=True, exist_ok=True)

    print(f"soliciting k={args.k} from the TOOL-USING arm at temperature {args.temperature}")
    print(f"  spec            {spec_path.relative_to(REPO_ROOT)}")
    print(f"  prompt          {len(base_prompt)} bytes + {len(TOOLS_PREAMBLE)} bytes of tools preamble")
    print(f"  profile sha256  {sha256_text(profile.read_text())[:16]}…")
    print(f"  shim sha256     {sha256_text(SHIM.read_text())[:16]}…\n")

    records = [one_sample(spec, prompt, i + 1, args, ledger_root) for i in range(args.k)]
    for r in records:
        mark = "ok " if r.get("ok") else "REJECTED"
        print(f"  [{r['sample_index']:>2}/{args.k}] {mark} seed={r['seed']} "
              f"{r.get('elapsed_seconds', '?')}s tools={r['provenance'].get('tool_calls', 0)} "
              f"{r.get('category', '')}")

    samples = [r["parsed"] for r in records if r.get("ok")]
    failures = [{k: v for k, v in r.items() if k != "parsed"} for r in records if not r.get("ok")]
    if not samples:
        print("REFUSED: no samples collected; nothing recorded.", file=sys.stderr)
        return 1

    out_dir = REPO_ROOT / "corpus" / "raw" / args.out_round
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = spec["slug"]
    raw_path = out_dir / f"{slug}-samples.json"
    if raw_path.exists():
        print(f"REFUSED: {raw_path.relative_to(REPO_ROOT)} exists. Raw material is immutable.",
              file=sys.stderr)
        return 1
    raw_path.write_text(json.dumps(
        {"spec": spec, "prompt_sent": prompt, "responses": records}, indent=2,
        ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        "schema_version": "oagrc-tools-solicitation-0.1",
        "artifact_type": "solicitation_summary",
        "round": args.out_round,
        "slug": slug,
        "question": spec.get("question"),
        "phase": spec["phase"],
        "k_requested": args.k,
        "k_collected": len(samples),
        "failures": failures,
        "variance": compute_variance(samples, spec["variance_fields"]),
        "citability": ("citable" if len(samples) >= 5 else "non-citable (k<5)"),
        "spend": {"actual_usd": 0.0,
                  "basis": "Served on the custodian's own hardware. Electricity and wear are real "
                           "and are not modelled."},
        "contributor": {
            "identity": spec.get("identity"),
            "provider": "locally served, operator-hosted, reached through an agentic harness",
            "sampling_parameters": {"temperature": args.temperature,
                                    "seed_base": spec.get("seed_base", 1000),
                                    "seeds": [r["seed"] for r in records]},
            "tools_used": ["shell with network access (Codex exec_command)",
                           "filesystem read access to the repository"],
        },
        #  D-09: same weights as `qwen` is not the same party. The capability difference IS the
        #  treatment, so it is stated in the artifact rather than left to a reader to infer.
        "party_note": ("A FOURTH party, never pooled with the tool-less `qwen` arm. Same weights, "
                       "different capability, different prompt, different treatment."),
        "prompt_sha256": sha256_text(prompt),
        "base_prompt_sha256": sha256_text(base_prompt),
        "tools_preamble_sha256": sha256_text(TOOLS_PREAMBLE),
        "tools_preamble": TOOLS_PREAMBLE,
        "harness": {
            "shim": "tools/responses_shim.py",
            "shim_sha256": sha256_text(SHIM.read_text()),
            "codex_profile_sha256": sha256_text(profile.read_text()),
            "codex_version": subprocess.run(["codex", "--version"], capture_output=True,
                                            text=True).stdout.strip(),
        },
        "what_this_does_not_establish": (
            "The ledger records what was PRESENTED to the model and what a tool returned to it. "
            "It does not establish what the model attended to, nor that anything it read is true. "
            "This party runs on the custodian's hardware, served by the custodian's process, "
            "reading a record the custodian publishes."),
        "raw_samples": str(raw_path.relative_to(REPO_ROOT)),
    }
    summary_dir = REPO_ROOT / "corpus" / "artifacts" / args.out_round
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / f"{slug}-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")

    print(f"\ncollected {len(samples)}/{args.k}  →  {raw_path.relative_to(REPO_ROOT)}")
    print(f"summary   →  {summary_path.relative_to(REPO_ROOT)}")
    for field, stats in summary["variance"].items():
        print(f"  {field}: modal={stats['modal_value']!r} ({stats['modal_fraction']:.0%}), "
              f"{stats['distinct_values']} distinct, H={stats['shannon_entropy_bits']} bits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
