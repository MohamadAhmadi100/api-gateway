from source.message_broker.rabbit_server import RabbitRPC
from source.routers.cart.app import get_cart
from source.routers.customer.helpers.profile_view import get_profile_info


def ship_address_object(user, cart):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:
        result = []
        rpc.response_len_setter(response_len=1)
        storage_result = rpc.publish(
            message={
                "order": {
                    "action": "shipment_storage_detail",
                    "body": {
                        "cart_data": cart,
                    }
                }
            },
            headers={"order": True}
        )

        result.append(storage_result.get("order")['message'])
        rpc.response_len_setter(response_len=1)
        address_result = rpc.publish(
            message={
                "address": {
                    "action": "get_customer_addresses",
                    "body": {
                        "customerId": str(user[0].get("user_id"))
                    }
                }},
            headers={'address': True}
        )
        address = address_result.get("address")['result']
        for items in address:
            if items.get('isDefault'):
                address = items
                result.append(items)
                break
        stocks = []
        for items in result[0]:
            stocks.append({
                "stockName": items['warehouse_label'],
                "stockId": str(items['warehouse_id']),
                "origin": items['warehouse_city_id'],
                "destination": result[1]['cityId'],
                "weight": 0,
                "totalPrice": 0,
                "totalItem": 0
            })
        return_result = {
            "customerId": user[0].get("user_id"),
            "stocks": stocks,
        }
        rpc.response_len_setter(response_len=1)
        shipment_response = rpc.publish(
            message={
                "shipment": {
                    "action": "get_shipment_details",
                    "body": {
                        "data": str(return_result)
                    }
                }
            },
            headers={'shipment': True}
        ).get("shipment", {})['message']

        return shipment_response, address


def shipment_detail(auth_header, response):
    with RabbitRPC(exchange_name='headers_exchange', timeout=5) as rpc:

        cart = get_cart(response=response, auth_header=auth_header)
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
                "products": cart['products'],
                "totalPrice": cart['totalPrice']

            }
            return {"success": True, "message": result, "status_code": 200}

        else:
            # customer response
            return {"success": False, "message": "customer not responce!", "status_code": 404}
