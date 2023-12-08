import math
from . import database

# default
gravity_acceleration = 9.8  # m/s^2 (standard value)
air_density = 1.225  # kg/m^3 (standard value)
roll_deg = 15
drag_coefficient = 1.49
velocity = 1.5
# drone_name = get_drone_name()

# def get_drone_name():
#     from MFG import drone_name
#     get_drone_name = drone_name
#     print(get_drone_name)
#     return get_drone_name

# drone_name = get_drone_name()


# print("bt drone name: " , drone_name)
# drone_data = database.get_drone_spec(drone_name)

# # motor_efficiency = drone_data['motor_efficiency']
# # battery_efficiency = drone_data['battery_efficiency']
# # default_voltage = drone_data['default_voltage']
# # total_battery_capacity_mah = drone_data['total_battery_capacity_mah']
# # drone_weight = drone_data['drone_weight']
# # drone_cross_sectional_area = drone_data['drone_cross_sectional_area']
# # propeller_efficiency = drone_data['propeller_efficiency']
# # thrust_coefficient = drone_data['thrust_coefficient']



#드론 배터리 소모량 계산(mAh)
def calculate_battery_consumption(energy_consumption, drone_name, voltage=None):
    drone_data = database.get_drone_spec(drone_name)
    default_voltage = drone_data['default_voltage']
    # Use the provided voltage if available, otherwise use the default
    actual_voltage = voltage if voltage is not None else default_voltage

    # Convert energy consumption to battery consumption in mAh
    battery_consumption_mah = (energy_consumption / actual_voltage) * 3600 / 1000

    return battery_consumption_mah

#사용 비율 계산 (%)
def calculate_battery_percentage(used_battery_mah, total_battery_mah):
    # Calculate the percentage of used battery
    battery_percentage = (used_battery_mah / total_battery_mah) * 100

    return battery_percentage


#배터리 소모량 계산
def Calculate_energy_consumption(altitude_change,velocity,distance, payload, drone_name):
    drone_data = database.get_drone_spec(drone_name)

    motor_efficiency = drone_data['motor_efficiency']
    battery_efficiency = drone_data['battery_efficiency']
    drone_weight = drone_data['drone_weight']
    drone_cross_sectional_area = drone_data['drone_cross_sectional_area']
    propeller_efficiency = drone_data['propeller_efficiency']
    thrust_coefficient = drone_data['thrust_coefficient']
    actual_drone_weight = drone_weight + payload
    energy_consumption = (
        1
        / (motor_efficiency * battery_efficiency)
        * (
            #potential
            actual_drone_weight * gravity_acceleration * altitude_change * propeller_efficiency
            #aero
            + 0.5 * drag_coefficient * air_density * drone_cross_sectional_area * velocity**2 * distance / propeller_efficiency
            #Tx
            + velocity * propeller_efficiency  * actual_drone_weight * gravity_acceleration * distance*thrust_coefficient
            #Ty
            + actual_drone_weight * gravity_acceleration * math.sin(roll_deg) * drag_coefficient * distance*thrust_coefficient
        )
    )

    # Calculate battery consumption in mAh
    #used_battery_mah = calculate_battery_consumption(energy_consumption)
    #battery_percentage = calculate_battery_percentage(used_battery_mah, total_battery_capacity_mah)

    # Calculate battery consumption in mAh
    battery_consumption_mah = calculate_battery_consumption(energy_consumption, drone_name)


    return battery_consumption_mah

# 전체 에너지 소비량을 계산하는 함수
def calculate_total_energy_consumption(graph, altitudes, shortest_path, goal_node, input_payload, drone_name ):
    total_energy_consumption = 0
    payload = input_payload
    # 최단 경로의 각 노드 쌍에 대해 에너지 소비량을 계산
    print("input shortest_path : ", shortest_path)
    for i in range(len(shortest_path) - 1):
        current_node = shortest_path[i]
        next_node = shortest_path[i + 1]
        print(f"current_node : {current_node} to next_node : {next_node}")
        edge_info = next((info for info in graph[current_node]['adj_node'] if info[0] == next_node), None)
        if edge_info:
            _, _, distance = edge_info
            if next_node == goal_node:
                altitude_change = abs(altitudes[current_node])
            else:
                altitude_change = abs(altitudes[current_node] - int(altitudes[next_node]))

            # 에너지 소비량을 계산
            print(f"distance change : {distance}, altitude_change : {altitude_change}")
            energy_consumption_mah = Calculate_energy_consumption(altitude_change, velocity, distance, payload, drone_name)
            print(f"energy_consumption_mah is {energy_consumption_mah}")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            # 총 에너지 소비량 구하기
            total_energy_consumption += energy_consumption_mah

    return total_energy_consumption
