



### 期貨報價訂閱



```py
import shioaji as sj
import datetime as dt
import pandas as pd
import signal
import os
import sys
import json
import time

# from datetime import timedelta
from dateutil import relativedelta
from line_notify import LineNotify
from datetime import timezone, timedelta


tz = timezone(timedelta(hours=+8))


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


def get_week_of_month(day_of_month=dt.datetime.now(tz).day):
    return (day_of_month - 1) // 7 + 1


def getFutureDate(today=dt.datetime.now(tz)):
    week_of_month = get_week_of_month()
    weekday = today.weekday()
    print(today, week_of_month, weekday)
    # 第三週 星期三 小於 15:00 周選就是月選
    if (
        week_of_month == 3
        and weekday == 2
        and today < dt.datetime(today.year, today.month, today.day, 15, 0)
    ):
        return str(today.year) + str(today.month + 1).zfill(2)
    else:
        return str(today.year) + str(today.month).zfill(2)


def getOpenPrice(api, year, month, day, open_time):
    FutureDate = getFutureDate()
    TXF = "TXF" + FutureDate
    date = dt.datetime(year, month, day).strftime("%Y-%m-%d")
    kbars = api.kbars(api.Contracts.Futures.TXF[TXF], date)
    df = pd.DataFrame({**kbars})
    df.ts = pd.to_datetime(df.ts)
    df.set_index("ts", inplace=True)
    open_price = df.iloc[df.index.get_loc(open_time, method="nearest")]["Open"]
    return open_price


def getOptionsDealts(api, OP, year, month, day):
    date = dt.datetime(year, month, day).strftime("%Y-%m-%d")
    try:
        # print(OP[:3], OP, date)
        ticks = api.ticks(api.Contracts.Options[OP[:3]][OP], date)
        df = pd.DataFrame({**ticks})
        if df.empty:
            return pd.DataFrame()
        df.ts = pd.to_datetime(df.ts)
        df["OP"] = OP
    except:
        # print(OP)
        return pd.DataFrame()
    return df


# {1: buy deal, 2: sell deal, 0: can't judge}
def set_tick_type(df):
    if df["close"] == df["bid_price"]:
        return 1
    elif df["close"] == df["ask_price"]:
        return 2
    else:
        return 0


@sj.on_quote
def quote_callback(topic: str, quote: dict):
    TAG = str(topic.split("/")[0])
    # print(topic, TAG, json.dumps(quote, indent=4, ensure_ascii=False))
    print(TAG, quote)
    # if TAG == 'L':
    #    #print(f'逐筆報價:{quote}')
    #    print(topic)
    #    print(f"Time:{quote['Date']} {quote['Time']}, Close:{quote['Close']}", len(TICKS))
    #    TICKS = TICKS.append({'time':f"{quote['Date']} {quote['Time']}",
    #                                  'price':quote['Close'][0]}, ignore_index=True)
    # elif TAG == 'Q':
    #    pass
    #    #print(f"AskPrice:{quote['AskPrice']}, BidPrice:{quote['BidPrice']}")
    #    #print(f'五檔報價:{quote}')
    # elif TAG == 'I':
    #    print(topic)
    #    print(f"代碼:{quote['Code']}", \
    #          f"日期:{quote['Date']} {quote['Time']}\n", \
    #          f"開盤價:{quote['Open']}", \
    #          f"最低價:{quote['Low']}", \
    #          f"最高價:{quote['High']}", \
    #          f"成交價:{quote['Close']}", \
    #          f"總金額:{quote['AmountSum']}", \
    #          f"總成交張數:{quote['VolSum']}", \
    #          f"總成交筆數:{quote['Cnt']}",
    #          f"漲跌價:{quote['DiffPrice']}", \
    #          f"漲跌幅:{quote['DiffRate']}")
    # elif TAG == 'MKT':
    #    Code = str(topic.split('/')[-1])
    #    # TickType：1代表外盤、2代表內盤
    #    #print(quote['TickType'][0], type(quote['TickType'][0]))
    #    print(f"代碼:{Code}", \
    #          f"日期:{quote['Date']} {quote['Time']}\n", \
    #          f"成交價:{quote['Close'][0]}", \
    #          f"總金額:{quote['AmountSum'][0]}", \
    #          f"成交盤:{'外盤成交' if quote['TickType'][0] == 1 else '內盤成交'}", \
    #          f"總成交張數:{quote['VolSum'][0]}")


def main():
    api = sj.Shioaji(simulation=False)
    with open(os.environ["HOME"] + "/.mybin/login.txt", "r") as f:
        kw_login = json.loads(f.read())
        accounts = api.login(**kw_login, contracts_timeout=300000)

    FutureDate = getFutureDate()
    MXF = "MXF" + FutureDate
    TXF = "TXF" + FutureDate
    # print(api.Contracts.Futures.MXF)
    api.quote.subscribe(
        api.Contracts.Futures.TXF[TXF],  # 期貨Contract
        quote_type=sj.constant.QuoteType.Tick,  # 報價類型為Tick
        # version=sj.constant.QuoteVersion.v1,  # 回傳資訊版本為v1
    )
    api.quote.set_callback(quote_callback)
    print(MXF, TXF)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    Watcher()
    main()


```



