# Product experimentation playbook

## Current dataset decision
The supplied threshold experiment is not a valid test of SAR 50 versus SAR 75: all baskets are above both thresholds and the source fee was not recomputed. The existing observed comparison is A/A-like. The reported treatment effect is simulated and cannot support a launch decision.

## Production design before assignment
1. Define eligible users before randomisation (new/returning users, geography, platform, exclusions).
2. Randomise at stable customer/account ID, not event or order row, to prevent cross-device contamination.
3. Persist experiment_id, variant, assignment_timestamp, eligibility_reason, exposure_timestamp and assignment_version.
4. Define one primary metric (e.g. eligible user purchase conversion within a fixed window).
5. Pre-register guardrails: contribution margin per eligible user, cancellation, refund, delivery SLA and customer support contact rate.
6. Calculate sample size from baseline, minimum detectable effect, alpha and power before launch.
7. Monitor sample-ratio mismatch and exposure logging; do not repeatedly peek and stop on significance.
8. Analyse intention-to-treat at assignment grain; use cluster-robust methods if assignment is above user grain.
9. Define non-inferiority margins for guardrails. A non-significant p-value is not proof of no harm.
10. Report absolute and relative effects, confidence intervals, segment caveats and decision owner.

## Required decision states
- SHIP: primary metric meets pre-registered threshold and every guardrail passes its pre-registered margin.
- ITERATE: promising but inconclusive, implementation or exposure issue.
- STOP: primary harm or guardrail breach.
- INVALID: SRM, broken assignment/exposure, missing outcome, or contaminated groups.

Never use a simulated lift to make a production rollout recommendation.
