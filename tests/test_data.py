import json
from pathlib import Path

import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def raw():
    return pd.read_csv(ROOT / "data" / "raw" / "food_delivery.csv")


@pytest.fixture(scope="module")
def clean():
    return pd.read_csv(ROOT / "data" / "processed" / "orders_clean_sa.csv")


def test_rows_reconcile(raw, clean):
    quarantine = pd.read_csv(ROOT / "data" / "processed" / "quarantine_log.csv")
    assert len(raw) == len(clean) + len(quarantine) == 15000


def test_no_duplicate_order_id(clean):
    assert not clean.order_id.duplicated().any()


def test_cancellation_rate_in_range(clean):
    assert 0.10 <= clean.cancellation_flag.mean() <= 0.16


def test_delivery_time_mean_in_range(clean):
    assert 80 <= clean.delivery_time_minutes.mean() <= 110


def test_ab_split_passes_srm(clean):
    per_customer = clean.groupby("customer_id").ab_group.agg(["first", "nunique"])
    assert (per_customer["nunique"] == 1).all()
    assert stats.chisquare(per_customer["first"].value_counts().values).pvalue > 0.05


def test_sar_conversion_reproduces_from_raw(raw, clean):
    for col in ["order_value", "delivery_fee", "discount_amount", "tip_amount", "final_amount_paid"]:
        gap = ((raw[col] * 3.75).round(2) - clean[f"{col}_sar"]).abs().max()
        assert gap == 0, col


def test_headline_numbers_match_reference(clean):
    ref = json.loads((ROOT / "data" / "processed" / "validation_reference.json").read_text())
    delivered = clean[~clean.cancellation_flag]
    assert int(clean.cancellation_flag.sum()) == ref["cancelled"]
    assert int(clean.delayed_delivery_flag.sum()) == ref["delayed"]
    assert int(clean.refund_flag.sum()) == ref["refunds"]
    assert round(delivered.final_amount_paid_sar.sum(), 2) == ref["gmv_sar_delivered_only"]
    assert round(delivered.final_amount_paid_sar.mean(), 2) == ref["aov_sar_delivered_only"]
    assert clean.customer_id.nunique() == ref["distinct_customers"]


def test_events_four_per_order_in_time_order():
    events = pd.read_json(ROOT / "data" / "processed" / "events.json", lines=True, dtype={"order_id": str})
    assert len(events) == 60000
    assert (events.groupby("order_id").size() == 4).all()
    assert events.groupby("order_id").event_time.apply(lambda s: s.is_monotonic_increasing).all()


def test_ab_results_report_has_valid_srm_and_ci():
    ab = pd.read_csv(ROOT / "reports" / "ab_results.csv")
    srm = ab[ab.data == "SRM check"].iloc[0]
    assert srm.p_value > 0.05
    primary = ab[(ab.role == "primary")]
    assert primary[["ci_low", "ci_high", "p_value"]].notna().all().all()
    assert (primary.ci_low < primary["diff"]).all() and (primary["diff"] < primary.ci_high).all()
