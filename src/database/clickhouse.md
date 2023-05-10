#  clickhouse



https://phoenixnap.com/kb/install-clickhouse-on-ubuntu-20-04



## Installing ClickHouse on Ubuntu 20.04

```sh
sudo apt-get install -y apt-transport-https ca-certificates dirmngr
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754

echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee \
    /etc/apt/sources.list.d/clickhouse.list
    
sudo apt-get update

sudo apt-get install -y clickhouse-server clickhouse-client

sudo service clickhouse-server start
clickhouse-client # or "clickhouse-client --password" if you've set up a password.
```



## Getting Started With ClickHouse

```sh
sudo systemctl start clickhouse-server
sudo systemctl status clickhouse-server
```

```
● clickhouse-server.service - ClickHouse Server (analytic DBMS for big data)
     Loaded: loaded (/lib/systemd/system/clickhouse-server.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2022-09-12 16:07:10 CST; 5s ago
   Main PID: 429578 (clckhouse-watch)
      Tasks: 205 (limit: 18726)
     Memory: 73.7M
     CGroup: /system.slice/clickhouse-server.service
             ├─429578 clickhouse-watchdog        --config=/etc/clickhouse-server/config.xml --pid-file=/run/clickhouse-server/clickhouse-server.pid
             └─429596 /usr/bin/clickhouse-server --config=/etc/clickhouse-server/config.xml --pid-file=/run/clickhouse-server/clickhouse-server.pid

 9月 12 16:07:10 nb-jasonyao systemd[1]: Started ClickHouse Server (analytic DBMS for big data).
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429578]: Processing configuration file '/etc/clickhouse-server/config.xml'.
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429578]: Logging trace to /var/log/clickhouse-server/clickhouse-server.log
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429578]: Logging errors to /var/log/clickhouse-server/clickhouse-server.err.log
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429596]: Processing configuration file '/etc/clickhouse-server/config.xml'.
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429596]: Saved preprocessed configuration to '/var/lib/clickhouse/preprocessed_configs/config.xml'.
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429596]: Processing configuration file '/etc/clickhouse-server/users.xml'.
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429596]: Merging configuration file '/etc/clickhouse-server/users.d/default-password.xml'.
 9月 12 16:07:10 nb-jasonyao clickhouse-server[429596]: Saved preprocessed configuration to '/var/lib/clickhouse/preprocessed_configs/users.xml'.
```

```sh
clickhouse-client --password f0409 --user default
```

# python clickhouse-driver

```sh
pip install clickhouse-driver
```

```py
from clickhouse_driver import Client
from io import StringIO
import requests
import pandas as pd

client = Client(host="localhost", port="9000", user="default", password="f0409")

def get_wespai_data(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }
    TAIGU1 = requests.get(url, headers=headers)
    TAIGU1.encoding = "utf-8"
    raw_data = pd.read_html(StringIO(TAIGU1.text))[0]
    #raw_data.to_csv(FILE_name, header=True, index=False, encoding="utf-8")
    return raw_data

df = get_wespai_data("https://stock.wespai.com/p/48812")


def read_sql(sql):
    data, columns = client.execute(sql, columnar=True, with_column_types=True)
    df = pd.DataFrame({re.sub(r"\W", "_", col[0]): d for d, col in zip(data, columns)})
    return df


def get_type_dict(tb_name):
    sql = f"select name, type from system.columns where table='{tb_name}';"
    df = read_sql(sql)
    df = df.set_index("name")
    type_dict = df.to_dict("dict")["type"]
    return type_dict


def to_sql(df, tb_name):
    type_dict = get_type_dict(tb_name)
    columns = list(type_dict.keys())
    # 類型處理
    for i in range(len(columns)):
        col_name = columns[i]
        col_type = type_dict[col_name]
        if "Date" in col_type:
            df[col_name] = pd.to_datetime(df[col_name])
        elif "Int" in col_type:
            df[col_name] = df[col_name].astype("int")
        elif "Float" in col_type:
            df[col_name] = df[col_name].astype("float")
        elif col_type == "String":
            df[col_name] = df[col_name].astype("str").fillna("")
    # df數據存入clickhouse
    cols = ",".join(columns)
    data = df.to_dict("records")
    client.execute(f"INSERT INTO {tb_name} ({cols}) VALUES", data, types_check=True)


if __name__ == '__main__':
    print(client.execute("SHOW DATABASES"))
    client.execute("DROP TABLE IF EXISTS test")
    print(client.execute("SHOW TABLES"))
    client.execute("CREATE TABLE test (x Int32) ENGINE = Memory")
    print(client.execute("SHOW TABLES"))

    client.execute("INSERT INTO test (x) VALUES", [{"x": 100}])
    client.execute("INSERT INTO test (x) VALUES", [[200]])
    client.execute(
        "INSERT INTO test (x) " "SELECT * FROM system.numbers LIMIT %(limit)s", {"limit": 3}
    )
    df = get_wespai_data("https://stock.wespai.com/p/48812")
    print(df.to_markdown())

```

