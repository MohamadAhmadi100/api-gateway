import json

import pika

from source.config import settings


class RabbitRPCClient:
    def __init__(
            self,
            receiving_queue: str,
            callback: callable,
            exchange_name: str,
            headers: dict,
            headers_match_all: bool = False
    ):
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.user = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.connection = self.connect()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="headers")
        self.receiving_queue = receiving_queue
        self.channel.queue_declare(queue=self.receiving_queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.callback = callback
        self.fanout_callback = None
        self.headers = headers
        self.headers["x-match"] = "all" if headers_match_all else "any"
        self.channel.queue_bind(
            exchange=exchange_name,
            queue=self.receiving_queue,
            routing_key="",
            arguments=self.headers
        )

    def connect(self):
        # connect to rabbit with defined credentials
        credentials = pika.PlainCredentials(self.user, self.password)
        return pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials, heartbeat=5,
                                      blocked_connection_timeout=86400))  # 86400 seconds = 24 hours

    def publish(self, channel, method, properties, body):
        # publish result of messages
        message = self.callback(json.loads(body))
        channel.basic_publish(exchange='',
                              routing_key=properties.reply_to,
                              properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                              body=json.dumps(message))
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def fanout_callback_runnable(self, channel, method, properties, body):
        self.fanout_callback(json.loads(body))

    def fanout_callback_setter(self, fanout_callback):
        self.fanout_callback = fanout_callback

    def fanout_consume(self, exchange_name: str):
        # consume fanout messages
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        received_queue = self.channel.queue_declare(queue='', exclusive=True)
        received_queue_name = received_queue.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=received_queue_name)
        self.channel.basic_consume(
            queue=received_queue_name,
            on_message_callback=self.fanout_callback_runnable,
            auto_ack=True
        )
        self.channel.start_consuming()

    def consume(self):
        # wait and get messages from API GW
        self.channel.basic_consume(queue=self.receiving_queue, on_message_callback=self.publish)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()


if __name__ == "__main__":
    def callback(message: dict):
        message['another-test'] = 'testing...'
        return message


    rpc = RabbitRPCClient(receiving_queue="test_queue", callback=callback, exchange_name="test_exchange",
                          headers={'service': True}, headers_match_all=False)
    rpc.connect()
    rpc.consume()


    # ----------------------------------------------------------------------

    def fanout_callback(message: dict):
        if message.get("message"):
            print("fanout_message...")


    rpc.fanout_callback_setter(fanout_callback)
    rpc.fanout_consume("another_test_exchange")
