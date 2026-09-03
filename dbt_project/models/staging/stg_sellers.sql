WITH source AS (
    SELECT * FROM raw.sellers
)
SELECT
    seller_id,
    seller_zip_code_prefix,
    TRIM(seller_city)  AS seller_city,
    TRIM(seller_state) AS seller_state
FROM source
WHERE seller_id IS NOT NULL