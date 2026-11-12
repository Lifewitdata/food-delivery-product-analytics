-- 03_funnel.sql | Amazon Redshift dialect port
-- Redshift dialect port, validated in PostgreSQL 16, not run live on AWS.
-- SELECT body is identical to sql/postgres/03_funnel.sql (no FILTER clause, no JSONB operators, so it is Redshift-safe).
-- App-event funnel from the semi-structured events table (payload is JSON).
-- One checkout session = one order_id.
WITH stages AS (
    SELECT
        city,
        device,
        order_id,
        MAX(CASE WHEN event_type = 'browse' THEN 1 ELSE 0 END) AS browsed,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS carted,
        MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) AS checked_out,
        MAX(CASE WHEN event_type = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        MAX(CASE WHEN event_type = 'checkout'
                  AND json_extract_path_text(payload, 'promo_code_used') = 'true' THEN 1 ELSE 0 END) AS promo_at_checkout
    FROM events
    GROUP BY city, device, order_id
)
SELECT
    city,
    device,
    SUM(browsed) AS browse_sessions,
    SUM(carted) AS cart_sessions,
    SUM(checked_out) AS checkout_sessions,
    SUM(delivered) AS delivered_sessions,
    ROUND(1.0 * SUM(carted) / NULLIF(SUM(browsed), 0), 4) AS browse_to_cart,
    ROUND(1.0 * SUM(checked_out) / NULLIF(SUM(carted), 0), 4) AS cart_to_checkout,
    ROUND(1.0 * SUM(delivered) / NULLIF(SUM(checked_out), 0), 4) AS checkout_to_delivered,
    ROUND(1.0 * SUM(promo_at_checkout) / NULLIF(SUM(checked_out), 0), 4) AS promo_share_at_checkout
FROM stages
GROUP BY city, device
ORDER BY city, device;
