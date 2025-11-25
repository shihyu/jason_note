import ollama
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

def get_text_embedding(text):
    name = "EntropyYue/jina-embeddings-v2-base-zh:latest"
    try:
        response = ollama.embeddings(
            model=name, 
            prompt=text
        )
        return response['embedding']
    except Exception as e:
        print(f"Embeddings向量化錯誤: {e}")
        return None
    
def search_with_filter(query_text, category=None, limit=2):
    query_embedding = get_text_embedding(query_text)    
    if query_embedding is None:
        return    
    # 設定篩選條件
    search_filter = None
    if category:
        search_filter = {
            "must": [
                {
                    "key": "category",
                    "match": {"value": category}
                }
            ]
        }    
    results = client.query_points(
        collection_name="document_collection",
        query=query_embedding,
        query_filter=search_filter,
        limit=limit
    )
    print(f"查詢: '{query_text}' (類別: {category or '全部'})")
    print("最相似的結果：")
    for i, point in enumerate(results.points, 1):
        print(f"{i}. ID: {point.id}")
        print(f"   相似度分數: {point.score:.4f}")
        print(f"   內容: {point.payload['content'][:50]}...")
        print("-" * 20)   

# 測試篩選搜尋
search_with_filter("深度學習", "人工智慧", 2)

