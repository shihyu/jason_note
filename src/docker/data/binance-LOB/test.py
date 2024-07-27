from datetime import datetime
from typing import List, Optional
from infi.clickhouse_orm.models import Model
from infi.clickhouse_orm.fields import (
    ArrayField,
    DateTime64Field,
    StringField,
    UInt8Field,
    Float64Field,
    UInt64Field,
    LowCardinalityField,
)
from infi.clickhouse_orm.database import Database, DatabaseException
from infi.clickhouse_orm.engines import MergeTree, ReplacingMergeTree
from infi.clickhouse_orm.funcs import F
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
import json
from pathlib import Path
from typing import Dict, Any, List
import os
from pydantic import BaseSettings


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """
    encoding = settings.__config__.env_file_encoding
    return json.loads(Path("config.json").read_text(encoding))


class Config(BaseSettings):
    api_key: str = ""
    api_secret: str = ""
    symbols: List[str]
    full_fetch_interval: int = 60 * 60
    full_fetch_limit: int = 1000
    stream_interval: int = 100
    log_to_console: bool = True
    dispatcher_buffer_size: int = 1000
    db_name: str = "archive"
    host_name_docker: str = "clickhouse"
    host_name_default: str = "localhost"

    @property
    def host_name(self) -> str:
        if os.environ.get("AM_I_IN_DOCKER", False):
            return self.host_name_docker
        else:
            return self.host_name_default

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                json_config_settings_source,
                env_settings,
                file_secret_settings,
            )


class LoggingMsg(Model):
    timestamp = DateTime64Field(codec="Delta,ZSTD")
    msg = StringField()
    level = UInt8Field(codec="Delta, LZ4")
    payload = StringField(default="")

    engine = MergeTree("timestamp", order_by=("timestamp",))


class DepthSnapshot(Model):
    timestamp = DateTime64Field(codec="Delta,ZSTD")
    last_update_id = UInt64Field()
    bids_quantity = ArrayField(Float64Field())
    bids_price = ArrayField(Float64Field())
    asks_quantity = ArrayField(Float64Field())
    asks_price = ArrayField(Float64Field())
    symbol = LowCardinalityField(StringField())

    engine = MergeTree(
        partition_key=("symbol",),
        order_by=("timestamp", "last_update_id"),
    )


class DiffDepthStream(Model):
    timestamp = DateTime64Field(codec="Delta,ZSTD")
    first_update_id = UInt64Field(codec="Delta,ZSTD")
    final_update_id = UInt64Field(codec="Delta,ZSTD")
    bids_quantity = ArrayField(Float64Field())
    bids_price = ArrayField(Float64Field())
    asks_quantity = ArrayField(Float64Field())
    asks_price = ArrayField(Float64Field())
    symbol = LowCardinalityField(StringField())

    engine = ReplacingMergeTree(
        partition_key=(F.toMonday(timestamp), "symbol"),
        order_by=("timestamp", "first_update_id", "final_update_id"),
    )


if __name__ == "__main__":
    CONFIG = Config()

    db = Database(CONFIG.db_name, db_url=f"http://{CONFIG.host_name}:8123/")
    for model in [LoggingMsg, DepthSnapshot, DiffDepthStream]:
        db.create_table(model)
