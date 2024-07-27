from datetime import datetime, timedelta
from infi.clickhouse_orm.database import Database
from config import Config
import pytz


def read_diff_depth_stream(db: Database, start_time: datetime, end_time: datetime):
    """
    在指定的時間範圍內讀取並打印 DiffDepthStream 表中的記錄。

    :param db: 資料庫物件
    :param start_time: 時間範圍的開始（包含）（本地時間）
    :param end_time: 時間範圍的結束（包含）（本地時間）
    """
    # 將本地時間轉換為 UTC
    utc = pytz.UTC
    start_time_utc = start_time.astimezone(utc)
    end_time_utc = end_time.astimezone(utc)

    query = f"""
    SELECT *
    FROM diffdepthstream
    WHERE timestamp >= toDateTime('{start_time_utc.strftime('%Y-%m-%d %H:%M:%S')}')
      AND timestamp <= toDateTime('{end_time_utc.strftime('%Y-%m-%d %H:%M:%S')}')
    ORDER BY timestamp, first_update_id, final_update_id
    """
    records = db.select(query)
    for record in records:
        # 将 UTC 时间转换回本地时间
        local_time = record.timestamp.replace(tzinfo=utc).astimezone(
            pytz.timezone("Asia/Taipei")
        )
        print(f"Timestamp: {local_time}")
        print(f"First Update ID: {record.first_update_id}")
        print(f"Final Update ID: {record.final_update_id}")
        print(f"Bids Quantity: {record.bids_quantity}")
        print(f"Bids Price: {record.bids_price}")
        print(f"Asks Quantity: {record.asks_quantity}")
        print(f"Asks Price: {record.asks_price}")
        print(f"Symbol: {record.symbol}")
        print("------")


if __name__ == "__main__":
    CONFIG = Config()
    db = Database(CONFIG.db_name, db_url=f"http://{CONFIG.host_name}:8123/")

    # 範例：讀取最近一小時的記錄（使用本地時間）
    local_tz = pytz.timezone("Asia/Taipei")  # 使用台北時區作為示例
    end_time = datetime.now(local_tz)
    start_time = end_time - timedelta(minutes=5)

    read_diff_depth_stream(db, start_time, end_time)
