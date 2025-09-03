# sample.py

import asyncio
import traceback
from time import time
from datetime import datetime, timedelta
from collections import deque

from bybit import Bybit


class Sample:

    SYMBOL = "BTCUSD"  # シンボル[BTCUSD]
    # ---------------------------------------- #
    # init
    # ---------------------------------------- #
    def __init__(self, api_key, api_secret):
        self.bybit = Bybit(api_key=api_key, api_secret=api_secret)

        # タスクの設定およびイベントループの開始
        loop = asyncio.get_event_loop()
        tasks = [self.bybit.ws_run(self.realtime), self.run()]

        loop.run_until_complete(asyncio.wait(tasks))

    # ---------------------------------------- #
    # bot main
    # ---------------------------------------- #
    async def run(self):
        while True:
            await self.main()
            await asyncio.sleep(0)

    async def main(self):
        try:
            ## Orderbook
            # self.bybit.orderbook()
            # response = await self.bybit.send()

            ## Query Kline
            # from_timestamp=round(time()-10000)
            # print(from_timestamp)
            # self.bybit.kline(1, from_timestamp, 2)
            # response = await self.bybit.send()

            # Latest Information for Symbol
            # self.bybit.ticker()
            # response = await self.bybit.send()

            ## Public Trading Records
            # self.bybit.trading_records()
            # response = await self.bybit.send()

            ## Query Symbol
            # self.bybit.symbols()
            # response = await self.bybit.send()

            ## Liquidated Orders
            # self.bybit.liq_records()
            # response = await self.bybit.send()

            ## Query Mark Price Kline
            # from_timestamp=round(time()-10000)
            # print(from_timestamp)
            # self.bybit.mark_price_kline(1, from_timestamp, 2)
            # response = await self.bybit.send()

            ## Query index price kline
            #from_timestamp=round(time()-10000)
            #print(from_timestamp)
            #self.bybit.index_price_kline(1, from_timestamp, 2)
            #response = await self.bybit.send()

            ## Query premium index kline
            # from_timestamp=round(time()-10000)
            # print(from_timestamp)
            # self.bybit.premium_index_kline(1, from_timestamp, 2)
            # response = await self.bybit.send()

            ## Open Interest
            # self.bybit.open_interest('5min')
            # response = await self.bybit.send()

            ## Latest Big Deal
            # self.bybit.big_deal(5)
            # response = await self.bybit.send()

            ## Long-Short Ratio
            # self.bybit.account_ratio('5min',5)
            # response = await self.bybit.send()

            # Place Active Order
            # self.bybit.order_create(side='Buy', order_type='Limit', qty=10, price=30000, time_in_force='GoodTillCancel',)
            # response = await self.bybit.send()
            # print(response[0])
            # order_id = response[0]['result']['order_id']
            # await asyncio.sleep(5)

            ## Get Active Order
            # self.bybit.order_list()
            # response = await self.bybit.send()
            # print(response[0])

            ## Cancel Active Order
            # self.bybit.order_cancel(order_id=order_id)
            # response = await self.bybit.send()
            # print(response[0])

            ## Cancel All Active Orders
            # self.bybit.order_cancelall()
            # response = await self.bybit.send()
            # print(response[0])

            ## Replace Active Order
            # self.bybit.order_replace(order_id=order_id, p_r_qty=20)
            # response = await self.bybit.send()
            # print(response[0])

            ## Query Active Order
            # self.bybit.order(order_id=order_id)
            # response = await self.bybit.send()
            # print(response[0])

            ## My Position
            # self.bybit.position_list()
            # response = await self.bybit.send()
            # print(response[0])

            ## Change Margin
            # self.bybit.change_position_margin(4)
            # response = await self.bybit.send()
            # print(response[0])

            ## Set Leverage
            # self.bybit.leverage_save(10)
            # response = await self.bybit.send()
            # print(response[0])

            ## User Trade Records
            # self.bybit.execution_list()
            # response = await self.bybit.send()
            # print(response[0])

            ## Closed Profit and Loss
            # self.bybit.closed_pnl_list()
            # response = await self.bybit.send()
            # print(response[0])

            ## Get Risk Limit
            # self.bybit.risk_limit_list()
            # response = await self.bybit.send()
            # print(response[0])

            ## Set Risk Limit
            # self.bybit.risk_limit(1)
            # response = await self.bybit.send()
            # print(response[0])

            ## Get the Last Funding Rate
            # self.bybit.prev_funding_rate()
            # response = await self.bybit.send()
            # print(response[0])

            ## My Last Funding Fee
            # self.bybit.prev_funding()
            # response = await self.bybit.send()
            # print(response[0])

            ## Predicted Funding Rate and My Funding Fee
            # self.bybit.predicted_funding()
            # response = await self.bybit.send()
            # print(response[0])

            ## API Key Info
            # self.bybit.api_key_info()
            # response = await self.bybit.send()
            # print(response[0])

            ## LCP Info
            # self.bybit.lcp_info()
            # response = await self.bybit.send()
            # print(response[0])

            # Get Wallet Balance
            #self.bybit.wallet_balance()
            #response = await self.bybit.send()
            #print(response[0])

            ## Wallet Fund Records
            # self.bybit.wallet_fund_records()
            # response = await self.bybit.send()
            # print(response[0])

            ## Withdraw Records
            # self.bybit.wallet_withdraw_list()
            # response = await self.bybit.send()
            # print(response[0])

            ## Asset Exchange Records
            # self.bybit.wallet_exchange_order_list()
            # response = await self.bybit.send()
            # print(response[0])

            await asyncio.sleep(10)

        except Exception as e:
            print(e)
            print(traceback.format_exc().strip())

    # リアルタイムデータの受信
    async def realtime(self, response):
        # websocketから配信される情報を表示
        if response["topic"] == "trade." + self.SYMBOL:
            # trade
            print(response)
        if response["topic"] == "orderBookL2_25." + self.SYMBOL:
            # orderBookL2_25
            print(response)
        if response["topic"] == "instrument_info.100ms." + self.SYMBOL:
            # instrument_info
            print(response)
        if response["topic"] == "position":
            # private position
            print(response)
        if response["topic"] == "execution":
            # private execution
            print(response)
        if response["topic"] == "order":
            # private order
            print(response)
        if response["topic"] == "stop_order":
            # private stop_order
            print(response)


# --------------------------------------- #
# main
# --------------------------------------- #
if __name__ == "__main__":

    api_key = ""  # api_keyを入力
    api_secret = ""  # api_secretを入力

    Sample(api_key=api_key, api_secret=api_secret)
