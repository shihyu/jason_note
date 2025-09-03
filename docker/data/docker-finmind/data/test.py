import sqlite3
import pandas as pd

# Establish connection to SQLite database and create a dataframe object
connection = sqlite3.connect('example.db')
cursor = connection.cursor()

data1 = pd.DataFrame(
    {
        "stock_id": ["1102", "1102", "1102"],
        "date": ["2002-02-01", "2002-03-01", "2002-04-01"],
        "country": ["Taiwan", "Taiwan", "Taiwan"],
        "revenue": [955532000, 740852000, 1027790000],
        "revenue_month": [1, 2, 3],
        "revenue_year": [2002, 2002, 2002],
    }
)

data2 = pd.DataFrame(
    {
        "stock_id": ["1102", "1102", "1102", "1102"],
        "date": ["2002-02-01", "2002-03-01", "2002-04-01", "2002-05-01"],
        "country": ["Taiwan", "Taiwan", "Taiwan", "Taiwan"],
        "revenue": [955532000, 740852000, 1027790000, 2027790000],
        "revenue_month": [1, 2, 3, 4],
        "revenue_year": [2002, 2002, 2002, 2002],
    }
)

# Define a function to check if a row exists in the table or not
def check_row_exists(cursor, table_name, column_dict):
    query = 'SELECT * FROM {table_name} WHERE '.format(table_name=table_name)
    for column in column_dict:
        query += '{column} = ? AND '.format(column=column)
    query = query.strip(' AND ')
    cursor.execute(query, tuple(column_dict.values()))
    return cursor.fetchone() is not None

# Insert data1 into SQLite database
table_name = 'your_table_name'
for i, row in data1.iterrows():
    if not check_row_exists(cursor, table_name, row.to_dict()):
        row.to_frame().transpose().to_sql(table_name, connection, if_exists='append', index=False)

# Insert data2 into SQLite database
for i, row in data2.iterrows():
    if not check_row_exists(cursor, table_name, row.to_dict()):
        row.to_frame().transpose().to_sql(table_name, connection, if_exists='append', index=False)
    else:
        # If the row already exists, update the row to insert the new revenue
        update_query = 'UPDATE {table_name} SET revenue = ?, revenue_month = ?, revenue_year = ? WHERE stock_id = ? AND date = ?'.format(table_name=table_name)
        cursor.execute(update_query, (row['revenue'], row['revenue_month'], row['revenue_year'], row['stock_id'], row['date']))
        connection.commit()

# Close the database connection
cursor.close()
connection.close()
