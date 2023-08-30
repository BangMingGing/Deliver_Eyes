from pymongo import MongoClient

client = "mongodb+srv://bmk802:ahdrhelqlqlqjs1!@cluster0.psq7llu.mongodb.net/?retryWrites=true&w=majority"
database = "Deliver_Eyes"

mongodb_client = MongoClient(client)
db = mongodb_client[database]


## signup

def check_email(email):
    user = db['Users'].find_one({'email': email})
    if user is not None:
        return True
    else:
        return False

def insert_user(user):
    db['Users'].insert_one(dict(user))
    return True


## login

def get_user(email):
    user = db['Users'].find_one({'email': email})
    return user