## GUI TOOL

https://dbeaver.io/download/

https://dbeaver.io/files/dbeaver-ce-latest-linux.gtk.x86_64.tar.gz

## 使用 Pandas 讀寫 ClickHouse

Pandas 本身不支援 ClickHouse 相關操作, 本篇部落格主要是記錄一下自己封裝的一些讀寫操作, 所以嚴格來說標題應該是: 如何從 ClickHouse 讀取資料到 DataFrame 及將 DataFrame 寫入 ClickHouse.

### 一. Pandas 讀取 ClickHouse

GitHub 上面有幾個 Python 操作 ClickHouse 的開放原始碼專案, 不過收藏數量都不多(幾百個 star), 經過試用, 發現 clickhouse_driver 這個項目相對靠譜一點, 先使用 pip 安裝 clickhouse_driver, 讀取資料的程式碼如下:

```py
from clickhouse_driver import Client
import pandas as pd
import re

client = Client(host="xxx", database="xxx", user="xxx", password="xxx")

def read_sql(sql):
    data, columns = client.execute(sql, columnar=True, with_column_types=True)
    df = pd.DataFrame({re.sub(r"\W", "_", col[0]): d for d, col in zip(data, columns)})
    return df
```

使用 ClickHouse 的查詢命令也可以將資料讀出, 而且速度特別快, 但是得到的資料是一個超長的字串, 想要轉成 DataFrame 的話需要自己做切分和轉換, 操作比較麻煩, 以後有時間再嘗試, 查詢資料的程式碼如下:

```python
import subprocess

def read_sql(sql):
    cmd = f'clickhouse-client -t --query "{sql}"'
    data = subprocess.getoutput(cmd)
    return data
```

### 二. Pandas 寫入 ClickHouse

由於 Pandas 的資料類型跟 ClickHouse 不同, 所以有些資料類型需要做一些處理, 大概的思路是

- 獲取 ClickHouse 中指定表的各個欄位的資料類型

- 修改將要寫入 ClickHouse 的 DataFrame 的資料類型

- 將 DataFrame 裝換為字典形式
- 呼叫 ClickHouse 的 insert 命令將字典資料匯入庫中*

程式碼實現如下:

```py
from clickhouse_driver import Client
import pandas as pd
import re

client = Client(host="xxx", database="xxx", user="xxx", password="xxx")


def read_sql(sql):
    data, columns = client.execute(sql, columnar=True, with_column_types=True)
    df = pd.DataFrame({re.sub(r"\W", "_", col[0]): d for d, col in zip(data, columns)})
    return df


def get_type_dict(tb_name):
    sql = f"select name, type from system.columns where table='{tb_name}';"
    df = read_sql(sql)
    df = df.set_index("name")
    type_dict = df.to_dict("dict")["type"]
    return type_dict


def to_sql(df, tb_name):
    type_dict = get_type_dict(tb_name)
    columns = list(type_dict.keys())
    # 類型處理
    for i in range(len(columns)):
        col_name = columns[i]
        col_type = type_dict[col_name]
        if "Date" in col_type:
            df[col_name] = pd.to_datetime(df[col_name])
        elif "Int" in col_type:
            df[col_name] = df[col_name].astype("int")
        elif "Float" in col_type:
            df[col_name] = df[col_name].astype("float")
        elif col_type == "String":
            df[col_name] = df[col_name].astype("str").fillna("")
    # df數據存入clickhouse
    cols = ",".join(columns)
    data = df.to_dict("records")
    client.execute(f"INSERT INTO {tb_name} ({cols}) VALUES", data, types_check=True)

```

---

## Pandas 寫入 clickhouse 

