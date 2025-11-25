import os
import json
from scrapegraphai.graphs import ScriptCreatorMultiGraph

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
graph_config = {
    "llm": {
        "model": "google_genai/gemini-2.0-flash",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "temperature": 0,
        "model_tokens": 4096,
    },
    "library": "beautifulsoup",  # 指定使用 BeautifulSoup4
    "verbose": True, 
    "headless": True,
}

script_creator_graph = ScriptCreatorMultiGraph(
    prompt="""
    請為多個 Hacker News 頁面建立一個 Python 爬蟲腳本，需要：
    
    1. 爬取每個指定頁面的新聞內容
    2. 提取以下資訊：
       - 新聞標題（移除所有換行符號，用空格替代）
       - 新聞網址
       - 新聞分數（如果有的話，沒有則設為 null）
    
    3. 輸出要求：
       - 輸出有效的 JSON 格式
       - 正確跳脫所有特殊字符
       - 將結果保存到 'Hacker_news2.json' 檔案
    
    4. 腳本需要處理多個頁面的數據合併
    5. 包含適當的錯誤處理和日誌記錄
    
    請產生一個完整且可執行的 Python 腳本。
    """,
    source=[
        "https://news.ycombinator.com/",
        "https://news.ycombinator.com/?p=2", 
        "https://news.ycombinator.com/?p=3",
    ],
    config=graph_config,
)

result = script_creator_graph.run()
generated_script = str(result)
print("產生的 Python 腳本:")
print("=" * 50)
print(generated_script)
filename = "hacker_news_multi_scraper.py"
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

