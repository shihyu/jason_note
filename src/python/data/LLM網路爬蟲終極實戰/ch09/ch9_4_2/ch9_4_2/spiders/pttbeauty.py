import scrapy
from ch9_4_2.items import BeautyItem
from datetime import datetime

class PttbeautySpider(scrapy.Spider):
    name = "pttbeauty"
    allowed_domains = ["ptt.cc"]
    start_urls = ["https://www.ptt.cc/bbs/Beauty/index.html"]
    
    def __init__(self):
        self.max_pages = 10         # 最大頁數
        self.num_of_pages = 0       # 目前已爬取的頁數
        
    def start_requests(self):
        cookies =  {'over18' : '1'}
        yield scrapy.Request(
            self.start_urls[0],
            callback=self.parse,
            cookies=cookies
        )
   
    def parse(self, response):
        for href in response.css(".r-ent > div.title > a::attr(href)"):
            url = response.urljoin(href.extract())
            cookies =  {'over18' : '1'}
            yield scrapy.Request(url, cookies=cookies, callback=self.parse_post)
        self.num_of_pages = self.num_of_pages + 1    
        # 是否已經到達最大頁數
        if self.num_of_pages < self.max_pages:
            prev_page = response.xpath('//div[@id="action-bar-container"]//a[contains(text(), "上頁")]/@href')
            if prev_page:    # 是否有上一頁
                url = response.urljoin(prev_page[0].extract())
                yield scrapy.Request(url, self.parse)
            else:
                print("已經是最後一頁, 總共頁數: ", self.num_of_pages)
        else:
            print("已經到達最大頁數: ", self.max_pages)
            
    def parse_post(self, response):
        item = BeautyItem()
        
        item["author"] = response.css(".article-metaline:nth-child(1) .article-meta-value::text").extract_first()    
        item["title"] = response.css(".article-metaline-right+ .article-metaline .article-meta-value::text").extract_first()
    
        datetime_str = response.css(".article-metaline+ .article-metaline .article-meta-value::text").extract_first()
        item["date"] = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %Y')

        score = 0
        num_of_pushes = 0
        comments = response.xpath('//div[@class="push"]')
        for comment in comments:
            push = comment.css("span.push-tag::text")[0].extract()
            if "推" in push:
                score = score + 1
                num_of_pushes = num_of_pushes + 1
            elif "噓" in push:
                score = score - 1

        item["score"] = score
        item["pushes"] = num_of_pushes
        item["comments"] = len(comments)
        item["url"] = response.url
        img_urls = response.xpath('//a[contains(@href, "imgur.com")]/@href').extract()
        if img_urls:            
            item["images_len"] = len(img_urls)
            item["file_urls"] = img_urls
        else:
            item["images_len"] = 0
            item["file_urls"] = []

        yield item           