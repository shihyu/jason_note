## 取得目前週選擇代號

```python
from multiprocessing import Process, Queue
from shioaji.contracts import Contract
from shioaji import Exchange
from time import sleep
from line_notify import LineNotify

import sys
import platform
import signal
import datetime
import shioaji as sj
import os
import json
import pandas as pd


token_list = {

}


def line_notify(message):
    for _, token in token_list.items():
        LineNotify(token).send(message)


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


def get_previous_wednesday():
    today = datetime.datetime.today()
    wednesday = (
        today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=2)
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


def get_option_symbol(api):
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
                        return contract.symbol
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
                        return contract.symbol


if __name__ == "__main__":
    if platform.system().lower() == "linux":
        Watcher()

    with open(os.environ["HOME"] + "/.mybin/shioaji_token.txt", "r") as f:
        api = sj.Shioaji()
        kw_login = json.loads(f.read())
        print(kw_login)
        api.login(**kw_login, contracts_timeout=300000)
        # api.fetch_contracts(contract_download=True)
        print(get_option_symbol(api))
        api.logout()

```



## 取得週選週三換約15:00 後各履約價第一筆成交價

```python
import platform
import shioaji as sj
import datetime as dt
import pandas as pd
import signal
import os
import sys
import json

from line_notify import LineNotify


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


# 取得大臺期貨開盤價
def getOpenPrice(api, year, month, day, open_time):
    try:
        TXF = (
            sorted([x for x in dir(api.Contracts.Futures.TXF) if x.startswith("TXF")])
        )[0]
        date = dt.datetime(year, month, day).strftime("%Y-%m-%d")
        kbars = api.kbars(api.Contracts.Futures.TXF[TXF], date)
        df = pd.DataFrame({**kbars})
        if not df.empty:
            df.ts = pd.to_datetime(df.ts)
            df.set_index("ts", inplace=True)
            return df.iloc[df.index.get_loc(open_time, method="nearest")]["Open"]
        else:
            return None
    except:
        return None


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


def get_options_contracts(api):
    option_contracts = {"week": [], "month": []}
    symbols = sorted([x.symbol for x in api.Contracts.Options.TXO])
    near_option_symbol = symbols[0][3:9]

    for option in api.Contracts.Options:
        for contract in option:
            if "TX" in contract.category and near_option_symbol in contract.symbol:
                if contract.category == "TXO":
                    option_contracts["month"].append(contract)
                else:
                    option_contracts["week"].append(contract)

    return option_contracts


def main():
    api = sj.Shioaji(simulation=False)
    with open(os.environ["HOME"] + "/.mybin/shioaji_token.txt", "r") as f:
        # with open(os.environ["HOME"] + "/.mybin/login.txt", "r") as f:
        kw_login = json.loads(f.read())
        api.login(**kw_login, contracts_timeout=300000)

    options_contracts = get_options_contracts(api)

    week_options = []
    for c in options_contracts["week"]:
        week_options.append(c["symbol"])

    today = dt.date.today()
    last_thursday = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 3)

    first_row_list = []
    for OP in week_options:
        df = getOptionsDealts(
            api, OP, last_thursday.year, last_thursday.month, last_thursday.day
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
            # 假設日期時間欄位名稱為 'datetime'
            df["ts"] = pd.to_datetime(df["ts"])  # 將欄位轉換為日期時間格式
            # 選擇15:00之後的時間
            df = df[df["ts"].dt.hour >= 15]
            df["OP_close"] = df["OP"].str.extract(r"(\d{5})[PC]")
            df["OP_close"] = df["OP_close"].astype(int)
            df["OP_close"] = df["OP_close"] + df["close"]

            if not df.empty:
                df.reset_index(drop=True, inplace=True)
                first_row_list.append(df.iloc[0])
                # print(df, df.iloc[0], type(df.iloc[0]))

    df_new = pd.DataFrame(
        first_row_list,
        columns=[
            "OP",
            "ts",
            "close",
            "volume",
            "ask_price",
            "ask_volume",
            "bid_price",
            "bid_volume",
            "tick_type",
            "OP_close",
        ],
    )
    df_new.sort_values("OP", ascending=False, inplace=True)
    df_new = df_new.reset_index(drop=True)
    print(df_new)
    api.logout()


if __name__ == "__main__":
    if platform.system().lower() == "linux":
        Watcher()
    main()
```





### 取得最近期貨合約代號

