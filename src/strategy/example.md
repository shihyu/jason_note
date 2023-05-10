# example

```py
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
import talib as ta
import re 
import numpy as np

o = np.array([ 39.00, 39.00, 39.00, 39.00, 40.32, 40.51, 38.09, 35.00, 27.66, 30.80, 39.00, 39.00, 39.00, 39.00, 40.51, 38.09, 35.00, 27.66, 30.80])
h = np.array([ 40.84, 39.00, 40.84, 40.84, 41.69, 40.84, 38.12, 35.50, 31.74, 32.51, 40.84, 39.00, 40.84, 40.84, 40.84, 38.12, 35.50, 31.74, 32.51])
l = np.array([ 35.80, 35.80, 35.80, 35.80, 39.26, 36.73, 33.37, 30.03, 27.03, 28.31, 35.80, 35.80, 35.80, 35.80, 36.73, 33.37, 30.03, 27.03, 28.31])
c = np.array([ 40.29, 40.29, 40.29, 40.29, 40.46, 37.08, 33.37, 30.03, 31.46, 28.31, 40.29, 40.29, 40.29, 40.29, 37.08, 33.37, 30.03, 31.46, 28.31])

print('CDL3BLACKCROWS ', ta.CDL3BLACKCROWS(o, h, l, c))

trace = go.Candlestick( #x= pd.to_datetime(dfohlc.index.values),
            open=o,
            high=h,
            low=l,
            close=c)
data = [trace]

plot(data, filename='go_candle1.html')

```



```py
import pandas as pd
import mpl_finance as mpf
import matplotlib.pyplot as plt
from FinMind.data import DataLoader


def draw_candle_stick(df, index):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xticks(range(0, len(df.index)))
    ax.set_xticklabels(df[index])
    mpf.candlestick2_ochl(
        ax,
        df["open"],
        df["close"],
        df["max"],
        df["min"],
        width=0.7,
        colorup="r",
        colordown="g",
        alpha=1,
    )


dl = DataLoader()

stock_data = dl.taiwan_stock_daily(
    stock_id="TAIEX", start_date="2018-09-01", end_date="2022-08-31"
)
print(stock_data)

# 新增月份與星期欄位

stock_data["weekday"] = pd.to_datetime(stock_data["date"]).dt.weekday
stock_data["month"] = pd.to_datetime(stock_data["date"]).dt.month
stock_data = stock_data[stock_data["weekday"] < 5]
stock_data = stock_data.dropna()

# 把數據normalize到開盤價, 方便我們做比較

stock_data["max"] = stock_data["max"] / stock_data["open"]
stock_data["min"] = stock_data["min"] / stock_data["open"]
stock_data["close"] = stock_data["close"] / stock_data["open"]
stock_data["open"] = stock_data["open"] / stock_data["open"]


# 對星期做簡單平均

stock_data_gb_week = stock_data.groupby(["weekday"]).mean().reset_index()
weekday = ["星期一", "星期二", "星期三", "星期四", "星期五"]
stock_data_gb_week["weekday"] = stock_data_gb_week["weekday"].apply(
    lambda x: weekday[x]
)
draw_candle_stick(stock_data_gb_week, "weekday")

stock_data_gb_month = stock_data.groupby(["month"]).mean().reset_index()
month = [f"{i}月" for i in range(0, 13)]
stock_data_gb_month["month"] = stock_data_gb_month["month"].apply(lambda x: month[x])
draw_candle_stick(stock_data_gb_month, "month")
```

