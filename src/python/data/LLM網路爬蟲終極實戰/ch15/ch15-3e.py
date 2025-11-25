from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = QdrantClient("localhost", port=6333)
# 刪除資料 - 刪除ID值3的資料
client.delete(
    collection_name="my_collection",
    points_selector=[3]
)
print("資料刪除成功!")
# 剩餘資料數
remaining_points, _ = client.scroll(
              collection_name="my_collection")
print("剩餘資料數量:", len(remaining_points))



