import argparse
import os
import re
import webbrowser
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_futures_data(csv_file, start_time=None, end_time=None):
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return

    # Extract date from filename (assuming format like "2025-05-08.csv")
    filename_date_match = re.search(
        r"(\d{4})-(\d{2})-\d{2}", os.path.basename(csv_file)
    )
    if filename_date_match:
        year, month = filename_date_match.groups()
        expected_contract_date = f"{year}{month}"
        print(f"Filtering for contract_date: {expected_contract_date}")
    else:
        print(
            "Warning: Could not extract date from filename. No contract_date filtering applied."
        )
        expected_contract_date = None

    # Read CSV file
    df = pd.read_csv(csv_file)
    print(f"Read {len(df)} rows from CSV file")
    print(f"CSV columns: {df.columns.tolist()}")

    # Check if 'contract_date' column exists
    if "contract_date" not in df.columns:
        print(
            "Warning: 'contract_date' column not found in CSV file. Skipping contract filtering."
        )
    else:
        # Filter out entries where contract_date contains a slash "/"
        df = df[~df["contract_date"].astype(str).str.contains("/")]

        # Filter for the specific contract_date matching year and month from filename
        if expected_contract_date:
            original_count = len(df)
            df = df[df["contract_date"].astype(str) == expected_contract_date]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows with contract_date not matching {expected_contract_date}"
            )

    # Check if we have data after filtering
    if df.empty:
        print("No valid data to plot after filtering.")
        return

    # Print min and max date before conversion for debugging
    print(
        f"Before datetime conversion - first few date values: {df['date'].head().tolist()}"
    )

    # Convert date column to datetime if it's not already
    try:
        df["date"] = pd.to_datetime(df["date"])
        print(f"Date column converted to datetime. Sample date: {df['date'].iloc[0]}")
    except Exception as e:
        print(f"Error converting date column: {e}")
        print("Trying alternative date format...")
        try:
            # Try with different format if the standard conversion fails
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S.%f")
            print(
                f"Date column converted with explicit format. Sample date: {df['date'].iloc[0]}"
            )
        except Exception as e2:
            print(f"Error with alternative format: {e2}")
            return

    # Apply time range filter if specified
    if start_time and end_time:
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()

            # Print some sample times for debugging
            print(
                f"First 5 times in dataframe: {[d.time() for d in df['date'].head().tolist()]}"
            )
            print(f"Filtering for times between {start_time_obj} and {end_time_obj}")

            # Filter data by time range
            original_count = len(df)
            df = df[df["date"].dt.time.between(start_time_obj, end_time_obj)]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows outside time range {start_time} - {end_time}"
            )
            print(f"Remaining rows after time filtering: {len(df)}")

            # Check if we have data after time filtering
            if df.empty:
                print("No valid data to plot after time range filtering.")
                return
        except Exception as e:
            print(f"Error during time filtering: {e}")
            return

    # Sort by date to ensure chronological order
    df = df.sort_values("date")

    # Create subplot with 2 rows (price and volume)
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Price", "Volume"),
        row_heights=[0.7, 0.3],
    )

    # Add price trace
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["price"], name="Price", line=dict(color="blue", width=1)
        ),
        row=1,
        col=1,
    )

    # Add volume trace
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["volume"],
            name="Volume",
            marker=dict(color="rgba(58, 71, 80, 0.6)"),
        ),
        row=2,
        col=1,
    )

    # Create title with time range if specified
    title = f"Futures Data: {os.path.basename(csv_file)}"
    if expected_contract_date:
        title += f" (Contract: {expected_contract_date})"
    if start_time and end_time:
        title += f" [Time: {start_time} - {end_time}]"

    # Update layout
    fig.update_layout(
        title=title,
        height=800,
        hovermode="x unified",
        showlegend=False,
        template="plotly_white",
    )

    # Update x-axis - FORCE the x-axis range to match the filtered data
    if start_time and end_time:
        # Make sure the range is set exactly to our filtered data
        min_date = df["date"].min()
        max_date = df["date"].max()
        fig.update_xaxes(range=[min_date, max_date], row=1, col=1)
        fig.update_xaxes(range=[min_date, max_date], row=2, col=1)

    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

    # Create output filename with time range if specified
    time_suffix = ""
    if start_time and end_time:
        time_suffix = f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"

    output_file = f"futures_plot_{os.path.splitext(os.path.basename(csv_file))[0]}{time_suffix}.html"
    fig.write_html(output_file)

    # Open in browser
    webbrowser.open(f"file://{os.path.abspath(output_file)}")
    print(f"Plot saved to {output_file} and opened in browser.")

    return df  # Return filtered dataframe for potential reuse


