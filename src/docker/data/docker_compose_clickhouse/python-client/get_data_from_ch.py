import clickhouse_driver
import pandas as pd
import pickle


def get_data(client, sql):
    data = client.execute_iter(sql, with_column_types=True)
    columns = [column[0] for column in next(data)]
    return pd.DataFrame.from_records(data, columns=columns)


connection_settings = {
    "host": "clickhouse-server",
    "port": "9000",
    "user": "halobug",
    "password": "FcP5O5HY",
}

client = clickhouse_driver.Client(**connection_settings)

# 建立新資料庫
client.execute("CREATE DATABASE IF NOT EXISTS CRYPTO")

print(client.execute("SHOW DATABASES"))
client.execute("USE CRYPTO")

# 創建一個簡單的表格
df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})
client.execute(
    "CREATE TABLE IF NOT EXISTS test_table (name String, age Int32) ENGINE = Memory"
)

# 將資料框寫入表格
client.execute("INSERT INTO test_table VALUES", df.to_dict("records"))

# 讀取表格中的資料
result = client.execute("SELECT * FROM test_table")
print(result)

df = get_data(
        client,
        # "SELECT * FROM CRYPTO.Bitopro_Orderbook WHERE date > '2022-10-27' AND date < '2022-10-28 10:39:31' ORDER BY date ASC",
        "SELECT * FROM CRYPTO.BinanceOrderbookPartition_simplifiedFields WHERE date > '2023-08-15 15:10:17'",
        # "SELECT * FROM CRYPTO.Bitopro_Orderbook",
    )

# 保存 DataFrame 到 pickle 文件
with open('dataframe.pkl', 'wb') as file:
    pickle.dump(df, file)

# 从 pickle 文件加载 DataFrame
with open('dataframe.pkl', 'rb') as file:
    loaded_df = pickle.load(file)

# 打印加载的 DataFrame
print("Loaded DataFrame:")
print(loaded_df)
