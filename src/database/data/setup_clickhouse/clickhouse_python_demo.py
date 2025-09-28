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
import time

class ClickHouseDemo:
    def __init__(self, host='localhost', port=9000, user='trader', password='SecurePass123!', database='market_data'):
        """初始化 ClickHouse 連接"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self.client = Client(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    settings={'use_numpy': False}  # 避免 numpy 相關問題
                )
                # 測試連線
                self.client.execute('SELECT 1')
                print(f"✅ 連接到 ClickHouse {host}:{port}/{database}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  連線失敗，{retry_delay}秒後重試... (嘗試 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ 無法連接到 ClickHouse: {e}")
                    raise

    def create_table(self, table_name='market_ticks_demo'):
        """建立測試表（使用 ReplacingMergeTree 支援去重）"""
        try:
            # 刪除舊表
            self.client.execute(f"DROP TABLE IF EXISTS {table_name}")

            # 建立新表（使用 ReplacingMergeTree）
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
                tick_type UInt8,
                _version UInt64 DEFAULT toUnixTimestamp64Milli(now64(3))
            ) ENGINE = ReplacingMergeTree(_version)
            PARTITION BY toYYYYMM(ts)
            ORDER BY (symbol, ts)
            """
            self.client.execute(query)
            print(f"✅ 建立表 {table_name} (使用 ReplacingMergeTree 自動去重)")
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

            # 準備資料（不包含 _version，讓它使用預設值）
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

            # 批次插入（指定欄位名稱）
            self.client.execute(f'INSERT INTO {table_name} (ts, symbol, close, volume, bid_price, bid_volume, ask_price, ask_volume, tick_type) VALUES', data)
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

            # 指定欄位名稱插入
            self.client.execute(f'INSERT INTO {table_name} (ts, symbol, close, volume, bid_price, bid_volume, ask_price, ask_volume, tick_type) VALUES', data)
            print(f"✅ 插入 {len(data)} 筆測試資料")
            return True

        except Exception as e:
            print(f"❌ 插入測試資料失敗: {e}")
            return False

    def print_csv_format(self, table_name='market_ticks_demo'):
        """讀取資料庫並以 CSV 格式打印"""
        try:
            # 查詢所有資料，按時間排序
            result = self.client.execute(f"""
                SELECT
                    ts,
                    symbol,
                    close,
                    volume,
                    bid_price,
                    bid_volume,
                    ask_price,
                    ask_volume,
                    tick_type
                FROM {table_name}
                ORDER BY ts
            """)

            # 打印 CSV 標題
            print("ts,symbol,close,volume,bid_price,bid_volume,ask_price,ask_volume,tick_type")

            # 打印每一行資料
            for row in result:
                # 格式化時間戳，保留毫秒
                ts_str = row[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f"{ts_str},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}")

        except Exception as e:
            print(f"❌ 讀取失敗: {e}")

    def get_dataframe_with_markdown(self, table_name='market_ticks_demo'):
        """讀取資料庫內容到 DataFrame 並以 Markdown 格式顯示"""
        try:
            # 查詢所有資料，按時間排序
            result = self.client.execute(f"""
                SELECT
                    ts,
                    symbol,
                    close,
                    volume,
                    bid_price,
                    bid_volume,
                    ask_price,
                    ask_volume,
                    tick_type
                FROM {table_name}
                ORDER BY ts
            """, with_column_types=True)

            # 取得資料和欄位名稱
            data = result[0]
            columns = [col[0] for col in result[1]]

            # 建立 DataFrame
            df = pd.DataFrame(data, columns=columns)

            # 格式化時間戳欄位，保留毫秒
            df['ts'] = pd.to_datetime(df['ts']).dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-3]

            # 打印 Markdown 格式表格
            print("\n📊 資料庫內容 (Markdown 表格):")
            print(df.to_markdown(floatfmt=".2f", tablefmt="heavy_grid"))

            # 也顯示 DataFrame 資訊
            print(f"\n📈 DataFrame 資訊:")
            print(f"   總筆數: {len(df)} 筆")
            print(f"   欄位數: {len(df.columns)} 欄")
            print(f"   股票: {df['symbol'].unique().tolist()}")
            print(f"   時間範圍: {df['ts'].iloc[0]} ~ {df['ts'].iloc[-1]}")

            return df

        except Exception as e:
            print(f"❌ 讀取失敗: {e}")
            return None

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

    def test_deduplication(self, table_name='market_ticks_demo'):
        """測試去重功能"""
        print("\n" + "="*60)
        print("🔍 測試 ReplacingMergeTree 去重功能")
        print("="*60)

        try:
            # 插入重複資料進行測試
            test_data = []
            base_time = datetime.now()

            # 原始資料
            for i in range(3):
                test_data.append((
                    base_time,
                    'TEST_DUP',
                    100.0 + i,
                    1000 + i*100,
                    99.0 + i,
                    100,
                    101.0 + i,
                    100,
                    1
                ))

            # 插入原始資料
            self.client.execute(f'INSERT INTO {table_name} (ts, symbol, close, volume, bid_price, bid_volume, ask_price, ask_volume, tick_type) VALUES', test_data)
            print(f"✅ 插入 {len(test_data)} 筆原始資料")

            # 插入重複資料（相同的 ts 和 symbol）
            duplicate_data = []
            for i in range(3):
                duplicate_data.append((
                    base_time,  # 相同時間
                    'TEST_DUP',  # 相同股票
                    200.0 + i,  # 不同價格
                    2000 + i*100,
                    199.0 + i,
                    200,
                    201.0 + i,
                    200,
                    2
                ))

            self.client.execute(f'INSERT INTO {table_name} (ts, symbol, close, volume, bid_price, bid_volume, ask_price, ask_volume, tick_type) VALUES', duplicate_data)
            print(f"✅ 插入 {len(duplicate_data)} 筆重複資料（相同 ts 和 symbol）")

            # 查看去重前的資料
            result_before = self.client.execute(f"SELECT count(*) FROM {table_name} WHERE symbol = 'TEST_DUP'")
            print(f"\n去重前: {result_before[0][0]} 筆")

            # 執行優化以觸發去重
            self.client.execute(f"OPTIMIZE TABLE {table_name} FINAL")
            print("✅ 執行 OPTIMIZE TABLE FINAL 觸發去重")

            # 查看去重後的資料（使用 FINAL）
            result_after = self.client.execute(f"SELECT count(*) FROM {table_name} FINAL WHERE symbol = 'TEST_DUP'")
            print(f"去重後: {result_after[0][0]} 筆")

            # 顯示去重效果
            dedup_count = result_before[0][0] - result_after[0][0]
            dedup_rate = (dedup_count / result_before[0][0]) * 100 if result_before[0][0] > 0 else 0
            print(f"\n📊 去重效果:")
            print(f"  移除了 {dedup_count} 筆重複資料")
            print(f"  去重率: {dedup_rate:.1f}%")

            # 顯示保留的資料
            final_data = self.client.execute(f"""
                SELECT ts, symbol, close, volume
                FROM {table_name} FINAL
                WHERE symbol = 'TEST_DUP'
                ORDER BY ts, close
            """)

            if final_data:
                print(f"\n保留的資料（最新版本）:")
                for row in final_data:
                    print(f"  {row[0]} | {row[1]} | 價格: {row[2]} | 數量: {row[3]}")

        except Exception as e:
            print(f"❌ 去重測試失敗: {e}")

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
                FROM {table_name} FINAL
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
                FROM {table_name} FINAL
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

    try:
        # 建立連接
        demo = ClickHouseDemo()

        # 建立表
        if not demo.create_table():
            sys.exit(1)

        # 讀取 CSV 並插入（如果沒有 CSV 會自動產生測試資料）
        if not demo.read_csv_and_insert():
            sys.exit(1)

        # 測試去重功能
        demo.test_deduplication()

        # 打印 CSV 格式的資料（與 test_data.csv 相同格式）
        print("\n" + "="*60)
        print("📄 資料庫內容（CSV 格式）")
        print("="*60)
        demo.print_csv_format()

        # 將資料庫內容存放到 DataFrame 並使用 to_markdown 顯示
        print("\n" + "="*60)
        print("📊 使用 DataFrame 和 Markdown 顯示")
        print("="*60)
        df = demo.get_dataframe_with_markdown()

        # 執行查詢範例
        demo.query_examples()

        # 進階查詢
        demo.advanced_queries()

        # 匯出資料
        demo.export_to_csv()

        # 關閉連接
        demo.close()

        print("\n" + "="*60)
        print("✅ 範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 程式執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
