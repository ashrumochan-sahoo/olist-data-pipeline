WITH items AS (
    SELECT * FROM warehouse.fact_order_items
),
orders AS (
    SELECT * FROM warehouse.fact_orders
),
reviews AS (
    SELECT
        order_id,
        review_score
    FROM staging.stg_reviews
),
sellers AS (
    SELECT * FROM warehouse.dim_seller
)
SELECT
    i.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT i.order_id)                        AS orders,
    ROUND(SUM(i.price)::numeric, 2)                   AS revenue,
    ROUND(AVG(r.review_score)::numeric, 2)            AS average_review,
    ROUND(
        100.0 * SUM(CASE WHEN o.is_late_delivery THEN 1 ELSE 0 END)
        / NULLIF(COUNT(DISTINCT i.order_id), 0), 2
    )                                                  AS late_delivery_pct
FROM items i
LEFT JOIN orders  o USING (order_id)
LEFT JOIN reviews r USING (order_id)
LEFT JOIN sellers s ON i.seller_id = s.seller_id
GROUP BY i.seller_id, s.seller_city, s.seller_state
ORDER BY revenue DESC
