import time
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CrawlDataPipeline:
    
    def __init__(self):
        self.start = None
        self.end = None
        self.ids_seen = set()
    
    def process_item(self, item, spider):
        # 去除重复数据
        if item['jobid'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item}")
        else:
            self.ids_seen.add(item['jobid'])
            return item
    
    def open_spider(self, spider):
        self.start = time.time()
    
    def close_spider(self, spider):
        self.end = time.time()
        print(f'\033[34m>> 总计耗时{self.end - self.start:.2f}s\033[0m')
