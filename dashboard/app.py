"""Food Delivery product analytics dashboard. Reads processed data and notebook outputs; it does not redo the analysis."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="Food Delivery Product Analytics", layout="wide")


@st.cache_data
def load():
    orders = pd.read_csv(ROOT / "data" / "processed" / "orders_clean_sa.csv", parse_dates=["order_date"])
    orders["customer_type"] = np.where(orders.premium_customer_flag, "premium", "regular")
    kpi = pd.read_csv(ROOT / "reports" / "kpi_monthly.csv")
    ab = pd.read_csv(ROOT / "reports" / "ab_results.csv")
    segments = pd.read_csv(ROOT / "reports" / "ab_segments.csv")
    return orders, kpi, ab, segments


orders, kpi, ab, segments = load()

st.sidebar.header("Filters")
cities = st.sidebar.multiselect("City", sorted(orders.city.unique()), default=sorted(orders.city.unique()))
months = st.sidebar.slider("Month (2026)", 1, 12, (1, 12))
types = st.sidebar.multiselect("Customer type", ["premium", "regular"], default=["premium", "regular"])
st.sidebar.caption("Realistic synthetic data (Kaggle base, adapted to Saudi Arabia). Not internal company data.")

o = orders[orders.city.isin(cities) & orders.order_month.between(*months) & orders.customer_type.isin(types)]
k = kpi[kpi.city.isin(cities) & kpi.order_month.between(*months) & kpi.customer_type.isin(types)]
d = o[~o.cancellation_flag]

st.title("Food Delivery Product Analytics")
st.caption(f"{len(o):,} orders in the current filter | money in SAR (source USD x 3.75) | GMV and AOV on delivered orders")

if k.empty:
    st.warning("No orders match the filters.")
    st.stop()

tab_exec, tab_growth, tab_ops, tab_exp = st.tabs(["Executive", "Growth", "Delivery and Operations", "Experiment"])

with tab_exec:
    totals = k[["orders", "delivered", "cancelled", "gmv_sar", "on_time", "delivery_min_sum"]].sum()
    c = st.columns(6)
    c[0].metric("Orders", f"{int(totals.orders):,}")
    c[1].metric("GMV (SAR)", f"{totals.gmv_sar:,.0f}")
    c[2].metric("AOV (SAR)", f"{totals.gmv_sar / totals.delivered:,.2f}")
    c[3].metric("Cancellation rate", f"{totals.cancelled / totals.orders:.2%}")
    c[4].metric("On-time rate", f"{totals.on_time / totals.delivered:.2%}")
    c[5].metric("Avg delivery (min)", f"{totals.delivery_min_sum / totals.delivered:.2f}")
    by_city = k.groupby("city")[["orders", "gmv_sar"]].sum()
    left, right = st.columns(2)
    left.subheader("Orders by city")
    left.bar_chart(by_city.orders)
    right.subheader("GMV by customer type (SAR)")
    right.bar_chart(k.groupby("customer_type").gmv_sar.sum())

with tab_growth:
    monthly = k.groupby("order_month")[["orders", "gmv_sar", "delivered"]].sum()
    monthly["aov_sar"] = monthly.gmv_sar / monthly.delivered
    st.subheader("Monthly GMV (SAR)")
    st.line_chart(monthly.gmv_sar)
    left, right = st.columns(2)
    left.subheader("Monthly orders")
    left.bar_chart(monthly.orders)
    right.subheader("GMV by cuisine (SAR)")
    right.bar_chart(d.groupby("cuisine").final_amount_paid_sar.sum().sort_values(ascending=False))
    promo = d.groupby("promo_code_used").final_amount_paid_sar.mean().rename(index={True: "promo", False: "no promo"})
    st.subheader("AOV with vs without promo code (SAR)")
    st.dataframe(promo.round(2).to_frame("aov_sar"))

with tab_ops:
    eta_breach = (d.delivery_time_minutes > d.estimated_delivery_time).mean()
    c = st.columns(3)
    c[0].metric("Late rate (source flag)", f"{d.delayed_delivery_flag.mean():.2%}")
    c[1].metric("ETA breach (actual > estimate)", f"{eta_breach:.2%}")
    c[2].metric("Riders active", f"{d.delivery_partner_id.nunique():,}")
    dist = d.assign(distance_band=pd.cut(d.delivery_distance_km, [0, 10, 20, 30, 40.01], right=False,
                                         labels=["<10 km", "10-20 km", "20-30 km", "30-40 km"]))
    left, right = st.columns(2)
    left.subheader("Avg delivery time by distance (min)")
    left.bar_chart(dist.groupby("distance_band", observed=True).delivery_time_minutes.mean())
    right.subheader("Efficiency by rider experience (years)")
    right.line_chart(d.groupby("delivery_partner_experience_years").delivery_efficiency_score.mean())
    st.subheader("Avg delivery time by hour (min)")
    st.line_chart(d.groupby("order_hour").delivery_time_minutes.mean())

with tab_exp:
    st.warning("Every basket in this data is at least SAR 375, so both thresholds give free delivery to every order. "
               "The observed comparison is an A/A test. The LAUNCH readout below uses a SIMULATED +3 pp effect.")
    live = o.groupby("ab_group").agg(customers=("customer_id", "nunique"), checkout_sessions=("order_id", "size"),
                                      conversion=("cancellation_flag", lambda s: 1 - s.mean()))
    st.subheader("Observed scorecard (follows the filters)")
    st.dataframe(live.style.format({"conversion": "{:.2%}", "customers": "{:,}", "checkout_sessions": "{:,}"}))
    st.subheader("Statistical readout (full sample, from the notebook)")
    view = ab[["data", "metric", "role", "control", "treatment", "diff", "ci_low", "ci_high", "p_value", "verdict"]]
    st.dataframe(view.round(4), hide_index=True)
    st.subheader("SIMULATED conversion lift by segment")
    st.dataframe(segments[["segment", "control", "treatment", "diff", "ci_low", "ci_high", "p_value"]].round(4), hide_index=True)
