import yfinance as yf
import pandas as pd


def fetch_stock_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end)
    df = df.reset_index()
    df.columns = [col.lower() for col in df.columns]
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df[["date", "open", "high", "low", "close", "volume"]]
