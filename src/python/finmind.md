## EPS

```python
import requests
import pandas as pd

pd.options.display.float_format = lambda x: "%.2f" % x


url = "https://api.finmindtrade.com/api/v4/data"
parameter = {
    "dataset": "TaiwanStockFinancialStatements",
    "data_id": "2330",
    "start_date": "2019-01-01",
    "token": "",  # 參考登入，獲取金鑰
}
data = requests.get(url, params=parameter)
data = data.json()
data = pd.DataFrame(data["data"])
eps_data = data[data["type"] == "EPS"]
eps_data.reset_index(drop=True, inplace=True)
print(eps_data) 
```



```shell
pip install FinMind
```

## 臺灣還原股價資料表 TaiwanStockPriceAdj

```python
from FinMind.data import DataLoader

api = DataLoader()
# api.login_by_token(api_token='token')
# api.login(user_id='user_id',password='password')
df = api.taiwan_stock_daily_adj(
    stock_id="2330", start_date="2000-04-02", end_date="2023-04-12"
)
print(df)
```

## 股價日成交資訊 TaiwanStockPrice[¶](https://finmind.github.io/tutor/TaiwanMarket/Technical/#taiwanstockprice)

```python
from FinMind.data import DataLoader

api = DataLoader()
# api.login_by_token(api_token='token')
# api.login(user_id='user_id',password='password')
df = api.taiwan_stock_daily(
    stock_id='2330',
    start_date='2020-04-02',
    end_date='2020-04-12'
)
```

## 回測(引用外部 data)

```python
import numpy as np
import pandas as pd
from FinMind import strategies
from FinMind.data import DataLoader
from FinMind.strategies.base import Strategy
from ta.momentum import StochasticOscillator


class ShortSaleMarginPurchaseRatio(Strategy):
    """
    summary:
        策略概念: 券資比越高代表散戶看空，法人買超股票會上漲，這時候賣可以跟大部分散戶進行相反的操作，反之亦然
        策略規則: 券資比>=30% 且法人買超股票, 賣
                券資比<30% 且法人賣超股票 買
    """

    ShortSaleMarginPurchaseTodayRatioThreshold = 0.3

    def load_taiwan_stock_margin_purchase_short_sale(self):
        self.TaiwanStockMarginPurchaseShortSale = self.data_loader.taiwan_stock_margin_purchase_short_sale(
            stock_id=self.stock_id, start_date=self.start_date, end_date=self.end_date,
        )
        self.TaiwanStockMarginPurchaseShortSale[
            ["ShortSaleTodayBalance", "MarginPurchaseTodayBalance"]
        ] = self.TaiwanStockMarginPurchaseShortSale[
            ["ShortSaleTodayBalance", "MarginPurchaseTodayBalance"]
        ].astype(
            int
        )
        self.TaiwanStockMarginPurchaseShortSale["ShortSaleMarginPurchaseTodayRatio"] = (
            self.TaiwanStockMarginPurchaseShortSale["ShortSaleTodayBalance"]
            / self.TaiwanStockMarginPurchaseShortSale["MarginPurchaseTodayBalance"]
        )

    def load_institutional_investors_buy_sell(self):
        self.InstitutionalInvestorsBuySell = self.data_loader.taiwan_stock_institutional_investors(
            stock_id=self.stock_id, start_date=self.start_date, end_date=self.end_date,
        )
        self.InstitutionalInvestorsBuySell[["sell", "buy"]] = (
            self.InstitutionalInvestorsBuySell[["sell", "buy"]].fillna(0).astype(int)
        )
        self.InstitutionalInvestorsBuySell = self.InstitutionalInvestorsBuySell.groupby(
            ["date", "stock_id"], as_index=False
        ).agg({"buy": np.sum, "sell": np.sum})
        self.InstitutionalInvestorsBuySell["diff"] = (
            self.InstitutionalInvestorsBuySell["buy"]
            - self.InstitutionalInvestorsBuySell["sell"]
        )

    def create_trade_sign(self, stock_price: pd.DataFrame) -> pd.DataFrame:
        stock_price = stock_price.sort_values("date")
        self.load_taiwan_stock_margin_purchase_short_sale()
        self.load_institutional_investors_buy_sell()
        stock_price = pd.merge(
            stock_price,
            self.InstitutionalInvestorsBuySell[["stock_id", "date", "diff"]],
            on=["stock_id", "date"],
            how="left",
        ).fillna(0)
        stock_price = pd.merge(
            stock_price,
            self.TaiwanStockMarginPurchaseShortSale[
                ["stock_id", "date", "ShortSaleMarginPurchaseTodayRatio"]
            ],
            on=["stock_id", "date"],
            how="left",
        ).fillna(0)
        stock_price.index = range(len(stock_price))
        stock_price["signal"] = 0
        sell_mask = (
            stock_price["ShortSaleMarginPurchaseTodayRatio"]
            >= self.ShortSaleMarginPurchaseTodayRatioThreshold
        ) & (stock_price["diff"] > 0)
        stock_price.loc[sell_mask, "signal"] = -1
        buy_mask = (
            stock_price["ShortSaleMarginPurchaseTodayRatio"]
            < self.ShortSaleMarginPurchaseTodayRatioThreshold
        ) & (stock_price["diff"] < 0)
        stock_price.loc[buy_mask, "signal"] = 1
        return stock_price


data_loader = DataLoader()
# data_loader.login(user_id, password) # 可選
obj = strategies.BackTest(
    stock_id="0056",
    start_date="2018-01-01",
    end_date="2019-01-01",
    trader_fund=500000.0,
    fee=0.001425,
    data_loader=data_loader,
)

obj.add_strategy(ShortSaleMarginPurchaseRatio)
obj.simulate()

print(obj.final_stats)
print(obj.trade_detail)
obj.plot()
```



