WITH source AS (
    SELECT * FROM raw.orders
)
SELECT
    order_id,
    customer_id,
    TRIM(order_status)                            AS order_status,
    order_purchase_timestamp::timestamp           AS order_purchase_timestamp,
    order_approved_at::timestamp                  AS order_approved_at,
    order_delivered_carrier_date::timestamp       AS order_delivered_carrier_date,
    order_delivered_customer_date::timestamp      AS order_delivered_customer_date,
    order_estimated_delivery_date::timestamp      AS order_estimated_delivery_date
FROM source
WHERE order_id IS NOT NULL
  AND customer_id IS NOT NULL