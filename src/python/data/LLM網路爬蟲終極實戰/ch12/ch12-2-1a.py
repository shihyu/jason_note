from scrapegraphai.graphs import SmartScraperGraph
import json

graph_config = {
    "llm": {
        "model": "ollama/llama3.1:8b",
        "model_tokens": 8192,
        "format": "json"
    },
    "embeddings": {
        "model": "ollama/shaw/dmeta-embedding-zh:lastest",
    },
    "verbose": True,
    "headless": False,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="""
    請使用JSON格式從此頁面找出有用的資訊,
    一一列出ScrapeGraphAI支援的Models清單,
    鍵名是models
    """,
    source="https://scrapegraph-ai.readthedocs.io/en/latest/",
    config=graph_config
)

result = smart_scraper_graph.run()
output = json.dumps(result, indent=2, ensure_ascii=False)
line_list = output.split("\n")
for line in line_list:
    print(line)