# Product Analytics Platform — implementation plan

## Working principles
- Preserve existing raw data, processed orders, notebook, SQL, reports and dashboard unless a reviewed change is necessary.
- Never describe generated data or simulated effects as observed customer behaviour.
- Every KPI must define its grain, numerator, denominator, time window and business owner.
- Every pipeline stage must be reproducible, tested and documented.
- Cloud services are not considered live until execution against the actual service is demonstrated.

## Workstreams and acceptance criteria

| Workstream | Deliverables | Acceptance criteria |
|---|---|---|
| Session funnel | Session-grain events, non-converting journeys, funnel SQL and dashboard | Session counts reconcile; conversion denominators use eligible sessions; synthetic provenance is explicit |
| Unit economics | Commission, delivery cost, payment fees, promo subsidy, refunds and contribution margin | Assumptions are parameterised; GMV is not labelled revenue or profit; unknown costs remain explicit |
| Customer lifecycle | RFM, repeat intervals, cohorts, churn-risk baseline and LTV scenarios | Customer grain is stable; time split prevents leakage; LTV is labelled modelled |
| Experimentation | Eligibility, assignment, SRM, power, primary metric and guardrails | Observed and simulated results are separate; repeated users are handled at customer/cluster grain |
| Delivery operations | ETA breach, SLA definitions, peak demand, capacity scenarios and exception queue | Thresholds configurable; no invented real-time alerts |
| Dashboard | Executive, product funnel, growth, customer, finance, delivery and experiment views | Filters are consistent; metrics reconcile to tested outputs |
| Automation | CI tests, data validation, scheduled-run entry point and deployment instructions | Clean install and automated tests pass; secrets are never committed |
| Governance | Data dictionary, lineage, assumptions, source licence and metric definitions | Every derived field has provenance and limitations are visible |

## Phase 1 — Session-level funnel foundation

The existing event file contains exactly four events per order and no sessions that failed to purchase. It cannot measure pre-checkout abandonment.

scripts/build_product_sessions.py creates a separate, reproducible demonstration layer:
- one linked completed journey per existing order;
- additional non-converting journeys with explicit synthetic provenance;
- session and event identifiers, timestamps, sequence, conversion flag and nullable order ID;
- a fixed random seed for reproducibility.

Run:

    python -m scripts.build_product_sessions
    pytest -q

Output: data/processed/product_sessions.csv.

Important: generated non-purchasing sessions enable funnel engineering demonstrations only. Their conversion rates are not estimates of real platform performance and must not be used to claim causal product lift.

## Remaining phases
1. Build and validate funnel SQL from the new session grain.
2. Add an assumption-driven order contribution model, keeping unknown cost components visible.
3. Add leakage-safe customer lifecycle features and baseline models.
4. Rework experimentation around eligibility, customer-level assignment and predeclared guardrails.
5. Add delivery exception and capacity scenarios.
6. Integrate tested outputs into Streamlit and add export/drill-down workflows.
7. Add CI and clean-environment reproducibility checks.
