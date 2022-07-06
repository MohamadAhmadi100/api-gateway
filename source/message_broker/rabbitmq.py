import datetime
import json
import logging
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
        self.queue_result = self.consume_channel.queue_declare(queue="", exclusive=True, durable=True)
        self.callback_queue = self.queue_result.method.queue
        print(self.callback_queue)
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

    def publish(self, message: dict, headers: dict, extra_data: str = None):
        # publish message with given message and headers
        self.response_len = len(message)
        logging.info(f"expected response num: {self.response_len}")
        print(f"{datetime.datetime.now()} - expected response num {self.response_len}")
        self.corr_id = str(uuid.uuid4())
        logging.info(f"first corr id: {self.corr_id}")
        print(f"{datetime.datetime.now()} - first corr id : {self.corr_id}")
        try_count = 0
        while True:
            try_count += 1
            try:
                logging.info(f"Publishing message: {message}")
                # print("publish initiated...")
                print(f"{datetime.datetime.now()} - Publishing message: {message}")
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
                print(f"{datetime.datetime.now()} - message sent...")
                logging.info("Message sent...")
                break
            except Exception as e:
                logging.info(f"Error publishing to RabbitMQ... {e}")
                print(f"{datetime.datetime.now()} - Error publishing message... {e}")
                if try_count > 3:
                    raise e
                self.publish_connection, self.publish_channel = self.connect()
        started = datetime.datetime.now()
        while (len(self.broker_response) < self.response_len) and (
                (datetime.datetime.now() - started).total_seconds()) < self.timeout:
            try:
                self.consume_connection.process_data_events()
            except Exception as e:
                logging.info(f"Error consuming from RabbitMQ... {e}")
                print(f"{datetime.datetime.now()} - Error listening for response... {e}")
                self.consume_connection, self.consume_channel = self.connect()
                self.consume()
        print(f"{datetime.datetime.now()} - "
              f"actual response num: {len(self.broker_response)}"
              f", expected response num: {self.response_len}")
        logging.info(f"actual response num: {len(self.broker_response)}, expected response num: {self.response_len}")

        if len(self.broker_response) < self.response_len:
            print(f"{datetime.datetime.now()} - Couldn't get response from these services:")
            bad_services = list(message.keys() - self.broker_response.keys())
            print(f"{datetime.datetime.now()} - bad_services")
            logging.info(f"Timeout waiting for response... services: {bad_services}")
            print(f"{datetime.datetime.now()} - Timeout waiting for response... services: {bad_services}")
        result = self.broker_response.copy()
        logging.info(f"Final response is ...{result}")
        print(f"{datetime.datetime.now()} - Final response is ...{result}")
        logging.info(f"second corr id: {self.corr_id}")
        print(f"{datetime.datetime.now()} - second corr id: {self.corr_id}")
        self.broker_response.clear()
        return result

    def on_response(self, channel, method, properties, body):
        if self.corr_id == properties.correlation_id:
            # print("message received...")
            logging.info("Message received...")
            print(f"{datetime.datetime.now()} - Message received...")
            key = next(iter(json.loads(body)))
            self.broker_response[key] = json.loads(body).get(key)

    def consume(self):
        self.consume_channel.basic_consume(on_message_callback=self.on_response, queue=self.callback_queue,
                                           auto_ack=True)


if __name__ == '__main__':
    rpc = RabbitRPC(exchange_name='headers_exchange', timeout=15)
    count = 1
    while True:
        result = rpc.publish(
            message={
                "product": {
                    "action": "get_product_by_system_code",
                    "body": {
                        "system_code": "10010104302",
                        "lang": "fa_ir"
                    }
                }, "pricing": {
                    "action": "get_price",
                    "body": {
                        "system_code": "10010104302"
                    }
                }, "quantity": {
                    "action": "get_quantity",
                    "body": {
                        "system_code": "10010104302"
                    }
                }
            },
            headers={'product': True, "pricing": True, "quantity": True}
        )
        print(count)
        count += 1
