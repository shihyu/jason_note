# Step 1: 從 JSON 檔案載入文件資料
import json

with open('documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

if documents:
    print("Step 1: 文件資料載入完成：")
    for doc in documents:
        print(f"文件 {doc['id']}: {doc['title']}")
else:
    print("沒有載入任何文件資料")
# Step 2: 建立Embedding函式來取得向量尺寸    
import ollama

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
print("Step 2: 取得向量尺寸：", vector_size)
# Step 3: 建立 Qdrant 集合
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient("localhost", port=6333)
collection_name = "document_collection"
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
print("Step 3: 已經成功建立集合：", collection_name)
# Step 4: 將文件轉換為向量並且儲存到向量資料庫
from qdrant_client.models import PointStruct

points = []
print("Step 4: 開始儲存文件向量...")
for doc in documents:
    # 取得結合標題和內容的文本
    full_text = f"{doc['title']} {doc['content']}"
    # 取得向量
    embedding = get_text_embedding(full_text)
    
    if embedding:
        point = PointStruct(
            id=doc['id'],
            vector=embedding,
            payload={
                "title": doc['title'],
                "content": doc['content'],
                "category": doc['category']
            }
        )
        points.append(point)
        print(f"文件 {doc['id']} 向量化完成")

# 批量插入文件向量
if points:
    client.upsert(collection_name="document_collection",
                  points=points)
    print(f"Step 4: 已經成功儲存 {len(points)} 個文件向量")
