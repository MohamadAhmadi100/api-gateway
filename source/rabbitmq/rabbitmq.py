from json import dumps, loads
from pika import BlockingConnection, ConnectionParameters, BasicProperties, PlainCredentials
from uuid import uuid4


class RabbitMQClient:
    def __init__(self, host, port, correlation_id=None):
        self.host = host
        self.port = port

        self.connection = None
        self.channel = None

        self.correlation_id = correlation_id

        try:
            self.create_connection()

        except BaseException:
            pass

    def create_connection(self):
        credentials = PlainCredentials('rbtmq', 'DeVrab!t123')
        self.connection = BlockingConnection(
            ConnectionParameters(host=self.host, port=self.port, blocked_connection_timeout=90, credentials=credentials)
        )
        self.channel = self.connection.channel()

    def is_connected(self):
        return self.connection is not None and self.channel is not None

    def create_queue(self, queue_name):
        self.channel.queue_declare(queue_name)

    def get_queue_names(self, queue_name):
        return queue_name, queue_name

    def send_message(self, queue_name, message=''):
        if self.correlation_id is None:
            self.correlation_id = str(uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=dumps(message).encode('utf-8'),
            properties=BasicProperties(
                correlation_id=self.correlation_id
            ),
        )

    def sync_receive_message(self, queue_name):
        for method, properties, message in self.channel.consume(queue_name, inactivity_timeout=1):

            if not message or self.correlation_id != properties.correlation_id:
                continue

            return loads(message)

    def async_receive_message(self, queue_name, on_message_callback):
        self.channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback)

    def async_start_consuming(self):
        self.channel.start_consuming()

    def async_ack(self, method):
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def close_connection(self):
        self.connection.close()
