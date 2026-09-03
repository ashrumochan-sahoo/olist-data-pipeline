import os
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection to postgres-olist
DB_URL = os.getenv(
    "OLIST_DB_URL",
    "postgresql+psycopg2://olist:olist@postgres-olist:5432/olist_db"
)

# Map each CSV file to a table name in the raw schema
CSV_TABLE_MAP = {
    "olist_customers_dataset.csv":      "customers",
    "olist_orders_dataset.csv":         "orders",
    "olist_order_items_dataset.csv":    "order_items",
    "olist_order_payments_dataset.csv": "payments",
    "olist_products_dataset.csv":       "products",
    "olist_sellers_dataset.csv":        "sellers",
    "olist_order_reviews_dataset.csv":  "reviews",
}

DATA_DIR = os.getenv("DATA_DIR", "/opt/airflow/data/raw")


def get_engine():
    return create_engine(DB_URL)


def create_raw_schema(engine):
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
    logger.info("Raw schema ready")


def ingest_csv(engine, csv_filename, table_name):
    filepath = os.path.join(DATA_DIR, csv_filename)

    if not os.path.exists(filepath):
        logger.warning(f"File not found, skipping: {filepath}")
        return

    logger.info(f"Reading {csv_filename}...")
    df = pd.read_csv(filepath)

    # Strip whitespace from column names
    df.columns = [c.strip().lower() for c in df.columns]

    row_count = len(df)
    logger.info(f"Loaded {row_count} rows from {csv_filename}")

    # Write to raw schema
    # if_exists='replace' drops and recreates the table on each run
    # This handles reruns without duplicating data
    df.to_sql(
        name=table_name,
        schema="raw",
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000,
    )

    logger.info(f"Ingested {row_count} rows into raw.{table_name}")


def run_ingestion():
    engine = get_engine()
    create_raw_schema(engine)

    for csv_file, table_name in CSV_TABLE_MAP.items():
        ingest_csv(engine, csv_file, table_name)

    logger.info("All files ingested successfully")


if __name__ == "__main__":
    run_ingestion()