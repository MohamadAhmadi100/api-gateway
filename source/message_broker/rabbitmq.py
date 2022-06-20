import datetime
import json
import random
import uuid

import pika
import time

from source.config import settings


class RabbitRPC:
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
        self.publish_connection, self.publish_channel = self.connect()
        self.consume_connection, self.consume_channel = self.connect()
        self.queue_result = self.publish_channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = self.queue_result.method.queue
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
                return connection, channel
            except Exception as e:
                print("Error connecting to pika...")
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

    def publish(self, message: dict, headers: dict, extra_data: str = None):
        # publish message with given message and headers
        self.response_len = len(message)
        self.corr_id = str(uuid.uuid4())
        try_count = 0
        while True:
            try_count += 1
            try:
                print("publish initiated...")
                self.publish_channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key='',
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue,
                        correlation_id=self.corr_id,
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                        content_type=extra_data,
                        headers=headers
                    ),
                    body=json.dumps(message) if isinstance(message, dict) else message
                )
                print("message sent...")
                break
            except Exception as e:
                print("Error publishing message...")
                if try_count > 3:
                    raise e
                self.connect()
        started = datetime.datetime.now()
        while (len(self.broker_response) < self.response_len) and (
                (datetime.datetime.now() - started).total_seconds()) < self.timeout:
            try:
                self.publish_connection.process_data_events()
            except Exception:
                print("Error listening for response...")
                self.connect()
        if len(self.broker_response) < self.response_len:
            print("Couldn't get response from these services:")
            bad_services = list(message.keys() - self.broker_response.keys())
            print(bad_services)
        result = self.broker_response.copy()
        self.broker_response.clear()
        return result

    def on_response(self, channel, method, properties, body):
        if self.corr_id == properties.correlation_id:
            print("message received...")
            key = next(iter(json.loads(body)))
            self.broker_response[key] = json.loads(body).get(key)

    def consume(self):
        self.publish_channel.basic_consume(on_message_callback=self.on_response, queue=self.callback_queue,
                                           auto_ack=True)