```python
def getOpenPrice(api, year, month, day, open_time):
    TXF = (sorted([x for x in dir(api.Contracts.Futures.TXF) if x.startswith('TXF')]))[0]
    date = dt.datetime(year, month, day).strftime("%Y-%m-%d")
    kbars = api.kbars(api.Contracts.Futures.TXF[TXF], date)
    df = pd.DataFrame({**kbars})
    df.ts = pd.to_datetime(df.ts)
    df.set_index("ts", inplace=True)
    return df.iloc[df.index.get_loc(open_time, method="nearest")]["Open"]
```



### 取得週跟月選擇權合約

```python
import shioaji as sj
import os
import json


def get_options_contracts(api):
    option_contracts = {"week": [], "month": []}
    symbols = sorted([x.symbol for x in api.Contracts.Options.TXO])
    near_option_symbol = symbols[0][3:9]

    for option in api.Contracts.Options:
        for contract in option:
            if "TX" in contract.category and near_option_symbol in contract.symbol:
                if contract.category == "TXO":
                    option_contracts["month"].append(contract)
                else:
                    option_contracts["week"].append(contract)

    return option_contracts


if __name__ == "__main__":
    with open(os.environ["HOME"] + "/.mybin/shioaji_token.txt", "r") as f:
        api = sj.Shioaji()
        kw_login = json.loads(f.read())
        api.login(**kw_login, contracts_timeout=300000)
        options_contracts = get_options_contracts(api)
        print("Month option contracts:", options_contracts["month"])
        print("Week option contracts:", options_contracts["week"])
```



### 使用 Token 版本

```python
#
#
# 用來記錄 選擇權的 tick和報價
#
#

from multiprocessing import Process, Queue
from shioaji.contracts import Contract
from shioaji import contracts
from time import sleep


import datetime
import shioaji as sj
import os
import json
import queue


class shioaji_proxy:
    def __init__(self, queue: Queue, bool_call: bool, bool_TSE: bool):
        self.queue = queue
        self.bool_call = bool_call

        with open(os.environ["HOME"] + "/.mybin/shioaji_token.txt", "r") as f:
            self.api = sj.Shioaji()
            kw_login = json.loads(f.read())
            self.api.login(**kw_login, contracts_timeout=300000)

        # 之後改版會修正就不需要
        # self.api.fetch_contracts(contract_download=True)

        self.api.quote.set_on_bidask_fop_v1_callback(self.quote_callback)
        self.api.quote.set_on_tick_fop_v1_callback(self.quote_callback)
        option_contracts = self.get_options_contracts()

        c: Contract
        for c in option_contracts["week"]:
            if c.symbol[-1] == ("C" if self.bool_call else "P"):
                print(c)
                self.api.quote.subscribe(
                    c,
                    quote_type=sj.constant.QuoteType.Tick,
                    # version=sj.constant.QuoteVersion.v1,
                )
                self.api.quote.subscribe(
                    c,
                    quote_type=sj.constant.QuoteType.BidAsk,
                    # version=sj.constant.QuoteVersion.v1,
                )

        # self.contract: Contract = self.api.Contracts.Options.TXO.TXO202206016600C if bool_call else self.api.Contracts.Options.TXO.TXO202206016600P

        # if bool_TSE:
        #    self.api.quote.subscribe(
        #        self.api.Contracts.Indexs.TSE.TSE001,
        #        quote_type=sj.constant.QuoteType.Tick,
        #    )

    def get_options_contracts(self):
        option_contracts = {"week": [], "month": []}
        symbols = sorted([x.symbol for x in self.api.Contracts.Options.TXO])
        near_option_symbol = symbols[0][3:9]

        for option in self.api.Contracts.Options:
            for contract in option:
                if "TX" in contract.category and near_option_symbol in contract.symbol:
                    if contract.category == "TXO":
                        option_contracts["month"].append(contract)
                    else:
                        option_contracts["week"].append(contract)

        return option_contracts

    def quote_callback(self, topic: str, quote: dict):
        # print(topic, quote)
        self.queue.put((topic, quote))


def shioaji_subscriber(queue, bool_call, bool_TSE):
    proxy = shioaji_proxy(queue, bool_call, bool_TSE)

    while True:
        sleep(1)
        queue.put(f"{proxy} {datetime.datetime.now()}")


if __name__ == "__main__":
    q = Queue()  # 於主進程創建隊列物件
    process_list = []
    print("main queue id: %d" % id(q))

    proc = Process(target=shioaji_subscriber, args=(q, True, True))
    process_list.append(proc)
    proc.start()
    proc = Process(target=shioaji_subscriber, args=(q, False, False))
    process_list.append(proc)
    proc.start()

    bool_AM = (
        True
        if datetime.datetime.now().time() < datetime.time(hour=12, minute=0)
        else False
    )

    with open(
        f'TXO-{datetime.datetime.now().date()}-{"AM" if bool_AM else "PM"}.txt', "w+"
    ) as fp:
        ret_count = 0
        while True:
            try:
                ret = q.get(timeout=1)
            except queue.Empty:
                print(datetime.datetime.now())
            else:
                fp.write(f"{datetime.datetime.now()}\t{ret[0]}\t{ret[1]}\n")
                ret_count += 1

            # Check if we have written 100 records, then write to file and reset count
            if ret_count == 100:
                fp.flush()  # flush the file buffer to disk
                ret_count = 0

            # Check if current time is between 13:46 and 14:00, or between 5:01 and 5:10, then exit loop
            if (
                datetime.time(hour=13, minute=46)
                < datetime.datetime.now().time()
                < datetime.time(hour=14, minute=0)
            ) or (
                datetime.time(hour=5, minute=1)
                < datetime.datetime.now().time()
                < datetime.time(hour=5, minute=10)
            ):
                break

    for p in process_list:
        p.terminate()
        p.join()
        p.close()
        print(f"{p} joined")
```

