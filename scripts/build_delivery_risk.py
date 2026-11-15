"""Create a delivered-order SLA exception queue from supplied ETA fields."""
from pathlib import Path
import argparse
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def build_delivery_risk(orders:pd.DataFrame,eta_buffer_minutes:int=0)->pd.DataFrame:
    required={"order_id","city","order_hour","delivery_time_minutes","estimated_delivery_time","cancellation_flag","delivery_distance_km"}
    missing=required.difference(orders.columns)
    if missing:raise ValueError(f"Missing columns: {sorted(missing)}")
    if eta_buffer_minutes<0:raise ValueError("eta_buffer_minutes must be non-negative")
    d=orders.loc[~orders.cancellation_flag.astype(bool)].copy()
    d["eta_variance_minutes"]=d.delivery_time_minutes-d.estimated_delivery_time
    d["eta_breach"]=d.eta_variance_minutes>eta_buffer_minutes
    d["risk_band"]="within_eta"
    d.loc[d.eta_variance_minutes>eta_buffer_minutes,"risk_band"]="eta_breach"
    d.loc[d.eta_variance_minutes>15+eta_buffer_minutes,"risk_band"]="high_risk_15m_plus"
    d["risk_reason"]=d.risk_band.map({"within_eta":"Within configured ETA threshold","eta_breach":"Actual delivery exceeded ETA","high_risk_15m_plus":"Actual delivery exceeded ETA by more than 15 minutes"})
    d["operational_note"]="retrospective exception analysis; no live dispatch or rider-capacity feed"
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=ROOT/"data/processed/orders_clean_sa.csv");p.add_argument("--output-dir",type=Path,default=ROOT/"reports");p.add_argument("--eta-buffer",type=int,default=0);a=p.parse_args()
    out=build_delivery_risk(pd.read_csv(a.input),a.eta_buffer);a.output_dir.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.output_dir/"delivery_exception_queue.csv",index=False)
    out.groupby(["city","risk_band"]).size().rename("orders").reset_index().to_csv(a.output_dir/"delivery_risk_by_city.csv",index=False)
    print(out.groupby(["city","risk_band"]).size().to_string())
if __name__=="__main__":main()
