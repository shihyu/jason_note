"""
期貨資料下載工具 - 從 FinMind 下載期貨相關資料

此程式提供從 FinMind API 下載各種期貨相關資料的功能，包括期貨日K、期貨tick數據、
三大法人買賣表等，並將數據保存為 CSV 文件。
"""

import datetime
import os
from typing import Dict, Optional

import pandas as pd
import requests

# API設定
API_URL = "https://api.finmindtrade.com/api/v4/data"
API_TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMS0wNi0wNyA"
    "yMToyNTo1MSIsInVzZXJfaWQiOiJjYXJleWpvdSIsImlwIjoiMTAzLjIyNC4y"
    "MDEuOTUifQ.ncFRCARkaezyI711PlZtauprfDDSwg_7VNYgh8SDET0"
)

# 資料集定義
DATASET_CONFIG = {
    "TaiwanFuturesDaily": {  # 期貨日K
        "requires_data_id": True,
        "default_data_id": "TX",
        "min_data_points": 60,
    },
    "TaiwanFuturesTick": {  # 期貨tick
        "requires_data_id": True,
        "default_data_id": "TX",
        "min_data_points": 60,
    },
    "TaiwanFuturesInstitutionalInvestors": {  # 期貨三大法人買賣表
        "requires_data_id": True,
        "default_data_id": "TX",
        "min_data_points": 3,
        "requires_end_date": True,
    },
    "TaiwanStockEvery5SecondsIndex": {  # 每5秒指數統計
        "requires_data_id": False,
        "min_data_points": 60,
    },
    "TaiwanVariousIndicators5Seconds": {  # 加權指數5秒
        "requires_data_id": False,
        "min_data_points": 60,
    },
    "TaiwanStockStatisticsOfOrderBookAndTrade": {  # 每5秒委託成交統計
        "requires_data_id": False,
        "min_data_points": 60,
    },
}


def create_directories(folder_path: str) -> str:
    """
    創建所需的目錄結構

    Args:
        folder_path: 主目錄路徑

    Returns:
        日期數據保存的子目錄路徑
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folder_days = os.path.join(folder_path, "days")
    if not os.path.exists(folder_days):
        os.makedirs(folder_days)

    return folder_days


def get_latest_date_from_files(folder_days: str) -> Optional[datetime.datetime]:
    """
    從目錄中找出最新的文件日期

    Args:
        folder_days: 含有日期文件的目錄

    Returns:
        最新的日期或None（如果沒有文件）
    """
    files = os.listdir(folder_days)
    if not files:
        return None

    files.sort()
    latest_date = datetime.datetime.strptime(files[-1][0:10], "%Y-%m-%d")
    # 將日期往後加一天，因為我們已經有了這一天的數據
    return latest_date + datetime.timedelta(days=1)


def build_api_parameters(dataset: str, date: str, token: str) -> Dict:
    """
    根據數據集類型構建API參數

    Args:
        dataset: 數據集名稱
        date: 日期字符串 (YYYY-MM-DD)
        token: API令牌

    Returns:
        API請求參數字典
    """
    config = DATASET_CONFIG.get(dataset, {})
    params = {"dataset": dataset, "start_date": date, "token": token}

    # 添加數據ID（如果需要）
    if config.get("requires_data_id", False):
        params["data_id"] = config.get("default_data_id", "TX")

    # 添加結束日期（如果需要）
    if config.get("requires_end_date", False):
        params["end_date"] = date

    return params


def save_data(data: pd.DataFrame, filepath: str, dataset: str) -> bool:
    """
    保存數據到CSV文件，如果數據點數量足夠

    Args:
        data: 要保存的數據框
        filepath: 保存路徑
        dataset: 數據集名稱

    Returns:
        是否成功保存
    """
    config = DATASET_CONFIG.get(dataset, {})
    min_points = config.get("min_data_points", 60)

    if data.shape[0] >= min_points:
        data.to_csv(filepath)
        print(f"成功保存 {filepath}, 數據量:{data.shape[0]}")
        return True
    else:
        if data.shape[0] > 0:
            print(
                f"無法保存 {filepath}, 數據量不足:{data.shape[0]} (需要至少 {min_points})"
            )
        else:
            print(f"無數據: {data}")
        return False


def download_data(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    token: str,
    dataset: str,
    force_download: bool = False,
) -> None:
    """
    下載指定日期範圍內的數據

    Args:
        start_date: 開始日期
        end_date: 結束日期
        token: API令牌
        dataset: 數據集名稱
        force_download: 是否強制從起始日期下載，忽略已有數據
    """
    print(f"下載 {dataset} 資料，從 {start_date} 到 {end_date}")

    # 創建目錄
    folder_days = create_directories(dataset)

    # 如果不強制下載且已有數據文件，從最新日期開始
    if not force_download:
        latest_date = get_latest_date_from_files(folder_days)
        if latest_date:
            start_date = latest_date
            print(f"找到現有數據，從 {start_date} 開始下載")

    # 開始下載
    current_date = start_date
    while current_date <= end_date:
        # 跳過週末
        if current_date.weekday() >= 6:  # 6=週六, 0=週一
            current_date += datetime.timedelta(days=1)
            continue

        date_str = str(current_date.date())
        print(f"處理日期: {date_str}, 星期 {current_date.weekday() + 1}")

        # 檢查文件是否已存在
        filepath = os.path.join(folder_days, f"{date_str}.csv")
        if os.path.isfile(filepath):
            print(f"文件已存在: {filepath}，跳過")
            current_date += datetime.timedelta(days=1)
            continue

        # 構建API參數並發送請求
        params = build_api_parameters(dataset, date_str, token)
        print(f"API請求: {API_URL} {params}")

        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()  # 檢查HTTP錯誤

            data = response.json()
            if "data" not in data:
                print(f"API回應無數據: {data}")
                current_date += datetime.timedelta(days=1)
                continue

            df = pd.DataFrame(data["data"])
            if not df.empty:
                save_data(df, filepath, dataset)

        except requests.exceptions.RequestException as e:
            print(f"請求錯誤: {e}")
        except ValueError as e:
            print(f"JSON解析錯誤: {e}")
        except Exception as e:
            print(f"處理日期 {date_str} 時發生錯誤: {e}")

        # 前進到下一天
        current_date += datetime.timedelta(days=1)


def main():
    """主函數"""
    # 設定要下載的數據集
    datasets_to_download = ["TaiwanFuturesTick"]

    # 設定日期範圍
    start_date_str = "2025-05-01"
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.today()

    # 下載每個數據集
    for dataset in datasets_to_download:
        if dataset not in DATASET_CONFIG:
            print(f"未知數據集: {dataset}，跳過")
            continue

        download_data(
            start_date=start_date,
            end_date=end_date,
            token=API_TOKEN,
            dataset=dataset,
            force_download=False,
        )


if __name__ == "__main__":
    main()
