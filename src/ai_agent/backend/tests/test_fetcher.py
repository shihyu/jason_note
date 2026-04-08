# backend/tests/test_fetcher.py
import pytest
from datetime import datetime
import pandas as pd
from backend.data.fetcher import fetch_stock_data


def test_fetch_stock_data_columns():
    """驗證回傳 DataFrame 包含必要欄位"""
    # 使用真實 yfinance 測試
    df = fetch_stock_data("AAPL", "2024-01-01", "2024-01-31")
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(df) > 0


def test_fetch_stock_data_types():
    """驗證欄位型別正確"""
    df = fetch_stock_data("AAPL", "2024-01-01", "2024-01-31")
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert pd.api.types.is_float_dtype(df["close"])


def test_fetch_taiwan_stock():
    """驗證台股抓取（2330.TW）"""
    df = fetch_stock_data("2330.TW", "2024-01-01", "2024-01-31")
    assert len(df) > 0
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
