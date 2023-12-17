import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pymongo import MongoClient

from configuration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]


def getMissionFileByDrone(drone_name):
    return db['MissionFiles'].find_one({'drone_name': drone_name})


def getDroneStatusByDrone(drone_name):
    try:
        log = db['DroneStatus'].find({'drone_name': drone_name}).sort("create_at", -1).limit(1)
        return log[0]
    except:
        return None
    
def getTaskMessage():
    try:
        task_message = db['Task'].find_one()
        db['Task'].delete_one(task_message)
        # print(task_message)
        return task_message
    except:
        pass
        # print("no task_message")