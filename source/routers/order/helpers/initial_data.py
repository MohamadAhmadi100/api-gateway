from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.helpers.profile_view import get_profile_info


# TODO full product data in cart
# TODO add stocks in cart
# TODO reciver info api

def get_stocks(stocks):
    return stocks


def initial(user):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        customer = get_profile_info(user)
        rpc.response_len_setter(response_len=1)
        cart = rpc.publish(
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
        cart = cart['message']

        stocks = result_to_order = rpc.publish(
            message={
                "cart": {
                    "action": "get_cart",
                    "body": {
                        "user_id": user.get("user_id")
                    }
                }
            },
            headers={'order': True}
        )

        result = {
            "isDone": False,
            "customerData": {
                "customerName": customer['customerName'],
                "customerCity": customer['customerCity'],
                "customerCityId": customer['cityID'],
                "customerState": customer['customerProvince'],
                "customerStateId": customer['customerProvinceID'],
                "CustomerAddress": customer['customerAddress']
            },

        }

