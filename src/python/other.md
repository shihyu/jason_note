## 創立每列
```python
import pandas as pd

# 創建空的 DataFrame
df = pd.DataFrame(columns=['Technology', 'Consumer', 'Healthcare', 'Energy'])

# 股票字典
stocks = {
    'GOOG': ['Technology', 'Healthcare'],
    'AAPL': ['Consumer']
}

# 遍歷股票字典並將 DataFrame 中相應的單元格設置為 True
for stock, industries in stocks.items():
    for industry in industries:
        df.loc[stock, industry] = True

# 將缺失值（即 False）替換為 False
df.fillna(False, inplace=True)

print(df)
```

## 抓取美股分K歷史數據 

```python
import yfinance as yf
import pandas as pd
import datetime as dt

# 設置股票代碼和時間範圍
ticker = 'AAPL'
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=30)

# 將時間範圍拆分成多個時間段，每個時間段為 7 天
date_ranges = pd.date_range(start=start_date, end=end_date, freq='7d')

# 獲取歷史數據
dataframes = []
for i in range(len(date_ranges) - 1):
    start = date_ranges[i].strftime('%Y-%m-%d')
    end = date_ranges[i+1].strftime('%Y-%m-%d')
    df = yf.download(ticker, start=start, end=end, interval='1m')
    dataframes.append(df)

# 合併為一個 DataFrame 對象
data = pd.concat(dataframes)

# 打印 DataFrame 對象
print(data)
```

## keyvalue-sqlite

```python
# pip install keyvalue-sqlite
from keyvalue_sqlite import KeyValueSqlite

DB_PATH = './db.sqlite'

db = KeyValueSqlite(DB_PATH, 'table-name')

# Now use standard dictionary operators
db.set('0', {"1101":23, "2330": 100})
actual_value = db.get('0')
print(actual_value)
db.set('0', '211')
actual_value = db.get('0')
print(actual_value)
db.remove('0')
actual_value = db.get('0')
print(actual_value)
```



## sched 定時

```python
import sched
import time
import datetime

'''
導入 sched 模塊和 time 模塊。
定義一個 main() 函數，用於執行程序的主要邏輯。
定義一個 run_main() 函數，用於在指定時間執行 main() 函數。
獲取當前時間，並計算距離下一個執行時間的時間差 delta。
使用 sched 模塊的 enter() 方法，將 run_main() 函數添加到調度隊列中，並設置下一次執行的時間為當前時間加上 delta。
使用 sched 模塊的 run() 方法，啟動調度器。
'''

def main():
    # 在這裡編寫程序的主要邏輯
    print("Hello, world!")

def run_main():
    # 獲取當前時間
    now = datetime.datetime.now()

    # 計算距離下一個執行時間的時間差
    next_time = now.replace(hour=8, minute=45, second=0, microsecond=0)
    if next_time < now:
        next_time += datetime.timedelta(days=1)
    delta = next_time - now

    # 計算下一個執行時間，並輸出日誌
    next_time_str = next_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Next run time: {next_time_str}")

    # 在指定時間執行程序的主要邏輯
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(delta.total_seconds(), 1, main, ())
    scheduler.run()

if __name__ == "__main__":
    run_main()
```

## pdf 分割

```python
from PyPDF2 import PdfReader, PdfWriter


# PDF文件分割
def split_pdf(read_file, out_detail):
    try:
        fp_read_file = open(read_file, "rb")
        pdf_input = PdfReader(fp_read_file)  # 將要分割的PDF內容格式話
        page_count = pdf_input.pages  # 獲取PDF頁數
        print(page_count)  # 打印頁數

        with open(out_detail, "r", True, "utf-8") as fp:
            # print(fp)
            txt = fp.readlines()
            # print(txt)
            for detail in txt:  # 打開分割標準文件
                # print(type(detail))
                pages = detail.strip()  # 空格分組
                #  write_file, write_ext = os.path.splitext(write_file)  # 用於返回文件名和擴展名元組
                pdf_file = f"{pages}.pdf"
                # liststr=list(map(int, pages.split('-')))
                # print(type(liststr))
                start_page, end_page = list(map(int, pages.split("-")))  # 將字符串數組轉換成整形數組
                start_page -= 1
                try:
                    print(f"開始分割{start_page}頁-{end_page}頁，保存為{pdf_file}......")
                    pdf_output = PdfWriter()  # 實例一個 PDF文件編寫器
                    for i in range(start_page, end_page):
                        pdf_output.add_page(pdf_input.pages[i])
                    with open(pdf_file, "wb") as sub_fp:
                        pdf_output.write(sub_fp)
                    print(f"完成分割{start_page}頁-{end_page}頁，保存為{pdf_file}!")
                except IndexError:
                    print(f"分割頁數超過了PDF的頁數")
        # fp.close()
    except Exception as e:
        print(e)
    finally:
        fp_read_file.close()


split_pdf("./The Art of Writing Efficient Programs An advanced programmers guide to efficient hardware utilization and compiler... (Fedor G. Pikus) (Z-Library).pdf", "config.txt")
```





## 使用 `urllib.parse` 模組的 `unquote()` 函數將編碼過的 URL 字符串解碼

```python
import urllib.parse

url = "https://www.finlab.tw/wp-content/uploads/2022/07/%E6%88%AA%E5%9C%96-2022-07-25-%E4%B8%8B%E5%8D%8812.42.21-1536x431.png"
decoded_url = urllib.parse.unquote(url)

print(decoded_url)
```

## dataFrame 寫到csv, 再從csv 讀回dataframe

```python
import pandas as pd

# Create a sample DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'], 
        'Age': [25, 30, 35], 
        'City': ['New York', 'Paris', 'London']}
df = pd.DataFrame(data)

# Write the DataFrame to a CSV file
df.to_csv('data.csv', index=False)

# Read the CSV file back into a DataFrame
new_df = pd.read_csv('data.csv')

# Print the original and new DataFrames
print('Original DataFrame:\n', df)
print('\nNew DataFrame:\n', new_df)
```



## 顯示 datafrmae index 跟  欄位型態

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'col1': [1, 2, 3],
    'col2': ['a', 'b', 'c']
}, index=pd.date_range('2022-01-01', periods=3))

print(df.index)
print(df.dtypes)
```

## 已經在 sqlite 的 primary_keys 不 insert data

```python
import pandas as pd
import sqlite3


class FinmindAPI:
    db_path = "example.db"

    @staticmethod
    def insert_db(data):
        conn = sqlite3.connect(FinmindAPI.db_path)
        create_table = """
    CREATE TABLE IF NOT EXISTS TaiwanStockMonthRevenue (
        stock_id TEXT,
        date TEXT,
        revenue INTEGER
    );"""

        conn.execute(create_table)
        # Check if data already exists in the database
        primary_keys = ["stock_id", "date"]
        existing_data = pd.read_sql_query(
            f"SELECT {', '.join(primary_keys)} FROM TaiwanStockMonthRevenue", con=conn
        )
        if (
            existing_data.set_index(primary_keys)
            .index.isin(data.set_index(primary_keys).index)
            .any()
        ):
            print("Data already exists in database, skipping insertion")
            conn.close()
            return

        # Insert data into database
        data.to_sql(
            name="TaiwanStockMonthRevenue", con=conn, if_exists="append", index=False
        )
        conn.close()
        print(f"Data inserted to database successfully.")


if __name__ == "__main__":
    # Create example data
    data1 = pd.DataFrame(
        {
            "stock_id": ["2330", "2454", "2382"],
            "date": ["2020-01", "2020-01", "2020-01"],
            "revenue": [1000, 2000, 3000],
        }
    )
    data2 = pd.DataFrame(
        {
            "stock_id": ["2330", "2454", "2382"],
            "date": ["2020-02", "2020-02", "2020-02"],
            "revenue": [4000, 5000, 6000],
        }
    )

    # Insert first set of data
    print("Inserting first set of data ...")
    FinmindAPI.insert_db(data1)
    # Insert same data again
    print("Inserting same data again ...")
    FinmindAPI.insert_db(data1)
    # Insert new set of data
    print("Inserting new set of data ...")
    FinmindAPI.insert_db(data2)
```



## 產生num組加總為1的小數數值

```python
import random

def generate_random_decimals(num):
    """
    產生num組加總為1的小數數值

    Args:
        num: 需要產生的小數數值的組數

    Returns:
        一個包含num組小數數值的列表，每組小數數值都是一個長度為3的列表
    """
    result = []
    # 初始化三個數值
    for i in range(num):
        data = [0.0] * 3
        # 隨機產生兩個小數數值
        data[0] = round(random.uniform(0, 1), 2)
        data[1] = round(random.uniform(0, 1 - data[0]), 2)
        # 計算第三個小數數值
        data[2] = round(1 - data[0] - data[1], 2)
        result.append(data)
    return result

if __name__ == '__main__':
    data = generate_random_decimals(2)
    print(data)
```

## 讀檔正則取圖下載

```python
import os
import re
import requests
import cv2
import numpy as np

# 設置要讀取的文件路徑
file_path = "./learn_network.md"

# 設置下載目標目錄
target_dir = "images"

# 設置轉換後的圖檔格式
target_ext = ".jpg"

# 創建目標目錄
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 定義正則表達式來匹配圖像URL
with open(file_path, "r") as f:
    text = f.read()
    pattern = r"\!\[.*?\]\((.*?)\)"
    image_urls = re.findall(pattern, text)

    for img in image_urls:
        print(img)
    input()

    for url in image_urls:
        try:
            print(url)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # 取得圖像的文件名和擴展名
                filename = url.split("/")[-1]
                ext = os.path.splitext(filename)[1].lower()
                img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                filename = os.path.splitext(filename)[0] + target_ext
                filepath = os.path.join(target_dir, filename)
                cv2.imwrite(filepath, img)
                print(filename + " 下載成功")
            else:
                print(filename + " 下載失敗")
        except Exception as e:
            print(f"下載圖像失敗: {e}")
```

## 函數插入log

```python
import os
import sys

def insert_to_func(lines, func_lines, file_name):
    for i in func_lines:
        for j in range(i-1, len(lines)):
            if str(lines[j]).find(';') != -1:
                break

            if str(lines[j]).find('{') != -1:
                if str(lines[j]).find('}') != -1:
                    break

                if str(file_name).find('.java') != -1:
                    lines.insert(j+1, '\tSystem.out.println("YAO [" + Thread.currentThread().getStackTrace()[2].getClassName() + "|" + Thread.currentThread().getStackTrace()[2].getMethodName() + "|" + Thread.currentThread().getStackTrace()[2].getFileName() + ":" + Thread.currentThread().getStackTrace()[2].getLineNumber()+"]");\n')
                elif str(file_name).find('.cpp') != -1 or str(file_name).find('.c') != -1 or str(file_name).find('.cc') != -1:
                    lines.insert(j+1, '::printf ("This is line %d of file %s (function %s)\\n", __LINE__, __FILE__, __func__);')
                elif str(file_name).find('.go'): 
                    lines.insert(j+1,'\tutils.Trace("")')

                break

    return lines

