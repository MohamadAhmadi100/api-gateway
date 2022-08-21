from source.message_broker.rabbitmq import RabbitRPC as NewRabbit

new_rpc = NewRabbit(exchange_name='headers_exchange', timeout=10)
