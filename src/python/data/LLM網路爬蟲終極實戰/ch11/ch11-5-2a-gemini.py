import asyncio
from pydantic import BaseModel, Field
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
# 定義Schema結構
class Article(BaseModel):
    title: str = Field(description="文章標題")
    author: str = Field(description="作者名稱")
    publish_date: str = Field(description="發布日期")
    content: str = Field(description="文章內容")
    tags: List[str] = Field(description="標籤串列")
    url: Optional[str] = Field(description="文章網址")

class NewsData(BaseModel):
    articles: List[Article] = Field(description="新聞文章串列")
    total_count: int = Field(description="總文章數")
    
async def extract_news():
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=NewsData.model_json_schema(),
        extraction_type="schema",
        instruction="""
        請提取頁面中的所有新聞文章信息，
        包括:標題、作者、發布日期、內容和標籤。
        請回傳正確的 JSON 格式資料，
        並且確保包含 articles 陣列和 total_count 欄位。
        """,
        chunk_token_threshold=2000,
        overlap_rate=0.1,
        apply_chunking=True,
        input_format="markdown",
        extra_args={
            "temperature": 0.2, 
            "max_tokens": 4000,
            "top_p": 0.95,
            "response_format": {"type": "json_object"} 
        }
    )
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )
    browser_config = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://news.ebc.net.tw/realtime",
            config=run_config
        )        
        if result.success:
            extracted_data = result.extracted_content
            print("提取資料:", extracted_data)
        else:
            print("提取失敗:", result.error_message)

asyncio.run(extract_news())