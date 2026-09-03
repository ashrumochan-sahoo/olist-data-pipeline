WITH source AS (
    SELECT * FROM staging.stg_customers
)
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    customer_zip_code_prefix
FROM source
