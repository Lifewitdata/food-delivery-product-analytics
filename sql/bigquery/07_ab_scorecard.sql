-- 07_ab_scorecard.sql | BigQuery Standard SQL
-- Free-delivery threshold test: control SAR 75 vs treatment SAR 50, randomised by customer.
-- Runs on OBSERVED data. The simulated treatment effect lives only in the notebook (Step 7).
-- Primary: conversion = delivered / checkout sessions. Guardrails: cancellation, delivery time.
SELECT
  ab_group,
  MAX(ab_threshold_sar) AS threshold_sar,
  COUNT(DISTINCT customer_id) AS customers,
  COUNT(*) AS checkout_sessions,
  COUNTIF(NOT cancellation_flag) AS delivered_orders,
  ROUND(SAFE_DIVIDE(COUNTIF(NOT cancellation_flag), COUNT(*)), 4) AS conversion,
  ROUND(SAFE_DIVIDE(COUNTIF(cancellation_flag), COUNT(*)), 4) AS cancellation_rate,
  ROUND(AVG(IF(NOT cancellation_flag, delivery_time_minutes, NULL)), 2) AS avg_delivery_min,
  ROUND(SUM(IF(NOT cancellation_flag, final_amount_paid_sar, 0)), 2) AS gmv_sar,
  ROUND(SAFE_DIVIDE(SUM(IF(NOT cancellation_flag, final_amount_paid_sar, 0)), COUNT(DISTINCT customer_id)), 2) AS revenue_per_user_sar
FROM food_delivery.orders
GROUP BY ab_group
ORDER BY ab_group;
