# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import csv


class LeroyparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroy_290321

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        # image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f"full/{item['article']}/{request.url.split('/')[-1]}"

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


class LeroyCSVPipeline(object):
    def __init__(self):
        self.file = 'database.csv'
        with open(self.file, 'r', newline='') as csv_file:
            self.tmp_data = csv.DictReader(csv_file).fieldnames

        self.csv_file = open(self.file, 'a', newline='', encoding='UTF-8')

    def process_item(self, item, spider):
        colums = item.fields.keys()

        data = csv.DictWriter(self.csv_file, colums)
        if not self.tmp_data:
            data.writeheader()
            self.tmp_data = True
        try:
            data.writerow(item)
        except Exception as e:
            print(e)

        return item

    def __del__(self):
        self.csv_file.close()
