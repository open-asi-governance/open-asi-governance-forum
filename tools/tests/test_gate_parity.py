#!/usr/bin/env python3
"""Criterion A7: the JavaScript preview gates and the Python gates must agree.

    python3 tools/tests/test_gate_parity.py

Runs tools/capture_ui/gates.js under node and tools/capture_gates.py under python
over the same cases, and fails if any verdict or score disagrees. Two
implementations of one rule is a drift hazard; this makes the drift a build
failure rather than a hope.

WHAT THIS DOES NOT ESTABLISH. Agreement between two implementations written by the
same author is differential consistency, not ground truth -- both can be wrong
together, which is the D-25 failure mode. Correctness comes from
test_capture_gates.py, which checks behaviour against the real corpus. This checks
only that the preview does not lie about what ingest will do.

Skips with a clear message if node is unavailable, rather than passing silently --
a check that reports success when it did not run is D-29's own subject.
"""

from __future__ import annotations

import glob
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from capture_gates import lifecycle_state, run_gates, sent_prompt_text   # noqa: E402

NODE = shutil.which("node")
if NODE is None:
    print("SKIP  node is not available; the JS preview gates were NOT checked against Python.")
    print("      This is a skip, not a pass. Criterion A7 is unverified in this environment.")
    sys.exit(0)


def build_cases() -> list[dict]:
    """Real corpus captures, plus the constructed failures, plus the false-positive guards."""
    cases: list[dict] = []
    prompt2 = None
    for f in sorted(glob.glob(str(ROOT / "corpus/artifacts/*/*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if d.get("artifact_type") != "contribution":
            continue
        resp = (ROOT / d["raw"]["path"]).read_text(encoding="utf-8")
        prompt = sent_prompt_text((ROOT / d["prompt"]["path"]).read_text(encoding="utf-8"))
        if "review-round-02/" in d["round"] + "/":
            prompt2 = prompt
        cases.append({"label": f"real:{d['round']}/{d['contributor']['identity']}",
                      "response": resp, "prompt": prompt, "existing": {}})

    p = prompt2 or cases[0]["prompt"]
    words = p.split()
    cases += [
        {"label": "empty",              "response": "",              "prompt": p, "existing": {}},
        {"label": "whitespace",         "response": "  \n\t \n",     "prompt": p, "existing": {}},
        {"label": "prompt verbatim",    "response": p,               "prompt": p, "existing": {}},
        {"label": "short legit reply",
         "response": "The corrections to my items are faithful, no further findings.",
         "prompt": p, "existing": {}},
        {"label": "no terminal punctuation", "response": "A review ending mid-tabl", "prompt": p, "existing": {}},
        # Unicode and composition: NFC normalisation must agree across languages.
        {"label": "unicode composition", "response": "café " * 200 + "naïve résumé.", "prompt": p, "existing": {}},
        {"label": "fenced code block",
         "response": "Here is my finding.\n\n```json\n{\"a\": 1}\n```\n\n" + "Real analysis text. " * 60,
         "prompt": p, "existing": {}},
        {"label": "duplicate same party", "response": cases[0]["response"], "prompt": cases[0]["prompt"],
         "existing": {"prior.md": cases[0]["response"]}},
    ]
    for frac in (0.10, 0.30, 0.50, 0.90):
        cases.append({"label": f"partial paste {int(frac*100)}%",
                      "response": " ".join(words[:int(len(words) * frac)]),
                      "prompt": p, "existing": {}})
    return cases


CASES = build_cases()

RUNNER = r"""
const g = require(process.argv[2]);
const cases = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));
const out = cases.map(c => {
  const results = g.runGates(c.response, c.prompt, c.existing);
  const ls = g.lifecycleState(results);
  const sat = results.find(r => r.gate === 'G2c-prompt-saturation');
  return {
    label: c.label,
    state: ls.state,
    failed: results.filter(r => !r.passed).map(r => r.gate).sort(),
    saturation: sat && sat.scores ? Number(sat.scores.saturation.toFixed(4)) : null,
    coverage:   sat && sat.scores ? Number(sat.scores.coverage.toFixed(4))   : null,
    shingles:   sat && sat.scores ? sat.scores.shingles : null,
  };
});
process.stdout.write(JSON.stringify(out));
"""

scratch = ROOT / "tools" / "tests" / ".parity-cases.json"
runner = ROOT / "tools" / "tests" / ".parity-runner.js"
try:
    scratch.write_text(json.dumps(CASES), encoding="utf-8")
    runner.write_text(RUNNER, encoding="utf-8")
    proc = subprocess.run(
        [NODE, str(runner), str(ROOT / "tools/capture_ui/gates.js"), str(scratch)],
        capture_output=True, text=True,
    )
finally:
    scratch.unlink(missing_ok=True)
    runner.unlink(missing_ok=True)

if proc.returncode != 0:
    print("FAIL  node could not run the JS gates:")
    print(proc.stderr.strip()[:2000])
    sys.exit(1)

js = {r["label"]: r for r in json.loads(proc.stdout)}

failures = []
for case in CASES:
    results = run_gates(case["response"], case["prompt"], case["existing"])
    state, _ = lifecycle_state(results)
    sat = next((r for r in results if r.gate == "G2c-prompt-saturation"), None)
    py = {
        "state": state,
        "failed": sorted(r.gate for r in results if not r.passed),
        "saturation": round(sat.scores["saturation"], 4) if sat and sat.scores else None,
        "coverage": round(sat.scores["coverage"], 4) if sat and sat.scores else None,
        "shingles": sat.scores["shingles"] if sat and sat.scores else None,
    }
    other = js.get(case["label"])
    if other is None:
        failures.append(f"{case['label']}: JS produced no result")
        continue
    for key in ("state", "failed", "saturation", "coverage", "shingles"):
        if py[key] != other[key]:
            failures.append(f"{case['label']}: {key} — python {py[key]!r} vs js {other[key]!r}")

print(f"gate parity over {len(CASES)} cases (python vs node)")
print(f"{len(CASES) - len({f.split(':')[0] for f in failures})} agreed, {len(failures)} disagreements")
for f in failures:
    print(f"  FAIL  {f}")
sys.exit(1 if failures else 0)
