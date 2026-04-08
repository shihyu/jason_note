# backend/indicators/ma.py
import pandas as pd
from typing import List, Dict


def calculate_ma(
    df: pd.DataFrame, short_window: int = 5, long_window: int = 20
) -> pd.DataFrame:
    result = df.copy()
    result["ma_short"] = df["close"].rolling(window=short_window).mean()
    result["ma_long"] = df["close"].rolling(window=long_window).mean()
    return result


def detect_crossover(df: pd.DataFrame) -> List[Dict]:
    crossovers = []
    df = df.dropna()

    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        if prev["ma_short"] <= prev["ma_long"] and curr["ma_short"] > curr["ma_long"]:
            crossovers.append(
                {
                    "date": curr["date"],
                    "type": "golden_cross",
                    "price": curr["close"],
                }
            )
        elif prev["ma_short"] >= prev["ma_long"] and curr["ma_short"] < curr["ma_long"]:
            crossovers.append(
                {
                    "date": curr["date"],
                    "type": "death_cross",
                    "price": curr["close"],
                }
            )

    return crossovers
