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


class DBInterface():
	def __init__(self, __connection_parameters):
		self.__connection_parameters = __connection_parameters
		self.__client = MongoClient(
    		'mongodb://{user}:{password}@{host}:'
   			'{port}/{namespace}'.format(**self.__connection_parameters)
		)
		self.__collection = self.__client["help_db"]["LocalizationResults"]

	# Insert a new entry in the database
	def insert_db_entry(self, device, location):
		self.__collection.insert_one({"device":device, "room":location})

	# Delete a specific DB entry
	def delete_db_entry(self, device, location):
		self.__collection.delete_one({"device":device, "room":location})

	# Delete all the entries relative to a specific device
	def delete_device_entries(self, device):
		self.__collection.delete_many({"device":device})

	# Delete all the entries relative to a specific room
	def delete_room_entries(self, room):
		self.__collection.delete_many({"room":room})

	# Delete all the entries in the DB
	def clean_db(self):
		self.__collection.delete_many({})

	# Retrieve all the entries in the DB
	def get_all_entries(self):
		return self.__collection.find({})

	#Retrieve all the entries relative to a specific device
	def get_device(self, device):
		return self.__collection.find({"device":device})

	#Retrieve all the entries relative to a specific room
	def get_room(self, room):
		return self.__collection.find({"room":room})


def main():
    db = DBInterface(connection_params)

    db.clean_db()

    db.insert_db_entry("chiara", "Bache")
    db.insert_db_entry("andrea", "camera")
    db.insert_db_entry("luca", "cucina")
    db.insert_db_entry("chiara", "bagno")
    db.insert_db_entry("nerfgun", "camera")

    for doc in db.get_device("chiara"):
        print(doc["room"])

    print("\n")

    for doc in db.get_room("camera"):
        print(doc)

    

if __name__ == "__main__":
	main()