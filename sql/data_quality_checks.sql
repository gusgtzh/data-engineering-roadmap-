-- =========================================
-- DATA QUALITY CHECKS
-- =========================================

-- 1. Duplicate transactions (should be zero)
SELECT Transaction_SK, COUNT(*)
FROM fact_transactions
GROUP BY Transaction_SK
HAVING COUNT(*) > 1;

-- 2. Orphan records (fact → bridge)
SELECT ft.Transaction_SK
FROM fact_transactions ft
LEFT JOIN bridge_transaction_product btp
ON ft.Transaction_SK = btp.Transaction_SK
WHERE btp.Transaction_SK IS NULL;

-- 3. Orphan records (bridge → fact)
SELECT btp.Transaction_SK
FROM bridge_transaction_product btp
LEFT JOIN fact_transactions ft
ON btp.Transaction_SK = ft.Transaction_SK
WHERE ft.Transaction_SK IS NULL;