# bybit.py

import aiohttp
import asyncio
import async_timeout
import json
from aiohttp import WSMsgType
import traceback
import time
from datetime import datetime
import hmac
import hashlib
from requests import Request


class Bybit:

    # 定数
    TIMEOUT = 3600  # タイムアウト
    EXTEND_TOKEN_TIME = 3000  # アクセストークン延長までの時間
    SYMBOL = "BTCUSD"  # シンボル[BTCUSD]
    URLS = {
        "REST": "https://api.bybit.com",
        "WebSocket": "wss://stream.bybit.com/realtime",
    }
    PUBLIC_CHANNELS = [
        "trade." + SYMBOL,
        "orderBookL2_25." + SYMBOL,
        "instrument_info.100ms." + SYMBOL,
    ]

    PRIVATE_CHANNELS = ["position", "execution", "order", "stop_order"]

    # 変数
    api_key = ""
    api_secret = ""

    session = None  # セッション保持
    requests = []  # リクエストパラメータ
    heartbeat = 0

    # ------------------------------------------------ #
    # init
    # ------------------------------------------------ #
    def __init__(self, api_key, api_secret):
        # APIキー・SECRETをセット
        self.api_key = api_key
        self.api_secret = api_secret

    # ------------------------------------------------ #
    # async request for rest api
    # ------------------------------------------------ #

    def set_request(self, method, access_modifiers, target_path, params):
        if access_modifiers == "public":

            url = "".join([self.URLS["REST"], target_path])
            if method == "GET":
                headers = ""
                self.requests.append(
                    {
                        "method": method,
                        "access_modifiers": access_modifiers,
                        "target_path": target_path,
                        "url": url,
                        "params": params,
                        "headers": {},
                    }
                )

            if method == "POST":
                headers = {"Content-Type": "application/json"}
                self.requests.append(
                    {
                        "method": method,
                        "access_modifiers": access_modifiers,
                        "target_path": target_path,
                        "url": url,
                        "params": params,
                        "headers": headers,
                    }
                )

        if access_modifiers == "private":
            url = "".join([self.URLS["REST"], target_path])
            path = target_path

            timestamp = int((time.time()) * 1000)
            if method == "GET":
                url = "".join([url, "&api_key=", self.api_key])
                url = "".join([url, "&timestamp=", str(timestamp)])

                params["api_key"] = self.api_key
                params["timestamp"] = timestamp
                sign = ""
                for key in sorted(params.keys()):
                    v = params[key]
                    if isinstance(params[key], bool):
                        if params[key]:
                            v = "true"
                        else:
                            v = "false"
                    sign += key + "=" + str(v) + "&"
                sign = sign[:-1]
                signature = self.get_sign(sign)
                url = "".join([url, "&sign=", signature])

                headers = ""

                self.requests.append(
                    {
                        "url": url,
                        "method": method,
                        "headers": headers,
                        "params": params,
                    }
                )

            if method == "POST":
                headers = {"Content-Type": "application/json"}
                params["api_key"] = self.api_key
                params["timestamp"] = timestamp
                sign = ""
                for key in sorted(params.keys()):
                    v = params[key]
                    if isinstance(params[key], bool):
                        if params[key]:
                            v = "true"
                        else:
                            v = "false"
                    sign += key + "=" + str(v) + "&"
                sign = sign[:-1]

                signature = self.get_sign(sign)
                signature_real = {"sign": signature}
                body = json.dumps(dict(params, **signature_real))

                self.requests.append(
                    {"url": url, "method": method, "headers": headers, "params": body,}
                )

    def set_headers_for_private(self, timestamp, sign, params):
        headers = {
            "api_key": self.api_key,
            "symbol": self.SYMBOL,
            #'order_id':,
            "timestamp": timestamp,
            "sign": sign,
        }
        if len(params) > 0:
            headers["Content-Type"] = "application/json"
        return headers

    def get_payload(self, params):
        signature_payload = "".join(["{}".format(json.dumps(params))]).encode("utf-8")

        return signature_payload

    def get_sign(self, sign):
        signature = hmac.new(
            self.api_secret.encode("utf-8"), sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return signature

    async def fetch(self, request):
        status = 0
        content = []

        async with async_timeout.timeout(self.TIMEOUT):
            try:
                if self.session is None:
                    self.session = await aiohttp.ClientSession().__aenter__()
                if request["method"] is "GET":
                    async with self.session.get(
                        url=request["url"],
                        params=request["params"],
                        headers=request["headers"],
                    ) as response:
                        status = response.status
                        content = await response.read()
                        if status != 200:
                            # エラーのログ出力など必要な場合
                            pass

                elif request["method"] is "POST":
                    async with self.session.post(
                        url=request["url"],
                        data=request["params"],
                        headers=request["headers"],
                    ) as response:
                        status = response.status
                        content = await response.read()
                        if status != 200:
                            # エラーのログ出力など必要な場合
                            pass

                elif request["method"] is "PUT":
                    async with self.session.put(
                        url=request["url"],
                        data=request["params"],
                        headers=request["headers"],
                    ) as response:
                        status = response.status
                        content = await response.read()
                        if status != 200:
                            # エラーのログ出力など必要な場合
                            pass

                elif request["method"] is "DELETE":
                    async with self.session.delete(
                        url=request["url"],
                        data=request["params"],
                        headers=request["headers"],
                    ) as response:
                        status = response.status
                        content = await response.read()
                        if status != 200:
                            # エラーのログ出力など必要な場合
                            pass

                if len(content) == 0:
                    result = []

                else:
                    try:
                        result = json.loads(content.decode("utf-8"))
                    except Exception as e:
                        traceback.print_exc()

                return result

            except Exception as e:
                # セッション終了
                if self.session is not None:
                    await self.session.__aexit__(None, None, None)
                    await asyncio.sleep(0)
                    self.session = None

                traceback.print_exc()

    async def send(self):
        promises = [self.fetch(req) for req in self.requests]
        self.requests.clear()
        return await asyncio.gather(*promises)

    # ------------------------------------------------ #
    # REST API(Market Data Endpoints)
    # ------------------------------------------------ #
    # Orderbook
    # 確認済
    def orderbook(self):
        target_path = "".join(["/v2/public/orderBook/L2/?symbol=", self.SYMBOL])
        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Query Kline
    # 確認済
    def kline(self, interval, from_timestamp, limit=""):
        target_path = "".join(
            [
                "/v2/public/kline/list?symbol=",
                self.SYMBOL,
                "&interval=",
                str(interval),
                "&from=",
                str(from_timestamp),
            ]
        )
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])
        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Latest Information for Symbol
    # 確認済
    def ticker(self):
        target_path = "/v2/public/tickers"
        params = {"symbol": self.SYMBOL}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Public Trading Records
    # 確認済
    def trading_records(self, from_id="", limit=""):
        target_path = "".join(["/v2/public/trading-records?symbol=", self.SYMBOL])
        if len(str(from_id)) > 0:
            target_path = "".join([target_path, "&from=", str(from_id)])
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Query Symbol
    # 確認済
    def symbols(self):
        target_path = "/v2/public/symbols"
        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Liquidated Orders
    # 確認済
    def liq_records(self, from_id="", limit="", start_time="", end_time=""):
        target_path = "".join(["/v2/public/liq-records?symbol=", self.SYMBOL])

        if len(str(from_id)) > 0:
            target_path = "".join([target_path, "&from=", str(from_id)])
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])
        if len(str(start_time)) > 0:
            target_path = "".join([target_path, "&start_time=", str(start_time)])
        if len(str(end_time)) > 0:
            target_path = "".join([target_path, "&end_time=", str(end_time)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Query Mark Price Kline
    # 確認済
    def mark_price_kline(self, interval, from_timestamp, limit=""):
        target_path = "".join(
            [
                "/v2/public/mark-price-kline?symbol=",
                self.SYMBOL,
                "&interval=",
                str(interval),
                "&from=",
                str(from_timestamp),
            ]
        )

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Query index price kline
    # 確認済
    def index_price_kline(self, interval, from_timestamp, limit=""):
        target_path = "".join(
            [
                "/v2/public/index-price-kline?symbol=",
                self.SYMBOL,
                "&interval=",
                str(interval),
                "&from=",
                str(from_timestamp),
            ]
        )

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Query premium index kline
    # 確認済
    def premium_index_kline(self, interval, from_timestamp, limit=""):
        target_path = "".join(
            [
                "/v2/public/premium-index-kline?symbol=",
                self.SYMBOL,
                "&interval=",
                str(interval),
                "&from=",
                str(from_timestamp),
            ]
        )

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Open Interest
    # 確認済
    def open_interest(self, period, limit=""):
        target_path = "".join(
            ["/v2/public/open-interest?symbol=", self.SYMBOL, "&period=", str(period)]
        )

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Latest Big Deal
    # 確認済
    def big_deal(self, limit=""):
        target_path = "".join(["/v2/public/big-deal?symbol=", self.SYMBOL])

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # Long-Short Ratio
    # 確認済
    def account_ratio(self, period, limit=""):
        target_path = "".join(
            ["/v2/public/account-ratio?symbol=", self.SYMBOL, "&period=", period]
        )

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", str(limit)])

        params = {}
        self.set_request(
            method="GET",
            access_modifiers="public",
            target_path=target_path,
            params=params,
        )

    # ------------------------------------------------ #
    # REST API(Account Data Endpoints)
    # ------------------------------------------------ #

    # Place Active Order
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # side	            true	    string	    Side
    # symbol	        true	    string	    Symbol
    # order_type	    true	    string	    Active order type
    # qty	            true	    integer	    Order quantity in USD
    # price	            false	    number	    Order price
    # time_in_force	    true	    string	    Time in force
    # take_profit	    false	    number	    Take profit price, only take effect upon opening the position
    # stop_loss	        false	    number	    Stop loss price, only take effect upon opening the position
    # reduce_only	    false	    bool	    What is a reduce-only order? True means your position can only reduce in size if this order is triggered
    # close_on_trigger	false	    bool	    What is a close on trigger order? For a closing order. It can only reduce your position, not increase it. If the account has insufficient available balance when the closing order is triggered, then other active orders of similar contracts will be cancelled or reduced. It can be used to ensure your stop loss reduces your position regardless of current available margin.
    # order_link_id	    false	    string	    Customised order ID, maximum length at 36 characters, and order ID under the same agency has to be unique.
    def order_create(
        self,
        side,
        order_type,
        qty,
        price="",
        time_in_force="",
        take_profit="",
        stop_loss="",
        reduce_only=False,
        close_on_trigger=False,
        order_link_id="",
    ):
        target_path = "/v2/private/order/create"
        params = {
            "side": side,
            "symbol": self.SYMBOL,
            "order_type": order_type,
            "qty": qty,
            "time_in_force": time_in_force,
        }

        if len(str(price)) > 0:
            params["price"] = price
        if len(str(take_profit)) > 0:
            params["take_profit"] = take_profit
        if len(str(stop_loss)) > 0:
            params["stop_loss"] = stop_loss
        if len(str(reduce_only)) > 0:
            params["reduce_only"] = reduce_only
        if len(str(close_on_trigger)) > 0:
            params["close_on_trigger"] = close_on_trigger
        if len(str(order_link_id)) > 0:
            params["order_link_id"] = order_link_id

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Get Active Order
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # order_status	    false	    string	    Queries orders of all statuses if order_status not provided. If you want to query orders with specific statuses, you can pass the order_status split by ',' (eg Filled,New).
    # direction	        false	    string	    Search direction. prev: prev page, next: next page. Defaults to next
    # limit	            false	    integer	    Limit for data size per page, max size is 50. Default as showing 20 pieces of data per page
    # cursor	        false	    string	    Page turning mark. Use return cursor. Sign using origin data, in request please use urlencode
    def order_list(self, order_status="", direction="", limit="", cursor=""):
        target_path = "".join(["/v2/private/order/list?", "symbol=", self.SYMBOL])

        params = {"symbol": self.SYMBOL}

        if len(str(order_status)) > 0:
            target_path = "".join([target_path, "&order_status=", order_status])
            params["order_status"] = order_status
        if len(str(direction)) > 0:
            target_path = "".join([target_path, "&direction=", direction])
            params["direction"] = direction
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", limit])
            params["limit"] = limit
        if len(str(cursor)) > 0:
            target_path = "".join([target_path, "&cursor=", cursor])
            params["cursor"] = cursor

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Cancel Active Order
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # order_id	        false	    string	    Order ID. Required if not passing order_link_id
    # order_link_id	    false	    string	    Agency customized order ID. Required if not passing order_id
    def order_cancel(self, order_id="", order_link_id=""):
        target_path = "/v2/private/order/cancel"

        params = {"symbol": self.SYMBOL}

        if len(str(order_id)) > 0:
            params["order_id"] = order_id
        if len(str(order_link_id)) > 0:
            params["order_link_id"] = order_link_id

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Cancel All Active Orders
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    def order_cancelall(self):
        target_path = "/v2/private/order/cancelAll"

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Replace Active Order
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # order_id	        false	    string  	Your active order ID. The unique order ID returned to you when the corresponding active order was created
    # order_link_id	    false	    string	    Customised order ID, maximum length at 36 characters, and order ID under the same agency has to be unique.
    # symbol	        true	    string	    Symbol.
    # p_r_qty	        false	    string	    New order quantity. Do not pass this field if you don't want modify it
    # p_r_price	        false	    string	    New order price. Do not pass this field if you don't want modify it
    # ================================================================
    def order_replace(self, order_id="", order_link_id="", p_r_qty="", p_r_price=""):
        target_path = "/v2/private/order/replace"

        params = {"symbol": self.SYMBOL}

        if len(str(order_id)) > 0:
            params["order_id"] = order_id

        if len(str(order_link_id)) > 0:
            params["order_link_id"] = order_link_id

        if len(str(p_r_qty)) > 0:
            params["p_r_qty"] = p_r_qty

        if len(str(p_r_price)) > 0:
            params["p_r_price"] = p_r_price

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Query Active Order (real-time)
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # order_id	        false	    string	    Order ID. Required if not passing order_link_id
    # order_link_id	    false	    string	    Agency customized order ID. Required if not passing order_id
    # symbol	        true	    string	    Symbol
    # ================================================================
    def order(self, order_id="", order_link_id=""):
        target_path = "".join(["/v2/private/order?", "symbol=", self.SYMBOL])

        params = {"symbol": self.SYMBOL}

        if len(str(order_id)) > 0:
            target_path = "".join([target_path, "&order_id=", order_id])
            params["order_id"] = order_id
        if len(str(order_link_id)) > 0:
            target_path = "".join([target_path, "&order_link_id=", order_link_id])
            params["order_link_id"] = order_link_id

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Place Conditional Order
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # side	            true	    string	    Side
    # symbol	        true	    string	    Symbol
    # order_type	    true	    string	    Conditional order type
    # qty	            true	    string	    Order quantity in USD
    # price	            false	    string	    Execution price for conditional order. Required if you make limit price order
    # base_price	    true	    string	    It will be used to compare with the value of stop_px, to decide whether your conditional order will be triggered by crossing trigger price from upper side or lower side. Mainly used to identify the expected direction of the current conditional order.
    # stop_px	        true	    string	    Trigger price
    # time_in_force	    true	    string	    Time in force
    # trigger_by	    false	    string	    Trigger price type. Default LastPrice
    # close_on_trigger	false	    bool	    What is a close on trigger order? For a closing order. It can only reduce your position, not increase it. If the account has insufficient available balance when the closing order is triggered, then other active orders of similar contracts will be cancelled or reduced. It can be used to ensure your stop loss reduces your position regardless of current available margin.
    # order_link_id	    false	    string	    Customised order ID, maximum length at 36 characters, and order ID under the same agency has to be unique.
    # ================================================================
    def stop_order_create(
        self,
        side="",
        order_type="",
        qty="",
        price="",
        base_price="",
        stop_px="",
        time_in_force="",
        trigger_by="",
        close_on_trigger="",
        order_link_id="",
    ):
        target_path = "/v2/private/stop-order/create"

        params = {"symbol": self.SYMBOL}

        if len(str(side)) > 0:
            params["side"] = side

        if len(str(order_type)) > 0:
            params["order_type"] = order_type

        if len(str(qty)) > 0:
            params["qty"] = qty

        if len(str(price)) > 0:
            params["price"] = price

        if len(str(base_price)) > 0:
            params["base_price"] = base_price
        if len(str(stop_px)) > 0:
            params["stop_px"] = stop_px
        if len(str(time_in_force)) > 0:
            params["time_in_force"] = time_in_force
        if len(str(trigger_by)) > 0:
            params["trigger_by"] = trigger_by
        if len(str(close_on_trigger)) > 0:
            params["close_on_trigger"] = close_on_trigger
        if len(str(order_link_id)) > 0:
            params["order_link_id"] = order_link_id

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Get Conditional Order
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # stop_order_status	false	    string	    Queries orders of Untriggered,Active,Deactivated statuses if stop_order_status not provided. If you want to query orders with specific statuses, you can pass the stop_order_status split by ',' (eg Untriggered,Active)
    # direction	        false	    string	    Search direction. prev: prev page, next: next page. Defaults to next
    # limit	            false	    integer	    Limit for data size per page, max size is 50. Default as showing 20 pieces of data per page
    # cursor	        false	    string	    Page turning mark. Use return cursor. Sign using origin data, in request please use urlencode
    # ================================================================
    def stop_order_list(self, stop_order_status="", direction="", limit="", cursor=""):
        target_path = "/v2/private/stop-order/list"

        params = {"symbol": self.SYMBOL}

        if len(str(stop_order_status)) > 0:
            params["stop_order_status"] = stop_order_status

        if len(str(direction)) > 0:
            params["direction"] = direction

        if len(str(limit)) > 0:
            params["limit"] = limit

        if len(str(cursor)) > 0:
            params["cursor"] = cursor

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Cancel Conditional Order
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # stop_order_id	    false	    string	    Order ID. Required if not passing order_link_id
    # order_link_id	    false	    string	    Agency customized order ID. Required if not passing stop_order_id
    # ================================================================
    def stop_order_cancel(self, stop_order_id="", order_link_id=""):
        target_path = "/v2/private/stop-order/cancel"

        params = {"symbol": self.SYMBOL}

        if len(str(stop_order_id)) > 0:
            params["stop_order_id"] = stop_order_id

        if len(str(order_link_id)) > 0:
            params["order_link_id"] = order_link_id

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Cancel All Conditional Orders
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # ================================================================
    def stop_order_cancelall(self, stop_order_id="", order_link_id=""):
        target_path = "/v2/private/stop-order/cancelAll"

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Replace Conditional Order
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # stop_order_id	    false	    string	    Your conditional order ID. The unique order ID returned to you when the corresponding active order was created
    # order_link_id	    false	    string	    Customised order ID, maximum length at 36 characters, and order ID under the same agency has to be unique.
    # symbol	        true	    string	    Symbol.
    # p_r_qty	        false	    integer	    New order quantity. Do not pass this field if you don't want modify it
    # p_r_price	        false	    string	    New order price. Do not pass this field if you don't want modify it
    # p_r_trigger_price	false	    string	    New conditional order's trigger price or TP/SL order price, also known as stop_px. Do not pass this field if you don't want modify it
    # ================================================================
    def stop_order_replace(
        self,
        stop_order_id="",
        order_link_id="",
        p_r_qty="",
        p_r_price="",
        p_r_trigger_price="",
    ):
        target_path = "/v2/private/stop-order/replace"

        params = {"symbol": self.SYMBOL}

        if len(str(stop_order_id)) > 0:
            params["stop_order_id"] = stop_order_id

        if len(str(order_link_id)) > 0:
            params["order_link_id"] = order_link_id

        if len(str(p_r_qty)) > 0:
            params["p_r_qty"] = p_r_qty

        if len(str(p_r_price)) > 0:
            params["p_r_price"] = p_r_price

        if len(str(p_r_trigger_price)) > 0:
            params["p_r_trigger_price"] = p_r_trigger_price

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Query Conditional Order (real-time)　未実装
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # stop_order_id	    false	    string	    Order ID. Required if not passing order_link_id
    # order_link_id	    false	    string	    Agency customized order ID. Required if not passing order_id
    # ================================================================
    def stop_order(self, stop_order_id="", order_link_id=""):
        target_path = "".join(["/v2/private/stop-order?", "symbol=", self.SYMBOL])

        params = {"symbol": self.SYMBOL}

        if len(str(stop_order_id)) > 0:
            target_path = "".join([target_path, "&stop_order_id=", stop_order_id])
            params["stop_order_id"] = stop_order_id
        if len(str(order_link_id)) > 0:
            target_path = "".join([target_path, "&order_link_id=", order_link_id])
            params["order_link_id"] = order_link_id

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # My Position
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol.
    # ================================================================
    def position_list(self):
        target_path = "".join(["/v2/private/position/list?", "symbol=", self.SYMBOL])

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Change Margin
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # margin	        true	    string	    margin
    # ================================================================
    def change_position_margin(self, margin=""):
        target_path = "/v2/private/position/change-position-margin"

        params = {"symbol": self.SYMBOL}

        if len(str(margin)) > 0:
            params["margin"] = margin

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Set Trading-Stop
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # take_profit	    false	    number	    Cannot be less than 0, 0 means cancel TP
    # stop_loss	        false	    number	    Cannot be less than 0, 0 means cancel SL
    # trailing_stop	    false	    number	    Cannot be less than 0, 0 means cancel TS
    # tp_trigger_by	    false	    string	    take profit trigger price type，default: LastPrice
    # sl_trigger_by	    false	    string	    take profit trigger price type，default: LastPrice
    # new_trailing_active false	    number	    Trailing stop trigger price. Trailing stops are triggered only when the price reaches the specified price. Trailing stops are triggered immediately by default.
    # ================================================================
    def trading_stop(
        self,
        take_profit="",
        stop_loss="",
        trailing_stop="",
        tp_trigger_by="",
        sl_trigger_by="",
        new_trailing_active="",
    ):
        target_path = "/v2/private/position/trading-stop"

        params = {"symbol": self.SYMBOL}

        if len(str(take_profit)) > 0:
            params["take_profit"] = take_profit
        if len(str(stop_loss)) > 0:
            params["stop_loss"] = stop_loss
        if len(str(trailing_stop)) > 0:
            params["trailing_stop"] = trailing_stop
        if len(str(tp_trigger_by)) > 0:
            params["tp_trigger_by"] = tp_trigger_bymargin
        if len(str(sl_trigger_by)) > 0:
            params["sl_trigger_by"] = sl_trigger_by
        if len(str(new_trailing_active)) > 0:
            params["new_trailing_active"] = new_trailing_active

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Set Leverage
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # leverage	        true	    number	    Leverage. 0 means Cross Margin mode - any other value means Isolated Margin mode
    # ================================================================
    def leverage_save(self, leverage=""):
        target_path = "/v2/private/position/leverage/save"

        params = {"symbol": self.SYMBOL}

        if len(str(leverage)) > 0:
            params["leverage"] = leverage

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # User Trade Records
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # order_id	        false	    string	    OrderID. If not provided, will return user's trading records
    # symbol	        true	    string	    Contract type. Required
    # start_time	    false	    int	        Start timestamp point for result, in milliseconds
    # page	            false	    integer	    Page. By default, gets first page of data
    # limit	            false	    integer	    Limit for data size per page, max size is 200. Default as showing 50 pieces of data per page
    # order	            false	    string	    Sort orders by creation date
    # ================================================================
    def execution_list(self, order_id="", start_time="", page="", limit="", order=""):
        target_path = "".join(["/v2/private/execution/list?", "symbol=", self.SYMBOL])

        params = {"symbol": self.SYMBOL}

        if len(str(order_id)) > 0:
            target_path = "".join([target_path, "&order_id=", order_id])
            params["order_id"] = order_id
        if len(str(start_time)) > 0:
            target_path = "".join([target_path, "&start_time=", start_time])
            params["start_time"] = start_time
        if len(str(page)) > 0:
            target_path = "".join([target_path, "&page=", page])
            params["page"] = page
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", limit])
            params["limit"] = limit
        if len(str(order)) > 0:
            target_path = "".join([target_path, "&order=", order])
            params["order"] = order

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Closed Profit and Loss
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # start_time	    false	    int	        Start timestamp point for result, in seconds
    # end_time	        false	    int	        End timestamp point for result, in seconds
    # exec_type	        false	    string	    Execution type
    # page	            false	    integer	    Page. By default, gets first page of data. Maximum of 50 pages
    # limit	            false	    integer	    Limit for data size per page, max size is 50. Default as showing 20 pieces of data per page.
    # ================================================================
    def closed_pnl_list(
        self, start_time="", end_time="", exec_type="", page="", limit=""
    ):
        target_path = "".join(
            ["/v2/private/trade/closed-pnl/list?", "symbol=", self.SYMBOL]
        )

        params = {"symbol": self.SYMBOL}

        if len(str(start_time)) > 0:
            target_path = "".join([target_path, "&start_time=", start_time])
            params["start_time"] = start_time
        if len(str(end_time)) > 0:
            target_path = "".join([target_path, "&end_time=", end_timestart_time])
            params["end_time"] = end_time
        if len(str(exec_type)) > 0:
            target_path = "".join([target_path, "&exec_type=", exec_type])
            params["exec_type"] = exec_type
        if len(str(page)) > 0:
            target_path = "".join([target_path, "&page=", page])
            params["page"] = page
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "&limit=", limit])
            params["limit"] = limit

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Get Risk Limit
    #
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # ================================================================
    def risk_limit_list(
        self, start_time="", end_time="", exec_type="", page="", limit=""
    ):
        target_path = "/open-api/wallet/risk-limit/list?"

        params = {}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Set Risk Limit
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # risk_id	        true	    integer	    Risk ID.
    # ================================================================
    def risk_limit(self, risk_id=""):
        target_path = "/open-api/wallet/risk-limit"

        params = {"symbol": self.SYMBOL}

        if len(str(risk_id)) > 0:
            params["risk_id"] = risk_id

        self.set_request(
            method="POST",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Get the Last Funding Rate
    # 確認済？
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # ================================================================
    def prev_funding_rate(self):
        target_path = "".join(
            ["/v2/private/funding/prev-funding-rate?", "symbol=", self.SYMBOL]
        )

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # My Last Funding Fee
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # ================================================================
    def prev_funding(self):
        target_path = "".join(
            ["/v2/private/funding/prev-funding?", "symbol=", self.SYMBOL]
        )

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Predicted Funding Rate and My Funding Fee
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # ================================================================
    def predicted_funding(self):
        target_path = "".join(
            ["/v2/private/funding/predicted-funding?", "symbol=", self.SYMBOL]
        )

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # API Key Info
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # ================================================================
    def api_key_info(self):
        target_path = "/v2/private/account/api-key?"

        params = {}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # LCP Info
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # symbol	        true	    string	    Symbol
    # ================================================================
    def lcp_info(self):
        target_path = "".join(["/v2/private/account/lcp?", "symbol=", self.SYMBOL])

        params = {"symbol": self.SYMBOL}

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # ------------------------------------------------ #
    # REST API(Wallet Data Endpoints)
    # ------------------------------------------------ #

    # Get Wallet Balance
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # coin	            false	    string	    currency alias. Returns all wallet balances if not passed
    # ================================================================
    def wallet_balance(self, coin=""):
        target_path = "/v2/private/wallet/balance?"

        params = {}

        if len(str(coin)) > 0:
            target_path = "".join([target_path, "coin=", coin])
            params["coin"] = coin

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Wallet Fund Records
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # start_date	    false	    string	    Start point for result
    # end_date	        false	    string	    End point for result
    # currency	        false	    string	    Currency type
    # coin	            false	    string	    currency alias
    # wallet_fund_type	false	    string	    Wallet fund type
    # page	            false	    integer	    Page. By default, gets first page of data
    # limit	            false	    integer	    Limit for data size per page, max size is 50. Default as showing 20 pieces of data per page
    # ================================================================
    def wallet_fund_records(
        self,
        start_date="",
        end_date="",
        currency="",
        coin="",
        wallet_fund_type="",
        page="",
        limit="",
    ):
        target_path = "/v2/private/wallet/fund/records?"

        params = {}

        if len(str(start_date)) > 0:
            target_path = "".join([target_path, "start_date=", start_date])
            params["start_date"] = start_date
        if len(str(end_date)) > 0:
            target_path = "".join([target_path, "end_date=", end_date])
            params["end_date"] = end_date
        if len(str(currency)) > 0:
            target_path = "".join([target_path, "currency=", currency])
            params["currency"] = currency
        if len(str(coin)) > 0:
            target_path = "".join([target_path, "coin=", coin])
            params["coin"] = coin
        if len(str(wallet_fund_type)) > 0:
            target_path = "".join([target_path, "wallet_fund_type=", wallet_fund_type])
            params["wallet_fund_type"] = wallet_fund_type
        if len(str(page)) > 0:
            target_path = "".join([target_path, "page=", page])
            params["page"] = page
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "limit=", limit])
            params["limit"] = limit

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Withdraw Records
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # start_date	    false	    string	    Start point for result
    # end_date	        false	    string	    End point for result
    # coin	            false	    string	    Currency type
    # status	        false	    string	    Withdraw Status Enum
    # page	            false	    integer	    Page. By default, gets first page of data
    # limit	            false	    integer	    Limit for data size per page, max size is 50. Default as showing 20 pieces of data per page
    # ================================================================
    def wallet_withdraw_list(
        self, start_date="", end_date="", coin="", status="", page="", limit=""
    ):
        target_path = "/v2/private/wallet/withdraw/list?"

        params = {}

        if len(str(start_date)) > 0:
            target_path = "".join([target_path, "start_date=", start_date])
            params["start_date"] = start_date
        if len(str(end_date)) > 0:
            target_path = "".join([target_path, "end_date=", end_date])
            params["end_date"] = end_date
        if len(str(coin)) > 0:
            target_path = "".join([target_path, "coin=", coin])
            params["coin"] = coin
        if len(str(status)) > 0:
            target_path = "".join([target_path, "status=", status])
            params["status"] = status
        if len(str(page)) > 0:
            target_path = "".join([target_path, "page=", page])
            params["page"] = page
        if len(str(limit)) > 0:
            target_path = "".join([target_path, "limit=", limit])
            params["limit"] = limit

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # Asset Exchange Records
    # 確認済
    # ================================================================
    # Request Parameters
    # parameter	        required	type	    comments
    # ================================================================
    # limit	            false	    integer 	Limit for data size per page, max size is 50. Default as showing 20 pieces of data per page
    # from	            false	    integer	    Start ID. By default, returns the latest IDs
    # direction	        false	    string	    Search direction. Prev: searches in ascending order from start ID, Next: searches in descending order from start ID. Defaults to Next
    # ================================================================
    def wallet_exchange_order_list(self, limit="", from_id="", direction=""):
        target_path = "/v2/private/exchange-order/list?"

        params = {}

        if len(str(limit)) > 0:
            target_path = "".join([target_path, "limit=", limit])
            params["limit"] = limit
        if len(str(from_id)) > 0:
            target_path = "".join([target_path, "from_id=", from_id])
            params["from_id"] = from_id
        if len(str(direction)) > 0:
            target_path = "".join([target_path, "direction=", direction])
            params["direction"] = direction

        self.set_request(
            method="GET",
            access_modifiers="private",
            target_path=target_path,
            params=params,
        )

    # ------------------------------------------------ #
    # WebSocket
    # ------------------------------------------------ #
    async def ws_run(self, callback):
        # 変数
        end_point_public = self.URLS["WebSocket"]

        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                        end_point_public, receive_timeout=self.TIMEOUT
                    ) as client:

                        if (
                            len(self.PRIVATE_CHANNELS) > 0
                            and self.api_key != ""
                            and self.api_secret != ""
                        ):
                            result = await self.auth(client)
                            await self.subscribe(
                                client, "private", self.PRIVATE_CHANNELS
                            )

                        if len(self.PUBLIC_CHANNELS) > 0:
                            await self.subscribe(client, "public", self.PUBLIC_CHANNELS)

                        async for response in client:
                            if response.type != WSMsgType.TEXT:
                                print("response:" + str(response))
                                break
                            elif "error" in response[1]:
                                print(response[1])
                                break
                            elif "subscribed" in response[1]:
                                print(response[1])
                            elif '"success":true' in response[1]:
                                # heartbeat用タイム
                                self.heartbeat = time.time() + 30.0
                            else:
                                data = json.loads(response[1])
                                await self.handler(callback, data)

                            if self.heartbeat < time.time():
                                self.heartbeat = time.time() + 30.0
                                await self.ping(client)

            except Exception as e:
                print(e)
                print(traceback.format_exc().strip())
                await asyncio.sleep(10)

    # 購読
    async def subscribe(self, client, access_modifiers, channels):
        params = {"op": "subscribe", "args": channels}
        await asyncio.wait([client.send_str(json.dumps(params))])

    # 認証
    async def auth(self, client):
        try:
            timestamp = int((time.time() + 10.0) * 1000)
            signature = hmac.new(
                self.api_secret.encode(),
                "".join(["GET/realtime", str(timestamp)]).encode(),
                hashlib.sha256,
            ).hexdigest()

            params = {"op": "auth", "args": [self.api_key, timestamp, signature]}
            await asyncio.wait([client.send_str(json.dumps(params))])

            result = None

            return result

        except Exception as e:
            print(e)
            print(traceback.format_exc().strip())

    # ping
    async def ping(self, client):
        params = {"op": "ping"}
        await asyncio.wait([client.send_str(json.dumps(params))])

    # UTILS
    # コールバック、ハンドラー
    async def handler(self, func, *args):
        return await func(*args)
