-- 01_data_quality.sql | BigQuery Standard SQL
-- Grain: one row per order_id. Same rules as notebook Step 4.
-- Checked locally in DuckDB (scripts/run_sql_checks.py), not run live on BigQuery.
SELECT 'duplicate_order_id' AS rule, COUNT(*) AS rows_checked,
       COUNT(*) - COUNT(DISTINCT order_id) AS rows_failed, 'quarantine' AS action
FROM food_delivery.orders
UNION ALL
SELECT 'null_order_id', COUNT(*), COUNTIF(order_id IS NULL), 'quarantine'
FROM food_delivery.orders
UNION ALL
SELECT 'delivery_time_outside_0_300', COUNT(*),
       COUNTIF(delivery_time_minutes < 0 OR delivery_time_minutes > 300), 'quarantine'
FROM food_delivery.orders
UNION ALL
SELECT 'negative_preparation_time', COUNT(*), COUNTIF(preparation_time_minutes < 0), 'quarantine'
FROM food_delivery.orders
UNION ALL
SELECT 'negative_order_value', COUNT(*), COUNTIF(order_value_sar < 0), 'quarantine'
FROM food_delivery.orders
UNION ALL
SELECT 'negative_distance', COUNT(*), COUNTIF(delivery_distance_km < 0), 'quarantine'
FROM food_delivery.orders
UNION ALL
SELECT 'payment_identity_gap_gt_1_sar', COUNTIF(tip_amount_sar IS NOT NULL),
       COUNTIF(tip_amount_sar IS NOT NULL
               AND ABS(order_value_sar + delivery_fee_sar - discount_amount_sar + tip_amount_sar
                       - final_amount_paid_sar) > 1), 'quarantine'
FROM food_delivery.orders
UNION ALL
SELECT 'null_tip_amount', COUNT(*), COUNTIF(tip_amount_sar IS NULL), 'keep null, flag'
FROM food_delivery.orders
UNION ALL
SELECT 'null_customer_rating', COUNT(*), COUNTIF(customer_rating IS NULL), 'keep null, flag'
FROM food_delivery.orders
UNION ALL
SELECT 'null_delivery_partner_rating', COUNT(*), COUNTIF(delivery_partner_rating IS NULL), 'keep null, flag'
FROM food_delivery.orders
UNION ALL
SELECT 'order_date_outside_2026', COUNT(*), COUNTIF(EXTRACT(YEAR FROM order_date) <> 2026), 'quarantine'
FROM food_delivery.orders
ORDER BY rule;
