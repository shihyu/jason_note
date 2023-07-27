import clickhouse_connect

client = clickhouse_connect.get_client(
    host="clickhouse-server", port=8123, username="halobug", password="FcP5O5HY"
)

client.command('CREATE TABLE new_table (key UInt32, value String, metric Float64) ENGINE MergeTree ORDER BY key')
row1 = [1000, 'String Value 1000', 5.233]
row2 = [2000, 'String Value 2000', -107.04]
data = [row1, row2]
client.insert('new_table', data, column_names=['key', 'value', 'metric'])

#result = client.query('SELECT max(key), avg(metric) FROM new_table')
#print(result.result_rows)