### 用來記錄 選擇權的 tick和報價

```python
from multiprocessing import Process, Queue

import datetime
import shioaji as sj
from shioaji import contracts
from shioaji.contracts import Contract
import os
import json
from time import sleep
import queue


class shioaji_proxy:
    def __init__(self, queue: Queue, bool_call: bool, bool_TSE: bool):
        self.queue = queue
        self.bool_call = bool_call

        with open(os.environ["HOME"] + "/.mybin/login.txt", "r") as f:
            self.api = sj.Shioaji()
            kw_login = json.loads(f.read())
            self.api.login(**kw_login, contracts_timeout=300000)

        self.api.quote.set_quote_callback(self.quote_callback)

        symbols = []
        for x in self.api.Contracts.Options.TXO:
            symbols.append(x.symbol)
        symbols.sort()
        str_option_near = symbols[0][:9]

        contracts = []
        for x in self.api.Contracts.Options.TXO:
            if x.symbol.startswith(str_option_near):
                contracts.append(x)

        c: Contract
        for c in contracts:
            if c.symbol[-1] == ("C" if self.bool_call else "P"):
                self.api.quote.subscribe(c, quote_type=sj.constant.QuoteType.Tick)
                self.api.quote.subscribe(c, quote_type=sj.constant.QuoteType.BidAsk)

        # self.contract: Contract = self.api.Contracts.Options.TXO.TXO202206016600C if bool_call else self.api.Contracts.Options.TXO.TXO202206016600P

        if bool_TSE:
            self.api.quote.subscribe(
                self.api.Contracts.Indexs.TSE.TSE001,
                quote_type=sj.constant.QuoteType.Tick,
            )

    def quote_callback(self, topic: str, quote: dict):
        # print(topic, quote)
        self.queue.put((topic, quote))


def shioaji_subscriber(queue, bool_call, bool_TSE):
    proxy = shioaji_proxy(queue, bool_call, bool_TSE)

    while True:
        sleep(1)
        queue.put(f"{proxy} {datetime.datetime.now()}")


if __name__ == "__main__":
    q = Queue()  # 於主進程創建隊列物件
    process_list = []
    print("main queue id: %d" % id(q))

    # shioaji_subscriber(q, True, True)

    proc = Process(target=shioaji_subscriber, args=(q, True, True))
    process_list.append(proc)
    proc.start()
    proc = Process(target=shioaji_subscriber, args=(q, False, False))
    process_list.append(proc)
    proc.start()

    bool_AM = (
        True
        if datetime.datetime.now().time() < datetime.time(hour=12, minute=0)
        else False
    )

    with open(
        f'TXO-{datetime.datetime.now().date()}-{"AM" if bool_AM else "PM"}.txt', "w+"
    ) as fp:
        while True:
            try:
                ret = q.get(timeout=1)
            except queue.Empty:
                pass
                print(datetime.datetime.now())
            else:
                # print(ret)
                fp.write(f"{datetime.datetime.now()}\t{ret[0]}\t{ret[1]}\n")

            if (
                datetime.time(hour=13, minute=46)
                < datetime.datetime.now().time()
                < datetime.time(hour=14, minute=0)
            ):
                break

            if (
                datetime.time(hour=5, minute=1)
                < datetime.datetime.now().time()
                < datetime.time(hour=5, minute=10)
            ):
                break

    for p in process_list:
        p.terminate()
        p.join()
        p.close()
        print(f"{p} joined")
```





