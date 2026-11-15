from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Capacity Scenario",layout="wide")
st.title("Hourly Delivery Capacity — Scenario")
path=ROOT/"reports/hourly_capacity_scenario.csv"
if not path.exists():
    st.warning("Run python -m scripts.build_capacity_scenarios first.")
    st.stop()
d=pd.read_csv(path)
st.warning("Rider availability is an explicit scenario assumption, not a live workforce feed or actual shift plan.")
a,b,c=st.columns(3)
a.metric("City-hour periods",f"{len(d):,}")
b.metric("Potential shortfall periods",f"{int(d.capacity_status.eq('potential_shortfall').sum()):,}")
c.metric("Total orders",f"{int(d.orders.sum()):,}")
st.bar_chart(d.groupby(["city","hour"]).capacity_gap_orders.sum().unstack(0))
st.dataframe(d.sort_values("capacity_gap_orders",ascending=False),use_container_width=True,hide_index=True)
