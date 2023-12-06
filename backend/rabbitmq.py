import aio_pika
import asyncio
import pickle

from configuration import RABBITMQ_CONFIG

class Publisher():
    
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.exchange = None
    

    async def initialize(self):
        self.connection = await aio_pika.connect_robust(
            host=RABBITMQ_CONFIG.SERVER_IP,
            port=RABBITMQ_CONFIG.SERVER_PORT,
            login=RABBITMQ_CONFIG.USER,
            password=RABBITMQ_CONFIG.PASSWORD,
            virtualhost=RABBITMQ_CONFIG.HOST,
        )

        self.channel = await self.connection.channel()

        self.exchange = aio_pika.Exchange(
            self.channel, self.exchange_name, 
            type=aio_pika.ExchangeType.DIRECT
        )
        await self.exchange.declare()


    async def publish(self, message, queue_name):    
        await self.exchange.publish(
            aio_pika.Message(body=pickle.dumps(message)), 
            routing_key=f"to{queue_name}"
        )

    
    async def close(self):
        if self.connection:
            await self.connection.close()



async def main():
    publisher = Publisher('task')
    await publisher.initialize()


if __name__ == "__main__":
    asyncio.run(main())