#!/usr/bin/env python3
"""
ClickHouse Python 完整範例
包含讀取 CSV、寫入資料、查詢、匯出等功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from clickhouse_driver import Client
import sys

class ClickHouseDemo:
    def __init__(self, host='localhost', port=9000, user='trader', password='SecurePass123!', database='market_data'):
        """初始化 ClickHouse 連接"""
        self.client = Client(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print(f"✅ 連接到 ClickHouse {host}:{port}/{database}")

    def create_table(self, table_name='market_ticks_demo'):
        """建立測試表"""
        try:
            # 刪除舊表
            self.client.execute(f"DROP TABLE IF EXISTS {table_name}")

            # 建立新表
            query = f"""
            CREATE TABLE {table_name} (
                ts DateTime64(3),
                symbol String,
                close Decimal64(2),
                volume UInt64,
                bid_price Decimal64(2),
                bid_volume UInt32,
                ask_price Decimal64(2),
                ask_volume UInt32,
                tick_type UInt8
            ) ENGINE = MergeTree()
            PARTITION BY toYYYYMM(ts)
            ORDER BY (symbol, ts)
            """
            self.client.execute(query)
            print(f"✅ 建立表 {table_name}")
            return True
        except Exception as e:
            print(f"❌ 建立表失敗: {e}")
            return False

    def read_csv_and_insert(self, csv_file='test_data.csv', table_name='market_ticks_demo'):
        """從 CSV 讀取資料並插入"""
        try:
            # 讀取 CSV
            df = pd.read_csv(csv_file)
            print(f"✅ 讀取 {len(df)} 筆資料從 {csv_file}")

            # 轉換時間格式
            df['ts'] = pd.to_datetime(df['ts'])

            # 準備資料
            data = []
            for _, row in df.iterrows():
                data.append((
                    row['ts'],
                    str(row['symbol']),
                    float(row['close']),
                    int(row['volume']),
                    float(row['bid_price']),
                    int(row['bid_volume']),
                    float(row['ask_price']),
                    int(row['ask_volume']),
                    int(row['tick_type'])
                ))

            # 批次插入
            self.client.execute(f'INSERT INTO {table_name} VALUES', data)
            print(f"✅ 成功插入 {len(data)} 筆資料到 {table_name}")
            return True

        except FileNotFoundError:
            # 如果找不到檔案，建立測試資料
            print(f"⚠️  找不到 {csv_file}，建立測試資料...")
            return self.insert_test_data(table_name)

        except Exception as e:
            print(f"❌ 插入失敗: {e}")
            return False

    def insert_test_data(self, table_name='market_ticks_demo'):
        """插入測試資料"""
        try:
            # 產生測試資料
            symbols = ['AAPL', 'GOOGL', 'TSLA', 'NVDA', 'MSFT']
            data = []

            base_time = datetime.now() - timedelta(hours=1)

            for i in range(100):
                symbol = np.random.choice(symbols)
                ts = base_time + timedelta(seconds=i*10)
                price = 1000 + np.random.randn() * 50
                volume = np.random.randint(100, 1000)

                data.append((
                    ts,
                    symbol,
                    round(price, 2),
                    volume,
                    round(price - np.random.uniform(1, 5), 2),
                    np.random.randint(10, 100),
                    round(price + np.random.uniform(1, 5), 2),
                    np.random.randint(10, 100),
                    np.random.randint(1, 4)
                ))

            self.client.execute(f'INSERT INTO {table_name} VALUES', data)
            print(f"✅ 插入 {len(data)} 筆測試資料")
            return True

        except Exception as e:
            print(f"❌ 插入測試資料失敗: {e}")
            return False

    def query_examples(self, table_name='market_ticks_demo'):
        """各種查詢範例"""
        print("\n" + "="*60)
        print("📊 查詢範例")
        print("="*60)

        # 1. 總筆數
        result = self.client.execute(f"SELECT count(*) FROM {table_name}")
        print(f"\n1. 總資料筆數: {result[0][0]}")

        # 2. 按股票統計
        result = self.client.execute(f"""
            SELECT
                symbol,
                count(*) as tick_count,
                round(avg(toFloat64(close)), 2) as avg_price,
                max(volume) as max_volume,
                round(min(toFloat64(bid_price)), 2) as min_bid,
                round(max(toFloat64(ask_price)), 2) as max_ask
            FROM {table_name}
            GROUP BY symbol
            ORDER BY symbol
        """)

        print("\n2. 按股票統計:")
        print(f"{'股票':<10} {'筆數':<10} {'平均價':<10} {'最大量':<10} {'最低買價':<10} {'最高賣價':<10}")
        print("-"*60)
        for row in result:
            print(f"{row[0]:<10} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10}")

        # 3. 最新資料
        result = self.client.execute(f"""
            SELECT
                symbol,
                ts,
                close,
                volume
            FROM {table_name}
            ORDER BY ts DESC
            LIMIT 5
        """)

        print("\n3. 最新5筆資料:")
        print(f"{'股票':<10} {'時間':<25} {'收盤價':<10} {'成交量':<10}")
        print("-"*55)
        for row in result:
            print(f"{row[0]:<10} {str(row[1]):<25} {row[2]:<10} {row[3]:<10}")

    def export_to_csv(self, table_name='market_ticks_demo', output_file='exported_data.csv'):
        """匯出資料到 CSV"""
        try:
            # 查詢所有資料
            result = self.client.execute(f"""
                SELECT * FROM {table_name}
                ORDER BY ts
            """, with_column_types=True)

            # 取得資料和欄位名稱
            data = result[0]
            columns = [col[0] for col in result[1]]

            # 建立 DataFrame
            df = pd.DataFrame(data, columns=columns)

            # 儲存到 CSV
            df.to_csv(output_file, index=False)
            print(f"\n✅ 匯出 {len(df)} 筆資料到 {output_file}")

            return df

        except Exception as e:
            print(f"❌ 匯出失敗: {e}")
            return None

    def advanced_queries(self, table_name='market_ticks_demo'):
        """進階查詢範例"""
        print("\n" + "="*60)
        print("🚀 進階查詢範例")
        print("="*60)

        try:
            # 1. 時間序列分析
            result = self.client.execute(f"""
                SELECT
                    toStartOfMinute(ts) as minute,
                    count(*) as tick_count,
                    round(avg(toFloat64(close)), 2) as avg_price
                FROM {table_name}
                GROUP BY minute
                ORDER BY minute DESC
                LIMIT 10
            """)

            if result:
                print("\n1. 每分鐘統計 (最新10分鐘):")
                for row in result:
                    print(f"  {row[0]}: {row[1]} 筆, 平均價 {row[2]}")

            # 2. 價差分析
            result = self.client.execute(f"""
                SELECT
                    symbol,
                    round(avg(toFloat64(ask_price) - toFloat64(bid_price)), 2) as avg_spread,
                    round(max(toFloat64(ask_price) - toFloat64(bid_price)), 2) as max_spread
                FROM {table_name}
                GROUP BY symbol
                ORDER BY avg_spread DESC
            """)

            if result:
                print("\n2. 買賣價差分析:")
                for row in result:
                    print(f"  {row[0]}: 平均價差 {row[1]}, 最大價差 {row[2]}")

        except Exception as e:
            print(f"⚠️  進階查詢失敗: {e}")

    def close(self):
        """關閉連接"""
        self.client.disconnect()
        print("\n✅ 關閉 ClickHouse 連接")

def main():
    """主程式"""
    print("="*60)
    print("🚀 ClickHouse Python 完整範例")
    print("="*60)

    # 建立連接
    demo = ClickHouseDemo()

    # 建立表
    if not demo.create_table():
        sys.exit(1)

    # 讀取 CSV 並插入（如果沒有 CSV 會自動產生測試資料）
    if not demo.read_csv_and_insert():
        sys.exit(1)

    # 執行查詢範例
    demo.query_examples()

    # 進階查詢
    demo.advanced_queries()

    # 匯出資料
    df = demo.export_to_csv()

    # 關閉連接
    demo.close()

    print("\n" + "="*60)
    print("✅ 範例執行完成！")
    print("="*60)

if __name__ == "__main__":
    main()