def main():
    if len(sys.argv) < 2:
        print("please input python test.py filename")
        return

    file_name = sys.argv[1]
    print(file_name)
 
    if str(file_name).find('.java') != -1:
        os.system("ctags-exuberant -x " + file_name + " | ack -o -w 'method\s+.*' | ack -o '\d+\s+.*' | ack -o '^\d+\s+' | sort -k 1 -nr > /tmp/test.txt")
    elif str(file_name).find('.cpp') != -1 or str(file_name).find('.c') != -1:
        os.system("ctags-exuberant -x " + file_name + " | ack -o -w 'function\s+.*' | ack -o '\d+\s+.*' | ack -o '^\d+\s+' | sort -k 1 -nr > /tmp/test.txt")
    elif str(file_name).find('.go') != -1:
        os.system("ctags-exuberant -x " + file_name + " | ack -o -w 'func.*'  | ack -o '\d+\s+.*' | ack -o '^\d+\s+' | sort -k 1 -nr > /tmp/test.txt")
    else:
        print('unknown file type')
        return

    with open('/tmp/test.txt', 'r+') as f:
        func_lines = [int(i) for i in f.read().splitlines()]

    with open(file_name, 'r+') as f:
        lines = f.read().splitlines()

    insert_list_finish = insert_to_func(lines, func_lines, file_name)

    with open(file_name, "w+") as new_file:
        for l in insert_list_finish:
            new_file.write(l + '\n')

if __name__=='__main__':
    main()

```

## 輸入日期取得上週五日期

```python
from datetime import date, datetime, timedelta

#today = date.today()  # 取得今天日期
today = datetime(2023, 3, 10)
last_friday = today - timedelta(days=today.weekday() + 3)  # 回推到上週五
last_friday_str = last_friday.strftime('%Y/%m/%d')  # 轉換成指定格式的字串

print(last_friday_str)  # 印出上週五的日期
```

## 模擬程式執行一段時間後出現問題需要重啟

```python
import os
import sys
import time
import threading

def main():
    while True:
        # 模擬程式執行一段時間後出現問題需要重啟
        time.sleep(5)
        if should_restart():
            restart_program()

def should_restart():
    try:
        a = 1 / 0
        return False
    except Exception as err:
        print(err)
        return True

def restart_program():
    python = sys.executable
    print("Restarting program with PID {} and TID {}".format(os.getpid(), threading.get_ident()))
    os.execl(python, python, *sys.argv)

if __name__ == '__main__':
    print("Starting program with PID {} and TID {}".format(os.getpid(), threading.get_ident()))
    main()
```





## 輸入日期取得上個月最後一天日期

```python
import datetime

def get_last_day_of_month(date):
    first_day = datetime.datetime(date.year, date.month, 1)  # 當月份的第一天
    last_day = first_day.replace(month=first_day.month+1, day=1) - datetime.timedelta(days=1)  # 當月份的最後一天
    return last_day.strftime('%Y-%m-%d')  # 格式化輸出日期

# 呼叫函數並輸出結果
date = datetime.datetime(2023, 3, 12)  # 要計算的日期
print(get_last_day_of_month(date))
```



## 找出 Pct_Change_12M 和 Volume_12M 都為True的月份

```python
import pandas as pd
import yfinance as yf
from datetime import timedelta

# 下載資料
# df = yf.download("2324.TW", start="2000-01-01", end="2023-01-01")
df = yf.download("8299.TWO", start="2000-01-01", end="2023-01-01")

# 計算月K資料
monthly_df = df.resample("M").apply(
    {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
)

# 將日期轉換為月初的日期
monthly_df.index = monthly_df.index.to_period("M").to_timestamp("M")

# 計算月漲幅
monthly_df["Pct_Change"] = monthly_df["Close"].pct_change() * 100

# 計算成交量12個月移動平均
monthly_df["Volume_MA12"] = monthly_df["Volume"].rolling(window=12).mean()

# 計算是否股價創下過去12個月新高
monthly_df["New_High_12M"] = (
    monthly_df["High"] == monthly_df["High"].rolling(window=12).max()
)

# 判斷當月漲幅、成交量和股價是否都超過過去12個月移動平均和最高價格
monthly_df["Pct_Change_12M"] = (
    monthly_df["Pct_Change"] > monthly_df["Pct_Change"].rolling(window=12).mean()
)
monthly_df["Volume_12M"] = monthly_df["Volume"] > monthly_df["Volume_MA12"]
monthly_df["All_12M"] = (
    monthly_df["Pct_Change_12M"] & monthly_df["Volume_12M"] & monthly_df["New_High_12M"]
)

# 找出 Pct_Change_12M、Volume_12M、New_High_12M 和 within_3_months 都為 True 的月份
entries = monthly_df.loc[monthly_df["All_12M"]]


# 將 index 日期加 3 個月，並命名為 'Next_3_Months'
entries["Next_3_Months"] = entries.index + pd.DateOffset(months=3)

# 往下 shift 一列
entries["Next_3_Months"] = entries["Next_3_Months"].shift(1)

entries["Within_3_Months"] = entries["Next_3_Months"] >= entries.index


print(entries)
```



## 永豐期貨/選擇權計算周選代號

```python
from multiprocessing import Process, Queue
from shioaji.contracts import Contract
from shioaji import Exchange
from time import sleep
from line_notify import LineNotify
from datetime import datetime, timedelta

import re
import redis
import sys
import platform
import signal
import shioaji as sj
import os
import json


def get_option_week(api):
    def get_previous_wednesday():
        today = datetime.today()
        wednesday = today - timedelta(days=today.weekday()) + timedelta(days=2)
        previous_wednesday = wednesday - timedelta(days=7)
        return previous_wednesday.date()

    def get_this_week_wednesday():
        today = datetime.today()
        wednesday = (today + timedelta(days=(2 - today.weekday()))).date()
        return wednesday

    def get_next_week_wednesday():
        today = datetime.today()
        wednesday = (today + timedelta(days=(2 - today.weekday() + 7))).date()
        return wednesday

    option_symbols = (str(api.Contracts.Options))[1:-1].split(", ")
    near_week_option_symbol = [string for string in option_symbols if "TX" in string]
    print(near_week_option_symbol)

    symbols = sorted([x.symbol for x in api.Contracts.Options.TXO])
    near_option_symbol_date = symbols[0][3:9]

    for option in api.Contracts.Options:
        for contract in option:
            if "TX" in contract.category and near_option_symbol_date in contract.symbol:
                now = datetime.now()
                wednesday_time = get_this_week_wednesday()
                wednesday_time = datetime.combine(
                    wednesday_time, datetime.min.time()
                ) + timedelta(hours=15)

                # 根據當前時間判斷是否在星期三 15:00之前。如果在此時間之前，則列印上週三和本週三的日期；否則列印本週三和下週三的日期：
                if now < wednesday_time:
                    if datetime.strptime(
                        contract.update_date, "%Y/%m/%d"
                    ).date() >= get_previous_wednesday() and contract.delivery_date == get_this_week_wednesday().strftime(
                        "%Y/%m/%d"
                    ):
                        print(
                            contract.symbol,
                            contract.name,
                            contract.update_date,
                            contract.delivery_date,
                        )
                        return contract.symbol
                else:
                    if datetime.strptime(
                        contract.update_date, "%Y/%m/%d"
                    ).date() >= get_this_week_wednesday() and contract.delivery_date == get_next_week_wednesday().strftime(
                        "%Y/%m/%d"
                    ):
                        print(
                            contract.symbol,
                            contract.name,
                            contract.update_date,
                            contract.delivery_date,
                        )
                        return contract.symbol


with open(os.environ["HOME"] + "/.mybin/shioaji_token.txt", "r") as f:
    api = sj.Shioaji()
    kw_login = json.loads(f.read())
    api.login(**kw_login, contracts_timeout=300000)

    print(get_option_week(api))

    S = get_option_week(api)[:3]

    for option in api.Contracts.Options[S]:
        print(option)

```

```python
import datetime

def get_option_week():
    # 設定選擇權到期時間
    expiration_time = datetime.time(15, 0, 0)

    # 取得當前日期的年份和月份
    today = datetime.date.today()
    year = today.year
    month = today.month

    # 找到本月的第一個星期三
    first_wednesday = datetime.date(year, month, 1)
    while first_wednesday.weekday() != 2:
        first_wednesday = first_wednesday.replace(day=first_wednesday.day+1)

    # 計算今天是第幾週
    today_year, today_week, _ = today.isocalendar()
    first_wednesday_year, first_wednesday_week, _ = first_wednesday.isocalendar()
    week_num = today_week - first_wednesday_week + 1

    # 判斷是否過了選擇權到期時間
    if datetime.datetime.now().time() >= expiration_time:
        week_num += 1

    return week_num
```


```python
import cv2
import glob
import os

# 變更到指定尺寸，長寬邊不足者補黑色
def process_image(img, min_side=608):
    size = img.shape
    h, w = size[0], size[1]
    scale = max(w, h) / float(min_side)
    new_w, new_h = int(w / scale), int(h / scale)
    resize_img = cv2.resize(img, (new_w, new_h), cv2.INTER_AREA)  # 變更尺寸
    if new_w % 2 != 0 and new_h % 2 == 0:
        top, bottom, left, right = (
            (min_side - new_h) // 2,
            (min_side - new_h) // 2,
            (min_side - new_w) // 2 + 1,
            (min_side - new_w) // 2,
        )
    elif new_h % 2 != 0 and new_w % 2 == 0:
        top, bottom, left, right = (
            (min_side - new_h) // 2 + 1,
            (min_side - new_h) // 2,
            (min_side - new_w) // 2,
            (min_side - new_w) // 2,
        )
    elif new_h % 2 == 0 and new_w % 2 == 0:
        top, bottom, left, right = (
            (min_side - new_h) // 2,
            (min_side - new_h) // 2,
            (min_side - new_w) // 2,
            (min_side - new_w) // 2,
        )
    else:
        top, bottom, left, right = (
            (min_side - new_h) // 2 + 1,
            (min_side - new_h) // 2,
            (min_side - new_w) // 2 + 1,
            (min_side - new_w) // 2,
        )
    pad_img = cv2.copyMakeBorder(
        resize_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0]
    )
    return pad_img


# 讀寫目錄
inputPath = "video"
outputPath = "images"

files = os.path.join(inputPath, "*.mp4")
files_grabbed = []
files_grabbed.extend(sorted(glob.iglob(files)))

for videoId in range(len(files_grabbed)):
    print(files_grabbed[videoId])
    raw = cv2.VideoCapture(files_grabbed[videoId])
    fIndex = 1
    fCount = 0

    while 1:
        # 影片轉圖片
        ret, frame = raw.read()
        fCount += 1
        if ret == True:
            if (fCount % 5) == 0:
                img_pad = process_image(frame, min_side=608)
                cv2.imwrite(
                    "%s/%02d-frame-608x608-%04d.jpg" % (outputPath, videoId, fIndex),
                    img_pad,
                )
                fIndex += 1
        else:
            break
```



## 目前主機時區跟 Taipei 時區差多少 offset?

使用 Python 標準庫的 `datetime` 模組的 `now` 方法，並使用 `pytz` 模組的 `timezone` 方法，得到目前的本地時間，然後再使用 `astimezone` 方法，轉換為 Taipei 時間，並通過計算得到 offset：

```python
from datetime import datetime
import pytz

local_time = datetime.now()
local_time = pytz.timezone('UTC').localize(local_time)
taipei_time = local_time.astimezone(pytz.timezone('Asia/Taipei'))
offset = int((taipei_time - local_time).total_seconds() / 3600)
print(f"Local time is {local_time}. Taipei time is {taipei_time}. Offset is {offset} hours.")
```





## 裝飾器傳遞參數 *args 和 **kwargs

```python
def funA(fn):
    # 定義一個嵌套函數
    def say(*args,**kwargs):
        print(args, kwargs)
        fn(*args,**kwargs)
    return say
