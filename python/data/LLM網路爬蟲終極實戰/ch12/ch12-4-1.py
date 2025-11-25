from scrapegraphai.graphs import ScriptCreatorGraph
import json
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
graph_config = {
    "llm": {
        "model": "google_genai/gemini-2.0-flash",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "temperature": 0,
        "max_tokens": 8192, 
    },
    "library": "beautifulsoup",  # 指定使用 BeautifulSoup4
    "verbose": True,
    "headless": True,
}

script_creator_graph = ScriptCreatorGraph(
    prompt="""
    Create a Python script using BeautifulSoup4 to
    scrape Hacker News homepage and extract all news titles,
    URLs, and scores. The script should return the data
    in JSON format and save it to a file called 'news2.json'.
    """,
    source="https://news.ycombinator.com/",
    config=graph_config,
)

result = script_creator_graph.run()
generated_script = str(result)
print("產生的 Python 腳本:")
print("=" * 50)
print(generated_script)
filename = "hacker_news_scraper.py"
try:
    lines = generated_script.split('\n')
    if (lines[0].strip().startswith('```') and
        lines[-1].strip() == '```'):
        content_to_save = '\n'.join(lines[1:-1])
    else:
        content_to_save = generated_script
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content_to_save)
    print(f"\nPython 腳本已經儲存至: '{filename}'")
except Exception as e:
    print(f"儲存檔案時發生錯誤：{e}")

