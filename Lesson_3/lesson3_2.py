# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.


from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['vacancies_hh']


def find_vacancy(collection=db.vacancies):
    compensation = float(input(f'Введите желаемый размер зарплаты: '))
    find = {'$or': [
        {'compensation_min': {'$gte': compensation}},
        {'compensation_max': {'$gte': compensation}}
    ]}
    res = collection.find(find)
    for v in res:
        pprint(v)


find_vacancy()
