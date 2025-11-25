from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from uuid import uuid4
import ollama

# 設定中文Embedding模型
EMBEDDING_MODEL = "EntropyYue/jina-embeddings-v2-base-zh:latest"
# 建立Qdrant客戶端連接Qdrant伺服器
client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "rag_demo"   # 集合名稱
# 使用 Ollama 建立嵌入向量的函式
def get_text_embedding(text):
    try:
        response = ollama.embeddings(
            model=EMBEDDING_MODEL, 
            prompt=text
        )
        return response['embedding']
    except Exception as e:
        print(f"Embeddings向量化錯誤: {e}")
        return None
    
sample_embedding = get_text_embedding("測試文字")
if sample_embedding is None:
    print("錯誤! 無法取得向量...")
    exit()
# 取得向量的維度
VECTOR_SIZE = len(sample_embedding)
print("向量維度：", VECTOR_SIZE)
try:
    client.delete_collection(COLLECTION_NAME)
except:
    pass
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=VECTOR_SIZE,
                         distance=Distance.COSINE)
)
print("已建立集合: ", COLLECTION_NAME)
# 帶有重疊文本內容切分函式
def split_text_with_overlap(text, chunk_size=200,
                            overlap_ratio=0.2):
    if len(text) <= chunk_size:
        return [text]    
    chunks = []
    overlap_size = int(chunk_size * overlap_ratio)
    step_size = chunk_size - overlap_size    
    for i in range(0, len(text), step_size):
        end_idx = min(i + chunk_size, len(text))
        chunk = text[i:end_idx]        
        if chunk.strip():  # 只加入非空白段落
            chunks.append(chunk)        
        # 如果已經到達文本末尾，停止切分
        if end_idx >= len(text):
            break
    
    return chunks

# 將段落轉換成向量資料後寫入Qdrant集合
def insert_chunks(chunks):
    points = []
    successful_chunks = 0
    for i, chunk in enumerate(chunks):
        print(f"處理文件段落 {i+1}/{len(chunk)}...")
        vector = get_text_embedding(chunk)        
        if vector is not None:
            points.append(PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={"text": chunk}
            ))
            successful_chunks += 1
        else:
            print(f"跳過段落 {i+1}（嵌入失敗）")    
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"成功插入 {successful_chunks} 筆段落至集合")
    else:
        print("插入段落至集合失敗...")

# 建立知識庫
print("\n" + "="*50)
print("開始建立 Qdrant 知識庫")
print("="*50)
with open("愛因斯坦相對論.txt", "r", encoding="utf-8") as file:
    raw_text = file.read()
print("開始切分文本...")
chunks = split_text_with_overlap(raw_text, chunk_size=150,
                                 overlap_ratio=0.2)
print("文本內容切分結果：")
for i, chunk in enumerate(chunks):
    print(f"段落 {i+1}: {chunk[:50]}...")
print(f"\n已經將 {len(chunks)} 筆知識段落寫入向量資料庫...")
insert_chunks(chunks)
print("\nQdrant 知識庫建立完成！")