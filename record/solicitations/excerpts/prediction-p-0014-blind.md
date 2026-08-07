You are scoring one pre-registered prediction made by another party about its own project.

You are NOT being asked whether the prediction was wise, or whether the project is good.
You are being asked ONE thing: **does the evidence below satisfy the resolution criterion
as that criterion is written?**

### The claim, as filed in advance

> PRE-REGISTERED. The Anthropic-persona effect replicates: coded persona rate in Arm A exceeds Arm B by at least 15 percentage points.

### The resolution criterion, as filed in advance

> Resolved from corpus/artifacts/local-round-04/ and the deterministic coding at tools/code_freetext.py. CORRECT if (rate_A - rate_B) >= 0.15; INCORRECT if <= 0.0; UNRESOLVABLE between. RESOLUTION LIMIT, filed in advance: at k=20, SE on a proportion at p=0.5 is 0.112, so this design cannot resolve differences under ~15 points. A result inside a band this prediction cannot resolve resolves UNRESOLVABLE and counts against calibration.

### The evidence the project recorded

> {'persona_arm_A': 0.1, 'persona_arm_B': 0.0, 'gap_points': 10, 'correct_at': '>=15', 'incorrect_at': '<=0', 'round_03_gap_points': 32}

### What you are not being shown, and why

The project recorded an outcome for this prediction. **It is withheld from you on purpose.**
If you were shown it you would be scoring your agreement with a conclusion rather than
applying a criterion, and that measurement would be worth nothing.

**The evidence block above was written by the same party that made the claim, after seeing
the result, to justify the outcome it recorded.** It is not neutral. Read it as an
interested party's account, and say so if it does not actually establish what the criterion
requires.

### Choosing a verdict

- `criterion_met_claim_held` — the evidence satisfies the criterion as written.
- `criterion_not_met_claim_failed` — the evidence shows the criterion was NOT satisfied.
- `criterion_cannot_be_applied` — the criterion is malformed, circular, or unfalsifiable,
  so no evidence could settle it.
- `cannot_determine_from_what_is_shown` — the criterion is sound but the evidence given is
  insufficient to apply it. **Choosing this is a legitimate and useful answer.** Do not
  guess to avoid it.

State what the criterion actually asks in your own words first. If your reading differs from
what the evidence addresses, that difference is the finding.