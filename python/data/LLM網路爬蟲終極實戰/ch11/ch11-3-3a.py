import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def content_selection():
    run_config = CrawlerRunConfig(
        target_elements=["p.lead", "div.card"]
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://fchart.github.io/test/album.html", 
            config=run_config
        )
        print("部分HTML網頁內容長度:", len(result.cleaned_html))
        print("Raw Markdwon內容長度:", len(result.markdown.raw_markdown))
        print(result.markdown.raw_markdown)

asyncio.run(content_selection())
