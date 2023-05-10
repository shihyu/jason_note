from line_notify import LineNotify
from loguru import logger
from clickhouse_driver import Client
from multiprocessing import Process, Queue, Pipe
import signal
import multiprocessing
import rel
import numpy as np
import pandahouse as ph
import pandas as pd
import json
import websocket
import datetime as dt
import os
import sys
import traceback
import time


def monitor(monitor_queue, thread_name, ws_client_p, record_p):
    while True:
        try:
            data = monitor_queue.get(timeout=30)
            logger.info(f"{thread_name}, {os.getpid()}, {data[0]}")
        except Exception as e:
            logger.warning(f"{thread_name} monitor queue is empty, {e}")
            LineNotify("KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz").send(
                f"{thread_name} monitor queue is empty"
            )
            os.kill(ws_client_p.pid, signal.SIGUSR1)


def getErrMsg(e):
    error_class = e.__class__.__name__  # 取得錯誤類型
    detail = e.args[0]  # 取得詳細內容
    cl, exc, tb = sys.exc_info()  # 取得Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
    fileName = lastCallStack[0]  # 取得發生的檔案名稱
    lineNum = lastCallStack[1]  # 取得發生的行號
    funcName = lastCallStack[2]  # 取得發生的函數名稱
    errMsg = 'File "{}", line {}, in {}: [{}] {}'.format(
        fileName, lineNum, funcName, error_class, detail
    )
    return errMsg


logger.add(
    f"{__file__}.log", encoding="utf-8", enqueue=True, retention="10 days",
)


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


