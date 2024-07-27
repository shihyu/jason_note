from infi.clickhouse_orm.database import Database
from config import Config


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
    read_diff_depth_stream(db)
