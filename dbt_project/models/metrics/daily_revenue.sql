WITH orders AS (
    SELECT * FROM warehouse.fact_orders
),
items AS (
    SELECT * FROM warehouse.fact_order_items
),
daily AS (
    SELECT
        o.order_date,
        COUNT(DISTINCT o.order_id)        AS total_orders,
        SUM(i.price)                      AS gmv,
        SUM(i.price) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS aov
    FROM orders o
    JOIN items i USING (order_id)
    WHERE o.order_status NOT IN ('cancelled', 'unavailable')
    GROUP BY o.order_date
)
SELECT
    order_date AS date,
    total_orders AS orders,
    ROUND(gmv::numeric, 2)  AS gmv,
    ROUND(aov::numeric, 2)  AS aov
FROM daily
ORDER BY date
