# 當沖交易心法與技巧整理 (阿魯米)

## 當沖基本原則

### 選股條件
1. 選擇平均震幅大的股票
   - 近三日或五日平均震幅高於 5%
   - 避免選擇震幅小的股票(如中華電信)
2. 周轉率高的股票
   - 代表流動性好
   - 大量但周轉率低的股票(如台積電)不適合
3. 日線處於趨勢發動中或高檔震盪的股票
4. 年輕、股本小且震盪大的股票
   - 新上市櫃十年內
   - 法人持股不多
   - 容易有大波段

### 交易基本概念
1. 觀察大盤方向
   - 大盤是最主要的方向參考
   - 參考期貨,盡量不逆勢操作
   - 台指偏多則選多方名單,空方亦然

2. 開盤價的重要性
   - 不要只看漲跌,要看開盤價位置
   - 在開盤價附近區間脫離一段,基本上就是當天方向
   - 開盤價可視為多空分界
   - 價格在開盤價以下表示當天弱勢,收黑機率大
   - 價格持續在開盤價上方,表示強勢,收紅機率大

3. 均價線運用
   - 均價線代表當天成交平均價格
   - 可視為短期均線概念
   - 在均價線上方逢低接
   - 在均價線下方逢高空

4. 盤中量能觀察
   - 一個方向走一段時間出現大量,通常是極短線高低點
   - 可能出現拉回或反彈(但不代表反轉)
   - 出量位置若不拉回或反彈,則成為支撐壓力區
   - 上漲出量、拉回量縮是多方表現
   - 下跌出量、反彈量縮是空方表現

## 風險控制

### 停損原則
1. 停損、停損、停損(重要所以說三次)
2. 收盤前清理虧損部位,不帶回家
3. 每筆交易虧損控制在 2% 以內
4. 遇到重大虧損應:
   - 立即減少交易量或停止交易
   - 重點是重拾交易信心,而非急於彌補虧損
   - 避免單量越做越大想一舉翻身

### 心態管理
1. 保持平靜
   - 市場隨時可能重擊
   - 虧損時表示情況不利,不要急躁
   - 大賺大賠都要保持冷靜

2. 避免衝動交易
   - 最糟糕的交易來自衝動
   - 根據既定信號進行交易
   - 不要因一時衝動改變策略

3. 持續學習檢討
   - 每天分析每筆交易
   - 檢討是否有違規情況
   - 分析成功與失敗原因

## 進階技巧

### 季線理論
1. 股價在季線(60日均線)上徘徊一段時間後
2. 開盤價直接開在季線下至少 2%
3. 通常代表空方力量強大
4. 適合當沖做空
5. 觀察 09:30 前是否拉過平盤
6. 勝率約九成

### 交易時機選擇
1. 等待市場明朗再進場
2. 不預測行情,讓市場告訴方向
3. 選擇萬無一失的機會
4. 策略需具彈性應對市場變化

### 資金管理
1. 操作順利時可適度加碼
2. 情況不佳時減碼或停止交易
3. 著重如何減少虧損,而非如何多賺
4. 避免重倉操作
5. 好倉要耐心持有,壞倉要果斷減碼

## 市場認知

### 交易本質
1. 交易是一種對賭遊戲
2. 競爭對手是整體市場參與者
3. 獲利來自對手的錯誤決策
4. 重要的是認清自己,發現並改進錯誤
5. 遵守紀律,提高勝率

### 市場參與者
1. 不要高估對手能力
2. 也不要輕視對手
3. 資訊不對稱是主要優勢
4. 主力也會演戲誤導市場

### 長期生存之道
1. 穩定獲利比單次暴賺重要
2. 交易系統要持之以恆
3. 賺錢時要更加謹慎
4. 重點不是瞬間獲利多寡
5. 而是能賺得長,活得久

## 實戰注意事項

1. 當沖很難穩定獲利
   - 交易成本高
   - 隨機性強
   - 需要長期練習

2. 不要相信誇大廣告
   - 特別是號稱暴賺
   - 無本操作
   - 華麗詞彙包裝

3. 新手建議
   - 不要期待暴賺
   - 先求穩定獲利
   - 逐步提升層次
   - 從基本心法做起

4. 盈虧比例
   - 當沖輸的人多,贏的少
   - 穩定賺錢者極少
   - 要思考自己的優勢在哪

注意：本文整理僅供參考，投資一定有風險，須依個人判斷為準。

---


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
