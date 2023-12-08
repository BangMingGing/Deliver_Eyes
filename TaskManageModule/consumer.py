import aio_pika
import asyncio
import pickle

from task_manager import TaskManager
from configuration import RABBITMQ_CONFIG

async def task_consume(connection):
    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.TASK_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    queue = await channel.declare_queue(RABBITMQ_CONFIG.TASK_QUEUE)
    await queue.bind(exchange, f"to{queue}")
    
    task_manager = TaskManager(exchange)

    async def publish_message(message, drone_name):
        await exchange.publish(
            aio_pika.Message(
                body=pickle.dumps(message), 
                routing_key=f"to{drone_name}"
            )
        )

    async def publish_messages(self, messages, drone_name):
        for message in messages:
            await self.exchange.publish(
                aio_pika.Message(body=pickle.dumps(message)), 
                routing_key=f"to{drone_name}"
            )
        return

    async def consume():
        async for message in queue:
            async with message.process():
                message = pickle.loads(message.body, encoding='bytes')
                
                drone_name = message['drone_name']
                header = message['header']
                contents = message['contents']

                if header == 'mission_valid':
                    current_mission = contents['current_mission']
                    await task_manager.mission_valid(drone_name, current_mission)

                elif header == 'resume_valid':
                    current_mission = contents['current_mission']
                    await task_manager.resume_valid(drone_name, current_mission)
                
                elif header == 'mission_start':
                    direction = contents['direction']
                    await task_manager.mission_register(drone_name, direction)
                    await task_manager.mission_start(drone_name, direction)

                elif header == 'mission_finished':
                    direction = contents['direction']
                    await task_manager.mission_finished(drone_name, direction)

                
                print('message complete')
                print('message : ', message)

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