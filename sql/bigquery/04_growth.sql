-- 04_growth.sql | BigQuery Standard SQL
-- Long format: dimension / segment. GMV and AOV on delivered orders only.
-- gmv_growth_vs_prev is month-over-month and only filled for dimension = 'month'.
WITH seg AS (
  SELECT 'month' AS dimension, LPAD(CAST(order_month AS STRING), 2, '0') AS segment, * FROM food_delivery.orders
  UNION ALL
  SELECT 'city', city, * FROM food_delivery.orders
  UNION ALL
  SELECT 'cuisine', cuisine, * FROM food_delivery.orders
  UNION ALL
  SELECT 'hour', LPAD(CAST(order_hour AS STRING), 2, '0'), * FROM food_delivery.orders
  UNION ALL
  SELECT 'customer_type', IF(premium_customer_flag, 'premium', 'regular'), * FROM food_delivery.orders
),
agg AS (
  SELECT
    dimension,
    segment,
    COUNT(*) AS orders,
    COUNTIF(NOT cancellation_flag) AS delivered_orders,
    SUM(IF(NOT cancellation_flag, final_amount_paid_sar, 0)) AS gmv_sar
  FROM seg
  GROUP BY dimension, segment
)
SELECT
  dimension,
  segment,
  orders,
  delivered_orders,
  ROUND(gmv_sar, 2) AS gmv_sar,
  ROUND(SAFE_DIVIDE(gmv_sar, delivered_orders), 2) AS aov_sar,
  ROUND(SAFE_DIVIDE(gmv_sar, SUM(gmv_sar) OVER (PARTITION BY dimension)), 4) AS gmv_share,
  IF(dimension = 'month',
     ROUND(SAFE_DIVIDE(gmv_sar, LAG(gmv_sar) OVER (PARTITION BY dimension ORDER BY segment)) - 1, 4),
     NULL) AS gmv_growth_vs_prev
FROM agg
ORDER BY dimension, segment;
