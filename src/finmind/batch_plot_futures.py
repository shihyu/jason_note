import argparse
import os
import re
import webbrowser
from datetime import datetime
import concurrent.futures
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_futures_data(csv_file, start_time=None, end_time=None, open_browser=True):
    """生成價格和交易量圖表"""
    # 檢查文件是否存在
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return

    # 從文件名提取日期（假設格式為 "2025-05-08.csv"）
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

    # 讀取 CSV 文件
    df = pd.read_csv(csv_file)
    print(f"Read {len(df)} rows from CSV file: {os.path.basename(csv_file)}")

    # 檢查 'contract_date' 列是否存在
    if "contract_date" not in df.columns:
        print(
            "Warning: 'contract_date' column not found in CSV file. Skipping contract filtering."
        )
    else:
        # 過濾掉 contract_date 包含斜線 "/" 的項目
        df = df[~df["contract_date"].astype(str).str.contains("/")]

        # 過濾特定合約日期
        if expected_contract_date:
            original_count = len(df)
            df = df[df["contract_date"].astype(str) == expected_contract_date]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows with contract_date not matching {expected_contract_date}"
            )

    # 檢查過濾後是否還有數據
    if df.empty:
        print("No valid data to plot after filtering.")
        return

    # 轉換日期列為 datetime 類型
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        print(f"Error converting date column: {e}")
        try:
            # 如果標準轉換失敗，嘗試不同格式
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S.%f")
        except Exception as e2:
            print(f"Error with alternative format: {e2}")
            return

    # 如果指定了時間範圍，則應用過濾
    if start_time and end_time:
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()

            # 按時間範圍過濾數據
            original_count = len(df)
            df = df[df["date"].dt.time.between(start_time_obj, end_time_obj)]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows outside time range {start_time} - {end_time}"
            )

            # 檢查時間過濾後是否還有數據
            if df.empty:
                print("No valid data to plot after time range filtering.")
                return
        except Exception as e:
            print(f"Error during time filtering: {e}")
            return

    # 按日期排序以確保時間順序
    df = df.sort_values("date")

    # 創建具有 2 行的子圖（價格和交易量）
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Price", "Volume"),
        row_heights=[0.7, 0.3],
    )

    # 添加價格跟踪
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["price"], name="Price", line=dict(color="blue", width=1)
        ),
        row=1,
        col=1,
    )

    # 添加交易量跟踪
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

    # 創建帶有時間範圍的標題（如果指定）
    title = f"Futures Data: {os.path.basename(csv_file)}"
    if expected_contract_date:
        title += f" (Contract: {expected_contract_date})"
    if start_time and end_time:
        title += f" [Time: {start_time} - {end_time}]"

    # 更新佈局
    fig.update_layout(
        title=title,
        height=800,
        hovermode="x unified",
        showlegend=False,
        template="plotly_white",
    )

    # 更新 x 軸 - 強制 x 軸範圍與過濾後的數據匹配
    if start_time and end_time:
        # 確保範圍完全設置為我們過濾後的數據
        min_date = df["date"].min()
        max_date = df["date"].max()
        fig.update_xaxes(range=[min_date, max_date], row=1, col=1)
        fig.update_xaxes(range=[min_date, max_date], row=2, col=1)

    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

    # 創建帶有時間範圍的輸出文件名（如果指定）
    time_suffix = ""
    if start_time and end_time:
        time_suffix = f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"

    # 創建輸出目錄
    output_dir = "futures_plots"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        f"futures_plot_{os.path.splitext(os.path.basename(csv_file))[0]}{time_suffix}.html",
    )
    fig.write_html(output_file)

    # 在瀏覽器中打開（只有在 open_browser 為 True 時）
    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
        print(f"Plot saved to {output_file} and opened in browser.")
    else:
        print(f"Plot saved to {output_file}")

    return df  # 返回過濾後的數據框以供潛在重用


