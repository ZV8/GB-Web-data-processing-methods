# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов
# Superjob и HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
# * Наименование вакансии.
# * Предлагаемую зарплату (отдельно минимальную, максимальную и валюту).
# * Ссылку на саму вакансию.
# * Сайт, откуда собрана вакансия.
#
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd


def get_compensation(string):
    compensation = {}
    prices = string.split(' ')[0:-1]
    compensation['currency'] = string.split(' ')[-1]
    if prices[0] == 'от':
        compensation['min'] = prices[1]
        compensation['max'] = None
    elif prices[0] == 'до':
        compensation['min'] = None
        compensation['max'] = prices[1]
    else:
        compensation['min'] = prices[0].split('-')[0]
        compensation['max'] = prices[0].split('-')[1]
    return compensation


def scrap_hh(page, text, vacancies):
    main_link = 'https://hh.ru'
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
            vacancy_compensation = vacancy.find('span',
                                                {'data-qa': 'vacancy-serp__vacancy-compensation'})
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


vacancies = []
vacancies = scrap_hh(page='0', text='Data science', vacancies=vacancies)

df = pd.DataFrame(vacancies)
df.to_csv('vacancies.csv', sep=';')
print(df)
