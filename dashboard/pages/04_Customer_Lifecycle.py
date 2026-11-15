from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Customer Lifecycle",layout="wide")
st.title("Customer Lifecycle Analytics")
path=ROOT/"reports/customer_lifecycle.csv"
if not path.exists():
    st.warning("Run python -m scripts.build_customer_lifecycle first.")
    st.stop()
d=pd.read_csv(path)
st.caption("Descriptive customer recency and frequency segments, not a validated churn model or predictive LTV.")
a,b,c=st.columns(3)
a.metric("Customers",f"{d.customer_id.nunique():,}")
b.metric("Repeat customers",f"{int(d.repeat_customer.sum()):,}")
c.metric("Average delivered spend",f"SAR {d.monetary_sar.mean():,.2f}")
st.bar_chart(d.lifecycle_segment.value_counts())
st.dataframe(d.sort_values("recency_days",ascending=False),use_container_width=True,hide_index=True)
