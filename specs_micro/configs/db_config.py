from pymongo import MongoClient

mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['laptop_specs']
collection = db['laptops']


def save_to_mongodb(data):
    collection.insert_one(data)


def find_by_url(url):
    return collection.find_one({'url': url})
