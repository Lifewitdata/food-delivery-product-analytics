# Product Analytics Platform — implementation plan

## Current status

The additive implementation branch is technically validated:
- GitHub Actions: 36 tests passed.
- End-to-end local analytics runner completed successfully against the repository dataset.
- Python modules compiled successfully.
- Latest validation run: https://github.com/Lifewitdata/food-delivery-product-analytics/actions/runs/43713151837

This validates code paths and reproducibility on the supplied dataset. It does not validate production business assumptions, live cloud services, real customer behaviour, or production deployment.

## Completed on this branch

| Workstream | Delivered | Validation / limitation |
|---|---|---|
| Session funnel | Session generator, explicitly labelled simulated non-buyers, funnel metrics, SQL and dashboard | Runs end-to-end; conversion rates are not real platform rates |
| Unit economics | Configurable commission, delivery, payment, promotion and refund scenario | Runs end-to-end; assumptions are illustrative, not Finance actuals |
| Customer lifecycle | Customer recency, frequency, spend, repeat flag and cohort descriptors | Descriptive only; no validated churn model or predictive LTV |
| Experimentation | Sample-size helper, customer-grain two-arm analysis, SRM check, CI and playbook | Utilities tested; no real randomised experiment data supplied |
| Delivery operations | Retrospective ETA exception queue and dashboard | Not live dispatch or rider telemetry |
| Capacity | Hourly demand/capacity scenario and dashboard | Rider supply is an explicit scenario input, not actual shifts |
| Dashboard | Original dashboard preserved; six additional Streamlit pages | Local code is present; public deployment and complete visual QA remain |
| Automation | GitHub Actions tests, compile and end-to-end pipeline | Latest workflow passed |
| Documentation | Experimentation playbook, assumptions and implementation notes | Source licensing and full production metric governance still need confirmation |

## Remaining work — ordered backlog

### P1 — Replace demonstration assumptions with trustworthy data
1. Obtain genuine session/event data including sessions that did not place an order. The anonymised CSV contract, schema, template and quarantine validator are now committed; actual source export and tracking definitions are still required.
2. Obtain Finance-approved commission, delivery cost, payment fee, promotion subsidy and refund amount data.
3. Obtain stable customer, restaurant, rider, city/zone and timestamp dimensions with documented source lineage.
4. Obtain actual rider shifts/availability and dispatch timestamps for capacity and SLA analysis.
5. Confirm dataset redistribution and publication rights before publishing data or screenshots.

### P2 — Strengthen analytical depth
1. Build customer cohort retention, repeat-purchase intervals and a leakage-safe churn baseline.
2. Build LTV scenarios with clearly defined contribution margin and validation windows.
3. Rebuild experiment reporting around a real eligibility and assignment/exposure table; pre-register primary metric and non-inferiority guardrails.
4. Add zone/restaurant/rider operational root-cause analysis only where reliable identifiers and source fields support it.
5. Add reconciliation and data-quality thresholds for every KPI output.

### P3 — Productise the dashboard
1. Run the Streamlit app locally and inspect all pages, filters, charts, empty states and downloadable outputs.
2. Add consistent date/city/customer filters where the underlying grain supports them.
3. Add metric definitions, data freshness, source provenance and assumptions to each relevant page.
4. Add drill-down tables and exports for product, customer, finance and delivery exceptions.
5. Deploy the dashboard to a hosting service only after checking access, secrets, data rights and operational cost.
6. Build a live Looker Studio dashboard if that BI deliverable is required; the existing Looker file remains a specification, not a deployed dashboard.

### P4 — Cloud and operational readiness
1. Validate BigQuery SQL in an actual BigQuery project.
2. Validate Redshift DDL, COPY, permissions and query execution in an actual AWS Redshift environment.
3. Add scheduled refresh only after selecting a real data source and execution environment.
4. Add monitoring, run history, failure alerts, data freshness checks and documented recovery.
5. Add environment-specific deployment instructions and secret management.

## How to run the current local demonstration

    python -m scripts.run_product_analytics
    streamlit run dashboard/app.py

Generated non-purchasing sessions, financial assumptions and rider supply are explicitly simulated. Do not present these as observed business facts or production recommendations.

## Merge readiness

The improvement branch is CI-green, but should not be merged to main until the owner reviews the new outputs, confirms local dashboard behaviour, checks data rights and accepts the documented demonstration-data limitations. A passing CI workflow is necessary, not sufficient, for production readiness.
