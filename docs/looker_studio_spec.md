# Looker Studio dashboard specification

**Spec only, not a live dashboard.** No Google account or cloud warehouse is required to run this project.

## Data source

Import data/processed/orders_clean_sa.csv into a Google Sheet or an optional BigQuery table. Grain: one order_id. Date field: order_date; source weekday: order_day_of_week (do not derive weekday from seeded dates). Currency: SAR. The 15,000 rows fit a Google Sheet, but BigQuery would be preferable for production data.

Calculated fields: delivered = 1 if cancellation_flag is false; delivered_gmv = final_amount_paid_sar if delivered else 0; on_time_delivered = 1 if delivered and delayed_delivery_flag false. GMV = SUM(delivered_gmv); AOV = SUM(delivered_gmv)/SUM(delivered); cancellation rate = SUM(cancelled)/COUNT(order_id); on-time rate = SUM(on_time_delivered)/SUM(delivered); avg delivery time = SUM(delivered_delivery_minutes)/SUM(delivered). Never average pre-aggregated rates.

## Pages

1. Executive: six scorecards (orders, GMV, AOV, cancellation, on-time rate, delivery time); city orders bar; premium/regular GMV bar. Filters: city, order_date, premium_customer_flag.
2. Growth: monthly GMV line and orders bar (order_month); cuisine GMV bar; promo-code AOV table; premium AOV table. Same page filters.
3. Delivery: delivery-distance bands vs average minutes bar; hour vs minutes line; experience years vs efficiency line; ETA-breach and source-late-rate scorecards. Delivered orders only; same filters.

Label every page synthetic, Saudi adaptation, USD x 3.75. Footnote: AOV is inflated by the USD 100 source floor; late flag is not equivalent to ETA breach. All filters must affect every chart and scorecard. Cross-check unfiltered metrics against reports/headline_metrics.json and Riyadh orders = 3,723 before sharing.
