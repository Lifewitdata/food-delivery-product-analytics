"""Customer-randomised two-arm experiment utilities.

Input must contain one row per eligible, assigned customer. Do not pass order rows
or event rows as if they were independent randomisation units.
"""
import argparse
from pathlib import Path
import pandas as pd
from scipy.stats import chisquare
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
ROOT=Path(__file__).resolve().parents[1]

def sample_size_per_arm(baseline_rate:float,mde_absolute:float,alpha:float=.05,power:float=.8)->int:
    if not 0<baseline_rate<1:raise ValueError("baseline_rate must be between 0 and 1")
    treatment=baseline_rate+mde_absolute
    if not 0<treatment<1 or mde_absolute<=0:raise ValueError("MDE must be positive and baseline + MDE below 1")
    if not 0<alpha<1 or not 0<power<1:raise ValueError("alpha and power must be between 0 and 1")
    effect=abs(proportion_effectsize(treatment,baseline_rate))
    return int(NormalIndPower().solve_power(effect_size=effect,alpha=alpha,power=power,ratio=1,alternative="two-sided")+0.999999)

def analyse_two_arm(data:pd.DataFrame,unit_col:str="customer_id",variant_col:str="variant",outcome_col:str="converted",control:str="control",treatment:str="treatment",expected_ratio:float=1.0):
    required={unit_col,variant_col,outcome_col}
    missing=required.difference(data.columns)
    if missing:raise ValueError(f"Missing columns: {sorted(missing)}")
    d=data[[unit_col,variant_col,outcome_col]].dropna().copy()
    if d[unit_col].duplicated().any():raise ValueError("Input must have exactly one row per randomisation unit")
    if set(d[variant_col].unique())!={control,treatment}:raise ValueError("Exactly control and treatment variants are required")
    if not d[outcome_col].isin([0,1,False,True]).all():raise ValueError("Outcome must be binary 0/1")
    c=d[d[variant_col].eq(control)][outcome_col].astype(int);t=d[d[variant_col].eq(treatment)][outcome_col].astype(int)
    counts=d[variant_col].value_counts().reindex([control,treatment]).astype(int)
    srm=chisquare(counts.to_numpy(),f_exp=[counts.sum()/(1+expected_ratio),counts.sum()*expected_ratio/(1+expected_ratio)])
    z,p=proportions_ztest([int(t.sum()),int(c.sum())],[len(t),len(c)])
    pc=c.mean();pt=t.mean();diff=pt-pc
    se=((pt*(1-pt)/len(t))+(pc*(1-pc)/len(c)))**.5
    return {"control_n":len(c),"treatment_n":len(t),"control_rate":pc,"treatment_rate":pt,
      "absolute_lift":diff,"ci_low":diff-1.96*se,"ci_high":diff+1.96*se,"p_value":float(p),
      "srm_p_value":float(srm.pvalue),"srm_pass":bool(srm.pvalue>=.001),
      "randomisation_unit":unit_col,"analysis":"two-sided two-proportion z-test; customer-level ITT"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,default=ROOT/"reports/experiment_analysis.json");a=p.parse_args()
    import json
    d=pd.read_csv(a.input);result=analyse_two_arm(d);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
