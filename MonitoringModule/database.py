import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pymongo import MongoClient

from configration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]


def insert_log(log):
    # insert_log
    db['DroneStatus'].insert_one(log)
    # print('insert create_at : ', log['create_at'])
    
    # if log_count over 5, delete oldest log
    drone_name = log['drone_name']
    count = db['DroneStatus'].count_documents({'drone_name': drone_name})
    if count >= 5:
        oldest_log = db['DroneStatus'].find({'drone_name': drone_name}).sort('create_at', 1).limit(1)
        # print('remove_create_at : ', oldest_log[0]['create_at'])
        db['DroneStatus'].delete_one(oldest_log[0])
        
    return True