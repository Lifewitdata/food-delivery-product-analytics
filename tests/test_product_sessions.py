import pandas as pd
import pytest
from scripts.build_product_sessions import FUNNEL, build_sessions

@pytest.fixture
def orders():
    return pd.DataFrame([
        {"order_id":"o1","customer_id":"c1","city":"Riyadh","device":"iOS","order_datetime":"2026-01-01 12:00:00"},
        {"order_id":"o2","customer_id":"c2","city":"Jeddah","device":"Android","order_datetime":"2026-01-02 13:00:00"},
    ])

def test_every_source_order_has_one_complete_linked_journey(orders):
    events = build_sessions(orders, seed=7, non_converting_sessions_per_customer=0)
    purchased = events[events.order_id.notna()]
    assert purchased.session_id.nunique() == len(orders)
    assert purchased.groupby("session_id").event_name.apply(list).map(tuple).eq(tuple(FUNNEL)).all()

def test_non_converting_sessions_are_explicitly_labelled(orders):
    events = build_sessions(orders, seed=7, non_converting_sessions_per_customer=2)
    nonbuyers = events[events.order_id.isna()]
    assert nonbuyers.session_id.nunique() == 4
    assert not nonbuyers.converted.any()
    assert nonbuyers.data_provenance.eq("synthetic_non_converting_session").all()

def test_generation_is_reproducible(orders):
    pd.testing.assert_frame_equal(build_sessions(orders, seed=42), build_sessions(orders, seed=42))

def test_missing_required_columns_fail_clearly():
    with pytest.raises(ValueError, match="missing required columns"):
        build_sessions(pd.DataFrame({"order_id":["x"]}))

def test_negative_session_multiplier_is_rejected(orders):
    with pytest.raises(ValueError, match="must be >= 0"):
        build_sessions(orders, non_converting_sessions_per_customer=-1)