@funA
def funB(arc):
    print("C語言中文網：",arc)

@funA
def other_funB(name,arc):
    print(name,arc)

funB("http://c.biancheng.net")
other_funB("Python教程：","http://c.biancheng.net/python")
```

## 【Python line_profiler & memory_profiler】分析每一行程式碼的耗時及記憶體佔用情況

https://codeantenna.com/a/XoAFyhqZ2B

```sh
pip install line_profiler
```

```python
from line_profiler import LineProfiler


def func_line_time(follow=[]):
    def decorate(func):
        @wraps(func)
        def profiled_func(*args, **kwargs):
            try:
                profiler = LineProfiler()
                profiler.add_function(func)  # 增加每列的行數
                for f in follow:
                    profiler.add_function(f)
                profiler.enable_by_count()  # enable_by_count進行執行以獲取消耗的時間
                return func(*args, **kwargs)
            finally:
                profiler.print_stats()  # 顯示結果

        return profiled_func

    return decorate


@func_line_time()
def process(self, params):
    import pandas as pd`在這裡插入程式碼片`
    pass
```

- Hit：程式碼運行次數；
- %Time：程式碼佔了它所在函數的消耗的時間百分比，通常直接看這一列。
- 在這裡我們主要觀察%Time 所佔用的百分比，對百分比較高的行數進行最佳化為第一選擇。

## 藉助記憶體分析庫 memory_profiler 查看每一行消耗了多少記憶體？

```sh
pip install memory_profiler
```

```python
# 2. 藉助記憶體分析庫 memory_profiler 查看每一行消耗了多少記憶體？
from memory_profiler import profile


# precision 精確到小數點後幾位
# stream 此模組分析結果保存到‘memory_profiler.log’ 記錄檔。如果沒有此參數，分析結果會在控制檯輸出
# @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
@profile(precision=4)
def process():
    print('memory analysis------------')
    pass

process()
pri
```

Mem 是總消耗的記憶體

- Increment 是第幾行程式碼運行完後增加的記憶體
- 通過memory_profiler 我們可以分析到每一行運行完後佔用的記憶體。這部分記憶體在處理程序沒結束的時候是不好被回收掉的，因此在這裡如果有哪一行邏輯運行一直在增加記憶體消耗，則這行可能是罪魁禍首。

---

## simple  memory_profiler  example

```python
from memory_profiler import profile

@profile
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a

if __name__ == '__main__':
    my_func()

```



## python 引用放掉記憶體

```python
from memory_profiler import profile
import time
import gc

'''
在上面的程式碼中，我們創建了兩個類 A 和 B，並使用這些類創建了一個實例。由於類 B 引用了類 A 的實例，因此類 A 的實例將不能被內存管理器自動回收。因此，這將導致無法釋放內存的情況。
'''
# Example of un-collectable memory in Python
class A:
    def __init__(self, data):
        self.data = data
        self.b = B(self)

class B:
    def __init__(self, a):
        self.large_memory = bytearray(1024 * 1024)
        self.a = a

 
@profile
def call():
    a = A(10)
    del a
 
def main():
    while True:
        time.sleep(1)
        call()
 
if __name__ == "__main__":
    main()

```

## Test memory leak



```python
from memory_profiler import profile
import datetime as dt
import requests
import time
import httpx
import gc
 
@profile
def call():
    url = "https://api.bitopro.com/v3/provisioning/trading-pairs"
    response = httpx.get(url)
    if response.status_code == 200:
        data = response.json()
        print(response.status_code, dt.datetime.now())
        response.close()
        gc.collect()
    else:
        print("Request failed with status code:", response.status_code)
    
 
def main():
    while True:
        time.sleep(1)
        call()
 
if __name__ == "__main__":
    main()
```



## [每5秒委託成交統計](https://www.twse.com.tw/zh/page/trading/exchange/MI_5MINS.html)



```python
from datetime import timedelta
import time
import polars as pl
import datetime as dt 
import requests
import json


def get_webmsg(year, month, day):
    print(year, month, day)
    date = str(year) + "{0:0=2d}".format(month) + "{0:0=2d}".format(day)
    url_twse = (
        "http://www.twse.com.tw/exchangeReport/MI_5MINS?response=json&date=" + date
    )
    print(url_twse)
    res = requests.post(url_twse)
    data_json = json.loads(res.text)
    if data_json != {'stat': '很抱歉，沒有符合條件的資料!'}:
        df = pl.DataFrame(
            data_json["data"],
            schema=[
                "時間",
                "累積委託買進筆數",
                "累積委託買進數量",
                "累積委託賣出筆數",
                "累積委託賣出數量",
                "累積成交筆數",
                "累積成交數量",
                "累積成交金額",
            ],
        )
        return df
    return pl.DataFrame()


if __name__ == '__main__':
    start_date = dt.datetime(2019, 1, 1) #.strftime("%Y-%m-%d")
    end_date = dt.datetime(2023, 1, 20) #.strftime("%Y-%m-%d")

    while start_date < end_date:
        time.sleep(1)
        print(get_webmsg(start_date.year, start_date.month, start_date.day))
        start_date = start_date + timedelta(days=1)
```

## polars

https://github.com/pola-rs/polars

```sh
pip install polars
```

```python
import polars as pl

df = pl.DataFrame(
    {
        "A": [1, 2, 3, 4, 5],
        "fruits": ["banana", "banana", "apple", "apple", "banana"],
        "B": [5, 4, 3, 2, 1],
        "cars": ["beetle", "audi", "beetle", "beetle", "beetle"],
    }
)

print(df)
df = df.sort("fruits").select(
    [
        "fruits",
        "cars",
        pl.lit("fruits").alias("literal_string_fruits"),
        pl.col("B").filter(pl.col("cars") == "beetle").sum(),
        pl.col("A").filter(pl.col("B") > 2).sum().over("cars").alias("sum_A_by_cars"),
        pl.col("A").sum().over("fruits").alias("sum_A_by_fruits"),
        pl.col("A").reverse().over("fruits").alias("rev_A_by_fruits"),
        pl.col("A").sort_by("B").over("fruits").alias("sort_A_by_B_by_fruits"),
    ]
)
print(df)
```

## multiprocessing queue with non blocking

```python
from loguru import logger
import multiprocessing
import time


def processFun(conn):
    while True:
        try:
            print(conn.get(timeout=5)) # 等5秒沒數據就丟異常
        except Exception as e:
            logger.exception(e)
        print("接收到數據了", conn.qsize())


if __name__ == "__main__":
    # 創建管道
    conn = multiprocessing.Queue(10)
    # 創建子進程
    process = multiprocessing.Process(target=processFun, args=(conn,))
    # 啟動子進程
    process.start()
    i = 0
    while True:
        time.sleep(6)
        print(i)
        conn.put(i)
        i += 1
```

##  Dispatching Multiple WebSocketApps - Long-lived Connection

```python
# import websocket, rel
#
# addr = "wss://api.gemini.com/v1/marketdata/%s"
# for symbol in ["BTCUSD", "ETHUSD", "ETHBTC"]:
#    ws = websocket.WebSocketApp(addr % (symbol,), on_message=lambda w, m : print(m))
#    ws.run_forever(dispatcher=rel, reconnect=3)
#
#
# rel.signal(2, rel.abort) # Keyboard Interrupt
# rel.dispatch()

from multiprocessing import Process
import time
import websocket
import rel
import signal
import os


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("Opened connection")


def receive_signal(signum, stack):
    print("Received:", signum, os.getpid())
    ws.close()
    rel.abort()
    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic␣
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()


def monitor(pid, ws):
    print("Waiting ...")
    time.sleep(3)
    os.kill(pid, signal.SIGUSR1)


if __name__ == "__main__":
    print(os.getpid())
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://api.gemini.com/v1/marketdata/BTCUSD",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    signal.signal(signal.SIGUSR1, receive_signal)
    monitor_task = Process(target=monitor, args=(os.getpid(), ws),)

    monitor_task.start()
    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic␣
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
    monitor_task.join()
```



## How can I send a signal from a python program?

```python
import signal
import os
import time

def receive_signal(signum, stack):
    print('Received:', signum)

signal.signal(signal.SIGUSR1, receive_signal)
signal.signal(signal.SIGUSR2, receive_signal)

print('My PID is:', os.getpid())

while True:
    print('Waiting...')
    time.sleep(3)
    os.kill(os.getpid(), signal.SIGUSR1) 
```



## 記憶體監控

```python
from loguru import logger
import os
import time
import platform
import psutil
import signal
import sys


class Watcher:
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try:
            print("kill")
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass


logger.add(
    f"{__file__}.log",
    encoding="utf-8",
    enqueue=True,
    retention="10 days",
    # filter=error_only,
)


def getListOfProcessSortedByMemory():
    """
    Get list of running process sorted by Memory Usage
    """
    listOfProcObjects = []
    # Iterate over the list
    for proc in psutil.process_iter():
        try:
            # Fetch process details as dict
            pinfo = proc.as_dict(attrs=["pid", "name", "username"])
            pinfo["vms"] = proc.memory_info().vms / (1024 * 1024)
            # Append dict to list
            listOfProcObjects.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # Sort list of dict by key vms i.e. memory usage
    listOfProcObjects = sorted(
        listOfProcObjects, key=lambda procObj: procObj["vms"], reverse=True
    )
    return listOfProcObjects


def get_all_memory_usage():
    # Getting all memory using os.popen()
    total_memory, used_memory, free_memory = map(
        int, os.popen("free -t -m").readlines()[-1].split()[1:]
    )

    # Memory usage
    logger.info(f"RAM memory % used: {round((used_memory / total_memory) * 100, 2)}")
    return round((used_memory / total_memory) * 100, 2)


if __name__ == "__main__":
    if platform.system().lower() == "linux":
        Watcher()

    while True:
        time.sleep(10)
        listOfRunningProcess = getListOfProcessSortedByMemory()
        if get_all_memory_usage() > 50:
            for elem in listOfRunningProcess[:20]:
                # print(elem)
                logger.info(elem)
```





```python
import datetime as dt
from datetime import timedelta

print(dt.datetime(year=2022, month=12, day=2, hour=18, minute=0, second=0, microsecond=0) - timedelta(hours=8))
```



## 視化神器Highcharts

```python
from highcharts import Highchart
import datetime
from IPython.display import HTML, display
import yfinance as yf
import os

# 取得股價歷史資料(含臺股\美股\加密貨幣)

symbol = "2330.TW"  # 臺股上市:TW 臺股上櫃:TWO
start = "2018-01-01"  # 起始時間
end = "2022-12-31"  # 結束時間

ohlcv = yf.Ticker(symbol).history("max").loc[start:end]


# 客製化調整參數
color = "#4285f4"  # 線的顏色 (red/green/blue/purple)
linewidth = 2  # 線的粗細
title = symbol  # 標題名稱
width = 800  # 圖的寬度
height = 500  # 圖的高度

# 繪圖設定
H = Highchart(width=width, height=height)

x = ohlcv.index
y = round(ohlcv.Close, 2)

data = [[index, s] for index, s in zip(x, y)]
H.add_data_set(data, "line", "data", color=color)

H.set_options("xAxis", {"type": "datetime"})
H.set_options("title", {"text": title, "style": {"color": "black"}})  # 設定title
H.set_options(
    "plotOptions", {"line": {"lineWidth": linewidth, "dataLabels": {"enabled": False}}}
)  # 設定線的粗度
H.set_options("tooltip", {"shared": True, "crosshairs": True})  # 設定為可互動式

