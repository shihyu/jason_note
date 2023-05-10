##  dataframe 成 pickle 後寫入 redis, 之後取出在 unpickle

```python
from finlab import data
import redis
import pickle

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=11)

# Get the data and save it to Redis
營業利益成長率 = data.get("price:收盤價")
r.set('test', pickle.dumps(營業利益成長率))
with open('test.bin', 'wb') as f:
    pickle.dump(營業利益成長率, f)


with open('test.bin', 'rb') as f:
    new_dict = pickle.load(f)
    print(new_dict)

# Read the data from Redis and unpickle it
unpickled_df = pickle.loads(r.get('test'))

print(unpickled_df)

with open('gg.bin', 'wb') as f:
    pickle.dump(pickle.loads(r.get('test')) , f)

with open('gg.bin', 'rb') as f:
    new_dict = pickle.load(f)
    print(new_dict)
```

## 對一個欄位nan 使用 bfill

```python
import pandas as pd
import numpy as np

# 建立範例 DataFrame
df = pd.DataFrame({'A': [1, 2, 3, np.nan, np.nan, 6, np.nan, 8]})

# 針對欄位 A 使用 backfill 填充 NaN 值
df['A'] = df['A'].fillna(method='backfill')

# 印出填充後的 DataFrame
print(df)
```

## 兩個不同大小DF 使用 fillna() 方法使用後向填充法填充缺失值

```python
import pandas as pd

# 創建第一個 dataframe
df1 = pd.DataFrame({'IsTrue': [False]},
                   index=pd.to_datetime(['2023-02-28']))

# 創建第二個 dataframe
df2 = pd.DataFrame({'close': [239.0, 241.0, 247.0, 227.5, 231.0]},
                   index=pd.to_datetime(['2023-02-17', '2023-02-20', '2023-02-21', '2023-02-22', '2023-02-23']))

# 將第一個 dataframe 轉換為一列 dataframe，然後與第二個 dataframe 進行合併
df = pd.concat([df2, df1], axis=1)  # 使用 pd.concat() 方法將兩個 dataframe 合併
df.fillna(method='bfill', inplace=True)  # 使用 bfill 方法填充缺失值
df.dropna(how="any", inplace=True)  # 使用 dropna 方法刪除仍存在的 NaN 值

print(df)
```



## 的 `concat` 函數將兩個 DataFrame 以 df1 為主，然後指定 `axis=1` 將 df2 以欄位的方式合併至 df1

```python
import pandas as pd

# 創建 True/False 值 DataFrame
df1 = pd.DataFrame({'is_buy': [True, False, True, False]}, 
                   index=pd.to_datetime(['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04']))

# 創建均價 DataFrame（日期為 2022-01-01 和 2022-01-03）
df2 = pd.DataFrame({'mean_price': [100, 300]}, 
                   index=pd.to_datetime(['2022-01-01', '2022-01-03']))

# 將 df1 和 df2 以欄位的方式合併
df_merged = pd.concat([df1, df2.reindex(df1.index)], axis=1)

# 刪除含有 NaN 值的列
df_merged = df_merged.dropna(how='any')

print(df_merged)

```





