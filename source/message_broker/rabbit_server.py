import datetime
import json
import signal
import sys
import uuid

import pika
from pika.exceptions import StreamLostError

from source.config import settings
from source.helpers.exception_handler import ExceptionHandler


class RabbitRPC:
    def __init__(
            self,
            exchange_name: str,
            timeout: int,
            local: bool = False
    ):
        self.host = settings.RABBITMQ_HOST if not local else "localhost"
        self.port = settings.RABBITMQ_PORT if not local else 5672
        self.user = settings.RABBITMQ_USER if not local else "guest"
        self.password = settings.RABBITMQ_PASS if not local else "guest"
        self.exchange_name = exchange_name
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = None
        self.channel = None
        self.connect()
        self.broker_response = {}
        self.corr_id = None
        self.response_len = 0
        self.timeout = timeout
        self.consume()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def connect(self):
        # connect to rabbit with defined credentials
        if not self.connection or self.connection.is_closed:
            credentials = pika.PlainCredentials(self.user, self.password)
            try_counter = 1
            while True:
                try:
                    self.connection = pika.BlockingConnection(
                        pika.ConnectionParameters(
                            host=self.host,
                            port=self.port,
                            credentials=self.credentials,
                            heartbeat=0,
                            blocked_connection_timeout=86400  # 86400 seconds = 24 hours
                        )
                    )
                    break
                except Exception as e:
                    try_counter += 1
                    if try_counter > 3:
                        raise e
            # self.connection.sleep(1)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='headers')
            self.queue_result = self.channel.queue_declare(queue="", exclusive=True)
            self.callback_queue = self.queue_result.method.queue
            if self.channel_is_closed():
                self.connect()

    def fanout_publish(self, exchange_name: str, message: dict):
        # publish to all services
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', passive=True)
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=json.dumps(message)
        )

    def channel_is_closed(self):
        return self.channel.is_closed

    def response_len_setter(self, response_len: int):
        # response length setter for timeout handler
        self.response_len = response_len
        self.corr_id = str(uuid.uuid4())

    def publish(self, message: dict, headers: dict, extra_data: str = None):
        # publish message with given message and headers
        if self.channel_is_closed():
            self.connect()
            self.publish(message=message, headers=headers, extra_data=extra_data)
        try:
            self.channel.basic_publish(
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
            started = datetime.datetime.now()
            timed_out = False
            while len(self.broker_response) < self.response_len:
                if (datetime.datetime.now() - started).total_seconds() < 10 and not timed_out:
                    print(f"timeout {message}")
                    timed_out = True
                self.connection.process_data_events()
            result = self.broker_response.copy()
            self.broker_response.clear()
            return result
        except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed,
                pika.exceptions.ChannelWrongStateError, StreamLostError, pika.exceptions.AMQPHeartbeatTimeout,
                pika.exceptions.AMQPConnectionError) as error:
            sys.stdout.write("\033[1;31m")
            print("        !!! ERROR !!!       =================== Pika Exception raised: ", end="")
            sys.stdout.write("\033[;1m\033[1;31m")
            print(error, " ========================     ")
            self.connect()
        except Exception as e:
            sys.stdout.write("\033[1;31m")
            print("        !!! ERROR !!!       =================== Unknown Exception raised: ", end="")
            sys.stdout.write("\033[;1m\033[1;31m")
            print(e, " ========================     ")
            self.connect()

    def on_response(self, channel, method, properties, body):
        if self.corr_id == properties.correlation_id:
            print("message received...")
            key = next(iter(json.loads(body)))
            self.broker_response[key] = json.loads(body).get(key)

    def consume(self):
        self.channel.basic_consume(on_message_callback=self.on_response, queue=self.callback_queue, auto_ack=True)

    def timeout_handler(self, signum, frame):
        # manual handler for not taking response from consumers according to timeout
        signal.alarm(0)
        self.response_len = 0
        self.broker_response = {"error": "One or more services is not responding", "status_code": 408}
        exc_handler = ExceptionHandler(message="One or more services is not responding")
        exc_handler.logger()
        exc_handler.send_sms()


if __name__ == '__main__':
    rpc = RabbitRPC(exchange_name='test_exchange', timeout=5)
    rpc.connect()
    rpc.consume()
    rpc.response_len_setter(response_len=1)
    test_result = rpc.publish(
        message={
            "service": {
                "action": "get_something",
                "body": {
                    "test_data": "some_test_data"
                }
            }
        },
        headers={"service": True}
    )
    test_result = test_result.get("service", {})
    # -----------------------------------------------------------------

    rpc.fanout_publish('another_test_exchange', {"message": True})
