# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

from typing import List
from pymongo import MongoClient


def insert_if_not_exists(elements: List[dict], **kwargs):           # testing in hw2_task_1.py
    db_host = kwargs.get('host', 'mongodb://localhost:27017/')
    db_name = kwargs.get('database', 'gb_homework')
    collection_name = kwargs.get('collection', 'vacancies')

    # get database and collection
    client = MongoClient(db_host)
    db = client[db_name]
    collection = db[collection_name]

    for elem in elements[:]:
        if collection.count_documents(elem) > 0:
            elements.remove(elem)
    if elements:
        collection.insert_many(elements)


if __name__ == '__main__':
    pass
    # check DB content
    # cl = MongoClient('mongodb://localhost:27017/')
    # coll = cl.gb_homework.vacancies
    #
    # for num, el in enumerate(coll.find()):
    #     print(num + 1, el)
