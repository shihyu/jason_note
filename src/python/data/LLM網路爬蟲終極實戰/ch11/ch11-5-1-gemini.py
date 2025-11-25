import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.content_filter_strategy import LLMContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import os

# 設定 Gemini API 金鑰
os.environ["GOOGLE_API_KEY"] = "<GEMINI_API_KEY>"
llm_config = LLMConfig(
    provider="gemini/gemini-2.0-flash",  # 改用 2.0-flash,較穩定
    api_token=os.getenv("GOOGLE_API_KEY"),
)
async def run_python_content_crawl():
    # 使用 LLMContentFilter 過濾出 Python 相關內容
    llm_content_filter = LLMContentFilter(
        llm_config=llm_config,
        instruction="請擷取出Python相關的內容",
        verbose=True,
        chunk_token_threshold=500
    )    
    markdown_generator_with_llm_filter = DefaultMarkdownGenerator(
        content_filter=llm_content_filter
    )    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=markdown_generator_with_llm_filter
    )    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://fchart.github.io",
                                    config=run_config)
        
        if result.success:
            print("原始 Markdown 內容長度:",
                  len(result.markdown.raw_markdown))
            print("篩選後 Markdown 內容長度:",
                  len(result.markdown.fit_markdown))
            print("\n篩選後的 Python 相關內容:")
            print("================================")
            print(result.markdown.fit_markdown)
        else:
            print("爬取失敗:", result.error_message)

asyncio.run(run_python_content_crawl())