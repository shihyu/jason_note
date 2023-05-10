## 統計大盤每年平均日K振幅

```python
import yfinance as yf
import pandas as pd

# Fetch the TWSE index
twse = yf.Ticker("^TWII")

# Get the historical data for the longest possible time
history = twse.history(period="max")

# Calculate the daily range
history["Range"] = history["High"] - history["Low"]

# Group the data by year and calculate the average daily range
yearly_adr = history.groupby(pd.Grouper(freq="Y"))["Range"].mean()

# Print the yearly ADR
print(yearly_adr)
```



## 統計假突破次數

```python
'''
統計假突破次數的方法因策略而異，以下提供一個假設進場條件的範例：

假設在 5 日均線上，且 5 日均線上穿 20 日均線時買進，其他時間賣出。
接下來我們將 K 線資料與以 5 日、20 日為週期的均線做比較，並建立一個叫做假突破的佈林通道，當價格穿越了假突破的通道時，就表示有一個假突破信號。 通道的計算方式為：
上通道：上一期假突破的最高價+1.5*(上一期假突破的最高價-上一期假突破的最低價)
下通道：上一期假突破的最低價-1.5*(上一期假突破的最高價-上一期假突破的最低價)
當發現股價穿越了假突破區間時，即可記錄一次假突破。
'''
import numpy as np
import pandas as pd
import yfinance as yf

# 下載開高低收成交量（ohlcv）資料
symbol = 'AAPL' # 蘋果公司
ohlcv = yf.download(symbol, start="2016-01-01", end="2021-11-17")

# 設定進場和出場訊號
ohlcv['ma5'] = ohlcv['Close'].rolling(window=5).mean()
ohlcv['ma20'] = ohlcv['Close'].rolling(window=20).mean()

ohlcv["in_signal"] = np.where(ohlcv['ma5'] > ohlcv['ma20'].shift(1), 1, 0)
ohlcv["out_signal"] = np.where(ohlcv['ma5'] <= ohlcv['ma20'].shift(1), 1, 0)

# 設定假突破的條件
ohlcv_in = ohlcv[ohlcv['in_signal'] == 1]
ohlcv_out = ohlcv[ohlcv['out_signal'] == 1]

fake_breakout_upper = np.nan
fake_breakout_lower = np.nan

fake_breakout_upper_list = []
fake_breakout_lower_list = []
in_signal_flag = False

for date, row in ohlcv.iterrows():
    if in_signal_flag:
        if row['High'] > fake_breakout_upper:
            fake_breakout_upper = row['High']
        if row['Low'] < fake_breakout_lower:
            fake_breakout_lower = row['Low']
        
        if row['Low'] <= fake_breakout_lower and row['Close'] > fake_breakout_lower and not np.isnan(fake_breakout_lower):
            fake_breakout_upper_list.append(fake_breakout_upper)
            fake_breakout_lower_list.append(fake_breakout_lower)
            
            fake_breakout_upper = np.nan
            fake_breakout_lower = np.nan
            
            in_signal_flag = False
            
    else:
        if date in ohlcv_in.index:
            fake_breakout_upper = row['High']
            fake_breakout_lower = row['Low']
            in_signal_flag = True
            
counts = len(fake_breakout_upper_list)

print(f"假突破次數: {counts}")
```



# How to implement a Grid Trading Strategy (Python Tutorial)

https://medium.com/@chris_42047/how-to-implement-a-grid-trading-strategy-python-tutorial-338b38fc5e84

