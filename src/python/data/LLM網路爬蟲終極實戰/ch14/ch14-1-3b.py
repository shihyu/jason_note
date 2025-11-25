import requests
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
llm_config = {
    "type": "LLMConfig",
    "params": {
        "provider": "gemini/gemini-2.0-flash", 
        "api_token": os.getenv("GOOGLE_API_KEY"),
    }
}
schema = {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "description": {"type": "string"},
                        "availability": {"type": "boolean"}
                    },
                    "required": ["name", "price"]
                }
            }
        }
    }
llm_strategy = {
    "type": "LLMExtractionStrategy",
    "params": {
        "llm_config": llm_config,
        "schema": schema,
        "extraction_type": "schema",
        "instruction" : """請提取頁面中所有的商品資訊，
         包括: 名稱、定價、描述和是否可訂購""",
        "chunk_token_threshold": 1000,
        "overlap_rate": 0.1,
        "apply_chunking": True,
        "input_format": "markdown",
        "extra_args": {"temperature": 0.1,
                       "max_tokens": 1500}
   }
}
crawler_config = {
    "type": "CrawlerRunConfig",
    "params": {
               "stream": False,
               "cache_mode": "bypass",
               "extraction_strategy": llm_strategy
              } 
}
browser_config = {
    "type": "BrowserConfig",
    "params": {
            "headless": True,
            "viewport": {"width": 1920, "height": 1080}, 
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
}
payload = {
    "urls": ["https://24h.pchome.com.tw/search/?q=iphone%2015"],
    "browser_config": browser_config,
    "crawler_config": crawler_config
}
response = requests.post(
    "http://localhost:11235/crawl", 
    json=payload
)
print(f"狀態碼: {response.status_code}")
if response.ok:
    #print(response.json())
    print(response.json()["results"][0]
          ["extracted_content"])
else:
    print(f"錯誤: {response.text}")