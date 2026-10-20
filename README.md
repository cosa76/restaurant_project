# restaurant_project

Projet dbt d'analyse des ventes d'un restaurant, sur DuckDB, avec CI/CD GitHub Actions et trois environnements (dev, uat, prod).

## Architecture

```
seeds/restaurant_orders.csv          données brutes (commandes)
  └─ stg_restaurant_orders           staging : renommage, typage, montant
       ├─ fct_orders                 faits : une ligne par commande (contrat appliqué)
       ├─ dim_customers              dimension clients
       ├─ dim_menu_items             dimension plats
       └─ agg_*                      agrégats : jour, plat, paiement, heure
```

## Démarrer

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt -r requirements-dev.txt
dbt build --profiles-dir .      # seed + modèles + tests sur dev
sqlfluff lint models tests      # style SQL
```

## Simuler de nouvelles données

```bash
python scripts/generate_daily_orders.py            # le jour suivant
python scripts/generate_daily_orders.py --days 7   # une semaine
```

## Environnements

| Target | Base | Déploiement |
|--------|------|-------------|
| dev    | `restaurant.duckdb`      | local et CI sur chaque pull request |
| uat    | `restaurant_uat.duckdb`  | automatique à chaque merge sur `main` |
| prod   | `restaurant_prod.duckdb` | après l'uat, avec approbation manuelle |

## Règles de contribution

1. Une branche par changement, jamais de commit direct sur `main`.
2. Une pull request qui remplit le modèle fourni.
3. La CI (`sql-lint` et `dbt-build`) doit être verte avant le merge.
4. Tout nouveau modèle est documenté et testé dans un fichier `.yml`.

## Conventions

- `stg_` : une vue par source, sans règle métier.
- `fct_` / `dim_` : schéma en étoile, matérialisé en tables.
- `agg_` : agrégats prêts pour les tableaux de bord.
- SQL en minuscules, noms en `snake_case`, vérifiés par sqlfluff.
