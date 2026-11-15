"""Build scenario-based order contribution metrics; inputs are not actual finance data."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_CONFIG=ROOT/"config/unit_economics_assumptions.json"

def build_unit_economics(orders:pd.DataFrame, assumptions:dict)->pd.DataFrame:
    required={"order_id","customer_id","city","cancellation_flag","order_value_sar",
              "final_amount_paid_sar","discount_amount_sar","refund_flag"}
    missing=required.difference(orders.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    for key in ["commission_rate","delivery_cost_per_order_sar","payment_processing_rate",
                "promo_subsidy_rate_of_discount","refund_rate_of_refunded_order_value"]:
        if key not in assumptions: raise ValueError(f"Missing assumption: {key}")
    rates=[assumptions["commission_rate"],assumptions["payment_processing_rate"],
           assumptions["promo_subsidy_rate_of_discount"],assumptions["refund_rate_of_refunded_order_value"]]
    if any(not 0<=float(x)<=1 for x in rates): raise ValueError("Rates must be between 0 and 1")
    if float(assumptions["delivery_cost_per_order_sar"])<0: raise ValueError("Delivery cost cannot be negative")
    d=orders.copy()
    delivered=~d.cancellation_flag.astype(bool)
    d["is_delivered"]=delivered
    d["commission_revenue_sar"]=np.where(delivered,d.order_value_sar*assumptions["commission_rate"],0)
    d["delivery_cost_sar"]=np.where(delivered,assumptions["delivery_cost_per_order_sar"],0)
    d["payment_processing_cost_sar"]=np.where(delivered,d.final_amount_paid_sar*assumptions["payment_processing_rate"],0)
    d["promo_subsidy_sar"]=np.where(delivered,d.discount_amount_sar*assumptions["promo_subsidy_rate_of_discount"],0)
    d["refund_cost_sar"]=np.where(delivered & d.refund_flag.astype(bool),
       d.final_amount_paid_sar*assumptions["refund_rate_of_refunded_order_value"],0)
    d["contribution_scenario_sar"]=d.commission_revenue_sar-d.delivery_cost_sar-d.payment_processing_cost_sar-d.promo_subsidy_sar-d.refund_cost_sar
    d["economics_provenance"]="illustrative_assumption_scenario_not_actual_profit"
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=ROOT/"data/processed/orders_clean_sa.csv")
    p.add_argument("--config",type=Path,default=DEFAULT_CONFIG);p.add_argument("--output-dir",type=Path,default=ROOT/"reports");a=p.parse_args()
    orders=pd.read_csv(a.input); assumptions=json.loads(a.config.read_text(encoding="utf-8"))
    out=build_unit_economics(orders,assumptions);a.output_dir.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.output_dir/"order_unit_economics_scenario.csv",index=False)
    summary=out.groupby("city").agg(orders=("order_id","count"),delivered=("is_delivered","sum"),
       scenario_contribution_sar=("contribution_scenario_sar","sum")).reset_index()
    delivered_avg=out.loc[out.is_delivered].groupby("city").contribution_scenario_sar.mean().rename("avg_scenario_contribution_per_delivered_order")
    summary=summary.merge(delivered_avg,on="city",how="left")
    summary["provenance"]="illustrative_assumption_scenario_not_actual_profit"
    summary.to_csv(a.output_dir/"unit_economics_scenario_by_city.csv",index=False)
    print("Wrote scenario economics. These are not actual revenue, margin or profit.")
if __name__=="__main__":main()
