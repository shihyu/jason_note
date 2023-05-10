# 整合pyfolio了

出處:https://codeantenna.com/a/n8rxd9EgKz

下面介紹如何在backtrader裡使用pyfolio。

1 安裝pyfolio

必須使用如下命令安裝pyfolio，這樣安裝的是最新版：

pip install git+https://github.com/quantopian/pyfolio
不能使用pip install pyfolio來安裝。很多人整合不了pyfolio，就是因為安裝方式不對。

2 在backtrader中使用pyfolio

樣本程式碼test.ipynb如下

```python
from datetime import datetime
import pandas as pd
import backtrader as bt
import yfinance as yf

# 匯入pyfolio 包
import pyfolio as pf


# 建立策略類
class SmaCross(bt.Strategy):
    # 定義參數
    params = dict(period=5)  # 移動平均期數

    # 日誌函數
    def log(self, txt, dt=None):
        """日誌函數"""
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 訂單狀態 submitted/accepted，無動作
            return
        # 訂單完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("買單執行, %.2f" % order.executed.price)
            elif order.issell():
                self.log("賣單執行, %.2f" % order.executed.price)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("訂單 Canceled/Margin/Rejected")

    # 記錄交易收益情況（可省略，默認不輸出結果）
    def notify_trade(self, trade):
        if trade.isclosed:
            print(
                "毛收益 %0.2f, 扣傭後收益 % 0.2f, 佣金 %.2f"
                % (trade.pnl, trade.pnlcomm, trade.commission)
            )

    def __init__(self):
        # 移動平均線指標
        self.move_average = bt.ind.MovingAverageSimple(
            self.data, period=self.params.period
        )
        # 交叉訊號指標
        self.crossover = bt.ind.CrossOver(self.data, self.move_average)

        # sma10 = backtrader.ind.SMA(period=10)
        # sma30 = backtrader.ind.SMA(period=30)
        # crossover = backtrader.ind.CrossOver(sma10, sma30)

    def __bt_to_pandas__(self, btdata, len):
        get = lambda mydata: mydata.get(ago=0, size=len)

        fields = {
            "open": get(btdata.open),
            "high": get(btdata.high),
            "low": get(btdata.low),
            "close": get(btdata.close),
            "volume": get(btdata.volume),
        }
        time = [btdata.num2date(x) for x in get(btdata.datetime)]
        return pd.DataFrame(data=fields, index=time)

    def next(self):
        data = self.__bt_to_pandas__(self.datas[1], len(self.datas[1]))
        print(data)
        if not self.position:  # 還沒有倉位
            # 當日收盤價上穿5日均線，建立買單，買入100股
            if self.crossover > 0:
                self.log("建立買單")
                self.buy(size=100)
        # 有倉位，並且當日收盤價下破5日均線，建立賣單，賣出100股
        elif self.crossover < 0:
            self.log("建立賣單")
            self.sell(size=100)


##########################
# 主程序開始
#########################

# 建立大腦引擎對象
cerebro = bt.Cerebro()


# 建立行情資料對象，載入資料
data = bt.feeds.PandasData(dataname=yf.download("MSFT", "2011-01-01", "2023-01-01"))
# self.datas[0] 日K數據, self.datas[1] 月K數據
data = cerebro.resampledata(data, timeframe=bt.TimeFrame.Months, compression=1)
cerebro.adddata(data)  # 將行情資料對象注入引擎

cerebro.addstrategy(SmaCross)  # 將策略注入引擎

cerebro.broker.setcash(10000.0)  # 設定初始資金

# 加入pyfolio分析者
cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")

results = cerebro.run()  # 運行
strat = results[0]
pyfoliozer = strat.analyzers.getbyname("pyfolio")
returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
pf.create_full_tear_sheet(returns)
```

這裡pf.create_full_tear_sheet(returns)中pyfolio需要的收益率returns是日收益率。

如果backtrader原始資料不是日線資料，我估計returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()中，backtrader返回的returns應該是已經轉換成日收益率了，讀者可以驗證一下告訴我哈。
