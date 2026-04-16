-- ============================================================
-- FINANCIAL REPORTING FAILURE DETECTION SYSTEM
-- SQL Reconciliation Engine
-- Author: Yash Sonawane
-- ============================================================

-- CHECK 1: Missing records (source → transformed)
-- Transactions in source that never made it through ETL
SELECT
    s.transaction_id,
    s.account_id,
    s.amount,
    s.category,
    s.transaction_date,
    'MISSING_IN_TRANSFORM' AS failure_type,
    'CRITICAL' AS severity
FROM source_transactions s
LEFT JOIN transformed_transactions t
    ON s.transaction_id = t.transaction_id
WHERE t.transaction_id IS NULL;

-- CHECK 2: Duplicate records in transformed layer
SELECT
    transaction_id,
    COUNT(*) AS duplicate_count,
    'DUPLICATE_RECORD' AS failure_type,
    'HIGH' AS severity
FROM transformed_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- CHECK 3: Amount mismatches between source and transformed
SELECT
    s.transaction_id,
    s.amount AS source_amount,
    t.amount AS transformed_amount,
    ROUND(ABS(s.amount - t.amount), 2) AS variance,
    ROUND((ABS(s.amount - t.amount) / s.amount) * 100, 2) AS variance_pct,
    'AMOUNT_MISMATCH' AS failure_type,
    CASE
        WHEN ABS(s.amount - t.amount) / s.amount > 0.10 THEN 'CRITICAL'
        WHEN ABS(s.amount - t.amount) / s.amount > 0.05 THEN 'HIGH'
        ELSE 'MEDIUM'
    END AS severity
FROM source_transactions s
JOIN transformed_transactions t
    ON s.transaction_id = t.transaction_id
WHERE ROUND(ABS(s.amount - t.amount), 2) > 0.01;

-- CHECK 4: Category mapping failures
SELECT
    transaction_id,
    category,
    'INVALID_CATEGORY_MAPPING' AS failure_type,
    'HIGH' AS severity
FROM transformed_transactions
WHERE category = 'UNKNOWN'
   OR category NOT IN ('Revenue','COGS','OpEx','Tax','AR');

-- CHECK 5: Reporting layer balance variance
-- Aggregated totals don't match transformed layer totals
SELECT
    t.account_id,
    t.category,
    t.transaction_date,
    SUM(t.amount) AS expected_total,
    r.total_amount AS reported_total,
    ROUND(ABS(SUM(t.amount) - r.total_amount), 2) AS balance_variance,
    'REPORTING_BALANCE_VARIANCE' AS failure_type,
    'CRITICAL' AS severity
FROM transformed_transactions t
JOIN reporting_layer r
    ON t.account_id = r.account_id
    AND t.category = r.category
    AND t.transaction_date = r.transaction_date
GROUP BY t.account_id, t.category, t.transaction_date, r.total_amount
HAVING ROUND(ABS(SUM(t.amount) - r.total_amount), 2) > 1.00;
