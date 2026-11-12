-- 00_load.sql | PostgreSQL 16, manual route (pgAdmin Query Tool or psql)
-- scripts/run_sql.py does the same load automatically with COPY FROM STDIN.
-- Server-side COPY reads the file as the postgres service account; use forward slashes on Windows.
-- events.json is JSON lines, so load it through scripts/run_sql.py (it flattens the outer fields
-- and keeps payload as JSON) or pgAdmin Import after converting to CSV.
COPY orders FROM 'C:/path/to/food-delivery-product-analytics/data/processed/orders_clean_sa.csv'
WITH (FORMAT csv, HEADER true);

SELECT COUNT(*) AS clean_rows FROM orders;   -- expect 15000 (raw 15000 = clean 15000 + quarantined 0)
SELECT COUNT(*) AS events FROM events;       -- expect 60000
