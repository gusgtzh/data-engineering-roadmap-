-- =========================================
-- BUSINESS METRICS
-- =========================================

-- Metric: % of transactions with ≥3 products per day
-- Grain: day
-- Numerator: transactions with ≥3 products
-- Denominator: total transactions
-- Pattern: LEFT JOIN + conditional aggregation

SELECT 
    dd.Date,
    SUM(CASE WHEN t3.Transaction_SK IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
    / COUNT(*) AS pct_trans_3plus
FROM fact_transactions ft
JOIN dim_date dd
    ON ft.Date_ID = dd.Date_ID
LEFT JOIN (
    SELECT 
        ft.Transaction_SK
    FROM fact_transactions ft 
    JOIN bridge_transaction_product btp
        ON ft.Transaction_SK = btp.Transaction_SK
    GROUP BY ft.Transaction_SK
    HAVING COUNT(*) >= 3
) t3
    ON ft.Transaction_SK = t3.Transaction_SK
GROUP BY dd.Date
ORDER BY dd.Date;