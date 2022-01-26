import json
import uuid

import pika

from source.config import settings


class RabbitRPC:
    def __init__(
            self,
            exchange_name: str
    ):
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.user = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.connection = self.connect()
        self.channel = self.connection.channel()
        self.exchange_name = exchange_name
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='headers')
        queue_result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = queue_result.method.queue
        self.response = None
        self.corr_id = str(uuid.uuid4())

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials))
        return connection

    def fanout_publish(self, exchange_name: str, message: dict):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=json.dumps(message)
        )

    def publish(self, message: dict, headers: dict):
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key='',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                headers=headers
            ),
            body=json.dumps(message)
        )
        print("message sent...")
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def on_response(self, channel, method, properties, body):
        if self.corr_id == properties.correlation_id:
            print("message received...")
            self.response = json.loads(body)

    def consume(self):
        self.channel.basic_consume(on_message_callback=self.on_response, queue=self.callback_queue, auto_ack=True)


if __name__ == '__main__':
    rpc = RabbitRPC(exchange_name='qad-qamete-salat')
    rpc.connect()
    # rpc.consume()
    # rpc.publish(message={'type': 'qad'}, headers={'type': 'qad'})
    # print(rpc.response)
    inp = input("enter a message: ")
    rpc.fanout_publish('namaz', {inp: True})

