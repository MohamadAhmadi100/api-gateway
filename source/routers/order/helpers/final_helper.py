from source.message_broker.rabbit_server import RabbitRPC
from source.routers.order.helpers.payment_helper import wallet_payment_consume


def handle_order_bank_callback(result, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        user_cart = rpc.publish(
            message={
                "cart": {
                    "action": "get_cart",
                    "body": {
                        "user_id": result.get("customer_id")
                    }
                }
            },
            headers={'cart': True}
        ).get('cart', {}).get('message', {})

        # consume wallet
        if user_cart['payment'].get("walletAmount") is not None:
            wallet_result = wallet_payment_consume(result, user_cart)

        if result['is_paid']:
            rpc.response_len_setter(response_len=2)
            rpc.publish(
                message={
                    "order": {
                        "action": "order_bank_callback_processing",
                        "body": {
                            "payment_data": result
                        }
                    },
                    "cart": {
                        "action": "delete_cart",
                        "body": {
                            "user_id": result.get("customerId")
                        }
                    }

                },
                headers={'order': True, "cart": True}
            ).get("order", {})
            response.status_code = 200
            return {"result": True, "service_id": result.get("service_id")}
        else:
            rpc.response_len_setter(response_len=1)
            rpc.publish(
                message={
                    "order": {
                        "action": "order_bank_callback_cancel",
                        "body": {
                            "payment_data": result
                        }
                    }
                },
                headers={'order': True}
            ).get("order")
            rpc.response_len_setter(response_len=1)
            order_get_response = rpc.publish(
                message={
                    "order": {
                        "action": "get_order",
                        "body": {
                            "order_id": result.get("service_id")
                        }
                    }
                },
                headers={'order': True}
            ).get("order")
            rpc.response_len_setter(response_len=1)
            rpc.publish(
                message={
                    "quantity": {
                        "action": "remove_from_reserve",
                        "body": {
                            "order": order_get_response.get("order_object")
                        }
                    }
                },
                headers={"quantity": True}
            ).get("quantity")
            response.status_code = 200
            return {"result": False, "service_id": result.get("service_id")}


def reserve_order_items(order_object):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        order_response = rpc.publish(
            message={
                "quantity": {
                    "action": "add_to_reserve",
                    "body": {
                        "order": order_object,
                    }
                }
            },
            headers={'quantity': True}
        ).get("quantity", {})
        return order_response


def delete_order_reserving_fail(order_object):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        order_response = rpc.publish(
            message={
                "order": {
                    "action": "order_delete",
                    "body": {
                        "order_data": order_object,
                    }
                }
            },
            headers={'order': True}
        ).get("order", {})
        return order_response


def place_order(auth_header, cart, customer):
    user, token_dict = auth_header
    # check if all will have response(timeout)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        result = dict()
        result['cart'] = cart
        result['user_info'] = user
        result['customer'] = customer

        rpc.response_len_setter(response_len=1)
        result_to_order = rpc.publish(
            message={
                "order": {
                    "action": "place_order",
                    "body": {
                        "order_data": result,
                    }
                }
            },
            headers={'order': True}
        ).get("order")
        if result_to_order.get("success"):
            return result_to_order
        else:
            return {"success": False, "message": "something went wrong!"}


def add_final_flag_to_cart(auth_header):
    user, token_dict = auth_header
    # check if all will have response(timeout)
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        rpc.response_len_setter(response_len=1)
        result_to_order = rpc.publish(
            message={
                "cart": {
                    "action": "final_flag",
                    "body": {
                        "user_id": user.get("user_id"),
                    }
                }
            },
            headers={'cart': True}
        ).get("cart")
        if result_to_order.get("success"):
            return result_to_order
        else:
            return {"success": False, "message": "something went wrong!"}
