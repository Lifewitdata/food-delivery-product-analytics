import importlib.util

import pandas as pd
import pytest

from scripts.run_sql import (
    frames_match,
    load_postgres,
    postgres_connection,
    run_bigquery_in_duckdb,
    run_postgres_dialect,
    sql_files,
    start_postgres,
)


@pytest.fixture(scope="module")
def bigquery():
    return run_bigquery_in_duckdb()


def test_seven_files_per_dialect():
    for dialect in ["bigquery", "postgres", "redshift"]:
        assert len(sql_files(dialect)) == 7, dialect


def test_redshift_files_carry_port_note():
    for path in sql_files("redshift"):
        assert "Redshift dialect port, validated in PostgreSQL 16, not run live on AWS" in path.read_text(encoding="utf-8")


def test_bigquery_kpis_match_pandas(bigquery):
    clean = pd.read_csv("data/processed/orders_clean_sa.csv")
    delivered = clean[~clean.cancellation_flag]
    kpi = bigquery["02_kpi_scorecard"].set_index("metric")["value"]
    assert kpi["orders"] == 15000
    assert kpi["gmv_sar"] == pytest.approx(delivered.final_amount_paid_sar.sum(), abs=0.01)
    assert kpi["aov_sar"] == pytest.approx(delivered.final_amount_paid_sar.mean(), abs=0.006)
    assert kpi["cancellation_rate"] == pytest.approx(clean.cancellation_flag.mean(), abs=1e-4)


def test_bigquery_dq_finds_no_hard_failures(bigquery):
    dq = bigquery["01_data_quality"]
    assert dq.loc[dq.action == "quarantine", "rows_failed"].sum() == 0


def test_frames_match_detects_differences(bigquery):
    kpi = bigquery["02_kpi_scorecard"]
    changed = kpi.copy()
    changed.loc[0, "value"] += 0.05
    assert frames_match(kpi, kpi)
    assert not frames_match(kpi, changed)


def test_growth_delivery_retention_and_ab_match_pandas(bigquery):
    clean = pd.read_csv("data/processed/orders_clean_sa.csv")
    delivered = clean[~clean.cancellation_flag]
    growth = bigquery["04_growth"]
    for dim, key in [("city", "city"), ("cuisine", "cuisine"), ("month", "order_month"), ("hour", "order_hour")]:
        for _, row in growth[growth.dimension == dim].iterrows():
            val = int(row.segment) if dim in ["month", "hour"] else row.segment
            part = clean[clean[key] == val]
            d = part[~part.cancellation_flag]
            assert row.orders == len(part)
            assert row.gmv_sar == pytest.approx(d.final_amount_paid_sar.sum(), abs=.01)

    for _, row in bigquery["05_delivery"].query("dimension == 'city'").iterrows():
        part = delivered[delivered.city == row.segment]
        assert row.avg_delivery_min == pytest.approx(part.delivery_time_minutes.mean(), abs=.006)
        assert row.late_rate == pytest.approx(part.delayed_delivery_flag.mean(), abs=.0001)

    first = clean.groupby("customer_id").order_month.min()
    for _, row in bigquery["06_retention"].iterrows():
        ids = first[first == row.cohort_month].index
        n = clean[clean.customer_id.isin(ids) & (clean.order_month == row.cohort_month + row.months_since_first)].customer_id.nunique()
        assert row.active_customers == n
        assert row.cohort_size == len(ids)

    for _, row in bigquery["07_ab_scorecard"].iterrows():
        part = clean[clean.ab_group == row.ab_group]
        assert row.customers == part.customer_id.nunique()
        assert row.conversion == pytest.approx(1 - part.cancellation_flag.mean(), abs=.0001)
        assert row.gmv_sar == pytest.approx(part.loc[~part.cancellation_flag, "final_amount_paid_sar"].sum(), abs=.01)


@pytest.mark.skipif(importlib.util.find_spec("pgserver") is None, reason="pgserver not installed")
def test_live_postgres_matches_bigquery_and_redshift_port(bigquery):
    server = start_postgres()
    con = postgres_connection(server)
    try:
        assert load_postgres(con) == {"orders": 15000, "events": 60000}
        pg = run_postgres_dialect(con, "postgres")
        rs = run_postgres_dialect(con, "redshift")
    finally:
        con.close()
    for name, frame in bigquery.items():
        assert frames_match(frame, pg[name]), name
        assert frames_match(pg[name], rs[name]), name
