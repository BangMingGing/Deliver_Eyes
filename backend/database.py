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


## map

def getBaseCamp(baseCampName):
    baseCampNode = db['Basecamp'].find_one({'BC_name': baseCampName})
    baseCampLocation = baseCampNode['BC_coor']
    return baseCampLocation

def getNodes():
    # node_coor 데이터만 가져와 리스트로 반환
    projection = {'_id': 0, 'node_coor': 1}
    nodes = list(db['Nodes'].find({}, projection))
    # [{'node_coor': [lat, lon]}] --> [[lat, lon]]
    nodeCoordinates = [node['node_coor'] for node in nodes]
    return nodeCoordinates