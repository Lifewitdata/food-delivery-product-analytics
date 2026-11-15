"""Restaurant-level performance analysis with explicit synthetic-data caveats."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
st.set_page_config(page_title="Restaurant Performance", layout="wide")
st.title("Restaurant Performance")
path = ROOT / "data" / "processed" / "orders_clean_sa.csv"
if not path.exists():
    st.error("Processed orders file is missing. Run the repository data preparation workflow first.")
    st.stop()

orders = pd.read_csv(path, parse_dates=["order_date"])
required = {"restaurant_id", "city", "cuisine", "order_id", "cancellation_flag", "final_amount_paid_sar"}
missing = required.difference(orders.columns)
if missing:
    st.error(f"Restaurant analysis cannot run; missing columns: {', '.join(sorted(missing))}")
    st.stop()

st.warning("Portfolio demonstration data only. Restaurant IDs and city relationships are seeded; do not treat these rankings as real merchant performance.")
cities = st.multiselect("City", sorted(orders.city.dropna().unique()), default=sorted(orders.city.dropna().unique()))
cuisines = st.multiselect("Cuisine", sorted(orders.cuisine.dropna().unique()), default=sorted(orders.cuisine.dropna().unique()))
view = orders[orders.city.isin(cities) & orders.cuisine.isin(cuisines)].copy()
delivered = view.loc[~view.cancellation_flag.astype(bool)].copy()
summary = view.groupby(["restaurant_id", "city", "cuisine"], dropna=False).agg(
    orders=("order_id", "nunique"),
    cancellations=("cancellation_flag", "sum"),
).reset_index()
sales = delivered.groupby(["restaurant_id", "city", "cuisine"], dropna=False).agg(
    delivered_orders=("order_id", "nunique"),
    gmv_sar=("final_amount_paid_sar", "sum"),
    aov_sar=("final_amount_paid_sar", "mean"),
).reset_index()
summary = summary.merge(sales, on=["restaurant_id", "city", "cuisine"], how="left")
summary["delivered_orders"] = summary.delivered_orders.fillna(0).astype(int)
summary["gmv_sar"] = summary.gmv_sar.fillna(0)
summary["aov_sar"] = summary.aov_sar.fillna(0)
summary["cancellation_rate"] = summary.cancellations / summary.orders.replace(0, pd.NA)
summary = summary.sort_values(["gmv_sar", "delivered_orders"], ascending=False)

a, b, c, d = st.columns(4)
a.metric("Restaurants", f"{summary.restaurant_id.nunique():,}")
b.metric("Orders", f"{int(summary.orders.sum()):,}")
c.metric("Delivered GMV", f"SAR {summary.gmv_sar.sum():,.0f}")
d.metric("Cancellation rate", f"{summary.cancellations.sum() / summary.orders.sum():.1%}" if summary.orders.sum() else "—")
left, right = st.columns(2)
left.subheader("Top restaurants by delivered GMV")
left.bar_chart(summary.head(15).set_index("restaurant_id").gmv_sar)
right.subheader("Cancellation rate by cuisine")
cuisine = view.groupby("cuisine").cancellation_flag.mean().sort_values(ascending=False)
right.bar_chart(cuisine)
st.subheader("Restaurant scorecard")
st.dataframe(summary, use_container_width=True, hide_index=True)
st.download_button("Download filtered restaurant scorecard", summary.to_csv(index=False).encode("utf-8"), "restaurant_performance.csv", "text/csv")
with st.expander("Metric definitions"):
    st.markdown("- **Delivered GMV:** sum of final amount paid for non-cancelled orders; refunds are not deducted.\n- **AOV:** delivered GMV divided by delivered orders.\n- **Cancellation rate:** cancelled orders divided by all orders in the filtered view.")
