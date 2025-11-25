# 1. items.py - 定義資料結構
import scrapy

class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

# 2. spiders/quotes.py - 主要爬蟲程式
import scrapy
from quotes_scraper.items import QuoteItem

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # 提取每一頁的名言
        quotes = response.css('div.quote')
        
        for quote in quotes:
            item = QuoteItem()
            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()
            
            yield item
        
        # 處理分頁 - 找到下一頁連結
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            # 構建完整的 URL 並繼續爬取
            yield response.follow(next_page, self.parse)

# 3. pipelines.py - 資料處理管道
import json

class QuotesPipeline:
    def open_spider(self, spider):
        self.file = open('quotes.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
        
        line = json.dumps(dict(item), ensure_ascii=False, indent=2)
        self.file.write(line)
        return item

# 4. settings.py - 設定檔案
BOT_NAME = 'quotes_scraper'

SPIDER_MODULES = ['quotes_scraper.spiders']
NEWSPIDER_MODULE = 'quotes_scraper.spiders'

# 遵守 robots.txt 規則
ROBOTSTXT_OBEY = True

# 啟用管道
ITEM_PIPELINES = {
    'quotes_scraper.pipelines.QuotesPipeline': 300,
}

# 設定下載延遲（秒）
DOWNLOAD_DELAY = 1

# 隨機化下載延遲
RANDOMIZE_DOWNLOAD_DELAY = True

# 設定 User-Agent
USER_AGENT = 'quotes_scraper (+http://www.yourdomain.com)'

# 啟用 AutoThrottle 自動調節爬取速度
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# 5. 進階版本的 Spider - 包含更多功能
class AdvancedQuotesSpider(scrapy.Spider):
    name = 'advanced_quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # 提取所有名言
        quotes = response.css('div.quote')
        
        for quote in quotes:
            # 提取作者頁面連結
            author_url = quote.css('small.author ~ a::attr(href)').get()
            
            item = QuoteItem()
            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()
            
            # 如果需要更多作者資訊，可以發送請求到作者頁面
            if author_url:
                yield response.follow(
                    author_url, 
                    self.parse_author,
                    meta={'item': item}
                )
            else:
                yield item
        
        # 處理分頁
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):
        item = response.meta['item']
        # 提取作者的額外資訊
        item['author_birth_date'] = response.css('span.author-born-date::text').get()
        item['author_birth_location'] = response.css('span.author-born-location::text').get()
        item['author_description'] = response.css('div.author-description::text').get()
        
        yield item

# 6. 執行爬蟲的指令
"""
在終端機中執行以下指令：

# 執行基本版本
scrapy crawl quotes

# 執行進階版本
scrapy crawl advanced_quotes

# 將結果輸出到 JSON 檔案
scrapy crawl quotes -o quotes.json

# 將結果輸出到 CSV 檔案
scrapy crawl quotes -o quotes.csv

# 設定 log 級別
scrapy crawl quotes -L INFO
"""