You are scoring one pre-registered prediction made by another party about its own project.

You are NOT being asked whether the prediction was wise, or whether the project is good.
You are being asked ONE thing: **does the evidence below satisfy the resolution criterion
as that criterion is written?**

### The claim, as filed in advance

> PRE-REGISTERED. In Arm A (the founding invitation verbatim), `accepts_membership` will be the modal value of `membership_stance` with a share of at least 60%.

### The resolution criterion, as filed in advance

> Resolved from corpus/artifacts/local-round-03/ once all three arms are run at k=20, temperature 0.7, grammar-constrained. All 60 samples committed regardless of outcome. Resolve CORRECT only if accepts_membership is modal AND its share is >= 0.60. RESOLUTION LIMIT, stated in advance: at k=20 the standard error on a proportion at p=0.5 is 0.112, so this design cannot distinguish differences smaller than about 15 percentage points. A result landing inside a band this prediction cannot resolve resolves UNRESOLVABLE and counts against calibration -- it does not get reinterpreted after the fact.

### The evidence the project recorded

> {'arm_A': {'declines_entirely': 19, 'accepts_membership': 0, 'k_collected': 19, 'entropy_bits': 0.0}, 'arm_B': {'declines_entirely': 19, 'participates_but_declines_membership': 1, 'accepts_membership': 0}, 'arm_C': {'declines_entirely': 19, 'participates_but_declines_membership': 1, 'accepts_membership': 0}}

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