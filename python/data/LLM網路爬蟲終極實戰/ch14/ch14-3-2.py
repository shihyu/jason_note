import requests
import json
from scrapegraphai.graphs import SmartScraperGraph
import os

# Step 1：輸入關鍵字使用SearXNG進行搜尋。
searxng_url = "http://localhost:8888/search"
query = "台灣生成式AI在醫療上的應用"
params = {
    "q": query,
    "format": "json",
}
response = requests.get(searxng_url, params=params)
results = response.json()
# Step 2：取得搜尋結果的URL清單(過濾網址且只取出前3筆)。
exclude_names = ["facebook.com", "taiwan-city.com"]
urls = []
max_count = 3
for result in results.get("results", []):
    url = result.get("url")
    if not any(name in url for name in exclude_names):
        if len(urls) < max_count:
            urls.append(url)            
        else:
            break
# Step 3：逐一將URL送入ScrapeGraphAI來爬取資料。
# 設定 OpenAI API 金鑰
os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"
graph_config = {
    "llm": {
        "model": "openai/gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": 0.1,
    },
    "verbose": False,
    "headless": True,
}
scraped_data = []
for url in urls:
    print("正在處理網址:", url)
    smart_scraper_graph = SmartScraperGraph(
        prompt= """
        請擷取網頁中的標題與段落內容，
        並且使用 JSON 結構化格式來呈現。
        """,
        source=url,
        config=graph_config
    )
    result = smart_scraper_graph.run()
    # 將結果加入串列
    scraped_data.append({
        "url": url,
        "content": result['content']
    })
# Step 4：儲存爬取結果的資料，儲存成 JSON 檔案。
with open("results2.json", "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, ensure_ascii=False,
              indent=2)
print("已經成功儲存爬取結果至 results2.json")