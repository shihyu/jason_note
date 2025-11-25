import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def run_custom_markdown_crawl():
    markdown_generator_with_filter = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.48,
            threshold_type="fixed" # 'fixed' 或 'relative'
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
            print("Raw Markdwon內容長度:", len(result.markdown.raw_markdown))
            print("Fit Markdwon內容長度:", len(result.markdown.fit_markdown))
        else:
            print("爬取失敗:", result.error_message)

asyncio.run(run_custom_markdown_crawl())