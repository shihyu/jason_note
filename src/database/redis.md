# 安裝 Redis

```shell
sudo apt install redis-server
sudo systemctl status redis-server
```



```python
import redis

def delete_all_keys():
    redis_conn = redis.Redis(host="127.0.0.1", port=6379, db=8)
    redis_conn.flushdb()

if __name__ == "__main__":
    delete_all_keys()
```





```python
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.set('foo', 'bar')
print(r.get('foo'))
```

## 備份＆還原

```python
from github import Github
from finlab import data
from os.path import getsize
import finlab
import pickle
import redis
import zlib
import time


def update_github(git_file):
    token = ""
    # Step 1: Create a Github instance:
    g = Github(token)
    repo = g.get_user().get_repo("stockinfo")

    all_files = []
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(
                str(file).replace('ContentFile(path="', "").replace('")', "")
            )

    print(all_files)
    with open(git_file, "rb") as file:
        content = file.read()

    if git_file in all_files:
        contents = repo.get_contents("/")
        for item in contents:
            if item.path == git_file:
                contents = item
                break
        print(contents)

        while True:
            try:
                repo.update_file(
                    contents.path, "committing files", content, contents.sha
                )
                break
            except Exception as e:
                print(e)
                time.sleep(10)
                continue

        print(git_file + " UPDATED")
    else:
        while True:
            try:
                repo.create_file(git_file, "committing files", content)
                break
            except Exception as e:
                print(e)
                time.sleep(10)
                continue
        print(git_file + " CREATED")


def dump():
    redis_conn = redis.Redis(host="127.0.0.1", port=6379, db=8)
    data_keys = redis_conn.keys()
    for key in data_keys:
        with open(f'{key.decode("utf-8")}.bin', "wb") as f:
            f.write(redis_conn.get(key))
        print(
            key.decode("utf-8"),
            "==========================================================================================",
        )
        # github 單一檔案無法上傳超過50mb
        if getsize(f'{key.decode("utf-8")}.bin') < 52428800:
            update_github(f'{key.decode("utf-8")}.bin')
    redis_conn.close()


def restore(dataset):
    redis_conn = redis.Redis(host="127.0.0.1", port=6379, db=9)
    with open(f"{dataset}.bin", "rb") as f:
        redis_conn.set(dataset.encode("utf-8"), f.read())
    redis_conn.close()


def get_data():
    data_list = [
        "benchmark_return:發行量加權股價報酬指數",
        "etl:adj_close",
        "etl:finlab_tw_stock_market_ind",
        "financial_statement:合約負債_流動",
        "financial_statement:投資活動之淨現金流入_流出",
        "financial_statement:營業收入淨額",
        "financial_statement:營業活動之淨現金流入_流出",
        "financial_statement:研究發展費",
        "financial_statement:籌資活動之淨現金流入_流出",
        "financial_statement:股本",
        "financial_statement:股東權益總額",
        "fundamental_features:ROE稅後",
        "fundamental_features:業外收支營收率",
        "fundamental_features:營收成長率",
        "fundamental_features:營業利益成長率",
        "fundamental_features:營業利益率",
        "fundamental_features:經常稅後淨利",
        "institutional_investors_trading_summary:投信買賣超股數",
        "inventory",
        "margin_balance:融資券總餘額",
        "margin_transactions:融資今日餘額",
        "margin_transactions:融資使用率",
        "monthly_revenue:上月比較增減(%)",
        "monthly_revenue:去年同月增減(%)",
        "monthly_revenue:當月營收",
        "par_value_change_otc:otc_par_value_change_divide_ratio",
        "par_value_change_tse:twse_par_value_change_divide_ratio",
        "price_earning_ratio:本益比",
        "price_earning_ratio:殖利率(%)",
        "price_earning_ratio:股價淨值比",
        "price:成交股數",
        "price:收盤價",
        "price:收盤價",
        "security_industry_themes",
        "tw_business_indicators:景氣對策信號(分)",
        "tw_total_nmi:臺灣非製造業NMI",
        "tw_total_pmi:未來六個月展望",
        "tw_total_pmi:製造業PMI",
    ]
    for dataset in data_list:
        data.get(dataset)


if __name__ == "__main__":
    finlab.login(
        ""
    )
    get_data()
    dump()
    redis_conn = redis.Redis(host="127.0.0.1", port=6379, db=8)
    data_keys = redis_conn.keys()
    redis_conn.close()

    redis_conn = redis.Redis(host="127.0.0.1", port=6379, db=9)
    for key in data_keys:
        k = key.decode("utf-8")
        restore(k)
        print(k)
        print(pickle.loads(zlib.decompress(redis_conn.get(k))))
    redis_conn.close()
```

## 以字典形式寫入數據到 Redis 

```python
import redis

# 建立 Redis 連線
r = redis.Redis(host="localhost", port=6379, db=0)

if True:
    # 使用多次 hset 方法設置多個鍵值對
    r.hset("my_dict", "key1", "value1")
    r.hset("my_dict", "key2", "value2")
else:
    # 使用字典一次性設置多個鍵值對
    data = {"key1": "value1", "key2": "value2"}
    r.hmset("my_dict", data)  # 此行仍可以正常運作，但會出現 DeprecationWarning 警告


# 從 Redis 讀取字典
my_dict = r.hgetall("my_dict")
my_dict = {key.decode("utf-8"): val.decode("utf-8") for key, val in my_dict.items()}
print(my_dict)
```

