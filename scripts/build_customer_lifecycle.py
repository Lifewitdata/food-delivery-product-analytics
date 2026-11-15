"""Build descriptive customer lifecycle features; no causal churn claims."""
from pathlib import Path
import argparse
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def build_customer_lifecycle(orders:pd.DataFrame)->pd.DataFrame:
    required={"customer_id","order_date","order_id","final_amount_paid_sar","cancellation_flag"}
    missing=required.difference(orders.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    d=orders.copy();d["order_date"]=pd.to_datetime(d.order_date,errors="coerce")
    if d.order_date.isna().any():raise ValueError("order_date contains invalid values")
    d=d[~d.cancellation_flag.astype(bool)].copy()
    if d.empty:raise ValueError("No delivered orders available")
    snapshot=d.order_date.max()+pd.Timedelta(days=1)
    x=d.groupby("customer_id").agg(last_order_date=("order_date","max"),first_order_date=("order_date","min"),
       frequency=("order_id","nunique"),monetary_sar=("final_amount_paid_sar","sum")).reset_index()
    x["recency_days"]=(snapshot-x.last_order_date).dt.days
    x["tenure_days"]=(x.last_order_date-x.first_order_date).dt.days
    x["avg_order_value_sar"]=x.monetary_sar/x.frequency
    x["repeat_customer"]=x.frequency.gt(1)
    x["lifecycle_segment"]="active"
    x.loc[x.recency_days>30,"lifecycle_segment"]="at_risk_30d"
    x.loc[x.recency_days>60,"lifecycle_segment"]="dormant_60d"
    x.loc[x.frequency.eq(1),"lifecycle_segment"]="one_time_customer"
    x["cohort_month"]=x.first_order_date.dt.to_period("M").astype(str)
    x["data_note"]="descriptive recency segments; not a validated churn prediction"
    return x

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=ROOT/"data/processed/orders_clean_sa.csv");p.add_argument("--output",type=Path,default=ROOT/"reports/customer_lifecycle.csv");a=p.parse_args()
    out=build_customer_lifecycle(pd.read_csv(a.input));a.output.parent.mkdir(parents=True,exist_ok=True);out.to_csv(a.output,index=False)
    print(out.groupby("lifecycle_segment").customer_id.nunique().to_string())
if __name__=="__main__":main()
