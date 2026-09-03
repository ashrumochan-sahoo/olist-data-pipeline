from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

sys.path.insert(0, "/opt/airflow")

from pipeline.ingest import run_ingestion

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="olist_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Olist end-to-end data pipeline",
    tags=["olist"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_raw_data",
        python_callable=run_ingestion,
    )

    ingest_task