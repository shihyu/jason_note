import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.css("div.quote"):
            text = quote.css("span.text::text").extract_first()
            author = quote.xpath(".//small/text()").extract_first()
            scraped_quote = {
                "text" : text,
                "author": author
            }
            yield scraped_quote

