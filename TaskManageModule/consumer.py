import aio_pika
import asyncio
import pickle

from task_manager import TaskManager
from FaceRecogModule.server import Server_Inferer
from configuration import RABBITMQ_CONFIG

async def task_consume(connection):
    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.TASK_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    queue = await channel.declare_queue(RABBITMQ_CONFIG.TASK_QUEUE)
    await queue.bind(exchange, f"to{queue}")
    
    task_manager = TaskManager(exchange)
    server_inferer = Server_Inferer()

    async def consume():
        async for message in queue:
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
                    tensor = contents['tensor']
                    server_inferer.post_inference(drone_name, tensor)

                elif header == 'face_recog_finish':
                    print('face recog finish called')
                    receiver = contents['receiver']
                    face_recog_result = await server_inferer.get_face_recog_result(drone_name, receiver)
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

    consumer_task = loop.create_task(task_consume(connection))

    try:
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())