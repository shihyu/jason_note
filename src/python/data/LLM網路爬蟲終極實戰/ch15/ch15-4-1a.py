from openai import OpenAI

api_key = "<API-KEY>"

def get_text_embedding(text):
    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"OpenAI向量化錯誤: {e}")
        return None

# 測試OpenAI向量化
test_text = "人工智慧的應用"
openai_embedding = get_text_embedding(test_text)

if openai_embedding:
    print(f"文本: {test_text}")
    print(f"向量維度: {len(openai_embedding)}")
    print(f"向量前5個數值: {openai_embedding[:5]}")
else:    
    print("請確認API KEY是正確的...")

    