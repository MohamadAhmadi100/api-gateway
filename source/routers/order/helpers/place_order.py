from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.helpers.profile_view import get_profile_info

rpc = RabbitRPC(exchange_name='headers_exchange', timeout=5)
rpc.connect()
rpc.consume()


def place_order(auth_header):
    user, token_dict = auth_header
    # check if all will have response(timeout)
    rpc.response_len_setter(response_len=1)
    result = rpc.publish(
        message={
            "cart": {
                "action": "get_cart",
                "body": {
                    "user_id": user.get("user_id")
                }
            }
        },
        headers={'cart': True}
    )
    result['user_info'] = user
    result['customer'] = get_profile_info(user)

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
    )
    return result_to_order
