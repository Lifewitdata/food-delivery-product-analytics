-- 01_data_quality.sql | PostgreSQL 16 (live, local)
-- Grain: one row per order_id. Same rules as notebook Step 4 and sql/bigquery/01.
SELECT 'duplicate_order_id' AS rule, COUNT(*) AS rows_checked,
       COUNT(*) - COUNT(DISTINCT order_id) AS rows_failed, 'quarantine' AS action
FROM orders
UNION ALL
SELECT 'null_order_id', COUNT(*), SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END), 'quarantine'
FROM orders
UNION ALL
SELECT 'delivery_time_outside_0_300', COUNT(*),
       SUM(CASE WHEN delivery_time_minutes < 0 OR delivery_time_minutes > 300 THEN 1 ELSE 0 END), 'quarantine'
FROM orders
UNION ALL
SELECT 'negative_preparation_time', COUNT(*), SUM(CASE WHEN preparation_time_minutes < 0 THEN 1 ELSE 0 END), 'quarantine'
FROM orders
UNION ALL
SELECT 'negative_order_value', COUNT(*), SUM(CASE WHEN order_value_sar < 0 THEN 1 ELSE 0 END), 'quarantine'
FROM orders
UNION ALL
SELECT 'negative_distance', COUNT(*), SUM(CASE WHEN delivery_distance_km < 0 THEN 1 ELSE 0 END), 'quarantine'
FROM orders
UNION ALL
SELECT 'payment_identity_gap_gt_1_sar', SUM(CASE WHEN tip_amount_sar IS NOT NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN tip_amount_sar IS NOT NULL
                 AND ABS(order_value_sar + delivery_fee_sar - discount_amount_sar + tip_amount_sar
                         - final_amount_paid_sar) > 1 THEN 1 ELSE 0 END), 'quarantine'
FROM orders
UNION ALL
SELECT 'null_tip_amount', COUNT(*), SUM(CASE WHEN tip_amount_sar IS NULL THEN 1 ELSE 0 END), 'keep null, flag'
FROM orders
UNION ALL
SELECT 'null_customer_rating', COUNT(*), SUM(CASE WHEN customer_rating IS NULL THEN 1 ELSE 0 END), 'keep null, flag'
FROM orders
UNION ALL
SELECT 'null_delivery_partner_rating', COUNT(*), SUM(CASE WHEN delivery_partner_rating IS NULL THEN 1 ELSE 0 END), 'keep null, flag'
FROM orders
UNION ALL
SELECT 'order_date_outside_2026', COUNT(*), SUM(CASE WHEN EXTRACT(YEAR FROM order_date) <> 2026 THEN 1 ELSE 0 END), 'quarantine'
FROM orders
ORDER BY rule;
