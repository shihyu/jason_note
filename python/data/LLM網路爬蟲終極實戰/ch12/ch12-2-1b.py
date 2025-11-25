from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info
import json
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
graph_config = {
    "llm": {
        "model": "google_genai/gemini-2.0-flash",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "temperature": 0,
        "model_tokens": 8192,
    },
    "verbose": True, 
    "headless": True,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the news title, url, and score.",
    source="https://news.ycombinator.com/",
    config=graph_config,
)

result = smart_scraper_graph.run()
parsed_content = json.loads(result["content"])
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(parsed_content, f, indent=2, ensure_ascii=False)

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))