class WebSocketClient(multiprocessing.Process):
    def __init__(
        self, thread_name, ws_url, symbol, params, queue, monitor_queue, line_notify
    ):
        multiprocessing.Process.__init__(self)
        self.__thread_name = thread_name
        self.__ws_url = ws_url
        self.__symbol = symbol
        self.__params = params
        self.__queue = queue
        self.__monitor_queue = monitor_queue
        self.__line_notify = line_notify
        self.__ws = websocket.WebSocketApp(
            self.__ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error,
            # on_cont_message=self.on_cont_message,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
        )
        self.msg_count = 0
        self.reconnecting_flag = False
        signal.signal(signal.SIGUSR1, self.receive_signal)

    def receive_signal(self, signum, stack):
        logger.warning(
            f"Received:, {signum}, {os.getpid()}, reconnecting_flag:{self.reconnecting_flag}"
        )
        # if not self.reconnecting_flag:
        #    self.reconnecting_flag = True
        #    self.reconnecting()
        # thread = threading.Thread(target=self.reconnecting, args=())
        # thread.start()

    def run(self):
        # self.__ws.run_forever()
        try:
            self.__ws.run_forever(ping_interval=0, dispatcher=rel, reconnect=3)
            rel.signal(2, rel.abort)  # Keyboard Interrupt
            rel.dispatch()
        except Exception as e:
            logger.exception(e)
            # os.kill(os.getpid(), signal.SIGUSR1)
            self.reconnecting()

    def on_open(self, ws):
        logger.info(f"on_pong : {self.reconnecting_flag}")
        self.reconnecting_flag = False
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [self.__params],
            "id": 1,
        }
        ws.send(json.dumps(subscribe_message))

    def on_message(self, ws, message):
        if self.__queue.full():
            logger.error("queue is full")
            self.__line_notify.send("queue is full")
        else:
            msg = json.loads(message)
            self.__queue.put(msg)
            self.msg_count = self.msg_count + 1

        if self.msg_count % 20 == 0:
            self.__monitor_queue.put([dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            logger.info(
                f"{self.__thread_name} msg_count:{self.msg_count} qsize:{self.__queue.qsize()}"
            )
            self.msg_count = 0

        # print(json.dumps(msg, indent=4, ensure_ascii=False))

    def on_close(self, ws, status_code, message):
        logger.warning(f"on_close {status_code} {message}")
        self.__line_notify.send("on_close " + str(message))
        self.reconnecting()

    def on_error(self, ws, error):
        logger.error(str(error))
        self.__line_notify.send("on_error " + str(error))
        # self.reconnecting()

    def on_cont_message(self, ws, message, flag):
        logger.warning(f"on_cont_message: {message} {flag}")

    def on_ping(self, ws, message):
        logger.info(f"{self.__thread_name} on_ping")
        ws.send(message, websocket.ABNF.OPCODE_PONG)

    def on_pong(self, ws, message):
        logger.info(f"{self.__thread_name} on_pong")
        ws.send(message, websocket.ABNF.OPCODE_PONG)

    def reconnecting(self):
        logger.info(f"{self.__thread_name} {os.uname()[1]} reconnecting")
        # self.__ws.close()
        # thread = threading.Thread(target=self.__ws.close, args=())
        # thread.start()
        # thread.join()

        # self.__ws.my_close()
        # rel.abort()
        # logger.info(f"{self.__thread_name} websocket closed")

        rel.abort()
        self.__ws.run_forever(ping_interval=0, dispatcher=rel, reconnect=3)
        rel.signal(2, rel.abort)
        rel.dispatch()


class Record(multiprocessing.Process):
    def __init__(self, thread_name, ws_client_p, queue, line_notify):
        multiprocessing.Process.__init__(self)
        self.__thread_name = thread_name
        self.__ws_client_p = ws_client_p
        self.__queue = queue
        self.__line_notify = line_notify
        self.__data = []

    def clear_data(self):
        self.__data.clear()

    def create_db_table(self, df, str_database, str_table):
        dtypes_dict = dict(df.dtypes)
        ch_type_convert_dict = {
            np.dtype("datetime64[ns]"): "Datetime64",
            np.dtype("int64"): "Int64",
            np.dtype("float64"): "Float64",
            np.dtype("object"): "String",
            np.dtype("bool"): "Bool",
        }
        create_table_cmd_str = ""
        for x in dtypes_dict:
            type_str = ch_type_convert_dict.get(dtypes_dict[x], None)
            if type_str is None:
                print(f"Undefined type {dtypes_dict[x]}")
            create_table_cmd_str = (
                create_table_cmd_str + f"`{x}` {type_str} DEFAULT 0, "
            )
        # create_table_cmd_str = f"CREATE TABLE IF NOT EXISTS {str_database}.{str_table} ( {create_table_cmd_str[:-2]}) ENGINE = Log"
        create_table_cmd_str = f"CREATE TABLE IF NOT EXISTS {str_database}.{str_table} ({create_table_cmd_str[:-2]}) ENGINE = MergeTree PARTITION BY year_month_day ORDER BY year_month_day SETTINGS index_granularity = 16384"
        client = Client(host="clickhouse-server", port="9000", user="halobug", password="FcP5O5HY")
        client.execute(f"CREATE DATABASE IF NOT EXISTS {str_database};")
        client.execute(create_table_cmd_str)

    def write_orderbook_to_db(self):
        df = None
        try:
            if "e" in self.__data[0].keys() and self.__data[0]["e"] == "depthUpdate":
                df = pd.DataFrame(self.__data)
                if not df.isnull().values.any():
                    df.rename(
                        columns={"E": "timestamp", "a": "asks", "b": "bids"},
                        inplace=True,
                    )
                    df["date"] = [
                        dt.datetime.fromtimestamp(x / 1000.0) for x in df["timestamp"]
                    ]
                    df["year_month_day"] = [
                        dt.datetime.fromtimestamp(x / 1000.0).strftime("%Y-%m-%d")
                        for x in df["timestamp"]
                    ]
                    df.rename(columns={"s": "pair"}, inplace=True)
                    # 僅保留需要的列
                    df = df[["pair", "asks", "bids", "date", "year_month_day"]]

                    db_name = "CRYPTO"
                    table_name = "BinanceOrderbookPartition_simplifiedFields"
                    connection_info = dict(
                        database=db_name,
                        host="http://clickhouse-server:8123/",
                        user="halobug",
                        password="FcP5O5HY",
                    )

                    self.create_db_table(df, db_name, table_name)
                    ph.to_clickhouse(
                        df,
                        table_name,
                        index=False,
                        chunksize=100000,
                        connection=connection_info,
                    )
                print(df)

            if (
                "event" in self.__data[0].keys()
                and self.__data[0]["event"] == "ORDER_BOOK"
            ):
                df = pd.DataFrame(self.__data)
                if not df.isnull().values.any():
                    df["date"] = [
                        dt.datetime.fromtimestamp(x / 1000.0).strftime(
                            "%Y-%m-%d %H:%M:%S.%f"
                        )
                        for x in df["timestamp"]
                    ]
                    df["year_month_day"] = [
                        dt.datetime.fromtimestamp(x / 1000.0).strftime("%Y-%m-%d")
                        for x in df["timestamp"]
                    ]

                    df = df[["pair", "asks", "bids", "date", "year_month_day"]]
                    db_name = "CRYPTO"
                    table_name = "BitoProOrderbookPartition_simplifiedFields"
                    connection_info = dict(
                        database=db_name,
                        host="http://clickhouse-server:8123/",
                        user="halobug",
                        password="FcP5O5HY",
                    )

                    self.create_db_table(df, db_name, table_name)
                    ph.to_clickhouse(
                        df,
                        table_name,
                        index=False,
                        chunksize=100000,
                        connection=connection_info,
                    )
                print(df)
            self.__data.clear()
        except Exception as e:
            logger.error(df)
            self.__data.clear()
            self.__line_notify.send(getErrMsg(e))
            logger.exception(e)
            os.kill(self.__ws_client_p.pid, signal.SIGUSR1)

    def run(self):
        while True:
            try:
                msg = self.__queue.get(block=True)
                self.__data.append(msg)
                if len(self.__data) > 100:
                    self.write_orderbook_to_db()
            except Exception as e:
                self.__line_notify.send(getErrMsg(e))
                logger.exception(e)


class Manager(multiprocessing.Process):
    def __init__(self, thread_name, ws_url, symbol, params, queue, line_token):
        # threading.Thread.__init__(self)
        multiprocessing.Process.__init__(self)
        self.__thread_name = thread_name
        self.__ws_url = ws_url
        self.__symbol = symbol
        self.__params = params
        self.__queue = queue
        self.__line_notify = LineNotify(line_token)

    def run(self):
        self.__line_notify.send(f"thread_name:{self.__thread_name}")
        monitor_queue = Queue(100)
        ws_client_p = WebSocketClient(
            thread_name=self.__thread_name,
            ws_url=self.__ws_url,
            symbol=self.__symbol,
            params=self.__params,
            queue=self.__queue,
            monitor_queue=monitor_queue,
            line_notify=self.__line_notify,
        )
        record_p = Record(
            thread_name=self.__thread_name,
            ws_client_p=ws_client_p,
            queue=self.__queue,
            line_notify=self.__line_notify,
        )
        tasks = [
            ws_client_p,
            record_p,
        ]
        for t in tasks:
            t.start()

        monitor_task = Process(
            target=monitor,
            args=(monitor_queue, self.__thread_name, ws_client_p, record_p),
        )
        monitor_task.start()

        for task in tasks:
            task.join()


if __name__ == "__main__":
    Watcher()
    bitopro_orderbook_queue = Queue(1000)
    binance_orderbook_queue = Queue(1000)
    tasks = [
        Manager(
            thread_name="BitoPro Thread",
            ws_url="wss://stream.bitopro.com:9443/ws/v1/pub/order-books/BTC_USDT:20",
            symbol="",
            params="",
            queue=bitopro_orderbook_queue,
            line_token="KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz",
        ),
        Manager(
            thread_name="Binance Thread",
            ws_url="wss://stream.binance.com:9443/ws",
            symbol="",
            params="btcusdt@depth@100ms",
            queue=binance_orderbook_queue,
            line_token="KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz",
        ),
    ]
    for t in tasks:
        t.start()

    for task in tasks:
        task.join()

