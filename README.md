# Olist Data Pipeline

Production-style data pipeline built on the Brazilian Olist e-commerce dataset. Ingests raw CSVs into Postgres, cleans and transforms with dbt, loads a star schema analytics warehouse, and orchestrates everything with Airflow. Fully dockerized — runs from a single command.

## Architecture

```
CSV Files → raw schema → staging schema → warehouse schema → metrics schema
              (Python)      (dbt views)      (dbt tables)     (dbt tables)
                                    ↑
                              Airflow DAGs
                              Data Quality
```

## Tech Stack

- **Airflow 2.8.1** — pipeline orchestration
- **dbt 1.7.4** — staging, warehouse, and metric transformations
- **Postgres 15** — operational database (raw + staging) and analytics warehouse
- **Python 3.8** — ingestion scripts and data quality checks
- **Docker Compose** — full local environment

## Project Structure

```
olist-data-pipeline/
├── dags/                        # Airflow DAGs
│   └── olist_pipeline.py        # Full pipeline + incremental DAG
├── pipeline/                    # Python ingestion scripts
│   ├── ingest.py                # Full load (raw layer)
│   └── incremental_ingest.py    # Incremental load with watermark strategy
├── dbt_project/
│   ├── models/
│   │   ├── staging/             # 7 staging models (stg_*)
│   │   ├── warehouse/           # 4 dims + 3 facts
│   │   └── metrics/             # 3 business metric tables
│   └── macros/                  # Schema name override
├── tests/
│   └── test_data_quality.py     # 12 automated quality checks
├── Dockerfile.airflow            # Custom Airflow image with dbt
├── docker-compose.yml            # All services
└── requirements.txt
```

## Pipeline Parts

### Part 1 — Raw Ingestion
Loads all 7 Olist CSVs into a `raw` schema in Postgres. Infers schema, preserves types, supports reruns via DROP CASCADE + recreate.

### Part 2 — Staging (dbt)
Cleans raw tables into a `staging` schema. Parses timestamps, standardizes nulls, validates primary keys, fixes column names, filters invalid rows.

Models: `stg_customers`, `stg_orders`, `stg_order_items`, `stg_payments`, `stg_products`, `stg_sellers`, `stg_reviews`

### Part 3 — Warehouse (dbt)
Star schema in a `warehouse` schema, optimized for analytical queries.

**Dimensions:** `dim_customer`, `dim_product`, `dim_seller`, `dim_date`

**Facts:** `fact_orders`, `fact_order_items`, `fact_payments`

### Part 4 — Business Metrics (dbt)
Three pre-aggregated metric tables built on top of the warehouse:

- `daily_revenue` — date, orders, GMV, AOV
- `seller_performance` — orders, revenue, average review, late delivery %
- `customer_summary` — first order, last order, total orders, lifetime value, average basket

### Part 5 — Data Quality
12 automated checks run as the final pipeline task. Pipeline fails if any check fails.

Checks include: no duplicate order IDs, no NULL primary keys, revenue ≥ 0, payment values ≥ 0, every fact record has a matching dimension, valid review scores (1–5).

### Part 6 — Incremental Pipeline
Separate `olist_incremental` DAG runs on a daily schedule.

**Watermark strategy** — for tables with timestamps (`orders`, `order_items`, `reviews`): loads only rows newer than the current MAX timestamp in the raw table.

**PK dedup strategy** — for tables without timestamps (`customers`, `products`, `sellers`, `payments`): loads only rows whose primary key doesn't already exist in the raw table.

No CDC required. Duplicates are handled at ingestion time before data reaches staging.

## Quickstart

**Prerequisites:** Docker Desktop, Git

```bash
# 1. Clone the repo
git clone https://github.com/ashrumochan-sahoo/olist-data-pipeline.git
cd olist-data-pipeline

# 2. Download the Olist dataset from Kaggle
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Extract all CSVs (except geolocation) into data/raw/

# 3. Build and start all services
docker compose build
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler

# 4. Open Airflow UI
# http://localhost:8080
# Username: admin / Password: admin

# 5. Trigger the pipeline
# Enable and trigger the olist_pipeline DAG
```

## DAGs

| DAG | Schedule | Description |
|---|---|---|
| `olist_pipeline` | Manual | Full pipeline — ingest, transform, quality checks |
| `olist_incremental` | Daily | Incremental load — new rows only |

## Data Quality Results

All 12 checks pass on the full Olist dataset:

| Check | Result |
|---|---|
| No duplicate order IDs | ✅ PASS |
| No NULL order IDs | ✅ PASS |
| No NULL customer IDs | ✅ PASS |
| Revenue non-negative | ✅ PASS |
| Payment values non-negative | ✅ PASS |
| Fact items have matching orders | ✅ PASS |
| Fact items have matching products | ✅ PASS |
| Fact items have matching sellers | ✅ PASS |
| dim_customer not empty | ✅ PASS |
| dim_product not empty | ✅ PASS |
| Valid review scores (1–5) | ✅ PASS |
| No duplicate payments | ✅ PASS |

## Dataset

Brazilian E-Commerce Public Dataset by Olist — 100k orders from 2016–2018.

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce