import aio_pika
import asyncio
import pickle
import threading
import database

class TaskManager():
    def __init__(self, exchange):
        self.mission_file_cache = {}
        self.mission_lists = {}
        self.occupied_nodes = []
        self.occupied_nodes_lock = threading.Lock()

        self.exchange = exchange


    async def mission_valid(self, drone_name, current_mission):
        mission = self.mission_lists[drone_name]

        if current_mission+1 == len(mission):
            return
        next_node = mission[current_mission+1]

        try:
            self.occupied_nodes_lock.acquire()
            if (await self.isValidNode(next_node)):
                self.occupied_nodes.append(next_node)
                return

            else:
                pause_message = await self.get_mission_pause_message()
                await self.publish_message(pause_message, drone_name)
                return
        finally:
            self.occupied_nodes_lock.release()

            


    async def mission_register(self, drone_name):
        mission_file = {}
        if drone_name in self.mission_file_cache:
            mission_file = self.mission_file_cache[drone_name]
        
        else:
            mission_file = database.getMissionFileByDrone(drone_name)
            self.mission_file_cache[drone_name] = mission_file

        self.mission_lists[drone_name] = mission_file['mission']

        return

    async def mission_start(self, drone_name):
        mission = self.mission_lists[drone_name]
        first_node = mission[0]
        second_node = mission[1]

        while True:
            try:
                self.occupied_nodes_lock.acquire()
                if (await self.isValidNodes([first_node, second_node])):
                    self.occupied_nodes.append(first_node)
                    self.occupied_nodes.append(second_node)
                    messages = await self.get_mission_start_messages(mission)
                    await self.publish_messages(messages, drone_name)
                    return
                else:
                    await asyncio.sleep(1)
            finally:
                self.occupied_nodes_lock.release()

        

    async def isValidNode(self, node):
        if node in self.occupied_nodes:
            return False
        return True
    

    async def isValidNodes(self, nodes):
        for node in nodes:
            if node in self.occupied_nodes:
                return False
        return True


    async def get_mission_start_messages(self, mission):
        messages = []
        messages.append({
            'header': 'upload_mission', 
            'contents': {'mission': mission}
        })
        messages.append({
        'header': 'takeoff',
        'contents': {'takeoff_alt': 10}
        })
        messages.append({
            'header': 'start_mission',
            'contents': {}
        })
        return messages


    async def get_mission_pause_message(self):
        message = {
            'header': 'pause_mission',
            'contents': {}
        }
        return message


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