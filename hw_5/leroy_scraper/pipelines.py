# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pathlib

import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from settings import IMAGES_STORE

MONGO_HOST = 'mongodb://localhost:27017/'
DB_NAME = 'gb_homework'


class LeroyDataScraperPipeline:
    def __init__(self):
        client = MongoClient(MONGO_HOST)
        self.db = client[DB_NAME]
        self.base_path = pathlib.Path(IMAGES_STORE)

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        if collection.count_documents(item) == 0:
            item['images'] = self.base_path.joinpath(item['_id'])
            collection.insert_one(item)
        return item


class LeroyImagesScraperPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if not (images := item['images']):
            return
        for image in images:
            try:
                yield scrapy.Request(image)
            except Exception as e:
                print(f'Images not found! {e}')

    def item_completed(self, results, item, info):
        if results:
            item['images'] = [img[1] for img in results if img[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        base_path = pathlib.Path.home().joinpath('data', 'leroy_images').as_posix()
        folder = pathlib.Path().joinpath(item['_id'])
        filename = pathlib.Path(request.url).name
        return folder.joinpath(filename).as_posix()
