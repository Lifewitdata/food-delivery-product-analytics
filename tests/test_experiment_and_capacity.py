import pandas as pd
import pytest
from scripts.experiment_analysis import analyse_two_arm,sample_size_per_arm
from scripts.build_capacity_scenarios import build_capacity_scenarios

def test_sample_size_is_positive():
    assert sample_size_per_arm(.1,.02)>0

def test_experiment_analysis_uses_customer_grain():
    d=pd.DataFrame({"customer_id":["a","b","c","d"],"variant":["control","control","treatment","treatment"],"converted":[0,1,1,1]})
    result=analyse_two_arm(d)
    assert result["control_n"]==2 and result["treatment_n"]==2
    assert result["absolute_lift"]==.5

def test_experiment_rejects_duplicate_customers():
    d=pd.DataFrame({"customer_id":["a","a"],"variant":["control","treatment"],"converted":[0,1]})
    with pytest.raises(ValueError,match="one row per"):
        analyse_two_arm(d)

def test_capacity_scenario_labels_assumptions():
    d=pd.DataFrame({"order_datetime":["2026-01-01 12:00","2026-01-01 12:30"],"delivery_time_minutes":[30,30],"cancellation_flag":[False,False],"city":["Riyadh","Riyadh"]})
    out=build_capacity_scenarios(d,available_riders=1,utilisation_target=.5)
    assert out.iloc[0].orders==2
    assert out.iloc[0].provenance=="scenario_only_rider_supply_assumed_not_observed"

def test_capacity_rejects_invalid_rider_supply():
    d=pd.DataFrame({"order_datetime":["2026-01-01"],"delivery_time_minutes":[30],"cancellation_flag":[False],"city":["Riyadh"]})
    with pytest.raises(ValueError,match="available_riders"):
        build_capacity_scenarios(d,available_riders=0)
