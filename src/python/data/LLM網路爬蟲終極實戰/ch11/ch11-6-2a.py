import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

URL="https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
# 定義資料結構 Schema
schema = {
    "name": "Laptops",
    "baseSelector": "div.thumbnail",
    "fields": [
        {"name": "title", "selector": "a.title",
         "type": "text" },
        {"name": "price", "selector": "h4.price",
         "type": "text" },
        {"name": "description", "selector": "p.description",
         "type": "text" },
        {"name": "reviews", "selector": "p.review-count",
         "type": "text" }
    ]
}

async def scrape_laptops():
    # 瀏覽器配置
    browser_cfg = BrowserConfig(
        headless=False,
        verbose=True
    )    
    session_id = "webscraper_laptops"    
    # 等待商品載入
    base_wait = """js:() => {
        const selector = 'div.thumbnail';
        const products = document.querySelectorAll(selector);
        return products.length >= 1;
    }"""    
    # 步驟 1: 初始載入第一頁
    config_first_page = CrawlerRunConfig(
        wait_for=base_wait,
        session_id=session_id,
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema),
        page_timeout=60000
    )    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url=URL,
            config=config_first_page
        )        
        print(f"第 1 頁載入完成")
        print(f"資料筆數: {result.extracted_content.count('title')}")        
        # 寫入檔案
        with open('Ajax_Laptops_Page1.json', 'w', encoding='utf-8') as f:
            f.write(result.extracted_content)        
        # 步驟 2: 點擊 Next 按鈕載入更多頁面
        js_next_page = """
        const selector2 = 'div.pager > button.next';
        const nextButton = document.querySelector(selector2);
        if (nextButton) nextButton.click();
        """        
        # 等待新商品載入
        wait_for_new_products = """js:() => {
            const selector3 = 'div.thumbnail a.title';
            const products = document.querySelectorAll(selector3);
            // 記錄第一個商品標題
            if (!window.firstProductTitle && products.length > 0) {
                window.firstProductTitle = products[0].textContent.trim();
                return false;
            }
            // 檢查是否有新商品載入（第一個商品標題改變）
            if (products.length > 0) {
                const currentTitle = products[0].textContent.trim();
                const hasChanged = currentTitle &&
                      currentTitle !== window.firstProductTitle;
                if (hasChanged) {   // 更新為新的第一個商品
                    window.firstProductTitle = currentTitle; 
                }
                return hasChanged;
            }            
            return false;
        }"""        
        # 爬取接下來的 2 頁（測試用，總共 3 頁）
        for page_num in range(2, 4):
            print(f"\n正在載入第 {page_num} 頁...")
            config_next = CrawlerRunConfig(
                session_id=session_id,
                js_code=js_next_page,
                wait_for=wait_for_new_products,
                js_only=True,
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(schema),
                page_timeout=60000
            )            
            result_next = await crawler.arun(
                url=URL,
                config=config_next
            )            
            if result_next and result_next.extracted_content:
                print(f"第 {page_num} 頁載入完成")
                d_count = result_next.extracted_content.count('title')
                print(f"資料筆數: {d_count}")                
                # 寫入檔案
                with open(f'Ajax_Laptops_Page{page_num}.json',
                          'w', encoding='utf-8') as f:
                    f.write(result_next.extracted_content)
            else:
                print(f"第 {page_num} 頁載入失敗或無資料")
                break            
            # 小延遲避免請求過快
            await asyncio.sleep(2)
        
        print("\n爬取完成！已產生 3 個 JSON 檔案")

asyncio.run(scrape_laptops())