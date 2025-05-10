import argparse
import os
import re
import webbrowser

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_futures_data(csv_file):
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

    # Convert date column to datetime if it's not already
    df["date"] = pd.to_datetime(df["date"])

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

    # Update layout
    fig.update_layout(
        title=f"Futures Data: {os.path.basename(csv_file)} (Contract: {expected_contract_date})",
        height=800,
        hovermode="x unified",
        showlegend=False,
        template="plotly_white",
    )

    # Update x-axis
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

    # Make it zoomable (default in plotly)

    # Save to HTML file and open in browser
    output_file = f"futures_plot_{os.path.splitext(os.path.basename(csv_file))[0]}.html"
    fig.write_html(output_file)

    # Open in browser
    webbrowser.open(f"file://{os.path.abspath(output_file)}")
    print(f"Plot saved to {output_file} and opened in browser.")

    return df  # Return filtered dataframe for potential reuse


def plot_frequency_data(csv_file):
    """
    Plot the frequency of transactions per 10-second interval
    """
    # Get filtered dataframe from the main function or load it directly
    df = plot_futures_data(csv_file)

    if df is None or df.empty:
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

    # Update layout
    fig.update_layout(
        title=f"Transaction Frequency (10-second intervals): {os.path.basename(csv_file)}",
        xaxis_title="Time",
        yaxis_title="Number of Transactions",
        height=600,
        template="plotly_white",
        hovermode="x unified",
    )

    # Save to HTML file and open in browser
    output_file = (
        f"frequency_plot_{os.path.splitext(os.path.basename(csv_file))[0]}.html"
    )
    fig.write_html(output_file)

    # Open in browser
    webbrowser.open(f"file://{os.path.abspath(output_file)}")
    print(f"Frequency plot saved to {output_file} and opened in browser.")

    return transaction_counts  # Return the transaction counts for potential reuse


def plot_combined_data(csv_file):
    """
    Create a combined plot with price and transaction frequency overlapping
    with two different Y-axes
    """
    # Get filtered dataframe from the main function
    df = None
    transaction_counts = None

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

    # Convert date column to datetime if it's not already
    df["date"] = pd.to_datetime(df["date"])

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

    # Set titles
    fig.update_layout(
        title=f"Combined Futures Data: {os.path.basename(csv_file)} (Contract: {expected_contract_date})",
        xaxis_title="Time",
        height=800,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Price", secondary_y=False)
    fig.update_yaxes(title_text="Transaction Frequency", secondary_y=True)

    # Save to HTML file and open in browser
    output_file = (
        f"combined_plot_{os.path.splitext(os.path.basename(csv_file))[0]}.html"
    )
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
    args = parser.parse_args()

    if args.combined or args.all:
        plot_combined_data(args.csv_file)
    elif args.frequency:
        plot_frequency_data(args.csv_file)
    elif not args.all:  # Default behavior if no specific plot is requested
        plot_futures_data(args.csv_file)

    if args.all:
        plot_futures_data(args.csv_file)
        plot_frequency_data(args.csv_file)


if __name__ == "__main__":
    main()
