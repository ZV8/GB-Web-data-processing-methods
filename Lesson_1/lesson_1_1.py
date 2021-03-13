# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json

req = requests.get("https://api.github.com/users/ZV8/repos")
print(f'Код ответа: {req.status_code}')
res = req.json()
with open('repos.json', 'w', encoding='utf-8') as file:
    json.dump(res, file, indent=2, ensure_ascii=False)