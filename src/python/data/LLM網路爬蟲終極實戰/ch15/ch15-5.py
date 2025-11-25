import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

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
# 取得向量維度
sample_embedding = get_text_embedding("測試文字")
if sample_embedding is None:
    print("錯誤! 無法取得向量...")
    exit()
# 取得向量尺寸
vector_size = len(sample_embedding)
print("向量尺寸：", vector_size)
client = QdrantClient("localhost", port=6333)
collection_name = "n8n_collection"
# 建立新集合（如果存就先刪除集合）
try:
    client.delete_collection(collection_name)
except:
    pass
# 建立集合
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size,
                         distance=Distance.COSINE)
)
print("已經成功建立集合：", collection_name)
