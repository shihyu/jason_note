import ssl
import time
import typing

import pandas as pd
import requests
import urllib3
from loguru import logger

from visualization.config import FINMIND_API_TOKEN


def request_get(
    url: str, params: typing.Dict[str, typing.Union[int, str, float]], timeout: int,
):
    for i in range(10):
        try:
            response = requests.get(url, verify=True, params=params, timeout=timeout)
            break
        except requests.Timeout as exc:
            raise Exception("Timeout")
        except (
            requests.ConnectionError,
            ssl.SSLError,
            urllib3.exceptions.ReadTimeoutError,
            urllib3.exceptions.ProtocolError,
        ) as exc:
            logger.warning(f"{exc}, retry {i} and sleep {i * 0.1} seonds")
            time.sleep(i * 0.1)
    if response.json()["msg"] == "success" and response.status_code == 200:
        pass
    else:
        logger.error(params)
        logger.error(response.json()["msg"])
    return response.json()


def reach_api_limit(msg: str) -> bool:
    return "Requests reach the upper limit" in msg


class FinMindApi:
    def __init__(self):
        self.token = FINMIND_API_TOKEN
        self.url = "https://api.finmindtrade.com/api/v4/data"
        self._taiwan_stock_id_list = list()

    def get_taiwan_stock_id_list(self):
        parameter = {"dataset": "TaiwanStockInfo", "token": self.token}
        resp = requests.get(self.url, params=parameter)
        data = resp.json()
        data = pd.DataFrame(data["data"])
        data = data[data["industry_category"] != "Index"]
        stock_id_list = list(set(data["stock_id"]))
        return stock_id_list

    @property
    def taiwan_stock_id_list(self):
        if len(self._taiwan_stock_id_list) == 0:
            self._taiwan_stock_id_list = self.get_taiwan_stock_id_list()
        return self._taiwan_stock_id_list

    def clear_data(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in ["link", "note"]:
            if col in df.columns:
                df = df.drop(col, axis=1)
        return df

    def get_data(self, dataset: str, data_id: str, start_date: str, end_date: str):
        parameter = {
            "dataset": dataset,
            "data_id": data_id,
            "start_date": start_date,
            "end_date": end_date,
            "token": self.token,  # 參考登入，獲取金鑰
        }
        data = request_get(url=self.url, params=parameter, timeout=30)
        if reach_api_limit(msg=data.get("msg", "")):
            time.sleep(60 * 10)
            df = self.get_data(
                dataset=dataset,
                data_id=data_id,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            df = pd.DataFrame(data.get("data", dict()))
            df = self.clear_data(df)
        return df
