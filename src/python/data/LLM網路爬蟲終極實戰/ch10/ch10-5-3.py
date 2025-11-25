import ollama

prompt = """請問網路爬蟲是什麼？
為什麼我們需要網路爬蟲？
請使用200個字來表達Python如何建立網路爬蟲。"""

response = ollama.chat(
    model = "llama3.1:8b",
    messages = [
         {"role": "system", "content": "你是Python程式專家"},
         {"role": "user", "content": prompt}
    ])
print("Q:", prompt)
print(response['message']['content'])
