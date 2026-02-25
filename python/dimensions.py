import pandas as pd

def create_dimensions(df):
    
    # DIM PRODUCT
    df_products = df[["Product"]].copy()
    df_products = df_products.explode("Product")

    dim_product = (
        df_products[["Product"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_product["Product_ID"] = dim_product.index
    dim_product = dim_product[["Product_ID", "Product"]]
    
    # DIM CUSTOMER
    dim_customer = (
        df[["Customer_Name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_customer["Customer_ID"] = dim_customer.index
    dim_customer = dim_customer[["Customer_ID", "Customer_Name"]]
    
    
    # DIM DATE
    dim_date = (
        df[["Date"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_date["Date_ID"] = dim_date.index
    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["Month"] = dim_date["Date"].dt.month
    dim_date["Day"] = dim_date["Date"].dt.day
    dim_date = dim_date[["Date_ID", "Date", "Year", "Month", "Day"]]

    # Dim_Store_Context
    dim_store_context = (
        df[["City", "Store_Type"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_store_context["Store_Context_ID"] = dim_store_context.index
    dim_store_context = dim_store_context[["Store_Context_ID", "City", "Store_Type"]]

   
    
    return dim_product, dim_customer, dim_date, dim_store_context
