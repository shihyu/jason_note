from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = QdrantClient("localhost", port=6333)
# PointStruct 資料點串列
points = [
    PointStruct(
        id=1,
        vector=[0.1, 0.2, 0.3],
        payload={"name": "蘋果", "category": "水果", "price": 50}
    ),
    PointStruct(
        id=2,
        vector=[0.4, 0.5, 0.6],
        payload={"name": "香蕉", "category": "水果", "price": 30}
    ),
    PointStruct(
        id=3,
        vector=[0.7, 0.8, 0.9],
        payload={"name": "牛奶", "category": "飲品", "price": 60}
    )
]
# 插入資料
client.upsert(collection_name="my_collection", points=points)
print("成功插入", len(points), "個資料點!")
