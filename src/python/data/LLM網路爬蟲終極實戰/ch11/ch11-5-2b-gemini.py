import asyncio
import json
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai import LLMExtractionStrategy
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
llm_config = LLMConfig(
    provider="gemini/gemini-2.0-flash",  # 改用 2.0-flash,較穩定
    api_token=os.getenv("GOOGLE_API_KEY"),
)
class ArticleData(BaseModel):
    headline: str
    summary: str

async def extraction_strategy():
    llm_strategy = LLMExtractionStrategy(
        llm_config = llm_config,
        schema=ArticleData.model_json_schema(),
        extraction_type="schema",
        instruction="Extract 'headline' and a short 'summary' from the content."
    )
    run_config = CrawlerRunConfig(
        exclude_external_links=True,
        word_count_threshold=20,
        extraction_strategy=llm_strategy
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://news.ycombinator.com",
                                    config=run_config)
        article = json.loads(result.extracted_content)
        print(article)

asyncio.run(extraction_strategy())