## 選擇權最近合約排序

```python
import shioaji as sj
import os
import json

with open(os.environ["HOME"] + "/.mybin/login.txt", "r") as f:
    api = sj.Shioaji()
    kw_login = json.loads(f.read())
    api.login(**kw_login, contracts_timeout=300000)

symbols = []
for x in api.Contracts.Options.TXO:
    symbols.append(x.symbol)

symbols.sort()
str_option_near = symbols[0][:9]

contracts = []
for x in api.Contracts.Options.TXO:
    if x.symbol.startswith(str_option_near):
        contracts.append(x)

for c in contracts:
    print(c, c.symbol)
    # if c.symbol[-1] == ("C" if bool_call else "P"):
    # print(x)
```



```python
from shioaji import TickSTKv1, TickFOPv1, BidAskSTKv1, BidAskFOPv1, Exchange


def order_callback(stat, msg: dict):
    print(f"\n\033[1;33morder_callback: {stat} {msg}\033[0m\n")


def event_callback(resp_code, event, info, event_str):
    print(
        f"\n\033[1;33mevent_callback: {resp_code} {event} {info} {event_str}\033[0m\n"
    )


def quote_callback(topic: str, quote: dict):
    print(f"\n\033[1;33mquote_callback: {topic} {quote}\033[0m\n")


def stk_tick_callback_v1(exchange: Exchange, tick: TickSTKv1):
    print(f"stk_tick_callback_v1: {exchange} {tick}")
    print(json.dumps(tick))


def stk_bidask_callback_v1(exchange: Exchange, bidask: BidAskSTKv1):
    print(f"stk_bidask_callback_v1: {exchange} {bidask}")


# {'code': 'TXFG2', 'datetime': '2022-06-23T21:52:32.489000', 'bid_total_vol': 74, 'ask_total_vol': 44, 'bid_price': ['14933', '14932', '14931', '14930', '14929'], 'bid_volume': [3, 11, 20, 31, 9], 'diff_bid_vol': [-4, 0, -5, 4, -1], 'ask_price': ['14935', '14936', '14937', '14938', '14939'], 'ask_volume': [5, 8, 8, 11, 12], 'diff_ask_vol': [3, 3, 0, 0, 0], 'first_derived_bid_price': '0', 'first_derived_ask_price': '14939', 'first_derived_bid_vol': 0, 'first_derived_ask_vol': 1, 'underlying_price': '15176.44', 'simtrade': 0}
# {'code': 'TXFG2', 'datetime': '2022-06-23T21:52:32.407000', 'open': '14904', 'underlying_price': '15176.44', 'bid_side_total_vol': 29991, 'ask_side_total_vol': 29864, 'avg_price': '14949.592158', 'close': '14934', 'high': '15041', 'low': '14849', 'amount': '29868', 'total_amount': '695828767', 'volume': 2, 'total_volume': 46545, 'tick_type': 2, 'chg_type': 4, 'price_chg': '-5', 'pct_chg': '-0.033469', 'simtrade': 0}


def fop_tick_callback_v1(exchange: Exchange, tick: TickFOPv1):
    # print(f'fop_tick_callback_v1: {exchange} {tick}')
    print(tick.to_dict(raw=True))


def fop_bidask_callback_v1(exchange: Exchange, bidask: BidAskFOPv1):
    # print(f'fop_bidask_callback_v1: {exchange} {bidask}')
    print(bidask.to_dict(raw=True))


api.set_order_callback(order_callback)
api.quote.set_event_callback(event_callback)
api.quote.set_quote_callback(quote_callback)
api.quote.set_on_tick_stk_v1_callback(stk_tick_callback_v1)
api.quote.set_on_bidask_stk_v1_callback(stk_bidask_callback_v1)
api.quote.set_on_tick_fop_v1_callback(fop_tick_callback_v1)
api.quote.set_on_bidask_fop_v1_callback(fop_bidask_callback_v1)
```





