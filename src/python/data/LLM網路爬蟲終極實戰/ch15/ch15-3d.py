from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = QdrantClient("localhost", port=6333)
# 更新資料 - 修改ID值1的資料
updated_point = PointStruct(
    id=1,
    vector=[0.15, 0.25, 0.35],
    payload={"name": "紅蘋果", "category": "水果", "price": 55}
)

client.upsert(
    collection_name="my_collection",
    points=[updated_point]
)
print("資料更新成功!")