[資料科學與分析譯文集](https://ds.apachecn.org/#/)



```python
pd.options.display.float_format = lambda x: "%.2f" % x
```



## Python量化交易實戰之使用Resample函數轉換“日K”數據

https://walkonnet.com/archives/138620

使用Resample函數轉換時間序列

##  一、什麼是resample函數？

它是Python數據分析庫Pandas的方法函數。

它主要用於轉換時間序列的頻次。可以做一些統計匯總的工作。

什麼叫轉換時間序列的頻次呢？

比如說股票的日k和周k，

假設我隻能獲取到股票日K的數據，比如說11月1號到11月5號，那怎麼樣將它轉換為以周為單位的K線呢？



| 日期    | 週期 | 開盤價 | 收盤價 | 最高價 | 最低價 |
| ------- | ---- | ------ | ------ | ------ | ------ |
| 11月1號 | 週一 | 1.11   | 1.11   | 1.11   | 1.12   |
| 11月2號 | 週二 | 1.12   | 1.12   | 1.11   | 1.12   |
| 11月3號 | 週三 | 1.13   | 1.13   | 1.11   | 1.12   |
| 11月4號 | 週四 | 1.15   | 1.14   | 1.11   | 1.12   |
| 11月5號 | 週五 | 1.14   | 1.15   | 1.11   | 1.12   |

首先我們要明確，周K的開盤、收盤、最高、最低是什麼。每週的開盤價是當周第一天的開盤價，收盤價是當周最後一天的收盤價，它的最高價是這周最高的價格，最低價是本週所有最低價中最低的價格。所以你去看炒股平臺，它的周k都是以週五的交易日為記錄的時間點位置。開盤、收盤、最高、最低是按照我剛剛講解的這個規則來計算的。至於月K、年K的選取規則也是一樣的。月K的週期是一個月，年K的週期是一年。

這個計算準確性你也可以通過網上的數據進行驗證。這個計算規則，包括開盤、收盤、最高、最低的計算，收拾resample函數可以做到的事情。此外Resample還有個功能，就是做統計匯總，比如說我想計算一支股票總的周成交量，就可以使用Resample.sum函數去把週一到週五的成交量加起來。

為瞭方便大傢記憶 ，你也可以把resample理解為Excel表格中的透視表功能。你可以按照日期做各種篩選和匯總統計的。最重要的是他可以按照日期。

## 二、實戰Resample函數

因為這2節課還是一些比較基礎的部分，所以還沒有做模塊化的內容。

我們會在創建股票數據庫的時候 來做真正的模塊化的工作。到這裡都是初級的腳本的形式。先提前說下。

### 1.日K 轉換為 周K

1.1函數文檔學習

谷歌搜索`Pandas Resample`：第一個鏈接就是這個函數的官方文檔

https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html



這裡有介紹：Resample是屬於Pandas DataFrame下面的方法。這裡有關於參數的解釋。

這裡我們隻對2個常用參數講解，一個是rule，另一個是closed。

- rule表示的是你放一個什麼樣的週期性指標在裡面，用m代表Month，Y代表Year,w代表Week，
- closed代表你取哪一個分界線，舉例來說，比如說我把日k轉換為周k，到底我是取週一為分界線還是週五為分界線呢？這就是通過closed來確定的。

這裡有它的例子：

```python
>>>index = pd.date_range('1/1/2000', periods=9, freq='T')
>>>series = pd.Series(range(9), index=index)
>>>series
2000-01-01 00:00:00    0
2000-01-01 00:01:00    1
2000-01-01 00:02:00    2
2000-01-01 00:03:00    3
2000-01-01 00:04:00    4
2000-01-01 00:05:00    5
2000-01-01 00:06:00    6
2000-01-01 00:07:00    7
2000-01-01 00:08:00    8
Freq: T, dtype: int64
```

這裡首先創建瞭一個時間序列的`DataFrame`，就是這個`series`變量。你可以理解為它是一個隻有一個字段的表格樣式。接著往下看：

```python
>>>series.resample('3T').sum()
2000-01-01 00:00:00     3
2000-01-01 00:03:00    12
2000-01-01 00:06:00    21
Freq: 3T, dtype: int64
```

這裡使用瞭`Resample`方法，`3T`就是3分鐘，`T`表示分鐘。`sum()`就是匯總，也就是針對這一列數據進行匯總。

也就是說，每3分鐘統計依次。註意到，這個時間序列匯總的時間取的值是3分鐘的第一分鐘。如果我想取時間週期的最後一分鐘，可以將label的值改為“right”：

```python
>>>series.resample('3T', label='right').sum()
2000-01-01 00:03:00     3
2000-01-01 00:06:00    12
2000-01-01 00:09:00    21
Freq: 3T, dtype: int64
```

1.2實戰

獲取日K真實的數據：

```python
#獲取日k
df = get_price("000001.XSHG", end_date='2021-05-30 14:00:00',count=20, frequency='1d', fields=['open','close','high','low','volume','money'])  
print(df)
```

可以看到獲取到瞭`4月28號`到`5月28號`的所有數據。為瞭更方便理解 我們再添加一列數據，就是當前日期是`星期幾`的列。

```python
#獲取日k
df = get_price("000001.XSHG", end_date='2021-05-30 14:00:00',count=20, frequency='1d', fields=['open','close','high','low','volume','money'])  
df['weekday']=df.index.weekday
print(df)
```

這裡`0`代表週一，這裡如何轉換為按“**周**”統計呢

```python
#獲取周k
import pandas as pd
df_week = pd.DataFrame()
df_week = df['open'].resample('W').first()
print(df_week)
```

可以看到這裡的`2021-05-30`是一個禮拜的最後一天。它對應的開盤價確實是這個數字。說明我們計算的周K數據是正確的。

**收盤價**就是`每週收盤價`最後一天的數據。

**最高價**就是`每週收盤價`的最大值。

**最低價**就是`每週收盤價`的最小值。

```python
#獲取周k
import pandas as pd
df_week = pd.DataFrame()
df_week['open'] = df['open'].resample('W').first()
df_week['close'] = df['close'].resample('W').last()
df_week['high'] = df['high'].resample('W').max()
df_week['low'] = df['low'].resample('W').min()
print(df_week)
```

對比數據，close是最後一天的收盤價的數據。high是當前周的每天的最高價的最高價。low是當前周的每天的最低價的最低價。

我們通過不到10行代碼就能將`日K`的數據轉換為`周K`的數據。

### 2.匯總統計功能（統計月成交量、成交額）

匯總成交量和成交額

我想要把`volume`(成交量)和`money`(成交額)轉換為**總成交量**和**總成交額**

```python
#獲取周k
import pandas as pd
df_week = pd.DataFrame()
df_week['open'] = df['open'].resample('W').first()
df_week['close'] = df['close'].resample('W').last()
df_week['high'] = df['high'].resample('W').max()
df_week['low'] = df['low'].resample('W').min()
df_week['volume(sum)'] = df['volume'].resample('W').sum()
df_week['money(sum)'] = df['money'].resample('W').sum()
print(df_week)
```

### 3.日K 轉換為 月K

假設我有一年的數據，如果想轉換為月K應該怎麼轉？

隻需要改2個地方：

- 添加`start_date`獲取到一整年的數據
- 將`resample`的參數改為M即可，M代表Month

```python
#獲取日k
df = get_price("000001.XSHG", end_date='2021-05-30 14:00:00', start_date='2020-05-30', frequency='1d', fields=['open','close','high','low','volume','money'])  
df['weekday']=df.index.weekday
print(df)

#獲取周k
import pandas as pd
df_week = pd.DataFrame()
df_week['open'] = df['open'].resample('M').first()
df_week['close'] = df['close'].resample('M').last()
df_week['high'] = df['high'].resample('M').max()
df_week['low'] = df['low'].resample('M').min()
print(df_week)
```

以上就是Python量化交易實戰之使用Resample函數轉換“日K”數據的詳細內容，更多關於Python Resample函數轉換“日K”數據的資料請關註WalkonNet其它相關文章！

### 推薦閱讀：

- [Python Pandas高級教程之時間處理](https://walkonnet.com/archives/459801)
- [python數學建模之三大模型與十大常用算法詳情](https://walkonnet.com/archives/543015)
- [Python Pandas 中的數據結構詳解](https://walkonnet.com/archives/541137)
- [python Pandas時序數據處理](https://walkonnet.com/archives/540162)
- [Python pandas索引的設置和修改方法](https://walkonnet.com/archives/541225)

---

# pandas shift sum 

```py
import pandas as pd
import numpy

df = pd.DataFrame(numpy.random.randint(0, 10, (10, 2)), columns=['a','b'])
df['c'] = df.b.rolling(window = 3).sum().shift()
print(df)
```



```py
import pandas as pd

df = pd.DataFrame(
    {
        "Name": [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
        ],
        "Sex": [
            "M",
            "M",
            "M",
            "F",
            "F",
            "M",
            "F",
            "M",
            "F",
            "M",
            "M",
            "M",
            "F",
            "M",
            "M",
        ],
        "Age": [38, 28, 31, 34, 28, 28, 36, 33, 22, 39, 22, 24, 31, 29, 22],
        "Height": [
            1.74,
            1.51,
            1.67,
            1.87,
            1.8,
            1.51,
            1.85,
            1.89,
            1.81,
            1.72,
            1.75,
            1.64,
            1.9,
            1.62,
            1.61,
        ],
        "Weight": [45, 63, 39, 45, 67, 66, 53, 45, 72, 46, 58, 44, 73, 70, 51],
    }
)

df_eg1 = df.copy()
# 第 1 個用法
def BMI_1(r):
    return round(r["Weight"] / (r["Height"] ** 2), ndigits=2)


df_eg1["BMI_apply1"] = df_eg1.apply(BMI_1, axis=1)
# 第 2 個用法
def BMI_2(weight, height):
    return round(weight / (height ** 2), ndigits=2)


df_eg1["BMI_apply2"] = df_eg1.apply(lambda r: BMI_2(r["Weight"], r["Height"]), axis=1)
print(df_eg1)
```

```py
import pandas as pd

def sum(x, y, z, m, df):
    for index, row in df.iterrows():
        print(row)
    return (x + y + z) * m


df = pd.DataFrame({'A': [1, 2], 'B': [10, 20]})
df1 = df.apply(sum, args=(1, 2), m=10, df=df)
print(df1)

```

```py
import pandas as pd


def apply_func(tsC, tsD):
    return tsC.mean() + tsD.mean()


dates = pd.date_range("20130101", periods=13, freq="D")
df = pd.DataFrame(
    {
        "C": [1, 9, 2, 4, 5, -1, 6, 9, 3, 5, 10, -3, -5],
        "D": [3, 8, 2, 6, 9, 1, 26, 89, 4, 2, 1, -13, 75],
    },
    index=dates,
)
df.index.name = "datetime"
print(df)

df["rmean"] = (
    df["C"]
    .rolling(window=3)
    .apply(lambda x: apply_func(df.loc[x.index, "C"], df.loc[x.index, "D"]))
)

print(df)
```

```py
stringList = ["252.007", "546.658", "252.108"]
paramValue = ["252.017", "546.658", "252.008"]

def compareList(l1, l2):
    return [i>j for i, j in zip(l1, l2)]

print(compareList(stringList, paramValue)) 
```

```py
import pandas as pd
import numpy


def test(data):
    return sum(data)


df = pd.DataFrame(numpy.random.randint(0, 10, (10, 2)), columns=["a", "b"])
# print(df)
c = df.b.rolling(window=3).apply(test).shift()
# df['c'] = df.b.rolling(window = 3).sum().shift(1)
# df['d'] = df.b.rolling(window = 3).sum().shift(2)
print(df, "\n", c)
```



```py
from numpy_ext import rolling_apply
import pandas as pd
import numpy


def test(a, b):
    return sum(a) + sum(b)


df = pd.DataFrame(numpy.random.randint(0, 10, (10, 2)), columns=["a", "b"])
df["c"] = rolling_apply(test, 3, df.a.values, df.b.values)
df["c"] = df["c"].shift()
print(df, type(df["c"]))
```

###  Resample

```python
# https://medium.com/uxai/%E9%87%8F%E5%8C%96%E6%8A%95%E8%B3%87-ai-for-trading-1-%E7%8D%B2%E5%8F%96%E5%B8%82%E5%A0%B4%E8%B3%87%E6%96%99-109791cde0f5
import yfinance as yf
import pandas as pd


def get_info_on_stock(ticker):
    stock = yf.Ticker(ticker)
    # 拿上市至今的收盤價
    hist_all = stock.history(period="max")["Close"]
    # 拿近 30 天的所有資料
    hist_30 = stock.history(period="30d")
    return hist_all


def get_info_on_stocks(track_list):
    df = pd.DataFrame()
    for stock in track_list:
        stock_info = yf.Ticker(stock)
        # 拿近 10 天的資料
        hist = stock_info.history(period="360d")
        # 做一些簡單的處理後把 dataframe 接起來
        hist["Stock_id"] = stock
        hist["Date"] = hist.index
        hist = hist[
            [
                "Date",
                "Stock_id",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Dividends",
                "Stock Splits",
            ]
        ]
        df = pd.concat([df, hist])
    return df.set_index([pd.Index([i for i in range(len(df))])]).round(1)


if __name__ == "__main__":
    data = get_info_on_stock("2330.TW")
    print(data)

    # 選定我們要比較的公司
    track_list = ["2330.TW", "2303.TW"]
    df = get_info_on_stocks(track_list)
    print(df, type(df))

    # 接下來我們可以做一些簡單的計算，利用 pandas 內建的函數來看兩者資訊的平均 (mean):
    df_mean = df.groupby("Stock_id").mean()
    print(df_mean)

    # 前面的圖可以看到我們是將同一個時間的兩個公司資訊堆疊起來，接下來我們可以試著用另一種表示方式來做比較：
    open_prices = df.pivot(index="Date", columns="Stock_id", values="Open")
    high_prices = df.pivot(index="Date", columns="Stock_id", values="High")
    low_prices = df.pivot(index="Date", columns="Stock_id", values="Low")
    close_prices = df.pivot(index="Date", columns="Stock_id", values="Close")
    volume = df.pivot(index="Date", columns="Stock_id", values="Volume")
    print(close_prices.mean())
    print(close_prices)
    # print(close_prices['2303.TW'])
    df_month_open = open_prices.resample("M").first()
    df_month_high = high_prices.resample("M").max()
    df_month_low = low_prices.resample("M").min()
    df_month_close = close_prices.resample("M").last()
    print(df_month_open)
```


```python
from finlab import data
import datetime
import numpy as np
import pandas as pd
import finlab
import functools


class MyFinlabDataFrame(pd.DataFrame):
    """回測語法糖
    除了使用熟悉的 Pandas 語法外，我們也提供很多語法糖，讓大家開發程式時，可以用簡易的語法完成複雜的功能，讓開發策略更簡潔！
    我們將所有的語法糖包裹在 `MyFinlabDataFrame` 中，用起來跟 `pd.DataFrame` 一樣，但是多了很多功能！
    只要使用 `finlab.data.get()` 所獲得的資料，皆為 `MyFinlabDataFrame` 格式，
    接下來我們就來看看， `MyFinlabDataFrame` 有哪些好用的語法糖吧！

    當資料日期沒有對齊（例如: 財報 vs 收盤價 vs 月報）時，在使用以下運算符號：`+`, `-`, `*`, `/`, `>`, `>=`, `==`, `<`, `<=`, `&`, `|`, `~`，不需要先將資料對齊，因為 `MyFinlabDataFrame` 會自動幫你處理，以下是示意圖。

    <img src="https://i.ibb.co/pQr5yx5/Screen-Shot-2021-10-26-at-5-32-44-AM.png" alt="Screen-Shot-2021-10-26-at-5-32-44-AM">

    以下是範例：`cond1` 與 `cond2` 分別為「每天」，和「每季」的資料，假如要取交集的時間，可以用以下語法：

    ```py
    from finlab import data
    # 取得 MyFinlabDataFrame
    close = data.get('price:收盤價')
    roa = data.get('fundamental_features:ROA稅後息前')

    # 運算兩個選股條件交集
    cond1 = close > 37
    cond2 = roa > 0
    cond_1_2 = cond1 & cond2

    擷取 1101 臺泥 的訊號如下圖，可以看到 `cond1` 跟 `cond2` 訊號的頻率雖然不相同，但是由於 `cond1` 跟 `cond2` 是 `MyFinlabDataFrame`，所以可以直接取交集，而不用處理資料頻率對齊的問題。
    <br />
    <img src="https://i.ibb.co/m9chXSQ/imageconds.png" alt="imageconds">
    
    總結來說，MyFinlabDataFrame 與一般 dataframe 唯二不同之處：
    1. 多了一些 method，如`df.is_largest()`, `df.sustain()`...等。
    2. 在做四則運算、不等式運算前，會將 df1、df2 的 index 取聯集，column 取交集。
    """
    
    @property
    def _constructor(self):
        return MyFinlabDataFrame
    
    @staticmethod
    def reshape(df1, df2):
    
        isfdf1 = isinstance(df1, MyFinlabDataFrame)
        isfdf2 = isinstance(df2, MyFinlabDataFrame)
        isdf1 = isinstance(df1, pd.DataFrame)
        isdf2 = isinstance(df2, pd.DataFrame)
    
        both_are_dataframe = (isfdf1 + isdf1) * (isfdf2 + isdf2) != 0
    
        d1_index_freq = df1.get_index_str_frequency() if isfdf1 else None
        d2_index_freq = df2.get_index_str_frequency() if isfdf2 else None
    
        if (
            (d1_index_freq or d2_index_freq)
            and (d1_index_freq != d2_index_freq)
            and both_are_dataframe
        ):
    
            df1 = df1.index_str_to_date() if isfdf1 else df1
            df2 = df2.index_str_to_date() if isfdf2 else df2
    
        if isinstance(df2, pd.Series):
            df2 = pd.DataFrame({c: df2 for c in df1.columns})
    
        if both_are_dataframe:
            index = df1.index.union(df2.index)
            columns = df1.columns.intersection(df2.columns)
    
            if len(df1.index) * len(df2.index) != 0:
                index_start = max(df1.index[0], df2.index[0])
                index = [t for t in index if index_start <= t]
    
            return (
                df1.reindex(index=index, method="ffill")[columns],
                df2.reindex(index=index, method="ffill")[columns],
            )
        else:
            return df1, df2
    
    def __lt__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__lt__(df1, df2)
    
    def __gt__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__gt__(df1, df2)
    
    def __le__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__le__(df1, df2)
    
    def __ge__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__ge__(df1, df2)
    
    def __eq__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__eq__(df1, df2)
    
    def __ne__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__ne__(df1, df2)
    
    def __sub__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__sub__(df1, df2)
    
    def __add__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__add__(df1, df2)
    
    def __mul__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__mul__(df1, df2)
    
    def __truediv__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__truediv__(df1, df2)
    
    def __rshift__(self, other):
        return self.shift(-other)
    
    def __lshift__(self, other):
        return self.shift(other)
    
    def __and__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__and__(df1, df2)
    
    def __or__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__or__(df1, df2)
    
    def __getitem__(self, other):
        df1, df2 = self.reshape(self, other)
        return pd.DataFrame.__getitem__(df1, df2)
    
    def index_str_to_date(self):
        """財務月季報索引格式轉換
    
        將以下資料的索引轉換成datetime格式:
    
        月營收 (ex:2022-M1) 從文字格式轉為公告截止日。
    
        財務季報 (ex:2022-Q1) 從文字格式轉為財報電子檔資料上傳日。
    
        通常使用情境為對不同週期的dataframe做reindex，常用於以公告截止日作為訊號產生日。
    
        Returns:
          (pd.DataFrame): data
        Examples:
    
            ```py
            data.get('monthly_revenue:當月營收').index_str_to_date()
            data.get('financial_statement:現金及約當現金').index_str_to_date()
```
      """
        if len(self.index) == 0 or not isinstance(self.index[0], str):
            return self
    
        if self.index[0].find("M") != -1:
            return self._index_str_to_date_month()
        elif self.index[0].find("Q") != -1:
            return self._index_str_to_date_season()
    
        return self
    
    @staticmethod
    def to_business_day(date):
        def skip_weekend(d):
            add_days = {5: 2, 6: 1}
            wd = d.weekday()
            if wd in add_days:
                d += datetime.timedelta(days=add_days[wd])
            return d
    
        close = data.get("price:收盤價")
        return (
            pd.Series(date)
            .apply(
                lambda d: skip_weekend(d)
                if d in close.index or d < close.index[0] or d > close.index[-1]
                else close.loc[d:].index[0]
            )
            .values
        )
    
    def get_index_str_frequency(self):
    
        if len(self.index) == 0:
            return None
    
        if not isinstance(self.index[0], str):
            return None
    
        if (self.index.str.find("M") != -1).all():
            return "month"
    
        if (self.index.str.find("Q") != -1).all():
            return "season"
    
        return None
    
    def _index_date_to_str_month(self):
    
        # index is already str
        if len(self.index) == 0 or not isinstance(self.index[0], pd.Timestamp):
            return self
    
        index = (self.index - datetime.timedelta(days=30)).strftime("%Y-M%m")
        return MyFinlabDataFrame(self.values, index=index, columns=self.columns)
    
    def _index_str_to_date_month(self):
    
        # index is already timestamps
        if len(self.index) == 0 or not isinstance(self.index[0], str):
            return self
    
        if not (self.index.str.find("M") != -1).all():
            logger.warning(
                "MyFinlabDataFrame: invalid index, cannot format index to monthly timestamp."
            )
            return self
    
        index = (
            pd.to_datetime(self.index, format="%Y-M%m")
            + pd.offsets.MonthBegin()
            + datetime.timedelta(days=9)
        )
        # chinese new year and covid-19 impact monthly revenue deadline
        replacements = {
            datetime.datetime(2020, 2, 10): datetime.datetime(2020, 2, 15),
            datetime.datetime(2021, 2, 10): datetime.datetime(2021, 2, 15),
            datetime.datetime(2022, 2, 10): datetime.datetime(2022, 2, 14),
        }
        replacer = replacements.get
        index = [replacer(n, n) for n in index]
    
        index = self.to_business_day(index)
    
        ret = MyFinlabDataFrame(self.values, index=index, columns=self.columns)
        ret.index.name = "date"
    
        return ret
    
    def _index_date_to_str_season(self):
    
        # index is already str
        if len(self.index) == 0 or not isinstance(self.index[0], pd.Timestamp):
            return self
    
        q = (
            self.index.strftime("%m")
            .astype(int)
            .map({5: 1, 8: 2, 9: 2, 10: 3, 11: 3, 3: 4, 4: 4})
        )
        year = self.index.year.copy()
        year -= q == 4
        index = year.astype(str) + "-Q" + q.astype(str)
    
        return MyFinlabDataFrame(self.values, index=index, columns=self.columns)
    
    def deadline(self):
        """財務季報索引轉換成公告截止日
    
          將財務季報 (ex:2022Q1) 從文字格式轉為公告截止日的datetime格式，
          通常使用情境為對不同週期的dataframe做reindex，常用於以公告截止日作為訊號產生日。
          Returns:
            (pd.DataFrame): data
          Examples:
              ```py
              data.get('financial_statement:現金及約當現金').deadline()
              ```
        """
        return self._index_str_to_date_season(detail=False)
    
    def _index_str_to_date_season(self, detail=True):
    
        disclosure_dates = calc_disclosure_dates(detail).reindex_like(self).unstack()
    
        self.columns.name = "stock_id"
    
        unstacked = self.unstack()
    
        ret = (
            pd.DataFrame(
                {"value": unstacked.values, "disclosures": disclosure_dates.values,},
                unstacked.index,
            )
            .reset_index()
            .drop_duplicates(["disclosures", "stock_id"])
            .pivot(index="disclosures", columns="stock_id", values="value")
            .ffill()
            .pipe(lambda df: df.loc[df.index.notna()])
            .pipe(lambda df: MyFinlabDataFrame(df))
            .rename_axis("date")
        )
    
        if not detail:
            ret.index = self.to_business_day(ret.index)
    
        return ret
    
    def average(self, n):
        """取 n 筆移動平均
    
        若股票在時間窗格內，有 N/2 筆 NaN，則會產生 NaN。
        Args:
          n (positive-int): 設定移動窗格數。
        Returns:
          (pd.DataFrame): data
        Examples:
            股價在均線之上
            ```py
            from finlab import data
            close = data.get('price:收盤價')
            sma = close.average(10)
            cond = close > sma
            ```
            只需要簡單的語法，就可以將其中一部分的訊號繪製出來檢查：
            ```py
            import matplotlib.pyplot as plt
    
            close.loc['2021', '2330'].plot()
            sma.loc['2021', '2330'].plot()
            cond.loc['2021', '2330'].mul(20).add(500).plot()
    
            plt.legend(['close', 'sma', 'cond'])
            ```
            <img src="https://i.ibb.co/Mg1P85y/sma.png" alt="sma">
        """
        return self.rolling(n, min_periods=int(n / 2)).mean()
    
    def is_largest(self, n):
        """取每列前 n 筆大的數值
    
        若符合 `True` ，反之為 `False` 。用來篩選每天數值最大的股票。
    
        <img src="https://i.ibb.co/8rh3tbt/is-largest.png" alt="is-largest">
        Args:
          n (positive-int): 設定每列前 n 筆大的數值。
        Returns:
          (pd.DataFrame): data
        Examples:
            每季 ROA 前 10 名的股票
            ```py
            from finlab import data
    
            roa = data.get('fundamental_features:ROA稅後息前')
            good_stocks = roa.is_largest(10)
            ```
        """
        return (
            self.astype(float)
            .apply(lambda s: s.nlargest(n), axis=1)
            .reindex_like(self)
            .notna()
        )
    
    def is_smallest(self, n):
        """取每列前 n 筆小的數值
    
        若符合 `True` ，反之為 `False` 。用來篩選每天數值最小的股票。
        Args:
          n (positive-int): 設定每列前 n 筆小的數值。
        Returns:
          (pd.DataFrame): data
        Examples:
            股價淨值比最小的 10 檔股票
            ```py
            from finlab import data
    
            pb = data.get('price_earning_ratio:股價淨值比')
            cheap_stocks = pb.is_smallest(10)
            ```
        """
        return (
            self.astype(float)
            .apply(lambda s: s.nsmallest(n), axis=1)
            .reindex_like(self)
            .notna()
        )
    
    def is_entry(self):
        """進場點
    
        取進場訊號點，若符合條件的值則為True，反之為False。
        Returns:
          (pd.DataFrame): data
        Examples:
          策略為每日收盤價前10高，取進場點。
            ```py
            from finlab import data
            data.get('price:收盤價').is_largest(10).is_entry()
            ```
        """
        return self & ~self.shift(fill_value=False)
    
    def is_exit(self):
        """出場點
    
        取出場訊號點，若符合條件的值則為 True，反之為 False。
        Returns:
          (pd.DataFrame): data
        Examples:
          策略為每日收盤價前10高，取出場點。
            ```py
            from finlab import data
            data.get('price:收盤價').is_largest(10).is_exit()
            ```
        """
        return ~self & self.shift(fill_value=False)
    
    def rise(self, n=1):
        """數值上升中
    
        取是否比前第n筆高，若符合條件的值則為True，反之為False。
        <img src="https://i.ibb.co/Y72bN5v/Screen-Shot-2021-10-26-at-6-43-41-AM.png" alt="Screen-Shot-2021-10-26-at-6-43-41-AM">
        Args:
          n (positive-int): 設定比較前第n筆高。
        Returns:
          (pd.DataFrame): data
        Examples:
            收盤價是否高於10日前股價
            ```py
            from finlab import data
            data.get('price:收盤價').rise(10)
            ```
        """
        return self > self.shift(n)
    
    def fall(self, n=1):
        """數值下降中
    
        取是否比前第n筆低，若符合條件的值則為True，反之為False。
        <img src="https://i.ibb.co/Y72bN5v/Screen-Shot-2021-10-26-at-6-43-41-AM.png" alt="Screen-Shot-2021-10-26-at-6-43-41-AM">
        Args:
          n (positive-int): 設定比較前第n筆低。
        Returns:
          (pd.DataFrame): data
        Examples:
            收盤價是否低於10日前股價
            ```py
            from finlab import data
            data.get('price:收盤價').fall(10)
            ```
        """
        return self < self.shift(n)
    
    def groupby_category(self):
        """資料按產業分群
    
        類似 `pd.DataFrame.groupby()`的處理效果。
        Returns:
          (pd.DataFrame): data
        Examples:
          半導體平均股價淨值比時間序列
            ```py
            from finlab import data
            pe = data.get('price_earning_ratio:股價淨值比')
            pe.groupby_category().mean()['半導體'].plot()
            ```
            <img src="https://i.ibb.co/Tq2fKBp/pbmean.png" alt="pbmean">
    
            全球 2020 量化寬鬆加上晶片短缺，使得半導體股價淨值比衝高。
        """
        categories = data.get("security_categories")
        cat = categories.set_index("stock_id").category.to_dict()
        org_set = set(cat.values())
        set_remove_illegal = set(
            o for o in org_set if isinstance(o, str) and o != "nan"
        )
        set_remove_illegal
    
        refine_cat = {}
        for s, c in cat.items():
            if c == None or c == "nan":
                refine_cat[s] = "其他"
                continue
    
            if c == "電腦及週邊":
                refine_cat[s] = "電腦及週邊設備業"
                continue
    
            if c[-1] == "業" and c[:-1] in set_remove_illegal:
                refine_cat[s] = c[:-1]
            else:
                refine_cat[s] = c
    
        col_categories = pd.Series(
            self.columns.map(lambda s: refine_cat[s] if s in cat else "其他")
        )
    
        return self.groupby(col_categories.values, axis=1)
    
    def entry_price(self, trade_at="close"):
    
        signal = self.is_entry()
        adj = (
            data.get("etl:adj_close")
            if trade_at == "close"
            else data.get("etl:adj_open")
        )
        adj, signal = adj.reshape(adj.loc[signal.index[0] : signal.index[-1]], signal)
        return adj.bfill()[signal.shift(fill_value=False)].ffill()
    
    def sustain(self, nwindow, nsatisfy=None):
        """持續 N 天滿足條件
    
        取移動 nwindow 筆加總大於等於nsatisfy，若符合條件的值則為True，反之為False。
    
        Args:
          nwindow (positive-int): 設定移動窗格。
          nsatisfy (positive-int): 設定移動窗格計算後最低滿足數值。
        Returns:
          (pd.DataFrame): data
        Examples:
            收盤價是否連兩日上漲
            ```py
            from finlab import data
            data.get('price:收盤價').rise().sustain(2)
            ```
        """
        nsatisfy = nsatisfy or nwindow
        return self.rolling(nwindow).sum() >= nsatisfy
    
    def industry_rank(self, categories=None):
        """計算產業 ranking 排名，0 代表產業內最低，1 代表產業內最高
        Args:
          categories (list of str): 欲考慮的產業，ex: ['貿易百貨', '雲端運算']，預設為全產業，請參考 `data.get('security_industry_themes')` 中的產業項目。
        Examples:
            本意比產業排名分數
            ```py
            from finlab import data
    
            pe = data.get('price_earning_ratio:本益比')
            pe_rank = pe.industry_rank()
            print(pe_rank)
            ```
        """
    
        themes = (
            data.get("security_industry_themes")
            .copy()  # 複製
            .assign(
                category=lambda self: self.category.apply(lambda s: eval(s))
            )  # 從文字格式轉成陣列格
            .explode("category")  # 展開資料
        )
    
        categories = categories or set(
            themes.category[themes.category.str.find(":") == -1]
        )
    
        def calc_rank(ind):
            stock_ids = themes.stock_id[themes.category == ind]
            return self[stock_ids].pipe(lambda self: self.rank(axis=1, pct=True))
    
        return (
            pd.concat([calc_rank(ind) for ind in categories], axis=1)
            .groupby(level=0, axis=1)
            .mean()
        )
    
    def quantile_row(self, c):
        """股票當天數值分位數
    
        取得每列c定分位數的值。
        Args:
          c (positive-int): 設定每列 n 定分位數的值。
        Returns:
          (pd.DataFrame): data
        Examples:
            取每日股價前90％分位數
            ```py
            from finlab import data
            data.get('price:收盤價').quantile_row(0.9)
            ```
        """
        s = self.quantile(c, axis=1)
        return s
    
    def exit_when(self, exit):
    
        df, exit = self.reshape(self, exit)
    
        df.fillna(False, inplace=True)
        exit.fillna(False, inplace=True)
    
        entry_signal = df.is_entry()
        exit_signal = df.is_exit()
        exit_signal |= exit
    
        # build position using entry_signal and exit_signal
        position = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
        position[entry_signal] = 1
        position[exit_signal] = 0
    
        position.ffill(inplace=True)
        position = position == 1
        position.fillna(False)
        return position
    
    def hold_until(
        self,
        exit,
        nstocks_limit=None,
        stop_loss=-np.inf,
        take_profit=np.inf,
        trade_at="close",
        rank=None,
    ):
        """訊號進出場
    
        這大概是所有策略撰寫中，最重要的語法糖，上述語法中 `entries` 為進場訊號，而 `exits` 是出場訊號。所以 `entries.hold_until(exits)` ，就是進場訊號為 `True` 時，買入並持有該檔股票，直到出場訊號為 `True ` 則賣出。
        <img src="https://i.ibb.co/PCt4hPd/Screen-Shot-2021-10-26-at-6-35-05-AM.png" alt="Screen-Shot-2021-10-26-at-6-35-05-AM">
        此函式有很多細部設定，可以讓你最多選擇 N 檔股票做輪動。另外，當超過 N 檔進場訊號發生，也可以按照客製化的排序，選擇優先選入的股票。最後，可以設定價格波動當輪動訊號，來增加出場的時機點。
    
        Args:
          exit (pd.Dataframe): 出場訊號。
          nstocks_limit (int)`: 輪動檔數上限，預設為None。
          stop_loss (float): 價格波動輪動訊號，預設為None，不生成輪動訊號。範例：0.1，代表成本價下跌 10% 時產生出場訊號。
          take_profit (float): 價格波動輪動訊號，預設為None，不生成輪動訊號。範例：0.1，代表成本價上漲 10% 時產生出場訊號。
          trade_at (str): 價格波動輪動訊號參考價，預設為'close'。可選 `close` 或 `open`。
          rank (pd.Dataframe): 當天進場訊號數量超過 nstocks_limit 時，以 rank 數值越大的股票優先進場。
        Returns:
          (pd.DataFrame): data
        Examples:
            價格 > 20 日均線入場, 價格 < 60 日均線出場，最多持有10檔，超過 10 個進場訊號，則以股價淨值比小的股票優先選入。
    
            ```python
            from finlab import data
            from finlab.backtest import sim
    
            close = data.get('price:收盤價')
            pb = data.get('price_earning_ratio:股價淨值比')
    
            sma20 = close.average(20)
            sma60 = close.average(60)
    
            entries = close > sma20
            exits = close < sma60
    
            ＃pb前10小的標的做輪動
            position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
            sim(position)
            ```
        """
        if nstocks_limit is None:
            nstocks_limit = len(self.columns)
    
        union_index = self.index.union(exit.index)
        intersect_col = self.columns.intersection(exit.columns)
    
        if stop_loss != -np.inf or take_profit != np.inf:
            price = data.get(f"etl:adj_{trade_at}")
            union_index = union_index.union(
                price.loc[union_index[0] : union_index[-1]].index
            )
            intersect_col = intersect_col.intersection(price.columns)
        else:
            price = pd.DataFrame()
    
        if rank is not None:
            union_index = union_index.union(rank.index)
            intersect_col = intersect_col.intersection(rank.columns)
    
        entry = (
            self.reindex(union_index, columns=intersect_col, method="ffill")
            .ffill()
            .fillna(False)
        )
        exit = (
            exit.reindex(union_index, columns=intersect_col, method="ffill")
            .ffill()
            .fillna(False)
        )
    
        if price is not None:
            price = price.reindex(union_index, columns=intersect_col, method="ffill")
    
        if rank is not None:
            rank = rank.reindex(union_index, columns=intersect_col, method="ffill")
        else:
            rank = pd.DataFrame(1, index=union_index, columns=intersect_col)
    
        max_rank = rank.max().max()
        min_rank = rank.min().min()
        rank = (rank - min_rank) / (max_rank - min_rank)
        rank.fillna(0, inplace=True)
    
        def rotate_stocks(
            ret,
            entry,
            exit,
            nstocks_limit,
            stop_loss=-np.inf,
            take_profit=np.inf,
            price=None,
            ranking=None,
        ):
    
            nstocks = 0
    
            ret[0][np.argsort(entry[0])[-nstocks_limit:]] = 1
            ret[0][exit[0] == 1] = 0
            ret[0][entry[0] == 0] = 0
    
            entry_price = np.empty(entry.shape[1])
            entry_price[:] = np.nan
    
            for i in range(1, entry.shape[0]):
    
                # regitser entry price
                if stop_loss != -np.inf or take_profit != np.inf:
                    is_entry = (ret[i - 2] == 0) if i > 1 else (ret[i - 1] == 1)
    
                    is_waiting_for_entry = np.isnan(entry_price) & (ret[i - 1] == 1)
    
                    is_entry |= is_waiting_for_entry
    
                    entry_price[is_entry == 1] = price[i][is_entry == 1]
    
                    # check stop_loss and take_profit
                    returns = price[i] / entry_price
                    stop = (returns > 1 + abs(take_profit)) | (
                        returns < 1 - abs(stop_loss)
                    )
                    exit[i] |= stop
    
                # run signal
                rank = entry[i] * ranking[i] + ret[i - 1] * 3
                rank[exit[i] == 1] = -1
                rank[(entry[i] == 0) & (ret[i - 1] == 0)] = -1
    
                ret[i][np.argsort(rank)[-nstocks_limit:]] = 1
                ret[i][rank == -1] = 0
    
            return ret
    
        ret = pd.DataFrame(0, index=entry.index, columns=entry.columns)
        ret = rotate_stocks(
            ret.values,
            entry.astype(int).values,
            exit.astype(int).values,
            nstocks_limit,
            stop_loss,
            take_profit,
            price=price.values,
            ranking=rank.values,
        )
    
        return pd.DataFrame(ret, index=entry.index, columns=entry.columns)


@functools.lru_cache
def calc_disclosure_dates(detail=True):

    cinfo = data.get("company_basic_info").copy()
    cinfo["id"] = cinfo.stock_id.str.split(" ").str[0]
    cinfo = cinfo.set_index("id")
    cinfo = cinfo[~cinfo.index.duplicated(keep="last")]
    
    def calc_default_disclosure_dates(s):
        sid = s.name
        cat = cinfo.loc[sid].產業類別 if sid in cinfo.index else "etf"
        short_name = cinfo.loc[sid].公司簡稱 if sid in cinfo.index else "etf"
    
        if cat == "金融業":
            calendar = {
                "1": "-05-15",
                "2": "-08-31",
                "3": "-11-14",
                "4": "-03-31",
            }
        elif cat == "金融保險業":
            calendar = {
                "1": "-04-30",
                "2": "-08-31",
                "3": "-10-31",
                "4": "-03-31",
            }
        elif "KY" in short_name:
            calendar = {
                "old": {"1": "-05-15", "2": "-08-14", "3": "-11-14", "4": "-03-31",},
                "new": {"1": "-05-15", "2": "-08-31", "3": "-11-14", "4": "-03-31",},
            }
        else:
            calendar = {
                "1": "-05-15",
                "2": "-08-14",
                "3": "-11-14",
                "4": "-03-31",
            }
        get_year = (
            lambda year, season: str(year) if int(season) != 4 else str(int(year) + 1)
        )
        ky_policy_check = lambda year: "new" if year >= "2021" else "old"
        return pd.to_datetime(
            s.index.map(
                lambda d: get_year(d[:4], d[-1])
                + calendar[ky_policy_check(d[:4])][d[-1]]
            )
            if "KY" in short_name
            else s.index.map(lambda d: get_year(d[:4], d[-1]) + calendar[d[-1]])
        )
    
    def season_end(s):
    
        calendar = {
            "1": "-3-31",
            "2": "-6-30",
            "3": "-9-30",
            "4": "-12-31",
        }
        return pd.to_datetime(s.index.map(lambda d: d[:4] + calendar[d[-1]]))
    
    disclosure_dates = data.get("financial_statements_upload_detail:upload_date")
    disclosure_dates = disclosure_dates.apply(pd.to_datetime)
    
    financial_season_end = disclosure_dates.apply(season_end)
    default_disclosure_dates = disclosure_dates.apply(calc_default_disclosure_dates)
    
    disclosure_dates[
        (disclosure_dates > default_disclosure_dates)
        | (disclosure_dates < financial_season_end)
    ] = pd.NaT
    disclosure_dates[(disclosure_dates.diff() <= datetime.timedelta(days=0))] = pd.NaT
    disclosure_dates.loc["2019-Q1", "3167"] = pd.NaT
    disclosure_dates.loc["2015-Q1", "5536"] = pd.NaT
    disclosure_dates.loc["2018-Q1", "5876"] = pd.NaT
    
    disclosure_dates = disclosure_dates.fillna(default_disclosure_dates)
    disclosure_dates.columns.name = "stock_id"
    
    if detail:
        return disclosure_dates
    return default_disclosure_dates


if __name__ == "__main__":
    # finlab.login("")
    # close = data.get("price:收盤價")
    # close = MyFinlabDataFrame(close)
    # rev = data.get("monthly_revenue:當月營收")
    # rev = MyFinlabDataFrame(rev)

    ## 股價創年新高
    # cond1 = close == close.rolling(250).max()
    
    ## 確認營收底部，近月營收脫離近年穀底(連續3月的"單月營收近12月最小值/近月營收" < 0.8)
    # cond4 = ((rev.rolling(12).min()) / (rev) < 0.8).sustain(3)
    # print(cond1)
    # print(cond4)
    # print(cond1 & cond4)
    
    df = MyFinlabDataFrame(
        np.random.randint(0, 100, size=(10, 5)), columns=list("BCDEH")
    )
    df1 = MyFinlabDataFrame(
        np.random.randint(0, 100, size=(5, 4)), columns=list("ABCD")
    )
    df = df > 50
    df1 = df1 > 50
    print(df)
    print(df1)
    print(df & df1)
```


## pandas 找出重複的列
```python
import pandas as pd

# Example dataframes
df1 = pd.DataFrame({
    'date': ['2002-02-01', '2002-02-01', '2002-03-01', '2002-03-01', '2002-04-01'],
    'stock_id': [1101, 1101, 1101, 1101, 1101],
    'country': ['Taiwan', 'Taiwan', 'Taiwan', 'Taiwan', 'Taiwan'],
    'revenue': [2200067000, 2200067000, 1404336000, 1404336000, 2028782000],
    'revenue_month': [1, 1, 2, 2, 3],
    'revenue_year': [2002, 2002, 2002, 2002, 2002]
})

df2 = pd.DataFrame({
    'date': ['2023-02-01', '2023-03-01', '2023-03-01', '2023-04-01', '2023-04-01'],
    'stock_id': [1101, 1101, 1101, 1101, 1101],
    'country': ['Taiwan', 'Taiwan', 'Taiwan', 'Taiwan', 'Taiwan'],
    'revenue': [7325221000, 7306069000, 7306069000, 11730367000, 11730367000],
    'revenue_month': [1, 2, 2, 3, 3],
    'revenue_year': [2023, 2023, 2023, 2023, 2023]
})


print(df1, df2)
concatenated = pd.concat([df1, df2], ignore_index=True)
differences = concatenated.drop_duplicates(keep=False)
print(differences)
```



## 兩組 dataframe 找出多餘 row 組成 dataframe

```python
import pandas as pd

# create the DataFrame
import pandas as pd

df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 5, 6]})
df2 = pd.DataFrame({'A': [1, 2], 'B': [1, 5]})
df = df1 - df2
print(df1.to_markdown())
print("\n")
print(df2.to_markdown())


result = df1 - df2

indexs = []

for index, row in df.iterrows():
    if row.A != 0 or row.B != 0:
        indexs.append(index)
        

print("\n")
result_df = df1.loc[indexs]
print(result_df.to_markdown())
```