# 顯示圖表
H.save_file("chart")
display(HTML("chart.html"))
os.remove("chart.html")
```





## Test Redis 

```python
import redis

botID = 101
r = redis.StrictRedis(host="localhost", port=6379, db=2)

r.hset(
    f"BOT_INFO:{botID}", mapping={"grid_step": "50"},
)

fee = 0.1
r.hset(
    f"BOT_INFO:{botID}", mapping={"spotman_grid_fee": str(fee)},
)

print(r.exists("BOT_INFO:28"))
if not r.hexists(f"BOT_INFO:{botID}", "spotman_grid_fee") or (
    r.hexists(f"BOT_INFO:{botID}", "spotman_grid_fee")
    and float(r.hget(f"BOT_INFO:{botID}", "spotman_grid_fee")) == 0.0
):
    spotman_grid_fee = 0.0
else:
    spotman_grid_fee = fee

print(spotman_grid_fee)

# r.set("foo", "bar")
## print(r.get('foo'))
#
# botID = 28
# r.hset(
#    f"BOT_INFO:{botID}", mapping={"spotman_grid_fee": 0},
# )
#
# spotman_grid_fee = float(r.hget(f"BOT_INFO:{botID}", "spotman_grid_fee"))yy
# print(spotman_grid_fee == 0.0)
#
# print(r.hexists(f"BOT_INFO:{botID}", "spotman_grid_fee"))
# print(r.hget(f"BOT_INFO:{botID}", "grid_step"))


# if r.hexists(
#    f"BOT_INFO:{botID}", "bot_id"
# ):

# botID = 6804
# r = redis.StrictRedis(
#    host="staging-redis-trading.ruv0v5.ng.0001.apne1.cache.amazonaws.com",
#    port=6379,
#    db=1,
# )
# print(r.hget(f"BOT_INFO:{botID}", "grid_step"))
# print(not r.hexists(f"BOT_INFO:{botID}", "spotman_grid_fee"))
```





## [Python爬蟲教學]有效利用Python網頁爬蟲爬取免費的Proxy IP清單

```python
import requests
import re


def get_proxy():
    # https://www.learncodewithmike.com/2021/10/python-scrape-free-proxy-ip.html?m=1
    response = requests.get("https://www.sslproxies.org/")
    proxy_ips = re.findall("\d+\.\d+\.\d+\.\d+:\d+", response.text)  # 「\d+」代表數字一個位數以上
    valid_ips = []

    for ip in proxy_ips:
        try:
            result = requests.get(
                "https://ip.seeip.org/jsonip?",
                proxies={"http": ip, "https": ip},
                timeout=5,
            )
            print(result.json())
            valid_ips.append(ip)
        except:
            print(f"{ip} invalid")

    with open("proxy_list.txt", "w") as file:
        for ip in valid_ips:
            file.write(ip + "\n")
        file.close()


if __name__ == "__main__":
    # get_proxy()
    proxy_dict = {}
    with open("./proxy_list.txt") as f:
        proxy_list = f.read().splitlines()
        # print(proxy_list, type(proxy_list))
    """代理IP地址（高匿）"""
    #proxys = {
    #    "http": "http://118.27.113.167:8080",
    #    "https": "https://118.27.113.167:8080",
    #}
    """head 資訊"""
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Connection": "keep-alive",
    }
    """http://icanhazip.com會返回當前的IP地址"""
    for proxy in proxy_list:
        proxy_dict["http"] = "http://" + proxy
        proxy_dict["https"] = "https://" + proxy
        try:
            p = requests.get("http://icanhazip.com", headers=head, proxies=proxy_dict, timeout=5)
            print(p.text)
        except Exception as e:
            print(e)
            continue
```



##  同學,你的多線程可別再亂 join 了!

如果你在網上搜索「Python 多線程」，那麼你會看到很多文章裡面用到了一個關鍵詞，叫做.join()。但是很多人的代碼裡面都在亂用 join()，例如：

```python
import time
import threading

def sleep_5_seconds():
    time.sleep(5)
    print('睡眠5秒結束')

def sleep_3_seconds():
    time.sleep(3)
    print('睡眠3秒結束')



def sleep_8_seconds():
    time.sleep(8)
    print('睡眠8秒結束')


thread_1 = threading.Thread(target=sleep_8_seconds)
thread_2 = threading.Thread(target=sleep_5_seconds)
thread_3 = threading.Thread(target=sleep_5_seconds)
thread_1.start()
thread_2.start()
thread_3.start()
thread_1.join()
thread_2.join()
thread_3.join()


```

運行效果如下圖所示：

更有甚者，這樣寫代碼：

thread_1.start()
thread_1.join()
thread_2.start()
thread_2.join()
thread_3.start()
thread_3.join()



運行效果如下圖所示：

發現三個線程是串行執行的，要運行一共8+5+3=16秒才能結束，於是得出結論——Python 由於有 GIL 鎖的原因，所以多線程是一個線程運行完才運行另一個線程。

抱有這種想法的人，是根本不知道.join()有什麼用，就在跟著別人亂用，以為只要使用多線程，那麼每個線程都必須要 join。

實際上，根本不是這樣的，你只需要 join運行時間最長的那個線程就可以了：

你會發現這樣的運行效果，跟每個線程 join 一次是完全一樣的。

要理解這個問題，我們需要知道，join 有什麼作用。

當我們沒有 join 的時候，我們會發現子線程似乎也能正常運行，如下圖所示：

三個子線程啟動以後，主線程會繼續運行後面的代碼。

那 join 到底有什麼用呢？join 會卡住主線程，並讓當前已經 start 的子線程繼續運行，直到調用.join的這個線程運行完畢。

所以，如果代碼寫為：

thread_1.start()
thread_1.join()
thread_2.start()
thread_2.join()
thread_3.start()
thread_3.join()



當代碼運行到thread_1.join()時，主線程就卡住了，後面的thread_2.start()根本沒有執行。此時當前只有 thread_1執行過.start()方法，所以此時只有 thread_1再運行。這個線程需要執行8秒鐘。等8秒過後，thread_1結束，於是主線程才會運行到thread_2.start()，第二個線程才會開始運行。所以這個例子裡面，三個線程串行運行，完全是寫代碼的人有問題，而不是什麼 GIL 鎖的問題。

而當我們把代碼寫為：

thread_1.start()
thread_2.start()
thread_3.start()
thread_1.join()
thread_2.join()
thread_3.join()



當代碼執行到thread_1.join()時，當前三個子線程均已經執行過.start()方法了，所以此時主線程雖然卡住了，但是三個子線程會繼續運行。其中線程3先結束，然後線程2結束。此時線程1還剩3秒鐘，所以此時thread_1.join()依然是卡住的狀態，直到線程1結束，thread_1.join()解除阻塞，代碼運行到thread_2.join()中，但由於thread_2早就結束了，所以這行代碼一閃而過，不會卡住。同理，thread_3.join()也是一閃而過。所以整個過程中，thread_2.join()和thread_3.join()根本沒有起到任何作用。直接就結束了。

所以，你只需要 join 時間最長的這個線程就可以了。時間短的線程沒有 join 的必要。根本不需要把這麼多個 join 堆在一起。

為什麼會有 join 這個功能呢？我們設想這樣一個場景。你的爬蟲使用10個線程爬取100個 URL，主線程需要等到所有URL 都已經爬取完成以後，再來分析數據。此時就可以通過 join 先把主線程卡住，等到10個子線程全部運行結束了，再用主線程進行後面的操作。

那麼可能有人會問，如果我不知道哪個線程先運行完，那個線程後運行完怎麼辦？這個時候是不是就要每個線程都執行 join 操作了呢？

確實，這種情況下，每個線程使用 join是合理的：

```python
thread_list = []
for _ in range(10):
    thread = threading.Thread(target=xxx, args=(xxx, xxx)) 換行thread.start()
    thread_list.append(thread)

for thread in thread_list:
    thread.join()
```



## 監控指定Process狀態



```py
import threading, logging, time
import multiprocessing
import psutil


class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            # print("Producer is working...")
            time.sleep(1)


class Consumer(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            print("Consumer is working...")
            time.sleep(10)
            try:
                a = 1 / 0
            except Exception as ex:
                print(ex)
                continue


class Monitor(multiprocessing.Process):
    def __init__(self, target_pid):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        self.target_pid = target_pid

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            p = psutil.Process(self.target_pid)
            print("Monitor is working...", self.target_pid, p.status)
            time.sleep(1)


def main():
    tasks = [Producer(), Consumer()]

    for t in tasks:
        t.start()

    print(tasks[1].pid)
    t = Monitor(tasks[1].pid)
    t.start()
    time.sleep(3600)

    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s",
        level=logging.INFO,
    )
    main()
```







##  檔案拆成1.5G 一個資料夾

```py
#!/bin/env python3

from pathlib import Path
import os
import shutil

number = 0
current_size = 0
pattern = "new-folder-%03d"

new_directory = pattern % number
Path(pattern % number).mkdir(parents=True, exist_ok=True)

# 預設抓 /path/picture/* 該目錄內檔案，若是要包含子目錄，請使用像是 rglob('*.jpg') 替代
for item in Path("Camera").rglob("*"):
    current_size += item.stat().st_size
    if current_size >= 1024 * 1024 * 1500:
        number += 1
        current_size = 0
        new_directory = pattern % number
        Path(new_directory).mkdir(parents=True, exist_ok=True)
    shutil.move(
        os.path.join(item.parent, item.name), os.path.join(new_directory, item.name)
    )
```

## 刪除指定日期之前的Row 

```python
import pandas as pd

csiti = 23454
units = list(range(0, 400))
begin_date = '2019-10-16'

df = pd.DataFrame({'csiti':csiti, 
                   'units':units,
                   'forecast_date':pd.date_range(begin_date, periods=len(units), freq='1S')})


df.set_index("forecast_date", inplace=True)


df.index = pd.to_datetime(df.index)
print(df)

res = df[~(df.index < '2019-10-16 00:06')]
print(id(res))
# print(res, type(res.index.tolist()[-1]))


# Insert row to dataframe
res.loc[res.index.tolist()[-1]] = [12345, 362]
print(res)
print(id(res))

# Check if a date index exist in Pandas dataframe
print(pd.to_datetime('2019-10-16 00:06') not in df.index)
print(pd.to_datetime('2019-10-16 00:07') not in df.index)
```



## yfinance

```py
import yfinance as yf

dji_data = yf.download(tickers = "^DJI", interval = "1d", period = "10d")
dji_data['Rets'] = round(dji_data['Close'].pct_change() * 100, 2)
print(dji_data)

sox_data = yf.download(tickers="^SOX", interval = "1d", period="10d")
sox_data['Rets'] = round(sox_data['Close'].pct_change() * 100, 2)
print(sox_data)

ixic_data = yf.download(tickers="^IXIC", interval = "1d", period="10d")
ixic_data['Rets'] = round(ixic_data['Close'].pct_change() * 100, 2)
print(ixic_data)
```



## plotly  畫K bars

```python
# Raw Package
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr

# Market Data 
import yfinance as yf

#Graphing/Visualization
import datetime as dt 
import plotly.graph_objs as go 

# Override Yahoo Finance 
yf.pdr_override()

# Create input field for our desired stock 
stock=input("Enter a stock ticker symbol: ")

# Retrieve stock data frame (df) from yfinance API at an interval of 1m 
df = yf.download(tickers=stock,period='1d',interval='1m')

