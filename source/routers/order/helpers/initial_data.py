from starlette.exceptions import HTTPException

from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.order.helpers.check_out import check_price_qty
from source.routers.order.helpers.shipment_requests import ship_address_object


# TODO full product data in cart
# TODO add stocks in cart
# TODO reciver info api


class EditQuantity:
    def __init__(self, parent_system_code, system_code, storage_id, count):
        self.parent_system_code = parent_system_code
        self.system_code = system_code
        self.storage_id = storage_id
        self.count = count

def initial(auth_header, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        cart = get_cart(response=response, auth_header=auth_header)
        check_out = check_price_qty(auth_header[0], cart)
        if check_out['success']:
            rpc.response_len_setter(response_len=1)
            cart_result = rpc.publish(
                message={
                    "cart": {
                        "action": "remove_cart",
                        "body": {
                            "user_id": auth_header[0].get("user_id")
                        }
                    }
                },
                headers={'cart': True}
            ).get("cart", {})
            if cart_result['success']:
                initial_data = ship_address_object(auth_header, cart)
                customer = get_profile_info(auth_header[0])
                address = initial_data[1]
                shipment = initial_data[0]

                rpc.response_len_setter(response_len=1)
                reciver_info = rpc.publish(
                    message={
                        "customer": {
                            "action": "get_delivery_persons",
                            "body": {
                                "data": {
                                    "customer_phone_number": customer['customerPhoneNumber'],
                                }
                            }
                        }
                    },
                    headers={'customer': True}
                ).get("customer")
                if reciver_info['success']:
                    rpc.response_len_setter(response_len=1)
                    wallet_response = rpc.publish(
                        message={
                            "wallet": {
                                "action": "get_customer_wallet_customer_side",
                                "body": {
                                    "customer_id": auth_header[0].get("user_id")
                                }
                            }
                        },
                        headers={'wallet': True}
                    ).get("wallet", {})
                    if wallet_response['success']:
                        result = {
                            "customerData": {
                                "customerName": f'{customer["customerFirstName"]} {customer["customerLastName"]}',
                                "customerCity": customer['customerCity'],
                                "customerCityId": customer['cityID'],
                                "customerState": customer['customerProvince'],
                                "customerStateId": customer['customerProvinceCode'],
                                "CustomerAddress": address
                            },
                            "shipmentDetail": shipment,
                            "reciverInfo": reciver_info.get("message").get("data"),
                            "wallet": wallet_response['message'].get('remainingAmount'),
                            "products": cart['products'],
                            "totalPrice": cart['total_price']

                        }
                        return result

                    else:
                        # wallet response
                        return {"success": False, "message": "wallet not responce!"}
                else:
                    # customer result
                    return {"success": False, "message": "customer not responce!"}
            else:
                # cart result
                return {"success": False, "message": "cart not responce!"}

        else:
            # check out response
            return {"success": False, "message": check_out['message']}
