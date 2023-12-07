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


    async def mission_valid(self, drone_name, current_mission):
        mission = self.mission_lists[drone_name]

        if current_mission+1 == len(mission):
            past_node = mission[current_mission-1]
            await self.delete_node(past_node)
            return
        next_node = mission[current_mission+1]

        flag = await self.try_occypy_node(next_node)
        if flag == False:
            pause_message = await utils.get_mission_pause_message()
            await self.publish_message(pause_message, drone_name)
            return

        elif flag == True:
            if current_mission-1 >= 0:
                past_node = mission[current_mission-1]
                await self.delete_node(past_node)
            return


    async def mission_register(self, drone_name, direction):
        mission_file = {}
        if drone_name in self.mission_file_cache:
            mission_file = self.mission_file_cache[drone_name]
        elif drone_name not in self.mission_file_cache:
            mission_file = database.getMissionFileByDrone(drone_name)
            self.mission_file_cache[drone_name] = mission_file

        if direction == 'forward':
            self.mission_lists[drone_name] = mission_file['mission']
        elif direction == 'reverse':
            self.mission_lists[drone_name] = mission_file['mission'].reverse()


        return

    async def mission_start(self, drone_name, direction):
        mission = self.mission_lists[drone_name]
        first_node = mission[0]
        second_node = mission[1]

        while True:
            flag = await self.try_occypy_node(first_node)
            if flag == True:
                messages = await utils.get_mission_start_messages(mission, direction)
                await self.publish_messages(messages, drone_name)
                return
            elif flag == False:
                await asyncio.sleep(1)


    async def mission_finished(self, drone_name, direction):
        if direction == 'forward':
            message = await utils.get_forward_mission_finished_message()
            await self.publish_message(message, drone_name)
        elif direction == 'reverse':
            message = await utils.get_reverse_mission_finished_message()
            await self.publish_message(message, drone_name)
        

    async def try_occypy_node(self, node):
        flag = True
        async with self.lock:
            if node in self.occupied_nodes:
                flag = False
            if flag == True:
                self.occupied_nodes.append(node)
                print(f"Add {node}")
                print(f"Occupied_node : {self.occupied_nodes}")
        return flag
    

    async def try_occypy_nodes(self, nodes):
        flag = True
        async with self.lock:
            for node in nodes:
                if node in self.occupied_nodes:
                    flag = False
                    break
                if flag == True:
                    self.occupied_nodes.append(node)
        return flag
    

    async def delete_node(self, node):
        async with self.lock:
            self.occupied_nodes.remove(node)
            print(f"Remove {node}")
            print(f"Occupied_node : {self.occupied_nodes}")
        return


    async def publish_message(self, message, drone_name):
        await self.exchange.publish(
            aio_pika.Message(body=pickle.dumps(message)), 
            routing_key=f"to{drone_name}"
        )

    async def publish_messages(self, messages, drone_name):
        for message in messages:
            await self.exchange.publish(
                aio_pika.Message(body=pickle.dumps(message)), 
                routing_key=f"to{drone_name}"
            )
        return