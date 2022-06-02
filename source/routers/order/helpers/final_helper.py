from source.message_broker.rabbit_server import RabbitRPC


def handle_order_bank_callback(payment_detail):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        if payment_detail['is_paid']:
            rpc.response_len_setter(response_len=1)
            order_response = rpc.publish(
                message={
                    "order": {
                        "action": "order_bank_callback_processing",
                        "body": {
                            "peyment_data": payment_detail
                        }
                    }
                },
                headers={'order': True}
            ).get("order", {})
            return order_response
        else:
            rpc.response_len_setter(response_len=2)
            order_response = rpc.publish(
                message={
                    "order": {
                        "action": "order_bank_callback_cancel",
                        "body": {
                            "peyment_data": payment_detail
                        }
                    }
                },
                headers={'order': True}
            ).get("order", {})
            return order_response
