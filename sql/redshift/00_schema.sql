-- 00_schema.sql | Amazon Redshift dialect port
-- Redshift dialect port, not run live on AWS. Differences from sql/postgres/00_schema.sql:
--   DISTKEY(customer_id): co-locates a customer's orders, so retention / A-B joins on customer_id do not shuffle.
--   SORTKEY(order_date): zone maps prune blocks on monthly and date-range filters.
--   payload is VARCHAR (JSON text) read with JSON_EXTRACT_PATH_TEXT; no PRIMARY KEY enforcement in Redshift.
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    order_datetime TIMESTAMP,
    city VARCHAR(50),
    city_tier INT,
    customer_id VARCHAR(50),
    restaurant_id VARCHAR(50),
    restaurant_name VARCHAR(100),
    cuisine VARCHAR(50),
    delivery_partner_id VARCHAR(50),
    device VARCHAR(20),
    ab_group VARCHAR(20),
    ab_threshold_sar INT,
    order_hour INT,
    order_day_of_week INT,
    order_month INT,
    delivery_distance_km DOUBLE PRECISION,
    preparation_time_minutes INT,
    delivery_time_minutes INT,
    estimated_delivery_time INT,
    traffic_level_score DOUBLE PRECISION,
    weather_severity_score DOUBLE PRECISION,
    restaurant_rating DOUBLE PRECISION,
    delivery_partner_rating DOUBLE PRECISION,
    customer_rating DOUBLE PRECISION,
    order_value_sar DECIMAL(10,2),
    delivery_fee_sar DECIMAL(10,2),
    discount_amount_sar DECIMAL(10,2),
    tip_amount_sar DECIMAL(10,2),
    final_amount_paid_sar DECIMAL(10,2),
    number_of_items INT,
    cancellation_flag BOOLEAN,
    delayed_delivery_flag BOOLEAN,
    refund_flag BOOLEAN,
    promo_code_used BOOLEAN,
    premium_customer_flag BOOLEAN,
    festival_or_weekend_flag BOOLEAN,
    delivery_partner_experience_years INT,
    delivery_efficiency_score DOUBLE PRECISION,
    customer_age INT,
    customer_loyalty_score DOUBLE PRECISION
)
DISTKEY (customer_id)
SORTKEY (order_date);

CREATE TABLE IF NOT EXISTS events (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    event_type VARCHAR(20),
    event_time TIMESTAMP,
    device VARCHAR(20),
    city VARCHAR(50),
    payload VARCHAR(1024)
)
DISTKEY (customer_id)
SORTKEY (event_time);
