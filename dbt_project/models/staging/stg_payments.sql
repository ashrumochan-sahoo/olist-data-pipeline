WITH source AS (
    SELECT * FROM raw.payments
)
SELECT
    order_id,
    payment_sequential,
    TRIM(payment_type)          AS payment_type,
    payment_installments,
    payment_value::numeric(10,2) AS payment_value
FROM source
WHERE order_id IS NOT NULL
  AND payment_value >= 0