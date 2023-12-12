import asyncio
import json

from backend import token, database

def getUserFromCookies(cookies):
    try:
        access_token = cookies.get("access_token")
        user = token.verify_token(access_token)
        return user
    except:
        print("Error in getUserFromCookies function")
        return None

def add_new_neighbor(node_name, neighbor_node_list):
    try:
        # 기존 노드에 새로운 이웃 추가
        for neighbor_name, max_height, distance in neighbor_node_list:
            original_neighbor_name = neighbor_name  # 원본 neighbor_name을 보존
            neighbor_name = int(neighbor_name.replace('bc', ''))  # 'bc'를 제외한 부분을 정수로 변환
            
            # Check if neighbor_name contains 'bc'
            if 'bc' in original_neighbor_name:
                # Perform the same operation in 'Basecamp' collection
                basecamp_result = database.getBC_adjnode(original_neighbor_name)
                if basecamp_result and "adj_node" in basecamp_result:
                    is_already_neighbor_bc = False
                    
                    for adj_node_info_bc in basecamp_result["adj_node"]:
                        adj_node_name_bc = adj_node_info_bc[0]
                        
                        if node_name == adj_node_name_bc:
                            is_already_neighbor_bc = True
                            print("Already a neighbor in Basecamp!")
                            break  
                    node_name = str(node_name)
                    if not is_already_neighbor_bc and int(node_name) != original_neighbor_name:
                        bc_adj_node = [node_name, max_height, distance]
                        database.update_bc_neighbor(original_neighbor_name, bc_adj_node)
                        print(f"{original_neighbor_name} neighbor in Basecamp, {node_name} is registered!")

            # Continue with the original operation in 'Nodes' collection
            result = database.getnode_adjnode(neighbor_name)
            if result and "adj_node" in result:
                is_already_neighbor = False
                
                for adj_node_info in result["adj_node"]:
                    adj_node_name = adj_node_info[0]
                    
                    if node_name == adj_node_name:
                        is_already_neighbor = True
                        print("Already a neighbor!")
                        break  
                node_name = str(node_name)
                if not is_already_neighbor and int(node_name) !=neighbor_name:
                    node_adj_node = [node_name, max_height, distance]
                    database.update_node_neighbor(neighbor_name, node_adj_node)
                    print(f"{neighbor_name} neighbor, {node_name} is registered!")
            else:
                print("No neighbor in Nodes")
    
    except Exception as e:
        print(f"An error occurred: {e}")


def delete_node(node_name):
    node_name = int(node_name)
    #Nodes 컬렉션에서 node_name이 nodeName인 도큐먼트 삭제
    database.delete_node(node_name)
    try:
        # 노드를 찾음
        result = database.find_adj_node(node_name)
        # 결과가 있다면 출력
        result_list = list(result)
        if len(result_list) > 0:
            for doc in result_list:
                # 베이스캠프에서도 해당 노드를 찾음
                basecamp_result = database.find_BC_adj_node(node_name)
                basecamp_result_list = list(basecamp_result)
                # 베이스캠프에서 해당 노드를 찾았을 경우 베이스캠프의 adj_node 배열에서도 삭제
                if len(basecamp_result_list) > 0:
                    for basecamp_doc in basecamp_result_list:
                        # adj_node 배열에서 특정 노드를 삭제
                        new_basecamp_adj_node = [elem for elem in basecamp_doc['adj_node'] if elem[0] != str(node_name)]
                        # 베이스캠프 업데이트
                        database.reupdate_bc_adjnode(basecamp_doc,new_basecamp_adj_node)
                # Nodes에서 노드 삭제
                new_adj_node = [elem for elem in doc['adj_node'] if elem[0] != str(node_name)]
                database.reupdate_node_adjnode(doc,new_adj_node)
            return True
        else:
            # 노드가 1개 밖에 없는 경우에도 Basecamp에서 해당 노드를 찾아 삭제
            basecamp_result_single = database.find_BC_adj_node(node_name)
            basecamp_result_single_list = list(basecamp_result_single)

            if len(basecamp_result_single_list) > 0:
                for basecamp_doc_single in basecamp_result_single_list:
                    new_basecamp_adj_node_single = [elem for elem in basecamp_doc_single['adj_node'] if elem[0] != str(node_name)]
                    database.reupdate_bc_adjnode(basecamp_doc_single,new_basecamp_adj_node_single)
                return True
            else:
                return False
    except Exception as e:
            print(f"Error occurred while deleting node_name '{node_name}': {e}")
            return False

