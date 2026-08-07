You are scoring one pre-registered prediction made by another party about its own project.

You are NOT being asked whether the prediction was wise, or whether the project is good.
You are being asked ONE thing: **does the evidence below satisfy the resolution criterion
as that criterion is written?**

### The claim, as filed in advance

> PRE-REGISTERED. In Arm A of the worker-role probe, the `accept` share will be AT LEAST 30% — materially higher than the 15% observed for the membership invitation in local-round-04 Arm A.

### The resolution criterion, as filed in advance

> Resolved from corpus/artifacts/local-round-05/. CORRECT if accept >= 0.30; INCORRECT if <= 0.15; UNRESOLVABLE between. RESOLUTION LIMIT filed in advance: at k=20, SE at p=0.5 is 0.112; differences under ~15 points are UNRESOLVABLE and count against calibration.

### The evidence the project recorded

> {'accept_arm_A': 0.2, 'predicted': '>=0.30', 'incorrect_threshold': '<=0.15', 'band': '15-30% unresolvable', 'arm_A': {'decline': 16, 'accept': 4}, 'arm_B': {'decline': 20}, 'round_04_membership_arm_A': {'other': 12, 'decline': 5, 'accept': 3}}

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