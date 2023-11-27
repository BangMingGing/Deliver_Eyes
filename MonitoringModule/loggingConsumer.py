import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pika
import pickle

from backend import database
from config import RABBITMQ_CONFIG


RABBITMQ_SERVER_IP = RABBITMQ_CONFIG.SERVER_IP
RABBITMQ_SERVER_PORT = RABBITMQ_CONFIG.SERVER_PORT

class Logging_Consumer():
    
    def __init__(self):
        self.credentials = pika.PlainCredentials(RABBITMQ_CONFIG.USER, RABBITMQ_CONFIG.PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, RABBITMQ_CONFIG.HOST, self.credentials))
        self.channel = self.connection.channel()

        self.my_name = '[Logging_Consumer]'
        
        self.exchange_name = 'monitoring'
        self.queue_name = 'log_queue'

        # Queue 선언
        queue = self.channel.queue_declare(self.queue_name)
        # Exchange 선언
        self.channel.exchange_declare(self.exchange_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=f'to{self.queue_name}')

    
    def callback(self, ch, method, properties, body):
        log = pickle.loads(body, encoding='bytes')
        database.insert_log(log)
        # print(f'{self.my_name} Log_info : ', log)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print(f'{self.my_name} Start Consuming')
        self.channel.start_consuming()
        
        
if __name__ == '__main__':
    consumer = Logging_Consumer()
    consumer.consume()