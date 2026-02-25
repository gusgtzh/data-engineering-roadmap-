import sqlite3

def load_to_sqlite(
    dim_product,
    dim_customer,
    dim_date,
    dim_store_context,
    fact_transactions,
    bridge
):
    # Crear conexión (archivo se crea si no existe)
    conn = sqlite3.connect("retail_dw.db")

    # Escribir tablas
    dim_product.to_sql("dim_product", conn, if_exists="replace", index=False)
    dim_customer.to_sql("dim_customer", conn, if_exists="replace", index=False)
    dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
    dim_store_context.to_sql("dim_store_context", conn, if_exists="replace", index=False)
    fact_transactions.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    bridge.to_sql("bridge_transaction_product", conn, if_exists="replace", index=False)

    conn.close()

    print("Data Warehouse cargado en retail_dw.db")