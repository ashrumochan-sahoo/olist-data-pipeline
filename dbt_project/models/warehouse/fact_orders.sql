WITH orders AS (
    SELECT * FROM staging.stg_orders
),
customers AS (
    SELECT customer_id, customer_unique_id
    FROM staging.stg_customers
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.order_purchase_timestamp::date          AS order_date,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    CASE
        WHEN o.order_delivered_customer_date IS NOT NULL
         AND o.order_estimated_delivery_date IS NOT NULL
        THEN o.order_delivered_customer_date > o.order_estimated_delivery_date
        ELSE false
    END AS is_late_delivery
FROM orders o
LEFT JOIN customers c USING (customer_id)
