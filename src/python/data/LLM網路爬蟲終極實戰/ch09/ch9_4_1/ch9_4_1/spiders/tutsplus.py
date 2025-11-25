import scrapy
import re
from ch9_4_1.items import TutsplusItem

class TutsplusSpider(scrapy.Spider):
    name = "tutsplus"
    allowed_domains = ["code.tutsplus.com"]
    start_urls = ["https://code.tutsplus.com/t/tutorials"]

    def parse(self, response):
        # 取得目前頁面所有的超連結
        links = response.xpath('//a/@href').extract()
        
        crawledLinks = []
        # 取出符合條件的超連結, 即其他頁面 href="/t/tutorials?page=2"
        linkPattern = re.compile("^\/t/tutorials\?page=\d+")
        for link in links:
            if linkPattern.match(link) and not link in crawledLinks:
                link = "https://code.tutsplus.com" + link
                crawledLinks.append(link)
                yield scrapy.Request(link, self.parse)
 
        # 取得每一頁的詳細課程資訊
        for tut in response.css("li.w-full"):
            item = TutsplusItem()            
            item["title"] = tut.css(
                "h3.font-semibold::text").extract_first().strip()
            item["author"] = tut.css(
                "div.text-xs > a::text").extract_first().strip()
            item["category"] = tut.css(
                "a.text-bubble-gum.uppercase::text").extract_first().strip()
            item["date"] = tut.css(
                "time.text-grey-500::text").extract_first().strip()
            yield item
