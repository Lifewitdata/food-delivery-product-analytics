-- 00_load_s3.sql | Amazon Redshift dialect port
-- Redshift dialect port, not run live on AWS. Replaces PostgreSQL COPY ... FROM file with COPY ... FROM S3.
-- Replace <bucket> and <account-id>/<role> with your own; never paste access keys into this file.
COPY orders
FROM 's3://<bucket>/food-delivery/orders_clean_sa.csv'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
FORMAT AS CSV
IGNOREHEADER 1
DATEFORMAT 'YYYY-MM-DD'
TIMEFORMAT 'YYYY-MM-DD HH:MI:SS'
REGION 'me-central-1';

-- events.json is JSON lines; 'auto' maps top-level keys to columns, payload lands as JSON text.
COPY events
FROM 's3://<bucket>/food-delivery/events.json'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<redshift-s3-read-role>'
FORMAT AS JSON 'auto'
TIMEFORMAT 'auto'
REGION 'me-central-1';

SELECT COUNT(*) AS clean_rows FROM orders;   -- expect 15000
SELECT COUNT(*) AS events FROM events;       -- expect 60000
