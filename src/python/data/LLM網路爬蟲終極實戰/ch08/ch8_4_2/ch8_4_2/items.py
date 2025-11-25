# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NBAItem(scrapy.Item):
    # 定義Item的欄位
    title = scrapy.Field()
    vote = scrapy.Field()
    author = scrapy.Field()
