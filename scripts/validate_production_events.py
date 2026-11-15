"""Validate anonymised production event exports against the canonical event contract.

This script never generates customer behaviour. It validates a supplied export,
normalises approved event aliases and separates rejected rows into quarantine.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCHEMA_PATH=ROOT/"config/production_event_schema.json"
DEFAULT_OUTPUT=ROOT/"data/processed/production_events_validated.csv"
DEFAULT_QUARANTINE=ROOT/"data/processed/production_events_quarantine.csv"
DEFAULT_SUMMARY=ROOT/"reports/production_event_validation.json"

def validate_events(events:pd.DataFrame,schema:dict)->tuple[pd.DataFrame,pd.DataFrame,dict]:
    required=set(schema["required_columns"])
    missing=required.difference(events.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    d=events.copy()
    for col in schema.get("optional_columns",[]):
        if col not in d: d[col]=pd.NA
    d["event_timestamp_parsed"]=pd.to_datetime(d.event_timestamp,utc=True,errors="coerce")
    aliases=schema.get("event_name_aliases",{})
    d["event_name_normalized"]=d.event_name.astype("string").str.strip().str.lower().map(lambda x:aliases.get(x,x))
    allowed=set(schema["canonical_events"])
    duplicate_ids=d.event_id.notna() & d.event_id.duplicated(keep=False)
    errors=[]
    for pos,(_,row) in enumerate(d.iterrows()):
        issues=[]
        for col in ["event_id","session_id","event_name","event_timestamp","platform","city"]:
            if pd.isna(row[col]) or str(row[col]).strip()=="":
                issues.append(f"missing_{col}")
        if duplicate_ids.iloc[pos]:
            issues.append("duplicate_event_id")
        if pd.isna(row.event_timestamp_parsed): issues.append("invalid_event_timestamp")
        else:
            original=pd.Timestamp(row.event_timestamp)
            if original.tzinfo is None: issues.append("timestamp_missing_timezone")
        if row.event_name_normalized not in allowed: issues.append("unknown_event_name")
        if not pd.isna(row.properties_json) and str(row.properties_json).strip():
            try: json.loads(str(row.properties_json))
            except (TypeError,ValueError): issues.append("invalid_properties_json")
        errors.append("|".join(sorted(set(issues))))
    d["validation_errors"]=errors
    d["event_timestamp"]=d.event_timestamp_parsed
    d["event_name"]=d.event_name_normalized
    accepted=d[d.validation_errors.eq("")].drop(columns=["event_timestamp_parsed","event_name_normalized","validation_errors"]).copy()
    rejected=d[~d.validation_errors.eq("")].copy()
    summary={
      "input_rows":int(len(d)),"accepted_rows":int(len(accepted)),"quarantined_rows":int(len(rejected)),
      "acceptance_rate":float(len(accepted)/len(d)) if len(d) else 0.0,
      "unique_sessions":int(accepted.session_id.nunique()),
      "unique_customers":int(accepted.customer_id.nunique()) if accepted.customer_id.notna().any() else 0,
      "event_counts":{str(k):int(v) for k,v in accepted.event_name.value_counts().items()},
      "quarantine_reasons":{str(k):int(v) for k,v in rejected.validation_errors.value_counts().items()},
      "data_source":"user_supplied_production_export",
      "production_data_claim":"Only valid if the supplied export is genuinely sourced from production systems."
    }
    return accepted,rejected,summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True,help="Anonymised CSV export from the product event system")
    p.add_argument("--schema",type=Path,default=SCHEMA_PATH)
    p.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    p.add_argument("--quarantine",type=Path,default=DEFAULT_QUARANTINE)
    p.add_argument("--summary",type=Path,default=DEFAULT_SUMMARY)
    a=p.parse_args()
    schema=json.loads(a.schema.read_text(encoding="utf-8"))
    accepted,rejected,summary=validate_events(pd.read_csv(a.input,dtype="string"),schema)
    for path in [a.output,a.quarantine,a.summary]:path.parent.mkdir(parents=True,exist_ok=True)
    accepted.to_csv(a.output,index=False);rejected.to_csv(a.quarantine,index=False)
    a.summary.write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if len(rejected):raise SystemExit("Validation completed with quarantined rows; inspect quarantine before funnel analysis.")
if __name__=="__main__":main()
