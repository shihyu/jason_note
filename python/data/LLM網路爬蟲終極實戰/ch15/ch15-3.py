from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient("localhost", port=6333)
print("已經成功連接到 Qdrant")

collection_name = "my_collection"
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=3, distance=Distance.COSINE)
)
print("集合:", collection_name, "已經成功建立!")

# 顯示目前 Qdrant 的集合清單
collections = client.get_collections()
print("現有集合：")
for collection in collections.collections:
    print("-", collection.name)
