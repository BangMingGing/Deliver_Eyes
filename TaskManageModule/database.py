import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pymongo import MongoClient

from config import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]


def getMissionFileByDrone(drone):
    return db['MissionFiles'].find_one({'drone': drone})


def getDroneStatusByDrone(drone):
    try:
        log = db['DroneStatus'].find({'drone_name': drone_name}).sort("create_at", -1).limit(1)
        return log[0]
    except:
        return None