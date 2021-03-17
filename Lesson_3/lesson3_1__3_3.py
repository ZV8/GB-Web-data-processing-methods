# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
#    записывающую собранные вакансии в созданную БД.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.


from pymongo import MongoClient, errors
from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
import json
import datetime


client = MongoClient('localhost', 27017)
db = client['vacancies_hh']
collection = db.vacancies


def get_compensation(string):
    compensation = {}
    prices = string.split(' ')[0:-1]
    compensation['currency'] = string.split(' ')[-1]
    if prices[0] == 'от':
        compensation['min'] = float(prices[1])
        compensation['max'] = None
    elif prices[0] == 'до':
        compensation['min'] = None
        compensation['max'] = float(prices[1])
    else:
        compensation['min'] = float(prices[0].split('-')[0])
        compensation['max'] = float(prices[0].split('-')[1])
    return compensation


def scrap_hh(page, text, vacancies):
    main_link = 'https://hh.ru'
    id_pref = 'hh_'
    params = {'clusters': 'true',
              'enable_snippets': 'true',
              'text': text,
              'st': 'searchVacancy',
              'customDomain': '1',
              'page': page}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 YaBrowser/21.2.0.1122 Yowser/2.5 Safari/537.36'}

    response = requests.get(main_link + '/search/vacancy', params=params, headers=headers)
    print(f'Страница {page}. Ответ сервера: {response.status_code}')
    if response.ok:
        soup = bs(response.text, 'html.parser')
        vacancies_list = soup.findAll('div', {'class': 'vacancy-serp-item'})
        for vacancy in vacancies_list:
            vacancy_data = {}
            vacancy_name = vacancy.find('span', {'class': 'resume-search-item__name'})
            vacancy_link = vacancy_name.find('a')['href']
            vacancy_name = vacancy_name.getText()
            vacancy_compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            vacancy_response = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy_response'})
            vacancy_id = json.loads(vacancy_response.find('script')['data-params'])['vacancyId']
            try:
                vacancy_compensation_string = vacancy_compensation.getText().replace("\xa0", "")
            except Exception as e:
                vacancy_compensation_string = None

            if vacancy_compensation_string:
                vacancy_compensation_list = get_compensation(vacancy_compensation_string)
                vacancy_compensation_currency = vacancy_compensation_list['currency']
                vacancy_compensation_min = vacancy_compensation_list['min']
                vacancy_compensation_max = vacancy_compensation_list['max']
            else:
                vacancy_compensation_currency = None
                vacancy_compensation_min = None
                vacancy_compensation_max = None

            vacancy_data['source'] = main_link
            vacancy_data['search'] = text
            vacancy_data['name'] = vacancy_name
            vacancy_data['link'] = vacancy_link
            # vacancy_data['compensation'] = vacancy_compensation_string
            vacancy_data['compensation_min'] = vacancy_compensation_min
            vacancy_data['compensation_max'] = vacancy_compensation_max
            vacancy_data['compensation_currency'] = vacancy_compensation_currency
            vacancy_data['vacancy_id'] = int(vacancy_id)
            vacancy_data['_id'] = id_pref + vacancy_id
            vacancy_data['last_modified'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            #
            vacancies.append(vacancy_data)
        try:
            next_page_link = soup.find('a', {'data-qa': 'pager-next'})['href']
            if next_page_link:
                next_page = next_page_link.split('&page=')[1]
                scrap_hh(next_page, text, vacancies)
        except Exception as e:
            print('Скрапинг завершен')
        return vacancies


def add_vacancies(vacancies, collection):
    # collection.delete_many({})
    for vacancy in vacancies:
        change_list = {}
        try:
            collection.insert_one(vacancy)
        except errors.DuplicateKeyError:
            changed = False
            new_values = []
            prev_values = []
            for vacancy_key, vacancy_value in vacancy.items():
                if vacancy_key == 'last_modified':
                    continue
                collection_value = collection.find_one({'_id': vacancy['_id']})[vacancy_key]
                if collection_value != vacancy_value:
                    changed = True
                    new_values.append({vacancy_key: vacancy_value})
                    prev_values.append({vacancy_key: collection_value})
            if changed:
                change_list[vacancy['_id']] = [
                    {'date_update': vacancy['last_modified']},
                    {'new_values': new_values},
                    {'prev_values': prev_values}
                ]
                collection.replace_one({'_id': vacancy['_id']}, vacancy)
                pprint(change_list)
                # пример:
                # {'hh_42652449': [{'date_update': '2021-03-17 16:38'},
                #                  {'new_values': [{'search': '8_Data science'},
                #                                   {'name': '8_Field Application Scientist'}]},
                #                  {'prev_values': [{'search': '7_Data science'},
                #                                   {'name': '7_Field Application Scientist'}]}]}
                # далее сохраню это в БД для дальнейшей работы с историей изменений
                # ...


vacancies = []
vacancies = scrap_hh(page='0', text='Data science', vacancies=vacancies)

with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(vacancies, file, indent=2, ensure_ascii=False)
# with open('vacancies.json', 'r', encoding='utf-8') as file:
#     vacancies = json.load(file)

add_vacancies(vacancies, collection)

result = collection.find({})
for vacancy in result:
    pprint(vacancy)
