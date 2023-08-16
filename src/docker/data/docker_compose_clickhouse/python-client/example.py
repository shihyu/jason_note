from clickhouse_driver import Client
import numpy as np
import pandas as pd
import pandahouse as ph

# ClickHouse connection settings
connection_settings = {
    "host": "clickhouse-server",
    "port": "9000",
    "user": "halobug",
    "password": "FcP5O5HY",
}

def create_db_table(client, df, database, table):
    dtypes_dict = dict(df.dtypes)
    ch_type_convert_dict = {
        np.dtype("datetime64[ns]"): "Datetime64",
        np.dtype("int64"): "Int64",
        np.dtype("float64"): "Float64",
        np.dtype("object"): "String",
        np.dtype("bool"): "Bool",
    }
    columns = []
    for column, dtype in dtypes_dict.items():
        ch_type = ch_type_convert_dict.get(dtype, None)
        if ch_type is None:
            print(f"Undefined type {dtype}")
        columns.append(f"`{column}` {ch_type} DEFAULT 0")
    
    create_table_cmd = f"CREATE TABLE IF NOT EXISTS {database}.{table} ({', '.join(columns)}) ENGINE = MergeTree PARTITION BY date ORDER BY date SETTINGS index_granularity = 16384"
    client.execute(f"CREATE DATABASE IF NOT EXISTS {database};")
    client.execute(create_table_cmd)

def main():
    client = Client(**connection_settings)

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
    create_db_table(client, stock_df, db_name, table_name)

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
    result_df = pd.DataFrame(client.execute(query))
    print(result_df)

if __name__ == "__main__":
    main()
