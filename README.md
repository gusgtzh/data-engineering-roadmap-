# Retail Data Warehouse (SQLite) | Dimensional Modeling, SQL Validation & Data Integrity

## Overview

This project builds a retail Data Warehouse from raw transactional data using a modular ETL pipeline in Python and SQLite.

The focus is on **analytical correctness**, ensuring that all metrics remain consistent through proper grain definition, dimensional modeling, and SQL-based validation.

---

## Architecture

Pipeline structure:

* Extract → Load raw CSV data
* Transform → Clean and standardize data
* Dimensions → Build dimension tables
* Facts → Construct fact and bridge tables
* Load → Persist into SQLite

---

## Data Model

### Fact Table

* **fact_transactions**
* Grain: **1 row = 1 transaction**
* Metrics:

  * Total_Cost
  * Total_Items

### Dimensions

* dim_customer
* dim_product
* dim_date
* dim_store_context

### Bridge Table

* **bridge_transaction_product**
* Grain: **transaction-product**
* Handles many-to-many relationship between transactions and products

---

## Dimensional Model Diagram

                         +------------------+
                         |   Dim_Product    |
                         |------------------|
                         | Product_ID (PK)  |
                         | Product          |
                         +--------+---------+
                                  ^
                                  |
                                  |
                    +-------------+--------------+
                    | Bridge_Transaction_Product |
                    |----------------------------|
                    | Transaction_SK (FK)        |
                    | Product_ID (FK)            |
                    +-------------+--------------+
                                  |
                                  v
      +-------------------+    +-----------------------+    +-------------------+
      |   Dim_Customer    |    |   Fact_Transactions   |    |     Dim_Date      |
      |-------------------|    |-----------------------|    |-------------------|
      | Customer_ID (PK)  |<---| Transaction_SK (PK)   |--->| Date_ID (PK)      |
      | Customer_Name     |    | Transaction_ID (BK)    |   | Date              |
      +-------------------+    | Customer_ID (FK)       |   | Year              |
                                | Date_ID (FK)           |   | Month             |
      +-------------------+    | Store_Context_ID (FK)  |   | Day               |
      | Dim_Store_Context |    | Total_Items            |   +-------------------+
      |-------------------|    | Total_Cost             |
      | Store_Context_ID  |<---| Discount_Applied       |
      | City              |    | Promotion              |
      | Store_Type        |    +------------------------+
      +-------------------+

---

## Key Design Decisions

* Fact table contains only **metrics + foreign keys**
* Grain defined at transaction level to prevent metric inflation
* Bridge table used instead of lowering fact grain
* Non-atomic product lists normalized during transformation

---

## Data Limitations

* No product-level quantity
* No product-level revenue
* Cannot compute accurate sales per product

👉 Any attempt to calculate revenue at product level would produce incorrect results due to grain mismatch.

---

## SQL Analysis & Data Validation

### Metric Validation

```sql
SELECT SUM(Total_Cost) FROM fact_transactions;

SELECT SUM(ft.Total_Cost)
FROM fact_transactions ft
JOIN bridge_transaction_product btp
ON ft.Transaction_SK = btp.Transaction_SK;
```

→ Demonstrates metric inflation when joining across different grains

---

### Data Quality Checks

```sql
SELECT Transaction_SK, COUNT(*)
FROM fact_transactions
GROUP BY Transaction_SK
HAVING COUNT(*) > 1;
```

* Duplicate detection
* Orphan detection
* Grain validation

---

### Business Metric Example

```sql
SELECT 
    dd.Date,
    SUM(CASE WHEN t3.Transaction_SK IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
    / COUNT(*) AS pct_trans_3plus
FROM fact_transactions ft
JOIN dim_date dd ON ft.Date_ID = dd.Date_ID
LEFT JOIN (
    SELECT Transaction_SK
    FROM fact_transactions ft 
    JOIN bridge_transaction_product btp
        ON ft.Transaction_SK = btp.Transaction_SK
    GROUP BY ft.Transaction_SK
    HAVING COUNT(*) >= 3
) t3 ON ft.Transaction_SK = t3.Transaction_SK
GROUP BY dd.Date;
```

---

## Key Learnings

* Grain definition determines analytical correctness
* Joins across different grains can silently inflate metrics
* Many data issues are conceptual, not syntactic
* SQL validation is critical in production data systems

---

## How to Run

```bash
python src/main.py
```

---

## Notes

The SQLite database is not included due to size limitations.
Run the pipeline to generate it locally.

---

## Tech Stack

* Python
* Pandas
* SQLite
* SQL
