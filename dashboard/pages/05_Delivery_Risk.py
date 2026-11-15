from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Delivery Risk",layout="wide")
st.title("Delivery SLA and Exception Analysis")
path=ROOT/"reports/delivery_exception_queue.csv"
if not path.exists():
    st.warning("Run python -m scripts.build_delivery_risk first.")
    st.stop()
d=pd.read_csv(path)
st.caption("Retrospective ETA exception analysis from supplied fields. No live rider location, dispatch or capacity feed.")
a,b,c=st.columns(3)
a.metric("Delivered orders",f"{len(d):,}")
b.metric("ETA breach rate",f"{d.eta_breach.mean():.1%}")
c.metric("High risk (>15m)",f"{int(d.risk_band.eq('high_risk_15m_plus').sum()):,}")
st.bar_chart(d.groupby(["city","risk_band"]).size().unstack(fill_value=0))
st.dataframe(d[["order_id","city","order_hour","eta_variance_minutes","risk_band","risk_reason"]].sort_values("eta_variance_minutes",ascending=False),use_container_width=True,hide_index=True)
