import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def custom_markdown_options():
    # 建立Markdown生成器物件
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": False,
            "ignore_images": False,         # 保留圖片
            "ignore_tables": False,         # 保留表格
            "escape_html": True,
            "body_width": 80,               # 限制寬度是80字元
            "strip_tags": ["script", "style", "nav", "footer"],            
            "include_meta": True,           # 包含meta資料
            "preserve_formatting": True,    # 保留格式
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
