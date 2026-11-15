-- Run after loading data/processed/product_sessions.csv as product_sessions.
-- Session grain: one row per session in the final aggregation.
WITH session_stages AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_name = 'app_open' THEN 1 ELSE 0 END) AS app_open,
        MAX(CASE WHEN event_name = 'restaurant_view' THEN 1 ELSE 0 END) AS restaurant_view,
        MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
        MAX(CASE WHEN event_name = 'checkout_started' THEN 1 ELSE 0 END) AS checkout_started,
        MAX(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS order_placed,
        MIN(data_provenance) AS data_provenance
    FROM product_sessions
    GROUP BY session_id
)
SELECT
    data_provenance,
    COUNT(*) AS sessions,
    SUM(app_open) AS app_open_sessions,
    SUM(restaurant_view) AS restaurant_view_sessions,
    SUM(add_to_cart) AS add_to_cart_sessions,
    SUM(checkout_started) AS checkout_sessions,
    SUM(order_placed) AS converted_sessions,
    SUM(restaurant_view)::DOUBLE / NULLIF(SUM(app_open), 0) AS app_to_restaurant_rate,
    SUM(add_to_cart)::DOUBLE / NULLIF(SUM(restaurant_view), 0) AS restaurant_to_cart_rate,
    SUM(checkout_started)::DOUBLE / NULLIF(SUM(add_to_cart), 0) AS cart_to_checkout_rate,
    SUM(order_placed)::DOUBLE / NULLIF(SUM(checkout_started), 0) AS checkout_to_order_rate,
    SUM(order_placed)::DOUBLE / NULLIF(COUNT(*), 0) AS session_conversion_rate
FROM session_stages
GROUP BY data_provenance
ORDER BY data_provenance;
