import pandas as pd


def calculate_ma(
    df: pd.DataFrame, short_window: int = 5, long_window: int = 20
) -> pd.DataFrame:
    result = df.copy()
    result[f"ma_{short_window}"] = result["close"].rolling(window=short_window).mean()
    result[f"ma_{long_window}"] = result["close"].rolling(window=long_window).mean()
    return result


def detect_crossover(
    df: pd.DataFrame, short_col: str = "ma_5", long_col: str = "ma_20"
) -> pd.DataFrame:
    result = df.copy()
    result["signal"] = "hold"
    result["prev_short"] = result[short_col].shift(1)
    result["prev_long"] = result[long_col].shift(1)
    golden = (result["prev_short"] <= result["prev_long"]) & (
        result[short_col] > result[long_col]
    )
    death = (result["prev_short"] >= result["prev_long"]) & (
        result[short_col] < result[long_col]
    )
    result.loc[golden, "signal"] = "golden_cross"
    result.loc[death, "signal"] = "death_cross"
    return result
