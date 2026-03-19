# data-engineering-roadmap-
End-to-end Data Engineering project focused on dimensional modeling, SQL validation, and analytical integrity

## Dataset

This project uses the **Retail Transactions Dataset** from Kaggle.

- Source: https://www.kaggle.com/datasets/ (search: Retail Transactions Dataset)
- File: Retail_Transactions_Dataset.csv
- Size: >25MB (not stored in this repository)

### How to obtain the data

1. Go to Kaggle
2. Download `Retail_Transactions_Dataset.csv`
3. Place the file in:

   data/raw/Retail_Transactions_Dataset.csv

## 1. Project Overview

This project focuses on designing a clean and consistent dimensional data model from a retail transactional dataset.

- The goal was not only to process the dataset, but to:
- Analyze its structure
- Define the correct grain of the fact table
- Prevent metric inconsistencies
- Design a scalable dimensional model

The result is a modular ETL pipeline that builds:
- Dimension tables
- A transaction-level fact table
- A bridge table to handle many-to-many relationships

## 2. Initial Dataset Observations

The dataset contains:

1,000,000 transactions
- A list of products per transaction
- Aggregated metrics at transaction level:
   - Total_Cost
   - Total_Items
- Multiple descriptive attributes (City, Store_Type, Payment_Method, etc.)

Key observations:

- The Product column contains multiple products stored as stringified lists.
- Metrics are aggregated at transaction level, not product level.
- Dates included time components that created unnecessary cardinality.
- Some attributes required categorization for memory optimization.

## 3️. Grain Definition (Critical Decision)

The most important architectural decision was defining the grain of the fact table.

Initially, the data was exploded to transaction-product level.
However, this introduced a critical issue:

Metrics (Total_Cost, Total_Items) were defined at transaction level.

Lowering the grain caused metric inflation and analytical inconsistencies.

Final decision:

The fact table grain is defined at transaction level.
One row represents one business transaction event.

## 4️. Dimensional Model
### Dimensions

- Dim_Product
- Dim_Customer
- Dim_Date
- Dim_Store_Context

Each dimension includes surrogate keys for warehouse consistency.

Low-cardinality attributes were converted to categorical types to optimize memory usage.

Dates were normalized to day-level granularity to avoid artificial cardinality growth.

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

## 5. Fact Table
### Fact_Transactions

Grain:
One row per transaction.

Includes:
- Transaction_SK (surrogate key)
- Business Transaction_ID
- Foreign keys to dimensions
- Transaction-level metrics

This ensures metric integrity and prevents aggregation errors.

## 6️. Bridge Table
### Bridge_Transaction_Product

Because one transaction may include multiple products, a many-to-many relationship exists.

Instead of lowering the fact grain, a bridge table was implemented:
- Transaction_SK
- Product_ID

This preserves product-level analysis capability without inflating financial metrics.

## 7️. Architectural Decisions

- Key engineering decisions:
- Preserve metric-grain consistency.
- Avoid duplicate metric inflation.
- Normalize non-atomic product lists.
- Optimize categorical fields.
- Separate ETL stages into modular scripts:
   - extract.py
   - transform.py
   - dimensions.py
   - facts.py
   - main.py

## 8️. Limitations

- No unit-level pricing or quantity per product.
- Cannot compute product-level revenue.
- Customer demographic category removed due to inconsistency.

## 9️. Future Improvements

- Add product-level metrics if available.
- Load data into a relational database (PostgreSQL).
- Add incremental loading logic.
- Implement indexing strategies.
- Add data validation layer.

## 10. Lessons Learned

This project reinforced that Data Engineering is fundamentally about architecture and analytical integrity, not just coding.

Key takeaways:
- The grain of a fact table determines the validity of all metrics.
- Exploding data without aligning metrics to the correct grain can silently inflate results.
- Not all modeling decisions are technical — many are semantic.
- A clean dimensional design prevents incorrect analytical conclusions.
- Performance issues often reveal structural design problems (e.g., drop_duplicates on non-atomic fields).
- Many engineering decisions are about preventing future misuse of the data.

Most importantly, this project shifted the focus from:

"How do I process this dataset?"

to:

"How do I design a model that guarantees correct analysis?"

## Data Warehouse Output

The final dimensional model is persisted in a SQLite database (retail_dw.db), allowing direct SQL querying of:
- dim_product
- dim_customer
- dim_date
- dim_store_context
- fact_transactions
- bridge_transaction_product

This transforms the project from a pandas-only pipeline into a functional mini Data Warehouse.

## 11. SQL Analysis & Data Validation

This project was extended beyond data modeling into analytical validation and SQL-based debugging to ensure the integrity of the Data Warehouse.

## Key Areas Covered
Metric Validation

Validated consistency between fact tables and joins:

SELECT SUM(Total_Cost) FROM fact_transactions;

SELECT SUM(ft.Total_Cost)
FROM fact_transactions ft
JOIN bridge_transaction_product btp
ON ft.Transaction_SK = btp.Transaction_SK;

This revealed metric inflation when joining tables with different grains.

## Data Quality Checks

Implemented validation queries to ensure structural integrity:
- Duplicate detection in fact tables
- Orphan records between fact and bridge
- Grain consistency validation
Example:

SELECT Transaction_SK, COUNT(*)
FROM fact_transactions
GROUP BY Transaction_SK
HAVING COUNT(*) > 1;

## Business Metrics (SQL)

Computed analytical metrics directly from the Data Warehouse:

-- % of transactions with ≥3 products per day
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

## Key Learnings from SQL Layer

- Joins across different grains can silently inflate metrics
- Analytical correctness depends on aligning metric grain with query grain
- Many real-world errors are semantic, not syntactic
- Data validation queries are critical in production pipelines
