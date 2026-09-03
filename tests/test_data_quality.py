import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host":     "postgres-olist",
    "port":     5432,
    "dbname":   "olist_db",
    "user":     "olist",
    "password": "olist",
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def run_check(conn, check_name, query, expect_zero=True):
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchone()[0]

    if expect_zero and result != 0:
        logger.error(f"FAIL [{check_name}]: expected 0, got {result}")
        return False
    elif not expect_zero and result == 0:
        logger.error(f"FAIL [{check_name}]: expected > 0, got {result}")
        return False
    else:
        logger.info(f"PASS [{check_name}]: {result}")
        return True


def run_all_checks():
    conn = get_conn()
    results = []

    checks = [
        (
            "no_duplicate_order_ids",
            """
            SELECT COUNT(*) FROM (
                SELECT order_id, COUNT(*) AS cnt
                FROM warehouse.fact_orders
                GROUP BY order_id
                HAVING COUNT(*) > 1
            ) dupes
            """,
            True,
        ),
        (
            "no_null_order_ids",
            "SELECT COUNT(*) FROM warehouse.fact_orders WHERE order_id IS NULL",
            True,
        ),
        (
            "no_null_customer_ids",
            "SELECT COUNT(*) FROM warehouse.fact_orders WHERE customer_id IS NULL",
            True,
        ),
        (
            "revenue_non_negative",
            "SELECT COUNT(*) FROM warehouse.fact_order_items WHERE price < 0",
            True,
        ),
        (
            "payment_value_non_negative",
            "SELECT COUNT(*) FROM warehouse.fact_payments WHERE payment_value < 0",
            True,
        ),
        (
            "fact_items_have_orders",
            """
            SELECT COUNT(*) FROM warehouse.fact_order_items i
            LEFT JOIN warehouse.fact_orders o USING (order_id)
            WHERE o.order_id IS NULL
            """,
            True,
        ),
        (
            "fact_items_have_products",
            """
            SELECT COUNT(*) FROM warehouse.fact_order_items i
            LEFT JOIN warehouse.dim_product p USING (product_id)
            WHERE p.product_id IS NULL
            """,
            True,
        ),
        (
            "fact_items_have_sellers",
            """
            SELECT COUNT(*) FROM warehouse.fact_order_items i
            LEFT JOIN warehouse.dim_seller s USING (seller_id)
            WHERE s.seller_id IS NULL
            """,
            True,
        ),
        (
            "dim_customer_not_empty",
            "SELECT COUNT(*) FROM warehouse.dim_customer",
            False,
        ),
        (
            "dim_product_not_empty",
            "SELECT COUNT(*) FROM warehouse.dim_product",
            False,
        ),
        (
            "valid_review_scores",
            """
            SELECT COUNT(*) FROM staging.stg_reviews
            WHERE review_score NOT BETWEEN 1 AND 5
            """,
            True,
        ),
        (
            "no_duplicate_payments",
            """
            SELECT COUNT(*) FROM (
                SELECT order_id, payment_sequential, COUNT(*)
                FROM warehouse.fact_payments
                GROUP BY order_id, payment_sequential
                HAVING COUNT(*) > 1
            ) dupes
            """,
            True,
        ),
    ]

    for check_name, query, expect_zero in checks:
        passed = run_check(conn, check_name, query, expect_zero)
        results.append((check_name, passed))

    conn.close()

    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    logger.info(f"\n{'='*50}")
    logger.info(f"Results: {len(passed)} passed, {len(failed)} failed")

    if failed:
        failed_names = [name for name, _ in failed]
        raise ValueError(f"Data quality checks failed: {failed_names}")

    logger.info("All data quality checks passed.")
