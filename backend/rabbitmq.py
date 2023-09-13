import pika
import pickle

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

class Task_Publisher():
    
    def __init__(self, exchange_name):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()
        
        self.exchange_name = exchange_name
        # Exchange 선언
        self.channel.exchange_declare(self.exchange_name)

    
    def publish(self, message, target):        
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=f'to{target}',
            body=pickle.dumps(message)
        )

        return True