-- 03_funnel.sql | BigQuery Standard SQL
-- App-event funnel from the semi-structured events table (payload is JSON).
-- One checkout session = one order_id.
WITH stages AS (
  SELECT
    city,
    device,
    order_id,
    MAX(IF(event_type = 'browse', 1, 0)) AS browsed,
    MAX(IF(event_type = 'add_to_cart', 1, 0)) AS carted,
    MAX(IF(event_type = 'checkout', 1, 0)) AS checked_out,
    MAX(IF(event_type = 'delivered', 1, 0)) AS delivered,
    MAX(IF(event_type = 'checkout' AND JSON_VALUE(payload, '$.promo_code_used') = 'true', 1, 0)) AS promo_at_checkout
  FROM food_delivery.events
  GROUP BY city, device, order_id
)
SELECT
  city,
  device,
  SUM(browsed) AS browse_sessions,
  SUM(carted) AS cart_sessions,
  SUM(checked_out) AS checkout_sessions,
  SUM(delivered) AS delivered_sessions,
  ROUND(SAFE_DIVIDE(SUM(carted), SUM(browsed)), 4) AS browse_to_cart,
  ROUND(SAFE_DIVIDE(SUM(checked_out), SUM(carted)), 4) AS cart_to_checkout,
  ROUND(SAFE_DIVIDE(SUM(delivered), SUM(checked_out)), 4) AS checkout_to_delivered,
  ROUND(SAFE_DIVIDE(SUM(promo_at_checkout), SUM(checked_out)), 4) AS promo_share_at_checkout
FROM stages
GROUP BY city, device
ORDER BY city, device;