```python
if timestamp.time() < datetime.time(13, 25, 0):
    # 最後一盤 13:25:00 前下回補單。一率市價單回補
    self.order_cover = sdt.api.Order(
        price=0,
        quantity=current_number_to_cover,
        action="Buy",
        price_type="MKT",
        order_type="ROD",
        order_lot="Common",
        first_sell="false",
        account=sdt.api.stock_account,
    )
else:
    # 13:25 後回補，最後一盤，只能用：限價＋漲停價格 來確保一定會補回來
    self.order_cover = sdt.api.Order(
        price=self.today_limit_up,
        quantity=current_number_to_cover,
        action="Buy",
        price_type="LMT",
        order_type="ROD",
        order_lot="Common",
        first_sell="false",
        account=sdt.api.stock_account,
    )

# 下限價單 或是 下市價單
if sdt.config[w.order_setting][w.order_limited] == w.Yes:
    self.order_put = sdt.api.Order(
        price=self.today_put_order_price,
        quantity=abs(units),
        action="Sell",
        price_type="LMT",
        order_type="ROD",
        order_lot="Common",
        first_sell="true",
        account=sdt.api.stock_account,
    )
else:
    self.order_put = sdt.api.Order(
        price=0,
        quantity=abs(units),
        action="Sell",
        price_type="MKT",
        order_type="ROD",
        order_lot="Common",
        first_sell="true",
        account=sdt.api.stock_account,
    )

self.trade_put = sdt.place_order(self.__contract__, self.order_put)

```





## api.activate_ca 啟動電子憑證

官方說明文件：
https://sinotrade.github.io/tutor/order/CA/
在下單之前，需要先下載永豐證券帳戶的下單電子憑證，下載方式請參考官方說明
https://www.sinotrade.com.tw/CSCenter/CSCenter_13_1?tab=2
下載完成後，可以透過api.activate_ca來啟用下單電子憑證，範例如下：

```python
from dotenv import load_dotenv
import os
import shioaji as sj

load_dotenv('D:\\python\\shioaji\\.env') #讀取.env中的環境變數
api = sj.Shioaji()
api.login(
    person_id=os.getenv('YOUR_PERSON_ID'), 
    passwd=os.getenv('YOUR_PASSWORD')
)

result = api.activate_ca(
    ca_path=os.getenv('YOUR_CA_PATH'), # 下單電子憑證路徑及檔案名稱
    ca_passwd=os.getenv('YOUR_CA_PASS'), # 下單電子憑證密碼
    person_id=os.getenv('YOUR_PERSON_ID'), # 身份證字號
)
print(result)

api.logout()
```



## 下單電子憑證及Stock股票Order建立

出處 ： https://ithelp.ithome.com.tw/articles/10272506?sc=iThelpR

啟用下單電子憑證前要先執行api.login進行登入。在這裡一樣把電子憑證相關資訊先儲存在env檔案中，再透過os.getenv()取得資訊並傳入activate_ca中，若電子憑證啟用成功，則回傳的result就會是True。

> 若你要用虛擬帳戶登入並練習或測試下單功能，不必啟動電子憑證，可跳過這個步驟。

## Order物件建立說明

官方說明文件：https://sinotrade.github.io/tutor/order/Stock/#making-order-object
在發送委託單前，要先產生一個Order物件。
Order物件建立的參數說明如下：

|    參數     |    參數說明    |                           參數範例                           |
| :---------: | :------------: | :----------------------------------------------------------: |
|    price    |    委託價格    |                             18.5                             |
|  quantity   |    委託數量    |                              1                               |
|   action    |   委託單動作   |                         {Buy, Sell}                          |
| price_type  |    價格類型    |            {LMT, MKT, MKP} (限價、市價、範圍市價)            |
| order_type  |   委託單類型   | {ROD, IOC, FOK} (當日有效、立即成交否則取消、全部成交否則取消) |
| order_cond  |   委託單種類   |    {Cash, MarginTrading, ShortSelling} (現股、融資、融券)    |
|  order_lot  | 委託單交易單位 | {Common, Fixing, Odd, IntradayOdd} (整股、盤後定價、盤後零股、盤中零股) |
| first_sell  | 是否為現沖先賣 |                        {true, false}                         |
|   octype    |      倉別      | {Auto, NewPosition, Cover, DayTrade} (自動、新倉、平倉、當沖) |
| OptionRight |   選擇權類別   |                         {Call, Put}                          |
|   account   |    交易帳戶    |                    可由API取得account物件                    |

> order_cond、order_lot及first_sell，為股票Order物件特有屬性
> octype，為期貨或選擇權Order物件特有屬性
> OptionRight為選擇權Order物件特有屬性

### 現股買進，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Buy, #買進
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Common, 
    account=api.stock_account
)
```

### 現股賣出，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell, #賣出
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Common, 
    account=api.stock_account
)
```