```py
from clickhouse_driver import Client
from io import StringIO
import numpy as np
import pandahouse as ph
import requests
import pandas as pd


def get_wespai_data(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }
    TAIGU1 = requests.get(url, headers=headers)
    TAIGU1.encoding = "utf-8"
    raw_data = pd.read_html(StringIO(TAIGU1.text))[0]
    return raw_data


def insert_df_to_ch(df, str_database, str_table, bool_drop=True):
    dtypes_dict = dict(df.dtypes)
    dict_dtype = {}
    ch_type_convert_dict = {
        np.dtype("datetime64[ns]"): "Datetime64",
        np.dtype("int64"): "Int64",
        np.dtype("float64"): "Float64",
        np.dtype("object"): "String",
        np.dtype("bool"): "Bool",
    }

    create_table_cmd_str = ""
    for x in dtypes_dict:
        type_str = ch_type_convert_dict.get(dtypes_dict[x], None)
        if type_str is None:
            print(f"Undefined type {dtypes_dict[x]}")
        create_table_cmd_str = create_table_cmd_str + f"`{x}` {type_str} DEFAULT 0, "

    create_table_cmd_str = f"CREATE TABLE IF NOT EXISTS {str_database}.{str_table} ( {create_table_cmd_str[:-2]}) ENGINE = Log"
    # print(create_table_cmd_str)

    client = Client(host="localhost", port="9000", user="default", password="f0409")
    client.execute(f'CREATE DATABASE IF NOT EXISTS {str_database};')
    if bool_drop:
        client.execute(f'DROP TABLE IF EXISTS {str_database}.{str_table};')
    client.execute(create_table_cmd_str)

    connection = dict(
        database=str_database, host="http://127.0.0.1:8123/", user="default", password="f0409"
    )

    ph.to_clickhouse(df, str_table, index=False, chunksize=100000, connection=connection)


if __name__ == '__main__':
    df = get_wespai_data("https://stock.wespai.com/p/48812")
    #print(df)
    insert_df_to_ch(df, "CRYPTO", "TEST11" + "_MM_TEST", True)

```

---

```sh
組態檔案路徑：/etc/clickhouse-server/，默認的組態檔案為config.xml，但是建議將更新的組態放入config.d資料夾下，以防版本更新導致修改檔案被覆蓋。

默認資料保存路徑：/var/lib/clickhouse/

如果改路徑下的儲存空間比較小，建議將其該為大儲存空間下的目錄，例如：/app/clickhouse

注意：請注意/app/clickhouse的存取權，需要賦予clickhouse使用者的存取權，也可以直接使用chmod 775 /app/clickhouse為其設定寫存取權。


mkdir clickhouse_data/ 
sudo chown -R clickhouse:clickhouse clickhouse_data/
vim /etc/clickhouse-server/config.xml
<path>/home/shihyu/clickhouse_data/</path>
systemctl stop clickhouse-server
systemctl restart clickhouse-server
sudo systemctl status clickhouse-server
```



## 刪除XX日期之前的數據

```python
from clickhouse_driver import Client
from datetime import datetime, timedelta

client = Client(
    host="localhost",
    port="9000",
    user="default",
    password="f0409",
    settings={"allow_experimental_lightweight_delete": True},
)
str_database = "CRYPTO"
str_table = "Bitopro_Orderbook_Partition"

# 計算三個月前的日期
three_months_ago = datetime.now() - timedelta(days=90)
print(three_months_ago.strftime("%Y-%m-%d %H:%M:%S"))

# 構建 SQL 語句
# sql = f"DELETE FROM {str_database}.{str_table} WHERE date < toYYYYMMDD('{three_months_ago.strftime('%Y-%m-%d %H:%M:%S')}');"
# sql = "DELETE FROM CRYPTO.Binance_Orderbook_Partition WHERE date < '2023-01-27 10:24:30' "
sql = f"DELETE FROM CRYPTO.Binance_Orderbook_Partition WHERE date < '{three_months_ago.strftime('%Y-%m-%d %H:%M:%S')}' "
print(sql)

# 執行 SQL 語句
client.execute(sql)
```

## ClickHouse  Partition 

在 ClickHouse 中，Partition 是一種將表格分割成小塊的技術。可以在表格中設置一個或多個 Partition，這樣它們就可以存儲在不同的位置中。當查詢表格時，ClickHouse 能夠根據分區策略只查詢所需的分區，這樣就能夠提高查詢效率、降低維護成本。

在 ClickHouse 中，支持以下多種 Partition：

1. Range Partition: 根據特定的欄位和一個或多個範圍，將表格分割成多個 Partition，並將每個 Partition 存儲在一個獨立的目錄中。
2. List Partition: 根據特定的欄位和一個或多個值的列表，將表格分割成多個 Partition，並將每個 Partition 存儲在一個獨立的目錄中。
3. Hash Partition: 將表格分割成多個 Partition，並根據 Hash 函數將每個 Partition 存儲在不同的磁盤上。
4. Unpartitioned Table: 不對表格進行分區。

分區可以幫助 ClickHouse 實現更精確的查詢，因為可以通過分區信息更快地定位查找對象。例如，當表格被分成多個 Partition 時，ClickHouse 可以只查詢特定的 Partition，而非查詢整個表格，從而提高查詢效率。此外，當需要刪除 Partition 時，也不需要刪除整個表格。

總結來說，ClickHouse 中的 Partition 可以幫助你提高查詢效率、降低維護成本、以及增強表格的可用性和可擴展性。