print(df)

# Declare plotly figure (go)
fig=go.Figure()

fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'], name = 'market data'))

fig.update_layout(
    title= str(stock)+' Live Share Price:',
    yaxis_title='Stock Price (USD per Shares)')               

fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=15, label="15m", step="minute", stepmode="backward"),
            dict(count=45, label="45m", step="minute", stepmode="backward"),
            dict(count=1, label="HTD", step="hour", stepmode="todate"),
            dict(count=3, label="3h", step="hour", stepmode="backward"),
            dict(step="all")
        ])
    )
)

fig.show()
```



```python
import asyncio
import aiohttp
import multiprocessing
import threading


async def get_thread_id():
    return (multiprocessing.current_process().pid, threading.get_ident())


def get_exchange_rate(url, exchange_name, conn):
    if exchange_name == "RYBIT":
        asyncio.run(handle_rybit_exchange(url, conn))
    elif exchange_name == "ACE":
        asyncio.run(handle_ace_exchange(url, conn))
    elif exchange_name == "MAX":
        asyncio.run(handle_max_exchange(url, conn))
    elif exchange_name == "BITOPRO":
        asyncio.run(handle_bitopro_exchange(url, conn))
    else:
        print(f"Unknown exchange: {exchange_name}")


async def handle_rybit_exchange(url, conn):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    buy_rate = data.get("data").get("buy_rate")
                    sell_rate = data.get("data").get("sell_rate")
                    process_id, thread_id = await get_thread_id()
                    print(f"RYBIT Process ID:{process_id}, Thread ID:{thread_id}")
                    print("RYBIT 買入匯率:", buy_rate)
                    print("RYBIT 賣出匯率:", sell_rate)
                    conn.send(("RYBIT", buy_rate, sell_rate))
                else:
                    print("RYBIT 發生錯誤，HTTP 狀態碼為:", response.status)
        await asyncio.sleep(1)


async def handle_ace_exchange(url, conn):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    process_id, thread_id = await get_thread_id()
                    print(f"ACE Process ID:{process_id}, Thread ID:{thread_id}")
                    print(f"ACE USDT/TWD 買入委託價格: {data['orderbook']['bids'][0][1]}")
                    print(f"ACE USDT/TWD 賣出委託價格: {data['orderbook']['asks'][0][1]}")
                    conn.send(("ACE", data["orderbook"]["bids"][0][1], data["orderbook"]["asks"][0][1]))
                else:
                    print("ACE 發生錯誤，HTTP 狀態碼為:", response.status)
        await asyncio.sleep(1)


async def handle_max_exchange(url, conn):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    usdt_twd = data.get("usdttwd")
                    buy_price = usdt_twd.get("buy")
                    sell_price = usdt_twd.get("sell")
                    process_id, thread_id = await get_thread_id()
                    print(f"MAX Process ID:{process_id}, Thread ID:{thread_id}")
                    print(f"MAX USDT/TWD buy: {buy_price}")
                    print(f"MAX USDT/TWD sell: {sell_price}")
                    conn.send(("MAX", buy_price, sell_price))
                else:
                    print("MAX 發生錯誤，HTTP 狀態碼為:", response.status)
        await asyncio.sleep(1)


async def handle_bitopro_exchange(url, conn):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    bid_price = data["bids"][0]["price"]
                    ask_price = data["asks"][0]["price"]
                    process_id, thread_id = await get_thread_id()
                    print(f"BITOPRO Process ID:{process_id}, Thread ID:{thread_id}")
                    print(f"BITOPRO 買入委託價格：{bid_price}")
                    print(f"BITOPRO 賣出委託價格：{ask_price}")
                    conn.send(("BITOPRO", bid_price, ask_price))
                else:
                    print("BITOPRO 發生錯誤，HTTP 狀態碼為:", response.status)
        await asyncio.sleep(1)


def collect_exchange_rates(conn):
    exchange_rates = {}
    while True:
        exchange_name, buy_rate, sell_rate = conn.recv()
        exchange_rates[exchange_name] = {"buy": buy_rate, "sell": sell_rate}
        print(f"Exchange rates: {exchange_rates}")

async def main():
    exchanges = [
        {
            "name": "RYBIT",
            "url": "https://www.rybit.com/wallet-api/v1/kgi/exchange-rates/?symbol=USDT_TWD",
        },
        {
            "name": "ACE",
            "url": "https://ace.io/polarisex/oapi/list/orderBooks/USDT/TWD",
        },
        {"name": "MAX", "url": "https://max-api.maicoin.com/api/v2/tickers"},
        {"name": "BITOPRO", "url": "https://api.bitopro.com/v3/order-book/usdt_twd"},
    ]
    parent_conn, child_conn = multiprocessing.Pipe()
    processes = []
    for exchange in exchanges:
        p = multiprocessing.Process(
            target=get_exchange_rate, args=(exchange["url"], exchange["name"], child_conn)
        )
        processes.append(p)
        p.start()

    collector = multiprocessing.Process(target=collect_exchange_rates, args=(parent_conn,))
    collector.start()

    for p in processes:
        p.join()


if __name__ == "__main__":
    asyncio.run(main())
```



## Thread 共用變數

```python
import threading

# 自定義的類別，包含多個共享變數或字段
class SharedData:
    def __init__(self):
        self.variable1 = 0
        self.variable2 = "Hello"
        self.variable3 = []

# 定義一個函數，接受共享數據對象作為參數
def modify_shared_data(shared_data, lock):
    for _ in range(1000000):
        # 獲取鎖
        with lock:
            shared_data.variable1 += 1
            shared_data.variable2 = shared_data.variable2.upper()
            shared_data.variable3.append(shared_data.variable1)
        # 釋放鎖

# 創建一個共享數據對象
shared_data = SharedData()

# 創建一個Lock對象，用於線程同步
lock = threading.Lock()

# 創建兩個線程，將共享數據對象和鎖傳遞給它們的函數
thread1 = threading.Thread(target=modify_shared_data, args=(shared_data, lock))
thread2 = threading.Thread(target=modify_shared_data, args=(shared_data, lock))

# 啟動這兩個線程
thread1.start()
thread2.start()

# 等待這兩個線程完成
thread1.join()
thread2.join()

# 檢查共享數據對象的值
print("共享變數1的值:", shared_data.variable1)
print("共享變數2的值:", shared_data.variable2)
print("共享變數3的值:", shared_data.variable3)

```



## Redis 時間鎖

```python
import threading
import redis
import os
import time


class RedisLock:
    def __init__(self, redis_conn, lock_key, timeout=10):
        self.redis_conn = redis_conn
        self.lock_key = lock_key
        self.timeout = timeout

    def acquire(self):
        start_time = time.time()
        tid = threading.get_ident()  # Fetch the Thread ID (TID)

        while True:
            lock_acquired = self.redis_conn.setnx(self.lock_key, "locked")

            if lock_acquired:
                self.redis_conn.expire(self.lock_key, self.timeout)
                self.pid = os.getpid()  # Fetch the Process ID (PID) during initialization
                self.tid = tid  # Store Thread ID (TID) for printing in release
                print(f"PID:{self.pid} TID:{tid} acquired the lock.")
                return True
            else:
                time.sleep(0.1)

            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                return False

    def release(self):
        tid = self.tid  # Fetch the stored Thread ID (TID) during release
        print(f"PID:{self.pid} TID:{tid} released the lock.")
        self.redis_conn.delete(self.lock_key)

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Could not acquire the lock.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()


def worker(lock, thread_id):
    print(f"Thread-{thread_id} is trying to acquire the lock.")
    with lock:
        print(
            f"Thread-{thread_id} acquired the lock. Performing some critical section operations."
        )
        time.sleep(2)  # Simulating some critical section operations
    print(f"Thread-{thread_id} released the lock.")


# Redis connection setup
redis_conn = redis.StrictRedis(host="localhost", port=6379, db=0)
lock_key = "my_lock"
redis_lock = RedisLock(redis_conn, lock_key)

# Creating threads and starting them
thread1 = threading.Thread(target=worker, args=(redis_lock, 1))
thread2 = threading.Thread(target=worker, args=(redis_lock, 2))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
```

```python
import multiprocessing
import redis
import os
import time


class RedisLock:
    def __init__(self, redis_conn, lock_key, timeout=10):
        self.redis_conn = redis_conn
        self.lock_key = lock_key
        self.timeout = timeout

    def acquire(self):
        start_time = time.time()
        while True:
            lock_acquired = self.redis_conn.set(
                self.lock_key, "locked", ex=self.timeout, nx=True
            )
            if lock_acquired:
                self.pid = os.getpid()  # 取得初始化時的 Process ID (PID)
                print(f"PID:{self.pid} acquired the lock.")
                return True
            else:
                time.sleep(0.1)
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                return False

    def release(self):
        print(f"PID:{self.pid} released the lock.")
        self.redis_conn.delete(self.lock_key)

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Could not acquire the lock.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()


def worker(lock, process_id):
    print(f"Process-{process_id} is trying to acquire the lock.")
    with lock:
        print(
            f"Process-{process_id} acquired the lock. Performing some critical section operations."
        )
        time.sleep(2)  # 模擬一些關鍵區段操作
    print(f"Process-{process_id} released the lock.")


# Redis 連線設定
redis_conn = redis.StrictRedis(host="localhost", port=6379, db=0)
lock_key = "my_lock"
redis_lock = RedisLock(redis_conn, lock_key)

# 創建並啟動進程
process1 = multiprocessing.Process(target=worker, args=(redis_lock, 1))
process2 = multiprocessing.Process(target=worker, args=(redis_lock, 2))

process1.start()
process2.start()

process1.join()
process2.join()
```



## 透過Queue 監控 thread 重啟

```python
import threading
import time
import inspect
import ctypes

import threading
import time
import queue
import random


class WorkerThread(threading.Thread):
    def __init__(self, msg_queue, thread_no):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.thread_no = thread_no

    def run(self):
        print("Worker thread started, thread no: ", self.thread_no)
        while True:
            self.msg_queue.put("Running")
            sleep_time = random.randint(5, 12)
            print(
                f"Worker thread is running... {threading.get_ident()}, sleeping for {sleep_time} seconds"
            )
            time.sleep(sleep_time)


def restart_thread(worker_thread, status_queue, thread_no):
    print("Worker thread exited. Restarting...")
    worker_thread = WorkerThread(status_queue, thread_no)
    worker_thread.start()
    return worker_thread


