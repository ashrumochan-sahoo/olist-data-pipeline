WITH date_spine AS (
    SELECT generate_series(
        '2016-01-01'::date,
        '2018-12-31'::date,
        '1 day'::interval
    )::date AS date_day
)
SELECT
    date_day                          AS date_id,
    EXTRACT(year  FROM date_day)::int AS year,
    EXTRACT(month FROM date_day)::int AS month,
    EXTRACT(day   FROM date_day)::int AS day,
    EXTRACT(dow   FROM date_day)::int AS day_of_week,
    EXTRACT(week  FROM date_day)::int AS week_of_year,
    EXTRACT(quarter FROM date_day)::int AS quarter,
    TO_CHAR(date_day, 'Month')        AS month_name,
    TO_CHAR(date_day, 'Day')          AS day_name,
    CASE WHEN EXTRACT(dow FROM date_day) IN (0,6)
         THEN true ELSE false END     AS is_weekend
FROM date_spine
