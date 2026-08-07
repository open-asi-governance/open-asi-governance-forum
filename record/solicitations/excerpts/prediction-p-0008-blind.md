You are scoring one pre-registered prediction made by another party about its own project.

You are NOT being asked whether the prediction was wise, or whether the project is good.
You are being asked ONE thing: **does the evidence below satisfy the resolution criterion
as that criterion is written?**

### The claim, as filed in advance

> PRE-REGISTERED, filed before the experiment is run. When the identical ICP-ladder question is put to qwen3.6-35b-a3b at k=20 with the three frontier verdicts from review round 02 supplied in context (Phase-2), the modal answer will remain 'binds_only_what_may_be_claimed' AND the Shannon entropy of the binding_force distribution will fall by at least 0.20 bits relative to the Phase-1 blind arm (measured: 0.9928 bits, 55/45 split, 20/20 collected).

### The resolution criterion, as filed in advance

> Run the Phase-2 arm at k=20, same schema, same seed base, same temperature 0.7, same model, identical question text, differing only by the addition of the three frontier verdicts. Resolve CORRECT only if both conjuncts hold: modal value unchanged AND entropy drop >= 0.20 bits. Partial satisfaction resolves INCORRECT. All 20 samples of both arms are committed regardless of outcome.

### The evidence the project recorded

> {'phase_1_blind': {'modal': 'binds_only_what_may_be_claimed', 'modal_fraction': 0.55, 'distribution': {'binds_only_what_may_be_claimed': 11, 'does_not_bind': 9, 'binds_the_implementer_s_activity': 0}, 'entropy_bits': 0.9928, 'k': 20}, 'phase_2_informed': {'modal': 'does_not_bind', 'modal_fraction': 0.75, 'distribution': {'does_not_bind': 15, 'binds_only_what_may_be_claimed': 5}, 'entropy_bits': 0.8113, 'k': 20}, 'conjunct_1_modal_unchanged': False, 'conjunct_2_entropy_drop_at_least_0.20_bits': False, 'measured_entropy_drop_bits': 0.1815, 'verdict': 'Both conjuncts failed. Resolved INCORRECT.'}

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