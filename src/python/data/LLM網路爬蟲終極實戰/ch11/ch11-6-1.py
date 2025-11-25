import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BFSDeepCrawlStrategy

async def run_deep_crawl():
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2,    # 最大深度
            max_pages=10,   # 最大頁數
        )
    )
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(
            url="https://fchart.github.io/",
            config=run_conf
        )
        # 處理爬取結果
        pages_crawled = 0
        for result in results: #[:3]:
            if result.success:
                print("Raw Markdwon內容長度:",
                      len(result.markdown.raw_markdown))
                pages_crawled += 1
            else:
                print("錯誤URL:", result.url, "\n錯誤訊息:",
                      result.error_message)
        print("\n深度爬取的頁數:", pages_crawled)

asyncio.run(run_deep_crawl())