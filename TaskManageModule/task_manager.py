import asyncio
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
        next_node = mission[current_mission+1]

        self.occupied_nodes_lock.acquire()
        if (await self.isValidNode(next_node)):
            self.occupied_nodes.append(next_node)
            self.occupied_nodes_lock.release()
            return

        else:
            self.occupied_nodes_lock.release()
            await self.get_mission_pause_message()
            await self.publish_message(message, drone_name)
            return
            


    async def mission_register(self, drone_name):
        mission_file = {}
        if drone in self.mission_file_cache:
            mission_file = self.mission_file_cache[drone_name]
        
        elif drone not in self.mission_file_cache:
            mission_file = database.getMissionFileByDrone(drone_name)
            self.mission_file_cache[drone_name] = mission_file

        self.mission_lists[drone_name] = mission_file['way_points']

        return

    async def mission_start(self, drone_name):
        mission = self.mission_lists[drone_name]
        first_node = mission[0]
        second_node = mission[1]

        while True:
            self.occupied_nodes_lock.acquire()
            if (await self.isValidNodes([first_node, second_node])):
                self.occupied_nodes.append(first_node)
                self.occupied_nodes.append(second_node)
                self.occupied_nodes_lock.release()
                messages = await self.get_mission_start_messages(mission)
                await self.publihs_messages(messages, drone_name)
                return
            else:
                self.occupied_nodes_lock.release()
                await asyncio.sleep(1)
        

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
        message = {
            'header': 'upload_mission', 
            'contents': {'mission': mission}
        }
        message = {
        'header': 'takeoff',
        'contents': {'takeoff_alt': 10}
        }
        message = {
            'header': 'start_mission',
            'contents': {}
        }
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