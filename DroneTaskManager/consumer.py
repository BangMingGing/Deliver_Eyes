import pika
import pickle

from taskManager import TaskManager

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

class Consumer():
    def __init__(self):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = 'TaskScheduler'
        self.exchange_name = 'TaskScheduler'

        # Queue 선언
        queue = self.channel.queue_declare(self.queue_name)
        # Exchange 선언
        self.channel.exchange_declare(self.exchange_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=f'to{self.queue_name}')

        # TaskManager 인스턴스 생성
        self.task_manager = TaskManager()

    
    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')
        
        drone = message['drone']

        self.task_manager.run(drone)

        ch.basic_ack(deliver_tag=method.deliver_tag)


    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print(f'TaskScheduler Start Consuming')
        self.channel.start_consuming()



if __name__ == '__main__':
    consumer = Consumer()
    consumer.consume()