def _async_raise(tid, exctype):
    """Raises an exception in the threads with id tid"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(tid), ctypes.py_object(exctype)
    )
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def main():
    thread_no = 0
    status_queue = queue.Queue()
    worker_thread = WorkerThread(status_queue, thread_no)
    worker_thread.start()

    # 主線程監控
    while True:
        try:
            status = status_queue.get(timeout=10)
            print(status)
        except queue.Empty:
            stop_thread(worker_thread)
            thread_no += 1
            worker_thread = restart_thread(worker_thread, status_queue, thread_no)


if __name__ == "__main__":
    main()
```



# 讀取檔案中網址

```python
import re

def extract_urls_from_file(file_path):
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            urls_in_line = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
            urls.extend(urls_in_line)
    return urls

file_path = './bb'  

urls = extract_urls_from_file(file_path)

for url in urls:
    print(url)
```


## 事件驅動event實現

```python
from queue import Queue, Empty
from threading import Thread


class EventManager:
    def __init__(self):
        self._event_queue = Queue()
        self._active = False
        self._thread = Thread(target=self._run)
        self._count = 0
        self._handlers = {}

    def _run(self):
        while self._active:
            try:
                event = self._event_queue.get(block=True, timeout=1)
                self._event_process(event)
            except Empty:
                pass
            self._count += 1

    def _event_process(self, event):
        if event.type_ in self._handlers:
            for handler in self._handlers[event.type_]:
                handler(event)
        self._count += 1

    def start(self):
        self._active = True
        self._thread.start()
        self._count += 1

    def stop(self):
        self._active = False
        self._thread.join()
        self._count += 1

    def add_event_listener(self, type_, handler):
        handler_list = self._handlers.get(type_, [])
        if handler not in handler_list:
            handler_list.append(handler)
            self._handlers[type_] = handler_list
        self._count += 1

    def remove_event_listener(self, type_, handler):
        try:
            handler_list = self._handlers[type_]
            if handler in handler_list:
                handler_list.remove(handler)
                if not handler_list:
                    del self._handlers[type_]
        except KeyError:
            pass
        self._count += 1

    def send_event(self, event):
        self._event_queue.put(event)
        self._count += 1


class Event:
    def __init__(self, type_=None, args_=None):
        self.type_ = type_
        self.args = args_


###############################################################################

# 定義事件類型
EVENT_TURN_START = "Turn_start"
EVENT_BROADCAST = "Broadcast"
EVENT_UPDATE = "Update"
EVENT_DRAW_CARD = "Draw_card"
EVENT_TURN_END = "Turn_end"
EVENT_HEARTBEAT = "Heartbeat"


# 事件處理函數 (玩家)
class Player:
    def __init__(self, id):
        self._id = id

    def turn_start(self, event):
        print(f"{self._id} 回合開始")

    def broadcast(self, event):
        print(f"{self._id} 廣播訊息")

    def update(self, event):
        print(f"{self._id} 更新(場面資料)")

    def draw_card(self, event):
        print(f"{self._id} 玩家抽牌")

    def turn_end(self, event):
        print(f"{self._id} 回合結束")

    def heartbeat(self, event):
        print(f"{self._id} 心跳訊號")


def test():
    player1 = Player("player one")
    event_manager = EventManager()
    event_manager.add_event_listener(EVENT_TURN_START, player1.turn_start)
    event_manager.add_event_listener(EVENT_BROADCAST, player1.broadcast)
    event_manager.add_event_listener(EVENT_UPDATE, player1.update)
    event_manager.add_event_listener(EVENT_DRAW_CARD, player1.draw_card)
    event_manager.add_event_listener(EVENT_TURN_END, player1.turn_end)
    event_manager.add_event_listener(EVENT_HEARTBEAT, player1.heartbeat)
    event_manager.start()

    send = make_sender(event_manager)  # 創建 sender 傳送事件
    send(Event(type_=EVENT_TURN_START))
    send(Event(type_=EVENT_BROADCAST))
    send(Event(type_=EVENT_UPDATE))
    send(Event(type_=EVENT_DRAW_CARD))
    send(Event(type_=EVENT_TURN_END))
    send(Event(type_=EVENT_HEARTBEAT))


def make_sender(event_manager):
    em = event_manager

    def send(event):
        return em.send_event(event)

    return send


if __name__ == "__main__":
    test()
```


```python
import traceback
import faulthandler
import ctypes



def test_segmentation_fault():
    # 對於segmentation fault並不能catch到異常，即此處try沒效果
    try:
        ctypes.string_at(0)
    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    faulthandler.enable()
    test_segmentation_fault()
```





```python
"""
這個設計的主要特點：

使用asyncio實現異步編程，提高效能和並發性。
DataPublisher類實現了發布-訂閱模式，允許多個策略訂閱tick和orderbook數據。
使用asyncio.Queue作為數據緩衝，確保數據接收不會被策略處理阻塞。
每個策略都是獨立的對象，可以獨立處理接收到的數據。
主循環中的asyncio.create_task()確保數據處理在後臺運行，不會阻塞主程序。

