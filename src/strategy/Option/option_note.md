```python
from line_notify import LineNotify
from retry import retry

import datetime as dt
import sys
import platform
import signal
import datetime
import shioaji as sj
import os
import json
import pandas as pd
import requests

pd.options.display.float_format = lambda x: "%.2f" % x


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


@retry(exceptions=Exception, tries=3, delay=2, backoff=2)
def get_options_data(option_contract_period, queryStartDate=None, queryEndDate=None):
    if queryStartDate is None and queryEndDate is None:
        # now = datetime.datetime.now()
        now = datetime.datetime.now().time()  # 獲取當前時間的時間部分
        # now = datetime.datetime.now() - datetime.timedelta(days=1)
        # 如果超過15:00，日期加一天
        # if now.hour >= 15:
        #    now += datetime.timedelta(days=-1)
        queryStartDate = queryEndDate = now.strftime("%Y/%m/%d")
        if now < datetime.time(15, 0):  # 如果當前時間在 15:00 之前
            yesterday = datetime.date.today() - datetime.timedelta(days=1)  # 扣一天
            queryStartDate = queryEndDate = yesterday.strftime("%Y/%m/%d")
            print("目前時間在 15:00 之前，扣一天後為：", yesterday)

        # 轉換日期格式為年月日

    url = f"https://www.taifex.com.tw/cht/3/dlOptDataDown?down_type=1&commodity_id=txo&queryStartDate={queryStartDate}&queryEndDate={queryEndDate}"
    print(queryStartDate, queryEndDate, "\n", url)
    df = pd.read_csv(url, encoding="big5", index_col=False)
    # df = pd.read_csv("./夜盤.csv", encoding="big5", index_col=False)
    if not df.empty:
        df = df[
            ["交易日期", "契約", "買賣權", "到期月份(週別)", "履約價", "收盤價", "成交量", "交易時段", "未沖銷契約數"]
        ]
        df = df[df["收盤價"] != "-"]
        df["收盤價"] = df["收盤價"].astype(float)
        # df["收盤價"] = df["收盤價"].replace("-", "0").astype(float)
        df["成交量"] = df["成交量"].replace("-", "0").astype(float)
        df["未沖銷契約數"] = df["未沖銷契約數"].replace("-", "0").astype(float)
        df["履約價"] = df["履約價"].replace("-", "0").astype(float)
        df["到期月份(週別)"] = df["到期月份(週別)"].str.strip()
        df = df[
            (df["到期月份(週別)"] == option_contract_period)
            & (df["交易時段"] == "一般")
            & (df["收盤價"] > 0)
        ]
        # 新增未平倉金額欄位
        df["未平倉金額"] = df["收盤價"] * 50 * df["未沖銷契約數"]

        # 買權 DataFrame
        df_call = df[df["買賣權"] == "買權"]
        # 賣權 DataFrame
        df_put = df[df["買賣權"] == "賣權"]
        print(df.to_markdown(index=False, floatfmt=".2f"))
        df_call = df_call.sort_values("未平倉金額", ascending=False)
        print(df_call.to_markdown(index=False, floatfmt=".2f"))
        df_put = df_put.sort_values("未平倉金額", ascending=False)
        print(df_put.to_markdown(index=False, floatfmt=".2f"))
        return df
    else:
        return None


def get_TaiwanOptionDaily(symbol):
    date = datetime.datetime.now().time()  # 獲取當前時間的時間部分
    if date < datetime.time(15, 0):  # 如果當前時間在 15:00 之前
        date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        date = date.strftime("%Y-%m-%d")
    url = "https://api.finmindtrade.com/api/v3/data"
    parameter = {"dataset": "TaiwanOptionDaily", "data_id": "TXO", "date": date}
    data = requests.get(url, params=parameter)
    data = data.json()
    df = pd.DataFrame(data["data"])
    df = df[
        # (df["contract_date"] == "202303W5")
        (df["contract_date"] == symbol)
        & (df["date"] == date)
        & (df["trading_session"] == "position")
        & (df["close"] != 0)
    ]
    df["未平倉資金"] = df["close"] * 50 * df["open_interest"]
    print(df.to_markdown(index=False, floatfmt=".2f"))
    # 依據 call_put 欄位分成兩個 DataFrame
    df_call = df[df["call_put"] == "call"]
    df_put = df[df["call_put"] == "put"]
    print(df_call)
    print(df_put)


def get_option_week(api):
    def get_previous_wednesday():
        today = datetime.datetime.today()
        wednesday = (
            today
            - datetime.timedelta(days=today.weekday())
            + datetime.timedelta(days=2)
        )
        previous_wednesday = wednesday - datetime.timedelta(days=7)
        return previous_wednesday.date()

    def get_this_week_wednesday():
        today = datetime.datetime.today()
        wednesday = (today + datetime.timedelta(days=(2 - today.weekday()))).date()
        return wednesday

    def get_next_week_wednesday():
        today = datetime.datetime.today()
        wednesday = (today + datetime.timedelta(days=(2 - today.weekday() + 7))).date()
        return wednesday

    for option in api.Contracts.Options:
        for contract in option:
            if "TX" in contract.category:
                now = datetime.datetime.now()
                wednesday_time = get_this_week_wednesday()
                wednesday_time = datetime.datetime.combine(
                    wednesday_time, datetime.datetime.min.time()
                ) + datetime.timedelta(
                    hours=14
                )  # 因為程式是14:50啟動計算所以改設定14:00
                # print(wednesday_time)

                # 根據當前時間判斷是否在星期三 15:00之前。如果在此時間之前，則列印上週三和本週三的日期；否則列印本週三和下週三的日期：
                if now < wednesday_time:
                    if datetime.datetime.strptime(
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
                        return contract.symbol[:3]
                else:
                    if datetime.datetime.strptime(
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
                        return contract.symbol[:9]


if __name__ == "__main__":
    if platform.system().lower() == "linux":
        Watcher()

    with open(os.environ["HOME"] + "/.mybin/shioaji_token.txt", "r") as f:
        date = dt.datetime.now().strftime("%Y-%m-%d")
        api = sj.Shioaji()
        kw_login = json.loads(f.read())
        api.login(**kw_login, contracts_timeout=300000)
        symbol = get_option_week(api)
        if symbol[:3] == "TXO":
            option_contract_period = symbol[3:9]
            future_contract_code = "TXF"
        else:
            option_contract_period = symbol[3:9] + "W" + symbol[:3][-1]
            future_contract_code = "MX" + symbol[:3][-1]
            future_contract_period = future_contract_code + symbol[3:9]
            print(future_contract_code, future_contract_period)

            kbars = api.kbars(
                api.Contracts.Futures[future_contract_code][future_contract_period],
                date,
            )
            df = pd.DataFrame({**kbars})
            df.ts = pd.to_datetime(df.ts)
            df.set_index("ts", inplace=True)
            print(df)

        print(option_contract_period)
        get_TaiwanOptionDaily(option_contract_period)
        get_options_data(option_contract_period)

        TXF = (
            sorted([x for x in dir(api.Contracts.Futures.TXF) if x.startswith("TXF")])
        )[0]
        kbars = api.kbars(api.Contracts.Futures.TXF[TXF], date)
        df = pd.DataFrame({**kbars})
        df.ts = pd.to_datetime(df.ts)
        df.set_index("ts", inplace=True)
        print(df)
```


```python
import requests
import pandas as pd

pd.options.display.float_format = lambda x: "%.2f" % x

url = "https://api.finmindtrade.com/api/v3/data"
parameter = {"dataset": "TaiwanOptionDaily", "data_id": "TXO", "date": "2023-03-20"}
data = requests.get(url, params=parameter)
data = data.json()
df = pd.DataFrame(data["data"])
df = df[
    (df["contract_date"] == "202303W5")
    & (df["date"] == "2023-03-22")
    & (df["trading_session"] == "position")
    & (df["close"] != 0)
]
df['未平倉資金'] = df['close'] * 50 * df['open_interest']
print(df.to_markdown(index=False, floatfmt=".2f"))
```
