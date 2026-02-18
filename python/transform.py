import pandas as pd  

file_path = "data/raw/Retail_Transactions_Dataset.csv" #Variable con la ruta del archivo

df = pd.read_csv(file_path)   #crear el data frame(df) con pandas



## Esto es análisis de fuente antes de modelar.
# print(df.head())

# print("\nInformación del dataset:")
# print(df.info())

# print("\nCantidad de filas y columnas:")
# print(df.shape)

# print("\nValores nulos por columna:")
# print(df.isnull().sum())

# print("\nTipos de datos:")
# print(df.dtypes)

# print("\nValores únicos en columnas categóricas:")
# print("Payment_Method:", df["Payment_Method"].unique())
# print("City:", df["City"].unique())
# print("Store_Type:", df["Store_Type"].unique())



#Aqui empieza la optimizacion 
df["City"] = df["City"].astype("category")
df["Store_Type"] = df["Store_Type"].astype("category")
df["Payment_Method"] = df["Payment_Method"].astype("category")
# print("\nMemory usage by column:")
# print(df.memory_usage(deep=True))


#Analisis de cardinalidad:

# print("\nCardinalidad:")
# print("City:", df["City"].nunique())
# print("Customer_Name:", df["Customer_Name"].nunique())
# print("Product:", df["Product"].nunique())


#Verificar columna Products por datos extraños
# print(df["Product"].value_counts().head(10))

# ## PRUEBA DE TIPO Y VALOR DE LA COLUMNA PRODUCT
# print(df["Product"].iloc[0])
# print(type(df["Product"].iloc[0]))

# #PRUEBA PARA VER VALORES CRUDOS
# print(df["Product"].head(20).tolist())


#SE DETECTAN VALORES ANIDADOS EN LISTAS EN LA COLUMNA PRODUCTOS, 
# SIN EMBARGO PYTHON LEE CADA LISTA COMPLETA COMO UN STRING, ESTO 
# GENERA UNA CARDINALIDAD FALSA Y LIMITA EL ANALISIS

#PRIMER PASO CONVERTIR STRINGS A LISTAS
import ast

df["Product"] = df["Product"].apply(ast.literal_eval)

# #SEGUNDO PASO -- desglosar (explode)

df_exploded = df.explode("Product")

# print("Filas antes:", len(df))
# print("Filas después de explode:", len(df_exploded))

# print(df_exploded["Product"].nunique())
# #SE IMPRIME: Filas antes: 1000000
# #Filas después de explode: 3000343 EN PROMEDIO CADA TRANSACCION TIENE 3 PRODUCTOS

# #AL VER QUE PRODUCTS SOLO TIENE 81 VARIACIONES SE PUEDE CONSIDERAR 
# # CONVERTIRLO EN CATEGORIA

df_exploded["Product"] = df_exploded["Product"].astype("category")

# #PARA COMPARAR QUE TANTO SE REDUCE
# print("memoria Product object", df_exploded.memory_usage(deep=True).sum() / 1024**2)
# print("memoria Product category", df.memory_usage(deep=True).sum() / 1024**2)


##-------------------------------
#El siguiente paso será ordenar los tipos de datos
#PRIMERO PASAR LA COLUMNA "DATE" A FORMATO DATETIME, PARA PODER AGRUPAR Y FILTRAR

df_exploded["Date"] = pd.to_datetime(df_exploded["Date"])
# print(df_exploded["Date"].dtype)

#Pasar city a Category ya que solo tiene 10 variantes
df_exploded["City"] = df_exploded["City"].astype("category")
# print(df_exploded["City"].dtype)

#print(df_exploded.info(memory_usage="deep"))

#Analizar la cardinalidad de las columnas restantes
#for col in ["Payment_Method","Store_Type","Customer_Category","Season","Promotion"]:
#   print(col, df_exploded[col].nunique())

#Convertir las columnas a category
for col in ["Payment_Method","Store_Type","Customer_Category","Season","Promotion"]:
    df_exploded[col] = df_exploded[col].astype("category")


# for col in ["Payment_Method","Store_Type","Customer_Category","Season","Promotion"]:
#     print(col, df_exploded[col].dtype)

#print(df_exploded.info(memory_usage="deep"))

#EXPERIMENTO DE PASAR CUSTOMER NAME A CATEGORY(ALTA CARDINALIDAD)
df_exploded["Customer_Name"] = df_exploded["Customer_Name"].astype("category")

#print(df_exploded.info(memory_usage="deep"))


##---------
# SEPARAR LAS DIMENSIONES DEL DATA FRAME DESGLOSADO

#Paso 1 — Crear Dim_Product
dim_product = (
    df_exploded[["Product"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

dim_product["Product_ID"] = dim_product.index

#REORDENASR COLUMNAS
dim_product = dim_product[["Product_ID", "Product"]]

#Paso 2 — Crear Dim_Customer
dim_customer = (
    df_exploded[["Customer_Name", "Customer_Category"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_customer["Customer_ID"] = dim_customer.index
#REORDENAR
dim_customer = dim_customer[["Customer_ID", "Customer_Name", "Customer_Category"]]

# #Paso 3 — Crear Dim_Date

df_exploded["Date"] = df_exploded["Date"].dt.floor("D") #Eliminar la variacion de la hora

dim_date = (
    df_exploded[["Date"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

dim_date["Date_ID"] = dim_date.index
dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["Day"] = dim_date["Date"].dt.day

# #REORDENAR
dim_date = dim_date[["Date_ID", "Date", "Year", "Month", "Day"]]

#Paso 4 — Construir Fact_Sales
#REEMPLAZAR TEXTO POR ID´S
fact_sales = df_exploded.merge(
    dim_product, on="Product", how="left"
)

fact_sales = fact_sales.merge(
    dim_customer, on=["Customer_Name", "Customer_Category"], how="left"
)

fact_sales = fact_sales.merge(
    dim_date, on="Date", how="left"
)

#sELECCION DE COLUMNAS
fact_sales = fact_sales[
    [
        "Transaction_ID",
        "Product_ID",
        "Customer_ID",
        "Date_ID",
        "Total_Items",
        "Total_Cost",
        "Discount_Applied",
        "Promotion"
    ]
]

#Opcional: crear surrogate key
fact_sales = fact_sales.reset_index(drop=True)
fact_sales["Sale_ID"] = fact_sales.index
#veRIFICAR tAMAÑOS

# print("dim_product ", dim_product.shape)
# print("dim_customer ",dim_customer.shape)
# print("dim_date ", dim_date.shape)
# print("fact_sales ", fact_sales.shape)

#revision de date
#print(df_exploded["Date"].head())


#REVISAR TIPO DE DATO DE LAS COLUMNAS
print(fact_sales.dtypes)
