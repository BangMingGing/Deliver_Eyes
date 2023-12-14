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

def getNodeName(destination):
    # node_coor 데이터만 가져와 리스트로 반환
    projection = {'_id': 0, 'node_name': 1}
    data = db['Nodes'].find_one({'node_coor' : destination }, projection)
    node_name = str(data.get('node_name'))
    return node_name

def getMissionByUser(user):
    missionFile = db['MissionFiles'].find_one({'user': user})
    if missionFile is not None:
        return missionFile['mission']
    
    return None

def getInitialDataForMonitoring():
    projection = {'_id': 0, 'drone_name': 1, 'mission': 1}
    data = db['MissionFiles'].find({}, projection)
    
    # 커서를 순회하면서 각 문서의 'drone_name'과 'mission' 값을 추출하고 중복을 제거
    drone_data = [{'drone_name': document['drone_name'], 'mission': document['mission']} for document in data]
    
    if drone_data:
        return drone_data  # 중복 제거를 위해 리스트로 반환
    
    return None

def getDroneByUser(user):
    missionFile = db['MissionFiles'].find_one({'user': user})
    if missionFile is not None:
        return missionFile['drone_name']
    
    return None

def getDroneStatusByDroneName(drone_name):
    drone_status = db['DroneStatus'].find({'drone_name': drone_name}).sort('create_at', -1).limit(1)[0]
    if drone_status is not None:
        return drone_status

    return None

def getFaceRecogResultByDroneName(drone_name):
    query = {"drone_name": drone_name}
    projection = {"_id": 0, "face_recog_result": 1}

    result = db['MissionFiles'].find_one(query, projection)

    if result:
        return result.get("face_recog_result")
    else:
        return None
    
def getMissionFileByUser(user):
    missionFile = db['MissionFiles'].find_one({'user': user})
    if missionFile is not None:
        return missionFile
    
    return None


## Node

def insert_node(node):
    db['Nodes'].insert_one({'node':node})
    return True

def getBCcoor(BC_name):
    projection = {'_id': 0, 'BC_coor': 1}
    data = db['Basecamp'].find_one({'BC_name' : BC_name}, projection)
    basecamp_coor = data.get('BC_coor')
    print("basecamp_coor : " ,basecamp_coor)
    return basecamp_coor

def getBCNodes():
    projection = {'_id': 0, 'BC_name' : 1, 'BC_coor': 2}
    basecamps = list(db['Basecamp'].find({}, projection))
    return basecamps

def getBC_adjnode(bc_name):
    projection = {'_id': 0, 'adj_node' : 1}
    basecamp_result = db['Basecamp'].find_one({"BC_name": bc_name}, projection)
    return basecamp_result

def update_bc_neighbor(bc_name, adj_node):
    db['Basecamp'].update_one(
    {"BC_name": bc_name},
    {"$push": {"adj_node": adj_node}},
    upsert=True
    )

def getNodecoor(node_name):
    projection = {'_id': 0, 'node_coor': 1}
    data = db['Nodes'].find_one({'node_name' : node_name}, projection)
    node_coor = data.get('node_coor')
    return node_coor

def getnode_adjnode(node_name):
    projection = {'_id': 0, 'adj_node' : 1}
    adj_nodes = db['Nodes'].find_one({"node_name": node_name}, projection)
    return adj_nodes

def update_node_neighbor(neighbor_name,node_adj_node):
    db['Nodes'].update_one(
    {"node_name": neighbor_name},
    {"$push": {"adj_node": node_adj_node}},
    upsert=True
    )

def getNodes4node():
    projection = {'_id': 0, 'node_name' : 1, 'node_coor': 2}
    nodes = list(db['Nodes'].find({}, projection))
    return nodes

def insert_new_node(node_name, node_coor, adj_node):
    db['Nodes'].insert_one({'node_name' : int(node_name),
                            'node_coor' : node_coor,
                            'adj_node' : adj_node
                            })
    return True

def delete_node(node_name):
    db['Nodes'].delete_one({'node_name': node_name})
    return True

def find_adj_node(node_name):
    result = db['Nodes'].find({'adj_node': {'$elemMatch': {'0': str(node_name)}}})
    return result

def find_BC_adj_node(node_name):
    basecamp_result = db['Basecamp'].find({'adj_node': {'$elemMatch': {'0': str(node_name)}}})
    return basecamp_result

def reupdate_bc_adjnode(basecamp_doc,new_basecamp_adj_node):
    db['Basecamp'].update_one({'_id': basecamp_doc['_id']}, {'$set': {'adj_node': new_basecamp_adj_node}})
    return True
def reupdate_node_adjnode(doc,new_adj_node):
    db['Nodes'].update_one({'_id': doc['_id']}, {'$set': {'adj_node': new_adj_node}})
    return True


### graph

def findBCname(nodename):
    bcname = db['Basecamp'].find_one({'BC_name': str(nodename)})
    return bcname

def findNodes():
    nodes = db['Nodes'].find()
    return nodes

def findGraph():
    graphs = db['Graphs'].find()
    return graphs

def saveGraph(basecamp_name, graph):
    graph = db["Graphs"].insert_one({'BC_name' : basecamp_name,
                                    'graph' : graph})
    return True

def reviseGraph(basecamp_name, graph):
    db['Graphs'].update_one({"BC_name": basecamp_name},{"$set": {"graph": graph}})
    return True
