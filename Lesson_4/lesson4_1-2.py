# 1. Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
#    Для парсинга использовать XPath. Структура данных должна содержать:
#       название источника;
#       наименование новости;
#       ссылку на новость;
#       дата публикации.
# 2. Сложить собранные данные в БД


from pymongo import MongoClient, errors
from pprint import pprint
import requests
import json
from lxml import html
import time
import datetime


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 YaBrowser/21.2.0.1122 Yowser/2.5 Safari/537.36'}


def get_root_from_response(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    root = html.fromstring(response.text)
    return root


def aggr_news(source=None, name=None, link=None, date=None):
    news = {'source': source, 'name': name, 'link': link, 'date': date}
    return news


def request_to_mail():
    try:
        root = get_root_from_response(url='https://news.mail.ru/', headers=headers)
        result = root.xpath("//a[@class='list__text']/@href | "
                            "//a[@class='link link_flex']/@href | "
                            "//a[@class='newsitem__title link-holder']/@href")
        print(f'Найдено новостей mail.ru: {len(result)}')
        print(f'Получаем новости...')
        news = []
        for url in result:
            try:
                time.sleep(1)
                root = get_root_from_response(url=url, headers=headers)
                source = root.xpath("//span[@class='breadcrumbs__item'][2]/span/a/span/text()")[0]
                name = root.xpath("//h1/text()")[0]
                news.append(aggr_news(source=source, name=name, link=url,
                                      date=str(datetime.datetime.now().strftime("%d-%m-%Y"))))
            except:
                print(f'Ошибка получения новости: {url}')
        print(f'Готово')
        return news
    except:
        print('Ошибка запроса')


def request_to_yandex():
    try:
        time.sleep(1)
        root = get_root_from_response(url='https://yandex.ru/news/', headers=headers)
        news = []
        articles = root.xpath("//article")
        for article in articles:
            name = article.xpath("./div//a/h2/text()")[0].replace('\xa0', ' ')
            url = article.xpath("./div//a/h2/../@href")[0]
            source = article.xpath("./div//span[@class='mg-card-source__source']//a/text()")[0]
            news.append(
                aggr_news(source=source, name=name, link=url, date=str(datetime.datetime.now().strftime("%d-%m-%Y"))))
        print(f'Найдено новостей yandex.ru: {len(news)}')
        print(f'Готово')
        return news
    except:
        print('Ошибка запроса')


def request_to_lenta():
    try:
        time.sleep(1)
        root = get_root_from_response(url='https://lenta.ru/', headers=headers)
        news = []
        articles = root.xpath("//a[contains(@href,'/news/2021/')]")
        for article in articles:
            try:
                name = article.xpath("./span/text() | ./text()")[0].replace('\xa0', ' ')
            except:
                continue
            url = 'https://lenta.ru' + article.xpath("./@href")[0]
            source = 'lenta.ru'
            date = url.split('/')
            date = date[6] + '-' + date[5] + '-' + date[4]
            news.append(
                aggr_news(source=source, name=name, link=url, date=date))
        print(f'Найдено новостей lenta.ru: {len(news)}')
        print(f'Готово')
        return news
    except:
        print('Ошибка запроса')


result_m = request_to_mail()
result_y = request_to_yandex()
result_l = request_to_lenta()
combo_result = result_m + result_y + result_l
# pprint(combo_result)


# Сохраняем в файл
with open('news.json', 'w', encoding='utf-8') as file:
    json.dump(combo_result, file, indent=2, ensure_ascii=False)


# Сохраняем в БД
client = MongoClient('localhost', 27017)
db = client['news']
collection = db.news
collection.delete_many({})
for news_one in combo_result:
    try:
        collection.insert_one(news_one)
    except:
        print('Ошибка добавления в базу')
