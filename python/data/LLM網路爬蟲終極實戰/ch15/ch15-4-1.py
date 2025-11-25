import ollama

def get_text_embedding(text):
    try:
        response = ollama.embeddings(
            model="EntropyYue/jina-embeddings-v2-base-zh:latest", 
            prompt=text
        )
        return response['embedding']
    except Exception as e:
        print(f"Embeddings向量化錯誤: {e}")
        return None

# 測試向量化功能
test_text = "這是一個測試文本"
embedding = get_text_embedding(test_text)

if embedding:
    print(f"文本: {test_text}")
    print(f"向量維度: {len(embedding)}")
    print(f"向量前5個數值: {embedding[:5]}")
else:
    print("請確認Ollama服務執行中...")
    