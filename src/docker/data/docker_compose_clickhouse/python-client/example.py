from clickhouse_driver import Client
import pandahouse as ph
import numpy as np
import pandas as pd

# ClickHouse connection settings
clickhouse_settings = {
    "host": "clickhouse-server",
    "port": "9000",
    "user": "halobug",
    "password": "FcP5O5HY",
}

def convert_dtype_to_clickhouse(dtype):
    ch_type_convert_dict = {
        np.dtype("datetime64[ns]"): "Datetime64",
        np.dtype("int64"): "Int64",
        np.dtype("float64"): "Float64",
        np.dtype("object"): "String",
        np.dtype("bool"): "Bool",
    }
    return ch_type_convert_dict.get(dtype, None)

def create_table_query(df, database, table_name):
    columns = []
    for col_name, col_dtype in df.dtypes.items():
        ch_col_type = convert_dtype_to_clickhouse(col_dtype)
        if ch_col_type is None:
            print(f"Undefined type {col_dtype}")
            continue
        columns.append(f"`{col_name}` {ch_col_type} DEFAULT 0")
    
    columns_str = ", ".join(columns)
    query = (
        f"CREATE TABLE IF NOT EXISTS {database}.{table_name} ({columns_str}) "
        "ENGINE = MergeTree PARTITION BY date ORDER BY date SETTINGS index_granularity = 16384"
    )
    return query

def main():
    client = Client(**clickhouse_settings)
    
    data = {
        "date": ["2023-08-01", "2023-08-02", "2023-08-03"],
        "open": [100.00, 101.50, 102.75],
        "high": [102.50, 103.75, 104.50],
        "low": [98.25, 100.50, 101.25],
        "close": [101.25, 102.00, 103.00],
    }
    stock_df = pd.DataFrame(data)
    print(stock_df)
    
    db_name = "CRYPTO"
    table_name = "STOCK_info"
    
    create_table_query_str = create_table_query(stock_df, db_name, table_name)
    client.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
    client.execute(create_table_query_str)
    
    connection_info = {
        "database": db_name,
        "host": "http://clickhouse-server:8123/",
        "user": "halobug",
        "password": "FcP5O5HY",
    }
    
    ph.to_clickhouse(
        stock_df,
        table_name,
        index=False,
        chunksize=100000,
        connection=connection_info,
    )
    
    query = "SELECT * FROM CRYPTO.STOCK_info"
    data_frame = ph.read_clickhouse(query, connection=connection_info)
    print(data_frame)

if __name__ == "__main__":
    main()
