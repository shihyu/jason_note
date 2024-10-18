## 當沖

- 做空
  - 空頭年(2022年) 找弱勢股拉高隔天空 by 權證小哥
  - 原本基本面很好 突然不好用股期做空 by 非比斯



---

```python
from loguru import logger
import pandas as pd
import shioaji as sj
import os
import json


def login():
    api = sj.Shioaji(simulation=False)
    token_file = os.environ["HOME"] + "/.mybin/shioaji_tokens.json"
    with open(token_file, "r") as f:
        users = json.load(f)
        api.login(
            users["Jason"]["api_key"],
            users["Jason"]["secret_key"],
            contracts_timeout=30000,
        )
    return api


def detect_pullback(tick_data, threshold=0.02, lookback=10):
    """
    偵測符合條件的型態：
    1. 低點必須在高點左邊
    2. 高點與低點的差距必須超過 threshold (預設 2%)
    3. 當價格從高點拉回後觸發

    :param tick_data: 含有 'ts' 和 'close' 的 DataFrame
    :param threshold: 高低點差距的百分比門檻 (預設 2%)
    :param lookback: 在多少範圍內尋找高點與低點 (預設 10 個 tick)
    :return: 回傳一個字典，包含觸發與否和相關時間
    """
    # 初始化變量
    low_idx = None
    high_idx = None

    for i in range(lookback, len(tick_data)):
        # 在過去的 lookback 範圍內找低點和高點
        lookback_data = tick_data[i - lookback : i]

        low_idx = lookback_data["close"].idxmin()  # 找出低點的位置
        high_idx = lookback_data["close"].idxmax()  # 找出高點的位置

        # 確保低點在高點的左邊，且高點與低點的差異超過 threshold
        if (
            low_idx < high_idx
            and (tick_data["close"][high_idx] - tick_data["close"][low_idx])
            / tick_data["close"][low_idx]
            >= threshold
        ):
            # 檢查是否出現回檔，即價格從高點拉回
            if tick_data["close"][i] < tick_data["close"][high_idx]:
                return {
                    "triggered": True,
                    "low_time": low_idx,  # 直接使用 low_idx，稍後使用索引取得時間
                    "high_time": high_idx,  # 直接使用 high_idx，稍後使用索引取得時間
                    "pullback_time": tick_data.iloc[
                        i
                    ].name,  # 直接使用 i，稍後使用索引取得時間
                }

    return {"triggered": False}


def print_usage(api):
    usage_status = api.usage()
    connections = usage_status.connections
    usage_MB = usage_status.bytes / 1024 / 1024
    limit_MB = usage_status.limit_bytes / 1024 / 1024
    remaining_MB = usage_status.remaining_bytes / 1024 / 1024

    logger.info(
        f"connections={connections}, "
        f"usage MB={usage_MB:.2f}, "
        f"limit MB={limit_MB:.2f}, "
        f"remaining MB={remaining_MB:.2f}"
    )


if __name__ == "__main__":
    api = login()
    # 訂閱
    contract = api.Contracts.Stocks["2330"]
    # 取得tick
    ticks = api.ticks(contract=api.Contracts.Stocks["1316"], date="2024-02-27")
    df_ticks = pd.DataFrame({**ticks})
    df_ticks.ts = pd.to_datetime(df_ticks.ts)
    df_ticks = df_ticks.set_index("ts")
    print(df_ticks.to_markdown(floatfmt=".2f"))
    input()

    ## 偵測是否觸發回檔
    try:
        # 去除同個時間戳的重複數據，只保留最後一筆
        df_cleaned = df_ticks[~df_ticks.index.duplicated(keep="last")]
        result = detect_pullback(df_cleaned)
        print(result)
        print_usage(api)
        api.logout()
    except Exception as e:
        logger.exception(e)
        api.logout()

```
