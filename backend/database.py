from pymongo import MongoClient

from configuration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

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

def getMissionByUser(user):
    missionFile = db['MissionFiles'].find_one({'user': user})
    if missionFile is not None:
        return missionFile['mission']
    
    return None

def getDroneByUser(user):
    missionFile = db['MissionFiles'].find_one({'user': user})
    if missionFile is not None:
        return missionFile['drone_name']
    
    return None

def getDroneStatusByDroneName(drone_name):
    drone_status = db['DroneStatus'].find({'drone_name': drone_name}).sort('create_at', -1).limit(1)[0]
    if drone_status is not None:
        gps = drone_status['GPS_info']
        return [gps['lon'], gps['lat']]

    return None

## generateMissionFile

def rmPastMissionFile(user):
    oldMissionFile = db['MissionFiles'].find_one({'user': user})
    if oldMissionFile:
        db['MissionFiles'].delete_one({'user': user})

def saveMissionFile(missionFile):    
    db['MissionFiles'].insert_one(dict(missionFile))
    return True

