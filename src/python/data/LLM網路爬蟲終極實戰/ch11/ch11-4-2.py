import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai import JsonXPathExtractionStrategy

# 測試的 HTML 字串
html_str = """
<html><body>
<div>
    <article>
        <h2>Python非同步程式設計</h2>
        <div class="summary">學習Python的async/await語法</div>
        <a href="/python-async">閱讀更多</a>
    </article>
    <article>
        <h2>網路爬蟲最佳實戰</h2>
        <div class="summary">如何用Crawl4AI建立高效網路爬蟲</div>
        <a href="/web-crawling">閱讀更多</a>
    </article>
</div></body></html>
"""

async def xpath_extraction():
    # 定義 XPath 擷取結構
    schema = {
        "name": "文章清單",
        "baseSelector": "//article",  # 改用 XPath
        "type": "list",
        "fields": [
            {"name": "title", "selector": ".//h2", "type": "text"},
            {"name": "link", "selector": ".//a", "type": "attribute", "attribute": "href"},
            {"name": "summary", "selector": ".//*[@class='summary']", "type": "text"}
        ]
    }    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonXPathExtractionStrategy(schema)  # 使用 XPath 策略
    )    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="raw://" + html_str,
            config=run_config
        )
        
        if result.extracted_content:
            articles = json.loads(result.extracted_content)
            print("擷取出的項目:")
            for article in articles:
                print("  標題:", article["title"])
                print("  摘要:", article["summary"])
                print("  連結:", article["link"])
                print()

asyncio.run(xpath_extraction())