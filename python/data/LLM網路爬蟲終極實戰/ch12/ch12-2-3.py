import os
import json
from scrapegraphai.graphs import SmartScraperMultiGraph
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"

class NewsItem(BaseModel):
    title: str = Field(..., description="新聞標題",
                       min_length=1)
    url: HttpUrl = Field(..., description="新聞網址")
    score: Optional[int] = Field(None,
                           description="新聞分數", ge=0)

class NewsCollection(BaseModel):
    news_items: List[NewsItem] = Field(...,
                     description="新聞項目列表")

graph_config = {
    "llm": {
        "model": "google_genai/gemini-2.0-flash",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "temperature": 0,
        "model_tokens": 4096,
    },
    "verbose": True, 
    "headless": True,
}

multiple_scraper_graph = SmartScraperMultiGraph(
    prompt="""
    請提取所有新聞的標題、網址和分數。
    重要要求：
    1. 標題中的所有換行符號都必須移除，用空格替代
    2. 確保輸出的是有效的 JSON 格式
    3. 所有特殊字符都必須正確跳脫
    4. 如果沒有分數，請設定為 null
    
    請以 NewsCollection 的格式回傳資料""",
    source=[
        "https://news.ycombinator.com/",
        "https://news.ycombinator.com/?p=2",
        "https://news.ycombinator.com/?p=3",
    ],
    schema=NewsCollection,  # 使用 Schema 定義輸出格式
    config=graph_config,
)

result = multiple_scraper_graph.run()
news_data = result["news_items"]
if isinstance(news_data, list):
    parsed_content = news_data
elif isinstance(news_data, str):
    parsed_content = json.loads(news_data)

with open("Hacker_news.json", "w", encoding="utf-8") as f:
    json.dump(parsed_content, f, indent=2, ensure_ascii=False)
