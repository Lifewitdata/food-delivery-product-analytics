-- 04_growth.sql | PostgreSQL 16 (live, local)
-- Long format: dimension / segment. GMV and AOV on delivered orders only.
-- gmv_growth_vs_prev is month-over-month and only filled for dimension = 'month'.
WITH seg AS (
    SELECT 'month' AS dimension, LPAD(CAST(order_month AS VARCHAR), 2, '0') AS segment, * FROM orders
    UNION ALL
    SELECT 'city', city, * FROM orders
    UNION ALL
    SELECT 'cuisine', cuisine, * FROM orders
    UNION ALL
    SELECT 'hour', LPAD(CAST(order_hour AS VARCHAR), 2, '0'), * FROM orders
    UNION ALL
    SELECT 'customer_type', CASE WHEN premium_customer_flag THEN 'premium' ELSE 'regular' END, * FROM orders
),
agg AS (
    SELECT
        dimension,
        segment,
        COUNT(*) AS orders,
        SUM(CASE WHEN NOT cancellation_flag THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN NOT cancellation_flag THEN final_amount_paid_sar ELSE 0 END) AS gmv_sar
    FROM seg
    GROUP BY dimension, segment
)
SELECT
    dimension,
    segment,
    orders,
    delivered_orders,
    ROUND(gmv_sar, 2) AS gmv_sar,
    ROUND(gmv_sar / NULLIF(delivered_orders, 0), 2) AS aov_sar,
    ROUND(gmv_sar / NULLIF(SUM(gmv_sar) OVER (PARTITION BY dimension), 0), 4) AS gmv_share,
    CASE WHEN dimension = 'month'
         THEN ROUND(gmv_sar / NULLIF(LAG(gmv_sar) OVER (PARTITION BY dimension ORDER BY segment), 0) - 1, 4)
    END AS gmv_growth_vs_prev
FROM agg
ORDER BY dimension, segment;
