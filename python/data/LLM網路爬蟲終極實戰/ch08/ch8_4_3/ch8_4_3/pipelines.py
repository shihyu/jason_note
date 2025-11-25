# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
#from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class PttPipeline(object):
    def process_item(self, item, spider):
        if item["vote"]:
            if item["vote"] == "爆":
                item["vote"] = 500
            else:
                item["vote"] = int(item["vote"]) + 5
            return item
        else:
            raise DropItem("沒有推文數: %s" % item)
