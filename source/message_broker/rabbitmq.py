import datetime
import json
import logging
import time
import uuid

import pika
from fastapi import HTTPException

from source.config import settings
from source.helpers.saga_pattern import Saga


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
        self.saga = Saga()
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

    def publish_pre_requisite(self, message: list, saga: bool):
        messages = dict()
        for i in message:
            messages.update(i)
        if saga:
            self.saga.add(messages)
        self.response_len = len(messages)
        self.corr_id = str(uuid.uuid4())
        return messages

    def publish_response_handler(self, messages: dict, saga: bool, compensate: bool = False):
        if len(self.broker_response) < self.response_len:
            bad_services = list(messages.keys() - self.broker_response.keys())
            logging.info(f"Timeout waiting for response... services: {', '.join(bad_services)}")
            if saga:
                self.saga.remove(bad_services)
                stack = self.saga.compensate()
                for _ in range(len(stack)):
                    item = stack.pop()
                    self.publish(message=[item], compensate=True)
                self.saga.finish()

            self.broker_response.clear()
            raise HTTPException(
                status_code=500,
                detail={"error": f"{', '.join(bad_services)} does not respond..."}
            )
        else:
            result = list()
            error_services = [i for i in messages.keys() if not self.broker_response.get(i).get("success")]
            if len(error_services):
                if saga:
                    self.saga.remove(error_services)
                    stack = self.saga.compensate()
                    for _ in range(len(stack)):
                        item = stack.pop()
                        self.publish(message=[item], compensate=True)
                    self.saga.finish()

                status_code = self.broker_response.get(error_services[0]).get("status_code", 500)
                error = self.broker_response.get(error_services[0]).get("error", "Something went wrong...")
                self.broker_response.clear()
                raise HTTPException(
                    status_code=status_code,
                    detail=error
                )
            for i in messages.keys():
                result.append(self.broker_response.get(i, {}))
            result = result[0] if len(result) == 1 else result
            self.broker_response.clear()
            return result

    def publish(self, message: list, extra_data: str = None, saga: bool = False, compensate: bool = False):
        messages = self.publish_pre_requisite(message, saga)
        try_count = 0
        while True:
            try_count += 1
            try:
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
                break
            except Exception as e:
                logging.info(f"Error publishing to RabbitMQ... {e}")
                if try_count > 3:
                    raise e
                self.publish_connection, self.publish_channel, self.callback_queue = self.connect()
                self.consume()
        started = datetime.datetime.now()
        while (len(self.broker_response) < self.response_len) and (
                (datetime.datetime.now() - started).total_seconds()) < self.timeout:
            try:
                self.publish_connection.process_data_events()
            except Exception as e:
                logging.info(f"Error consuming from RabbitMQ... {e}")
                self.publish_connection, self.publish_channel, self.callback_queue = self.connect()
                self.consume()
        return self.publish_response_handler(messages, saga, compensate)

    def compensate_actions(self):
        items = self.saga.startup_action()

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


new_rpc = RabbitRPC(exchange_name='headers_exchange', timeout=10)
