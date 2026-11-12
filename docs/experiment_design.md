# Experiment design: SAR 75 vs SAR 50 free-delivery threshold

Synthetic portfolio exercise, not a real company experiment. This document records the design used by notebook Step 7; it was written after the exploratory data profile, not prospectively registered with a real experiment platform.

## Hypothesis and population

Lowering the threshold from SAR 75 to SAR 50 increases checkout-to-delivery conversion without meaningfully worsening delivery performance. In a real test, include eligible app users with baskets near the threshold; log non-buying sessions too. In this dataset, every basket is at least SAR 375, so both thresholds qualify identically and fees were never adjusted. The observed comparison is an A/A check, not a valid test of the business hypothesis.

## Assignment

Existing seeded customer assignment: control SAR 75, treatment SAR 50. One customer always stays in one group. Count distinct customers, not orders, for the sample-ratio-mismatch check. Pearson chi-square against 50/50; SRM p < 0.05 invalidates the readout. Customer IDs are artificial and do not identify real people.

## Metrics

- Primary: delivered orders / checkout sessions (one checkout per order_id).
- Robustness: mean conversion per customer, Welch t-test; avoids treating all repeated orders as independent. This weights customers equally, so it is a different estimand from the session-weighted primary.
- Secondary: delivered GMV / assigned customer, Welch t-test of customer revenue totals. Include zero revenue for customers whose orders all cancelled.
- Guardrails: mean delivery time and source late rate on delivered orders. Cancellation is also shown, but it is exactly 1 minus conversion, not an independent guardrail.
- Segments: city and premium vs regular; exploratory, no multiplicity adjustment and not launch gates.

## Sample size and stopping

Two-sided alpha 0.05, 80% power, 3 percentage-point MDE. `NormalIndPower.solve_power(proportion_effectsize(p + .03, p), alpha=.05, power=.8)` gives 4,041 sessions per arm at p=.35, or 1,779 at this dataset's control rate .8693. The latter uses an exploratory baseline, not a prospectively specified one. Repeated sessions per customer reduce effective sample size; use the customer-level robustness check and a cluster-aware power calculation before a real test. Fixed sample readout; no repeated peeking.

## Simulation

Seed 42; copy the orders, randomly flip 228 treatment cancellations to delivered (+3 pp over its own baseline). Do not modify the source data. Revenue changes solely because those orders now count as delivered, not by adding an unrelated SAR 2 offset. Preserve recorded delivery times and late flags. They also exist on cancelled source rows, which is a synthetic artefact.

## Decision rule and limits

Demonstration rule: LAUNCH if the primary 95% CI is above zero and no delivery guardrail is significantly worse; DO NOT LAUNCH if the primary CI is below zero; otherwise REVISE AND RETEST. Two-sample proportion difference CIs use a normal approximation, Welch comparisons use normal-approximation difference CIs. Non-significance on a guardrail does **not** establish non-inferiority: a real launch needs predeclared acceptable harm margins, confidence bounds within those margins, a contribution-margin metric and a clustered primary analysis. The demonstration LAUNCH is therefore not a real deployment recommendation.

Observed and simulated results, CI bounds, p-values and verdicts are saved separately in reports/ab_results.csv.
