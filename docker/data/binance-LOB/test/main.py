import logging
from infi.clickhouse_orm.database import Database
from infi.clickhouse_orm.models import Model
from config import Config
from models import LoggingMsg, DepthSnapshot, DiffDepthStream
from datetime import datetime

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


def read_diff_depth_stream(db: Database):
    """
    Read and print all records from DiffDepthStream table.
    """
    query = "SELECT * FROM diffdepthstream"
    records = db.select(query)
    for record in records:
        print(f"Timestamp: {record.timestamp}")
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
    for model in [LoggingMsg, DepthSnapshot, DiffDepthStream]:
        db.create_table(model)

    # Sample data to insert
    sample_data = {
        "timestamp": datetime.utcnow(),
        "first_update_id": 1,
        "final_update_id": 2,
        "bids_quantity": [1.0, 2.0],
        "bids_price": [100.0, 101.0],
        "asks_quantity": [1.5, 2.5],
        "asks_price": [102.0, 103.0],
        "symbol": "BTCUSD",
    }

    # Insert sample data
    # insert_diff_depth_stream(db, sample_data)

    # Read and print data
    read_diff_depth_stream(db)