def plot_frequency_data(csv_file, start_time=None, end_time=None, open_browser=True):
    """每10秒間隔繪製交易頻率圖"""
    # 檢查文件是否存在
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return

    # 從文件名提取合約日期
    filename_date_match = re.search(
        r"(\d{4})-(\d{2})-\d{2}", os.path.basename(csv_file)
    )
    expected_contract_date = None
    if filename_date_match:
        year, month = filename_date_match.groups()
        expected_contract_date = f"{year}{month}"

    # 讀取並過濾數據
    df = pd.read_csv(csv_file)
    print(f"Read {len(df)} rows for frequency analysis: {os.path.basename(csv_file)}")

    # 檢查 'contract_date' 列是否存在
    if "contract_date" in df.columns:
        # 過濾掉 contract_date 包含斜線 "/" 的項目
        df = df[~df["contract_date"].astype(str).str.contains("/")]

        # 過濾特定合約日期
        if expected_contract_date:
            original_count = len(df)
            df = df[df["contract_date"].astype(str) == expected_contract_date]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows with contract_date not matching {expected_contract_date}"
            )

    # 轉換日期列為 datetime 類型
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        print(f"Error converting date column: {e}")
        try:
            # 如果標準轉換失敗，嘗試不同格式
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S.%f")
        except Exception as e2:
            print(f"Error with alternative format: {e2}")
            return

    # 如果指定了時間範圍，則應用過濾
    if start_time and end_time:
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()

            # 按時間範圍過濾數據
            original_count = len(df)
            df = df[df["date"].dt.time.between(start_time_obj, end_time_obj)]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows outside time range {start_time} - {end_time}"
            )

            if df.empty:
                print("No data available for frequency analysis after time filtering.")
                return
        except Exception as e:
            print(f"Error during time filtering: {e}")
            return

    if df.empty:
        print("No data available for frequency analysis.")
        return

    # 創建數據框的副本以避免修改原始數據
    freq_df = df.copy()

    # 將時間戳四捨五入到 10 秒間隔
    freq_df["interval"] = freq_df["date"].apply(
        lambda x: x.replace(second=10 * (x.second // 10), microsecond=0)
    )

    # 計算每 10 秒間隔的交易數
    transaction_counts = freq_df.groupby("interval").size().reset_index(name="count")

    # 創建圖表
    fig = go.Figure()

    # 添加交易頻率跟踪
    fig.add_trace(
        go.Bar(
            x=transaction_counts["interval"],
            y=transaction_counts["count"],
            name="Transaction Frequency",
            marker=dict(color="rgba(0, 128, 0, 0.7)"),
        )
    )

    # 創建帶有時間範圍的標題（如果指定）
    title = f"Transaction Frequency (10-second intervals): {os.path.basename(csv_file)}"
    if start_time and end_time:
        title += f" [Time: {start_time} - {end_time}]"

    # 更新佈局
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Number of Transactions",
        height=600,
        template="plotly_white",
        hovermode="x unified",
    )

    # 如果指定了時間範圍，則顯式設置 x 軸範圍
    if start_time and end_time and not transaction_counts.empty:
        min_date = transaction_counts["interval"].min()
        max_date = transaction_counts["interval"].max()
        fig.update_xaxes(range=[min_date, max_date])

    # 創建帶有時間範圍的輸出文件名（如果指定）
    time_suffix = ""
    if start_time and end_time:
        time_suffix = f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"

    # 創建輸出目錄
    output_dir = "futures_plots"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        f"frequency_plot_{os.path.splitext(os.path.basename(csv_file))[0]}{time_suffix}.html",
    )
    fig.write_html(output_file)

    # 在瀏覽器中打開（只有在 open_browser 為 True 時）
    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
        print(f"Frequency plot saved to {output_file} and opened in browser.")
    else:
        print(f"Frequency plot saved to {output_file}")

    return transaction_counts  # 返回交易計數以供潛在重用


