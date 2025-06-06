from pymongo import MongoClient

#url link for connecting to the MongoDB database
mongo_link = "mongodb+srv://farmuser:farm12345@cluster88013.uygbstv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster88013"
#connects to Mongo, gets the smartfarm database and selects all readings
mongo_client = MongoClient(mongo_link)
db = mongo_client.smartfarm
collection = db.readings

#function for getting all the readings from the system
def get_all_data():
    data = list(collection.find({}, {"_id": 0}))
    data.reverse()
    return data