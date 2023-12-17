import aio_pika
import asyncio
import pickle

import database

from task_manager import TaskManager
from configuration import RABBITMQ_CONFIG

async def task_consume(task_queue, task_manager):

    async def consume():
        async for message in task_queue:
            async with message.process():
                message = pickle.loads(message.body, encoding='bytes')
                
                drone_name = message['drone_name']
                header = message['header']
                contents = message['contents']

                if header == 'mission_valid':
                    print('mission_valid called')
                    current_mission = contents['current_mission']
                    await task_manager.mission_valid(drone_name, current_mission)

                elif header == 'resume_valid':
                    print('resume_valid called')
                    current_mission = contents['current_mission']
                    await task_manager.resume_valid(drone_name, current_mission)
                
                elif header == 'mission_start':
                    print('mission_start called')
                    direction = contents['direction']
                    await task_manager.mission_register(drone_name, direction)
                    await task_manager.mission_start(drone_name, direction)

                elif header == 'mission_finished':
                    print('mission_finished called')
                    direction = contents['direction']
                    await task_manager.mission_finished(drone_name, direction)

                elif header == 'face_recog_start':
                    print('face recog start called')
                    await task_manager.face_recog_start(drone_name)

                elif header == 'face_recog':
                    print('face recog called')
                    await database.send_to_face_module(message)

                elif header == 'face_recog_finish':
                    print('face recog finish called')
                    await database.send_to_face_module(message)
                    
                elif header == 'face_inference_finish':
                    print('face inference finish called')
                    face_recog_result = contents['face_recog_result']
                    if face_recog_result:
                        await task_manager.certification_success(drone_name)

                elif header == 'password_certify_success':
                    print('password_certify_success called')
                    await task_manager.certification_success(drone_name)
                
                elif header == 'password_certify_failed':
                    print('password_certify_failed called')
                    await task_manager.certification_failed(drone_name)


                print('message complete')
                

    print(" -- [Task Consumer] started")

    while True:
        await consume()

async def db_consume(task_manager):

    print(" -- [DB Task Consumer] started")
    while True:
        message = database.getTaskMessage()
        if message is not None:
            drone_name = message['drone_name']
            header = message['header']
            contents = message['contents']

            if header == 'mission_valid':
                print('mission_valid called')
                current_mission = contents['current_mission']
                await task_manager.mission_valid(drone_name, current_mission)

            elif header == 'resume_valid':
                print('resume_valid called')
                current_mission = contents['current_mission']
                await task_manager.resume_valid(drone_name, current_mission)
            
            elif header == 'mission_start':
                print('mission_start called')
                direction = contents['direction']
                await task_manager.mission_register(drone_name, direction)
                await task_manager.mission_start(drone_name, direction)

            elif header == 'mission_finished':
                print('mission_finished called')
                direction = contents['direction']
                await task_manager.mission_finished(drone_name, direction)

            elif header == 'face_recog_start':
                print('face recog start called')
                await task_manager.face_recog_start(drone_name)

            elif header == 'face_recog':
                print('face recog called')
                await database.send_to_face_module(message)

            elif header == 'face_recog_finish':
                print('face recog finish called')
                await database.send_to_face_module(message)
                
            elif header == 'face_inference_finish':
                print('face inference finish called')
                face_recog_result = contents['face_recog_result']
                if face_recog_result:
                    await task_manager.certification_success(drone_name)

            elif header == 'password_certify_success':
                print('password_certify_success called')
                await task_manager.certification_success(drone_name)
            
            elif header == 'password_certify_failed':
                print('password_certify_failed called')
                await task_manager.certification_failed(drone_name)


            print('message complete')
            await asyncio.sleep(1)
        
        else:
            await asyncio.sleep(1)


async def task_manager_status(task_manager):
    while True:
        print("Mission File Cache Saved Drones : ", task_manager.mission_file_cache.keys())
        print("Mission Lists Saved Drones : ", task_manager.mission_lists.keys())
        print("Occupied Nodes : ", task_manager.occupied_nodes)
        await asyncio.sleep(5)


async def rabbitmq_connect():
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_CONFIG.SERVER_IP,
        port=RABBITMQ_CONFIG.SERVER_PORT,
        login=RABBITMQ_CONFIG.USER,
        password=RABBITMQ_CONFIG.PASSWORD,
        virtualhost=RABBITMQ_CONFIG.HOST,
    )
    print(" -- [Task Consumer] Connected to Rabbitmq")
    return connection


async def main():
    loop = asyncio.get_event_loop()

    connection = await rabbitmq_connect()
    channel = await connection.channel()
    task_exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.TASK_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await task_exchange.declare()
    task_queue = await channel.declare_queue(RABBITMQ_CONFIG.TASK_QUEUE)
    await task_queue.bind(task_exchange, f"to{task_queue}")
    
    task_manager = TaskManager(task_exchange)

    consumer_task = loop.create_task(task_consume(task_queue, task_manager))
    db_consume_task = loop.create_task(db_consume(task_manager))
    status_task = loop.create_task(task_manager_status(task_manager))

    try:
        # await asyncio.gather(consumer_task)
        await asyncio.gather(consumer_task, db_consume_task, status_task)
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())