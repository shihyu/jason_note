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

def search_documents(query_text, limit=3):
    # 將查詢文本轉換為向量
    query_embedding = get_text_embedding(query_text)
    
    if query_embedding is None:
        print("查詢向量化失敗")
        return
    # 執行相似度查詢
    results = client.query_points(
        collection_name="document_collection",
        query=query_embedding,
        limit=limit
    )
    print("查詢:", query_text)
    print("最相似的結果：")
    for i, point in enumerate(results.points, 1):
        print(f"{i}. ID: {point.id}")
        print(f"   相似度分數: {point.score:.4f}")
        print(f"   內容: {point.payload['content'][:50]}...")
        print("-" * 20)    

# 測試查詢
search_documents("神經網路技術")
