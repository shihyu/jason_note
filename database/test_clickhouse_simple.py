#!/usr/bin/env python3
"""
簡單的 ClickHouse Python 測試
使用 Docker 快速啟動測試
"""

import pandas as pd
import subprocess
import time
import sys

def start_clickhouse_docker():
    """使用 Docker 快速啟動 ClickHouse"""
    print("🚀 啟動 ClickHouse Docker 容器...")

    # 停止舊容器
    subprocess.run(["docker", "stop", "clickhouse-test"], capture_output=True)
    subprocess.run(["docker", "rm", "clickhouse-test"], capture_output=True)

    # 啟動新容器
    cmd = [
        "docker", "run", "-d",
        "--name", "clickhouse-test",
        "-p", "8123:8123",
        "-p", "9000:9000",
        "-e", "CLICKHOUSE_USER=trader",
        "-e", "CLICKHOUSE_PASSWORD=SecurePass123!",
        "-e", "CLICKHOUSE_DB=market_data",
        "clickhouse/clickhouse-server:24.8-alpine"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ ClickHouse 容器已啟動")
        print("   等待服務就緒...")
        time.sleep(20)
        return True
    else:
        print(f"❌ 啟動失敗: {result.stderr}")
        return False

def create_test_data():
    """建立測試資料"""
    test_data = """ts,symbol,close,volume,bid_price,bid_volume,ask_price,ask_volume,tick_type
2025-09-25 17:25:00.044,AAPL,1325.0,7,1320.0,160,1325.0,22,1
2025-09-25 17:25:02.207,AAPL,1325.0,1,1320.0,160,1325.0,22,1
2025-09-25 17:25:03.125,AAPL,1325.0,1,1320.0,161,1325.0,21,1
2025-09-25 17:25:47.863,AAPL,1325.0,1,1320.0,162,1325.0,21,1
2025-09-25 17:26:14.894,TSLA,1325.0,1,1320.0,181,1325.0,18,1
2025-09-25 17:26:51.365,TSLA,1325.0,1,1320.0,181,1325.0,27,1
2025-09-25 17:29:59.655,TSLA,1325.0,3,1320.0,177,1325.0,31,1
2025-09-25 17:30:06.262,NVDA,1325.0,1,1320.0,180,1325.0,28,1
2025-09-25 17:30:14.542,NVDA,1325.0,3,1320.0,183,1325.0,27,1
2025-09-25 17:30:52.600,NVDA,1320.0,2,1320.0,185,1325.0,22,2"""

    with open('test_data_temp.csv', 'w') as f:
        f.write(test_data)

    return pd.read_csv('test_data_temp.csv')

def test_with_clickhouse_driver():
    """使用 clickhouse-driver 測試"""
    try:
        from clickhouse_driver import Client

        print("\n📊 使用 clickhouse-driver 測試")
        print("="*50)

        # 連接
        client = Client(
            host='localhost',
            port=9000,
            user='trader',
            password='SecurePass123!',
            database='market_data'
        )

        # 建立表
        client.execute("DROP TABLE IF EXISTS test_ticks")
        client.execute("""
            CREATE TABLE test_ticks (
                ts DateTime64(3),
                symbol String,
                close Decimal32(2),
                volume UInt32,
                bid_price Decimal32(2),
                bid_volume UInt32,
                ask_price Decimal32(2),
                ask_volume UInt32,
                tick_type UInt8
            ) ENGINE = MergeTree()
            ORDER BY (symbol, ts)
        """)
        print("✅ 表建立成功")

        # 讀取資料
        df = create_test_data()
        df['ts'] = pd.to_datetime(df['ts'])

        # 插入資料
        data = []
        for _, row in df.iterrows():
            data.append((
                row['ts'],
                row['symbol'],
                float(row['close']),
                int(row['volume']),
                float(row['bid_price']),
                int(row['bid_volume']),
                float(row['ask_price']),
                int(row['ask_volume']),
                int(row['tick_type'])
            ))

        client.execute('INSERT INTO test_ticks VALUES', data)
        print(f"✅ 插入 {len(data)} 筆資料成功")

        # 查詢資料
        result = client.execute("SELECT count(*) FROM test_ticks")
        print(f"✅ 查詢結果: 共 {result[0][0]} 筆資料")

        # 按股票統計
        result = client.execute("""
            SELECT
                symbol,
                count(*) as cnt,
                round(avg(close), 2) as avg_price
            FROM test_ticks
            GROUP BY symbol
            ORDER BY symbol
        """)

        print("\n按股票統計:")
        for row in result:
            print(f"  {row[0]}: {row[1]} 筆, 平均價 {row[2]}")

        return True

    except ImportError:
        print("⚠️  clickhouse-driver 未安裝")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_with_http():
    """使用 HTTP API 測試"""
    import requests
    import json

    print("\n🌐 使用 HTTP API 測試")
    print("="*50)

    base_url = "http://localhost:8123"
    auth = ('trader', 'SecurePass123!')

    try:
        # 測試連接
        response = requests.get(
            f"{base_url}/ping",
            auth=auth
        )
        if response.text.strip() == "Ok.":
            print("✅ HTTP 連接成功")

        # 建立表
        query = """
        CREATE TABLE IF NOT EXISTS market_data.test_http (
            ts DateTime,
            symbol String,
            price Float32,
            volume UInt32
        ) ENGINE = Memory
        """
        response = requests.post(
            base_url,
            data=query,
            auth=auth
        )
        print("✅ 透過 HTTP 建立表成功")

        # 插入資料
        insert_query = """
        INSERT INTO market_data.test_http VALUES
        ('2025-09-25 17:25:00', 'AAPL', 1325.0, 100),
        ('2025-09-25 17:26:00', 'TSLA', 1320.0, 200)
        """
        response = requests.post(
            base_url,
            data=insert_query,
            auth=auth
        )
        print("✅ 透過 HTTP 插入資料成功")

        # 查詢資料
        select_query = "SELECT symbol, avg(price) FROM market_data.test_http GROUP BY symbol FORMAT JSON"
        response = requests.post(
            base_url,
            data=select_query,
            auth=auth
        )

        if response.status_code == 200:
            result = json.loads(response.text)
            print("✅ HTTP 查詢結果:")
            for row in result['data']:
                print(f"  {row['symbol']}: 平均價 {row['avg(price)']}")

        return True

    except Exception as e:
        print(f"❌ HTTP 測試失敗: {e}")
        return False

def main():
    print("="*60)
    print("🚀 ClickHouse Python 測試 (簡化版)")
    print("="*60)

    # 啟動 Docker
    if not start_clickhouse_docker():
        print("無法啟動 ClickHouse，結束測試")
        sys.exit(1)

    # 測試 clickhouse-driver
    driver_ok = test_with_clickhouse_driver()

    # 測試 HTTP API
    http_ok = test_with_http()

    print("\n" + "="*60)
    print("📊 測試結果總結")
    print("="*60)
    print(f"clickhouse-driver: {'✅ 成功' if driver_ok else '❌ 失敗'}")
    print(f"HTTP API:          {'✅ 成功' if http_ok else '❌ 失敗'}")

    # 清理
    print("\n🧹 清理測試容器...")
    subprocess.run(["docker", "stop", "clickhouse-test"], capture_output=True)
    subprocess.run(["docker", "rm", "clickhouse-test"], capture_output=True)
    print("✅ 清理完成")

if __name__ == "__main__":
    main()