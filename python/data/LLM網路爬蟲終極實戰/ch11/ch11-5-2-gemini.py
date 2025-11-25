import asyncio
from typing import List, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
llm_config = LLMConfig(
    provider="gemini/gemini-2.0-flash",  # 改用 2.0-flash,較穩定
    api_token=os.getenv("GOOGLE_API_KEY"),
)
# 定義 JSON Schema
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

async def extract_products():
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=schema,
        extraction_type="schema",
        instruction="""請提取頁面中所有的商品資訊，
         包括: 名稱、定價、描述和是否可訂購""",
        chunk_token_threshold=1000,
        overlap_rate=0.1,
        apply_chunking=True,
        input_format="markdown",
        extra_args={"temperature": 0.1,
                    "max_tokens": 1500}
    )    
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )
    browser_config = BrowserConfig(headless=True)    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://24h.pchome.com.tw/search/?q=iphone%2015",
            config=run_config
        )        
        if result.success:
            extracted_data = result.extracted_content
            print("提取資料:", extracted_data)
        else:
            print("提取失敗:", result.error_message)

asyncio.run(extract_products())

