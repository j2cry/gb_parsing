# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

MONGO_HOST = 'mongodb://localhost:27017/'
DB_NAME = 'gb_homework'


class JobScraperPipeline:
    def __init__(self):
        client = MongoClient(MONGO_HOST)
        self.db = client[DB_NAME]

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item
