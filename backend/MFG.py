from backend import database

def generateMissionFile(basecamp, destination, user):
    # basecamp, destination을 가지고 경로 생성
    route = [basecamp, destination]

    # 거리를 기준으로 드론 배정?
    drone = 'test_drone'
    flight_alt = database.getFlightAlt(drone)

    # 미션 파일 생성

    # 테스트 미션 파일
    missionFile = {
        'user': user,
        'basecamp': basecamp,
        'destination': destination,
        'route': route,
        'drone': drone,
        'flight_alt': flight_alt,
        'receiver_info': 'test_receiver_info'
    }

    # user의 과거 미션 파일 삭제
    database.rmPastMissionFile(user)

    # 미션 파일 DB에 저장
    database.saveMissionFile(missionFile)

    return