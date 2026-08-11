#!/usr/bin/env python3
"""Daily watch on every surface an outside party could arrive through.

    python3 tools/watch_arrivals.py

WHY. `CHALLENGE.md` tells implementers to **open an issue on this repository**, and until
2026-08-11 nobody was watching it. Prediction P-0031 — that no outside party attempts a FICP
verifier by 2026-10-05 — would most likely be falsified by an issue appearing here, so the surface
the challenge names is the surface that must be checked.

Every query ships with a **negative control**: the identical call against a repository known to
have the thing being counted. An empty result and a broken query are indistinguishable, and this
record has published a false zero before. If a control returns nothing, the tool reports the query
as BROKEN rather than reporting a zero.

READING THE TRAFFIC NUMBERS — the trap is baked in here so it does not have to be remembered.
On 2026-08-11 this repository had **195 unique cloners and 2 unique visitors**. Clone counts
include CI, mirrors, scrapers and training-data crawlers; a clone is not a reader. The visitor
count is the human-ish number and one of those two is probably the custodian. **Reporting the
clone count as interest would be exactly the flattering aggregate this record keeps having to
correct.** The tool prints both, always, adjacent.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

REPO = "open-asi-governance/open-asi-governance-forum"
#  Known to have issues, forks and stars. If a control comes back empty the query shape is wrong.
CONTROL_REPO = "singnet/snet-daemon"


def api(path: str):
    token = os.environ.get("GH_TOKEN_OAGF") or os.environ.get("GH_TOKEN") or ""
    env = dict(os.environ, GH_TOKEN=token) if token else dict(os.environ)
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, env=env)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except Exception:                                                    # noqa: BLE001
        return None


def counted(path_tmpl: str, label: str) -> tuple[str, int | None]:
    """Run a query and its negative control. Returns (verdict, count-or-None)."""
    real = api(path_tmpl.format(repo=REPO))
    control = api(path_tmpl.format(repo=CONTROL_REPO))
    if real is None or control is None:
        return (f"{label}: QUERY FAILED — reporting nothing rather than zero", None)
    n, c = len(real), len(control)
    if c == 0:
        return (f"{label}: BROKEN — the negative control on {CONTROL_REPO} also returned 0, "
                f"so a zero here means nothing", None)
    return (f"{label}: {n}   (control {CONTROL_REPO}: {c} — query works)", n)


def main() -> int:
    print(f"  arrivals watch — {REPO}\n")
    arrivals = 0
    unknown: list[str] = []
    for tmpl, label in (
        ("repos/{repo}/issues?state=all&per_page=50", "issues and PRs, all states"),
        ("repos/{repo}/forks", "forks"),
    ):
        verdict, n = counted(tmpl, label)
        print(f"    {verdict}")
        if n is None:
            unknown.append(label)
        else:
            arrivals += n

    #  Stars come from the repo object, not /stargazers, which this token cannot read (403).
    #  Its negative control is the same field on a repo known to have stars.
    mine, ctrl = api(f"repos/{REPO}"), api(f"repos/{CONTROL_REPO}")
    if mine is None or ctrl is None or not ctrl.get("stargazers_count"):
        print("    stars: QUERY FAILED or control empty — reporting nothing rather than zero")
        unknown.append("stars")
    else:
        #  NO DEFAULT. `.get("stargazers_count", 0)` would report zero stars when the field is
        #  ABSENT, which is the absence-as-zero defect this whole tool exists to avoid -- found
        #  by C53a in scan_own_code.py, in code written the same day, hours after fixing the
        #  neighbouring branch for claiming absence it had not checked.
        n = mine.get("stargazers_count")
        if n is None:
            print("    stars: FIELD ABSENT from the repo object — unknown, not zero")
            unknown.append("stars")
        else:
            print(f"    stars: {n}   (control {CONTROL_REPO}: {ctrl['stargazers_count']} — works)")
            arrivals += n

    print()
    views = api(f"repos/{REPO}/traffic/views") or {}
    clones = api(f"repos/{REPO}/traffic/clones") or {}
    v, vu = views.get("count"), views.get("uniques")
    c, cu = clones.get("count"), clones.get("uniques")
    print(f"    visitors (14d):  {v} views, {vu} unique")
    print(f"    clones   (14d):  {c} clones, {cu} unique")
    if isinstance(cu, int) and isinstance(vu, int) and vu and cu > vu * 5:
        print(f"    ^ {cu} cloners against {vu} visitors. That ratio is machines — CI, mirrors,")
        print("      scrapers, training-data crawlers. A clone is not a reader, and the clone")
        print("      count is NOT evidence of interest. Do not report it as such.")

    print()
    if arrivals:
        print(f"  {arrivals} arrival(s) on a surface an outsider could use. READ THEM.")
        print("  If it is an implementation attempt, P-0031 resolves NEGATIVE and the mothball")
        print("  checkpoint does not fire on that limb.")
    elif unknown:
        #  NEVER claim absence for a surface that was not checked. The first version of this
        #  summary printed "No issue, fork or star" while the stars query had failed -- a false
        #  zero, in the tool written to prevent false zeros.
        print(f"  Nothing on the surfaces that could be checked, but {len(unknown)} could NOT be "
              f"checked: {', '.join(unknown)}.")
        print("  That is UNKNOWN, not zero, and P-0031 cannot be assessed from a partial sweep.")
    else:
        print("  No issue, fork or star. P-0031 remains open and on track to resolve positive.")
    print("\n  This checks the surfaces the challenge names. Someone could build a verifier and")
    print("  never tell us, and nothing here would see it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
