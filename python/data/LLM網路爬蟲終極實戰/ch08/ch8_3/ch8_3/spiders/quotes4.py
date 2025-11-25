import scrapy


class Quotes4Spider(scrapy.Spider):
    name = "quotes4"
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.css("div.quote"):
            text = quote.css("span.text::text").extract_first()
            author = quote.xpath(".//small/text()").extract_first()
            scraped_quote = {
                "text" : text,
                "author": author,
                "birthday": None
            }
            authorHref = quote.css(".author + a::attr(href)").extract_first()
            authorPg = response.urljoin(authorHref)
            yield scrapy.Request(authorPg,meta={"item": scraped_quote},
                                 callback=self.parse_author)
            
        nextPg = response.xpath("//li[@class='next']/a/@href").extract_first()
        if nextPg is not None:
            yield response.follow(nextPg, callback=self.parse)
            
    def parse_author(self, response):
        item = response.meta["item"]
        b = response.css(".author-born-date::text").extract_first().strip()
        item["birthday"] = b
        return item
        