def plot_combined_data(csv_file, start_time=None, end_time=None, open_browser=True):
    """使用兩個不同的 Y 軸創建價格和交易頻率重疊的組合圖"""
    # 檢查文件是否存在
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        return

    # 從文件名提取日期（假設格式為 "2025-05-08.csv"）
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

    # 讀取 CSV 文件
    df = pd.read_csv(csv_file)
    print(f"Read {len(df)} rows for combined plot: {os.path.basename(csv_file)}")

    # 檢查 'contract_date' 列是否存在
    if "contract_date" in df.columns:
        # 過濾掉 contract_date 包含斜線 "/" 的項目
        df = df[~df["contract_date"].astype(str).str.contains("/")]

        # 過濾特定合約日期
        if expected_contract_date:
            original_count = len(df)
            df = df[df["contract_date"].astype(str) == expected_contract_date]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows with contract_date not matching {expected_contract_date}"
            )
    else:
        print("Warning: 'contract_date' column not found. Skipping contract filtering.")

    # 檢查過濾後是否還有數據
    if df.empty:
        print("No valid data to plot after filtering.")
        return

    # 轉換日期列為 datetime 類型
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as e:
        print(f"Error converting date column: {e}")
        try:
            # 如果標準轉換失敗，嘗試不同格式
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S.%f")
        except Exception as e2:
            print(f"Error with alternative format: {e2}")
            return

    # 如果指定了時間範圍，則應用過濾
    if start_time and end_time:
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()

            # 按時間範圍過濾數據
            original_count = len(df)
            df = df[df["date"].dt.time.between(start_time_obj, end_time_obj)]
            filtered_count = original_count - len(df)
            print(
                f"Filtered out {filtered_count} rows outside time range {start_time} - {end_time}"
            )

            # 檢查時間過濾後是否還有數據
            if df.empty:
                print("No valid data to plot after time range filtering.")
                return
        except Exception as e:
            print(f"Error during time filtering: {e}")
            return

    # 按日期排序以確保時間順序
    df = df.sort_values("date")

    # 計算 10 秒間隔交易頻率
    freq_df = df.copy()
    freq_df["interval"] = freq_df["date"].apply(
        lambda x: x.replace(second=10 * (x.second // 10), microsecond=0)
    )
    transaction_counts = freq_df.groupby("interval").size().reset_index(name="count")

    # 創建具有次要 y 軸的圖形
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 在主 y 軸上添加價格跟踪
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["price"], name="Price", line=dict(color="blue", width=1)
        ),
        secondary_y=False,
    )

    # 在次要 y 軸上添加交易頻率
    fig.add_trace(
        go.Bar(
            x=transaction_counts["interval"],
            y=transaction_counts["count"],
            name="Transaction Frequency (10s interval)",
            marker=dict(color="rgba(0, 128, 0, 0.5)"),
        ),
        secondary_y=True,
    )

    # 創建帶有時間範圍的標題（如果指定）
    title = f"Combined Futures Data: {os.path.basename(csv_file)}"
    if expected_contract_date:
        title += f" (Contract: {expected_contract_date})"
    if start_time and end_time:
        title += f" [Time: {start_time} - {end_time}]"

    # 設置標題
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        height=800,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # 設置 y 軸標題
    fig.update_yaxes(title_text="Price", secondary_y=False)
    fig.update_yaxes(title_text="Transaction Frequency", secondary_y=True)

    # 如果指定了時間範圍，則顯式設置 x 軸範圍
    if start_time and end_time:
        min_date = df["date"].min()
        max_date = df["date"].max()
        fig.update_xaxes(range=[min_date, max_date])

    # 創建帶有時間範圍的輸出文件名（如果指定）
    time_suffix = ""
    if start_time and end_time:
        time_suffix = f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"

    # 創建輸出目錄
    output_dir = "futures_plots"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        f"combined_plot_{os.path.splitext(os.path.basename(csv_file))[0]}{time_suffix}.html",
    )
    fig.write_html(output_file)

    # 在瀏覽器中打開（只有在 open_browser 為 True 時）
    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
        print(f"Combined plot saved to {output_file} and opened in browser.")
    else:
        print(f"Combined plot saved to {output_file}")


def process_csv_file(
    csv_file, start_time=None, end_time=None, plot_type="all", open_browser=False
):
    """處理單個 CSV 文件並生成指定類型的圖表"""
    print(f"\nProcessing file: {csv_file}")

    try:
        if plot_type == "price" or plot_type == "all":
            plot_futures_data(csv_file, start_time, end_time, open_browser)

        if plot_type == "frequency" or plot_type == "all":
            plot_frequency_data(csv_file, start_time, end_time, open_browser)

        if plot_type == "combined" or plot_type == "all":
            plot_combined_data(csv_file, start_time, end_time, open_browser)

        return True
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")
        return False


