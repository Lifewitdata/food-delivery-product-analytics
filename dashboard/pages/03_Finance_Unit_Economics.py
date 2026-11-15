from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Unit Economics",layout="wide")
st.title("Unit Economics — Scenario Analysis")
path=ROOT/"reports/order_unit_economics_scenario.csv"
if not path.exists():
    st.warning("Run python -m scripts.build_unit_economics first.")
    st.stop()
d=pd.read_csv(path)
st.warning("Illustrative assumption-based scenario only. Not actual revenue, margin, refunds or profit. Replace assumptions with Finance-approved data.")
c1,c2,c3=st.columns(3)
c1.metric("Orders modelled",f"{len(d):,}")
c2.metric("Scenario contribution (SAR)",f"{d.contribution_scenario_sar.sum():,.0f}")
c3.metric("Avg scenario contribution / order",f"{d.contribution_scenario_sar.mean():,.2f}")
st.subheader("Scenario contribution by city")
st.bar_chart(d.groupby("city").contribution_scenario_sar.sum())
st.dataframe(d.groupby("city")[["commission_revenue_sar","delivery_cost_sar","payment_processing_cost_sar","promo_subsidy_sar","refund_cost_sar","contribution_scenario_sar"]].sum().round(2),use_container_width=True)
