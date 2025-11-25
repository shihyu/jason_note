from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
# 使用 ID 查詢資料
result = client.retrieve(
    collection_name="my_collection",
    ids=[1, 2]
)
print("ID查詢結果：")
for point in result:
    print("ID:", point.id)
    print("向量:", point.vector)
    print("Metadata資料:", point.payload)
    print("-" * 20)

# 取得集合中的前 10 筆資料點
all_points, _ = client.scroll(
    collection_name="my_collection",
    limit=10
)
print("集合中共有", len(all_points), "個資料點!")

