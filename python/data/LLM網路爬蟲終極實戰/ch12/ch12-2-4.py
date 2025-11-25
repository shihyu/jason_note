from scrapegraphai.graphs import SmartScraperGraph
import json
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
# 目標網站 URL
source = "https://news.ebc.net.tw/realtime"
# 提示詞
prompt = """
請依照下方的格式，從此新聞網站提取前5則新聞資訊，
**只回傳合法 JSON 陣列**（不包含任何自然語言描述）：
[
  {
    "title": "新聞標題",
    "date": "發布日期",
    "author": "作者名稱",
    "summary": "新聞摘要",
    "link": "文章連結"
  },
  ...
]

請勿加入解說或其他文字，只回傳 JSON 陣列。
"""

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
    prompt=prompt,
    source=source,
    config=graph_config
)

result = smart_scraper_graph.run()
news_data = result["content"]
if isinstance(news_data, list):
    parsed_content = news_data
elif isinstance(news_data, str):
    parsed_content = json.loads(news_data)
with open("EBC_news.json", "w", encoding="utf-8") as f:
    json.dump(parsed_content, f, indent=2, ensure_ascii=False)
