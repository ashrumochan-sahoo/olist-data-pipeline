WITH source AS (
    SELECT * FROM raw.order_items
)
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp AS shipping_limit_date,
    price::numeric(10,2)           AS price,
    freight_value::numeric(10,2)   AS freight_value
FROM source
WHERE order_id IS NOT NULL
  AND product_id IS NOT NULL
  AND price >= 0
  AND freight_value >= 0