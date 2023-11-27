import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pika
import pickle

from configration import RABBITMQ_CONFIG

RABBITMQ_SERVER_IP = RABBITMQ_CONFIG.SERVER_IP
RABBITMQ_SERVER_PORT = RABBITMQ_CONFIG.SERVER_PORT

class Publisher():
    
    def __init__(self):
        self.credentials = pika.PlainCredentials(RABBITMQ_CONFIG.USER, RABBITMQ_CONFIG.PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, RABBITMQ_CONFIG.HOST, self.credentials))
        self.channel = self.connection.channel()

    
    def publish(self, message, exchange_name, target):        
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=f'to{target}',
            body=pickle.dumps(message)
        )

        return True
    

    def declareExchange(self, exchange_name):
        self.channel.exchange_declare(exchange_name)