def batch_process_directory(
    directory,
    start_time=None,
    end_time=None,
    plot_type="all",
    max_workers=4,
    open_last=True,
):
    """批量處理目錄中的所有 CSV 文件"""
    # 確保目錄存在
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    # 獲取所有 CSV 文件
    csv_files = []
    for file in os.listdir(directory):
        if file.endswith(".csv") and re.search(r"\d{4}-\d{2}-\d{2}", file):
            csv_files.append(os.path.join(directory, file))

    if not csv_files:
        print(f"No CSV files with date format found in directory: {directory}")
        return

    # 按日期排序文件
    csv_files.sort()
    print(f"Found {len(csv_files)} CSV files to process.")

    # 使用線程池並行處理文件
    successful_files = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 為每個文件創建任務
        future_to_file = {
            executor.submit(
                process_csv_file,
                csv_file,
                start_time,
                end_time,
                plot_type,
                False,  # 不在處理過程中打開瀏覽器
            ): csv_file
            for csv_file in csv_files
        }

        # 處理結果
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                if future.result():
                    successful_files.append(file)
            except Exception as exc:
                print(f"File {file} generated an exception: {exc}")

    print(
        f"\nSuccessfully processed {len(successful_files)} of {len(csv_files)} files."
    )

    # 打開最後一個文件的圖（如果有的話）
    if open_last and successful_files:
        last_file = max(successful_files)  # 獲取最新的文件
        base_name = os.path.splitext(os.path.basename(last_file))[0]

        # 創建要打開的 HTML 文件路徑
        output_dir = "futures_plots"
        time_suffix = ""
        if start_time and end_time:
            time_suffix = (
                f"_time_{start_time.replace(':', '')}_{end_time.replace(':', '')}"
            )

        plots_to_open = []
        if plot_type == "price" or plot_type == "all":
            plots_to_open.append(
                os.path.join(output_dir, f"futures_plot_{base_name}{time_suffix}.html")
            )
        if plot_type == "frequency" or plot_type == "all":
            plots_to_open.append(
                os.path.join(
                    output_dir, f"frequency_plot_{base_name}{time_suffix}.html"
                )
            )
        if plot_type == "combined" or plot_type == "all":
            plots_to_open.append(
                os.path.join(output_dir, f"combined_plot_{base_name}{time_suffix}.html")
            )

        # 打開圖表
        for plot_file in plots_to_open:
            if os.path.exists(plot_file):
                print(f"Opening plot: {plot_file}")
                webbrowser.open(f"file://{os.path.abspath(plot_file)}")


