import datetime
import json
import logging
import uuid
import pika
import time
from source.config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RabbitRPC(metaclass=Singleton):
    def __init__(
            self,
            exchange_name: str,
            timeout: int,
    ):
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.user = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASS
        self.exchange_name = exchange_name
        self.publish_connection, self.publish_channel, self.callback_queue = self.connect()
        self.broker_response = {}
        self.corr_id = None
        self.response_len = 0
        self.timeout = timeout
        self.consume()

    def connect(self):
        # connect to rabbit with defined credentials
        credentials = pika.PlainCredentials(self.user, self.password)
        try_count = 0
        while True:
            try_count += 1
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host,
                                              port=self.port,
                                              credentials=credentials)
                )
                channel = connection.channel()
                channel.exchange_declare(exchange=self.exchange_name, exchange_type='headers')
                queue_result = channel.queue_declare(queue="", exclusive=True)
                return connection, channel, queue_result.method.queue
            except Exception as e:
                logging.info(f"Error connecting to RabbitMQ... {e}")
                print(f"{datetime.datetime.now()} - Error connecting to pika...{e}")
                if try_count > 1000:
                    raise e
                time.sleep(1)

    def fanout_publish(self, exchange_name: str, message: dict):
        # publish to all services
        self.publish_channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', passive=True)
        self.publish_channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=json.dumps(message)
        )

    def publish(self, message: list, extra_data: str = None):
        messages = dict()
        for i in message:
            messages.update(i)
        # publish message with given message and headers
        self.response_len = len(messages)
        logging.info(f"expected response num: {self.response_len}")
        print(f"{datetime.datetime.now()} - expected response num {self.response_len}")
        self.corr_id = str(uuid.uuid4())
        logging.info(f"first corr id: {self.corr_id}")
        print(f"{datetime.datetime.now()} - first corr id : {self.corr_id}")
        try_count = 0
        while True:
            try_count += 1
            try:
                logging.info(f"Publishing message: {messages}")
                # print("publish initiated...")
                print(f"{datetime.datetime.now()} - Publishing message: {messages}")
                self.publish_channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key='',
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue,
                        correlation_id=self.corr_id,
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                        content_type=extra_data,
                        headers={i: True for i in messages.keys()}
                    ),
                    body=json.dumps(messages) if isinstance(messages, dict) else messages
                )
                print(f"{datetime.datetime.now()} - message sent...")
                logging.info("Message sent...")
                break
            except Exception as e:
                logging.info(f"Error publishing to RabbitMQ... {e}")
                print(f"{datetime.datetime.now()} - Error publishing message... {e}")
                if try_count > 3:
                    raise e
                self.publish_connection, self.publish_channel, self.callback_queue = self.connect()

    def on_response(self, channel, method, properties, body):
        if self.corr_id == properties.correlation_id:
            # print("message received...")
            logging.info("Message received...")
            print(f"{datetime.datetime.now()} - Message received...")
            key = next(iter(json.loads(body)))
            self.broker_response[key] = json.loads(body).get(key)

    def consume(self):
        try_count = 0
        while True:
            try:
                try_count += 1
                self.publish_channel.basic_consume(on_message_callback=self.on_response, queue=self.callback_queue,
                                                   auto_ack=True)
                break
            except Exception as e:
                if try_count > 100:
                    raise e
                self.publish_connection, self.publish_channel, self.callback_queue = self.connect()


rabbit_rpc = RabbitRPC(exchange_name='headers_exchange', timeout=10)
