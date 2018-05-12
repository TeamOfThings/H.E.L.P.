import pymongo
import pymongo.collection
from pymongo import MongoClient, InsertOne, DeleteOne, ReplaceOne

connection_params = {
    'user': 'TeamOfThings',
    'password': 'totproject',
    'host': 'ds219130.mlab.com',
    'port': 19130,
    'namespace': 'help_db',
}

client = MongoClient(
    'mongodb://{user}:{password}@{host}:'
    '{port}/{namespace}'.format(**connection_params)
)

collection = client["help_db"]["LocalizationResults"]

requests = [InsertOne({"device": "luca", "room":"bagno"})]
result = collection.bulk_write(requests)

for doc in collection.find({}):
     print(doc)