```python
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())
import pandas as pd
from backtesting import Strategy
from backtesting import Backtest
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def CHOP(df, chop_len, atr_len):
    #  Calculate Choppiness
    chop_series = ta.chop(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        length=chop_len,
        atr_length=atr_len,
    )
    return chop_series


def plot_chart(
    i, symbol, df, current_price, buy_grid, sell_grid, buy_stop_loss, sell_stop_loss
):
    light_palette = {}
    light_palette["bg_color"] = "#ffffff"
    light_palette["plot_bg_color"] = "#ffffff"
    light_palette["grid_color"] = "#e6e6e6"
    light_palette["text_color"] = "#2e2e2e"
    light_palette["dark_candle"] = "black"
    light_palette["light_candle"] = "steelblue"
    light_palette["volume_color"] = "#c74e96"
    light_palette["border_color"] = "#2e2e2e"
    light_palette["color_1"] = "#5c285b"
    light_palette["color_2"] = "#802c62"
    light_palette["color_3"] = "#a33262"
    light_palette["color_4"] = "#c43d5c"
    light_palette["color_5"] = "#de4f51"
    light_palette["color_6"] = "#f26841"
    light_palette["color_7"] = "#fd862b"
    light_palette["color_8"] = "#ffa600"
    light_palette["color_9"] = "#3366d6"
    palette = light_palette
    #  Array of colors for support/resistance lines
    buy_grid_colors = ["#e28743", "#e28743", "#e28743", "#e28743", "#e28743"]
    sell_grid_colors = ["#2596be", "#2596be", "#2596be", "#2596be", "#2596be"]
    #  Create sub plots
    fig = make_subplots(
        rows=1,
        cols=1,
        subplot_titles=[f"{i} {symbol} Chart",],
        specs=[[{"secondary_y": False}]],
        vertical_spacing=0.04,
        shared_xaxes=True,
    )
    #  Plot close price
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["Close"], line=dict(color="blue", width=1), name=f"Close"
        ),
        row=1,
        col=1,
    )
    #  Current price
    fig.add_hline(
        y=current_price,
        line_width=0.6,
        line_dash="solid",
        line_color="blue",
        row=1,
        col=1,
    )
    #  Add buy and sell grids
    i = 0
    for level in buy_grid:
        line_color = (
            buy_grid_colors[i] if i < len(buy_grid_colors) else buy_grid_colors[0]
        )
        fig.add_hline(
            y=level,
            line_width=0.6,
            line_dash="dash",
            line_color=line_color,
            row=1,
            col=1,
        )
        i += 1
    #  stop loss
    fig.add_hline(
        y=buy_stop_loss,
        line_width=0.6,
        line_dash="solid",
        line_color="red",
        row=1,
        col=1,
    )
    i = 0
    for level in sell_grid:
        line_color = (
            sell_grid_colors[i] if i < len(sell_grid_colors) else sell_grid_colors[0]
        )
        fig.add_hline(
            y=level, line_width=1, line_dash="dash", line_color=line_color, row=1, col=1
        )
        i += 1
    #  stop loss
    fig.add_hline(
        y=sell_stop_loss,
        line_width=1,
        line_dash="solid",
        line_color="red",
        row=1,
        col=1,
    )
    fig.update_layout(
        title={"text": "", "x": 0.5},
        font=dict(family="Verdana", size=12, color=palette["text_color"]),
        autosize=True,
        width=1280,
        height=720,
        xaxis={"rangeslider": {"visible": False}},
        plot_bgcolor=palette["plot_bg_color"],
        paper_bgcolor=palette["bg_color"],
    )
    fig.update_yaxes(visible=False, secondary_y=True)
    #  Change grid color
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor=palette["grid_color"],
        gridcolor=palette["grid_color"],
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor=palette["grid_color"],
        gridcolor=palette["grid_color"],
    )
    file_name = f"{i}_{symbol}_grid_trading_1.png"
    fig.write_image(file_name, format="png")
    return fig


class GridStrategy(Strategy):
    chop_len = 14
    atr_len = 1
    num_grid_lines = 5  #  number of grid lines for buy/sell
    grid_interval = 10 / 10000  # 10 pips, 50 pips, or 100 pips or whatever
    take_profit_interval = 20 / 10000  #  pips
    stop_loss_interval = 10 / 10000  # pips
    buy_grid_prices = []
    sell_grid_prices = []
    executed_buy_grid_prices = []
    executed_sell_grid_prices = []
    last_purchase_price = 0
    long_hold = 0
    short_hold = 0
    buy_stop_loss_price = 0
    sell_stop_loss_price = 0
    grid_in_progress = False
    grid_start_index = 0  #  time index when grid starts
    grid_max_interval = 2000  #  max time steps to run the grid
    i = 0

    def init(self):
        super().init()
        #  Calculate indicators
        self.chop = self.I(CHOP, self.data.df, self.chop_len, self.atr_len)

    def reset_grid(self):
        self.grid_in_progress = False
        self.buy_grid_prices = []
        self.sell_grid_prices = []
        self.grid_start_index = 0
        self.buy_stop_loss_price = 0
        self.sell_stop_loss_price = 0

    def next(self):
        super().init()
        self.i += 1
        #  Check ranging or trending markets
        is_ranging = False
        if self.chop[-1] > 50 and self.chop[-2] <= 50:
            is_ranging = True
        #  Set up new grid for ranging -> against the trend
        current_price = self.data.Close[-1]
        if not self.grid_in_progress and is_ranging:
            self.reset_grid()
            self.grid_in_progress = True
            self.grid_start_index = self.i
            #  Stop loss
            buy_stop_loss = (
                current_price
                - (self.num_grid_lines * self.grid_interval)
                - self.stop_loss_interval
            )
            sell_stop_loss = (
                current_price
                + (self.num_grid_lines * self.grid_interval)
                + self.stop_loss_interval
            )
            #  Set buy/sell grid prices
            for i in range(1, self.num_grid_lines + 1):
                #  Calculate buy grid price
                grid_buy_price = current_price - (i * self.grid_interval)
                buy_take_profit = grid_buy_price + self.take_profit_interval
                self.buy_grid_prices.append(grid_buy_price)
                #  Create buy order
                self.buy(
                    size=0.1, limit=grid_buy_price, sl=buy_stop_loss, tp=buy_take_profit
                )
                #  Calculate sell grid price
                grid_sell_price = current_price + (i * self.grid_interval)
                sell_take_profit = grid_sell_price - self.take_profit_interval
                self.sell_grid_prices.append(grid_sell_price)
                #  Create sell order
                self.sell(
                    size=0.1,
                    limit=grid_sell_price,
                    sl=sell_stop_loss,
                    tp=sell_take_profit,
                )
            #  Optional - Plot the grid
            # plot_chart(self.i, symbol, df, current_price, self.buy_grid_prices, self.sell_grid_prices, buy_stop_loss, sell_stop_loss)


def run_backtest(df):
    # If exclusive orders (each new order auto-closes previous orders/position),
    # cancel all non-contingent orders and close all open trades beforehand
    bt = Backtest(
        df,
        GridStrategy,
        cash=10000,
        commission=0.00075,
        trade_on_close=True,
        exclusive_orders=False,
        hedging=False,
    )
    stats = bt.run()
    print(stats)
    bt.plot()


# MAIN
if __name__ == "__main__":
    symbol = "EURUSD=X"
    #  Download data
    # intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    interval = "1m"
    #  periods:  1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    data = yf.download(tickers=symbol, period="5d", interval=interval)
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    #  Run backtest
    run_backtest(df)
```



