import aio_pika
import asyncio
import pickle

from FaceRecogModule.server import Server_Inferer
from configuration import RABBITMQ_CONFIG

async def face_consume(face_queue, server_inferer, task_exchange):

    async def send_to_task_module(message):
        await task_exchange.publish(
            aio_pika.Message(body=pickle.dumps(message)), 
            routing_key=f"to{RABBITMQ_CONFIG.FACE_QUEUE}"
        )

    async def consume():
        async for message in face_queue:
            async with message.process():
                message = pickle.loads(message.body, encoding='bytes')
                
                drone_name = message['drone_name']
                header = message['header']
                contents = message['contents']

                if header == 'face_recog':
                    print('face recog called')
                    tensor = contents['tensor']
                    server_inferer.post_inference(drone_name, tensor)

                elif header == 'face_recog_finish':
                    print('face recog finish called')
                    receiver = contents['receiver']
                    face_recog_result = await server_inferer.get_face_recog_result(drone_name, receiver)
                    new_message = {'header': header, 'drone_name': drone_name, contents: {'face_recog_result': face_recog_result}}
                    await send_to_task_module(new_message)

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
    channel = await connection.channel()
    face_exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.FACE_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await face_exchange.declare()
    face_queue = await channel.declare_queue(RABBITMQ_CONFIG.FACE_QUEUE)
    await face_queue.bind(face_exchange, f"to{face_queue}")

    task_exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.TASK_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await task_exchange.declare()
    
    server_inferer = Server_Inferer()

    consumer_task = loop.create_task(face_consume(face_queue, server_inferer, task_exchange))

    try:
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())