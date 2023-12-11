import heapq

from . import database
from . import battery_consumption

def set_drone_name(get_drone_name):
    global drone_name
    drone_name = get_drone_name

def payload_calcurator(motor_thrust, drone_weight):
    #quadcopter의 경우 총 추력  = 
    total_thrust = (motor_thrust*6)/2
    payload = (total_thrust - drone_weight*1000)/1000
    return payload


async def drone_path_select(payload, destination_node):
    #drone4selectlist = [[drone_name, motor_thrust drone_weight] ...]
    drone4selectlist = database.drone_info()
    available_drone = []
    #페이로드를 고려하여 이용가능한 드론 선정
    for drone in drone4selectlist : 
        caculate_payload = payload_calcurator(drone[1],drone[2])
        print(caculate_payload)
        if (caculate_payload > payload ):
            available_drone.append([drone[0], drone[3]])
    print(f"available_drone is {available_drone}")

    #최단거리 수행 가능한지 판별
    #drone4selectlist = [[BC_name, graph] ...]
    BC_graph_list = database.get_BC_graphs()
    usable_drone = []
    for drone in available_drone:
        drone_name = drone[0]
        set_drone_name(drone_name)
        total_battery_capacity = float(drone[1])
        for info in BC_graph_list:
            start_node = info[0]
            graph = info[1]
            shortest_path = dijkstra(graph, start_node, destination_node, payload, drone_name)
            altitudes = {node: int(graph[node]['adj_node'][0][1]) if 'adj_node' in graph[node] and graph[node]['adj_node'] else 0 for node in graph}
            altitude_list = [altitudes[node] for node in shortest_path]
            altitudes[start_node] = int(database.findBCname(start_node).get('altitude', 0))
            total_energy_consumption = battery_consumption.calculate_total_energy_consumption(graph, altitudes, shortest_path, destination_node, payload, drone_name)
            
            print(f" drone name : {drone_name} total_energy_consumption : {total_energy_consumption}")
            if (total_battery_capacity > total_energy_consumption*2):
                usable_drone.append([drone_name, total_battery_capacity])
            else : 
                print(f"No suitable drone found.")

    #사용 가능한 드론들 중 배터리 용량이 가장 적은 것으로 배정
    use_drone = min(usable_drone, key=lambda x: x[1], default=None)
    selected_drone_name = None
    if use_drone:
        selected_drone_name = use_drone[0]
        print(f"Selected drone: {selected_drone_name}")
    else:
        print("No suitable drone found.")

    mission = await makeMission(shortest_path, altitude_list)
    print(selected_drone_name)
    return selected_drone_name, mission

async def makeMission(shortest_path, altitude_list):
    mission = []
    for i, path in enumerate(shortest_path):
        coor = None
        if 'bc' in path:
            coor = database.getBCcoor(path)
        else:
            coor = database.getNodecoor(int(path))

        lon = coor[0]
        lat = coor[1]
        alt = altitude_list[i]
        
        mission.append([lon, lat, alt])
    
    return mission


async def saveMissionFile(user, drone_name, mission):
    # 테스트 미션 파일
    missionFile = {
        'user': user,
        'mission': mission, # [위도, 경도, 고도]
        'drone_name': drone_name
    }

    # user의 과거 미션 파일 삭제
    database.rmPastMissionFile(user)

    # 미션 파일 DB에 저장
    database.saveMissionFile(missionFile)

    return missionFile

    

# Dijkstra 알고리즘을 적용하여 최단 경로를 찾는 함수
def dijkstra(graph, start, goal, payload, drone_name):
    # 우선순위 큐를 사용하여 노드와 해당 노드의 예비 에너지 소비를 저장
    priority_queue = [(0, start, 0)]  # 업데이트: 초기 고도 0을 포함
    # 예비 에너지 소비를 저장하는 딕셔너리
    energy_consumptions = {node: float('infinity') for node in graph}
    energy_consumptions[start] = 0
    # 최적 경로에서 이전 노드를 저장하는 딕셔너리
    previous_nodes = {node: None for node in graph}

    while priority_queue:
        current_energy, current_node, current_altitude = heapq.heappop(priority_queue)

        if current_node == goal:
            path = []
            while previous_nodes[current_node] is not None:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.append(start)
            return path[::-1]

        for neighbor, altitude, distance in graph[current_node]['adj_node']:
            # 이전 노드의 고도를 기반으로 고도 변경을 계산
            altitude_change = abs(current_altitude - altitude)
            if neighbor == goal:
                altitude_change = current_altitude  # 착륙 고도가 0이고 현재 고도가 8인 경우, 실제 착륙 고도로 업데이트
            energy_to_neighbor = current_energy + battery_consumption.Calculate_energy_consumption(
                altitude_change, 1.5, distance, payload, drone_name
            )
            if energy_to_neighbor < energy_consumptions[neighbor]:
                energy_consumptions[neighbor] = energy_to_neighbor
                previous_nodes[neighbor] = current_node
                # 업데이트: 다음 반복을 위해 현재 노드의 고도를 포함
                heapq.heappush(priority_queue, (energy_to_neighbor, neighbor, altitude))

# 드론 경로를 생성하는 함수
def generate_drone_path(start_node, destination_node,input_payload):
    payload = input_payload
    graph = database.get_graph(start_node)
    altitudes = {node: int(graph[node]['adj_node'][0][1]) if 'adj_node' in graph[node] and graph[node]['adj_node'] else 0 for node in graph}
    altitudes[start_node] = int(database.findBCname(start_node).get('altitude', 0))
    shortest_path = dijkstra(graph, start_node, destination_node, payload)
    if shortest_path:
        total_energy_consumption = battery_consumption.calculate_total_energy_consumption(graph, altitudes, shortest_path, destination_node, payload, drone_name)
        return shortest_path, total_energy_consumption
    else:
        print("경로를 찾을 수 없습니다.")




# # Input data(front)
start_node = "bc1"
# destination_node = "5"
# input_payload = 1.5

# data = drone_path_select(input_payload, destination_node)
# print(data[0], data[1])
