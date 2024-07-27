import logging
from infi.clickhouse_orm.database import Database
from config import Config
from models import LoggingMsg, DepthSnapshot, DiffDepthStream

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

if __name__ == "__main__":
    CONFIG = Config()

    db = Database(CONFIG.db_name, db_url=f"http://{CONFIG.host_name}:8123/")
    for model in [LoggingMsg, DepthSnapshot, DiffDepthStream]:
        db.create_table(model)
