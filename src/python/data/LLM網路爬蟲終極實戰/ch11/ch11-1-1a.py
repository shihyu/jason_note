# 非同步程式設計
import asyncio
import aiohttp
import time

async def fetch(session, url):
    async with session.get(url) as response:
        return url, response.status

async def async_crawl():
    urls = ["https://fchart.github.io", "http://fchart.is-best.net",
            "https://httpbin.org"]
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for url, status in results:
            print(f"爬取 {url}: {status}")
    
    print(f"總耗時: {time.time() - start_time:.2f}秒")

asyncio.run(async_crawl())
