from motor.motor_asyncio import AsyncIOMotorClient


mongo_client = AsyncIOMotorClient('mongodb://mongodb:27017/')
db = mongo_client['laptops']
collection = db['specs']


async def save_to_mongodb(data):
    await collection.insert_one(data)


async def find_by_url(url):
    document = await collection.find_one({'url': url})
    return document
