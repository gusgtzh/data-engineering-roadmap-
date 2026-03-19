import sqlite3

def load_to_sqlite(
    dim_product,
    dim_customer,
    dim_date,
    dim_store_context,
    fact_transactions,
    bridge
):

    conn = sqlite3.connect("retail_dw.db")
    cursor = conn.cursor()

    # Activar FK enforcement
    cursor.execute("PRAGMA foreign_keys = ON")

    # Eliminar tablas si existen
    cursor.executescript("""

    DROP TABLE IF EXISTS bridge_transaction_product;
    DROP TABLE IF EXISTS fact_transactions;
    DROP TABLE IF EXISTS dim_product;
    DROP TABLE IF EXISTS dim_customer;
    DROP TABLE IF EXISTS dim_date;
    DROP TABLE IF EXISTS dim_store_context;

    """)

    # Crear dimensiones
    cursor.executescript("""

    CREATE TABLE dim_product (
        Product_ID INTEGER PRIMARY KEY,
        Product TEXT NOT NULL
    );

    CREATE TABLE dim_customer (
        Customer_ID INTEGER PRIMARY KEY,
        Customer_Name TEXT NOT NULL
    );

    CREATE TABLE dim_date (
        Date_ID INTEGER PRIMARY KEY,
        Date TEXT NOT NULL,
        Year INTEGER,
        Month INTEGER,
        Day INTEGER
    );

    CREATE TABLE dim_store_context (
        Store_Context_ID INTEGER PRIMARY KEY,
        City TEXT,
        Store_Type TEXT
    );

    CREATE TABLE fact_transactions (
        Transaction_SK INTEGER PRIMARY KEY,
        Transaction_ID INTEGER,
        Customer_ID INTEGER,
        Date_ID INTEGER,
        Store_Context_ID INTEGER,
        Total_Items INTEGER,
        Total_Cost REAL,
        Discount_Applied INTEGER,
        Promotion TEXT,

        FOREIGN KEY (Customer_ID)
            REFERENCES dim_customer(Customer_ID),

        FOREIGN KEY (Date_ID)
            REFERENCES dim_date(Date_ID),

        FOREIGN KEY (Store_Context_ID)
            REFERENCES dim_store_context(Store_Context_ID)
    );

    CREATE TABLE bridge_transaction_product (
        Transaction_SK INTEGER,
        Product_ID INTEGER,

        PRIMARY KEY (Transaction_SK, Product_ID),

        FOREIGN KEY (Transaction_SK)
            REFERENCES fact_transactions(Transaction_SK),

        FOREIGN KEY (Product_ID)
            REFERENCES dim_product(Product_ID)
    );

    """)

    # Insertar datos
    dim_product.to_sql("dim_product", conn, if_exists="append", index=False)
    dim_customer.to_sql("dim_customer", conn, if_exists="append", index=False)
    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
    dim_store_context.to_sql("dim_store_context", conn, if_exists="append", index=False)
    fact_transactions.to_sql("fact_transactions", conn, if_exists="append", index=False)
    bridge.to_sql("bridge_transaction_product", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print("DW cargado con constraints en retail_dw.db")