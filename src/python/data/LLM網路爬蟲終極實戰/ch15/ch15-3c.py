from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
# 定義欲查詢的向量
search_vector = [0.2, 0.3, 0.4]
# 執行相似度查詢
search_result = client.query_points(
    collection_name="my_collection",
    query=search_vector,
    limit=2
)
print("查詢向量:", search_vector)
print("最相似的結果：")
for i, point in enumerate(search_result.points, 1):
    print(f"{i}. ID: {point.id}")
    print(f"   相似度分數: {point.score:.4f}")
    print(f"   名稱: {point.payload['name']}")
    print(f"   分類: {point.payload['category']}")
    print("-" * 20)

