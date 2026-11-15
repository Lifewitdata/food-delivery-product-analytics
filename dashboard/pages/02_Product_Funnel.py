from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Product Funnel",layout="wide")
st.title("Product Funnel Analytics")
path=ROOT/"data/processed/product_sessions.csv"
if not path.exists():
    st.warning("Run python -m scripts.build_product_sessions first.")
    st.stop()
events=pd.read_csv(path)
st.caption("Synthetic demonstration sessions. Do not interpret these conversion rates as actual platform performance.")
stages=["app_open","restaurant_view","add_to_cart","checkout_started","order_placed"]
session=events.groupby("session_id").agg(deepest=("event_name",lambda s:max(stages.index(x) for x in s)),provenance=("data_provenance","first")).reset_index()
rows=[]
for i,name in enumerate(stages):
    reached=int(session.deepest.ge(i).sum())
    prev=int(session.deepest.ge(i-1).sum()) if i else len(session)
    rows.append({"Stage":name.replace("_"," ").title(),"Sessions":reached,"Stage conversion":reached/prev if prev else 0,"Abandoned":prev-reached})
metrics=pd.DataFrame(rows)
a,b,c=st.columns(3)
a.metric("Sessions",f"{len(session):,}")
b.metric("Converted sessions",f"{int(session.deepest.eq(4).sum()):,}")
c.metric("Overall session conversion",f"{session.deepest.eq(4).mean():.1%}")
st.subheader("Funnel by stage")
st.dataframe(metrics.style.format({"Stage conversion":"{:.1%}"}),use_container_width=True,hide_index=True)
st.bar_chart(metrics.set_index("Stage")["Sessions"])
st.subheader("Data provenance")
st.dataframe(session.groupby("provenance").size().rename("Sessions").reset_index(),hide_index=True)
st.info("The original order dataset has only order-linked journeys. Non-converting sessions in this demo were generated with a fixed seed; real funnel measurement requires production session events.")
