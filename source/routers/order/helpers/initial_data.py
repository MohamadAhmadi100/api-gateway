from source.message_broker.rabbit_server import RabbitRPC
from source.routers.customer.helpers.profile_view import get_profile_info
from source.routers.cart.helpers.get_cart_helper import get_cart
from source.routers.order.helpers.check_out import check_price_qty
from source.routers.order.helpers.shipment_requests import ship_address_object


# TODO full product data in cart
# TODO add stocks in cart
# TODO reciver info api


def initial(user):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        cart = get_cart(user[0])['message']
        # check_out = check_price_qty(user[0], cart)
        # if check_out['success']:
        initial_data = ship_address_object(user, cart)
        customer = get_profile_info(user[0])
        address = initial_data[1]
        shipment = initial_data[0]
        result = rpc.publish(
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
        )
        customer_result = result.get("customer", {})
        reciver_info = None
        wallet_response = rpc.publish(
            message={
                "wallet": {
                    "action": "get_customer_wallet_customer_side",
                    "body": {
                        "customer_id": user[0].get("customer_id")
                    }
                }
            },
            headers={'wallet': True}
        ).get("wallet", {})['message']
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
            "reciverInfo": reciver_info,
            "wallet": wallet_response,
            "products": cart['products'],

        }
        return result
    # else:
    #     return {"success": False, "message": "ya abalfaaaaaaaaaaaz"}
