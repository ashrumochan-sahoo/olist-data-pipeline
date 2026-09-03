from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import sys

sys.path.insert(0, "/opt/airflow")

from pipeline.ingest import run_ingestion
from pipeline.incremental_ingest import run_incremental
from tests.test_data_quality import run_all_checks

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

DBT_CMD = (
    "cd /opt/airflow/dbt_project && "
    "dbt run --profiles-dir /opt/airflow/dbt_project --select {select}"
)

with DAG(
    dag_id="olist_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Olist end-to-end data pipeline",
    tags=["olist"],
) as dag:

    # Part 1 — Full ingestion (first run)
    ingest_raw = PythonOperator(
        task_id="ingest_raw_data",
        python_callable=run_ingestion,
    )

    # Part 2 — dbt staging models
    run_staging = BashOperator(
        task_id="dbt_staging",
        bash_command=DBT_CMD.format(select="staging"),
    )

    # Part 3 — dbt warehouse models
    run_warehouse = BashOperator(
        task_id="dbt_warehouse",
        bash_command=DBT_CMD.format(select="warehouse"),
    )

    # Part 4 — dbt metrics models
    run_metrics = BashOperator(
        task_id="dbt_metrics",
        bash_command=DBT_CMD.format(select="metrics"),
    )

    # Part 5 — data quality checks
    quality_checks = PythonOperator(
        task_id="data_quality_checks",
        python_callable=run_all_checks,
    )

    # Part 6 — incremental load DAG (separate, runs daily)
    ingest_raw >> run_staging >> run_warehouse >> run_metrics >> quality_checks


with DAG(
    dag_id="olist_incremental",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    description="Olist incremental daily pipeline",
    tags=["olist"],
) as incremental_dag:

    # Part 6 — incremental ingestion
    incremental_ingest = PythonOperator(
        task_id="incremental_ingest",
        python_callable=run_incremental,
    )

    # Rebuild staging, warehouse, metrics on top of new data
    inc_staging = BashOperator(
        task_id="dbt_staging",
        bash_command=DBT_CMD.format(select="staging"),
    )

    inc_warehouse = BashOperator(
        task_id="dbt_warehouse",
        bash_command=DBT_CMD.format(select="warehouse"),
    )

    inc_metrics = BashOperator(
        task_id="dbt_metrics",
        bash_command=DBT_CMD.format(select="metrics"),
    )

    inc_quality = PythonOperator(
        task_id="data_quality_checks",
        python_callable=run_all_checks,
    )

    incremental_ingest >> inc_staging >> inc_warehouse >> inc_metrics >> inc_quality
