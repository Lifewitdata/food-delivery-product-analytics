-- 06_retention.sql | Amazon Redshift dialect port
-- Redshift dialect port, validated in PostgreSQL 16, not run live on AWS.
-- SELECT body is identical to sql/postgres/06_retention.sql (no FILTER clause, no JSONB operators, so it is Redshift-safe).
-- Monthly cohort retention. Cohort = month of a customer's first order (all orders placed).
-- retention = cohort customers ordering in that month offset / cohort size.
WITH firsts AS (
    SELECT customer_id, MIN(order_month) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT o.customer_id, f.cohort_month, o.order_month - f.cohort_month AS months_since_first
    FROM orders AS o
    JOIN firsts AS f USING (customer_id)
),
sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size FROM firsts GROUP BY cohort_month
)
SELECT
    a.cohort_month,
    a.months_since_first,
    s.cohort_size,
    COUNT(*) AS active_customers,
    ROUND(1.0 * COUNT(*) / NULLIF(s.cohort_size, 0), 4) AS retention
FROM activity AS a
JOIN sizes AS s USING (cohort_month)
GROUP BY a.cohort_month, a.months_since_first, s.cohort_size
ORDER BY a.cohort_month, a.months_since_first;
