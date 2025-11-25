import scrapy
from ch8_4_2.items import NBAItem

class PttnbaSpider(scrapy.Spider):
    name = "pttnba"
    allowed_domains = ["ptt.cc"]
    start_urls = ["https://www.ptt.cc/bbs/NBA/index.html"]

    def parse(self, response):
        for sel in response.css(".r-ent"):
            item = NBAItem()
            item["title"] = sel.css("div.title > a::text").extract_first()
            item["vote"]  = \
             sel.xpath("./div[@class='nrec']/span/text()").extract_first()
            item["author"] = \
             sel.xpath("./div[@class='meta']/div[1]/text()").extract_first()
            yield item

