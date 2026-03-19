-- =========================================
-- DEBUGGING & VALIDATION
-- =========================================

-- Metric consistency check
SELECT SUM(Total_Cost) AS total_fact
FROM fact_transactions;

SELECT SUM(ft.Total_Cost) AS total_after_join
FROM fact_transactions ft
JOIN bridge_transaction_product btp
ON ft.Transaction_SK = btp.Transaction_SK;

-- Expectation:
-- total_after_join > total_fact → metric inflation due to join