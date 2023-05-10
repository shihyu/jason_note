## 臺股個股線圖繪製

https://hackmd.io/@s02260441/Hki9NN5jL

```python
import pandas as pd
import datetime as datetime
import matplotlib
import mplfinance as mpf
import pandas_datareader as pdr

# 導入pandas、matplotlib、mplfinance模組，將mplfinance模組縮寫為mpf
# 這邊要導入matplotlib的原因是因為mplfinance繪圖時需要調用mptplotlib模組

target_stock = "2330.TW"  # 設定要繪製走勢圖的股票
start = datetime.datetime(2018, 4, 1)
df = pdr.DataReader("2330.TW", "yahoo", start=start)
print(df)


mc = mpf.make_marketcolors(up="r", down="g", inherit=True)
s = mpf.make_mpf_style(base_mpf_style="yahoo", marketcolors=mc)
# 針對線圖的外觀微調，將上漲設定為紅色，下跌設定為綠色，符合臺股表示習慣
# 接著把自訂的marketcolors放到自訂的style中，而這個改動是基於預設的yahoo外觀

kwargs = dict(
    type="candle",
    mav=(5, 20, 60),
    volume=True,
    figratio=(10, 8),
    figscale=0.75,
    title=target_stock,
    style=s,
)
# 設定可變參數kwargs，並在變數中填上繪圖時會用到的設定值

mpf.plot(df, **kwargs)
# 選擇df資料表為資料來源，帶入kwargs參數，畫出目標股票的走勢圖
```

https://yhhuang1966.blogspot.com/2022/09/python-mplfinance.html





```py
# https://python.plainenglish.io/plot-stock-chart-using-mplfinance-in-python-9286fc69689
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import mplfinance as mpf

# download stock price data
symbol = "AAPL"
df = yf.download(symbol, period="6mo")

# Add MACD as subplot
def MACD(df, window_slow, window_fast, window_signal):
    macd = pd.DataFrame()
    macd["ema_slow"] = df["Close"].ewm(span=window_slow).mean()
    macd["ema_fast"] = df["Close"].ewm(span=window_fast).mean()
    macd["macd"] = macd["ema_slow"] - macd["ema_fast"]
    macd["signal"] = macd["macd"].ewm(span=window_signal).mean()
    macd["diff"] = macd["macd"] - macd["signal"]
    macd["bar_positive"] = macd["diff"].map(lambda x: x if x > 0 else 0)
    macd["bar_negative"] = macd["diff"].map(lambda x: x if x < 0 else 0)
    return macd


macd = MACD(df, 12, 26, 9)
macd_plot = [
    mpf.make_addplot(
        (macd["macd"]), color="#606060", panel=2, ylabel="MACD", secondary_y=False
    ),
    mpf.make_addplot((macd["signal"]), color="#1f77b4", panel=2, secondary_y=False),
    mpf.make_addplot((macd["bar_positive"]), type="bar", color="#4dc790", panel=2),
    mpf.make_addplot((macd["bar_negative"]), type="bar", color="#fd6b6c", panel=2),
]

mpf.plot(df, type="candle", volume=True, addplot=macd_plot)
```



```py
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import mplfinance as mpf
import talib as ta

# download stock price data
symbol = "AAPL"
df = yf.download(symbol, start="2021-01-01", end="2022-05-01")
for num in [10, 120]:
    df[f"SMA{num}"] = ta.SMA(df["Close"], timeperiod=num)

df["CLOSE_LINEARREG_ANGLE"] = ta.LINEARREG_ANGLE(df["Close"], timeperiod=14)
df["SMA_LINEARREG_ANGLE"] = ta.LINEARREG_ANGLE(df["SMA10"], timeperiod=14)
df = df.dropna()

add_plot = [
    mpf.make_addplot(df["CLOSE_LINEARREG_ANGLE"]),
    mpf.make_addplot(df["SMA_LINEARREG_ANGLE"]),
]
mc = mpf.make_marketcolors(up="r", down="g", inherit=True)
mpf.plot(
    df,
    type="candle",
    volume=True,
    style=mpf.make_mpf_style(base_mpf_style="yahoo", marketcolors=mc),
    addplot=add_plot,
)
```



