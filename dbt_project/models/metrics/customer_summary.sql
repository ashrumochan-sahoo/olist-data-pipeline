WITH orders AS (
    SELECT * FROM warehouse.fact_orders
),
items AS (
    SELECT * FROM warehouse.fact_order_items
),
customer_orders AS (
    SELECT
        o.customer_unique_id,
        COUNT(DISTINCT o.order_id)              AS total_orders,
        MIN(o.order_date)                       AS first_order,
        MAX(o.order_date)                       AS last_order,
        SUM(i.price)                            AS lifetime_value,
        SUM(i.price) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_basket
    FROM orders o
    JOIN items i USING (order_id)
    WHERE o.order_status NOT IN ('cancelled', 'unavailable')
    GROUP BY o.customer_unique_id
)
SELECT
    customer_unique_id                          AS customer,
    first_order,
    last_order,
    total_orders,
    ROUND(lifetime_value::numeric, 2)           AS lifetime_value,
    ROUND(average_basket::numeric, 2)           AS average_basket
FROM customer_orders
ORDER BY lifetime_value DESC
