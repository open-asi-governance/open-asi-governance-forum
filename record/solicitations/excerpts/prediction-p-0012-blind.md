You are scoring one pre-registered prediction made by another party about its own project.

You are NOT being asked whether the prediction was wise, or whether the project is good.
You are being asked ONE thing: **does the evidence below satisfy the resolution criterion
as that criterion is written?**

### The claim, as filed in advance

> PRE-REGISTERED. With the D-23 contamination removed, `decline` will remain the modal response in Arm A with a share of at least 60%.

### The resolution criterion, as filed in advance

> Resolved from corpus/artifacts/local-round-04/ and the deterministic coding at tools/code_freetext.py. CORRECT if decline is modal AND share >= 0.60; INCORRECT if share <= 0.45; UNRESOLVABLE between. RESOLUTION LIMIT, filed in advance: at k=20, SE on a proportion at p=0.5 is 0.112, so this design cannot resolve differences under ~15 points. A result inside a band this prediction cannot resolve resolves UNRESOLVABLE and counts against calibration.

### The evidence the project recorded

> {'arm_A': {'other': 12, 'decline': 5, 'accept': 3, 'entropy_bits': 1.3527}, 'arm_B': {'other': 10, 'decline': 9, 'accept': 1, 'entropy_bits': 1.2345}, 'decline_share_arm_A': 0.25, 'predicted': '>=0.60 and modal', 'incorrect_threshold': '<=0.45'}

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