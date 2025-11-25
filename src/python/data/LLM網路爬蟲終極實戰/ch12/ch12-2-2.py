from scrapegraphai.graphs import SmartScraperGraph
import json
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
graph_config = {
    "llm": {
        "model": "google_genai/gemini-2.0-flash",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "temperature": 0.1,
        "model_tokens": 8192        
    },
    "verbose": True,
    "headless": False,    
}

smart_scraper_graph = SmartScraperGraph(
    prompt="""
    請使用JSON格式從相片簿網頁提取出下列資訊：
    - 照片網址(url): img標籤的src屬性值
    - 描述文字(description)
    - 贊助金額(amount)
    - 瀏覽數(reviews)
    """,
    source="https://fchart.github.io/test/album.html",
    config=graph_config,
)

result = smart_scraper_graph.run()    
output = json.dumps(result, indent=2, ensure_ascii=False)
line_list = output.split("\n")
for line in line_list:
    print(line)