```py
from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import talib as ta
import datetime as dt
import json
import os


class binanceAPI:
    def __init__(self, configPath):
        with open(configPath, "r") as f:
            self.kw_login = json.loads(f.read())
        self.api = self.__login(self.kw_login["PUBLIC"], self.kw_login["SECRET"])

    def __login(self, PUBLIC, SECRET):
        return Client(api_key=PUBLIC, api_secret=SECRET)


def build_df(klines):
    cols = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_av",
        "trades",
        "tb_base_av",
        "tb_quote_av",
        "ignore",
    ]
    df = pd.DataFrame(klines, columns=cols)
    df["timestamp"] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df["timestamp"]]
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df[["open", "high", "low", "close", "volume"]] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)
    for num in [5, 10, 120]:
        df[f"SMA{num}"] = ta.SMA(df["close"], timeperiod=num)
    df["SMA_LINEARREG_ANGLE"] = ta.LINEARREG_ANGLE(df["SMA5"], timeperiod=14)
    df["CLOSE_LINEARREG_ANGLE"] = ta.LINEARREG_ANGLE(df["close"], timeperiod=14)
    df = df.dropna()
    df["idx"] = range(0, len(df))
    return df


if __name__ == "__main__":
    client = binanceAPI(os.environ["HOME"] + f"/.mybin/jason/binance_login.txt")
    KLINE_INTERVAL = Client.KLINE_INTERVAL_30MINUTE
    start_time = dt.datetime(2022, 11, 1, hour=8, minute=00, second=0)
    end_time = dt.datetime.now()

    klines = client.api.get_historical_klines(
        symbol="BTCUSDT",
        interval=KLINE_INTERVAL,
        start_str=start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_str=end_time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    df = build_df(klines)
    print(df.to_markdown())
    input()
    add_plot = [
        mpf.make_addplot(df["CLOSE_LINEARREG_ANGLE"]),
        mpf.make_addplot(df["SMA_LINEARREG_ANGLE"]),
    ]
    mc = mpf.make_marketcolors(up="r", down="g", inherit=True)
    mpf.plot(
        df,
        type="candle",
        volume=True,
        style=mpf.make_mpf_style(base_mpf_style="yahoo", marketcolors=mc),
        addplot=add_plot,
    )
```

---

