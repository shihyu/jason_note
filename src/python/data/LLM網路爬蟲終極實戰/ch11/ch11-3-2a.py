import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def run_custom_markdown_crawl():
    # 建立 BM25 內容篩選器的 Markdown 生成器
    markdown_generator_with_filter = DefaultMarkdownGenerator(
        content_filter=BM25ContentFilter(
            user_query="python tutorial",  # 設定查詢關鍵字
            bm25_threshold=1.0  # BM25 相關性閾值
        )
    )    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS, 
        markdown_generator=markdown_generator_with_filter
    )    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://fchart.github.io",
            config=run_config
        )        
        if result.success:
            print("Raw Markdown 內容長度:", len(result.markdown.raw_markdown))
            print("Fit Markdown 內容長度:", len(result.markdown.fit_markdown))
            print(result.markdown.fit_markdown)
        else:
            print("爬取失敗:", result.error_message)

asyncio.run(run_custom_markdown_crawl())