def plot_frequency_data(csv_file, start_time=None, end_time=None):
    """
    Plot the frequency of transactions per 10-second interval
    """
    # Get filtered dataframe without reusing the previous plot's result
    # (to avoid opening too many browser windows)

    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return

    # Extract contract date from filename
    filename_date_match = re.search(
        r"(\d{4})-(\d{2})-\d{2}", os.path.basename(csv_file)
    )
    expected_contract_date = None
    if filename_date_match:
        year, month = filename_date_match.groups()
        expected_contract_date = f"{year}{month}"

    # Read and filter data
    df = pd.read_csv(csv_file)

    # Check if 'contract_date' column exists
    if "contract_date" in df.columns:
        # Filter out entries where contract_date contains a slash "/"
        df = df[~df["contract_date"].astype(str).str.contains("/")]

        # Filter for specific contract_date
        if expected_contract_date:
            df = df[df["contract_date"].astype(str) == expected_contract_date]

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Apply time range filter if specified
    if start_time and end_time:
        start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()
        df = df[df["date"].dt.time.between(start_time_obj, end_time_obj)]

    if df.empty:
        print("No data available for frequency analysis.")
        return

    # Create a copy of the dataframe to avoid modifying the original
    freq_df = df.copy()

    # Round timestamps to 10-second intervals
    freq_df["interval"] = freq_df["date"].apply(
        lambda x: x.replace(second=10 * (x.second // 10), microsecond=0)
    )

    # Count transactions per 10-second interval
    transaction_counts = freq_df.groupby("interval").size().reset_index(name="count")

    # Create the plot
    fig = go.Figure()

    # Add transaction frequency trace
    fig.add_trace(
        go.Bar(
            x=transaction_counts["interval"],
            y=transaction_counts["count"],
            name="Transaction Frequency",
            marker=dict(color="rgba(0, 128, 0, 0.7)"),
        )
    )

    # Create title with time range if specified
    title = f"Transaction Frequency (10-second intervals): {os.path.basename(csv_file)}"
    if start_time and end_time:
        title += f" [Time: {start_time} - {end_time}]"

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Number of Transactions",
        height=600,
        template="plotly_white",
        hovermode="x unified",
    )

    # If time range is specified, set x-axis range explicitly
    if start_time and end_time:
        min_date = transaction_counts["interval"].min()
        max_date = transaction_counts["interval"].max()
        fig.update_xaxes(range=[min_date, max_date])

    # Create output filename with time range if specified
    time_suffix = ""
    if start_time and end_time:
        time_suffix = f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"

    output_file = f"frequency_plot_{os.path.splitext(os.path.basename(csv_file))[0]}{time_suffix}.html"
    fig.write_html(output_file)

    # Open in browser
    webbrowser.open(f"file://{os.path.abspath(output_file)}")
    print(f"Frequency plot saved to {output_file} and opened in browser.")

    return transaction_counts  # Return the transaction counts for potential reuse


def plot_combined_data(csv_file, start_time=None, end_time=None):
    """
    Create a combined plot with price and transaction frequency overlapping
    with two different Y-axes
    """
    # Extract date from filename (assuming format like "2025-05-08.csv")
    filename_date_match = re.search(
        r"(\d{4})-(\d{2})-\d{2}", os.path.basename(csv_file)
    )
    if filename_date_match:
        year, month = filename_date_match.groups()
        expected_contract_date = f"{year}{month}"
        print(f"Filtering for contract_date: {expected_contract_date}")
    else:
        print(
            "Warning: Could not extract date from filename. No contract_date filtering applied."
        )
        expected_contract_date = None

    # Read and filter data
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return

    # Read CSV file
    df = pd.read_csv(csv_file)
    print(f"Read {len(df)} rows from CSV file")

    # Check if 'contract_date' column exists
    if "contract_date" in df.columns:
        # Filter out entries where contract_date contains a slash "/"
        df = df[~df["contract_date"].astype(str).str.contains("/")]

        # Filter for the specific contract_date matching year and month from filename
        if expected_contract_date:
            original_count = len(df)
            df = df[df["contract_date"].astype(str) == expected_contract_date]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows with contract_date not matching {expected_contract_date}"
            )
    else:
        print("Warning: 'contract_date' column not found. Skipping contract filtering.")

    # Check if we have data after filtering
    if df.empty:
        print("No valid data to plot after filtering.")
        return

    # Convert date column to datetime if it's not already
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        print(f"Error converting date column: {e}")
        try:
            # Try with different format if the standard conversion fails
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S.%f")
        except Exception as e2:
            print(f"Error with alternative format: {e2}")
            return

    # Apply time range filter if specified
    if start_time and end_time:
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()

            # Filter data by time range
            original_count = len(df)
            df = df[df["date"].dt.time.between(start_time_obj, end_time_obj)]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows outside time range {start_time} - {end_time}"
            )
            print(f"Remaining rows after time filtering: {len(df)}")

            # Check if we have data after time filtering
            if df.empty:
                print("No valid data to plot after time range filtering.")
                return
        except Exception as e:
            print(f"Error during time filtering: {e}")
            return

    # Sort by date to ensure chronological order
    df = df.sort_values("date")

    # Calculate 10-second interval transaction frequency
    freq_df = df.copy()
    freq_df["interval"] = freq_df["date"].apply(
        lambda x: x.replace(second=10 * (x.second // 10), microsecond=0)
    )
    transaction_counts = freq_df.groupby("interval").size().reset_index(name="count")

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add price trace on primary y-axis
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["price"], name="Price", line=dict(color="blue", width=1)
        ),
        secondary_y=False,
    )

    # Add transaction frequency on secondary y-axis
    fig.add_trace(
        go.Bar(
            x=transaction_counts["interval"],
            y=transaction_counts["count"],
            name="Transaction Frequency (10s interval)",
            marker=dict(color="rgba(0, 128, 0, 0.5)"),
        ),
        secondary_y=True,
    )

    # Create title with time range if specified
    title = f"Combined Futures Data: {os.path.basename(csv_file)}"
    if expected_contract_date:
        title += f" (Contract: {expected_contract_date})"
    if start_time and end_time:
        title += f" [Time: {start_time} - {end_time}]"

    # Set titles
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        height=800,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Price", secondary_y=False)
    fig.update_yaxes(title_text="Transaction Frequency", secondary_y=True)

    # If time range is specified, set x-axis range explicitly
    if start_time and end_time:
        min_date = df["date"].min()
        max_date = df["date"].max()
        fig.update_xaxes(range=[min_date, max_date])

    # Create output filename with time range if specified
    time_suffix = ""
    if start_time and end_time:
        time_suffix = f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"

    output_file = f"combined_plot_{os.path.splitext(os.path.basename(csv_file))[0]}{time_suffix}.html"
    fig.write_html(output_file)

    # Open in browser
    webbrowser.open(f"file://{os.path.abspath(output_file)}")
    print(f"Combined plot saved to {output_file} and opened in browser.")


