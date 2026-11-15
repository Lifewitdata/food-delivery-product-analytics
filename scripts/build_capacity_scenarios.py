"""Hourly rider capacity scenario. Rider supply is a user-provided assumption."""
from pathlib import Path
import argparse
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def build_capacity_scenarios(orders:pd.DataFrame,available_riders:int=100,utilisation_target:float=.8)->pd.DataFrame:
    required={"order_datetime","delivery_time_minutes","cancellation_flag","city"}
    missing=required.difference(orders.columns)
    if missing:raise ValueError(f"Missing columns: {sorted(missing)}")
    if available_riders<1:raise ValueError("available_riders must be >= 1")
    if not 0<utilisation_target<=1:raise ValueError("utilisation_target must be in (0, 1]")
    d=orders.loc[~orders.cancellation_flag.astype(bool)].copy()
    d["order_datetime"]=pd.to_datetime(d.order_datetime,errors="coerce")
    if d.order_datetime.isna().any():raise ValueError("order_datetime contains invalid values")
    d["hour"]=d.order_datetime.dt.floor("h")
    demand=d.groupby(["city","hour"]).agg(orders=("order_datetime","size"),
      avg_delivery_minutes=("delivery_time_minutes","mean")).reset_index()
    demand["available_riders_assumption"]=available_riders
    demand["capacity_orders_per_hour"]=available_riders*60/demand.avg_delivery_minutes.clip(lower=1)
    demand["target_capacity_orders_per_hour"]=demand.capacity_orders_per_hour*utilisation_target
    demand["capacity_gap_orders"]=demand.orders-demand.target_capacity_orders_per_hour
    demand["capacity_status"]=demand.capacity_gap_orders.gt(0).map({True:"potential_shortfall",False:"within_scenario_capacity"})
    demand["provenance"]="scenario_only_rider_supply_assumed_not_observed"
    return demand

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=ROOT/"data/processed/orders_clean_sa.csv")
    p.add_argument("--output-dir",type=Path,default=ROOT/"reports");p.add_argument("--available-riders",type=int,default=100)
    p.add_argument("--utilisation-target",type=float,default=.8);a=p.parse_args()
    out=build_capacity_scenarios(pd.read_csv(a.input),a.available_riders,a.utilisation_target)
    a.output_dir.mkdir(parents=True,exist_ok=True);out.to_csv(a.output_dir/"hourly_capacity_scenario.csv",index=False)
    out.groupby(["city","capacity_status"]).agg(hours=("hour","count"),orders=("orders","sum"),
      avg_capacity_gap=("capacity_gap_orders","mean")).reset_index().to_csv(a.output_dir/"capacity_scenario_summary.csv",index=False)
    print("Scenario output written; rider supply is assumed, not observed.")
if __name__=="__main__":main()
