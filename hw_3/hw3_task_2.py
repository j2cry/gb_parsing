import pandas as pd
from pymongo import MongoClient

MONGO_HOST = 'mongodb://localhost:27017/'
DB_NAME = 'gb_homework'
COLLECTION_NAME = 'vacancies'

CROSS = {'USD': 74.2197}
BASE_CURRENCY = 'руб.'
minimal_salary = 90000


def recalculate_salary(row):
    return row.min_salary if row.currency not in CROSS.keys() else float(row.min_salary) * CROSS[row.currency]


# get database and collection
client = MongoClient(MONGO_HOST)
db = client[DB_NAME]
db_collection = db[COLLECTION_NAME]

# request to MongoDB
query = db_collection.find(filter={'min_salary': {'$ne': ''}, 'currency': {'$ne': ''}},
                           projection={'_id': 1, 'min_salary': 1, 'currency': 1})
data = list(query)

# cast to DataFrame and recalculate salaries if required
df = pd.DataFrame(data)
cond = df['currency'] != BASE_CURRENCY
df.loc[cond, 'min_salary'] = df.loc[cond, ['min_salary', 'currency']].apply(recalculate_salary, axis=1)

ids = df.loc[df['min_salary'].astype('float') > minimal_salary, '_id']

# get full info about vacancies from MongoDB
query = db_collection.find(filter={'_id': {'$in': ids.tolist()}}, projection={'_id': 0})
data = list(query)
df = pd.DataFrame(data)
df.to_csv('vacancies_filtered.csv')