def create_index_html(output_dir="futures_plots"):
    """創建索引HTML頁面，列出所有生成的圖表"""
    # 確保輸出目錄存在
    if not os.path.exists(output_dir):
        print(f"No plots found in {output_dir}. Index creation skipped.")
        return

    # 收集所有html文件
    html_files = [f for f in os.listdir(output_dir) if f.endswith(".html")]

    if not html_files:
        print(f"No HTML files found in {output_dir}. Index creation skipped.")
        return

    # 按日期排序
    html_files.sort(reverse=True)  # 最新的文件排在最前面

    # 創建索引HTML
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taiwan Futures Data Plots</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .date-section {
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 20px;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
            border-radius: 3px;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .plot-type {
            display: inline-block;
            width: 120px;
            font-weight: bold;
        }
        .time-range {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .search-container {
            margin-bottom: 20px;
            text-align: center;
        }
        #searchInput {
            padding: 10px;
            width: 50%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Taiwan Futures Data Plots</h1>
        
        <div class="search-container">
            <input type="text" id="searchInput" placeholder="Search by date or plot type...">
        </div>
        
"""

    # 按日期分組
    date_groups = {}
    for html_file in html_files:
        # 提取日期
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", html_file)
        if date_match:
            date = date_match.group(0)
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(html_file)

    # 為每個日期創建一個部分
    for date in sorted(date_groups.keys(), reverse=True):
        index_content += f'        <div class="date-section">\n'
        index_content += f"            <h2>Date: {date}</h2>\n"
        index_content += f"            <ul>\n"

        # 按圖表類型排序：先合併圖，然後價格圖，最後頻率圖
        sorted_files = sorted(
            date_groups[date],
            key=lambda x: (
                0 if "combined_plot" in x else (1 if "futures_plot" in x else 2),
                x,  # 次要排序依據
            ),
        )

        for html_file in sorted_files:
            # 確定圖表類型
            plot_type = "Combined Plot"
            if "futures_plot" in html_file:
                plot_type = "Price & Volume"
            elif "frequency_plot" in html_file:
                plot_type = "Frequency"

            # 提取時間範圍（如果有）
            time_range = ""
            time_match = re.search(
                r"time_(\d{2})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})", html_file
            )
            if time_match:
                start_h, start_m, start_s, end_h, end_m, end_s = time_match.groups()
                time_range = f"{start_h}:{start_m}:{start_s} - {end_h}:{end_m}:{end_s}"

            index_content += f'                <li><a href="{html_file}"><span class="plot-type">{plot_type}</span>{html_file}</a>'
            if time_range:
                index_content += f' <span class="time-range">({time_range})</span>'
            index_content += "</li>\n"

        index_content += "            </ul>\n"
        index_content += "        </div>\n"

    # 完成 HTML
    index_content += """
        <script>
            // 簡單的搜索功能
            document.getElementById('searchInput').addEventListener('keyup', function() {
                const searchText = this.value.toLowerCase();
                const sections = document.querySelectorAll('.date-section');
                
                sections.forEach(function(section) {
                    const dateText = section.querySelector('h2').textContent.toLowerCase();
                    const items = section.querySelectorAll('li');
                    let hasVisibleItems = false;
                    
                    items.forEach(function(item) {
                        const itemText = item.textContent.toLowerCase();
                        if (itemText.includes(searchText) || dateText.includes(searchText)) {
                            item.style.display = '';
                            hasVisibleItems = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });
                    
                    section.style.display = hasVisibleItems ? '' : 'none';
                });
            });
        </script>
    </div>
</body>
</html>
"""

    # 寫入索引文件
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"Index created at {index_path}")
    webbrowser.open(f"file://{os.path.abspath(index_path)}")
    return index_path


def main():
    parser = argparse.ArgumentParser(
        description="Batch process futures data from CSV files"
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        help="Directory containing CSV files (e.g., TaiwanFuturesTick/days)",
        default="TaiwanFuturesTick/days",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="Process a single CSV file instead of a directory",
    )
    parser.add_argument(
        "--plot-type",
        "-p",
        type=str,
        choices=["price", "frequency", "combined", "all"],
        default="all",
        help="Type of plot to generate (default: all)",
    )
    parser.add_argument(
        "--start-time", type=str, help="Start time in HH:MM:SS format (e.g., 00:00:00)"
    )
    parser.add_argument(
        "--end-time", type=str, help="End time in HH:MM:SS format (e.g., 05:00:00)"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing (default: 4)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open plots in browser automatically",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug information about the CSV file",
    )
    args = parser.parse_args()

    # 驗證時間格式（如果提供）
    start_time = args.start_time
    end_time = args.end_time

    # 檢查是否同時提供了開始和結束時間，或者都未提供
    if (start_time and not end_time) or (not start_time and end_time):
        print("Error: Both --start-time and --end-time must be specified together.")
        return

    # 驗證時間格式
    if start_time and end_time:
        try:
            datetime.strptime(start_time, "%H:%M:%S")
            datetime.strptime(end_time, "%H:%M:%S")
            print(f"Filtering data for time range: {start_time} - {end_time}")
        except ValueError:
            print("Error: Time format should be HH:MM:SS (e.g., 00:00:00)")
            return

    # 處理單個文件或目錄
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found.")
            return

        process_csv_file(
            args.file, start_time, end_time, args.plot_type, not args.no_browser
        )
    else:
        # 批量處理目錄
        batch_process_directory(
            args.directory,
            start_time,
            end_time,
            args.plot_type,
            args.workers,
            not args.no_browser,
        )

        # 創建索引 HTML
        create_index_html()


# python batch_plot_futures.py --start-time 00:00:00 --end-time 05:00:00  --plot-type combined
if __name__ == "__main__":
    main()
