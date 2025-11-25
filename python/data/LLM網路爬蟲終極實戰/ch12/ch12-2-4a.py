import os
from scrapegraphai.graphs import SmartScraperGraph
import json

# 搜尋關鍵字
product_keyword = "NBA"
# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
# 目標網站 URL
source = f"https://24h.pchome.com.tw/search/?q={product_keyword}"
# 提示詞
prompt = f"""
請依照下方的格式, 從此購物網提取 "{product_keyword}" 產品資訊：
**只回傳合法 JSON 陣列**（不包含任何自然語言描述）：
{{
    "products": [
        {{
            "name": "產品名稱",
            "price": "價格數字",
            "original_price": "原價",
            "discount": "折扣資訊",
            "product_url": "產品連結",
            "image_url": "產品img圖片的src連結"
        }},
        ...
    ]
}}
注意事項：
1. 只提取前 10 個商品
2. 價格轉換為數字型態
3. 評分轉換為數字格式
4. 請確保網址完整（包含 http/https 或相對路徑）
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
products_data = result["content"]["products"]
if isinstance(products_data, list):
    parsed_content = products_data
elif isinstance(products_data, str):
    parsed_content = json.loads(products_data)
with open("PCHOME_products.json", "w", encoding="utf-8") as f:
    json.dump(parsed_content, f, indent=2, ensure_ascii=False)