---



## TD Ameritrade API  

```py
import requests
import datetime
import pandas as pd

apikey = ""
url = "https://api.tdameritrade.com/v1/marketdata/hours"
payload = {"apikey": apikey, "markets": "EQUITY"}
response = requests.get(url=url, params=payload)
data = response.json()
print(data)
```





---



# 網格買/賣單數量計算

- base_diff_ratio :
  - 此值動態計算得到, 如果大於1則設定為1 
  -  網格預估需要的base數量與實際外站能買到base數量比例 
  - ex: 網格預估5顆 但實際外站買到4.5顆, - base_diff_ratio = (4.5 / 5) = 0.9
  
 -  各價位點計算
```py
def round_to_rule(value: float, rule: str) -> float:
    return round(value, int(rule))


def round_to_rule_floor(n, decimals=0):
    multiplier = 10 ** int(decimals)
    return math.floor(n * multiplier) / multiplier

# 網格間距
grid_step = round_to_rule_floor((upper_limit - lower_limit) / float(grid_count), quotePrecision) 

price_points = []
price_points.append(upper_limit)
while True:
    price_point = round_to_rule(price_points[-1] - grid_step, quotePrecision)

    if upper_limit >= price_point and price_point >= lower_limit:
        price_points.append(price_point)

    if price_point <= lower_limit:
        print(f"各價位點:{price_points}")
        break

```

## 全買單  (現價 > 上限) 
`註: 全買單沒有站外買幣需要因此 base_diff_ratio 固定為1`
```
current_price = 658990 
capital = 1000 
grid_count = 2 
upper_limit = 4 
lower_limit = 1 
base_diff_ratio = 1
```

```
# capital = capital * base_diff_ratio * 0.998;  
1000 * 1 * 0.998 = 998

# grid_position = capital / (SUM(各價位點, 不包含最下面那格)  
round(998 / (4+3+2), 8) = 110.88888888888889

# fee = (grid_position * 最高價 * 0.002 * grid_count) + (1 * grid_count) 
(110.88888888888889 * 4 * 0.002 * 2) + (1 * 2) = 3.774222222222222

# capital = capital - fee  
(998 - 3.774222222222222) = 994.2257777777778

# grid_position = capital / (SUM(各價位點, 不包含最下面那格)  
round(994.2257777777778 / (4+3+2), 8) = 110.46953086
```

## 全賣單  現價 < 下限 

`註: 全賣單會先預扣買單所需要手續費 `

```
current_price = 658990 
capital = 1000 
grid_count = 2 
upper_limit = 800000 
lower_limit = 700000 
base_diff_ratio = 1.0894263392162356
```

```
# grid_position = capital / (SUM(各價位點, 不包含最下面那格) 
round(1000 / (800000 + 750000), 8) = 0.00064516

# fee = (grid_position * 最高價 * 0.002 * grid_count) + (1 * grid_count)  
(0.00064516 * 800000 * 0.002 * 2) + (1 * 2) = 4.064512000000001

# capital = (capital - fee) * 1 * 0.998;    # base_diff_ratio 大於1則設定為1
(1000 - 4.064512000000001) * 1 * 0.998 = 993.943617024

# grid_position = capital / (SUM(各價位點, 不包含最下面那格) 
round(993.943617024 / (800000 + 750000), 8) = 0.00064125
```

