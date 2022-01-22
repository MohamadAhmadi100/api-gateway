from source.rabbitmq.rabbitmq import RabbitMQClient


class RabbitMQ:
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

    def client_process_message(self, host, port, queue_name):

        message_broker = RabbitMQClient(host, port)

        message = {
            'status': False,
            'data': [],
        }

        if message_broker.is_connected():
            request_queue_name, response_queue_name = message_broker.get_queue_names(queue_name)

            message_broker.create_queue(request_queue_name)
            message_broker.send_message(request_queue_name, self.__dict__)

            message = message_broker.sync_receive_message(response_queue_name)

            message_broker.close_connection()

        return message.values()

    def server_process_message(self, host, port, queue_name, message, method, correlation_id):

        message_broker = RabbitMQClient(host, port, correlation_id)

        if message_broker.is_connected():
            request_queue_name, response_queue_name = message_broker.get_queue_names(queue_name)

            message_broker.send_message(response_queue_name, message)
            message_broker.async_ack(method)
