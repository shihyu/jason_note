import clickhouse_driver
import pandas as pd


connection_settings = {
    'host': 'clickhouse-server',
    'port': '9000',
    'user': 'halobug',
    'password': 'FcP5O5HY'
}

client = clickhouse_driver.Client(**connection_settings)

# 建立新資料庫
client.execute('CREATE DATABASE IF NOT EXISTS CRYPTO')

print(client.execute("SHOW DATABASES"))
client.execute('USE CRYPTO')

# 創建一個簡單的表格
df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie'], 'age': [25, 30, 35]})
client.execute('CREATE TABLE IF NOT EXISTS test_table (name String, age Int32) ENGINE = Memory')

# 將資料框寫入表格
client.execute('INSERT INTO test_table VALUES', df.to_dict('records'))

# 讀取表格中的資料
result = client.execute('SELECT * FROM test_table')
print(result)

