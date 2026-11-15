import json
import pandas as pd
import pytest
from scripts.validate_production_events import validate_events

@pytest.fixture
def schema():
    return {"required_columns":["event_id","session_id","event_name","event_timestamp","platform","city"],
      "optional_columns":["customer_id","anonymous_id","order_id","properties_json"],
      "canonical_events":["app_open","restaurant_view","add_to_cart","checkout_started","order_placed"],
      "event_name_aliases":{"browse":"app_open","checkout":"checkout_started","purchase":"order_placed"}}

def test_accepts_anonymised_timezone_aware_events(schema):
    d=pd.DataFrame([{"event_id":"e1","session_id":"s1","customer_id":None,"event_name":"browse",
      "event_timestamp":"2026-10-01T10:00:00Z","platform":"ios","city":"Riyadh","properties_json":"{}"}])
    accepted,rejected,summary=validate_events(d,schema)
    assert len(accepted)==1 and rejected.empty
    assert accepted.iloc[0].event_name=="app_open"
    assert summary["unique_sessions"]==1

def test_quarantines_duplicate_event_ids(schema):
    d=pd.DataFrame([{"event_id":"e1","session_id":"s1","event_name":"browse","event_timestamp":"2026-10-01T10:00:00Z","platform":"ios","city":"Riyadh"},
      {"event_id":"e1","session_id":"s2","event_name":"browse","event_timestamp":"2026-10-01T10:01:00Z","platform":"ios","city":"Riyadh"}])
    accepted,rejected,summary=validate_events(d,schema)
    assert accepted.empty and len(rejected)==2
    assert "duplicate_event_id" in rejected.iloc[0].validation_errors

def test_quarantines_timestamp_without_timezone(schema):
    d=pd.DataFrame([{"event_id":"e1","session_id":"s1","event_name":"browse","event_timestamp":"2026-10-01 10:00:00","platform":"ios","city":"Riyadh"}])
    accepted,rejected,_=validate_events(d,schema)
    assert accepted.empty and "timestamp_missing_timezone" in rejected.iloc[0].validation_errors

def test_quarantines_unknown_event_and_bad_json(schema):
    d=pd.DataFrame([{"event_id":"e1","session_id":"s1","event_name":"random_click","event_timestamp":"2026-10-01T10:00:00Z","platform":"ios","city":"Riyadh","properties_json":"{bad"}])
    accepted,rejected,_=validate_events(d,schema)
    assert accepted.empty
    assert "unknown_event_name" in rejected.iloc[0].validation_errors
    assert "invalid_properties_json" in rejected.iloc[0].validation_errors

def test_missing_required_columns_raises(schema):
    with pytest.raises(ValueError,match="Missing required columns"):
        validate_events(pd.DataFrame({"event_id":["e1"]}),schema)
