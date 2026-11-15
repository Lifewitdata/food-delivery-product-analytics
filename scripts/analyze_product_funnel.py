"""Create session-grain funnel metrics from product_sessions.csv.

This is a demonstration dataset: the generated non-converting journeys are not
observed traffic and resulting conversion rates are not production estimates.
"""
from pathlib import Path
import argparse
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
STAGES=["app_open","restaurant_view","add_to_cart","checkout_started","order_placed"]

def analyze(events: pd.DataFrame):
    required={"session_id","event_name","event_timestamp","event_sequence","converted","data_provenance"}
    missing=required.difference(events.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    if events.session_id.isna().any(): raise ValueError("session_id cannot be null")
    if events.duplicated(["session_id","event_sequence"]).any():
        raise ValueError("Duplicate event sequence within a session")
    events=events.copy()
    events["event_timestamp"]=pd.to_datetime(events.event_timestamp,errors="coerce")
    if events.event_timestamp.isna().any(): raise ValueError("Invalid event_timestamp")
    unknown=set(events.event_name.dropna())-set(STAGES)
    if unknown: raise ValueError(f"Unknown funnel events: {sorted(unknown)}")
    per_session=events.sort_values(["session_id","event_sequence"]).groupby("session_id").agg(
        deepest_stage=("event_name",lambda s:max((STAGES.index(x) for x in s),default=-1)),
        converted=("converted","max"), provenance=("data_provenance","first"),
        customer_id=("customer_id","first") if "customer_id" in events else ("session_id","first")
    )
    total=len(per_session)
    rows=[]
    for i,stage in enumerate(STAGES):
        reached=int((per_session.deepest_stage>=i).sum())
        previous=int((per_session.deepest_stage>=i-1).sum()) if i else total
        rows.append({"stage":stage,"sessions_reached":reached,
                     "conversion_from_entry":reached/total if total else 0,
                     "stage_conversion":reached/previous if previous else 0,
                     "stage_abandonment":1-reached/previous if previous else 0,
                     "sessions_lost_at_stage":previous-reached,
                     "total_sessions":total})
    summary=pd.DataFrame(rows)
    provenance=per_session.groupby("provenance").size().rename("sessions").reset_index()
    return summary, provenance, per_session.reset_index()

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",type=Path,default=ROOT/"data/processed/product_sessions.csv")
    p.add_argument("--output-dir",type=Path,default=ROOT/"reports"); a=p.parse_args()
    events=pd.read_csv(a.input); summary,provenance,detail=analyze(events)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    summary.to_csv(a.output_dir/"product_funnel.csv",index=False)
    provenance.to_csv(a.output_dir/"funnel_data_provenance.csv",index=False)
    detail.to_csv(a.output_dir/"session_funnel_detail.csv",index=False)
    print(summary.to_string(index=False)); print("Generated sessions are simulated; do not interpret as actual platform conversion.")
if __name__=="__main__": main()
