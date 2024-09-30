# JUMP

```python
import pandas as pd
import warnings
import numpy as np
import vectorbt as vbt
import talib
from vectorbt.portfolio.enums import NoOrder
from vectorbt.portfolio import nb
from numba import njit
from loguru import logger

# Suppress warnings
warnings.filterwarnings("ignore")


def initialize_data(data):
    """
    Convert DataFrame columns to NumPy arrays for performance.

    Parameters:
        data (pd.DataFrame): The trading data.

    Returns:
        tuple: Contains various NumPy arrays extracted from the DataFrame.
    """
    is_thursday = data["Is_Thursday"].to_numpy()
    is_open_time = data["Is_Open_Time"].to_numpy()
    is_close_time = data["Is_Close_Time"].to_numpy()
    dates = data.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    timestamps = (pd.to_datetime(data.index).astype(int) // 10**9).tolist()
    open_prices = data["open"].to_numpy()
    close_prices = data["close"].to_numpy()
    high_prices = data["high"].to_numpy()
    low_prices = data["low"].to_numpy()
    long_conditions = data["long_condition"].to_numpy()
    short_conditions = data["short_condition"].to_numpy()
    long_atr_exit = data["long_atr_exit_value"].to_numpy()
    short_atr_exit = data["short_atr_exit_value"].to_numpy()
    atr_values = data["ATR"].to_numpy()

    return (
        is_thursday,
        is_open_time,
        is_close_time,
        dates,
        timestamps,
        open_prices,
        close_prices,
        high_prices,
        low_prices,
        long_conditions,
        short_conditions,
        long_atr_exit,
        short_atr_exit,
        atr_values,
    )


@njit
def execute_order(
    context,
    long_entry,
    short_entry,
    open_prices,
    high_prices,
    low_prices,
    entry_timestamps,
    trading_dates,
    trading_timestamps,
    is_thursday_flags,
    market_open_flags,
    market_close_flags,
    long_atr_sl,
    short_atr_sl,
    atr_vals,
    highest_since_entry,
    lowest_since_entry,
    max_high_M,
    min_low_M,
    check_interval_M,
    trading_mode,
):
    """
    Numba-compiled function to execute trading orders based on conditions.

    Parameters:
        context: Context object containing current state.
        ... (other parameters as in original function)

    Returns:
        Order action or NoOrder.
    """
    # Extract current data
    is_long = long_entry[context.i]
    is_short = short_entry[context.i]
    current_close = context.close[context.i, context.col]
    current_open = open_prices[context.i]
    current_high = high_prices[context.i]
    current_low = low_prices[context.i]
    current_date = trading_dates[context.i]
    current_timestamp = trading_timestamps[context.i]
    is_thursday = is_thursday_flags[context.i]
    is_market_open = market_open_flags[context.i]
    is_market_close = market_close_flags[context.i]
    current_position = context.position_now
    long_sl = long_atr_sl[context.i]
    short_sl = short_atr_sl[context.i]
    atr = atr_vals[context.i]

    if check_interval_M > 0:
        recent_max_high = max_high_M[context.i]
        recent_min_low = min_low_M[context.i]

    time_held = 0
    if entry_timestamps[0] > 0:
        time_held = int(current_timestamp - entry_timestamps[0])

    # Entry Logic
    if trading_mode in (0, 2):  # Long or Both
        if current_position == 0 and is_long and is_market_open:
            entry_timestamps[0] = current_timestamp
            highest_since_entry[0] = current_high
            return nb.order_nb(price=current_open, size=1)  # Enter Long

    if trading_mode in (1, 2):  # Short or Both
        if current_position == 0 and is_short and is_market_open:
            entry_timestamps[0] = current_timestamp
            lowest_since_entry[0] = current_low
            return nb.order_nb(price=current_open, size=-1)  # Enter Short

    # Long Position Management
    if trading_mode in (0, 2) and current_position > 0:
        highest_since_entry[0] = max(highest_since_entry[0], current_high)

        # ATR Stop Loss
        if current_close < long_sl:
            entry_timestamps[0] = 0
            highest_since_entry[0] = 0
            return nb.order_nb(price=current_close, size=-current_position)

        # Interval Check for Exiting
        if time_held >= (check_interval_M * 60) and check_interval_M > 0:
            if highest_since_entry[0] < recent_max_high:
                entry_timestamps[0] = 0
                highest_since_entry[0] = 0
                return nb.order_nb(price=current_close, size=-current_position)

    # Short Position Management
    if trading_mode in (1, 2) and current_position < 0:
        lowest_since_entry[0] = min(lowest_since_entry[0], current_low)

        # ATR Stop Loss
        if current_close > short_sl:
            entry_timestamps[0] = 0
            lowest_since_entry[0] = 0
            return nb.order_nb(price=current_close, size=-current_position)

        # Interval Check for Exiting
        if time_held >= (check_interval_M * 60) and check_interval_M > 0:
            if lowest_since_entry[0] > recent_min_low:
                entry_timestamps[0] = 0
                lowest_since_entry[0] = 0
                return nb.order_nb(price=current_close, size=-current_position)

    return NoOrder


def compute_open_price_change(df, open_time, close_time):
    """
    Calculate the percentage change in open prices compared to the previous close.

    Parameters:
        df (pd.DataFrame): The trading data.
        open_time (str): The opening time in "HH:MM:SS" format.
        close_time (str): The closing time in "HH:MM:SS" format.

    Returns:
        pd.DataFrame: DataFrame with an additional 'open_price_delta' column.
    """
    df_copy = df.copy()
    df_copy["open_price_delta"] = 0.0
    dates = df.index.strftime("%Y-%m-%d").tolist()
    unique_dates = sorted(set(dates))
    previous_date = unique_dates[0]

    for current_date in unique_dates[1:]:
        open_datetime = f"{current_date} {open_time}"
        close_datetime = f"{previous_date} {close_time}"
        if open_datetime not in df.index or close_datetime not in df.index:
            previous_date = current_date
            continue
        open_price = df.loc[open_datetime, "open"]
        close_price = df.loc[close_datetime, "close"]
        df_copy.loc[open_datetime, "open_price_delta"] = (open_price / close_price) - 1
        previous_date = current_date

    return df_copy


def calculate_atr(data, atr_period=14):
    """
    Calculate True Range (TR) and Average True Range (ATR).

    Parameters:
        data (pd.DataFrame): The trading data.
        atr_period (int): The period for ATR calculation.

    Returns:
        pd.DataFrame: DataFrame with additional 'TR' and 'ATR' columns.
    """
    data["TR"] = talib.TRANGE(data["high"], data["low"], data["close"])
    data["ATR"] = talib.EMA(data["TR"], timeperiod=atr_period)
    return data


def prepare_exit_levels(data, atr_multiplier):
    """
    Calculate ATR-based exit levels for long and short positions.

    Parameters:
        data (pd.DataFrame): The trading data with ATR calculated.
        atr_multiplier (float): The multiplier for ATR to set exit levels.

    Returns:
        pd.DataFrame: DataFrame with 'long_atr_exit_value' and 'short_atr_exit_value' columns.
    """
    data["long_atr_exit_value"] = data["high"].rolling(window=2).max() - (
        data["ATR"] * atr_multiplier
    )
    data["short_atr_exit_value"] = data["low"].rolling(window=2).min() + (
        data["ATR"] * atr_multiplier
    )
    return data


def load_and_process_data(filepath, start_date="2017-05-16"):
    """
    Load trading data from a CSV file and preprocess it.

    Parameters:
        filepath (str): Path to the CSV file.
        start_date (str): The starting date for the data.

    Returns:
        pd.DataFrame: Preprocessed trading data.
    """
    df = pd.read_csv(filepath)
    df["DateTime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"], format="%Y/%m/%d %H:%M:%S"
    )
    df = df.drop(columns=["Date", "Time"])
    df.set_index("DateTime", inplace=True)
    df = df.rename(
        columns={
            "Close": "close",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "TotalVolume": "volume",
        }
    )
    df = df[df.index >= pd.Timestamp(start_date)]
    return df


def main():
    # === Parameter Configuration ===
    # Toggle this to switch between different parameter sets
    use_first_set = True

    if use_first_set:
        # Parameter Set 1
        close_time = "13:24:00"
        open_time = "00:00:00"
        long_threshold = 0.001
        short_threshold = -0.01
        atr_length = 86
        atr_multiplier = 6.3
        M_values = [1260]  # Example: [1260]
        # M_values = range(100, 1501, 20)  # M 參數範圍
        trading_mode = 2  # 0: Long only, 1: Short only, 2: Both
    else:
        # Parameter Set 2
        close_time = "13:30:00"
        open_time = "00:46:00"
        long_threshold = 0.003
        short_threshold = -0.01
        atr_length = 82
        atr_multiplier = 9.5
        M_values = [-1]  # Example: [3700] or [-1]
        trading_mode = 1  # 0: Long only, 1: Short only, 2: Both

    # === Data Loading and Preprocessing ===
    data_filepath = "./TWF.TXF-HOT-Minute-Trade.txt"
    raw_data = load_and_process_data(data_filepath)
    data_with_change = compute_open_price_change(raw_data, open_time, close_time)
    data_with_change["long_condition"] = (
        data_with_change["open_price_delta"] > long_threshold
    )
    data_with_change["short_condition"] = (
        data_with_change["open_price_delta"] < short_threshold
    )
    data_with_change["Is_Thursday"] = data_with_change.index.weekday == 3
    data_with_change["Is_Open_Time"] = (
        data_with_change.index.time == pd.Timestamp(open_time).time()
    )
    data_with_change["Is_Close_Time"] = (
        data_with_change.index.time == pd.Timestamp(close_time).time()
    )
    data_with_atr = calculate_atr(data_with_change, atr_period=atr_length)
    data_with_exits = prepare_exit_levels(data_with_atr, atr_multiplier)

    # === Initialize Data for Numba ===
    (
        is_thursday,
        is_open_time,
        is_close_time,
        dates,
        timestamps,
        open_prices,
        close_prices,
        high_prices,
        low_prices,
        long_conditions,
        short_conditions,
        long_atr_exit,
        short_atr_exit,
        atr_values,
    ) = initialize_data(data_with_exits)

    # Initialize variables for tracking entries
    entry_timestamps = np.zeros(1, dtype=np.int64)
    highest_price_since_entry = np.zeros(1)
    lowest_price_since_entry = np.zeros(1)

    # === Optimization Loop ===
    best_M = 0
    best_return = -np.inf

    for check_interval_M in M_values:
        try:
            if check_interval_M > 0:
                max_high_M = (
                    data_with_exits["high"]
                    .rolling(window=check_interval_M)
                    .max()
                    .to_numpy()
                )
                min_low_M = (
                    data_with_exits["low"]
                    .rolling(window=check_interval_M)
                    .min()
                    .to_numpy()
                )
            else:
                max_high_M = np.empty(len(data_with_exits))
                min_low_M = np.empty(len(data_with_exits))

            # Create Portfolio using VectorBT
            portfolio = vbt.Portfolio.from_order_func(
                data_with_exits["close"],
                execute_order,
                long_conditions,
                short_conditions,
                open_prices,
                high_prices,
                low_prices,
                entry_timestamps,
                dates,
                timestamps,
                is_thursday,
                is_open_time,
                is_close_time,
                long_atr_exit,
                short_atr_exit,
                atr_values,
                highest_price_since_entry,
                lowest_price_since_entry,
                max_high_M,
                min_low_M,
                check_interval_M,
                trading_mode,
                init_cash=1_000_000,
            )

            # Display Orders
            print(
                portfolio.orders.records_readable.to_markdown(
                    floatfmt=".5f", tablefmt="heavy_grid"
                )
            )

            # Display Portfolio Statistics
            print(portfolio.stats())

            # Calculate Total Return
            total_return = portfolio.total_return()
            if total_return > best_return:
                best_M = check_interval_M
                best_return = total_return

            print(f"check_interval_M={check_interval_M} total return: {total_return}")
        except Exception as e:
            logger.exception(f"Error with M={check_interval_M}: {e}")

    # === Display Best Results ===
    print(f"Best check_interval_M: {best_M}")
    print(f"Best return: {best_return}")


if __name__ == "__main__":
    main()
```

