WITH source AS (
    SELECT * FROM raw.customers
)
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    TRIM(customer_city)  AS customer_city,
    TRIM(customer_state) AS customer_state
FROM source
WHERE customer_id IS NOT NULL