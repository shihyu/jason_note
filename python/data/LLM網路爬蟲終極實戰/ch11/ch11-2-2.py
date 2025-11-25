import asyncio
from crawl4ai import AsyncWebCrawler

async def first_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://fchart.github.io")
        if result.status_code == 200:
            print("標題:", result.metadata.get("title", "N/A"))
            print("前300字:", result.markdown[:300])
        else:
            print("請求失敗，狀態碼：", result.status_code)

asyncio.run(first_crawl())

