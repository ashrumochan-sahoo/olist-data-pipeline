WITH payments AS (
    SELECT * FROM staging.stg_payments
),
orders AS (
    SELECT order_id, order_purchase_timestamp::date AS order_date
    FROM staging.stg_orders
)
SELECT
    p.order_id,
    p.payment_sequential,
    p.payment_type,
    p.payment_installments,
    p.payment_value,
    o.order_date
FROM payments p
LEFT JOIN orders o USING (order_id)
