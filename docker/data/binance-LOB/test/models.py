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
from infi.clickhouse_orm.engines import MergeTree, ReplacingMergeTree
from infi.clickhouse_orm.funcs import F


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
