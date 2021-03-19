# 2. Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
#    Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import json
import time


driver = webdriver.Chrome(executable_path="./chromedriver")
driver.get("https://www.mvideo.ru/")
wait = WebDriverWait(driver, 10)

try:
    next = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Хиты продаж')][1]/../../..//a[contains(@class, 'next-btn')]")))
    for x in range(5):
        next.click()
        time.sleep(2)
    items = driver.find_elements_by_xpath("//div[contains(text(), 'Хиты продаж')][1]/../../..//div/ul/li//h4/a")
    hits = []
    for item in items:
        product_info = json.loads(item.get_attribute('data-product-info'))
        hits.append(product_info)
    print(f'Обработано {len(hits)} товаров')
finally:
    print(f'Данные получены')
    driver.close()


# Сохраняем в файл
try:
    with open('mvideo.json', 'w', encoding='utf-8') as file:
        json.dump(hits, file, indent=2, ensure_ascii=False)
    print(f'Файл json сохранен')
except:
    print(f'Ошибка сохранения файла')


# Сохраняем в БД
try:
    client = MongoClient('localhost', 27017)
    db = client['lesson5']
    collection = db.mvideo
    collection.delete_many({})
    for hit in hits:
        try:
            collection.insert_one(hit)
        except:
            print(f'Ошибка добавления в базу: {hit}')
    print(f'Данные записаны в БД')
except:
    print(f'Ошибка записи в БД')
