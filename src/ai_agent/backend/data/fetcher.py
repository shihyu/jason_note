# backend/data/fetcher.py
import yfinance as yf
import pandas as pd


def fetch_stock_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    抓取股票歷史 K 線數據

    Args:
        symbol: 股票代碼（如 "2330.TW", "AAPL"）
        start: 開始日期（如 "2024-01-01"）
        end: 結束日期（如 "2024-12-31"）

    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    df = yf.download(symbol, start=start, end=end, progress=False)

    # 重設索引，將 date 變成欄位
    df = df.reset_index()

    # yfinance 回傳的欄位可能是 MultiIndex，扁平化處理
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            col[0] if col[1] == "" or col[1] == symbol else col[0] for col in df.columns
        ]

    # 確保 date 欄位是 datetime 格式
    date_col = "Date" if "Date" in df.columns else "date"
    df = df.rename(columns={date_col: "date"})
    df["date"] = pd.to_datetime(df["date"])

    # 選取必要欄位並確保順序（yfinance 欄位名稱可能是大寫）
    col_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    df = df.rename(columns=col_map)

    # 確保只保留必要欄位
    df = df[["date", "open", "high", "low", "close", "volume"]]

    return df
