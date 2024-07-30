import logging
from infi.clickhouse_orm.database import Database
from config import Config
from models import LoggingMsg, DepthSnapshot, DiffDepthStream
from datetime import datetime
import random
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def insert_diff_depth_stream(db: Database, data: dict):
    """
    Insert a DiffDepthStream record into the database.
    """
    record = DiffDepthStream(
        timestamp=data["timestamp"],
        first_update_id=data["first_update_id"],
        final_update_id=data["final_update_id"],
        bids_quantity=data["bids_quantity"],
        bids_price=data["bids_price"],
        asks_quantity=data["asks_quantity"],
        asks_price=data["asks_price"],
        symbol=data["symbol"],
    )
    db.insert([record])
    logging.info(f"Inserted record into DiffDepthStream: {record}")


def generate_random_data():
    """
    Generate random data for DiffDepthStream.
    """
    symbols = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "BNBUSD"]
    return {
        "timestamp": datetime.utcnow(),
        "first_update_id": random.randint(1, 1000),
        "final_update_id": random.randint(1001, 2000),
        "bids_quantity": [round(random.uniform(0.1, 10.0), 2) for _ in range(5)],
        "bids_price": [round(random.uniform(100.0, 1000.0), 2) for _ in range(5)],
        "asks_quantity": [round(random.uniform(0.1, 10.0), 2) for _ in range(5)],
        "asks_price": [round(random.uniform(100.0, 1000.0), 2) for _ in range(5)],
        "symbol": random.choice(symbols),
    }


if __name__ == "__main__":
    CONFIG = Config()
    db = Database(CONFIG.db_name, db_url=f"http://{CONFIG.host_name}:8123/")

    for model in [LoggingMsg, DepthSnapshot, DiffDepthStream]:
        db.create_table(model)

    # Generate and insert 10 random records
    while True:
        random_data = generate_random_data()
        insert_diff_depth_stream(db, random_data)
        time.sleep(1)
