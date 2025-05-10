#
# 從 FinMind 下載期貨 tick 資料
# 這部分把 tick 資料可以用來回測 小吳 和 小楊的東西
#

import numpy as np
import pandas as pd
import math

import datetime as datetime
import requests
import json
import time
import os
from os.path import isfile, join
from pandasql import sqldf

# set up sql df
pysqldf = lambda q: sqldf(q, globals())

daily_dataset = "TaiwanFuturesDaily"  # 期貨日K
tick_dataset = "TaiwanFuturesTick"  # 期貨tick
major3_dataset = "TaiwanFuturesInstitutionalInvestors"  # 期貨三大法人買賣表
index_5sec_dataset = "TaiwanStockEvery5SecondsIndex"  # 每5秒指數統計
twse_5sec_dataset = "TaiwanVariousIndicators5Seconds"  # 加權指數5秒
twse_order_5sec_dataset = (
    "TaiwanStockStatisticsOfOrderBookAndTrade"  # 每5秒委託成交統計
)
token = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMS0wNi0wNyA"
    "yMToyNTo1MSIsInVzZXJfaWQiOiJjYXJleWpvdSIsImlwIjoiMTAzLjIyNC4y"
    "MDEuOTUifQ.ncFRCARkaezyI711PlZtauprfDDSwg_7VNYgh8SDET0"
)

# 日常必做更新工作1 獲取某日的交易資料來更新歷史資料
daily_dataset = "TaiwanFuturesDaily"  # 期貨日K data_id TX
tick_dataset = "TaiwanFuturesTick"  # 期貨tick data_id TX
major3_dataset = "TaiwanFuturesInstitutionalInvestors"  # 期貨三大法人買賣表 data_id TX
index_5sec_dataset = "TaiwanStockEvery5SecondsIndex"  # 每5秒指數統計
twse_5sec_dataset = "TaiwanVariousIndicators5Seconds"  # 加權指數5秒 no data_id
twse_order_5sec_dataset = (
    "TaiwanStockStatisticsOfOrderBookAndTrade"  # 每5秒委託成交統計
)


def get_finMind_date_range(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    token,
    folder,
    dataset,
    bool_force_download=False,
):
    print(f"Download {dataset} to {folder} since {start_date} to {end_date}.")

    url = "https://api.finmindtrade.com/api/v4/data"

    if not os.path.exists(folder):
        os.makedirs(folder)
    folder_days = folder + "/days"
    if not os.path.exists(folder_days):
        os.makedirs(folder_days)

    # 修改這部分，增加對空目錄的檢查
    if bool_force_download is False:
        files = os.listdir(folder_days)
        if len(files) > 0:  # 確保文件列表不為空
            files.sort()
            start_date = datetime.datetime.strptime(files[-1][0:10], "%Y-%m-%d")
            # 將日期往後加一天，因為我們已經有了這一天的數據
            start_date = start_date + datetime.timedelta(days=1)
        # 如果為空，則使用原始的 start_date 值

    while start_date <= end_date:
        if start_date.weekday() > 5:
            start_date = start_date + datetime.timedelta(days=1)
            continue

        date = str(start_date.date())
        print(date, start_date.weekday())
        if dataset == daily_dataset or dataset == tick_dataset:
            parameter = {
                "dataset": dataset,
                "data_id": "TX",
                "start_date": date,
                "token": token,
            }
        elif dataset == major3_dataset:
            parameter = {
                "dataset": dataset,
                "data_id": "TX",
                "start_date": date,
                "end_date": date,
                "token": token,
            }
        else:
            parameter = {
                "dataset": dataset,
                "start_date": date,
                "token": token,
            }
        filepath = f"{folder_days}/{date}.csv"
        if os.path.isfile(filepath):
            start_date = start_date + datetime.timedelta(days=1)
            continue
        print(url, parameter)
        data = requests.get(url, params=parameter)
        # print(data)
        data = data.json()
        data = pd.DataFrame(data["data"])

        # 將每日所有股票當沖的資料存在TaiwanStockDayTrading/days的目錄中
        if data.shape[0] > 60 or (dataset == major3_dataset and data.shape[0] > 3):
            data.to_csv(filepath)
            print(f"success to save {filepath}, shape:{data.shape[0]}")
        else:
            if data.shape[0] > 0:
                print(f"fail to save {filepath}, shape:{data.shape[0]}")
            else:
                print(data)

        start_date = start_date + datetime.timedelta(days=1)


# dataset_list = [twse_5sec_dataset, tick_dataset, daily_dataset, major3_dataset, twse_order_5sec_dataset]
dataset_list = [tick_dataset]

# dataset_list = [twse_5sec_dataset, tick_dataset, daily_dataset, major3_dataset]
# dataset_list = [twse_order_5sec_dataset]

# start_date_str = '2020-06-04'
start_date_str = "2019-01-02"

start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.datetime.today()

for dataset in dataset_list:
    get_finMind_date_range(
        start_date,
        datetime.datetime.today(),
        token,
        dataset,
        dataset,
        bool_force_download=False,
    )
    # get_finMind_date_range(start_date, datetime.datetime.today(), token, dataset, dataset, bool_force_download=True)
