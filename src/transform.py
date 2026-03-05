import pandas as pd
import ast

def transform_data(df):
    # Convertir columna Product de string a lista
    df["Product"] = df["Product"].apply(ast.literal_eval)

    # Convertir Date a datetime
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date"] = df["Date"].dt.floor("D")

    # Convertir columnas categóricas
    categorical_cols = [
        "City",
        "Store_Type",
        "Payment_Method",
        "Customer_Category",
        "Season",
        "Promotion"
    ]

    for col in categorical_cols:
        df[col] = df[col].astype("category")

    return df
