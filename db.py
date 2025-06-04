from pymongo import MongoClient

# MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://farmuser:farm12345@cluster88013.uygbstv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster88013"

# Establish the connection
mongo_client = MongoClient(MONGO_URI)

# Get the database and collection
db = mongo_client.smartfarm
collection = db.readings

# Optional helper function
def get_all_data():
    data = list(collection.find({}, {"_id": 0}))
    data.reverse()  # Newest first
    return data