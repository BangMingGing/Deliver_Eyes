import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pymongo import MongoClient

from configuration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]


def update_face_recog_result_to_mission_file(drone_name, mse, result):
    query = {'drone_name': drone_name}
    update = {"$set": {'face_recog_result': result, 'mse': mse}}

    result = db['MissionFiles'].update_one(query, update)

    if result.matched_count > 0:
        print(f"Successfully updated the face recog result")
    else:
        print(f"No matching document found for drone {drone_name}")

    return

def getFaceMessage():
    try:
        task_message = db['Face'].find_one()
        db['Face'].delete_one(task_message)
        # print(task_message)
        return task_message
    except:
        pass
        # print("no task_message")


def send_to_task_module(new_messsage):
    db['Task'].insert_one(new_messsage)
    return