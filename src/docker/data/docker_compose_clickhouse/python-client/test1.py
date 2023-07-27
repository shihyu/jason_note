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
df = pd.DataFrame({
    '賣超券商': ['元大前金', '富邦台北', '元大敦化', '元大中壢', '摩根大通', '國泰敦南', '元大福營', '永豐金敦北', '群益建成', '富邦竹北', '第一金新竹', '新光台中', '元富佳里', '富邦興業', '群益彰化'],
    '買進': [16, 8, 0, 4, 438, 127, 0, 4, 0, 0, 0, 42, 0, 0, 0],
    '賣出': [768, 672, 652, 356, 746, 362, 215, 203, 198, 172, 170, 211, 154, 150, 106],
    '賣超張數': [-752, -664, -652, -352, -308, -235, -215, -199, -198, -172, -170, -169, -154, -150, -106]
})

print(df.to_markdown())

# 建立表格，設定欄位類型
table_name = 'test_table'
create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        賣超券商 String,
        買進 Int32,
        賣出 Int32,
        賣超張數 Int32
    ) ENGINE = Memory
'''

client.execute(create_table_query)

# 將資料框寫入表格
insert_query = f'INSERT INTO {table_name} VALUES'
insert_values = ','.join([f'(\'{row[0]}\', {row[1]}, {row[2]}, {row[3]})' for row in df.values])
client.execute(insert_query + insert_values)

# 讀取表格中的資料
result = client.execute(f'SELECT * FROM {table_name}')
print(result)

