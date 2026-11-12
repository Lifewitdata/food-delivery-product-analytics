-- 02_kpi_scorecard.sql | Amazon Redshift dialect port
-- Redshift dialect port, validated in PostgreSQL 16, not run live on AWS.
-- SELECT body is identical to sql/postgres/02_kpi_scorecard.sql (no FILTER clause, no JSONB operators, so it is Redshift-safe).
-- GMV and AOV use delivered orders only. Delivery time and on-time rate use delivered orders only.
WITH base AS (
    SELECT
        COUNT(*) AS orders,
        SUM(CASE WHEN NOT cancellation_flag THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN cancellation_flag THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(CASE WHEN NOT cancellation_flag THEN final_amount_paid_sar ELSE 0 END) AS gmv_sar,
        SUM(CASE WHEN NOT cancellation_flag AND NOT delayed_delivery_flag THEN 1 ELSE 0 END) AS on_time_delivered,
        AVG(CASE WHEN NOT cancellation_flag THEN delivery_time_minutes END) AS avg_delivery_min,
        SUM(CASE WHEN refund_flag THEN 1 ELSE 0 END) AS refunds,
        COUNT(DISTINCT customer_id) AS customers
    FROM orders
),
repeaters AS (
    SELECT SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END) AS repeat_customers
    FROM (SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id) AS per_customer
)
SELECT 'orders' AS metric, CAST(orders AS NUMERIC(18,4)) AS value FROM base
UNION ALL SELECT 'delivered_orders', delivered_orders FROM base
UNION ALL SELECT 'cancelled_orders', cancelled_orders FROM base
UNION ALL SELECT 'cancellation_rate', ROUND(1.0 * cancelled_orders / NULLIF(orders, 0), 4) FROM base
UNION ALL SELECT 'gmv_sar', ROUND(gmv_sar, 2) FROM base
UNION ALL SELECT 'aov_sar', ROUND(gmv_sar / NULLIF(delivered_orders, 0), 2) FROM base
UNION ALL SELECT 'on_time_rate', ROUND(1.0 * on_time_delivered / NULLIF(delivered_orders, 0), 4) FROM base
UNION ALL SELECT 'avg_delivery_min', ROUND(CAST(avg_delivery_min AS NUMERIC), 2) FROM base
UNION ALL SELECT 'refunds', refunds FROM base
UNION ALL SELECT 'customers', customers FROM base
UNION ALL SELECT 'orders_per_customer', ROUND(1.0 * orders / NULLIF(customers, 0), 4) FROM base
UNION ALL SELECT 'repeat_rate', ROUND(1.0 * r.repeat_customers / NULLIF(b.customers, 0), 4)
          FROM base AS b CROSS JOIN repeaters AS r
ORDER BY metric;
