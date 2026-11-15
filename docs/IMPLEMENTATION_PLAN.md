# Product Analytics Platform — implementation status

## Delivered on the improvement branch

- Additive product analytics pipeline: session funnel, assumption-driven unit economics, customer lifecycle descriptors, retrospective delivery-risk queue and hourly capacity scenarios.
- Customer-level experiment analysis utilities: sample-size calculation, two-arm comparison, sample-ratio mismatch check and confidence interval.
- Production-event CSV contract, template, validator, quarantine output and delivered-event semantics. The validator is ready for an anonymised real export; no real production export has been supplied.
- Streamlit dashboard: original Executive, Growth, Delivery and Experiment tabs retained; added Product Funnel, Unit Economics, Customer Lifecycle, Delivery Risk, Capacity Scenario, Experiment Design, Restaurant Performance and Data Quality Monitoring pages.
- Dashboard exports: filtered order export, restaurant scorecard export and data-quality results export; relevant pages state metric definitions and data provenance.
- GitHub Actions workflow runs tests, end-to-end analytics pipeline and Python compilation.
- All changes remain on `improvement/product-analytics-foundation`; `main` is untouched.

## Validation boundaries

- The existing repository CI runs confirmed successful tests, pipeline execution and Python compilation for the production-event validator changes.
- The two newest dashboard pages and latest dashboard integration changes require the CI run on the current branch head to finish before they can be called verified.
- Redshift SQL query bodies are locally compared through PostgreSQL 16. This is dialect-port validation, not execution on AWS Redshift.
- BigQuery SQL is exercised locally in DuckDB, not a live BigQuery project.
- Streamlit is the implemented BI deliverable. Looker Studio is not required and has not been deployed.
- No production event export, Finance-approved cost data, live rider shift feed or dispatch feed is available. These are external source-data dependencies; code cannot manufacture them honestly.
- Seeded order, customer, restaurant and rider identifiers are demonstration data. Non-converting sessions and unit economics/capacity assumptions are explicitly synthetic or illustrative.

## Remaining external dependencies (not code defects)

1. Supply an anonymised production event export and confirm event semantics to replace simulated funnel sessions.
2. Supply Finance-approved commission, delivery, payment, promotion and refund amounts to replace scenario assumptions.
3. Supply actual rider shift/availability and dispatch timestamps to replace capacity assumptions and retrospective delivery flags.
4. Confirm source dataset redistribution rights before public deployment or public sharing of bundled data.
5. If cloud execution is specifically required, provide an authorised AWS Redshift/BigQuery environment; no credentials or paid cloud resources are assumed by this project.

## Run locally

```bash
python -m scripts.run_product_analytics
python -m pytest -q
python -m scripts.run_sql
streamlit run dashboard/app.py
```

The local runner and dashboard are the completed portfolio path. Live cloud deployment, live production ingestion and operational monitoring remain dependent on access to real systems and approved data; they are not represented as completed.