### 現沖先賣，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell,
    price_type=sj.constant.StockPriceType.LMT,
    order_type=sj.constant.TFTOrderType.ROD,
    order_lot=sj.constant.TFTStockOrderLot.Common,
    first_sell=sj.constant.StockFirstSell.Yes, #現沖先賣，設定為StockFirstSell.Yes or True
    account=api.stock_account
)
```

### 盤中零股，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Buy, #買進
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.IntradayOdd, #指定盤中零股
    account=api.stock_account
)
```

### 盤中零股，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Buy, #買進
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.IntradayOdd, #指定盤中零股
    account=api.stock_account
)
```

### 盤後定價，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Buy, #買進
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Fixing, #指定盤後定價
    account=api.stock_account
)
```

### 盤後零股，Order範例

```python
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Buy, #買進
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Odd, #指定盤後零股
    account=api.stock_account
)
```

以上為現股Order的建立及下單相關操作，若是要使用融資或融券，只要在建立Order時指定order_cond為StockOrderCond.MarginTrading(融資)或是StockOrderCond.ShortSelling(融券)即可；若在建立Order時沒有指定order_cond，預設都是以StockOrderCond.Cash建立。



---

```python
from Jlab.watcher import Watcher
import shioaji as sj
import json
import os
import sys


def login(simulation=False):
    api = sj.Shioaji(simulation=simulation)
    token_file = os.environ["HOME"] + "/.mybin/shioaji_tokens.json"
    with open(token_file, "r") as f:
        users = json.load(f)
        print("All users: " + ", ".join(users.keys()))

        user = input("Select a user from the list above: ")
        if user not in users:
            print("User not found.")
            sys.exit()

        api.login(
            users[user]["api_key"], users[user]["secret_key"], fetch_contract=False
        )
        api.fetch_contracts(contract_download=True)
        print(f"Logged in as {user}")
        return api


def get_near_month_txf_contract(api):
    contract = min(
        [x for x in api.Contracts.Futures.TXF if x.code[-2:] not in ["R1", "R2"]],
        key=lambda x: x.delivery_date,
    )
    return contract


def simulation(api):
    contract = api.Contracts.Stocks.TSE["2890"]
    # order - edit it
    order = api.Order(
        action=sj.constant.Action.Buy,
        price=20,
        quantity=1,
        price_type=sj.constant.StockPriceType.LMT,
        order_type=sj.constant.OrderType.ROD,
        account=api.stock_account,
    )

    # place order
    trade = api.place_order(contract, order, timeout=0)
    print(trade)


if __name__ == "__main__":
    Watcher()
    # 設置參數以決定是使用模擬還是實際交易
    SIMULATION = False
    api = login(simulation=SIMULATION)
    if SIMULATION:
        simulation(api)
    else:
        contract = get_near_month_txf_contract(api)
        print(contract)

        # print(api.account_balance())
        # print(api.list_positions(api.stock_account))
        contracts = [api.Contracts.Stocks["2330"], api.Contracts.Stocks["2317"]]
        snapshots = api.snapshots(contracts)
        print(snapshots)
        # Stock default account  證券目前的預設帳戶
    print(api.stock_account)

    # Futures default account 期貨目前的預設帳戶
    print(api.futopt_account)

    api.logout()
```

---

```python
accounts = api.list_accounts()
```

若你登入虛擬環境後，執行print(accounts)，會顯示以下內容

```
[FutureAccount(person_id='QBCCAIGJBJ', broker_id='F002000', account_id='9100020', signed=True, username='PAPIUSER01'), StockAccount(person_id='QBCCAIGJBJ', broker_id='9A95', account_id='0504350', signed=True, username='PAPIUSER01')]
```

可以看到虛擬環境帳號底下，分別有FutureAccount期貨帳戶及StockAccount股票帳戶，相關變數說明如下：

| 變數名稱   | 說明              |                                               |
| :--------- | :---------------- | :-------------------------------------------- |
| person_id  | 身份證號碼        |                                               |
| broker_id  | 券商分點號碼      |                                               |
| account_id | 帳戶號碼          |                                               |
| **signed** | 是否已簽署API下單 | 若帳號資訊無此變數，表示此帳戶尚未簽署API下單 |
| username   | 使用者名稱        | 若使用個人帳號登入，此欄位顯示你的姓名        |

若你的帳戶尚未簽署API下單，可開啟永豐金iLeader，找到「數位e櫃臺」並開啟





