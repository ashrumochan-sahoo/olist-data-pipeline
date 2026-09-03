import os
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv(
    "OLIST_DB_URL",
    "postgresql+psycopg2://olist:olist@postgres-olist:5432/olist_db"
)

DATA_DIR = os.getenv("DATA_DIR", "/opt/airflow/data/raw")

# Each table's watermark column — the column we use to detect new records
WATERMARK_CONFIG = {
    "orders": {
        "csv":       "olist_orders_dataset.csv",
        "pk":        "order_id",
        "watermark": "order_purchase_timestamp",
    },
    "order_items": {
        "csv":       "olist_order_items_dataset.csv",
        "pk":        "order_id",
        "watermark": "shipping_limit_date",
    },
    "reviews": {
        "csv":       "olist_order_reviews_dataset.csv",
        "pk":        "review_id",
        "watermark": "review_answer_timestamp",
    },
    "payments": {
        "csv":       "olist_order_payments_dataset.csv",
        "pk":        "order_id",
        "watermark": None,  # no timestamp — use PK-based dedup
    },
    "customers": {
        "csv":       "olist_customers_dataset.csv",
        "pk":        "customer_id",
        "watermark": None,
    },
    "products": {
        "csv":       "olist_products_dataset.csv",
        "pk":        "product_id",
        "watermark": None,
    },
    "sellers": {
        "csv":       "olist_sellers_dataset.csv",
        "pk":        "seller_id",
        "watermark": None,
    },
}


def get_engine():
    return create_engine(DB_URL)


def get_max_watermark(engine, table_name, watermark_col):
    """Get the highest watermark value currently in the raw table."""
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT MAX({watermark_col}) FROM raw.{table_name}")
        ).fetchone()
    return result[0] if result else None


def get_existing_pks(engine, table_name, pk_col):
    """Get all existing primary keys from the raw table."""
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT {pk_col} FROM raw.{table_name}")
        ).fetchall()
    return set(row[0] for row in result)


def incremental_load(engine, table_name, config):
    csv_file = config["csv"]
    pk_col   = config["pk"]
    wm_col   = config["watermark"]

    filepath = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(filepath):
        logger.warning(f"File not found, skipping: {filepath}")
        return

    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower() for c in df.columns]
    total_rows = len(df)

    if wm_col and wm_col in df.columns:
        # Watermark strategy — only load rows newer than max watermark
        max_wm = get_max_watermark(engine, table_name, wm_col)
        if max_wm:
            df[wm_col] = pd.to_datetime(df[wm_col], errors="coerce")
            new_rows = df[df[wm_col] > pd.Timestamp(max_wm)]
            logger.info(
                f"{table_name}: watermark={max_wm}, "
                f"new rows={len(new_rows)}/{total_rows}"
            )
        else:
            new_rows = df
            logger.info(f"{table_name}: no watermark found, loading all {total_rows} rows")
    else:
        # PK dedup strategy — only insert rows whose PK doesn't exist yet
        existing_pks = get_existing_pks(engine, table_name, pk_col)
        new_rows = df[~df[pk_col].isin(existing_pks)]
        logger.info(
            f"{table_name}: pk dedup, "
            f"new rows={len(new_rows)}/{total_rows}"
        )

    if len(new_rows) == 0:
        logger.info(f"{table_name}: no new rows to load")
        return

    new_rows.to_sql(
        name=table_name,
        schema="raw",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    logger.info(f"{table_name}: inserted {len(new_rows)} new rows")


def run_incremental():
    engine = get_engine()
    for table_name, config in WATERMARK_CONFIG.items():
        incremental_load(engine, table_name, config)
    logger.info("Incremental load complete")


if __name__ == "__main__":
    run_incremental()
