from backend import database

def generateMissionFile(basecamp, destination, user):
    # basecamp, destination을 가지고 경로 생성
    route = [basecamp, destination]

    # 거리를 기준으로 드론 배정?
    drone = 'test_drone'

    # 미션 파일 생성

    way_points = [
        (47.398039859999997, 8.5455725400000002, 10),   
        (47.398036222362471, 8.5450146439425509, 10),
        (47.397825620791885, 8.5450092830163271, 10),
        (47.398039859999997, 8.5455725400000002, 10),   
        (47.398036222362471, 8.5450146439425509, 10),
        (47.397825620791885, 8.5450092830163271, 10),
        (47.398039859999997, 8.5455725400000002, 10),   
        (47.398036222362471, 8.5450146439425509, 10),
        (47.397825620791885, 8.5450092830163271, 10),
        (47.398039859999997, 8.5455725400000002, 10),   
        (47.398036222362471, 8.5450146439425509, 10),
        (47.397825620791885, 8.5450092830163271, 10)
    ]


    # 테스트 미션 파일
    missionFile = {
        'user': user,
        'basecamp': basecamp, # 위도, 경도
        'destination': destination, # 위도, 경도
        'mission': way_points, # [위도, 경도, 고도]
        'drone': drone, 
        'receiver_info': 'test_receiver_info'
    }

    # user의 과거 미션 파일 삭제
    database.rmPastMissionFile(user)

    # 미션 파일 DB에 저장
    database.saveMissionFile(missionFile)
    
    

    return