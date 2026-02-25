from extract import extract_data
from transform import transform_data
from dimensions import create_dimensions
from facts import create_fact_and_bridge
from load import load_to_sqlite



def main():

    path = "data/raw/Retail_Transactions_Dataset.csv"

    # 1. Extract
    df = extract_data(path)

    # 2. Transform
    df_clean = transform_data(df)

    # 3. Build Dimensions
    dim_product, dim_customer, dim_date,  dim_store_context = create_dimensions(df_clean)

    # 4. Build Fact Table
    fact_transactions, bridge = create_fact_and_bridge(
        df_clean,
        dim_product,
        dim_customer,
        dim_date,
        dim_store_context
    )   

    # 5. Load to SQLite
    load_to_sqlite(
        dim_product,
        dim_customer,
        dim_date,
        dim_store_context,
        fact_transactions,
        bridge
)

    print("Pipeline ejecutado correctamente")
    print("Dim Product:", dim_product.shape)
    print("Dim Customer:", dim_customer.shape)
    print("Dim Date:", dim_date.shape)
    print("Dim Store Context:", dim_store_context.shape)
    print("Fact Sales:", fact_transactions.shape)


if __name__ == "__main__":
    main()



