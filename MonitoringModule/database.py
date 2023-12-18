import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pymongo import MongoClient, ASCENDING

from configuration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]
collection = db['DroneStatus']
collection.create_index([("create_at", ASCENDING)], expireAfterSeconds=60)


def insert_log(log):
    # insert_log
    collection.insert_one(log)
    # print('insert create_at : ', log['create_at'])
    
    # if log_count over 5, delete oldest log
    # drone_name = log['drone_name']
    # count = db['DroneStatus'].count_documents({'drone_name': drone_name})
    # if count > 5:
    #     oldest_logs = db['DroneStatus'].find({'drone_name': drone_name}).sort('create_at', 1).limit(count - 5)
    #     for oldest_log in oldest_logs:
    #         db['DroneStatus'].delete_one({'_id': oldest_log['_id']})

    return True