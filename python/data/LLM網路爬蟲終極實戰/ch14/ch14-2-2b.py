import requests

url = "http://localhost:8888/search"
params = {
    "q": "什麼是RAG",
    "format": "json",
    "time_range": "week",  # 限制為最近一週的結果
    "language": "zh-TW",
    "categories": "general"
}

response = requests.get(url, params=params)
data = response.json()

for result in data["results"][:5]:
    print("標題:", result["title"])
    print("URL:", result["url"])
    print("內容:", result["content"])
    print("-" * 50)
