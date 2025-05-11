import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io


# 讀取CSV數據
def read_csv_data(csv_string):
    """
    從CSV字串讀取數據並轉換成DataFrame格式
    """
    # 使用io.StringIO來從字串讀取CSV
    df = pd.read_csv(io.StringIO(csv_string))

    # 轉換日期欄位為datetime格式
    df["date"] = pd.to_datetime(df["date"])

    # 按時間排序
    df = df.sort_values("date")

    return df


# 創建5秒K線資料
def create_5sec_candles(df):
    """
    將tick資料轉換為5秒間隔的K線資料
    每個K線包含這5秒內的最高價和最低價
    """
    # 建立5秒間隔的時間組
    df["time_group"] = df["date"].dt.floor("5S")

    # 根據時間組分組並計算每組的最高和最低價
    candles = df.groupby("time_group").agg(
        {"price": ["max", "min"], "volume": "sum"}  # 同時計算交易量
    )

    # 展平多層索引列
    candles.columns = ["high", "low", "volume"]

    # 重設索引，使time_group成為一個列
    candles = candles.reset_index()

    return candles


# 計算滾動箱子
def calculate_rolling_boxes(candles):
    """
    計算滾動箱子：每5根K線組成一個箱子
    對於每根K線，如果它是5根K線中的最後一根，則添加箱子的高低點
    箱子的高低點為這5根K線的最高價和最低價
    """
    # 添加箱子高低點的列
    candles["box_high"] = np.nan
    candles["box_low"] = np.nan

    # 確保有足夠的K線數據
    if len(candles) < 5:
        print("警告：K線數據少於5根，無法建立完整箱子")
        return candles

    # 對於第5根K線及之後的每根K線
    for i in range(4, len(candles)):
        # 取得最新的5根K線
        current_box_candles = candles.iloc[i - 4 : i + 1]

        # 計算這5根K線的最高價和最低價
        box_high = current_box_candles["high"].max()
        box_low = current_box_candles["low"].min()

        # 將箱子的高低點添加到當前K線
        candles.loc[candles.index[i], "box_high"] = box_high
        candles.loc[candles.index[i], "box_low"] = box_low

    return candles


# 主函數：處理CSV數據
def process_tick_data(csv_data):
    """
    主處理函數：
    1. 讀取tick數據
    2. 創建5秒K線
    3. 計算滾動箱子
    """
    # 讀取tick數據
    tick_df = read_csv_data(csv_data)
    print(f"已讀取 {len(tick_df)} 筆tick數據")

    # 創建5秒K線
    candles = create_5sec_candles(tick_df)
    print(f"已創建 {len(candles)} 根5秒K線")

    # 計算滾動箱子
    result_df = calculate_rolling_boxes(candles)

    # 計算有箱子資訊的K線數量
    box_count = len(result_df[~result_df["box_high"].isna()])
    print(f"已創建 {box_count} 個箱子資訊")

    return result_df


# 範例使用
if __name__ == "__main__":
    # 處理數據
    with open("./2025-05-08.csv", "r") as file:
        csv_data = file.read()

    result = process_tick_data(csv_data)

    # 顯示結果
    print("\n包含箱子資訊的K線資料:")
    print(result[["time_group", "high", "low", "box_high", "box_low"]].tail(10))

    # 只顯示有箱子資訊的K線
    print("\n只顯示有箱子資訊的K線:")
    print(
        result[~result["box_high"].isna()][
            ["time_group", "high", "low", "box_high", "box_low"]
        ]
    )

# 使用說明：
# 1. 將您的CSV文件內容保存為文本文件，或者直接使用變數存儲
# 2. 調用process_tick_data函數處理數據
# 3. 結果中的box_high和box_low列表示每5根K線的最高價和最低價
# 4. 只有第5根K線及之後的K線會有箱子資訊
