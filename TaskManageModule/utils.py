import database


def getMissionFileByDrone(drone):
        if (drone in missionFileCache):
            return missionFileCache[drone]
        else:
            missionFile = database.getMissionFileByDrone(drone)
            missionFileCache[drone] = missionFile
            return missionFile


def makeCheckList(missionFile):
        basecamp_node = missionFile['basecamp']
        destination_node = missionFile['destination']
        way_points = missionFile['route']
        flight_alt = missionFile['flight_alt']
        receiver_info = missionFile['receiver_info']
        
        check_list = []
        
        check_list.append({'header': 'basecamp_takeoff', 'contents': {'alt': flight_alt}})
        for way_point in way_points:
            check_list.append({'header': 'goto_node', 'contents': {'lat': way_point['lat'], 'lon': way_point['lon'], 'alt': waypoint['alt']}})
        check_list.append({'header': 'goto_hovering_node', 'contents': {'lat': destination[1], 'lon': destination[0]}, 'alt': self.hovering_alt})
        check_list.append({'header': 'face_recognition', 'contents': {'receiver_info': receiver_info}})
        check_list.append({'header': 'destination_landing', 'contents': {}})
        check_list.append({'header': 'destination_takeoff', 'contents':{'alt': flight_alt}})
        for way_point in way_points.reverse():
            check_list.append({'header': 'goto_node', 'contents': {'lat': way_point['lat'], 'lon': way_point['lon'], 'alt': waypoint['alt']}})
        check_list.append({'header': 'basecamp_landing', 'contents': {}})

        return check_list


def distance_calc(coord1,coord2):
    # 지구 반경 (km)
    R = 6373.0

    # 위도, 경도를 라디안으로 변환
    lat1 = radians(coord1[0])
    lon1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lon2 = radians(coord2[1])

    # 경도, 위도 차이 계산
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # haversine 공식 적용
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # 거리 계산
    distance = R * c

    return distance