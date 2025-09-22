# FinOps Python — Exercices guidés (vous codez)

## Objectif
Implémentez des fonctions **pas à pas** pour analyser un jeu de facturation cloud et produire des **KPI** utiles.
Vous validez chaque étape avec `pytest`.

## Environnement
```bash
pip install -r requirements.txt
pytest -q
```

## Étapes
1. **Chargement & enrichissement** (`load_data`, `add_month_flags`)
2. **KPI mensuels** (`monthly_costs`), **par service** (`service_costs_by_month`)
3. **Prod vs non-prod** (`prod_nonprod_by_month`)
4. **Anomalies 3σ** (`detect_anomalies_by_service_env`)
5. **Scénarios d'économies** (`apply_scenarios`) — scheduling non-prod, droitsizing, réservations

## Livrables attendus aujourd'hui
- Tests **verts** (tous passent).
- Trois CSV exportés: `kpi_month.csv`, `kpi_service_month.csv`, `prod_vs_nonprod.csv`.
- Un bref `reports/first_findings.md` (3–5 points).

> **IMPORTANT** : pas de solutions dans ce repo. Si vous êtes bloqué, demandez et je vous donnerai un hint ciblé.
