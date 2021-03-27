# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy2703

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            ready_salary = self.process_salary_hhru(item['salary'])
        if spider.name == 'sjobru':
            ready_salary = self.process_salary_sjobru(item['salary'])
        item['min_salary'] = ready_salary[0]
        item['max_salary'] = ready_salary[1]
        item['currency'] = ready_salary[2]
        item['type_salary'] = ready_salary[3]
        del item['salary']
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hhru(self, salary):
        ready_salary = (None, None, None, None)
        salary = [s.replace('\xa0', '').strip() for s in salary]
        if len(salary) == 5:
            if salary[0] == 'от':
                ready_salary = (salary[1], None, salary[-2], salary[-1])
            if salary[0] == 'до':
                ready_salary = (None, salary[1], salary[-2], salary[-1])
        elif len(salary) == 7:
            ready_salary = (salary[1], salary[3], salary[-2], salary[-1])
        return ready_salary

    def process_salary_sjobru(self, salary):
        ready_salary = (None, None, None, None)
        cur = salary[2].split('\xa0')[-1]
        sal = ''.join(salary[2].split('\xa0')[0:-1])
        salary = [s.replace('\xa0', '').strip() for s in salary]
        if len(salary) == 3:
            if salary[0] == 'от':
                ready_salary = (sal, None, cur, None)
            elif salary[0] == 'до':
                ready_salary = (None, sal, cur, None)
            else:
                ready_salary = (salary[0], salary[0], salary[3], None)
        elif len(salary) == 4:
            ready_salary = (salary[0], salary[1], salary[3], None)
        return ready_salary
