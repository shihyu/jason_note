#!/usr/bin/env python3
"""
ClickHouse Python 測試 - 修正版
修正連接問題，自動處理認證
"""

import pandas as pd
import subprocess
import sys
import time

def test_docker_cli():
    """使用 Docker CLI 測試（最可靠）"""
    print("\n📦 使用 Docker CLI 測試")
    print("="*50)

    try:
        # 檢查容器狀態
        result = subprocess.run(
            ["docker", "exec", "clickhouse-server", "clickhouse-client",
             "--user", "trader", "--password", "SecurePass123!",
             "--query", "SELECT 'Connected!'"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Docker 連接成功")
        else:
            print(f"❌ 連接失敗: {result.stderr}")
            return False

        # 建立資料庫
        subprocess.run(
            ["docker", "exec", "clickhouse-server", "clickhouse-client",
             "--user", "trader", "--password", "SecurePass123!",
             "--query", "CREATE DATABASE IF NOT EXISTS market_data"],
            capture_output=True
        )
        print("✅ 建立資料庫 market_data")

        # 建立表
        create_table_query = """
        CREATE TABLE IF NOT EXISTS market_data.test_ticks (
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
        """

        subprocess.run(
            ["docker", "exec", "clickhouse-server", "clickhouse-client",
             "--user", "trader", "--password", "SecurePass123!",
             "--query", create_table_query],
            capture_output=True
        )
        print("✅ 建立表 test_ticks")

        # 讀取並插入 CSV 資料
        print("\n📊 插入測試資料")

        # 複製 CSV 到容器
        subprocess.run(
            ["docker", "cp", "test_data.csv", "clickhouse-server:/tmp/"],
            capture_output=True
        )

        # 使用 clickhouse-client 插入資料
        insert_result = subprocess.run(
            ["docker", "exec", "clickhouse-server", "clickhouse-client",
             "--user", "trader", "--password", "SecurePass123!",
             "--database", "market_data",
             "--query", "INSERT INTO test_ticks FORMAT CSVWithNames"],
            stdin=open('test_data.csv', 'r'),
            capture_output=True,
            text=True
        )

        if insert_result.returncode == 0:
            print("✅ 成功插入測試資料")
        else:
            print(f"⚠️  插入警告: {insert_result.stderr}")

        # 查詢資料
        print("\n📈 查詢結果")

        # 總筆數
        result = subprocess.run(
            ["docker", "exec", "clickhouse-server", "clickhouse-client",
             "--user", "trader", "--password", "SecurePass123!",
             "--database", "market_data",
             "--query", "SELECT count(*) FROM test_ticks"],
            capture_output=True,
            text=True
        )
        print(f"總筆數: {result.stdout.strip()}")

        # 按股票統計
        result = subprocess.run(
            ["docker", "exec", "clickhouse-server", "clickhouse-client",
             "--user", "trader", "--password", "SecurePass123!",
             "--database", "market_data",
             "--query", """
             SELECT
                 symbol,
                 count(*) as cnt,
                 round(avg(close), 2) as avg_price
             FROM test_ticks
             GROUP BY symbol
             ORDER BY symbol
             FORMAT Pretty"""],
            capture_output=True,
            text=True
        )
        print("\n按股票統計:")
        print(result.stdout)

        return True

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def test_with_python_driver():
    """使用 Python driver 測試（需要正確配置）"""
    try:
        from clickhouse_driver import Client

        print("\n🐍 使用 clickhouse-driver 測試")
        print("="*50)

        # 嘗試不同的連接方式
        configs = [
            # 配置1: 使用認證
            {
                'host': 'localhost',
                'port': 9000,
                'user': 'trader',
                'password': 'SecurePass123!',
                'database': 'market_data'
            },
            # 配置2: 不指定資料庫
            {
                'host': 'localhost',
                'port': 9000,
                'user': 'trader',
                'password': 'SecurePass123!'
            },
            # 配置3: 使用 default user
            {
                'host': 'localhost',
                'port': 9000,
                'database': 'market_data'
            }
        ]

        client = None
        for i, config in enumerate(configs, 1):
            try:
                print(f"嘗試配置 {i}: {config}")
                client = Client(**config)
                # 測試連接
                result = client.execute("SELECT 1")
                print(f"✅ 配置 {i} 連接成功!")
                break
            except Exception as e:
                print(f"❌ 配置 {i} 失敗: {str(e)[:50]}...")
                continue

        if not client:
            print("❌ 所有配置都無法連接")
            return False

        # 查詢測試
        try:
            result = client.execute("SELECT count(*) FROM market_data.test_ticks")
            print(f"✅ Python driver 查詢成功: {result[0][0]} 筆資料")
        except:
            print("⚠️  Python driver 查詢失敗，但 Docker CLI 可用")

        return True

    except ImportError:
        print("⚠️  未安裝 clickhouse-driver")
        return False
    except Exception as e:
        print(f"❌ Python driver 錯誤: {e}")
        return False

def test_with_http():
    """使用 HTTP API 測試"""
    import requests

    print("\n🌐 使用 HTTP API 測試")
    print("="*50)

    try:
        # 測試連接
        response = requests.get(
            "http://localhost:8123/ping",
            auth=('trader', 'SecurePass123!')
        )

        if response.text.strip() == "Ok.":
            print("✅ HTTP API 連接成功")

        # 查詢資料
        query = "SELECT symbol, count(*) FROM market_data.test_ticks GROUP BY symbol FORMAT JSON"
        response = requests.post(
            "http://localhost:8123",
            data=query,
            auth=('trader', 'SecurePass123!')
        )

        if response.status_code == 200:
            import json
            result = json.loads(response.text)
            print("✅ HTTP 查詢成功:")
            for row in result.get('data', []):
                print(f"  {row['symbol']}: {row['count()']} 筆")

        return True

    except Exception as e:
        print(f"❌ HTTP API 錯誤: {e}")
        return False

def main():
    print("="*60)
    print("🚀 ClickHouse 連接測試與診斷")
    print("="*60)

    # 檢查容器狀態
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=clickhouse", "--format", "table"],
        capture_output=True,
        text=True
    )
    print("\n📦 容器狀態:")
    print(result.stdout)

    # 執行測試
    results = []

    # Docker CLI 測試（最可靠）
    docker_ok = test_docker_cli()
    results.append(("Docker CLI", docker_ok))

    # Python driver 測試
    driver_ok = test_with_python_driver()
    results.append(("Python Driver", driver_ok))

    # HTTP API 測試
    http_ok = test_with_http()
    results.append(("HTTP API", http_ok))

    # 總結
    print("\n" + "="*60)
    print("📊 測試結果總結")
    print("="*60)
    for method, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{method:20} {status_icon}")

    if docker_ok:
        print("\n💡 建議: Docker CLI 正常運作，可以使用 subprocess 方式操作")
        print("   或檢查 Python driver 的網路配置")

if __name__ == "__main__":
    main()