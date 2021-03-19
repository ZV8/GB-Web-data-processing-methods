# 1. Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
#    и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from pymongo import MongoClient
import json
import time


def format_date(d):
    month_list = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
           'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
    time = d.split(', ')[1]
    date_str = d.split(', ')[0]
    if date_str == 'Сегодня':
        return str(datetime.now().strftime("%d-%m-%Y")) + ' ' + time
    if date_str == 'Вчера':
        yesterday = datetime.now() - timedelta(days=1)
        return str(yesterday.strftime("%d-%m-%Y")) + ' ' + time
    date_list = date_str.split(' ')
    day = date_list[0]
    month = month_list[date_list[1]]
    if len(date_list) == 3:
        year = date_list[2]
    else:
        year = str(datetime.now().strftime("%Y"))
    return day + '-' + month + '-' + year + ' ' + time


driver = webdriver.Chrome(executable_path="./chromedriver")
driver.get("https://mail.ru/")
login = driver.find_element_by_name("login")
login.send_keys("************")
login.send_keys(Keys.RETURN)
time.sleep(1)
password = driver.find_element_by_name("password")
password.send_keys("************")
password.send_keys(Keys.RETURN)

try:
    wait = WebDriverWait(driver, 10)
    urls = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href,'/inbox/0')]")))
    links = []
    for url in urls:
        links.append(url.get_attribute('href'))
    mails = []
    print(f'Идет процесс сбора данных...')
    for link in links:
        driver.get(link)
        author = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='letter-contact'][1]"))).text
        date = format_date(wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='letter__date']"))).text)
        theme = wait.until(EC.presence_of_element_located((By.XPATH, "//h2"))).text
        message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='mailsub_mr_css_attr'] | //div[@class='js-helper js-readmsg-msg']"))).text
        mails.append({'author': author, 'date': date, 'theme': theme, 'message': message})
        time.sleep(2)
finally:
    print(f'Данные получены')
    driver.close()


# Сохраняем в файл
try:
    with open('mail.json', 'w', encoding='utf-8') as file:
        json.dump(mails, file, indent=2, ensure_ascii=False)
    print(f'Файл json сохранен')
except:
    print(f'Ошибка сохранения файла')


# Сохраняем в БД
try:
    client = MongoClient('localhost', 27017)
    db = client['lesson5']
    collection = db.mails
    collection.delete_many({})
    for mail in mails:
        try:
            collection.insert_one(mail)
        except:
            print(f'Ошибка добавления в базу: {mail}')
    print(f'Данные записаны в БД')
except:
    print(f'Ошибка записи в БД')
