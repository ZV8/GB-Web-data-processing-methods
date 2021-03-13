# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
import json

token = 'xxxxxxxxxx'

url = 'https://api.vk.com/method/groups.get'
params = {
    'access_token': token,
    'user_id': '21507694',
    'v': '5.130',
    'extended': 1
}

req = requests.get(url, params=params)
print(f'Код ответа: {req.status_code}')
if req.ok:
    try:
        res = req.json()
        with open('groups.json', 'w', encoding='utf-8') as file:
            json.dump(res, file, indent=2, ensure_ascii=False)
        print('Список групп:')
        for item in res.get('response').get('items'):
            print(f'{item.get("name")}')
    except ValueError:
        print('Ошибка сохранения в файл')
