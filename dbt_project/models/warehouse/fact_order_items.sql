WITH items AS (
    SELECT * FROM staging.stg_order_items
),
orders AS (
    SELECT order_id, order_purchase_timestamp::date AS order_date
    FROM staging.stg_orders
)
SELECT
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    o.order_date,
    i.price,
    i.freight_value,
    i.price + i.freight_value AS total_amount,
    i.shipping_limit_date
FROM items i
LEFT JOIN orders o USING (order_id)