這個設計允許高效地接收和處理tick和orderbook數據，同時支持多個策略並發運行。你可以根據實際需求進一步優化和擴展這個框架，例如添加錯誤處理、日誌記錄、性能監控等功能。
"""

import asyncio
from collections import deque
from typing import Dict, List, Callable


class DataPublisher:
    def __init__(self):
        self.tick_subscribers: List[Callable] = []
        self.orderbook_subscribers: List[Callable] = []
        self.tick_queue = asyncio.Queue()
        self.orderbook_queue = asyncio.Queue()

    def subscribe_tick(self, callback: Callable):
        self.tick_subscribers.append(callback)

    def subscribe_orderbook(self, callback: Callable):
        self.orderbook_subscribers.append(callback)

    async def publish_tick(self, tick_data):
        await self.tick_queue.put(tick_data)

    async def publish_orderbook(self, orderbook_data):
        await self.orderbook_queue.put(orderbook_data)

    async def process_tick_queue(self):
        while True:
            tick_data = await self.tick_queue.get()
            for subscriber in self.tick_subscribers:
                await subscriber(tick_data)

    async def process_orderbook_queue(self):
        while True:
            orderbook_data = await self.orderbook_queue.get()
            for subscriber in self.orderbook_subscribers:
                await subscriber(orderbook_data)


class Strategy:
    def __init__(self, name: str):
        self.name = name

    async def on_tick(self, tick_data):
        print(f"Strategy {self.name} received tick: {tick_data}")

    async def on_orderbook(self, orderbook_data):
        print(f"Strategy {self.name} received orderbook: {orderbook_data}")


async def main():
    publisher = DataPublisher()

    # 創建多個策略
    strategies = [Strategy(f"Strategy{i}") for i in range(3)]

    # 訂閱數據
    for strategy in strategies:
        publisher.subscribe_tick(strategy.on_tick)
        publisher.subscribe_orderbook(strategy.on_orderbook)

    # 啟動數據處理任務
    asyncio.create_task(publisher.process_tick_queue())
    asyncio.create_task(publisher.process_orderbook_queue())

    # 模擬接收數據
    for i in range(10):
        await publisher.publish_tick(f"Tick {i}")
        await publisher.publish_orderbook(f"Orderbook {i}")
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
```

## 線程模型：
優勢：
使用線程可以利用多核 CPU 的優勢，在某些情況下提高併發任務的處理速度。
每個線程獨立運行，不會相互影響，因此適合處理獨立的 IO 任務，如 WebSocket 數據處理。
劣勢：
線程開銷較大，尤其是在大量線程的情況下，可能導致上下文切換開銷增大，影響整體性能。
需要處理線程同步和線程安全問題。

```python
import asyncio
import websockets
import os
import json
import threading
import queue
import pandas as pd
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from loguru import logger


def print_pid_tid(tag):
    print(f"{tag} PID: {os.getpid()}, TID: {threading.get_ident()}")


class DataPublisher:
    def __init__(self, tick_queue, orderbook_queue):
        symbol = "btcusdt"
        self.tick_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        self.orderbook_url = f"wss://stream.binance.com:9443/ws/{symbol}@depth20@100ms"
        self.tick_queue = tick_queue
        self.orderbook_queue = orderbook_queue

    def _start_websocket(self, url, queue):
        asyncio.run(self._websocket_handler(url, queue))

    async def _websocket_handler(self, url, queue):
        async with websockets.connect(url) as websocket:
            while True:
                print_pid_tid(url)
                response = await websocket.recv()
                data = json.loads(response)
                # print(f"Received Data: {data}")
                queue.put(data)  # Put data into the queue (no await)

    def start(self):
        # Start tick and order book WebSocket connections in separate threads
        threading.Thread(
            target=self._start_websocket,
            args=(self.tick_url, self.tick_queue),
            daemon=True,
        ).start()
        threading.Thread(
            target=self._start_websocket,
            args=(self.orderbook_url, self.orderbook_queue),
            daemon=True,
        ).start()


class DataProcessor:
    def __init__(self, event_loop, tick_queue, orderbook_queue):
        self.kline_subscribers = []
        self.current_kline = {
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": 0,
            "start_time": None,
        }
        self.kline_df = pd.DataFrame(
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        self.orderbook_history = deque(maxlen=1000)
        self.latest_tick = None
        self.latest_orderbook = None
        self.max_kline_history = 1000  # Limit K-line history to 1000 records
        self.kline_lock = threading.Lock()
        self.tick_data_list = deque(maxlen=5000)  # Collect tick data
        self.executor = ThreadPoolExecutor(max_workers=4)  # Create thread pool
        self.event_loop = event_loop
        self.tick_queue = tick_queue
        self.orderbook_queue = orderbook_queue

    def subscribe_kline(self, callback):
        self.kline_subscribers.append(callback)

    def process_ticks(self):
        while True:
            tick_data = self.tick_queue.get()  # Get tick data from the queue
            print_pid_tid("process_ticks")
            # self.on_tick(tick_data)

    def process_orderbooks(self):
        while True:
            orderbook_data = (
                self.orderbook_queue.get()
            )  # Get orderbook data from the queue
            print_pid_tid("process_orderbooks")
            # self.on_orderbook(orderbook_data)

    def on_tick(self, tick_data):
        print_pid_tid("DataProcessor on_tick")
        self.latest_tick = tick_data
        self.tick_data_list.append(
            {"datetime": tick_data["T"], "close": tick_data["p"]}
        )

        # Use thread pool to process K-line calculation
        future = self.executor.submit(self.update_and_publish_kline)
        future.add_done_callback(self._handle_thread_result)

    def on_orderbook(self, orderbook_data):
        print_pid_tid("DataProcessor on_orderbook")
        self.latest_orderbook = orderbook_data
        self.orderbook_history.append(orderbook_data)

    def update_and_publish_kline(self):
        print_pid_tid("DataProcessor update_and_publish_kline")
        try:
            # Convert tick data to DataFrame
            tick_df = pd.DataFrame(list(self.tick_data_list))
            tick_df.set_index("datetime", inplace=True)
            tick_df.index = pd.to_datetime(tick_df.index, unit="ms")

            now = pd.Timestamp.now(tz="UTC")
            current_minute_start = now.floor("T").to_datetime64()

            # Only process the latest 1 minute of data
            recent_ticks = tick_df.loc[tick_df.index >= current_minute_start]

            # If there is sufficient data, calculate 1-minute K-line data
            if not recent_ticks.empty:
                futures_1min_kbars = recent_ticks["close"].resample("1T").ohlc()

                with self.kline_lock:
                    for timestamp, kline in futures_1min_kbars.iterrows():
                        self.current_kline = {
                            "open": kline["open"],
                            "high": kline["high"],
                            "low": kline["low"],
                            "close": kline["close"],
                            "volume": 0,  # Assume no volume data
                            "start_time": timestamp,
                        }
                        new_kline = pd.DataFrame([self.current_kline])
                        self.kline_df = pd.concat(
                            [self.kline_df, new_kline]
                        ).reset_index(drop=True)

                        # Limit K-line history to the latest 1000 records
                        if len(self.kline_df) > self.max_kline_history:
                            self.kline_df = self.kline_df.iloc[
                                -self.max_kline_history :
                            ]

                        for subscriber in self.kline_subscribers:
                            asyncio.run_coroutine_threadsafe(
                                subscriber(self.current_kline), self.event_loop
                            )

            self.tick_data_list = deque(
                [
                    tick
                    for tick in self.tick_data_list
                    if pd.to_datetime(tick["datetime"], unit="ms").to_datetime64()
                    >= current_minute_start
                ]
            )

        except Exception as e:
            logger.error(f"Error in update_and_publish_kline: {e}")

    def _handle_thread_result(self, future):
        try:
            future.result()
        except Exception as e:
            logger.error(f"Thread processing error: {e}")

    def get_latest_data(self):
        with self.kline_lock:
            return {
                "latest_tick": self.latest_tick,
                "latest_kline": (
                    self.kline_df.iloc[-1] if not self.kline_df.empty else None
                ),
                "kline_history": self.kline_df,
                "latest_orderbook": self.latest_orderbook,
                "orderbook_history": list(self.orderbook_history),
            }


async def main():
    tick_queue = queue.Queue()
    orderbook_queue = queue.Queue()
    event_loop = asyncio.get_event_loop()

    data_processor = DataProcessor(event_loop, tick_queue, orderbook_queue)
    data_publisher = DataPublisher(tick_queue, orderbook_queue)
    data_publisher.start()  # Start DataPublisher in a separate thread

    loop = asyncio.get_event_loop()

    # Process both ticks and order books in separate threads
    threading.Thread(target=data_processor.process_ticks, daemon=True).start()
    threading.Thread(target=data_processor.process_orderbooks, daemon=True).start()

    while True:
        data = data_processor.get_latest_data()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
```

## asyncio.gather 異步模型
優勢：
異步模型的開銷較低，沒有線程切換的開銷，適合大量 IO 密集型任務。
在單線程內管理所有任務，簡化了同步和資源管理。
異步任務之間可以更高效地共享 CPU 資源，避免了不必要的等待時間。
劣勢：
異步模型依賴事件循環，無法充分利用多核 CPU。對於 CPU 密集型任務，性能不如多線程模型。
在處理非常高的併發情況下，如果單線程成為瓶頸，可能導致性能下降。

```python
import asyncio
import websockets
import os
import json
import threading
import queue
import pandas as pd
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from loguru import logger


def print_pid_tid(tag):
    print(f"{tag} PID: {os.getpid()}, TID: {threading.get_ident()}")


class DataPublisher:
    def __init__(self, tick_queue, orderbook_queue):
        symbol = "btcusdt"
        self.tick_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        self.orderbook_url = f"wss://stream.binance.com:9443/ws/{symbol}@depth20@100ms"
        self.tick_queue = tick_queue
        self.orderbook_queue = orderbook_queue

    def _start_websocket(self, url, queue):
        asyncio.run(self._websocket_handler(url, queue))

    async def _websocket_handler(self, url, queue):
        async with websockets.connect(url) as websocket:
            while True:
                print_pid_tid(url)
                response = await websocket.recv()
                data = json.loads(response)
                # print(f"Received Data: {data}")
                queue.put(data)  # Put data into the queue (no await)

    def start(self):
        # Start tick and order book WebSocket connections in separate threads
        threading.Thread(
            target=self._start_websocket,
            args=(self.tick_url, self.tick_queue),
            daemon=True,
        ).start()
        threading.Thread(
            target=self._start_websocket,
            args=(self.orderbook_url, self.orderbook_queue),
            daemon=True,
        ).start()


class DataProcessor:
    def __init__(self, event_loop, tick_queue, orderbook_queue):
        self.kline_subscribers = []
        self.current_kline = {
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": 0,
            "start_time": None,
        }
        self.kline_df = pd.DataFrame(
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        self.orderbook_history = deque(maxlen=1000)
        self.latest_tick = None
        self.latest_orderbook = None
        self.max_kline_history = 1000  # Limit K-line history to 1000 records
        self.kline_lock = threading.Lock()
        self.tick_data_list = deque(maxlen=5000)  # Collect tick data
        self.executor = ThreadPoolExecutor(max_workers=4)  # Create thread pool
        self.event_loop = event_loop
        self.tick_queue = tick_queue
        self.orderbook_queue = orderbook_queue

    def subscribe_kline(self, callback):
        self.kline_subscribers.append(callback)

    def process_ticks(self):
        while True:
            tick_data = self.tick_queue.get()  # Get tick data from the queue
            print_pid_tid("process_ticks")
            # self.on_tick(tick_data)

    def process_orderbooks(self):
        while True:
            orderbook_data = (
                self.orderbook_queue.get()
            )  # Get orderbook data from the queue
            print_pid_tid("process_orderbooks")
            # self.on_orderbook(orderbook_data)

    def on_tick(self, tick_data):
        print_pid_tid("DataProcessor on_tick")
        self.latest_tick = tick_data
        self.tick_data_list.append(
            {"datetime": tick_data["T"], "close": tick_data["p"]}
        )

        # Use thread pool to process K-line calculation
        future = self.executor.submit(self.update_and_publish_kline)
        future.add_done_callback(self._handle_thread_result)

    def on_orderbook(self, orderbook_data):
        print_pid_tid("DataProcessor on_orderbook")
        self.latest_orderbook = orderbook_data
        self.orderbook_history.append(orderbook_data)

    def update_and_publish_kline(self):
        print_pid_tid("DataProcessor update_and_publish_kline")
        try:
            # Convert tick data to DataFrame
            tick_df = pd.DataFrame(list(self.tick_data_list))
            tick_df.set_index("datetime", inplace=True)
            tick_df.index = pd.to_datetime(tick_df.index, unit="ms")

            now = pd.Timestamp.now(tz="UTC")
            current_minute_start = now.floor("T").to_datetime64()

            # Only process the latest 1 minute of data
            recent_ticks = tick_df.loc[tick_df.index >= current_minute_start]

            # If there is sufficient data, calculate 1-minute K-line data
            if not recent_ticks.empty:
                futures_1min_kbars = recent_ticks["close"].resample("1T").ohlc()

                with self.kline_lock:
                    for timestamp, kline in futures_1min_kbars.iterrows():
                        self.current_kline = {
                            "open": kline["open"],
                            "high": kline["high"],
                            "low": kline["low"],
                            "close": kline["close"],
                            "volume": 0,  # Assume no volume data
                            "start_time": timestamp,
                        }
                        new_kline = pd.DataFrame([self.current_kline])
                        self.kline_df = pd.concat(
                            [self.kline_df, new_kline]
                        ).reset_index(drop=True)

                        # Limit K-line history to the latest 1000 records
                        if len(self.kline_df) > self.max_kline_history:
                            self.kline_df = self.kline_df.iloc[
                                -self.max_kline_history :
                            ]

                        for subscriber in self.kline_subscribers:
                            asyncio.run_coroutine_threadsafe(
                                subscriber(self.current_kline), self.event_loop
                            )

            self.tick_data_list = deque(
                [
                    tick
                    for tick in self.tick_data_list
                    if pd.to_datetime(tick["datetime"], unit="ms").to_datetime64()
                    >= current_minute_start
                ]
            )

        except Exception as e:
            logger.error(f"Error in update_and_publish_kline: {e}")

    def _handle_thread_result(self, future):
        try:
            future.result()
        except Exception as e:
            logger.error(f"Thread processing error: {e}")

    def get_latest_data(self):
        with self.kline_lock:
            return {
                "latest_tick": self.latest_tick,
                "latest_kline": (
                    self.kline_df.iloc[-1] if not self.kline_df.empty else None
                ),
                "kline_history": self.kline_df,
                "latest_orderbook": self.latest_orderbook,
                "orderbook_history": list(self.orderbook_history),
            }


async def main():
    tick_queue = queue.Queue()
    orderbook_queue = queue.Queue()
    event_loop = asyncio.get_event_loop()

    data_processor = DataProcessor(event_loop, tick_queue, orderbook_queue)
    data_publisher = DataPublisher(tick_queue, orderbook_queue)
    data_publisher.start()  # Start DataPublisher in a separate thread

    loop = asyncio.get_event_loop()

    # Process both ticks and order books in separate threads
    threading.Thread(target=data_processor.process_ticks, daemon=True).start()
    threading.Thread(target=data_processor.process_orderbooks, daemon=True).start()

    while True:
        data = data_processor.get_latest_data()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

```

```python
import asyncio
import websockets
import os
import json
import threading
import queue
import pandas as pd
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from loguru import logger


def print_pid_tid(tag):
    print(f"{tag} PID: {os.getpid()}, TID: {threading.get_ident()}")


class DataPublisher:
    def __init__(self, tick_queue, orderbook_queue):
        symbol = "btcusdt"
        self.tick_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        self.orderbook_url = f"wss://stream.binance.com:9443/ws/{symbol}@depth20@100ms"
        self.tick_queue = tick_queue
        self.orderbook_queue = orderbook_queue

    async def _websocket_handler(self, url, queue):
        async with websockets.connect(url) as websocket:
            while True:
                print_pid_tid(url)
                response = await websocket.recv()
                data = json.loads(response)
                queue.put(data)  # Put data into the queue (no await)

    async def start(self):
        await asyncio.gather(
            self._websocket_handler(self.tick_url, self.tick_queue),
            self._websocket_handler(self.orderbook_url, self.orderbook_queue),
        )


class DataProcessor:
    def __init__(self, event_loop, tick_queue, orderbook_queue):
        self.kline_subscribers = []
        self.current_kline = {
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": 0,
            "start_time": None,
        }
        self.kline_df = pd.DataFrame(
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        self.orderbook_history = deque(maxlen=1000)
        self.latest_tick = None
        self.latest_orderbook = None
        self.max_kline_history = 1000  # Limit K-line history to 1000 records
        self.kline_lock = threading.Lock()
        self.tick_data_list = deque(maxlen=5000)  # Collect tick data
        self.executor = ThreadPoolExecutor(max_workers=4)  # Create thread pool
        self.event_loop = event_loop
        self.tick_queue = tick_queue
        self.orderbook_queue = orderbook_queue

    def subscribe_kline(self, callback):
        self.kline_subscribers.append(callback)

    def process_ticks(self):
        while True:
            tick_data = self.tick_queue.get()  # Get tick data from the queue
            print_pid_tid("process_ticks")
            # self.on_tick(tick_data)

    def process_orderbooks(self):
        while True:
            orderbook_data = (
                self.orderbook_queue.get()
            )  # Get orderbook data from the queue
            print_pid_tid("process_orderbooks")
            # self.on_orderbook(orderbook_data)

    def on_tick(self, tick_data):
        print_pid_tid("DataProcessor on_tick")
        self.latest_tick = tick_data
        self.tick_data_list.append(
            {"datetime": tick_data["T"], "close": tick_data["p"]}
        )

        # Use thread pool to process K-line calculation
        future = self.executor.submit(self.update_and_publish_kline)
        future.add_done_callback(self._handle_thread_result)

    def on_orderbook(self, orderbook_data):
        print_pid_tid("DataProcessor on_orderbook")
        self.latest_orderbook = orderbook_data
        self.orderbook_history.append(orderbook_data)

    def update_and_publish_kline(self):
        print_pid_tid("DataProcessor update_and_publish_kline")
        try:
            # Convert tick data to DataFrame
            tick_df = pd.DataFrame(list(self.tick_data_list))
            tick_df.set_index("datetime", inplace=True)
            tick_df.index = pd.to_datetime(tick_df.index, unit="ms")

            now = pd.Timestamp.now(tz="UTC")
            current_minute_start = now.floor("T").to_datetime64()

            # Only process the latest 1 minute of data
            recent_ticks = tick_df.loc[tick_df.index >= current_minute_start]

            # If there is sufficient data, calculate 1-minute K-line data
            if not recent_ticks.empty:
                futures_1min_kbars = recent_ticks["close"].resample("1T").ohlc()

                with self.kline_lock:
                    for timestamp, kline in futures_1min_kbars.iterrows():
                        self.current_kline = {
                            "open": kline["open"],
                            "high": kline["high"],
                            "low": kline["low"],
                            "close": kline["close"],
                            "volume": 0,  # Assume no volume data
                            "start_time": timestamp,
                        }
                        new_kline = pd.DataFrame([self.current_kline])
                        self.kline_df = pd.concat(
                            [self.kline_df, new_kline]
                        ).reset_index(drop=True)

                        # Limit K-line history to the latest 1000 records
                        if len(self.kline_df) > self.max_kline_history:
                            self.kline_df = self.kline_df.iloc[
                                -self.max_kline_history :
                            ]

                        for subscriber in self.kline_subscribers:
                            asyncio.run_coroutine_threadsafe(
                                subscriber(self.current_kline), self.event_loop
                            )

            self.tick_data_list = deque(
                [
                    tick
                    for tick in self.tick_data_list
                    if pd.to_datetime(tick["datetime"], unit="ms").to_datetime64()
                    >= current_minute_start
                ]
            )

        except Exception as e:
            logger.error(f"Error in update_and_publish_kline: {e}")

    def _handle_thread_result(self, future):
        try:
            future.result()
        except Exception as e:
            logger.error(f"Thread processing error: {e}")

    def get_latest_data(self):
        with self.kline_lock:
            return {
                "latest_tick": self.latest_tick,
                "latest_kline": (
                    self.kline_df.iloc[-1] if not self.kline_df.empty else None
                ),
                "kline_history": self.kline_df,
                "latest_orderbook": self.latest_orderbook,
                "orderbook_history": list(self.orderbook_history),
            }


async def main():
    tick_queue = queue.Queue()
    orderbook_queue = queue.Queue()
    event_loop = asyncio.get_event_loop()

    data_processor = DataProcessor(event_loop, tick_queue, orderbook_queue)
    data_publisher = DataPublisher(tick_queue, orderbook_queue)

    # 使用 asyncio.run_coroutine_threadsafe 啟動數據發佈器
    threading.Thread(
        target=lambda: asyncio.run_coroutine_threadsafe(
            data_publisher.start(), event_loop
        ),
        daemon=True,
    ).start()

    # Process both ticks and order books in separate threads
    threading.Thread(target=data_processor.process_ticks, daemon=True).start()
    threading.Thread(target=data_processor.process_orderbooks, daemon=True).start()

    while True:
        data = data_processor.get_latest_data()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

```

## 使用 Multiprocessing Pool 和 Thread 的範例

```python
import multiprocessing
import threading
import time


def generate_data(data, num_elements=10):
    for i in range(num_elements):
        data.append(i)
        time.sleep(0.5)  # 模擬生成數據的延遲


def square(x):
    print(
        f"square PID: {multiprocessing.current_process().pid}, TID: {threading.current_thread().ident}"
    )
    return x * x


def main():
    data = []
    num_elements = 10

    # 創建一個線程來生成數據
    data_thread = threading.Thread(target=generate_data, args=(data, num_elements))
    data_thread.start()

    # 創建一個進程池
    pool = multiprocessing.Pool()

    # 獲取進程池中各個進程的 PID
    pool_pids = [p.pid for p in pool._pool]
    print(f"Pool PIDs: {pool_pids}")

    while True:
        print(
            f"main PID: {multiprocessing.current_process().pid}, TID: {threading.current_thread().ident}"
        )
        # 如果數據生成完成，退出循環
        if len(data) == num_elements:
            break
        # 當前數據量
        current_data = data[:]
        # 使用 pool.map 計算當前數據
        if current_data:
            results = pool.map(square, current_data)
            print(f"Current data: {current_data}, Squared results: {results}")
        time.sleep(1)  # 等待一段時間以便數據生成

    # 等待數據生成線程結束
    data_thread.join()

    # 處理最終數據
    results = pool.map(square, data)
    print(f"Final data: {data}, Final squared results: {results}")

    # 關閉進程池
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()

```


## Numba 可以用於加速一些涉及 DataFrame 的操作 

```python
import pandas as pd
import numpy as np
from numba import njit

# 创建一个示例 DataFrame
df = pd.DataFrame({
    'A': np.random.rand(1000),
    'B': np.random.rand(1000)
})

@njit
def calculate_sum(A, B):
    result = np.empty(A.shape[0])
    for i in range(A.shape[0]):
        result[i] = A[i] + B[i]
    return result

# 将 DataFrame 转换为 NumPy 数组
A = df['A'].values
B = df['B'].values

# 使用 Numba 加速计算
df['C'] = calculate_sum(A, B)

print(df.head())
```

## 指定 CPU 跑在特定核心上運行 

```python
import os
import psutil

# 取得當前進程的 PID
pid = os.getpid()
p = psutil.Process(pid)

# 設置程序只運行在 CPU 核心 1（第二核）
p.cpu_affinity([1])

# 驗證當前的 CPU 親和性設定
print(f"CPU 親和性設定為: {p.cpu_affinity()}")

# 模擬負載，觀察運行情況
while True:
    pass  # 佔用 CPU，方便觀察


```



## talib  pandas_ta

```python
import pandas as pd
import talib
import pandas_ta as ta

# 模擬較多的 K 線數據
data = {
    "high": [130, 132, 131, 133, 135, 136, 138, 140, 142, 145, 147, 149, 151, 153, 155],
    "low": [125, 126, 128, 130, 132, 133, 134, 137, 139, 141, 143, 145, 146, 148, 150],
    "close": [
        128,
        129,
        130,
        132,
        134,
        135,
        137,
        139,
        141,
        143,
        145,
        147,
        149,
        151,
        153,
    ],
}

df = pd.DataFrame(data)

# 設定 ATR 長度
atr_len = 5

# 使用 talib 計算 TR 和 ATR
df["TR_talib"] = talib.TRANGE(df["high"], df["low"], df["close"])
df["ATR_talib"] = talib.EMA(df["TR_talib"], timeperiod=atr_len)

# 使用 pandas_ta 計算 TR 和 ATR
df["ATR_pandas_ta"] = ta.atr(df["high"], df["low"], df["close"], length=1)
df["ATR_pandas_ta_ema"] = ta.ema(df["ATR_pandas_ta"], length=atr_len)

# 輸出結果
print("DataFrame 結果：")
print(df)
```

---

## 富邦 API  FubonSDK

```sh
docker pull python:3.10-slim
docker run -it --name my_python_env python:3.10-slim bash
apt update && apt install -y vim unzip wget

wget https://www.fbs.com.tw/TradeAPI_SDK/fubon_binary/fubon_neo-1.3.2-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.zip
unzip fubon_neo-1.3.2-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.zip
pip install fubon_neo-1.3.2-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
pip install requests
```

```python
from fubon_neo.sdk import FubonSDK
sdk = FubonSDK() 
```

```sh
python -m venv myenv
source myenv/bin/activate
pip install fubon_neo-1.3.2-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

---
## Python 工作時間監控與自動進程重啟系統

```python
import threading
import time
import datetime
import os
import sys
import logging
import ctypes
import subprocess

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [PID:%(process)d][TID:%(thread)d] - %(message)s",
)
logger = logging.getLogger(__name__)


def get_thread_id():
    """獲取當前線程ID"""
    if hasattr(threading, "get_native_id"):  # Python 3.8+
        return threading.get_native_id()
    elif sys.platform == "win32":
        return ctypes.windll.kernel32.GetCurrentThreadId()
    else:
        # Linux/Unix系統通過調用syscall獲取
        try:
            import ctypes

            libc = ctypes.cdll.LoadLibrary("libc.so.6")
            return libc.syscall(186)  # SYS_gettid
        except:
            return os.getpid()  # 備用方案


def is_work_time():
    """檢查當前是否在工作時間內（星期一到星期五，8:20-13:31）"""
    now = datetime.datetime.now()
    # 獲取星期幾 (0=星期一, 6=星期日)
    weekday = now.weekday()

    # 檢查是否為工作日（星期一到星期五）
    if weekday >= 5:  # 星期六或星期日
        return False

    # 獲取當前時間
    current_time = now.time()
    work_start = datetime.time(8, 20)
    work_end = datetime.time(13, 31)

    # 檢查是否在工作時間內
    return work_start <= current_time <= work_end


def restart_program():
    """重新啟動當前程式（保留相同的PID）"""
    logger.info(f"重新啟動程式 (PID: {os.getpid()} 將保持不變)")
    python = sys.executable
    os.execl(python, python, *sys.argv)


def restart_with_new_pid():
    """用新的 PID 重啟程序"""
    logger.info(f"用新 PID 重啟程序 (當前 PID: {os.getpid()})")
    python = sys.executable
    subprocess.Popen([python] + sys.argv)
    sys.exit(0)  # 終止當前進程


def monitoring_thread(use_new_pid=False):
    """監控時間並在非工作時間重啟程式"""
    tid = get_thread_id()
    logger.info(f"時間監控線程已啟動 (TID: {tid})")

    while True:
        if not is_work_time():
            logger.info(f"當前時間不在工作時間範圍內 (TID: {tid})")
            time.sleep(5)  # 延遲5秒後重啟

            if use_new_pid:
                restart_with_new_pid()  # 使用新的PID重啟
            else:
                restart_program()  # 使用原有PID重啟

        # 每分鐘檢查一次
        time.sleep(60)


def main():
    """主程式"""
    pid = os.getpid()
    tid = get_thread_id()
    logger.info(f"\n\n程式啟動 (PID: {pid}, 主線程 TID: {tid})")

    # 決定是否使用新PID重啟
    use_new_pid = True  # 設為True可以使用新PID重啟

    # 啟動監控線程
    monitor = threading.Thread(
        target=monitoring_thread, args=(use_new_pid,), daemon=True
    )
    monitor.start()
    logger.info(f"監控線程 ID: {monitor.ident}")

    # 這裡放置您的主要程式邏輯
    try:
        while True:
            # 您的程式主邏輯
            logger.info(f"主程式運行中... (PID: {pid}, TID: {tid})")

            # 添加更多的主程式邏輯...

            time.sleep(300)  # 示例：每5分鐘執行一次某些任務
    except KeyboardInterrupt:
        logger.info(f"程式被使用者中斷 (PID: {pid}, TID: {tid})")
        sys.exit(0)


if __name__ == "__main__":
    main()
```


---
## 使用 multiprocessing 進行 fork 並殺死主行程的範例


```python

import multiprocessing
import os
import time
import sys

def 子行程():
    """子行程要執行的任務"""
    print(f"新行程啟動，行程ID: {os.getpid()}")
    while True:
        print("子行程正在執行...")
        time.sleep(5)

def 主程式():
    # 建立上下文
    ctx = multiprocessing.get_context('fork')
    
    # 建立新行程
    子行程實例 = ctx.Process(target=子行程)
    子行程實例.start()
    
    print(f"主行程ID: {os.getpid()}")
    print(f"新行程ID: {子行程實例.pid}")
    
    # 等待一段時間
    time.sleep(3)
    
    # 嘗試殺死主行程
    try:
        # 在某些系統可能需要管理員權限
        os.kill(os.getpid(), 9)  # 9 對應 SIGKILL
    except Exception as e:
        print(f"殺死行程出錯: {e}")
        sys.exit()

if __name__ == "__main__":
    主程式()
```
