-- 07_ab_scorecard.sql | Amazon Redshift dialect port
-- Redshift dialect port, validated in PostgreSQL 16, not run live on AWS.
-- SELECT body is identical to sql/postgres/07_ab_scorecard.sql (no FILTER clause, no JSONB operators, so it is Redshift-safe).
-- Free-delivery threshold test: control SAR 75 vs treatment SAR 50, randomised by customer.
-- Runs on OBSERVED data. The simulated treatment effect lives only in the notebook (Step 7).
-- Primary: conversion = delivered / checkout sessions. Guardrails: cancellation, delivery time.
SELECT
    ab_group,
    MAX(ab_threshold_sar) AS threshold_sar,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(*) AS checkout_sessions,
    SUM(CASE WHEN NOT cancellation_flag THEN 1 ELSE 0 END) AS delivered_orders,
    ROUND(1.0 * SUM(CASE WHEN NOT cancellation_flag THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 4) AS conversion,
    ROUND(1.0 * SUM(CASE WHEN cancellation_flag THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 4) AS cancellation_rate,
    ROUND(AVG(CASE WHEN NOT cancellation_flag THEN delivery_time_minutes END), 2) AS avg_delivery_min,
    ROUND(SUM(CASE WHEN NOT cancellation_flag THEN final_amount_paid_sar ELSE 0 END), 2) AS gmv_sar,
    ROUND(SUM(CASE WHEN NOT cancellation_flag THEN final_amount_paid_sar ELSE 0 END)
          / NULLIF(COUNT(DISTINCT customer_id), 0), 2) AS revenue_per_user_sar
FROM orders
GROUP BY ab_group
ORDER BY ab_group;