## 部份買單部份賣單 (上限> 現價 >下限) 

```
current_price = 658990 
capital = 1000 
grid_count = 2 
upper_limit = 800000 
lower_limit = 600000 
base_diff_ratio = 0.86
```

```
# capital = capital * base_diff_ratio * 0.998
(1000 * 0.86 * 0.998) = 858.28

# grid_position = capital / (SUM(各價位點, 不包含最下面那格)  
round(858.28 / (800000 + 700000), 8) = 0.00057219

# fee = (grid_position * 最高價 * 0.002 * grid_count) + (1 * grid_count) 
(0.00057219 * 800000 * 0.002 * 2) + (1 * 2) = 3.8310079999999997

# capital = capital - fee  
(858.28 - 3.8310079999999997) = 854.448992

# grid_position = capital / (SUM(各價位點, 不包含最下面那格)
round(854.448992 / (800000 + 700000), 8) = 0.00056963
```
# 網格顆數計算

```py
import math


def round_to_rule(value: float, rule: str) -> float:
    return round(value, int(rule))


def round_to_rule_floor(n, decimals=0):
    multiplier = 10 ** int(decimals)
    return math.floor(n * multiplier) / multiplier


def get_fee(upper_limit, lower_limit, grid_count, basePrecision, quotePrecision):
    price_points = []
    grid_step = round_to_rule_floor(
        (upper_limit - lower_limit) / float(grid_count), quotePrecision
    )
    print(f"grid step:{grid_step}")
    price_points.append(upper_limit)
    while True:
        price_point = round_to_rule(price_points[-1] - grid_step, quotePrecision)

        if upper_limit >= price_point and price_point >= lower_limit:
            price_points.append(price_point)

        if price_point <= lower_limit:
            print(f"各價位點:{price_points}")
            break

    # round(998 / (200000+ 160080.0+ 120160.0+ 80240.0+ 40320.0), 8) = 0.00166112
    grid_position = round_to_rule(capital / sum(price_points[:-1]), basePrecision)
    # print(grid_position)
    return (
        (grid_position * price_points[0] * 0.002 * grid_count) + (1 * grid_count),
        price_points,
    )


def get_grid_position(
    capital, upper_limit, lower_limit, grid_count, basePrecision, quotePrecision
):
    fee, price_points = get_fee(
        upper_limit, lower_limit, grid_count, basePrecision, quotePrecision
    )
    # 資金扣除預留手續費
    # 998 - ((0.0016611185086551265 * 200000 * 0.002 * 5) + (1+5)) = 988.6777629826897
    if current_price < lower_limit:
        fee = 0

    print(f"get_grid_position fee:{fee}")
    capital = capital - fee
    print(f"扣除手續費後的資金:{capital}")

    # 扣掉預留費用，每格該下的btc數量，之後下單以這個為準
    grid_position = round_to_rule(capital / sum(price_points[:-1]), basePrecision)
    return grid_position


if __name__ == "__main__":
    current_price = # Test Log - base price bitopro
    capital = 1000
    grid_count = 2
    upper_limit = 800000
    lower_limit = 600000
    base_diff_ratio = # Test Log - base difference ratio
    basePrecision = 8
    quotePrecision = 0
    fee = 0

    # 目前價格小於網格最低價
    if current_price < lower_limit:
        fee, _ = get_fee(
            upper_limit, lower_limit, grid_count, basePrecision, quotePrecision
        )

    if base_diff_ratio > 1.0:
        capital = (capital - fee) * 0.998
    else:
        capital = (capital - fee) * base_diff_ratio * 0.998

    print(f"capital:{capital}, fee:{fee}")
    grid_position = get_grid_position(
        capital, upper_limit, lower_limit, grid_count, basePrecision, quotePrecision
    )
    print(f"grid position:{grid_position}")
```



## DeFiLlama

```py
from defillama import DefiLlama
import json

import requests

# initialize api client
llama = DefiLlama()

# Get all protocols data
response = llama.get_all_protocols()
#print(response, type(response[0]))
print(json.dumps(response[0], indent=4, ensure_ascii=False))

# Get a protocol data
response = llama.get_protocol(name='uniswap')
print(json.dumps(response, indent=4, ensure_ascii=False))

# Get historical values of total TVL
response = llama.get_historical_tvl()
print(json.dumps(response[0], indent=4, ensure_ascii=False))

# Get protocol TVL
response = llama.get_protocol_tvl(name='uniswap')
print(json.dumps(response, indent=4, ensure_ascii=False))
```

