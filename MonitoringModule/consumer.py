import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pika
import pickle

import database

from configuration import RABBITMQ_CONFIG


async def log_consume(connection):
    channel = await connection.channel()
    exchange = aio_pika.Exchange(channel, RABBITMQ_CONFIG.LOG_EXCHANGE, type=aio_pika.ExchangeType.DIRECT)
    await exchange.declare()
    queue = await channel.declare_queue(RABBITMQ_CONFIG.LOG_QUEUE)
    await queue.bind(exchange, f"to{queue}")

    semaphore = asyncio.Semaphore(value=1)

    async def consume_with_semaphore():
        async with semaphore:
            async for message in queue:
                async with message.process():
                    message_data = pickle.loads(message.body, encoding='bytes')
                    database.insert_log(message_data)
                    # print(f"Received message: {message_data}")


    print("Log Consumer started")

    while True:
        await consume_with_semaphore()

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