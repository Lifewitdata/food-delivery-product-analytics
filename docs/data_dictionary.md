# Data dictionary

Grain: one order_id per order row; one generated app event per JSON line. Source meanings are taken from field names and supplied notes, not a verified upstream specification. Operational definitions not supplied are marked assumed. The raw file is unchanged. The provided Saudi adaptation contains 41 columns, not 45 as claimed in the dataset pack's text.

## All 30 raw columns

| Raw field | Type / units | Meaning and caveat |
|---|---|---|
| order_id | string UUID | Unique order identifier |
| city_tier | integer 1-3 | Source location category, mapped literally to three Saudi cities; not real city geography |
| customer_age | integer years | Synthetic customer age recorded per order; IDs were added independently |
| customer_loyalty_score | float, roughly 0-100 | Assumed loyalty score, higher treated as more loyal; formula not supplied |
| order_hour | integer 0-23 | Source order hour; preserved |
| order_day_of_week | integer | Source weekday category (observed 1-6); encoding not supplied, so no weekday names assigned |
| order_month | integer 1-12 | Source month; preserved in seeded 2026 dates |
| delivery_distance_km | float km | Delivery distance; assumed order-to-destination travel distance |
| preparation_time_minutes | integer minutes | Restaurant prep duration |
| delivery_time_minutes | integer minutes | Actual source delivery duration; exists even on cancelled rows, so use delivered-only operational averages |
| estimated_delivery_time | integer minutes | Estimated duration, not timestamp; ETA breach = actual > estimated |
| traffic_level_score | float 0-10 | Assumed traffic severity, higher worse; formula not supplied |
| weather_severity_score | float 0-10 | Assumed weather severity, higher worse; formula not supplied |
| restaurant_rating | float stars | Recorded per-order restaurant rating, averaged for restaurant summaries; restaurant IDs added independently |
| delivery_partner_rating | float stars, nullable | Recorded delivery partner rating; 150 nulls, not all cancelled |
| customer_rating | float stars, nullable | Assumed customer feedback on order/service, not a rating of the customer; 150 nulls |
| order_value | float USD | Basket before fee, discount and tip; minimum 100, 59.74% at that floor |
| delivery_fee | float USD | Source delivery fee, not modified by the simulated threshold policy |
| discount_amount | float USD | Source discount; positive on every order, even without promo code |
| tip_amount | float USD, nullable | Tip; 150 missing values remain missing, never imputed to zero |
| final_amount_paid | float USD | Paid amount; equals basket + fee - discount + tip when tip known, to tolerance |
| number_of_items | integer | Basket item count |
| cancellation_flag | boolean | Order cancelled; only false rows counted as delivered |
| delayed_delivery_flag | boolean | Source late flag; a subset of ETA breaches, rule not supplied |
| refund_flag | boolean | Refund occurred; refund amount absent, so GMV not net of refunds |
| promo_code_used | boolean | Promo redemption; distinguish from positive discount_amount |
| premium_customer_flag | boolean | Source order premium status; may vary per seeded customer |
| festival_or_weekend_flag | boolean | Source combined festival/weekend flag, not computed from Saudi calendar |
| delivery_partner_experience_years | integer years | Source rider experience per order; rider IDs were generated independently |
| delivery_efficiency_score | float roughly 0-100 | Higher treated as more efficient; formula not supplied, not an independently validated performance measure |

## Saudi adaptation: replacements and additions

All 25 non-money raw columns above pass through unchanged. Five USD fields are replaced by `order_value_sar`, `delivery_fee_sar`, `discount_amount_sar`, `tip_amount_sar`, `final_amount_paid_sar`: multiply by 3.75, round to 2 decimals, preserve nulls.

| Added field | Type | Meaning / provenance |
|---|---|---|
| order_date | date | Seeded date in 2026, source month preserved; source weekday not preserved |
| order_datetime | timestamp | Seeded date plus source hour; no timezone supplied |
| city | string | Tier 1 Riyadh, tier 2 Jeddah, tier 3 Dammam |
| customer_id | string | Seeded CUST ID; 7,309 distinct, repeat orders; no real person |
| restaurant_id | string | Seeded REST ID; 350 distinct, each receives orders across all cities |
| restaurant_name | string | Synthetic city/cuisine name, not necessarily aligned to order city |
| cuisine | string | One of 10 seeded cuisines |
| delivery_partner_id | string | Seeded RIDER ID; 800 distinct, attributes not a real consistent rider profile |
| device | string | Seeded Android, iOS or Web |
| ab_group | string | Seeded control/treatment assignment, fixed per customer |
| ab_threshold_sar | integer SAR | 75 control, 50 treatment; label only, not applied to source fees |

## Events and other supplied tables

`events.json`: 60,000 lines, exactly 4 per order. Outer keys: order_id, customer_id, event_type, event_time, device, city, payload. Event types browse, add_to_cart, checkout, delivered/cancelled. Payload keys are event-specific: items_viewed, items, promo_code_used, ab_threshold_sar, delivery_time_minutes. No sessions without an order; 100% browse/cart/checkout completion is generated, not observed.

Supplied customers.csv: customer_id, city, first_order_date, last_order_date, orders, total_spent_sar, avg_loyalty, premium. Supplied restaurants.csv: restaurant_id, restaurant_name, city, cuisine, orders, gmv_sar, avg_rating. These are retained as supplementary inputs; metrics in the notebook are recomputed from orders, not trusted from these summaries. Their aggregation definitions were not supplied.

`validation_reference.json` is the pack's reference, not a new verification claim. `saudi_mapping.csv` and `quarantine_log.csv` are written by the notebook. Quarantine grain: one failing order/rule/bad_value; empty because all current hard checks pass. Missing-tip payment identities are not evaluated: the input required to evaluate them is absent.

## Reporting denominators

GMV/AOV, on-time rate and average delivery minutes use delivered orders only. Cancellation uses all orders. Cohorts and repeat rate use all placed orders (including cancelled); month-3 weights only cohorts with sufficient follow-up. GMV uses final paid amount, not basket value; it is not net revenue, not profit and not net of refunds.
