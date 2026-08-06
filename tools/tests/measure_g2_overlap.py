#!/usr/bin/env python3
"""Measure the two-sided shingle overlap proposed for gate G2, on real corpus data.

Validation record: record/designs/T13-g2-rule-validation.md

This is measurement, not a committed coding rule. D-25 requires a rule be validated
against a hand-checked subset BEFORE it scores anything; this produces the numbers
that validation would rest on, so the threshold is derived rather than chosen.

Negatives (must NOT fire): every real capture against the prompt it cites.
Positives (MUST fire):     each prompt file treated as its own reply (synthetic),
                           plus the genuine D-10 case from the founding transcript.
"""
import json, re, glob, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
N = 8

def normalise(text: str) -> list[str]:
    t = text.lower()
    t = re.sub(r"```.*?```", " ", t, flags=re.S)      # fenced code
    t = re.sub(r"[^a-z0-9\s]", " ", t)                 # markdown/punctuation
    return t.split()

def shingles(text: str, n: int = N) -> set:
    w = normalise(text)
    if len(w) < n:
        return set()
    return {tuple(w[i:i+n]) for i in range(len(w) - n + 1)}

def two_sided(prompt: str, response: str) -> tuple[float, float, int]:
    P, R = shingles(prompt), shingles(response)
    if not P or not R:
        return 0.0, 0.0, 0
    inter = P & R
    return len(inter)/len(P), len(inter)/len(R), len(inter)

def sent_text(path: pathlib.Path) -> str:
    """Extract what was ACTUALLY SENT: the '> '-prefixed blockquote, de-prefixed.

    The committed prompt files wrap the outbound text in a blockquote and surround it
    with metadata and capture requirements that were never sent. Anchoring the whole
    file as `prompt` therefore hashes material the model never saw.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    quoted = [l[2:] if l.startswith("> ") else l[1:] if l == ">" else None for l in lines]
    body = [q for q in quoted if q is not None]
    return "\n".join(body) if body else path.read_text(encoding="utf-8")

rows = []

# ---- negatives: real captures vs the prompt they cite -----------------------
for f in sorted(glob.glob(str(ROOT/"corpus/artifacts/*/*.json"))):
    d = json.loads(pathlib.Path(f).read_text())
    if d.get("artifact_type") != "contribution":
        continue
    praw = ROOT/d["prompt"]["path"]
    resp = (ROOT/d["raw"]["path"]).read_text(encoding="utf-8")
    cov_w, sat_w, _ = two_sided(praw.read_text(encoding="utf-8"), resp)
    cov_s, sat_s, _ = two_sided(sent_text(praw), resp)
    rows.append(("NEG", f"{d['round'][:22]}/{d['contributor']['identity'][:14]}",
                 cov_w, sat_w, cov_s, sat_s))

# ---- positives, synthetic: prompt file pasted as its own reply --------------
for p in sorted(glob.glob(str(ROOT/"record/*-prompt.md"))):
    pp = pathlib.Path(p)
    whole = pp.read_text(encoding="utf-8")
    cov_w, sat_w, _ = two_sided(whole, whole)
    # realistic paste: the custodian copies the SENT text, not the whole file
    cov_s, sat_s, _ = two_sided(sent_text(pp), sent_text(pp))
    rows.append(("POS-syn", pp.name[:37], cov_w, sat_w, cov_s, sat_s))

# ---- positive, genuine: D-10, founding transcript ---------------------------
tr = (ROOT/"corpus/raw/initial-transcript.txt").read_text(encoding="utf-8").splitlines()
operator = "\n".join(tr[2318:2373])   # raw 2319-2373, operator's message
grok_seg = "\n".join(tr[2376:2431])   # raw 2377-2431, attributed to Grok
cov, sat, inter = two_sided(operator, grok_seg)
rows.append(("POS-real", "D-10 raw2377 vs raw2319", cov, sat, cov, sat))

print(f"{'class':<9} {'case':<38} {'cov(file)':>9} {'sat(file)':>9} {'cov(sent)':>9} {'sat(sent)':>9}")
print("-"*88)
for c, name, cw, sw, cs, ss in rows:
    print(f"{c:<9} {name:<38} {cw:>9.3f} {sw:>9.3f} {cs:>9.3f} {ss:>9.3f}")

neg = [r for r in rows if r[0] == "NEG"]
pos = [r for r in rows if r[0].startswith("POS")]
print("-"*88)
for label, idx in (("cov(sent)", 4), ("sat(sent)", 5)):
    nmax = max(r[idx] for r in neg); pmin = min(r[idx] for r in pos)
    print(f"{label}: worst negative {nmax:.3f} | weakest positive {pmin:.3f} | margin {pmin-nmax:+.3f}")
