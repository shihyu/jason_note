import requests
import json
from qdrant_client import QdrantClient

# 設定Ollama API端點, LLM和中文Embedding模型
OLLAMA_BASE_URL = "http://localhost:11434"
CHAT_MODEL = "llama3.1:8b"
EMBEDDING_MODEL = "EntropyYue/jina-embeddings-v2-base-zh:latest"
# 建立Qdrant客戶端連接Qdrant伺服器
client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "rag_demo"   # 集合名稱
# 使用 Ollama 建立嵌入向量的函式
def get_text_embedding(text):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            }
        )
        if response.status_code == 200:
            embedding = response.json()["embedding"]
            return embedding
        else:
            print("無法獲取向量...")
            return None
    except Exception as e:
        print(f"Embeddings向量化錯誤: {e}")
        return None
# 函數是用輸入問題query來並查詢Qdrant向量資料庫
def search_similar_docs(query, top_k=3):
    print("搜尋查詢：", query)
    query_embedding = get_text_embedding(query)    
    if query_embedding is None:
        print("查詢嵌入失敗...")
        return []    
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    )
    similar_docs = [hit.payload["text"] for hit in results.points]
    print(f"找到 {len(similar_docs)} 個相關段落")
    return similar_docs
# 使用Ollama LLM來生成回答
def generate_answer_with_ollama(query):
    docs = search_similar_docs(query)
    if not docs:
        return "抱歉，我無法在知識庫中找到相關資訊。"
    context = "\n".join(docs)
    prompt = f"""
根據以下資料來回答問題，請使用繁體中文回答問題：
參考資料：
{context}
問題：{query}
請根據上述資料提供準確的答案：
"""    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": CHAT_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"生成回答時發生錯誤：{response.status_code}"    
    except Exception as e:
        return f"連接 Ollama 時發生錯誤：{e}"

# 測試 RAG 查詢
print("\n" + "="*50)
print("開始測試 RAG 系統")
print("="*50)
test_queries = [
    "誰提出了狹義相對論？",
    "廣義相對論何時提出的？",
    "什麼是質能等價公式？",
    "相對論包含哪些部分？"
]
for query in test_queries:
    print("\n問題：", query)
    answer = generate_answer_with_ollama(query)
    print("回答：", answer)
    print("-" * 40)
print("\nRAG 系統測試完成！")
 