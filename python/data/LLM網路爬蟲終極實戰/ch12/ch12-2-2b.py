from scrapegraphai.graphs import SmartScraperGraph
import json
import os
from pydantic import BaseModel
from typing import List, Optional

# 設定 OpenAI API 金鑰
os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"
# 定義資料結構 Schema
class PhotoInfo(BaseModel):
    url: str  # 照片網址
    description: str  # 描述文字
    amount: Optional[str] = None  # 贊助金額
    reviews: Optional[str] = None  # 瀏覽數

class PhotoAlbum(BaseModel):
    photos: List[PhotoInfo]

graph_config = {
    "llm": {
        "model": "openai/gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": 0.1
    },
    "verbose": True,
    "headless": False,    
}

smart_scraper_graph = SmartScraperGraph(
    prompt="""
    請從相片簿網頁中提取所有照片的資訊。
    仔細尋找所有的 img 標籤，並提取以下資訊：
    - url: 圖片的完整 src 屬性值（包含 http/https 或相對路徑）
    - description: 圖片的 alt 屬性或相關的文字描述
    - amount: 任何相關的贊助金額資訊（如果有的話）
    - reviews: 任何相關的瀏覽數或評論數（如果有的話）
    
    請確保提取所有找到的圖片，不要遺漏任何一張。
    """,
    source="https://fchart.github.io/test/album.html",
    schema=PhotoAlbum,  # 使用 Schema 定義輸出格式
    config=graph_config,
)

try:
    result = smart_scraper_graph.run()    
    if isinstance(result, dict) and 'photos' in result:
        print("=== 相片簿爬取結果 ===")
        print(f"總共找到 {len(result['photos'])} 張照片\n")
        for i, photo in enumerate(result['photos'], 1):
            print(f"照片 {i}:")
            print(f"  URL: {photo.get('url', 'N/A')}")
            print(f"  描述: {photo.get('description', 'N/A')}")
            print(f"  贊助金額: {photo.get('amount', 'N/A')}")
            print(f"  瀏覽數: {photo.get('reviews', 'N/A')}")
            print("-" * 50)
    
    print("\n=== 完整 JSON 輸出 ===")
    output = json.dumps(result, indent=2, ensure_ascii=False)
    print(output)    
except Exception as e:
    print(f"爬取過程中發生錯誤: {e}")
    print("請檢查網址是否正確，以及網路連線是否正常。")