https://github.com/eyelash500/2021_ironman_Shioaji

```py
import threading
import time
from datetime import datetime

import shioaji as sj


class trader:
    """The Shioaji Object"""

    def __init__(self) -> None:
        self.simulation = True  # 是否為測試環境
        self.id = "PAPIUSER07"
        self.pwd = "2222"
        self.api = sj.Shioaji()
        self.diff = 0  # 大臺的點數差

    def login(self, id=None, pwd=None, simulation=True):
        """Login to Shioaji.
        Args:
            id(str): user ID
            pwd(str): the login password
        Returns:
            bool: True is login successfully, False is not.
        """

        print(f"=start login-{datetime.now().strftime('%Y%m%d')}")
        if id and pwd:
            self.id = id
            self.pwd = pwd

        try:
            # 登入 shioaji
            self.api = sj.Shioaji(simulation=simulation)
            self.api.login(person_id=self.id, passwd=self.pwd)
        except Exception as exc:
            print(f"id={self.id}, pwd={self.pwd}...{exc}")
            return False

        return True

    def _get_subscribe(self) -> bool:
        """Get the subscibe format."""

        print(self.api.quote.subscribe)

        return True

    def subscribe(self, contract):
        """subscribe the contract quote."""

        print("=Subscribe=")
        self.api.quote.subscribe(contract, quote_type=sj.constant.QuoteType.Tick)

    def unsubscribe(self, contract):
        """unsubscribe the contract."""

        print("unsubscribe")
        self.api.quote.unsubscribe(contract, quote_type=sj.constant.QuoteType.Tick)

    def quote_callback(self, topic: str, quote: dict):
        """Get the quote info and change the oder price.
        The quote's format is v0: quote is a dict and the value is a list.
        """

        print(
            f"{topic}-Price:[{quote['Close']}]Diff:[{quote['DiffPrice']}]volumn:[{quote['Volume']}]"
        )

        if topic.find("TFE/TXF") > 0:
            self.diff = quote["DiffPrice"][0]
        elif topic.find("OPT/TX") > 0:
            reduced_point = 1

            # 設定要減少的點數
            if self.diff < quote["Close"][0]:
                reduced_point = self.diff  # 比市價還要低的數字
            else:
                # 當變動很多時，要剪去的價格會比較大，但比現價還要小
                reduced_point = quote["Close"][0] - reduced_point

            self.change_price(quote["Close"], True, reduced_point)  # 價格比現價還要低，

    def change_price(self, price, diff, points):
        """Simulate to change the price of the order."""

        self.mxf_price = price[0] - points if diff else price[0] + points
        print(f"選擇權：current price:{price[0]}-new price:{self.mxf_price}")


def sleeper():
    """For sleeping... Let us get the quote and change the price."""

    print("-start sleep...")
    time.sleep(60)
    print("-Wake up!!!!")


timer = threading.Thread(target=sleeper)  # 建立執行緒

t = trader()
t.login()

t.subscribe(t.api.Contracts.Futures.TXF["TXF202110"])  # 訂閱臺指期-2021/10
t.subscribe(t.api.Contracts.Options.TX2.TX2202110016300C)  # 訂閱臺指選擇權10W2月 16300C

t.api.quote.set_quote_callback(t.quote_callback)  # 設定處理回報的功能

timer.start()  # 執行thread
timer.join()  # 等待結束thread

t.unsubscribe(t.api.Contracts.Futures.TXF["TXF202110"])  # 取消訂閱臺指期-2021/10
t.unsubscribe(t.api.Contracts.Options.TX2.TX2202110016300C)  # 取消訂閱臺指選擇權10W2月 16300C
```



