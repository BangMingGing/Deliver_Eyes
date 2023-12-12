import aio_pika
import asyncio
import pickle

import database
import utils

class TaskManager():
    def __init__(self, exchange):
        self.mission_file_cache = {}
        self.mission_lists = {}
        self.occupied_nodes = []
        self.lock = asyncio.Lock()

        self.exchange = exchange

        self.hover_alt = 3


    async def mission_valid(self, drone_name, current_mission):
        mission = self.mission_lists[drone_name]

        # 미자막 노드인 경우
        if current_mission+1 == len(mission):
            past_node = mission[current_mission-1]
            await self.delete_occupied_node(past_node)
            return
        next_node = mission[current_mission+1]

        flag = await self.try_occypy_node(next_node)
        # 노드가 이미 선점된 경우 -> 검증 실패 -> pause
        if flag == False:
            pause_message = await utils.get_mission_pause_message()
            await self.publish_message(pause_message, drone_name)
            return
        # 노드가 선점되지 않은 경우 -> 검증 성공
        elif flag == True:
            # 첫번째 노드의 경우 지난 노드가 없기 때문에 삭제 X
            if current_mission == 0:
                return
            # 나머지 노드의 경우 지난 노드가 있기 때문에 삭제 O
            past_node = mission[current_mission-1]
            await self.delete_occupied_node(past_node)
            return

    
    async def resume_valid(self, drone_name, current_mission):
        mission = self.mission_lists[drone_name]

        # 선점 못했던 노드
        next_node = mission[current_mission+1]

        # 노드를 선점할때까지 반복
        while True:
            # 노드를 선점한 경우
            if (await self.try_occypy_node(next_node)):
                resume_message = await utils.get_resume_message()
                await self.publish_message(resume_message, drone_name)
                return
            await asyncio.sleep(1)


    async def mission_register(self, drone_name, direction):
        mission_file = await self.get_mission_file(drone_name)

        # 정방향 미션을 미션리스트에 추가
        if direction == 'forward':
            # mission의 값만 복제하여 새로운 mission 생성
            mission = mission_file['mission'][:]
            destination = mission[-1]
            mission.append([destination[0], destination[1], self.hover_alt])
            self.mission_lists[drone_name] = mission
        # 역방향(복귀) 미션을 미션리스트에 추가
        elif direction == 'reverse':
            self.mission_lists[drone_name] = mission_file['mission'][::-1]

        return

    async def mission_start(self, drone_name, direction):
        mission = self.mission_lists[drone_name]
        first_node = mission[0]

        # 첫 노드를 선점할때까지 반복
        while True:
            flag = await self.try_occypy_node(first_node)
            # 첫 노드를 선점한 경우 미션 시작
            if flag == True:
                if direction == 'forward':
                    mission_file = self.mission_file_cache[drone_name]
                    receiver = mission_file['user']
                    messages = await utils.get_mission_start_messages(mission, direction, receiver)
                    await self.publish_messages(messages, drone_name)
                if direction == 'reverse':
                    messages = await utils.get_mission_start_messages(mission, direction, None)
                    await self.publish_messages(messages, drone_name)
                return
            elif flag == False:
                await asyncio.sleep(1)


    async def mission_finished(self, drone_name, direction):
        mission = self.mission_lists[drone_name]
        # 정방향 미션의 경우 대기
        if direction == 'forward':
            return
        # 역방향(복귀) 미션의 경우 랜딩 명령 전달
        elif direction == 'reverse':
            message = await utils.get_land_message()
            await self.publish_message(message, drone_name)
            await self.delete_occupied_node(mission[-1])
            del self.mission_lists[drone_name]
            del self.mission_file_cache[drone_name]
        return
    
    async def face_recog_start(self, drone_name):
        message = await utils.get_face_recog_start_message()
        await self.publish_message(message, drone_name)
        return

    async def certification_success(self, drone_name):
        mission = self.mission_lists[drone_name]
        message = await utils.get_land_message()
        await self.publish_message(message, drone_name)
        await self.delete_occupied_node(mission[-1])
        del self.mission_lists[drone_name]
        return

    async def certification_failed(self, drone_name):
        # 역방향으로 설정
        direction = 'reverse'
        # 이전 미션 저장
        mission_past = self.mission_lists[drone_name]
        print(1)
        # 미션리스트에서 미션 삭제
        del self.mission_lists[drone_name]
        print(2)
        # 역방향 미션 등록
        await self.mission_register(drone_name, direction)
        print(3)
        # 이륙 없이 역방향 미션 시작
        await self.mission_start(drone_name, direction)
        print(4)
        # 미션이 시작되었다면 호버링하고 있던 노드를 선점된 노드에서 삭제
        await self.delete_occupied_node(mission_past[-1])
        print(5)
        return

    async def get_mission_file(self, drone_name):
        # 캐시에 미션파일이 있다면 캐시에서 가져오기
        if drone_name in self.mission_file_cache:
            return self.mission_file_cache[drone_name]
        # 캐시에 미션파일이 없다면 DB에서 미션파일 가져와 캐시에 저장 후 미션파일 반환
        elif drone_name not in self.mission_file_cache:
            mission_file = database.getMissionFileByDrone(drone_name)
            self.mission_file_cache[drone_name] = mission_file
            return mission_file


    async def try_occypy_node(self, node):
        flag = True
        async with self.lock:
            # 노드가 이미 선점되었다면 flag값 false로 변환
            if node in self.occupied_nodes:
                flag = False
            # 노드가 선점되지 않았다면 선점
            if flag == True:
                self.occupied_nodes.append(node)
                print(f"Add {node}")
                print(f"Occupied_node : {self.occupied_nodes}")
        return flag


    # 지나온 노드를 삭제하는 함수
    async def delete_occupied_node(self, node):
        async with self.lock:
            self.occupied_nodes.remove(node)
            print(f"Remove {node}")
            print(f"Occupied_node : {self.occupied_nodes}")
        return

    # 메시지 하나를 드론에게 전달하는 함수
    async def publish_message(self, message, drone_name):
        await self.exchange.publish(
            aio_pika.Message(body=pickle.dumps(message)), 
            routing_key=f"to{drone_name}"
        )

    # 여러 메시지를 하나씩 드론에게 전달하는 함수
    async def publish_messages(self, messages, drone_name):
        for message in messages:
            await self.exchange.publish(
                aio_pika.Message(body=pickle.dumps(message)), 
                routing_key=f"to{drone_name}"
            )
        return