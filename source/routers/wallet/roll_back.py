import logging
from source.routers.wallet.app import app
from source.saga_pattern.saga import SagaBuilder, SagaError
from source.message_broker.rabbit_server import RabbitRPC

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


class WalletRollBack:
    def __init__(self, service: str, action: str, data: dict):
        self.service = service
        self.action = action
        self.data = data

    app.on_event(self="create", event_type=rpc)

    def action_handler(self):
        logging.basicConfig(
            filename="saga.log",
            level=logging.WARNING,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        try:
            SagaBuilder \
                .create() \
                .action(lambda: self.action_builder(), lambda: self.action_rollback()) \
                .build() \
                .execute()
        except SagaError as e:
            logging.warning("---- Saga pattern Error ----", "\n", e)

    def action_builder(self):
        action_response = rpc.publish(
            message={
                self.service: {
                    "action": self.action,
                    "body": {
                        "values": self.data

                    }
                }
            },
            headers={self.service: True}
        )
        return action_response

    def action_rollback(self):
        rollback_response = rpc.publish(
            message={
                self.service: {
                    "action": f"{self.action}_rollback",
                    "body": {
                        "values": self.data
                    }
                }
            },
            headers={self.service: True}
        )
        return rollback_response
