import os
import json
from scrapegraphai.graphs import SmartScraperGraph
from typing import List
from pydantic import BaseModel, Field

class Project(BaseModel):
    title: str = Field(..., description="工具名稱")
    description: str = Field(..., description="工具描述")

class Projects(BaseModel):
    projects: List[Project]
    
graph_config = {
    "llm": {
        "model": "ollama/llama3.1:8b",
        "model_tokens": 8192,
        "format": "json"
    },
    "embeddings": {
        "model": "ollama/EntropyYue/jina-embeddings-v2-base-zh:latest",
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