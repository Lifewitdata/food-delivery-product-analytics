-- 05_delivery.sql | Amazon Redshift dialect port
-- Redshift dialect port, validated in PostgreSQL 16, not run live on AWS.
-- SELECT body is identical to sql/postgres/05_delivery.sql (no FILTER clause, no JSONB operators, so it is Redshift-safe).
-- Delivered orders only. Late rate = share of delivered orders with delayed_delivery_flag.
-- Weather and traffic scores (0-10) are banded in steps of 2; 10 falls in the 8 band.
WITH delivered AS (
    SELECT * FROM orders WHERE NOT cancellation_flag
),
seg AS (
    SELECT 'city' AS dimension, city AS segment, * FROM delivered
    UNION ALL
    SELECT 'hour', LPAD(CAST(order_hour AS VARCHAR), 2, '0'), * FROM delivered
    UNION ALL
    SELECT 'weather_band', LPAD(CAST(LEAST(CAST(FLOOR(weather_severity_score / 2) AS INT) * 2, 8) AS VARCHAR), 2, '0'), * FROM delivered
    UNION ALL
    SELECT 'traffic_band', LPAD(CAST(LEAST(CAST(FLOOR(traffic_level_score / 2) AS INT) * 2, 8) AS VARCHAR), 2, '0'), * FROM delivered
    UNION ALL
    SELECT 'prep_band',
           CASE WHEN preparation_time_minutes < 15 THEN '1_under_15'
                WHEN preparation_time_minutes < 25 THEN '2_15_24'
                WHEN preparation_time_minutes < 35 THEN '3_25_34'
                ELSE '4_35_plus' END, * FROM delivered
    UNION ALL
    SELECT 'rider_experience_years', LPAD(CAST(delivery_partner_experience_years AS VARCHAR), 2, '0'), * FROM delivered
)
SELECT
    dimension,
    segment,
    COUNT(*) AS delivered_orders,
    ROUND(AVG(delivery_time_minutes), 2) AS avg_delivery_min,
    ROUND(1.0 * SUM(CASE WHEN delayed_delivery_flag THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 4) AS late_rate,
    ROUND(CAST(AVG(delivery_efficiency_score) AS NUMERIC), 2) AS avg_efficiency_score,
    COUNT(DISTINCT delivery_partner_id) AS riders
FROM seg
GROUP BY dimension, segment
ORDER BY dimension, segment;