- [**PositionAid.py**](https://gist.github.com/ypochien/ecc4abb7e18d21fc988c75a09e4df6e4#file-positionaid-py)
- https://gist.github.com/ypochien

```py
# 先透過 createPositionFromPnl 建立當下部位狀態，後面透過 Shioaji 成交回報 即時更新股票持倉部位

from loguru import logger
from dataclasses import dataclass
from typing import Optional, Dict, List
import math
import shioaji as sj
from shioaji.constant import OrderState, Action, StockOrderCond


@dataclass
class StockPosition:
    symbol: str
    action: Action
    quantity: int
    cost: int
    ordercond: StockOrderCond


class PositionAid:
    def __init__(self, api: sj.Shioaji):
        self.api = api
        self.api.set_order_callback(self.onOrderStatusChange)
        self.position: Dict[str, StockPosition] = {}

    def onOrderStatusChange(self, state: OrderState, data: Dict):
        if state == OrderState.TFTOrder:
            pass
        elif state == OrderState.TFTDeal:
            self.updatePosition(data)

    def createPositionFromPnl(self):
        """
        從 api list_position 損益建立 Position 資訊
        """
        all_pnl = self.api.list_positions()
        for pnl in all_pnl:
            position = StockPosition(
                symbol=pnl.code,
                action=pnl.direction,
                quantity=pnl.quantity,
                cost=math.floor(pnl.price * pnl.quantity * 1000),
                ordercond=pnl.cond,
            )
            self.position[position.symbol] = position

    def getAllPosition(self) -> List[StockPosition]:
        return list(self.position.values())

    def updatePosition(self, deal: Dict):
        code = deal["code"]
        action = deal["action"]
        order_cond = deal["order_cond"]
        quantity = deal["quantity"]
        cost = math.floor(deal["price"] * deal["quantity"] * 1000)

        position = self.getPosition(code)
        if position == None:
            position = StockPosition(
                symbol=code,
                action=action,
                quantity=quantity,
                cost=cost,
                ordercond=order_cond,
            )
        else:
            if position.action == action:
                position.quantity += quantity
                position.cost += cost
            else:
                position.quantity -= quantity
                position.cost -= cost
        self.position[code] = position
        logger.info(
            f"{code} {self.api.Contracts.Stocks[code].name} {action} {deal['price']} 元 {quantity}張  -> {position}"
        )

    def getPosition(self, code: str) -> Optional[StockPosition]:
        """code: 股票代碼
        透過 股票代碼 取得 StockPosition 資訊
        沒有此檔股票 則回傳 = None
        """
        return self.position.get(code, None)


if __name__ == "__main__":
    # 建立 Shioaji 並登入
    api = sj.Shioaji() 
    api.login("SJ_USER","SJ_PASSWORD")

    # 建立 PositionAid
    aid = PositionAid(api) # 自動接手 SJ 主動回報 並處理 成交資訊
    aid.createPositionFromPnl() # 從 api list_position 損益建立 Position 資訊
    
    aid.getPosition("2330") # 取得 2330 持倉資訊 (如果沒有 2330 則得到 None)

```



[**CancelAllOrder.py**](https://gist.github.com/ypochien/272f062d249e057322afbd6db0b51dce#file-cancelallorder-py)

```py
# 刪除全部的委託單
api.update_status()
for idx,t in enumerate(api.list_trades()):
    if t.status.status in [shioaji.constant.Status.PreSubmitted,shioaji.constant.Status.Submitted,shioaji.constant.Status.PartFilled] :
        api.cancel_order(t,timeout=0)
```

[**clear_all.py**](https://gist.github.com/ypochien/d0236f4b9b89bf74a392118066d40d4c)

```py
# 13:25之後用漲跌停價格反向出場
def clear_all():
    """13:25之後用漲跌停價格反向出場"""
    #只處理今天新增的現股 (現股當沖、不含興櫃)
    pnls = [one for one in api.list_positions() if abs(one.quantity) - one.yd_quantity!=0]
    for one_pnl in pnls:
        contract = api.Contracts.Stocks[one_pnl.code]
        if contract == None:
            print(f"無此商品 {one_pnl.code}")
            continue
        action = "Buy"
        price = contract.limit_up
        if one_pnl.direction=='Buy':
            action = "Sell"
            price = contract.limit_down
        quantity = abs(one_pnl.quantity) - one_pnl.yd_quantity
        if quantity > 0 and contract.exchange!="OES":
            order = api.Order(price=price, quantity=quantity, action=action, price_type="LMT", order_type="ROD", order_lot="Common",first_sell="false")
            for _ in range(0,quantity // 499):
                order.quantity = 499
                api.place_order(api.Contracts.Stocks[one_pnl.code],order)
                print(f"{one_pnl.code} {[pnl.pnl for pnl in pnls if pnl.code==one_pnl.code]} {order.action.value} {order.quantity} 張 {order.price} 元")
            left = quantity % 499
            if left > 0:
                order.quantity = left
                api.place_order(api.Contracts.Stocks[one_pnl.code],order)
                print(f"{one_pnl.code} {[pnl.pnl for pnl in pnls if pnl.code==one_pnl.code]} {order.action.value} {order.quantity} 張 {order.price} 元")
```





[永豐金API之30天不中斷Q&A 系列](https://ithelp.ithome.com.tw/users/20140938/ironman/4335)

