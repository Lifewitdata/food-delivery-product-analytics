-- 02_kpi_scorecard.sql | BigQuery Standard SQL
-- GMV and AOV use delivered orders only (cancelled orders earn nothing).
-- Delivery time and on-time rate use delivered orders only.
WITH base AS (
  SELECT
    COUNT(*) AS orders,
    COUNTIF(NOT cancellation_flag) AS delivered_orders,
    COUNTIF(cancellation_flag) AS cancelled_orders,
    SUM(IF(NOT cancellation_flag, final_amount_paid_sar, 0)) AS gmv_sar,
    COUNTIF(NOT cancellation_flag AND NOT delayed_delivery_flag) AS on_time_delivered,
    AVG(IF(NOT cancellation_flag, delivery_time_minutes, NULL)) AS avg_delivery_min,
    COUNTIF(refund_flag) AS refunds,
    COUNT(DISTINCT customer_id) AS customers
  FROM food_delivery.orders
),
repeaters AS (
  SELECT COUNTIF(n > 1) AS repeat_customers
  FROM (SELECT customer_id, COUNT(*) AS n FROM food_delivery.orders GROUP BY customer_id)
)
SELECT 'orders' AS metric, CAST(orders AS FLOAT64) AS value FROM base
UNION ALL SELECT 'delivered_orders', delivered_orders FROM base
UNION ALL SELECT 'cancelled_orders', cancelled_orders FROM base
UNION ALL SELECT 'cancellation_rate', ROUND(SAFE_DIVIDE(cancelled_orders, orders), 4) FROM base
UNION ALL SELECT 'gmv_sar', ROUND(gmv_sar, 2) FROM base
UNION ALL SELECT 'aov_sar', ROUND(SAFE_DIVIDE(gmv_sar, delivered_orders), 2) FROM base
UNION ALL SELECT 'on_time_rate', ROUND(SAFE_DIVIDE(on_time_delivered, delivered_orders), 4) FROM base
UNION ALL SELECT 'avg_delivery_min', ROUND(avg_delivery_min, 2) FROM base
UNION ALL SELECT 'refunds', refunds FROM base
UNION ALL SELECT 'customers', customers FROM base
UNION ALL SELECT 'orders_per_customer', ROUND(SAFE_DIVIDE(orders, customers), 4) FROM base
UNION ALL SELECT 'repeat_rate', ROUND(SAFE_DIVIDE(r.repeat_customers, b.customers), 4)
          FROM base AS b CROSS JOIN repeaters AS r
ORDER BY metric;
