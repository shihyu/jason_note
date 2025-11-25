import scrapy


class PttnbaSpider(scrapy.Spider):
    name = "pttnba"
    allowed_domains = ["ptt.cc"]
    start_urls = ["https://www.ptt.cc/bbs/NBA/index.html"]

    def parse(self, response):
        titles = response.css("div.r-ent > div.title > a::text").extract()
        votes = response.xpath("//div[@class='nrec']/span/text()").extract()
        authors = response.xpath("//div[@class='meta']/div[1]/text()").extract()
        for item in zip(titles, votes, authors):
            scraped_info = {
                    "title" : item[0],
                    "vote"  : item[1],
                    "author": item[2]
            }
            yield scraped_info