def main():
    parser = argparse.ArgumentParser(description="Plot futures data from CSV file")
    parser.add_argument(
        "csv_file",
        type=str,
        help="CSV file containing futures data (e.g., 2025-05-08.csv)",
    )
    parser.add_argument(
        "--frequency",
        action="store_true",
        help="Plot transaction frequency per 10-second interval",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Create combined plot with price and frequency",
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate all available plots"
    )
    # Add time range parameters
    parser.add_argument(
        "--start-time",
        type=str,
        help="Start time in HH:MM:SS format (e.g., 00:00:00)",
    )
    parser.add_argument(
        "--end-time",
        type=str,
        help="End time in HH:MM:SS format (e.g., 05:00:00)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug information about the CSV file",
    )
    args = parser.parse_args()

    # Debug mode - print file info
    if args.debug:
        try:
            if not os.path.exists(args.csv_file):
                print(f"Error: File '{args.csv_file}' not found.")
                return

            df = pd.read_csv(args.csv_file)
            print(f"CSV file contains {len(df)} rows")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Sample data (first 5 rows):")
            print(df.head())

            if "date" in df.columns:
                print("Sample dates (first 5):")
                print(df["date"].head())
                # Try to convert to datetime
                try:
                    dates = pd.to_datetime(df["date"])
                    print(f"Successfully converted dates. Sample: {dates.head()}")
                    if len(dates) > 0:
                        print(f"Min date: {dates.min()}")
                        print(f"Max date: {dates.max()}")
                except Exception as e:
                    print(f"Error converting dates: {e}")
        except Exception as e:
            print(f"Error in debug mode: {e}")
        return

    # Validate time format if provided
    start_time = args.start_time
    end_time = args.end_time

    # Check if both start and end times are provided or none are provided
    if (start_time and not end_time) or (not start_time and end_time):
        print("Error: Both --start-time and --end-time must be specified together.")
        return

    # Validate time format
    if start_time and end_time:
        try:
            datetime.strptime(start_time, "%H:%M:%S")
            datetime.strptime(end_time, "%H:%M:%S")
            print(f"Filtering data for time range: {start_time} - {end_time}")
        except ValueError:
            print("Error: Time format should be HH:MM:SS (e.g., 00:00:00)")
            return

    if args.combined or args.all:
        plot_combined_data(args.csv_file, start_time, end_time)
    elif args.frequency:
        plot_frequency_data(args.csv_file, start_time, end_time)
    elif not args.all:  # Default behavior if no specific plot is requested
        plot_futures_data(args.csv_file, start_time, end_time)

    if args.all:
        # For 'all' option, we still want to do other plots
        # But we've already done combined above, so just do the other two
        plot_futures_data(args.csv_file, start_time, end_time)
        plot_frequency_data(args.csv_file, start_time, end_time)


# python plot_future.py --start-time 00:00:00 --end-time 05:00:00 --combined TaiwanFuturesTick/days/2025-05-08.csv

if __name__ == "__main__":
    main()
