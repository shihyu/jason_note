## 當沖

- 做空
  - 空頭年(2022年) 找弱勢股拉高隔天空 by 權證小哥
  - 原本基本面很好 突然不好用股期做空 by 非比斯



---

```python
import os
import json
from loguru import logger
import pandas as pd
import shioaji as sj
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


def load_credentials(file_path):
    """Load API credentials from a JSON file."""
    with open(file_path, "r") as f:
        users = json.load(f)
    return users["Jason"]["api_key"], users["Jason"]["secret_key"]


def login(simulation=False):
    """Login to the Shioaji API."""
    api = sj.Shioaji(simulation=simulation)
    token_file = os.path.expanduser("~/.mybin/shioaji_tokens.json")
    api_key, secret_key = load_credentials(token_file)
    api.login(api_key, secret_key, contracts_timeout=30000)
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
    for i in range(lookback, len(tick_data)):
        window = tick_data.iloc[i - lookback : i]
        low_idx = window["close"].idxmin()
        high_idx = window["close"].idxmax()
        if low_idx < high_idx:
            price_change = (
                tick_data.loc[high_idx, "close"] - tick_data.loc[low_idx, "close"]
            ) / tick_data.loc[low_idx, "close"]
            if (
                price_change >= threshold
                and tick_data.iloc[i]["close"] < tick_data.loc[high_idx, "close"]
            ):
                return {
                    "triggered": True,
                    "low_time": low_idx,
                    "high_time": high_idx,
                    "pullback_time": tick_data.index[i],
                }
    return {"triggered": False}


def print_usage(api):
    """Print API usage statistics."""
    usage_status = api.usage()
    usage_MB = usage_status.bytes / (1024 * 1024)
    limit_MB = usage_status.limit_bytes / (1024 * 1024)
    remaining_MB = usage_status.remaining_bytes / (1024 * 1024)
    logger.info(
        f"connections={usage_status.connections}, "
        f"usage MB={usage_MB:.2f}, "
        f"limit MB={limit_MB:.2f}, "
        f"remaining MB={remaining_MB:.2f}"
    )


def fetch_and_process_ticks(api, stock_code, date):
    """Fetch and process tick data for a given stock and date."""
    contract = api.Contracts.Stocks[stock_code]
    ticks = api.ticks(contract=contract, date=date)
    df_ticks = pd.DataFrame({**ticks})
    df_ticks["ts"] = pd.to_datetime(df_ticks["ts"])
    df_ticks = df_ticks.set_index("ts")
    return df_ticks[~df_ticks.index.duplicated(keep="last")]


def plot_ticks_with_markers(df_ticks, result):
    """Plot tick data with markers for high, low, and pullback points."""
    plt.figure(figsize=(12, 6))
    plt.plot(df_ticks.index, df_ticks["close"], label="Close Price")

    if result["triggered"]:
        plt.scatter(
            result["low_time"],
            df_ticks.loc[result["low_time"], "close"],
            color="green",
            s=100,
            marker="^",
            label="Low Point",
        )
        plt.scatter(
            result["high_time"],
            df_ticks.loc[result["high_time"], "close"],
            color="red",
            s=100,
            marker="v",
            label="High Point",
        )
        plt.scatter(
            result["pullback_time"],
            df_ticks.loc[result["pullback_time"], "close"],
            color="blue",
            s=100,
            marker="o",
            label="Pullback Point",
        )

    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("Tick Data with Pullback Detection")
    plt.legend()

    # Format x-axis to show time
    plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    api = login()
    try:
        df_ticks = fetch_and_process_ticks(api, "1316", "2024-02-27")
        print(df_ticks.to_markdown(floatfmt=".2f"))
        result = detect_pullback(df_ticks)
        print(result)
        print_usage(api)

        # Plot the tick data with markers
        plot_ticks_with_markers(df_ticks, result)
    except Exception as e:
        logger.exception(e)
    finally:
        api.logout()


if __name__ == "__main__":
    main()

`
