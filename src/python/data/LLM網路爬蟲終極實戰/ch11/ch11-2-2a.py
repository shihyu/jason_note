import asyncio
from crawl4ai import AsyncWebCrawler

async def multi_crawl():
    urls = [
        "https://example.com",
        "https://www.python.org",
        "https://www.wikipedia.org"
    ]
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(urls)

        for result in results:
            print(f"\n網址: {result.url}")
            print(f"狀態碼: {result.status_code}")
            print(f"標題: {result.metadata.get('title', 'N/A')}")
            print(f"內容前300字:\n{result.markdown[:300]}")
            
asyncio.run(multi_crawl())


