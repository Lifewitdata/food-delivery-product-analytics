"""Data-quality scorecard calculated from the supplied processed order data."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Data Quality", layout="wide")
st.title("Data Quality Monitoring")
path = ROOT / "data" / "processed" / "orders_clean_sa.csv"
if not path.exists():
    st.error("Processed orders file is missing. Run the repository data preparation workflow first.")
    st.stop()
df = pd.read_csv(path)
st.caption("Checks are recalculated from the local portfolio dataset at page load. They are not a live production monitor.")
checks = []
def add_check(name, failed, checked, severity="Error"):
    checks.append({"check": name, "rows_checked": int(checked), "rows_failed": int(failed),
                   "failure_rate": (float(failed) / checked) if checked else 0.0, "severity": severity,
                   "status": "PASS" if failed == 0 else "FAIL"})

add_check("Duplicate order_id", df.order_id.duplicated(keep=False).sum(), len(df))
for col in ["order_id", "customer_id", "city", "order_date", "final_amount_paid_sar", "cancellation_flag"]:
    if col in df:
        add_check(f"Null values: {col}", df[col].isna().sum(), len(df))
if "final_amount_paid_sar" in df:
    add_check("Negative paid amount", (pd.to_numeric(df.final_amount_paid_sar, errors="coerce") < 0).sum(), len(df))
if "delivery_time_minutes" in df:
    delivery = pd.to_numeric(df.delivery_time_minutes, errors="coerce")
    add_check("Delivery time outside 0–300 minutes", ((delivery < 0) | (delivery > 300)).sum(), delivery.notna().sum())
if "delivery_distance_km" in df:
    distance = pd.to_numeric(df.delivery_distance_km, errors="coerce")
    add_check("Negative delivery distance", (distance < 0).sum(), distance.notna().sum())
if "order_value_sar" in df:
    amount = pd.to_numeric(df.order_value_sar, errors="coerce")
    add_check("Negative order value", (amount < 0).sum(), amount.notna().sum())

result = pd.DataFrame(checks)
failed = int(result.rows_failed.sum())
a, b, c, d = st.columns(4)
a.metric("Rows checked", f"{len(df):,}")
b.metric("Quality checks", f"{len(result):,}")
c.metric("Failed checks", f"{int(result.status.eq('FAIL').sum()):,}")
d.metric("Rows flagged across checks", f"{failed:,}")
if failed:
    st.error("One or more data-quality rules failed. Review the checks and affected records before using the metrics.")
else:
    st.success("All implemented data-quality checks passed for this local dataset.")
st.subheader("Quality rule results")
st.dataframe(result, use_container_width=True, hide_index=True)
st.download_button("Download quality results", result.to_csv(index=False).encode("utf-8"), "data_quality_results.csv", "text/csv")
dq_path = ROOT / "reports" / "dq_summary.csv"
if dq_path.exists():
    st.subheader("Original pipeline DQ audit")
    original = pd.read_csv(dq_path)
    st.dataframe(original, use_container_width=True, hide_index=True)
    st.download_button("Download original DQ audit", original.to_csv(index=False).encode("utf-8"), "pipeline_dq_summary.csv", "text/csv")
with st.expander("Scope and interpretation"):
    st.markdown("These checks run against the repository's supplied demonstration dataset. They do not monitor a production ingestion pipeline, validate source-system SLAs, or guarantee semantic correctness. A production implementation needs source freshness, schema drift, referential integrity, reconciliation and owner-approved thresholds.")
