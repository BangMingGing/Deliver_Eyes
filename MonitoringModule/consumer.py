import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import aio_pika
import asyncio
import pickle

import database

from configuration import RABBITMQ_CONFIG


async def log_consume(connection):
    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.LOG_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    queue = await channel.declare_queue(RABBITMQ_CONFIG.LOG_QUEUE)
    await queue.bind(exchange, f"to{queue}")

    async def consume():
        async for message in queue:
            async with message.process():
                message_data = pickle.loads(message.body, encoding='bytes')
                database.insert_log(message_data)
                print(f"Send Drone name : {message_data['drone_name']}")


    print(" -- [Log Consumer] started")

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
    print(" -- [Log Consumer] Connected to Rabbitmq")
    return connection

async def main():
    loop = asyncio.get_event_loop()

    connection = await rabbitmq_connect()

    consumer_task = loop.create_task(log_consume(connection))

    try:
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        pass
    finally:
        await connection.close()
        print("Connection closed")

if __name__ == "__main__":
    asyncio.run(main())