from pymongo import MongoClient

from configuration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]


def update_face_recog_result_to_mission_file(drone_name, result, mse):
    query = {'drone_name': drone_name}
    update = {"$set": {'face_recog_result': result, 'mse': mse}}

    result = db['MissionFiles'].update_one(query, update)

    if result.matched_count > 0:
        print(f"Successfully updated the face recog result")
    else:
        print(f"No matching document found for drone {drone_name}")

    return