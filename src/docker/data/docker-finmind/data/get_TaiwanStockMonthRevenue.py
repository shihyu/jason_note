from finlab import data as finlab_data
from Jlab.utils import (
    get_github_repo,
    update_file,
)
from clickhouse_driver import Client
import numpy as np
import finlab
import requests
import pandas as pd
import time
import pandahouse as ph
import sqlite3
import os


class FinmindAPI:
    db_path = "finance.db"

    def __init__(self, token):
        self.token = token

    def api_info(self):
        api_info_url = "https://api.web.finmindtrade.com/v2/user_info"
        api_info_payload = {"token": self.token}
        api_info_resp = requests.get(api_info_url, params=api_info_payload)
        return api_info_resp.json()

    def get_finmind_data(self, dataset, data_id, start_date):
        api_info_dict = self.api_info()
        user_count = api_info_dict["user_count"]
        api_request_limit = api_info_dict["api_request_limit"]
        print(f"API requests left: {api_request_limit - user_count}")

        if user_count < api_request_limit:
            # 使用普通 API 獲取數據
            url = "https://api.finmindtrade.com/api/v4/data"
            parameter = {
                "dataset": dataset,
                "data_id": data_id,
                "start_date": start_date,
                "token": self.token,
            }

            time.sleep(0.2)
            data = requests.get(url, params=parameter)
            while data.status_code != 200:
                print(f"Failed to get response, retrying after 20 minutes...")
                time.sleep(1200)
                data = requests.get(url, params=parameter)

            data = pd.DataFrame(data.json()["data"])
            return data

        else:
            print(f"API request limit reached, waiting for 20 minutes...")
            time.sleep(1800)
            return self.get_finmind_data(dataset, data_id, start_date)

    @staticmethod
    def create_table_from_df(client, df, database_name, table_name):
        # define ClickHouse data types for each Pandas data type
        ch_type_convert_dict = {
            np.dtype("datetime64[ns]"): "DateTime",
            np.dtype("int64"): "Int64",
            np.dtype("float64"): "Float64",
            np.dtype("object"): "String",
            np.dtype("bool"): "UInt8",
        }

        # create table schema from DataFrame columns and data types
        columns = []
        for col_name, dtype in df.dtypes.items():
            ch_type = ch_type_convert_dict.get(dtype, "String")
            columns.append(f"{col_name} {ch_type}")
        schema = ", ".join(columns)

        # create ClickHouse client and check if table exists
        client.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        table_exists = client.execute(f"EXISTS TABLE {database_name}.{table_name}")

        # create table if it doesn't exist
        if not table_exists:
            client.execute(
                f"CREATE TABLE {database_name}.{table_name} ({schema}) ENGINE = MergeTree ORDER BY (date, stock_id) SETTINGS index_granularity = 8192"
            )

    @staticmethod
    def get_data(client, sql):
        data = client.execute_iter(sql, with_column_types=True)
        columns = [column[0] for column in next(data)]
        return pd.DataFrame.from_records(data, columns=columns)

    @staticmethod
    def update_db_to_github():
        repo = get_github_repo(os.getenv("GITHUB_TOKEN"), "data")
        update_file(repo, "finance.db")


def compare_data(finmind_api):
    # 取得股票資料
    data = finmind_api.get_stock_data(stock_id="2330")

    # 取得當月營收和去年同月增減(%)
    rev = finlab_data.get("monthly_revenue:當月營收")
    rev_year_growth = finlab_data.get("monthly_revenue:去年同月增減(%)")

    # 將股票資料推送到 GitHub
    finmind_api.update_db_to_github()

    # 取得上月比較增減(%)
    rev_month_growth = finlab_data.get("monthly_revenue:上月比較增減(%)")

    # 顯示結果
    print(data, rev["2330"], rev_year_growth["2330"], rev_month_growth["2330"])


if __name__ == "__main__":
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMy0wNC0wMyAxOTo1ODoyOSIsInVzZXJfaWQiOiJ5YW9zaGloeXUiLCJpcCI6IjU4LjExNC4yMi4xNDYifQ.BjoBlPla2vY0W8y3i_2m_VGtGbef0SW2r-2KjPaBOfQ"
    finmind_api = FinmindAPI(token=token)
    finlab.login(
        "dyrZWjkJWYCrHnLrnfj3kI7BCTw/jLBDHfsAc7RI8EwcUs/+dv70ktgffV867g9v#vip_m"
    )
    # compare_data(finmind_api)
    # input()

    # 獲取台灣股票資訊
    dataset = "TaiwanStockInfo"
    parameter = {"dataset": dataset, "token": token}
    resp = requests.get("https://api.finmindtrade.com/api/v4/data", params=parameter)

    if resp.status_code == 200:
        data = pd.DataFrame(resp.json()["data"])
        four_digits_condition = data["stock_id"].astype(str).str.len() == 4
        range_condition = (data["stock_id"] >= "1101") & (data["stock_id"] <= "9962")
        filtered_data = data.loc[four_digits_condition & range_condition]
        print(filtered_data)

        client = Client(host="localhost", port="9911")
        dataset = "TaiwanStockMonthRevenue"
        data_ids = filtered_data["stock_id"].tolist()
        start_date = "1900-01-01"
        str_database = "TaiwanStockInfo"
        str_table = "stock_monthly_revenue"
        connection = dict(database=str_database, host="http://127.0.0.1:1121/",)
        finmind_api.create_table_from_df(client, data, str_database, str_table)

        # data = finmind_api.get_data(client, f"SELECT * FROM {str_database}.{str_table} WHERE date >= '2023-04-01' and stock_id = '{data_ids[0]}'")
        db_df = finmind_api.get_data(client, f"SELECT * FROM {str_database}.{str_table} WHERE stock_id = '{data_ids[0]}'")
        print(db_df, db_df.dtypes)
        input()

        for data_id in data_ids:
            data = finmind_api.get_finmind_data(dataset, data_id, start_date)
            if not data.empty:
                print(data.dtypes)
                input()
                diff = data - db_df
                print(diff)
                input()
                input()
                input()

                ph.to_clickhouse(
                    data,
                    str_table,
                    index=False,
                    chunksize=100000,
                    connection=connection,
                )

    #        finmind_api.insert_db(data)
    #        print(data)

    # 獲取股票 1101 的月營收資料
    # data = finmind_api.get_stock_data(stock_id="1101")
    # print(data)
