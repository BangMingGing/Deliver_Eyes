from . import database

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

# 그래프에 노드를 추가하는 함수
def add_node_to_graph(graph, node_info, visited_nodes):
    node_name = str(node_info['node_name'])
    adj_nodes_info = node_info.get('adj_node', [])
    filtered_adj_nodes = [
        (str(neighbor_info[0]), neighbor_info[1], neighbor_info[2])
        for neighbor_info in adj_nodes_info
        if str(neighbor_info[0]) not in visited_nodes and str(neighbor_info[0]) != node_name
    ]
    graph[node_name] = {'adj_node': filtered_adj_nodes}
    visited_nodes.add(node_name)
    return graph

# 그래프를 구축하는 함수
def build_graph(start_node):
    visited_nodes = set()
    graph = initialize_graph(database.findBCname(start_node))
    for node_info in database.findNodes():
        print('node_info :' , node_info)
        if str(node_info['node_name']) != start_node:
            graph = add_node_to_graph(graph, node_info, visited_nodes)
        else:
            graph[node_info['node_name']] = {'adj_node': []}
    return graph



