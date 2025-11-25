# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
#from itemadapter import ItemAdapter


class CleanCsvFieldsPipeline:
    def process_item(self, item, spider):
        item['text'] = self._clean_field(item.get('text', ''))
        item['author'] = self._clean_field(item.get('author', ''))
        return item

    def _clean_field(self, value):
        value = str(value)
        # 刪除非標準引號
        value = value.replace('“', '').replace('”', '')
        # 將雙引號轉成 CSV 標準的兩個雙引號
        value = value.replace('"', '""')
        return value
