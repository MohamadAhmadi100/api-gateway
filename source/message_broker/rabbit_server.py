import json
import signal
import uuid

import pika

from source.config import settings
from source.helpers.exception_handler import ExceptionHandler


class RabbitRPC:
    def __init__(
            self,
            exchange_name: str,
            timeout: int,
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
        self.broker_response = dict()
        self.corr_id = None
        self.response_len = 0
        self.timeout = timeout
        signal.signal(signal.SIGALRM, self.timeout_handler)

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                blocked_connection_timeout=3600  # 86400 seconds = 24 hours
            )
        )
        return connection

    def fanout_publish(self, exchange_name: str, message: dict):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=json.dumps(message)
        )

    def response_len_setter(self, response_len: int):
        self.response_len = response_len
        self.corr_id = str(uuid.uuid4())

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
        signal.alarm(self.timeout)
        while len(self.broker_response) < self.response_len:
            self.connection.process_data_events()
        signal.alarm(0)
        result = self.broker_response.copy()
        self.broker_response.clear()
        return result

    def on_response(self, channel, method, properties, body):
        if self.corr_id == properties.correlation_id:
            print("message received...")
            key = next(iter(json.loads(body)))
            self.broker_response[key] = json.loads(body).get(key)

    def consume(self):
        self.channel.basic_consume(on_message_callback=self.on_response, queue=self.callback_queue, auto_ack=True)

    def timeout_handler(self, signum, frame):
        signal.alarm(0)
        self.response_len = 0
        self.broker_response = {"error": "One or more services is not responding", "status_code": 408}
        exc_handler = ExceptionHandler(message="One or more services is not responding")
        exc_handler.logger()
        exc_handler.send_sms()


if __name__ == '__main__':
    rpc = RabbitRPC(exchange_name='qad-qamete-salat')
    rpc.connect()
    # rpc.consume()
    # rpc.publish(message={'type': 'qad'}, headers={'type': 'qad'})
    # print(rpc.response)
    inp = input("enter a message: ")
    rpc.fanout_publish('namaz', {inp: True})