#graph 관련

# 그래프를 기본 정보로 초기화하는 함수
def initialize_graph(start_basecamp_info):
    graph = {}
    basecamp_name = start_basecamp_info['BC_name']
    adj_nodes_info = start_basecamp_info.get('adj_node', [])

    graph[basecamp_name] = {
        'adj_node': [
            (str(neighbor_info[0]), neighbor_info[1], neighbor_info[2])
            for neighbor_info in adj_nodes_info
            if str(neighbor_info[0]) != basecamp_name
        ]
    }
    return graph

def add_node_to_graph(graph, node_info):
    node_name = str(node_info['node_name'])
    adj_nodes_info = node_info.get('adj_node', [])
    print(f"node_name {node_name} : adj_nodes_info {adj_nodes_info}")
    filtered_adj_nodes = [
        (str(neighbor_info[0]), neighbor_info[1], neighbor_info[2])
        for neighbor_info in adj_nodes_info
        if str(neighbor_info[0]) != node_name
    ]
    graph[node_name] = {'adj_node': filtered_adj_nodes}
    return graph

# 그래프 그리기
def build_graph_for_basecamps(basecamps):
    existing_graphs = database.findGraph()  # Graph 컬렉션의 도큐먼트들을 가져옴
    existing_BC_names = {graph.get('BC_name') for graph in existing_graphs}  # 이미 존재하는 BC_name들을 세트로 저장
    for basecamp in basecamps:
        BC_name = basecamp.get('BC_name')
        if BC_name and BC_name not in existing_BC_names:
                visited_nodes = set()
                graph = initialize_graph(database.findBCname(BC_name))
                for node_info in database.findNodes():
                    if str(node_info['node_name']) != BC_name:
                        graph = add_node_to_graph(graph, node_info, visited_nodes)
                    else:
                        graph[node_info['node_name']] = {'adj_node': []}
                database.saveGraph(BC_name, graph)

# 그래프 수정하기
def revise_graph(basecamps):
    for basecamp in basecamps:
        BC_name = basecamp.get('BC_name')
        #visited_nodes = set()
        graph = initialize_graph(database.findBCname(BC_name))
        for node_info in database.findNodes():
            if str(node_info['node_name']) != BC_name:
                #graph = add_node_to_graph(graph, node_info, visited_nodes)
                graph = add_node_to_graph(graph, node_info)
            else:
                graph[node_info['node_name']] = {'adj_node': []}
        print("revised graph is " , graph)
        database.reviseGraph(BC_name, graph)

#path를 입력 받아 path_coor로 반환해주는 함수
def getpath_coor(path):
    path_coor = []
    for node_name in path:
        if 'bc' in node_name.lower():
            bc_coor = database.getBCcoor(node_name)
            path_coor.append(bc_coor)
        else:
            node_coor = database.getNodecoor(int(node_name))
            path_coor.append(node_coor)
    return path_coor

def getRoute(mission):
    route = []
    for (lon, lat, alt) in mission:
        route.append([lon, lat])
    return route


async def gps_event_generator(drone_name):
    while True:
        drone_status = database.getDroneStatusByDroneName(drone_name)
        gps_info = drone_status['GPS_info']
        gps_data = [gps_info['lon'], gps_info['lat']]
        face_recog_start_flag = (drone_status['mission_status'] == "Mission Finished")
        yield f"data: {json.dumps({'gps_data': gps_data, 'face_recog_start_flag': face_recog_start_flag})}\n\n"
        await asyncio.sleep(1)

async def face_recog_result_event_generator(drone_name):
    while True:
        face_recog_result = database.getFaceRecogResultByDroneName(drone_name)
        yield f"data: {json.dumps({'face_recog_result': face_recog_result})}\n\n"
        await asyncio.sleep(1)


async def get_all_gps_event_generator():
    while True:
        drone_data = database.getdata4gps()
        data = {}

        for entry in drone_data:
            drone_name = entry['drone_name']
            mission = entry['mission']
            
            # 드론 상태에서 드론 좌표 가져오기
            gps_data = database.getDroneStatusByDroneName(drone_name)
            data[drone_name] = {'gps_data': gps_data, 'mission': mission}
        # JSON 형태로 변환하여 SSE로 보냅니다.
        yield f"data: {json.dumps(data)}\n\n"
        # 1초 간격으로 반복합니다.
        await asyncio.sleep(1)
