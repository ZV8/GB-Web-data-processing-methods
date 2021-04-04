# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь


from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['insta_040421']
collection = db.instagram


def find_users(collection=collection, type='subscriber'):
    result = []
    username = input(f'Введите логин пользователя instagram: ')
    find = {'$and': [
        {'owner': username},
        {'type': type}
    ]}
    res = collection.find(find)
    for item in res:
        del item['_id']
        del item['user']
        del item['owner']
        del item['type']
        result.append(item)
    return username, result


print(f'Получить данные о подписчиках пользователя.')
user, subscribers = find_users(type='subscriber')
pprint(subscribers)
print(f'Количество подписчиков у {user}: {len(subscribers)}\n\n\n')


print(f'Получить данные, на кого подписан пользователь.')
user, subscriptions = find_users(type='subscription')
pprint(subscriptions)
print(f'Количество подписок у {user}: {len(subscriptions)}')
