import os
import numpy as np
import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    """
    Lit un CSV et convertit 'date' en datetime.
    """
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def add_month_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute deux colonnes :
      - month : 'YYYY-MM'
      - is_weekend : True si samedi/dimanche
    Retourne une COPIE du DataFrame.
    """
    out = df.copy()
    out["month"] = out["date"].dt.to_period("M").astype(str)
    out["is_weekend"] = out["date"].dt.weekday >= 5
    return out


def monthly_costs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retourne le coût total par mois avec colonnes ['month','monthly_cost'],
    trié par 'month' croissant.
    """
    out = (
        df.groupby("month", as_index=False)["cost"].sum()
          .rename(columns={"cost": "monthly_cost"})
          .sort_values("month")
    )
    return out


def service_costs_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retourne le coût par service et par mois avec colonnes ['month','service','cost'].
    """
    out = df.groupby(["month", "service"], as_index=False)["cost"].sum()
    return out


def prod_nonprod_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrège prod vs non-prod (dev/test) par mois.
    Colonnes: ['month','env2','cost'] où env2 ∈ {'prod','non-prod'}.
    """
    tmp = df.copy()
    tmp["env2"] = np.where(tmp["environment"] == "prod", "prod", "non-prod")
    out = tmp.groupby(["month", "env2"], as_index=False)["cost"].sum()
    return out

def detect_anomalies_by_service_env(df: pd.DataFrame, z: float = 3.0) -> pd.DataFrame:
    """
    Ajoute 'is_anomaly' selon un z-score de 'cost' par groupe (service, environment, month).
    Même nombre de lignes que df en sortie.
    """
    out = df.copy()
    if "month" not in out.columns:
        out["date"] = pd.to_datetime(out["date"])
        out["month"] = out["date"].dt.to_period("M").astype(str)

    grp = out.groupby(["service", "environment", "month"])["cost"]
    mu = grp.transform("mean")
    sigma = grp.transform("std").replace(0, np.nan)

    zscore = (out["cost"] - mu) / sigma
    out["is_anomaly"] = zscore.abs() >= z
    out["is_anomaly"] = out["is_anomaly"].fillna(False)
    return out


def apply_scenarios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée un nouveau DF avec 'scenario'='v1' et coûts ajustés:
      - Scheduling non-prod (dev/test): -40%
      - Droitsizing Compute: -15% si env=prod; -25% si env∈{dev,test}
      - Réservations Database (prod): -20%
    """
    out = df.copy()
    out["scenario"] = "v1"

    reduction = np.ones(len(out), dtype=float)

    # Scheduling non-prod
    nonprod = out["environment"].isin(["dev", "test"])
    reduction[nonprod] *= 0.60

    # Droitsizing Compute
    compute = out["service"].eq("Compute")
    reduction[compute & out["environment"].eq("prod")] *= 0.85
    reduction[compute & nonprod] *= 0.75

    # Réservations Database (prod)
    dbprod = out["service"].eq("Database") & out["environment"].eq("prod")
    reduction[dbprod] *= 0.80

    out["cost"] = (out["cost"] * reduction).round(2)
    return out

if __name__ == "__main__":
    # Chemin robuste + dossier outputs
    here = os.path.dirname(__file__)
    data_path = os.path.normpath(os.path.join(here, "..", "data", "billing.csv"))
    outputs_dir = os.path.normpath(os.path.join(here, "..", "outputs"))
    os.makedirs(outputs_dir, exist_ok=True)

    print("Chemin utilisé:", data_path)

    if os.path.exists(data_path):
        # 1) Charger + enrichir
        df = load_data(data_path)
        df2 = add_month_flags(df)

        # 2) Exports KPI
        monthly_costs(df2).to_csv(os.path.join(outputs_dir, "kpi_month.csv"), index=False)
        service_costs_by_month(df2).to_csv(os.path.join(outputs_dir, "kpi_service_month.csv"), index=False)
        prod_nonprod_by_month(df2).to_csv(os.path.join(outputs_dir, "prod_vs_nonprod.csv"), index=False)

        # 3) Anomalies + Scénario
        df_anom = detect_anomalies_by_service_env(df2)
        df_anom.to_csv(os.path.join(outputs_dir, "anomalies.csv"), index=False)

        df_scen = apply_scenarios(df2)
        df_scen.to_csv(os.path.join(outputs_dir, "scenario_v1.csv"), index=False)

        # 4) Économie globale
        base = df2["cost"].sum()
        scen = df_scen["cost"].sum()
        savings = base - scen
        pct = (savings / base) * 100 if base else 0
        print(f"Économie estimée scénario v1: {savings:.2f} ({pct:.1f}%)")

        # 5) Graphiques
        import matplotlib.pyplot as plt

        # (a) Coûts mensuels
        mc = monthly_costs(df2)
        plt.figure()
        plt.plot(mc["month"], mc["monthly_cost"], marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.title("Monthly Costs")
        plt.tight_layout()
        plt.savefig(os.path.join(outputs_dir, "monthly_costs.png"))
        plt.close()

        # (b) Prod vs Non-prod par mois (barres)
        pp = prod_nonprod_by_month(df2).pivot(index="month", columns="env2", values="cost").fillna(0)
        months = pp.index.tolist()
        x = range(len(months))
        width = 0.4
        plt.figure()
        plt.bar([i - width/2 for i in x], pp.get("prod", 0),  width, label="prod")
        plt.bar([i + width/2 for i in x], pp.get("non-prod", 0), width, label="non-prod")
        plt.xticks(list(x), months, rotation=45, ha="right")
        plt.title("Prod vs Non-Prod by Month")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(outputs_dir, "prod_vs_nonprod.png"))
        plt.close()

    else:
        print("Erreur : fichier introuvable:", data_path)
