import pandas as pd
import pytest
from scripts.build_unit_economics import build_unit_economics
from scripts.build_customer_lifecycle import build_customer_lifecycle
from scripts.build_delivery_risk import build_delivery_risk

@pytest.fixture
def orders():
    return pd.DataFrame([
      {"order_id":"1","customer_id":"a","city":"Riyadh","order_date":"2026-01-01","order_hour":12,"delivery_time_minutes":50,"estimated_delivery_time":40,"delivery_distance_km":8,"cancellation_flag":False,"order_value_sar":100,"final_amount_paid_sar":110,"discount_amount_sar":5,"refund_flag":False},
      {"order_id":"2","customer_id":"a","city":"Riyadh","order_date":"2026-01-10","order_hour":13,"delivery_time_minutes":30,"estimated_delivery_time":40,"delivery_distance_km":5,"cancellation_flag":False,"order_value_sar":80,"final_amount_paid_sar":90,"discount_amount_sar":0,"refund_flag":False},
      {"order_id":"3","customer_id":"b","city":"Jeddah","order_date":"2026-01-05","order_hour":18,"delivery_time_minutes":60,"estimated_delivery_time":40,"delivery_distance_km":12,"cancellation_flag":False,"order_value_sar":120,"final_amount_paid_sar":130,"discount_amount_sar":10,"refund_flag":True},
    ])

def test_unit_economics_is_explicit_scenario(orders):
    assumptions={"commission_rate":.2,"delivery_cost_per_order_sar":10,"payment_processing_rate":.02,"promo_subsidy_rate_of_discount":1,"refund_rate_of_refunded_order_value":1}
    out=build_unit_economics(orders,assumptions)
    assert out.economics_provenance.str.contains("not_actual_profit").all()
    assert out.loc[0,"commission_revenue_sar"]==20

def test_invalid_assumption_rejected(orders):
    with pytest.raises(ValueError,match="Rates"):
        build_unit_economics(orders,{"commission_rate":2,"delivery_cost_per_order_sar":1,"payment_processing_rate":.02,"promo_subsidy_rate_of_discount":1,"refund_rate_of_refunded_order_value":1})

def test_customer_lifecycle_counts_repeat(orders):
    out=build_customer_lifecycle(orders)
    assert bool(out.loc[out.customer_id.eq("a"),"repeat_customer"].iloc[0])

def test_delivery_risk_identifies_eta_breach(orders):
    out=build_delivery_risk(orders)
    assert bool(out.loc[out.order_id.eq("1"),"eta_breach"].iloc[0])
    assert not bool(out.loc[out.order_id.eq("2"),"eta_breach"].iloc[0])
