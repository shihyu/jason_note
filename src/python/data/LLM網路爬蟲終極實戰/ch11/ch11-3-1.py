import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def custom_markdown_options():
    # 建立Markdown生成器物件
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": False,          # 保留超連結
            "ignore_images": True,          # 忽略圖片
            "escape_html": True,            # 轉譯HTML
            "body_width": 0,                # 不限制寬度
            "strip_tags": ["script", "style", "nav", "footer"],  # 移除特定標籤
        }
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://fchart.github.io",
                                    config=run_config)
        print("=== 生成的Markdown ===")
        print(result.markdown[:500])

asyncio.run(custom_markdown_options())