## Python 即時資料 Pipeline，以版塊圖X即時股市資料為例

https://medium.com/finmind/python-%E5%8D%B3%E6%99%82%E8%B3%87%E6%96%99-pipeline-%E4%BB%A5%E7%89%88%E5%A1%8A%E5%9C%96x%E5%8D%B3%E6%99%82%E8%82%A1%E5%B8%82%E8%B3%87%E6%96%99%E7%82%BA%E4%BE%8B-a55de908dd5b

```python
import os
import typing

import numpy as np
import pandas as pd
import plotly.express as px
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from FinMind.data import DataLoader
from flask import Flask
from loguru import logger


class TreeMap:
    def __init__(self):
        self.token = os.environ.get("FINMIND_API_TOKEN")
        self.html = "初始化~~~"
        self.api = DataLoader()
        self.api.login_by_token(api_token=self.token)
        self.stock_info = self.api.taiwan_stock_info()
        self.data_clean()

    def data_clean(self) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
        logger.info("data_clean")
        self.stock_info.drop(["date", "type"], axis=1, inplace=True)

    def filter_top_5_stock(self, plot_df: pd.DataFrame) -> pd.DataFrame:
        top_df = plot_df[["stock_id", "industry_category", "Trading_Money"]]
        top_df = top_df.sort_values("Trading_Money", ascending=False)
        top_df = top_df.groupby("industry_category").head(5)
        top_df = top_df[["stock_id", "industry_category"]]
        plot_df = top_df.merge(
            plot_df, how="left", on=["stock_id", "industry_category"]
        )
        return plot_df

    def feature_engineer(self, snapshot_df: pd.DataFrame):
        logger.info("feature_engineer")
        last_datetime = max(snapshot_df["date"])
        plot_df = snapshot_df[
            ["stock_id", "total_amount", "change_rate", "close"]
        ]
        plot_df.columns = ["stock_id", "Trading_Money", "漲跌幅%", "close"]
        plot_df = plot_df.merge(self.stock_info, how="inner", on=["stock_id"])
        for col in ["Index", "大盤"]:
            plot_df = plot_df[plot_df["industry_category"] != col]

        index_df = plot_df.groupby(["industry_category"])["Trading_Money"].agg(
            sum
        )
        index_df = index_df.reset_index()
        index_df.columns = ["industry_category", "Index_Trading_Money"]
        plot_df = plot_df.merge(index_df, how="inner", on=["industry_category"])
        plot_df = self.filter_top_5_stock(plot_df)
        plot_df["stock_name"] = (
            plot_df["stock_id"] + " " + plot_df["stock_name"]
        )
        plot_df["spread_rate_label"] = plot_df["漲跌幅%"].astype(str)
        return plot_df, last_datetime

    def plot(self, plot_df: pd.DataFrame, last_datetime: str):
        logger.info("plot")
        fig = px.treemap(
            plot_df,
            path=["industry_category", "stock_name"],
            values="Trading_Money",
            color="漲跌幅%",
            color_continuous_scale=[[0, "green"], [0.5, "white"], [1, "red"]],
            color_continuous_midpoint=0,
            custom_data=["stock_name", "close", "spread_rate_label"],
            title=f"臺股交易額X漲跌幅 {last_datetime}",
            width=1350,
            height=900,
        )
        texttemplate = "%{customdata[0]}<br>收盤價 %{customdata[1]}<br>漲跌幅(%) %{customdata[2]}<br>"
        fig.update_traces(
            textposition="middle center",
            textfont_size=24,
            texttemplate=texttemplate,
        )
        # fig.data[0].labels
        fig.data[0]["marker"]["colors"] = np.round(
            fig.data[0]["marker"]["colors"], 2
        )

        html = fig.to_html()
        return html

    def get_snapshot(self) -> pd.DataFrame:
        logger.info("get snapshot")
        url = "https://api.finmindtrade.com/api/v4/taiwan_stock_tick_snapshot"
        parameter = {
            "token": self.token,  # 參考登入，獲取金鑰
        }
        resp = requests.get(url, params=parameter)
        data = resp.json()
        if data["status"] != 200:
            raise Exception(data["msg"])
        df = pd.DataFrame(data["data"])
        return df

    def main(self):
        # load data
        snapshot_df = self.get_snapshot()
        # feature engineer
        plot_df, last_datetime = self.feature_engineer(snapshot_df)
        # plot
        self.html = self.plot(plot_df, last_datetime)


def set_scheduler():
    scheduler = BackgroundScheduler(
        timezone="Asia/Taipei", job_defaults={"max_instances": 1}
    )
    scheduler.add_job(
        id="snapshot",
        func=tree_map.main,
        trigger="cron",
        day_of_week="*",
        hour="*",
        minute="*",
        second="*/5",
    )
    scheduler.start()
    logger.info("scheduler start")


app = Flask(__name__)
tree_map = TreeMap()


@app.route("/", methods=["GET", "POST"])
def submit():
    html = tree_map.html
    return f"""
        <meta http-equiv="refresh" content="1" /> 
        {html}
    """


set_scheduler()
app.run(host="0.0.0.0", debug=True)
```

