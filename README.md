![tests](https://github.com/xavi092000/finops-project-exercises/actions/workflows/tests.yml/badge.svg)
![tests](https://github.com/xavi092000/finops-project-exercises/actions/workflows/tests.yml/badge.svg)
# FinOps Project Exercises

![tests](https://github.com/xavi092000/finops-project-exercises/actions/workflows/tests.yml/badge.svg)

Analyse des coûts cloud (Juin–Août 2025) avec **KPIs mensuels**, **comparaison prod vs non-prod**, **détection d’anomalies** (z-score) et un **scénario d’économies v1 ~20%**.  
Exports au format CSV + graphiques, suite de tests PyTest (**6/6**), et CI GitHub Actions.

## Sommaire
- [Fonctionnalités](#fonctionnalités)
- [Données](#données)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Exécution rapide](#exécution-rapide)
- [Graphiques générés](#graphiques-générés)
- [API (src/finops_exercises.py)](#api-srcfinops_exercisespy)
- [Tests](#tests)
- [Structure du dépôt](#structure-du-dépôt)
- [Feuille de route](#feuille-de-route)
- [Licence](#licence)

---

## Fonctionnalités
- **KPIs mensuels** : coût total par mois (`kpi_month.csv`).
- **Coûts par service et par mois** : Compute, Storage, Database, Network, AI (`kpi_service_month.csv`).
- **Prod vs Non-prod** : répartition des coûts par environnement (`prod_vs_nonprod.csv`).
- **Anomalies** : détection simple via **z-score** par *service × environnement × jour* (flag `is_anomaly`) → `anomalies.csv`.
- **Scénario d’économies v1** : application d’une politique simple (réduction de coûts) pour estimer une **économie ≈ 20%**, exportée dans `scenario_v1.csv`.
- **CI GitHub Actions** : exécution automatique de la suite de tests à chaque push.

## Données
Source : `data/billing.csv`  
**Schéma des colonnes** :
- `date` (YYYY-MM-DD), `provider`, `service`, `region`, `environment` (`prod`/`non-prod`), `team`,  
  `usage` (unité métier), `unit_cost` (prix unitaire), `cost` (coût *effectif*).

## Prérequis
- Python **3.12+** (OK 3.13)
- `pip`

## Installation
```bash
pip install -r requirements.txt




