import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from pymongo import MongoClient
from configuration import DB_CONFIG

client = DB_CONFIG.CONNECTION_URL
database = DB_CONFIG.DATABASE

mongodb_client = MongoClient(client)
db = mongodb_client[database]


def get_drone_spec(drone_name):
    # DB에서 드론 정보 가져오기
    drone_data = db['Drones'].find_one({'drone': drone_name})
    return drone_data


## drone_select
def drone_info():
    # Drones 컬렉션에서 데이터 가져오기
    drone_data = db['Drones'].find()

    # 드론 이름과 모터 추력을 담을 리스트 초기화
    drone4selectlist = []

    # 각 드론의 이름과 모터 추력을 리스트에 추가
    for drone in drone_data:
        drone_name = drone['drone']
        motor_thrust = drone['motor_thrust']
        drone_weight = drone['drone_weight']
        total_battery_capacity = drone['total_battery_capacity_mah']
        drone4selectlist.append([drone_name, motor_thrust,drone_weight,total_battery_capacity])

    return drone4selectlist

def get_BC_graphs():
    graphs = db['Graphs'].find()
    BC_graph_list = []
    for BC in graphs:
        BC_name = BC['BC_name']
        graph = BC['graph']
        BC_graph_list.append([BC_name, graph])

    return BC_graph_list

def findBCname(nodename):
    bcname = db['Basecamp'].find_one({'BC_name': str(nodename)})
    return bcname


def get_graph(BC_name):
        graphresult = db['Graphs'].find_one({'BC_name': BC_name},{'_id' : 0,'graph' : 1})
        graph = graphresult.get('graph')
        return graph

## generateMissionFile
def rmPastMissionFile(user):
    oldMissionFile = db['MissionFiles'].find_one({'user': user})
    if oldMissionFile:
        db['MissionFiles'].delete_many({'user': user})

def saveMissionFile(missionFile):    
    db['MissionFiles'].insert_one(dict(missionFile))
    return True




## Mission File generate

def getBCcoor(BC_name):
    projection = {'_id': 0, 'BC_coor': 1}
    data = db['Basecamp'].find_one({'BC_name' : BC_name}, projection)
    basecamp_coor = data.get('BC_coor')
    print("basecamp_coor : " ,basecamp_coor)
    return basecamp_coor

def getNodecoor(node_name):
    projection = {'_id': 0, 'node_coor': 1}
    data = db['Nodes'].find_one({'node_name' : node_name}, projection)
    node_coor = data.get('node_coor')
    return node_coor
