import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig
from crawl4ai import CrawlerRunConfig, CacheMode

# 建立瀏覽器配置
browser_config = BrowserConfig(
    headless=True,
    java_script_enabled=True
)
# 建立執行配置
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    page_timeout=30000,
    word_count_threshold=10,
    stream=False
)
async def configured_crawl():
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://fchart.github.io",
            config=run_config
        )    
        if result.success:
            print("爬取成功，內容長度:", len(result.markdown))
        else:
            print("爬取失敗:", result.error_message)

asyncio.run(configured_crawl())