```py
# Function.py
# 載入套件
import yfinance as yf
import mplfinance as mpf
import numpy as np

# 透過Yfinance取得K棒歷史資料
def GetKBar(SDate, EDate, Prod, Kind, Cycle):
    # 轉換日期格式
    SDate = SDate[:4] + "-" + SDate[4:6] + "-" + SDate[6:]
    EDate = EDate[:4] + "-" + EDate[4:6] + "-" + EDate[6:]
    # 指數前面要加 ^ 符號
    if Kind == "Index":
        Prod = "^" + Prod
    # 從 yahoo finance 下載資料
    Data = yf.download(Prod, start=SDate, end=EDate, interval=Cycle)
    # 將欄位名稱改為英文小寫
    Data.columns = [i.lower() for i in Data.columns]
    # 因python會有小數點精確度問題，故將股價取到小數後兩位
    Data.open = [round(i, 2) for i in Data.open]
    Data.high = [round(i, 2) for i in Data.high]
    Data.low = [round(i, 2) for i in Data.low]
    Data.close = [round(i, 2) for i in Data.close]
    return Data


# 圖片物件
class DrawKBar:
    # 初始設定
    def __init__(self, KBar):
        self.KBar = KBar
        self.TableList = []

    # 新增附圖
    def Add(
        self,
        data,
        panel=0,
        type="line",
        marker=".",
        color="black",
        scatter=False,
        ylabel="",
    ):
        # Table = mpf.make_addplot(data,panel=panel,type=type,color=color)
        Table = mpf.make_addplot(
            data,
            panel=panel,
            type=type,
            marker=marker,
            color=color,
            scatter=scatter,
            ylabel=ylabel,
            secondary_y=False,
        )
        self.TableList.append(Table)

    # 顯示圖片
    def Show(self):
        KBar_color = mpf.make_marketcolors(
            up="red", down="green", edge="inherit", wick="inherit", volume="inherit"
        )
        KBar_style = mpf.make_mpf_style(
            base_mpf_style="yahoo", edgecolor="black", marketcolors=KBar_color
        )
        mpf.plot(
            self.KBar,
            type="candle",
            style=KBar_style,
            volume=True,
            addplot=self.TableList,
        )


# 計算績效KPI
def GetKPI(ProfitList):
    # 將 List 轉為 numpy array 格式
    ProfitList = np.array(ProfitList)
    print()

    # 交易次數
    TotalNum = len(ProfitList)
    print("交易次數:", TotalNum, "次")

    # 總損益
    TotalProfit = round(sum(ProfitList), 2)
    print("總損益:", TotalProfit, "元")

    # 平均損益
    if TotalNum == 0:
        AvgProfit = None
    else:
        AvgProfit = round(TotalProfit / TotalNum, 2)
    print("平均損益:", AvgProfit, "元")

    # 總勝率
    Win = [i for i in ProfitList if i > 0]  # 獲利的部分
    Loss = [i for i in ProfitList if i < 0]  # 虧損的部分
    if TotalNum == 0:
        WinRate = None
    else:
        WinRate = round(len(Win) / TotalNum * 100, 2)
    print("總勝率:", WinRate, "%")

    # 平均獲利
    if len(Win) == 0:
        AvgWin = None
    else:
        AvgWin = round(np.mean(Win), 2)
    print("平均獲利:", AvgWin, "元")

    # 平均虧損
    if len(Loss) == 0:
        AvgLoss = None
    else:
        AvgLoss = round(np.mean(Loss), 2)
    print("平均虧損:", AvgLoss, "元")

    # 獲利因子
    if sum(Loss) == 0:
        ProfitFactor = None
    else:
        ProfitFactor = round(sum(Win) / abs(sum(Loss)), 2)
    print("獲利因子:", ProfitFactor, "倍")

    # 最大資金回落
    MaxCapital = 0
    Capital = 0
    MDD = 0
    DD = 0
    for i in ProfitList:
        Capital += i
        MaxCapital = max(MaxCapital, Capital)
        DD = round(MaxCapital - Capital, 2)
        MDD = max(MDD, DD)
    print("最大資金回落:", abs(MDD), "元")
```

```py
# python 8-2.py "20210101" "20220501"  "AAPL" ""  "1D"
# 載入套件
from plotly.offline import plot
import talib as ta
import plotly.graph_objs as go
import sys, Function

# 資料參數 (可自行調整)
SDate = sys.argv[1]  # 資料起始日
EDate = sys.argv[2]  # 資料結束日
Prod = sys.argv[3]  # 商品代碼
Kind = sys.argv[4]  # 商品種類
Cycle = sys.argv[5]  # K棒週期

# 取得K棒資料
KBar = Function.GetKBar(SDate, EDate, Prod, Kind, Cycle)
print(KBar)

# 計算技術指標
flag = False
KBar["CDL3BLACKCROWS"] = ta.CDL3BLACKCROWS(
    KBar["open"], KBar["high"], KBar["low"], KBar["close"]
)
print(KBar)
print(KBar["CDL3BLACKCROWS"].tolist(), len(KBar["CDL3BLACKCROWS"]))
for i in range(0, len(KBar["CDL3BLACKCROWS"])):
    signal = KBar.iloc[0]["CDL3BLACKCROWS"]
    if float(signal) < 0:
        print(KBar.index[i], signal)
        flag = True

if flag == False:
    print("期間內無觸發此型態訊號")

trace = go.Candlestick(  # x= pd.to_datetime(dfohlc.index.values),
    open=KBar["open"], high=KBar["high"], low=KBar["low"], close=KBar["close"]
)
data = [trace]

plot(data, filename="go_candle1.html")
```

---