### 選擇權訂閱

```py
import shioaji as sj
import datetime as dt
import pandas as pd
import signal
import os
import sys
import json
import time

# from datetime import timedelta
from dateutil import relativedelta
from line_notify import LineNotify
from datetime import timezone, timedelta


tz = timezone(timedelta(hours=+8))


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


def get_week_of_month(year, month, day):
    """
    獲取指定的某天是某個月的第幾周
    週一為一週的開始
    實現思路：就是計算當天在本年的第y周，本月一1號在本年的第x周，然後求差即可。
    因為查閱python的系統庫可以得知：
    """
    begin = int(dt.date(year, month, 1).strftime("%W"))
    end = int(dt.date(year, month, day).strftime("%W"))
    return end - begin + 1


def getFutureDate(today=dt.datetime.now(tz)):
    week_of_month = get_week_of_month(today.year, today.month, today.day)
    weekday = today.weekday()
    # 第三週 星期三 小於 15:00 周選就是月選
    if (
        week_of_month == 3
        and weekday == 2
        and today < dt.datetime(today.year, today.month, today.day, 15, 0)
    ):
        print(today.year, today.month)
        return str(today.year) + str(today.month).zfill(2)
    else:
        return str(today.year) + str(today.month + 1).zfill(2)


def getOpenPrice(api, year, month, day, open_time):
    FutureDate = getFutureDate()
    TXF = "TXF" + FutureDate
    date = dt.datetime(year, month, day).strftime("%Y-%m-%d")
    kbars = api.kbars(api.Contracts.Futures.TXF[TXF], date)
    df = pd.DataFrame({**kbars})
    df.ts = pd.to_datetime(df.ts)
    df.set_index("ts", inplace=True)
    open_price = df.iloc[df.index.get_loc(open_time, method="nearest")]["Open"]
    return open_price


def get_week_of_month(year, month, day):
    """
    獲取指定的某天是某個月的第幾周
    週一為一週的開始
    實現思路：就是計算當天在本年的第y周，本月一1號在本年的第x周，然後求差即可。
    因為查閱python的系統庫可以得知：

    """

    begin = int(dt.date(year, month, 1).strftime("%W"))
    end = int(dt.date(year, month, day).strftime("%W"))

    return end - begin + 1


def getOptionsDealts(api, OP, year, month, day):
    date = dt.datetime(year, month, day).strftime("%Y-%m-%d")
    try:
        # print(OP[:3], OP, date)
        ticks = api.ticks(api.Contracts.Options[OP[:3]][OP], date)
        df = pd.DataFrame({**ticks})
        if df.empty:
            return pd.DataFrame()
        df.ts = pd.to_datetime(df.ts)
        df["OP"] = OP
    except:
        # print(OP)
        return pd.DataFrame()
    return df


# {1: buy deal, 2: sell deal, 0: can't judge}
def set_tick_type(df):
    if df["close"] == df["bid_price"]:
        return 1
    elif df["close"] == df["ask_price"]:
        return 2
    else:
        return 0


def main():
    api = sj.Shioaji(simulation=False)
    with open(os.environ["HOME"] + "/.mybin/login.txt", "r") as f:
        kw_login = json.loads(f.read())
        accounts = api.login(**kw_login, contracts_timeout=300000)

    now = dt.datetime.now(tz)
    wm = get_week_of_month(now.year, now.month, now.day)
    n_w = dt.datetime.today().weekday()
    # print(wm, n_w)
    # print(api.Contracts.Options)
    # print(now.strftime("%Y%m"))
    week_delivery_month = now.strftime("%Y%m")
    month_delivery_month = (
        (now + relativedelta.relativedelta(months=1)).strftime("%Y%m")
        if wm >= 3 and n_w >= 2
        else now.strftime("%Y%m")
    )
    print(week_delivery_month, month_delivery_month)
    month_options = []
    week_options = []
    strike_price_list = []
    for option in api.Contracts.Options:
        for o in option:
            if "TX" in o["category"] and (
                o["delivery_month"] == week_delivery_month
                or o["delivery_month"] == month_delivery_month
            ):
                strike_price_list.append(int(o["strike_price"]))
                if o["category"] == "TXO":
                    month_options.append(o["symbol"])
                else:
                    week_options.append(o["symbol"])
    now = dt.datetime.now(tz)
    week_of_month = get_week_of_month(now.year, now.month, now.day)
    weekday = now.weekday()

    # 第三週 星期三 小於 15:00 周選就是月選
    if (
        week_of_month == 3
        and weekday == 2
        and now < dt.datetime(now.year, now.month, now.day, 15, 0)
    ):
        week_options = month_options

    EndDate = dt.datetime.now(tz) + dt.timedelta(days=1)
    StartDate = EndDate - dt.timedelta(days=7)
    DataFrameList = []
    OptionsDict = {}

    if now.hour < 15:
        open_time = dt.datetime(now.year, now.month, now.day, 8, 45, 0)
    else:
        # open_time = dt.datetime(now.year, now.month, now.day, 8, 45, 0)
        open_time = dt.datetime(now.year, now.month, now.day, 15, 0, 0)

    open_price = getOpenPrice(api, now.year, now.month, now.day, open_time)
    strike_price_list = sorted(list(set(strike_price_list)))
    strike_price = min(strike_price_list, key=lambda x: abs(x - open_price))
    # print(strike_price_list, strike_price)
    # print(week_options)
    week_options = [s for s in week_options if str(strike_price) in s]
    print(week_options)

    while StartDate <= EndDate:
        for OP in week_options:
            df = getOptionsDealts(
                api, OP, StartDate.year, StartDate.month, StartDate.day
            )
            if not df.empty:
                columns = [
                    "OP",
                    "ts",
                    "close",
                    "volume",
                    "ask_price",
                    "ask_volume",
                    "bid_price",
                    "bid_volume",
                ]
                df = df[columns]
                df = df.assign(tick_type=df.apply(set_tick_type, axis=1))
                DataFrameList.append(df)
        StartDate = StartDate + dt.timedelta(days=1)

    if DataFrameList != []:
        df_final = pd.concat(DataFrameList, axis=0, ignore_index=True)
        # print(df_final.to_markdown())
        options = list(set(df_final["OP"].tolist()))
        # print(options)
        for option in options:
            indexs = df_final[df_final.OP == option].index.tolist()
            # print(indexs)
            # print(df_final.iloc[indexs])
            OptionsDict[option] = (
                df_final.iloc[indexs].sort_index(ascending=True).reset_index(drop=True)
            )

    Resistance_Support = {}
    for key, value in OptionsDict.items():
        # print(value, type(value))
        value.ts = pd.to_datetime(value.ts)
        value.set_index("ts", inplace=True)
        for t, row in value.iterrows():
            if t >= open_time:
                if key[-1] == "P":
                    print(open_price + row.close)
                    Resistance_Support["Resistance"] = open_price + row.close
                else:
                    print(open_price - row.close)
                    Resistance_Support["Support"] = open_price - row.close
                break

    LineNotify("KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz").send(
        f"\nOpen Price: {open_price} \nResistance: {Resistance_Support['Resistance']} \nSupport: {Resistance_Support['Support']}"
    )
    LineNotify("eTd1BOTLRXu4VtFWNwwFr3DjOcQnm7ZdLIyEuR4ZgII").send(
        f"\nOpen Price: {open_price} \nResistance: {Resistance_Support['Resistance']} \nSupport: {Resistance_Support['Support']}"
    )
    print("OPEN PRICE:", open_price, open_time)
    # open_price = df.iloc[df.index.get_loc(open_time, method="nearest")]["Open"]


if __name__ == "__main__":
    Watcher()
    print(getFutureDate())
    input()
    main()

```

