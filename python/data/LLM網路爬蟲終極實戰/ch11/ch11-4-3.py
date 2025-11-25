import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def extraction_strategy():
    schema = {
        "name": "News Items",
        "baseSelector": "div.card",
        "fields": [
           {"name": "image_url", "selector": ".card-img-top",
            "type": "attribute", "attribute": "src" },
           {"name": "description", "selector": ".card-text", "type": "text"},
           {"name": "sponsor_amount", "selector": ".pull-right.price", "type": "text"},
           {"name": "reviews_count", "selector": ".text-muted", "type": "text"}
        ]
    }

    run_config = CrawlerRunConfig(
        excluded_tags=["header", "footer"],
        css_selector="div.row",
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://fchart.github.io/test/album.html", 
            config=run_config
        )
        items = json.loads(result.extracted_content)
        print("擷取出的項目:")
        for item in items:
            print("  圖片:", item["image_url"])
            print("  描述:", item["description"])
            print("  贊助:", item["sponsor_amount"])
            print("  評論數:", item["reviews_count"])
            print()

asyncio.run(extraction_strategy())

