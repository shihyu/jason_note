import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def ecommerce_crawler():
    browser_config = BrowserConfig(
        headless=False,
        java_script_enabled=True
    )
    js_code = """
         for(let i=0;i<3;i++) {
             window.scrollTo(0,document.body.scrollHeight);
             await new Promise(r=>setTimeout(r,1000));
         }"""
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        css_selector="div.row",
        js_code=js_code
    )    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        url = "https://webscraper.io/test-sites/e-commerce/scroll/computers/laptops"
        result = await crawler.arun(url, config=run_config)
        if result.success:
            print("爬取成功，內容長度:", len(result.html))            

asyncio.run(ecommerce_crawler())
