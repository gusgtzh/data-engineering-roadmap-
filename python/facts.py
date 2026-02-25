def create_fact_and_bridge(df, dim_product, dim_customer, dim_date, dim_store_context):

    # =========================
    # FACT_TRANSACTIONS
    # =========================

    # Iniciar desde df original
    fact_transactions = df.copy()

    # Merge con dim_customer
    fact_transactions = fact_transactions.merge(
        dim_customer, on="Customer_Name", how="left"
    )

    # Merge con dim_date
    fact_transactions = fact_transactions.merge(
        dim_date, on="Date", how="left"
    )

    # Merge con dim_store_context
    fact_transactions = fact_transactions.merge(
        dim_store_context, on=["City", "Store_Type"], how="left"
    )

    # Selección final de columnas (nivel transacción)
    fact_transactions = fact_transactions[
        [
            "Transaction_ID",
            "Customer_ID",
            "Date_ID",
            "Store_Context_ID",
            "Total_Items",
            "Total_Cost",
            "Discount_Applied",
            "Promotion"
        ]
    ]

    fact_transactions = fact_transactions.drop_duplicates().reset_index(drop=True)
    fact_transactions["Transaction_SK"] = fact_transactions.index


    # =========================
    # BRIDGE_TRANSACTION_PRODUCT
    # =========================

    df_products = df[["Transaction_ID", "Product"]].copy()

    # Explode para relación many-to-many
    df_products = df_products.explode("Product")

    df_products = df_products.merge(
        dim_product,
        on="Product",
        how="left"
    )

    # Merge para traer Transaction_SK
    bridge = df_products.merge(
        fact_transactions[["Transaction_ID", "Transaction_SK"]],
        on="Transaction_ID",
        how="left"
    )

    bridge = bridge[
        [
            "Transaction_SK",
            "Product_ID"
        ]
    ]

    bridge = bridge.drop_duplicates().reset_index(drop=True)

    return fact_transactions, bridge