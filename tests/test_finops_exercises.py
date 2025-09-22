import pandas as pd
import numpy as np
from src.finops_exercises import (
    load_data, add_month_flags, monthly_costs,
    service_costs_by_month, prod_nonprod_by_month,
    detect_anomalies_by_service_env, apply_scenarios
)

DATA_PATH = "data/billing.csv"

def test_load_and_flags():
    df = load_data(DATA_PATH)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    df2 = add_month_flags(df.copy())
    assert "month" in df2.columns
    assert "is_weekend" in df2.columns
    assert set(df2["month"].str.len().unique()) == {7}  # 'YYYY-MM'

def test_monthly_costs():
    df = add_month_flags(load_data(DATA_PATH))
    kpi = monthly_costs(df)
    assert list(kpi.columns) == ["month","monthly_cost"]
    # three months (Jun, Jul, Aug)
    assert len(kpi) == 3
    assert (kpi["monthly_cost"] > 0).all()

def test_service_costs():
    df = add_month_flags(load_data(DATA_PATH))
    svc = service_costs_by_month(df)
    assert set(["month","service","cost"]).issubset(svc.columns)
    # at least 5 services across 3 months
    assert svc.shape[0] >= 5*3

def test_prod_nonprod():
    df = add_month_flags(load_data(DATA_PATH))
    pnp = prod_nonprod_by_month(df)
    assert set(["month","env2","cost"]).issubset(pnp.columns)
    assert set(pnp["env2"].unique()) <= {"prod","non-prod"}

def test_anomalies():
    df = add_month_flags(load_data(DATA_PATH))
    out = detect_anomalies_by_service_env(df.copy(), z=3.0)
    assert "is_anomaly" in out.columns
    assert out["is_anomaly"].dtype == bool

def test_scenarios():
    df = add_month_flags(load_data(DATA_PATH))
    scen = apply_scenarios(df)
    assert "scenario" in scen.columns and scen["scenario"].eq("v1").any()
    # cost must be <= original (no negative inflation)
    assert (scen["cost"] <= df["cost"]).all()
