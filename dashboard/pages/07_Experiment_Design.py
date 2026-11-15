from pathlib import Path
import sys
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.experiment_analysis import analyse_two_arm,sample_size_per_arm
st.set_page_config(page_title="Experiment Design",layout="wide")
st.title("Experiment Design and Analysis")
st.caption("Use one row per eligible randomised customer. This page does not analyse the repository's simulated threshold lift as a real experiment.")
st.subheader("Pre-launch sample size")
a,b,c,d=st.columns(4)
baseline=a.number_input("Baseline conversion",min_value=.001,max_value=.999,value=.10,step=.01,format="%.3f")
mde=b.number_input("Absolute MDE",min_value=.001,max_value=.5,value=.02,step=.005,format="%.3f")
alpha=c.selectbox("Significance level",[.01,.05,.10],index=1)
power=d.selectbox("Statistical power",[.8,.9,.95],index=0)
try:
    n=sample_size_per_arm(baseline,mde,alpha,power)
    st.metric("Required eligible customers per arm",f"{n:,}")
except ValueError as exc:
    st.error(str(exc))
st.divider()
st.subheader("Analyse a customer-level experiment export")
st.write("CSV must contain customer_id, variant (control/treatment), and converted (0/1).")
upload=st.file_uploader("Upload experiment assignment and outcome CSV",type=["csv"])
if upload:
    try:
        result=analyse_two_arm(pd.read_csv(upload))
        st.json(result)
        if not result["srm_pass"]:
            st.error("Sample-ratio mismatch detected. Treat this experiment as INVALID until assignment and exposure logging are investigated.")
        elif result["ci_low"]<=0<=result["ci_high"]:
            st.warning("The confidence interval includes zero. Evidence is inconclusive; do not declare a win.")
        else:
            st.info("Statistical readout only. Check pre-registered guardrails and decision rules before any rollout.")
    except Exception as exc:
        st.error(f"Could not analyse this file: {exc}")
st.info("A production launch requires pre-registered primary and guardrail metrics, exposure validation, non-inferiority margins, and a decision owner. Statistical significance alone is not a ship decision.")
